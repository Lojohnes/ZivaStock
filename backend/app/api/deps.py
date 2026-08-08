from fastapi import Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.models.role import Role, Permission


def get_current_user_id(
    request: Request,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> int:
    """Get current user ID from JWT token.
    Accepts token via Authorization Bearer header OR ?token= query param.
    """
    raw_token: Optional[str] = None

    # 1. Try Authorization: Bearer <token> header (frontend)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        raw_token = auth_header[7:]

    # 2. Fall back to ?token= query param (Android app)
    if not raw_token and token:
        raw_token = token

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials not provided"
        )

    payload = decode_token(raw_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    return int(user_id)


def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> User:
    """Load the full current User with role + permissions eagerly joined."""
    user = (
        db.query(User)
        .options(joinedload(User.role).joinedload(Role.permissions))
        .filter(User.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")
    if user.is_locked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is locked")
    return user


def get_user_permissions(user: User) -> set:
    if not user.role:
        return set()
    return {p.name for p in user.role.permissions}


def require_permission(permission_name: str):
    """Dependency factory: raises 403 unless the current user's role grants
    the given permission (e.g. 'products.create')."""

    def _checker(current_user: User = Depends(get_current_user)) -> User:
        perms = get_user_permissions(current_user)
        if permission_name not in perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission_name}",
            )
        return current_user

    return _checker


def require_any_permission(*permission_names: str):
    """Dependency factory: raises 403 unless the current user has at least
    one of the given permissions."""

    def _checker(current_user: User = Depends(get_current_user)) -> User:
        perms = get_user_permissions(current_user)
        if not perms.intersection(permission_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission (any of): {', '.join(permission_names)}",
            )
        return current_user

    return _checker
