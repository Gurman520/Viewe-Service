import sqlite3


def init_database(db_path: str = "documents.db"):
    """Инициализация базы данных с новыми полями"""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE,
                title TEXT,
                author TEXT,
                tags TEXT,
                group_name TEXT,
                subgroup TEXT,
                description TEXT,
                password TEXT,
                hide BOOLEAN DEFAULT FALSE,
                type TEXT DEFAULT 'adm',
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                content_hash TEXT,
                is_deleted BOOLEAN DEFAULT FALSE,
                last_sync TIMESTAMP
            )
        ''')
        conn.commit()
        