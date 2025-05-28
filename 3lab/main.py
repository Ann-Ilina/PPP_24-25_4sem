# main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from app.api.endpoints import router
from app.db.db import engine
from app.models.models import Base
from app.websocket.websocket import websocket_endpoint

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # Убедись, что эта строка выполняется
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(router)
app.websocket("/ws")(websocket_endpoint)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Your API",
        version="1.0.0",
        description="API with Bearer Authentication",
        routes=app.routes,
    )
    security_scheme = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["components"]["securitySchemes"] = security_scheme
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi