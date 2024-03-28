from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.recibos import RecibosDB
from schemas.recibos import ReciboOut, ReciboConDetalles

from starlette import status


def get_recibos(db: Session,
                skip: int = 0,
                limit: int = 10) -> list[ReciboOut]:
    recibos_db = db.\
        query(RecibosDB)\
        .order_by(RecibosDB.id_recibo.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    recibos = [ReciboOut.model_validate(recibo) for recibo in recibos_db]
    return recibos


def get_recibo(db: Session, id_recibo: int) -> ReciboConDetalles:
    recibo_db = db\
        .query(RecibosDB)\
        .filter(RecibosDB.id_recibo == id_recibo)\
        .first()
    if not recibo_db:
        msg = f'Recibo con id: {id_recibo} no encontrado'
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=msg)
    recibo = ReciboConDetalles.model_validate(recibo_db)
    return recibo


def get_recibos_dispersion(db: Session, id_dispersio: int):
    pass


def get_recibos_empleado(db: Session, id_empleado: int):
    pass
