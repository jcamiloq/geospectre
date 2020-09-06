import os
from os import path

class FileManagement():
    @staticmethod
    def to_relative(route: str, script_dir: str = ""):
        file_dir = route.replace("/", '\\')
        if script_dir == "":
            script_dir = os.path.dirname(__file__)
        return os.path.join(script_dir + file_dir)

    
