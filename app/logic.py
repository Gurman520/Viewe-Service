from re import sub
from markdown import markdown
from typing import Optional
from frontmatter import load
from app.puty import DOCUMENTS_DIR, IMAGES_DIR, ALLOWED_FILE_EXTENSIONS
from secrets import compare_digest
from fastapi.security import HTTPBasicCredentials
from pathlib import Path
from app.logger import logger


DEFAULT_GROUP = "Без группы"  # Группа по умолчанию


def load_document_without_password(file_path: Path):
    """Загружает документ, удаляя пароль из метаданных"""
    with open(file_path, 'r', encoding='utf-8') as f:
        post = load(f)
        # Создаем копию метаданных без пароля
        clean_metadata = {k: v for k, v in post.metadata.items() if k != 'password'}
        post.metadata = clean_metadata
        return post

def check_password(credentials: HTTPBasicCredentials, correct_password: str):
    is_correct_password = compare_digest(credentials.password, correct_password)
    return  is_correct_password

def get_document_list(search_query: Optional[str] = None) -> dict[str, list[dict]]:
    """Возвращает документы сгруппированные по категориям"""
    documents = dict()
    
    for md_file in DOCUMENTS_DIR.glob("*.md"):
        with open(md_file, "r", encoding="utf-8") as f:
            post = load(f)

            # Безопасное получение группы
            group = post.get("group", DEFAULT_GROUP)
            if not group or group.strip() == "":
                group = DEFAULT_GROUP
            
            doc_data = {
                "file_name": md_file.stem,
                "title": post.get("title", md_file.stem),
                "description": post.get("description", ""),
                "group": group  # Добавляем группу
            }
            logger.info("Получил такое: " + str(doc_data))

            if doc_data["group"] not in documents.keys():
                documents[doc_data["group"]] = list()

            if search_query:
                search_lower = search_query.lower()
                if (search_lower in doc_data["title"].lower() or
                    search_lower in doc_data["description"].lower()):
                    documents[doc_data["group"]].append(doc_data)
            else:
                documents[doc_data["group"]].append(doc_data)
    
    # Сортируем группы и документы внутри групп
    sorted_groups = {}
    for group in sorted(documents.keys()):
        sorted_groups[group] = sorted(documents[group], key=lambda x: x["title"])
    
    return sorted_groups

# def get_document_list(search_query: Optional[str] = None):
#     """Получить список всех markdown-документов с возможностью поиска"""
#     documents = []
#     for md_file in DOCUMENTS_DIR.glob("*.md"):
#         with open(md_file, "r", encoding="utf-8") as f:
#             post = load(f)
#             doc_data = {
#                 "file_name": md_file.stem,
#                 "title": post.get("title", md_file.stem),
#                 "description": post.get("description", ""),
#                 "content": post.content  # Для поиска по содержимому
#             }
            
#             # Если есть поисковый запрос, проверяем соответствие
#             if search_query:
#                 search_lower = search_query.lower()
#                 if (search_lower in doc_data["title"].lower() or
#                     search_lower in doc_data["description"].lower() or 
#                     search_lower in doc_data["content"].lower() ):
#                     documents.append(doc_data)
#             else:
#                 documents.append(doc_data)
    
#     return sorted(documents, key=lambda x: x["title"])


def process_wiki_links(content: str) -> str:
    """Обрабатывает вики-синтаксис ссылок ![[filename.ext]]"""

    def replace_match(match):
        """Подготовливает ссылки на скачивание файлов"""
        filename = match.group(1)
        file_path = IMAGES_DIR / filename
        
        # Если файл существует и его расширение разрешено
        if file_path.exists() and file_path.suffix.lower() in ALLOWED_FILE_EXTENSIONS:
            return f'<a href="/files/{filename}" class="file-link" download>{filename}</a>'
        # Если это изображение
        elif (IMAGES_DIR / filename).exists():
            return f'<img src="/images/{filename}" alt="{filename}" class="wiki-image">'
        # Если файл не найден
        else:
            return f'<span class="text-danger">[File not found: {filename}]</span>'
    
    content = sub(
        r'!\[\[([^\]\n]+)\]\]',
        replace_match,
        content
    )

    def replace_wiki_link(match):
        """Подготавливает ссылки на связанные документы"""
        doc_name = match.group(1)
        # Экранируем специальные символы в URL
        encoded_name = doc_name.replace(' ', '_')
        return f'<a href="/api/document/doc/{encoded_name}" class="wiki-link">{doc_name}</a>'
    
    # Регулярка для поиска [[Имя Документа]]
    content = sub(r'\[\[([^\]\n]+)\]\]', replace_wiki_link, content)

    return content

def render_markdown(content: str) -> str:
    """Преобразовать markdown в HTML"""
    # Сначала обрабатываем вики-синтаксис изображений
    processed_content = process_wiki_links(content)
    
    extensions = [
        "fenced_code",
        "codehilite",
        "tables",
        "footnotes",
        "toc",
    ]
    return markdown(processed_content, extensions=extensions)
