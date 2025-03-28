# main.py
from fastapi import FastAPI
from app.api.endpoints import router
from app.db.db import engine
from app.models.models import Base

app = FastAPI()
app.include_router(router)

from fastapi import FastAPI
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.openapi.models import SecurityScheme
from fastapi.openapi.utils import get_openapi
from app.api.endpoints import router  # Подключаем роутеры

app = FastAPI()

# Подключаем эндпоинты
app.include_router(router)

# Добавляем схему аутентификации вручную
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


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)