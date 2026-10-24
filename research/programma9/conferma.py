"""Programma 9, prima conferma (PRIMA.md): P9A e P9B sul periodo di conferma (1° gennaio 2024 – 26 giugno 2026), con i costi.

Uso: python3 -m research.programma9.conferma
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma9.dati import DATI

QUI = Path(__file__).parent
RIS = QUI / "risultati_prima"
SOGLIA_BTC = -0.0607
COPERTURA = 0.0005


def terzo(df: pd.DataFrame, col: str) -> pd.Series:
    r = df.groupby("giorno")[col].rank(pct=True)
    return np.minimum((r * 3).fillna(-1).astype(int), 2).where(r.notna())


def funding_dopo(pan: dict, h: int) -> dict:
    """{(giorno, simbolo): somma del funding nei giorni t+1..t+h}."""
    F = np.nan_to_num(pan["funding"])
    c = np.cumsum(F, axis=0)
    out = np.full(F.shape, np.nan)
    out[:-h] = c[h:] - c[:-h]
    return out


def coorti(df: pd.DataFrame, cella: pd.Series, h: int, verso: int, costo: dict, fund: np.ndarray, pan: dict) -> pd.DataFrame:
    righe = []
    t0, simboli = pan["t0"], pan["simboli"]
    jdi = {s: j for j, s in enumerate(simboli)}
    for g, d in df.groupby("giorno"):
        dentro = d[cella.loc[d.index].fillna(False).astype(bool) & d[f"y{h}"].notna()]
        if dentro.empty:
            continue
        i = g - t0
        fc = np.nanmean([fund[i, jdi[s]] for s in dentro["simbolo"]])
        fu = np.nanmean([fund[i, jdi[s]] for s in d["simbolo"]])
        spese = 2 * float(np.mean([costo[s] for s in dentro["simbolo"]])) + 2 * COPERTURA
        r = verso * float(dentro[f"y{h}"].mean()) - spese - verso * (fc - fu)
        righe.append({"giorno": int(g), "uscita": int(g + h), "monete": len(dentro), "r": r, "spese": spese})
    return pd.DataFrame(righe)


def settimane(c: pd.DataFrame, h: int) -> pd.DataFrame:
    lun = c["uscita"].to_numpy() - ((c["uscita"].to_numpy() + 3) % 7)
    s = pd.Series(c["r"].to_numpy() / h, index=lun).groupby(level=0).sum()
    sp = pd.Series(c["spese"].to_numpy() / h, index=lun).groupby(level=0).sum()
    tutte = np.arange(s.index.min(), s.index.max() + 7, 7)
    out = pd.DataFrame({"netto": s.reindex(tutte).fillna(0.0)})
    out["spese"] = sp.reindex(tutte).fillna(0.0)
    out["netto_doppio"] = out["netto"] - out["spese"]
    for k in ("lordo", "funding", "giro", "long", "short"):
        out[k] = 0.0
    out["monete"] = 1
    return out


def esegui(log=print) -> dict:
    df = pd.read_pickle(DATI / "conferma.pkl")
    pan = sc.pannello()
    costo = dict(zip(pan["simboli"], sc.costi_moneta(pan["simboli"])))
    f3, f7 = funding_dopo(pan, 3), funding_dopo(pan, 7)
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    ta, tb, to = terzo(df, "dist_hi30"), terzo(df, "ls_diff"), terzo(df, "oi30")
    giu = df["btc_r30"] <= SOGLIA_BTC
    casi = {
        "79 P9A": (((ta == 2) & (tb == 0)), 7, -1, f7),
        "80 P9B": (((to == 0) & giu), 3, +1, f3),
        "P9A solo vicino al massimo": ((ta == 2), 7, -1, f7),
        "P9A solo la folla più long": ((tb == 0), 7, -1, f7),
        "P9B solo la leva pulita (sempre)": ((to == 0), 3, +1, f3),
    }
    out, serie = {}, {}
    RIS.mkdir(exist_ok=True)
    for nome, (cella, h, verso, fund) in casi.items():
        c = coorti(df, cella, h, verso, costo, fund, pan)
        s = settimane(c, h)
        s.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
        e = te.esame(s, btc, inizio=int(s.index.min()), anni_pieni=(2024, 2025))
        e["coorti"], e["monete_medie"] = len(c), float(c["monete"].mean()) if len(c) else 0.0
        e["giorni_con_la_casella"] = int(len(c))
        out[nome], serie[nome] = e, s["netto"]
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "79 P9A": serie["79 P9A"], "80 P9B": serie["80 P9B"]},
                                   {"79 P9A": out["79 P9A"]["intero"], "80 P9B": out["80 P9B"]["intero"]})
    for n in ("79 P9A", "80 P9B"):
        r = rivisto["candidate"][n]
        out[n]["sharpe_corretto"], out[n]["t"], out[n]["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
        out[n]["esito"] = te.esito(out[n], out[n]["sharpe_corretto"])
        anni = out[n]["per_anno"]
        out[n]["regola_del_proprietario"] = bool(out[n]["sharpe_corretto"] >= 0.90 and all(v > 0 for v in anni.values()) and out[n]["t"] > 3)
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    righe = ["# Programma 9 — risultati della prima conferma (P9A, P9B), dal 1° gennaio 2024 al 26 giugno 2026", "",
             "Regole in `PRIMA.md` (scritte prima di aprire il periodo di conferma).", "",
             "| | Sharpe | l'anno | discesa | per anno | giorni con la casella | monete in media |", "|---|---|---|---|---|---|---|"]
    for n, e in out.items():
        i = e["intero"]
        righe.append(f"| {n} | {i['sharpe']:.2f} | {100 * i['annuo']:+.1f}% | {100 * i['discesa_max']:.1f}% | " +
                     ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + f" | {e['giorni_con_la_casella']} | {e['monete_medie']:.1f} |")
    for n in ("79 P9A", "80 P9B"):
        e = out[n]
        righe.append(f"\n* **{n}**: Sharpe corretto {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi), t {e['t']:.2f}; esito: {e['esito']}; "
                     f"regola del proprietario del 24 ottobre (da 0,90, ogni anno positiva, t sopra 3): {'sì' if e['regola_del_proprietario'] else 'no'}.")
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_PRIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CONFERMA FINITA", flush=True)
