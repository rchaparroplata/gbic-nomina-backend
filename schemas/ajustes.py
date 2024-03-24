from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from schemas.empleados import Empleado
from schemas.users import User


class AjusteBase(BaseModel):
    fecha_inicio: date
    fecha_fin: Optional[date] | None = None
    motivo: str
    monto: float
    id_empleado: int

    @model_validator(mode='after')
    def validate_fechas(self) -> 'AjusteBase':
        f_ini = self.fecha_inicio
        f_fin = self.fecha_fin

        if f_fin < f_ini:
            raise ValueError('La fecha final debe ser después de la inicial')
        return self


class AjusteIn(AjusteBase):
    pass


class Ajuste(AjusteBase):
    model_config = ConfigDict(from_attributes=True)

    id_ajuste: int
    id_usuario: int
    fecha: date
    usuario: User
    empleado: Empleado


class AjusteOut(Ajuste):
    usuario: str
    empleado: str

    @field_validator('usuario', mode='before')
    def flat_usuario(cls, v):
        if v.username:
            return v.username
        return v  # pragma: no cover

    @field_validator('empleado', mode='before')
    def nombre_empelado(cls, v):
        if v.nombre:
            return ' '.join([v.nombre, v.paterno, v.materno])
        return v  # pragma: no cover

