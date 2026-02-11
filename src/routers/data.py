from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from controllers.DataController import DataController
from controllers.ProjectController import ProjectController
from controllers.ProcessController import ProcessController
from helpers.config import Settings, get_settings
import os 
import aiofiles
from models.Enums.ResponseEnum import ResponseEnum
import logging
from .schemas.data_schema import ProcessRequest

logger = logging.getLogger('uvicorn.error')


data_router = APIRouter(   
    prefix="/data",
    tags=["data"]
)

@data_router.post("/upload/{project_id}")
async def upload_file(project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):

    data_controller = DataController()
    is_valid, error_message = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": error_message})

    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path, file_id = data_controller.generate_unique_filename(original_filename=file.filename, project_id=project_id)

    try:
        
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error uploading file: {e}") # Log the error for debugging purposes & do not expose internal error details to the client

        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": ResponseEnum.FILE_UPLOAD_FAILED.value})

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": ResponseEnum.FILE_UPLOADED_SUCCESSFULLY.value, "file_path": file_path, "file_id": file_id})

@data_router.post("/process/{project_id}")
async def process_file(project_id: str, request: ProcessRequest):
    file_id = request.file_id
    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id=file_id)
    chunks = process_controller.process_file_content(file_content = file_content,file_id=file_id, chunk_size=request.chunk_size, overlap_size=request.overlap_size)

    if not chunks or len(chunks) == 0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": ResponseEnum.FILE_PROCESSING_FAILED.value})

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": ResponseEnum.FILE_PROCESSED_SUCCESSFULLY.value, "chunks": [chunk.page_content for chunk in chunks]})