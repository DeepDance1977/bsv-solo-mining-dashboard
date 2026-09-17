"""
BSV Solo Mining Dashboard - Backend Entry Point
Autor / Eigentuemer: DeepDance
Lizenz: MIT

Startet die FastAPI-Anwendung, legt beim ersten Start das Datenbankschema an,
erstellt einen Admin-Bootstrap-Benutzer (falls noch keiner existiert) und
startet den Hintergrund-Scheduler fuer Node-, Miner- und Systemueberwachung.
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine, SessionLocal
from app.models import User, UserRole
from app.security import hash_password
from app.services.scheduler import start_scheduler, shutdown_scheduler
from app.routers import auth, node, miners, wallet, system, ws

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("main")

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Web-Dashboard fuer eine Bitcoin SV Full Node und Solo-Mining-Umgebung "
                 "(Raspberry Pi 5 / 5tratumOS). Entwickelt von DeepDance.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(node.router)
app.include_router(miners.router)
app.include_router(wallet.router)
app.include_router(system.router)
app.include_router(ws.router)


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok", "app": settings.APP_NAME}


def _bootstrap_admin():
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin = User(
                username=settings.BOOTSTRAP_ADMIN_USERNAME,
                hashed_password=hash_password(settings.BOOTSTRAP_ADMIN_PASSWORD),
                role=UserRole.ADMIN,
            )
            db.add(admin)
            db.commit()
            logger.warning(
                "Erstbenutzer angelegt: '%s'. BITTE Passwort sofort nach dem ersten "
                "Login aendern!", settings.BOOTSTRAP_ADMIN_USERNAME,
            )
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    _bootstrap_admin()
    start_scheduler()
    logger.info("%s gestartet.", settings.APP_NAME)


@app.on_event("shutdown")
def on_shutdown():
    shutdown_scheduler()
