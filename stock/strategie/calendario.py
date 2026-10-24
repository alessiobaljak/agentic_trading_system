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
