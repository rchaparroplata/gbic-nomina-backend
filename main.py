import uvicorn
from fastapi import FastAPI

from routers import ajustes, bancos, empleados, prestamos, users

app = FastAPI(title='GBIC Nomina API')

app.include_router(ajustes.router)
app.include_router(bancos.router)
app.include_router(empleados.router)
app.include_router(prestamos.router)
app.include_router(users.router)


@app.get('/')
def root():
    return {'message': 'Server is running'}


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(app, host="0.0.0.0", port=8000)
