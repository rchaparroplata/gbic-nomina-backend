from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from dependencies.database import Base
from main import app
from dependencies.database import get_db
from dependencies.users import get_current_user
from schemas.users import User

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False,
                                   autoflush=False,
                                   bind=engine)


# Dependency to override the get_db dependency in the main app
def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


fake_user_data = {
        'id_user': 1,
        'username': 'fakeuser',
        'nombre': 'Fake username',
        'scopes': ['fake'],
        'activo': True
    }


def ovrd_get_current_user(
        csecurity_scopes=[],
        token='',
        db=''
        ):
    return User(**fake_user_data)


def ovrd_get_current_user_inactive(
        security_scopes=[],
        token='',
        db=''
        ):
    fake_inactive = fake_user_data.copy()
    fake_inactive.update({'activo': False})
    return User(**fake_inactive)


app.dependency_overrides[get_db] = override_get_db


def setup() -> None:
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)


def teardown() -> None:
    # Drop the tables in the test database
    Base.metadata.drop_all(bind=engine)


def test_get_current_user_401():
    app.dependency_overrides = {}
    with TestClient(app) as client:
        response = client.get('/users/me')
        assert response.status_code == 401
        assert response.json() == {'detail': 'Not authenticated'}


def test_get_current_inactive_user():
    app.dependency_overrides[get_current_user] = ovrd_get_current_user_inactive
    with TestClient(app) as client:
        response = client.get('/users/me')
        assert response.status_code == 400
        assert response.json() == {'detail': 'User Inactive'}


def test_get_current_user():
    app.dependency_overrides[get_current_user] = ovrd_get_current_user
    with TestClient(app) as client:
        response = client.get('/users/me')
        assert response.status_code == 200
        assert response.json() == fake_user_data


def test_get_all_users_401():
    app.dependency_overrides = {}
    with TestClient(app) as client:
        response = client.get('/users')
        assert response.status_code == 401
        assert response.json() == {'detail': 'Not authenticated'}
