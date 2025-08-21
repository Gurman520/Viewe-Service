import os
import zipfile
from datetime import datetime


def create_backup_zip(source_folder, target_disk, zip_name=None):
    """
    Создаёт ZIP-архив из всех файлов в source_folder и сохраняет его на target_disk.
    :param source_folder: Путь к папке с файлами для архивирования
    :param target_disk: Буква диска (например, "D:") или путь для сохранения архива
    :param zip_name: Имя ZIP-архива (если None, будет использована дата)
    """
    # Проверяем, существует ли исходная папка
    if not os.path.exists(source_folder):
        print(f"Ошибка: Папка {source_folder} не существует!")
        return
    
    # Создаём имя архива, если не указано
    if zip_name is None:
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
        
        print(f"Архив успешно создан: {zip_path}")
        print(f"Размер архива: {os.path.getsize(zip_path) / (1024*1024):.2f} MB")
    except Exception as e:
        print(f"Ошибка при создании архива: {e}")


if __name__ == "__main__":
    # Укажите путь к папке, которую нужно заархивировать
    source_folder = "T:\\work-house"
    
    # Укажите диск или путь для сохранения архива
    target_disk = "D:\\Backups"
    
    # Можно указать имя архива
    # zip_name = "project_backup.zip"
    
    create_backup_zip(source_folder, target_disk)
