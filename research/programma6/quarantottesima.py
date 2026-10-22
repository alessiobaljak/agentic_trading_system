"""Programma 6, quarantottesima prova (QUARANTOTTESIMA.md): R1, il regista. Il primo lunedi' di ogni mese si tengono
solo le strategie fra F5, M7, K2 con le 4 settimane prima sopra zero, a rischio uguale; nessuna accesa: fuori.

Uso: python3 -m research.programma6.quarantottesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import quarantacinquesima as qc
from research.programma6 import seconda as sc
from research.programma6 import terza as te

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantottesima"
DA, A = sc.giorno(2022, 4, 4), sc.giorno(2026, 10, 5)
SETTIMANE_MOMENTO, FINESTRA, MINIMO, COSTO = 4, 26, 13, 0.0007
NOMI = ("F5", "M7", "K2")


def regista(serie: dict) -> pd.DataFrame:
    netto = pd.DataFrame({n: serie[n]["netto"] for n in NOMI})
    doppio = pd.DataFrame({n: serie[n]["netto_doppio"] for n in NOMI})
    vol = netto.rolling(FINESTRA, min_periods=MINIMO).std().shift(1)
    momento = netto.rolling(SETTIMANE_MOMENTO, min_periods=SETTIMANE_MOMENTO).sum().shift(1)
    idx = netto.index[(netto.index >= DA) & (netto.index <= A)]
    pesi = pd.DataFrame(0.0, index=idx, columns=list(NOMI))
    w = pd.Series(0.0, index=list(NOMI))
    mese = None
    for m in idx:
        ym = sc.data(int(m))[:7]
        if ym != mese:                                   # il primo lunedi' del mese
            mese = ym
            accese = [n for n in NOMI if momento.loc[m, n] > 0]
            w = pd.Series(0.0, index=list(NOMI))
            if accese:
                inv = 1.0 / vol.loc[m, accese]
                w[accese] = inv / inv.sum()
        pesi.loc[m] = w
    giro = pesi.diff().abs().sum(axis=1)
    giro.iloc[0] = pesi.iloc[0].abs().sum()           # la prima settimana si entra
    cambio = giro * 2 * COSTO
    out = pd.DataFrame({"netto": (pesi * netto.loc[idx]).sum(axis=1) - cambio,
                        "netto_doppio": (pesi * doppio.loc[idx]).sum(axis=1) - 2 * cambio})
    for n in NOMI:
        out[f"peso_{n}"] = pesi[n]
    for c in ("lordo", "spese", "funding", "giro", "long", "short"):
        out[c] = 0.0
    out["monete"] = 1
    return out


def esegui(log=print) -> dict:
    serie = {"F5": pd.read_csv(QUI / "risultati_ventiquattresima" / "settimane_F5.csv.gz", index_col=0),
             "M7": pd.read_csv(QUI / "risultati_venticinquesima" / "settimane_M7.csv.gz", index_col=0),
             "K2": pd.read_csv(QUI / "risultati_ventottesima" / "settimane_K2.csv.gz", index_col=0)}
    tre = pd.read_csv(QUI / "risultati_ventottesima" / "settimane_F5_M7_K2.csv.gz", index_col=0)
    r1 = regista(serie)
    RIS.mkdir(exist_ok=True)
    r1.to_csv(RIS / "settimane_R1.csv.gz")
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    sr = qc.prove_fino_alla_quarantaquattresima()
    e45 = json.loads((QUI / "risultati_quarantacinquesima" / "esame.json").read_text())
    sr += [e45["I1"]["intero"]["sharpe"], e45["I2"]["portafoglio"]["intero"]["sharpe"]]
    sr += [e["intero"]["sharpe"] for e in json.loads((QUI / "risultati_quarantaseiesima" / "esame.json").read_text()).values()]
    sr += [e["intero"]["sharpe"] for e in json.loads((QUI / "risultati_quarantasettesima" / "esame.json").read_text()).values()]
    e = te.esame(r1, btc, inizio=DA)
    sr.append(e["intero"]["sharpe"])
    i = e["intero"]
    e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
    e["prove_nel_conto"] = len(sr)
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    stesse = tre[(tre.index >= DA) & (tre.index <= A)]
    e["sempre_accese"] = te.numeri_settimana(stesse["netto"])
    e["mesi_spenta"] = {n: int(((r1[f"peso_{n}"] == 0).groupby([sc.data(int(x))[:7] for x in r1.index]).all()).sum()) for n in NOMI}
    e["mesi_fuori"] = int((r1[[f"peso_{n}" for n in NOMI]].sum(axis=1) == 0).groupby([sc.data(int(x))[:7] for x in r1.index]).all().sum())
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    s = e["sempre_accese"]
    testo = "\n".join([
        "# Programma 6 — risultati della quarantottesima prova (R1: il regista)", "",
        "Regole in `QUARANTOTTESIMA.md` (scritte prima).", "",
        f"* R1: Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%.",
        f"* F5 + M7 + K2 sempre accese sulle stesse settimane: Sharpe {s['sharpe']:.2f}, {100 * s['annuo']:+.1f}% l'anno, "
        f"discesa {100 * s['discesa_max']:.1f}%.",
        "* Mesi in cui ogni strategia è stata spenta: " + ", ".join(f"{n} {k}" for n, k in e["mesi_spenta"].items())
        + f"; mesi tutti fuori {e['mesi_fuori']}.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Sharpe corretto {e['sharpe_corretto']:.2f} con {len(sr)} prove.", "", f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_QUARANTOTTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTOTTESIMA FINITA", flush=True)
