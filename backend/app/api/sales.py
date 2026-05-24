from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.database import get_db
from app.schemas import SaleCreate, SaleResponse
from app.services import SaleService, ExchangeRateService, bcv_service
from app.core.jwt import verify_token


router = APIRouter(prefix="/sales", tags=["Ventas/Facturación"])


async def get_current_user(token: str = None):
    """Dependencia para obtener usuario actual (simplificada)"""
    return {"username": "test_user", "role": "admin", "id": 1}


@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
async def create_sale(
    sale_data: SaleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Crea una nueva venta/factura.
    Calcula automáticamente IVA (16%) e IGTF (3% si paga en divisas).
    """
    # Obtener tasa de cambio actual
    current_rate = await ExchangeRateService.get_current_rate(db)
    
    if not current_rate:
        # Intentar obtener del BCV
        bcv_result = await bcv_service.get_rate_with_alert()
        exchange_rate = bcv_result["rate"]
        
        # Guardar la tasa
        from app.services import ExchangeRateService
        await ExchangeRateService.set_new_rate(
            db, 
            exchange_rate, 
            source=bcv_result["source"]
        )
    else:
        exchange_rate = current_rate.rate
    
    try:
        sale = await SaleService.create_sale(
            db, 
            sale_data, 
            exchange_rate,
            user_id=current_user.get("id", 1)
        )
        return sale
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[SaleResponse])
async def get_sales(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene lista de ventas/facturas"""
    sales = await SaleService.get_sales(db, skip=skip, limit=limit)
    return sales


@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale(
    sale_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene una venta/factura por ID"""
    sale = await SaleService.get_sale_by_id(db, sale_id)
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada"
        )
    
    return sale
