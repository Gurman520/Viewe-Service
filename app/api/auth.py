from fastapi import APIRouter, Request, HTTPException,  Depends, status, Response
from app.logi.auth import verify_jwt_token, parse_utf8_basic_auth, auth_document
from app.log.logger import logger


router = APIRouter()

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
