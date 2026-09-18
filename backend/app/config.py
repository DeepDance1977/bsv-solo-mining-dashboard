"""
Zentrale Konfiguration der Anwendung.
Alle Werte werden aus Umgebungsvariablen (.env) geladen.
"""
from functools import lru_cache
from typing import ClassVar
from pydantic import field_validator
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

    # ---------------------------------------------------------------
    # Robustheit: Wenn die BSV-Node-App (noch) nicht installiert ist,
    # liefert die Plattform (Umbrel/5tratumOS) fuer verknuepfte
    # Umgebungsvariablen wie $APP_BITCOIN_RPC_PORT einen LEEREN String
    # statt die Variable ganz wegzulassen. Ohne diesen Validator wuerde
    # das Backend beim Start abstuerzen (Crash-Loop), nur weil die
    # Node-App noch fehlt. Leere Werte werden daher auf den jeweiligen
    # Standardwert zurueckgesetzt; der RPC-Aufruf schlaegt dann spaeter
    # kontrolliert fehl (Node zeigt "nicht erreichbar" statt Crash-Loop).
    # ---------------------------------------------------------------
    _INT_DEFAULTS: ClassVar[dict[str, int]] = {
        "BSV_RPC_PORT": 8332,
        "BSV_RPC_TIMEOUT": 10,
        "STRATUM_POLL_INTERVAL_SECONDS": 10,
        "MINER_OFFLINE_THRESHOLD_SECONDS": 120,
        "SYSTEM_POLL_INTERVAL_SECONDS": 5,
        "ACCESS_TOKEN_EXPIRE_MINUTES": 60 * 12,
        "REFRESH_TOKEN_EXPIRE_MINUTES": 60 * 24 * 7,
    }

    @field_validator(*_INT_DEFAULTS.keys(), mode="before")
    @classmethod
    def _empty_int_to_default(cls, v, info):
        if v == "":
            return cls._INT_DEFAULTS[info.field_name]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
