from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict

from schemas.users import User


class AjusteBase(BaseModel):
    fecha_inicio: date
    fecha_fin: Optional[date] | None = None
    motivo: str
    id_empleado: int


class Ajuste(AjusteBase):
    model_config = ConfigDict(from_attributes=True)
    id_ajuste: int
    id_usuario: int
    fecha: date
    usuario: User.username
