"""Programma 6, trentacinquesima prova (TRENTACINQUESIMA.md): T3, contro gli eccessi. Short quando l'RSI a 14 candele da 4
ore passa sopra 70 e il funding dei 7 giorni e' nel 40% piu' alto; long quando passa sotto 30 e il funding e' nel 40% piu'
basso. Stop a 2 ATR, uscita quando l'RSI torna a 50, al massimo 42 candele. Monete, costi ed esame come la prova 34.

Uso: python3 -m research.programma6.trentacinquesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

from research.programma5.strumenti import motore5 as m5
from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import trentaquattresima as tq
from research.programma6.motore import TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentacinquesima"
N_RSI, ALTO, BASSO, CENTRO = 14, 70.0, 30.0, 50.0
P_SOGLIA = 0.01


def rsi(c: np.ndarray, n: int = N_RSI) -> np.ndarray:
    """RSI con la media di Wilder."""
    d = np.diff(c, prepend=np.nan)
    su, giu = pd.Series(np.where(d > 0, d, 0.0)), pd.Series(np.where(d < 0, -d, 0.0))
    ms, mg = su.ewm(alpha=1 / n, adjust=False, min_periods=n).mean(), giu.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    with np.errstate(all="ignore"):
        return (100 - 100 / (1 + ms / mg)).to_numpy()


@njit(cache=True)
def _simula(o, h, l, c, segnali_long, segnali_short, atr, r):
    n = len(c)
    out = []
    i = 0
    while i < n - 1:
        verso = 1 if segnali_long[i] else (-1 if segnali_short[i] else 0)
        if verso == 0 or not atr[i] > 0:
            i += 1
            continue
        e = i + 1
        p0 = o[e]
        stop = p0 - verso * 2.0 * atr[i]
        uscita, prezzo, motivo = -1, 0.0, 0
        j = e
        while j < n:
            if verso > 0 and o[j] <= stop:
                uscita, prezzo, motivo = j, o[j], 1
            elif verso > 0 and l[j] <= stop:
                uscita, prezzo, motivo = j, stop, 1
            elif verso < 0 and o[j] >= stop:
                uscita, prezzo, motivo = j, o[j], 1
            elif verso < 0 and h[j] >= stop:
                uscita, prezzo, motivo = j, stop, 1
            if uscita >= 0:
                break
            if j + 1 < n and ((verso > 0 and r[j] >= CENTRO) or (verso < 0 and r[j] <= CENTRO)):
                uscita, prezzo, motivo = j + 1, o[j + 1], 2
                break
            if j - e + 1 >= 42 and j + 1 < n:
                uscita, prezzo, motivo = j + 1, o[j + 1], 3
                break
            j += 1
        if uscita < 0:
            break
        out.append((i, e, uscita, verso, p0, prezzo, motivo))
        i = uscita
    return out


def operazioni(pan: dict, R: np.ndarray, Ud: np.ndarray) -> pd.DataFrame:
    sim = pan["simboli"]
    righe = []
    for j in np.flatnonzero(Ud.any(axis=0)):
        s = sim[j]
        b = tq.quattro_ore(es.ore_di(s))
        if len(b) < 40:
            continue
        o, h, l, c = (b[k].to_numpy(float) for k in ("open", "high", "low", "close"))
        blocco = b.index.to_numpy()
        giorno = blocco * 4 // 24 - pan["t0"]
        cp = np.r_[np.nan, c[:-1]]
        atr = pd.Series(np.nanmax(np.vstack([h - l, np.abs(h - cp), np.abs(l - cp)]), axis=0)).rolling(14).mean().to_numpy()
        rr = rsi(c)
        prima = np.r_[np.nan, rr[:-1]]
        g = np.clip(giorno, 0, Ud.shape[0] - 1)
        nel = (giorno >= 0) & (giorno < Ud.shape[0]) & Ud[g, j] & (giorno + pan["t0"] >= tq.DA) & (giorno + pan["t0"] <= tq.A)
        rk = R[g, j]
        corto = nel & (rr >= ALTO) & (prima < ALTO) & (rk >= 1 - tq.FILTRO)
        lungo = nel & (rr <= BASSO) & (prima > BASSO) & (rk <= tq.FILTRO)
        for i, e, u, verso, p0, p1, motivo in _simula(o, h, l, c, lungo, corto, atr, rr):
            ore_tenuta = (blocco[u] - blocco[e]) * 4
            gi, ge = int(giorno[e]), int(min(giorno[u], pan["funding"].shape[0] - 1))
            f = float(pan["funding"][gi: ge + 1, j].sum()) * ore_tenuta / max(1, (ge - gi + 1) * 24)
            r = verso * (p1 / p0 - 1) - 2 * (TAKER + m5.scarto(s)) - verso * f
            righe.append({"simbolo": s, "data": sc.data(gi + pan["t0"]), "uscita": sc.data(int(giorno[u]) + pan["t0"]),
                          "annuncio": int((gi + pan["t0"] + 3) // 7), "verso": verso, "r": r, "ore": ore_tenuta,
                          "motivo": {1: "stop", 2: "obiettivo", 3: "tempo"}[motivo]})
    return pd.DataFrame(righe)


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    R, Ud = tq.rango_funding(pan, ps)
    df = operazioni(pan, R, Ud)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "operazioni_T3.csv.gz", index=False)
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    sr = tq.prove_fino_alla_trentatreesima()
    e34 = json.loads((QUI / "risultati_trentaquattresima" / "esame.json").read_text())
    sr += [e34["T1"]["portafoglio"]["intero"]["sharpe"], e34["T2"]["portafoglio"]["intero"]["sharpe"]]
    tq.P_SOGLIA = P_SOGLIA
    e = {"operazioni": tq.esame_operazioni(df), "numero": int(len(df))}
    po = tq.portafoglio(df)
    e["portafoglio"] = te.esame(po, btc, inizio=tq.DA, anni_pieni=se.ANNI_PIENI)
    sr.append(e["portafoglio"]["intero"]["sharpe"])
    i = e["portafoglio"]["intero"]
    e["portafoglio"]["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
    e["portafoglio"]["prove_nel_conto"] = len(sr)
    e["portafoglio"]["esito"] = te.esito(e["portafoglio"], e["portafoglio"]["sharpe_corretto"])
    e["esito"] = "VALIDA" if e["operazioni"]["passa"] and e["portafoglio"]["esito"] == "VALIDA" else "non valida"
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    o, p = e["operazioni"], e["portafoglio"]
    m = o["motivi"]
    testo = "\n".join([
        "# Programma 6 — risultati della trentacinquesima prova (T3: contro gli eccessi, RSI e funding)", "",
        "Regole in `TRENTACINQUESIMA.md` (scritte prima). Candele a 4 ore, monete dell'universo settimanale delle 100, dal 4 "
        "gennaio 2021.", "",
        f"* {e['numero']} operazioni; media netta {100 * o['boot']['media']:+.3f}% (intervallo {100 * o['boot']['basso']:+.3f}; "
        f"{100 * o['boot']['alto']:+.3f}, p {o['boot']['p']:.4f}); vinte {100 * o['vinte']:.0f}%; tenuta media {o['ore_medie']:.0f} ore.",
        f"* Long {100 * o['long_short'].get(1, float('nan')):+.3f}%, short {100 * o['long_short'].get(-1, float('nan')):+.3f}%; uscite: "
        f"stop {100 * m.get('stop', 0):.0f}%, obiettivo {100 * m.get('obiettivo', 0):.0f}%, tempo {100 * m.get('tempo', 0):.0f}%.",
        f"* Metà: {100 * o['prima_meta']:+.3f}%, {100 * o['seconda_meta']:+.3f}%; senza le 5 migliori {100 * o['senza_5_migliori']:+.3f}%.",
        f"* Portafoglio (5% a operazione, al massimo 20): Sharpe {p['intero']['sharpe']:.2f}, {100 * p['intero']['annuo']:+.1f}% l'anno, "
        f"discesa {100 * p['intero']['discesa_max']:.1f}%; per anno " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in p["per_anno"].items())
        + f"; Sharpe corretto {p['sharpe_corretto']:.2f} con {len(sr)} prove.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_TRENTACINQUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTACINQUESIMA FINITA", flush=True)
