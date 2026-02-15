"""
Unit tests for the Hilo backend API.
Tests cover: auth, DFC CRUD, and dashboard functionality.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from datetime import datetime, timedelta

# Import the app and models
from app.main import app
from app.database import get_session
from app.models.user import User
from app.models.dfc import DFC
from app.core.security import get_password_hash, create_access_token


# Setup test database
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a test user."""
    user = User(
        matricule="TEST001",
        last_name="Test",
        first_name="User",
        email="test@example.com",
        role="admin",
        hashed_password=get_password_hash("testpass123")
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_token")
def test_token_fixture(test_user: User):
    """Create a test JWT token."""
    return create_access_token(subject=test_user.id)


class TestAuth:
    """Test authentication endpoints."""
    
    def test_register_success(self, client: TestClient):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={
                "matricule": "NEW001",
                "last_name": "New",
                "first_name": "User",
                "email": "new@example.com",
                "password": "securepass123"
            }
        )
        assert response.status_code == 200
        assert response.json()["user"]["matricule"] == "NEW001"
    
    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login."""
        response = client.post(
            "/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.json()


class TestDFC:
    """Test DFC CRUD operations."""
    
    def test_create_dfc_success(self, client: TestClient, test_token: str):
        """Test successful DFC creation."""
        response = client.post(
            "/dfcs/",
            headers={"Authorization": f"Bearer {test_token}"},
            json={
                "numero_dfc": 12345,
                "description": "Test DFC",
                "type_dfc": "T1",
                "statut": "ouvert",
                "date_reception": "2026-02-01T00:00:00",
                "faisabilite": "OG"
            }
        )
        assert response.status_code == 201
        assert response.json()["numero_dfc"] == 12345
    
    def test_create_dfc_missing_numero(self, client: TestClient, test_token: str):
        """Test DFC creation without numero_dfc."""
        response = client.post(
            "/dfcs/",
            headers={"Authorization": f"Bearer {test_token}"},
            json={
                "description": "Test DFC",
                "type_dfc": "T1"
            }
        )
        assert response.status_code == 400
    
    def test_list_dfcs(self, client: TestClient, test_token: str):
        """Test listing DFCs."""
        response = client.get(
            "/dfcs/",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_update_dfc_success(
        self,
        client: TestClient,
        test_token: str,
        session: Session
    ):
        """Test successful DFC update."""
        # Create a DFC first
        dfc = DFC(
            numero_dfc=99999,
            description="Original",
            statut="ouvert"
        )
        session.add(dfc)
        session.commit()
        session.refresh(dfc)
        
        # Update it
        response = client.put(
            f"/dfcs/{dfc.id}",
            headers={"Authorization": f"Bearer {test_token}"},
            json={
                "description": "Updated",
                "statut": "ferme"
            }
        )
        assert response.status_code == 200
        assert response.json()["description"] == "Updated"
    
    def test_delete_dfc_success(
        self,
        client: TestClient,
        test_token: str,
        session: Session
    ):
        """Test successful DFC deletion."""
        # Create a DFC first
        dfc = DFC(numero_dfc=88888, statut="ouvert")
        session.add(dfc)
        session.commit()
        session.refresh(dfc)
        
        # Delete it
        response = client.delete(
            f"/dfcs/{dfc.id}",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 204


class TestDashboard:
    """Test dashboard endpoints."""
    
    def test_admin_dashboard_access(self, client: TestClient, test_token: str):
        """Test admin dashboard access with valid token."""
        response = client.get(
            "/admin/dashboard",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "statistics" in data
        assert data["summary"]["total_dfc"] >= 0
    
    def test_dashboard_metrics(
        self,
        client: TestClient,
        test_token: str,
        session: Session
    ):
        """Test that dashboard metrics are calculated correctly."""
        # Create test DFCs
        dfc1 = DFC(
            numero_dfc=11111,
            description="Open DFC",
            statut="ouvert",
            type_dfc="T1"
        )
        dfc2 = DFC(
            numero_dfc=22222,
            description="Closed DFC",
            statut="ferme",
            type_dfc="T2",
            date_reception=datetime.now(),
            date_reponse=datetime.now() + timedelta(days=5)
        )
        session.add_all([dfc1, dfc2])
        session.commit()
        
        response = client.get(
            "/admin/dashboard",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["open_dfc"] >= 1
        assert data["summary"]["closed_dfc"] >= 1
