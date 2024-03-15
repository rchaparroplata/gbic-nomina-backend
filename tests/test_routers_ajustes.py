from datetime import date

from fastapi.testclient import TestClient

from dependencies.database import Base, get_db
from dependencies.users import create_access_token, create_user
from main import app
from models.ajustes import AjusteDB
from models.colonias import ColoniaDB
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
    'scopes': ['ajustes:writer', 'ajustes:reader']
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
empleado = EmpleadoDB(**empleado_data)
colonia = ColoniaDB(**colonia_data)
ajuste = AjusteDB(**ajuste_data)


def setup():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = ovrd_get_db
    create_user(usr, theDb)
    create_user(usr_scope, theDb)
    theDb.add(colonia)
    theDb.add(empleado)
    theDb.add(ajuste)
    theDb.commit()


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
        assert response.status_code == 200
        assert len(res_json) == 1
        assert res_json[0]['motivo'] == 'test'


def test_get_all_ajustes_401():
    with TestClient(app) as client:
        response = client.get('/ajustes')
        res_json = response.json()
        assert response.status_code == 401
        assert res_json == {'detail': 'Not authenticated'}


def test_get_all_ajustes_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/ajustes',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              })
        res_json = response.json()
        assert response.status_code == 401
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_create_ajuste():
    pass


def test_create_ajuste_401():
    pass


def test_create_ajuste_no_scope():
    pass


def test_create_ajuste_fecha_ini():
    # Validar fecha_inicio >= ahora
    pass


def test_create_ajuste_fecha_fin():
    # Validar fecha_fin >= a fecha_inicio
    pass


def test_edit_ajuste():
    pass


def test_edit_ajuste_401():
    pass


def test_edit_ajuste_no_scope():
    pass


def test_edit_ajuste_fecha_ini():
    # Validar fecha_inicio >= ahora
    pass


def test_edit_ajuste_fecha_fin():
    # Validar fecha_fin >= a fecha_inicio
    pass


def test_edit_ajuste_fecha_ini_aplicada():
    # Validar fecha_inicio no cambiar si ya aplicada
    pass


def test_edit_ajuste_fecha_fin_aplicada():
    # Validar fecha_fin no menor a ultima aplicada
    pass
