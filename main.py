from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from dependencies.database import Base, engine
from routers import ajustes, bancos, empleados, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title='GBIC Nomina API',
    lifespan=lifespan)

app.include_router(ajustes.router)
app.include_router(bancos.router)
app.include_router(empleados.router)
app.include_router(users.router)


@app.get('/')
def root():
    return {'message': 'Server is running'}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
