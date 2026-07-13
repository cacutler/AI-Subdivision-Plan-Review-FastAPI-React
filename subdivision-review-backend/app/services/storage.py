"""
File storage service — saves uploaded PDFs to disk and returns their path.
Swap the implementation here when moving to S3 or another object store.
"""

import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile, status

from app.config import settings

_ALLOWED_CONTENT_TYPES = {"application/pdf"}
_UPLOAD_DIR = Path(settings.upload_dir)


def _ensure_upload_dir() -> None:
    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def save_upload(file: UploadFile) -> str:
    """
    Validate and persist an uploaded PDF.

    Returns the absolute file path to store in the DB.
    Raises HTTP 400/413 on invalid input.
    """
    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only PDF files are accepted (got {file.content_type!r})",
        )

    _ensure_upload_dir()

    # Unique filename — never trust the client-supplied name for the path
    dest = _UPLOAD_DIR / f"{uuid.uuid4()}.pdf"

    bytes_written = 0
    async with aiofiles.open(dest, "wb") as out:
        while chunk := await file.read(1024 * 256):  # 256 KB chunks
            bytes_written += len(chunk)
            if bytes_written > settings.max_upload_bytes:
                await out.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds the {settings.max_upload_bytes // (1024 * 1024)} MB limit",
                )
            await out.write(chunk)

    return str(dest)


def delete_file(file_path: str) -> None:
    """Remove a stored PDF from disk. Silent if already gone."""
    Path(file_path).unlink(missing_ok=True)