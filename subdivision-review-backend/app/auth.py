"""
Authentication utilities:
  - Password hashing/verification via bcrypt (passlib)
  - JWT creation and decoding (python-jose)
  - FastAPI dependency for extracting the current user from a request
"""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import hashlib

from app.config import settings
from app.database import get_db
from app.models import User

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------


def hash_password(plain: str) -> str:
    """Return a SHA-256 hash of the plain-text password."""
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored hash."""
    return hash_password(plain) == hashed


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(subject: str | UUID, extra: dict[str, Any] | None = None) -> str:
    """
    Mint a signed JWT.

    Args:
        subject: Typically the user's UUID (stored as the 'sub' claim).
        extra:   Optional additional claims to embed (e.g. {"status": "admin"}).

    Returns:
        A signed JWT string.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        **(extra or {}),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def _decode_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT. Raises HTTP 401 on any failure.
    Internal helper — callers should use the FastAPI dependencies below.
    """
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------


async def get_current_user(
    token: str = Depends(_oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency that resolves the Bearer token to a User ORM object.
    Raises 401 if the token is invalid/expired, 404 if the user no longer exists.

    Usage:
        @router.get("/me")
        async def me(user: User = Depends(get_current_user)): ...
    """
    payload = _decode_token(token)
    user_id: str | None = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed token")

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency that additionally enforces admin status.
    Raises 403 if the authenticated user is not an admin.

    Usage:
        @router.delete("/users/{id}")
        async def delete_user(user: User = Depends(require_admin)): ...
    """
    if current_user.status != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user