import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.log.logger import logger


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
            logger.info(f"Добавлен документ: {file_path}")
    except Exception as e:
        logger.error(f"Ошибка при добавлении документа {file_path}: {e}")

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
            logger.info(f"Обновлен документ: {file_path}")
    except Exception as e:
        logger.error(f"Ошибка при обновлении документа {file_path}: {e}")

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
            logger.info(f"Помечен как удаленный: {file_path}")
    except Exception as e:
        logger.error(f"Ошибка при пометке документа как удаленного {file_path}: {e}")

def get_all_db_files(db_path: str) -> List[str]:
    """Получение всех файлов из базы данных"""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM documents WHERE is_deleted = FALSE")
        return [row[0] for row in cursor.fetchall()]
    
def get_documents_by_type(search_query: Optional[str] = None, db_path: str = "content.db", doc_type: str = None) -> List[Dict]:
    """
    Получает документы с возможностью фильтрации по типу
    
    Args:
        db_path: Путь к базе данных
        doc_type: Тип документа ('doctor', 'adm' и т.д.). Если None - все документы
        
    Returns:
        Список документов с фильтрацией по типу
    """
    documents = dict()
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if doc_type and doc_type != 'adm':
                query = '''
                    SELECT file_path, title, content_hash, group_name, subgroup, description
                    FROM documents 
                    WHERE is_deleted = FALSE AND hide = FALSE AND type = ?
                    ORDER BY group_name, subgroup
                '''
                cursor.execute(query, (doc_type,))
            else:
                query = '''
                    SELECT file_path, title, content_hash, group_name, subgroup, description
                    FROM documents 
                    WHERE is_deleted = FALSE AND hide = FALSE
                    ORDER BY group_name, subgroup
                '''
                cursor.execute(query)
            
            results = []
            for row in cursor.fetchall():
                doc_data = {
                    "file_name": Path(row['file_path']).stem,
                    'title': row['title'],
                    'content_hash': row['content_hash'],
                    'group': row['group_name'],
                    'subgroup': row['subgroup'],
                    'description': row['description']
                }

                if doc_data["group"] not in documents.keys():
                    documents[doc_data["group"]] = list()

                if search_query:
                    search_lower = search_query.lower()
                    if (search_lower in doc_data["title"].lower() or
                        search_lower in doc_data["description"].lower() or
                        search_lower in doc_data["subgroup"].lower()):
                        documents[doc_data["group"]].append(doc_data)
                    elif len(documents[doc_data["group"]]) < 1:
                        del documents[doc_data["group"]]
                else:
                    documents[doc_data["group"]].append(doc_data)

            sorted_groups = {}
            for group in sorted(documents.keys()):
                sorted_groups[group] = sorted(documents[group], key=lambda x: x["title"])
            
            return sorted_groups
            
    except Exception as e:
        print(f"Ошибка при получении документов: {e}")
        return []
    
def get_document_by_hash(content_hash: str, db_path: str = "content.db") -> Optional[Dict]:
    """
    Находит документ по хешу содержимого
    
    Args:
        db_path: Путь к базе данных
        content_hash: Хеш для поиска
        
    Returns:
        Данные документа или None если не найден
    """
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    file_path,
                    title,
                    password,
                    content_hash,
                    group_name,
                    subgroup,
                    description
                FROM documents 
                WHERE is_deleted = FALSE AND content_hash = ?
            ''', (content_hash,))
            
            row = cursor.fetchone()

            if row:
                logger.info("Получен результат из БД")
                return {
                    'file_path': Path(row['file_path']).name,
                    'title': row['title'],
                    'password': row['password'],
                    'content_hash': row['content_hash'],
                    'group': row['group_name'],
                    'subgroup': row['subgroup'],
                    'description': row['description']
                }
            return None
            
    except Exception as e:
        logger.error(f"Ошибка при поиске документа по хешу: {e}")
        return None

def get_document_by_filename(filename: str, db_path: str = "content.db") -> Optional[Dict]:
    """
    Находит один документ по имени файла
    
    Args:
        db_path: Путь к базе данных
        filename: Имя файла для поиска (например: "document.md")
        
    Returns:
        Данные документа или None если не найден
    """
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    file_path,
                    content_hash,
                    group_name,
                    subgroup,
                    description,
                    title,
                    author,
                    password,
                    hide,
                    type,
                    created_at,
                    updated_at
                FROM documents 
                WHERE is_deleted = FALSE AND LOWER(title) LIKE LOWER(?)
            ''', (f'%{filename}%',))
            
            row = cursor.fetchone()
            if row:
                return {
                    'file_path': row['file_path'],
                    'file_name': Path(row['file_path']).name,
                    'content_hash': row['content_hash'],
                    'group': row['group_name'],
                    'subgroup': row['subgroup'],
                    'description': row['description'],
                    'title': row['title'],
                    'author': row['author'],
                    'password': row['password'],
                    'hide': bool(row['hide']),
                    'type': row['type'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return None
            
    except Exception as e:
        print(f"Ошибка при поиске документа по имени файла '{filename}': {e}")
        return None
