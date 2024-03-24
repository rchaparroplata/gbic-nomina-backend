from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator

from schemas.users import User


class DispersionBase(BaseModel):
    periodo: int
    periodo_fecha: date


class DispersionIn(DispersionBase):
    pass


class Dispersion(DispersionBase):
    model_config = ConfigDict(from_attributes=True)

    id_dispersion: int
    fecha: date
    total: float
    id_usuario: int
    usuario: User


class DispersionOut(Dispersion):
    usuario: str

    @field_validator('usuario', mode='before')
    def falt_user(cls, v):
        if v.username:
            return v.username
        return v  # pragma: no cover
