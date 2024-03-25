from typing import Annotated

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from dependencies.database import get_db
from dependencies.recibos import (get_recibo, get_recibos,
                                  get_recibos_dispersion, get_recibos_empleado)
from dependencies.users import get_current_active_user, user_responses
from schemas.recibos import ReciboConDetalles, ReciboOut
from schemas.users import User

router = APIRouter(
    prefix='/recibos',
    tags=['recibos']
)

db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/',
            response_model=list[ReciboOut],
            responses=user_responses)
def get_all_recibos(
    db: db_dependency,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=['recibos:read'])],
    skip: int = 0,
    limit: int = 10
):
    recibos = get_recibos(db, skip, limit)
    return recibos


@router.get('/{id_recibo}',
            response_model=ReciboConDetalles,
            responses=user_responses)
def get_on_recibo(
    db: db_dependency,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=['recibos:read'])],
    id_recibo: int
):
    recibos = get_recibo(db, id_recibo)
    return recibos


@router.get('/empleado/{id_emp}',
            response_model=list[ReciboOut],
            responses=user_responses)
def get_all_recibos_empleado(
    db: db_dependency,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=['recibos:read'])],
    id_empleado: int
):
    recibos = get_recibos_empleado(db, id_empleado)
    return recibos


@router.get('/dispersion/{id_disp}',
            response_model=list[ReciboOut],
            responses=user_responses)
def get_all_recibos_dispersion(
    db: db_dependency,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=['recibos:read'])],
    id_disp: int
):
    recibos = get_recibos_dispersion(db, id_disp)
    return recibos
