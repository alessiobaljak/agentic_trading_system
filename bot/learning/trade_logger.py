"""
Trade Logger — registra OGNI trade chiuso su Firestore con TUTTO il contesto
necessario al learning loop per segmentare la performance, e tiene i trade
chiusi IN MEMORIA per chi li rilegge.

LA CACHE (28 set 2026). Il 28 settembre la quota gratuita di Firestore (50.000
letture al giorno) si e' esaurita alle 06:18 UTC. Il bot rileggeva i trade da
Firestore a ogni candela (`recent(100)` per i verdetti: ~9.600 letture al
giorno), dopo ogni chiusura e ogni ora (`all_since` 30 giorni per i pesi:
~8.200), ogni ora per il controllo (tutti i trade: ~3.600) e a ogni decisione
per il tetto per coin. Ma i trade li scrive SOLO il bot: rileggerli era pagare
per sapere cio' che aveva appena scritto.

Da qui: `all_since` e `recent` rispondono dalla cache. La cache si carica
intera al primo uso (N letture, una volta), poi:
  * `log` e `aggiorna` (le due scritture del bot) aggiornano la cache subito;
  * a ogni lettura, al massimo ogni `aggiorna_min_s` secondi, si chiede a
    Firestore SOLO i trade con `exit_ts >= ultimo visto` (1 lettura quando non
    c'e' niente di nuovo): e' la rete contro uno scrittore esterno;
  * una volta al giorno (`manutenzione`) si conta la collection con
    l'aggregazione del server (1 lettura) e la si ricarica per intero: se il
    conteggio non torna lo si dice (`[trades] cache disallineata`) e finisce
    nel controllo come `CACHE_TRADE_DISALLINEATA`.
Atteso: da ~20.000 letture al giorno per i trade a poche centinaia.
"""
from __future__ import annotations

import threading
import time
from typing import Optional

from bot.core.firebase_client import get_firebase, kw_chi
from bot.core.models import ClosedTrade

#: etichetta nel contatore delle letture
CHI = "trade"
#: al massimo ogni quanti secondi una lettura chiede a Firestore i trade nuovi
AGGIORNA_MIN_S = 300.0
#: ogni quanto la cache si ricarica per intero e si verifica col conteggio
RICARICA_S = 86400.0


class TradeLogger:
    COLLECTION = "trades"

    def __init__(self, firebase=None) -> None:
        self.fb = firebase or get_firebase()
        self._lock = threading.RLock()
        self._cache: Optional[dict[str, dict]] = None     # trade_id -> documento
        self._ordinati: Optional[list[dict]] = None        # per exit_ts decrescente
        self._ultimo_exit_ts = 0.0
        self._caricata_at = 0.0
        self._aggiornata_at = 0.0
        self.aggiorna_min_s = AGGIORNA_MIN_S
        #: l'esito dell'ultima verifica giornaliera: {firestore, cache, allineata,
        #: verificata_at, ricaricata}; None finche' non e' mai girata
        self.ultima_verifica: Optional[dict] = None

    # ------------------------------------------------------------------ #
    # scritture: aggiornano anche la cache                                #
    # ------------------------------------------------------------------ #
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
        self._metti(data)

    def aggiorna(self, doc: dict) -> None:
        """Riscrive un trade gia' loggato (i verdetti trailing/post-stop che
        `evaluate_pending_trailing` aggiunge sul posto) e allinea la cache."""
        self.fb.set_doc(self.COLLECTION, doc["trade_id"], doc)
        self._metti(doc)

    def _metti(self, doc: dict) -> None:
        with self._lock:
            if self._cache is None:
                return            # non ancora caricata: la prima lettura la carichera'
            self._cache[str(doc.get("trade_id"))] = doc
            self._ordinati = None
            try:
                self._ultimo_exit_ts = max(self._ultimo_exit_ts, float(doc.get("exit_ts") or 0))
            except (TypeError, ValueError):
                pass

    # ------------------------------------------------------------------ #
    # letture: dalla cache                                                #
    # ------------------------------------------------------------------ #
    def recent(self, limit: int = 20) -> list[dict]:
        """Ultimi N trade per exit_ts (per i verdetti, il prompt, il tetto per coin)."""
        with self._lock:
            self._pronta()
            return list(self._lista()[:limit])

    def all_since(self, since_ts: float) -> list[dict]:
        """Tutti i trade con exit dopo `since_ts` (learning loop, pesi, controllo)."""
        with self._lock:
            self._pronta()
            return [t for t in self._lista() if _exit(t) >= since_ts]

    @property
    def n_cache(self) -> Optional[int]:
        """Quanti trade ha la cache; None se non e' mai stata caricata."""
        with self._lock:
            return None if self._cache is None else len(self._cache)

    def _lista(self) -> list[dict]:
        if self._ordinati is None:
            self._ordinati = sorted((self._cache or {}).values(), key=_exit, reverse=True)
        return self._ordinati

    def _pronta(self, now: Optional[float] = None) -> None:
        """Carica la cache se manca, altrimenti la aggiorna coi soli trade nuovi
        (al massimo ogni `aggiorna_min_s`)."""
        now = time.time() if now is None else now
        if self._cache is None:
            self.ricarica(now)
            return
        if now - self._aggiornata_at < self.aggiorna_min_s:
            return
        self._aggiornata_at = now
        nuovi = self.fb.query_collection(self.COLLECTION, order_by="exit_ts",
                                         min_value=self._ultimo_exit_ts, **kw_chi(self.fb, CHI))
        for d in nuovi or []:
            if isinstance(d, dict) and d.get("trade_id") is not None:
                self._cache[str(d["trade_id"])] = d
                self._ultimo_exit_ts = max(self._ultimo_exit_ts, _exit(d))
        if nuovi:
            self._ordinati = None

    def ricarica(self, now: Optional[float] = None) -> int:
        """Ricarica la cache per intero da Firestore (N letture). Ritorna N."""
        now = time.time() if now is None else now
        with self._lock:
            docs = self.fb.query_collection(self.COLLECTION, order_by="exit_ts",
                                            **kw_chi(self.fb, CHI)) or []
            self._cache = {str(d["trade_id"]): d for d in docs
                           if isinstance(d, dict) and d.get("trade_id") is not None}
            self._ordinati = None
            self._ultimo_exit_ts = max((_exit(d) for d in self._cache.values()), default=0.0)
            self._caricata_at = now
            self._aggiornata_at = now
            return len(self._cache)

    # ------------------------------------------------------------------ #
    # la verifica giornaliera                                             #
    # ------------------------------------------------------------------ #
    def verifica(self, now: Optional[float] = None) -> dict:
        """Conta i documenti su Firestore (aggregazione: 1 lettura) e li confronta
        con la cache; se non tornano, ricarica e lo stampa. Ritorna e conserva
        {firestore, cache, allineata, verificata_at, ricaricata}."""
        now = time.time() if now is None else now
        with self._lock:
            self._pronta(now)
            in_cache = len(self._cache or {})
            conta = getattr(self.fb, "count_collection", None)
            if callable(conta):
                su_fs = int(conta(self.COLLECTION, **kw_chi(self.fb, CHI)))
            else:                       # client finto senza aggregazione: si conta a mano
                su_fs = len(self.fb.query_collection(self.COLLECTION) or [])
            allineata = su_fs == in_cache
            ricaricata = False
            if not allineata:
                self.ricarica(now)
                ricaricata = True
                print(f"[trades] cache disallineata: {su_fs} su Firestore vs {in_cache} "
                      f"in cache, ricaricata ({len(self._cache or {})})")
            self.ultima_verifica = {"firestore": su_fs, "cache": in_cache, "allineata": allineata,
                                    "verificata_at": float(now), "ricaricata": ricaricata}
            return dict(self.ultima_verifica)

    def manutenzione(self, now: Optional[float] = None) -> Optional[dict]:
        """Da chiamare dal ramo orario del bot: una volta al giorno verifica il
        conteggio e ricarica per intero (rete contro modifiche esterne ai
        documenti, che la lettura incrementale per exit_ts non vede). Ritorna
        l'esito della verifica quando gira, None altrimenti. Non solleva."""
        now = time.time() if now is None else now
        try:
            with self._lock:
                if self._cache is not None and now - self._caricata_at < RICARICA_S:
                    return None
                # una cache mai caricata la carica `verifica` stessa: non due volte
                appena_caricata = self._cache is None
                esito = self.verifica(now)
                if not esito["ricaricata"] and not appena_caricata:
                    self.ricarica(now)
                return esito
        except Exception as exc:  # noqa: BLE001
            print(f"[trades] manutenzione della cache saltata ({exc})")
            return None


def _exit(t: dict) -> float:
    try:
        return float(t.get("exit_ts") or 0)
    except (TypeError, ValueError, AttributeError):
        return 0.0
