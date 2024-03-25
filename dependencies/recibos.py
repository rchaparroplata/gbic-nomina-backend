from sqlalchemy.orm import Session


def get_recibos(db: Session, skip: int = 0, limit: int = 10):
    pass


def get_recibo(db: Session, id_recibo: int):
    pass


def get_recibos_dispersion(db: Session, id_dispersio: int):
    pass


def get_recibos_empleado(db: Session, id_empleado: int):
    pass
