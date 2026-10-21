"""Programma 6, paper: la misura in avanti di N3 (`paper/REGOLE.md`, sezione 11; regola in `TRENTESIMA.md`), dal 21 ottobre
2026, su Gate.io (monete nuove non ancora perpetuo su Binance) e su Binance (monete nuove dei perpetui). Per ogni moneta con
la prima candela dal giorno d'inizio: short all'eta' di 7 giorni contro il Bitcoin, uscita a +30% (candele a 1 ora) o dopo
30 giorni. Un evento non ancora chiuso resta «in corso».
"""
from __future__ import annotations

import io
import zipfile
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

from research.programma5.strumenti.scarico import BASE as BASE_B, _prendi, elenca
from research.programma6 import scarico_gate as sg
from research.programma6 import seconda as sc
from research.programma6 import trentesima as tr
from research.programma6 import ventisettesima as vt

INIZIO = sc.giorno(2026, 10, 21)
DATI_B = sc.DATI


def _ore_binance(simbolo: str, giorni: range) -> pd.DataFrame:
    """Le candele a 1 ora di Binance dei ``giorni`` (file giornalieri dell'archivio, salvati in p6g/<S>/ore_giorni)."""
    cartella = DATI_B / simbolo / "ore_giorni"
    cartella.mkdir(parents=True, exist_ok=True)

    def uno(g):
        nome = f"{simbolo}-1h-{sc.data(g)}.zip"
        f = cartella / nome
        if not f.exists():
            dati = _prendi(f"{BASE_B}data/futures/um/daily/klines/{simbolo}/1h/{nome}")
            if not dati:
                return None
            f.write_bytes(dati)
        with zipfile.ZipFile(f) as z:
            testo = z.read(z.namelist()[0]).decode()
        righe = [r.split(",") for r in testo.split() if r and r[0].isdigit()]
        return pd.DataFrame([(int(r[0]) // 3_600_000 if int(r[0]) < 10 ** 14 else int(r[0]) // 3_600_000_000,
                              float(r[1]), float(r[2]), float(r[4])) for r in righe], columns=["ora", "open", "high", "close"])
    with ThreadPoolExecutor(max_workers=8) as ex:
        parti = [p for p in ex.map(uno, giorni) if p is not None]
    if not parti:
        return pd.DataFrame()
    return pd.concat(parti).drop_duplicates("ora").set_index("ora").sort_index()


def monete_binance() -> set:
    """I perpetui lanciati con un annuncio di moneta (simbolo nel titolo, senza «TradFi» né «Pre-IPO»)."""
    import re
    from research.programma6 import annunci as an
    out = set()
    for x in an._carica("quotazioni"):
        tit = x["titolo"]
        if "Futures Will Launch" in tit and "TradFi" not in tit and "Pre-IPO" not in tit:
            out |= set(re.findall(r"\b([0-9A-Z]{2,}USDT)\b", tit))
    return out


def binance(pan: dict, inizio: int = INIZIO) -> list:
    monete = monete_binance()
    ok = np.isfinite(pan["close"])
    primo = ok.argmax(axis=0) + pan["t0"]
    ultimo = pan["t0"] + pan["close"].shape[0] - 1
    jb = pan["simboli"].index("BTCUSDT")
    fb = pd.Series(pan["funding"][:, jb], index=np.arange(pan["close"].shape[0]) + pan["t0"])
    out = []
    for j, s in enumerate(pan["simboli"]):
        g0 = int(primo[j])
        if s == "BTCUSDT" or g0 < inizio or not ok[:, j].any() or s not in monete:
            continue
        e = g0 + tr.ETA
        r = {"mercato": "Binance", "simbolo": s, "ingresso": sc.data(e), "stato": "in attesa"}
        if e <= ultimo:
            fine = min(e + tr.GIORNI + 1, ultimo + 1)
            c, cb = _ore_binance(s, range(e, fine)), _ore_binance("BTCUSDT", range(e, fine))
            f = pd.Series(pan["funding"][:, j], index=fb.index)
            if not c.empty and not cb.empty:
                op = tr.operazione(c, cb, f, fb, e, True)
                chiuso = op and (op["fermata"] or e + tr.GIORNI <= ultimo)
                r.update({"stato": "chiuso" if chiuso else "in corso", **({"r": op["r"], "fermata": op["fermata"]} if chiuso else {})})
        out.append(r)
    return out


def gate(pan: dict, inizio: int = INIZIO) -> list:
    """Gli eventi su Gate.io dai file mensili gia' scaricati (`scarico_gate.py` con i mesi del periodo P)."""
    da, a = tr.DA, tr.A
    tr.DA, tr.A = inizio, sc.giorno(2100, 1, 1)
    try:
        cand = tr.candidati(pan)
    finally:
        tr.DA, tr.A = da, a
    if not cand:
        return []
    tr.scarica_ore(cand)
    mesi = sorted({p.name for p in (vt.DATI / "candlesticks_1h").iterdir()})
    cb = tr.ore("BTC_USDT", mesi)
    fb = vt.funding_giorni(vt._leggi("funding_applies", "BTC_USDT"))
    out = []
    for nome, g0 in cand:
        e = g0 + tr.ETA
        r = {"mercato": "Gate.io", "simbolo": nome, "ingresso": sc.data(e), "stato": "in attesa"}
        c = tr.ore(nome, sorted({tr._mese(g) for g in range(e, e + tr.GIORNI + 2)}))
        if not c.empty and not cb.empty and e * 24 in c.index:
            op = tr.operazione(c, cb, vt.funding_giorni(vt._leggi("funding_applies", nome)), fb, e, True)
            ultimo = int(min(c.index.max(), cb.index.max()) // 24)
            chiuso = op and (op["fermata"] or e + tr.GIORNI <= ultimo)
            r.update({"stato": "chiuso" if chiuso else "in corso", **({"r": op["r"], "fermata": op["fermata"]} if chiuso else {})})
        out.append(r)
    return out


def aggiorna_gate_mesi() -> None:
    """Scarica i mesi del periodo P dall'archivio di Gate.io (funding e candele giornaliere) quando ci sono."""
    import pandas as _pd
    oggi = _pd.Timestamp.now(tz="UTC").strftime("%Y%m")
    for m in sg.mesi("202610", oggi):
        for tipo in sg.TIPI:
            for k in sg.elenco(f"futures_usdt/{tipo}/{m}/"):
                if k.endswith(".csv.gz"):
                    try:
                        sg.scarica(k)
                    except Exception:
                        pass
