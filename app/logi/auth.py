from fastapi import HTTPException, Response, status
from app.puty import Config
from app.db.process import get_document_by_hash
from app.logger import logger
from fastapi.responses import JSONResponse
from frontmatter import load
from app.logic import get_document_list, render_markdown, load_document_without_password
from app.security import get_document_name_from_token
from re import finditer, findall
from pathlib import Path
from app.security import create_jwt_token, verify_jwt_token, ACCESS_TOKEN_EXPIRE_MINUTES, parse_utf8_basic_auth
from app.logic import check_password


def auth_document(hash: str, response: Response, credentials: dict):
    document = get_document_by_hash(hash)
    logger.info(f"Получен hash - {hash}")

    if document:
        if document['password']:
            logger.debug('Будем запрашивать пароль')
            logger.info(f"Получен пароль: {credentials} - Корректный пароль: {document['password']}")
            if not check_password(credentials, document['password']):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect password",
                    headers={"WWW-Authenticate": "Basic"},
                )
        token = create_jwt_token({"doc": hash}, Config.TOKEN_EXPIRE)
        response.set_cookie(
            key=Config.SESSION_COOKIE_NAME,
            value=token,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax"
        )
        logger.info("Сформировались Coolie")
        return {"status": "authenticated"}

