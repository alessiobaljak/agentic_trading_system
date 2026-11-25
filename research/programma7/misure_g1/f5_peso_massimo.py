"""Misura (25 nov 2026, domanda 180 di live-path-reviewer, voce P36 del backlog): il peso massimo per moneta e la somma dei pesi di F5
sul passato, al lunedi' e durante la settimana con le quantita' ferme (la deriva). Solo lettura: usa il motore di F5 corretto
(controllo_parita.py: stessi pesi W5, stesso pannello) e non cambia niente.

Convenzione del motore: il giorno t si tiene da apertura(t) ad apertura(t+1); la settimana va dall'apertura del lunedi' (giorno 0)
a quella del lunedi' dopo (giorno 7). Il conto del giorno d: 1 - spese del giro + guadagno dei prezzi fino a d (senza funding, che
sposta il conto di meno di mezzo punto a settimana). Peso vero della moneta i al giorno d = x_i * g_i(d) / conto(d), con g_i il
prezzo al giorno d diviso quello del lunedi'. Prezzi giornalieri di apertura: i picchi dentro il giorno non ci sono.

Uso: python3 -m research.programma7.misure_g1.f5_peso_massimo   (scrive f5_peso_massimo_risultati.json e _settimane.csv.gz)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq

QUI = Path(__file__).parent
LIM_MONETA, LIM_SOMMA = 0.60, 2.0
FINE = sc.giorno(2026, 10, 4)


def data(g) -> str:
    return str(pd.to_datetime(int(g) * 86400, unit="s").date())


def esegui() -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    costo = sc.costi_moneta(ps["simboli"])
    W5 = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, lun), np.nan), ps["U"], sig)
    df = te.conto(W5, ps["R"], ps["F"], costo)
    sim = ps["simboli"]
    r = np.log1p(np.clip(sc.rendimenti(pan), -0.999999, None))
    cum = np.vstack([np.zeros((1, r.shape[1])), np.cumsum(r, axis=0)])
    righe, eventi = [], []
    for k, m in enumerate(lun):
        g0 = int(ps["lunedi"][k])
        if g0 < se.INIZIO or g0 > FINE:
            continue
        x = W5[k]
        if not (x != 0).any():
            continue
        spese = float(df["spese"].iloc[k])
        g = np.exp(cum[m: m + 8] - cum[m])                  # (8, monete): giorno 0..7
        g = np.where(np.isfinite(g), g, 1.0)
        conto = 1 - spese + (g - 1) @ x                     # (8,)
        pesi = x[None, :] * g / conto[:, None]              # peso con segno
        ass = np.abs(pesi)
        somma = ass.sum(axis=1)
        j0 = int(np.argmax(np.abs(x)))
        dd = int(np.argmax(ass.max(axis=1)))
        jj = int(np.argmax(ass[dd]))
        corti = np.flatnonzero(x < 0)
        perd = x * (g[7] - 1)                                # contributo al conto a fine settimana (negativo = perdita)
        jp = int(np.argmin(perd))
        # perdita massima sul conto durante la settimana (min sui giorni 1..7 del contributo della moneta)
        righe.append({"lunedi": data(g0), "peso_lunedi": float(np.abs(x).max()), "moneta_lunedi": sim[j0],
                      "somma_lunedi": float(np.abs(x).sum()), "peso_max_settimana": float(ass.max()),
                      "giorno_max": dd, "moneta_max": sim[jj], "somma_max_settimana": float(somma.max()), "somma_fine": float(somma[7]),
                      "peso_fine_settimana": float(ass[7].max()), "conto_min": float(conto.min()),
                      "peggior_moneta": sim[jp], "peggior_contributo": float(perd[jp]),
                      "peggior_x": float(x[jp]), "peggior_salita": float(g[7, jp] - 1),
                      "peggior_peso_fine": float(abs(pesi[7, jp]))})
        for d in range(1, 8):
            for j in np.flatnonzero(ass[d] > LIM_MONETA):
                eventi.append({"lunedi": data(g0), "giorno": d, "moneta": sim[j], "peso": float(ass[d, j]), "lato": "short" if x[j] < 0 else "long"})
    s = pd.DataFrame(righe)
    s.to_csv(QUI / "f5_peso_massimo_settimane.csv.gz", index=False)
    ev = pd.DataFrame(eventi)
    sett_moneta = ev.groupby("lunedi").size() if len(ev) else pd.Series(dtype=int)
    a = s.loc[s["peso_lunedi"].idxmax()]
    b = s.loc[s["peso_max_settimana"].idxmax()]
    c = s.loc[s["somma_max_settimana"].idxmax()]
    p = s.loc[s["peggior_contributo"].idxmin()]
    q = s.loc[s["peggior_peso_fine"].idxmax()]
    out = {
        "settimane": int(len(s)), "prima": s["lunedi"].iloc[0], "ultima": s["lunedi"].iloc[-1],
        "1_lunedi_peso_max": {"peso": float(a.peso_lunedi), "moneta": a.moneta_lunedi, "data": a.lunedi,
                              "percentile_99": float(s["peso_lunedi"].quantile(0.99)), "mediana": float(s["peso_lunedi"].median())},
        "1_lunedi_somma_max": float(s["somma_lunedi"].max()),
        "2_settimana_peso_max": {"peso": float(b.peso_max_settimana), "moneta": b.moneta_max, "lunedi": b.lunedi, "giorno": int(b.giorno_max),
                                 "percentile_99": float(s["peso_max_settimana"].quantile(0.99)),
                                 "mediana": float(s["peso_max_settimana"].median())},
        "2_settimana_somma_max": {"somma": float(c.somma_max_settimana), "lunedi": c.lunedi, "giorno": int(c.giorno_max),
                                  "mediana": float(s["somma_max_settimana"].median())},
        "3_settimane_sopra_60_moneta": int((s["peso_max_settimana"] > LIM_MONETA).sum()),
        "3_settimane_sopra_60_lunedi": int((s["peso_lunedi"] > LIM_MONETA + 1e-9).sum()),
        "3_settimane_sopra_200_somma": int((s["somma_max_settimana"] > LIM_SOMMA + 1e-6).sum()),
        "3_settimane_sopra_200_lunedi": int((s["somma_lunedi"] > LIM_SOMMA + 1e-6).sum()),
        "3_settimane_sopra_50_moneta": int((s["peso_max_settimana"] > 0.50).sum()),
        "3_somma_soglie": {str(v): int((s["somma_max_settimana"] > v).sum()) for v in (2.1, 2.25, 2.5, 3.0)},
        "3_somma_quantili": {str(q_): float(s["somma_max_settimana"].quantile(q_)) for q_ in (0.5, 0.9, 0.99)},
        "3_somma_fine_settimana_max": float(s["somma_fine"].max()),
        "3_eventi_sopra_60": ev.sort_values("peso", ascending=False).head(15).to_dict("records") if len(ev) else [],
        "3_sopra_200_date": s.nlargest(5, "somma_max_settimana")[
            ["lunedi", "somma_max_settimana", "giorno_max"]].to_dict("records"),
        "4_peggior_perdita": {"moneta": p.peggior_moneta, "lunedi": p.lunedi, "peso_lunedi_x": float(p.peggior_x),
                              "salita_settimana": float(p.peggior_salita), "peso_fine_settimana": float(p.peggior_peso_fine),
                              "perdita_sul_conto": float(p.peggior_contributo)},
        "4_peggior_peso_fine": {"moneta": q.peggior_moneta, "lunedi": q.lunedi, "peso_fine": float(q.peggior_peso_fine),
                                "perdita_sul_conto": float(q.peggior_contributo)},
        "conto_minimo_in_settimana": {"valore": float(s["conto_min"].min()), "lunedi": s.loc[s["conto_min"].idxmin(), "lunedi"]},
    }
    top = s.nsmallest(5, "peggior_contributo")[["lunedi", "peggior_moneta", "peggior_x", "peggior_salita", "peggior_peso_fine",
                                                "peggior_contributo"]]
    out["4_cinque_peggiori"] = top.to_dict("records")
    (QUI / "f5_peso_massimo_risultati.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    o = esegui()
    print(f"{o['settimane']} settimane {o['prima']}..{o['ultima']}")
    for k in ("1_lunedi_peso_max", "1_lunedi_somma_max", "2_settimana_peso_max", "2_settimana_somma_max",
              "3_settimane_sopra_60_moneta", "3_settimane_sopra_60_lunedi", "3_settimane_sopra_200_somma",
              "3_settimane_sopra_200_lunedi", "3_settimane_sopra_50_moneta", "4_peggior_perdita", "4_peggior_peso_fine",
              "conto_minimo_in_settimana"):
        print(k, o[k])
