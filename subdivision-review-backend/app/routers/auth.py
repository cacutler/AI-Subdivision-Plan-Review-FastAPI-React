from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, verify_password
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """
    Authenticate with username + password.
    Returns a Bearer JWT on success.
    """
    result = await db.execute(select(User).where(User.username == body.username))
    user = result.scalar_one_or_none()

    # Deliberate: same error for unknown user and wrong password (no user enumeration)
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        subject=user.id,
        extra={"status": user.status},
    )
    return TokenResponse(access_token=token)