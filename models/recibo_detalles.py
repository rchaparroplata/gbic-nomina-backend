from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from dependencies.database import Base
from models.ajustes import AjusteDB
from models.prestamos import PrestamosDB
from models.cuentas import CuentasDB
from models.recibos import ReciboDB
from models.salarios import SalariosDB


class RecibosDetalle(Base):
    __tablename__ = 'recibos_detalle'

    id_recibos_detalle = Column(Integer, primary_key=True, index=True)
    id_recibo = Column(Integer,
                       ForeignKey(ReciboDB.id_recibo),
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
    recibo = relationship('ReciboDB', lazy='joined')
    ajuste = relationship('AjusteDB', lazy='joined')
    cuenta = relationship('CuentaDB', lazy='joined')
    prestamo = relationship('PrestamosDB', lazy='joined')
    salario = relationship('SalariosDB', lazy='joined')
