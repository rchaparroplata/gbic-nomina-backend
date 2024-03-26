from datetime import timedelta

from fastapi.testclient import TestClient
from starlette import status

from dependencies.database import Base, get_db
from dependencies.users import create_access_token, create_user, encode_token
from main import app
from models.users import UserDB
from schemas.users import UserIn
from tests.core import engine, ovrd_get_db

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

false_user_data = {
        'username': 'No',
        'password': 'Existo',
        'nombre': 'Nunca Creado',
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
user_false = UserIn(**false_user_data)


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


def test_create_access_token():
    tkn = create_access_token(usr_access, theDb)
    assert tkn.token_type == 'bearer'


def test_get_current_user_401():
    with TestClient(app) as client:
        response = client.get('/users/me')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


def test_get_current_inactive_user():
    inactive_tkn = create_access_token(usr_inactive, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/users/me',
                              headers={
                                  'Authorization': 'Bearer '+inactive_tkn
                              })
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'Usuario Desactivado'}


def test_bad_token():
    bad_tkn = encode_token({'yes': 'yes'}, timedelta(minutes=20))
    with TestClient(app) as client:
        response = client.get('/users/me',
                              headers={
                                  'Authorization': 'Bearer '+bad_tkn
                              })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user():
    reader_tkn = create_access_token(usr_reader, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/users/me',
                              headers={
                                  'Authorization': 'Bearer '+reader_tkn
                              })
        assert response.status_code == status.HTTP_200_OK
        res_json = response.json()
        assert res_json['username'] == reader_user_data['username']
        assert res_json['nombre'] == reader_user_data['nombre']
        assert res_json['activo'] == reader_user_data['activo']


def test_get_all_users_401():
    with TestClient(app) as client:
        response = client.get('/users')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


def test_get_user_token():
    with TestClient(app) as client:
        response = client.post('/users/token', data={
            "username": admin_user_data.get('username'),
            "password": admin_user_data.get('password')})
        assert response.status_code == status.HTTP_200_OK


def test_get_user_token_false_user():
    with TestClient(app) as client:
        response = client.post('/users/token', data={
            "username": false_user_data.get('username'),
            "password": false_user_data.get('password')})
        res_json = response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert res_json == {'detail': 'Usuario y/o Password no validos'}


def test_get_user_token_wrong_pass():
    with TestClient(app) as client:
        response = client.post('/users/token', data={
            "username": access_user_data.get('username'),
            "password": false_user_data.get('password')})
        res_json = response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert res_json == {'detail': 'Usuario y/o Password no validos'}


def test_get_all_users_no_scope():
    access_tkn = create_access_token(usr_access, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/users',
                              headers={
                                  'Authorization': 'Bearer '+access_tkn
                              })
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'Sin Privilegios Necesarios'}


def test_get_all_users():
    reader_tkn = create_access_token(usr_reader, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/users',
                              headers={
                                  'Authorization': 'Bearer '+reader_tkn
                              })
        assert response.status_code == status.HTTP_200_OK
        res_json = response.json()
        assert len(res_json) == 6


def test_get_all_users_limit():
    reader_tkn = create_access_token(usr_reader, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/users?limit=2',
                              headers={
                                  'Authorization': 'Bearer '+reader_tkn
                              })
        assert response.status_code == status.HTTP_200_OK
        res_json = response.json()
        assert len(res_json) == 2


def test_get_all_users_admin():
    admin_tkn = create_access_token(usr_admin, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/users',
                              headers={
                                  'Authorization': 'Bearer '+admin_tkn
                              })
        assert response.status_code == status.HTTP_200_OK
        res_json = response.json()
        assert len(res_json) == 6


def test_create_user_401():
    with TestClient(app) as client:
        response = client.post('/users')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


def test_create_user():
    writer_tkn = create_access_token(usr_writer, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/users',
                               headers={
                                  'Authorization': 'Bearer '+writer_tkn
                                  },
                               json={
                                  'username': 'UserNew',
                                  'nombre': 'Usuario New',
                                  'password': 'EsUnSecreto',
                                  'scopes': ['empty']
                                })
        assert response.status_code == status.HTTP_201_CREATED
        res_json = response.json()
        assert res_json['username'] == 'UserNew'


def test_create_user_missing_field():
    writer_tkn = create_access_token(usr_writer, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/users',
                               headers={
                                  'Authorization': 'Bearer '+writer_tkn
                                  },
                               json={
                                  'nombre': 'Usuario New',
                                  'scopes': ['empty']
                                })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        res_json = response.json()
        assert res_json['detail'][0]['msg'] == 'Field required'
        assert res_json['detail'][0]['loc'] == ['body', 'username']


def test_deactivate_user():
    # Generate Token
    access_tkn = create_access_token(usr_access2, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/users/me',
                              headers={
                                  'Authorization': 'Bearer '+access_tkn
                              })
        assert response.status_code == status.HTTP_200_OK
        res_json = response.json()
        assert res_json['username'] == access2_user_data['username']
        # Edit DB to deActivate
        theDb.query(UserDB)\
            .filter(UserDB.username == access2_user_data['username'])\
            .update({'activo': False})
        theDb.commit()
        # Get /Me
        response = client.get('/users/me',
                              headers={
                                  'Authorization': 'Bearer '+access_tkn
                              })
        assert response.status_code == status.HTTP_403_FORBIDDEN
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
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_create_existing_user():
    writer_tkn = create_access_token(usr_writer, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/users',
                               headers={
                                  'Authorization': 'Bearer '+writer_tkn
                                  },
                               json={
                                  'username': 'Admin',
                                  'nombre': 'Usuario New',
                                  'password': 'EsUnSecreto',
                                  'scopes': ['empty']
                                })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        res_json = response.json()
        assert res_json['detail'] == 'Usuario ya existente'


def test_create_user_no_scope():
    access_tkn = create_access_token(usr_access, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/users',
                               headers={
                                  'Authorization': 'Bearer '+access_tkn
                               },
                               json={
                                  'username': 'UserNew',
                                  'nombre': 'Usuario New',
                                  'password': 'EsUnSecreto',
                                  'scopes': ['empty']
                                })
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'Sin Privilegios Necesarios'}


def test_edit_user():
    writer_tkn = create_access_token(usr_writer, theDb).access_token
    with TestClient(app) as client:
        response = client.put('/users/5',
                              headers={
                                  'Authorization': 'Bearer '+writer_tkn
                              },
                              json={
                                  'username': 'EditedUsername',
                                  'nombre': 'Edited User',
                                  'password': 'EsNuevoUnSecreto',
                                  'scopes': ['empty'],
                                  'activo': True
                              })
        assert response.status_code == status.HTTP_202_ACCEPTED
        res_json = response.json()
        assert res_json['username'] == 'EditedUsername'


def test_edit_user_no_password():
    writer_tkn = create_access_token(usr_writer, theDb).access_token
    with TestClient(app) as client:
        response = client.put('/users/5',
                              headers={
                                  'Authorization': 'Bearer '+writer_tkn
                              },
                              json={
                                  'username': 'EditedUsernameAgain',
                                  'nombre': 'Edited User',
                                  'scopes': ['empty'],
                                  'activo': True
                              })
        assert response.status_code == status.HTTP_202_ACCEPTED
        res_json = response.json()
        assert res_json['username'] == 'EditedUsernameAgain'


def test_edit_admin_not_allowed():
    writer_tkn = create_access_token(usr_writer, theDb).access_token
    with TestClient(app) as client:
        response = client.put('/users/1',
                              headers={
                                  'Authorization': 'Bearer '+writer_tkn
                              },
                              json={
                                  'username': 'Whatever',
                                  'nombre': 'Edited User',
                                  'scopes': ['empty'],
                                  'activo': True
                              })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        res_json = response.json()
        assert res_json == {'detail': 'No puedes editar al Administardor'}


def test_edit_user_no_scope():
    reader_tkn = create_access_token(usr_reader, theDb).access_token
    with TestClient(app) as client:
        response = client.put('/users/5',
                              headers={
                                  'Authorization': 'Bearer '+reader_tkn
                              },
                              json={
                                  'username': 'Whatever',
                                  'nombre': 'Edited User',
                                  'scopes': ['empty'],
                                  'activo': True
                              })
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'Sin Privilegios Necesarios'}


def test_edit_user_non_exist():
    writer_tkn = create_access_token(usr_writer, theDb).access_token
    with TestClient(app) as client:
        response = client.put('/users/100',
                              headers={
                                  'Authorization': 'Bearer '+writer_tkn
                              },
                              json={
                                  'username': 'Whatever',
                                  'nombre': 'Edited User',
                                  'scopes': ['empty'],
                                  'activo': True
                              })
        assert response.status_code == status.HTTP_404_NOT_FOUND
        res_json = response.json()
        assert res_json == {'detail': 'Usuario con id: 100 no encontrado'}
