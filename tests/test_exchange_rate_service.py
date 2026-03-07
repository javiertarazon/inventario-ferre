"""
Tests for BCV rate synchronization service and pricing route.
"""
from datetime import date

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