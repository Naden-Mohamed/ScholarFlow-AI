import re
from .BaseController import BaseController
from fastapi import UploadFile
from src.models.Enums.ResponseEnum import ResponseStatus
import os
from src.controllers.ProjectController import ProjectController

class DataController(BaseController):
    def __init__(self):
        super().__init__()

    def validate_uploaded_file(self, file: UploadFile):
        if file.content_type not in self.settings.FILE_ALLOWED_TYPES:
            return False, ResponseStatus.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.settings.FILE_MAX_SIZE_MB * 1024 * 1024:
            return False, ResponseStatus.FILE_SIZE_EXCEEDED.value

        return True, ResponseStatus.FILE_VALIDATED_SUCCESSFULLY.value

    def generate_unique_filename(self, original_filename: str, project_id: str = None):
        random_filename = self.generate_random_strings()
        project_path = ProjectController().get_project_path(project_id=project_id)
        cleaned_filename = self.get_clean_file_name(original_filename)
        unique_filename = os.path.join(project_path, f"{random_filename}_{cleaned_filename}")

        while os.path.exists(unique_filename):
            random_filename = self.generate_random_strings()
            unique_filename = os.path.join(project_path, f"{random_filename}_{cleaned_filename}")

        return unique_filename, f"{random_filename}_{cleaned_filename}"



    def get_clean_file_name(self, orig_file_name: str):

        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name