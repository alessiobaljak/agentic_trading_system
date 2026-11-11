"""Audit della prova 28 (11 novembre 2026): tre controlli fatti a mano durante l'audit, rieseguibili.

1. I giorni che mancano nell'archivio (26-28 febbraio e 1-2 aprile 2022, circa 48 monete): il movimento fra l'ultima chiusura
   prima del buco e la prima apertura dopo si perde, e la moneta esce dall'universo del lunedi' dopo (uscita implicita
   all'ultima chiusura). Rendimento perso per settimana, con i pesi di K2 e di F5.
2. K2 e F5 con i segnali a 6 e 8 giorni: rendimento per anno.
3. Discesa piu' grande e piu' lunga di K2 e della miscela, con le date.

Uso: python3 audits/repro/prova28_buchi_2026-11-11.py <cartella_m7>
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from research.programma6 import quindicesima as qd  # noqa: E402
from research.programma6 import seconda as sc  # noqa: E402
from research.programma6 import terza as te  # noqa: E402
from research.programma6 import undicesima as un  # noqa: E402

a28 = importlib.import_module("prova28_2026-11-11")
QUI = Path(__file__).parent


def perso_nei_buchi(pan, ps, W) -> dict:
    C, O = pan["close"], pan["open"]
    T = C.shape[0]
    lun = ps["lunedi"] - pan["t0"]
    sett = np.flatnonzero(ps["lunedi"] >= a28.INIZIO)
    per_sett, dett = {}, []
    for w in sett:
        m = lun[w]
        for j in np.flatnonzero(W[w] != 0):
            pieno = np.isfinite(C[m:m + 7, j]).all() and (m + 7 >= T or np.isfinite(O[m + 7, j]))
            if pieno:
                continue
            dopo = [g for g in range(m + 7, min(T, m + 12)) if np.isfinite(O[g, j])]
            if not dopo:
                continue
            vero = O[dopo[0], j] / O[m, j] - 1
            d = float(W[w, j] * (vero - ps["R"][w, j]))
            k = sc.data(int(ps["lunedi"][w]))
            per_sett[k] = round(per_sett.get(k, 0.0) + d, 4)
            dett.append([round(d, 4), ps["simboli"][j], k])
    return {"per_settimana": per_sett, "piu_grandi": sorted(dett, key=lambda x: -abs(x[0]))[:5]}


def discese(x) -> dict:
    eq = np.cumprod(1 + x.to_numpy())
    pk = np.maximum.accumulate(eq)
    dd = eq / pk - 1
    i = int(dd.argmin())
    p = int(np.flatnonzero(eq[:i + 1] == pk[i])[-1])
    r = np.flatnonzero(eq[i:] >= pk[i])
    lunga, cur, st, da, a = 0, 0, 0, 0, 0
    for k, s in enumerate(eq < pk):
        if s:
            st = k if cur == 0 else st
            cur += 1
            if cur > lunga:
                lunga, da, a = cur, st, k
        else:
            cur = 0
    d = lambda k: sc.data(int(x.index[k]))
    return {"piu_grande": round(float(dd[i]), 3), "picco": d(p), "fondo": d(i), "recupero": d(i + int(r[0])) if len(r) else "mai",
            "piu_lunga_settimane": lunga, "piu_lunga_da": d(da), "piu_lunga_a": d(a)}


def main(cartella: Path) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    pm = un.pannello_metrics(pan)
    costo = sc.costi_moneta(ps["simboli"])
    Pm = np.load(cartella / "Pm.npy")
    W, _ = a28.tre_pesi(pan, ps, pm, Pm, costo)
    out = {"buchi": {n: perso_nei_buchi(pan, ps, W[n]) for n in ("K2", "F5")}}
    out["segnali_6_e_8_giorni"] = {}
    for k in (6, 8):
        W2, _ = a28.tre_pesi(pan, ps, pm, None, costo, k=k)
        for n in ("K2", "F5"):
            x = a28.periodo(a28.conto(W2[n], ps, costo), a28.FINE_FUNDING_VERO)["netto"]
            out["segnali_6_e_8_giorni"][f"{n} {k} giorni"] = {"sharpe": a28.sharpe(x), "per_anno": a28.misure(x)["per_anno"]}
    c = {n: a28.conto(W[n], ps, costo) for n in W}
    t = qd.combina({"F5": c["F5"], "M7": c["M7"], "K2": c["K2"]})
    out["discese"] = {"K2": discese(a28.periodo(c["K2"], a28.FINE_FUNDING_VERO)["netto"]),
                      "F5 + M7 + K2": discese(a28.periodo(t, a28.FINE_FUNDING_VERO)["netto"])}
    (QUI / "prova28_buchi_2026-11-11_esito.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    print(json.dumps(main(Path(sys.argv[1])), ensure_ascii=False)[:2500])
