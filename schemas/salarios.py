from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from schemas.empleados import Empleado
from schemas.users import User


class SalarioBase(BaseModel):
    fecha_valido: date
    monto: float
    id_empleado: int


class SalarioIn(SalarioBase):
    pass


class SalarioEdit(SalarioBase):
    id_empleado: Optional[int] | None = None


class Salario(SalarioBase):
    model_config = ConfigDict(from_attributes=True)

    id_salario: int
    id_usuario: int
    fecha: date
    usuario: User
    empleado: Empleado


class SalarioOut(Salario):
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
