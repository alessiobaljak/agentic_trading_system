"""LA STORIA DEL GATE, TENUTA (1 ott 2026, la cattura dei dati mancanti).

IL BUCO. Il registro `strategy_registry/validated` si RISCRIVE a ogni giro: dopo
una settimana nessuno sa piu' dire con quanti passaggi era una coppia martedi',
che PF prometteva, quando e' stata declassata, quale criterio ha fermato piu'
candidate in quel giro. Senza quella storia «quali idee reggono dopo il gate»
non ha una risposta misurata.

COSA FA. Alla fine di ogni giro della discovery (`scripts/discover_strategies.py`,
dopo `discovered_last_run`) si AGGIUNGONO righe a un file JSONL del mese sulla
macchina, `data/gate_storia/AAAA-MM.jsonl` (cartella fuori da git, vedi
.gitignore; `GATE_STORIA_DIR` la sposta):
  * una riga «giro»: quando, timeframe, modalita', commit, valutazioni,
    passate, conteggi dei criteri che hanno fermato le candidate (`binding`
    dell'autopsia), durata, quante coppie e quante validate;
  * una riga per OGNI coppia del registro, compatta (chiavi di una-due lettere):
    k = chiave, p = pass_count, f = fail_count, pf = last_pf, wr =
    last_win_rate, t = last_t, d = declassata (1/0), v = validata (1/0).
    Le righe coppia NON hanno l'ora: appartengono alla riga «giro» che le
    precede nel file.
ZERO Firestore: il registro e' quello che il giro ha appena scritto (in
memoria), i conteggi sono quelli dell'autopsia locale.

QUANTO PESA (STIMA, misurata con `test_dati_gate_storia` su 3.000 coppie finte
con chiavi lunghe come quelle vere): ~92 byte a riga coppia. Con il tetto del
registro (OPTIMIZER_MAX_PAIRS = 3.000) ~270 KB a giro; con ~1.200 coppie
(ordine di grandezza del registro di fine settembre) ~110 KB. A 8-16 giri al
giorno (discovery ogni 3 ore, piu' la passata a 1 ora) sono 1-4,5 MB al
giorno, 30-130 MB al mese nel caso peggiore. Nessuna pulizia automatica: e'
storia da tenere; si comprime a mano (`gzip data/gate_storia/2026-09.jsonl`) se
serve spazio.

FAIL-OPEN: niente qui puo' far fallire un giro del gate. Al massimo una riga
di log.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from typing import Optional

#: la cartella dei file del mese (relativa alla cartella da cui gira il gate)
STORIA_DIR = os.getenv("GATE_STORIA_DIR", "data/gate_storia")
#: versione del formato delle righe
FORMATO = 1


def _num(v) -> Optional[float]:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f else None


def _r(v, nd: int = 3) -> Optional[float]:
    f = _num(v)
    return round(f, nd) if f is not None else None


def percorso(now: float, cartella: str | None = None) -> str:
    """`<cartella>/AAAA-MM.jsonl` del mese (UTC) di `now`."""
    mese = datetime.fromtimestamp(float(now), tz=timezone.utc).strftime("%Y-%m")
    return os.path.join(cartella or STORIA_DIR, f"{mese}.jsonl")


def riga_coppia(key: str, rec: dict, validate: set) -> dict:
    """La riga compatta di UNA coppia del registro. Pura."""
    rec = rec if isinstance(rec, dict) else {}
    out = {"k": str(key), "p": int(_num(rec.get("pass_count")) or 0),
           "f": int(_num(rec.get("fail_count")) or 0)}
    for corto, campo, nd in (("pf", "last_pf", 3), ("wr", "last_win_rate", 3), ("t", "last_t", 2)):
        v = _r(rec.get(campo), nd)
        if v is not None:
            out[corto] = v
    if rec.get("declassata"):
        out["d"] = 1
    if key in validate:
        out["v"] = 1
    return out


def righe_giro(pairs: dict, validated, *, n_eval: int, n_passed: int, binding: dict | None,
               durata_s: float, modalita: str, commit: Optional[str], interval: str,
               now: float, fase: str = "discover") -> list[dict]:
    """Le righe di un giro: prima la riga «giro», poi una per coppia (ordinate
    per chiave). Pura."""
    pairs = pairs if isinstance(pairs, dict) else {}
    validate = {str(k) for k in (validated or []) if isinstance(k, str)}
    giro = {
        "tipo": "giro", "formato": FORMATO, "at": float(now), "interval": str(interval),
        "fase": str(fase), "modalita": str(modalita or ""), "commit": commit,
        "n_eval": int(n_eval or 0), "n_passed": int(n_passed or 0),
        "binding": {str(k): int(v) for k, v in (binding or {}).items()
                    if _num(v) is not None},
        "durata_s": int(max(0.0, float(durata_s or 0.0))),
        "coppie": len(pairs), "validate": len(validate),
    }
    righe = [giro]
    for key in sorted(pairs):
        # niente `at` sulla riga della coppia (19 byte x migliaia di righe): vale
        # quello della riga «giro» che la precede nel file
        righe.append({"tipo": "c", **riga_coppia(key, pairs[key], validate)})
    return righe


def scrivi(righe: list[dict], now: float | None = None, cartella: str | None = None) -> int:
    """Aggiunge le righe al file del mese. Ritorna i byte scritti (0 se non ha
    potuto). Non solleva mai."""
    try:
        now = time.time() if now is None else now
        path = percorso(now, cartella)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        parti = []
        for r in righe or []:
            try:
                parti.append(json.dumps(r, ensure_ascii=False, allow_nan=False,
                                        separators=(",", ":")))
            except (TypeError, ValueError):
                continue                      # un NaN salta LA RIGA, non il giro
        testo = "".join(p + "\n" for p in parti)
        with open(path, "a", encoding="utf-8") as f:
            f.write(testo)
        return len(testo.encode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"[gate-storia] righe non scritte ({str(exc)[:120]})")
        return 0


def registra_giro(pairs: dict, validated, **kw) -> int:
    """`righe_giro` + `scrivi`, con una riga di log. Non solleva mai."""
    try:
        cartella = kw.pop("cartella", None)
        now = float(kw.get("now") or time.time())
        kw["now"] = now
        righe = righe_giro(pairs, validated, **kw)
        n = scrivi(righe, now, cartella)
        if n:
            print(f"[gate-storia] {len(righe) - 1} coppie + riga del giro in "
                  f"{percorso(now, cartella)} ({n // 1024} KiB)")
        return n
    except Exception as exc:  # noqa: BLE001
        print(f"[gate-storia] giro non registrato ({str(exc)[:120]})")
        return 0
