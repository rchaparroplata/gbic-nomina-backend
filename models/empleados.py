from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from dependencies.database import Base
from models.colonias import ColoniaDB


class EmpleadoDB(Base):
    __tablename__ = 'empleados'

    id_empleado = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    paterno = Column(String)
    materno = Column(String)
    rfc = Column(String, unique=True)
    curp = Column(String, unique=True)
    calle = Column(String)
    exterior = Column(String)
    interior = Column(String, nullable=True)
    id_colonia = Column(Integer, ForeignKey(ColoniaDB.id_colonia))
    telefono = Column(String, nullable=True)
    celular = Column(String, nullable=True)
    activo = Column(Boolean, default=True)
    colonia = relationship("ColoniaDB", lazy='joined')
