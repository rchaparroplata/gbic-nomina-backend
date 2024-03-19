from datetime import datetime, timedelta
from typing import Annotated
from pydantic import ValidationError

from decouple import config
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from dependencies.database import get_db
from models.users import UserDB
from schemas.users import Token, TokenData, User, UserIn

SECRET_KEY = config('SECRET_KEY')
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='users/token')


user_responses = {
    status.HTTP_400_BAD_REQUEST: {
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'detail': {
                            'type': "string"
                        }
                    }
                },
                'example': {'detail': 'Usuario Desactivado'}
            }
        }
    },
    status.HTTP_401_UNAUTHORIZED: {
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'detail': {
                            'type': "string"
                        }
                    }
                },
                'example': {'detail': "Could not validate credentials"}
            }
        }
    },
    status.HTTP_403_FORBIDDEN: {
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'detail': {
                            'type': "string"
                        }
                    }
                },
                'example': {'detail': "Sin Privilegios Necesarios"}
            }
        }
    }
}

user_resp_edit = {
    status.HTTP_404_NOT_FOUND: {
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'detail': {
                            'type': "string"
                        }
                    }
                },
                'example': {'detail': "Usuario con id: 1 no encontrado"}
            }
        }
    }
}


async def get_current_user(
        security_scopes: SecurityScopes,
        token: Annotated[str, Depends(oauth2_bearer)],
        db: Annotated[Session, Depends(get_db)]) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = 'Bearer'
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    scope_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Sin Privilegios Necesarios",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenData.model_validate(payload)
        user = get_user_by_username(token_data.username, db)
        if user is None:
            raise credentials_exception
        found = False
        if 'Admin' not in user.scopes and len(security_scopes.scopes) != 0:
            for scope in security_scopes.scopes:
                if scope in user.scopes:
                    found = True
                    break
            if not found:
                raise scope_exception
        return User.model_validate(user)
    except (ValidationError, JWTError):
        raise credentials_exception


def get_users(db: Session, skip: int = 0, limit: int = 10) -> list[User]:
    users_db = db.query(UserDB).offset(skip).limit(limit).all()
    users = []
    for user in users_db:
        users.append(User.model_validate(user))
    return users


def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
        ):
    if not current_user.activo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Usuario Desactivado")
    return current_user


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return bcrypt_context.hash(password)


def get_user_by_username(username: str, db: Session) -> UserDB:
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if user:
        return user


def authenticate_user(username: str, password: str, db: Session) -> UserDB:
    user = get_user_by_username(username, db)
    if not user:
        return False
    if not verify_password(password, user.password_h):
        return False
    return user


def encode_token(data: dict, exp: timedelta):
    encode = data.copy()
    expires = datetime.utcnow() + exp
    encode.update({'exp': expires})
    jwt_encode = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_encode


def create_access_token(form_data: dict, db: Session) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Usuario y/o Password no validos')
    token = encode_token(
        {
            "username": user.username,
            "id": user.id_user,
            "nombre": user.nombre,
            "scopes": user.scopes
        }, timedelta(minutes=20))
    return Token(access_token=token, token_type="bearer")


def create_user(user_data: UserIn, db: Session) -> UserDB:
    db_user = get_user_by_username(user_data.username, db)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Usuario ya existente')
    user_data_extra = user_data.model_dump()
    user_data_extra.update(
        {'password_h': get_password_hash(user_data.password)})
    del user_data_extra['password']
    user_data_extra.update({'scopes': ','.join(user_data.scopes)})
    user_create = UserDB(**user_data_extra)
    db.add(user_create)
    db.commit()
    db.refresh(user_create)
    return user_create


def edit_user(id_user: int, user_data: UserIn, db: Session) -> UserDB:
    db_user = db.query(UserDB).filter(UserDB.id_user == id_user).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Usuario con id: {id_user} no encontrado')
    updated_data = user_data.model_dump(exclude_unset=True)
    if user_data.password:
        updated_data.update(
             {'password_h': get_password_hash(user_data.password)}
        )
        del updated_data['password']
    updated_data.update({'scopes': ','.join(user_data.scopes)})
    for key, value in updated_data.items():
        setattr(db_user, key, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
