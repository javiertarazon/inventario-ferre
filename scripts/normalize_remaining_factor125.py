"""Normalize remaining active products with factor_ajuste 1.25 to 1.00."""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.extensions import db
from app.models import Product

TARGET_FACTOR = Decimal('1.25')
NEW_FACTOR = Decimal('1.00')


def main() -> None:
    app = create_app('development')
    with app.app_context():
        products = Product.query.filter_by(deleted_at=None).filter(Product.factor_ajuste == TARGET_FACTOR).all()

        for product in products:
            product.factor_ajuste = NEW_FACTOR
            product.updated_at = datetime.utcnow()

        db.session.commit()

        print(f'productos_normalizados={len(products)}')
        print(f'factor_nuevo={NEW_FACTOR}')


if __name__ == '__main__':
    main()
