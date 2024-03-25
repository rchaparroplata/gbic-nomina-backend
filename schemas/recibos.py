from pydantic import BaseModel, ConfigDict, field_validator

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
    empleado: str

    @field_validator('empleado', mode='before')
    def nombre_empelado(cls, v):
        if v.nombre:
            return ' '.join([v.nombre, v.paterno, v.materno])
        return v  # pragma: no cover


class _ReciboDetallesbase(BaseModel):
    id_recibo: int
    id_ajuste: int
    id_prestamo: int
    id_salario: int
    id_cuenta: int
    texto: str
    monto: float


class ReciboDetalles(_ReciboDetallesbase):
    model_config = ConfigDict(from_attributes=True)

    id_recibo_detalle: int
    ajuste: Ajuste
    cuenta: Cuenta
    prestamo: Prestamo
    salario: Salario


class ReciboConDetalles(ReciboOut):
    detalles: list[ReciboDetalles]
