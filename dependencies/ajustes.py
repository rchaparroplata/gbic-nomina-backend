from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from models.ajustes import AjusteDB
from schemas.ajustes import AjusteIn, AjusteOut
from schemas.users import User

ajustes_resp_edit = {
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
                'example': {'detail': "Ajuste con id: 1 no encontrado"}
            }
        }
    }
}


def get_ajustes(db: Session,
                skip: int = 0,
                limit: int = 10) -> list[AjusteOut]:
    ajustes_db = db.\
        query(AjusteDB)\
        .offset(skip)\
        .limit(limit).all()
    ajustes = [AjusteOut.model_validate(ajuste) for ajuste in ajustes_db]
    return ajustes


def create_ajuste(db: Session,
                  ajuste_data: AjusteIn,
                  current_user: User) -> AjusteDB:
    ajuste_create = AjusteDB(**ajuste_data.model_dump(exclude_unset=True),
                             id_usuario=current_user.id_user)
    db.add(ajuste_create)
    db.commit()
    db.refresh(ajuste_create)
    return ajuste_create


def edit_ajuste(id_ajs: int,
                ajuste_data: AjusteIn,
                db: Session):
    ajuste_db = db.query(AjusteDB).filter(AjusteDB.id_ajuste == id_ajs).first()
    if not ajuste_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Ajuste con id: {id_ajs} no encontrado')
    # aplicado = db\
    #     .query(RecibosDB)\
    #     .filter(RecibosDB.id_ajuste == id_ajs)\
    #     .order_by(RecibosDB.fecha.desc())\
    #     .first()
    # TODO: Validar fecha_fin no menor a ultima aplicada
    # if aplicado and ajuste_data.fecha_fin < aplicado.fecha:
    #   raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
    #                       detail=f'Ajuste con id: {id_ajs} ya aplicado, '
    #                              'no se puede cambiar la fecha de fin '
    #                              'a antes de {aplicado.fecha})
    # TODO: Validar fecha_inicio no cambiar si ya aplicada
    # if aplicado and\
    #    not ajuste_data.fecha_inicio == aplicado.ajuste.fecha_inicio:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
    #                         detail=f'Ajuste con id: {id_ajs} ya aplicado, '
    #                                'no se puede cambiar la fecha de inicio')
    del ajuste_data.id_empleado
    edited_data = ajuste_data.model_dump(exclude_unset=True)
    for key, value in edited_data.items():
        setattr(ajuste_db, key, value)
    db.add(ajuste_db)
    db.commit()
    db.refresh(ajuste_db)
    return ajuste_db


def delete_ajuste(db: Session, id_ajs: int):
    ajuste_db = db.query(AjusteDB).filter(AjusteDB.id_ajuste == id_ajs).first()
    if not ajuste_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Ajuste con id: {id_ajs} no encontrado')
    # TODO: Validar que no esté aplicada
    # aplicado = db\
    #     .query(RecibosDB)\
    #     .filter(RecibosDB.id_ajuste == id_ajs)\
    #     .first()
    # if aplicado:
    #   raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
    #                       detail=f'Ajuste con id: {id_ajs} ya aplicado, '
    #                              'no se puede eliminar')
    db.delete(ajuste_db)
    db.commit()
