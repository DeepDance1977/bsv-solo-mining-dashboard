"""
Datenbankmodell (SQLAlchemy ORM).

Tabellen:
- users            : Benutzerverwaltung / Rollenmodell
- miners           : bekannte Miner (Stammdaten)
- miner_status     : aktueller Live-Status je Miner (1:1)
- hashrate_history : Zeitreihe der Hashrate (Node-Netzwerk + je Miner)
- block_history     : gefundene / gesehene Bloecke
- event_log         : allgemeines Ereignisprotokoll (Fehler, Alarme, Logins ...)
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    String, Integer, Float, BigInteger, Boolean, DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Erzwingt eine Passwortaenderung beim naechsten Login. Wird fuer den
    # automatisch angelegten Erstbenutzer auf True gesetzt, damit sich
    # niemand dauerhaft auf ein systemseitig vorgegebenes Passwort verlassen
    # muss (unabhaengig davon, ob/wie eine Plattform wie Umbrel/5tratumOS
    # eigene Zufallspasswoerter einspeist).
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Miner(Base):
    __tablename__ = "miners"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    worker_name: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    ip_address: Mapped[str] = mapped_column(String(64), nullable=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    status: Mapped["MinerStatus"] = relationship(
        back_populates="miner", uselist=False, cascade="all, delete-orphan"
    )


class MinerStatus(Base):
    """Aktueller Live-Zustand eines Miners (wird bei jedem Poll aktualisiert)."""
    __tablename__ = "miner_status"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    miner_id: Mapped[str] = mapped_column(String(36), ForeignKey("miners.id"), unique=True)

    hashrate: Mapped[float] = mapped_column(Float, default=0.0)  # H/s
    accepted_shares: Mapped[int] = mapped_column(BigInteger, default=0)
    rejected_shares: Mapped[int] = mapped_column(BigInteger, default=0)
    last_share_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    connected_since: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    miner: Mapped["Miner"] = relationship(back_populates="status")


class HashrateHistory(Base):
    """Zeitreihen-Tabelle fuer Charts (Netzwerk-Hashrate und Miner-Hashrate)."""
    __tablename__ = "hashrate_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    scope: Mapped[str] = mapped_column(String(16))  # "network" oder "pool" oder "<worker_name>"
    hashrate: Mapped[float] = mapped_column(Float)


class BlockHistory(Base):
    """Historie gefundener / relevanter Bloecke."""
    __tablename__ = "block_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    height: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    block_hash: Mapped[str] = mapped_column(String(64), unique=True)
    found_by_worker: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reward_satoshi: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    found_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_own_block: Mapped[bool] = mapped_column(Boolean, default=False)


class EventSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventLog(Base):
    """Allgemeines Ereignisprotokoll: Miner-Online/Offline, Node-Fehler, Bloecke, Logins."""
    __tablename__ = "event_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    category: Mapped[str] = mapped_column(String(32))  # node, miner, wallet, auth, system
    severity: Mapped[EventSeverity] = mapped_column(Enum(EventSeverity), default=EventSeverity.INFO)
    message: Mapped[str] = mapped_column(Text)
    notified_telegram: Mapped[bool] = mapped_column(Boolean, default=False)
