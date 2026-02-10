"""API v1 router configuration."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    settings,
    notifications,
    files,
    portcos,
    me,
    billing,
    analysis,
    data,
    tenant,
    tables,
    chats,
)

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(me.router, prefix="/me", tags=["Current User"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(data.router, prefix="/data", tags=["Data Tables"])
api_router.include_router(tables.router, prefix="/tables", tags=["Generic Tables CRUD"])
api_router.include_router(tenant.router, prefix="/tenant", tags=["Tenant Configuration"])
api_router.include_router(chats.router, prefix="/chats", tags=["Chat"])
