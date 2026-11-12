"""Backlog P34 (12 novembre 2026): lo Sharpe corretto per famiglie con il mazzo di prima (fermo alla prova 102, `asticella.py` al
commit 366d72c), con quello pubblicato alle 13 (commit 78235da) e con il mazzo corretto dopo la revisione
(`audits/reports/2026-11-12-MAZZO_ASTICELLA.md`): G1, G1 a 280 USDT, F5 + M7 + K2, C3 e le tre varianti della prova 152. Stessa
formula, stesso taglio, N = famiglie e V con l'aggiunta del 23 ottobre; i tagli 0,3 e 0,7 accanto (ASTICELLA.md, sezioni 3 e 4).
In piu', per una decisione di metodo del proprietario: G1 contando le prove fino alla 57, fino alla 57 piu' le varianti della sua
famiglia provate dopo, fino alla 148, tutte. Le misure delle candidate vengono dagli esiti dei loro esami (`audits/repro/...`,
`programma7/risultati_novantesima/risultati.json`).

Uso: python3 -m research.programma6.mazzo_asticella   (qualche minuto; scrive risultati_asticella/mazzo_12_novembre.json)
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import terza as te

QUI = Path(__file__).parent
RADICE = QUI.parents[1]
COMMIT_DI_PRIMA, COMMIT_PUBBLICATO = "366d72c", "78235da"
K = ("sharpe", "settimane", "asimmetria", "curtosi")


def asticella_del_commit(commit: str):
    testo = subprocess.run(["git", "show", f"{commit}:research/programma6/asticella.py"], cwd=RADICE, check=True,
                           capture_output=True, text=True).stdout
    f = Path(tempfile.mkdtemp()) / f"asticella_{commit}.py"
    f.write_text(testo, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"asticella_{commit}", f)
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


def conto(prove: list, nuove: dict, soli_in_piu: list, cand: dict, taglio: float = ast.TAGLIO) -> dict:
    serie = {n: ast.periodo(s) for n, s, _ in prove if s is not None}
    serie.update({n: ast.periodo(s) for n, s in nuove.items()})
    soli = [x for _, s, x in prove if s is None] + list(soli_in_piu)
    gr = ast.gruppi(serie, taglio)
    sr_g, sr_v = ast.per_v(gr, soli, False), ast.per_v(gr, soli, True)
    return {"serie": len(serie), "senza_serie": len(soli), "famiglie": len(sr_g), "in_V": len(sr_v),
            "deviazione_V": round(float(np.std(sr_v, ddof=1)), 4),
            "corretto": {n: round(te.sharpe_corretto(*a, sr_v, 52, n_prove=len(sr_g)), 4) for n, a in cand.items()},
            "gruppo_di_G1": next(g["membri"] for g in gr if "57 G1" in g["membri"])}


def esegui(log=print) -> dict:
    cand = candidate()
    g1 = {k: v for k, v in cand.items() if k in ("G1", "G1 a 280 USDT (A)")}
    prove = ast.le_prove()
    prima, pubblicato = asticella_del_commit(COMMIT_DI_PRIMA).serie_nuove(), asticella_del_commit(COMMIT_PUBBLICATO).serie_nuove()
    nuove, senza = ast.serie_nuove(), ast.senza_serie()
    s152 = pd.read_csv(RADICE / "research/programma7/risultati_novantesima/settimane_conto1.csv.gz", index_col=0)
    v152 = {f"152 {v}": s152[v] for v in ("V1", "V2", "V3")}
    numero = lambda n: int(n.split()[0])                                     # noqa: E731
    out = {"senza_serie": senza, "scenari": {}, "metodo_G1": {}}

    def scrivi(dove, nome, r):
        out[dove][nome] = r
        log(f"{nome}: serie {r['serie']}, senza serie {r['senza_serie']}, famiglie {r['famiglie']}, in V {r['in_V']}; "
            + ", ".join(f"{n} {v:.3f}" for n, v in r["corretto"].items()))

    scrivi("scenari", "prima (366d72c)", conto(prove, prima, [], cand))
    scrivi("scenari", "prima, con le tre serie della 152", conto(prove, {**prima, **v152}, [], cand))
    scrivi("scenari", "pubblicato (78235da)", conto(prove, pubblicato, [], cand))
    soli = [sr for _, sr in senza]
    for taglio in (ast.TAGLIO,) + ast.ALTRI_TAGLI:
        scrivi("scenari", f"corretto, taglio {taglio}", conto(prove, nuove, soli, cand, taglio))
    # la stessa cosa con la funzione dell'esame (controllo che corretto_famiglie dia lo stesso numero)
    cf = ast.corretto_famiglie({}, {n: dict(zip(K, a)) for n, a in cand.items()})
    out["corretto_famiglie"] = {n: round(c["corretto"], 4) for n, c in cf["candidate"].items()}
    # la domanda di metodo (G1): quali prove contare
    fam = out["scenari"][f"corretto, taglio {ast.TAGLIO}"]["gruppo_di_G1"]
    dopo57 = [n for n in fam if n.split()[0].isdigit() and numero(n) > 57]
    out["varianti_della_famiglia_di_G1_dopo_la_57"] = dopo57
    fino = lambda k: ({n: s for n, s in nuove.items() if numero(n) <= k}, [sr for n, sr in senza if numero(n) <= k])  # noqa: E731
    s57, z57 = fino(57)
    scrivi("metodo_G1", "fino alla 57", conto(prove, s57, z57, g1))
    scrivi("metodo_G1", "fino alla 57 piu' le varianti della famiglia di G1 provate dopo",
           conto(prove, {**s57, **{n: nuove[n] for n in dopo57}}, z57, g1))
    scrivi("metodo_G1", "fino alla 148", conto(prove, *fino(148), g1))
    out["metodo_G1"]["tutte"] = {k: out["scenari"][f"corretto, taglio {ast.TAGLIO}"][k] for k in ("serie", "famiglie", "in_V")}
    out["metodo_G1"]["tutte"]["corretto"] = {k: out["scenari"][f"corretto, taglio {ast.TAGLIO}"]["corretto"][k] for k in g1}
    # la 152 come l'ha calcolata la prova: corretto_rivisto con le sole sue tre serie (mazzo fino alla 48)
    cr = ast.corretto_rivisto(v152, {f"152 {v}": dict(zip(K, cand[f"152 {v}"])) for v in ("V1", "V2", "V3")})
    out["152_come_nella_prova"] = {"famiglie": cr["gruppi"], **{n: {"V_tutti": round(c["corretto"], 4),
                                                                  "V_con_aggiunta": round(c["corretto_con_aggiunta"], 4)}
                                                              for n, c in cr["candidate"].items()}}
    ast.RIS.mkdir(exist_ok=True)
    (ast.RIS / "mazzo_12_novembre.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
