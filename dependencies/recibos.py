from sqlalchemy.orm import Session

from models.recibos import RecibosDB
from schemas.recibos import ReciboOut


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


def get_recibo(db: Session, id_recibo: int):
    pass


def get_recibos_dispersion(db: Session, id_dispersio: int):
    pass


def get_recibos_empleado(db: Session, id_empleado: int):
    pass
