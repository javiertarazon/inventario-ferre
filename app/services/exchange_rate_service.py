"""
Service layer for exchange rate management and BCV synchronization.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
import re
import ssl
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin
from urllib.error import URLError
from urllib.request import Request, urlopen

from flask import current_app
import pandas as pd

try:
    import certifi
except ImportError:  # pragma: no cover - certifi is expected in runtime envs
    certifi = None

try:
    import xlrd  # noqa: F401
except ImportError:  # pragma: no cover - required only for historical BCV XLS parsing
    xlrd = None

from app.extensions import db
from app.models import ExchangeRate
from app.utils.exceptions import BusinessLogicError, ValidationError


class ExchangeRateService:
    """Manage manual and automated USD/Bs exchange rates."""

    HISTORICAL_LISTING_PATH = '/estadisticas/tipo-cambio-de-referencia-smc'

    def get_current_rate(self):
        """Return the latest persisted exchange rate."""
        return ExchangeRate.get_current_rate()

    def get_recent_rates(self, limit: int = 10):
        """Return recent persisted rates ordered descending by date."""
        return ExchangeRate.query.order_by(ExchangeRate.date.desc()).limit(limit).all()

    def get_rates_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        search_date: Optional[date] = None,
    ):
        """Return paginated exchange rates optionally filtered by an exact date."""
        query = ExchangeRate.query.order_by(ExchangeRate.date.desc())

        if search_date is not None:
            query = query.filter(ExchangeRate.date == search_date)

        return query.paginate(page=page, per_page=per_page, error_out=False)

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

    def sync_historical_from_bcv(
        self,
        start_date: date,
        end_date: Optional[date] = None,
        user_id: Optional[int] = None,
    ) -> Dict[str, object]:
        """Fetch BCV historical XLS workbooks and persist rates for a calendar range."""
        end_date = end_date or date.today()

        if start_date > end_date:
            raise ValidationError('La fecha inicial no puede ser mayor a la fecha final', field='start_date')

        if xlrd is None:
            raise BusinessLogicError('Falta la dependencia xlrd para procesar el historico BCV en formato XLS')

        workbook_urls = self.get_historical_workbook_urls()
        historical_entries = self._collect_historical_entries(workbook_urls, start_date, end_date)

        if not historical_entries:
            raise BusinessLogicError('No se encontraron tasas historicas del BCV para el rango solicitado')

        calendar_rates = self._expand_entries_to_calendar(historical_entries, start_date, end_date)

        created_count = 0
        updated_count = 0
        for target_date, rate_value in sorted(calendar_rates.items()):
            _, created = self.upsert_rate(rate_value, target_date=target_date, user_id=user_id)
            if created:
                created_count += 1
            else:
                updated_count += 1

        return {
            'start_date': start_date,
            'end_date': end_date,
            'created_count': created_count,
            'updated_count': updated_count,
            'total_dates': len(calendar_rates),
            'source_entries': len(historical_entries),
            'workbooks': len(workbook_urls),
        }

    def get_historical_workbook_urls(self, max_pages: int = 5) -> List[str]:
        """Return BCV historical XLS workbook URLs from the listing pages."""
        base_url = self._get_bcv_base_url()
        workbook_urls: List[str] = []
        seen_urls = set()

        for page_number in range(max_pages):
            listing_url = urljoin(base_url, self.HISTORICAL_LISTING_PATH)
            if page_number:
                listing_url = f'{listing_url}?page={page_number}'

            html = self._fetch_remote_document(target_url=listing_url)
            matches = re.findall(r'href=["\']([^"\']+_smc\.xls)["\']', html, flags=re.I)
            page_urls = [urljoin(base_url, match) for match in matches]

            if not page_urls:
                break

            new_urls = 0
            for page_url in page_urls:
                if page_url in seen_urls:
                    continue
                seen_urls.add(page_url)
                workbook_urls.append(page_url)
                new_urls += 1

            if new_urls == 0:
                break

        return workbook_urls

    def _collect_historical_entries(
        self,
        workbook_urls: List[str],
        start_date: date,
        end_date: date,
    ) -> List[Dict[str, object]]:
        """Parse historical BCV workbooks and extract USD entries."""
        entries_by_operation_date: Dict[date, Dict[str, object]] = {}

        for workbook_url in workbook_urls:
            workbook = pd.ExcelFile(workbook_url, engine='xlrd')
            for sheet_name in workbook.sheet_names:
                sheet = pd.read_excel(workbook, sheet_name=sheet_name, header=None)
                entry = self._extract_historical_sheet_entry(sheet_name, sheet)
                if entry is None:
                    continue

                operation_date = entry['operation_date']
                value_date = entry['value_date']
                if operation_date > end_date:
                    continue
                if value_date < start_date:
                    continue

                entries_by_operation_date[operation_date] = entry

        return sorted(entries_by_operation_date.values(), key=lambda item: item['operation_date'])

    def _extract_historical_sheet_entry(self, sheet_name: str, sheet: pd.DataFrame) -> Optional[Dict[str, object]]:
        """Extract operation date, value date and USD BID rate from a BCV worksheet."""
        operation_date = self._extract_sheet_date(sheet_name, 'sheet')
        value_date = None

        preview_rows = min(len(sheet.index), 10)
        for row_index in range(preview_rows):
            for cell_value in sheet.iloc[row_index].tolist():
                if not isinstance(cell_value, str):
                    continue
                if 'Fecha Valor:' not in cell_value:
                    continue
                match = re.search(r'Fecha Valor:\s*(\d{2}/\d{2}/\d{4})', cell_value)
                if match:
                    value_date = self._extract_sheet_date(match.group(1), 'cell')
                    break
            if value_date:
                break

        if value_date is None:
            return None

        usd_rate = None
        for _, row in sheet.iterrows():
            normalized_cells = {str(value).strip().upper() for value in row.tolist() if pd.notna(value)}
            if 'USD' not in normalized_cells:
                continue

            if len(row) > 5 and pd.notna(row.iloc[5]):
                usd_rate = self._normalize_rate(str(row.iloc[5]))
            elif len(row) > 6 and pd.notna(row.iloc[6]):
                usd_rate = self._normalize_rate(str(row.iloc[6]))
            break

        if usd_rate is None:
            return None

        return {
            'operation_date': operation_date,
            'value_date': value_date,
            'rate': usd_rate,
        }

    def _expand_entries_to_calendar(
        self,
        historical_entries: List[Dict[str, object]],
        start_date: date,
        end_date: date,
    ) -> Dict[date, Decimal]:
        """Expand BCV entries so non-business gap days inherit the next value date rate already published."""
        calendar_rates: Dict[date, Decimal] = {}

        for entry in historical_entries:
            operation_date = entry['operation_date']
            value_date = entry['value_date']
            rate_value = entry['rate']

            if start_date <= operation_date <= end_date:
                calendar_rates[operation_date] = rate_value

            fill_date = max(operation_date + timedelta(days=1), start_date)
            fill_limit = min(value_date - timedelta(days=1), end_date)
            while fill_date <= fill_limit:
                calendar_rates[fill_date] = rate_value
                fill_date += timedelta(days=1)

        return calendar_rates

    def _extract_sheet_date(self, raw_value: str, source_label: str) -> date:
        """Parse ddmmyyyy or dd/mm/yyyy dates found inside BCV historical workbooks."""
        candidate = str(raw_value or '').strip()
        if re.fullmatch(r'\d{8}', candidate):
            return datetime.strptime(candidate, '%d%m%Y').date()
        if re.fullmatch(r'\d{2}/\d{2}/\d{4}', candidate):
            return datetime.strptime(candidate, '%d/%m/%Y').date()
        raise BusinessLogicError(f'No fue posible interpretar la fecha {source_label} del historico BCV: {raw_value}')

    def _get_bcv_base_url(self) -> str:
        """Return BCV base URL derived from the configured rate URL."""
        configured_url = current_app.config.get('BCV_RATE_URL', 'https://www.bcv.org.ve/')
        match = re.match(r'^(https?://[^/]+)', configured_url)
        return match.group(1) if match else 'https://www.bcv.org.ve'

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

    def _fetch_remote_document(self, target_url: Optional[str] = None) -> str:
        """Download the BCV source HTML."""
        target_url = target_url or current_app.config.get('BCV_RATE_URL', 'https://www.bcv.org.ve/')
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