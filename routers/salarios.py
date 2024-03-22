from typing import Annotated

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session
from starlette import status

from dependencies.database import get_db
from dependencies.salarios import (create_salario, delete_salario,
                                   edit_salario, get_salarios,
                                   salarios_resp_edit)
from dependencies.users import get_current_active_user, user_responses
from schemas.salarios import SalarioEdit, SalarioIn, SalarioOut
from schemas.users import User

router = APIRouter(
    prefix='/salarios',
    tags=['salarios']
)

db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/',
            responses=user_responses,
            response_model=list[SalarioOut])
def get_all_salarios(
    db: db_dependency,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=["salarios:read"])],
    skip: int = 0,
    limit: int = 10
):
    salarios = get_salarios(db, skip, limit)
    return salarios


@router.post('/',
             status_code=status.HTTP_201_CREATED,
             responses=user_responses,
             response_model=SalarioOut)
def post_create_salario(
    db: db_dependency,
    create_request: SalarioIn,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=["salarios:write"])]
):
    new_salario = create_salario(db, create_request, current_user)
    return SalarioOut.model_validate(new_salario)


@router.put('/{id_salario}',
            status_code=status.HTTP_202_ACCEPTED,
            responses={**user_responses, **salarios_resp_edit},
            response_model=SalarioOut)
def put_edit_salario(
    db: db_dependency,
    edit_request: SalarioEdit,
    id_salario: int,
    current_user: Annotated[User,
                            Security(get_current_active_user,
                                     scopes=["salarios:write"])]):
    edited_salario = edit_salario(id_salario, edit_request, db)
    return SalarioOut.model_validate(edited_salario)


@router.delete('/{id_salario}',
               status_code=status.HTTP_204_NO_CONTENT,
               responses={**user_responses, **salarios_resp_edit}
               )
def delete_delete_salario(
    db: db_dependency,
    id_salario: int,
    current_user: Annotated[User,
                            Security(get_current_active_user,
                                     scopes=['salarios:writer'])]):
    delete_salario(db, id_salario)
