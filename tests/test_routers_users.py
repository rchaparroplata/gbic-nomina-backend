from datetime import timedelta
from dependencies.database import Base, get_db
from dependencies.users import (
    create_user,
    create_access_token,
    encode_token
)
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from models.users import UserDB
from schemas.users import UserIn

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
def ovrd_get_db():
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()


db_gen = ovrd_get_db()
theDb = next(db_gen)

writer_user_data = {
        'username': 'writer',
        'password': 'IamPassword',
        'nombre': 'Writer Test User',
        'scopes': ['users:read', 'users:write'],
        'activo': True
    }

reader_user_data = {
        'username': 'reader',
        'password': 'IamPassword',
        'nombre': 'Reader Test User',
        'scopes': ['users:read'],
        'activo': True
    }

inactive_user_data = {
        'username': 'inactive',
        'password': 'IamPassword',
        'nombre': 'Inactive Test User',
        'scopes': ['noScope'],
        'activo': False
    }

access_user_data = {
        'username': 'access',
        'password': 'IamPassword',
        'nombre': 'Access Test User',
        'scopes': ['noScope'],
        'activo': True

    }
access2_user_data = {
        'username': 'access2',
        'password': 'IamPassword',
        'nombre': 'Access Two Test User',
        'scopes': ['noScope'],
        'activo': True
    }

admin_user_data = {
        'username': 'Admin',
        'password': 'IamPassword',
        'nombre': 'The Administrator',
        'scopes': ['Admin'],
        'activo': True
    }
usr_writer = UserIn(**writer_user_data)
usr_reader = UserIn(**reader_user_data)
usr_admin = UserIn(**admin_user_data)
usr_inactive = UserIn(**inactive_user_data)
usr_access = UserIn(**access_user_data)
usr_access2 = UserIn(**access2_user_data)


def setup() -> None:
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = ovrd_get_db
    create_user(usr_admin, theDb)
    create_user(usr_writer, theDb)
    create_user(usr_reader, theDb)
    create_user(usr_inactive, theDb)
    create_user(usr_access, theDb)
    create_user(usr_access2, theDb)


def teardown() -> None:
    # Drop the tables in the test database
    Base.metadata.drop_all(bind=engine)


def test_get_current_user_401():
    with TestClient(app) as client:
        response = client.get('/users/me')
        assert response.status_code == 401
        assert response.json() == {'detail': 'Not authenticated'}


def test_get_current_inactive_user():
    inactive_tkn = create_access_token(usr_inactive, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/users/me',
                              headers={
                                  'Authorization': 'Bearer '+inactive_tkn
                              })
        assert response.status_code == 400
        assert response.json() == {'detail': 'Usuario Desactivado'}


def test_get_current_user():
    reader_tkn = create_access_token(usr_reader, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/users/me',
                              headers={
                                  'Authorization': 'Bearer '+reader_tkn
                              })
        assert response.status_code == 200
        res_json = response.json()
        assert res_json['username'] == reader_user_data['username']
        assert res_json['nombre'] == reader_user_data['nombre']
        assert res_json['activo'] == reader_user_data['activo']


def test_get_all_users_401():
    with TestClient(app) as client:
        response = client.get('/users')
        assert response.status_code == 401
        assert response.json() == {'detail': 'Not authenticated'}


def test_get_user_token():
    with TestClient(app) as client:
        response = client.post('/users/token', data={
            "username": admin_user_data.get('username'),
            "password": admin_user_data.get('password')})
        assert response.status_code == 200


def test_get_all_users_no_scope():
    access_tkn = create_access_token(usr_access, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/users',
                              headers={
                                  'Authorization': 'Bearer '+access_tkn
                              })
        assert response.status_code == 401
        assert response.json() == {'detail': 'Sin Privilegios Necesarios'}


def test_get_all_users():
    access_tkn = create_access_token(usr_reader, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/users',
                              headers={
                                  'Authorization': 'Bearer '+access_tkn
                              })
        assert response.status_code == 200
        res_json = response.json()
        assert len(res_json) == 6


def test_get_all_users_limit():
    access_tkn = create_access_token(usr_reader, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/users?limit=2',
                              headers={
                                  'Authorization': 'Bearer '+access_tkn
                              })
        assert response.status_code == 200
        res_json = response.json()
        assert len(res_json) == 2


def test_get_all_users_admin():
    access_tkn = create_access_token(usr_admin, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/users',
                              headers={
                                  'Authorization': 'Bearer '+access_tkn
                              })
        assert response.status_code == 200
        res_json = response.json()
        assert len(res_json) == 6


def test_create_user():
    pass


def test_deactivate_user():
    # Generate Token
    access_tkn = create_access_token(usr_access2, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/users/me',
                              headers={
                                  'Authorization': 'Bearer '+access_tkn
                              })
        assert response.status_code == 200
        res_json = response.json()
        assert res_json['username'] == access2_user_data['username']
        # Edit DB to deActivate
        theDb.query(UserDB)\
            .filter(UserDB.username == access2_user_data['username'])\
            .update({'activo': False})
        # Get /Me
        response = client.get('/users/me',
                              headers={
                                  'Authorization': 'Bearer '+access_tkn
                              })
        assert response.status_code == 400
        assert response.json() == {'detail': 'Usuario Desactivado'}
    pass


def test_valid_token_invalid_user():
    token = encode_token({
        "username": 'NoExiste',
        "id": 1,
        "nombre": 'No existente',
        "scopes": 'user.scopes'
    }, timedelta(minutes=20))
    with TestClient(app) as client:
        response = client.get('/users/me',
                              headers={
                                  'Authorization': 'Bearer '+token
                              })
        assert response.status_code == 401
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_create_existing_user():
    pass


def test_create_user_no_scope():
    pass


def test_edit_user():
    pass


def test_edit_user_no_scope():
    pass
