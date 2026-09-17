"""
Hintergrund-Scheduler (APScheduler), der periodisch:
- Node-Status abfragt (RPC) und bei Fehlern/neuen Bloecken Events schreibt
- Miner ueber den Stratum-Monitor abfragt, Online/Offline-Wechsel erkennt
- System-Metriken erfasst
- alle Ergebnisse per WebSocket an das Frontend broadcastet
- relevante Ereignisse per Telegram versendet und in der DB (event_log) speichert
"""
import asyncio
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models import (
    Miner, MinerStatus, HashrateHistory, BlockHistory, EventLog, EventSeverity
)
from app.services.bsv_rpc import bsv_rpc, BsvRpcError
from app.services.stratum_monitor import fetch_miners
from app.services.system_metrics import get_system_metrics
from app.services.broadcaster import manager
from app.services import telegram_bot

settings = get_settings()
logger = logging.getLogger("scheduler")

_last_known_height: int | None = None


def _log_event(db: Session, category: str, severity: EventSeverity, message: str) -> EventLog:
    event = EventLog(category=category, severity=severity, message=message)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


async def poll_node():
    """Fragt den Node-Status ab, erkennt neue Bloecke und Fehler."""
    global _last_known_height
    db = SessionLocal()
    try:
        try:
            info = bsv_rpc.get_blockchain_info()
            mining_info = bsv_rpc.get_mining_info()
            peers = bsv_rpc.get_peer_info()
            uptime = bsv_rpc.uptime()

            height = info["blocks"]
            progress = info.get("verificationprogress", 0.0)
            difficulty = info.get("difficulty", 0.0)
            network_hashrate = mining_info.get("networkhashps", 0.0)

            payload = {
                "connected": True,
                "chain": info.get("chain"),
                "block_height": height,
                "headers": info.get("headers"),
                "verification_progress": progress,
                "is_synced": progress >= 0.9999,
                "peer_count": len(peers),
                "difficulty": difficulty,
                "network_hashrate": network_hashrate,
                "uptime_seconds": uptime,
            }
            await manager.broadcast("node_status", payload)

            db.add(HashrateHistory(scope="network", hashrate=network_hashrate))
            db.commit()

            if _last_known_height is not None and height > _last_known_height:
                block_hash = info.get("bestblockhash", "")
                existing = db.query(BlockHistory).filter(BlockHistory.height == height).first()
                if not existing:
                    db.add(BlockHistory(height=height, block_hash=block_hash))
                    db.commit()
                    _log_event(db, "node", EventSeverity.INFO, f"Neuer Block erkannt: #{height}")
                    await manager.broadcast("new_block", {"height": height, "hash": block_hash})
            _last_known_height = height

        except BsvRpcError as exc:
            logger.error("Node-Fehler: %s", exc)
            _log_event(db, "node", EventSeverity.ERROR, str(exc))
            await manager.broadcast("node_status", {"connected": False, "error": str(exc)})
            await telegram_bot.notify_node_error(str(exc))
    finally:
        db.close()


async def poll_miners():
    """Fragt den Stratum-Server ab, aktualisiert Miner-Status und erkennt Online/Offline-Wechsel."""
    db = SessionLocal()
    try:
        samples = fetch_miners()
        now = datetime.utcnow()
        seen_workers = set()

        for sample in samples:
            seen_workers.add(sample.worker)
            miner = db.query(Miner).filter(Miner.worker_name == sample.worker).first()
            if miner is None:
                miner = Miner(worker_name=sample.worker, ip_address=sample.ip)
                db.add(miner)
                db.flush()
                miner.status = MinerStatus(miner_id=miner.id)
                db.add(miner.status)

            was_online = miner.status.is_online if miner.status else False
            miner.ip_address = sample.ip or miner.ip_address

            status = miner.status
            status.hashrate = sample.hashrate
            status.accepted_shares = sample.accepted
            status.rejected_shares = sample.rejected
            status.last_share_at = sample.last_share or status.last_share_at
            if sample.connected_since:
                status.connected_since = sample.connected_since
            elif status.connected_since is None:
                status.connected_since = now

            is_stale = (
                status.last_share_at is not None
                and (now - status.last_share_at).total_seconds()
                > settings.MINER_OFFLINE_THRESHOLD_SECONDS
            )
            status.is_online = not is_stale

            db.add(HashrateHistory(scope=sample.worker, hashrate=sample.hashrate))

            if status.is_online and not was_online:
                _log_event(db, "miner", EventSeverity.INFO, f"Miner {sample.worker} ist online.")
                await telegram_bot.notify_miner_online(sample.worker)
            elif not status.is_online and was_online:
                _log_event(db, "miner", EventSeverity.WARNING, f"Miner {sample.worker} ist offline.")
                await telegram_bot.notify_miner_offline(sample.worker)

        # Miner, die gar nicht mehr gemeldet werden -> als offline markieren
        all_miners = db.query(Miner).all()
        for miner in all_miners:
            if miner.worker_name not in seen_workers and miner.status and miner.status.is_online:
                if miner.status.last_share_at and (now - miner.status.last_share_at).total_seconds() \
                        > settings.MINER_OFFLINE_THRESHOLD_SECONDS:
                    miner.status.is_online = False
                    _log_event(db, "miner", EventSeverity.WARNING, f"Miner {miner.worker_name} ist offline.")
                    await telegram_bot.notify_miner_offline(miner.worker_name)

        db.commit()

        miners_payload = [
            {
                "worker_name": m.worker_name,
                "ip_address": m.ip_address,
                "hashrate": m.status.hashrate if m.status else 0,
                "accepted_shares": m.status.accepted_shares if m.status else 0,
                "rejected_shares": m.status.rejected_shares if m.status else 0,
                "last_share_at": m.status.last_share_at if m.status else None,
                "connected_since": m.status.connected_since if m.status else None,
                "is_online": m.status.is_online if m.status else False,
            }
            for m in all_miners
        ]
        await manager.broadcast("miners", miners_payload)

    except Exception:
        logger.exception("Fehler beim Abfragen der Miner")
    finally:
        db.close()


async def poll_system():
    """Erfasst CPU/RAM/Disk/Temperatur des Raspberry Pi und broadcastet sie."""
    try:
        metrics = get_system_metrics()
        await manager.broadcast("system_metrics", metrics.model_dump())
    except Exception:
        logger.exception("Fehler beim Erfassen der Systemmetriken")


scheduler = AsyncIOScheduler()


def start_scheduler():
    scheduler.add_job(poll_node, "interval", seconds=15, id="poll_node", max_instances=1)
    scheduler.add_job(
        poll_miners, "interval",
        seconds=settings.STRATUM_POLL_INTERVAL_SECONDS, id="poll_miners", max_instances=1,
    )
    scheduler.add_job(
        poll_system, "interval",
        seconds=settings.SYSTEM_POLL_INTERVAL_SECONDS, id="poll_system", max_instances=1,
    )
    scheduler.start()


def shutdown_scheduler():
    scheduler.shutdown(wait=False)
