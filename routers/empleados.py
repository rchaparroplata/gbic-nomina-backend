from typing import Annotated

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session
from starlette import status

from dependencies.database import get_db
from dependencies.empleados import (create_empleado, edit_empleado,
                                    get_empleados)
from dependencies.users import get_current_active_user
from schemas.empleados import Empleado, EmpleadoBase
from schemas.users import User

router = APIRouter(
    prefix='/empleados',
    tags=['empleados']
)

db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/', response_model=list[Empleado])
def get_all_empleados(
    db: db_dependency,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=["empleados:read"])],
    skip: int = 0,
    limit: int = 10
):
    empleados = get_empleados(db, skip, limit)
    return empleados


@router.post('/',
             status_code=status.HTTP_201_CREATED,
             response_model=Empleado)
def post_create_empleado(
    db: db_dependency,
    create_request: EmpleadoBase,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=["empleados:write"])]):
    new_empleado = create_empleado(db, create_request)
    return Empleado.model_validate(new_empleado)


@router.put('/{id_empleado}',
            status_code=status.HTTP_202_ACCEPTED,
            response_model=Empleado)
def put_edit_empleado(
    db: db_dependency,
    edit_request: EmpleadoBase,
    id_empleado: int,
    current_user: Annotated[User,
                            Security(get_current_active_user,
                                     scopes=["empleados:write"])]):
    edited_empleado = edit_empleado(id_empleado, edit_request, db)
    return Empleado.model_validate(edited_empleado)
