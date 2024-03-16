from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class UserBase(BaseModel):
    username: str
    nombre: str
    scopes: list[str]
    activo: bool = True


class UserIn(UserBase):
    password: str


class UserUpdate(UserIn):
    password: Optional[str] | None = None


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id_user: int

    @field_validator('scopes', mode='before')
    def split_str(cls, v):
        if isinstance(v, str):
            return v.split(',')
        return v


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int
    username: str
    nombre: str
