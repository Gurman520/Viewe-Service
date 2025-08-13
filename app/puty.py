from dotenv import load_dotenv
from pathlib import Path
from os import getenv


class Conf(object):
    BASE_DIR = Path(__file__).parent
    CONTENT_DIR = ""
    DOCUMENTS_DIR = ""
    IMAGES_DIR = ""
    PORT = ""
    ALLOWED_FILE_EXTENSIONS = {
        '.txt', '.bat', '.sh', '.csv', '.json', '.exe',
        '.xml', '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
        '.mp4', '.avi'
    }
    subgroup_list = list()

    def __init__(self):
        load_dotenv()

        self.CONTENT_DIR = Path(getenv('CONTENT_DIR'))
        self.DOCUMENTS_DIR = self.CONTENT_DIR / getenv('DOCUMENTS_DIR')
        self.IMAGES_DIR = self.CONTENT_DIR / getenv('IMAGES_DIR')
        self.PORT = int(getenv('PORT'))

    def set_list(self, new_data: list):
        self.subgroup_list = new_data.copy()


Config = Conf()
