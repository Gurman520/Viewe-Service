from fastapi import HTTPException, Response, status
from app.puty import Config
from app.db.process import get_document_by_hash
from app.logi.doc_logic import check_password
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Request
from typing import Optional, Dict
from app.log.logger import logger
import base64


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
            max_age=Config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax"
        )
        logger.info("Сформировались Coolie")
        return {"status": "authenticated"}

def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)

def verify_jwt_token(token: str) -> Dict:
    """Проверка валидности JWT Токена"""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.PyJWTError:
        logger.warning("Не корректный ТОКЕН!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

def get_document_name_from_token(token: str) -> str:
    """Получение имени документа из Токена"""
    payload = verify_jwt_token(token)
    logger.info("Расшиврованный токен: \n" + str(payload))
    return payload.get("doc")

async def parse_utf8_basic_auth(request: Request):
    logger.debug("SECURITY - parse utf8")
    auth_header = request.headers.get("Authorization")
    logger.debug(f'{auth_header}, а так же {auth_header.startswith("Basic ")}')
    if not auth_header or not auth_header.startswith("Basic "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid auth header",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    try:
        # Декодируем Base64 → UTF-8
        decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
        logger.info(f'{decoded}')
        _, password = decoded.split(":", 1)  # Разделяем по первому ":"
        logger.info(f'{password}')
        return {"password": password}
    except (UnicodeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid UTF-8 in credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
