from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordRequestForm
from schemas.users import UserIn, Token, User
from starlette import status
from typing import Annotated
from dependencies.users import (
    create_access_token,
    create_user,
    get_db,
    get_current_active_user,
    get_user_by_username,
    get_users
)
from sqlalchemy.orm import Session

router = APIRouter(
    prefix='/users',
    tags=['users']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_active_user)]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def post_create_user(db: db_dependency,
                           create_user_request: UserIn,
                           current_user: Annotated[User, Security(
                               get_current_active_user,
                               scopes=["users:write"])]
                           ):
    db_user = get_user_by_username(create_user_request.username, db)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Usuario ya existente')
    create_user(create_user_request, db)


@router.post('/token', response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: db_dependency):
    token = create_access_token(form_data, db)
    return token


@router.get('/me', response_model=User)
def me(current_user: user_dependency, db: db_dependency):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Favor de iniciar sesion')
    return current_user


@router.get('/', response_model=list[User])
async def get_all_users(
        db: db_dependency,
        current_user: Annotated[User, Security(get_current_active_user,
                                               scopes=["users:read"])],
        skip: int = 0,
        limit: int = 10
):
    users = get_users(db, skip, limit)
    return users
