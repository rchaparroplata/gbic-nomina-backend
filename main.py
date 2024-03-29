import uvicorn
from fastapi import FastAPI

from routers import (ajustes, bancos, cuentas, dispersiones, empleados,
                     prestamos, recibos, salarios, users)

app = FastAPI(title='GBIC Nomina API')

app.include_router(ajustes.router)
app.include_router(cuentas.router)
app.include_router(dispersiones.router)
app.include_router(bancos.router)
app.include_router(empleados.router)
app.include_router(prestamos.router)
app.include_router(recibos.router)
app.include_router(salarios.router)
app.include_router(users.router)


@app.get('/')
def root():
    return {'message': 'Server is running'}


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(app, host="0.0.0.0", port=8000)
