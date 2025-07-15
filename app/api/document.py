from fastapi import APIRouter, Request, Form, HTTPException, status, Cookie
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from frontmatter import load
from re import finditer
from zipfile import ZipFile
from typing import Optional
from tempfile import NamedTemporaryFile
from pathlib import Path
from app.puty import DOCUMENTS_DIR, IMAGES_DIR, ALLOWED_FILE_EXTENSIONS
from app.logic import get_document_list, render_markdown, load_document_without_password
from app.security import get_document_name_from_token
from app.logger import logger


router = APIRouter()

# Шаблоны
templates = Jinja2Templates(directory="app/templates")


@router.get("/list", name="document_list")
async def list_documents(request: Request, q: Optional[str] = None):
    """Страница со списком всех документов с поиском"""
    documents = get_document_list(search_query=q)
    logger.info("Отправлен запрос на получение Списка документов")
    return templates.TemplateResponse(
        "list.html",
        {"request": request, "documents": documents, "search_query": q}
    )

@router.get("/d/{doc_id}", name="document_short_link")
async def document_short_link(doc_id: str, request: Request):
    """Короткая ссылка на документ"""
    original_name = doc_id.replace('_', ' ')
    md_file = DOCUMENTS_DIR / f"{original_name}.md"
    
    if not md_file.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    return RedirectResponse(url=request.url_for("view_document", document_name=doc_id))

@router.post("/search", name="search_documents")
async def search_documents(request: Request, search_query: str = Form(...)):
    """Обработка поискового запроса из формы"""
    documents = get_document_list(search_query=search_query)
    return templates.TemplateResponse(
        "list.html",
        {"request": request, "documents": documents, "search_query": search_query}
    )

@router.get("/{document_name}")
async def view_document(
    request: Request,
    document_name: str,
    doc_session: str = Cookie(default=None)
):
    original_name = document_name.replace('_', ' ')
    md_file = DOCUMENTS_DIR / f"{original_name}.md"
    
    if not md_file.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    with open(md_file, "r", encoding="utf-8") as f:
        post = load(f)
        password = post.metadata.get("password")
        # Если документ защищен паролем
        if password:
            try:
                if not doc_session:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not authenticated",
                        headers={"WWW-Authenticate": "Basic"},
                    )
        
                token_doc_name = get_document_name_from_token(doc_session)
                logger.info("Оригинальное название файла:-" + original_name + "- Полученное имя из Токена:-" + str(token_doc_name) + "-")

                if str(token_doc_name) != original_name:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token not valid for this document",
                    )
            except HTTPException:
                logger.info("Не соответсвие файлов, отправляем на повторную авторизацию")
                return templates.TemplateResponse(
                "auth.html",
                {"request": request, "document_name": document_name}
            )
    
    return await get_document_response(md_file, original_name, request)


async def get_document_response(md_file: Path, original_name: str, request):
    """Создает ответ с содержимым документа"""
    post = load_document_without_password(md_file)
    content = render_markdown(post.content)

    attachments = []
    for match in finditer(r'!\[\[([^\]\n]+)\]\]', post.content):
        filename = match.group(1)
        if (IMAGES_DIR / filename).exists() or (IMAGES_DIR / filename).exists():
            attachments.append(filename)
    
    return templates.TemplateResponse(
        "document.html",
        {
            "request": request,
            "title": post.get("title", original_name),
            "content": content,
            "metadata": post.metadata,
            "document_name": original_name.replace(' ', '_'),
            "is_protected": True,
            "original_name": original_name,
            "document_attachments": attachments 
        }
    )
    
@router.get("/{document_name}/download", name="download_document_with_assets")
async def download_document_with_assets(document_name: str):
    """Скачивание документа со всеми вложениями в ZIP-архиве"""
    original_name = document_name.replace('_', ' ')
    md_file = DOCUMENTS_DIR / f"{original_name}.md"
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
                    if (IMAGES_DIR / filename).exists():
                        zipf.write(IMAGES_DIR / filename, arcname=f"images/{filename}")
        
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
    file_path = IMAGES_DIR / filename

    # Проверка безопасности
    if ".." in filename or not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if file_path.suffix.lower() not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(status_code=403, detail="File type not allowed")
    
    return FileResponse(
        file_path,
        filename=filename,
        media_type="application/octet-stream"
    )

@router.get("/view/{document_name}", name="isolated_view")
async def isolated_view(request: Request, document_name: str):
    """Изолированный просмотр документа без навигации"""
    original_name = document_name.replace('_', ' ')
    md_file = DOCUMENTS_DIR / f"{original_name}.md"
    
    if not md_file.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    with open(md_file, "r", encoding="utf-8") as f:
        post = load(f)
        # Загружаем документ, очищая пароль
        post = load_document_without_password(md_file)
        content = render_markdown(post.content)
        
        return templates.TemplateResponse(
            "isolated.html",  # Новый шаблон для изолированного просмотра
            {
                "request": request,
                "title": post.get("title", original_name),
                "content": content,
                "metadata": post.metadata,
                "document_name": document_name
            }
        )

@router.get("/doc/{document_name}", name="view_document")
async def document_router(
    request: Request,
    document_name: str,
    doc_session: str = Cookie(default=None)
):
    logger.info("Запрошен файл: " + document_name)
    original_name = document_name.replace('_', ' ')
    md_file = DOCUMENTS_DIR / f"{original_name}.md"
    
    if not md_file.exists():
        logger.info("Запрошенный файл - " + document_name + " не найден")
        raise HTTPException(status_code=404, detail="Document not found")

    with open(md_file, "r", encoding="utf-8") as f:
        post = load(f)
        password = post.metadata.get("password")
        # Если документ защищен паролем
        if password and not doc_session:
            logger.info("Отправляем на авторизацию файл: |" + document_name)
            return templates.TemplateResponse(
                "auth.html",
                {"request": request, "document_name": document_name}
            )
    
    return await view_document(request, document_name, doc_session)
