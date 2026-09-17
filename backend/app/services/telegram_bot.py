"""
Telegram-Benachrichtigungen. Verwendet die Telegram Bot HTTP-API direkt
(httpx), um eine leichte, asynchrone Anbindung ohne zusaetzliche Event-Loop-
Komplikationen der python-telegram-bot-Bibliothek zu haben.
"""
import logging

import httpx

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger("telegram")


async def send_telegram_message(text: str) -> None:
    if not settings.TELEGRAM_ENABLED or not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": settings.TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                logger.error("Telegram-Versand fehlgeschlagen: %s", resp.text)
    except httpx.RequestError as exc:
        logger.error("Telegram nicht erreichbar: %s", exc)


async def notify_miner_offline(worker_name: str) -> None:
    await send_telegram_message(f"⚠️ Miner <b>{worker_name}</b> ist OFFLINE gegangen.")


async def notify_miner_online(worker_name: str) -> None:
    await send_telegram_message(f"✅ Miner <b>{worker_name}</b> ist wieder ONLINE.")


async def notify_block_found(height: int, block_hash: str, worker: str | None) -> None:
    who = f" von <b>{worker}</b>" if worker else ""
    await send_telegram_message(
        f"⛏️ Neuer Block #{height} gefunden{who}!\nHash: <code>{block_hash}</code>"
    )


async def notify_node_error(message: str) -> None:
    await send_telegram_message(f"🚨 Node-Fehler: {message}")
