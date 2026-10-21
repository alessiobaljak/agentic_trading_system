"""Programma 6, trentottesima prova (TRENTOTTESIMA.md): T7, solo lo short delle rotture di Donchian verso il basso a 4 ore con
il funding dei 7 giorni nel 40% piu' alto, sulle monete 101-200 per volume (conferma); uscite come T2, scarto 0,10%.

Uso: python3 -m research.programma6.trentottesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import trentaquattresima as tq
from research.programma6.motore import TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentottesima"
SCARTO = 0.0010


def operazioni(pan: dict, R: np.ndarray, Ud: np.ndarray) -> pd.DataFrame:
    sim = pan["simboli"]
    righe = []
    for j in np.flatnonzero(Ud.any(axis=0)):
        s = sim[j]
        b = tq.quattro_ore(es.ore_di(s))
        if len(b) < tq.N_DON + tq.N_ATR + 2:
            continue
        o, h, l, c = (b[k].to_numpy(float) for k in ("open", "high", "low", "close"))
        blocco = b.index.to_numpy()
        giorno = blocco * 4 // 24 - pan["t0"]
        ll = pd.Series(l).rolling(tq.N_DON).min().shift(1).to_numpy()
        cp = np.r_[np.nan, c[:-1]]
        atr = pd.Series(np.nanmax(np.vstack([h - l, np.abs(h - cp), np.abs(l - cp)]), axis=0)).rolling(tq.N_ATR).mean().to_numpy()
        g = np.clip(giorno, 0, Ud.shape[0] - 1)
        nel = (giorno >= 0) & (giorno < Ud.shape[0]) & Ud[g, j] & (giorno + pan["t0"] >= tq.DA) & (giorno + pan["t0"] <= tq.A)
        corto = nel & (c < ll) & (R[g, j] >= 1 - tq.FILTRO)
        for i, e, u, verso, p0, p1, motivo in tq._simula(o, h, l, c, np.zeros(len(c), np.bool_), corto, atr):
            ore_tenuta = (blocco[u] - blocco[e]) * 4
            gi, ge = int(giorno[e]), int(min(giorno[u], pan["funding"].shape[0] - 1))
            f = float(pan["funding"][gi: ge + 1, j].sum()) * ore_tenuta / max(1, (ge - gi + 1) * 24)
            r = verso * (p1 / p0 - 1) - 2 * (TAKER + SCARTO) - verso * f
            righe.append({"simbolo": s, "data": sc.data(gi + pan["t0"]), "uscita": sc.data(int(giorno[u]) + pan["t0"]),
                          "annuncio": int((gi + pan["t0"] + 3) // 7), "verso": verso, "r": r, "ore": ore_tenuta,
                          "motivo": {1: "stop", 2: "uscita mobile", 3: "tempo"}[motivo]})
    return pd.DataFrame(righe)


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps2 = te.pannello_settimane(pan, log=lambda x: None, da=100, a=200, indicatori_si=False)
    R, Ud = tq.rango_funding(pan, ps2)
    df = operazioni(pan, R, Ud)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "operazioni_T7.csv.gz", index=False)
    tq.P_SOGLIA = 0.01
    e = {"operazioni": tq.esame_operazioni(df), "numero": int(len(df))}
    jb = ps2["simboli"].index("BTCUSDT")
    btc = pd.Series(ps2["R"][:, jb], index=ps2["lunedi"])
    e["portafoglio"] = te.esame(tq.portafoglio(df), btc, inizio=tq.DA, anni_pieni=se.ANNI_PIENI)
    e["esito"] = "CONFERMATA" if e["operazioni"]["passa"] else "non confermata"
    d = df.sort_values("data")
    e["per_anno"] = {a: {"operazioni": int(len(x)), "media": float(x["r"].mean())} for a, x in d.groupby(d["data"].str[:4])}
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    o, p = e["operazioni"], e["portafoglio"]
    testo = "\n".join([
        "# Programma 6 — risultati della trentottesima prova (T7: solo short delle rotture verso il basso dove i long pagano, monete 101-200)", "",
        "Regole in `TRENTOTTESIMA.md` (scritte prima). Conferma su monete mai guardate per questa regola.", "",
        f"* {e['numero']} operazioni; media netta {100 * o['boot']['media']:+.3f}% (intervallo {100 * o['boot']['basso']:+.3f}; "
        f"{100 * o['boot']['alto']:+.3f}, p {o['boot']['p']:.4f}); vinte {100 * o['vinte']:.0f}%; tenuta media {o['ore_medie']:.0f} ore.",
        f"* Metà: {100 * o['prima_meta']:+.3f}%, {100 * o['seconda_meta']:+.3f}%; senza le 5 migliori {100 * o['senza_5_migliori']:+.3f}%.",
        "* Per anno: " + ", ".join(f"{a} {100 * v['media']:+.2f}% ({v['operazioni']})" for a, v in e["per_anno"].items()) + ".",
        f"* Portafoglio (5% a operazione, al massimo 20): Sharpe {p['intero']['sharpe']:.2f}, {100 * p['intero']['annuo']:+.1f}% l'anno, "
        f"discesa {100 * p['intero']['discesa_max']:.1f}%.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_TRENTOTTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTOTTESIMA FINITA", flush=True)
