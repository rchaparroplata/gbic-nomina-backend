from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from dependencies.database import Base
from models.ajustes import AjustesDB
from models.cuentas import CuentasDB
from models.dispersiones import DispersionesDB
from models.empleados import EmpleadosDB
from models.prestamos import PrestamosDB
from models.salarios import SalariosDB


class RecibosDB(Base):
    __tablename__ = 'recibos'

    id_recibo = Column(Integer, primary_key=True, index=True)
    id_emplado = Column(Integer, ForeignKey(EmpleadosDB.id_empleado))
    id_dispersion = Column(Integer, ForeignKey(DispersionesDB.id_dispersion))
    monto = Column(Float)
    empleado = relationship('EmpleadosDB', lazy='joined')
    dispersion = relationship('DispersionesDB', lazy='joined')
    detalles = relationship('RecibosDetalleDB')


class RecibosDetalleDB(Base):
    __tablename__ = 'recibos_detalle'

    id_recibos_detalle = Column(Integer, primary_key=True, index=True)
    id_recibo = Column(Integer,
                       ForeignKey(RecibosDB.id_recibo),
                       nullable=False)
    id_ajuste = Column(Integer,
                       ForeignKey(AjustesDB.id_ajuste),
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
    ajuste = relationship('AjustesDB', lazy='joined')
    cuenta = relationship('CuentasDB', lazy='joined')
    prestamo = relationship('PrestamosDB', lazy='joined')
    salario = relationship('SalariosDB', lazy='joined')
