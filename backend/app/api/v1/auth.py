from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.schemas.user import LoginRequest, TokenResponse, RefreshTokenRequest, UserWithRole, RegisterRequest, UserCreate
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user (assigned to first available role)"""
    from app.models.role import Role
    role = db.query(Role).order_by(Role.id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No roles configured. Please seed the database first."
        )
    auth_service = AuthService(db)
    try:
        user_data = UserCreate(
            email=register_data.email,
            first_name=register_data.first_name,
            last_name=register_data.last_name,
            password=register_data.password,
            role_id=role.id
        )
        user = auth_service.create_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return auth_service.create_tokens(user)


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Authenticate user and return tokens"""
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(login_data.email, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password, or account locked"
        )

    # Update last login
    user_service = UserService(db)
    user_service.update_last_login(user.id, ip_address=request.client.host if request.client else None)

    return auth_service.create_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    payload = decode_token(refresh_data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    auth_service = AuthService(db)
    user = auth_service.get_current_user(int(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return auth_service.create_tokens(user)


@router.post("/logout")
def logout():
    """Logout user (client-side token invalidation)"""
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserWithRole)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user (role + permissions eagerly loaded)"""
    permission_names = [p.name for p in current_user.role.permissions] if current_user.role else []
    return UserWithRole(
        id=current_user.id,
        uuid=current_user.uuid,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone_number=current_user.phone_number,
        role_id=current_user.role_id,
        is_active=current_user.is_active,
        is_locked=current_user.is_locked,
        last_login_at=current_user.last_login_at,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        role=current_user.role,
        permissions=permission_names,
    )
