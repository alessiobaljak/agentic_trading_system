"""I numeri di `ESAME_NUMERI_2026-11-27_REGOLA_NUOVA.md`: l'esame in vigore dal 27 novembre 2026 (ASTICELLA.md, sezione 7) per le prove
162-169 e le strategie del paper (G1, G1 neutra, G11, F5, F5 + M7 + K2), sul mazzo di oggi e, per G1, sul mazzo fino alla 57; lo
Sharpe che serve. Solo lettura dei risultati; scrive `risultati_asticella/esame_27_novembre.json` e stampa un riassunto corto.

Uso: python3 -m research.programma6.esame_27_novembre
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

from research.programma6 import asticella as ast

QUI = Path(__file__).parent
RADICE = QUI.parent.parent
PROVE = ["162 A", "162 B", "163 A", "163 B", "165 A", "165 B", "168 A", "168 B", "169 A", "169 B"]
PAPER = ["57 G1", "88 G1N", "69 G11", "24 F5", "28 F5+M7+K2"]
SETTIMANE = (300, 150, 100, 52, 22)


def candidate() -> dict:
    """Le candidate: le serie del mazzo, piu' la miscela con la misura del suo riesame (251 settimane fino al 19 ottobre, funding vero)
    e G1 con la misura del 12 novembre (quella dello 0,945)."""
    p28 = json.loads((RADICE / "audits/repro/prova28_2026-11-11_esito.json").read_text())
    p28 = p28["misure"]["fino_al_2026-10-19_funding_vero"]["F5 + M7 + K2"]
    g1 = json.loads((RADICE / "audits/repro/g1_parte2_2026-11-12_esito_misure.json").read_text())["misure"]["G1"]
    out = {n: None for n in PROVE + PAPER}
    out["miscela riesame"] = {**{k: float(p28[k]) for k in ("sharpe", "settimane", "asimmetria", "curtosi", "annuo")},
                              "serie": "28 F5+M7+K2"}
    out["G1 misura 12 novembre"] = {**{k: float(g1[k]) for k in ("sharpe", "settimane", "asimmetria", "curtosi")}, "serie": "57 G1"}
    return out


def fortuna(v: list, n: int) -> float:
    """Lo Sharpe l'anno che N prove senza vantaggio danno per caso (il massimo atteso con la dispersione di V)."""
    g = 0.5772156649
    return float(np.std(v, ddof=1)) * ((1 - g) * stats.norm.ppf(1 - 1 / n) + g * stats.norm.ppf(1 - 1 / (n * math.e)))


def esegui(log=print) -> dict:
    cand = candidate()
    R = ast.esame(candidate=cand, base=ast.mazzo(fino_alla=169))
    R57 = ast.esame(candidate={"G1 misura 12 novembre": cand["G1 misura 12 novembre"], "57 G1": None}, base=ast.mazzo(fino_alla=57))
    iv, nu = R["in_vigore"], R["non_ufficiali"]
    r_g1 = R["candidate"]["57 G1"]["in_vigore"]["rapporto"]
    mazzi = {"regola nuova": (iv["v"], iv["famiglie"], 1.0), "regola nuova, settimane legate come G1": (iv["v"], iv["famiglie"], r_g1),
             "(a) regola nuova senza 157, 159, 161": (nu["a_senza_incasso_fisso"]["v"], nu["a_senza_incasso_fisso"]["famiglie"], 1.0),
             "regola fino al 27 novembre": (nu["regola_fino_al_27_novembre"]["v"], nu["regola_fino_al_27_novembre"]["famiglie"], 1.0)}
    soglie = {k: {"famiglie": n, "in_v": len(v), "deviazione_v": float(np.std(v, ddof=1)), "fortuna": fortuna(v, n), "rapporto": r,
                  "sharpe_per_0_80": {w: ast.sharpe_minimo(w, v, n, rapporto=r) for w in SETTIMANE},
                  "sharpe_per_t_3": {w: 3 * math.sqrt(52 / (w * r)) for w in SETTIMANE}} for k, (v, n, r) in mazzi.items()}

    def senza_v(d: dict) -> dict:
        return {k: x for k, x in d.items() if k != "v"}

    out = {k: {"in_vigore": senza_v(r["in_vigore"]), "non_ufficiali": {n: senza_v(x) for n, x in r["non_ufficiali"].items()},
               "candidate": r["candidate"]} for k, r in (("oggi", R), ("fino_alla_57", R57))}
    out["sharpe_che_serve"] = soglie
    ast.RIS.mkdir(exist_ok=True)
    (ast.RIS / "esame_27_novembre.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    log(f"mazzo di oggi: N {iv['famiglie']}, in V {iv['in_v']}, deviazione {iv['deviazione_v']:.4f}")
    for nome, c in list(R["candidate"].items()) + [(f"{k} (mazzo fino alla 57)", c) for k, c in R57["candidate"].items()]:
        i, p = c["in_vigore"], c["non_ufficiali"]["regola_fino_al_27_novembre"]
        log(f"{nome}: {i['probabilita']:.3f} t {i['t']:.2f} ({i['settimane_efficaci']} sett.) {i['esito'][:15]} "
            f"| prima {p['probabilita']:.3f}")
    return out


if __name__ == "__main__":
    esegui()
