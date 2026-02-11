from helpers.config import Settings, get_settings
import os
import random
import string
class BaseController:
    def __init__(self):
        self.settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__)) # Get the directory of the current file
        self.file_path = os.path.join(self.base_dir, "assets/files") # Define the path to the files directory

    def generate_random_strings(self, length: int = 8):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    