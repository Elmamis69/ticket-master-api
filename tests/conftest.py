import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import Base, get_db
import json
from app.models.user import User, UserRole
from app.core.security import get_password_hash

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """
    Create a fresh database for each test.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Create a test client with database dependency override.
    """
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def user_token(client, db):
    """Crea un usuario normal y retorna su token JWT"""
    email = "user@example.com"
    password = "12345678"
    user = User(email=email, full_name="Usuario Test", password_hash=get_password_hash(password), role=UserRole.USER)
    db.add(user)
    db.commit()
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def admin_token(client, db):
    """Crea un admin y retorna su token JWT"""
    email = "admin@example.com"
    password = "adminpass"
    user = User(email=email, full_name="Admin Test", password_hash=get_password_hash(password), role=UserRole.ADMIN)
    db.add(user)
    db.commit()
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def agent_token(client, db):
    """Crea un agente y retorna su token JWT"""
    email = "agent@example.com"
    password = "agentpass"
    user = User(email=email, full_name="Agente Test", password_hash=get_password_hash(password), role=UserRole.AGENT)
    db.add(user)
    db.commit()
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def ticket_id(client, user_token):
    """Crea un ticket y retorna su id"""
    response = client.post(
        "/api/v1/tickets/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"title": "Ticket para comentarios", "description": "desc", "priority": "medium"}
    )
    return response.json()["id"]

@pytest.fixture(scope="function")
def comment_id(client, user_token, ticket_id):
    """Crea un comentario y retorna su id"""
    response = client.post(
        f"/api/v1/tickets/{ticket_id}/comments",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"content": "Comentario inicial"}
    )
    return response.json()["id"]

@pytest.fixture(scope="function")
def agent_id(db):
    """Crea y retorna el id de un agente"""
    user = User(email="agent2@example.com", full_name="Agente 2", password_hash=get_password_hash("agentpass2"), role=UserRole.AGENT)
    db.add(user)
    db.commit()
    return user.id
