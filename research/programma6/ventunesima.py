"""Programma 6, ventunesima prova (VENTUNESIMA.md): gli annunci di Binance. Per ogni moneta messa sotto l'etichetta di
monitoraggio (E1) o tolta dal listino a pronti (E2), con il perpetuo attivo: short il perpetuo e long il Bitcoin
dall'apertura del giorno dopo l'annuncio a 7 giorni dopo; esame per evento con il bootstrap sugli annunci.

Uso: python3 -m research.programma6.ventunesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import annunci as an
from research.programma6 import seconda as sc
from research.programma6.motore import TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_ventunesima"
GIORNI, ALTRI = 7, (1, 3, 14, 28)
COSTO_MONETA, COSTO_BTC = 2 * (TAKER + 0.0010), 2 * (TAKER + 0.0001)
P_SOGLIA = 0.005


def _prezzo(O: np.ndarray, C: np.ndarray, t: int, j: int) -> float:
    """L'apertura del giorno t, o l'ultima chiusura prima se la serie finisce prima."""
    if t < len(O) and np.isfinite(O[t, j]):
        return float(O[t, j])
    ok = np.flatnonzero(np.isfinite(C[: min(t, len(C)), j]))
    return float(C[ok[-1], j]) if len(ok) else float("nan")


def rendimento(pan: dict, j: int, jb: int, e: int, giorni: int) -> float:
    """Short la moneta j e long il Bitcoin dall'apertura del giorno e a quella di e + giorni, netto di costi e funding."""
    O, C, F = pan["open"], pan["close"], pan["funding"]
    x = e + giorni
    rc = _prezzo(O, C, x, j) / O[e, j] - 1
    rb = _prezzo(O, C, x, jb) / O[e, jb] - 1
    fc, fb = F[e: min(x, len(F)), j].sum(), F[e: min(x, len(F)), jb].sum()
    return float(rb - rc - COSTO_MONETA - COSTO_BTC + fc - fb)


def tabella(pan: dict, eventi: list) -> pd.DataFrame:
    sim = pan["simboli"]
    ok = np.isfinite(pan["close"])
    primo = ok.argmax(axis=0)
    V = np.nan_to_num(pan["quote_volume"])
    jb = sim.index("BTCUSDT")
    T = V.shape[0]
    righe = []
    for ms, annuncio, sigla in eventi:
        p = an.perpetuo(sigla, sim)
        if not p:
            continue
        j = sim.index(p)
        g = ms // 86_400_000 - pan["t0"]
        e = g + 1
        if not (0 <= g < T - 1 and primo[j] < g and V[g, j] > 0 and np.isfinite(pan["open"][e, j])
                and np.isfinite(pan["open"][e, jb])):
            continue
        r = {"data": sc.data(g + pan["t0"]), "annuncio": annuncio, "simbolo": p,
             "reazione": float((pan["open"][e, jb] / pan["open"][g, jb]) - (pan["open"][e, j] / pan["open"][g, j]))
             if np.isfinite(pan["open"][g, j]) else float("nan")}
        for k in (GIORNI,) + ALTRI:
            r[f"r{k}"] = rendimento(pan, j, jb, e, k) if e + k <= T else float("nan")
        righe.append(r)
    return pd.DataFrame(righe)


def bootstrap_annunci(df: pd.DataFrame, col: str, n: int = 10000, seme: int = 2026) -> dict:
    d = df[np.isfinite(df[col])]
    gruppi = [g[col].to_numpy() for _, g in d.groupby("annuncio")]
    rng = np.random.default_rng(seme)
    medie = np.empty(n)
    for b in range(n):
        scelti = rng.integers(0, len(gruppi), len(gruppi))
        v = np.concatenate([gruppi[i] for i in scelti])
        medie[b] = v.mean()
    return {"media": float(d[col].mean()), "basso": float(np.percentile(medie, 2.5)), "alto": float(np.percentile(medie, 97.5)),
            "p": float((np.sum(medie <= 0) + 1) / (n + 1)), "eventi": int(len(d)), "annunci": len(gruppi)}


def esame(df: pd.DataFrame) -> dict:
    col = f"r{GIORNI}"
    d = df[np.isfinite(df[col])].sort_values("data")
    e = {"boot": bootstrap_annunci(d, col)}
    meta = len(d) // 2
    e["prima_meta"], e["seconda_meta"] = float(d[col].iloc[:meta].mean()), float(d[col].iloc[meta:].mean())
    e["senza_5_migliori"] = float(d[col].sort_values(ascending=False).iloc[5:].mean())
    e["vinti"] = float((d[col] > 0).mean())
    e["altri_orizzonti"] = {f"{k} giorni": float(df[f"r{k}"].mean()) for k in ALTRI}
    e["reazione"] = float(df["reazione"].mean())
    e["per_anno"] = {a: float(g[col].mean()) for a, g in d.groupby(d["data"].str[:4])}
    es = "VALIDA"
    if not e["boot"]["p"] <= P_SOGLIA:
        es = f"media non sopra zero con p ≤ 0,005 (p {e['boot']['p']:.4f})"
    elif not (e["prima_meta"] > 0 and e["seconda_meta"] > 0):
        es = "non positiva in tutte e due le metà"
    elif not e["senza_5_migliori"] > 0:
        es = "non positiva senza i 5 eventi migliori"
    e["esito"] = es
    return e


def esegui(log=print) -> dict:
    pan = sc.pannello()
    RIS.mkdir(exist_ok=True)
    out = {}
    for nome, f in (("E1", an.eventi_monitoraggio), ("E2", an.eventi_rimozione)):
        df = tabella(pan, f())
        df.to_csv(RIS / f"eventi_{nome}.csv", index=False)
        out[nome] = esame(df)
        log(f"[ventunesima] {nome}: {out[nome]['boot']} {out[nome]['esito']}")
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    righe = ["# Programma 6 — risultati della ventunesima prova (gli annunci di Binance)", "",
             "Regole in `VENTUNESIMA.md` (scritte prima). Short il perpetuo della moneta e long il Bitcoin dall'apertura del "
             "giorno dopo l'annuncio a 7 giorni dopo, netto di costi e funding; eventi in `risultati_ventunesima/`.", "",
             "| Prova | Eventi (annunci) | Media a 7 giorni | Intervallo | p | Prima metà, seconda metà | Senza i 5 migliori | "
             "Vinti | A 1, 3, 14, 28 giorni | Prima reazione | Esito |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for nome, e in out.items():
        b = e["boot"]
        ao = e["altri_orizzonti"]
        righe.append(f"| {nome} | {b['eventi']} ({b['annunci']}) | {100 * b['media']:+.2f}% | {100 * b['basso']:+.2f}%; "
                     f"{100 * b['alto']:+.2f}% | {b['p']:.4f} | {100 * e['prima_meta']:+.2f}%, {100 * e['seconda_meta']:+.2f}% | "
                     f"{100 * e['senza_5_migliori']:+.2f}% | {100 * e['vinti']:.0f}% | "
                     + ", ".join(f"{100 * v:+.2f}%" for v in ao.values())
                     + f" | {100 * e['reazione']:+.2f}% | {e['esito']} |")
    for nome, e in out.items():
        righe += ["", f"**{nome}, per anno (media a 7 giorni)**: " + ", ".join(f"{a} {100 * v:+.2f}%" for a, v in e["per_anno"].items())]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_VENTUNESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTUNESIMA FINITA", flush=True)
