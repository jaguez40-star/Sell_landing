"""Configuración central de la aplicación (cargada desde entorno / .env)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "DISPOLA API"
    environment: str = "development"

    # Base de datos — SQLite en fase de desarrollo (D2)
    database_url: str = "sqlite:///./data/dispola.db"

    # CORS — el sitio Astro corre en 8889 en desarrollo (D1)
    frontend_origin: str = "http://localhost:8889"

    # Secreto para cookies firmadas de sesión
    session_secret: str = "cambiar-en-produccion"


settings = Settings()
