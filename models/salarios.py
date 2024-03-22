from sqlalchemy import Column, Date, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from dependencies.database import Base
from models.empleados import EmpleadoDB
from models.users import UserDB


class SalariosDB(Base):
    __tablename__ = 'salarios'

    id_salario = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, server_default=func.current_date())
    fecha_valido = Column(Date)
    monto = Column(Float)
    id_empleado = Column(Integer, ForeignKey(EmpleadoDB.id_empleado))
    id_usuario = Column(Integer, ForeignKey(UserDB.id_user))
    usuario = relationship('UserDB', lazy='joined')
    empleado = relationship('EmpleadoDB', lazy='joined')
