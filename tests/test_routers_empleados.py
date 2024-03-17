from fastapi.testclient import TestClient

from dependencies.database import Base, get_db
from dependencies.users import create_access_token, create_user
from main import app
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
    'scopes': ['empleados:writer', 'empleados:reader']

}
no_scope_user_data = {
    'username': 'JustUser',
    'password': 'password',
    'nombre': 'name',
    'scopes': ['None']
}

usr = UserIn(**user_data)
usr_scope = UserIn(**no_scope_user_data)
empleado = EmpleadoDB(**empleado_data)
colonia = ColoniaDB(**colonia_data)


def setup():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = ovrd_get_db
    create_user(usr, theDb)
    create_user(usr_scope, theDb)
    theDb.add(colonia)
    theDb.add(empleado)
    theDb.commit()


def teardown():
    Base.metadata.drop_all(bind=engine)


def test_get_all_empleados():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/empleados',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              })
        res_json = response.json()
        assert response.status_code == 200
        assert len(res_json) == 1
        assert res_json[0]['nombre'] == 'Nombre'


def test_get_all_empleados_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.get('/empleados',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                              })
        res_json = response.json()
        assert response.status_code == 403
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_get_all_empleados_401():
    with TestClient(app) as client:
        response = client.get('/empleados')
        assert response.status_code == 401
        assert response.json() == {'detail': 'Not authenticated'}


def test_create_empleado():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/empleados',
                               headers={
                                  'Authorization': 'Bearer '+tkn
                                  },
                               json={
                                   "nombre": "Nombre2",
                                   "paterno": "Paterno2",
                                   "materno": "Materno2",
                                   "rfc": "RFC001XXX",
                                   "curp": "CURPXXX001",
                                   "calle": "Calle",
                                   "exterior": "200",
                                   "id_colonia": 1,
                                   "celular": "1231232132",
                                })
        res_json = response.json()
        assert response.status_code == 201
        assert res_json['nombre'] == 'Nombre2'


def test_create_empleado_401():
    with TestClient(app) as client:
        response = client.post('/empleados')
        assert response.status_code == 401
        assert response.json() == {'detail': 'Not authenticated'}


def test_create_empleado_no_scope():
    tkn = create_access_token(usr_scope, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/empleados',
                               headers={
                                  'Authorization': 'Bearer '+tkn
                                  },
                               json={
                                   "nombre": "Nombre2",
                                   "paterno": "Paterno2",
                                   "materno": "Materno2",
                                   "rfc": "RFC001XXX",
                                   "curp": "CURPXXX001",
                                   "calle": "Calle",
                                   "exterior": "200",
                                   "id_colonia": 1,
                                   "celular": "1231232132",
                                })
        res_json = response.json()
        assert response.status_code == 403
        assert res_json == {'detail': 'Sin Privilegios Necesarios'}


def test_create_empleado_rfc():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/empleados',
                               headers={
                                  'Authorization': 'Bearer '+tkn
                                  },
                               json={
                                   "nombre": "Nombre2",
                                   "paterno": "Paterno2",
                                   "materno": "Materno2",
                                   "rfc": "RFC000XXX",
                                   "curp": "CURPXXX000",
                                   "calle": "Calle",
                                   "exterior": "200",
                                   "id_colonia": 1,
                                   "celular": "1231232132",
                                })
        res_json = response.json()
        assert response.status_code == 400
        assert res_json == {'detail': 'RFC ya registrado'}


def test_create_empleado_curp():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.post('/empleados',
                               headers={
                                  'Authorization': 'Bearer '+tkn
                                  },
                               json={
                                   "nombre": "Nombre2",
                                   "paterno": "Paterno2",
                                   "materno": "Materno2",
                                   "rfc": "RFC005XXX",
                                   "curp": "CURPXXX000",
                                   "calle": "Calle",
                                   "exterior": "200",
                                   "id_colonia": 1,
                                   "celular": "1231232132",
                                })
        res_json = response.json()
        assert response.status_code == 400
        assert res_json == {'detail': 'CURP ya registrado'}


def test_edit_empleado():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put('/empleados/1',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                                  },
                              json={
                                   "nombre": "NombreNuevo",
                                   "paterno": "Paterno2",
                                   "materno": "Materno2",
                                   "rfc": "RFC000XXX",
                                   "curp": "CURPXXX000",
                                   "calle": "Calle",
                                   "exterior": "200",
                                   "id_colonia": 1,
                                   "celular": "1231232132",
                                })
        res_json = response.json()
        assert response.status_code == 202
        assert res_json['nombre'] == 'NombreNuevo'


def test_edit_empleado_401():
    with TestClient(app) as client:
        response = client.put('/empleados/1')
        assert response.status_code == 401
        assert response.json() == {'detail': 'Not authenticated'}


def test_edit_empleado_rfc():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put('/empleados/2',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                                  },
                              json={
                                   "nombre": "NombreNuevo",
                                   "paterno": "Paterno2",
                                   "materno": "Materno2",
                                   "rfc": "RFC000XXX",
                                   "curp": "CURPXXX000",
                                   "calle": "Calle",
                                   "exterior": "200",
                                   "id_colonia": 1,
                                   "celular": "1231232132",
                                })
        res_json = response.json()
        assert response.status_code == 400
        assert res_json == {'detail': 'RFC ya registrado'}


def test_edit_empleado_curp():
    tkn = create_access_token(usr, theDb).access_token
    with TestClient(app) as client:
        response = client.put('/empleados/2',
                              headers={
                                  'Authorization': 'Bearer '+tkn
                                  },
                              json={
                                   "nombre": "NombreNuevo",
                                   "paterno": "Paterno2",
                                   "materno": "Materno2",
                                   "rfc": "RFC000XZZZX",
                                   "curp": "CURPXXX000",
                                   "calle": "Calle",
                                   "exterior": "200",
                                   "id_colonia": 1,
                                   "celular": "1231232132",
                                })
        res_json = response.json()
        assert response.status_code == 400
        assert res_json == {'detail': 'CURP ya registrado'}
