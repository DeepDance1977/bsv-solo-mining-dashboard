"""
Pydantic-Schemas fuer Request-/Response-Validierung der API.
"""
from datetime import datetime
from pydantic import BaseModel, Field
from app.models import UserRole, EventSeverity


# ---------- Auth ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: int


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.VIEWER


class UserOut(BaseModel):
    id: str
    username: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: datetime | None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    password: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


# ---------- Node ----------
class NodeStatus(BaseModel):
    connected: bool
    chain: str | None = None
    block_height: int | None = None
    headers: int | None = None
    verification_progress: float | None = None  # 0..1
    is_synced: bool = False
    peer_count: int | None = None
    difficulty: float | None = None
    network_hashrate: float | None = None  # H/s, aus difficulty geschaetzt
    uptime_seconds: int | None = None
    version: str | None = None
    error: str | None = None


class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    temperature_celsius: float | None
    host_uptime_seconds: int


# ---------- Miner ----------
class MinerOut(BaseModel):
    worker_name: str
    ip_address: str | None
    hashrate: float
    accepted_shares: int
    rejected_shares: int
    last_share_at: datetime | None
    connected_since: datetime | None
    uptime_seconds: int | None = None
    is_online: bool

    class Config:
        from_attributes = True


class HashratePoint(BaseModel):
    timestamp: datetime
    hashrate: float


# ---------- Wallet ----------
class TransactionOut(BaseModel):
    txid: str
    category: str
    amount: float
    confirmations: int
    time: datetime
    is_mining_reward: bool = False


class WalletInfo(BaseModel):
    address: str | None
    balance: float
    unconfirmed_balance: float
    transactions: list[TransactionOut]
    last_mining_rewards: list[TransactionOut]


# ---------- Events ----------
class EventOut(BaseModel):
    id: int
    timestamp: datetime
    category: str
    severity: EventSeverity
    message: str

    class Config:
        from_attributes = True
