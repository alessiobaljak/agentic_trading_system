"""I titoli appena tolti dall'S&P 500 (`stock/prove/P008_usciti_dall_indice.md`)."""
from __future__ import annotations

import math
from datetime import date

from stock.simulatore.motore import Ordine
from stock.simulatore.portafoglio import Storia, StatoConto

QUOTA = 0.10
MASSIMO = 10
SEDUTE = 20


def eventi_di_uscita(composizione, dal: date, al: date) -> list[tuple[date, str]]:
    """(primo giorno fuori dall'elenco, simbolo) per ogni uscita fra `dal` e `al`."""
    out = []
    for (d0, m0), (d1, m1) in zip(composizione, composizione[1:]):
        if dal <= d1 <= al:
            out += [(d1, t) for t in sorted(m0 - m1)]
    return out


def strategia(eventi: list[tuple[date, str]], calendario: list[date]):
    giorni = sorted(calendario)
    indice = {d: i for i, d in enumerate(giorni)}
    # il giorno di borsa dell'ingresso: il primo giorno di borsa non prima del giorno dell'uscita
    import bisect
    piano: dict[date, list[str]] = {}            # giorno della decisione -> simboli da comprare
    uscita_di: dict[tuple[str, date], date] = {}
    for d, t in eventi:
        k = bisect.bisect_left(giorni, d)
        if k == 0 or k + SEDUTE - 1 >= len(giorni):
            continue
        decisione = giorni[k - 1]
        piano.setdefault(decisione, []).append(t)
        uscita_di[(t, giorni[k])] = giorni[k + SEDUTE - 1]   # decisione di vendita: chiusura della 20ª seduta
    da_vendere: dict[date, list[str]] = {}

    def decidi(giorno: date, storia: Storia, stato: StatoConto) -> list:
        ordini = []
        for t in da_vendere.pop(giorno, []):
            q = stato.azioni.get(t, 0)
            if q > 0:
                ordini.append((t, Ordine(-q, "mercato", etichetta="uscita")))
        tenuti = {t for t, q in stato.azioni.items() if q > 0} - {t for t, _ in ordini}
        liberi = MASSIMO - len(tenuti)
        prossimo = giorni[indice[giorno] + 1] if giorno in indice and indice[giorno] + 1 < len(giorni) else None
        for t in sorted(piano.get(giorno, [])):
            if liberi <= 0 or t in tenuti or prossimo is None:
                continue
            h = storia(t)
            if h is None or h.empty:
                continue
            prezzo = float(h["close"].iloc[-1])
            q = math.floor(QUOTA * stato.valore() / prezzo)
            if q <= 0:
                continue
            ordini.append((t, Ordine(q, "mercato", etichetta="ingresso")))
            da_vendere.setdefault(uscita_di[(t, prossimo)], []).append(t)
            liberi -= 1
        return ordini
    return decidi
