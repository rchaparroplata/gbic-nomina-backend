from pydantic import BaseModel, ConfigDict


class BancoBase(BaseModel):
    nombre: str
    activo: bool = True


class BancoIn(BancoBase):
    pass


class Banco(BancoBase):
    id_banco: int
    model_config = ConfigDict(from_attributes=True)


class BancoOut(Banco):
    pass
