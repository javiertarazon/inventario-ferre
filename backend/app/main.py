from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import init_db, engine, Base
from app.core.config import settings
from app.api import (
    auth_router,
    products_router,
    customers_router,
    sales_router,
    exchange_rate_router
)
from app.services import bcv_service, ExchangeRateService
from app.core.database import async_session_maker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando aplicación...")
    
    # Crear tablas de base de datos
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Base de datos inicializada")
    
    # Intentar obtener tasa del BCV al iniciar
    logger.info("Obteniendo tasa de cambio del BCV...")
    bcv_result = await bcv_service.get_rate_with_alert()
    
    if bcv_result["is_alert"]:
        logger.warning(bcv_result["message"])
    else:
        logger.info(f"Tasa BCV obtenida: {bcv_result['rate']}")
        
        # Guardar tasa inicial en base de datos
        async with async_session_maker() as db:
            try:
                from sqlalchemy import update
                
                # Desactivar tasas anteriores
                await db.execute(
                    update(ExchangeRateService.__dict__.get('ExchangeRate'))
                    .where(ExchangeRateService.__dict__.get('ExchangeRate').is_active == True)
                    .values(is_active=False)
                )
                
                from app.models import ExchangeRate
                new_rate = ExchangeRate(
                    rate=bcv_result["rate"],
                    source=bcv_result["source"],
                    is_active=True
                )
                db.add(new_rate)
                await db.commit()
                logger.info("Tasa inicial guardada en base de datos")
            except Exception as e:
                logger.error(f"Error guardando tasa inicial: {e}")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema de Inventario y Facturación para Ferretería con normativa SENIAT Venezuela",
    lifespan=lifespan
)

# Configurar CORS para permitir acceso desde frontend y móviles
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios concretos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers de API
app.include_router(auth_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(customers_router, prefix="/api/v1")
app.include_router(sales_router, prefix="/api/v1")
app.include_router(exchange_rate_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Sistema de Ferretería - API REST",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Endpoint para verificar estado del servicio"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
