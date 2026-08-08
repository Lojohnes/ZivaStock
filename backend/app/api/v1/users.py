from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserWithRole, PasswordResetRequest
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.models.role import Role
from app.models.user import User
from app.api.deps import get_current_user_id, get_current_user, require_permission

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("users.create")),
):
    """Create a new user (requires users.create permission)"""
    auth_service = AuthService(db)
    try:
        user = auth_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=PaginatedResponse[UserResponse])
def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get users with pagination"""
    user_service = UserService(db)
    skip = (page - 1) * limit
    users, total = user_service.get_users(skip=skip, limit=limit, role_id=role_id, search=search)
    pages = (total + limit - 1) // limit
    
    return PaginatedResponse(
        items=users,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.get("/{user_id}", response_model=UserWithRole)
def get_user(user_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    """Get user by ID"""
    user_service = UserService(db)
    user = user_service.get_user(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    role = db.query(Role).filter(Role.id == user.role_id).first()
    permission_names = [p.name for p in role.permissions] if role else []

    return UserWithRole(
        id=user.id,
        uuid=user.uuid,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        role_id=user.role_id,
        is_active=user.is_active,
        is_locked=user.is_locked,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
        role=role,
        permissions=permission_names,
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("users.update")),
):
    """Update user (requires users.update permission)"""
    user_service = UserService(db)
    user = user_service.update_user(user_id, user_data)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("users.delete")),
):
    """Delete user (requires users.delete permission)"""
    user_service = UserService(db)
    success = user_service.delete_user(user_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"message": "User deleted successfully"}


@router.post("/{user_id}/unlock", response_model=UserResponse)
def unlock_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("users.update")),
):
    """Unlock a locked user account (requires users.update permission)"""
    user_service = UserService(db)
    user = user_service.unlock_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/{user_id}/reset-password", response_model=MessageResponse)
def reset_user_password(
    user_id: int,
    reset_data: PasswordResetRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("users.update")),
):
    """Reset a user's password (requires users.update permission)"""
    user_service = UserService(db)
    user = user_service.reset_password(user_id, reset_data.new_password)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"message": "Password reset successfully"}
