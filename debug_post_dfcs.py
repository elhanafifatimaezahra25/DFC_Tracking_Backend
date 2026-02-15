from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from sqlmodel.pool import StaticPool
from app.main import app
from app.database import get_session

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SQLModel.metadata.create_all(engine)
session = Session(engine)

def get_session_override():
    return session

app.dependency_overrides[get_session] = get_session_override
client = TestClient(app)

from app.core.security import get_password_hash, create_access_token
from app.models.user import User

user = User(matricule="TEST001", last_name="Test", first_name="User", email="test@example.com", role="admin", hashed_password=get_password_hash("testpass123"))
session.add(user)
session.commit()
session.refresh(user)

token = create_access_token(str(user.id))

resp = client.post(
    "/dfcs/",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "numero_dfc": 12345,
        "description": "Test DFC",
        "type_dfc": "T1",
        "statut": "ouvert",
        "date_reception": "2026-02-01T00:00:00",
        "faisabilite": "OG"
    }
)
print(resp.status_code)
try:
    print(resp.json())
except Exception as e:
    print('no json', e)
