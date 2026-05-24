from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.database import get_db
from app.schemas import ProductCreate, ProductResponse, ProductUpdate
from app.services import ProductService, ExchangeRateService
from app.core.jwt import verify_token


router = APIRouter(prefix="/products", tags=["Productos"])


async def get_current_user(token: str = None):
    """Dependencia para obtener usuario actual (simplificada)"""
    # En producción, validar el token completamente
    return {"username": "test_user", "role": "admin"}


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Crea un nuevo producto"""
    # Obtener tasa de cambio actual
    current_rate = await ExchangeRateService.get_current_rate(db)
    exchange_rate = current_rate.rate if current_rate else 36.5
    
    try:
        product = await ProductService.create_product(db, product_data, exchange_rate)
        return product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene lista de productos con paginación y filtros"""
    products = await ProductService.get_products(
        db, 
        skip=skip, 
        limit=limit, 
        category=category, 
        search=search
    )
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene un producto por ID"""
    product = await ProductService.get_product_by_id(db, product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Actualiza un producto existente"""
    # Obtener tasa de cambio actual
    current_rate = await ExchangeRateService.get_current_rate(db)
    exchange_rate = current_rate.rate if current_rate else None
    
    product = await ProductService.update_product(
        db, 
        product_id, 
        product_data,
        exchange_rate
    )
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Elimina lógicamente un producto (lo marca como inactivo)"""
    product = await ProductService.get_product_by_id(db, product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    product.is_active = False
    await db.commit()
