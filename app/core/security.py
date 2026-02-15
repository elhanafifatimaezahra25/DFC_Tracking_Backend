from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import os
import hashlib
import hmac
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from sqlmodel import Session
from .. import models, database
from .config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password hashed with PBKDF2-SHA256.

    Hashed format: pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
    """
    try:
        scheme, iterations, salt_hex, hash_hex = hashed_password.split("$")
        if scheme != "pbkdf2_sha256":
            return False
        iterations = int(iterations)
        salt = bytes.fromhex(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", plain_password.encode(), salt, iterations)
        return hmac.compare_digest(dk.hex(), hash_hex)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using PBKDF2-SHA256."""
    iterations = 100_000
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${dk.hex()}"

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(database.get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = session.get(models.user.User, int(user_id))
    if not user:
        raise credentials_exception
    return user


def get_current_admin(current_user: models.user.User = Depends(get_current_user)):
    """Verify that the current user has admin privileges."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )
    return current_user
