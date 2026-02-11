from .BaseController import BaseController
from fastapi import UploadFile
from models.Enums.ResponseEnum import ResponseEnum
import os 

class ProjectController(BaseController):
    def __init__(self):
        super().__init__()

    def get_project_path(self, project_id: str):
        project_path = os.path.join(self.file_path, project_id)
        if not os.path.exists(project_path):
            os.makedirs(project_path)
        return project_path