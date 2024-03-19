from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from models.prestamos import PrestamosDB
from schemas.prestamos import PrestamoIn, PrestamoOut
from schemas.users import User

prestamos_resp_edit = {
    status.HTTP_404_NOT_FOUND: {
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'detail': {
                            'type': "string"
                        }
                    }
                },
                'example': {'detail': "Prestamo con id: 1 no encontrado"}
            }
        }
    }
}


def get_prestamos(db: Session,
                  skip: int = 0,
                  limit: int = 10) -> list[PrestamoOut]:
    prestamo_db = db.\
        query(PrestamosDB)\
        .offset(skip)\
        .limit(limit).all()
    prestamos = [PrestamoOut.model_validate(prestamo)
                 for prestamo in prestamo_db]
    return prestamos


def create_prestamo(db: Session,
                    input_data: PrestamoIn,
                    current_user: User) -> PrestamosDB:
    prestamo_create = PrestamosDB(**input_data.model_dump(exclude_unset=True),
                                  id_usuario=current_user.id_user)
    db.add(prestamo_create)
    db.commit()
    db.refresh(prestamo_create)
    return prestamo_create


def edit_prestamo(id_pres: int,
                  input_data: PrestamoIn,
                  db: Session):
    prestamo_db = db.query(PrestamosDB)\
        .filter(PrestamosDB.id_prestamo == id_pres).first()
    if not prestamo_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Prestamo con id: {id_pres} no encontrado')
    del input_data.id_empleado
    edited_data = input_data.model_dump(exclude_unset=True)
    for key, value in edited_data.items():
        setattr(prestamo_db, key, value)
    db.add(prestamo_db)
    db.commit()
    db.refresh(prestamo_db)
    return prestamo_db
