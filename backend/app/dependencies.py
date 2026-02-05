"""
FastAPI dependencies for authentication and authorization.
"""

from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.config import settings
from app.utils.database import get_db

security = HTTPBearer()


class CurrentUser:
    """Represents the currently authenticated user."""
    def __init__(self, id: str, email: str, role: str = "user", **kwargs):
        self.id = id
        self.email = email
        self.role = role
        for key, value in kwargs.items():
            setattr(self, key, value)


class PortcoAccess:
    """Represents portfolio company access permissions."""
    def __init__(self, portco_id: str, access_level: str = "read"):
        self.portco_id = portco_id
        self.access_level = access_level


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> CurrentUser:
    """
    Validate JWT token and return the current user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        email: str = payload.get("email", "")
        role: str = payload.get("role", "user")

        if user_id is None:
            raise credentials_exception

        return CurrentUser(id=user_id, email=email, role=role)

    except JWTError:
        raise credentials_exception


async def get_portco_access(
    portco_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> PortcoAccess:
    """
    Check if current user has access to the specified portfolio company.
    """
    # For now, grant access to all authenticated users
    # TODO: Implement actual access control logic
    return PortcoAccess(portco_id=portco_id, access_level="write")


def require_detailed_access(
    access: PortcoAccess = Depends(get_portco_access)
) -> PortcoAccess:
    """
    Require detailed (write) access to portfolio company.
    """
    if access.access_level not in ["write", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for this operation"
        )
    return access
