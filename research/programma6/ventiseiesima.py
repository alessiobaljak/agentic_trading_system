"""Programma 6, ventiseiesima prova (VENTISEIESIMA.md): il funding che tocca il tetto. Al primo regolamento con l'intervallo
del funding piu' corto: E3 (funding negativo) long la moneta e short il Bitcoin, E4 (positivo) il contrario, dall'apertura
del giorno dopo a 7 giorni dopo; esame per evento con il bootstrap sulle settimane.

Uso: python3 -m research.programma6.ventiseiesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import ventunesima as vu
from research.src.dati import funding_da_zip

QUI = Path(__file__).parent
RIS = QUI / "risultati_ventiseiesima"


def eventi(pan: dict) -> list:
    """(simbolo, ms, segno del funding) per ogni passaggio a un intervallo del funding piu' corto."""
    out = []
    for s in pan["simboli"]:
        righe = []
        for f in sorted((sc.DATI / s / "funding").glob("*.zip")):
            righe += funding_da_zip(f)
        if not righe:
            continue
        df = pd.DataFrame(righe, columns=["ts", "ore", "tasso"]).drop_duplicates("ts").sort_values("ts")
        o, ts, r = df["ore"].to_numpy(), df["ts"].to_numpy(), df["tasso"].to_numpy()
        for k in np.flatnonzero(o[1:] < o[:-1]):
            segno = np.sign(r[k + 1]) if r[k + 1] != 0 else np.sign(r[k])
            out.append((s, int(ts[k + 1]), int(segno)))
    return out


def rendimento(pan: dict, j: int, jb: int, e: int, giorni: int, verso: int) -> float:
    """verso +1: long la moneta e short il Bitcoin; −1: il contrario (come ``ventunesima.rendimento``)."""
    if verso < 0:
        return vu.rendimento(pan, j, jb, e, giorni)
    O, C, F = pan["open"], pan["close"], pan["funding"]
    x = e + giorni
    rc = vu._prezzo(O, C, x, j) / O[e, j] - 1
    rb = vu._prezzo(O, C, x, jb) / O[e, jb] - 1
    fc, fb = F[e: min(x, len(F)), j].sum(), F[e: min(x, len(F)), jb].sum()
    return float(rc - rb - vu.COSTO_MONETA - vu.COSTO_BTC - fc + fb)


def tabella(pan: dict, ev: list, verso: int) -> pd.DataFrame:
    sim = pan["simboli"]
    jb = sim.index("BTCUSDT")
    V = np.nan_to_num(pan["quote_volume"])
    T = V.shape[0]
    righe = []
    for s, ms, segno in ev:
        if segno != -verso:                       # E3 (verso +1) vuole il funding negativo, E4 il positivo
            continue
        j = sim.index(s)
        g = ms // 86_400_000 - pan["t0"]
        e = g + 1
        if s == "BTCUSDT" or not (0 <= g < T - 1 and V[g, j] > 0 and np.isfinite(pan["open"][e, j])
                                  and np.isfinite(pan["open"][e, jb])):
            continue
        r = {"data": sc.data(g + pan["t0"]), "annuncio": int((g + pan["t0"] + 3) // 7), "simbolo": s,
             "reazione": float(verso * ((pan["open"][e, j] / pan["open"][g, j]) - (pan["open"][e, jb] / pan["open"][g, jb])))
             if np.isfinite(pan["open"][g, j]) else float("nan")}
        for k in (vu.GIORNI,) + vu.ALTRI:
            r[f"r{k}"] = rendimento(pan, j, jb, e, k, verso) if e + k <= T else float("nan")
        righe.append(r)
    return pd.DataFrame(righe)


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ev = eventi(pan)
    RIS.mkdir(exist_ok=True)
    out = {}
    for nome, verso in (("E3", 1), ("E4", -1)):
        df = tabella(pan, ev, verso)
        df.to_csv(RIS / f"eventi_{nome}.csv", index=False)
        out[nome] = vu.esame(df)
        log(f"[ventiseiesima] {nome}: {out[nome]['boot']} {out[nome]['esito']}")
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    righe = ["# Programma 6 — risultati della ventiseiesima prova (il funding che tocca il tetto)", "",
             "Regole in `VENTISEIESIMA.md` (scritte prima). Dall'apertura del giorno dopo il primo regolamento con l'intervallo "
             "più corto a 7 giorni dopo, contro il Bitcoin, netto di costi e funding; bootstrap sulle settimane.", "",
             "| Prova | Eventi (settimane) | Media a 7 giorni | Intervallo | p | Prima metà, seconda metà | Senza i 5 migliori | "
             "Vinti | A 1, 3, 14, 28 giorni | Prima reazione | Esito |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for nome, e in out.items():
        b = e["boot"]
        righe.append(f"| {nome} | {b['eventi']} ({b['annunci']}) | {100 * b['media']:+.2f}% | {100 * b['basso']:+.2f}%; "
                     f"{100 * b['alto']:+.2f}% | {b['p']:.4f} | {100 * e['prima_meta']:+.2f}%, {100 * e['seconda_meta']:+.2f}% | "
                     f"{100 * e['senza_5_migliori']:+.2f}% | {100 * e['vinti']:.0f}% | "
                     + ", ".join(f"{100 * v:+.2f}%" for v in e["altri_orizzonti"].values())
                     + f" | {100 * e['reazione']:+.2f}% | {e['esito']} |")
    for nome, e in out.items():
        righe += ["", f"**{nome}, per anno (media a 7 giorni)**: " + ", ".join(f"{a} {100 * v:+.2f}%" for a, v in e["per_anno"].items())]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_VENTISEIESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTISEIESIMA FINITA", flush=True)
