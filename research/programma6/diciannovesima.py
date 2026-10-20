"""Programma 6, diciannovesima prova (DICIANNOVESIMA.md): il premio del perpetuo sullo spot fra monete. P1: long il quinto
con la media del premio orario delle 168 ore prima piu' bassa, short il piu' alto; P2: la media dei ranghi di −funding dei
7 giorni e −premio. Portafoglio, costi ed esame come F3, dati con le correzioni di ``controllo_zombi``.

Uso: python3 -m research.programma6.diciannovesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import controllo_zombi as cz
from research.programma6 import diciottesima as di
from research.programma6 import ottava as ot
from research.programma6 import quattordicesima as q
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te

QUI = Path(__file__).parent
RIS = QUI / "risultati_diciannovesima"
ORE, MIN_ORE = 168, 120


def premio_orario(pan: dict) -> np.ndarray:
    """Ore × monete: la chiusura oraria dell'indice del premio (NaN dove manca)."""
    T, S = pan["close"].shape
    H, h0 = T * 24, pan["t0"] * 24
    out = np.full((H, S), np.nan, np.float32)
    for j, s in enumerate(pan["simboli"]):
        for f in sorted((sc.DATI / s / "premio_mesi").glob("*.zip")):
            if not f.with_suffix(".zip.ok").exists():
                continue
            df = m5._csv_da_zip(f, m5.KLINE)
            h = (m5._ms(df["open_time"]).to_numpy() // 3_600_000 - h0).astype(np.int64)
            ok = (h >= 0) & (h < H)
            out[h[ok], j] = df["close"].to_numpy(float)[ok]
    return out


def premio_7(P: np.ndarray, lun_idx: np.ndarray) -> np.ndarray:
    """Settimane × monete: la media del premio delle 168 ore prima del lunedi' alle 00:00 (NaN con meno di 120 ore)."""
    v = np.nan_to_num(P.astype(np.float64))
    n = np.isfinite(P).astype(np.int64)
    cs = np.vstack([np.zeros((1, P.shape[1])), np.cumsum(v, axis=0)])
    cn = np.vstack([np.zeros((1, P.shape[1]), np.int64), np.cumsum(n, axis=0)])
    fine = lun_idx * 24
    inizio = np.maximum(fine - ORE, 0)
    somma, quante = cs[fine] - cs[inizio], cn[fine] - cn[inizio]
    with np.errstate(all="ignore"):
        return np.where(quante >= MIN_ORE, somma / np.maximum(quante, 1), np.nan)


def settimane_pari(S7: np.ndarray, U: np.ndarray) -> np.ndarray:
    """Vero nelle settimane in cui il confine del quinto alto o basso cade fra monete con lo stesso funding dei 7 giorni."""
    out = np.zeros(len(S7), bool)
    for k in range(len(S7)):
        idx = np.flatnonzero(U[k] & np.isfinite(S7[k]))
        kq = len(idx) // 5
        if kq < 1:
            continue
        o = np.sort(np.round(S7[k, idx], 7))
        out[k] = o[-kq] == o[-kq - 1] or o[kq - 1] == o[kq]
    return out


def segnale(nome: str, S7: np.ndarray, Pr7: np.ndarray, U: np.ndarray) -> np.ndarray:
    if nome == "P1":
        return -Pr7
    a, b = q.rango_nan(-S7, U & np.isfinite(Pr7)), q.rango_nan(-Pr7, U & np.isfinite(S7))
    return (a + b) / 2


def esegui(log=print) -> dict:
    pan0 = sc.pannello()
    pan, ps = cz.correggi(pan0, False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    S7 = se.funding_7(pan, lun)
    P = premio_orario(pan)
    Pr7 = premio_7(P, lun)
    del P
    U = ps["U"]
    dentro = ps["lunedi"] >= se.INIZIO
    mancanti = int((U & ~np.isfinite(Pr7))[dentro].sum())
    log(f"[diciannovesima] monete-settimana senza premio: {mancanti} su {int(U[dentro].sum())}")
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    costo = sc.costi_moneta(ps["simboli"])
    f3 = pd.read_csv(QUI / "risultati_ottava" / "settimane_F3.csv.gz", index_col=0)["netto"]
    m1 = pd.read_csv(QUI / "risultati_quattordicesima" / "settimane_M1.csv.gz", index_col=0)["netto"]
    f3_qui = ot.portafoglio_f3(pan, ps, costo)
    pari = settimane_pari(S7, U) & dentro
    RIS.mkdir(exist_ok=True)
    sr = di.prove_fino_alla_diciassettesima()
    e18 = json.loads((QUI / "risultati_diciottesima" / "esame.json").read_text())
    sr += [e18["N1"]["intero"]["sharpe"], e18["N2"]["intero"]["sharpe"]]
    esami = {}
    for nome in ("P1", "P2"):
        ct = np.where(np.isfinite(sig), segnale(nome, S7, Pr7, U), np.nan)
        Wt = te.pesi_portafoglio(ct, U, np.nan_to_num(1.0 / sig), True)
        df = te.conto(Wt, ps["R"], ps["F"], costo)
        df.index = ps["lunedi"]
        df.to_csv(RIS / f"settimane_{nome}.csv.gz")
        e = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        d = df[df.index >= se.INIZIO]
        e["dal_funding_annuo"] = float(-d["funding"].mean() * 52)
        e["dal_prezzo_annuo"] = float(d["lordo"].mean() * 52)
        for n, s in (("F3", f3), ("M1", m1)):
            c = d.index.intersection(s.index)
            e[f"correlazione_{n}"] = float(np.corrcoef(d.loc[c, "netto"], s.loc[c])[0, 1])
        e["settimane_pari"] = {"settimane": int(pari.sum()), "media": float(df["netto"].to_numpy()[pari].mean()),
                               "media_F3": float(f3_qui["netto"].to_numpy()[pari].mean())}
        esami[nome] = e
        sr.append(e["intero"]["sharpe"])
        log(f"[diciannovesima] {nome}: Sharpe {e['intero']['sharpe']:.2f}")
    for nome, e in esami.items():
        i = e["intero"]
        e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
        e["prove_nel_conto"] = len(sr)
        e["esito"] = te.esito(e, e["sharpe_corretto"])
    d3 = f3_qui[f3_qui.index >= se.INIZIO]["netto"]
    esami["F3_sugli_stessi_dati"] = {"sharpe": float(d3.mean() / d3.std(ddof=1) * np.sqrt(52)), "annuo": float(d3.mean() * 52)}
    esami["monete_settimana_senza_premio"] = mancanti
    (RIS / "esame.json").write_text(json.dumps(esami, ensure_ascii=False, indent=1), encoding="utf-8")
    righe = ["# Programma 6 — risultati della diciannovesima prova (il premio del perpetuo sullo spot fra monete)", "",
             "Regole in `DICIANNOVESIMA.md` (scritte prima). Le 100 monete più scambiate, dal 4 gennaio 2021, ogni lunedì; dati "
             "con le correzioni del controllo del 20 ottobre.", "",
             f"Monete-settimana senza il premio: {mancanti} su {int(U[dentro].sum())}. F3 sugli stessi dati: Sharpe "
             f"{esami['F3_sugli_stessi_dati']['sharpe']:.2f}, {100 * esami['F3_sugli_stessi_dati']['annuo']:+.1f}% l'anno.", "",
             "| Variante | Rendimento/anno | Sharpe | Intervallo (settimana) | Sharpe corretto | Anni positivi | Ultimo anno | "
             "Dal prezzo | Dal funding | Correlazione F3, M1 | Settimane dei pari: questa, F3 | Esito |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for nome in ("P1", "P2"):
        e = esami[nome]
        i = e["intero"]
        sp = e["settimane_pari"]
        anni = sum(1 for x in e["per_anno"].values() if x > 0)
        righe.append(f"| {nome} | {100 * i['annuo']:+.1f}% | {i['sharpe']:.2f} | {100 * e['boot']['basso']:+.2f}%; "
                     f"{100 * e['boot']['alto']:+.2f}% | {e['sharpe_corretto']:.2f} | {anni}/{len(e['per_anno'])} | "
                     f"{100 * e['ultimo_anno']:+.1f}% | {100 * e['dal_prezzo_annuo']:+.1f}% | {100 * e['dal_funding_annuo']:+.1f}% | "
                     f"{e['correlazione_F3']:.2f}, {e['correlazione_M1']:.2f} | {100 * sp['media']:+.2f}%, {100 * sp['media_F3']:+.2f}% "
                     f"a settimana ({sp['settimane']}) | {e['esito']} |")
    for nome in ("P1", "P2"):
        righe += ["", f"**{nome}, per anno**: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in esami[nome]["per_anno"].items())]
    righe += ["", f"Sharpe corretto con {len(sr)} prove (serve almeno 0,95)."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_DICIANNOVESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return esami


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("DICIANNOVESIMA FINITA", flush=True)
