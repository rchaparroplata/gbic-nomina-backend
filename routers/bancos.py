from typing import Annotated

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session
from starlette import status

from dependencies.bancos import (create_banco, delete_banco, edit_banco,
                                 get_bancos)
from dependencies.database import get_db
from dependencies.users import get_current_active_user, user_responses
from schemas.bancos import BancoIn, BancoOut
from schemas.users import User

router = APIRouter(
    prefix='/bancos',
    tags=['bancos']
)

db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/',
            response_model=list[BancoOut],
            responses=user_responses)
def get_all_bancos(
    db: db_dependency,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=['bancos:read'])],
    skip: int = 0,
    limit: int = 10
):
    bancos = get_bancos(db, skip, limit)
    return bancos


@router.post('/',
             status_code=status.HTTP_201_CREATED,
             response_model=BancoOut,
             responses=user_responses)
def post_create_banco(
    db: db_dependency,
    create_request: BancoIn,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=['bancos:write'])]
):
    new_banco = create_banco(db, create_request)
    return BancoOut.model_validate(new_banco)


@router.put('/{id_banco}',
            status_code=status.HTTP_202_ACCEPTED,
            response_model=BancoOut,
            responses=user_responses)
def put_edit_banco(
    db: db_dependency,
    edit_request: BancoIn,
    id_banco: int,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=['bancos:write'])]
):
    edited_banco = edit_banco(db, id_banco, edit_request)
    return BancoOut.model_validate(edited_banco)


@router.delete('/{id_banco}',
               status_code=status.HTTP_204_NO_CONTENT,
               responses={**user_responses}
               )
def delete_delete_banco(
    db: db_dependency,
    id_banco: int,
    current_user: Annotated[User,
                            Security(get_current_active_user,
                                     scopes=['bancos:write'])]):
    delete_banco(db, id_banco)
