"""
Service layer for exchange rate management and BCV synchronization.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re
import ssl
from typing import Dict, Optional, Tuple
from urllib.error import URLError
from urllib.request import Request, urlopen

from flask import current_app

try:
    import certifi
except ImportError:  # pragma: no cover - certifi is expected in runtime envs
    certifi = None

from app.extensions import db
from app.models import ExchangeRate
from app.utils.exceptions import BusinessLogicError, ValidationError


class ExchangeRateService:
    """Manage manual and automated USD/Bs exchange rates."""

    def get_current_rate(self):
        """Return the latest persisted exchange rate."""
        return ExchangeRate.get_current_rate()

    def get_recent_rates(self, limit: int = 10):
        """Return recent persisted rates ordered descending by date."""
        return ExchangeRate.query.order_by(ExchangeRate.date.desc()).limit(limit).all()

    def upsert_rate(
        self,
        rate_value,
        target_date: Optional[date] = None,
        user_id: Optional[int] = None,
    ) -> Tuple[ExchangeRate, bool]:
        """Create or update a rate for a specific date."""
        target_date = target_date or date.today()

        try:
            normalized_rate = Decimal(str(rate_value)).quantize(Decimal('0.0001'))
        except (InvalidOperation, ValueError) as exc:
            raise ValidationError('La tasa de cambio es inválida', field='rate') from exc

        if normalized_rate <= 0:
            raise ValidationError('La tasa de cambio debe ser mayor que cero', field='rate')

        existing_rate = ExchangeRate.query.filter_by(date=target_date).first()
        created = existing_rate is None

        if existing_rate:
            existing_rate.rate = normalized_rate
            existing_rate.created_at = datetime.utcnow()
            if user_id:
                existing_rate.created_by = user_id
            record = existing_rate
        else:
            record = ExchangeRate(
                date=target_date,
                rate=normalized_rate,
                created_by=user_id,
            )
            db.session.add(record)

        db.session.commit()
        return record, created

    def sync_today_from_bcv(self, user_id: Optional[int] = None) -> Dict[str, object]:
        """Fetch the current BCV USD rate and persist it for today."""
        html = self._fetch_remote_document()
        rate_value = self.extract_rate_from_html(html)
        rate_record, created = self.upsert_rate(rate_value, target_date=date.today(), user_id=user_id)

        return {
            'rate': float(rate_record.rate),
            'date': rate_record.date,
            'created': created,
        }

    def extract_rate_from_html(self, html: str) -> Decimal:
        """Extract the USD rate from BCV HTML markup."""
        currency_code = current_app.config.get('BCV_CURRENCY_CODE', 'USD')
        compact_html = re.sub(r'\s+', ' ', html or '')

        patterns = [
            r'(?is)<div[^>]+id=["\"]dolar["\"][^>]*>.*?<strong>\s*([0-9][0-9\.,]+)\s*</strong>',
            rf'(?is)<span>\s*{currency_code}\s*</span>.*?<strong>\s*([0-9][0-9\.,]+)\s*</strong>',
            rf'(?is){currency_code}.*?<strong>\s*([0-9][0-9\.,]+)\s*</strong>',
            rf'(?is){currency_code}(?:</[^>]+>|[^0-9]){{0,120}}(\d{{1,3}}(?:\.\d{{3}})*,\d{{2,8}})',
            rf'(?is){currency_code}(?:</[^>]+>|[^0-9]){{0,120}}(\d{{1,3}}(?:,\d{{3}})*\.\d{{2,8}})',
            r'(?is)D[oó]lar(?:\s+estadounidense|\s+de\s+los\s+EEUU)?(?:</[^>]+>|[^0-9]){0,120}(\d{1,3}(?:\.\d{3})*,\d{2,6})',
        ]

        for pattern in patterns:
            match = re.search(pattern, compact_html)
            if match:
                return self._normalize_rate(match.group(1))

        raise BusinessLogicError('No fue posible identificar la tasa USD del BCV en la respuesta recibida')

    def _fetch_remote_document(self) -> str:
        """Download the BCV source HTML."""
        target_url = current_app.config.get('BCV_RATE_URL', 'https://www.bcv.org.ve/')
        timeout = current_app.config.get('BCV_TIMEOUT_SECONDS', 15)
        user_agent = current_app.config.get(
            'BCV_USER_AGENT',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) FerreExitoInventario/1.0'
        )

        request = Request(target_url, headers={'User-Agent': user_agent})
        ssl_context = self._build_ssl_context()

        try:
            with urlopen(request, timeout=timeout, context=ssl_context) as response:
                return response.read().decode('utf-8', errors='ignore')
        except URLError as exc:
            if self._should_retry_insecure(exc):
                current_app.logger.warning(
                    'Fallo SSL validado contra BCV; reintentando sin verificacion por configuracion del entorno'
                )
                insecure_context = ssl._create_unverified_context()
                try:
                    with urlopen(request, timeout=timeout, context=insecure_context) as response:
                        return response.read().decode('utf-8', errors='ignore')
                except URLError as insecure_exc:
                    raise BusinessLogicError(f'No fue posible consultar el BCV: {insecure_exc}') from insecure_exc
        except URLError as exc:
            raise BusinessLogicError(f'No fue posible consultar el BCV: {exc}') from exc

    def _build_ssl_context(self):
        """Build an SSL context using certifi when available."""
        if certifi is not None:
            return ssl.create_default_context(cafile=certifi.where())
        return ssl.create_default_context()

    def _should_retry_insecure(self, exc: URLError) -> bool:
        """Allow insecure retry only for certificate validation failures when configured."""
        if not current_app.config.get('BCV_ALLOW_INSECURE_SSL_FALLBACK', False):
            return False

        reason = getattr(exc, 'reason', None)
        return isinstance(reason, ssl.SSLCertVerificationError)

    def _normalize_rate(self, raw_rate: str) -> Decimal:
        """Normalize localized decimal strings into Decimal values."""
        cleaned = (raw_rate or '').strip()
        if ',' in cleaned and '.' in cleaned:
            cleaned = cleaned.replace('.', '').replace(',', '.')
        elif ',' in cleaned:
            cleaned = cleaned.replace(',', '.')

        try:
            return Decimal(cleaned).quantize(Decimal('0.0001'))
        except InvalidOperation as exc:
            raise BusinessLogicError(f'La tasa obtenida del BCV es inválida: {raw_rate}') from exc