"""
Zentrale Konfiguration der Anwendung.
Alle Werte werden aus Umgebungsvariablen (.env) geladen.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = "BSV Solo Mining Dashboard"
    ENV: str = "production"
    DEBUG: bool = False

    # Security / JWT
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12  # 12 Stunden
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 Tage

    # Datenbank
    DATABASE_URL: str = "postgresql+psycopg2://bsvdash:bsvdash@postgres:5432/bsvdash"

    # Bitcoin SV Full Node (RPC)
    BSV_RPC_HOST: str = "127.0.0.1"
    BSV_RPC_PORT: int = 8332
    BSV_RPC_USER: str = "rpcuser"
    BSV_RPC_PASSWORD: str = "rpcpassword"
    BSV_RPC_TIMEOUT: int = 10
    BSV_ZMQ_BLOCK_ADDR: str | None = None  # z.B. tcp://127.0.0.1:28332

    # Stratum Server Integration
    # Der Stratum-Server (z.B. p2pool, ckpool, public-pool-Fork o.ä.) muss
    # entweder eine HTTP-API bereitstellen ODER ein Log-/Status-File schreiben.
    STRATUM_API_URL: str | None = "http://127.0.0.1:9000/stats"
    STRATUM_LOG_PATH: str | None = "/var/log/stratum/stratum.log"
    STRATUM_POLL_INTERVAL_SECONDS: int = 10
    MINER_OFFLINE_THRESHOLD_SECONDS: int = 120

    # Wallet (nutzt die bitcoind Wallet-RPCs)
    WALLET_NAME: str = ""  # leer = Default-Wallet

    # System-Metriken
    SYSTEM_POLL_INTERVAL_SECONDS: int = 5
    RASPBERRY_PI_THERMAL_ZONE: str = "/sys/class/thermal/thermal_zone0/temp"
    DISK_PATH: str = "/"

    # Telegram Benachrichtigungen
    TELEGRAM_ENABLED: bool = False
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Erstbenutzer (wird beim ersten Start angelegt, falls keine Nutzer existieren)
    BOOTSTRAP_ADMIN_USERNAME: str = "admin"
    BOOTSTRAP_ADMIN_PASSWORD: str = "changeme123"


@lru_cache
def get_settings() -> Settings:
    return Settings()
