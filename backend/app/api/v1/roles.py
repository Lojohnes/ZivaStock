from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.role import RoleResponse, PermissionResponse, RoleWithPermissions, RolePermissionsUpdate, RoleCreate, RoleUpdate
from app.schemas.common import MessageResponse
from app.services.user_service import UserService
from app.models.user import User
from app.api.deps import get_current_user_id, require_permission

router = APIRouter()


@router.get("", response_model=List[RoleWithPermissions])
def get_roles(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    """Get all roles with their permissions"""
    user_service = UserService(db)
    roles = user_service.get_roles()
    return roles


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("roles.create")),
):
    """Create a new role (requires roles.create permission)"""
    user_service = UserService(db)
    try:
        return user_service.create_role(role_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("roles.update")),
):
    """Update a role (requires roles.update permission)"""
    user_service = UserService(db)
    try:
        role = user_service.update_role(role_id, role_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


@router.delete("/{role_id}")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("roles.delete")),
):
    """Delete a non-system role (requires roles.delete permission)"""
    user_service = UserService(db)
    try:
        success = user_service.delete_role(role_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return {"message": "Role deleted successfully"}


@router.get("/{role_id}", response_model=RoleWithPermissions)
def get_role(role_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    """Get role by ID with permissions"""
    user_service = UserService(db)
    role = user_service.get_role(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


@router.get("/permissions/all", response_model=List[PermissionResponse])
def get_permissions(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    """Get all available permissions"""
    user_service = UserService(db)
    permissions = user_service.get_permissions()
    return permissions


@router.put("/{role_id}/permissions", response_model=MessageResponse)
def update_role_permissions(
    role_id: int,
    update_data: RolePermissionsUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("roles.update")),
):
    """Update permissions for a role (requires roles.update permission)"""
    user_service = UserService(db)
    role = user_service.set_role_permissions(role_id, update_data.permission_ids)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return {"message": "Role permissions updated successfully"}
