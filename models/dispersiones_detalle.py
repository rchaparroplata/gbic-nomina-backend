from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from dependencies.database import Base
from models.cuentas import CuentasDB
from models.dispersiones import DispersionesDB


class DisepersionesDetalleDB(Base):
    __tablename__ = 'dispersiones_detalle'

    id_dispersiones_detalle = Column(Integer, primary_key=True, index=True)
    id_dispersion = Column(Integer, ForeignKey(DispersionesDB.id_dispersion))
    id_cuenta = Column(Integer, ForeignKey(CuentasDB.id_cuenta))
    monto = Column(Float)
    dispersion = relationship('DispersionesDB', lazy='joined')
    cuenta = relationship('CuentasDB', lazy='joined')
