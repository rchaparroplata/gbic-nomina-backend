from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from models.ajustes import AjusteDB
from schemas.ajustes import Ajuste, AjusteBase
from schemas.users import User


def get_ajustes(db: Session,
                skip: int = 0,
                limit: int = 10) -> list[Ajuste]:
    ajustes_db = db.\
        query(AjusteDB)\
        .offset(skip)\
        .limit(limit).all()
    ajustes = []
    for ajuste in ajustes_db:
        ajustes.append(Ajuste.model_validate(ajuste))
    return ajustes


def create_ajuste(db: Session,
                  ajuste_data: AjusteBase,
                  current_user: User):
    ajuste_create = AjusteDB(**ajuste_data.model_dump(exclude_unset=True),
                             id_usuario=current_user.id_user)
    # TODO: Validar fecha_inicio >= ahora
    db.add(ajuste_create)
    db.commit()
    db.refresh(ajuste_create)
    return ajuste_create


def edit_ajuste(id_ajs: int,
                ajuste_data: AjusteBase,
                db: Session):
    ajuste_db = db.query(AjusteDB).filter(AjusteDB.id_ajuste == id_ajs).first()
    if not ajuste_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Ajuste con id: {id_ajs} no encontrado')
    # TODO: Validar fecha_fin no menor a ultima aplicada
    # TODO: Validar fecha_inicio no cambiar si ya aplicada
    # TODO: Validar fecha_inicio >= ahora
    del ajuste_data.id_empleado
    edited_data = ajuste_data.model_dump(exclude_unset=True)
    for key, value in edited_data.items():
        setattr(ajuste_db, key, value)
    db.add(ajuste_db)
    db.commit()
    db.refresh(ajuste_db)
    return ajuste_db