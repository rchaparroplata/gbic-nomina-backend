from pydantic import BaseModel, ConfigDict


class ColoniaBase(BaseModel):
    nombre: str
    ciudad: str
    estado: str
    cp: str


class Colonia(ColoniaBase):
    model_config = ConfigDict(from_attributes=True)
    
    id_colonia: int

