from sqlalchemy import Column, Integer, String

from dependencies.database import Base


class ColoniaDB(Base):
    __tablename__ = 'colonias'

    id_colonia = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    ciudad = Column(String)
    estado = Column(String)
    cp = Column(String, index=True)
