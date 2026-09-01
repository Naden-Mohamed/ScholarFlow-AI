import logging
import os

import aiofiles
from fastapi import APIRouter, Depends, Request, UploadFile, status
from fastapi.responses import JSONResponse
from models.DataChunkModel import DataChunk, DataChunkModel

from controllers import DataController, ProcessController
from helpers.config import Settings, get_settings
from models.AssetModel import AssetModel
from models.db_schemas import Asset
from models.Enums.ResponseEnum import ResponseStatus
from models.ProjectModel import ProjectModel
from routers.schemas.data_schema import DataSchema

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/data",
    tags=["Data"],
)


@data_router.post("/upload/{project_id}")
async def upload_file(
    request: Request,  # this store all info about each request used to access app state exsit in main if needed
    project_id: str,
    file: UploadFile,
    settings: Settings = Depends(get_settings),
):
    # If project_id wasn't given, create one
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )
    project = await project_model.get_project_or_create_one(project_id=project_id)
    print(f"Project ID: {project.project_id}, Project Unique ID: {project.project_id}")

    # Validate file properties
    data_controller = DataController.DataController()
    is_valid, response_signal = data_controller.validate_uploaded_file(file=file)
    print(f"File validation result: {is_valid}, Signal: {response_signal}")

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"is_valid": is_valid, "response_signal": response_signal},
        )

    original_filename = file.filename or "unnamed_file"
    file_path, file_id = data_controller.generate_unique_filename(
        original_filename=original_filename, project_id=project_id
    )
    print(f"File path: {file_path}, File ID: {file_id}")
    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await file.read(settings.FILE_DEFAULT_CHUNK_SIZE):
                await out_file.write(chunk)

    except (OSError, ValueError) as e:
        logger.error(f"Error uploading file: {e}")
        # NOT all errors should be exposed to the user (might be sensitive)
        # log the error for just internal review
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "is_valid": False,
                "response_signal": ResponseStatus.FILE_UPLOAD_FAILED.value,
            },
        )

    asset_model = await AssetModel.create_instance(
        db_client=request.app.state.db_client
    )

    asset = Asset(
        asset_project_id=project.project_id,
        asset_type=file.content_type,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),
        asset_config={"file_path": file_path, "file_id": file_id},
    )
    asset_record = await asset_model.create_asset(asset=asset)
    print(
        f"Asset record created with ID: {asset_record.asset_uuid} for file: {file.filename}"
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "response_signal": ResponseStatus.FILE_UPLOADED_SUCCESSFULLY.value,
            "file_id": file_id,
            "project_id": str(asset_record.asset_project_id),  # don't expose yourself
        },
    )


@data_router.post("/process/{project_id}")
async def process_file(request: Request, project_id: str, data: DataSchema):

    chunk_size = data.chunk_size or 512
    chunk_overlap = data.overlap_size or 50
    do_reset = data.do_reset

    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )
    project = await project_model.get_project_or_create_one(project_id=project_id)

    # If file_id is given, process that file only, else process all project files
    project_files_id = []

    asset_model = await AssetModel.create_instance(
        db_client=request.app.state.db_client
    )

    if data.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=str(project_id), asset_id=data.file_id
        )
        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "response_signal": ResponseStatus.FILE_ID_ERROR.value,
                },
            )

        project_files_id = [(asset_record.asset_uuid, asset_record.asset_config)]
    else:
        project_files = await asset_model.get_all_project_assets(
            asset_project_id=str(project.project_id), asset_type="application/pdf"
        )
        project_files_id = [
            (record.asset_uuid, record.asset_config) for record in project_files
        ]

    if len(project_files_id) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "response_signal": ResponseStatus.NO_FILES_FOUNDED_TO_PROCESS.value,
            },
        )

    process_controller = ProcessController.ProcessController(project_id=project_id)

    inserted_count = 0
    files_count = 0
    failed_files = []  # so callers/logs can see *why* it was a no-op

    data_chunk_model = await DataChunkModel.create_instance(
        db_client=request.app.state.db_client
    )

    if do_reset == 1:
        _ = await data_chunk_model.delete_chunks_by_project_id(
            project_id=str(project.project_id)
        )

    for asset_uuid, asset_config in project_files_id:
        if not asset_config:
            logger.warning(f"Asset config missing for id: {asset_uuid}")
            failed_files.append(str(asset_uuid))
            continue

        file_path = asset_config.get("file_path")
        file_id = asset_config.get("file_id", "Not found")

        if not file_path or not os.path.exists(file_path):
            logger.warning(f"File not found on disk: {file_path}")
            failed_files.append(file_id)
            continue

        file_content = process_controller.get_file_content(file_path=file_path)
        if file_content is None:
            logger.warning(f"Could not parse file: {file_path}")
            failed_files.append(file_id)
            continue

        file_chunks = process_controller.get_chunks(
            document=file_content, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        if not file_chunks:
            logger.warning(f"No chunks produced for file: {file_path}")
            failed_files.append(file_id)
            continue

        file_chunks_records = [
            DataChunk(
                chunk_id=None,
                chunk_text=chunk["text"],
                chunk_metadata={
                    **chunk["metadata"],
                    "raw_text": chunk["raw_text"],
                    "original_filename": file_id,
                },
                chunk_order=chunk["metadata"]["chunk_index"] + 1,
                chunk_project_id=project.project_id,
                chunk_asset_id=asset_uuid,
            )
            for chunk in file_chunks
        ]

        inserted_count += await data_chunk_model.insert_many_chunks(
            chunks=file_chunks_records
        )
        files_count += 1

    if files_count == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "response_signal": ResponseStatus.FILE_PROCESSING_FAILED.value,
                "processed_chunks": inserted_count,
                "processed_files_count": files_count,
                "failed_files": failed_files,
            },
        )
    return JSONResponse(
        content={
            "response_signal": ResponseStatus.FILE_PROCESSED_SUCCESSFULLY.value,
            "processed_chunks": inserted_count,
            "processed_files_count": files_count,
        }
    )
