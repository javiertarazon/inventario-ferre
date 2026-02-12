# Corrección: Categoría no se muestra después de editar producto

## Problema Reportado

Cuando se edita un producto y se le asigna una categoría que no tenía previamente, la categoría no se muestra en el listado de productos.

## Causa Raíz

El problema tenía dos causas:

1. **Falta de Eager Loading**: El repositorio de productos no estaba cargando la relación `item_group` de forma anticipada (eager loading), lo que causaba que la relación no estuviera disponible en el template.

2. **Sesión no refrescada**: Después de actualizar un producto, la sesión de SQLAlchemy no estaba refrescando el objeto para cargar las relaciones actualizadas.

## Solución Implementada

### 1. Agregado Eager Loading en ProductRepository

**Archivo**: `app/repositories/product_repository.py`

Se agregó `joinedload` para cargar las relaciones `item_group` y `proveedor` de forma anticipada:

```python
from sqlalchemy.orm import joinedload

def search_products(self, query: str, filters: Dict[str, Any] = None, 
                   page: int = 1, per_page: int = 20) -> PaginatedResult[Product]:
    try:
        from sqlalchemy.orm import joinedload
        
        q = db.session.query(Product).filter(Product.deleted_at.is_(None))
        
        # Eager load relationships to avoid N+1 queries
        q = q.options(joinedload(Product.item_group), joinedload(Product.proveedor))
        
        # ... resto del código
```

**Beneficios**:
- Evita el problema N+1 de consultas
- Carga las relaciones en una sola consulta
- Mejora el rendimiento general

### 2. Refresh después de actualizar

**Archivo**: `app/services/product_service.py`

Se agregó `db.session.refresh()` después de actualizar el producto:

```python
# Save changes
updated_product = self.product_repo.update(product)

# Refresh to load relationships
db.session.refresh(updated_product)

current_app.logger.info(
    f"Product updated: {updated_product.codigo} by user {user_id}"
)

return updated_product
```

**Beneficios**:
- Asegura que las relaciones estén actualizadas
- Recarga el objeto desde la base de datos
- Garantiza que los cambios sean visibles inmediatamente

## Verificación

Se creó un script de prueba `test_item_group_relation.py` que verifica:

1. ✅ La relación `item_group` funciona correctamente
2. ✅ Se puede acceder a `product.item_group.name`
3. ✅ Se puede acceder a `product.item_group.color` e `icon`
4. ✅ El listado muestra correctamente las categorías

## Resultado

Ahora cuando editas un producto y le asignas una categoría:

1. La categoría se guarda correctamente en la base de datos
2. La relación se carga automáticamente con eager loading
3. La categoría se muestra inmediatamente en el listado de productos
4. El badge de categoría aparece con el color e icono correspondiente

## Archivos Modificados

- `app/repositories/product_repository.py` - Agregado eager loading
- `app/services/product_service.py` - Agregado refresh después de actualizar
- `test_item_group_relation.py` - Script de prueba (nuevo)

## Fecha de Corrección

11 de Febrero de 2026

## Estado

✅ CORREGIDO Y VERIFICADO
