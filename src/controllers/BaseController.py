import os
import random
import string

from src.helpers.config import get_settings


class BaseController:
    def __init__(self):
        self.settings = get_settings()
        self.base_dir = os.path.dirname(
            os.path.dirname(__file__)
        )  # Get the directory of the current file
        self.file_path = os.path.join(
            self.base_dir, "assets/files"
        )  # Define the path to the files directory
        self.database_dir = os.path.join(self.base_dir, "assets/databases")

    def generate_random_strings(self, length: int = 8):
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    def get_database_path(self, db_name: str):
        database_path = os.path.join(self.database_dir, db_name)
        if not os.path.exists(database_path):
            os.makedirs(database_path)
        return database_path
