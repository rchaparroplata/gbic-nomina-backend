from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from models.dispersiones import DispersionesDB
from schemas.dispersiones import (DispersionConDetalles, DispersionIn,
                                  DispersionOut)


def get_dispersiones(db: Session,
                     skip: int = 0,
                     limit: int = 10) -> list[DispersionOut]:
    dispersiones_db = db\
        .query(DispersionesDB)\
        .order_by(DispersionesDB.id_dispersion.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    dispersiones = [DispersionOut.model_validate(dispersion)
                    for dispersion in dispersiones_db]
    return dispersiones


def get_dispersion(db: Session, id_disp: int) -> DispersionConDetalles:
    dispersion_db = db\
        .query(DispersionesDB)\
        .filter(DispersionesDB.id_dispersion == id_disp)\
        .first()
    if not dispersion_db:
        msg = f'Dispersión con id: {id_disp} no encontrada'
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=msg)
    dispersion = DispersionConDetalles.model_validate(dispersion_db)
    return dispersion


def create_dispersion(db: Session,
                      create_request: DispersionIn,
                      dry_run: bool = True):
    pass


def delete_dispersion(db: Session, id_disp: int):
    pass
