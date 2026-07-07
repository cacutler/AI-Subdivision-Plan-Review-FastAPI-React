"""
Pydantic schemas for request validation, response serialisation, and the
structured AI review output that gets stored in plans.ai_review_notes.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Shared enums
# ---------------------------------------------------------------------------


class UserStatus(str, Enum):
    engineer = "engineer"
    admin = "admin"


class ReviewStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class OverallReviewStatus(str, Enum):
    pass_ = "pass"
    pass_with_notes = "pass_with_notes"
    fail = "fail"


class ReviewConfidence(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class FindingCategory(str, Enum):
    setback = "setback"
    lot_coverage = "lot_coverage"
    easement = "easement"
    grading = "grading"
    utilities = "utilities"
    notation = "notation"
    other = "other"


# ---------------------------------------------------------------------------
# AI review schema  (stored as JSONB in plans.ai_review_notes)
# ---------------------------------------------------------------------------


class ReviewFinding(BaseModel):
    id: str = Field(
        ...,
        pattern=r"^F-\d{3,}$",
        description="Stable finding ID, e.g. F-001",
    )
    category: FindingCategory
    description: str = Field(..., min_length=10)
    code_reference: str | None = Field(
        None,
        description="Specific code clause, e.g. §18.40.050(B). Null if model cannot identify one with confidence.",
    )
    location_description: str | None = Field(
        None,
        description="Human-readable location on the drawing, e.g. 'north property line, approx. 12 ft from corner'",
    )
    page: int | None = Field(
        None,
        ge=1,
        description="Page/sheet number for multi-page drawings. Null for single-page.",
    )


class DrawingMetadata(BaseModel):
    drawing_type: str | None = Field(
        None,
        description="e.g. 'site plan', 'grading plan', 'utility plan'",
    )
    scale_detected: str | None = Field(
        None,
        description="e.g. '1\\\" = 20\\'' if legible on the drawing",
    )
    north_arrow_present: bool | None = None
    legend_present: bool | None = None


class AIReviewNotes(BaseModel):
    """
    Exact shape of the JSON stored in plans.ai_review_notes.
    Also used to validate the model's raw output before it hits the DB.
    """

    review_version: Literal["1.0"] = "1.0"
    reviewed_at: datetime
    model: str = Field(..., description="Model string used, e.g. 'claude-sonnet-4-6'")
    overall_status: OverallReviewStatus
    confidence: ReviewConfidence
    summary: str = Field(..., min_length=10)
    jurisdiction: str | None = None
    findings: list[ReviewFinding] = Field(default_factory=list)
    drawing_metadata: DrawingMetadata | None = None


# ---------------------------------------------------------------------------
# User schemas
# ---------------------------------------------------------------------------


class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, description="Plain-text; hashed before storage")
    status: UserStatus = UserStatus.engineer

    @field_validator("username")
    @classmethod
    def username_lowercase(cls, v: str) -> str:
        return v.lower()


class UserUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    status: UserStatus | None = None


class UserResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    username: str
    email: str
    status: UserStatus
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Plan schemas
# ---------------------------------------------------------------------------


class PlanCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    # file_path is set server-side after the upload is stored — not in the request body


class PlanUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)


class PlanResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    file_path: str
    ai_review_notes: AIReviewNotes | None = None
    review_status: ReviewStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PlanSummaryResponse(BaseModel):
    """Lightweight list view — omits the full review notes."""

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    review_status: ReviewStatus
    overall_status: OverallReviewStatus | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_plan(cls, plan: "PlanResponse") -> "PlanSummaryResponse":
        overall = None
        if plan.ai_review_notes:
            overall = plan.ai_review_notes.overall_status
        return cls(
            id=plan.id,
            user_id=plan.user_id,
            title=plan.title,
            review_status=plan.review_status,
            overall_status=overall,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
        )


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
