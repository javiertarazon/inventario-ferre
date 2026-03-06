# Corrección: Categoría no se muestra después de editar producto

## Problema Reportado

Cuando se edita un producto y se le asigna una categoría que no tenía previamente, la categoría no se muestra en el listado de productos ni se guarda en la base de datos.

## Causa Raíz

El problema tenía TRES causas:

1. **Falta de Eager Loading**: El repositorio de productos no estaba cargando la relación `item_group` de forma anticipada (eager loading), lo que causaba que la relación no estuviera disponible en el template.

2. **Sesión no refrescada**: Después de actualizar un producto, la sesión de SQLAlchemy no estaba refrescando el objeto para cargar las relaciones actualizadas.

3. **ValidationService no validaba item_group_id**: El servicio de validación NO estaba incluyendo el campo `item_group_id` en los datos validados, por lo que nunca se actualizaba en la base de datos. **Esta era la causa principal**.

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

### 3. Agregada validación de item_group_id en ValidationService (SOLUCIÓN PRINCIPAL)

**Archivo**: `app/services/validation_service.py`

Se agregó la validación del campo `item_group_id` en el método `validate_product_data`:

```python
# Validate item_group_id (category)
item_group_id = data.get('item_group_id')
if item_group_id is not None:
    if item_group_id == '':  # Empty string should be treated as None
        validated_data['item_group_id'] = None
    else:
        try:
            validated_data['item_group_id'] = int(item_group_id)
        except (ValueError, TypeError):
            errors.append("El ID de la categoría debe ser un número entero válido")

# Validate reorder_point
reorder_point = data.get('reorder_point')
if reorder_point is not None:
    if reorder_point == '':
        validated_data['reorder_point'] = None
    else:
        try:
            reorder_value = int(reorder_point)
            if reorder_value < 0:
                errors.append("El punto de reorden no puede ser negativo")
            else:
                validated_data['reorder_point'] = reorder_value
        except (ValueError, TypeError):
            errors.append("El punto de reorden debe ser un número entero válido")

# Validate reorder_quantity
reorder_quantity = data.get('reorder_quantity')
if reorder_quantity is not None:
    if reorder_quantity == '':
        validated_data['reorder_quantity'] = None
    else:
        try:
            quantity_value = int(reorder_quantity)
            if quantity_value < 0:
                errors.append("La cantidad de reorden no puede ser negativa")
            else:
                validated_data['reorder_quantity'] = quantity_value
        except (ValueError, TypeError):
            errors.append("La cantidad de reorden debe ser un número entero válido")
```

**Beneficios**:
- Ahora el campo `item_group_id` se incluye en los datos validados
- Se actualiza correctamente en la base de datos
- Maneja correctamente valores vacíos (los convierte a None)
- También se agregó validación para `reorder_point` y `reorder_quantity`

## Verificación

Se creó un script de prueba `test_update_category.py` que verifica:

1. ✅ La relación `item_group` funciona correctamente
2. ✅ Se puede acceder a `product.item_group.name`
3. ✅ Se puede acceder a `product.item_group.color` e `icon`
4. ✅ El campo `item_group_id` se actualiza en la base de datos
5. ✅ La categoría se muestra correctamente en el listado de productos
6. ✅ Los cambios persisten después de recargar desde la base de datos

**Resultado del test**:
```
UPDATE products SET item_group_id=?, updated_at=? WHERE products.id = ?
✅ CATEGORÍA ASIGNADA CORRECTAMENTE
✅ CATEGORÍA GUARDADA EN BD CORRECTAMENTE
```

## Resultado

Ahora cuando editas un producto y le asignas una categoría:

1. ✅ La categoría se guarda correctamente en la base de datos (`item_group_id` se actualiza)
2. ✅ La relación se carga automáticamente con eager loading
3. ✅ La categoría se muestra inmediatamente en el listado de productos
4. ✅ El badge de categoría aparece con el color e icono correspondiente
5. ✅ Los cambios persisten y son visibles en todas las vistas

## Archivos Modificados

- `app/repositories/product_repository.py` - Agregado eager loading
- `app/services/product_service.py` - Agregado refresh después de actualizar
- `app/services/validation_service.py` - **Agregada validación de item_group_id, reorder_point y reorder_quantity**
- `test_update_category.py` - Script de prueba (nuevo)

## Fecha de Corrección

11 de Febrero de 2026

## Estado

✅ CORREGIDO Y VERIFICADO COMPLETAMENTE
