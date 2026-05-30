from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import bcrypt
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse

SECRET_KEY = "cambiar-esta-clave-en-produccion-123456"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 120

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def create_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

def get_admin_user(request: Request) -> str | None:
    token = request.cookies.get("admin_token")
    if not token:
        return None
    return decode_token(token)

async def require_admin(request: Request):
    user = get_admin_user(request)
    if not user:
        raise HTTPException(status_code=303, detail="No autorizado")
    return user

async def optional_admin(request: Request):
    return get_admin_user(request)
