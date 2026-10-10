"""Costo di un giro (commissione e slippage, andata e ritorno) in R, per le previsioni al netto dei costi (lezioni/metodo.md).

Uso: python3 -u costi_in_r.py TF STOP_ATR [STOP_ATR ...]
Solo dati di costruzione (fino al 2023-01-16). Per ogni moneta: mediana di ATR di Wilder a 14 barre / chiusura;
costo di un giro = 2 x (commissione + slippage della scheda) / (STOP_ATR x quella mediana). Riporta la
distribuzione fra le monete. E' una descrizione dei dati, non il risultato di una strategia.
"""
import statistics
import sys
from datetime import date

from comune import RADICE_RICERCA, dati, schede

COMMISSIONE = 0.0005
FINE_COSTRUZIONE = date(2023, 1, 16)


def atr_relativi(candele, periodo=14):
    out, atr, somma = [], None, 0.0
    for k, b in enumerate(candele):
        tr = b.high - b.low if k == 0 else max(b.high - b.low, abs(b.high - candele[k - 1].close),
                                                abs(b.low - candele[k - 1].close))
        if k < periodo:
            somma += tr
            if k == periodo - 1:
                atr = somma / periodo
        else:
            atr = (atr * (periodo - 1) + tr) / periodo
        if atr is not None:
            out.append(atr / b.close)
    return out


if __name__ == "__main__":
    tf = sys.argv[1]
    moltiplicatori = [float(x) for x in sys.argv[2:]]
    mediane, costi_lato = {}, {}
    for s, scheda in schede().items():
        serie = dati.carica_serie_allineate(s, tf, scheda["primo_mese"], FINE_COSTRUZIONE, RADICE_RICERCA)
        rel = atr_relativi(serie["candele"])
        mediane[s] = statistics.median(rel)
        costi_lato[s] = COMMISSIONE + scheda["slippage_per_lato"]
    valori = sorted(mediane.values())
    print(f"{tf}: ATR14/chiusura, mediana per moneta: min {valori[0]:.4f}, decimo {valori[len(valori)//10]:.4f}, "
          f"mediana {statistics.median(valori):.4f}, novantesimo {valori[9*len(valori)//10]:.4f}, max {valori[-1]:.4f}")
    for m in moltiplicatori:
        costi = sorted(2 * costi_lato[s] / (m * mediane[s]) for s in mediane)
        print(f"stop {m} ATR: distanza mediana {m*statistics.median(valori):.2%}; costo di un giro in R: "
              f"mediana {statistics.median(costi):.3f}, novantesimo {costi[9*len(costi)//10]:.3f}, max {costi[-1]:.3f}")
