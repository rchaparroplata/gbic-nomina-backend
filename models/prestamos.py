from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from dependencies.database import Base
from models.empleados import EmpleadosDB
from models.users import UserDB


class PrestamosDB(Base):
    __tablename__ = 'prestamos'

    id_prestamo = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, server_default=func.current_date())
    fecha_inicio = Column(Date)
    monto = Column(Float)
    monto_quincenal = Column(Float)
    comentarios = Column(String, nullable=True)
    id_usuario = Column(Integer, ForeignKey(UserDB.id_user))
    id_empleado = Column(Integer, ForeignKey(EmpleadosDB.id_empleado))
    usuario = relationship("UserDB", lazy='joined')
    empleado = relationship("EmpleadosDB", lazy='joined')
