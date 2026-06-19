"""
Client Firebase con DEGRADAZIONE GRACEFUL.

Se `FIREBASE_SERVICE_ACCOUNT` non è configurato (es. in test o in un primo
paper trading locale) il client cade su uno store IN-MEMORY, così tutto il
resto del sistema funziona comunque. In produzione (VPS / GitHub Actions) usa
Firestore + Realtime DB reali.

Schema (vedi docs/firebase_schema.md):
  Firestore:
    trades/{trade_id}                  -> ClosedTrade
    memory/{lookback}                  -> MemoryReport (es. memory/30)
    strategy_weights/current           -> {weights: [...]}
    user_risk_settings/current         -> RiskSettings
    insights/{week_id}                 -> insight settimanale (RAG long-term)
  Realtime DB:
    /positions/{symbol}                -> stato posizione live
    /bot_status                        -> {state, regime, equity, updated_at}
    /commands/kill_switch              -> bool (dashboard -> bot)
"""
from __future__ import annotations

import json
import os
import threading
from typing import Any, Optional

from bot.config import settings


def encode_pairs(pairs: dict) -> str:
    """Serializza la mappa `pairs` del registro come stringa JSON: Firestore la
    indicizza come UN singolo campo invece di indicizzare ogni sottocampo di ogni
    coppia (che con centinaia di strategie supera il limite di 40k voci d'indice)."""
    return json.dumps(pairs or {})


def decode_pairs(value) -> dict:
    """Legge `pairs` sia come stringa JSON (nuovo formato) sia come mappa (vecchio)."""
    if isinstance(value, str):
        try:
            return json.loads(value) or {}
        except Exception:  # noqa: BLE001
            return {}
    return value or {}


def resolve_service_account(raw: str) -> Optional[dict]:
    """
    Accetta il service account Firebase in DUE forme:
      * JSON inline (la stringa intera, es. dai GitHub Secrets)
      * un PERCORSO a un file .json (più comodo sulla VPS)
    Ritorna il dict, o None se vuoto/non valido.
    """
    raw = (raw or "").strip()
    if not raw:
        return None
    if raw.startswith("{"):
        return json.loads(raw)
    if os.path.exists(raw):
        with open(raw, "r", encoding="utf-8") as f:
            return json.load(f)
    # ultimo tentativo: provalo come JSON comunque (solleva se non lo è)
    return json.loads(raw)



class _InMemoryStore:
    """Fallback thread-safe quando Firebase non è configurato."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._docs: dict[str, dict[str, Any]] = {}
        self._rtdb: dict[str, Any] = {}

    # Firestore-like
    def set_doc(self, collection: str, doc_id: str, data: dict) -> None:
        with self._lock:
            self._docs[f"{collection}/{doc_id}"] = data

    def get_doc(self, collection: str, doc_id: str) -> Optional[dict]:
        with self._lock:
            return self._docs.get(f"{collection}/{doc_id}")

    def query_collection(self, collection: str) -> list[dict]:
        with self._lock:
            prefix = f"{collection}/"
            return [v for k, v in self._docs.items() if k.startswith(prefix)]

    # RTDB-like
    def set_rtdb(self, path: str, data: Any) -> None:
        with self._lock:
            if data is None:
                # come il RTDB vero: scrivere None = cancellare il nodo
                self._rtdb.pop(path, None)
            else:
                self._rtdb[path] = data

    def get_rtdb(self, path: str) -> Any:
        with self._lock:
            if path in self._rtdb:
                return self._rtdb[path]
            # emula la gerarchia RTDB: leggere un nodo padre ritorna i figli
            # diretti come dict (es. /positions -> {BTCUSDT: {...}, ...}).
            prefix = path.rstrip("/") + "/"
            children: dict[str, Any] = {}
            for k, v in self._rtdb.items():
                if k.startswith(prefix) and v is not None:
                    child = k[len(prefix):].split("/", 1)[0]
                    children[child] = v
            return children or None


class FirebaseClient:
    """Interfaccia unica usata da tutto il bot."""

    def __init__(self) -> None:
        self._memory = _InMemoryStore()
        self._fs = None   # firestore client
        self._db = None   # realtime db module
        self._live = False
        self._init_firebase()

    def _init_firebase(self) -> None:
        if not settings.FIREBASE_SERVICE_ACCOUNT:
            print("[firebase] FIREBASE_SERVICE_ACCOUNT non impostato -> store IN-MEMORY")
            return
        try:
            import firebase_admin
            from firebase_admin import credentials, db, firestore

            cred_dict = resolve_service_account(settings.FIREBASE_SERVICE_ACCOUNT)
            cred = credentials.Certificate(cred_dict)
            opts = {}
            if settings.FIREBASE_RTDB_URL:
                opts["databaseURL"] = settings.FIREBASE_RTDB_URL
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred, opts)
            self._fs = firestore.client()
            self._db = db
            self._live = True
            print("[firebase] connesso (Firestore + RTDB)")
        except Exception as exc:  # noqa: BLE001
            print(f"[firebase] init fallito ({exc}) -> store IN-MEMORY")
            self._live = False

    @property
    def is_live(self) -> bool:
        return self._live

    # ---- Firestore ----
    def set_doc(self, collection: str, doc_id: str, data: dict) -> None:
        if self._live:
            self._fs.collection(collection).document(doc_id).set(data)
        else:
            self._memory.set_doc(collection, doc_id, data)

    def get_doc(self, collection: str, doc_id: str) -> Optional[dict]:
        if self._live:
            snap = self._fs.collection(collection).document(doc_id).get()
            return snap.to_dict() if snap.exists else None
        return self._memory.get_doc(collection, doc_id)

    def query_collection(
        self, collection: str, order_by: Optional[str] = None, limit: Optional[int] = None
    ) -> list[dict]:
        if self._live:
            q = self._fs.collection(collection)
            if order_by:
                q = q.order_by(order_by, direction="DESCENDING")
            if limit:
                q = q.limit(limit)
            return [d.to_dict() for d in q.stream()]
        docs = self._memory.query_collection(collection)
        if order_by:
            docs = sorted(docs, key=lambda d: d.get(order_by, 0), reverse=True)
        if limit:
            docs = docs[:limit]
        return docs

    def list_doc_ids(self, collection: str) -> list[str]:
        if self._live:
            return [d.id for d in self._fs.collection(collection).stream()]
        prefix = f"{collection}/"
        return [k[len(prefix):] for k in self._memory._docs if k.startswith(prefix)]

    def delete_doc(self, collection: str, doc_id: str) -> None:
        if self._live:
            self._fs.collection(collection).document(doc_id).delete()
        else:
            self._memory._docs.pop(f"{collection}/{doc_id}", None)

    # ---- Realtime DB (stato live) ----
    def set_rtdb(self, path: str, data: Any) -> None:
        if self._live and self._db is not None:
            # ATTENZIONE: il RTDB lancia "Value must not be None" se passi None
            # a .set(). Per cancellare un nodo (es. posizione chiusa) si usa
            # .delete(). Senza questo, la chiusura di una posizione crashava e il
            # trade non veniva mai loggato.
            ref = self._db.reference(path)
            if data is None:
                ref.delete()
            else:
                ref.set(data)
        else:
            self._memory.set_rtdb(path, data)

    def get_rtdb(self, path: str) -> Any:
        if self._live and self._db is not None:
            return self._db.reference(path).get()
        return self._memory.get_rtdb(path)


_client: Optional[FirebaseClient] = None


def get_firebase() -> FirebaseClient:
    """Singleton lazy."""
    global _client
    if _client is None:
        _client = FirebaseClient()
    return _client
