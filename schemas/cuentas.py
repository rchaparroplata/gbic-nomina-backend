from datetime import date
from typing import Optional

from pydantic import (BaseModel, ConfigDict, field_validator,
                      model_validator)

from schemas.bancos import Banco
from schemas.empleados import Empleado
from schemas.users import User

tipo_dict = {
    1: 'Ahorro',
    2: 'Nómina'
}


class CuentaBase(BaseModel):
    numero: str
    tipo: int
    activa: bool = True
    id_banco: int
    id_empleado: int


class CuentaIn(CuentaBase):
    pass


class CuentaEdit(CuentaBase):
    pass


class Cuenta(CuentaBase):
    model_config = ConfigDict(from_attributes=True)

    id_cuenta: int
    id_usuario: int
    fecha: date
    usuario: User
    empleado: Empleado
    banco: Banco
    tipo_txt: Optional[str] | None = None

    @model_validator(mode='before')
    def validate_fechas(self) -> 'CuentaBase':
        t = self.tipo
        self.tipo_txt = tipo_dict.get(t)

        return self


class CuentaOut(Cuenta):
    usuario: str
    empleado: str
    banco: str

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

    @field_validator('banco', mode='before')
    def nombre_banco(cls, v):
        if v.nombre:
            return v.nombre
        return v  # pragma: no cover
