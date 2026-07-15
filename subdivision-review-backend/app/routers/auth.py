from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, TokenResponse, UserCreate

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
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """
    Public self-registration. Always creates an 'engineer' account —
    the `status` field on the request body is ignored, regardless of what
    the client sends, to prevent self-registering as admin.
    """
    existing = await db.execute(
        select(User).where((User.username == body.username) | (User.email == body.email))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already in use",
        )

    user = User(
        first_name=body.first_name,
        last_name=body.last_name,
        username=body.username,
        email=body.email,
        password_hash=hash_password(body.password),
        status="engineer",
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    token = create_access_token(subject=user.id, extra={"status": user.status})
    return TokenResponse(access_token=token)