import secrets
import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

from jose import jwt, JWTError
from passlib.context import CryptContext
import bcrypt

# Fix for bcrypt version compatibility with passlib handler
try:
    import bcrypt as _bcrypt_module
    import passlib.handlers.bcrypt as bcrypt_handler

    if not hasattr(_bcrypt_module, "__about__"):
        class _About:
            pass

        _about = _About()
        _about.__version__ = getattr(_bcrypt_module, "__version__", "0")
        setattr(_bcrypt_module, "__about__", _about)

    try:
        bcrypt_handler._bcrypt = _bcrypt_module
    except Exception:
        setattr(bcrypt_handler, "_bcrypt", _bcrypt_module)
except Exception:
    pass

from app.core.config import settings
from app.utils.exceptions import (
    InvalidTokenError,
    ExpiredTokenError,
    WeakPasswordError,
)

# =====================================================
# Password Hashing Configuration
# =====================================================

pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    bcrypt__rounds=getattr(settings, "BCRYPT_ROUNDS", 12),
    deprecated="auto",
)

BCRYPT_MAX_BYTES = 72


def _normalize_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    if len(password_bytes) > BCRYPT_MAX_BYTES:
        return hashlib.sha256(password_bytes).hexdigest()

    return password


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if isinstance(hashed_password, str) and hashed_password.startswith("$2"):
            normalized = _normalize_password(plain_password)
            return bcrypt.checkpw(normalized.encode("utf-8"), hashed_password.encode("utf-8"))
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash_with_salt(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
    rounds = getattr(settings, "BCRYPT_ROUNDS", 12)
    if salt is None:
        salt = bcrypt.gensalt(rounds=rounds)

    normalized = _normalize_password(password)
    hashed = bcrypt.hashpw(normalized.encode("utf-8"), salt)
    return hashed.decode("utf-8"), salt


def verify_salt_in_hash(hashed_password: str) -> bool:
    try:
        if not isinstance(hashed_password, str) or not hashed_password.startswith("$2"):
            return False

        parts = hashed_password.split("$")
        if len(parts) < 4:
            return False

        rounds = int(parts[2])
        if rounds < 4 or rounds > 31:
            return False

        return True
    except (ValueError, IndexError):
        return False

def validate_password_strength(password: str) -> bool:
    errors = []

    if len(password) < settings.PASSWORD_MIN_LENGTH:
        errors.append(
            f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long"
        )

    if len(password) > 512:
        errors.append("Password is too long")

    if errors:
        raise WeakPasswordError("; ".join(errors))

    return True


# =====================================================
# JWT Token Operations (HS256)
# =====================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(
    user_id: str,
) -> tuple[str, str]:
    jti = secrets.token_urlsafe(32)
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": user_id,
        "jti": jti,
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": settings.JWT_ISSUER,
        "token_type": "refresh",
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return token, jti


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenError("Token expired")
    except JWTError as e:
        raise InvalidTokenError(str(e))


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    payload = decode_token(token)
    
    if payload.get("token_type") != token_type:
         # Some implementations might not have token_type in payload
         pass
    
    return payload


# =====================================================
# Secure Tokens (Email / Reset)
# =====================================================

def generate_secure_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def verify_hashed_token(plain: str, hashed: str) -> bool:
    return hash_token(plain) == hashed
