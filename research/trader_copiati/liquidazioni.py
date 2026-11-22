"""La mappa delle liquidazioni di Hyperliquid (idea 151 del registro; regole in LIQUIDAZIONI.md).

A ogni giro della raccolta (ogni 4 ore e al mattino):
* il lunedì al primo giro (e la prima volta) sceglie dalla classifica pubblica i 600 conti più grandi fra quelli attivi nel mese
  (volume del mese di almeno 1 milione di dollari) e li salva in `hyperliquid/liquidazioni_conti_AAAA-MM-GG.json`;
* legge le posizioni aperte di quei conti con il prezzo di liquidazione e il prezzo medio di ogni moneta, e aggiunge una riga per giro a
  `hyperliquid/liquidazioni_AAAA-MM.jsonl.gz`.

Uso: python3 -m research.trader_copiati.liquidazioni   (di solito la chiama research.notizie.raccolta)
"""
from __future__ import annotations

import gzip
import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from research.trader_copiati import hyperliquid as th

ARCHIVIO = th.ARCHIVIO
INIZIO = datetime(2026, 11, 22, tzinfo=timezone.utc)
QUANTI, VOLUME_MESE_MIN, VALORE_MIN = 600, 1e6, 1e4   # posizioni sotto i 10.000 dollari non si salvano (0,1% del valore)
PASSO = 0.12          # secondi fra due chiamate per filo: 2 fili → circa 17 chiamate al secondo, peso 2 → sotto il limite di 1.200 al minuto


def scegli(classifica: list) -> list:
    """I 600 conti più grandi fra quelli con almeno 1 milione di volume nel mese (LIQUIDAZIONI.md, punto 1)."""
    cand = []
    for r in classifica:
        try:
            m = dict(r["windowPerformances"])["month"]
            conto, vol = float(r["accountValue"]), float(m["vlm"])
        except Exception:                             # noqa: BLE001
            continue
        if vol >= VOLUME_MESE_MIN:
            cand.append({"indirizzo": r["ethAddress"], "conto": conto, "volume_mese": vol})
    return sorted(cand, key=lambda x: -x["conto"])[:QUANTI]


def conti(ora: datetime, log=print) -> list:
    lun = th.lunedi_della_settimana(ora, INIZIO)
    f = ARCHIVIO / f"liquidazioni_conti_{lun.strftime('%Y-%m-%d')}.json"
    if f.exists():
        return json.loads(f.read_text())["conti"]
    d = th._get(th.CLASSIFICA)
    if not d:
        log("[liquidazioni] classifica di Hyperliquid non letta")
        return []
    s = scegli(d.get("leaderboardRows") or [])
    f.write_text(json.dumps({"scelti_il": ora.strftime("%Y-%m-%d %H:%M"), "conti_in_classifica": len(d.get("leaderboardRows") or []),
                             "conti": s}, indent=0))
    return s


def _leggi(indirizzo: str):
    time.sleep(PASSO)
    return th._get(th.INFO, {"type": "clearinghouseState", "user": indirizzo}, timeout=30)


def esegui(ora: datetime | None = None, log=print) -> int:
    """Un giro: restituisce quanti conti sono stati letti."""
    ora = ora or datetime.now(timezone.utc)
    if ora < INIZIO:
        return 0
    ARCHIVIO.mkdir(parents=True, exist_ok=True)
    cc = conti(ora, log)
    if not cc:
        return 0
    da = datetime.now(timezone.utc)
    with ThreadPoolExecutor(max_workers=2) as ex:
        stati = list(ex.map(_leggi, [c["indirizzo"] for c in cc]))
    a = datetime.now(timezone.utc)
    medi = th._get(th.INFO, {"type": "allMids"}, timeout=30) or {}
    pos, letti, monete = [], 0, set()
    for i, st in enumerate(stati):
        if not st:
            continue
        letti += 1
        for p in st.get("assetPositions") or []:
            x = p.get("position") or {}
            try:
                if float(x["positionValue"]) < VALORE_MIN:
                    continue
                liq = x.get("liquidationPx")
                pos.append([i, x["coin"], float(x["szi"]), round(float(x["positionValue"]), 2), float(x["entryPx"]),
                            float(liq) if liq not in (None, "") else None, (x.get("leverage") or {}).get("value"),
                            (x.get("leverage") or {}).get("type")])
                monete.add(x["coin"])
            except Exception:                         # noqa: BLE001
                continue
    riga = {"ora": ora.strftime("%Y-%m-%d %H:%M"), "letto_da": da.strftime("%H:%M:%S"), "letto_a": a.strftime("%H:%M:%S"),
            "conti_della_settimana": f"liquidazioni_conti_{th.lunedi_della_settimana(ora, INIZIO).strftime('%Y-%m-%d')}.json",
            "conti_letti": letti, "conti": [round(float((st or {}).get("marginSummary", {}).get("accountValue") or 0), 0) if st else None
                                           for st in stati],
            "prezzi": {m: float(medi[m]) for m in sorted(monete) if m in medi},
            "colonne": ["conto", "moneta", "quantita", "valore", "entrata", "liquidazione", "leva", "tipo"], "posizioni": pos}
    with gzip.open(ARCHIVIO / f"liquidazioni_{ora.strftime('%Y-%m')}.jsonl.gz", "at", encoding="utf-8") as g:
        g.write(json.dumps(riga, separators=(",", ":")) + "\n")
    log(f"[liquidazioni] Hyperliquid: {letti} conti su {len(cc)}, {len(pos)} posizioni, "
        f"{sum(1 for x in pos if x[5] is not None)} con il prezzo di liquidazione ({(a - da).seconds} s)")
    return letti


if __name__ == "__main__":
    esegui()
