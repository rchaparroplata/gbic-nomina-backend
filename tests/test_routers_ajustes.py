from datetime import date

from fastapi.testclient import TestClient
from starlette import status

from dependencies.database import Base, get_db
from dependencies.users import create_access_token, create_user
from main import app
from models.ajustes import AjustesDB
from models.colonias import ColoniaDB
from models.empleados import EmpleadosDB
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
    'scopes': ['ajustes:write', 'ajustes:read']
}

no_scope_user_data = {
    'username': 'JustUser',
    'password': 'password',
    'nombre': 'name',
    'scopes': ['None']
}

ajuste_data = {
    'fecha_inicio': date(2024, 3, 1),
    'fecha_fin': date(2024, 3, 1),
    'motivo': 'test',
    'monto': 10,
    'id_empleado': 1,
    'id_usuario': 1
}

usr = UserIn(**user_data)
usr_scope = UserIn(**no_scope_user_data)
empleado = EmpleadosDB(**empleado_data)
colonia = ColoniaDB(**colonia_data)
ajuste = AjustesDB(**ajuste_data)


def setup():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = ovrd_get_db
    create_user(usr, theDb)
    create_user(usr_scope, theDb)
    theDb.add(colonia)
    theDb.add(empleado)
    theDb.add(ajuste)
    theDb.commit()
    theDb.refresh(ajuste)


def teardown():
    Base.metadata.drop_all(bind=engine)


def test_get_all_ajustes():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/ajustes',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert len(res_json) == 1
        assert res_json[0]['motivo'] == 'test'


def test_get_all_ajustes_401():
    with TestClient(app) as client:
        response = client.get('/ajustes')
        res_json = response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert res_json == {'detail': 'Not authenticated'}


def test_get_all_ajustes_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/ajustes',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_create_ajuste():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/ajustes',
                               headers={
                                   'Authorization': 'Bearer '+tkn
                               },
                               json={
                                   'fecha_inicio': '2024-03-01',
                                   'fecha_fin': '2024-03-01',
                                   'motivo': 'New Ajuste',
                                   'monto': 100,
                                   'id_empleado': 1
                               })
        res_json = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        assert res_json['motivo'] == 'New Ajuste'
        assert res_json['id_ajuste'] is not None


def test_create_ajuste_401():
    with TestClient(app) as client:
        response = client.post('/ajustes')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


def test_create_ajuste_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/ajustes',
                               headers={
                                   'Authorization': 'Bearer '+tkn
                               },
                               json={
                                   'fecha_inicio': '2024-03-01',
                                   'fecha_fin': '2024-03-01',
                                   'motivo': 'New Ajuste',
                                   'monto': 100,
                                   'id_empleado': 1
                               })
        res_json = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_create_ajuste_fecha_fin():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/ajustes',
                               headers={
                                   'Authorization': 'Bearer '+tkn
                               },
                               json={
                                   'fecha_inicio': '2024-03-01',
                                   'fecha_fin': '2023-03-01',
                                   'motivo': 'New Ajuste',
                                   'monto': 100,
                                   'id_empleado': 1
                               })
        res_json = response.json()
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert res_json['detail'][0]['msg'] ==\
            'Value error, La fecha final debe ser después de la inicial'


def test_edit_ajuste():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/ajustes/{ajuste.id_ajuste}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                'fecha_inicio': '2024-03-01',
                                'fecha_fin': '2024-03-01',
                                'motivo': 'New Motivo',
                                'monto': 100,
                                'id_empleado': 1
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert res_json['motivo'] == 'New Motivo'
        assert res_json['id_ajuste'] == ajuste.id_ajuste


def test_edit_ajuste_fields():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/ajustes/{ajuste.id_ajuste}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                'fecha_inicio': '2024-03-01',
                                'fecha_fin': '2024-03-01',
                                'motivo': 'New Motivo',
                                'monto': 100,
                                'id_empleado': 100
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert res_json['id_empleado'] == ajuste.id_ajuste


def test_edit_ajuste_404():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put('/ajustes/10000',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                'fecha_inicio': '2024-03-01',
                                'fecha_fin': '2024-03-01',
                                'motivo': 'New Motivo',
                                'monto': 100,
                                'id_empleado': 1
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert res_json == {'detail': 'Ajuste con id: 10000 no encontrado'}


def test_edit_ajuste_401():
    with TestClient(app) as client:
        response = client.put('/ajustes/1')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


def test_edit_ajuste_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/ajustes/{ajuste.id_ajuste}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                  'fecha_inicio': '2024-03-01',
                                  'fecha_fin': '2024-03-01',
                                  'motivo': 'New Ajuste',
                                  'monto': 100,
                                  'id_empleado': 1
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_edit_ajuste_fecha_fin():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/ajustes/{ajuste.id_ajuste}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                'fecha_inicio': '2024-03-01',
                                'fecha_fin': '2023-03-01',
                                'motivo': 'New Motivo',
                                'monto': 100,
                                'id_empleado': 100
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert res_json['detail'][0]['msg'] ==\
            'Value error, La fecha final debe ser después de la inicial'


def test_edit_ajuste_fecha_ini_aplicada():
    # Validar fecha_inicio no cambiar si ya aplicada
    # TODO: Validate Aplicado
    pass


def test_edit_ajuste_fecha_fin_aplicada():
    # Validar fecha_fin no menor a ultima aplicada
    # TODO: Validate Aplicado
    pass


def test_delete_ajuste_401():
    with TestClient(app) as client:
        response = client.delete('/ajustes/1')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


def test_delete_ajuste_404():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.delete('/ajustes/10000',
                                 headers={
                                     'Authorization': 'Bearer '+tkn
                                 })
        res_json = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert res_json == {'detail': 'Ajuste con id: 10000 no encontrado'}


def test_delete_ajuste_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.delete(f'/ajustes/{ajuste.id_ajuste}',
                                 headers={
                                     'Authorization': 'Bearer '+tkn
                                 })
        res_json = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_delete_ajuste():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.delete(f'/ajustes/{ajuste.id_ajuste}',
                                 headers={
                                     'Authorization': 'Bearer '+tkn
                                 })
        ajuste_db = theDb\
            .query(AjustesDB)\
            .filter(AjustesDB.id_ajuste == ajuste.id_ajuste)\
            .first()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ajuste_db
