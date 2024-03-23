from datetime import date

from fastapi.testclient import TestClient
from starlette import status

from dependencies.database import Base, get_db
from dependencies.users import create_access_token, create_user
from main import app
from models.colonias import ColoniaDB
from models.empleados import EmpleadoDB
from models.salarios import SalariosDB
from schemas.users import UserIn
from tests.core import engine, ovrd_get_db

db_gen = ovrd_get_db()
theDb = next(db_gen)

colonia_data = {
    'nombre': 'La Colonia',
    'estado': 'Estado',
    'ciudad': 'Ciudad',
    'cp': '00000'
}

empleado_data = {
    "nombre": "Nombre",
    "paterno": "Paterno",
    "materno": "Materno",
    "rfc": "RFC000XXX",
    "curp": "CURPXXX000",
    "calle": "Calle",
    "exterior": "200",
    "id_colonia": 1,
    "celular": "1231232132",
}

user_data = {
    'username': 'writer',
    'password': 'password',
    'nombre': 'name',
    'scopes': ['salarios:writer', 'salarios:reader']
}

no_scope_user_data = {
    'username': 'JustUser',
    'password': 'password',
    'nombre': 'name',
    'scopes': ['None']
}

salario_data = {
    'fecha_valido': date(2024, 3, 1),
    'monto': 1000,
    'id_empleado': 1,
    'id_usuario': 1
}

usr = UserIn(**user_data)
usr_scope = UserIn(**no_scope_user_data)
empleado = EmpleadoDB(**empleado_data)
colonia = ColoniaDB(**colonia_data)
salario = SalariosDB(**salario_data)


def setup():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = ovrd_get_db
    create_user(usr, theDb)
    create_user(usr_scope, theDb)
    theDb.add(colonia)
    theDb.add(empleado)
    theDb.add(salario)
    theDb.commit()
    theDb.refresh(salario)


def teardown():
    Base.metadata.drop_all(bind=engine)


def test_get_all_salarios():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/salarios',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert len(res_json) == 1
        assert res_json[0]['monto'] == 1000


def test_get_all_salarios_401():
    with TestClient(app) as client:
        response = client.get('/salarios')
        res_json = response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert res_json == {'detail': 'Not authenticated'}


def test_get_all_salarios_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/salarios',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_edit_salario_fecha_mayor():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/salarios/{salario.id_salario}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                  'fecha_valido': '2024-02-01',
                                  'monto': 1010.00,
                                  'id_empleado': empleado.id_empleado,
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert res_json['detail'] ==\
            f'La fecha de inicio debe ser mayor a {salario.fecha_valido}'


def test_edit_salario():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/salarios/{salario.id_salario}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                  'fecha_valido': '2024-04-01',
                                  'monto': 1010.00,
                                  'id_empleado': empleado.id_empleado,
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert res_json['monto'] == 1010.00
        theDb.refresh(salario)


def test_edit_salario_404():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put('/salarios/10000',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                  'fecha_valido': '2024-02-01',
                                  'monto': 1010.00,
                                  'id_empleado': empleado.id_empleado,
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert res_json == {'detail': 'Salario con id: 10000 no encontrado'}


def test_edit_salario_401():
    with TestClient(app) as client:
        response = client.put('/salarios/1')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


def test_edit_salario_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/salarios/{salario.id_salario}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={})
        res_json = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_edit_salario_fields():
    # id_empleado remains the same
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        fecha = salario.fecha_valido.isoformat()
        response = client.put(f'/salarios/{salario.id_salario}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                  'fecha_valido': fecha,
                                  'monto': salario.monto,
                                  'id_empleado': 500,
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert res_json['monto'] == salario.monto
        assert res_json['fecha_valido'] == salario.fecha_valido.isoformat()
        assert res_json['id_empleado'] == salario.id_empleado

# def test_edit_salario_fecha_ini_aplicada():
#     # TODO: Validar no cambiar si ya fue aplicado
#     pass


def test_create_salario_fecha_valido():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/salarios/',
                               headers={
                                  'Authorization': 'Bearer '+tkn
                               },
                               json={
                                  'fecha_valido': '2024-03-01',
                                  'monto': 10,
                                  'id_empleado': empleado.id_empleado
                               })
        res_json = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert res_json['detail'] ==\
            f'La fecha de inicio debe ser mayor a {salario.fecha_valido}'


def test_create_salario():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/salarios',
                               headers={
                                   'Authorization': 'Bearer '+tkn
                               },
                               json={
                                    'fecha_valido': '2024-05-01',
                                    'monto': 1200.50,
                                    'id_empleado': empleado.id_empleado,
                               })
        res_json = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        assert res_json['monto'] == 1200.50
        assert 'id_salario' in res_json.keys()


def test_create_salario_401():
    with TestClient(app) as client:
        response = client.post('/salarios')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


def test_create_salario_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/salarios',
                               headers={
                                   'Authorization': 'Bearer '+tkn
                               },
                               json={})
        res_json = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_delete_salario_401():
    with TestClient(app) as client:
        response = client.delete('/salarios/1')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


# def test_delete_salario_404():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.delete('/salarios/10000',
                                 headers={
                                     'Authorization': 'Bearer '+tkn
                                 })
        res_json = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert res_json == {'detail': 'Salario con id: 10000 no encontrado'}


# def test_delete_salario_aplicada():
#     # TODO: Validar no cambiar fecha_ini < last_aplicada
#     # res_json = response.json()
#     # assert response.status_code == status.HTTP_400_BAD_REQUEST
#     # assert res_json == {'detail': f'Salario con id: {salario.id_salario} '
#     #                     'ya aplicado, no se puede eliminar'}
#     pass


def test_delete_salario():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.delete(f'/salarios/{salario.id_salario}',
                                 headers={
                                     'Authorization': 'Bearer '+tkn
                                 })
        salario_db = theDb\
            .query(SalariosDB)\
            .filter(SalariosDB.id_salario == salario.id_salario)\
            .first()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not salario_db
