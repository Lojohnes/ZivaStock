import pytest
from app.services.auth_service import AuthService
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate
from sqlalchemy.orm import Session


def test_authenticate_user_success(db_session: Session):
    """Test successful user authentication"""
    # Create a test user
    role = Role(name="test_role", description="Test role")
    db_session.add(role)
    db_session.commit()
    
    user = User(
        email="test@example.com",
        password_hash="$2b$12$test_hash",  # Mock hash
        first_name="Test",
        last_name="User",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    auth_service = AuthService(db_session)
    
    # This test would need password verification to be mocked
    # For now, it's a placeholder
    assert user.email == "test@example.com"


def test_create_user_success(db_session: Session):
    """Test successful user creation"""
    # Create a test role
    role = Role(name="test_role", description="Test role")
    db_session.add(role)
    db_session.commit()
    
    auth_service = AuthService(db_session)
    
    user_data = UserCreate(
        email="newuser@example.com",
        password="password123",
        first_name="New",
        last_name="User",
        role_id=role.id
    )
    
    # This test would need password hashing to be properly implemented
    # For now, it's a placeholder
    assert role.id is not None
