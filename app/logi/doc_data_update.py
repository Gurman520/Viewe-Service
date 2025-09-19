from app.db.init import init_database
from pathlib import Path
from app.log.logger import logger
from typing import List, Dict
from datetime import datetime, timedelta
import frontmatter
import hashlib
import sqlite3
from app.puty import Config
from app.db.process import file_exists_in_db, update_document, insert_document


def calculate_hash(file_path: Path) -> str:
    """Вычисление хеша содержимого файла"""
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        return file_hash.hexdigest()
    except Exception as e:
        logger.error(f"APP | DOC_UPADTE - Ошибка при вычислении хеша {file_path}: {e}")
        return ""
    
def get_all_md_files(documents_dir: Path) -> List[Path]:
    """Получение всех .md файлов в директории и поддиректориях"""
    return list(documents_dir.rglob("*.md"))

def extract_metadata(file_path: Path) -> Dict:
    """Извлечение метаданных из markdown файла с новыми полями"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # Обработка новых полей
        group = post.metadata.get('group')
        subgroup = post.metadata.get('subgroup')
        description = post.metadata.get('description')
        password = post.metadata.get('password')
        hide = post.metadata.get('hide')
        doc_type = post.metadata.get('type')
        
        metadata = {
            'title': post.metadata.get('title', file_path.stem),
            'author': post.metadata.get('author', 'Unknown'),
            'tags': ','.join(post.metadata.get('tags', [])),
            'created_at': post.metadata.get('date', datetime.now()),
            'content_hash': calculate_hash(file_path),
            'group': group if group is not None else 'Без группы',
            'subgroup': subgroup if subgroup is not None else '',
            'description': description if description is not None else '',
            'password': password,  # Может быть None
            'hide': bool(hide) if hide is not None else False,
            'type': doc_type if doc_type is not None else 'adm'
        }
        return metadata
    except Exception as e:
        logger.error(f"APP | DOC_UPADTE - Ошибка при чтении файла {file_path}: {e}")
        return {}

def process_first_run(documents_dir: Path, db_path: str = "documents.db"):
    """Первый запуск - обработка всех документов"""
    logger.info("APP | DOC_UPADTE - Получение документов при первом запуске")
    init_database(db_path)
    
    md_files = get_all_md_files(documents_dir)
    logger.info(f"APP | DOC_UPADTE - Найдено {len(md_files)} .md файлов")
    
    for md_file in md_files:
        metadata = extract_metadata(md_file)
        if metadata:
            if file_exists_in_db(db_path, str(md_file)):
                update_document(db_path, md_file, metadata)
            else:
                insert_document(db_path, md_file, metadata)
    
    logger.info("APP | DOC_UPADTE - получение документов при первом запуске завершилось успешно")


def get_recently_modified_files(documents_dir: Path, minutes: int = 10) -> List[Path]:
    """Получение файлов, измененных за последние N минут"""
    cutoff_time = datetime.now() - timedelta(minutes=minutes)
    recent_files = []
    
    for md_file in get_all_md_files(documents_dir):
        if md_file.is_file():
            mod_time = datetime.fromtimestamp(md_file.stat().st_mtime)
            if mod_time > cutoff_time:
                recent_files.append(md_file)
    
    return recent_files

def file_exists_in_db(db_path: str, file_path: str) -> bool:
    """Проверка существования файла в базе данных"""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM documents WHERE file_path = ? AND is_deleted = FALSE",
            (str(file_path),)
        )
        return cursor.fetchone()[0] > 0

def insert_document(db_path: str, file_path: Path, metadata: Dict):
    """Вставка нового документа в базу данных с новыми полями"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO documents 
                (file_path, title, author, tags, group_name, subgroup, description, 
                 password, hide, type, created_at, updated_at, content_hash, last_sync)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(file_path),
                metadata['title'],
                metadata['author'],
                metadata['tags'],
                metadata['group'],
                metadata['subgroup'],
                metadata['description'],
                metadata['password'],
                metadata['hide'],
                metadata['type'],
                metadata['created_at'],
                datetime.now(),
                metadata['content_hash'],
                datetime.now()
            ))
            conn.commit()
            logger.info(f"APP | DOC_UPADTE - Добавлен документ: {file_path}")
    except Exception as e:
        logger.error(f"APP | DOC_UPADTE - Ошибка при добавлении документа {file_path}: {e}")

def update_document(db_path: str, file_path: Path, metadata: Dict):
    """Обновление существующего документа с новыми полями"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE documents 
                SET title = ?, author = ?, tags = ?, group_name = ?, subgroup = ?,
                    description = ?, password = ?, hide = ?, type = ?, updated_at = ?, 
                    content_hash = ?, last_sync = ?, is_deleted = FALSE
                WHERE file_path = ?
            ''', (
                metadata['title'],
                metadata['author'],
                metadata['tags'],
                metadata['group'],
                metadata['subgroup'],
                metadata['description'],
                metadata['password'],
                metadata['hide'],
                metadata['type'],
                datetime.now(),
                metadata['content_hash'],
                datetime.now(),
                str(file_path)
            ))
            conn.commit()
            logger.info(f"APP | DOC_UPADTE - Обновлен документ: {file_path}")
    except Exception as e:
        logger.error(f"APP | DOC_UPADTE - Ошибка при обновлении документа {file_path}: {e}")

def mark_as_deleted(db_path: str, file_path: str):
    """Пометка документа как удаленного"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE documents 
                SET is_deleted = TRUE, updated_at = ?, last_sync = ?
                WHERE file_path = ?
            ''', (datetime.now(), datetime.now(), file_path))
            conn.commit()
            logger.info(f"APP | DOC_UPADTE - Помечен как удаленный: {file_path}")
    except Exception as e:
        logger.error(f"APP | DOC_UPADTE - Ошибка при пометке документа как удаленного {file_path}: {e}")

def get_all_db_files(db_path: str) -> List[str]:
    """Получение всех файлов из базы данных"""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM documents WHERE is_deleted = FALSE")
        return [row[0] for row in cursor.fetchall()]
    
def process_subsequent_run(documents_dir: Path = Config.DOCUMENTS_DIR, db_path: str = Config.DB_PATH, minutes: int = 10):
    """Повторный запуск - обработка измененных документов"""
    logger.info("APP | DOC_UPADTE - Переодическая проверка обновлений по документам")
    init_database(db_path)
    
    # Обработка измененных файлов
    recent_files = get_recently_modified_files(documents_dir, minutes)
    logger.info(f"APP | DOC_UPADTE - Найдено {len(recent_files)} измененных файлов за последние {minutes} минут")
    
    for md_file in recent_files:
        metadata = extract_metadata(md_file)
        if metadata:
            if file_exists_in_db(db_path, str(md_file)):
                update_document(db_path, md_file, metadata)
            else:
                insert_document(db_path, md_file, metadata)
    
    # Проверка удаленных файлов
    db_files = get_all_db_files(db_path)
    for db_file in db_files:
        if not Path(db_file).exists():
            mark_as_deleted(db_path, db_file)
    
    logger.info("APP | DOC_UPADTE - переодическое обновление данных завершено")
