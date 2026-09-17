"""
Stratum-Server Monitor.

Da es keinen einheitlichen Standard fuer Solo-Mining-Stratum-Server (ckpool,
public-pool, benutzerdefinierte 5tratumOS-Forks etc.) gibt, unterstuetzt dieser
Monitor zwei austauschbare Quellen:

1. HTTP-API  (empfohlen): der Stratum-Server liefert JSON unter STRATUM_API_URL,
   z.B. [{"worker": "rig1.worker1", "ip": "192.168.1.50", "hashrate": 123.4,
          "accepted": 100, "rejected": 2, "last_share": 1699999999,
          "connected_since": 1699990000}, ...]

2. Log-Datei-Fallback: einfache ckpool-artige Statuszeilen werden geparst,
   falls keine API verfuegbar ist.

Neue Backends koennen ergaenzt werden, indem `fetch_miners()` erweitert wird.
"""
import json
import re
import time
from datetime import datetime, timezone

import httpx

from app.config import get_settings

settings = get_settings()

_LOG_LINE_RE = re.compile(
    r"worker=(?P<worker>\S+)\s+ip=(?P<ip>\S+)\s+hashrate=(?P<hashrate>[\d.]+)\s+"
    r"accepted=(?P<accepted>\d+)\s+rejected=(?P<rejected>\d+)\s+last_share=(?P<last_share>\d+)"
)


class MinerSample:
    def __init__(self, worker: str, ip: str | None, hashrate: float,
                 accepted: int, rejected: int, last_share: datetime | None,
                 connected_since: datetime | None):
        self.worker = worker
        self.ip = ip
        self.hashrate = hashrate
        self.accepted = accepted
        self.rejected = rejected
        self.last_share = last_share
        self.connected_since = connected_since


def _parse_ts(value) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc).replace(tzinfo=None)
    except (ValueError, TypeError):
        return None


def _fetch_via_api() -> list[MinerSample]:
    with httpx.Client(timeout=5) as client:
        resp = client.get(settings.STRATUM_API_URL)
        resp.raise_for_status()
        data = resp.json()

    samples = []
    for entry in data:
        samples.append(
            MinerSample(
                worker=entry.get("worker") or entry.get("workername") or "unknown",
                ip=entry.get("ip"),
                hashrate=float(entry.get("hashrate", 0.0)),
                accepted=int(entry.get("accepted", 0)),
                rejected=int(entry.get("rejected", 0)),
                last_share=_parse_ts(entry.get("last_share")),
                connected_since=_parse_ts(entry.get("connected_since")),
            )
        )
    return samples


def _fetch_via_log() -> list[MinerSample]:
    samples: dict[str, MinerSample] = {}
    try:
        with open(settings.STRATUM_LOG_PATH, "r", errors="ignore") as fh:
            lines = fh.readlines()[-2000:]  # nur die letzten Zeilen betrachten
    except FileNotFoundError:
        return []

    for line in lines:
        match = _LOG_LINE_RE.search(line)
        if not match:
            continue
        gd = match.groupdict()
        samples[gd["worker"]] = MinerSample(
            worker=gd["worker"],
            ip=gd["ip"],
            hashrate=float(gd["hashrate"]),
            accepted=int(gd["accepted"]),
            rejected=int(gd["rejected"]),
            last_share=_parse_ts(gd["last_share"]),
            connected_since=None,
        )
    return list(samples.values())


def fetch_miners() -> list[MinerSample]:
    """Versucht zuerst die HTTP-API, faellt auf die Log-Datei zurueck."""
    if settings.STRATUM_API_URL:
        try:
            return _fetch_via_api()
        except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError, ValueError):
            pass
    if settings.STRATUM_LOG_PATH:
        return _fetch_via_log()
    return []
