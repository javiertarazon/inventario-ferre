from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.schemas import ExchangeRateResponse
from app.services import ExchangeRateService, bcv_service


router = APIRouter(prefix="/exchange-rate", tags=["Tasa de Cambio"])


@router.get("/", response_model=ExchangeRateResponse)
async def get_current_exchange_rate(db: AsyncSession = Depends(get_db)):
    """Obtiene la tasa de cambio actual"""
    rate = await ExchangeRateService.get_current_rate(db)
    
    if not rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay tasa de cambio registrada"
        )
    
    return rate


@router.get("/bcv")
async def get_bcv_rate():
    """
    Obtiene la tasa de cambio del BCV con reintentos automáticos.
    Si falla después de 3 intentos, retorna alerta con tasa por defecto.
    """
    result = await bcv_service.get_rate_with_alert()
    
    return {
        "rate": result["rate"],
        "message": result["message"],
        "is_alert": result["is_alert"],
        "source": result["source"],
        "default_rate_used": result["default_rate_used"]
    }


@router.post("/", response_model=ExchangeRateResponse)
async def set_manual_exchange_rate(
    rate: float,
    db: AsyncSession = Depends(get_db)
):
    """Establece una tasa de cambio manual"""
    if rate <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La tasa debe ser mayor a 0"
        )
    
    new_rate = await ExchangeRateService.set_new_rate(
        db, 
        rate, 
        source="manual",
        deactivate_previous=True
    )
    
    return new_rate


@router.post("/refresh-bcv")
async def refresh_bcv_rate(db: AsyncSession = Depends(get_db)):
    """
    Refresca la tasa de cambio desde el BCV.
    Útil para actualizar manualmente cuando hay alertas.
    """
    result = await bcv_service.get_rate_with_alert()
    
    if result["is_alert"]:
        return {
            "success": False,
            "message": result["message"],
            "rate": result["rate"]
        }
    
    # Guardar nueva tasa
    new_rate = await ExchangeRateService.set_new_rate(
        db,
        result["rate"],
        source="BCV",
        deactivate_previous=True
    )
    
    return {
        "success": True,
        "message": result["message"],
        "rate": new_rate.rate,
        "products_updated": True
    }
