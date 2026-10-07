"""Fase 5, controllo positivo degli strumenti: una strategia con lookahead DICHIARATO deve
risultare un vantaggio enorme e netto, e il test del ritardo di una barra deve azzerarlo.

Non e' una variante (non e' un'idea da operare) e non consuma budget: serve a rispondere allo
scettico che chiede «e se i tuoi strumenti non fossero in grado di vedere un vantaggio?».
La strategia bara apposta: alla chiusura della barra i legge il close della barra i+1 (che
in realta' non conosce) ed entra nel suo verso, con la stessa uscita comune (stop 2 ATR,
H = 1 barra), su candele da 4h nel periodo di costruzione. Si confrontano baseline e
bootstrap come per le varianti vere; poi si rilancia con ritardo di una barra, che deve
distruggere il vantaggio (l'informazione rubata diventa inutile). Risultato in
risultati/controllo_positivo.json e in una voce nota del log.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import comune  # noqa: E402
from comune import Uscita  # noqa: E402
from log import aggiungi  # noqa: E402

s = comune.serie("4h", comune.INIZIO_DATI, comune.FINE_COSTRUZIONE)
atr_serie = comune.atr(s, 14)
da, a = 20, len(s.ts)
# segnale che BARA: usa il rendimento della barra successiva (dalla sua apertura alla sua chiusura)
r_futuro = np.full(len(s.ts), np.nan)
r_futuro[:-1] = s.close[1:] / s.open[1:] - 1.0
soglia = 0.01  # entra solo quando il futuro «noto» supera l'1 %, per avere qualche centinaio di trade
segn = np.where(r_futuro > soglia, 1, np.where(r_futuro < -soglia, -1, 0))
segn[~np.isfinite(r_futuro)] = 0
usc = Uscita(k_atr=2.0, h_barre=1)
out = {}
for nome_dir, direzione in (("long", 1), ("short", -1)):
    sg = np.where(segn == direzione, direzione, 0)
    strat = comune.costruisci_strategia(s, sg, usc, atr_serie, da, a)
    ris = comune.esegui(s, strat)
    m = comune.riassunto(ris, s)
    r_c = comune.serie_r(ris)
    blocco = comune.lunghezza_blocco(ris)
    cas = comune.baseline_casuale(s, direzione, usc, atr_serie, da, a, len(ris.trades), 1, n_strategie=200, seme=1)
    netto = comune.confronto_netto(r_c, cas["serie_mediana"], blocco, seme=5)
    pct = comune.percentile_di(float(np.mean(r_c)), cas["r_medi"])
    ris_rit = comune.esegui(s, strat, comune.parametri_motore(ritardo_barre=1))
    m_rit = comune.riassunto(ris_rit, s)
    out[nome_dir] = {"n": m["n_trade"], "pf": m["profit_factor"], "r_medio": m["r_medio"], "win_rate": m["win_rate"],
                     "percentile_caso": pct, "netto_vs_caso": netto,
                     "con_ritardo_1_barra": {"n": m_rit["n_trade"], "pf": m_rit["profit_factor"], "r_medio": m_rit["r_medio"], "win_rate": m_rit["win_rate"]}}
    print(nome_dir, json.dumps(out[nome_dir], default=str))

(QUI.parent / "risultati" / "controllo_positivo.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
ok = all(v["netto_vs_caso"]["netta"] and v["netto_vs_caso"]["segno"] > 0 and v["percentile_caso"] >= 99 and v["con_ritardo_1_barra"]["pf"] < 1.1 for v in out.values())
aggiungi({"id": "ETHUSDT-N009", "tipo": "nota", "oggetto": "Fase 5, controllo positivo degli strumenti (strategia con lookahead dichiarato, non e' una variante)",
          "testo": ("Una strategia che bara leggendo il close della barra successiva, con la stessa uscita comune e le stesse baseline delle varianti vere, "
                    "deve risultare nettamente sopra le entrate casuali e crollare con il ritardo di una barra. " +
                    ("Esito: SI', gli strumenti vedono un vantaggio quando c'e' e il test del ritardo lo smaschera." if ok else
                     "Esito: NO, qualcosa negli strumenti non funziona: da indagare prima di qualunque conclusione.")),
          "risultati": out, "controllo_superato": ok})
print("controllo superato:", ok)
