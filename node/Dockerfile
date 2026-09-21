# ============================================================
# Bitcoin SV Full Node - sauberer arm64-Build aus dem Quellcode
# Fuer Raspberry Pi 5 (Cortex-A76, 64-bit) und 5tratumOS.
# Autor/Eigentuemer: DeepDance | Lizenz dieses Dockerfiles: MIT
# Bitcoin SV selbst unterliegt der Open BSV License (siehe
# THIRD_PARTY_LICENSES.md im Hauptprojekt).
#
# WICHTIG: Dieses Image wird bewusst NATIV auf arm64 gebaut
# (kein QEMU-Cross-Build noetig, wenn direkt auf dem Pi 5 oder via
# "docker buildx build --platform linux/arm64" auf einem arm64-Runner
# gebaut wird). Cross-Kompilation unter QEMU ist ein haeufiger Grund
# dafuer, dass BSV-Node-Builds auf dem Pi fehlschlagen oder ewig dauern.
# ============================================================

ARG BSV_VERSION=1.2.0
ARG UBUNTU_VERSION=22.04

# ---------- Stage 1: Build ----------
FROM ubuntu:${UBUNTU_VERSION} AS builder
ARG BSV_VERSION
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libtool autotools-dev automake pkg-config bsdmainutils \
    python3 git curl ca-certificates \
    libssl-dev libevent-dev \
    libboost-system-dev libboost-filesystem-dev libboost-chrono-dev \
    libboost-test-dev libboost-thread-dev \
    libminiupnpc-dev libzmq3-dev \
    libdb5.3++-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Bitcoin SV Quellcode (offizielles Repository, per Tag gepinnt)
RUN git clone --branch v${BSV_VERSION} --depth 1 \
    https://github.com/bitcoin-sv/bitcoin-sv.git bitcoin-sv

# Berkeley DB: BSV verlangt laut eigener Dokumentation "5.3 oder neuer" (nicht
# zwingend die alte 4.8er-Version wie beim originalen Bitcoin Core) - deshalb
# reicht das fertige Ubuntu-Systempaket libdb5.3++-dev (oben installiert),
# ganz ohne fehleranfaelliges manuelles Kompilieren einer alten BDB-Version.
# --with-incompatible-bdb erlaubt ausdruecklich eine von 4.8 abweichende
# BDB-Version (unproblematisch, da hier ohnehin neue Wallets angelegt werden).
RUN cd bitcoin-sv && \
    ./autogen.sh && \
    ./configure \
      --with-incompatible-bdb \
      --disable-tests \
      --disable-bench \
      --without-gui \
      --with-miniupnpc \
      --enable-zmq \
      --prefix=/opt/bitcoin-sv && \
    make -j"$(nproc)" && \
    make install

# ---------- Stage 2: Runtime ----------
FROM ubuntu:${UBUNTU_VERSION} AS runtime
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl3 libevent-2.1-7 libevent-pthreads-2.1-7 \
    libboost-system1.74.0 libboost-filesystem1.74.0 libboost-chrono1.74.0 \
    libboost-thread1.74.0 libminiupnpc17 libzmq5 \
    libdb5.3++ \
    tini curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/bitcoin-sv /opt/bitcoin-sv
ENV PATH="/opt/bitcoin-sv/bin:${PATH}"

RUN useradd -r -m -d /data -s /usr/sbin/nologin bsv
VOLUME ["/data"]

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
COPY bitcoin.conf.template /opt/bitcoin-sv/bitcoin.conf.template
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

USER bsv
WORKDIR /data

EXPOSE 8333 8332 28332

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD bitcoin-cli -datadir=/data getblockchaininfo >/dev/null 2>&1 || exit 1

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/docker-entrypoint.sh"]
CMD ["bitcoind"]
