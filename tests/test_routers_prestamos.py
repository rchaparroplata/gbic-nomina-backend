from datetime import date

from fastapi.testclient import TestClient
from starlette import status

from dependencies.database import Base, get_db
from dependencies.users import create_access_token, create_user
from main import app
from models.colonias import ColoniaDB
from models.empleados import EmpleadosDB
from models.prestamos import PrestamosDB
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
    'scopes': ['prestamos:write', 'prestamos:read']
}

no_scope_user_data = {
    'username': 'JustUser',
    'password': 'password',
    'nombre': 'name',
    'scopes': ['None']
}

prestamo_data = {
    'fecha_inicio': date(2024, 3, 1),
    'monto': 1000,
    'monto_quincenal': 100,
    'comentarios': 'Prestamo Test',
    'id_empleado': 1,
    'id_usuario': 1
}

usr = UserIn(**user_data)
usr_scope = UserIn(**no_scope_user_data)
empleado = EmpleadosDB(**empleado_data)
colonia = ColoniaDB(**colonia_data)
prestamo = PrestamosDB(**prestamo_data)


def setup():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = ovrd_get_db
    create_user(usr, theDb)
    create_user(usr_scope, theDb)
    theDb.add(colonia)
    theDb.add(empleado)
    theDb.add(prestamo)
    theDb.commit()
    theDb.refresh(prestamo)


def teardown():
    Base.metadata.drop_all(bind=engine)


def test_get_all_prestamos():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/prestamos',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert len(res_json) == 1
        assert res_json[0]['comentarios'] == 'Prestamo Test'


def test_get_all_prestamos_401():
    with TestClient(app) as client:
        response = client.get('/prestamos')
        res_json = response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert res_json == {'detail': 'Not authenticated'}


def test_get_all_prestamos_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/prestamos',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_create_prestamo():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/prestamos',
                               headers={
                                   'Authorization': 'Bearer '+tkn
                               },
                               json={
                                    'fecha_inicio': '2024-03-01',
                                    'monto': 1000,
                                    'monto_quincenal': 100,
                                    'comentarios': 'Nuevo Prestamo',
                                    'id_empleado': empleado.id_empleado,
                               })
        res_json = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        assert res_json['comentarios'] == 'Nuevo Prestamo'
        assert 'id_prestamo' in res_json.keys()


def test_create_prestamo_401():
    with TestClient(app) as client:
        response = client.post('/prestamos')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


def test_create_prestamo_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/prestamos',
                               headers={
                                   'Authorization': 'Bearer '+tkn
                               },
                               json={})
        res_json = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_create_prestamo_monto_total():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/prestamos/',
                               headers={
                                  'Authorization': 'Bearer '+tkn
                               },
                               json={
                                  'fecha_inicio': '2024-03-01',
                                  'monto': 10,
                                  'monto_quincenal': 100,
                                  'id_empleado': empleado.id_empleado
                               })
        res_json = response.json()
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert res_json['detail'][0]['msg'] ==\
            'Value error, El monto quicenal no puede ser mayor al total'


def test_edit_prestamo():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/prestamos/{prestamo.id_prestamo}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                  'fecha_inicio': '2024-03-01',
                                  'monto': 1005,
                                  'monto_quincenal': 100
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert res_json['comentarios'] == 'Prestamo Test'
        assert res_json['monto'] == 1005


def test_edit_prestamo_fields():
    # id_empleado remains the same
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/prestamos/{prestamo.id_prestamo}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                  'fecha_inicio': '2024-03-01',
                                  'monto': 1008,
                                  'monto_quincenal': 100,
                                  'id_empelado': 200
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert res_json['comentarios'] == 'Prestamo Test'
        assert res_json['monto'] == 1008
        assert res_json['id_empleado'] == empleado.id_empleado


def test_edit_prestamo_404():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put('/prestamos/10000',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                  'fecha_inicio': '2024-03-01',
                                  'monto': 1000,
                                  'monto_quincenal': 100,
                                  'comentarios': 'Prestamo Test'
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert res_json == {'detail': 'Prestamo con id: 10000 no encontrado'}


def test_edit_prestamo_401():
    with TestClient(app) as client:
        response = client.put('/prestamos/1')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


def test_edit_prestamo_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/prestamos/{prestamo.id_prestamo}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={})
        res_json = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_edit_prestamo_monto_total():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put(f'/prestamos/{prestamo.id_prestamo}',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              },
                              json={
                                  'fecha_inicio': '2024-03-01',
                                  'monto': 10,
                                  'monto_quincenal': 100
                              })
        res_json = response.json()
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert res_json['detail'][0]['msg'] ==\
            'Value error, El monto quicenal no puede ser mayor al total'


def test_edit_prestamo_fecha_ini_aplicada():
    # TODO: Validar no cambiar fecha_ini < last_aplicada
    pass


def test_delete_prestamo_401():
    with TestClient(app) as client:
        response = client.delete('/prestamos/1')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


def test_delete_prestamo_404():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.delete('/prestamos/10000',
                                 headers={
                                     'Authorization': 'Bearer '+tkn
                                 })
        res_json = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert res_json == {'detail': 'Prestamo con id: 10000 no encontrado'}


def test_delete_prestamo_aplicada():
    # TODO: Validar no cambiar fecha_ini < last_aplicada
    # res_json = response.json()
    # assert response.status_code == status.HTTP_400_BAD_REQUEST
    # assert res_json == {'detail': f'Prestamo con id: {prestamo.id_prestamo} '
    #                     'ya aplicado, no se puede eliminar'}
    pass


def test_delete_prestamo():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.delete(f'/prestamos/{prestamo.id_prestamo}',
                                 headers={
                                     'Authorization': 'Bearer '+tkn
                                 })
        prestamo_db = theDb\
            .query(PrestamosDB)\
            .filter(PrestamosDB.id_prestamo == prestamo.id_prestamo)\
            .first()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not prestamo_db
