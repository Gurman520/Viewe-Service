from fastapi import APIRouter, Request, Form, HTTPException, status, Cookie
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from frontmatter import load
from re import finditer, findall
from zipfile import ZipFile
from typing import Optional
from tempfile import NamedTemporaryFile
from pathlib import Path
from app.puty import Config
from app.logic import get_document_list, render_markdown, load_document_without_password
from app.security import get_document_name_from_token
from app.logger import logger
from app.logi.document import get_document, get_isolated_document


router = APIRouter()

# Шаблоны
templates = Jinja2Templates(directory="app/templates")


@router.get("/list")
async def list_documents(request: Request, q: Optional[str] = None, type: str = None):
    """Страница со списком всех документов с поиском"""
    logger.info("Получен запрос на получение Списка документов")
    documents = get_document_list(search_query=q, type=type)
    logger.info("Отправлен запрос на получение Списка документов")
    return JSONResponse(content={"document": documents}, status_code=200)

@router.get("/d/{doc_id}", name="document_short_link")
async def document_short_link(doc_id: str, request: Request):
    """Короткая ссылка на документ"""
    original_name = doc_id.replace('_', ' ')
    md_file = Config.DOCUMENTS_DIR / f"{original_name}.md"
    
    if not md_file.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    return RedirectResponse(url=request.url_for("view_document", document_name=doc_id))

@router.post("/search", name="search_documents")
async def search_documents(request: Request, search_query: str = Form(...), type: str = ""):
    """Обработка поискового запроса из формы"""
    documents = get_document_list(search_query=search_query, type=type)
    logger.info(f"Получен список при поиске: {documents}")
    return templates.TemplateResponse(
        "list.html",
        {"request": request, "documents": documents, "search_query": search_query, "subgroup": Config.subgroup_list, "type": type}
    )
    
@router.get("/{document_name}/download", name="download_document_with_assets")
async def download_document_with_assets(document_name: str):
    """Скачивание документа со всеми вложениями в ZIP-архиве"""
    original_name = document_name.replace('_', ' ')
    md_file = Config.DOCUMENTS_DIR / f"{original_name}.md"
    logger.info("Пытаемся скачать файл: |" + str(md_file))
    
    if not md_file.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Создаем временный ZIP-архив
    with NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
        zip_path = tmp_zip.name
    
    try:
        with ZipFile(zip_path, 'w') as zipf:
            # Добавляем основной MD-файл
            zipf.write(md_file, arcname=f"{document_name}.md")
            
            # Читаем MD-файл чтобы найти все вложения
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Ищем все вложения в формате ![[filename]]
                attachments = findall(r'!\[\[([^\]\n]+)\]\]', content)
                
                # Добавляем найденные файлы
                for filename in attachments:
                    # Проверяем существование файла в images или files
                    if (Config.IMAGES_DIR / filename).exists():
                        zipf.write(Config.IMAGES_DIR / filename, arcname=f"images/{filename}")
        
        # Используем FileResponse в режиме потоковой передачи
        response = FileResponse(
            zip_path,
            filename=f"{document_name}_with_assets.zip",
            media_type="application/zip"
        )

        lambda: Path(zip_path).unlink() if Path(zip_path).exists() else None
        return response
        
    except Exception as e:
        # Удаляем временный файл в случае ошибки
        if Path(zip_path).exists():
            Path(zip_path).unlink()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/download/{filename:path}", name="download_file")
async def download_file(filename: str):
    """Скачивание файла"""
    file_path = Config.IMAGES_DIR / filename

    # Проверка безопасности
    if ".." in filename or not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if file_path.suffix.lower() not in Config.ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(status_code=403, detail="File type not allowed")
    
    return FileResponse(
        file_path,
        filename=filename,
        media_type="application/octet-stream"
    )

@router.get("/isolated_view/{hash}")
async def create_isolated_view(request: Request, hash: str):
    """Изолированный просмотр документа без навигации"""

    logger.info("Запрошен файл по hash: " + hash)

    d = get_isolated_document(hash=hash)
    
    return d

@router.get("/{hash}")
async def document_route(
    request: Request,
    hash: str,
    doc_session: str = Cookie(default=None)
):
    logger.info("Запрошен файл по hash: " + hash)

    d = await get_document(hash=hash, doc_session=doc_session)
    logger.info(f"Получен d - {d}")
    
    return d
