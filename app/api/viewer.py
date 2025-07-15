from fastapi import APIRouter, Request, Form, HTTPException, status, Cookie
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from frontmatter import load
from re import finditer, findall
from zipfile import ZipFile
from typing import Optional
from tempfile import NamedTemporaryFile
from pathlib import Path
from app.puty import DOCUMENTS_DIR, IMAGES_DIR, ALLOWED_FILE_EXTENSIONS
# from app.logic import get_document_list, render_markdown, load_document_without_password
from app.security import get_document_name_from_token
from app.logger import logger
from httpx import AsyncClient


router = APIRouter()

# Шаблоны
templates = Jinja2Templates(directory="app/templates")


@router.get("/list", name="document_list")
async def list_documents(request: Request, q: Optional[str] = None):
    """Страница со списком всех документов с поиском"""
    try:
        async with AsyncClient() as client:
            response = await client.get("http://127.0.0.1:5031/api/document/list")
        
        if response.is_success:
            doc = response.json()
            logger.info("Открываем страницу со списком инструкций")
            return templates.TemplateResponse(
                "list.html",
                {"request": request, "documents": doc["document"], "search_query": q}
            )
        else:
            raise HTTPException(status_code=response.status_code, detail=f"External API returned error: {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_name}", name="view_document")
async def document_router(
    request: Request,
    document_name: str,
    doc_session: str = Cookie(default=None)
):
    try:
        async with AsyncClient() as client:
            response = await client.get(f"http://127.0.0.1:5031/api/document/{document_name}", cookies={"doc_session": doc_session})
        logger.info("Jndtn^ " + str(response.status_code) + " - " + str(response.text))
        if response.status_code == 301 :
            doc = response.json()
            logger.info("Ошибка 301")
            return templates.TemplateResponse(
                "auth.html",
                {"request": request, "document_name": doc["document_name"]}
            )
        elif response.status_code == 200:
            logger.info("Все отлично")
            doc = response.json()
            doc["request"] = request
            return templates.TemplateResponse(
                "document.html",
                doc
            )
        elif response.status_code == 401:
            logger.info("Ошибка 401 - Пользователь не авторизован")
            return templates.TemplateResponse(
                "auth.html",
                {"request": request, "document_name": document_name}
            )
        else:
            logger.critical("Ошикбка " + str(response.text))
            raise HTTPException(status_code=response.status_code, detail=f"External API returned error: {response.text}")
    except Exception as e:
        logger.critical("Ошибка " + str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/d/isolated_view/{document_name}", name="isolated_view")
async def isolated_view(request: Request, document_name: str):
    """Изолированный просмотр документа без навигации"""
    try:
        async with AsyncClient() as client:
            response = await client.get(f"http://127.0.0.1:5031/api/document/isolated_view/{document_name}")
        
        if response.status_code == 200:
            logger.info("Отправлен документ для изолированного просмотра - " + str(document_name))
            doc = response.json()
            doc["request"] = request
            return templates.TemplateResponse(
                "isolated.html",
                doc
            )
        else:
            raise HTTPException(status_code=response.status_code, detail=f"External API returned error: {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
