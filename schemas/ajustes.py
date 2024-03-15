from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator
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


class Ajuste(AjusteBase):
    model_config = ConfigDict(from_attributes=True)
    id_ajuste: int
    id_usuario: int
    fecha: date
    usuario: str
