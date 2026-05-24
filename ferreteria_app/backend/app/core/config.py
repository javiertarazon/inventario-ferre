from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Ferretería Venezuela - Sistema de Inventario y Facturación"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./ferreteria.db"
    
    # Security
    SECRET_KEY: str = "tu_clave_secreta_muy_segura_cambiar_en_produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    # BCV API
    BCV_URL: str = "https://www.bcv.org.ve/"
    BCV_RETRY_ATTEMPTS: int = 3
    BCV_TIMEOUT: int = 10
    
    # Currency
    BASE_CURRENCY: str = "USD"  # Dólar como moneda base
    IGTF_RATE: float = 0.03  # 3% IGTF
    
    # IVA Rates
    IVA_GENERAL: float = 0.16  # 16%
    IVA_REDUCED: float = 0.08  # 8% (ejemplo)
    IVA_EXEMPT: float = 0.00  # Exento
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
