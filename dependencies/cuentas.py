from fastapi import HTTPException
from sqlalchemy.orm import Session
# from sqlalchemy.sql import func
from starlette import status

from models.cuentas import CuentasDB
from schemas.cuentas import CuentaIn, CuentaOut
from schemas.users import User

cuentas_resp_edit = {
    status.HTTP_404_NOT_FOUND: {
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'detail': {
                            'type': "string"
                        }
                    }
                },
                'example': {'detail': "Cuenta con id: 1 no encontrada"}
            }
        }
    }
}


def get_cuentas(db: Session,
                skip: int = 0,
                limit: int = 10) -> list[CuentaOut]:
    cuentas_db = db.\
        query(CuentasDB)\
        .offset(skip)\
        .limit(limit).all()
    cuentas = [CuentaOut.model_validate(cuenta)
               for cuenta in cuentas_db]
    return cuentas


def create_cuenta(db: Session,
                  input_data: CuentaIn,
                  current_user: User) -> CuentasDB:
    cuenta_create = CuentasDB(**input_data.model_dump(exclude_unset=True,
                                                      exclude=['tipo_txt']),
                              id_usuario=current_user.id_user)
    db.add(cuenta_create)
    db.commit()
    db.refresh(cuenta_create)
    return cuenta_create


def edit_cuenta(id_cta: int,
                input_data: CuentaIn,
                db: Session):
    cuenta_db = db.query(CuentasDB)\
        .filter(CuentasDB.id_cuenta == id_cta).first()
    if not cuenta_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Cuenta con id: {id_cta} no encontrada')
    if input_data.activa != cuenta_db.activa:
        setattr(cuenta_db, 'activa', input_data.activa)
    else:
        del input_data.id_empleado
        # TODO: Validar que no haya sido utilizada
        # aplicado = db\
        #     .query(RecibosDB)\
        #     .filter(RecibosDB.id_salario == id_sal)\
        #     .first()
        # if aplicado:
        #   raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        #                       detail=f'Cuenta con id: {id_sal} ya utilizada,'
        #                              'no se puede editar')
        edited_data = input_data.model_dump(exclude_unset=True)
        for key, value in edited_data.items():
            setattr(cuenta_db, key, value)
    db.add(cuenta_db)
    db.commit()
    db.refresh(cuenta_db)
    return cuenta_db


def delete_cuenta(db: Session, id_cta: int):
    cuenta_db = db\
        .query(CuentasDB)\
        .filter(CuentasDB.id_cuenta == id_cta)\
        .first()
    if not cuenta_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Cuenta con id: {id_cta} no encontrada')
    # TODO: Validar que no haya sido utilizada
    # aplicado = db\
    #     .query(RecibosDB)\
    #     .filter(RecibosDB.id_cuenta == id_cta)\
    #     .first()
    # if aplicado:
    #   raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
    #                       detail=f'Cuenta con id: {id_cta} ya utilizada, '
    #                              'no se puede eliminar')
    db.delete(cuenta_db)
    db.commit()
