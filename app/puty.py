from pathlib import Path


# Настройка путей
BASE_DIR = Path(__file__).parent
CONTENT_DIR = Path("T:\\Sulima\\work-house")
DOCUMENTS_DIR = CONTENT_DIR / "База знаний"
IMAGES_DIR = CONTENT_DIR / "Вложения"

# Разрешенные расширения файлов
ALLOWED_FILE_EXTENSIONS = {
    '.txt', '.bat', '.sh', '.csv', '.json', '.exe',
    '.xml', '.pdf', '.doc', '.docx', '.xls', '.xlsx'
}