from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from models.empleados import EmpleadoDB
from schemas.empleados import Empleado, EmpleadoIn


def get_empleados(db: Session,
                  skip: int = 0,
                  limit: int = 10) -> list[Empleado]:
    empleados_db = db.query(EmpleadoDB).offset(skip).limit(limit).all()
    empleados = []
    for empleado in empleados_db:
        empleados.append(Empleado.model_validate(empleado))
    return empleados


def create_empleado(db: Session,
                    empleado_data: EmpleadoIn) -> EmpleadoDB:
    emp_rfc = db.query(EmpleadoDB)\
        .filter(EmpleadoDB.rfc == empleado_data.rfc).first()
    if emp_rfc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='RFC ya registrado')
    emp_curp = db.query(EmpleadoDB)\
        .filter(EmpleadoDB.curp == empleado_data.curp).first()
    if emp_curp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='CURP ya registrado')
    empleado_create = EmpleadoDB(**empleado_data.model_dump())
    db.add(empleado_create)
    db.commit()
    db.refresh(empleado_create)
    return empleado_create


def edit_empleado(id_emp: int,
                  empleado_data: EmpleadoIn,
                  db: Session):
    empleado_db = db.query(EmpleadoDB)\
        .filter(EmpleadoDB.id_empleado == id_emp).first()
    if not empleado_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Empleado con id: {id_emp} no encontrado')
    emp_rfc = db.query(EmpleadoDB)\
        .filter((EmpleadoDB.rfc == empleado_data.rfc)
                & (EmpleadoDB.id_empleado != id_emp)).first()
    if emp_rfc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='RFC ya registrado')
    emp_curp = db.query(EmpleadoDB)\
        .filter((EmpleadoDB.curp == empleado_data.curp)
                & (EmpleadoDB.id_empleado != id_emp)).first()
    if emp_curp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='CURP ya registrado')
    edited_data = empleado_data.model_dump(exclude_unset=True)
    for key, value in edited_data.items():
        setattr(empleado_db, key, value)
    db.add(empleado_db)
    db.commit()
    db.refresh(empleado_db)
    return empleado_db
