from fastapi.testclient import TestClient
from starlette import status

from dependencies.database import Base, get_db
from dependencies.users import create_access_token, create_user
from main import app
from models.bancos import BancosDB
from schemas.users import UserIn
from tests.core import engine, ovrd_get_db

db_gen = ovrd_get_db()
theDb = next(db_gen)

banco_data = {
    'nombre': 'Banco Uno'
}

banco2_data = {
    'nombre': 'Banco Dos'
}

user_data = {
    'username': 'writer',
    'password': 'password',
    'nombre': 'name',
    'scopes': ['bancos:write', 'bancos:read']
}

no_scope_user_data = {
    'username': 'JustUser',
    'password': 'password',
    'nombre': 'name',
    'scopes': ['None']
}

usr = UserIn(**user_data)
usr_scope = UserIn(**no_scope_user_data)
banco = BancosDB(**banco_data)
banco2 = BancosDB(**banco2_data)


def setup():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = ovrd_get_db
    create_user(usr, theDb)
    create_user(usr_scope, theDb)
    theDb.add(banco)
    theDb.add(banco2)
    theDb.commit()
    theDb.refresh(banco)
    theDb.refresh(banco2)


def teardown():
    Base.metadata.drop_all(bind=engine)


def test_get_all_bancos():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/bancos',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              })
        res_json = response.json()
        assert response.status_code == 200
        assert len(res_json) == 2
        assert res_json[0]['nombre'] == 'Banco Uno'


def test_get_all_bancos_401():
    with TestClient(app) as client:
        response = client.get('/bancos')
        res_json = response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert res_json == {'detail': 'Not authenticated'}


def test_get_all_bancos_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/bancos',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_create_banco():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/bancos',
                               headers={
                                  'Authorization': 'Bearer '+tkn
                               },
                               json={
                                   'nombre': 'Banco Nuevo'
                               })
        res_json = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        assert res_json['nombre'] == 'Banco Nuevo'
        assert res_json['activo'] is True


def test_create_banco_401():
    with TestClient(app) as client:
        response = client.post('/bancos')
        res_json = response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert res_json == {'detail': 'Not authenticated'}


def test_create_banco_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/bancos',
                               headers={
                                   'Authorization': 'Bearer '+tkn
                               })
        res_json = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_create_banco_nombre_existente():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/bancos',
                               headers={
                                  'Authorization': 'Bearer '+tkn
                               },
                               json={
                                   'nombre': 'Banco Dos'
                               })
        res_json = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert res_json == {'detail': 'Banco con nombre Banco Dos '
                            'ya existente'}


def test_edit_banco():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/bancos/{banco2.id_banco}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                  'nombre': 'Banco Editado'
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert res_json['nombre'] == 'Banco Editado'
        assert res_json['id_banco'] == banco2.id_banco
        assert res_json['activo'] is True


def test_edit_banco_401():
    with TestClient(app) as client:
        response = client.put(f'/bancos/{banco2.id_banco}',
                              json={
                                  'nombre': 'Banco Editado'
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert res_json == {'detail': 'Not authenticated'}


def test_edit_banco_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/bancos/{banco2.id_banco}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                  'nombre': 'Banco Editado'
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_edit_banco_404():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put('/bancos/1000',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                  'nombre': 'Banco Editado'
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert res_json == {'detail': 'Banco con Id: 1000 no encontrado'}


def test_edit_banco_nombre():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/bancos/{banco2.id_banco}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                  'nombre': 'Banco Uno'
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert res_json == {'detail': 'Banco con nombre Banco Uno '
                            'ya existente'}


def test_edit_banco_deactivate_cascade():
    # TODO: Cuentas de ese banco pasen a desactivarse
    pass


def test_delete_banco_401():
    with TestClient(app) as client:
        response = client.delete('/bancos/1')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


def test_delete_banco_404():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.delete('/bancos/10000',
                                 headers={
                                     'Authorization': 'Bearer '+tkn
                                 })
        res_json = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert res_json == {'detail': 'Banco con id: 10000 no encontrado'}


def test_delete_banco_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.delete(f'/bancos/{banco.id_banco}',
                                 headers={
                                     'Authorization': 'Bearer '+tkn
                                 })
        res_json = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_delete_banco_activo():
    # si hay cuentas usandolo no poder borrar
    pass


def test_delete_banco():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.delete(f'/bancos/{banco.id_banco}',
                                 headers={
                                     'Authorization': 'Bearer '+tkn
                                 })
        banco_db = theDb\
            .query(BancosDB)\
            .filter(BancosDB.id_banco == banco.id_banco)\
            .first()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not banco_db
