from sqlalchemy import Column, Date, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship

from dependencies.database import Base
from models.dispersiones import DisepersionesDB
from models.empleados import EmpleadoDB


class ReciboDB(Base):
    __tablename__ = 'recibos'

    id_recibo = Column(Integer, primary_key=True, index=True)
    id_emplado = Column(Integer, ForeignKey(EmpleadoDB.id_empleado))
    id_dispersion = Column(Integer, ForeignKey(DisepersionesDB.id_dispersion))
    monto = Column(Float)
    fecha = Column(Date)
    empleado = relationship('EmpleadoDB', lazy='joined')
    dispersion = relationship('DispersionDB', lazy='joined')
