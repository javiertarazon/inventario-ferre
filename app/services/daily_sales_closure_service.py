"""Service for daily sales closures and estimated exit reconstruction."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
from typing import Any, Dict, List

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.extensions import db
from app.models import DailySalesClosure, DailySalesClosureAllocation, Movimiento, Product
from app.utils.exceptions import BusinessLogicError, NotFoundError, ValidationError


class DailySalesClosureService:
    """Create and inspect daily closures with reconstructed stock outputs."""

    DEFAULT_INVOICED_SHARE = Decimal('0.6000')
    DEFAULT_NON_INVOICED_SHARE = Decimal('0.4000')

    def list_closures(self, page: int = 1, per_page: int = 20):
        """Return paginated daily closures ordered from newest to oldest."""
        return (
            DailySalesClosure.query
            .filter_by(deleted_at=None)
            .options(selectinload(DailySalesClosure.allocations))
            .order_by(DailySalesClosure.closure_date.desc(), DailySalesClosure.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

    def get_closure(self, closure_id: int) -> DailySalesClosure:
        """Return one closure with reconstructed allocations."""
        closure = (
            DailySalesClosure.query
            .filter_by(id=closure_id, deleted_at=None)
            .options(
                selectinload(DailySalesClosure.allocations).selectinload(DailySalesClosureAllocation.product),
                selectinload(DailySalesClosure.allocations).selectinload(DailySalesClosureAllocation.movement),
            )
            .first()
        )
        if not closure:
            raise NotFoundError('DailySalesClosure', closure_id)
        return closure

    def create_closure(self, data: Dict[str, Any], user_id: int) -> DailySalesClosure:
        """Persist one daily closure and generate estimated SALIDA movements."""
        closure_date = self._parse_date(data.get('closure_date'))

        existing = DailySalesClosure.query.filter_by(closure_date=closure_date, deleted_at=None).first()
        if existing:
            raise ValidationError(
                f'Ya existe un cierre diario para la fecha {closure_date.isoformat()}',
                field='closure_date',
            )

        total_sales_usd = self._parse_decimal(data.get('total_sales_usd'), 'total_sales_usd', required=False)
        invoiced_sales_usd = self._parse_decimal(data.get('invoiced_sales_usd'), 'invoiced_sales_usd', required=False)
        non_invoiced_sales_usd = self._parse_decimal(data.get('non_invoiced_sales_usd'), 'non_invoiced_sales_usd', required=False)
        invoiced_share = self._parse_share(data.get('invoiced_share'), default=self.DEFAULT_INVOICED_SHARE)
        non_invoiced_share = self._parse_share(data.get('non_invoiced_share'), default=self.DEFAULT_NON_INVOICED_SHARE)

        if total_sales_usd is None:
            if invoiced_sales_usd is None or non_invoiced_sales_usd is None:
                raise ValidationError(
                    'Debe indicar el total del cierre o ambos montos con factura y sin factura',
                    field='total_sales_usd',
                )
            total_sales_usd = (invoiced_sales_usd + non_invoiced_sales_usd).quantize(Decimal('0.0001'))

        if total_sales_usd <= 0:
            raise ValidationError('El total del cierre debe ser mayor que cero', field='total_sales_usd')

        shares_total = (invoiced_share + non_invoiced_share).quantize(Decimal('0.0001'))
        if abs(shares_total - Decimal('1.0000')) > Decimal('0.0001'):
            raise ValidationError('La suma de porcentajes facturado/no facturado debe ser 100%', field='invoiced_share')

        if invoiced_sales_usd is None:
            invoiced_sales_usd = (total_sales_usd * invoiced_share).quantize(Decimal('0.0001'))
        if non_invoiced_sales_usd is None:
            non_invoiced_sales_usd = (total_sales_usd - invoiced_sales_usd).quantize(Decimal('0.0001'))

        candidate_products = self._get_candidate_products()
        allocations = self._estimate_allocations(candidate_products, total_sales_usd)
        if not allocations:
            raise BusinessLogicError('No se pudo reconstruir salidas: no hay inventario disponible para asignar')

        closure = DailySalesClosure(
            closure_date=closure_date,
            total_sales_usd=total_sales_usd,
            invoiced_share=invoiced_share,
            non_invoiced_share=non_invoiced_share,
            invoiced_sales_usd=invoiced_sales_usd,
            non_invoiced_sales_usd=non_invoiced_sales_usd,
            reconstructed_sales_usd=Decimal('0.0000'),
            generated_exit_units=0,
            source_file_name=(data.get('source_file_name') or '').strip() or None,
            notes=(data.get('notes') or '').strip() or None,
            created_by=user_id,
            updated_by=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        try:
            db.session.add(closure)
            db.session.flush()

            reconstructed_total = Decimal('0.0000')
            generated_units = 0

            for allocation in allocations:
                product = allocation['product']
                quantity = allocation['quantity']
                unit_price = allocation['unit_price']
                allocated_sales = allocation['allocated_sales']

                movement = Movimiento(
                    producto_id=product.id,
                    tipo='SALIDA',
                    cantidad=quantity,
                    fecha=closure_date,
                    descripcion=(
                        f'Cierre diario {closure_date.isoformat()} reconstruido 60/40 '
                        f'(facturado {invoiced_share * 100:.0f}% / sin factura {non_invoiced_share * 100:.0f}%)'
                    ),
                    created_by=user_id,
                    updated_by=user_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.session.add(movement)
                db.session.flush()

                db.session.add(DailySalesClosureAllocation(
                    closure_id=closure.id,
                    product_id=product.id,
                    movement_id=movement.id,
                    reference_unit_price_usd=unit_price,
                    allocated_sales_usd=allocated_sales,
                    estimated_quantity=quantity,
                    weighting_value_usd=allocation['weight'],
                ))

                product.stock = int(product.stock or 0) - quantity
                product.updated_by = user_id
                product.updated_at = datetime.utcnow()

                reconstructed_total += allocated_sales
                generated_units += quantity

            closure.reconstructed_sales_usd = reconstructed_total.quantize(Decimal('0.0001'))
            closure.generated_exit_units = generated_units
            db.session.commit()

            current_app.logger.info(
                'Daily closure reconstructed: %s total=%s allocations=%s by user %s',
                closure_date.isoformat(),
                str(total_sales_usd),
                len(allocations),
                user_id,
            )
            return self.get_closure(closure.id)
        except SQLAlchemyError as exc:
            db.session.rollback()
            current_app.logger.error('Database error creating daily closure: %s', str(exc))
            raise BusinessLogicError(f'Error al registrar el cierre diario: {exc}') from exc

    def _get_candidate_products(self) -> List[Product]:
        """Return active products with positive stock available for reconstruction."""
        return (
            Product.query
            .filter(Product.deleted_at.is_(None), Product.stock > 0)
            .order_by(Product.stock.desc(), Product.codigo.asc())
            .all()
        )

    def _estimate_allocations(self, products: List[Product], total_sales_usd: Decimal) -> List[Dict[str, Any]]:
        """Estimate product outputs weighted by current inventory value."""
        weighted_rows = []
        for product in products:
            unit_price = self._get_reference_unit_price(product)
            stock = int(product.stock or 0)
            if stock <= 0:
                continue
            weight = (Decimal(stock) * unit_price).quantize(Decimal('0.0001'))
            weighted_rows.append({
                'product': product,
                'unit_price': unit_price,
                'stock': stock,
                'weight': weight,
                'allocated_quantity': 0,
                'allocated_sales': Decimal('0.0000'),
            })

        if not weighted_rows:
            return []

        total_weight = sum((row['weight'] for row in weighted_rows), Decimal('0.0000'))
        if total_weight <= 0:
            total_weight = sum((Decimal(row['stock']) for row in weighted_rows), Decimal('0.0000'))
            for row in weighted_rows:
                row['weight'] = Decimal(row['stock'])

        allocatable_sales = min(
            total_sales_usd,
            sum((Decimal(row['stock']) * row['unit_price'] for row in weighted_rows), Decimal('0.0000')),
        ).quantize(Decimal('0.0001'))

        for row in weighted_rows:
            proportional_sales = (allocatable_sales * row['weight'] / total_weight).quantize(Decimal('0.0001'))
            quantity = int((proportional_sales / row['unit_price']).to_integral_value(rounding=ROUND_FLOOR))
            quantity = max(0, min(row['stock'], quantity))
            if quantity > 0:
                row['allocated_quantity'] = quantity
                row['allocated_sales'] = (Decimal(quantity) * row['unit_price']).quantize(Decimal('0.0001'))

        remaining_sales = (allocatable_sales - sum((row['allocated_sales'] for row in weighted_rows), Decimal('0.0000'))).quantize(Decimal('0.0001'))
        while remaining_sales > Decimal('0.0000'):
            affordable_rows = [
                row for row in weighted_rows
                if row['allocated_quantity'] < row['stock'] and row['unit_price'] <= remaining_sales
            ]
            if not affordable_rows:
                break
            affordable_rows.sort(key=lambda row: (row['weight'], -row['unit_price']), reverse=True)
            selected = affordable_rows[0]
            selected['allocated_quantity'] += 1
            selected['allocated_sales'] = (
                selected['allocated_sales'] + selected['unit_price']
            ).quantize(Decimal('0.0001'))
            remaining_sales = (remaining_sales - selected['unit_price']).quantize(Decimal('0.0001'))

        if all(row['allocated_quantity'] == 0 for row in weighted_rows):
            cheapest_row = min(weighted_rows, key=lambda row: row['unit_price'])
            cheapest_row['allocated_quantity'] = 1
            cheapest_row['allocated_sales'] = cheapest_row['unit_price']

        return [
            {
                'product': row['product'],
                'unit_price': row['unit_price'],
                'quantity': row['allocated_quantity'],
                'allocated_sales': row['allocated_sales'],
                'weight': row['weight'],
            }
            for row in weighted_rows
            if row['allocated_quantity'] > 0
        ]

    def _get_reference_unit_price(self, product: Product) -> Decimal:
        """Resolve unit price for estimated exits, falling back to a minimal value."""
        base_price = Decimal(str(product.precio_dolares or 0))
        factor = Decimal(str(product.factor_ajuste or 1))
        resolved = (base_price * factor).quantize(Decimal('0.0001'))
        return resolved if resolved > 0 else Decimal('0.0100')

    def _parse_date(self, raw_value: Any) -> date:
        if not raw_value:
            raise ValidationError('La fecha del cierre es requerida', field='closure_date')
        if hasattr(raw_value, 'year') and hasattr(raw_value, 'month') and hasattr(raw_value, 'day'):
            return raw_value
        raw_string = str(raw_value).strip()
        for pattern in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'):
            try:
                return datetime.strptime(raw_string, pattern).date()
            except ValueError:
                continue
        raise ValidationError('La fecha del cierre debe tener formato YYYY-MM-DD', field='closure_date')

    def _parse_decimal(self, raw_value: Any, field: str, required: bool = True) -> Decimal | None:
        if raw_value in (None, ''):
            if required:
                raise ValidationError(f'El campo {field} es requerido', field=field)
            return None
        try:
            return Decimal(str(raw_value)).quantize(Decimal('0.0001'))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValidationError(f'El campo {field} debe ser numérico', field=field) from exc

    def _parse_share(self, raw_value: Any, default: Decimal) -> Decimal:
        if raw_value in (None, ''):
            return default
        try:
            parsed = Decimal(str(raw_value)).quantize(Decimal('0.0001'))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValidationError('El porcentaje debe ser numérico', field='invoiced_share') from exc
        if parsed > Decimal('1'):
            parsed = (parsed / Decimal('100')).quantize(Decimal('0.0001'))
        if parsed < 0 or parsed > 1:
            raise ValidationError('El porcentaje debe estar entre 0 y 1', field='invoiced_share')
        return parsed