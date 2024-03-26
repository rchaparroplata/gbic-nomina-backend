from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from dependencies.database import Base
from models.ajustes import AjusteDB
from models.cuentas import CuentasDB
from models.dispersiones import DispersionesDB
from models.empleados import EmpleadoDB
from models.prestamos import PrestamosDB
from models.salarios import SalariosDB


class RecibosDB(Base):
    __tablename__ = 'recibos'

    id_recibo = Column(Integer, primary_key=True, index=True)
    id_emplado = Column(Integer, ForeignKey(EmpleadoDB.id_empleado))
    id_dispersion = Column(Integer, ForeignKey(DispersionesDB.id_dispersion))
    monto = Column(Float)
    empleado = relationship('EmpleadoDB', lazy='joined')
    dispersion = relationship('DispersionDB', lazy='joined')
    detalles = relationship('RecibosDetalles')


class RecibosDetalleDB(Base):
    __tablename__ = 'recibos_detalle'

    id_recibos_detalle = Column(Integer, primary_key=True, index=True)
    id_recibo = Column(Integer,
                       ForeignKey(RecibosDB.id_recibo),
                       nullable=False)
    id_ajuste = Column(Integer,
                       ForeignKey(AjusteDB.id_ajuste),
                       nullable=True)
    id_prestamo = Column(Integer,
                         ForeignKey(PrestamosDB.id_prestamo),
                         nullable=True)
    id_salario = Column(Integer,
                        ForeignKey(SalariosDB.id_salario),
                        nullable=True)
    id_cuenta = Column(Integer,
                       ForeignKey(CuentasDB.id_cuenta),
                       nullable=True)
    texto = Column(String,
                   nullable=True)
    monto = Column(Float,
                   nullable=False)
    ajuste = relationship('AjusteDB', lazy='joined')
    cuenta = relationship('CuentaDB', lazy='joined')
    prestamo = relationship('PrestamosDB', lazy='joined')
    salario = relationship('SalariosDB', lazy='joined')
