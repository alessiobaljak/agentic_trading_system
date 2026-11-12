"""Backlog P34 (12 novembre 2026): lo Sharpe corretto per famiglie con il mazzo di prima (fermo alla prova 102, `asticella.py` al
commit 366d72c) e con il mazzo completo (`asticella.py` di oggi), per G1, G1 a 280 USDT, F5 + M7 + K2, C3 e le tre varianti della
prova 152. Stessa formula, stesso taglio, stesso modo di contare (N = famiglie, V con l'aggiunta del 23 ottobre); cambia solo il mazzo.
Le misure delle candidate vengono dagli esiti dei loro esami (`audits/repro/...`, `programma7/risultati_novantesima/risultati.json`).

Uso: python3 -m research.programma6.mazzo_asticella   (qualche minuto; scrive risultati_asticella/mazzo_12_novembre.json)
"""
from __future__ import annotations

import importlib.util
import json
import math
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import terza as te

QUI = Path(__file__).parent
RADICE = QUI.parents[1]
COMMIT_DI_PRIMA = "366d72c"
K = ("sharpe", "settimane", "asimmetria", "curtosi")
PRIMA_DELLA_103_A_PORTAFOGLIO = ("50", "77", "79", "80", "85", "87")


def asticella_di_prima():
    testo = subprocess.run(["git", "show", f"{COMMIT_DI_PRIMA}:research/programma6/asticella.py"], cwd=RADICE, check=True,
                           capture_output=True, text=True).stdout
    f = Path(tempfile.mkdtemp()) / "asticella_prima.py"
    f.write_text(testo, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("asticella_prima", f)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.QUI = QUI                                      # i file dei risultati restano quelli del repository
    return m


def candidate() -> dict:
    au, p7 = RADICE / "audits" / "repro", RADICE / "research" / "programma7"
    mis = json.loads((au / "g1_parte2_2026-11-12_esito_misure.json").read_text())["misure"]
    p28 = json.loads((au / "prova28_2026-11-11_esito.json").read_text())["misure"]
    b55 = json.loads((au / "prova55_2026-11-12_esito_base.json").read_text())
    b55 = b55.get("base", b55)["misure_C3_corretta_dichiarato"]
    r152 = json.loads((p7 / "risultati_novantesima" / "risultati.json").read_text())["varianti"]
    out = {"G1": [mis["G1"][x] for x in K], "G1 a 280 USDT (A)": [mis["A280"][x] for x in K],
           "F5 + M7 + K2 al 12 ottobre": [p28["fino_al_2026-10-12"]["F5 + M7 + K2"][x] for x in K],
           "F5 + M7 + K2 al 19 ottobre": [p28["fino_al_2026-10-19_funding_vero"]["F5 + M7 + K2"][x] for x in K],
           "C3 corretta al 5 ottobre": [b55[x] for x in K]}
    out.update({f"152 {v}": [r152[v]["conto1"]["numeri_settimana_corretto"][x] for x in K] for v in ("V1", "V2", "V3")})
    return out


def conto(prove: list, nuove: dict, cand: dict) -> dict:
    serie = {n: ast.periodo(s) for n, s, _ in prove if s is not None}
    serie.update({n: ast.periodo(s) for n, s in nuove.items()})
    soli = [x for _, s, x in prove if s is None]
    gr = ast.gruppi(serie, ast.TAGLIO)
    sr_g, sr_v = ast.per_v(gr, soli, False), ast.per_v(gr, soli, True)
    return {"serie": len(serie), "soli": len(soli), "famiglie": len(sr_g), "in_V": len(sr_v),
            "deviazione_V": round(float(np.std(sr_v, ddof=1)), 4),
            "corretto": {n: round(te.sharpe_corretto(*a, sr_v, 52, n_prove=len(sr_g)), 4) for n, a in cand.items()},
            "gruppo_di_G1": next(g["membri"] for g in gr if "57 G1" in g["membri"]),
            "fuori_da_V": [[g["membri"], round(g["sharpe"], 2)] for g in gr
                           if g["sharpe"] * math.sqrt(g["settimane"] / 52) < ast.T_PERDENTI]}


def esegui(log=print) -> dict:
    cand = candidate()
    prove = ast.le_prove()
    vecchie = asticella_di_prima().serie_nuove()
    nuove = ast.serie_nuove()
    s152 = pd.read_csv(RADICE / "research/programma7/risultati_novantesima/settimane_conto1.csv.gz", index_col=0)
    v152 = {f"152 {v}": s152[v] for v in ("V1", "V2", "V3")}
    aggiunte = [n for n in nuove if n not in vecchie]
    prima_103 = [n for n in aggiunte if int(n.split()[0]) < 103]
    out = {"aggiunte": aggiunte, "aggiunte_prima_della_103": prima_103, "scenari": {}}
    scenari = {"prima": vecchie, "prima, con le tre serie della 152": {**vecchie, **v152}, "dopo": nuove,
               "dopo, senza le 60 della 149": {n: s for n, s in nuove.items() if not n.startswith("149 ")},
               "dopo, senza le 17 prove prima della 103": {n: s for n, s in nuove.items() if n not in prima_103},
               "dopo, senza le 6 a portafoglio prima della 103": {n: s for n, s in nuove.items()
                                                                if n.split()[0] not in PRIMA_DELLA_103_A_PORTAFOGLIO},
               "dopo, senza la 147 (8 settimane)": {n: s for n, s in nuove.items() if n != "147 GA2C"}}
    for nome, mazzo in scenari.items():
        out["scenari"][nome] = r = conto(prove, mazzo, cand)
        log(f"{nome}: serie {r['serie']}, famiglie {r['famiglie']}, in V {r['in_V']}; "
            + ", ".join(f"{n} {v:.3f}" for n, v in r["corretto"].items()))
    # la 152 come l'ha calcolata la prova: corretto_rivisto con le sole sue tre serie (non legge serie_nuove)
    cr = ast.corretto_rivisto(v152, {f"152 {v}": dict(zip(K, cand[f"152 {v}"])) for v in ("V1", "V2", "V3")})
    out["152_come_nella_prova"] = {"famiglie": cr["gruppi"], **{n: {"V_tutti": round(c["corretto"], 4),
                                                                  "V_con_aggiunta": round(c["corretto_con_aggiunta"], 4)}
                                                              for n, c in cr["candidate"].items()}}
    log(f"152 come nella prova ({cr['gruppi']} famiglie): "
        + ", ".join(f"{n} {c['V_tutti']:.3f}" for n, c in out["152_come_nella_prova"].items() if n != "famiglie"))
    ast.RIS.mkdir(exist_ok=True)
    (ast.RIS / "mazzo_12_novembre.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
