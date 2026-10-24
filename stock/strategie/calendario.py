"""Le regole di calendario sull'indice (`stock/prove/P006_cambio_del_mese.md`)."""
from __future__ import annotations

from datetime import date

from stock.simulatore.portafoglio import Storia, StatoConto, verso_pesi


def posizione_nel_mese(calendario: list[date]) -> dict[date, tuple[int, int]]:
    """Per ogni giorno di borsa: (numero del giorno nel mese, dall'1; giorni di borsa del mese)."""
    per_mese: dict[tuple[int, int], list[date]] = {}
    for d in sorted(calendario):
        per_mese.setdefault((d.year, d.month), []).append(d)
    out = {}
    for giorni in per_mese.values():
        for i, d in enumerate(giorni):
            out[d] = (i + 1, len(giorni))
    return out


def strategia_cambio_del_mese(simbolo: str, calendario: list[date]):
    pos = posizione_nel_mese(calendario)

    def decidi(giorno: date, storia: Storia, stato: StatoConto) -> list:
        k, n = pos.get(giorno, (0, 0))
        h = storia(simbolo)
        if h is None or h.empty or h.index[-1] != giorno:
            return []
        prezzo = {simbolo: float(h["close"].iloc[-1])}
        if k == n - 2 and not stato.azioni:                 # terz'ultimo giorno: si compra all'apertura del penultimo
            return verso_pesi(stato, {simbolo: 1.0}, prezzo, etichetta="ingresso")
        if k == 3 and stato.azioni:                          # terzo giorno: si vende all'apertura del quarto
            return verso_pesi(stato, {}, prezzo, etichetta="uscita")
        return []
    return decidi


NY = "America/New_York"


def prepara_prima_della_fed(barre, cal, comunicati, giorni_esclusi: set) -> dict:
    """Barre al minuto di seduta: decisione d'acquisto alla barra delle 13:59 del giorno di borsa prima del comunicato,
    decisione di vendita alla barra delle 13:58 del giorno del comunicato (`stock/prove/P007_prima_della_fed.md`)."""
    import numpy as np
    import pandas as pd
    t = barre.index.tz_convert(NY)
    pos = {x: i for i, x in enumerate(t)}
    giorni = sorted(cal.index)
    prima = dict(zip(giorni[1:], giorni[:-1]))
    compra = np.zeros(len(barre), dtype=bool)
    vendi = np.zeros(len(barre), dtype=bool)
    saltati = []
    for d in comunicati:
        p = prima.get(d)
        if p is None or d in giorni_esclusi or p in giorni_esclusi:
            saltati.append(d)
            continue
        servono = [pd.Timestamp(f"{p} 13:59", tz=NY), pd.Timestamp(f"{p} 14:00", tz=NY),
                   pd.Timestamp(f"{d} 13:58", tz=NY), pd.Timestamp(f"{d} 13:59", tz=NY)]
        if not all(x in pos for x in servono):
            saltati.append(d)
            continue
        compra[pos[servono[0]]] = True
        vendi[pos[servono[2]]] = True
    return {"compra": compra, "vendi": vendi, "saltati": saltati}


def strategia_finestre(seg: dict, quota: float = 0.98):
    """Compra alle barre segnate `compra`, vende alle barre segnate `vendi` (esecuzione alla barra dopo)."""
    import math

    from stock.simulatore.motore import Ordine
    compra, vendi = seg["compra"], seg["vendi"]

    def decidi(storia, stato) -> list:
        i = len(storia) - 1
        if vendi[i] and stato.azioni > 0:
            return [Ordine(-stato.azioni, "mercato", etichetta="uscita")]
        if compra[i] and stato.azioni == 0:
            c = float(storia["close"].iat[-1])
            q = math.floor(quota * stato.valore(c) / c)
            return [Ordine(q, "mercato", etichetta="ingresso")] if q > 0 else []
        return []
    return decidi
