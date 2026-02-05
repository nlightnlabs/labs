"""Users API endpoints."""

import os
import uuid as uuid_lib
from typing import Optional
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Header, UploadFile, File
from sqlalchemy.orm import Session

from app.utilities.security import (
    verify_access_token,
    verify_password,
    get_password_hash,
    validate_password_strength,
)
from app.config import settings
from app.utils.database import get_db
from app.models.user import User
from app.models.session import Session as SessionModel
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.auth import ChangePasswordRequest
from app.schemas.common import APIResponse

# Allowed image types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

router = APIRouter()


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )

    token = authorization.split(" ")[1]
    user_id = verify_access_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    return user


@router.get("/me", response_model=APIResponse[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return APIResponse(
        success=True,
        data=UserResponse.model_validate(current_user)
    )


@router.put("/me", response_model=APIResponse[UserResponse])
async def update_current_user(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    update_data = data.model_dump(exclude_unset=True, by_alias=False)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)

    return APIResponse(
        success=True,
        data=UserResponse.model_validate(current_user)
    )


@router.delete("/me")
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user account."""
    db.delete(current_user)
    db.commit()

    return APIResponse(
        success=True,
        data={"message": "Account deleted successfully"}
    )


@router.patch("/me/password", response_model=APIResponse)
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user's password."""
    # Verify current password
    if not current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change password for SSO-only accounts"
        )

    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Validate new password
    is_valid, error_msg = validate_password_strength(data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # Update password
    current_user.password_hash = get_password_hash(data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()

    return APIResponse(
        success=True,
        data={"message": "Password changed successfully"}
    )


@router.patch("/me/avatar", response_model=APIResponse)
async def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user avatar."""
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: JPEG, PNG, GIF, WebP"
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB"
        )

    # Generate unique filename
    file_ext = file.filename.split(".")[-1] if file.filename else "jpg"
    unique_filename = f"{uuid_lib.uuid4()}.{file_ext}"

    # For local development, save to static directory
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "static", "avatars")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, unique_filename)
    with open(file_path, "wb") as f:
        f.write(content)

    # Update user avatar URL
    avatar_url = f"/static/avatars/{unique_filename}"
    current_user.avatar_url = avatar_url
    current_user.updated_at = datetime.utcnow()
    db.commit()

    return APIResponse(
        success=True,
        data={"avatarUrl": avatar_url}
    )


@router.delete("/me/avatar", response_model=APIResponse)
async def delete_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user avatar."""
    # Delete old file if it exists
    if current_user.avatar_url and current_user.avatar_url.startswith("/static/avatars/"):
        old_filename = current_user.avatar_url.split("/")[-1]
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "static", "avatars")
        old_file_path = os.path.join(upload_dir, old_filename)
        if os.path.exists(old_file_path):
            os.remove(old_file_path)

    current_user.avatar_url = None
    current_user.updated_at = datetime.utcnow()
    db.commit()

    return APIResponse(
        success=True,
        data={"message": "Avatar removed successfully"}
    )


@router.get("/me/sessions", response_model=APIResponse)
async def get_user_sessions(
    authorization: Optional[str] = Header(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active sessions for current user."""
    current_token = authorization.split(" ")[1] if authorization else None

    sessions = db.query(SessionModel).filter(
        SessionModel.user_id == current_user.id,
        SessionModel.expires_at > datetime.utcnow()
    ).all()

    session_list = []
    for session in sessions:
        session_list.append({
            "id": str(session.id),
            "userId": str(session.user_id),
            "ipAddress": session.ip_address,
            "userAgent": session.user_agent,
            "expiresAt": session.expires_at.isoformat(),
            "createdAt": session.created_at.isoformat(),
            "isCurrent": session.token == current_token,
        })

    return APIResponse(success=True, data=session_list)


@router.delete("/me/sessions/{session_id}")
async def revoke_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke a specific session."""
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    db.delete(session)
    db.commit()

    return APIResponse(
        success=True,
        data={"message": "Session revoked successfully"}
    )


@router.delete("/me/sessions")
async def revoke_all_sessions(
    authorization: Optional[str] = Header(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke all sessions except current."""
    current_token = authorization.split(" ")[1] if authorization else None

    db.query(SessionModel).filter(
        SessionModel.user_id == current_user.id,
        SessionModel.token != current_token
    ).delete()

    db.commit()

    return APIResponse(
        success=True,
        data={"message": "All other sessions revoked"}
    )
