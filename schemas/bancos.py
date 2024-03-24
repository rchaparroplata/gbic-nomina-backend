from pydantic import BaseModel, ConfigDict


class BancoBase(BaseModel):
    nombre: str
    activo: bool = True


class BancoIn(BancoBase):
    pass


class Banco(BancoBase):
    model_config = ConfigDict(from_attributes=True)
    
    id_banco: int


class BancoOut(Banco):
    pass
