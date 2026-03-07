"""
Tests for company settings integration in the web UI and reports.
"""

from app.models import CompanySettings


def login_test_user(client):
    """Authenticate the shared test user through the real login form."""
    return client.post(
        '/login',
        data={'username': 'testuser', 'password': 'testpass123'},
        follow_redirects=False,
    )


def test_company_settings_can_be_updated_and_used_in_reports(app, client, test_user):
    """Company profile should be editable and reflected in report headers."""
    login_response = login_test_user(client)
    assert login_response.status_code == 302

    response = client.post(
        '/settings/company',
        data={
            'company_name': 'FERRE EXITO PRUEBA, C.A.',
            'rif': 'J-12345678-9',
            'fiscal_address': 'Av. Principal de Prueba, Maracay',
            'phone': '0412-0000000',
            'email': 'admin@ferre-exito.test',
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert 'Configuración de empresa actualizada correctamente' in response.get_data(as_text=True)

    with app.app_context():
        settings = CompanySettings.query.first()
        assert settings is not None
        assert settings.company_name == 'FERRE EXITO PRUEBA, C.A.'
        assert settings.rif == 'J-12345678-9'

    report_response = client.get('/reports/libro-inventario')
    html = report_response.get_data(as_text=True)

    assert report_response.status_code == 200
    assert 'FERRE EXITO PRUEBA, C.A.' in html
    assert 'J-12345678-9' in html


def test_company_settings_page_requires_auth(client):
    """Anonymous users should be redirected to login."""
    response = client.get('/settings/company')

    assert response.status_code == 302
    assert '/login' in response.headers['Location']