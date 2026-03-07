"""
Service layer for singleton company settings.
"""
from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from typing import Any, Dict

from flask import current_app

from app.extensions import db
from app.models import CompanySettings
from app.utils.exceptions import ValidationError


class CompanySettingsService:
    """Manage fiscal and contact settings for the company profile."""

    DEFAULTS = {
        'company_name': 'INVERSIONES FERRE-EXITO, C.A',
        'rif': 'J-31764195-7',
        'fiscal_address': 'Calle Bolívar. Palo Negro, Municipio Libertador. Estado Aragua',
        'phone': '0412-7434522',
        'email': 'administracion@ferre-exito.local',
    }

    def get_settings(self, create_if_missing: bool = True):
        """Return persisted settings or create defaults on first access."""
        try:
            settings = CompanySettings.query.order_by(CompanySettings.id.asc()).first()
            if settings:
                return settings

            if not create_if_missing:
                return SimpleNamespace(id=None, **self.DEFAULTS)

            settings = CompanySettings(
                company_name=self.DEFAULTS['company_name'],
                rif=self.DEFAULTS['rif'],
                fiscal_address=self.DEFAULTS['fiscal_address'],
                phone=self.DEFAULTS['phone'],
                email=self.DEFAULTS['email'],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.session.add(settings)
            db.session.commit()
            return settings
        except Exception as exc:
            current_app.logger.warning('No fue posible cargar configuracion de empresa: %s', exc)
            return SimpleNamespace(id=None, **self.DEFAULTS)

    def get_company_context(self) -> Dict[str, Any]:
        """Return a template-friendly company profile dictionary."""
        settings = self.get_settings()
        return {
            'id': getattr(settings, 'id', None),
            'company_name': getattr(settings, 'company_name', self.DEFAULTS['company_name']),
            'rif': getattr(settings, 'rif', self.DEFAULTS['rif']),
            'fiscal_address': getattr(settings, 'fiscal_address', self.DEFAULTS['fiscal_address']) or '',
            'phone': getattr(settings, 'phone', self.DEFAULTS['phone']) or '',
            'email': getattr(settings, 'email', self.DEFAULTS['email']) or '',
        }

    def update_settings(self, data: Dict[str, Any], user_id: int):
        """Persist updated company settings."""
        company_name = (data.get('company_name') or '').strip()
        rif = (data.get('rif') or '').strip().upper()
        fiscal_address = (data.get('fiscal_address') or '').strip()
        phone = (data.get('phone') or '').strip()
        email = (data.get('email') or '').strip().lower()

        if not company_name:
            raise ValidationError('La razón social es requerida', field='company_name')
        if not rif:
            raise ValidationError('El RIF es requerido', field='rif')

        settings = self.get_settings(create_if_missing=True)
        settings.company_name = company_name
        settings.rif = rif
        settings.fiscal_address = fiscal_address or None
        settings.phone = phone or None
        settings.email = email or None
        settings.updated_by = user_id
        settings.updated_at = datetime.utcnow()
        if not settings.created_by:
            settings.created_by = user_id

        db.session.commit()
        return settings