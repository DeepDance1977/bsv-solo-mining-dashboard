"""
Minimaler JSON-RPC Client fuer eine Bitcoin SV Full Node (bitcoind-kompatibel).
Nutzt httpx, keine externen Node-Bibliotheken noetig.
"""
import time
import httpx

from app.config import get_settings

settings = get_settings()


class BsvRpcError(Exception):
    pass


class BsvRpcClient:
    def __init__(self):
        self._url = f"http://{settings.BSV_RPC_HOST}:{settings.BSV_RPC_PORT}/"
        self._auth = (settings.BSV_RPC_USER, settings.BSV_RPC_PASSWORD)
        self._timeout = settings.BSV_RPC_TIMEOUT
        self._start_time = time.time()

    def _call(self, method: str, params: list | None = None, wallet: str | None = None):
        url = self._url
        if wallet:
            url = f"{self._url}wallet/{wallet}"
        payload = {"jsonrpc": "1.0", "id": "bsv-dashboard", "method": method, "params": params or []}
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.post(url, json=payload, auth=self._auth)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as exc:
            raise BsvRpcError(f"HTTP-Fehler beim RPC-Aufruf '{method}': {exc}") from exc
        except httpx.RequestError as exc:
            raise BsvRpcError(f"Node nicht erreichbar ({method}): {exc}") from exc

        if data.get("error"):
            raise BsvRpcError(f"RPC-Fehler bei '{method}': {data['error']}")
        return data["result"]

    # ---- Node Status ----
    def get_blockchain_info(self) -> dict:
        return self._call("getblockchaininfo")

    def get_network_info(self) -> dict:
        return self._call("getnetworkinfo")

    def get_peer_info(self) -> list:
        return self._call("getpeerinfo")

    def get_mining_info(self) -> dict:
        return self._call("getmininginfo")

    def uptime(self) -> int:
        return self._call("uptime")

    # ---- Wallet ----
    def get_new_address(self, label: str = "dashboard") -> str:
        return self._call("getnewaddress", [label], wallet=settings.WALLET_NAME or None)

    def get_receiving_address(self) -> str:
        """Liefert eine vorhandene oder neue Empfangsadresse."""
        addrs = self._call(
            "listreceivedbyaddress", [0, True], wallet=settings.WALLET_NAME or None
        )
        if addrs:
            return addrs[0]["address"]
        return self.get_new_address()

    def get_balance(self) -> float:
        return self._call("getbalance", [], wallet=settings.WALLET_NAME or None)

    def get_unconfirmed_balance(self) -> float:
        return self._call("getunconfirmedbalance", [], wallet=settings.WALLET_NAME or None)

    def list_transactions(self, count: int = 20) -> list:
        return self._call(
            "listtransactions", ["*", count, 0, True], wallet=settings.WALLET_NAME or None
        )


bsv_rpc = BsvRpcClient()
