"""Programma 7, quarantasettesima prova (QUARANTASETTESIMA.md): GR, il trading a griglia: 21 livelli dal −10% al +10%, ordini limite,
ripartenza fuori dall'intervallo; griglia lunga (come a pronti) e neutra (future), 6 monete, 2024-2026, candele a 1 minuto.

Uso: python3 -m research.programma7.quarantasettesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

from research.programma6 import asticella as ast
from research.programma6 import dati as d6
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma7 import quarantaseiesima as sk

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantasettesima"
MONETE = sk.MONETE
PASSO = 1.1 ** (1 / 10) - 1
LIVELLI = 10
MAKER = 0.0002


@njit(cache=True)
def _griglia(o, h, l, c, giorno, fund_giorno, neutra, passo, livelli, maker, taker):
    n = len(o)
    g0 = giorno[0]
    ng = giorno[-1] - g0 + 1
    eq_giorno = np.full(ng, np.nan)
    spese_giorno = np.zeros(ng)
    ripartenze = 0
    E = 1.0
    P0 = o[0]
    q = E / ((livelli if neutra else 2 * livelli) * P0)
    units = 0.0 if neutra else livelli * q
    cash = E - (0.0 if neutra else livelli * q * P0 * (1 + maker))
    if not neutra:
        spese_giorno[0] += livelli * q * P0 * maker
    a = 0
    for j in range(n):
        gi = giorno[j] - g0
        if c[j] < o[j]:
            while a > -livelli:
                L = P0 * (1 + passo) ** (a - 1)
                if l[j] <= L:
                    cash -= q * L * (1 + maker)
                    spese_giorno[gi] += q * L * maker
                    units += q
                    a -= 1
                else:
                    break
            if a == -livelli and l[j] <= P0 * (1 + passo) ** (-livelli - 1):
                if units > 0:
                    cash += units * c[j] * (1 - taker)
                else:
                    cash -= -units * c[j] * (1 + taker)
                spese_giorno[gi] += abs(units) * c[j] * taker
                E = cash
                P0 = c[j]
                q = E / ((livelli if neutra else 2 * livelli) * P0)
                units = 0.0 if neutra else livelli * q
                cash = E - (0.0 if neutra else livelli * q * P0 * (1 + maker))
                if not neutra:
                    spese_giorno[gi] += livelli * q * P0 * maker
                a = 0
                ripartenze += 1
        else:
            while a < livelli:
                L = P0 * (1 + passo) ** (a + 1)
                if h[j] >= L:
                    cash += q * L * (1 - maker)
                    spese_giorno[gi] += q * L * maker
                    units -= q
                    a += 1
                else:
                    break
            if a == livelli and h[j] >= P0 * (1 + passo) ** (livelli + 1):
                if units > 0:
                    cash += units * c[j] * (1 - taker)
                else:
                    cash -= -units * c[j] * (1 + taker)
                spese_giorno[gi] += abs(units) * c[j] * taker
                E = cash
                P0 = c[j]
                q = E / ((livelli if neutra else 2 * livelli) * P0)
                units = 0.0 if neutra else livelli * q
                cash = E - (0.0 if neutra else livelli * q * P0 * (1 + maker))
                if not neutra:
                    spese_giorno[gi] += livelli * q * P0 * maker
                a = 0
                ripartenze += 1
        if j == n - 1 or giorno[j + 1] != giorno[j]:
            f = fund_giorno[gi]
            if f == f:
                cash -= units * c[j] * f
            eq_giorno[gi] = cash + units * c[j]
    return eq_giorno, spese_giorno, ripartenze


def una(simbolo: str, pan: dict, neutra: bool) -> tuple:
    df = sk.candele(simbolo, 1)
    m = df.index.to_numpy()
    giorno = (m // 1440).astype(np.int64)
    j = pan["simboli"].index(simbolo)
    fg = np.full(giorno[-1] - giorno[0] + 1, np.nan)
    for g in range(giorno[0], giorno[-1] + 1):
        k = g - pan["t0"]
        if 0 <= k < pan["funding"].shape[0]:
            fg[g - giorno[0]] = pan["funding"][k, j]
    taker = sk.TAKER + sk.SCARTO.get(simbolo, sk.SCARTO_ALTRE)
    eq, sp, rip = _griglia(*(df[k].to_numpy(np.float64) for k in ("open", "high", "low", "close")), giorno, fg, neutra, PASSO, LIVELLI,
                           MAKER, taker)
    idx = np.arange(giorno[0], giorno[-1] + 1)
    eq = pd.Series(eq, index=idx).ffill()
    r = eq.pct_change().fillna(eq.iloc[0] - 1.0)
    chiusure = df.groupby(giorno)["close"].last().reindex(idx).ffill()
    rm = chiusure.pct_change().fillna(0.0)
    sp_rel = pd.Series(sp, index=idx) / eq.shift().fillna(1.0)
    return r, rm, sp_rel, rip


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    RIS.mkdir(exist_ok=True)
    out = {}
    for nome, neutra in (("GR-L", False), ("GR-N", True)):
        rr, rmm, spp, per_moneta = {}, {}, {}, {}
        for s in MONETE:
            r, rm, sp, rip = una(s, pan, neutra)
            rr[s], rmm[s], spp[s] = r, rm, sp
            X = np.vstack([np.ones(len(r)), rm.to_numpy()]).T
            coef, *_ = np.linalg.lstsq(X, r.to_numpy(), rcond=None)
            per_moneta[s] = {"annuo": float(r.mean() * 365), "alfa_annuo": float(coef[0] * 365), "pendenza": float(coef[1]),
                             "tenere_annuo": float(rm.mean() * 365), "ripartenze": int(rip), "discesa": float(((1 + r).cumprod() / (1 + r).cumprod().cummax() - 1).min())}
            log(f"[quarantasettesima] {nome} {s}: {100 * per_moneta[s]['annuo']:+.1f}% l'anno, oltre la moneta {100 * per_moneta[s]['alfa_annuo']:+.1f}%")
        R = pd.DataFrame(rr).fillna(0.0).mean(axis=1)
        RM = pd.DataFrame(rmm).fillna(0.0).mean(axis=1)
        SP = pd.DataFrame(spp).fillna(0.0).mean(axis=1)
        giorni = R.index.to_numpy()
        lun = giorni - ((giorni + 3) % 7)
        d = pd.DataFrame({"netto": R.to_numpy(), "spese": SP.to_numpy(), "settimana": lun})
        sett = d.groupby("settimana").agg(netto=("netto", "sum"), spese=("spese", "sum"))
        sett["lordo"] = sett["netto"] + sett["spese"]
        sett["netto_doppio"] = sett["netto"] - sett["spese"]
        for k in ("funding", "giro", "long", "short"):
            sett[k] = 0.0
        sett["monete"] = len(MONETE)
        sett.to_csv(RIS / f"settimane_{nome}.csv.gz")
        e = te.esame(sett, btc, inizio=int(sett.index.min()), anni_pieni=(2024, 2025))
        X = np.vstack([np.ones(len(R)), RM.to_numpy()]).T
        coef, *_ = np.linalg.lstsq(X, R.to_numpy(), rcond=None)
        e["alfa_annuo_sul_paniere"], e["pendenza_sul_paniere"] = float(coef[0] * 365), float(coef[1])
        e["tenere_il_paniere_annuo"] = float(RM.mean() * 365)
        e["per_moneta"] = per_moneta
        out[nome] = e
    serie = {**ast.serie_nuove(), "109 GR-L": pd.read_csv(RIS / "settimane_GR-L.csv.gz", index_col=0)["netto"],
             "109 GR-N": pd.read_csv(RIS / "settimane_GR-N.csv.gz", index_col=0)["netto"]}
    rivisto = ast.corretto_rivisto(serie, {"109 GR-L": out["GR-L"]["intero"], "109 GR-N": out["GR-N"]["intero"]})
    for nome in ("GR-L", "GR-N"):
        r = rivisto["candidate"][f"109 {nome}"]
        out[nome]["sharpe_corretto"], out[nome]["t"] = r["corretto_con_aggiunta"], r["t"]
        out[nome]["esito"] = te.esito(out[nome], out[nome]["sharpe_corretto"])
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: f"{100 * v:+.1f}%"  # noqa: E731
    righe = ["# Programma 7 — risultati della quarantasettesima prova (GR: il trading a griglia)", "",
             "Regole in `QUARANTASETTESIMA.md` (scritte prima). 6 monete con lo stesso peso, dal 1° gennaio 2024 al 30 settembre 2026.", "",
             "| | Sharpe | l'anno | volatilità | discesa | per anno | oltre la moneta, l'anno | pendenza sulla moneta | tenere le monete, l'anno |",
             "|---|---|---|---|---|---|---|---|---|"]
    for nome in ("GR-L", "GR-N"):
        e, i = out[nome], out[nome]["intero"]
        righe.append(f"| {nome} | {i['sharpe']:.2f} | {pc(i['annuo'])} | {100 * i['volatilita']:.1f}% | {100 * i['discesa_max']:.1f}% | "
                     + ", ".join(f"{a} {pc(v)}" for a, v in e["per_anno"].items()) + f" | {pc(e['alfa_annuo_sul_paniere'])} | {e['pendenza_sul_paniere']:.2f} | "
                     f"{pc(e['tenere_il_paniere_annuo'])} |")
    righe.append("")
    for nome in ("GR-L", "GR-N"):
        righe.append(f"* **{nome}** per moneta: " + "; ".join(f"{s[:-4]} {pc(v['annuo'])} (oltre la moneta {pc(v['alfa_annuo'])}, ripartenze {v['ripartenze']}, "
                                                        f"discesa {100 * v['discesa']:.0f}%)" for s, v in out[nome]["per_moneta"].items()) + ".")
        righe.append(f"  Sharpe corretto {out[nome]['sharpe_corretto']:.2f}, t {out[nome]['t']:.2f}; esito {out[nome]['esito']}.")
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_QUARANTASETTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTASETTESIMA FINITA", flush=True)
