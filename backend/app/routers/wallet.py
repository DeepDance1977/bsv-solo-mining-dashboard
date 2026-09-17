"""
Wallet-Endpunkte: Empfangsadresse, Guthaben, letzte Transaktionen, Mining-Belohnungen.
"""
from datetime import datetime

from fastapi import APIRouter, Depends
from app.schemas import WalletInfo, TransactionOut
from app.services.bsv_rpc import bsv_rpc, BsvRpcError
from app.deps import require_viewer

router = APIRouter(prefix="/api/wallet", tags=["wallet"], dependencies=[Depends(require_viewer)])


@router.get("", response_model=WalletInfo)
def get_wallet_info():
    try:
        address = bsv_rpc.get_receiving_address()
        balance = bsv_rpc.get_balance()
        unconfirmed = bsv_rpc.get_unconfirmed_balance()
        raw_txs = bsv_rpc.list_transactions(30)
    except BsvRpcError:
        return WalletInfo(address=None, balance=0.0, unconfirmed_balance=0.0,
                           transactions=[], last_mining_rewards=[])

    transactions = []
    for tx in raw_txs:
        # "generate"/"immature" Kategorien kennzeichnen Coinbase- (Mining-) Ausgaben
        is_reward = tx.get("category") in ("generate", "immature")
        transactions.append(
            TransactionOut(
                txid=tx.get("txid", ""),
                category=tx.get("category", "unknown"),
                amount=tx.get("amount", 0.0),
                confirmations=tx.get("confirmations", 0),
                time=datetime.fromtimestamp(tx.get("time", 0)),
                is_mining_reward=is_reward,
            )
        )

    transactions.sort(key=lambda t: t.time, reverse=True)
    rewards = [t for t in transactions if t.is_mining_reward][:10]

    return WalletInfo(
        address=address,
        balance=balance,
        unconfirmed_balance=unconfirmed,
        transactions=transactions[:20],
        last_mining_rewards=rewards,
    )
