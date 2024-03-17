from sqlalchemy import Boolean, Column, Integer, String

from dependencies.database import Base


class BancosDB(Base):
    __tablename__ = 'bancos'

    id_banco = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True)
    activo = Column(Boolean, default=True)
