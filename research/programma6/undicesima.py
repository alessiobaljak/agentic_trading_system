"""Programma 6, undicesima prova (UNDICESIMA.md): P1 (grandi contro piccoli: log del rapporto long/short delle posizioni
dei conti grandi meno log di quello dei conti di tutti, media dei 7 giorni prima, si segue) e P2 (crescita dell'interesse
aperto in 7 giorni, si va contro), fra le 100 monete piu' scambiate, pesi secondo la volatilita', dal 3 gennaio 2022.

Uso: python3 -m research.programma6.undicesima
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import nona as no
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6.scarico_metrics import DATI as DATI_M

QUI = Path(__file__).parent
RIS = QUI / "risultati_undicesima"
INIZIO = sc.giorno(2022, 1, 3)
ANNI_PIENI = (2022, 2023, 2024, 2025)


def pannello_metrics(pan: dict) -> dict:
    T, S = pan["close"].shape
    out = {k: np.full((T, S), np.nan) for k in ("oi", "grandi", "tutti")}
    for j, s in enumerate(pan["simboli"]):
        f = DATI_M / f"{s}.pkl"
        if not f.exists():
            continue
        d = pd.read_pickle(f)
        d = d[(d.index >= pan["t0"]) & (d.index < pan["t0"] + T)]
        r = d.index.to_numpy() - pan["t0"]
        out["oi"][r, j] = d["oi_valore_fine"].to_numpy(float)
        out["grandi"][r, j] = d["sum_toptrader_long_short_ratio"].to_numpy(float)
        out["tutti"][r, j] = d["count_long_short_ratio"].to_numpy(float)
    return out


def p1(pm: dict, lun_idx: np.ndarray) -> np.ndarray:
    with np.errstate(all="ignore"):
        x = np.log(pm["grandi"]) - np.log(pm["tutti"])
    x[~np.isfinite(x)] = np.nan
    out = np.full((len(lun_idx), x.shape[1]), np.nan)
    for k, m in enumerate(lun_idx):
        f = x[max(0, m - 7): m]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            mu = np.nanmean(f, axis=0)
        out[k] = np.where(np.isfinite(f).sum(axis=0) >= 5, mu, np.nan)
    return out


def p2(pm: dict, lun_idx: np.ndarray) -> np.ndarray:
    oi = pm["oi"]
    with np.errstate(all="ignore"):
        out = np.log(oi[lun_idx - 1]) - np.log(oi[lun_idx - 8])
    out[~np.isfinite(out)] = np.nan
    return out


def portafoglio(pan, ps, costo, s, segno) -> pd.DataFrame:
    """``segno`` +1: long il quinto con il segnale piu' alto; -1: long il piu' basso."""
    lun_idx = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun_idx)
    ct = np.where(np.isfinite(sig) & np.isfinite(s), segno * s, np.nan)
    Wt = te.pesi_portafoglio(ct, ps["U"], np.nan_to_num(1.0 / sig), True)
    df = te.conto(Wt, ps["R"], ps["F"], costo)
    df.index = ps["lunedi"]
    return df


def esegui(log=print) -> dict:
    pan = sc.pannello()
    pm = pannello_metrics(pan)
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun_idx = ps["lunedi"] - pan["t0"]
    costo = sc.costi_moneta(ps["simboli"])
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    RIS.mkdir(exist_ok=True)
    sr = sc.sharpe_prove()
    for v in ("C1", "C2", "C3"):
        sr.append(json.loads((te.RIS / f"{v}.json").read_text())["intero"]["sharpe"])
    for v in ("F1", "F2"):
        sr.append(json.loads((se.RIS / f"{v}.json").read_text())["intero"]["sharpe"])
    sr.append(json.loads((ot.RIS / "esame.json").read_text())["cento"]["intero"]["sharpe"])
    nn = json.loads((no.RIS / "esame.json").read_text())
    sr += [nn["G1"]["cento"]["intero"]["sharpe"], nn["G2"]["cento"]["intero"]["sharpe"]]
    sr.append(json.loads((QUI / "risultati_decima" / "esame.json").read_text())["cento"]["intero"]["sharpe"])
    esami = {}
    for nome, s, segno in (("P1", p1(pm, lun_idx), 1.0), ("P2", p2(pm, lun_idx), -1.0)):
        df = portafoglio(pan, ps, costo, s, segno)
        df.to_csv(RIS / f"settimane_{nome}.csv.gz")
        e = te.esame(df, btc, inizio=INIZIO, anni_pieni=ANNI_PIENI)
        d = df[df.index >= INIZIO]
        e["dal_funding_annuo"] = float(-d["funding"].mean() * 52)
        e["dal_prezzo_annuo"] = float(d["lordo"].mean() * 52)
        e["monete_con_dato"] = int(np.isfinite(s[lun_idx + pan["t0"] >= INIZIO]).sum(axis=1).mean())
        esami[nome] = e
        sr.append(e["intero"]["sharpe"])
    out = {}
    for nome, e in esami.items():
        i = e["intero"]
        e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
        e["prove_nel_conto"] = len(sr)
        es = te.esito(e, e["sharpe_corretto"])
        if es == "VALIDA" and not (e["per_anno"].get(2022, -1) > 0 and e["ultimo_anno"] > 0):
            es = "non positiva nel 2022 o nell'ultimo anno"
        e["esito"] = es
        out[nome] = e
        log(f"[undicesima] {nome}: {es}")
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def rapporto() -> str:
    r = json.loads((RIS / "esame.json").read_text())
    righe = ["# Programma 6 — risultati dell'undicesima prova (l'affollamento misurato con le posizioni)", "",
             "Regole in `UNDICESIMA.md` (scritte prima di avere i dati). Le 100 monete più scambiate, dal 3 gennaio 2022, "
             "pesi secondo la volatilità.", "",
             "| Segnale | Rendimento/anno | Sharpe | Intervallo (settimana) | Sharpe corretto | Anni positivi | 2022 | Ultimo anno | "
             "Dal prezzo | Dal funding | Monete con il dato | Esito |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for nome in ("P1", "P2"):
        e = r[nome]
        i = e["intero"]
        anni = sum(1 for x in e["per_anno"].values() if x > 0)
        righe.append(f"| {nome} | {100 * i['annuo']:+.1f}% | {i['sharpe']:.2f} | {100 * e['boot']['basso']:+.2f}%; "
                     f"{100 * e['boot']['alto']:+.2f}% | {e['sharpe_corretto']:.2f} | {anni}/{len(e['per_anno'])} | "
                     f"{100 * e['per_anno'].get('2022', float('nan')):+.1f}% | {100 * e['ultimo_anno']:+.1f}% | "
                     f"{100 * e['dal_prezzo_annuo']:+.1f}% | {100 * e['dal_funding_annuo']:+.1f}% | {e['monete_con_dato']} | {e['esito']} |")
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_UNDICESIMA.md").write_text(testo, encoding="utf-8")
    return testo


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print(rapporto())
    print("UNDICESIMA FINITA", flush=True)
