import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Tuple
import re

from app.core.config import settings


class BCVService:
    """Servicio para obtener la tasa de cambio del Banco Central de Venezuela"""
    
    def __init__(self):
        self.bcv_url = settings.BCV_URL
        self.timeout = settings.BCV_TIMEOUT
        self.max_retries = settings.BCV_RETRY_ATTEMPTS
    
    async def fetch_exchange_rate(self) -> Tuple[Optional[float], str]:
        """
        Obtiene la tasa de cambio del BCV con reintentos automáticos.
        Retorna una tupla: (tasa, mensaje_de_estado)
        """
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                rate = await self._scrape_bcv_rate()
                if rate is not None and rate > 0:
                    return (rate, f"Tasa obtenida exitosamente en intento {attempt}")
                else:
                    last_error = "Tasa inválida obtenida del BCV"
            except httpx.TimeoutException as e:
                last_error = f"Timeout en intento {attempt}: {str(e)}"
            except httpx.RequestError as e:
                last_error = f"Error de conexión en intento {attempt}: {str(e)}"
            except Exception as e:
                last_error = f"Error inesperado en intento {attempt}: {str(e)}"
            
            if attempt < self.max_retries:
                # Esperar antes del próximo reintento
                import asyncio
                await asyncio.sleep(2)
        
        # Si llegamos aquí, todos los intentos fallaron
        alert_message = f"ALERTA: No se pudo obtener la tasa del BCV después de {self.max_retries} intentos. Último error: {last_error}"
        return (None, alert_message)
    
    async def _scrape_bcv_rate(self) -> Optional[float]:
        """
        Scraping de la página del BCV para obtener la tasa del dólar.
        Nota: El scraping puede fallar si el BCV cambia su estructura o bloquea el acceso.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Intentar acceder a la página principal del BCV
                response = await client.get(self.bcv_url, follow_redirects=True)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Buscar la tasa del dólar en diferentes posibles ubicaciones
                # El BCV suele mostrar las tasas en elementos con clase específica
                
                # Método 1: Buscar por texto que contenga "Dólar" o "USD"
                dollar_elements = soup.find_all(string=re.compile(r'Dólar|USD|Dollar', re.IGNORECASE))
                
                for element in dollar_elements:
                    parent = element.find_parent()
                    if parent:
                        # Buscar el valor numérico cercano
                        rate_text = self._extract_rate_from_element(parent)
                        if rate_text:
                            rate = float(rate_text.replace(',', '.'))
                            if 1.0 < rate < 100.0:  # Rango razonable para la tasa
                                return rate
                
                # Método 2: Buscar en tablas de tasas
                tables = soup.find_all('table')
                for table in tables:
                    rate = self._extract_rate_from_table(table)
                    if rate:
                        return rate
                
                # Método 3: Buscar en divs con clases comunes
                rate_divs = soup.find_all('div', class_=re.compile(r'tasa|rate|dolar|usd', re.IGNORECASE))
                for div in rate_divs:
                    rate_text = self._extract_rate_from_element(div)
                    if rate_text:
                        rate = float(rate_text.replace(',', '.'))
                        if 1.0 < rate < 100.0:
                            return rate
                
                return None
                
            except Exception as e:
                print(f"Error scraping BCV: {e}")
                return None
    
    def _extract_rate_from_element(self, element) -> Optional[str]:
        """Extrae un número decimal de un elemento HTML"""
        if not element:
            return None
        
        text = element.get_text()
        # Buscar patrón de número decimal (ej: 36,50 o 36.50)
        pattern = r'\d+[,.]\d{2}'
        match = re.search(pattern, text)
        if match:
            return match.group()
        
        return None
    
    def _extract_rate_from_table(self, table) -> Optional[float]:
        """Extrae la tasa del dólar de una tabla HTML"""
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                cell_text = ' '.join([cell.get_text() for cell in cells])
                if re.search(r'Dólar|USD|Dollar', cell_text, re.IGNORECASE):
                    for cell in cells:
                        rate_text = self._extract_rate_from_element(cell)
                        if rate_text:
                            try:
                                rate = float(rate_text.replace(',', '.'))
                                if 1.0 < rate < 100.0:
                                    return rate
                            except ValueError:
                                continue
        return None
    
    async def get_rate_with_fallback(self, fallback_rate: float = 36.0) -> Tuple[float, str, bool]:
        """
        Obtiene la tasa del BCV con un fallback si falla.
        Retorna: (tasa, mensaje, es_fallback)
        """
        rate, message = await self.fetch_exchange_rate()
        
        if rate is None:
            # Usar tasa de fallback
            return (fallback_rate, f"{message}. Usando tasa de respaldo: {fallback_rate}", True)
        
        return (rate, message, False)


# Instancia global del servicio
bcv_service = BCVService()
