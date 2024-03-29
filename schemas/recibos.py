from datetime import date

from pydantic import (BaseModel, ConfigDict, Field, field_validator,
                      model_validator)
from pydantic.json_schema import SkipJsonSchema

from schemas.ajustes import Ajuste
from schemas.cuentas import Cuenta
from schemas.dispersiones import Dispersion
from schemas.empleados import Empleado
from schemas.prestamos import Prestamo
from schemas.salarios import Salario


class ReciboBase(BaseModel):
    id_empleado: int
    id_dispersion: int
    monto: float


class ReciboIn(ReciboBase):
    pass


class Recibo(ReciboBase):
    model_config = ConfigDict(from_attributes=True)

    id_recibo: int
    empleado: Empleado
    dispersion: Dispersion


class ReciboOut(Recibo):
    dispersion: SkipJsonSchema[Dispersion] = Field(exclude=True)
    empleado: str
    periodo: int
    periodo_fecha: date
    fecha: date

    @field_validator('empleado', mode='before')
    def nombre_empelado(cls, v):
        if v.nombre:
            return ' '.join([v.nombre, v.paterno, v.materno])
        return v  # pragma: no cover

    @model_validator(mode='before')
    def flat_dispersion(self) -> 'ReciboOut':
        self.periodo = self.dispersion.periodo
        self.periodo_fecha = self.dispersion.periodo_fecha
        self.fecha = self.dispersion.fecha

        return self


class ReciboDetallesbase(BaseModel):
    id_recibo: int
    id_ajuste: int
    id_prestamo: int
    id_salario: int
    id_cuenta: int
    texto: str
    monto: float


class ReciboDetalles(ReciboDetallesbase):
    model_config = ConfigDict(from_attributes=True)

    id_recibo_detalle: int
    ajuste: Ajuste
    cuenta: Cuenta
    prestamo: Prestamo
    salario: Salario


class ReciboDetallesOut(ReciboDetalles):
    ajuste: SkipJsonSchema[Ajuste] = Field(exclude=True)
    prestamo: SkipJsonSchema[Prestamo] = Field(exclude=True)
    salario: SkipJsonSchema[Salario] = Field(exclude=True)
    id_recibo: SkipJsonSchema[int] = Field(exclude=True)
    id_ajuste: SkipJsonSchema[int] = Field(exclude=True)
    id_prestamo: SkipJsonSchema[int] = Field(exclude=True)
    id_salario: SkipJsonSchema[int] = Field(exclude=True)
    id_cuenta: SkipJsonSchema[int] = Field(exclude=True)
    id_externo: int
    texto: str
    monto: float

    banco: str
    cuenta: str
    tipo: str

    @model_validator(mode='after')
    def flat_fields(self) -> 'ReciboDetallesOut':
        self.banco = self.cuenta.banco.nombre
        self.tipo = self.cuenta.tipo_txt
        self.cuenta = self.cuenta.numero

        if self.prestamo:
            self.id_externo = self.prestamo.id_prestamo
            self.monto = self.prestamo.monto_quincenal
            self.texto = self.prestamo.comentarios
        if self.salario:
            self.id_externo = self.salario.id_salario
            self.monto = self.salario.monto
            self.texto = 'Salario'
        if self.ajuste:
            self.id_externo = self.ajuste.id_ajuste
            self.monto = self.ajuste.monto
            self.texto = self.ajuste.motivo

        self.periodo = self.dispersion.periodo
        self.periodo_fecha = self.dispersion.periodo_fecha
        self.fecha = self.dispersion.fecha

        return self


class ReciboConDetalles(ReciboOut):
    detalles: list[ReciboDetallesOut]
