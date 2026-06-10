"""
Trade Logger — registra OGNI trade chiuso su Firestore con TUTTO il contesto
necessario al learning loop per segmentare la performance.
"""
from __future__ import annotations

from typing import Optional

from bot.core.firebase_client import get_firebase
from bot.core.models import ClosedTrade


class TradeLogger:
    COLLECTION = "trades"

    def __init__(self, firebase=None) -> None:
        self.fb = firebase or get_firebase()

    def log(self, trade: ClosedTrade) -> None:
        """Salva il trade chiuso. La chiave è trade_id (idempotente)."""
        data = trade.model_dump(mode="json")
        # campi derivati utili alle query/aggregazioni del learning
        data["duration_seconds"] = trade.duration_seconds
        data["hour_bucket"] = trade.hour_bucket
        data["is_win"] = trade.is_win
        # timestamp ordinabile per le query "ultimi N trade"
        data["exit_ts"] = trade.exit_time.timestamp()
        self.fb.set_doc(self.COLLECTION, trade.trade_id, data)

    def recent(self, limit: int = 20) -> list[dict]:
        """Ultimi N trade per il prompt dell'orchestratore."""
        return self.fb.query_collection(self.COLLECTION, order_by="exit_ts", limit=limit)

    def all_since(self, since_ts: float) -> list[dict]:
        """Tutti i trade con exit dopo `since_ts` (per il learning loop)."""
        docs = self.fb.query_collection(self.COLLECTION, order_by="exit_ts")
        return [d for d in docs if d.get("exit_ts", 0) >= since_ts]
