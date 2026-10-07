"""Fase 4: verifiche sui dati di costruzione per una variante sopravvissuta alla Fase 2.

Uso: python -m research.campagne.SOLUSDT.codice.fase4 NOME ID_VARIANTE
Scrive PRIMA una registrazione di tipo verifica (con verifica_di = id della
variante) per ogni prova, poi la esegue e scrive il risultato. Le prove:
robustezza dei parametri (vicinato), timeframe adiacenti, regola intra-barra
opposta, ritardo di una barra, costi doppi, trade vicini ai buchi dei dati.
"""
import json
import sys
from pathlib import Path

import numpy as np

from research.campagne.SOLUSDT.codice import campagna as cp, strategie as st
from research.campagne.SOLUSDT.codice.varianti import VARIANTI, regola

sys.path.insert(0, str(Path(__file__).resolve().parent))
import log  # noqa: E402

ADIACENTI = {"15m": ["30m"], "30m": ["15m", "1h"], "1h": ["30m", "2h"], "2h": ["1h", "4h"], "4h": ["2h", "6h"],
             "6h": ["4h", "8h"], "8h": ["6h", "12h"], "12h": ["8h", "1d"], "1d": ["12h"]}

# buchi dei dati (fase0_dati.md), in ms UTC: inizio e fine
BUCHI = [("2022-02-26", "2022-03-01"), ("2022-04-01", "2022-04-03"), ("2021-07-01", "2021-07-02"),
         ("2021-07-24", "2021-07-28"), ("2022-10-02", "2022-10-03"), ("2023-02-24", "2023-02-25")]


def _ms(g):
    from datetime import datetime, timezone
    return int(datetime.strptime(g, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)


def compatto(ris):
    r = cp.riassunto(ris)
    return {k: r[k] for k in ("trade", "profit_factor", "r_medio", "r_mediano", "win_rate", "rendimento_totale",
                              "drawdown_max", "r_medio_per_anno", "esiti", "violazioni_liquidazione", "ridotti")}


def vicinato(nome):
    """Parametri vicini: ogni parametro numerico della regola x0,75 e x1,25 (interi arrotondati)."""
    idea, tf, direzione, costruttore, _ = VARIANTI[nome]
    base = {k: v for k, v in regola(nome).p.items() if k not in ("funding", "btc") and isinstance(v, (int, float)) and not isinstance(v, bool)}
    out = []
    for k, v in base.items():
        for f in (0.75, 1.25):
            nv = v * f
            if isinstance(v, int):
                nv = max(1, int(round(nv)))
            if nv == v:
                continue
            out.append((k, nv))
    return out


def costruisci(nome, periodo, **modifiche):
    idea, tf, direzione, costruttore, _ = VARIANTI[nome]
    r = costruttore(periodo)
    r.p = dict(r.p); r.p.update(modifiche)
    return r


def main(nome, id_variante):
    idea, tf, direzione, _, _ = VARIANTI[nome]
    periodo = cp.COSTRUZIONE
    prove = [
        ("robustezza", "i risultati reggono con ogni parametro numerico a x0,75 e x1,25? Si cerca un'area stabile: R medio dello stesso segno nella maggioranza dei vicini",
         "la maggioranza dei vicini ha R medio positivo e profit factor sopra 1"),
        ("timeframe_adiacenti", f"la stessa regola sui timeframe adiacenti {ADIACENTI[tf]}", "R medio positivo su almeno uno dei due; non serve per scegliere"),
        ("intrabarra_opposta", "regola target prima dello stop nella stessa barra", "differenza di R medio sotto 0,05 (il risultato non dipende dall'ordine ignoto)"),
        ("ritardo_1_barra", "esecuzione ritardata di una barra", "peggiora gradualmente: R medio ancora dello stesso segno o vicino a zero, non crollo sotto zero di oltre 0,1"),
        ("costi_doppi", "commissioni, slippage e funding (se costo) raddoppiati", "profit factor sopra 1 e R medio positivo"),
        ("vicino_ai_buchi", "togliere i trade aperti o chiusi entro 2 giorni dai buchi dei dati", "R medio invariato entro 0,02"),
    ]
    ids = {}
    for chiave, cosa, criterio in prove:
        voce = log.scrivi({"id": f"SOLUSDT-{log.prossimo_numero():03d}", "tipo": "registrazione", "tipo_test": "verifica",
                           "verifica_di": id_variante, "variante": nome, "verifica": chiave, "cosa": cosa,
                           "periodo": "costruzione", "criterio_successo": criterio, "fase": "4"})
        ids[chiave] = voce["id"]
    base = cp.esegui(st.fabbrica(regola(nome), direzione), tf, periodo)
    rb = compatto(base)
    # robustezza
    tab = []
    for k, nv in vicinato(nome):
        r = costruisci(nome, periodo, **{k: nv})
        ris = cp.esegui(st.fabbrica(r, direzione), tf, periodo)
        c = compatto(ris)
        tab.append({"parametro": k, "valore": nv, "trade": c["trade"], "r_medio": c["r_medio"], "profit_factor": c["profit_factor"]})
    positivi = sum(1 for t in tab if isinstance(t["r_medio"], float) and t["r_medio"] > 0)
    log.scrivi({"id": ids["robustezza"], "tipo": "risultato", "base": {"trade": rb["trade"], "r_medio": rb["r_medio"], "profit_factor": rb["profit_factor"]},
                "vicini": tab, "vicini_con_r_positivo": f"{positivi}/{len(tab)}"})
    # timeframe adiacenti
    adj = {}
    for tfa in ADIACENTI[tf]:
        r = VARIANTI[nome][3](periodo)
        ris = cp.esegui(st.fabbrica(r, direzione), tfa, periodo)
        adj[tfa] = compatto(ris)
    log.scrivi({"id": ids["timeframe_adiacenti"], "tipo": "risultato", "base": rb, "adiacenti": adj})
    # intrabarra opposta
    ris = cp.esegui(st.fabbrica(regola(nome), direzione), tf, periodo, intrabarra="target_prima")
    c = compatto(ris)
    log.scrivi({"id": ids["intrabarra_opposta"], "tipo": "risultato", "stop_prima": {"r_medio": rb["r_medio"], "profit_factor": rb["profit_factor"]},
                "target_prima": {"r_medio": c["r_medio"], "profit_factor": c["profit_factor"], "trade": c["trade"]},
                "differenza_r_medio": round(c["r_medio"] - rb["r_medio"], 3)})
    # ritardo
    ris = cp.esegui(st.fabbrica(regola(nome), direzione), tf, periodo, ritardo=1)
    c = compatto(ris)
    log.scrivi({"id": ids["ritardo_1_barra"], "tipo": "risultato", "senza_ritardo": {"r_medio": rb["r_medio"], "profit_factor": rb["profit_factor"]},
                "con_ritardo": c, "differenza_r_medio": round(c["r_medio"] - rb["r_medio"], 3)})
    # costi doppi
    ris = cp.esegui(st.fabbrica(regola(nome), direzione), tf, periodo, moltiplicatore_costi=2.0)
    c = compatto(ris)
    log.scrivi({"id": ids["costi_doppi"], "tipo": "risultato", "costi_normali": {"r_medio": rb["r_medio"], "profit_factor": rb["profit_factor"]},
                "costi_doppi": c})
    # vicino ai buchi
    margine = 2 * 86_400_000
    finestre = [(_ms(a) - margine, _ms(b) + margine) for a, b in BUCHI]
    tenuti = [t for t in base.trades if not any(a <= t.ts_entrata <= b or a <= t.ts_uscita <= b for a, b in finestre)]
    r_t = float(np.mean([t.r for t in tenuti])) if tenuti else 0.0
    log.scrivi({"id": ids["vicino_ai_buchi"], "tipo": "risultato", "trade_tolti": len(base.trades) - len(tenuti),
                "r_medio_prima": rb["r_medio"], "r_medio_senza": round(r_t, 3)})
    print("fatto", nome, ids)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
