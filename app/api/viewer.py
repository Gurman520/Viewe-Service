from fastapi import APIRouter, Request, HTTPException, Cookie
from fastapi.templating import Jinja2Templates
from typing import Optional
from app.logger import logger
from httpx import AsyncClient
from app.puty import Config


router = APIRouter()

# Шаблоны
templates = Jinja2Templates(directory="app/templates")

@router.get("/adm/list", name="document_adm_list")
async def list_documents(request: Request, q: Optional[str] = None):
    """Страница со списком всех документов с поиском"""
    try:
        async with AsyncClient() as client:
            response = await client.get(f"http://127.0.0.1:{Config.PORT}/api/document/list",
                                        params={"type": ""})
        
        if response.is_success:
            doc = response.json()
            # logger.info(f"Открываем страницу со списком инструкций {Config.subgroup_list}")
            return templates.TemplateResponse(
                "list.html",
                {"request": request, "documents": doc["document"], "search_query": q, "subgroup": Config.subgroup_list, "type": "adm"}
            )
        else:
            raise HTTPException(status_code=response.status_code, detail=f"External API returned error: {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", name="document_list")
async def list_documents(request: Request, q: Optional[str] = None):
    """Страница со списком всех документов с поиском"""
    try:
        async with AsyncClient() as client:
            response = await client.get(f"http://127.0.0.1:{Config.PORT}/api/document/list",
                                        params={"type": "doctor"})
        
        if response.is_success:
            doc = response.json()
            # logger.info(f"Открываем страницу со списком инструкций {Config.subgroup_list}")
            return templates.TemplateResponse(
                "list.html",
                {"request": request, "documents": doc["document"], "search_query": q, "subgroup": Config.subgroup_list, "type": "doctor"}
            )
        else:
            raise HTTPException(status_code=response.status_code, detail=f"External API returned error: {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_name}", name="view_document")
async def document_router(
    request: Request,
    document_name: str,
    type_d: str = "",
    doc_session: str = Cookie(default=None)
):
    """Получение страницы с документом"""
    try:
        logger.info(f'Получен параметр type {type_d}')
        async with AsyncClient() as client:
            response = await client.get(f"http://127.0.0.1:{Config.PORT}/api/document/{document_name}", 
                                        cookies={"doc_session": doc_session})
        if response.status_code == 301 :
            doc = response.json()
            logger.info("Ошибка 301 - отправляем на авторизацию")
            return templates.TemplateResponse(
                "auth.html",
                {"request": request, "document_name": doc["document_name"]}
            )
        elif response.status_code == 200:
            logger.info("Все отлично")
            doc = response.json()
            doc["request"] = request
            doc["type"] = type_d
            return templates.TemplateResponse(
                "document.html",
                doc
            )
        elif response.status_code == 401:
            logger.info("Ошибка 401 - Пользователь не авторизован")
            raise HTTPException(status_code=401, detail=str(document_name))
        elif response.status_code == 404:
            logger.info("Ошибка 404 - Документ не найден")
            raise HTTPException(status_code=404, detail=str(document_name))
        else:
            logger.critical("Ошикбка " + str(response.text))
            raise HTTPException(status_code=response.status_code, detail=f"External API returned error: {response.text}")
    except HTTPException as exc:
        if exc.status_code == 404:
            raise HTTPException(status_code=404, detail=str(exc.detail))
        if exc.status_code == 401:
            raise HTTPException(status_code=401, detail=str(exc.detail))
        else:
            raise HTTPException(status_code=500, detail=str(exc.detail))
    except Exception as e:
        logger.critical("Ошибка " + str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/d/isolated_view/{document_name}", name="isolated_view")
async def isolated_view(request: Request, document_name: str):
    """Изолированный просмотр документа без навигации"""
    try:
        async with AsyncClient() as client:
            response = await client.get(f"http://127.0.0.1:{Config.PORT}/api/document/isolated_view/{document_name}")
        
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
    except HTTPException as exc:
        if exc.status_code == 404:
            raise HTTPException(status_code=404, detail=str(exc.detail))
        else:
            raise HTTPException(status_code=500, detail=str(exc.detail))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
