from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException
from .api import base, document, auth, viewer
from app.puty import Config
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from app.archivaruis import create_backup_zip
from app.log.logger import logger
from app.logi.doc_data_update import process_first_run, process_subsequent_run


templates = Jinja2Templates(directory="app/templates")

app = FastAPI(
    title="Markdown Viewer",
    description="Сервис отображения документации созданной в Obsidian",
    version="1.1.2")

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

# Кастомный обработчик HTTP Ошибок 
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    logger.info(f'Запрос пришел {request.url}')
    if exc.status_code == 500:
        return templates.TemplateResponse(
            "500.html",
            {"request": request, "error_detail": exc.detail},
            status_code=500,
        )
    elif exc.status_code == 404:
        return templates.TemplateResponse(
            "404.html",
            {"request": request},
            status_code=404
        )
    elif exc.status_code == 401:
        if '/api/auth/' in request.url.path:
            return Response(status_code=401, content="Incorrect password")
        q = request.url.query.split('=')[1]
        logger.debug(f'Запрос пришел {q} - Тип {type(q)}')
        return templates.TemplateResponse(
            "auth.html",
            {"request": request, "hash": exc.detail, "type": q}
        )


from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.logi.doc_logic import get_subgroup_list
from datetime import datetime

# Инициализация данных в БД
process_first_run(Config.DOCUMENTS_DIR, Config.DB_PATH)

# Инициализация scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    get_subgroup_list,
    trigger=IntervalTrigger(hours=10),
    next_run_time = datetime.now()  # Запустить сразу при старте
)

scheduler.add_job(
    process_subsequent_run,
    trigger=IntervalTrigger(minutes=10),
    next_run_time = datetime.now()  # Запустить сразу при старте
)

if Config.IS_BACKUP:
    scheduler.add_job(
        create_backup_zip,
        trigger=IntervalTrigger(hours=24),
        next_run_time = datetime.now()  # Запустить сразу при старте
    )

scheduler.start()
