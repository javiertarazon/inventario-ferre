"""
Tests for pricing blueprint search endpoints.
"""

from datetime import date
from decimal import Decimal

from app.extensions import db
from app.models import ExchangeRate, ItemGroup, Product, Proveedor


def login_test_user(client):
    """Authenticate the shared test user through the real login form."""
    return client.post(
        '/login',
        data={'username': 'testuser', 'password': 'testpass123'},
        follow_redirects=False
    )


def test_search_products_requires_auth_returns_json(client):
    """Anonymous requests should receive JSON instead of an HTML redirect."""
    response = client.get('/pricing/search-products?q=martillo')

    assert response.status_code == 401
    assert response.is_json is True
    assert response.get_json()['success'] is False


def test_search_products_returns_filtered_products_for_logged_in_user(app, client, test_user):
    """Authenticated users can search calculated prices with category and supplier filters."""
    user_id, _ = test_user

    with app.app_context():
        supplier_a = Proveedor(nombre='Proveedor A', created_by=user_id, updated_by=user_id)
        supplier_b = Proveedor(nombre='Proveedor B', created_by=user_id, updated_by=user_id)
        category_a = ItemGroup(name='Categoria A', created_by=user_id, updated_by=user_id)
        category_b = ItemGroup(name='Categoria B', created_by=user_id, updated_by=user_id)
        db.session.add_all([supplier_a, supplier_b, category_a, category_b])
        db.session.flush()

        db.session.add(ExchangeRate(date=date.today(), rate=Decimal('40.00'), created_by=user_id))
        db.session.add_all([
            Product(
                codigo='H-MA-01',
                descripcion='Martillo grande',
                stock=10,
                precio_dolares=Decimal('5.00'),
                factor_ajuste=Decimal('1.20'),
                proveedor_id=supplier_a.id,
                item_group_id=category_a.id,
                reorder_point=2,
                created_by=user_id,
                updated_by=user_id
            ),
            Product(
                codigo='D-MA-02',
                descripcion='Martillo demo',
                stock=8,
                precio_dolares=Decimal('6.00'),
                factor_ajuste=Decimal('1.10'),
                proveedor_id=supplier_b.id,
                item_group_id=category_b.id,
                reorder_point=2,
                created_by=user_id,
                updated_by=user_id
            ),
        ])
        db.session.commit()
        supplier_a_id = supplier_a.id
        category_a_id = category_a.id

    login_response = login_test_user(client)
    assert login_response.status_code == 302

    response = client.get(
        f'/pricing/search-products?q=martillo&category_id={category_a_id}&proveedor_id={supplier_a_id}'
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['count'] == 1
    assert data['products'][0]['codigo'] == 'H-MA-01'
    assert data['products'][0]['categoria'] == 'Categoria A'
    assert data['products'][0]['proveedor'] == 'Proveedor A'
    assert data['products'][0]['precio_bs'] == 200.0
    assert data['products'][0]['precio_final_bs'] == 240.0


def test_pricing_page_uses_dedicated_results_container(app, client, test_user):
    """Pricing page should not reuse the global search results container ID."""
    login_response = login_test_user(client)
    assert login_response.status_code == 302

    response = client.get('/pricing/')
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'id="pricingSearchResults"' in html
    assert 'static/js/pricing_config.js' in html


def test_pricing_page_supports_rate_search_by_date_and_pagination(app, client, test_user):
    """Pricing page should expose date search and paginate exchange rate history."""
    user_id, _ = test_user

    with app.app_context():
        for day in range(1, 26):
            db.session.add(
                ExchangeRate(
                    date=date(2026, 2, day),
                    rate=Decimal('40.00') + Decimal(str(day)),
                    created_by=user_id,
                )
            )
        db.session.commit()

    login_response = login_test_user(client)
    assert login_response.status_code == 302

    first_page = client.get('/pricing/')
    html = first_page.get_data(as_text=True)
    assert first_page.status_code == 200
    assert 'name="search_date"' in html
    assert 'Paginación historial tasas' in html
    assert '2026-02-25' in html
    assert '2026-02-06' in html
    assert '2026-02-05' not in html

    filtered = client.get('/pricing/?search_date=2026-02-10')
    filtered_html = filtered.get_data(as_text=True)
    assert filtered.status_code == 200
    assert '2026-02-10' in filtered_html
    assert '2026-02-11' not in filtered_html
