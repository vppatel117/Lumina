import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'lumina.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEFAULT_LOAN_DURATION_DAYS = int(os.getenv("DEFAULT_LOAN_DURATION_DAYS", "14"))
    EXTERNAL_API_BASE_URL = os.getenv("EXTERNAL_API_BASE_URL", "")
    EXTERNAL_API_TOKEN = os.getenv("EXTERNAL_API_TOKEN", "")

    @property
    def external_api_enabled(self) -> bool:
        return bool(self.EXTERNAL_API_BASE_URL)


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}


def get_config():
    """Return the config class tied to FLASK_CONFIG or default to development."""
    config_name = os.getenv("FLASK_CONFIG", "development").lower()
    return CONFIG_MAP.get(config_name, Config)
