import jwt
import secrets
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Request
from typing import Optional, Dict
from app.logger import logger
import base64


# Генерация секретного ключа при первом запуске
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120  # 2 часа

def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token(token: str) -> Dict:
    """Проверка валидности JWT Токена"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
    logger.info('Djitk')
    auth_header = request.headers.get("Authorization")
    logger.info(f'{auth_header}, а так же {auth_header.startswith("Basic ")}')
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
