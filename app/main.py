from fastapi import FastAPI
from .routes import auth_routes, service_router

app = FastAPI(title="Servicio de Envío de Correos", version="1.0")


app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])

app.include_router(service_router.router, prefix="/service", tags=["service"])


@app.get("/")
async def root():
    return {"message": "Servicio de Envío de Correos Activo"}


