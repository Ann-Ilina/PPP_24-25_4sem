# main.py
from fastapi import FastAPI
from app.api.endpoints import router
from app.db.db import engine
from app.models.models import Base

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
