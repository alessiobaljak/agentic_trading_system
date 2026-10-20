"""Programma 6, quindicesima prova (QUINDICESIMA.md): F3 e M1 insieme, il capitale diviso ogni lunedi' in parti
inversamente proporzionali alla volatilita' delle 26 settimane prima di ciascuna; esame come la terza prova.

Uso: python3 -m research.programma6.quindicesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import quattordicesima as q
from research.programma6 import seconda as sc
from research.programma6 import terza as te

QUI = Path(__file__).parent
RIS = QUI / "risultati_quindicesima"


def combina(serie: dict, finestra: int = 26, minimo: int = 13) -> pd.DataFrame:
    """Rendimento settimanale netto e a costi doppi della combinazione a rischio uguale (pesi dalle settimane prima)."""
    nomi = list(serie)
    idx = serie[nomi[0]].index
    for n in nomi[1:]:
        idx = idx.intersection(serie[n].index)
    netto = pd.DataFrame({n: serie[n].loc[idx, "netto"] for n in nomi})
    doppio = pd.DataFrame({n: serie[n].loc[idx, "netto_doppio"] for n in nomi})
    vol = netto.rolling(finestra, min_periods=minimo).std().shift(1)
    inv = 1.0 / vol
    pesi = inv.div(inv.sum(axis=1), axis=0)
    pesi = pesi.where(pesi.notna().all(axis=1), 1.0 / len(nomi))
    out = pd.DataFrame({"netto": (pesi * netto).sum(axis=1), "netto_doppio": (pesi * doppio).sum(axis=1)})
    for n in nomi:
        out[f"peso_{n}"] = pesi[n]
    # colonne che l'esame si aspetta (giro, lati e spese non hanno senso qui: zero)
    for c in ("lordo", "spese", "funding", "giro", "long", "short"):
        out[c] = 0.0
    out["monete"] = 1
    return out


def esegui() -> dict:
    qq = QUI / "risultati_quattordicesima"
    f3 = pd.read_csv(QUI / "risultati_ottava" / "settimane_F3.csv.gz", index_col=0)
    m1 = pd.read_csv(qq / "settimane_M1.csv.gz", index_col=0)
    k1 = pd.read_csv(QUI / "risultati_dodicesima" / "settimane_K1.csv.gz", index_col=0)
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    RIS.mkdir(exist_ok=True)
    df = combina({"F3": f3, "M1": m1})
    df = df[df.index >= q.INIZIO - 26 * 7]
    df.to_csv(RIS / "settimane_F3_M1.csv.gz")
    e = te.esame(df, btc, inizio=q.INIZIO, anni_pieni=q.ANNI_PIENI)
    sr = q.tutte_le_prove()
    ee = json.loads((qq / "esame.json").read_text())
    sr += [ee["M1"]["intero"]["sharpe"], ee["M2"]["intero"]["sharpe"], e["intero"]["sharpe"]]
    i = e["intero"]
    e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
    e["prove_nel_conto"] = len(sr)
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    d = df[df.index >= q.INIZIO]
    e["peso_medio_F3"] = float(d["peso_F3"].mean())
    tre = combina({"F3": f3, "M1": m1, "K1": k1})
    t = tre[tre.index >= q.INIZIO]["netto"]
    e["tre_informazione"] = te.numeri_settimana(t)
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    pa = e["per_anno"]
    testo = "\n".join([
        "# Programma 6 — risultati della quindicesima prova (F3 e M1 insieme)", "",
        "Regole in `QUINDICESIMA.md` (scritte prima). Dal 3 gennaio 2022; pesi dalle 26 settimane prima.", "",
        f"* {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, **Sharpe {i['sharpe']:.2f}**, discesa massima "
        f"{100 * i['discesa_max']:.1f}%; media settimanale {100 * e['boot']['media']:+.3f}% (intervallo "
        f"{100 * e['boot']['basso']:+.3f}; {100 * e['boot']['alto']:+.3f}).",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in pa.items()) + f"; ultimo anno {100 * e['ultimo_anno']:+.1f}%.",
        f"* Trimestri: " + ", ".join(f"{k} {100 * v:+.0f}%" for k, v in e["per_trimestre"].items()) + ".",
        f"* A costi doppi {100 * e['costi_doppi']:+.3f}% a settimana; peso medio di F3 {100 * e['peso_medio_F3']:.0f}%; in più del "
        f"Bitcoin {100 * e['extra_btc_annuo']:+.1f}% l'anno.",
        f"* **Sharpe corretto {e['sharpe_corretto']:.2f}** con {e['prove_nel_conto']} prove.",
        f"* Solo informazione, F3 + M1 + K1: {100 * e['tre_informazione']['annuo']:+.1f}% l'anno, Sharpe "
        f"{e['tre_informazione']['sharpe']:.2f}, discesa massima {100 * e['tre_informazione']['discesa_max']:.1f}%.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_QUINDICESIMA.md").write_text(testo, encoding="utf-8")
    print(testo)
    return e


if __name__ == "__main__":
    esegui()
