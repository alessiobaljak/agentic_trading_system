"""La raccolta per la copia dei trader migliori di Hyperliquid (HYPERLIQUID.md, idea 132 del registro).

A ogni giro (lo chiama la raccolta delle notizie, ogni 4 ore):
* il lunedì al primo giro dopo le 00:00 UTC (e la prima volta) sceglie i 20 conti della settimana dalla classifica pubblica e li salva in
  `hyperliquid/scelti_AAAA-MM-GG.json`;
* dal 5 novembre 2026 sceglie anche le 20 «balene» (i conti piu' grandi, HYPERLIQUID.md, aggiunta del 5 novembre) in
  `hyperliquid/scelti_balene_AAAA-MM-GG.json`: la prima volta subito, poi ogni lunedi';
* legge le posizioni dei conti dei due gruppi (ognuno una volta) e le aggiunge a `hyperliquid/posizioni_AAAA-MM.jsonl.gz` (una riga per
  conto e per giro).

Uso: python3 -m research.trader_copiati.hyperliquid
"""
from __future__ import annotations

import gzip
import json
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

QUI = Path(__file__).parent
ARCHIVIO = QUI / "hyperliquid"
CLASSIFICA = "https://stats-data.hyperliquid.xyz/Mainnet/leaderboard"
INFO = "https://api.hyperliquid.xyz/info"
INIZIO = datetime(2026, 11, 2, tzinfo=timezone.utc)
INIZIO_BALENE = datetime(2026, 11, 5, tzinfo=timezone.utc)
QUANTI, CONTO_MIN, VOLUME_MIN = 20, 1e6, 1e7
UA = {"User-Agent": "ricerca/1.0"}


def _get(url: str, dati: dict | None = None, timeout: int = 90):
    for k in range(3):
        try:
            if dati is None:
                req = urllib.request.Request(url, headers=UA)
            else:
                req = urllib.request.Request(url, data=json.dumps(dati).encode(), headers={**UA, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except Exception:                             # noqa: BLE001
            time.sleep(3 * (k + 1))
    return None


def lunedi_della_settimana(ora: datetime, inizio: datetime = INIZIO) -> datetime:
    g = (ora - timedelta(days=ora.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(g, inizio)


def _candidati(classifica: list) -> list:
    """I conti con almeno 1 milione nel conto, 10 milioni di volume nel mese e guadagno del mese sopra zero."""
    cand = []
    for r in classifica:
        w = dict(r.get("windowPerformances") or [])
        m = w.get("month") or {}
        try:
            conto, vol, pnl, roi = float(r["accountValue"]), float(m["vlm"]), float(m["pnl"]), float(m["roi"])
        except Exception:                             # noqa: BLE001
            continue
        if conto >= CONTO_MIN and vol >= VOLUME_MIN and pnl > 0:
            cand.append({"indirizzo": r["ethAddress"], "conto": conto, "rendimento_mese": roi, "guadagno_mese": pnl, "volume_mese": vol})
    return cand


def scegli(classifica: list) -> list:
    """I 20 conti con il rendimento del mese più alto fra quelli con almeno 1 milione nel conto, 10 milioni di volume nel mese e
    guadagno del mese sopra zero (HYPERLIQUID.md, sezione 2)."""
    cand = _candidati(classifica)
    cand.sort(key=lambda x: -x["rendimento_mese"])
    return cand[:QUANTI]


def scegli_balene(classifica: list) -> list:
    """I 20 conti con il valore del conto piu' alto fra quelli con almeno 10 milioni di volume nel mese e guadagno del mese sopra zero
    (HYPERLIQUID.md, aggiunta del 5 novembre 2026)."""
    cand = _candidati(classifica)
    cand.sort(key=lambda x: -x["conto"])
    return cand[:QUANTI]


GRUPPI = {"": (INIZIO, scegli), "balene_": (INIZIO_BALENE, scegli_balene)}


def scelti(ora: datetime, log=print, gruppo: str = "", cache: dict | None = None) -> list:
    """I conti della settimana del gruppo ('' = i migliori del mese, 'balene_' = i piu' grandi); la classifica si legge una volta."""
    inizio, regola = GRUPPI[gruppo]
    if ora < inizio:
        return []
    lun = lunedi_della_settimana(ora, inizio)
    f = ARCHIVIO / f"scelti_{gruppo}{lun.strftime('%Y-%m-%d')}.json"
    if f.exists():
        return json.loads(f.read_text())["conti"]
    cache = {} if cache is None else cache
    if "classifica" not in cache:
        cache["classifica"] = _get(CLASSIFICA)
    d = cache["classifica"]
    if not d:
        log("[trader] classifica di Hyperliquid non letta")
        return []
    s = regola(d.get("leaderboardRows") or [])
    f.write_text(json.dumps({"scelti_il": ora.strftime("%Y-%m-%d %H:%M"), "conti_in_classifica": len(d.get("leaderboardRows") or []),
                             "conti": s}, indent=1))
    return s


def esegui(ora: datetime | None = None, log=print) -> int:
    """Un giro: sceglie i conti se serve e salva le loro posizioni; restituisce quanti conti sono stati letti."""
    ora = ora or datetime.now(timezone.utc)
    ARCHIVIO.mkdir(parents=True, exist_ok=True)
    cache: dict = {}
    conti = {}
    for gruppo in GRUPPI:
        for c in scelti(ora, log, gruppo, cache):
            conti.setdefault(c["indirizzo"], c)
    conti = list(conti.values())
    righe = []
    for c in conti:
        st = _get(INFO, {"type": "clearinghouseState", "user": c["indirizzo"]}, timeout=30)
        if not st:
            continue
        pos = []
        for p in st.get("assetPositions") or []:
            x = p.get("position") or {}
            try:
                pos.append({"moneta": x["coin"], "quantita": float(x["szi"]), "valore": float(x["positionValue"]),
                            "entrata": float(x["entryPx"]), "leva": (x.get("leverage") or {}).get("value")})
            except Exception:                         # noqa: BLE001
                continue
        righe.append({"ora": ora.strftime("%Y-%m-%d %H:%M"), "letto": int(st.get("time") or 0), "indirizzo": c["indirizzo"],
                      "conto": float((st.get("marginSummary") or {}).get("accountValue") or 0), "posizioni": pos})
    if righe:
        with gzip.open(ARCHIVIO / f"posizioni_{ora.strftime('%Y-%m')}.jsonl.gz", "at", encoding="utf-8") as g:
            for r in righe:
                g.write(json.dumps(r) + "\n")
    log(f"[trader] Hyperliquid: {len(righe)} conti letti su {len(conti)}")
    return len(righe)


if __name__ == "__main__":
    esegui()
