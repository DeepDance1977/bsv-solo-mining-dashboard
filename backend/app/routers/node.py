"""
Node-Status Endpunkte: Sync-Status, Blockhoehe, Peers, Difficulty, Netzwerk-Hashrate, Uptime.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import HashrateHistory, BlockHistory
from app.schemas import NodeStatus, HashratePoint
from app.services.bsv_rpc import bsv_rpc, BsvRpcError
from app.deps import require_viewer

router = APIRouter(prefix="/api/node", tags=["node"], dependencies=[Depends(require_viewer)])


@router.get("/status", response_model=NodeStatus)
def get_status():
    try:
        info = bsv_rpc.get_blockchain_info()
        mining_info = bsv_rpc.get_mining_info()
        peers = bsv_rpc.get_peer_info()
        uptime = bsv_rpc.uptime()
        network_info = bsv_rpc.get_network_info()

        progress = info.get("verificationprogress", 0.0)
        return NodeStatus(
            connected=True,
            chain=info.get("chain"),
            block_height=info.get("blocks"),
            headers=info.get("headers"),
            verification_progress=progress,
            is_synced=progress >= 0.9999,
            peer_count=len(peers),
            difficulty=info.get("difficulty"),
            network_hashrate=mining_info.get("networkhashps"),
            uptime_seconds=uptime,
            version=str(network_info.get("subversion", "")),
        )
    except BsvRpcError as exc:
        return NodeStatus(connected=False, error=str(exc))


@router.get("/hashrate-history", response_model=list[HashratePoint])
def hashrate_history(limit: int = Query(200, le=2000), db: Session = Depends(get_db)):
    rows = (
        db.query(HashrateHistory)
        .filter(HashrateHistory.scope == "network")
        .order_by(HashrateHistory.timestamp.desc())
        .limit(limit)
        .all()
    )
    return list(reversed([HashratePoint(timestamp=r.timestamp, hashrate=r.hashrate) for r in rows]))


@router.get("/blocks")
def block_history(limit: int = Query(50, le=500), db: Session = Depends(get_db)):
    rows = (
        db.query(BlockHistory)
        .order_by(BlockHistory.height.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "height": r.height,
            "block_hash": r.block_hash,
            "found_by_worker": r.found_by_worker,
            "found_at": r.found_at,
            "is_own_block": r.is_own_block,
        }
        for r in rows
    ]
