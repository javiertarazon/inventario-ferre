import httpx
import re
from typing import Optional, Tuple
from app.core.config import settings


class BCVService:
    """Servicio para obtener la tasa de cambio del BCV"""
    
    def __init__(self):
        self.bcv_url = settings.BCV_URL
        self.max_retries = settings.BCV_MAX_RETRIES
        self.default_rate = settings.DEFAULT_RATE
    
    async def get_exchange_rate(self) -> Tuple[Optional[float], str]:
        """
        Obtiene la tasa de cambio del BCV con reintentos automáticos.
        Retorna una tupla (tasa, mensaje_de_estado)
        """
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                rate = await self._scrape_bcv_rate()
                if rate and rate > 0:
                    return (rate, f"Tasa BCV obtenida exitosamente en intento {attempt}")
                
                last_error = "Tasa no válida obtenida del BCV"
                
            except Exception as e:
                last_error = f"Error en intento {attempt}: {str(e)}"
                
                if attempt < self.max_retries:
                    continue
                break
        
        # Si fallaron todos los intentos, retornar tasa por defecto con alerta
        alert_message = (
            f"ALERTA: No se pudo obtener la tasa del BCV después de {self.max_retries} intentos. "
            f"Último error: {last_error}. "
            f"Se usará la tasa por defecto: {self.default_rate} VES/USD. "
            f"Por favor verifique la conexión a internet o actualice manualmente."
        )
        
        return (self.default_rate, alert_message)
    
    async def _scrape_bcv_rate(self) -> Optional[float]:
        """
        Hace scraping de la página del BCV para obtener la tasa del dólar.
        Nota: El BCV no tiene API oficial, esto es un scraping básico.
        """
        try:
            # URLs alternativas del BCV
            urls = [
                "http://www.bcv.org.ve/",
                "https://www.bcv.org.ve/",
            ]
            
            for url in urls:
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        response = await client.get(url, follow_redirects=True)
                        response.raise_for_status()
                        
                        # Buscar patrones de tasa de cambio en el HTML
                        content = response.text
                        
                        # Patrones comunes para encontrar la tasa
                        patterns = [
                            r'Dólar\s*[:\-]?\s*Bs\.\s*([\d,]+\.?\d*)',
                            r'USD\s*[:\-]?\s*([\d,]+\.?\d*)',
                            r'(\d+,\d{2})\s*(?:VES|Bs)',
                            r'tasa.*?(\d+,\d{2})',
                        ]
                        
                        for pattern in patterns:
                            match = re.search(pattern, content, re.IGNORECASE)
                            if match:
                                rate_str = match.group(1).replace(',', '.')
                                try:
                                    rate = float(rate_str)
                                    if 1 < rate < 1000:  # Validación razonable
                                        return rate
                                except ValueError:
                                    continue
                    
                except httpx.RequestError:
                    continue
            
            return None
            
        except Exception as e:
            raise Exception(f"Error scraping BCV: {str(e)}")
    
    async def get_rate_with_alert(self) -> dict:
        """
        Obtiene la tasa y retorna información completa con alertas si es necesario.
        """
        rate, message = await self.get_exchange_rate()
        
        is_alert = "ALERTA" in message
        
        return {
            "rate": rate,
            "message": message,
            "is_alert": is_alert,
            "source": "BCV" if not is_alert else "DEFAULT",
            "default_rate_used": is_alert
        }


bcv_service = BCVService()
