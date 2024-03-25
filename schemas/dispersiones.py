from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator

from schemas.cuentas import Cuenta
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
    def flat_user(cls, v):
        if v.username:
            return v.username
        return v  # pragma: no cover


class _DispersionDetallesBase(BaseModel):
    id_dispersion: int
    id_cuenta: int
    monto: float


class DispersionDetalles(_DispersionDetallesBase):
    model_config = ConfigDict(from_attributes=True)

    cuenta: Cuenta
    id_dispersion_detalle: int


class DispersionConDetalles(DispersionOut):
    detalles: list[DispersionDetalles]
