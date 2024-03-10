from sqlalchemy import Boolean, Column, Integer, String

from dependencies.database import Base


class UserDB(Base):
    __tablename__ = 'users'

    id_user = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    nombre = Column(String)
    password_h = Column(String)
    scopes = Column(String)
    activo = Column(Boolean, default=True)
