from sqlalchemy import Column, Date, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from dependencies.database import Base
from models.cuentas import CuentasDB
from models.users import UserDB


class DispersionesDB(Base):
    __tablename__ = 'dispersiones'

    id_dispersion = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, server_default=func.current_date())
    periodo = Column(Integer)
    periodo_fecha = Column(Date)
    total = Column(Float)
    id_usuario = Column(Integer, ForeignKey(UserDB.id_user))
    usuario = relationship('UserDB', lazy='joined')
    detalles = relationship('DisepersionesDetalleDB')


class DisepersionesDetalleDB(Base):
    __tablename__ = 'dispersiones_detalle'

    id_dispersiones_detalle = Column(Integer, primary_key=True, index=True)
    id_dispersion = Column(Integer, ForeignKey(DispersionesDB.id_dispersion))
    id_cuenta = Column(Integer, ForeignKey(CuentasDB.id_cuenta))
    monto = Column(Float)
    cuenta = relationship('CuentasDB', lazy='joined')
