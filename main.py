import uvicorn
from contextlib import asynccontextmanager
from dependencies.database import engine, Base
from fastapi import FastAPI
from routers.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users_router)


@app.get('/')
def root():
    return {'message': 'Server is running'}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
