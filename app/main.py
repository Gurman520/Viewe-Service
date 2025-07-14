from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .api import base, document, auth
from app.puty import IMAGES_DIR


app = FastAPI(title="Markdown Viewer")

# Подключение статических файлов
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
app.mount("/files", StaticFiles(directory=IMAGES_DIR), name="files")

app.include_router(document.router, prefix="/api/document", tags=["document"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(base.router, tags=["base"])



