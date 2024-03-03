import uvicorn
from database import engine
from fastapi import Depends, FastAPI
from typing import Annotated
from sqlalchemy.orm import Session
from routers.users import router as users_router
import models.users
from dependencies.users import get_db, get_current_active_user

app = FastAPI()

app.include_router(users_router)

models.users.Base.metadata.create_all(bind=engine)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_active_user)]


@app.get('/')
def root():
    return {'message': 'Server is running'}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
