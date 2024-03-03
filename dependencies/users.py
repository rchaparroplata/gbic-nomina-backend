from datetime import timedelta, datetime
from typing import Annotated
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from schemas.users import Token, TokenData, User, UserIn
from jose import jwt, JWTError
from decouple import config
from models.users import Users

SECRET_KEY = config('SECRET_KEY')
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='users/token')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close


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
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenData(**payload)
        if token_data.username is None or token_data.id is None:
            raise credentials_exception
        user = get_user_by_username(token_data.username, db)
        if user is None:
            raise credentials_exception
        user.scopes = user.scopes.split(',')
        found = False
        if 'Admin' not in user.scopes and len(security_scopes.scopes) != 0:
            for scope in security_scopes.scopes:
                if scope in user.scopes:
                    found = True
                    continue
            if not found:
                raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Sin Privilegios",
                        headers={"WWW-Authenticate": authenticate_value},
                    )
        return User(**user.__dict__)
    except JWTError:
        raise credentials_exception


def get_users(db: Session, skip: int = 0, limit: int = 10) -> list[User]:
    users_db = db.query(Users).offset(skip).limit(limit).all()
    users = []
    for user in users_db:
        user.scopes = user.scopes.split(',')
        print('Ussr->', user)
        users.append(User.model_validate(user))
    return users


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
        ):
    if not current_user.activo:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return bcrypt_context.hash(password)


def get_user_by_username(username: str, db: Session) -> Users:
    user = db.query(Users).filter(Users.username == username).first()
    if user:
        return user


def authenticate_user(username: str, password: str, db: Session) -> Users:
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


def create_user(user_data: UserIn, db: Session):
    user_data_extra = user_data.__dict__.copy()
    user_data_extra.update(
        {'password_h': get_password_hash(user_data.password)})
    del user_data_extra['password']
    user_data_extra.update({'scopes': ','.join(user_data.scopes)})
    create_user = Users(**user_data_extra)
    db.add(create_user)
    db.commit()
    db.refresh(create_user)
