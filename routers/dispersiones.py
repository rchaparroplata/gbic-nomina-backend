from typing import Annotated

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session
from starlette import status

from dependencies.database import get_db
from dependencies.dispersiones import (create_dispersion, delete_dispersion,
                                       get_dispersiones)
from dependencies.users import get_current_active_user, user_responses
from schemas.dispersiones import DispersionIn, DispersionOut
from schemas.users import User

router = APIRouter(
    prefix='/dispersiones',
    tags=['dispersiones']
)

db_dependency = Annotated[Session, Depends(get_db)]


# Get dispersiones
# Get dispersion detalle
# Generar Dispersion
# Generar Dispersion DryRun

@router.get('/',
            response_model=list[DispersionOut],
            responses=user_responses)
def get_all_dispersiones(
    db: db_dependency,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=['dispersiones:read'])],
    skip: int = 0,
    limit: int = 10
):
    dispersiones = get_dispersiones(db, skip, limit)
    return dispersiones


@router.post('/',
             status_code=status.HTTP_201_CREATED,
             response_model=DispersionOut,
             responses=user_responses)
def post_create_dispersion(
    db: db_dependency,
    create_request: DispersionIn,
    current_user: Annotated[User, Security(get_current_active_user,
                                           scopes=['dispersiones:write'])]
):
    new_dispersion = create_dispersion(db, create_request)
    return DispersionOut.model_validate(new_dispersion)


@router.delete('/{id_dispersion}',
               status_code=status.HTTP_204_NO_CONTENT,
               responses={**user_responses}
               )
def delete_delete_prestamo(
    db: db_dependency,
    id_dispersion: int,
    current_user: Annotated[User,
                            Security(get_current_active_user,
                                     scopes=['dispersiones:delete'])]):
    delete_dispersion(db, id_dispersion)
