"""Programma 7, ottava prova (OTTAVA.md): G7, il long (contro il Bitcoin) il giorno dopo una salita di almeno +30% sui perpetui
di Gate.io delle monete senza il perpetuo su Binance; uscita a −30% o dopo 30 giorni.

Uso: python3 -m research.programma7.ottava
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import annunci as an
from research.programma6 import seconda as sc
from research.programma6 import tipi_gate as tg
from research.programma6 import trentesima as tr
from research.programma6 import ventisettesima as vt
from research.programma6 import ventunesima as vu

QUI = Path(__file__).parent
RIS = QUI / "risultati_ottava"
SALITA, ETA_MIN, DISTANZA, GIORNI, STOP, SCARTO = 0.30, 30, 30, 30, 0.30, 0.01
DA, A = sc.giorno(2023, 2, 1), sc.giorno(2026, 8, 31)


def candele_complete(righe: list) -> pd.DataFrame:
    """Giorno → apertura, massimo, minimo, chiusura, volume (colonne di Gate.io: t, v, c, h, l, o)."""
    if not righe:
        return pd.DataFrame()
    d = pd.DataFrame([(int(r[0]) // 86400, float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])) for r in righe],
                     columns=["giorno", "volume", "close", "high", "low", "open"]).drop_duplicates("giorno", keep="last")
    return d.set_index("giorno").sort_index()


def eventi(c: pd.DataFrame, fuori_da: int) -> list:
    """I giorni d'ingresso (il giorno dopo una salita di almeno SALITA, apertura su apertura), con almeno ETA_MIN giorni di
    candele prima, volume non zero, ingresso fra DA e A e prima di ``fuori_da`` (il primo giorno su Binance), uno ogni DISTANZA."""
    out, ultimo = [], -10 ** 9
    if c.empty:
        return out
    g0 = int(c.index[0])
    o = c["open"]
    for g in c.index:
        g = int(g)
        if g + 1 not in o.index or not (o[g] > 0) or c.loc[g, "volume"] <= 0:
            continue
        e = g + 1
        if o[e] / o[g] - 1 < SALITA or g - g0 < ETA_MIN or not (DA <= e <= A) or e >= fuori_da or e - ultimo < DISTANZA:
            continue
        out.append(e)
        ultimo = e
    return out


def operazione(c: pd.DataFrame, cb: pd.DataFrame, f: pd.Series, fb: pd.Series, e: int, protezione: bool) -> dict:
    """Long la moneta e short il Bitcoin dall'apertura del giorno ``e``; con ``protezione`` l'uscita a −30% (minimo del giorno)."""
    if e not in c.index or e not in cb.index:
        return {}
    p0, b0 = c.loc[e, "open"], cb.loc[e, "open"]
    tratto = c[(c.index >= e) & (c.index < e + GIORNI)]
    uscita_g, pc, fermata = None, None, False
    if protezione:
        giu = tratto.index[tratto["low"].to_numpy() <= p0 * (1 - STOP)]
        if len(giu):
            uscita_g, pc, fermata = int(giu[0]), p0 * (1 - STOP) * (1 - SCARTO), True
    if uscita_g is None:
        if e + GIORNI in c.index:
            uscita_g, pc = e + GIORNI, c.loc[e + GIORNI, "open"]
        elif len(tratto):
            uscita_g, pc = int(tratto.index[-1]) + 1, tratto["close"].iloc[-1]
        else:
            return {}
    bb = cb[cb.index <= uscita_g]
    pb = cb.loc[uscita_g, "open"] if (not fermata and uscita_g in cb.index) else bb["close"].iloc[-1]
    fc = f[(f.index >= e) & (f.index <= uscita_g)].sum()
    fbb = fb[(fb.index >= e) & (fb.index <= uscita_g)].sum()
    r = (pc / p0 - 1) - (pb / b0 - 1) - vu.COSTO_MONETA - vu.COSTO_BTC - fc + fbb
    return {"r": float(r), "fermata": fermata, "giorni": float(uscita_g - e)}


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ok = np.isfinite(pan["close"])
    primo_b = ok.argmax(axis=0) + pan["t0"]
    tipi = tg.carica()
    cb = candele_complete(vt._leggi("candlesticks_1d", "BTC_USDT"))
    fb = vt.funding_giorni(vt._leggi("funding_applies", "BTC_USDT"))
    nomi = sorted({f.name.rsplit("-", 1)[0] for f in (vt.DATI / "candlesticks_1d").glob("*/*.csv.gz")})
    righe = []
    contratti = 0
    for nome in nomi:
        sigla = nome.split("_")[0]
        if not nome.endswith("_USDT") or nome == "BTC_USDT" or f"{sigla}USDT" in sc.ESCLUSI or not tg.moneta(nome, tipi) \
                or sigla in tr.STABILI:
            continue
        p = an.perpetuo(sigla, pan["simboli"])
        fuori_da = int(primo_b[pan["simboli"].index(p)]) if p else 10 ** 9
        c = candele_complete(vt._leggi("candlesticks_1d", nome))
        ev = eventi(c, fuori_da)
        if not ev:
            continue
        contratti += 1
        f = vt.funding_giorni(vt._leggi("funding_applies", nome))
        for e in ev:
            con, senza = operazione(c, cb, f, fb, e, True), operazione(c, cb, f, fb, e, False)
            if con and senza:
                righe.append({"data": sc.data(e), "annuncio": int((e + 3) // 7), "contratto": nome,
                              "salita": float(c.loc[e, "open"] / c.loc[e - 1, "open"] - 1),
                              "r": con["r"], "fermata": con["fermata"], "giorni": con["giorni"], "r_senza": senza["r"]})
    df = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_G7.csv", index=False)
    out = {"con_uscita": tr.esame(df, "r"), "senza_uscita": tr.esame(df, "r_senza"), "fermate": float(df["fermata"].mean()),
           "contratti_con_eventi": contratti}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    righe_t = ["# Programma 7 — risultati dell'ottava prova (G7: il long dopo una salita enorme, su Gate.io)", "",
               "Regole in `OTTAVA.md` (scritte prima). Long contro il Bitcoin all'apertura del giorno dopo una salita di almeno +30%, "
               "monete senza il perpetuo su Binance; uscita a −30% (1% di scarto) o dopo 30 giorni.", "",
               f"Contratti con almeno un evento: {contratti}.", "",
               "| Versione | Eventi (settimane) | Media a evento | Intervallo | p | Mediana | Vinti | Prima metà, seconda metà | "
               "Senza i 5 migliori | Esito |", "|---|---|---|---|---|---|---|---|---|---|"]
    for nome, x in (("con l'uscita a −30% (la regola)", out["con_uscita"]), ("senza l'uscita (per capire)", out["senza_uscita"])):
        b = x["boot"]
        righe_t.append(f"| {nome} | {b['eventi']} ({b['annunci']}) | {100 * b['media']:+.2f}% | {100 * b['basso']:+.2f}%; "
                       f"{100 * b['alto']:+.2f}% | {b['p']:.4f} | {100 * x['mediana']:+.2f}% | {100 * x['vinti']:.0f}% | "
                       f"{100 * x['prima_meta']:+.2f}%, {100 * x['seconda_meta']:+.2f}% | {100 * x['senza_5_migliori']:+.2f}% | "
                       f"{x['esito'] if 'regola' in nome else '—'} |")
    righe_t += ["", f"L'uscita a −30% scatta nel {100 * out['fermate']:.0f}% degli eventi.", "",
                "**Per anno (con l'uscita)**: " + ", ".join(f"{a} {100 * v['media']:+.2f}% ({v['eventi']})"
                                                         for a, v in out["con_uscita"]["per_anno"].items())]
    testo = "\n".join(righe_t) + "\n"
    (QUI / "RISULTATI_OTTAVA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("OTTAVA FINITA", flush=True)
