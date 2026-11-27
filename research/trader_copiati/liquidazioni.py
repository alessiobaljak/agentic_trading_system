"""La mappa delle liquidazioni di Hyperliquid (idea 151 del registro; regole in LIQUIDAZIONI.md).

A ogni giro della raccolta (ogni 4 ore e al mattino):
* il lunedì al primo giro (e la prima volta) sceglie i 600 conti della settimana e li salva in
  `hyperliquid/liquidazioni_conti_AAAA-MM-GG.json`: fra i conti della classifica pubblica attivi nel mese (volume del mese di almeno 1
  milione di dollari), fino al 23 novembre 2026 i 600 più grandi per valore in classifica; dal 30 novembre (LIQUIDAZIONI.md, nota del 27
  novembre) si leggono dal più grande fino a 1.500 conti in al più 4 minuti (circa 1.230 nella prova del 27 novembre) e si tengono i 600
  con più posizioni aperte in dollari, e la lettura della scelta fa da giro per quel lunedì;
* legge le posizioni aperte di quei conti con il prezzo di liquidazione e il prezzo medio di ogni moneta, e aggiunge una riga per giro a
  `hyperliquid/liquidazioni_AAAA-MM.jsonl.gz`;
* dal 27 novembre 2026 (audit del 26 novembre) salva anche, una riga per giro, le risposte intere di `allMids` e di `metaAndAssetCtxs`
  (interesse aperto, funding, premio, volume del giorno e prezzi di tutti i perpetui) in `hyperliquid/mercato_AAAA-MM.jsonl.gz`.

Uso: python3 -m research.trader_copiati.liquidazioni   (di solito la chiama research.notizie.raccolta)
"""
from __future__ import annotations

import gzip
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from research.trader_copiati import hyperliquid as th

ARCHIVIO = th.ARCHIVIO
INIZIO = datetime(2026, 11, 22, tzinfo=timezone.utc)
QUANTI, VOLUME_MESE_MIN, VALORE_MIN = 600, 1e6, 1e4   # posizioni sotto i 10.000 dollari non si salvano (0,1% del valore)
PASSO = 0.12          # secondi fra due chiamate per filo: 2 fili, circa 5,5 letture al secondo nei giri del 25-27 novembre (peso 2 l'una)
# La scelta del lunedì dal 30 novembre 2026 (LIQUIDAZIONI.md, nota del 27 novembre)
CANDIDATI = 1500      # quanti conti della classifica si leggono, dal più grande
RITMO_SCELTA = 6.0    # letture al secondo per tutti i fili insieme: prova del 27 novembre, a 7 al secondo 199 risposte 429 su 1.500
#                       (Hyperliquid ne accetta circa 300-360 al minuto); con la pausa sotto, a 6 al secondo 30 rifiuti e 4 conti persi
FILI_SCELTA = 4       # un tentativo per volta, senza le attese di _get: un filo fermo su una risposta lenta non rallenta gli altri
TEMPO_SCELTA = 240    # secondi al massimo per la scelta, classifica compresa: con il resto del giro si resta sotto i 5 minuti
TIMEOUT_SCELTA = 10   # secondi per tentativo nelle letture della scelta
PAUSA_SCELTA = 2.0    # dopo una lettura rifiutata (429) tutti i fili aspettano 2 secondi, poi quel conto si riprova una volta
REGOLA = ("dal 30 novembre 2026: fra i conti con almeno 1 milione di volume nel mese, letti dal più grande in classifica fino a 1.500 in "
          "al più 4 minuti, i 600 con più posizioni aperte in dollari (LIQUIDAZIONI.md, nota del 27 novembre)")


def candidati(classifica: list) -> list:
    """I conti con almeno 1 milione di volume nel mese, dal più grande per valore in classifica (LIQUIDAZIONI.md, punto 1)."""
    cand = []
    for r in classifica:
        try:
            m = dict(r["windowPerformances"])["month"]
            conto, vol = float(r["accountValue"]), float(m["vlm"])
        except Exception:                             # noqa: BLE001
            continue
        if vol >= VOLUME_MESE_MIN:
            cand.append({"indirizzo": r["ethAddress"], "conto": conto, "volume_mese": vol})
    return sorted(cand, key=lambda x: -x["conto"])


def scegli(classifica: list) -> list:
    """La regola fino al 23 novembre 2026: i 600 conti più grandi in classifica fra quelli con almeno 1 milione di volume nel mese."""
    return candidati(classifica)[:QUANTI]


def aperte(stato: dict | None) -> float:
    """Le posizioni aperte in dollari di un conto: la somma dei valori di tutte le sue posizioni (anche quelle sotto i 10.000 dollari)."""
    tot = 0.0
    for p in (stato or {}).get("assetPositions") or []:
        try:
            tot += abs(float((p.get("position") or {})["positionValue"]))
        except Exception:                             # noqa: BLE001
            continue
    return tot


def scegli_per_posizioni(cand: list, stati: dict) -> list:
    """La regola dal 30 novembre 2026: fra i candidati letti, i 600 con più posizioni aperte in dollari (a parità, il più grande in
    classifica); se se ne sono letti meno di 600, si completa con quelli non letti nell'ordine della classifica."""
    letti, non_letti = [], []
    for k, c in enumerate(cand):
        st = stati.get(c["indirizzo"])
        if st:
            valore = float((st.get("marginSummary") or {}).get("accountValue") or 0)
            letti.append((-aperte(st), k, {**c, "posto": k + 1, "posizioni_aperte": round(aperte(st), 2), "conto_a_leva": round(valore, 2)}))
        else:
            non_letti.append({**c, "posto": k + 1, "posizioni_aperte": None, "conto_a_leva": None})
    scelti = [x[2] for x in sorted(letti, key=lambda x: (x[0], x[1]))[:QUANTI]]
    return scelti + non_letti[:QUANTI - len(scelti)]


class _Ritmo:
    """Al più ``n`` chiamate al secondo fra tutti i fili insieme."""

    def __init__(self, n: float):
        self.passo, self.prossima, self.lock = 1.0 / n, time.monotonic(), threading.Lock()

    def aspetta(self) -> None:
        with self.lock:
            adesso = time.monotonic()
            t = max(adesso, self.prossima)
            self.prossima = t + self.passo
        time.sleep(max(0.0, t - adesso))

    def frena(self, secondi: float) -> None:
        """La prossima chiamata, di qualunque filo, non prima di ``secondi`` da adesso."""
        with self.lock:
            self.prossima = max(self.prossima, time.monotonic() + secondi)


def leggi_candidati(indirizzi: list, scadenza: float, tentati: list | None = None) -> dict:
    """Le posizioni dei candidati, nell'ordine della classifica e al ritmo della scelta; dopo la ``scadenza`` (orologio monotono) non se
    ne leggono altri. Una lettura rifiutata o fallita ferma tutti i fili per ``PAUSA_SCELTA`` secondi e si riprova una volta sola (le
    attese di ``_get`` fermavano un filo solo e gli altri continuavano a farsi rifiutare). Restituisce {indirizzo: stato o None}; in
    ``tentati`` gli indirizzi per cui la lettura è partita."""
    ritmo = _Ritmo(RITMO_SCELTA)

    def uno(indirizzo):
        for k in range(2):
            if time.monotonic() > scadenza:
                return indirizzo, None, k > 0
            ritmo.aspetta()
            if time.monotonic() > scadenza:
                return indirizzo, None, k > 0
            st = th._get(th.INFO, {"type": "clearinghouseState", "user": indirizzo}, timeout=TIMEOUT_SCELTA, tentativi=1)
            if st:
                return indirizzo, st, True
            ritmo.frena(PAUSA_SCELTA)
        return indirizzo, None, True

    with ThreadPoolExecutor(max_workers=FILI_SCELTA) as ex:
        esiti = list(ex.map(uno, indirizzi))
    if tentati is not None:
        tentati.extend(i for i, _, partito in esiti if partito)
    return {i: st for i, st, _ in esiti}


def conti(ora: datetime, log=print) -> tuple[list, dict]:
    """I conti della settimana e, il lunedì della scelta, le posizioni lette per sceglierli (``{"stati": {indirizzo: stato}, "da": ...,
    "a": ...}``: fanno da giro per quel lunedì); gli altri giorni il secondo elemento è vuoto."""
    lun = th.lunedi_della_settimana(ora, INIZIO)
    f = ARCHIVIO / f"liquidazioni_conti_{lun.strftime('%Y-%m-%d')}.json"
    if f.exists():
        return json.loads(f.read_text())["conti"], {}
    inizio = time.monotonic()
    d = th._get(th.CLASSIFICA)
    if not d:
        log("[liquidazioni] classifica di Hyperliquid non letta")
        return [], {}
    righe = d.get("leaderboardRows") or []
    cand = candidati(righe)[:CANDIDATI]
    da = datetime.now(timezone.utc)
    tentati: list = []
    stati = leggi_candidati([c["indirizzo"] for c in cand], inizio + TEMPO_SCELTA, tentati)
    a = datetime.now(timezone.utc)
    s = scegli_per_posizioni(cand, stati)
    letti = sum(1 for c in cand if stati.get(c["indirizzo"]))
    f.write_text(json.dumps({"scelti_il": ora.strftime("%Y-%m-%d %H:%M"), "conti_in_classifica": len(righe), "regola": REGOLA,
                             "candidati": len(cand), "candidati_tentati": len(tentati), "candidati_letti": letti,
                             "letti_da": da.strftime("%Y-%m-%d %H:%M:%S"), "letti_a": a.strftime("%Y-%m-%d %H:%M:%S"), "conti": s},
                            indent=0))
    con = sum(1 for c in s if c["posizioni_aperte"])
    log(f"[liquidazioni] scelta della settimana: {letti} candidati letti su {len(cand)} ({len(tentati) - letti} letture rifiutate o "
        f"fallite) in {(a - da).seconds} s; dei {len(s)} scelti {con} con posizioni aperte")
    return s, {"stati": {c["indirizzo"]: stati[c["indirizzo"]] for c in s if stati.get(c["indirizzo"])}, "da": da, "a": a}


def _leggi(indirizzo: str):
    time.sleep(PASSO)
    return th._get(th.INFO, {"type": "clearinghouseState", "user": indirizzo}, timeout=30)


def salva_mercato(ora: datetime, medi: dict | None = None, letto_medi: datetime | None = None, log=print) -> bool:
    """Una riga per giro in `mercato_AAAA-MM.jsonl.gz`: le risposte intere di `allMids` (quella del giro, se c'è) e di
    `metaAndAssetCtxs`, con l'ora di lettura di ognuna (audit del 26 novembre: l'interesse aperto giro per giro non si recupera dopo)."""
    if not medi:
        medi = th._get(th.INFO, {"type": "allMids"}, timeout=30)
        letto_medi = datetime.now(timezone.utc)
    ctx = th._get(th.INFO, {"type": "metaAndAssetCtxs"}, timeout=30)
    letto_ctx = datetime.now(timezone.utc)
    if not medi and not ctx:
        log("[liquidazioni] mercato di Hyperliquid non letto")
        return False
    riga = {"ora": ora.strftime("%Y-%m-%d %H:%M"),
            "allMids_letto": letto_medi.strftime("%Y-%m-%d %H:%M:%S") if medi and letto_medi else None, "allMids": medi or None,
            "metaAndAssetCtxs_letto": letto_ctx.strftime("%Y-%m-%d %H:%M:%S") if ctx else None, "metaAndAssetCtxs": ctx or None}
    with gzip.open(ARCHIVIO / f"mercato_{ora.strftime('%Y-%m')}.jsonl.gz", "at", encoding="utf-8") as g:
        g.write(json.dumps(riga, separators=(",", ":")) + "\n")
    n = len(ctx[1]) if isinstance(ctx, list) and len(ctx) > 1 and isinstance(ctx[1], list) else 0
    log(f"[liquidazioni] mercato di Hyperliquid: {n} perpetui, {len(medi or {})} prezzi medi")
    return True


def _mercato(ora: datetime, medi: dict | None, letto_medi: datetime | None, log) -> None:
    try:
        salva_mercato(ora, medi, letto_medi, log)
    except Exception as ex:                           # noqa: BLE001
        log(f"[liquidazioni] mercato di Hyperliquid non salvato ({ex})")


def esegui(ora: datetime | None = None, log=print) -> int:
    """Un giro: restituisce quanti conti sono stati letti."""
    ora = ora or datetime.now(timezone.utc)
    if ora < INIZIO:
        return 0
    ARCHIVIO.mkdir(parents=True, exist_ok=True)
    cc, scelta = conti(ora, log)
    if not cc:
        _mercato(ora, None, None, log)
        return 0
    gia = scelta.get("stati") or {}
    mancano = [c["indirizzo"] for c in cc if c["indirizzo"] not in gia]
    da = scelta["da"] if gia else datetime.now(timezone.utc)
    with ThreadPoolExecutor(max_workers=2) as ex:
        nuovi = dict(zip(mancano, ex.map(_leggi, mancano)))
    stati = [gia.get(c["indirizzo"]) or nuovi.get(c["indirizzo"]) for c in cc]
    a = datetime.now(timezone.utc)
    medi = th._get(th.INFO, {"type": "allMids"}, timeout=30) or {}
    letto_medi = datetime.now(timezone.utc)
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
    if gia:
        riga["letto_nella_scelta"] = len(gia)        # il lunedì della scelta: posizioni lette per scegliere i conti
    with gzip.open(ARCHIVIO / f"liquidazioni_{ora.strftime('%Y-%m')}.jsonl.gz", "at", encoding="utf-8") as g:
        g.write(json.dumps(riga, separators=(",", ":")) + "\n")
    log(f"[liquidazioni] Hyperliquid: {letti} conti su {len(cc)}, {len(pos)} posizioni, "
        f"{sum(1 for x in pos if x[5] is not None)} con il prezzo di liquidazione ({(a - da).seconds} s)")
    _mercato(ora, medi, letto_medi, log)
    return letti


if __name__ == "__main__":
    esegui()
