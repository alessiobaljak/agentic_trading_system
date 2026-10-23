"""Programma 7, nona prova (NONA.md): G8, N3 con l'entrata al 7o giorno dopo la prima ora che chiude sopra l'apertura del giorno.

Uso: python3 -m research.programma7.nona
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import trentaduesima as td
from research.programma6 import trentesima as tr
from research.programma6 import ventunesima as vu

QUI = Path(__file__).parent
RIS = QUI / "risultati_nona"
ULTIMA, RISERVA = 20, 21          # l'ultima candela d'entrata chiude alle 20:00; senza segnale si entra alle 21:00


def ora_di_entrata(c: pd.DataFrame, e: int) -> int | None:
    """L'ora d'entrata del 7o giorno ``e``: dopo la prima candela (00:00-19:00) che chiude sopra l'apertura delle 00:00, altrimenti
    le 21:00. None senza candele."""
    h0 = e * 24
    if h0 not in c.index:
        return None
    apertura = c.loc[h0, "open"]
    for k in range(ULTIMA):
        h = h0 + k
        if h in c.index and c.loc[h, "close"] > apertura:
            return h + 1
    return h0 + RISERVA


def operazione(c: pd.DataFrame, cb: pd.DataFrame, f: pd.Series, fb: pd.Series, h_e: int) -> dict:
    """Short la moneta e long il Bitcoin dall'apertura dell'ora ``h_e``, uscita a +30% o dopo 30 giorni (come N3)."""
    h1 = h_e + tr.GIORNI * 24
    if h_e not in c.index or h_e not in cb.index:
        return {}
    p0, b0 = c.loc[h_e, "open"], cb.loc[h_e, "open"]
    tratto = c[(c.index >= h_e) & (c.index < h1)]
    uscita_h, pc, fermata = None, None, False
    su = tratto.index[tratto["high"].to_numpy() >= p0 * (1 + tr.STOP)]
    if len(su):
        uscita_h, pc, fermata = int(su[0]), p0 * (1 + tr.STOP) * (1 + tr.SCARTO_STOP), True
    if uscita_h is None:
        if h1 in c.index:
            uscita_h, pc = h1, c.loc[h1, "open"]
        elif len(tratto):
            uscita_h, pc = int(tratto.index[-1]) + 1, tratto["close"].iloc[-1]
        else:
            return {}
    bb = cb[cb.index <= uscita_h]
    pb = cb.loc[uscita_h, "open"] if (not fermata and uscita_h in cb.index) else bb["close"].iloc[-1]
    e, gu = h_e // 24, uscita_h // 24
    fc = f[(f.index >= e) & (f.index <= gu)].sum()
    fbb = fb[(fb.index >= e) & (fb.index <= gu)].sum()
    r = (pb / b0 - 1) - (pc / p0 - 1) - vu.COSTO_MONETA - vu.COSTO_BTC + fc - fbb
    return {"r": float(r), "fermata": fermata, "giorni": float((uscita_h - h_e) / 24)}


def esegui(log=print) -> dict:
    pan = sc.pannello()
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    jb = pan["simboli"].index("BTCUSDT")
    fb = pd.Series(pan["funding"][:, jb], index=giorni)
    cb = td.ore("BTCUSDT")
    n3 = pd.read_csv(QUI.parent / "programma6" / "risultati_trentaduesima" / "eventi_N3B.csv")
    righe, senza = [], 0
    for _, x in n3.iterrows():
        e = sc.giorno(*map(int, x["data"].split("-")))
        c = td.ore(x["simbolo"])
        h_e = ora_di_entrata(c, e) if not c.empty else None
        if h_e is None:
            senza += 1
            continue
        f = pd.Series(pan["funding"][:, pan["simboli"].index(x["simbolo"])], index=giorni)
        r = operazione(c, cb, f, fb, h_e)
        if r:
            righe.append({"data": x["data"], "annuncio": int(x["annuncio"]), "simbolo": x["simbolo"], "ora": int(h_e - e * 24),
                          "r": r["r"], "fermata": r["fermata"], "giorni": r["giorni"], "r_N3": float(x["r"])})
    df = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_G8.csv", index=False)
    d = df["r"] - df["r_N3"]
    rng = np.random.default_rng(64)
    boot = np.array([d.sample(len(d), replace=True, random_state=int(rng.integers(1 << 31))).mean() for _ in range(5000)])
    out = {"esame": tr.esame(df, "r"), "N3_stessi_eventi": float(df["r_N3"].mean()), "differenza": float(d.mean()),
           "differenza_intervallo": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
           "fermate": float(df["fermata"].mean()), "senza_candele": senza,
           "entrate_alle_21": float((df["ora"] == 21).mean()), "ora_media": float(df["ora"].mean())}
    out["il_bot_cambia"] = bool(out["esame"]["esito"] == "VALIDA" and out["differenza"] >= 0.005)
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    b, x = out["esame"]["boot"], out["esame"]
    testo = "\n".join([
        "# Programma 7 — risultati della nona prova (G8: N3 con l'entrata scelta dentro la giornata)", "",
        "Regole in `NONA.md` (scritte prima).", "",
        f"* Eventi: {b['eventi']} ({senza} senza candele a 1 ora); entrata in media alle {out['ora_media']:.1f}, alle 21:00 (nessun "
        f"segnale) nel {100 * out['entrate_alle_21']:.0f}% dei casi.",
        f"* G8: **{100 * b['media']:+.2f}% a evento** (intervallo {100 * b['basso']:+.2f}%; {100 * b['alto']:+.2f}%), p {b['p']:.4f}, "
        f"mediana {100 * x['mediana']:+.2f}%, vinti {100 * x['vinti']:.0f}%, metà {100 * x['prima_meta']:+.2f}% e "
        f"{100 * x['seconda_meta']:+.2f}%, senza i 5 migliori {100 * x['senza_5_migliori']:+.2f}%; uscita a +30% nel "
        f"{100 * out['fermate']:.0f}%.",
        f"* N3 sugli stessi eventi: {100 * out['N3_stessi_eventi']:+.2f}%; differenza G8 − N3 {100 * out['differenza']:+.2f} punti "
        f"(intervallo {100 * out['differenza_intervallo'][0]:+.2f}; {100 * out['differenza_intervallo'][1]:+.2f}).",
        "* Per anno: " + ", ".join(f"{a} {100 * v['media']:+.2f}% ({v['eventi']})" for a, v in x["per_anno"].items()) + ".", "",
        f"**Esito: {x['esito']}. Per il bot: {'l’entrata di N3 cambia' if out['il_bot_cambia'] else 'N3 resta all’apertura del 7° giorno'}** "
        "(regola scritta prima: passa l'esame e almeno +0,5 punti su N3)."]) + "\n"
    (QUI / "RISULTATI_NONA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("NONA FINITA", flush=True)
