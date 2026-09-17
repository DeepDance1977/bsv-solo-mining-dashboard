# Installationsanleitung

## Voraussetzungen

- Raspberry Pi 5 (8 GB RAM empfohlen)
- 5tratumOS (oder Raspberry Pi OS 64-bit / Ubuntu Server 64-bit arm64)
- Externe SSD/NVMe fuer die Blockchain-Daten (microSD wird **nicht** empfohlen)
- Docker + Docker Compose v2 (oder native Installation, siehe unten)

## Variante A: Docker Compose (empfohlen)

```bash
git clone https://github.com/DeepDance1977/bsv-solo-mining-dashboard.git
cd bsv-solo-mining-dashboard
cp .env.example .env
```

`.env` bearbeiten und mindestens folgende Werte setzen:

- `SECRET_KEY` – langer, zufaelliger String (z.B. `openssl rand -hex 32`)
- `BOOTSTRAP_ADMIN_PASSWORD` – Erstpasswort fuer den Admin-Account
- `BSV_RPC_USER` / `BSV_RPC_PASSWORD` – Zugangsdaten fuer den Node
- `STRATUM_API_URL` bzw. `STRATUM_LOG_PATH` – je nachdem, welche Schnittstelle
  dein Stratum-Server bereitstellt
- `TELEGRAM_ENABLED=true`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` – falls
  Benachrichtigungen gewuenscht sind (Bot per @BotFather anlegen, Chat-ID
  z.B. per @userinfobot ermitteln)

Danach:

```bash
docker compose up -d --build
```

Der BSV-Node (`./node`) wird beim ersten Start **aus dem Quellcode kompiliert**
– das kann auf einem Raspberry Pi 5 **1–3 Stunden** dauern. Fortschritt pruefen:

```bash
docker compose logs -f bsv-node
```

Falls du bereits eine eigene BSV-Node betreibst (z.B. als separate App),
kommentiere den `bsv-node`-Service in `docker-compose.yml` aus und setze in
`.env`: `BSV_RPC_HOST=host.docker.internal` (bzw. die IP der Node).

## Variante B: Native Installation (ohne Docker, via systemd)

1. Backend:
   ```bash
   cd backend
   python3.12 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. `.env` im Projekt-Root anlegen (siehe `.env.example`), Pfad in der
   systemd-Unit anpassen.
3. Frontend bauen und z.B. per Nginx ausliefern:
   ```bash
   cd frontend
   npm install
   npm run build   # erzeugt dist/, per Nginx/Apache servieren
   ```
4. systemd-Units installieren:
   ```bash
   sudo cp systemd/bsv-dashboard.service /etc/systemd/system/
   sudo cp systemd/bsv-node.service /etc/systemd/system/   # falls Node nativ laeuft
   sudo systemctl daemon-reload
   sudo systemctl enable --now bsv-dashboard
   ```

## HTTPS aktivieren

Empfohlen: Reverse-Proxy (z.B. Caddy oder Nginx mit Let's Encrypt/Certbot)
vor dem Frontend-Container/-Port platzieren. Beispiel mit Caddy:

```
dashboard.deinedomain.de {
    reverse_proxy localhost:3000
}
```

Caddy kuemmert sich automatisch um das TLS-Zertifikat.

## Installation als App über Umbrel oder 5tratumOS

Dieses Projekt liegt fix und fertig als **Umbrel-kompatibles App-Store-Paket**
unter `app-store/` vor – 5tratumOS (WillItMod/5tratum) verwendet ebenfalls
das Umbrel-App-Format ueber einen eigenen Community-Store, daher funktioniert
dasselbe Manifest fuer beide Plattformen.

### 1. Docker-Images veroeffentlichen

Die GitHub-Actions-Pipeline (`.github/workflows/docker-build.yml`) baut und
veroeffentlicht bei jedem Tag automatisch:
- `ghcr.io/deepdance1977/bsv-solo-mining-dashboard-backend`
- `ghcr.io/deepdance1977/bsv-solo-mining-dashboard-frontend`
- `ghcr.io/deepdance1977/bsv-full-node-arm64` (benoetigt einen
  **self-hosted arm64 Runner**, z.B. den Pi 5 selbst, siehe Kommentare in
  der Workflow-Datei)

Passe `env.OWNER` im Workflow an deinen eigenen GitHub-Benutzernamen an,
falls abweichend.

### 2. Bei Umbrel einreichen (offizieller Store)

1. Fork von https://github.com/getumbrel/umbrel-apps
2. Ordner `app-store/bsv-solo-mining-dashboard/` in den Fork unter
   `bsv-solo-mining-dashboard/` kopieren (inkl. `icon.svg` und Screenshots
   unter `gallery/`)
3. Pull Request gegen `getumbrel/umbrel-apps` stellen

Fuer die Node-App analog mit `app-store/deepdance-bitcoin-sv/`.

### 3. Bei 5tratumOS einreichen (Community-Store)

1. Fork des 5tratumOS-Community-App-Stores (z.B.
   `WillItMod/umbrel-community-store` oder den in der 5tratumOS-Doku
   verlinkten Store)
2. Gleiches Vorgehen wie bei Umbrel – Ordnerstruktur ist identisch, da
   beide auf dem Umbrel-App-Manifest-Format basieren
3. Pull Request stellen bzw. Store-URL in 5tratumOS unter "App Store
   hinzufuegen" eintragen, um waehrend der Review-Phase bereits selbst zu
   testen

### 4. Screenshots (Gallery) ergaenzen

Vor der Einreichung `gallery/1.jpg`, `2.jpg`, `3.jpg` (empfohlen: 1440×900px,
JPG) mit echten Screenshots des laufenden Dashboards in beiden
App-Store-Ordnern ablegen – Platzhalter sind in den `umbrel-app.yml`-Dateien
bereits referenziert.

## Troubleshooting

- **Node-Build schlaegt fehl**: siehe Tabelle in `node/README.md`
  (Berkeley DB, Boost, Architektur-Mismatch)
- **WebSocket verbindet nicht**: pruefen, ob der Reverse-Proxy
  `Upgrade`/`Connection`-Header durchreicht (siehe `frontend/nginx.conf`)
- **Miner werden nicht erkannt**: `STRATUM_API_URL` bzw. `STRATUM_LOG_PATH`
  in `.env` pruefen; das erwartete JSON-/Log-Format ist in
  `backend/app/services/stratum_monitor.py` dokumentiert
