"""Programma 6, controllo dei dati (20 ottobre 2026): le monete tolte dal listino restano nei file dell'archivio con il
prezzo fermo e il volume zero, e il funding di quei giorni veniva riempito con la media dei 90 giorni prima (la regola
pensata per i mesi mancanti dell'archivio). Qui si misura quanto cambiano F3, K1 e M1 con le due correzioni:

1. funding zero nei giorni a volume zero (il contratto e' chiuso: nessuno paga e nessuno riceve);
2. fuori dall'universo della settimana le monete con volume zero la domenica prima (lo si sa alla decisione).

Non e' una prova nuova: stesse regole, dati corretti. Uso: python3 -m research.programma6.controllo_zombi
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import dodicesima as do
from research.programma6 import ottava as ot
from research.programma6 import quattordicesima as q
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import undicesima as un

QUI = Path(__file__).parent


def giorni_fermi(pan: dict) -> np.ndarray:
    """Vero dove c'e' la candela ma il volume e' zero (moneta tolta dal listino, prezzo fermo)."""
    return np.isfinite(pan["close"]) & (np.nan_to_num(pan["quote_volume"]) == 0)


def correggi(pan: dict, indicatori_si: bool) -> tuple:
    pan2 = dict(pan)
    pan2["funding"] = np.where(giorni_fermi(pan), 0.0, pan["funding"])
    ps2 = te.pannello_settimane(pan2, log=lambda x: None, indicatori_si=indicatori_si)
    lun = ps2["lunedi"] - pan["t0"]
    ps2["U"] = ps2["U"] & (np.nan_to_num(pan["quote_volume"][lun - 1]) > 0)
    return pan2, ps2


def _numeri(df: pd.DataFrame, inizio: int) -> dict:
    d = df[df.index >= inizio]["netto"]
    return {"sharpe": float(d.mean() / d.std(ddof=1) * math.sqrt(52)), "annuo": float(d.mean() * 52),
            "settimane": int(len(d))}


def _m1(pan: dict, ps: dict) -> pd.DataFrame:
    lun_idx = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun_idx)
    X, _, Y = q.tabella_settimanale(pan, ps, ps["U"])
    P, _ = q.previsioni("M1", X, Y, ps["U"], ps["lunedi"], 6, lambda x: None)
    ct = np.where(np.isfinite(sig), P, np.nan)
    Wt = te.pesi_portafoglio(ct, ps["U"], np.nan_to_num(1.0 / sig), True)
    df = te.conto(Wt, ps["R"], ps["F"], sc.costi_moneta(ps["simboli"]))
    df.index = ps["lunedi"]
    return df


def esegui(log=print) -> dict:
    pan = sc.pannello()
    z = giorni_fermi(pan)
    out = {"giorni_fermi": int(z.sum()), "giorni_fermi_con_funding": int((z & (pan["funding"] != 0)).sum()),
           "ultimo_giorno": sc.data(pan["t0"] + pan["close"].shape[0] - 1)}
    ps = te.pannello_settimane(pan, log=lambda x: None)
    pan2, ps2 = correggi(pan, True)
    out["celle_tolte"] = int((ps["U"] & ~ps2["U"]).sum())
    pm = un.pannello_metrics(pan)
    costo = sc.costi_moneta(ps["simboli"])
    for nome, f, inizio in (("F3", lambda p, s: ot.portafoglio_f3(p, s, costo), se.INIZIO),
                            ("K1", lambda p, s: do.portafoglio_k1(p, s, pm, costo), un.INIZIO),
                            ("M1", _m1, q.INIZIO)):
        out[nome] = {"prima": _numeri(f(pan, ps), inizio), "dopo": _numeri(f(pan2, ps2), inizio)}
        log(f"[zombi] {nome}: {out[nome]}")
    (QUI / "controllo_zombi.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("ZOMBI FINITO", flush=True)
