from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from dependencies.database import Base
from models.bancos import BancosDB
from models.empleados import EmpleadoDB
from models.users import UserDB


class CuentasDB(Base):
    __tablename__ = 'cuentas'

    id_cuenta = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, server_default=func.current_date())
    numero = Column(String)
    tipo = Column(Integer)
    activa = Column(Boolean, default=True)
    id_banco = Column(Integer, ForeignKey(BancosDB.id_banco))
    id_empleado = Column(Integer, ForeignKey(EmpleadoDB.id_empleado))
    id_usuario = Column(Integer, ForeignKey(UserDB.id_user))
    banco = relationship('BancosDB', lazy='joined')
    usuario = relationship("UserDB", lazy='joined')
    empleado = relationship('EmpleadoDB', lazy='joined')
