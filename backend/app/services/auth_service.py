from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, TokenResponse, UserWithRole
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.core.config import settings
from typing import Optional
from datetime import timedelta


class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password. Locks the account after
        5 consecutive failed attempts (unlocked via admin reset)."""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if user.is_locked or not user.is_active:
            return None
        if not verify_password(password, user.password_hash):
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= 5:
                user.is_locked = True
            self.db.commit()
            return None
        user.failed_login_attempts = 0
        self.db.commit()
        return user
    
    def create_tokens(self, user: User) -> TokenResponse:
        """Create access and refresh tokens for user"""
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )

        # Load user with role
        user_with_role = self.db.query(User).filter(User.id == user.id).first()
        role = self.db.query(Role).filter(Role.id == user_with_role.role_id).first()
        permission_names = [p.name for p in role.permissions] if role else []

        user_response = UserWithRole(
            id=user_with_role.id,
            uuid=user_with_role.uuid,
            email=user_with_role.email,
            first_name=user_with_role.first_name,
            last_name=user_with_role.last_name,
            phone_number=user_with_role.phone_number,
            profile_picture=user_with_role.profile_picture,
            role_id=user_with_role.role_id,
            is_active=user_with_role.is_active,
            is_locked=user_with_role.is_locked,
            last_login_at=user_with_role.last_login_at,
            created_at=user_with_role.created_at,
            updated_at=user_with_role.updated_at,
            role=role,
            permissions=permission_names,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if email already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # Check if role exists
        role = self.db.query(Role).filter(Role.id == user_data.role_id).first()
        if not role:
            raise ValueError("Role not found")
        
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone_number=user_data.phone_number,
            role_id=user_data.role_id,
            is_active=True
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_current_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
