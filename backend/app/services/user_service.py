from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role, Permission, RolePermission
from app.schemas.user import UserUpdate
from app.schemas.role import RoleCreate, RoleUpdate
from app.core.security import get_password_hash
from typing import Optional, List
from datetime import datetime


class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_users(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        role_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> tuple[List[User], int]:
        """Get users with pagination and filters"""
        query = self.db.query(User)
        
        if role_id:
            query = query.filter(User.role_id == role_id)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (User.first_name.ilike(search_pattern)) |
                (User.last_name.ilike(search_pattern)) |
                (User.email.ilike(search_pattern))
            )
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        
        return users, total
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user"""
        user = self.get_user(user_id)
        if not user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def update_last_login(self, user_id: int, ip_address: Optional[str] = None):
        """Update user's last login timestamp"""
        user = self.get_user(user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            if ip_address:
                user.last_login_ip = ip_address
            self.db.commit()

    def unlock_user(self, user_id: int) -> Optional[User]:
        """Unlock a locked user account and reset failed attempts"""
        user = self.get_user(user_id)
        if not user:
            return None
        user.is_locked = False
        user.failed_login_attempts = 0
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """Get all permissions for a user"""
        user = self.get_user(user_id)
        if not user:
            return []

        permissions = self.db.query(Permission).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).join(
            Role, RolePermission.role_id == Role.id
        ).filter(Role.id == user.role_id).all()

        return [perm.name for perm in permissions]

    def reset_password(self, user_id: int, new_password: str) -> Optional[User]:
        """Reset a user's password"""
        user = self.get_user(user_id)
        if not user:
            return None
        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_roles(self) -> List[Role]:
        """Get all roles"""
        return self.db.query(Role).order_by(Role.id).all()

    def create_role(self, role_data: RoleCreate) -> Role:
        """Create a new (non-system) role"""
        existing = self.db.query(Role).filter(Role.name == role_data.name).first()
        if existing:
            raise ValueError("Role name already exists")
        role = Role(name=role_data.name, description=role_data.description, is_system=False)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def update_role(self, role_id: int, role_data: RoleUpdate) -> Optional[Role]:
        """Update a role's name/description (system roles' names are protected)"""
        role = self.get_role(role_id)
        if not role:
            return None
        update_data = role_data.model_dump(exclude_unset=True)
        if role.is_system and "name" in update_data:
            raise ValueError("Cannot rename a system role")
        for field, value in update_data.items():
            setattr(role, field, value)
        self.db.commit()
        self.db.refresh(role)
        return role

    def delete_role(self, role_id: int) -> bool:
        """Delete a non-system role"""
        role = self.get_role(role_id)
        if not role:
            return False
        if role.is_system:
            raise ValueError("Cannot delete a system role")
        self.db.delete(role)
        self.db.commit()
        return True

    def get_role(self, role_id: int) -> Optional[Role]:
        """Get role by ID with permissions"""
        return self.db.query(Role).filter(Role.id == role_id).first()

    def get_permissions(self) -> List[Permission]:
        """Get all permissions"""
        return self.db.query(Permission).order_by(Permission.name).all()

    def set_role_permissions(self, role_id: int, permission_ids: List[int]) -> Optional[Role]:
        """Set permissions for a role"""
        role = self.get_role(role_id)
        if not role:
            return None
        self.db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
        for perm_id in permission_ids:
            self.db.add(RolePermission(role_id=role_id, permission_id=perm_id))
        self.db.commit()
        self.db.refresh(role)
        return role
