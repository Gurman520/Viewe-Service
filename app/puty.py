from dotenv import load_dotenv
from pathlib import Path
from os import getenv
from datetime import timedelta
from app.security import ACCESS_TOKEN_EXPIRE_MINUTES


class Conf(object):
    BASE_DIR = Path(__file__).parent
    CONTENT_DIR = ""
    DOCUMENTS_DIR = ""
    IMAGES_DIR = ""
    PORT = ""
    DB_PATH = "content.db"
    ALLOWED_FILE_EXTENSIONS = {
        '.txt', '.bat', '.sh', '.csv', '.json', '.exe',
        '.xml', '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
        '.mp4', '.avi'
    }
    IS_BACKUP = ""
    TARGET_DISK = ""

    SESSION_COOKIE_NAME = "doc_session"
    TOKEN_EXPIRE = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    subgroup_list = list()

    def __init__(self):
        load_dotenv()

        self.CONTENT_DIR = Path(getenv('CONTENT_DIR'))
        self.DOCUMENTS_DIR = self.CONTENT_DIR / getenv('DOCUMENTS_DIR')
        self.IMAGES_DIR = self.CONTENT_DIR / getenv('IMAGES_DIR')
        self.PORT = int(getenv('PORT'))
        self.IS_BACKUP = bool(getenv('IS_BACKUP'))
        self.TARGET_DISK = Path(getenv('TARGET_FOLDER'))

    def set_list(self, new_data: list):
        self.subgroup_list = new_data.copy()


Config = Conf()
