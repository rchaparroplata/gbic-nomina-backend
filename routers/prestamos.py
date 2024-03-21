from typing import Annotated

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session
from starlette import status

from dependencies.database import get_db
from dependencies.prestamos import (create_prestamo, edit_prestamo,
                                    get_prestamos, prestamos_resp_edit)
from dependencies.users import get_current_active_user, user_responses
from schemas.prestamos import PrestamoIn, PrestamoOut
from schemas.users import User

router = APIRouter(
    prefix='/prestamos',
    tags=['prestamos']
)

db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/',
            responses=user_responses,
            response_model=list[PrestamoOut])
def get_all_prestamos(
    db: db_dependency,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=["prestamos:read"])],
    skip: int = 0,
    limit: int = 10
):
    prestamos = get_prestamos(db, skip, limit)
    return prestamos


@router.post('/',
             status_code=status.HTTP_201_CREATED,
             responses=user_responses,
             response_model=PrestamoOut)
def post_create_prestamo(
    db: db_dependency,
    create_request: PrestamoIn,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=["prestamos:write"])]
):
    new_prestamo = create_prestamo(db, create_request, current_user)
    return PrestamoOut.model_validate(new_prestamo)


@router.put('/{id_prestamo}',
            status_code=status.HTTP_202_ACCEPTED,
            responses={**user_responses, **prestamos_resp_edit},
            response_model=PrestamoOut)
def put_edit_prestamo(
    db: db_dependency,
    edit_request: PrestamoIn,
    id_prestamo: int,
    current_user: Annotated[User,
                            Security(get_current_active_user,
                                     scopes=["prestamos:write"])]):
    edited_prestamo = edit_prestamo(id_prestamo, edit_request, db)
    return PrestamoOut.model_validate(edited_prestamo)
