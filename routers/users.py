from dependencies.database import get_db
from dependencies.users import (
    create_access_token,
    create_user,
    edit_user,
    get_current_active_user,
    get_users
)
from fastapi import APIRouter, Depends, Security
from fastapi.security import OAuth2PasswordRequestForm
from schemas.users import UserIn, UserUpdate, Token, User
from starlette import status
from sqlalchemy.orm import Session
from typing import Annotated

router = APIRouter(
    prefix='/users',
    tags=['users']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_active_user)]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=User)
async def post_create_user(db: db_dependency,
                           create_user_request: UserIn,
                           current_user: Annotated[User, Security(
                               get_current_active_user,
                               scopes=["users:write"]
                                )]
                           ):
    new_user = create_user(create_user_request, db)
    return User.model_validate(new_user)


@router.put('/{id_user}',
            status_code=status.HTTP_202_ACCEPTED,
            response_model=User)
async def put_edit_user(db: db_dependency,
                        edit_user_request: UserUpdate,
                        current_user: Annotated[User, Security(
                            get_current_active_user,
                            scopes=['users:write']
                        )],
                        id_user: int
                        ):
    edited_user = edit_user(id_user, edit_user_request, db)
    return User.model_validate(edited_user)


@router.post('/token', response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: db_dependency):
    token = create_access_token(form_data, db)
    return token


@router.get('/me', response_model=User)
def me(current_user: user_dependency, db: db_dependency):
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
