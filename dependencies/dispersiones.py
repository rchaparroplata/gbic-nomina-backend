from sqlalchemy.orm import Session

from schemas.dispersiones import DispersionIn


def get_dispersiones(db: Session, skip: int = 0, limit: int = 10):
    pass


def get_dispersion(db: Session, id_disp: int):
    pass


def create_dispersion(db: Session,
                      create_request: DispersionIn,
                      dry_run: bool = True):
    pass


def delete_dispersion(db: Session, id_disp: int):
    pass
