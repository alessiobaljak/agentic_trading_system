"""Audit della prova 28 (11 novembre 2026): la miscela F5 + M7 + K2 (un solo conto, posizioni compensate) e K2 da sola con un
capitale dichiarato e i filtri del conto vero (`bot/portafoglio/filtri_conto_vero.json`, 6 novembre 2026).

Ogni lunedi' all'apertura: obiettivo = peso x capitale; la variazione si fa solo se vale almeno il valore minimo della moneta
e la quantita' si arrotonda al passo; una posizione da chiudere si chiude sempre (ipotesi favorevole: ordine di sola
riduzione accettato sotto il minimo, DA VERIFICARE con Binance). Monete senza filtro oggi (tolte dal listino): minimo 5 USDT,
senza passo (ipotesi favorevole). Il capitale si compone, o resta fisso ("fissi": ogni settimana si riparte dallo
stesso capitale, come un conto che parte oggi). Costi, funding e rendimenti come la prova.

Solo lettura della ricerca. Scrive solo ``audits/repro/prova28_conto_vero_2026-11-11_esito.json``.

Uso: python3 audits/repro/prova28_conto_vero_2026-11-11.py <cartella_m7>
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from research.programma6 import quindicesima as qd  # noqa: E402
from research.programma6 import seconda as sc  # noqa: E402
from research.programma6 import terza as te  # noqa: E402
from research.programma6 import undicesima as un  # noqa: E402

a28 = importlib.import_module("prova28_2026-11-11")
QUI = Path(__file__).parent


def simula(pan, ps, Wc, capitale, costo, filtri, composto=True) -> pd.Series:
    O = pan["open"]
    lun = ps["lunedi"] - pan["t0"]
    R0 = np.nan_to_num(ps["R"])
    F = ps["F"]
    sett = np.flatnonzero((ps["lunedi"] >= a28.INIZIO) & (ps["lunedi"] <= a28.FINE_FUNDING_VERO))
    E = float(capitale)
    n = np.zeros(Wc.shape[1])                 # valore delle posizioni (USDT, con il segno)
    netti, saltati, totali = [], 0, 0
    for w in sett:
        m = lun[w]
        t = Wc[w] * E
        spese = 0.0
        for j in np.flatnonzero((np.abs(t - n) > 1e-12)):
            totali += 1
            f = filtri.get(ps["simboli"][j], {"passo": 0.0, "valore_minimo": 5.0})
            p = O[m, j]
            if t[j] == 0:
                spese += abs(n[j]) * costo[j]
                n[j] = 0.0
                continue
            d = t[j] - n[j]
            if not np.isfinite(p) or p <= 0 or abs(d) < f["valore_minimo"]:
                saltati += 1
                continue
            qd_ = d / p
            if f["passo"] > 0:
                qd_ = round(qd_ / f["passo"]) * f["passo"]
            if qd_ == 0 or abs(qd_ * p) < f["valore_minimo"]:
                saltati += 1
                continue
            spese += abs(qd_ * p) * costo[j]
            n[j] += qd_ * p
        lordo = float((n * R0[w]).sum())
        fund = float((n * F[w]).sum())
        r = (lordo - spese - fund) / E
        netti.append(r)
        E = E * (1 + r) if composto else float(capitale)
        n = n * (1 + R0[w])
        if E <= 0:
            break
    s = pd.Series(netti, index=ps["lunedi"][sett][:len(netti)])
    s.attrs["saltati"] = saltati / max(totali, 1)
    return s


def main(cartella: Path) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    pm = un.pannello_metrics(pan)
    costo = sc.costi_moneta(ps["simboli"])
    Pm = np.load(cartella / "Pm.npy")
    W, _ = a28.tre_pesi(pan, ps, pm, Pm, costo)
    comp = {n: a28.conto(W[n], ps, costo) for n in W}
    tre = qd.combina({"F5": comp["F5"], "M7": comp["M7"], "K2": comp["K2"]})
    pesi = tre[["peso_F5", "peso_M7", "peso_K2"]].rename(columns=lambda c: c[5:])
    Wc = a28.pesi_insieme(W, pesi)
    filtri = json.loads((a28.RADICE / "bot" / "portafoglio" / "filtri_conto_vero.json").read_text())["filtri"]
    ideale = a28.periodo(a28.conto(Wc, ps, costo), a28.FINE_FUNDING_VERO)["netto"]
    out = {"ideale_un_solo_conto": {"sharpe": a28.sharpe(ideale), "annuo": round(float(ideale.mean() * 52), 4)}}
    for nome, Wx in (("F5 + M7 + K2 un solo conto", Wc), ("K2", W["K2"])):
        for cap in (280, 1000, 10000):
            s = simula(pan, ps, Wx, cap, costo, filtri)
            mm = a28.misure(s)
            out[f"{nome}, {cap} USDT"] = {"sharpe": mm["sharpe"], "annuo": mm["annuo"], "discesa_max": mm["discesa_max"],
                                          "per_anno": mm["per_anno"], "variazioni_saltate": round(s.attrs["saltati"], 3)}
            s2 = simula(pan, ps, Wx, cap, costo, filtri, composto=False)
            m2 = a28.misure(s2)
            out[f"{nome}, {cap} USDT fissi"] = {"sharpe": m2["sharpe"], "annuo": m2["annuo"], "per_anno": m2["per_anno"],
                                                "variazioni_saltate": round(s2.attrs["saltati"], 3)}
    (QUI / "prova28_conto_vero_2026-11-11_esito.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    o = main(Path(sys.argv[1]))
    for k, v in o.items():
        print(k, json.dumps(v, ensure_ascii=False))
