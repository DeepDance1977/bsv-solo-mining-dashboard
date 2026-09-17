# Lizenzen von Drittkomponenten (Third-Party Licenses)

Dieses Projekt (BSV Solo Mining Dashboard, © DeepDance, MIT-Lizenz) nutzt
folgende Open-Source- bzw. Freeware-Komponenten. Die jeweiligen Lizenzen
gelten zusaetzlich zur MIT-Lizenz dieses Projekts und muessen bei
Weitergabe/Distribution beachtet werden.

## Backend (Python)

| Komponente | Lizenz | Projekt |
|---|---|---|
| FastAPI | MIT | https://github.com/tiangolo/fastapi |
| Uvicorn | BSD-3-Clause | https://github.com/encode/uvicorn |
| SQLAlchemy | MIT | https://github.com/sqlalchemy/sqlalchemy |
| psycopg2-binary | LGPL-3.0 (mit Ausnahme fuer dynamisches Linken) | https://github.com/psycopg/psycopg2 |
| Alembic | MIT | https://github.com/sqlalchemy/alembic |
| Pydantic / pydantic-settings | MIT | https://github.com/pydantic/pydantic |
| python-jose | MIT | https://github.com/mpdavis/python-jose |
| passlib | BSD-3-Clause | https://foss.heptapod.net/python-libs/passlib |
| psutil | BSD-3-Clause | https://github.com/giampaolo/psutil |
| httpx | BSD-3-Clause | https://github.com/encode/httpx |
| python-telegram-bot | LGPL-3.0 | https://github.com/python-telegram-bot/python-telegram-bot |
| APScheduler | MIT | https://github.com/agronholm/apscheduler |
| python-dotenv | BSD-3-Clause | https://github.com/theskumar/python-dotenv |

## Frontend (JavaScript/TypeScript)

| Komponente | Lizenz | Projekt |
|---|---|---|
| React / React-DOM | MIT | https://github.com/facebook/react |
| React Router | MIT | https://github.com/remix-run/react-router |
| Recharts | MIT | https://github.com/recharts/recharts |
| Axios | MIT | https://github.com/axios/axios |
| Vite | MIT | https://github.com/vitejs/vite |
| Tailwind CSS | MIT | https://github.com/tailwindlabs/tailwindcss |
| TypeScript | Apache-2.0 | https://github.com/microsoft/TypeScript |

## Infrastruktur

| Komponente | Lizenz | Projekt |
|---|---|---|
| PostgreSQL | PostgreSQL License (freizuegige, BSD-/MIT-aehnliche Lizenz) | https://www.postgresql.org/about/licence/ |
| Nginx | BSD-2-Clause | https://nginx.org/ |
| Docker / Docker Compose | Apache-2.0 | https://www.docker.com/ |

## Bitcoin SV Node (separates Teilprojekt `node/`)

| Komponente | Lizenz | Hinweis |
|---|---|---|
| Bitcoin SV (bitcoind) | **Open BSV License** (keine MIT/BSD-Lizenz!) | Die Open BSV License gestattet Nutzung, Kopie und Modifikation, **solange die Software zur Interaktion mit der Bitcoin-SV-Blockchain (BSV) verwendet wird**. Volltext: https://github.com/bitcoin-sv/bitcoin-sv/blob/master/LICENSE |
| Berkeley DB 4.8 | Sleepycat License | Wird ausschliesslich fuer die Legacy-Wallet-Funktion aus dem Quellcode gebaut, siehe `node/Dockerfile` |
| Boost | Boost Software License 1.0 | https://www.boost.org/ |
| OpenSSL | Apache-2.0 (ab Version 3.x) | https://www.openssl.org/ |
| libevent | BSD-3-Clause | https://libevent.org/ |
| ZeroMQ (libzmq) | LGPL-3.0 (mit statischer Linking-Ausnahme) | https://zeromq.org/ |
| miniupnpc | BSD-3-Clause | http://miniupnp.free.fr/ |

## Hinweis zu Copyleft-Komponenten (LGPL)

psycopg2-binary, python-telegram-bot und libzmq stehen unter der LGPL-3.0.
Diese Bibliotheken werden unveraendert und nur dynamisch eingebunden
verwendet; es wurden keine Modifikationen an ihrem Quellcode vorgenommen.
Bei eigener Weiterverteilung im Binaerformat (z.B. Docker-Images) empfiehlt
es sich, auf den jeweiligen Quellcode der verwendeten Version zu verlinken.

## Icons/Design

Das Anwendungs-Icon ("BSV Node" / "DeepDance") wurde eigens fuer dieses
Projekt erstellt (© DeepDance, MIT-Lizenz, Teil dieses Repositories unter
`assets/icon.svg` und `icon.png`).
