from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.core.config import settings
from app.db.database import init_db
from app.api.routes import router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema profesional de inventario y facturación para ferreterías con normativa SENIAT Venezuela"
)

# Configurar CORS para permitir acceso desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Inicializar la base de datos al iniciar la aplicación"""
    await init_db()
    print(f"✅ {settings.APP_NAME} iniciado correctamente")
    print(f"📊 Base de datos: {settings.DATABASE_URL}")
    print(f"💱 Moneda base: {settings.BASE_CURRENCY}")
    print(f"🏦 Tasa BCV: Se actualizará automáticamente")


@app.get("/")
async def root():
    """Endpoint raíz con información del sistema"""
    return {
        "message": "Bienvenido al Sistema de Ferretería Venezuela",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Verificar estado del sistema"""
    return {"status": "healthy", "service": "ferreteria-api"}


# Incluir rutas de la API
app.include_router(router, prefix="/api/v1", tags=["API"])


# Servir archivos estáticos del frontend (en producción)
# frontend_build_path = os.path.join(os.path.dirname(__file__), "../../frontend/build")
# if os.path.exists(frontend_build_path):
#     app.mount("/static", StaticFiles(directory=frontend_build_path), name="static")
#     
#     @app.get("/{full_path:path}")
#     async def serve_frontend(full_path: str):
#         if not full_path.startswith("api"):
#             index_path = os.path.join(frontend_build_path, "index.html")
#             if os.path.exists(index_path):
#                 return FileResponse(index_path)
#         return {"error": "Not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
