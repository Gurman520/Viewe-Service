from re import sub
from markdown import markdown
from typing import Optional
from frontmatter import load
from app.puty import Config
from secrets import compare_digest
from fastapi.security import HTTPBasicCredentials
from pathlib import Path
from app.logger import logger
import os


DEFAULT_GROUP = "Без группы"  # Группа по умолчанию


def load_document_without_password(file_path: Path):
    """Удаление пароля из метаданных"""
    with open(file_path, 'r', encoding='utf-8') as f:
        post = load(f)
        logger.info("Очистка пароля из методанных")
        # Создаем копию метаданных без пароля
        clean_metadata = {k: v for k, v in post.metadata.items() if k != 'password'}
        post.metadata = clean_metadata
        return post

def check_password(credentials: HTTPBasicCredentials, correct_password: str):
    """Функция проверки корректности пароля"""
    logger.info("Проверка пароля")
    is_correct_password = compare_digest(credentials.password, correct_password)
    return  is_correct_password

def get_document_list(search_query: Optional[str] = None) -> dict[str, list[dict]]:
    """Возвращает документы сгруппированные по категориям"""
    documents = dict()
    
    for md_file in Config.DOCUMENTS_DIR.glob("*.md"):
        with open(md_file, "r", encoding="utf-8") as f:
            post = load(f)

            # Получение группы
            group = post.get("group", DEFAULT_GROUP)
            if not group or group.strip() == "":
                group = DEFAULT_GROUP

            # Получение факта скрытности
            hide = post.get("hide", "")
            if hide.strip() == "True":
                continue
            
            doc_data = {
                "file_name": md_file.stem,
                "title": post.get("title", md_file.stem),
                "description": post.get("description", ""),
                "group": group  # Добавляем группу
            }

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
    logger.info("Подготовлен список документов")
    return sorted_groups

def process_wiki_links(content: str) -> str:
    """Обрабатывает вики-синтаксис ссылок ![[filename.ext]]"""

    def replace_match(match):
        """Подготовливает ссылки на скачивание файлов"""
        text = match.group(1)
        text = text.split('|')
        filename = text[0].strip()
        l = ''
        if len(text) > 1:
            l = text[1].strip()
        file_path = Config.IMAGES_DIR / filename
        
        # Если файл существует и его расширение разрешено
        if file_path.exists() and file_path.suffix.lower() in Config.ALLOWED_FILE_EXTENSIONS:
            return f'<a href="/files/{filename}" class="file-link" download>{filename}</a>'
        # Если это изображение
        elif (Config.IMAGES_DIR / filename).exists():
            if l == 'L':
                return f'<br> <img src="/images/{filename}" alt="{filename}" class="wiki-image-left"> <br>'
            else:
                return f'<br> <img src="/images/{filename}" alt="{filename}" class="wiki-image"> <br>'
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
        return f'<br/> <a href="/view/{encoded_name}" class="wiki-link">{doc_name}</a>'
    
    # Регулярка для поиска [[Имя Документа]]
    content = sub(r'\[\[([^\]\n]+)\]\]', replace_wiki_link, content)

    logger.info("Подготовка ссылок завершена")
    return content

def render_markdown(content: str) -> str:
    """Преобразовать markdown в HTML"""
    # Сначала обрабатываем вики-синтаксис изображений
    processed_content = process_wiki_links(content)
    
    extensions = [
        "fenced_code",
        "nl2br",
        "pymdownx.tasklist",
        "codehilite",
        "tables",
        "footnotes",
        "toc",
        "extra",
        "pymdownx.mark",
    ]
    return markdown(processed_content, extensions=extensions)

def check_doc(directory_path = Config.DOCUMENTS_DIR) -> bool:
    """Проверка существования Директории"""
    if os.path.exists(directory_path):
        logger.info(f"Дирректория '{directory_path}' существует.")
        return True
    
    logger.info(f"Дирректория '{directory_path}' отсутствует.")
    return False
