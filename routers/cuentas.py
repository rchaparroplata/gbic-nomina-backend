from typing import Annotated

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session
from starlette import status

from dependencies.cuentas import (create_cuenta, cuentas_resp_edit,
                                  delete_cuenta, edit_cuenta, get_cuentas)
from dependencies.database import get_db
from dependencies.users import get_current_active_user, user_responses
from schemas.cuentas import CuentaEdit, CuentaIn, CuentaOut
from schemas.users import User

router = APIRouter(
    prefix='/cuentas',
    tags=['cuentas']
)

db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/',
            responses=user_responses,
            response_model=list[CuentaOut])
def get_all_cuentas(
    db: db_dependency,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=["cuentas:read"])],
    skip: int = 0,
    limit: int = 10
):
    cuentas = get_cuentas(db, skip, limit)
    return cuentas


@router.post('/',
             status_code=status.HTTP_201_CREATED,
             responses=user_responses,
             response_model=CuentaOut)
def post_create_cuenta(
    db: db_dependency,
    create_request: CuentaIn,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=["cuentas:write"])]
):
    new_cuenta = create_cuenta(db, create_request, current_user)
    return CuentaOut.model_validate(new_cuenta)


@router.put('/{id_cuenta}',
            status_code=status.HTTP_202_ACCEPTED,
            responses={**user_responses, **cuentas_resp_edit},
            response_model=CuentaOut)
def put_edit_cuenta(
    db: db_dependency,
    edit_request: CuentaEdit,
    id_cuenta: int,
    current_user: Annotated[User,
                            Security(get_current_active_user,
                                     scopes=["cuentas:write"])]):
    edited_cuenta = edit_cuenta(id_cuenta, edit_request, db)
    return CuentaOut.model_validate(edited_cuenta)


@router.delete('/{id_cuenta}',
               status_code=status.HTTP_204_NO_CONTENT,
               responses={**user_responses, **cuentas_resp_edit}
               )
def delete_delete_cuenta(
    db: db_dependency,
    id_cuenta: int,
    current_user: Annotated[User,
                            Security(get_current_active_user,
                                     scopes=['cuentas:write'])]):
    delete_cuenta(db, id_cuenta)
