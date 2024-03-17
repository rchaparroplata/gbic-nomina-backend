from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from models.bancos import BancosDB
from schemas.bancos import BancoOut, BancoIn


def get_bancos(db: Session,
               skip: int = 0,
               limit: int = 10) -> list[BancoOut]:
    bancos_db = db.query(BancosDB).offset(skip).limit(limit).all()
    bancos = [BancoOut.model_validate(banco) for banco in bancos_db]
    return bancos


def create_banco(db: Session,
                 banco_data: BancoIn) -> BancosDB:
    banco_db = db.query(BancosDB)\
        .filter(BancosDB.nombre == banco_data.nombre)\
        .first()
    if banco_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Banco con nombre {banco_data.nombre}'
                                   'ya existente')
    banco_create = BancosDB(**banco_data.model_dump(exclude_unset=True))
    db.add(banco_create)
    db.commit()
    db.refresh(banco_create)
    return banco_create


def edit_banco(db: Session,
               id_banco: int,
               banco_data: BancoIn) -> BancosDB:
    banco_db = db.query(BancosDB).filter(BancosDB.id_banco == id_banco).first()

    if not banco_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Banco con Id: {id_banco} no encontrado')
    banco_nombre = db.query(BancosDB)\
                     .filter(BancosDB.nombre == banco_data.nombre and
                             BancosDB.id_banco != id_banco).first()
    if banco_nombre is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Banco con nombre: {banco_data.nombre}'
                                   'ya existente')
    # TODO: If activo = False; todas las cuentas = False
    edited_data = banco_data.model_dump(exclude_unset=True)
    [setattr(banco_db, key, value) for key, value in edited_data.items()]
    db.add(banco_db)
    db.commit()
    db.refresh(banco_db)
    return banco_db


def delete_banco(db: Session,
                 id_banco: int):
    # TODO: To implement
    # Verificar que exista el banco
    # Verificar que no haya cuentas en ese banco
    # Eliminarlo
    pass
