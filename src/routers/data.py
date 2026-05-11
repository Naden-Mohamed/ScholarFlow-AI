import os

from ..helpers.config import get_settings, Settings
from fastapi import APIRouter, UploadFile, Depends, status, Request
from fastapi.responses import JSONResponse
from ..controllers import DataController, ProjectController, ProcessController
from ..models.Enums.ResponseEnum import ResponseStatus
import logging
import aiofiles
from .schemas.data_schema import DataSchema
from src.models import ProjectModel, DataChunkModel,DataChunk,AssetModel
from src.models.db_schemas.asset import Asset
from bson.objectid import ObjectId
from src.models.Enums.DataBaseEnum import DataBaseEnums

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/data",
    tags=["Data"],
)

@data_router.post("/upload/{project_id}")
async def upload_file(
    request: Request, # this store all info about each request used to access app state exsit in main if needed 
    project_id: str,
    file: UploadFile,
    settings: Settings = Depends(get_settings)
):
    # If project_id wasn't given, create one
    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)
    print(f"Project ID: {project.id}, Project Unique ID: {project.project_id}")

    # Validate file properties
    data_controller = DataController.DataController()
    is_valid, response_signal = data_controller.validate_uploaded_file(file = file)
    print(f"File validation result: {is_valid}, Signal: {response_signal}")

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "is_valid": is_valid,   
                "response_signal": response_signal
            }
        )

    project_dir_path = ProjectController.ProjectController().get_project_path(project_id=project_id)
    file_path, file_id = data_controller.generate_unique_filename(original_filename=file.filename, project_id=project_id)
    print(f"File path: {file_path}, File ID: {file_id}")
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while chunk := await file.read(settings.FILE_DEFAULT_CHUNK_SIZE):
                await out_file.write(chunk)

    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        # NOT all errors should be exposed to the user (might be sensitive)
        # log the error for just internal review
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "is_valid": False,   
                "response_signal": ResponseStatus.FILE_UPLOAD_FAILED.value,
            }
        )
    
    asset_model = await AssetModel.create_instance(db_client=request.app.mongodb_client)
    asset = Asset(
        asset_project_id=project.id,
        asset_type="file",
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),
        asset_config= {
                "file_path": file_path,
                "file_id": file_id
            }
    )
    asset_record = await asset_model.create_asset(asset=asset)
    print(f"Asset record created with ID: {asset_record.id} for file: {file.filename}")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            # "is_valid": is_valid,   
            "response_signal": ResponseStatus.FILE_UPLOADED_SUCCESSFULLY.value,
            # "file_path": file_path,
            "file_id": str(asset_record.id),
            "project_id" : str(asset_record.asset_project_id )#don't expose yourself
        }
    )


@data_router.post("/process/{project_id}")
async def process_file(request: Request,project_id: str, data: DataSchema): 
   
    chunk_size = data.chunk_size
    chunk_overlap = data.overlap_size
    do_reset = data.do_reset

    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)


    # If file_id is given, process that file only, else process all project files
    project_files_id = {}

    asset_model = await AssetModel.create_instance(db_client=request.app.mongodb_client)

    if data.file_id:
        asset_record = await asset_model.get_asset_record(asset_project_id=project_id, asset_id=data.file_id)
        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={  
                    "response_signal": ResponseStatus.FILE_ID_ERROR.value,
                }
            )
        
        project_files_id = { str(asset_record.id): asset_record.asset_name }
    else:
        
        project_files = await asset_model.get_all_project_assets(asset_project_id=project.id, asset_type="application/pdf")
        project_files_id = { str(record.id): record.asset_name for record in project_files}

    if len(project_files_id) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={  
                "response_signal": ResponseStatus.NO_FILES_FOUNDED_TO_PROCESS.value,
            }
        )


    process_controller = ProcessController.ProcessController(project_id=project_id)

    inserted_count = 0
    files_count = 0

    data_chunk_model = await DataChunkModel.create_instance(db_client=request.app.mongodb_client)

    if do_reset == 1:
        _= await data_chunk_model.delete_chunk_by_project_id(project_id=project.id)


    for asset_id, file_id in project_files_id.items():
        file_path = asset_record.asset_config.get("file_path")

        if not file_path or not os.path.exists(file_path):
            logger.warning(f"File not found on disk: {file_path}")
            continue

        # ✅ Fix 5: load file content directly from local path
        file_content = process_controller.get_file_content(file_id=file_path)

        if file_content is None or len(file_content) == 0:
            logger.warning(f"File {file_path} has no content or could not be processed.")
            continue

        # ✅ Fix 6: pass file_path as file_id for extension detection
        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            chunk_size=chunk_size,
            overlap_size=chunk_overlap
        )
        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "is_valid": False,   
                    "response_signal": ResponseStatus.FILE_PROCESSING_FAILED.value,
                    "file_id": file_id
                }
            )
        
        file_chunks_records = [
            DataChunk(
                chunk_text= chunk.page_content, 
                chunk_metadata= chunk.metadata,
                chunk_order= idx + 1,
                chunk_project_id= project.id,
                chunk_asset_id= ObjectId(asset_id)
        )
            for idx, chunk in enumerate(file_chunks)
        ]


        inserted_count += await data_chunk_model.insert_many_chunks(chunks=file_chunks_records)
        files_count += 1

    return JSONResponse(
            content={  
                "response_signal": ResponseStatus.FILE_PROCESSED_SUCCESSFULLY.value,
                "processed_chunks": inserted_count,
                "processed_files_count": files_count
            }
        )
        


