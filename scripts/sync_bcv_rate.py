"""
Manual entry point for daily BCV rate synchronization.
Useful for Windows Task Scheduler or cron-style execution.
"""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.services.exchange_rate_service import ExchangeRateService


def main():
    """Sync today's BCV rate and print the persisted value."""
    app = create_app()
    with app.app_context():
        result = ExchangeRateService().sync_today_from_bcv()
        print(
            f"Tasa BCV sincronizada para {result['date'].isoformat()}: "
            f"{result['rate']:.4f} Bs/USD"
        )


if __name__ == '__main__':
    main()