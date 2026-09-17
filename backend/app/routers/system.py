"""
System-Endpunkte: CPU/RAM/Disk/Temperatur des Raspberry Pi sowie Event-Log.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import EventLog
from app.schemas import SystemMetrics, EventOut
from app.services.system_metrics import get_system_metrics
from app.deps import require_viewer

router = APIRouter(prefix="/api/system", tags=["system"], dependencies=[Depends(require_viewer)])


@router.get("/metrics", response_model=SystemMetrics)
def metrics():
    return get_system_metrics()


@router.get("/events", response_model=list[EventOut])
def events(limit: int = Query(100, le=1000), db: Session = Depends(get_db)):
    rows = db.query(EventLog).order_by(EventLog.timestamp.desc()).limit(limit).all()
    return rows
