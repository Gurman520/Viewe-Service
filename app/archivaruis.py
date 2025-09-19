import os
import zipfile
from datetime import datetime
from app.puty import Config
from app.log.logger import logger


def create_backup_zip():
    """
    Создаёт ZIP-архив из всех файлов в source_folder и сохраняет его на target_disk.
    """
    source_folder = Config.CONTENT_DIR
    target_disk = Config.TARGET_DISK

    # Проверяем, существует ли исходная папка
    if not os.path.exists(source_folder):
        print(f"Ошибка: Папка {source_folder} не существует!")
        return
    
    # Создаём имя архива, если не указано
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_name = f"backup_{current_time}.zip"
    
    # Формируем полный путь для сохранения архива
    zip_path = os.path.join(target_disk, zip_name)
    
    # Создаём ZIP-архив
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_LZMA) as zipf:
            for root, dirs, files in os.walk(source_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Добавляем файл в архив, сохраняя относительный путь
                    arcname = os.path.relpath(file_path, start=source_folder)
                    zipf.write(file_path, arcname)
        
        logger.info(f"Архив успешно создан: {zip_path}")
        logger.info(f"Размер архива: {os.path.getsize(zip_path) / (1024*1024):.2f} MB")
    except Exception as e:
        logger.error(f"Ошибка при создании архива: {e}")