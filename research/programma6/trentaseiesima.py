"""Programma 6, trentaseiesima prova (TRENTASEIESIMA.md): T5, la tendenza a 1 giorno della regola pubblicata (9 canali di
Donchian, long e short, peso secondo la volatilita') presa solo nel verso del funding: long nel 40% con il funding piu'
basso, short nel 40% piu' alto; universo delle 100, peso / 40, dal 1 gennaio 2021.

Uso: python3 -m research.programma6.trentaseiesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import trentaquattresima as tq

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentaseiesima"
DIVISORE = 40.0


def pesi(pan: dict, R: np.ndarray, Ud: np.ndarray, filtro: bool) -> np.ndarray:
    C = pan["close"]
    s = sc._per_moneta(C, lambda c: sc.segnale_moneta(c, True))
    m = sc._per_moneta(C, sc.moltiplicatore)
    s, m = np.nan_to_num(s), np.nan_to_num(m)
    if filtro:
        lungo = np.where(np.nan_to_num(R, nan=0.5) <= tq.FILTRO, np.maximum(s, 0), 0.0)
        corto = np.where(np.nan_to_num(R, nan=0.5) >= 1 - tq.FILTRO, np.minimum(s, 0), 0.0)
        s = lungo + corto
    W = s * m / DIVISORE
    domani_u = np.vstack([Ud[1:], np.zeros((1, C.shape[1]), bool)])
    domani = np.vstack([np.isfinite(pan["open"][1:]), np.zeros((1, C.shape[1]), bool)])
    return np.where(domani_u & domani & Ud, W, 0.0)


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    R, Ud = tq.rango_funding(pan, ps)
    jb = pan["simboli"].index("BTCUSDT")
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    btc = pd.Series(sc.rendimenti(pan)[:, jb], index=giorni)
    sr = tq.prove_fino_alla_trentatreesima()
    e34 = json.loads((QUI / "risultati_trentaquattresima" / "esame.json").read_text())
    sr += [e34["T1"]["portafoglio"]["intero"]["sharpe"], e34["T2"]["portafoglio"]["intero"]["sharpe"],
           json.loads((QUI / "risultati_trentacinquesima" / "esame.json").read_text())["portafoglio"]["intero"]["sharpe"]]
    RIS.mkdir(exist_ok=True)
    out = {}
    for nome, filtro in (("T5", True), ("senza filtro", False)):
        df = sc.portafoglio(pan, pesi(pan, R, Ud, filtro))
        df.to_csv(RIS / f"giorni_{'T5' if filtro else 'senza_filtro'}.csv.gz")
        out[nome] = sc.esame_a(df, btc)
    e = out["T5"]
    sr_tutte = sr + [e["intero"]["sharpe"]]
    i = e["intero"]
    e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["giorni"], i["asimmetria"], i["curtosi"], sr_tutte, 365)
    e["prove_nel_conto"] = len(sr_tutte)
    es = "VALIDA"
    if not e["boot"]["basso"] > 0:
        es = "netto con l'intervallo non sopra zero"
    elif not e["sharpe_corretto"] >= 0.95:
        es = f"Sharpe corretto {e['sharpe_corretto']:.2f} sotto 0,95"
    elif sum(1 for v in e["per_anno"].values() if v > 0) < 4:
        es = "positiva in meno di 4 anni"
    elif not e["ultimo_anno"] > 0:
        es = "non positiva nell'ultimo anno"
    elif not e["costi_doppi"] > 0:
        es = "non positiva a costi doppi"
    elif not e["extra_btc_annuo"] > 0:
        es = "niente in più del Bitcoin"
    e["esito"] = es
    d = pd.read_csv(RIS / "giorni_T5.csv.gz", index_col=0)["netto"]
    sett = d[d.index >= sc.INIZIO].groupby(((d[d.index >= sc.INIZIO].index.to_numpy() + 3) // 7) * 7 - 3).sum()
    f5 = pd.read_csv(QUI / "risultati_ventiquattresima" / "settimane_F5.csv.gz", index_col=0)["netto"]
    c = sett.index.intersection(f5.index)
    e["correlazione_F5"] = float(np.corrcoef(sett.loc[c], f5.loc[c])[0, 1])
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    s0 = out["senza filtro"]["intero"]
    testo = "\n".join([
        "# Programma 6 — risultati della trentaseiesima prova (T5: la tendenza a 1 giorno nel verso del funding)", "",
        "Regole in `TRENTASEIESIMA.md` (scritte prima). Universo delle 100, dal 1 gennaio 2021, si opera ogni giorno.", "",
        f"* T5: {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, **Sharpe {i['sharpe']:.2f}**, discesa "
        f"{100 * i['discesa_max']:.1f}%; media giornaliera {100 * e['boot']['media']:+.4f}% (intervallo {100 * e['boot']['basso']:+.4f}; "
        f"{100 * e['boot']['alto']:+.4f}).",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + f"; ultimo anno {100 * e['ultimo_anno']:+.1f}%.",
        f"* Giro {e['giro_annuo']:.0f} volte l'anno, spese {100 * e['spese_annue']:.1f}% l'anno, funding {100 * e['funding_annuo']:+.1f}% "
        f"(pagato); a costi doppi {100 * e['costi_doppi']:+.4f}% al giorno; in più del Bitcoin {100 * e['extra_btc_annuo']:+.1f}% l'anno.",
        f"* Senza il filtro (solo per capire): Sharpe {s0['sharpe']:.2f}, {100 * s0['annuo']:+.1f}% l'anno.",
        f"* Correlazione settimanale con F5 {e['correlazione_F5']:.2f}; Sharpe corretto {e['sharpe_corretto']:.2f} con {e['prove_nel_conto']} prove.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_TRENTASEIESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTASEIESIMA FINITA", flush=True)
