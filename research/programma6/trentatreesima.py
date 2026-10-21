"""Programma 6, trentatreesima prova (TRENTATREESIMA.md): N3 a portafoglio (5% del capitale per gamba a operazione, al
massimo 20 aperte, valore giorno per giorno) e F5 + N3 a rischio uguale. Dal 4 gennaio 2021.

Uso: python3 -m research.programma6.trentatreesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import quindicesima as qd
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import trentesima as tr
from research.programma6 import ventinovesima as vn
from research.programma6 import ventunesima as vu

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentatreesima"
QUOTA, MAX_APERTE = 0.05, 20


def giorni_n3(pan: dict, eventi: pd.DataFrame) -> tuple:
    """(rendimento giornaliero del portafoglio N3 netto, lo stesso a costi doppi, operazioni aperte, saltate)."""
    O, C, F = pan["open"], pan["close"], pan["funding"]
    T = C.shape[0]
    jb = pan["simboli"].index("BTCUSDT")
    netto, spese, aperte = np.zeros(T), np.zeros(T), np.zeros(T)
    uscite, saltate = [], 0
    for _, ev in eventi.sort_values("data").iterrows():
        e = sc.giorno(*map(int, ev["data"].split("-"))) - pan["t0"]
        g_usc = e + int(np.floor(ev["giorni"])) if ev["fermata"] else e + tr.GIORNI
        uscite = [u for u in uscite if u > e]
        if len(uscite) >= MAX_APERTE:
            saltate += 1
            continue
        uscite.append(g_usc)
        j = pan["simboli"].index(ev["simbolo"])
        p0 = O[e, j]
        p_usc = p0 * (1 + tr.STOP) * (1 + tr.SCARTO_STOP) if ev["fermata"] else None
        prec_c, prec_b = p0, O[e, jb]
        for d in range(e, min(g_usc, T - 1) + 1):
            if d == g_usc:
                pc = p_usc if p_usc is not None else (O[d, j] if np.isfinite(O[d, j]) else prec_c)
                pb = C[d, jb] if p_usc is not None else O[d, jb]
            else:
                pc = C[d, j] if np.isfinite(C[d, j]) else prec_c
                pb = C[d, jb]
            rc, rb = pc / prec_c - 1, pb / prec_b - 1
            netto[d] += QUOTA * (rb - rc)
            if d < g_usc:
                netto[d] += QUOTA * (F[d, j] - F[d, jb])
                aperte[d] += 1
            prec_c, prec_b = pc, pb
        for d in (e, min(g_usc, T - 1)):
            c = QUOTA * (vu.COSTO_MONETA + vu.COSTO_BTC) / 2
            netto[d] -= c
            spese[d] += c
    return netto, netto - spese, aperte, saltate


def settimane(giornaliero: np.ndarray, t0: int) -> pd.Series:
    giorni = np.arange(len(giornaliero)) + t0
    lun = ((giorni + 3) // 7) * 7 - 3
    return pd.Series(giornaliero, index=lun).groupby(level=0).apply(lambda x: float(np.prod(1 + x.to_numpy()) - 1))


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ev = pd.read_csv(QUI / "risultati_trentaduesima" / "eventi_N3B.csv")
    ev = ev[np.isfinite(ev["r"])]
    netto, doppio, aperte, saltate = giorni_n3(pan, ev)
    sn, sd = settimane(netto, pan["t0"]), settimane(doppio, pan["t0"])
    sa = pd.Series(aperte, index=((np.arange(len(aperte)) + pan["t0"] + 3) // 7) * 7 - 3).groupby(level=0).mean()
    n3 = pd.DataFrame({"netto": sn, "netto_doppio": sd, "lordo": 0.0, "spese": 0.0, "funding": 0.0, "giro": 0.0,
                       "long": 0.0, "short": 0.0, "monete": sa.reindex(sn.index).fillna(0).to_numpy()})
    f5 = pd.read_csv(QUI / "risultati_ventiquattresima" / "settimane_F5.csv.gz", index_col=0)
    insieme = qd.combina({"F5": f5, "N3": n3})
    RIS.mkdir(exist_ok=True)
    n3.to_csv(RIS / "settimane_N3.csv.gz")
    insieme.to_csv(RIS / "settimane_F5_N3.csv.gz")
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    from research.programma6 import venticinquesima as v25
    sr = v25.prove_fino_alla_ventiquattresima()
    for f, chiavi in (("risultati_venticinquesima", ("M7", "F5 + M7")), ("risultati_ventottesima", ("K2", "F5 + M7 + K2"))):
        e_ = json.loads((QUI / f / "esame.json").read_text())
        sr += [e_[k]["intero"]["sharpe"] for k in chiavi]
    sr += [json.loads((QUI / f / "esame.json").read_text())["intero"]["sharpe"]
           for f in ("risultati_ventinovesima", "risultati_trentunesima")]
    esami = {}
    for nome, df in (("N3 a portafoglio", n3), ("F5 + N3", insieme)):
        esami[nome] = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        sr.append(esami[nome]["intero"]["sharpe"])
    for nome in esami:
        i = esami[nome]["intero"]
        esami[nome]["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
        esami[nome]["prove_nel_conto"] = len(sr)
        esami[nome]["esito"] = te.esito(esami[nome], esami[nome]["sharpe_corretto"])
    d5 = f5[f5.index >= se.INIZIO]["netto"]
    c = d5.index.intersection(sn.index)
    info = {"saltate": saltate, "operazioni": int(len(ev)), "aperte_in_media": float(aperte[aperte > 0].mean()),
            "correlazione_F5_N3": float(np.corrcoef(d5.loc[c], sn.loc[c])[0, 1]), "F5_stessi_anni": te.numeri_settimana(d5)}
    esami["informazioni"] = info
    (RIS / "esame.json").write_text(json.dumps(esami, ensure_ascii=False, indent=1), encoding="utf-8")
    righe = ["# Programma 6 — risultati della trentatreesima prova (N3 a portafoglio; F5 + N3)", "",
             "Regole in `TRENTATREESIMA.md` (scritte prima). Dal 4 gennaio 2021; N3 con il 5% del capitale per gamba a "
             f"operazione, al massimo 20 aperte ({saltate} operazioni saltate su {len(ev)}; aperte in media "
             f"{info['aperte_in_media']:.1f} quando ce n'è almeno una).", "",
             "| Portafoglio | Rendimento/anno | Volatilità | Sharpe | Discesa massima | Sharpe corretto | Anni positivi | Ultimo anno | Esito |",
             "|---|---|---|---|---|---|---|---|---|"]
    for nome in ("N3 a portafoglio", "F5 + N3"):
        e = esami[nome]
        i = e["intero"]
        anni = sum(1 for x in e["per_anno"].values() if x > 0)
        righe.append(f"| {nome} | {100 * i['annuo']:+.1f}% | {100 * i['volatilita']:.1f}% | {i['sharpe']:.2f} | "
                     f"{100 * i['discesa_max']:.1f}% | {e['sharpe_corretto']:.2f} | {anni}/{len(e['per_anno'])} | "
                     f"{100 * e['ultimo_anno']:+.1f}% | {e['esito']} |")
    f5s = info["F5_stessi_anni"]
    righe.append(f"| F5 (confronto) | {100 * f5s['annuo']:+.1f}% | {100 * f5s['volatilita']:.1f}% | {f5s['sharpe']:.2f} | "
                 f"{100 * f5s['discesa_max']:.1f}% | — | — | — | — |")
    for nome in ("N3 a portafoglio", "F5 + N3"):
        righe += ["", f"**{nome}, per anno**: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in esami[nome]["per_anno"].items())]
    righe += ["", f"Correlazione settimanale fra F5 e N3: {info['correlazione_F5_N3']:.2f}. Sharpe corretto con {len(sr)} prove."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_TRENTATREESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return esami


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTATREESIMA FINITA", flush=True)
