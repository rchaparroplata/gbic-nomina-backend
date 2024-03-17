from dependencies.database import Base, get_db
from dependencies.users import create_user
from main import app
from schemas.users import UserIn
from tests.core import engine, ovrd_get_db
from models.bancos import BancosDB


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
    'scopes': ['bancos:writer', 'bancos:reader']
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


def tet_get_all_bancos():
    pass


def test_get_all_bancos_401():
    pass


def test_get_all_bancos_no_scope():
    pass


def test_create_banco():
    pass


def test_create_banco_401():
    pass


def test_create_banco_no_scope():
    pass


def test_create_banco_nombre_existente():
    pass


def test_edit_banco():
    pass


def test_edit_banco_401():
    pass


def test_edit_banco_no_scope():
    pass


def test_edit_banco_404():
    pass


def test_edit_banco_nombre():
    # Editar un banco con nombre ya existente en la BD
    pass


def test_edit_banco_deactivate_cascade():
    # TODO: Cuentas de ese banco pasen a desactivarse
    pass


def test_delete_banco():
    pass


def test_delete_banco_401():
    pass


def test_delete_banco_404():
    pass


def test_delete_banco_no_scope():
    pass


def test_delete_banco_activo():
    # si hay cuentas usandolo no poder borrar
    pass
