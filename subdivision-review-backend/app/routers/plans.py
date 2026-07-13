import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, require_admin
from app.database import get_db
from app.models import Plan, User
from app.schemas import PlanResponse, PlanSummaryResponse, PlanUpdate, OverallReviewStatus, ReviewStatus
from app.services.ai_review import run_ai_review
from app.services.storage import delete_file, save_upload

router = APIRouter(prefix="/plans", tags=["plans"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_plan_or_404(plan_id: uuid.UUID, db: AsyncSession) -> Plan:
    result = await db.execute(select(Plan).where(Plan.id == plan_id))
    plan = result.scalar_one_or_none()
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan


def _assert_owner_or_admin(plan: Plan, current_user: User) -> None:
    """Raise 403 if the user doesn't own the plan and isn't an admin."""
    if plan.user_id != current_user.id and current_user.status != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this plan",
        )


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


@router.get("", response_model=list[PlanSummaryResponse])
async def list_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[PlanSummaryResponse]:
    """
    List plans. Engineers see only their own; admins see all.
    Returns the lightweight summary shape (no full review JSON).
    """
    query = select(Plan).offset(skip).limit(limit).order_by(Plan.created_at.desc())
    if current_user.status != "admin":
        query = query.where(Plan.user_id == current_user.id)

    result = await db.execute(query)
    plans = result.scalars().all()

    summaries = []
    for plan in plans:
        overall = None
        if plan.ai_review_notes and isinstance(plan.ai_review_notes, dict):
            overall = plan.ai_review_notes.get("overall_status")
        summaries.append(
            PlanSummaryResponse(
                id=plan.id,
                user_id=plan.user_id,
                title=plan.title,
                review_status=ReviewStatus(plan.review_status),
                overall_status=OverallReviewStatus(overall) if overall else None,
                created_at=plan.created_at,
                updated_at=plan.updated_at,
            )
        )
    return summaries


# ---------------------------------------------------------------------------
# Get single
# ---------------------------------------------------------------------------


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Plan:
    """Fetch a plan with its full review notes. Owner or admin only."""
    plan = await _get_plan_or_404(plan_id, db)
    _assert_owner_or_admin(plan, current_user)
    return plan


# ---------------------------------------------------------------------------
# Upload / create
# ---------------------------------------------------------------------------


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def upload_plan(
    title: str,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Plan:
    """
    Upload a PDF plan. Stores the file and creates the DB record.
    Review status starts as 'pending' — trigger review separately via
    POST /plans/{id}/review.
    """
    file_path = await save_upload(file)

    plan = Plan(
        user_id=current_user.id,
        title=title,
        file_path=file_path,
        review_status="pending",
    )
    db.add(plan)
    await db.flush()
    await db.refresh(plan)
    return plan


# ---------------------------------------------------------------------------
# Update metadata
# ---------------------------------------------------------------------------


@router.put("/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: uuid.UUID,
    body: PlanUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Plan:
    """Update plan metadata (title only for now). Owner or admin only."""
    plan = await _get_plan_or_404(plan_id, db)
    _assert_owner_or_admin(plan, current_user)

    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    for field, value in update_data.items():
        setattr(plan, field, value)

    await db.flush()
    await db.refresh(plan)
    return plan


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a plan and its PDF file. Owner or admin only."""
    plan = await _get_plan_or_404(plan_id, db)
    _assert_owner_or_admin(plan, current_user)

    delete_file(plan.file_path)
    await db.delete(plan)


# ---------------------------------------------------------------------------
# AI review trigger
# ---------------------------------------------------------------------------


@router.post("/{plan_id}/review", response_model=PlanResponse)
async def trigger_review(
    plan_id: uuid.UUID,
    jurisdiction: str | None = Query(None, description="e.g. 'City of Springfield – Title 18'"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Plan:
    """
    Trigger AI review for a plan. Owner or admin only.
    Runs synchronously — the request hangs until the model responds
    (typically 10–30 s for a civil drawing). Plan review_status is set
    to 'processing' before the call and 'completed' or 'failed' after.
    """
    plan = await _get_plan_or_404(plan_id, db)
    _assert_owner_or_admin(plan, current_user)

    if plan.review_status == "processing":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Review already in progress",
        )

    # Mark as processing so concurrent requests don't double-trigger
    plan.review_status = "processing"
    await db.flush()

    try:
        review = await run_ai_review(plan.file_path, jurisdiction=jurisdiction)
        plan.ai_review_notes = review.model_dump(mode="json")
        plan.review_status = "completed"
    except Exception as exc:
        plan.review_status = "failed"
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI review failed: {exc}",
        )

    await db.flush()
    await db.refresh(plan)
    return plan