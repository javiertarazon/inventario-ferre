from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Ferretería Inventario & Facturación"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./ferreteria.db"
    
    # Security
    SECRET_KEY: str = "tu_clave_secreta_muy_segura_cambiala_en_produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    # BCV Settings
    BCV_URL: str = "http://www.bcv.org.ve/"
    BCV_MAX_RETRIES: int = 3
    DEFAULT_RATE: float = 36.5  # Tasa por defecto si falla BCV
    
    # Currency
    BASE_CURRENCY: str = "USD"  # USD o VES
    
    # IGTF
    IGTF_RATE: float = 0.03  # 3%
    
    # IVA rates
    IVA_GENERAL: float = 0.16  # 16%
    IVA_REDUCED: float = 0.08  # 8% (alimentos, medicinas)
    IVA_EXEMPT: float = 0.00  # Exento
    
    class Config:
        env_file = ".env"


settings = Settings()
