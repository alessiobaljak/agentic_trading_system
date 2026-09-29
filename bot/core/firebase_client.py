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
    ai_spesa/{YYYY-MM-DD}              -> token AI del giorno italiano, per ragione
                                          (bot/ai/spesa.py, scritto con `incrementa`)
  Realtime DB:
    /positions/{symbol}                -> stato posizione live
    /bot_status                        -> {state, regime, equity, updated_at}
    /commands/kill_switch              -> bool (dashboard -> bot)
"""
from __future__ import annotations

import copy
import json
import os
import sys
import threading
import time
from typing import Any, Optional

from bot.config import settings


def encode_pairs(pairs: dict) -> str:
    """Serializza la mappa `pairs` del registro come stringa JSON: Firestore la
    indicizza come UN singolo campo invece di indicizzare ogni sottocampo di ogni
    coppia (che con centinaia di strategie supera il limite di 40k voci d'indice)."""
    return json.dumps(pairs or {})


# --------------------------------------------------------------------------- #
# FORMATO COMPATTO DEL REGISTRO                                                #
# --------------------------------------------------------------------------- #
# Il registro e' UN SOLO documento Firestore e il limite e' 1 MiB. Il 19 settembre
# era a 759 KiB su 900.000 byte (86%) e cresceva di ~37 KiB al giorno: tre giorni
# al muro. Superato il limite Firestore RIFIUTA la scrittura, e quel run perde le
# conferme appena guadagnate — cioe' settimane di attesa, in silenzio.
#
# La compressione vive TUTTA qui dentro. `decode_pairs` restituisce sempre i nomi
# lunghi, quindi nessun lettore (bot, learning, script, autopsia) cambia di una
# riga: se la compressione fosse sparsa nei chiamanti, il primo che se ne
# dimenticasse leggerebbe un registro vuoto invece di dare errore.
#
# Tre risparmi, tutti senza perdita di informazione:
#   1. NOMI BREVI — `last_pass_data_end` diventa `d`. Le chiavi JSON si ripetono
#      identiche 2.600 volte: da sole erano meta' del documento.
#   2. SYMBOL E STRATEGY TOLTI — sono gia' dentro la chiave `COINUSDT|strategia`.
#      Si tolgono SOLO se combaciano con la chiave: un record incoerente si tiene
#      com'e', perche' qui un dubbio va risolto conservando, non indovinando.
#   3. TEMPI INTERI — `1758258123.456789` diventa `1758258123`. Al secondo: le
#      finestre del gate durano una settimana, i microsecondi non decidono nulla.
REGISTRY_FORMAT = 2

_BREVI = {
    "pass_count": "p", "last_pass_data_end": "d", "fail_count": "f",
    "last_seen_at": "v", "last_params": "m", "scale_r_mults": "r",
    "drift_seen_at": "x", "window_start": "w", "passed_in_window": "q",
    "generated": "g", "last_passed_at": "l",
    # QUANDO la coppia e' entrata fra le validate. Senza, la domanda «quanto vive
    # una strategia validata?» non ha risposta: il registro contiene solo i
    # sopravvissuti, e chi esce sparisce senza lasciare la sua eta'.
    "validated_at": "a",
    # i contatori della maggioranza della finestra (27 set 2026): su ~2.800
    # coppie i nomi lunghi costerebbero ~140 KB del documento
    "window_evals": "e", "window_passes": "s", "window_contata": "c",
}
_LUNGHI = {v: k for k, v in _BREVI.items()}
_TEMPI = {"last_seen_at", "last_passed_at", "window_start", "last_pass_data_end",
          "drift_seen_at", "validated_at", "sostituita_at", "intorno_at", "nata_intorno_at",
          # l'azzeramento per la sessione (27 set 2026, J13): un epoch come gli altri
          "sessione_azzerata_at"}


def encode_registry(pairs: dict) -> str:
    """La mappa del registro nel formato compatto, come stringa JSON."""
    compatte = {}
    for chiave, rec in (pairs or {}).items():
        if not isinstance(rec, dict):
            compatte[chiave] = rec
            continue
        sym, _, strat = str(chiave).partition("|")
        fuori = {}
        for campo, valore in rec.items():
            # ridondanti con la chiave: si tolgono solo se combaciano davvero
            if campo == "symbol" and valore == sym:
                continue
            if campo == "strategy" and valore == strat:
                continue
            if campo in _TEMPI and isinstance(valore, (int, float)):
                valore = int(valore)
            fuori[_BREVI.get(campo, campo)] = valore
        compatte[chiave] = fuori
    return json.dumps({"v": REGISTRY_FORMAT, "k": compatte})


def _espandi_registro(compatte: dict) -> dict:
    """Formato compatto -> nomi lunghi, con symbol/strategy ricostruiti dalla chiave."""
    fuori = {}
    for chiave, rec in (compatte or {}).items():
        if not isinstance(rec, dict):
            fuori[chiave] = rec
            continue
        lungo = {_LUNGHI.get(campo, campo): valore for campo, valore in rec.items()}
        sym, sep, strat = str(chiave).partition("|")
        if sep:
            lungo.setdefault("symbol", sym)
            lungo.setdefault("strategy", strat)
        fuori[chiave] = lungo
    return fuori


def decode_pairs(value) -> dict:
    """Legge `pairs` in TUTTI i formati mai scritti: mappa nuda (il piu' vecchio),
    stringa JSON coi nomi lunghi, e stringa JSON compatta.

    Ritorna SEMPRE i nomi lunghi. La retro-compatibilita' non e' cortesia: il
    registro vivo e' scritto nel formato vecchio finche' il primo run col codice
    nuovo non lo riscrive, e nel mezzo il bot deve continuare a operare."""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception:  # noqa: BLE001
            return {}
    if not isinstance(value, dict):
        return value or {}
    # una chiave di coppia e' sempre "SYMBOL|strategia", quindi "v"/"k" al primo
    # livello non possono essere coppie: il marcatore non e' ambiguo.
    if value.get("v") == REGISTRY_FORMAT and isinstance(value.get("k"), dict):
        return _espandi_registro(value["k"])
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



# --------------------------------------------------------------------------- #
# IL CONTATORE DELLE LETTURE (28 set 2026)                                     #
# --------------------------------------------------------------------------- #
# Il 28 settembre alle 06:18 UTC la quota gratuita di Firestore (50.000 letture
# al giorno) si e' esaurita: `mfe` e `frequenza` hanno risposto «429 Quota
# exceeded» (ops 0331, 0332). Dalla console: 8k letture il 20 set, 39k il 26,
# quota finita il 28. Le cause erano nel codice (verdetti a ogni candela su 100
# trade, pesi su tutti i trade dopo ogni chiusura, controllo orario che rilegge
# tutto, ombra dei rifiutati su una finestra di 17 giorni), ma NESSUNO le aveva
# misurate: la stima del 28 set era «dal codice, non misurata».
#
# Da qui il contatore: ogni `get_doc` vale 1, ogni `query_collection` vale i
# documenti tornati (almeno 1: anche una query vuota costa una lettura), e ogni
# lettura porta un'etichetta di chi l'ha chiesta (`chi=`; senza, il nome della
# funzione chiamante). L'anello per ora tiene le ultime 24 ore; il bot stampa
# il totale ogni ora e lo pubblica nel controllo (`salute.letture_firestore_24h`,
# anomalia `LETTURE_FIRESTORE`). Il Realtime DB NON si conta: e' un altro
# prodotto con un'altra quota.
#: la quota gratuita di Firestore (letture al giorno, si azzera alle 07:00 UTC)
QUOTA_LETTURE_GIORNO = 50_000
#: ore di anello tenute (24 + quella in corso)
_ORE_ANELLO = 25
#: quante etichette al massimo nel riepilogo
_TOP_CHIAMANTI = 8


def _chiamante(profondita: int = 2) -> str:
    """Il nome della funzione che ha chiesto la lettura (senza `inspect`: un
    frame e' abbastanza e costa nulla a questi volumi)."""
    try:
        return sys._getframe(profondita).f_code.co_name   # noqa: SLF001
    except Exception:  # noqa: BLE001
        return "?"


class ContatoreLetture:
    """Letture Firestore per ora e per chiamante. Thread-safe (il reconciler
    gira in un thread suo)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.totale = 0
        self._ore: dict[int, dict[str, int]] = {}    # ora (epoch // 3600) -> {chi: n}

    def conta(self, n: int, chi: str, now: Optional[float] = None) -> None:
        n = max(1, int(n))
        ora = int((time.time() if now is None else now) // 3600)
        with self._lock:
            self.totale += n
            per = self._ore.setdefault(ora, {})
            per[chi] = per.get(chi, 0) + n
            if len(self._ore) > _ORE_ANELLO:
                for vecchia in sorted(self._ore)[:len(self._ore) - _ORE_ANELLO]:
                    self._ore.pop(vecchia, None)

    def riepilogo(self, now: Optional[float] = None) -> dict:
        """{totale, ultime_24h, per_chiamante: [{chi, n}] (top 8 delle 24 h)}."""
        ora = int((time.time() if now is None else now) // 3600)
        with self._lock:
            recenti = {o: dict(v) for o, v in self._ore.items() if ora - 23 <= o <= ora}
            totale = self.totale
        per: dict[str, int] = {}
        for v in recenti.values():
            for chi, n in v.items():
                per[chi] = per.get(chi, 0) + n
        top = sorted(per.items(), key=lambda kv: (-kv[1], kv[0]))[:_TOP_CHIAMANTI]
        return {"totale": totale, "ultime_24h": sum(per.values()),
                "per_chiamante": [{"chi": chi, "n": n} for chi, n in top]}


def kw_chi(fb, chi: str) -> dict:
    """`{"chi": chi}` se `fb` e' un client che conta le letture, `{}` altrimenti:
    cosi' i chiamanti passano l'etichetta senza rompere i client finti dei test
    (che hanno `get_doc(coll, id)` senza parola chiave)."""
    return {"chi": chi} if hasattr(fb, "letture") else {}


def riga_letture(riepilogo: dict) -> str:
    """La riga di log oraria: `[firebase] letture ultime 24 h: N (registro X · ...)`."""
    parti = " · ".join(f"{r['chi']} {r['n']}" for r in (riepilogo.get("per_chiamante") or []))
    return (f"[firebase] letture ultime 24 h: {riepilogo.get('ultime_24h', 0)}"
            + (f" ({parti})" if parti else "")
            + f" — quota gratuita {QUOTA_LETTURE_GIORNO}/giorno")


def _solo_numeri(annidato: dict) -> dict:
    """Copia di `annidato` controllata per `incrementa`: chiavi stringhe non vuote
    (Firestore non accetta un nome di campo vuoto), foglie solo numeri (un
    booleano non e' una quantita' da sommare), sotto-dizionari vuoti tolti — su
    Firestore un `{}` scritto con merge AZZERA la mappa che c'era, cioe' cancellerebbe
    i conti del giorno invece di non toccarli."""
    fuori: dict = {}
    for k, v in (annidato or {}).items():
        if not isinstance(k, str) or not k:
            raise TypeError(f"incrementa: chiave non valida {k!r}")
        if isinstance(v, dict):
            dentro = _solo_numeri(v)
            if dentro:
                fuori[k] = dentro
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            fuori[k] = v
        else:
            raise TypeError(f"incrementa: {k}={v!r} non e' un numero (i valori da "
                            f"scrivere cosi' come sono vanno in `imposta`)")
    return fuori


def _somma_annidata(dest: dict, add: dict) -> None:
    """`dest += add` foglia per foglia. Come l'Increment di Firestore: una foglia
    che non c'era, o che non era un numero, riparte da zero."""
    for k, v in add.items():
        if isinstance(v, dict):
            sotto = dest.get(k)
            if not isinstance(sotto, dict):
                sotto = {}
                dest[k] = sotto
            _somma_annidata(sotto, v)
        else:
            prima = dest.get(k)
            if not isinstance(prima, (int, float)) or isinstance(prima, bool):
                prima = 0
            dest[k] = prima + v


def _fondi(dest: dict, src: dict) -> None:
    """Scrittura con merge, come `set(..., merge=True)`: le mappe si fondono, il
    resto si sovrascrive."""
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dest.get(k), dict):
            _fondi(dest[k], v)
        else:
            dest[k] = copy.deepcopy(v)


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

    def incrementa(self, collection: str, doc_id: str, annidato: dict,
                   imposta: Optional[dict] = None) -> None:
        """Somma annidata sotto lock (vedi `FirebaseClient.incrementa`). Si lavora
        su una copia e la si rimette al posto: chi ha letto il documento prima
        tiene la sua versione, come con Firestore."""
        with self._lock:
            chiave = f"{collection}/{doc_id}"
            doc = copy.deepcopy(self._docs.get(chiave) or {})
            _somma_annidata(doc, annidato)
            _fondi(doc, imposta or {})
            self._docs[chiave] = doc

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
    """Interfaccia unica usata da tutto il bot.

    DUE MODI DI NON AVERE FIREBASE, e vanno trattati diversamente.

      * NON CONFIGURATO (test, primo avvio locale): si parte direttamente sullo
        store in-memory. Tutto funziona, niente e' persistente, e si sa in
        partenza.
      * CONFIGURATO MA IRRAGGIUNGIBILE a meta' corsa (rete giu', quota finita,
        credenziali revocate): qui il client e' vivo e ogni chiamata SOLLEVA. Il
        Realtime DB e' sul percorso caldo del loop — stato, equity, comandi,
        heartbeat — quindi un'eccezione li' fermava il ciclo; e l'heartbeat sta
        in un `finally`, dove un'eccezione non e' intercettata da nessuno e
        TERMINA il processo. Cioe': un buco di rete su Firebase spegneva il bot
        lasciando aperte le posizioni.

    Da qui la regola: **il Realtime DB non solleva mai**. Le scritture vanno
    comunque nello specchio in memoria, le letture ricadono sull'ultimo valore
    noto, e il guasto viene CONTATO (`degraded_for`) invece che propagato. Il
    loop resta vivo e continua a gestire le posizioni aperte — che vivono in
    memoria e si chiudono coi prezzi di Binance, senza bisogno di Firebase.

    Firestore invece continua a sollevare, ed e' voluto: li' ci sono i trade
    CHIUSI. Se una scrittura fallita passasse per riuscita, il WAL verrebbe
    cancellato subito dopo e quel trade sparirebbe per sempre (equity mai piu'
    riconciliabile). Meglio un ciclo interrotto che un trade perso.
    """

    def __init__(self) -> None:
        self._memory = _InMemoryStore()
        self._fs = None   # firestore client
        self._db = None   # realtime db module
        self._live = False
        # salute del RTDB: istante del PRIMO fallimento della serie in corso
        # (None = sano), quanti ne sono seguiti, e l'ultimo errore visto.
        self._rtdb_down_since: Optional[float] = None
        self._rtdb_failures = 0
        self._last_rtdb_error: Optional[str] = None
        # le letture Firestore, contate (28 set 2026): vedi ContatoreLetture
        self._letture = ContatoreLetture()
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

    def incrementa(self, collection: str, doc_id: str, annidato: dict,
                   imposta: Optional[dict] = None, timeout: float = 10.0) -> None:
        """SOMMA i numeri di `annidato` a quelli del documento, foglia per foglia
        (29 set 2026, per la spesa AI: `bot/ai/spesa.py`).

        PERCHE' NON set_doc. Lo stesso documento lo aggiornano processi diversi
        (bot, optimize, discovery, il runner GitHub della domenica): leggere,
        sommare e riscrivere perderebbe i conti di chi scrive nello stesso istante,
        e costerebbe una lettura a ogni chiamata. Qui dal vivo e' UNA scrittura e
        ZERO letture: `set(merge=True)` con ogni numero avvolto in
        `firestore.Increment`: la somma la fa il server, in modo atomico.

        `imposta`: campi da scrivere cosi' come sono, nella stessa scrittura (es.
        `aggiornato_at`). Come `set_doc` PUO' SOLLEVARE: chi chiama decide se la
        misura vale un'eccezione (per la spesa AI no: la avvolge). `timeout`: una
        misura non deve tenere fermo il giro che la produce.

        UN SOLO TENTATIVO (`retry=None`, 29 set 2026). Senza, `set()` usa la
        politica di default di Firestore per il commit: ritenta i 503/429 fino a
        60 s, e ogni tentativo riceve di nuovo tutto il `timeout` — nel ciclo di
        trading (l'ombra AI) sarebbe fino a un minuto fermo. E un Increment NON e'
        idempotente: se il primo commit e' passato ma la risposta si e' persa, il
        secondo somma di nuovo e la spesa si conta due volte. Una misura persa
        costa una riga di log; una doppia non si vede.
        """
        numeri = _solo_numeri(annidato)
        if self._live:
            from firebase_admin import firestore

            def _avvolgi(d: dict) -> dict:
                return {k: (_avvolgi(v) if isinstance(v, dict) else firestore.Increment(v))
                        for k, v in d.items()}

            dati = _avvolgi(numeri)
            dati.update(imposta or {})
            self._fs.collection(collection).document(doc_id).set(
                dati, merge=True, retry=None, timeout=timeout)
        else:
            self._memory.incrementa(collection, doc_id, numeri, imposta)

    def get_doc(self, collection: str, doc_id: str, chi: Optional[str] = None) -> Optional[dict]:
        """Un documento (1 lettura). `chi` e' l'etichetta del chiamante nel
        contatore delle letture; senza, il nome della funzione che chiama."""
        self._letture.conta(1, chi or _chiamante())
        if self._live:
            snap = self._fs.collection(collection).document(doc_id).get()
            return snap.to_dict() if snap.exists else None
        return self._memory.get_doc(collection, doc_id)

    def get_doc_field(self, collection: str, doc_id: str, fields: list[str],
                      chi: Optional[str] = None) -> Optional[dict]:
        """SOLO alcuni campi di un documento (1 lettura, proiezione lato server:
        il documento resta a casa, viaggiano i campi). E' cio' che `registro_cambiato`
        faceva passando dal client interno (backlog J10, «da fare»): il registro e'
        ~1 MB e la domanda «e' cambiato?» vuole un solo campo. In memoria si legge
        il documento intero e si filtra: li' non costa niente."""
        self._letture.conta(1, chi or _chiamante())
        if self._live:
            snap = self._fs.collection(collection).document(doc_id).get(field_paths=list(fields))
            return (snap.to_dict() or {}) if getattr(snap, "exists", False) else None
        doc = self._memory.get_doc(collection, doc_id)
        if doc is None:
            return None
        return {k: doc[k] for k in fields if k in doc}

    def query_collection(
        self, collection: str, order_by: Optional[str] = None, limit: Optional[int] = None,
        min_value: Optional[float] = None, max_value: Optional[float] = None,
        chi: Optional[str] = None,
    ) -> list[dict]:
        """`min_value` / `max_value`: filtri SERVER-SIDE `order_by >= min_value` e
        `order_by <= max_value` (es. exit_ts degli ultimi 30g). Senza, ogni chiamata
        scarica l'INTERA collection — costo Firestore e latenza che crescono per
        sempre con lo storico. Conta i documenti tornati (almeno 1)."""
        etichetta = chi or _chiamante()
        if self._live:
            q = self._fs.collection(collection)
            if order_by and min_value is not None:
                q = q.where(order_by, ">=", min_value)
            if order_by and max_value is not None:
                q = q.where(order_by, "<=", max_value)
            if order_by:
                q = q.order_by(order_by, direction="DESCENDING")
            if limit:
                q = q.limit(limit)
            docs = [d.to_dict() for d in q.stream()]
            self._letture.conta(len(docs), etichetta)
            return docs
        docs = self._memory.query_collection(collection)
        if order_by and min_value is not None:
            docs = [d for d in docs if d.get(order_by, 0) >= min_value]
        if order_by and max_value is not None:
            docs = [d for d in docs if d.get(order_by, 0) <= max_value]
        if order_by:
            docs = sorted(docs, key=lambda d: d.get(order_by, 0), reverse=True)
        if limit:
            docs = docs[:limit]
        self._letture.conta(len(docs), etichetta)
        return docs

    def count_collection(self, collection: str, chi: Optional[str] = None) -> int:
        """Quanti documenti ha una collection, con l'aggregazione `count()` del
        server: costa 1 lettura ogni 1.000 documenti, non una per documento. Serve
        alla verifica giornaliera della cache dei trade (trade_logger)."""
        self._letture.conta(1, chi or _chiamante())
        if self._live:
            res = self._fs.collection(collection).count().get()
            return int(res[0][0].value)
        return len(self._memory.query_collection(collection))

    def list_doc_ids(self, collection: str, chi: Optional[str] = None) -> list[str]:
        etichetta = chi or _chiamante()
        if self._live:
            ids = [d.id for d in self._fs.collection(collection).stream()]
            self._letture.conta(len(ids), etichetta)
            return ids
        prefix = f"{collection}/"
        ids = [k[len(prefix):] for k in self._memory._docs if k.startswith(prefix)]
        self._letture.conta(len(ids), etichetta)
        return ids

    def letture(self, now: Optional[float] = None) -> dict:
        """Le letture Firestore di QUESTO processo: {totale, ultime_24h,
        per_chiamante: [{chi, n}]} (vedi ContatoreLetture)."""
        return self._letture.riepilogo(now)

    def delete_doc(self, collection: str, doc_id: str) -> None:
        if self._live:
            self._fs.collection(collection).document(doc_id).delete()
        else:
            self._memory._docs.pop(f"{collection}/{doc_id}", None)

    # ---- Realtime DB (stato live) ----
    def _note_rtdb(self, ok: bool, exc: Optional[BaseException] = None) -> None:
        """Tiene il conto dei guasti del RTDB. Un buco si giudica dalla DURATA, non
        dal singolo errore: una richiesta persa capita, dieci minuti di silenzio no."""
        if ok:
            if self._rtdb_down_since is not None:
                import time as _t
                print(f"[firebase] RTDB di nuovo raggiungibile dopo "
                      f"{_t.time() - self._rtdb_down_since:.0f}s "
                      f"({self._rtdb_failures} chiamate fallite)")
            self._rtdb_down_since = None
            self._rtdb_failures = 0
            return
        import time as _t
        self._rtdb_failures += 1
        self._last_rtdb_error = str(exc)[:200] if exc else "?"
        if self._rtdb_down_since is None:
            self._rtdb_down_since = _t.time()
            print(f"[firebase] RTDB irraggiungibile ({self._last_rtdb_error}): "
                  f"si continua sullo specchio in memoria")

    def degraded_for(self, now: Optional[float] = None) -> float:
        """Da quanti secondi il RTDB e' muto. 0 = sano (o non configurato).

        Chi decide se APRIRE legge questo: col database muto non si legge piu' il
        kill switch, cioe' il freno dell'utente, e aggiungere rischio mentre il
        freno e' scollegato non e' una scelta difendibile.
        """
        if self._rtdb_down_since is None:
            return 0.0
        import time as _t
        return max(0.0, (now if now is not None else _t.time()) - self._rtdb_down_since)

    def health(self) -> dict:
        """Diagnostica leggibile: serve al report e ai log, non alle decisioni."""
        return {"live": self._live, "rtdb_down_since": self._rtdb_down_since,
                "rtdb_failures": self._rtdb_failures,
                "rtdb_degraded_for_s": round(self.degraded_for(), 1),
                "last_rtdb_error": self._last_rtdb_error}

    def set_rtdb(self, path: str, data: Any) -> bool:
        """Scrive lo stato live. NON solleva mai. True se e' finita DAVVERO su
        Firebase, False se e' rimasta solo nello specchio in memoria.

        Il valore di ritorno esiste perche' un chiamante puo' avere bisogno di
        sapere se la scrittura e' durevole (il WAL dei trade chiusi lo usa): senza,
        "scritto" e "perso al prossimo riavvio" sarebbero indistinguibili.
        """
        # lo specchio si aggiorna SEMPRE: e' quello che regge le letture quando il
        # database e' muto, e resta allineato quando non lo e'.
        self._memory.set_rtdb(path, data)
        if not (self._live and self._db is not None):
            return False
        try:
            # ATTENZIONE: il RTDB lancia "Value must not be None" se passi None
            # a .set(). Per cancellare un nodo (es. posizione chiusa) si usa
            # .delete(). Senza questo, la chiusura di una posizione crashava e il
            # trade non veniva mai loggato.
            ref = self._db.reference(path)
            if data is None:
                ref.delete()
            else:
                ref.set(data)
            self._note_rtdb(True)
            return True
        except Exception as exc:  # noqa: BLE001
            self._note_rtdb(False, exc)
            return False

    def get_rtdb(self, path: str) -> Any:
        """Legge lo stato live. NON solleva mai: se il database e' muto ritorna
        l'ULTIMO VALORE NOTO (specchio in memoria), che e' sempre meglio di far
        cadere il ciclo di trading.

        ATTENZIONE a come si legge un valore in degrado: per i nodi che scrive il
        BOT lo specchio e' esatto, per quelli che scrive la DASHBOARD (i comandi)
        e' vecchio quanto il buco. Per questo il degrado ha anche una durata, e
        oltre quella si smette di aprire invece di fidarsi di un comando stantio.
        """
        if not (self._live and self._db is not None):
            return self._memory.get_rtdb(path)
        try:
            val = self._db.reference(path).get()
            self._note_rtdb(True)
            # lettura riuscita -> aggiorna lo specchio: cosi' il valore piu' fresco
            # e' gia' li' quando il database smettera' di rispondere
            self._memory.set_rtdb(path, val)
            return val
        except Exception as exc:  # noqa: BLE001
            self._note_rtdb(False, exc)
            return self._memory.get_rtdb(path)


_client: Optional[FirebaseClient] = None


def get_firebase() -> FirebaseClient:
    """Singleton lazy."""
    global _client
    if _client is None:
        _client = FirebaseClient()
    return _client
