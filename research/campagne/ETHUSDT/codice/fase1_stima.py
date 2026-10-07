"""Fase 1, punto 7: stima dei trade per ogni variante, SOLO dai segnali sui dati di costruzione.

Per ogni idea e direzione conta i segnali nel periodo di costruzione con la regola di non
sovrapposizione (un segnale conta se dista dal precedente contato almeno H+1 barre).
Non esegue alcun backtest e non guarda alcun rendimento. Scrive il risultato in
fase1_stime.json e lo stampa; la registrazione nel log la fa fase2_registra.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import comune  # noqa: E402
import strategie  # noqa: E402

MINIMO_COSTRUZIONE = 100


class _PosizioneFinta:
    """Solo la direzione: basta alle regole di chiusura su segnale delle idee."""

    def __init__(self, direzione: str) -> None:
        self.direzione = direzione


def stima_con_uscita_segnale(sg: np.ndarray, uscita, da: int, a: int) -> int:
    """Seconda stima (aggiunta il 7 ott dopo la prima, vedi log ETHUSDT-C001): entra al primo
    segnale da piatto, esce quando la regola di chiusura su segnale dell'idea lo dice o dopo
    H barre. Usa solo segnali, mai prezzi di uscita ne' rendimenti; ignora gli stop, che
    potrebbero solo aumentare il conteggio (stima prudente)."""
    n, i, in_pos, i_entrata, pos = 0, da, False, -1, None
    while i < a:
        if not in_pos:
            if sg[i] != 0:
                in_pos, i_entrata, pos = True, i + 1, _PosizioneFinta("long" if sg[i] > 0 else "short")
                n += 1
        else:
            if i - i_entrata + 1 >= uscita.h_barre or (uscita.chiusura_segnale and i >= i_entrata and uscita.chiusura_segnale(i, pos)):
                in_pos = False
        i += 1
    return n


stime = {}
for codice, idea in strategie.IDEE.items():
    s = comune.serie(idea.timeframe, comune.INIZIO_DATI, comune.FINE_COSTRUZIONE, con_btc=idea.con_btc)
    segn, uscita, riscaldamento = idea.costruisci(s)
    da = max(riscaldamento, 0)
    a = len(s.ts)
    for direzione in idea.direzioni:
        nome = "long" if direzione > 0 else "short"
        sg = strategie.solo(segn, direzione)
        n_segnali = int(np.count_nonzero(sg[da:a]))
        n_stima = comune.stima_trade(sg, uscita.h_barre, da, a)
        n_stima2 = stima_con_uscita_segnale(sg, uscita, da, a) if uscita.chiusura_segnale else None
        decisiva = n_stima2 if n_stima2 is not None else n_stima
        stime[f"{codice}-{nome}"] = {
            "idea": codice, "direzione": nome, "timeframe": idea.timeframe,
            "barre_costruzione": int(a - da), "segnali": n_segnali,
            "trade_stimati_distanza_h": n_stima, "trade_stimati_uscita_segnale": n_stima2,
            "trade_stimati": decisiva,
            "h_barre": uscita.h_barre, "k_atr": uscita.k_atr, "rr_target": uscita.rr_target,
            "sotto_minimo": decisiva < MINIMO_COSTRUZIONE,
        }
        print(f"{codice} {nome:5s} {idea.timeframe:3s} barre {a - da:6d} segnali {n_segnali:6d} stima(distanza H) {n_stima:5d} stima(uscita segnale) {str(n_stima2):>5s}" + ("  <-- sotto 100" if decisiva < MINIMO_COSTRUZIONE else ""))

(QUI.parent / "fase1_stime.json").write_text(json.dumps(stime, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
