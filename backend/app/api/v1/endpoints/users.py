"""Users API endpoints using postgres_db with IAM token authentication."""

import os
import uuid as uuid_lib
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Header, UploadFile, File

from app.utilities.security import verify_access_token
from app.utilities.encryption import match_encrypted_text, hash_text
from app.config import settings
from app.utilities.postgres_db import (
    db_connect,
    serialize_value,
    edit_user,
    UserModel,
    DBHOST,
    DBPORT,
    DBUSER,
    DEFAULT_DB,
)
from app.schemas.user import UserUpdate
from app.schemas.auth import ChangePasswordRequest
from app.schemas.common import APIResponse

# Allowed image types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

router = APIRouter()


def user_dict_to_response(user: dict) -> dict:
    """Convert user dict to response dict with frontend-compatible fields."""
    def _get_role_from_access_level(access_level: Optional[str]) -> str:
        if access_level:
            level = access_level.lower()
            if "super" in level or "admin" in level:
                return "admin"
            elif "power" in level or "manager" in level:
                return "manager"
        return "user"

    return {
        "id": str(user.get("id", "")),
        "email": user.get("email"),
        "username": user.get("username"),
        "firstName": user.get("first_name"),
        "lastName": user.get("last_name"),
        "mobilePhone": user.get("mobile_phone"),
        "jobTitle": user.get("job_title"),
        "companyName": user.get("company_name"),
        "tenantName": user.get("tenant_name"),
        "accessLevel": user.get("access_level"),
        "businessUnit": user.get("business_unit"),
        "avatarUrl": user.get("photo_url"),
        "userType": user.get("user_type"),
        "status": user.get("status"),
        "stage": user.get("stage"),
        "createdAt": user.get("creation_date"),
        "updatedAt": user.get("last_updated"),
        "role": _get_role_from_access_level(user.get("access_level")),
        "isActive": user.get("status") and str(user.get("status")).lower() == "active",
        "isVerified": True,
    }


async def get_user_by_id(user_id: str, include_password: bool = False) -> Optional[dict]:
    """Get user by ID using asyncpg with IAM auth."""
    conn = await db_connect(
        db_host=DBHOST,
        db_port=DBPORT,
        db_user=DBUSER,
        db_name=DEFAULT_DB
    )

    if not conn:
        return None

    try:
        query = "SELECT * FROM data.users WHERE id = $1;"
        row = await conn.fetchrow(query, user_id)

        if row:
            user = {k: serialize_value(v) for k, v in dict(row).items()}
            if not include_password:
                user.pop("password", None)
            return user
        return None
    finally:
        await conn.close()


async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> dict:
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

    user = await get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user_status = user.get("status")
    if user_status and str(user_status).lower() != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )

    return user


async def update_user_in_db(user_id: str, updates: dict) -> Optional[dict]:
    """Update user in database using asyncpg."""
    if not updates:
        return None

    conn = await db_connect(
        db_host=DBHOST,
        db_port=DBPORT,
        db_user=DBUSER,
        db_name=DEFAULT_DB
    )

    if not conn:
        return None

    try:
        # Build SET clause
        columns = sorted(updates.keys())
        values = [updates[col] for col in columns]

        set_clause = ", ".join(
            f"{col} = ${i + 1}" for i, col in enumerate(columns)
        )

        query = f"""
            UPDATE data.users
            SET {set_clause}
            WHERE id = ${len(columns) + 1}
            RETURNING *;
        """

        row = await conn.fetchrow(query, *values, user_id)

        if row:
            user = {k: serialize_value(v) for k, v in dict(row).items()}
            user.pop("password", None)
            return user
        return None
    finally:
        await conn.close()


async def delete_user_from_db(user_id: str) -> bool:
    """Delete user from database."""
    conn = await db_connect(
        db_host=DBHOST,
        db_port=DBPORT,
        db_user=DBUSER,
        db_name=DEFAULT_DB
    )

    if not conn:
        return False

    try:
        query = "DELETE FROM data.users WHERE id = $1 RETURNING id;"
        row = await conn.fetchrow(query, user_id)
        return row is not None
    finally:
        await conn.close()


@router.get("/me", response_model=APIResponse)
async def get_current_user_info(
    authorization: Optional[str] = Header(None),
):
    """Get current user information."""
    current_user = await get_current_user(authorization)
    return APIResponse(
        success=True,
        data=user_dict_to_response(current_user)
    )


@router.put("/me", response_model=APIResponse)
async def update_current_user(
    data: UserUpdate,
    authorization: Optional[str] = Header(None),
):
    """Update current user information."""
    current_user = await get_current_user(authorization)

    update_data = data.model_dump(exclude_unset=True, by_alias=False)

    if not update_data:
        return APIResponse(
            success=True,
            data=user_dict_to_response(current_user)
        )

    # Add last_updated timestamp
    update_data["last_updated"] = datetime.utcnow()

    updated_user = await update_user_in_db(current_user.get("id"), update_data)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

    return APIResponse(
        success=True,
        data=user_dict_to_response(updated_user)
    )


@router.delete("/me")
async def delete_current_user(
    authorization: Optional[str] = Header(None),
):
    """Delete current user account."""
    current_user = await get_current_user(authorization)

    success = await delete_user_from_db(current_user.get("id"))

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

    return APIResponse(
        success=True,
        data={"message": "Account deleted successfully"}
    )


@router.patch("/me/password", response_model=APIResponse)
async def change_password(
    data: ChangePasswordRequest,
    authorization: Optional[str] = Header(None),
):
    """Change current user's password."""
    current_user = await get_current_user(authorization)

    # Get user with password for verification
    user_with_password = await get_user_by_id(current_user.get("id"), include_password=True)

    if not user_with_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    stored_password = user_with_password.get("password")

    if not stored_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change password - no password set"
        )

    # Verify current password using bcrypt
    if not match_encrypted_text(data.current_password, stored_password, "bcrypt"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Update password with bcrypt hash
    new_password_hash = hash_text(data.new_password, "bcrypt")

    updated_user = await update_user_in_db(
        current_user.get("id"),
        {
            "password": new_password_hash,
            "last_updated": datetime.utcnow(),
        }
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )

    return APIResponse(
        success=True,
        data={"message": "Password changed successfully"}
    )


@router.patch("/me/avatar", response_model=APIResponse)
async def update_avatar(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
):
    """Update user avatar."""
    current_user = await get_current_user(authorization)

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

    # Update user photo URL
    photo_url = f"/static/avatars/{unique_filename}"

    updated_user = await update_user_in_db(
        current_user.get("id"),
        {
            "photo_url": photo_url,
            "last_updated": datetime.utcnow(),
        }
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update avatar"
        )

    return APIResponse(
        success=True,
        data={"avatarUrl": photo_url}
    )


@router.delete("/me/avatar", response_model=APIResponse)
async def delete_avatar(
    authorization: Optional[str] = Header(None),
):
    """Delete user avatar."""
    current_user = await get_current_user(authorization)

    # Delete old file if it exists
    photo_url = current_user.get("photo_url")
    if photo_url and photo_url.startswith("/static/avatars/"):
        old_filename = photo_url.split("/")[-1]
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "static", "avatars")
        old_file_path = os.path.join(upload_dir, old_filename)
        if os.path.exists(old_file_path):
            os.remove(old_file_path)

    updated_user = await update_user_in_db(
        current_user.get("id"),
        {
            "photo_url": None,
            "last_updated": datetime.utcnow(),
        }
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove avatar"
        )

    return APIResponse(
        success=True,
        data={"message": "Avatar removed successfully"}
    )
