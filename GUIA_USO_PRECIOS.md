# Guía de Uso - Sistema de Precios

## Acceso Rápido

**URL:** http://127.0.0.1:5000/pricing/

**Credenciales:**
- Usuario: `admin`
- Contraseña: `admin`

---

## 1. Actualizar Tasa de Cambio

### Pasos:

1. Hacer clic en "Configuración de Precios" en el menú superior
2. Ver la tasa actual en la primera sección
3. Ingresar la nueva tasa en el campo "Nueva Tasa (Bs/$)"
4. Hacer clic en "Actualizar Tasa"

### Ejemplo:

```
Tasa actual: 36.50 Bs/$
Nueva tasa: 38.00 Bs/$
```

### Resultado:

- La tasa se actualiza para el día actual
- Se guarda en el historial
- Todos los cálculos usan la nueva tasa inmediatamente

---

## 2. Aplicar Factor de Ajuste

### Opción A: Aplicar a TODOS los productos

1. Seleccionar "Todos los productos"
2. Ingresar el factor (ej: 1.20 para 20% de incremento)
3. Hacer clic en "Aplicar Factor"

### Opción B: Aplicar a una CATEGORÍA

1. Seleccionar "Categoría específica"
2. Elegir la categoría del dropdown
3. Ingresar el factor
4. Hacer clic en "Aplicar Factor"

### Opción C: Aplicar a un PRODUCTO

1. Seleccionar "Producto específico"
2. Buscar el producto en el buscador
3. Seleccionar el producto
4. Ingresar el factor
5. Hacer clic en "Aplicar Factor"

### Ejemplos de Factores:

- `1.00` = Sin ajuste (precio base)
- `1.10` = 10% de incremento
- `1.20` = 20% de incremento
- `1.50` = 50% de incremento
- `0.90` = 10% de descuento

---

## 3. Buscar Productos con Precios

### Pasos:

1. En la sección "Buscar Productos"
2. Ingresar término de búsqueda (opcional)
3. Seleccionar categoría (opcional)
4. Hacer clic en "Buscar"

### Resultado:

Tabla con columnas:
- **Código:** Código del producto
- **Descripción:** Nombre del producto
- **Categoría:** Categoría del producto
- **Precio USD:** Precio en dólares
- **Precio Bs:** Precio en bolívares (USD × tasa)
- **Factor:** Factor de ajuste aplicado
- **Precio Final Bs:** Precio final (Precio Bs × factor)

### Ejemplo de Resultado:

```
Código: A-01-01
Descripción: Producto de Prueba
Precio USD: $10.50
Precio Bs: 383.25 Bs (10.50 × 36.50)
Factor: 1.20
Precio Final: 459.90 Bs (383.25 × 1.20)
```

---

## 4. Ver Precios en Listado de Productos

### Pasos:

1. Ir a "Inventario" → "Productos"
2. Ver la tabla de productos

### Columnas de Precios:

- **Precio USD:** Precio base en dólares (pequeño, gris)
- **Precio Bs:** Precio en bolívares sin ajuste
- **Factor:** Factor de ajuste aplicado (pequeño)
- **Precio Final Bs:** Precio final con ajuste (destacado, negrita)

---

## 5. Exportar Inventario en Bolivares

### Pasos:

1. Ir a "Inventario" → "Libro de Inventario"
2. Seleccionar rango de fechas
3. Hacer clic en "Exportar a Excel"

### Resultado:

Archivo Excel con:
- Todas las columnas de precios en Bolivares
- Cálculos usando la tasa actual
- Factores de ajuste aplicados
- Formato Art. 177 del Reglamento ISLR

### Columnas de Precios:

- Existencia Inicial - Costo Unitario (Bs)
- Existencia Inicial - Monto (Bs)
- Entradas - Costo Unitario (Bs)
- Entradas - Monto (Bs)
- Salidas - Costo Unitario (Bs)
- Salidas - Monto (Bs)
- Inv.final - Costo Unitario (Bs)
- Inv.final - Monto (Bs)

---

## 6. Historial de Tasas

### Ubicación:

En la página "Configuración de Precios", sección inferior

### Información Mostrada:

- Fecha de la tasa
- Valor de la tasa (Bs/$)
- Usuario que la creó/actualizó
- Fecha y hora de creación

### Uso:

- Auditoría de cambios
- Verificación de tasas anteriores
- Seguimiento de actualizaciones

---

## Fórmulas de Cálculo

### Precio en Bolivares:
```
Precio Bs = Precio USD × Tasa de Cambio
```

### Precio Final:
```
Precio Final Bs = Precio Bs × Factor de Ajuste
```

### Fórmula Completa:
```
Precio Final Bs = (Precio USD × Tasa de Cambio) × Factor de Ajuste
```

---

## Ejemplos Prácticos

### Ejemplo 1: Producto con Factor 1.0 (sin ajuste)

```
Producto: Cable 16
Precio USD: $80.00
Tasa: 36.50 Bs/$
Factor: 1.00

Cálculo:
Precio Bs = $80.00 × 36.50 = 2,920.00 Bs
Precio Final = 2,920.00 × 1.00 = 2,920.00 Bs
```

### Ejemplo 2: Producto con Factor 1.20 (20% incremento)

```
Producto: Producto de Prueba
Precio USD: $10.50
Tasa: 36.50 Bs/$
Factor: 1.20

Cálculo:
Precio Bs = $10.50 × 36.50 = 383.25 Bs
Precio Final = 383.25 × 1.20 = 459.90 Bs
```

### Ejemplo 3: Producto con Factor 0.90 (10% descuento)

```
Producto: Socate Porcelana
Precio USD: $0.90
Tasa: 36.50 Bs/$
Factor: 0.90

Cálculo:
Precio Bs = $0.90 × 36.50 = 32.85 Bs
Precio Final = 32.85 × 0.90 = 29.57 Bs
```

---

## Casos de Uso Comunes

### Caso 1: Actualización Diaria de Tasa

**Situación:** La tasa de cambio cambió hoy

**Acción:**
1. Ir a Configuración de Precios
2. Actualizar tasa con el nuevo valor
3. Los precios se recalculan automáticamente

### Caso 2: Incremento General de Precios

**Situación:** Necesito aumentar todos los precios un 15%

**Acción:**
1. Ir a Configuración de Precios
2. Seleccionar "Todos los productos"
3. Ingresar factor 1.15
4. Aplicar

### Caso 3: Ajuste por Categoría

**Situación:** Los productos eléctricos necesitan 25% de incremento

**Acción:**
1. Ir a Configuración de Precios
2. Seleccionar "Categoría específica"
3. Elegir "Eléctricos"
4. Ingresar factor 1.25
5. Aplicar

### Caso 4: Promoción en Producto Específico

**Situación:** Quiero hacer 20% de descuento en un producto

**Acción:**
1. Ir a Configuración de Precios
2. Seleccionar "Producto específico"
3. Buscar y seleccionar el producto
4. Ingresar factor 0.80
5. Aplicar

---

## Verificación de Cambios

### Después de Actualizar Tasa:

1. Ir a listado de productos
2. Verificar que los precios en Bs cambiaron
3. Verificar en el buscador de precios

### Después de Aplicar Factor:

1. Ir a listado de productos
2. Verificar la columna "Factor"
3. Verificar la columna "Precio Final Bs"
4. Buscar productos específicos para confirmar

---

## Solución de Problemas

### Problema: No veo el enlace "Configuración de Precios"

**Solución:**
- Verificar que el servidor esté corriendo
- Refrescar la página (F5)
- Cerrar sesión y volver a iniciar

### Problema: Los precios no se actualizan

**Solución:**
- Verificar que la tasa se actualizó correctamente
- Refrescar la página de productos
- Verificar que el factor se aplicó correctamente

### Problema: Error al aplicar factor

**Solución:**
- Verificar que el factor sea mayor que 0
- Verificar que seleccionó correctamente el alcance
- Si es por categoría/producto, verificar que existe

---

## Notas Importantes

1. **La tasa de cambio es única por día:** Si actualiza la tasa dos veces el mismo día, se sobrescribe

2. **El factor se guarda en cada producto:** Cada producto mantiene su factor hasta que se cambie

3. **Los cálculos son en tiempo real:** No se guardan precios en Bs, se calculan al momento

4. **La exportación usa la tasa actual:** El Excel siempre usa la tasa vigente al momento de exportar

5. **El historial es permanente:** Todas las tasas quedan registradas para auditoría

---

## Contacto y Soporte

Para dudas o problemas, contactar al administrador del sistema.

**Servidor:** http://127.0.0.1:5000
**Usuario:** admin
**Contraseña:** admin
