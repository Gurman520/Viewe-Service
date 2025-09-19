from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.logi.doc_logic import check_doc


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def home(request: Request):
    """редирект"""
    return RedirectResponse("/view/list")

@router.get("/admin")
async def adm_home(request: Request):
    """редирект"""
    return RedirectResponse("/view/adm/list")

@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Получение изображении Favicon"""
    return FileResponse("app/static/favicon.ico")

@router.get("/check-headers")
async def check_headers(request: Request):
    """Проверка Headers"""
    return {
        "host": request.headers.get("host"),
        "x-forwarded-host": request.headers.get("x-forwarded-host"),
        "url": str(request.url)
    }

@router.get("/healthcheck")
async def health_check():
    """Проверяет состояние сервиса и возвращает OK, если всё хорошо."""
    return {"status": "OK"}

@router.get("/checkDOC")
async def health_check():
    """Проверяет подключение к хранилищу файлов"""
    if not check_doc():
        raise HTTPException(status_code=404, detail="Directory not found")
    return {"status": "OK", "Dir": "OK"}
