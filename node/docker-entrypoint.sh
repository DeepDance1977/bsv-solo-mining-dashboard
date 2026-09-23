#!/usr/bin/env bash
# Wird als root gestartet (siehe Dockerfile), korrigiert einmalig die
# Zugriffsrechte auf den vom Host bereitgestellten Datenordner (der bei
# Docker-Bind-Mounts standardmaessig root gehoert) und wechselt danach zum
# unprivilegierten Benutzer "bsv", bevor bitcoind tatsaechlich ausgefuehrt
# wird. Ohne diesen Schritt schlaegt der Schreibzugriff auf /data mit
# "Permission denied" fehl.
set -euo pipefail

RPC_USER="${RPC_USER:-rpcuser}"
RPC_PASSWORD="${RPC_PASSWORD:-please-change-me}"
RPC_ALLOW_IP="${RPC_ALLOW_IP:-172.16.0.0/12}"
NETWORK="${NETWORK:-mainnet}"
PRUNE_SIZE_MB="${PRUNE_SIZE_MB:-5000}"

CONF_FILE="/data/bitcoin.conf"

# Zugriffsrechte auf das (evtl. vom Host als root angelegte) Datenverzeichnis
# korrigieren, damit der Benutzer "bsv" hineinschreiben darf.
chown -R bsv:bsv /data

if [ ! -f "$CONF_FILE" ]; then
  sed \
    -e "s|__RPC_USER__|${RPC_USER}|g" \
    -e "s|__RPC_PASSWORD__|${RPC_PASSWORD}|g" \
    -e "s|__RPC_ALLOW_IP__|${RPC_ALLOW_IP}|g" \
    -e "s|__PRUNE_SIZE_MB__|${PRUNE_SIZE_MB}|g" \
    /opt/bitcoin-sv/bitcoin.conf.template > "$CONF_FILE"

  if [ "$NETWORK" = "testnet" ]; then
    echo "testnet=1" >> "$CONF_FILE"
  fi
  chown bsv:bsv "$CONF_FILE"
  echo "[entrypoint] Neue bitcoin.conf unter $CONF_FILE erstellt."
else
  echo "[entrypoint] Bestehende bitcoin.conf gefunden, wird unveraendert verwendet."
fi

exec runuser -u bsv -- bitcoind -datadir=/data -conf="$CONF_FILE"
