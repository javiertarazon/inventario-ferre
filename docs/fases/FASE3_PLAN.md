# FASE 3: TESTING & VALIDACIÓN - PLAN EJECUTABLE

## 🎯 Objetivo
Implementar suite de tests (unitarios, integración, seguridad) con coverage ≥70%

## 📋 Plan por Tareas

### Tarea 1: Base de Tests & Fixtures (30 min)
- [ ] Mejorar conftest.py con context + client fixtures
- [ ] Crear factories para generar datos de prueba
- [ ] Setup SQLite in-memory database para tests

### Tarea 2: Tests Unitarios (60 min)
- [ ] product_service.py (8 tests: CRUD + búsqueda)
- [ ] customer_service.py (7 tests: CRUD + búsqueda)
- [ ] movement_service.py (5 tests: entrada/salida/ajuste)
- [ ] validation_service.py (6 tests: validación de datos)

### Tarea 3: Tests de Integración (60 min)
- [ ] Flujo: crear producto → crear orden → confirmar stock
- [ ] Flujo: crear cliente → crear orden → validar crédito
- [ ] Flujo: movimientos de inventario

### Tarea 4: Tests de Seguridad (30 min)
- [ ] JWT validation
- [ ] RBAC (roles/permissions)
- [ ] SQL injection prevention
- [ ] XSS prevention

### Tarea 5: Coverage & Reporting (30 min)
- [ ] Ejecutar pytest con coverage
- [ ] Generar report HTML
- [ ] Validar target 70%

## ⏱️ Duración Total
**~3 horas de implementación** (incluyendo testing y debugging)

## ✅ Definición de Éxito
- [ ] 30+ tests implementados y pasados
- [ ] Coverage ≥ 70%
- [ ] Sin broken imports
- [ ] Reportes automáticos funcionando
