"""Prova meccanica degli strumenti della campagna (non e' un test di ipotesi).

Gira una regola banale (long ogni 20 barre, stop 2 ATR, uscita a 5 barre) su
1d e 1h in costruzione, per controllare: nessun errore, tempi, allineamento
delle serie, baseline costruibili, log scrivibile. I NUMERI NON SI USANO.
"""
from __future__ import annotations
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import strumenti as s
import dati_btc as d

for tf in ("1d", "1h"):
    t0 = time.time()
    serie = s.Serie(tf)
    entra = lambda i: "long" if i % 20 == 0 else None
    uscita = {"stop_atr": 2.0, "atr_n": 14, "max_barre": 5}
    stima = s.stima_trade(serie, entra, d.COSTRUZIONE, 5)
    out, ris = s.esamina(serie, entra, uscita, d.COSTRUZIONE, n_sim_caso=5, direzione_di=lambda i: "long")
    dt = time.time() - t0
    print(tf, "stima", stima, "| trade", out["metriche"]["n_trade"], "| esiti", out["metriche"]["esiti"], "| blocco", out["blocco_bootstrap"], f"| {dt:.1f}s")
    print("   baseline chiavi:", sorted(k for k in out if k.startswith("baseline")), "| sim caso n_trade medio", out["baseline_b_casuale"]["n_sim"])
    # controllo lookahead grossolano: con ritardo di 1 barra la strategia deve ancora girare
    out2, _ = s.esamina(serie, entra, uscita, d.COSTRUZIONE, parametri=d.parametri(ritardo_barre=1), con_baseline=False)
    print("   con ritardo 1 barra: trade", out2["metriche"]["n_trade"])

s.registra({"id": "BTCUSDT-F0-04", "tipo": "nota", "fase": "0",
            "oggetto": "prova meccanica degli strumenti della campagna (codice/strumenti.py, dati_btc.py)",
            "cosa": "regola banale (long ogni 20 barre, stop 2 ATR, uscita a 5 barre) su 1d e 1h in costruzione: nessun errore, baseline a/b/c costruibili, test del ritardo eseguibile",
            "nota": "i numeri di questa prova non sono un risultato e non si usano"})
