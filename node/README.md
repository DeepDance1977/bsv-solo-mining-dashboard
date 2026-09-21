# Bitcoin SV Full Node – arm64 Docker-Image (DeepDance)

Sauberer, aus dem offiziellen Quellcode gebauter Bitcoin-SV-Node fuer
**64-bit ARM** (Raspberry Pi 5 / 5tratumOS). Kein amd64-Image, keine
QEMU-Emulation – dadurch deutlich zuverlaessiger als generische
Cross-Build-Setups.

## Build

```bash
docker buildx build --platform linux/arm64 -t bsv-full-node:1.2.0 .
```

Am besten **direkt auf dem Raspberry Pi 5** bauen (native Kompilierung),
nicht per QEMU auf einem x86-Rechner – das ist die haeufigste Ursache fuer
fehlschlagende oder unvollstaendige BSV-Builds auf ARM.

## Bekannte Stolpersteine (und wie dieses Image sie vermeidet)

| Problem | Ursache | Loesung in diesem Image |
|---|---|---|
| `db_cxx.h: No such file or directory` | Ubuntu liefert `libdb4.8-dev` nicht mehr aus | BSV verlangt laut eigener Doku nur "BerkeleyDB 5.3 oder neuer" - das fertige Ubuntu-Paket `libdb5.3++-dev` reicht, kein manuelles Kompilieren noetig (`--with-incompatible-bdb` beim Konfigurieren) |
| Build haengt / OOM-Kill waehrend `make` | Zu wenig RAM/Swap auf dem Pi | Mit 8&nbsp;GB RAM unkritisch; bei kleineren Pi-Modellen vorher Swap auf mind. 2&nbsp;GB erhoehen |
| `configure: error: boost not found` | Falsche/fehlende Boost-Pakete | Alle benoetigten `libboost-*-dev`-Pakete werden explizit installiert |
| Falsches Zielsystem / Segfault beim Start | Cross-Kompilat fuer amd64 auf arm64 ausgefuehrt (oder umgekehrt) | Natives `ubuntu:22.04`-Basisimage, kein Cross-Compile-Toolchain |
| RPC nicht erreichbar | `rpcallowip` zu restriktiv oder `rpcbind` fehlt | Werden ueber Umgebungsvariablen gesetzt, Standard erlaubt private Netze |

## Wichtige Umgebungsvariablen

| Variable | Standard | Beschreibung |
|---|---|---|
| `RPC_USER` | `rpcuser` | RPC-Benutzername |
| `RPC_PASSWORD` | *(muss gesetzt werden)* | RPC-Passwort |
| `RPC_ALLOW_IP` | `172.16.0.0/12` | Erlaubtes Subnetz fuer RPC-Zugriff (z.B. Docker-Netzwerk) |
| `NETWORK` | `mainnet` | `mainnet` oder `testnet` |

## Speicherbedarf

Die BSV-Blockchain (Mainnet, vollstaendig, `txindex=1`) benoetigt aktuell
mehrere hundert GB und waechst kontinuierlich. Fuer den produktiven Betrieb
wird eine externe SSD (USB 3.0 / NVMe-Hat) statt einer microSD-Karte dringend
empfohlen – microSD-Karten sind fuer die dauerhafte I/O-Last eines Full Nodes
zu langsam und verschleissanfaellig.

## Lizenzhinweis

Bitcoin SV selbst steht unter der **Open BSV License** (nicht MIT/BSD) –
siehe `THIRD_PARTY_LICENSES.md` im Hauptprojekt fuer Details und
Nutzungsbedingungen. Dieses Dockerfile/Entrypoint-Skript steht unter der
MIT-Lizenz von DeepDance.
