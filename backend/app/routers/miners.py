"""
Miner-Endpunkte: Liste aller erkannten Miner mit Live-Status und Historie.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Miner, HashrateHistory
from app.schemas import MinerOut, HashratePoint
from app.deps import require_viewer

router = APIRouter(prefix="/api/miners", tags=["miners"], dependencies=[Depends(require_viewer)])


@router.get("", response_model=list[MinerOut])
def list_miners(db: Session = Depends(get_db)):
    miners = db.query(Miner).all()
    result = []
    now = datetime.utcnow()
    for m in miners:
        s = m.status
        uptime = None
        if s and s.connected_since and s.is_online:
            uptime = int((now - s.connected_since).total_seconds())
        result.append(
            MinerOut(
                worker_name=m.worker_name,
                ip_address=m.ip_address,
                hashrate=s.hashrate if s else 0.0,
                accepted_shares=s.accepted_shares if s else 0,
                rejected_shares=s.rejected_shares if s else 0,
                last_share_at=s.last_share_at if s else None,
                connected_since=s.connected_since if s else None,
                uptime_seconds=uptime,
                is_online=s.is_online if s else False,
            )
        )
    return result


@router.get("/{worker_name}/hashrate-history", response_model=list[HashratePoint])
def miner_hashrate_history(worker_name: str, limit: int = Query(200, le=2000),
                            db: Session = Depends(get_db)):
    rows = (
        db.query(HashrateHistory)
        .filter(HashrateHistory.scope == worker_name)
        .order_by(HashrateHistory.timestamp.desc())
        .limit(limit)
        .all()
    )
    return list(reversed([HashratePoint(timestamp=r.timestamp, hashrate=r.hashrate) for r in rows]))
