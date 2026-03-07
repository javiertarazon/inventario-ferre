"""
Backfill BCV historical USD rates into the local database.
"""
from datetime import date, datetime
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.services.exchange_rate_service import ExchangeRateService


def _parse_date(raw_value: str | None, default_value: date) -> date:
    if not raw_value:
        return default_value
    return datetime.strptime(raw_value, '%Y-%m-%d').date()


def main(argv: list[str] | None = None):
    argv = argv or sys.argv[1:]
    start_date = _parse_date(argv[0] if len(argv) >= 1 else None, date(2025, 8, 1))
    end_date = _parse_date(argv[1] if len(argv) >= 2 else None, date.today())

    app = create_app()
    with app.app_context():
        result = ExchangeRateService().sync_historical_from_bcv(start_date, end_date)
        print(
            f"Historico BCV cargado {result['start_date'].isoformat()}..{result['end_date'].isoformat()} | "
            f"creados={result['created_count']} actualizados={result['updated_count']} "
            f"fechas={result['total_dates']} fuentes={result['source_entries']} libros={result['workbooks']}"
        )


if __name__ == '__main__':
    main()