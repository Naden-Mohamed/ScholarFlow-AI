from .BaseController import BaseController
from .ProjectController import ProjectController
import os

class ProcessController(BaseController):
    def __init__(self,project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=self.project_id)

    def get_file_extension(self, file_path: str):
        return os.path.splitext(file_path)[-1].lower()
