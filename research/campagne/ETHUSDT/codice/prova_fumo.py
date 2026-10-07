"""Prova di funzionamento del codice comune, SENZA registrare nulla nel log e senza guardare
metriche di vantaggio: controlla solo che motore, strategia, baseline e bootstrap girino
e che il numero di trade sia nell'ordine della stima. Si lancia su un pezzo corto di dati
(primi 90 giorni del 2020, 1h) con segnali casuali fissi."""
from __future__ import annotations

import sys
import time
from datetime import date
from pathlib import Path

import numpy as np

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import comune  # noqa: E402
from comune import Uscita  # noqa: E402

t0 = time.time()
s = comune.serie("1h", date(2020, 1, 1), date(2020, 3, 31), con_btc=True)
print("barre 1h:", len(s.ts), "mark allineate:", len(s.mark), "funding:", len(s.funding), "btc nan:", int(np.isnan(s.btc_close).sum()))
atr_serie = comune.atr(s, 14)
rng = np.random.default_rng(0)
segn = np.where(rng.random(len(s.ts)) < 0.02, 1, 0)
usc = Uscita(k_atr=2.0, h_barre=4)
strat = comune.costruisci_strategia(s, segn, usc, atr_serie, 20, len(s.ts))
ris = comune.esegui(s, strat)
print("segnali:", int(segn[20:].sum()), "stima:", comune.stima_trade(segn, 4, 20, len(s.ts)), "trade:", len(ris.trades),
      "esiti:", {k: v for k, v in comune.riassunto(ris, s)["esiti"].items() if v})
print("blocco:", comune.lunghezza_blocco(ris), "durate ore:", comune.riassunto(ris, s)["durata_media_ore"])
bl = comune.baseline_casuale(s, 1, usc, atr_serie, 20, len(s.ts), len(ris.trades), 3, n_strategie=5, seme=1)
print("baseline casuale: 5 strategie, r medi calcolati:", len(bl["r_medi"]), "serie mediana trade:", len(bl["serie_mediana"]))
print("confronto netto:", comune.confronto_netto(comune.serie_r(ris), bl["serie_mediana"], comune.lunghezza_blocco(ris)))
bla = comune.baseline_ogni_barra(s, 1, usc, atr_serie, 20, len(s.ts))
print("baseline ogni barra trade:", len(bla.trades), "attesi circa", (len(s.ts) - 20) // 5)
print("buy and hold:", comune.buy_and_hold(s, 20, len(s.ts)))
# controllo di causalita': il segnale in i non deve dipendere da barre > i. Tronco la serie e confronto gli indicatori.
r_full = comune.rsi(s.close, 2)
r_tronca = comune.rsi(s.close[:500], 2)
print("rsi causale:", bool(np.allclose(np.nan_to_num(r_full[:500]), np.nan_to_num(r_tronca))))
a_full = comune.atr(s, 14)
print("tempo:", round(time.time() - t0, 1), "s")
