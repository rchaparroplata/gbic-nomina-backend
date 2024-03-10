from typing import Optional

from pydantic import BaseModel, ConfigDict

from schemas.colonias import Colonia


class EmpleadoBase(BaseModel):
    nombre: str
    paterno: str
    materno: str
    rfc: str
    curp: str
    calle: str
    exterior: str
    interior: Optional[str] | None = None
    id_colonia:  int
    telefono: Optional[str] | None = None
    celular: Optional[str] | None = None
    activo: bool = True


class Empleado(EmpleadoBase):
    model_config = ConfigDict(from_attributes=True)
    id_empleado: int
    colonia: Colonia
