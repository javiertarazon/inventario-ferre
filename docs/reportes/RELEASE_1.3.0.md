# Release 1.3.0

Fecha: 2026-03-07

## Resumen Ejecutivo

Esta entrega amplía el manejo de tasa cambiaria para uso operativo real. Se incorporó la carga histórica BCV desde archivos oficiales publicados por el banco central y se mejoró la consulta del historial con buscador por fecha y paginación desde el módulo de precios.

## Cambios Incluidos

- Carga histórica de tasa BCV desde archivos XLS trimestrales del BCV.
- Cobertura de sábados, domingos y feriados basada en la fecha valor publicada por BCV.
- Script nuevo `scripts/backfill_bcv_history.py` para ejecutar la reconstrucción histórica.
- Historial de tasa cambiaria con filtro por fecha exacta.
- Paginación del historial de tasas en la interfaz de precios.
- Pruebas actualizadas para parser histórico BCV, cobertura de no hábiles, búsqueda por fecha y paginación.

## Validación Ejecutada

- `tests/test_exchange_rate_service.py` en verde.
- `tests/test_pricing_blueprint.py` en verde.
- Carga histórica verificada sobre base local para el rango `2025-08-01` a `2026-03-06`.
- Cobertura validada: `218` días esperados y `218` tasas persistidas en el rango.

## Archivos Relevantes

- `app/services/exchange_rate_service.py`
- `app/blueprints/pricing.py`
- `app/templates/pricing_config.html`
- `scripts/backfill_bcv_history.py`
- `tests/test_exchange_rate_service.py`
- `tests/test_pricing_blueprint.py`