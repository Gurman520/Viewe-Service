from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException
from .api import base, document, auth, viewer
from app.puty import Config
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from app.logger import logger


templates = Jinja2Templates(directory="app/templates")

app = FastAPI(
    title="Markdown Viewer",
    description="Сервис отображения документации созданной в Obsidian",
    version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/images", StaticFiles(directory=Config.IMAGES_DIR), name="images")
app.mount("/files", StaticFiles(directory=Config.IMAGES_DIR), name="files")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(document.router, prefix="/api/document", tags=["document"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(viewer.router, prefix="/view", tags=["viewed page"])
app.include_router(base.router, tags=["base"])

# Обработчик 404 ошибки
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    logger.debug(f'Запрос пришел {request.url.path}')
    return templates.TemplateResponse(
        "404.html",
        {"request": request},
        status_code=404
    )