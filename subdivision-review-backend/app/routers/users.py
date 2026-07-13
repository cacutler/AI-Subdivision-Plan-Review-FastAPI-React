import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, hash_password, require_admin
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


# ---------------------------------------------------------------------------
# Self-service (any authenticated user)
# ---------------------------------------------------------------------------


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Return the currently authenticated user's profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Update own profile. Engineers cannot change their own status —
    only admins can promote/demote via PUT /users/{id}.
    """
    update_data = body.model_dump(exclude_unset=True, exclude={"status"})
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    if "email" in update_data:
        conflict = await db.execute(
            select(User).where(User.email == update_data["email"], User.id != current_user.id)
        )
        if conflict.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.flush()
    await db.refresh(current_user)
    return current_user


# ---------------------------------------------------------------------------
# Admin-only CRUD
# ---------------------------------------------------------------------------


@router.get("", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 50,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[User]:
    """List all users. Admin only."""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Fetch a single user by ID. Admin only."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Create a new user. Admin only.
    For self-registration, wire up a separate public /auth/register endpoint.
    """
    # Check uniqueness
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
        status=body.status.value,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    body: UserUpdate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Update any user's fields, including status. Admin only."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    if "email" in update_data:
        conflict = await db.execute(
            select(User).where(User.email == update_data["email"], User.id != user_id)
        )
        if conflict.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

    for field, value in update_data.items():
        # Pydantic enums → unwrap to string value for the ORM
        setattr(user, field, value.value if hasattr(value, "value") else value)

    await db.flush()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a user and cascade-delete their plans. Admin only."""
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admins cannot delete their own account",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await db.delete(user)