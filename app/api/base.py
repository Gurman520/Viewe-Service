from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from app.logic import get_document_list
from app.logger import logger


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", name="document_list")
async def list_documents(request: Request, q: Optional[str] = None):
    """Страница со списком всех документов с поиском"""
    documents = get_document_list(search_query=q)
    logger.info("Отправлен запрос на получение Списка документов")
    return templates.TemplateResponse(
        "list.html",
        {"request": request, "documents": documents, "search_query": q}
    )

@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/logo.ico")
