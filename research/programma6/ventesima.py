"""Programma 6, ventesima prova (VENTESIMA.md): la quota del volume a pronti sul volume totale (a pronti + perpetuo). S1: long
il quinto con la quota dei 7 giorni piu' alta, short il piu' basso; S2: long il quinto con la quota dei 7 giorni salita di
piu' rispetto ai 90 giorni. Portafoglio, costi ed esame come F3, dati con le correzioni di ``controllo_zombi``.

Uso: python3 -m research.programma6.ventesima
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
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te

QUI = Path(__file__).parent
RIS = QUI / "risultati_ventesima"
MIN_7, MIN_90 = 5, 60


def volume_a_pronti(pan: dict) -> np.ndarray:
    """Giorni × monete: il volume a pronti in dollari della coppia contro USDT (NaN dove manca)."""
    T, S = pan["close"].shape
    out = np.full((T, S), np.nan)
    for j, s in enumerate(pan["simboli"]):
        for f in sorted((sc.DATI / s / "spot").glob("*.zip")):
            if not f.with_suffix(".zip.ok").exists():
                continue
            df = m5._csv_da_zip(f, m5.KLINE)
            g = (m5._ms(df["open_time"]).to_numpy() // 86_400_000 - pan["t0"]).astype(np.int64)
            ok = (g >= 0) & (g < T)
            out[g[ok], j] = df["quote_volume"].to_numpy(float)[ok]
    return out


def quota(spot: np.ndarray, perp: np.ndarray, lun_idx: np.ndarray, giorni: int, minimo: int) -> np.ndarray:
    """Settimane × monete: la quota a pronti dei ``giorni`` prima del lunedi', sui giorni con tutti e due i volumi (NaN con
    meno di ``minimo`` giorni)."""
    ok = np.isfinite(spot) & np.isfinite(perp) & (np.nan_to_num(perp) > 0)
    a = np.where(ok, spot, 0.0)
    b = np.where(ok, perp, 0.0)
    ca, cb, cn = (np.vstack([np.zeros((1, spot.shape[1])), np.cumsum(x, axis=0)]) for x in (a, b, ok.astype(float)))
    i0 = np.maximum(lun_idx - giorni, 0)
    sa, sb, n = ca[lun_idx] - ca[i0], cb[lun_idx] - cb[i0], cn[lun_idx] - cn[i0]
    with np.errstate(all="ignore"):
        return np.where((n >= minimo) & (sa + sb > 0), sa / (sa + sb), np.nan)


def esegui(log=print) -> dict:
    pan0 = sc.pannello()
    pan, ps = cz.correggi(pan0, False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    spot = volume_a_pronti(pan)
    perp = pan["quote_volume"]
    q7, q90 = quota(spot, perp, lun, 7, MIN_7), quota(spot, perp, lun, 90, MIN_90)
    with np.errstate(all="ignore"):
        cambio = np.where((q7 > 0) & (q90 > 0), np.log(q7 / q90), np.nan)
    U = ps["U"]
    dentro = ps["lunedi"] >= se.INIZIO
    info = {"monete_settimana": int(U[dentro].sum()), "senza_quota_7": int((U & ~np.isfinite(q7))[dentro].sum()),
            "senza_cambio": int((U & ~np.isfinite(cambio))[dentro].sum()),
            "quota_media": float(np.nanmean(np.where(U, q7, np.nan)[dentro]))}
    log(f"[ventesima] {info}")
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    costo = sc.costi_moneta(ps["simboli"])
    f3 = pd.read_csv(QUI / "risultati_ottava" / "settimane_F3.csv.gz", index_col=0)["netto"]
    m1 = pd.read_csv(QUI / "risultati_quattordicesima" / "settimane_M1.csv.gz", index_col=0)["netto"]
    RIS.mkdir(exist_ok=True)
    sr = di.prove_fino_alla_diciassettesima()
    for n, f in (("N1", "risultati_diciottesima"), ("N2", "risultati_diciottesima"), ("P1", "risultati_diciannovesima"),
                 ("P2", "risultati_diciannovesima")):
        sr.append(json.loads((QUI / f / "esame.json").read_text())[n]["intero"]["sharpe"])
    esami = {}
    for nome, x in (("S1", q7), ("S2", cambio)):
        ct = np.where(np.isfinite(sig), x, np.nan)
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
        esami[nome] = e
        sr.append(e["intero"]["sharpe"])
        log(f"[ventesima] {nome}: Sharpe {e['intero']['sharpe']:.2f}")
    for nome, e in esami.items():
        i = e["intero"]
        e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
        e["prove_nel_conto"] = len(sr)
        e["esito"] = te.esito(e, e["sharpe_corretto"])
    esami["dati"] = info
    (RIS / "esame.json").write_text(json.dumps(esami, ensure_ascii=False, indent=1), encoding="utf-8")
    righe = ["# Programma 6 — risultati della ventesima prova (il volume a pronti contro quello del perpetuo)", "",
             "Regole in `VENTESIMA.md` (scritte prima). Le 100 monete più scambiate, dal 4 gennaio 2021, ogni lunedì; dati con "
             "le correzioni del controllo del 20 ottobre.", "",
             f"Monete-settimana {info['monete_settimana']}: senza la quota dei 7 giorni {info['senza_quota_7']}, senza il cambio "
             f"{info['senza_cambio']}; quota a pronti media {100 * info['quota_media']:.1f}%.", "",
             "| Variante | Rendimento/anno | Sharpe | Intervallo (settimana) | Sharpe corretto | Anni positivi | Ultimo anno | "
             "Dal prezzo | Dal funding | Correlazione F3, M1 | Esito |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for nome in ("S1", "S2"):
        e = esami[nome]
        i = e["intero"]
        anni = sum(1 for x in e["per_anno"].values() if x > 0)
        righe.append(f"| {nome} | {100 * i['annuo']:+.1f}% | {i['sharpe']:.2f} | {100 * e['boot']['basso']:+.2f}%; "
                     f"{100 * e['boot']['alto']:+.2f}% | {e['sharpe_corretto']:.2f} | {anni}/{len(e['per_anno'])} | "
                     f"{100 * e['ultimo_anno']:+.1f}% | {100 * e['dal_prezzo_annuo']:+.1f}% | {100 * e['dal_funding_annuo']:+.1f}% | "
                     f"{e['correlazione_F3']:.2f}, {e['correlazione_M1']:.2f} | {e['esito']} |")
    for nome in ("S1", "S2"):
        righe += ["", f"**{nome}, per anno**: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in esami[nome]["per_anno"].items())]
    righe += ["", f"Sharpe corretto con {len(sr)} prove (serve almeno 0,95)."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_VENTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return esami


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTESIMA FINITA", flush=True)
