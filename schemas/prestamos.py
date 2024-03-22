from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from schemas.empleados import Empleado
from schemas.users import User


class PrestamoBase(BaseModel):
    fecha_inicio: date
    monto: float
    monto_quincenal: float
    comentarios: Optional[str] | None = None
    id_empleado: int

    @model_validator(mode='after')
    def validate_fechas(self) -> 'PrestamoBase':
        m_t = self.monto
        m_q = self.monto_quincenal

        if m_q > m_t:
            raise ValueError('El monto quicenal no puede ser mayor al total')
        return self


class PrestamoIn(PrestamoBase):
    pass


class PrestamoEdit(PrestamoBase):
    id_empleado: Optional[int] | None = None


class Prestamo(PrestamoBase):
    model_config = ConfigDict(from_attributes=True)
    id_prestamo: int
    id_usuario: int
    fecha: date
    usuario: User
    empleado: Empleado


class PrestamoOut(PrestamoBase):
    id_prestamo: int
    fecha: date
    usuario: str
    empleado: str

    @field_validator('usuario', mode='before')
    def flat_usuario(cls, v):
        if v.username:
            return v.username
        return v

    @field_validator('empleado', mode='before')
    def nombre_empelado(cls, v):
        if v.nombre:
            return ' '.join([v.nombre, v.paterno, v.materno])

    model_config = ConfigDict(from_attributes=True)
