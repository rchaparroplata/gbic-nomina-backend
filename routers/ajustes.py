from typing import Annotated

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session
from starlette import status

from dependencies.ajustes import create_ajuste, edit_ajuste, get_ajustes
from dependencies.database import get_db
from dependencies.users import get_current_active_user
from schemas.ajustes import AjusteIn, AjusteOut
from schemas.users import User

router = APIRouter(
    prefix='/ajustes',
    tags=['ajustes']
)

db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/', response_model=list[AjusteOut])
def get_all_ajustes(
    db: db_dependency,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=["ajustes:read"])],
    skip: int = 0,
    limit: int = 10
):
    ajustes = get_ajustes(db, skip, limit)
    return ajustes


@router.post('/',
             status_code=status.HTTP_201_CREATED,
             response_model=AjusteOut)
def post_create_ajuste(
    db: db_dependency,
    create_request: AjusteIn,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=["ajustes:write"])]
):
    new_ajuste = create_ajuste(db, create_request, current_user)
    return AjusteOut.model_validate(new_ajuste)


@router.put('/{id_ajuste}',
            status_code=status.HTTP_202_ACCEPTED,
            response_model=AjusteOut)
def put_edit_ajuste(
    db: db_dependency,
    edit_request: AjusteIn,
    id_ajuste: int,
    current_user: Annotated[User,
                            Security(get_current_active_user,
                                     scopes=["ajustes:write"])]):
    edited_ajuste = edit_ajuste(id_ajuste, edit_request, db)
    return AjusteOut.model_validate(edited_ajuste)
