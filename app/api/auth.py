from fastapi import APIRouter, Request, HTTPException,  Depends, status, Response
from frontmatter import load
from app.puty import Config
from datetime import timedelta
from app.security import create_jwt_token, verify_jwt_token, ACCESS_TOKEN_EXPIRE_MINUTES, parse_utf8_basic_auth
from app.logger import logger
from app.logic import check_password


router = APIRouter()

# Настройки сессии
SESSION_COOKIE_NAME = "doc_session"
TOKEN_EXPIRE = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

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


@router.post("/{document_name}")
async def authenticate_document(
    document_name: str,
    response: Response,
    credentials: dict = Depends(parse_utf8_basic_auth)
):
    logger.debug('Получен запрос на авторизацию')
    """Проверка авторизации на документе"""
    original_name = document_name.replace('_', ' ')
    logger.info("Имя документа: | " + document_name)
    md_file = Config.DOCUMENTS_DIR / f"{original_name}.md"
    
    with open(md_file, "r", encoding="utf-8") as f:
        post = load(f)
        password = post.metadata.get("password")
        # Если документ защищен паролем
        logger.debug('Будем запрашивать пароль')
        if password:
            if not check_password(credentials, password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect password",
                    headers={"WWW-Authenticate": "Basic"},
                )
    
    token = create_jwt_token({"doc": document_name}, TOKEN_EXPIRE)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    logger.info("Сформировались Coolie")
    return {"status": "authenticated"}