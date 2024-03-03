from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    username: str
    nombre: str
    scopes: list[str]


class UserIn(UserBase):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int
    username: str
    nombre: str

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id_user: int
    activo: bool = True



class UserInDB(User):
    password_h: str