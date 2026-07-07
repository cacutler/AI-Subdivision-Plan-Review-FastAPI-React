import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=uuid.uuid4,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="engineer",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        default=lambda: datetime.now(timezone.utc),
    )

    plans: Mapped[list["Plan"]] = relationship(
        "Plan", back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("status IN ('engineer', 'admin')", name="ck_users_status"),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} status={self.status!r}>"


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Path or URL to the PDF on disk / S3 — never store the binary in Postgres
    file_path: Mapped[str] = mapped_column(Text, nullable=False)

    # Structured AI review output (matches the JSON schema we designed)
    ai_review_notes: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Tracks where the review is in its lifecycle
    review_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship("User", back_populates="plans")

    __table_args__ = (
        CheckConstraint(
            "review_status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_plans_review_status",
        ),
    )

    def __repr__(self) -> str:
        return f"<Plan id={self.id} title={self.title!r} review_status={self.review_status!r}>"
