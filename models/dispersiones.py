from sqlalchemy import Column, Date, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from dependencies.database import Base
from models.users import UserDB


class DispersionesDB(Base):
    __tablename__ = 'dispersiones'

    id_dispersion = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, server_default=func.current_date())
    periodo = Column(Integer)
    periodo_fecha = Column(Date)
    total = Column(Float)
    id_usuario = Column(Integer, ForeignKey(UserDB.id_user))
    usuario = relationship('UserDB', lazy='joined')
