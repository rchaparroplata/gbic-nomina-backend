from sqlalchemy import Column, Date, ForeignKey, Integer, String, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from dependencies.database import Base
from models.empleados import EmpleadoDB
from models.users import UserDB


class AjusteDB(Base):
    __tablename__ = 'ajustes'

    id_ajuste = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, server_default=func.current_date())
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date, nullable=True)
    motivo = Column(String)
    monto = Column(Float)
    id_empleado = Column(Integer, ForeignKey(EmpleadoDB.id_empleado))
    id_usuario = Column(Integer, ForeignKey(UserDB.id_user))
    usuario = relationship("UserDB", lazy='joined')