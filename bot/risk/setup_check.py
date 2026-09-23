"""IL CONTROLLO DEL SETUP PRIMA DI APRIRE, E L'AUTOPSIA DOPO — dagli stessi numeri.

Domanda del proprietario, 23 set 2026, sul long MUBARAK chiuso in stop dopo ore in
positivo: «perche' queste analisi che fai a posteriori il sistema non le puo' fare
PRIMA di aprire? E per ogni trade chiuso in negativo voglio questa analisi come
parte del processo, scritta da qualche parte e usata per migliorare».

Qui vivono tutte e due le cose, e sono la stessa aritmetica:

  * `analizza_setup`: dato prezzo, stop e scala, dice quanto e' largo lo stop in
    percentuale, dove sta il primo incasso e dove si armerebbe la protezione.
    Se lo stop supera MAX_STOP_PCT il setup NON e' tradabile: lo usa il motore di
    backtest (salta l'ingresso) e il risk manager (rifiuta con il motivo). Stessa
    funzione da tutte e due le parti, quindi parita' gate<->paper.
  * `post_mortem`: alla chiusura, dagli stessi numeri piu' l'escursione vera
    (mfe), scrive il referto: classe della morte (ingresso / uscita /
    protezione), se il lock si e' mai potuto armare, se lo stop era largo, se era
    controtrend, e un verdetto in una riga. Viaggia dentro il documento del trade
    (`post_mortem`), lo stampa `trades`, e da li' lo leggono il referto
    settimanale e — quando ce ne saranno abbastanza — l'AI (backlog B4).

Il caso che ha fatto nascere il file, coi numeri veri:
  entry 0,07022 · stop 0,0595 (-15,3%) · scala 2/4/6 -> primo incasso +31%,
  lock a +15,3%; il prezzo e' salito del 3-6% e tornato: mfe ~0,3R. Verdetto:
  «stop troppo largo (15,3% > 6%): setup non tradabile, il lock non poteva
  armarsi prima di +15%».
"""
from __future__ import annotations

from typing import Optional

from bot.config import settings

CLASSI = ("ingresso", "uscita", "protezione")


def analizza_setup(entry: float, stop: float, mults: Optional[tuple] = None,
                   max_stop_pct: Optional[float] = None) -> dict:
    """La geometria del trade PRIMA di aprirlo. `tradabile` e' la sola decisione."""
    mults = tuple(mults) if mults else tuple(settings.SCALE_OUT_R_MULTIPLES)
    tetto = settings.MAX_STOP_PCT if max_stop_pct is None else max_stop_pct
    if not entry or entry <= 0 or stop is None:
        return {"stop_pct": None, "tradabile": True, "motivo": ""}
    stop_pct = abs(entry - stop) / entry
    primo = mults[0] * stop_pct
    lock = settings.PROFIT_LOCK_TRIGGER * primo
    out = {
        "stop_pct": round(stop_pct, 4),
        "primo_gradino_pct": round(primo, 4),
        "lock_arma_pct": round(lock, 4),
        "tradabile": True,
        "motivo": "",
    }
    if tetto and tetto > 0 and stop_pct > tetto:
        out["tradabile"] = False
        out["motivo"] = (f"stop troppo largo: {stop_pct * 100:.1f}% del prezzo > "
                         f"{tetto * 100:.0f}% (ATR gonfiato: primo incasso a "
                         f"+{primo * 100:.0f}%, lock a +{lock * 100:.0f}%)")
    return out


def _controtrend(direction: str, regime: str) -> Optional[bool]:
    d, r = str(direction or "").lower(), str(regime or "").lower()
    if "bull" in r:
        return d == "short"
    if "bear" in r:
        return d == "long"
    return None


def post_mortem(t: dict) -> dict:
    """Il referto di un trade chiuso. `t` e' il documento del trade (o un dict con
    gli stessi campi). Non decide niente: descrive, con gli stessi numeri del
    controllo pre-trade, cosi' referto e controllo non possono divergere."""
    entry = float(t.get("entry_price") or 0)
    stop = t.get("orig_stop") if t.get("orig_stop") else t.get("stop_price")
    mults = t.get("scale_r_mults") or None
    geo = analizza_setup(entry, float(stop) if stop else None, mults)
    mfe_r = t.get("mfe_r")
    mfe_r = float(mfe_r) if mfe_r is not None else None
    m0 = float((mults or settings.SCALE_OUT_R_MULTIPLES)[0])
    pnl = float(t.get("pnl") or 0)
    classe = None
    if mfe_r is not None:
        classe = ("ingresso" if mfe_r < 0.25 else "uscita" if mfe_r < m0 else "protezione")
    lock_mai = (mfe_r is not None and mfe_r < settings.PROFIT_LOCK_TRIGGER * m0)
    contro = _controtrend(t.get("direction"), t.get("regime_at_entry"))
    stop_pct = geo.get("stop_pct")
    pezzi = []
    if not geo["tradabile"]:
        pezzi.append(geo["motivo"])
    if classe == "ingresso":
        pezzi.append(f"mai andato a favore (mfe {mfe_r:.2f}R): direzione sbagliata")
    elif classe == "uscita":
        pezzi.append(f"a favore fino a {mfe_r:.2f}R ma sotto il primo gradino ({m0:g}R)")
    elif classe == "protezione":
        pezzi.append(f"oltre il primo gradino ({mfe_r:.2f}R) e poi stop")
    if lock_mai and classe != "ingresso":
        pezzi.append(f"il lock non si e' mai armato (serviva {settings.PROFIT_LOCK_TRIGGER * m0:.2g}R)")
    if contro:
        pezzi.append("controtrend rispetto al regime all'ingresso")
    if pnl >= 0:
        pezzi.insert(0, "chiuso in guadagno")
    return {
        "classe": classe,
        "stop_pct": stop_pct,
        "primo_gradino_pct": geo.get("primo_gradino_pct"),
        "lock_arma_pct": geo.get("lock_arma_pct"),
        "stop_largo": not geo["tradabile"],
        "lock_mai_armato": bool(lock_mai),
        "controtrend": contro,
        "mfe_r": mfe_r,
        "verdetto": " · ".join(pezzi) if pezzi else "nessun rilievo",
    }
