"""Merge duplicated products created by factor_ajuste 1.25 variants.

Rule:
- Active products grouped by normalized descripcion + categoria + proveedor.
- If a group contains at least one product with factor 1.25 and another with a different factor,
  keep the oldest non-1.25 product.
- Transfer stock and references from 1.25 products to the kept product.
- Soft delete 1.25 products and free their unique codes.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.extensions import db
from app.models import Product, Movimiento, SalesOrderItem


TARGET_FACTOR = Decimal('1.25')


def normalize_description(text: str) -> str:
    return ' '.join((text or '').strip().split()).upper()


def choose_keeper(products: list[Product]) -> Product | None:
    candidates = [p for p in products if Decimal(str(p.factor_ajuste or 0)) != TARGET_FACTOR]
    if not candidates:
        return None
    return sorted(candidates, key=lambda p: (p.created_at or datetime.max, p.id))[0]


def free_deleted_code(product: Product, suffix: str) -> None:
    product.codigo = f"DEL125-{product.id:06d}-{suffix}"


def main() -> None:
    app = create_app('development')

    with app.app_context():
        products = Product.query.filter_by(deleted_at=None).order_by(Product.descripcion, Product.id).all()
        grouped = defaultdict(list)

        for product in products:
            key = (
                normalize_description(product.descripcion),
                product.item_group_id or 0,
                product.proveedor_id or 0,
            )
            grouped[key].append(product)

        groups_to_merge = []
        for key, items in grouped.items():
            if len(items) < 2:
                continue
            if any(Decimal(str(item.factor_ajuste or 0)) == TARGET_FACTOR for item in items):
                keeper = choose_keeper(items)
                if keeper:
                    targets = [i for i in items if Decimal(str(i.factor_ajuste or 0)) == TARGET_FACTOR and i.id != keeper.id]
                    if targets:
                        groups_to_merge.append((key, keeper, targets))

        merged_products = 0
        merged_stock = 0
        moved_movements = 0
        moved_sales_items = 0
        timestamp_suffix = datetime.utcnow().strftime('%Y%m%d%H%M%S')

        for _, keeper, targets in groups_to_merge:
            for target in targets:
                target_stock = int(target.stock or 0)
                keeper.stock = int(keeper.stock or 0) + target_stock
                merged_stock += target_stock

                moved_movements += Movimiento.query.filter_by(producto_id=target.id, deleted_at=None).update(
                    {'producto_id': keeper.id}, synchronize_session=False
                )
                moved_sales_items += SalesOrderItem.query.filter_by(product_id=target.id).update(
                    {'product_id': keeper.id}, synchronize_session=False
                )

                if (not keeper.proveedor_id) and target.proveedor_id:
                    keeper.proveedor_id = target.proveedor_id
                if (not keeper.item_group_id) and target.item_group_id:
                    keeper.item_group_id = target.item_group_id
                if float(keeper.precio_dolares or 0) <= 0 and float(target.precio_dolares or 0) > 0:
                    keeper.precio_dolares = target.precio_dolares

                target.deleted_at = datetime.utcnow()
                free_deleted_code(target, timestamp_suffix)
                merged_products += 1

        db.session.commit()

        print(f'Grupos procesados: {len(groups_to_merge)}')
        print(f'Productos factor 1.25 eliminados: {merged_products}')
        print(f'Stock transferido al articulo conservado: {merged_stock}')
        print(f'Movimientos reasignados: {moved_movements}')
        print(f'Items de orden reasignados: {moved_sales_items}')


if __name__ == '__main__':
    main()