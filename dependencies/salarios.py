from fastapi import HTTPException
from sqlalchemy.orm import Session, lazyload
# from sqlalchemy.sql import func
from starlette import status

from models.salarios import SalariosDB
from schemas.salarios import SalarioIn, SalarioOut
from schemas.users import User

salarios_resp_edit = {
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
                'example': {'detail': "Salario con id: 1 no encontrado"}
            }
        }
    }
}


def get_salarios(db: Session,
                 skip: int = 0,
                 limit: int = 10) -> list[SalarioOut]:
    salario_db = db.\
        query(SalariosDB)\
        .offset(skip)\
        .limit(limit).all()
    salarios = [SalarioOut.model_validate(salario)
                for salario in salario_db]
    return salarios


def create_salario(db: Session,
                   input_data: SalarioIn,
                   current_user: User) -> SalariosDB:
    salario_create = SalariosDB(**input_data.model_dump(exclude_unset=True),
                                id_usuario=current_user.id_user)
    salarios_db = db\
        .query(SalariosDB)\
        .filter(SalariosDB.id_empleado == input_data.id_empleado)\
        .order_by(SalariosDB.fecha_valido.desc)\
        .options(lazyload(SalariosDB.usuario))\
        .options(lazyload(SalariosDB.empleado))\
        .all()
    for salario in salarios_db:
        msg = f'La fecha de inicio debe ser mayor a {salario.fecha_valido}'
        if input_data.fecha_valido <= salario.fecha_valido:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=msg)
    db.add(salario_create)
    db.commit()
    db.refresh(salario_create)
    return salario_create


def edit_salario(id_sal: int,
                 input_data: SalarioIn,
                 db: Session):
    salario_db = db.query(SalariosDB)\
        .filter(SalariosDB.id_salario == id_sal).first()
    if not salario_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Salario con id: {id_sal} no encontrado')
    salarios_db = db\
        .query(SalariosDB)\
        .filter(
            (SalariosDB.id_empleado == input_data.id_empleado) and
            (SalariosDB.id_salario != id_sal)
        )\
        .order_by(SalariosDB.fecha_valido.desc)\
        .options(lazyload(SalariosDB.usuario))\
        .options(lazyload(SalariosDB.empleado))\
        .all()
    for salario in salarios_db:
        msg = f'La fecha de inicio debe ser mayor a {salario.fecha_valido}'
        if input_data.fecha_valido <= salario.fecha_valido:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=msg)
    del input_data.id_empleado
    edited_data = input_data.model_dump(exclude_unset=True)
    for key, value in edited_data.items():
        setattr(salario_db, key, value)
    db.add(salario_db)
    db.commit()
    db.refresh(salario_db)
    return salario_db


def delete_salario(db: Session, id_sal: int):
    salario_db = db\
        .query(SalariosDB)\
        .filter(SalariosDB.id_salario == id_sal)\
        .first()
    if not salario_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Salario con id: {id_sal} no encontrado')
    # TODO: Validar que no esté aplicada
    # aplicado = db\
    #     .query(RecibosDB)\
    #     .filter(RecibosDB.id_salario == id_sal)\
    #     .first()
    # if aplicado:
    #   raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
    #                       detail=f'Salario con id: {id_sal} ya aplicado, '
    #                              'no se puede eliminar')
    db.delete(salario_db)
    db.commit()
