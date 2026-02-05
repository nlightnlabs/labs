"""Authentication API endpoints."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.utilities.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    validate_password_strength,
    generate_password_reset_token,
)
from app.utils.database import get_db
from app.models.user import User, UserRole
from app.models.session import Session as SessionModel
from app.models.password_reset_token import PasswordResetToken
from app.models.user_preferences import UserPreferences
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


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email address."""
    return db.query(User).filter(User.email == email).first()


def create_user_session(
    db: Session,
    user: User,
    request: Request,
    remember_me: bool = False
) -> tuple[str, str]:
    """Create a new user session with tokens."""
    access_token = create_access_token(str(user.id))

    refresh_expires = timedelta(days=30 if remember_me else settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(str(user.id), refresh_expires)

    # Create session record
    session = SessionModel(
        user_id=user.id,
        token=access_token,
        refresh_token=refresh_token,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        expires_at=datetime.utcnow() + refresh_expires,
    )
    db.add(session)
    db.commit()

    return access_token, refresh_token


@router.post("/register", response_model=APIResponse[TokenResponse])
async def register(
    data: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    # Check if email already exists
    existing_user = get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )

    # Validate password strength
    is_valid, error_msg = validate_password_strength(data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # Check terms acceptance
    if not data.accept_terms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must accept the terms and conditions"
        )

    # Create user
    user = User(
        email=data.email,
        password_hash=get_password_hash(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        role=UserRole.USER,
    )
    db.add(user)
    db.flush()

    # Create default preferences
    preferences = UserPreferences(user_id=user.id)
    db.add(preferences)
    db.commit()
    db.refresh(user)

    # Create session
    access_token, refresh_token = create_user_session(db, user, request)

    return APIResponse(
        success=True,
        data=TokenResponse(
            user=UserResponse.model_validate(user),
            token=access_token,
            refresh_token=refresh_token,
        )
    )


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens."""
    user = get_user_by_email(db, data.email)

    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account locked. Please try again later"
        )

    # Verify password
    if not user.password_hash or not verify_password(data.password, user.password_hash):
        # Increment failed attempts
        failed_attempts = int(user.failed_login_attempts or "0") + 1
        user.failed_login_attempts = str(failed_attempts)

        if failed_attempts >= settings.ACCOUNT_LOCKOUT_THRESHOLD:
            user.locked_until = datetime.utcnow() + timedelta(
                minutes=settings.ACCOUNT_LOCKOUT_DURATION_MINUTES
            )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Reset failed attempts and update last login
    user.failed_login_attempts = "0"
    user.locked_until = None
    user.last_login_at = datetime.utcnow()
    db.commit()

    # Create session
    access_token, refresh_token = create_user_session(db, user, request, data.remember_me)

    return APIResponse(
        success=True,
        data=TokenResponse(
            user=UserResponse.model_validate(user),
            token=access_token,
            refresh_token=refresh_token,
        )
    )


@router.post("/logout")
async def logout(db: Session = Depends(get_db)):
    """Logout user and invalidate session."""
    # In production, you would invalidate the token here
    return APIResponse(success=True, data={"message": "Logged out successfully"})


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Refresh access token."""
    payload = verify_refresh_token(data.refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Invalidate old session
    db.query(SessionModel).filter(
        SessionModel.refresh_token == data.refresh_token
    ).delete()

    # Create new session
    access_token, new_refresh_token = create_user_session(db, user, request)

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
    db: Session = Depends(get_db)
):
    """Request password reset email."""
    user = get_user_by_email(db, data.email)

    # Always return success to prevent email enumeration
    if user:
        # Create reset token
        token = generate_password_reset_token()
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(
                hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
            ),
        )
        db.add(reset_token)
        db.commit()

        # In production, send email with reset link
        # await send_password_reset_email(user.email, token)

    return APIResponse(
        success=True,
        data={"message": "If an account exists, a reset email has been sent"}
    )


@router.post("/reset-password", response_model=APIResponse)
async def reset_password(
    data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Reset password using token."""
    # Find valid reset token
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == data.token,
        PasswordResetToken.used_at.is_(None),
        PasswordResetToken.expires_at > datetime.utcnow(),
    ).first()

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Validate password strength
    is_valid, error_msg = validate_password_strength(data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # Update password
    user = reset_token.user
    user.password_hash = get_password_hash(data.password)
    reset_token.used_at = datetime.utcnow()

    # Invalidate all existing sessions
    db.query(SessionModel).filter(SessionModel.user_id == user.id).delete()

    db.commit()

    return APIResponse(
        success=True,
        data={"message": "Password has been reset successfully"}
    )


@router.post("/verify-email", response_model=APIResponse)
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """Verify email address."""
    # In production, implement email verification logic
    return APIResponse(
        success=True,
        data={"message": "Email verified successfully"}
    )
