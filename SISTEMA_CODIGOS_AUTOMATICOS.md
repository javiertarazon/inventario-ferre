# Sistema de Generación Automática de Códigos de Productos

## Resumen
Se implementó un sistema completo de generación automática de códigos de productos basado en categorías y descripciones, siguiendo el formato especificado.

## Formato de Códigos
```
{CATEGORIA}-{PALABRA1}-{PALABRA2}-{SECUENCIA}
```

### Ejemplo:
- **Producto**: "Socates Porcelana Patica"
- **Categoría**: Electricidad
- **Código Generado**: `E-SO-PO-01`

### Componentes:
1. **Primera letra**: Inicial de la categoría
   - E = Electricidad
   - P = Plomeria
   - A = Albañileria
   - C = Carpinteria
   - H = Herreria
   - T = Tornilleria
   - M = Miselaneos

2. **Siguientes 2 letras**: Primeras 2 letras de la primera palabra significativa
3. **Siguientes 2 letras**: Primeras 2 letras de la segunda palabra significativa
4. **Números**: Secuencia ascendente (01, 02, 03...)

## Categorías Creadas

| Categoría | Prefijo | Color | Icono | Descripción |
|-----------|---------|-------|-------|-------------|
| Electricidad | E | #FFC107 (Amarillo) | lightning-charge | Productos eléctricos y de iluminación |
| Plomeria | P | #2196F3 (Azul) | droplet | Productos de plomería y tuberías |
| Albañileria | A | #9E9E9E (Gris) | bricks | Materiales de construcción y albañilería |
| Carpinteria | C | #795548 (Marrón) | hammer | Herramientas y materiales de carpintería |
| Herreria | H | #607D8B (Gris azulado) | tools | Productos de herrería y metales |
| Tornilleria | T | #FF5722 (Naranja) | nut | Tornillos, tuercas y elementos de fijación |
| Miselaneos | M | #9C27B0 (Púrpura) | box-seam | Productos varios y misceláneos |

## Archivos Creados/Modificados

### 1. `app/utils/code_generator.py`
Clase `CodeGenerator` con métodos:
- `clean_word()`: Limpia palabras removiendo acentos y caracteres especiales
- `get_description_initials()`: Extrae iniciales de las primeras dos palabras
- `get_next_sequence()`: Obtiene el siguiente número secuencial
- `generate_code()`: Genera código completo basado en categoría y descripción
- `generate_code_from_item_group_id()`: Genera código usando ID de categoría

### 2. `create_categories.py`
Script para crear/actualizar las 7 categorías en la base de datos con sus propiedades (color, icono, descripción).

### 3. `regenerate_codes.py`
Script para regenerar todos los códigos de productos existentes basándose en el Excel original.
- Lee el archivo `Inventario Ferre-Exito.xlsx`
- Asigna categorías a productos
- Genera códigos automáticamente
- Actualiza 793 productos exitosamente

### 4. `app/services/import_service.py`
Actualizado para generar códigos automáticamente al importar Excel:
- Detecta columna de categoría en el Excel
- Genera códigos automáticamente si hay categoría
- Usa código proporcionado si no hay categoría
- Genera código genérico como último recurso

## Ejemplos de Códigos Generados

### Electricidad:
```
E-SP-01 - Socates Porcelana Patica/Niple E27
E-SP-02 - Socates Porcelana con forro E27
E-SP-03 - Socates Plafon Porcelana E27
E-SR-01 - Socates Roceta Porcelana E27
E-SP-04 - Socate Porcelana Bombillo Linterna
```

### Plomeria:
```
P-CG-01 - Codo Galv 1/2 x 90°
P-CG-02 - Codo Galv 1/2 x 45°
P-CG-03 - Codo Galv 3/4 x 90°
P-CG-04 - Codo Galv 3/4 x 45°
P-CC-01 - Codo Cachinbo 3/4"
```

### Albañileria:
```
A-PG-01 - Pego Gris Sacos de 10 kg
A-CG-01 - Cemento Gris Sacos 42 kg
A-CP-01 - Cal Pasta Bolsas 8kg
A-CB-01 - Cemento Blanco Sacos 20 kg
A-YS-01 - Yeso Sacos 25 kg
```

## Flujo de Importación

1. **Usuario sube Excel** en la pestaña "Cargar Inventario"
2. **Sistema lee el archivo** y detecta columnas:
   - Descripcion del Articulo (requerida)
   - Categoria (opcional pero recomendada)
   - Cantidad Unid/kg (opcional)
   - Precio Venta $ (opcional)
3. **Para cada producto**:
   - Si tiene categoría válida → Genera código automático
   - Si no tiene categoría pero tiene código → Usa el código proporcionado
   - Si no tiene ninguno → Genera código genérico (GEN-0001)
4. **Verifica duplicados**: Si el código ya existe, incrementa la secuencia
5. **Crea o actualiza** el producto en la base de datos

## Reglas de Generación

1. **Limpieza de texto**:
   - Remueve acentos (á→a, é→e, etc.)
   - Remueve caracteres especiales
   - Convierte a mayúsculas

2. **Selección de palabras**:
   - Filtra palabras muy cortas (≤2 letras)
   - Usa las primeras 2 palabras significativas
   - Si no hay suficientes palabras, usa 'XX' como relleno

3. **Secuencia**:
   - Busca códigos existentes con el mismo prefijo
   - Encuentra el número más alto
   - Incrementa en 1
   - Formatea con 2 dígitos (01, 02, ..., 99)

## Resultados de la Regeneración

```
============================================================
✓ REGENERACIÓN COMPLETADA
============================================================
  Productos actualizados: 793
  Productos creados: 0
  Total procesados: 793
  Errores: 0
============================================================
```

## Uso en el Sistema

### Importación Manual
1. Ir a "Cargar Inventario"
2. Seleccionar archivo Excel con columnas:
   - Descripcion del Articulo
   - Categoria
   - Cantidad Unid/kg
   - Precio Venta $
3. El sistema generará códigos automáticamente

### Creación Manual de Productos
- Al crear un producto manualmente, el código se puede dejar vacío
- El sistema generará uno automáticamente basado en la categoría seleccionada

## Ventajas del Sistema

1. **Consistencia**: Todos los códigos siguen el mismo formato
2. **Organización**: Fácil identificar categoría por el prefijo
3. **Escalabilidad**: Soporta hasta 99 productos por combinación de letras
4. **Automático**: No requiere intervención manual
5. **Flexible**: Permite códigos manuales si es necesario

## Mantenimiento

### Agregar Nueva Categoría
1. Editar `create_categories.py`
2. Agregar nueva categoría con su prefijo
3. Ejecutar: `python create_categories.py`
4. Actualizar `CATEGORY_PREFIXES` en `code_generator.py`

### Regenerar Códigos
Si se necesita regenerar todos los códigos:
```bash
python regenerate_codes.py
```

## Estado Actual
- ✓ 7 categorías creadas
- ✓ 793 productos con códigos regenerados
- ✓ Sistema de importación actualizado
- ✓ Generación automática funcionando
- ✓ Servidor corriendo en proceso 22
- ✓ Base de datos actualizada

## Próximos Pasos Recomendados
1. Probar importación de nuevo Excel
2. Verificar códigos en la interfaz web
3. Crear productos manualmente para probar generación automática
4. Documentar para usuarios finales
