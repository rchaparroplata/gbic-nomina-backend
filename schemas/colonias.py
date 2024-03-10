from pydantic import BaseModel, ConfigDict


class ColoniaBase(BaseModel):
    nombre: str
    ciudad: str
    estado: str
    cp: str


class Colonia(ColoniaBase):
    id_colonia: int

    model_config = ConfigDict(from_attributes=True)
