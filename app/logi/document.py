from fastapi import HTTPException, Cookie, status
from app.puty import Config
from app.db.process import get_document_by_hash
from app.log.logger import logger
from fastapi.responses import JSONResponse
from app.logi.doc_logic import render_markdown, load_document_without_password
from app.logi.auth import get_document_name_from_token
from re import finditer
from pathlib import Path


async def view_document(
    document: dict,
    doc_session: str = Cookie(default=None),
    doc_type: str = ""
):
    md_file = Config.DOCUMENTS_DIR / document['file_path']
    
    if not md_file.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document['password']:
        try:
            if not doc_session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Basic"},
                )
    
            token_doc_name = get_document_name_from_token(doc_session)

            if str(token_doc_name) != document['content_hash']:
                raise HTTPException(
                    status_code=401,
                    detail="Token not valid for this document",
                )
        except HTTPException:
            logger.info("APP - Не соответсвие файлов, отправляем на повторную авторизацию")
            raise HTTPException(
                    status_code=401,
                    detail="Not authenticated",
                )
        
    logger.info("APP - Начинаем формировать итоговый ответ")
    return await get_document_response(md_file, doc_type)


async def get_document_response(md_file: Path, doc_type: str):
    """Создает ответ с содержимым документа"""
    post = load_document_without_password(md_file)
    content = render_markdown(post.content, doc_type)

    attachments = []
    for match in finditer(r'!\[\[([^\]\n]+)\]\]', post.content):
        filename = match.group(1)
        if (Config.IMAGES_DIR / filename).exists() or (Config.IMAGES_DIR / filename).exists():
            attachments.append(filename)
    doc = {
        "title": md_file.stem,
        "content": content,
        "metadata": post.metadata,
        "document_name": md_file.stem,
        "is_protected": True,
        "original_name": md_file.stem,
        "document_attachments": attachments 
    }
    return JSONResponse(content=doc, status_code=200)

async def get_document(hash: str, doc_session: str, doc_type: str):
    logger.info("APP - Получение документа")
    document = get_document_by_hash(hash)

    if document:
        if document['password'] and not doc_session:
            logger.info("Отправляем на авторизацию файл: | " + document['file_path'])
            return JSONResponse(content={"document_name": document['file_path']}, status_code=401)

        try:
            return await view_document(document, doc_session, doc_type=doc_type)
        except HTTPException as exp:
            logger.debug(f"Получена ошибка при обработке - {exp.status_code} - {exp.detail}")
            return JSONResponse(content=exp.detail, status_code=exp.status_code)
    else:
        raise HTTPException(status_code=404, detail="Document not found")
    

def get_isolated_document(hash: str, doc_type: str = ""):
    logger.info("APP - Получение изолированного документа")
    document = get_document_by_hash(hash)

    if document:
        try:

            md_file = Config.DOCUMENTS_DIR / document['file_path']
            post = load_document_without_password(md_file)
            content = render_markdown(post.content, doc_type)
            doc = {
                "title": md_file.stem,
                "content": content,
                "metadata": post.metadata,
                "document_name": md_file.stem
                }
            return JSONResponse(content=doc, status_code=200)
        except HTTPException as exp:
            logger.debug(f"Получена ошибка при обработке - {exp.status_code} - {exp.detail}")
            return JSONResponse(content=exp.detail, status_code=exp.status_code)
    else:
        raise HTTPException(status_code=404, detail="Document not found")
