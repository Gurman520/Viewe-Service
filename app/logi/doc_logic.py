from re import sub
from markdown import markdown
from typing import Optional
from frontmatter import load
from app.puty import Config
from secrets import compare_digest
from pathlib import Path
from app.log.logger import logger
from collections import Counter
import os
from app.db.process import get_documents_by_type, get_document_by_filename


DEFAULT_GROUP = "Без группы"  # Группа по умолчанию
DEFAULT_SUBGROUP = ""
DEFAULT_TYPE = "ALL"


def load_document_without_password(file_path: Path):
    """Удаление пароля из метаданных"""
    with open(file_path, 'r', encoding='utf-8') as f:
        post = load(f)
        logger.info("APP - Очистка пароля из методанных")
        # Создаем копию метаданных без пароля
        clean_metadata = {k: v for k, v in post.metadata.items() if k != 'password'}
        post.metadata = clean_metadata
        return post

def check_password(credentials: dict, correct_password: str):
    """Функция проверки корректности пароля"""
    logger.info("APP - Проверка пароля")
    is_correct_password = compare_digest(credentials['password'], correct_password)
    return  is_correct_password

def get_document_list(search_query: Optional[str] = None, type: str = "") -> dict[str, list[dict]]:
    """Возвращает документы сгруппированные по категориям"""
    document = get_documents_by_type(search_query = search_query, doc_type=type)
    logger.info("APP - Получен список документов для отображения в списке")
    return document

def process_wiki_links(content: str, doc_type: str) -> str:
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
            if file_path.suffix.lower() != '.mp4':
                return f'<a href="/files/{filename}" class="file-link" download>{filename}</a>'
            return f'<a href="/files/{filename}" class="file-link" download>{filename}</a>' + f'''
        <div class="video-container">
            <video  controls>
              <source src="/files/{filename}" type="video/mp4">
            </video>
        </div>
        '''
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
        r'(?<!`)!\[\[([^\]\n]+)\]\]',
        replace_match,
        content
    )

    def replace_wiki_link(match, doc_type):
        """Подготавливает ссылки на связанные документы"""
        doc_name = match.group(1)
        doc = get_document_by_filename(doc_name)
        hash = "not_found_doc"
        if doc:
            hash = doc['content_hash']
        return f'<a href="/view/{hash}?type_d={doc_type}" class="wiki-link">{doc_name}</a>'
    
    # Регулярка для поиска [[Имя Документа]]
    content = sub(
        r'(?<!`!)\[\[([^\]\n]+)\]\]', 
        lambda match: replace_wiki_link(match, doc_type),  
        content
    )

    logger.info("APP - Подготовка ссылок завершена")
    return content

def render_markdown(content: str, doc_type: str = "") -> str:
    """Преобразовать markdown в HTML"""
    # Сначала обрабатываем вики-синтаксис изображений
    processed_content = process_wiki_links(content, doc_type)
    
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
        logger.info(f"APP - Дирректория '{directory_path}' существует.")
        return True
    
    logger.info(f"APP - Дирректория '{directory_path}' отсутствует.")
    return False

def get_subgroup_list() -> list:
    """Возвращает список подгруп из всех документов"""
    sub = list()
    
    for md_file in Config.DOCUMENTS_DIR.glob("*.md"):
        with open(md_file, "r", encoding="utf-8") as f:
            post = load(f)

            # Получение группы
            group = post.get("subgroup", DEFAULT_SUBGROUP)
            if not group or group.strip() == "":
                group = DEFAULT_GROUP

            sub.append(group)

    counter = Counter(sub)
    filtered_data = {key for key, count in counter.items() if count >= 3}
    filtered_data = list(filtered_data)
    if 'Без группы' in filtered_data:
        filtered_data.remove('Без группы')
    logger.info(f'APP - Сформирован список подгрупп')
    Config.set_list(filtered_data)
