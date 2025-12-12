"""
Tests for authentication endpoints.

Run with: docker-compose exec api pytest tests/test_auth.py -v
"""
import pytest
from fastapi.testclient import TestClient
from app.models.user import User, UserRole
from app.core.security import get_password_hash


def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "testpass123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email(client, db):
    """Test registration with duplicate email"""
    # Create a user first
    user = User(
        email = "existing@example.com",
        full_name="Existing User",
        password_hash=get_password_hash("password123"),
        role=UserRole.USER
    )
    db.add(user)
    db.commit()
    
    # Try to register with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "existing@example.com",
            "full_name": "Another User",
            "password": "testpass123"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client, db):
    """Test successful login"""
    # Create a user
    user = User(
        email = "testuser@example.com",
        full_name="Test User",
        password_hash=get_password_hash("testpass123"),
        role=UserRole.USER
    )
    db.add(user)
    db.commit()
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, db):
    """Test login with wrong password"""
    # Create a user
    user = User(
        email = "testuser@example.com",
        full_name="Test User",
        password_hash=get_password_hash("correctpass"),
        role=UserRole.USER
    )
    db.add(user)
    db.commit()
    
    # Try to login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser@example.com",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "somepass"
        }
    )
    assert response.status_code == 401


def test_get_current_user(client, db):
    """Test getting current user info"""
    # Create a user
    user = User(
        email = "testuser@example.com",
        full_name="Test User",
        password_hash=get_password_hash("testpass123"),
        role=UserRole.USER
    )
    db.add(user)
    db.commit()
    
    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser@example.com",
            "password": "testpass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["full_name"] == "Test User"


def test_get_current_user_no_token(client):
    """Test getting current user without token"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token"""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
