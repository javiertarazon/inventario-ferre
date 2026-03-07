"""
Tests for BCV rate synchronization service and pricing route.
"""
from datetime import date

import pandas as pd

from app.models import ExchangeRate
from app.services.exchange_rate_service import ExchangeRateService


def login_test_user(client):
    """Authenticate the shared test user through the real login form."""
    return client.post(
        '/login',
        data={'username': 'testuser', 'password': 'testpass123'},
        follow_redirects=False,
    )


def test_extract_rate_from_html_supports_bcv_like_markup(app):
    """HTML extraction should parse localized BCV values with comma decimals."""
    html = '<div><strong>USD</strong></div><div class="rate">40,1234</div>'

    with app.app_context():
        rate = ExchangeRateService().extract_rate_from_html(html)

    assert float(rate) == 40.1234


def test_sync_rate_route_persists_today_rate(app, client, test_user, monkeypatch):
    """Pricing sync route should fetch and persist today's BCV rate."""
    login_response = login_test_user(client)
    assert login_response.status_code == 302

    sample_html = '<section><span>USD</span><strong>41,5678</strong></section>'
    monkeypatch.setattr(ExchangeRateService, '_fetch_remote_document', lambda self: sample_html)

    response = client.post('/pricing/sync-rate', follow_redirects=True)
    assert response.status_code == 200
    assert 'Tasa BCV sincronizada correctamente' in response.get_data(as_text=True)

    with app.app_context():
        rate = ExchangeRate.query.filter_by(date=date.today()).first()
        assert rate is not None
        assert float(rate.rate) == 41.5678


def test_extract_historical_sheet_entry_reads_operation_value_and_usd_rate(app):
    """Historical BCV worksheet parsing should extract the USD BID rate and dates."""
    sheet = pd.DataFrame([
        [None, 'BANCO CENTRAL DE VENEZUELA', None, None, None, None, '30/12/2025 04:54 PM'],
        [None, None, None, None, None, None, None],
        [None, None, None, None, 'TIPO DE CAMBIO DE REFERENCIA (*)', None, None],
        [None, 'Fecha Operacion: 30/12/2025', None, 'Fecha Valor: 02/01/2026', None, None, None],
        [None, None, None, '(a) Cotización M.E./US$', None, 'Bs./M.E.', None],
        [None, None, 'Moneda/País', 'Compra (BID)', 'Venta (ASK)', 'Compra (BID)', 'Venta (ASK)'],
        [None, 'USD', 'E.U.A.', 1, 1, '300.617473', '301.370900'],
    ])

    with app.app_context():
        entry = ExchangeRateService()._extract_historical_sheet_entry('30122025', sheet)

    assert entry is not None
    assert entry['operation_date'] == date(2025, 12, 30)
    assert entry['value_date'] == date(2026, 1, 2)
    assert float(entry['rate']) == 300.6175


def test_expand_entries_to_calendar_covers_weekends_and_holidays(app):
    """Gap dates before the next value date should inherit the next business rate."""
    entries = [
        {
            'operation_date': date(2026, 3, 6),
            'value_date': date(2026, 3, 9),
            'rate': ExchangeRateService()._normalize_rate('433.1664'),
        },
        {
            'operation_date': date(2026, 3, 9),
            'value_date': date(2026, 3, 10),
            'rate': ExchangeRateService()._normalize_rate('434.2000'),
        },
    ]

    with app.app_context():
        calendar_rates = ExchangeRateService()._expand_entries_to_calendar(
            entries,
            start_date=date(2026, 3, 6),
            end_date=date(2026, 3, 9),
        )

    assert float(calendar_rates[date(2026, 3, 6)]) == 433.1664
    assert float(calendar_rates[date(2026, 3, 7)]) == 433.1664
    assert float(calendar_rates[date(2026, 3, 8)]) == 433.1664
    assert float(calendar_rates[date(2026, 3, 9)]) == 434.2