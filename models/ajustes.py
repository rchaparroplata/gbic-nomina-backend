from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from dependencies.database import Base
from models.empleados import EmpleadosDB
from models.users import UserDB


class AjustesDB(Base):
    __tablename__ = 'ajustes'

    id_ajuste = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, server_default=func.current_date())
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date, nullable=True)
    motivo = Column(String)
    monto = Column(Float)
    id_empleado = Column(Integer, ForeignKey(EmpleadosDB.id_empleado))
    id_usuario = Column(Integer, ForeignKey(UserDB.id_user))
    usuario = relationship("UserDB", lazy='joined')
    empleado = relationship('EmpleadosDB', lazy='joined')
