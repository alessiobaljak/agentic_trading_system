"""Programma 5: la statistica comune delle esplorazioni su C (REGOLE.md, sezione 6bis): t per gruppi di giorni di
calendario, riassunto per anno e per moneta, tabella dei risultati. Le righe di una cella sono un DataFrame con le
colonne ``s`` (moneta), ``minuto`` (della decisione o dell'ingresso), ``v`` (lordo del trade) e ``x`` (contro il caso)."""
from __future__ import annotations

import numpy as np
import pandas as pd


def t_giorni(v: np.ndarray, giorno: np.ndarray) -> float:
    if len(v) < 5:
        return float("nan")
    unici, inv = np.unique(giorno, return_inverse=True)
    S, N = np.bincount(inv, weights=v), np.bincount(inv)
    m = S.sum() / N.sum()
    G = len(unici)
    if G < 3:
        return float("nan")
    se = np.sqrt(np.sum((S - m * N) ** 2) * G / (G - 1)) / N.sum()
    return float(m / se) if se > 0 else float("nan")


def riassumi(righe: pd.DataFrame) -> dict:
    v = righe["v"].to_numpy(float)
    out = {"trade": int(len(v))}
    if len(v) == 0:
        return out
    minuto = righe["minuto"].to_numpy(np.int64)
    out["lordo"] = float(v.mean())
    out["contro_caso"] = float(righe["x"].mean())
    out["t"] = t_giorni(v, minuto // 1440)
    anni = pd.to_datetime(minuto * 60, unit="s").year
    out["per_anno"] = {int(a): [int((anni == a).sum()), float(v[anni == a].mean())] for a in sorted(set(anni))}
    out["per_moneta"] = {m: [int(len(g)), float(g["v"].mean())] for m, g in righe.groupby("s")}
    return out


def promossa(r: dict, lordo_min: float, caso_min: float, solo_positivo: bool = False) -> bool:
    """I criteri di promozione dei piani: lordo e contro il caso oltre le soglie, |t| >= 3, stesso segno in ogni anno
    con almeno 20 trade e su almeno il 70% delle monete con almeno 10 trade (almeno 6), almeno 100 trade."""
    if r.get("trade", 0) < 100 or not np.isfinite(r.get("t", np.nan)):
        return False
    segno = 1.0 if solo_positivo else np.sign(r["lordo"])
    if segno * r["lordo"] < lordo_min or segno * r["contro_caso"] < caso_min or segno * r["t"] < 3:
        return False
    if any(segno * m <= 0 for n, m in r["per_anno"].values() if n >= 20):
        return False
    monete = [m for n, m in r["per_moneta"].values() if n >= 10]
    giuste = sum(1 for m in monete if segno * m > 0)
    return len(monete) >= 6 and giuste >= 0.7 * len(monete)


def riga(n: str, r: dict) -> str:
    anni = " ".join(f"{a}:{100 * m:+.2f}({k})" for a, (k, m) in r.get("per_anno", {}).items())
    monete = [m for k, m in r.get("per_moneta", {}).values() if k >= 10]
    segno = np.sign(r.get("lordo", 0))
    giuste = sum(1 for m in monete if segno * m > 0)
    return (f"| {n} | {r['trade']} | {100 * r['lordo']:+.3f}% | {100 * r['contro_caso']:+.3f}% | {r['t']:+.2f} | "
            f"{anni} | {giuste}/{len(monete)} | {'**sì**' if r['promossa'] else ''} |")


TESTA = ["| Cella | Trade | Lordo | Contro il caso | t | Per anno (lordo %, trade) | Monete col segno del lordo "
         "(≥10 trade) | Promossa |", "|---|---|---|---|---|---|---|---|"]


def tabella_md(titolo: str, introduzione: list, ris: dict, quante_t: int = 40, quante_lordo: int = 30) -> str:
    validi = {n: r for n, r in ris.items() if r.get("trade", 0) > 0 and np.isfinite(r.get("t", np.nan))}
    promosse = {n: r for n, r in validi.items() if r["promossa"]}
    righe = [f"# {titolo}", ""] + introduzione + [
        "", f"Celle calcolate: **{len(ris)}** ({len(validi)} con trade). Promosse: **{len(promosse)}**.", "",
        "## Celle promosse", ""]
    if promosse:
        righe += TESTA + [riga(n, r) for n, r in sorted(promosse.items(), key=lambda x: -abs(x[1]["t"]))]
    else:
        righe.append("Nessuna.")
    righe += ["", f"## Le {quante_t} celle con |t| più alto", ""] + TESTA
    righe += [riga(n, r) for n, r in sorted(validi.items(), key=lambda x: -abs(x[1]["t"]))[:quante_t]]
    grandi = {n: r for n, r in validi.items() if r["trade"] >= 100}
    righe += ["", f"## Le {quante_lordo} celle con |lordo| più alto (almeno 100 trade)", ""] + TESTA
    righe += [riga(n, r) for n, r in sorted(grandi.items(), key=lambda x: -abs(x[1]["lordo"]))[:quante_lordo]]
    righe += ["", "Tutte le celle, con i numeri per moneta, sono in `risultati.json`."]
    return "\n".join(righe) + "\n"
