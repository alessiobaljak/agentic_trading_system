"""Programma 6, quarantaquattresima prova (QUARANTAQUATTRESIMA.md): S1, long il Bitcoin per la settimana se l'offerta
totale delle stablecoin e' cresciuta nella settimana prima (dal sabato al sabato), altrimenti niente.

Uso: python3 -m research.programma6.scarico_stablecoin && python3 -m research.programma6.quarantaquattresima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import quarantesima as qr
from research.programma6 import scarico_stablecoin as ss
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6.motore import TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantaquattresima"
DA, A = sc.giorno(2021, 1, 4), sc.giorno(2026, 10, 5)
COSTO = TAKER + 0.0001


def segnale(offerta: pd.Series, lunedi: int) -> float:
    """La variazione dell'offerta dal sabato di due settimane prima al sabato prima del lunedi'."""
    a, b = lunedi - 9, lunedi - 2
    if a not in offerta.index or b not in offerta.index:
        return float("nan")
    return float(offerta[b] / offerta[a] - 1)


def settimane(pan: dict, offerta: pd.Series) -> pd.DataFrame:
    jb = pan["simboli"].index("BTCUSDT")
    O, F, t0 = pan["open"][:, jb], pan["funding"][:, jb], pan["t0"]
    righe, w_prima = [], 0.0
    for m in range(DA, A + 1, 7):
        k = m - t0
        g = segnale(offerta, m)
        w = 1.0 if g > 0 else 0.0
        lordo = w * (O[k + 7] / O[k] - 1)
        fund = w * float(F[k: k + 7].sum())
        spese = abs(w - w_prima) * COSTO
        righe.append({"lunedi": m, "segnale": g, "w": w, "lordo": lordo, "spese": spese, "funding": fund,
                      "netto": lordo - spese - fund, "netto_doppio": lordo - 2 * spese - fund, "giro": abs(w - w_prima),
                      "long": lordo - fund, "short": 0.0, "monete": 1, "btc": O[k + 7] / O[k] - 1 - float(F[k: k + 7].sum())})
        w_prima = w
    return pd.DataFrame(righe).set_index("lunedi")


def esegui(log=print) -> dict:
    pan = sc.pannello()
    d = json.loads((ss.DATI / "totale.json").read_text())
    offerta = pd.Series({x["giorno"]: x["offerta"] for x in d})
    df = settimane(pan, offerta)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "settimane_S1.csv.gz")
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    sr = qr.prove_fino_alla_trentanovesima()
    for f in ("risultati_quarantesima", "risultati_quarantunesima"):
        sr.append(json.loads((QUI / f / "esame.json").read_text())["portafoglio"]["intero"]["sharpe"])
    sr.append(json.loads((QUI / "risultati_quarantaduesima" / "esame.json").read_text())["intero"]["sharpe"])
    e43 = json.loads((QUI / "risultati_quarantatreesima" / "esame.json").read_text())
    sr += [e43[k]["portafoglio"]["intero"]["sharpe"] for k in ("Q1", "Q2")]
    e = te.esame(df, btc, inizio=DA, anni_pieni=se.ANNI_PIENI)
    sr.append(e["intero"]["sharpe"])
    i = e["intero"]
    e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
    e["prove_nel_conto"] = len(sr)
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    tenuto = df.assign(netto=df["btc"], netto_doppio=df["btc"])
    eb = te.esame(tenuto, btc, inizio=DA, anni_pieni=se.ANNI_PIENI)
    e["bitcoin_tenuto"] = {k: eb["intero"][k] for k in ("sharpe", "annuo", "volatilita", "discesa_max")}
    e["bitcoin_per_anno"] = eb["per_anno"]
    e["quota_in_posizione"] = float(df["w"].mean())
    e["cambi"] = int(df["giro"].sum())
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    b = e["bitcoin_tenuto"]
    testo = "\n".join([
        "# Programma 6 — risultati della quarantaquattresima prova (S1: il denaro nuovo delle stablecoin)", "",
        "Regole in `QUARANTAQUATTRESIMA.md` (scritte prima).", "",
        f"* In posizione {100 * e['quota_in_posizione']:.0f}% delle settimane, {e['cambi']} cambi.",
        f"* S1: Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; più del Bitcoin {100 * e['extra_btc_annuo']:+.1f}% l'anno (beta {e['beta_btc']:.2f}).",
        f"* Bitcoin tenuto sempre: Sharpe {b['sharpe']:.2f}, {100 * b['annuo']:+.1f}% l'anno, discesa {100 * b['discesa_max']:.1f}%.",
        "* Per anno: S1 " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + "; Bitcoin "
        + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["bitcoin_per_anno"].items()) + ".",
        f"* Sharpe corretto {e['sharpe_corretto']:.2f} con {len(sr)} prove.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_QUARANTAQUATTRESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTAQUATTRESIMA FINITA", flush=True)
