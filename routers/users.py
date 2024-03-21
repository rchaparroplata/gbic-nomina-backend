from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from dependencies.database import get_db
from dependencies.users import (create_access_token, create_user, edit_user,
                                get_current_active_user, get_users,
                                user_resp_edit, user_responses)
from schemas.users import Token, User, UserIn, UserUpdate

router = APIRouter(
    prefix='/users',
    tags=['users']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_active_user)]


# @router.get('/Admin')
# async def admin(db: db_dependency):
#     admin_user_data = {
#         'username': 'Admin',
#         'password': '123',
#         'nombre': 'The Administrator',
#         'scopes': ['Admin'],
#         'activo': True
#     }
#     usr_admin = UserIn(**admin_user_data)
#     x = create_user(usr_admin, db)
#     return x


@router.post("/",
             status_code=status.HTTP_201_CREATED,
             responses=user_responses,
             response_model=User)
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
            responses={**user_responses, **user_resp_edit},
            response_model=User)
async def put_edit_user(db: db_dependency,
                        edit_user_request: UserUpdate,
                        current_user: Annotated[User, Security(
                            get_current_active_user,
                            scopes=['users:write']
                        )],
                        id_user: int
                        ):
    if id_user == 1 and current_user.id_user != 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='No puedes editar al Administardor')
    edited_user = edit_user(id_user, edit_user_request, db)
    return User.model_validate(edited_user)


@router.post('/token', response_model=Token, responses=user_responses)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: db_dependency,):
    token = create_access_token(form_data, db)
    return token


@router.get('/me', response_model=User, responses=user_responses,)
def me(current_user: user_dependency, db: db_dependency):
    return current_user


@router.get('/', response_model=list[User], responses=user_responses,)
async def get_all_users(
        db: db_dependency,
        current_user: Annotated[User, Security(get_current_active_user,
                                               scopes=["users:read"])],
        skip: int = 0,
        limit: int = 10
):
    users = get_users(db, skip, limit)
    return users
