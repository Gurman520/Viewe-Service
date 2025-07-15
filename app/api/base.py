from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates



router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def home(request: Request):
    """редирект"""
    return RedirectResponse("/api/document/list")

@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/logo.ico")
