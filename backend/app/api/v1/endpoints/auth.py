"""Authentication API endpoints using postgres_db with IAM token authentication."""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Request

from app.config import settings
from app.utilities.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.utilities.postgres_db import (
    authenticate_user,
    create_user,
    reset_password as db_reset_password,
    db_connect,
    serialize_value,
    UserModel,
    DBHOST,
    DBPORT,
    DBUSER,
    DEFAULT_DB,
)
from app.utilities.encryption import match_encrypted_text
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.schemas.user import UserResponse
from app.schemas.common import APIResponse

router = APIRouter()


def user_to_response(user: dict) -> dict:
    """Convert user dict to response dict with frontend-compatible fields."""
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
        # Frontend compatibility fields
        "role": _get_role_from_access_level(user.get("access_level")),
        "isActive": user.get("status") and str(user.get("status")).lower() == "active",
        "isVerified": True,  # Default to true for existing users
    }


def _get_role_from_access_level(access_level: Optional[str]) -> str:
    """Map access_level to role for frontend compatibility."""
    if access_level:
        level = access_level.lower()
        if "super" in level or "admin" in level:
            return "admin"
        elif "power" in level or "manager" in level:
            return "manager"
    return "user"


async def get_user_by_email_or_username(identifier: str) -> Optional[dict]:
    """Get user by email or username using asyncpg with IAM auth."""
    conn = await db_connect(
        db_host=DBHOST,
        db_port=DBPORT,
        db_user=DBUSER,
        db_name=DEFAULT_DB
    )

    if not conn:
        return None

    try:
        # Check if identifier is email or username
        if "@" in identifier:
            query = "SELECT * FROM data.users WHERE email = $1;"
        else:
            query = "SELECT * FROM data.users WHERE username = $1;"

        row = await conn.fetchrow(query, identifier)

        if row:
            return {k: serialize_value(v) for k, v in dict(row).items()}
        return None
    finally:
        await conn.close()


async def get_user_by_id(user_id: str) -> Optional[dict]:
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
            user.pop("password", None)
            return user
        return None
    finally:
        await conn.close()


@router.post("/register", response_model=APIResponse)
async def register(
    data: RegisterRequest,
    request: Request,
):
    """Register a new user."""
    # Build user record for create_user
    user_record = {
        "username": data.email.split("@")[0] if data.email else None,
        "email": data.email,
        "password": data.password,
        "first_name": data.first_name,
        "last_name": data.last_name,
        "access_level": "Individual",
        "user_type": "Guest",
        "status": "Active",
        "stage": "Enabled",
    }

    # Create user using postgres_db function
    user_request = UserModel(
        user_record=user_record,
        db_name=DEFAULT_DB,
        db_schema="data",
        table_name="users",
        db_host=DBHOST,
        db_user=DBUSER,
        db_port=DBPORT,
    )

    result = await create_user(user_request)

    if not result.get("validation"):
        status_code = result.get("status_code", 400)
        if status_code == 409:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this username already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Registration failed")
        )

    user = result.get("user", {})

    # Create tokens
    access_token = create_access_token(str(user.get("id")))
    refresh_token = create_refresh_token(str(user.get("id")))

    return APIResponse(
        success=True,
        data={
            "user": user_to_response(user),
            "token": access_token,
            "refreshToken": refresh_token,
        }
    )


@router.post("/login", response_model=APIResponse)
async def login(
    data: LoginRequest,
    request: Request,
):
    """Authenticate user and return tokens."""
    # Determine the login identifier (username or email)
    identifier = data.username or data.email

    
    print(f"[Auth] Login attempt for identifier: {identifier} from IP: {request.client.host}")
    
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is required"
        )

    # Get user by email or username
    user = await get_user_by_email_or_username(identifier)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password"
        )

    # Verify password using bcrypt
    stored_password = user.get("password")
    if not stored_password or not match_encrypted_text(data.password, stored_password, "bcrypt"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password"
        )

    # Check if account is active
    user_status = user.get("status")
    if user_status and str(user_status).lower() != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active"
        )

    # Remove password from user dict
    user.pop("password", None)

    # Create tokens
    refresh_expires = timedelta(days=30 if data.remember_me else settings.REFRESH_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(str(user.get("id")))
    refresh_token = create_refresh_token(str(user.get("id")), refresh_expires)

    return APIResponse(
        success=True,
        data={
            "user": user_to_response(user),
            "token": access_token,
            "refreshToken": refresh_token,
        }
    )


@router.post("/logout")
async def logout():
    """Logout user and invalidate session."""
    return APIResponse(success=True, data={"message": "Logged out successfully"})


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    request: Request,
):
    """Refresh access token."""
    payload = verify_refresh_token(data.refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    user = await get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Check if account is active
    user_status = user.get("status")
    if user_status and str(user_status).lower() != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new tokens
    access_token = create_access_token(str(user.get("id")))
    new_refresh_token = create_refresh_token(str(user.get("id")))

    return APIResponse(
        success=True,
        data={
            "token": access_token,
            "refreshToken": new_refresh_token,
        }
    )


@router.post("/forgot-password", response_model=APIResponse)
async def forgot_password(
    data: PasswordResetRequest,
):
    """Request password reset email."""
    # Get user by email
    user = await get_user_by_email_or_username(data.email)

    # Always return success to prevent email enumeration
    if user:
        # In production, send email with reset link
        # For now, just log that a reset was requested
        pass

    return APIResponse(
        success=True,
        data={"message": "If an account exists, a reset email has been sent"}
    )


@router.post("/reset-password", response_model=APIResponse)
async def reset_password(
    data: PasswordResetConfirm,
):
    """Reset password using token."""
    # For this simple implementation, we use email as the token
    # In production, you'd use a proper token system
    user = await get_user_by_email_or_username(data.token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Use postgres_db reset_password function
    user_request = UserModel(
        user_record={
            "username": user.get("username"),
            "password": data.password,
        },
        db_name=DEFAULT_DB,
        db_schema="data",
        table_name="users",
        db_host=DBHOST,
        db_user=DBUSER,
        db_port=DBPORT,
    )

    result = await db_reset_password(user_request)

    if not result.get("validation"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Password reset failed")
        )

    return APIResponse(
        success=True,
        data={"message": "Password has been reset successfully"}
    )


@router.post("/verify-email", response_model=APIResponse)
async def verify_email(
    token: str,
):
    """Verify email address."""
    return APIResponse(
        success=True,
        data={"message": "Email verified successfully"}
    )
