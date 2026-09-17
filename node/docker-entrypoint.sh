#!/usr/bin/env bash
# Ersetzt Platzhalter in der Konfigurationsvorlage anhand von Umgebungs-
# variablen und startet anschliessend bitcoind mit persistentem Datadir.
set -euo pipefail

RPC_USER="${RPC_USER:-rpcuser}"
RPC_PASSWORD="${RPC_PASSWORD:-please-change-me}"
RPC_ALLOW_IP="${RPC_ALLOW_IP:-172.16.0.0/12}"
NETWORK="${NETWORK:-mainnet}"

CONF_FILE="/data/bitcoin.conf"

if [ ! -f "$CONF_FILE" ]; then
  sed \
    -e "s|__RPC_USER__|${RPC_USER}|g" \
    -e "s|__RPC_PASSWORD__|${RPC_PASSWORD}|g" \
    -e "s|__RPC_ALLOW_IP__|${RPC_ALLOW_IP}|g" \
    /opt/bitcoin-sv/bitcoin.conf.template > "$CONF_FILE"

  if [ "$NETWORK" = "testnet" ]; then
    echo "testnet=1" >> "$CONF_FILE"
  fi
  echo "[entrypoint] Neue bitcoin.conf unter $CONF_FILE erstellt."
else
  echo "[entrypoint] Bestehende bitcoin.conf gefunden, wird unveraendert verwendet."
fi

exec bitcoind -datadir=/data -conf="$CONF_FILE"
