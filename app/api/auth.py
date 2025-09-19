from fastapi import APIRouter, Request, HTTPException,  Depends, status, Response
from frontmatter import load
from app.puty import Config
from datetime import timedelta
from app.security import create_jwt_token, verify_jwt_token, ACCESS_TOKEN_EXPIRE_MINUTES, parse_utf8_basic_auth
from app.logger import logger
from app.logi.auth import auth_document


router = APIRouter()

# Настройки сессии
# SESSION_COOKIE_NAME = "doc_session"
# TOKEN_EXPIRE = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

@router.post("/verify_token")
async def verify_token(request: Request):
    """Эндпоинт пверификации JWT токена"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = auth_header.split(" ")[1]
    verify_jwt_token(token)  # Вызовет исключение если токен невалиден
    return {"status": "valid"}


@router.post("/{hash}")
async def authenticate_document(
    hash: str,
    response: Response,
    credentials: dict = Depends(parse_utf8_basic_auth)
):
    """Проверка авторизации на документе"""

    logger.info('Получен запрос на авторизацию')
    return auth_document(hash=hash, response=response, credentials=credentials)
