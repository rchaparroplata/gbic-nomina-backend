from datetime import date
from typing import Optional

from pydantic import (BaseModel, ConfigDict, Field, field_validator,
                      model_validator)
from pydantic.json_schema import SkipJsonSchema

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
    id_usuario: SkipJsonSchema[int] = Field(exclude=True)
    usuario: str

    @field_validator('usuario', mode='before')
    def flat_user(cls, v):
        if v.username:
            return v.username
        return v  # pragma: no cover


class DispersionDetallesBase(BaseModel):
    id_dispersion: int
    id_cuenta: int
    monto: float


class DispersionDetalles(DispersionDetallesBase):
    model_config = ConfigDict(from_attributes=True)

    cuenta: Cuenta
    id_dispersiones_detalle: int


class DispersionDetallesOut(DispersionDetalles):
    id_dispersion: SkipJsonSchema[int] = Field(exclude=True)
    id_cuenta: SkipJsonSchema[int] = Field(exclude=True)
    cuenta_tmp: SkipJsonSchema[Cuenta] = Field(exclude=True)
    banco: str
    cuenta: str | None = None
    empleado: str
    tipo: str

    @model_validator(mode="wrap")
    def flat_fields(self, handler) -> 'DispersionDetallesOut':
        c = self.cuenta
        e = c.empleado
        numero = c.numero
        self.banco = c.banco.nombre
        self.empleado = ' '.join([e.nombre, e.paterno, e.materno])
        self.cuenta_tmp = self.cuenta
        del self.cuenta
        self.tipo = ''
        validated_self = handler(self)
        validated_self.cuenta = numero
        validated_self.tipo = validated_self.cuenta_tmp.tipo_txt
        del validated_self.cuenta_tmp
        return validated_self


class DispersionConDetalles(DispersionOut):
    detalles: list[DispersionDetallesOut]
