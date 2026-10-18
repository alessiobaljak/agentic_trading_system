"""Programma 5: il calcolo comune delle idee «esplosione del prezzo + interesse aperto» (I-001, I-002, I-003).

Una variante e' un dizionario:
    L       livello dell'esplosione (multiplo della mediana di |r5| delle 24 ore prima)
    verso   -1 solo crolli, +1 solo salite, 0 tutte e due
    oi      "basso" (variazione dell'interesse aperto nel 5% piu' negativo dei 30 giorni prima), "alto" (5% piu'
            positivo) o None (nessuna condizione)
    trade   "contro" (si entra contro l'esplosione) o "segue" (nella sua direzione)
    minuti  durata del trade (uscita a tempo); la pausa per moneta e' uguale alla durata, almeno 60 minuti
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma5.strumenti.eventi import eventi, metro24, ritorno5, variazione_oi

MONETE = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT",
          "ADAUSDT", "LINKUSDT", "AVAXUSDT", "LTCUSDT", "DOTUSDT", "TRXUSDT")
QUANTILE_OI = 0.05


def per_moneta(idea: str, varianti: dict, simbolo: str, periodo: str) -> dict:
    df = m5.minuti(simbolo, periodo, idea)
    if df.empty:
        return {}
    met = m5.metrics(simbolo, periodo, idea, storia_giorni=35)
    fund = m5.funding(simbolo)
    r5 = ritorno5(df)
    metro = metro24(r5)
    _, pct_oi, presente = variazione_oi(df, met)
    base = df["periodo"].to_numpy() & presente & np.isfinite(r5) & np.isfinite(metro) & (metro > 0)
    out = {}
    for nome, v in varianti.items():
        soglia = v["L"] * metro
        if v["verso"] < 0:
            cond = base & (r5 < -soglia)
        elif v["verso"] > 0:
            cond = base & (r5 > soglia)
        else:
            cond = base & (np.abs(r5) > soglia)
        if v["oi"] == "basso":
            cond &= np.isfinite(pct_oi) & (pct_oi <= QUANTILE_OI)
        elif v["oi"] == "alto":
            cond &= np.isfinite(pct_oi) & (pct_oi >= 1 - QUANTILE_OI)
        ev = eventi(cond, max(60, v["minuti"]))
        segno_ev = np.sign(r5[ev]).astype(int)
        direzioni = -segno_ev if v["trade"] == "contro" else segno_ev
        uscita = m5.Uscita(minuti=v["minuti"])
        t = m5.simula(df, simbolo, ev, direzioni, uscita, fund, esplosione=np.ones(len(ev), bool))
        c = m5.caso(df, simbolo, t, uscita, fund) if not t.empty else t
        out[nome] = (t, c)
    return out


def calcola(idea: str, varianti: dict, periodo: str, cartella: Path, monete=MONETE) -> dict:
    raccolti = {n: ([], []) for n in varianti}
    for s in monete:
        ris = per_moneta(idea, varianti, s, periodo)
        for n, (t, c) in ris.items():
            raccolti[n][0].append(t)
            raccolti[n][1].append(c)
        print(f"[{idea} {periodo}] {s}: " + ", ".join(f"{n} {len(t)}" for n, (t, _) in ris.items()), flush=True)
    esito = {}
    for n, (tt, cc) in raccolti.items():
        pieni_t = [x for x in tt if not x.empty]
        pieni_c = [x for x in cc if not x.empty]
        t = pd.concat(pieni_t, ignore_index=True) if pieni_t else pd.DataFrame()
        c = pd.concat(pieni_c, ignore_index=True) if pieni_c else pd.DataFrame()
        esito[n] = m5.esame(t, c, n_boot=10000 if periodo != "C" else 2000)
        if not t.empty:
            t.to_csv(cartella / f"trade_{periodo}_{n}.csv.gz", index=False)
    (cartella / f"{periodo}.json").write_text(json.dumps(esito, ensure_ascii=False, indent=1, default=float),
                                              encoding="utf-8")
    return esito


def riassunto(esito: dict) -> str:
    righe = []
    for n, e in esito.items():
        if not e.get("trade"):
            righe.append(f"{n}: nessun trade")
            continue
        nt, nd = e["netto"], e["netto_doppio"]
        righe.append(f"{n}: {e['trade']} trade · netto {100 * nt['media']:+.3f}% ({100 * nt['basso']:+.3f}; "
                     f"{100 * nt['alto']:+.3f}) p {nt['p']:.4f} · a costi doppi {100 * nd['media']:+.3f}% · "
                     f"caso {100 * e.get('caso_netto', float('nan')):+.3f}% · lordo {100 * e['lordo']:+.3f}%")
    return "\n".join(righe)
