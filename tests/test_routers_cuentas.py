from datetime import date

from fastapi.testclient import TestClient
from starlette import status

from dependencies.database import Base, get_db
from dependencies.users import create_access_token, create_user
from main import app
from models.bancos import BancosDB
from models.colonias import ColoniaDB
from models.cuentas import CuentasDB
from models.empleados import EmpleadoDB
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
    'scopes': ['cuentas:write', 'cuentas:read']
}

no_scope_user_data = {
    'username': 'JustUser',
    'password': 'password',
    'nombre': 'name',
    'scopes': ['None']
}

banco_data = {
    'nombre': 'Banco Uno'
}

ahorro_data = {
    'fecha': date(2024, 3, 1),
    'numero': '12312',
    'tipo': 1,
    'id_banco': 1,
    'id_empleado': 1,
    'id_usuario': 1
}

nomina_data = {
    'fecha': date(2024, 3, 1),
    'numero': '25101988123412343',
    'tipo': 2,
    'id_banco': 1,
    'id_empleado': 1,
    'id_usuario': 1
}
usr = UserIn(**user_data)
usr_scope = UserIn(**no_scope_user_data)
empleado = EmpleadoDB(**empleado_data)
colonia = ColoniaDB(**colonia_data)
ahorro = CuentasDB(**ahorro_data)
nomina = CuentasDB(**nomina_data)
banco = BancosDB(**banco_data)


def setup():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = ovrd_get_db
    create_user(usr, theDb)
    create_user(usr_scope, theDb)
    theDb.add(banco)
    theDb.add(colonia)
    theDb.add(empleado)
    theDb.add(ahorro)
    theDb.add(nomina)
    theDb.commit()
    theDb.refresh(ahorro)
    theDb.refresh(nomina)


def teardown():
    Base.metadata.drop_all(bind=engine)


def test_get_all_cuentas():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/cuentas',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert len(res_json) == 2


def test_get_all_cuentas_401():
    with TestClient(app) as client:
        response = client.get('/cuentas')
        res_json = response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert res_json == {'detail': 'Not authenticated'}


def test_get_all_cuentas_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/cuentas',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


# def test_edit_cuenta_fecha_mayor():
#     tkn = create_access_token(usr, theDb).access_token
#     with TestClient(app) as client:
#         response = client.put(f'/cuentas/{cuenta.id_cuenta}',
#                               headers={
#                                   'Authorization': 'Bearer '+tkn
#                               },
#                               json={
#                                   'fecha_valido': '2024-02-01',
#                                   'monto': 1010.00,
#                                   'id_empleado': empleado.id_empleado,
#                               })
#         res_json = response.json()
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         assert res_json['detail'] ==\
#             f'La fecha de inicio debe ser mayor a {cuenta.fecha_valido}'


def test_edit_cuenta():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/cuentas/{ahorro.id_cuenta}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                  'numero': '251088',
                                  'tipo': 2,
                                  'id_banco': banco.id_banco,
                                  'id_empleado': empleado.id_empleado
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert res_json['numero'] == '251088'
        theDb.refresh(ahorro)


def test_edit_cuenta_solo_activa():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/cuentas/{ahorro.id_cuenta}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                  'numero': 'xxxxx',
                                  'tipo': 5,
                                  'id_banco': banco.id_banco,
                                  'id_empleado': empleado.id_empleado,
                                  'activa': False
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert res_json['numero'] == ahorro.numero
        assert res_json['tipo'] == ahorro.tipo
        assert res_json['activa'] is False
        theDb.refresh(ahorro)


def test_edit_cuenta_404():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put('/cuentas/10000',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                  'numero': '25101988123412343',
                                  'tipo': 2,
                                  'id_banco': banco.id_banco,
                                  'id_empleado': empleado.id_empleado
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert res_json == {'detail': 'Cuenta con id: 10000 no encontrada'}


def test_edit_cuenta_401():
    with TestClient(app) as client:
        response = client.put('/cuentas/1')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


def test_edit_cuenta_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/cuentas/{ahorro.id_cuenta}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={})
        res_json = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_edit_cuenta_fields():
    # id_empleado remains the same
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/cuentas/{ahorro.id_cuenta}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                  'numero': ahorro.numero,
                                  'tipo': ahorro.tipo,
                                  'id_banco': ahorro.id_banco,
                                  'id_empleado': 500,
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert res_json['numero'] == ahorro.numero
        assert res_json['id_empleado'] == ahorro.id_empleado

# def test_edit_cuenta_fecha_ini_aplicada():
#     # TODO: Validar no cambiar si ya fue aplicado
#     pass


# def test_create_cuenta_fecha_valido():
#     tkn = create_access_token(usr, theDb).access_token
#     with TestClient(app) as client:
#         response = client.post('/cuentas/',
#                                headers={
#                                   'Authorization': 'Bearer '+tkn
#                                },
#                                json={
#                                   'fecha_valido': '2024-03-01',
#                                   'monto': 10,
#                                   'id_empleado': empleado.id_empleado
#                                })
#         res_json = response.json()
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         assert res_json['detail'] ==\
#             f'La fecha de inicio debe ser mayor a {cuenta.fecha_valido}'


def test_create_cuenta():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/cuentas',
                               headers={
                                   'Authorization': 'Bearer '+tkn
                               },
                               json={
                                    'numero': '123321',
                                    'tipo': 2,
                                    'id_banco': banco.id_banco,
                                    'id_empleado': empleado.id_empleado,
                               })
        res_json = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        assert res_json['numero'] == '123321'
        assert 'id_cuenta' in res_json.keys()


def test_create_cuenta_401():
    with TestClient(app) as client:
        response = client.post('/cuentas')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


def test_create_cuenta_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/cuentas',
                               headers={
                                   'Authorization': 'Bearer '+tkn
                               },
                               json={})
        res_json = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_delete_cuenta_401():
    with TestClient(app) as client:
        response = client.delete('/cuentas/1')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


def test_delete_cuenta_404():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.delete('/cuentas/10000',
                                 headers={
                                     'Authorization': 'Bearer '+tkn
                                 })
        res_json = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert res_json == {'detail': 'Cuenta con id: 10000 no encontrada'}


# def test_delete_cuenta_aplicada():
#     # TODO: Validar no cambiar fecha_ini < last_aplicada
#     # res_json = response.json()
#     # assert response.status_code == status.HTTP_400_BAD_REQUEST
#     # assert res_json == {'detail': f'Cuenta con id: {cuenta.id_cuenta} '
#     #                     'ya aplicado, no se puede eliminar'}
#     pass


def test_delete_cuenta():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.delete(f'/cuentas/{nomina.id_cuenta}',
                                 headers={
                                     'Authorization': 'Bearer '+tkn
                                 })
        cuenta_db = theDb\
            .query(CuentasDB)\
            .filter(CuentasDB.id_cuenta == nomina.id_cuenta)\
            .first()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not cuenta_db
