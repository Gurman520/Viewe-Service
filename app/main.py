from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .api import base, document, auth, viewer
from app.puty import IMAGES_DIR
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Markdown Viewer",
    description="Сервис отображения документации созданной в Obsidian",
    version="0.0.9")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
app.mount("/files", StaticFiles(directory=IMAGES_DIR), name="files")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(document.router, prefix="/api/document", tags=["document"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(viewer.router, prefix="/view", tags=["viewed page"])
app.include_router(base.router, tags=["base"])



