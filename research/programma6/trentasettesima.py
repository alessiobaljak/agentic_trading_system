"""Programma 6, trentasettesima prova (TRENTASETTESIMA.md): T6, i segnali di T2 (rottura di Donchian a 4 ore con il filtro
del funding) con l'entrata a ordine limite al prezzo di chiusura della candela del segnale, valido per la candela dopo
(commissione da limite, niente scarto); uscite a mercato come T2.

Uso: python3 -m research.programma6.trentasettesima
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
from research.programma6.motore import MAKER, TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentasettesima"
MAKER_ENTRATA = 0.0002


@njit(cache=True)
def _simula(o, h, l, c, segnali_long, segnali_short, atr):
    """Come `trentaquattresima._simula`, con l'entrata a limite al prezzo di chiusura del segnale; motivo 0 = non eseguita."""
    n = len(c)
    out = []
    i = 0
    while i < n - 1:
        verso = 1 if segnali_long[i] else (-1 if segnali_short[i] else 0)
        if verso == 0 or not atr[i] > 0:
            i += 1
            continue
        e = i + 1
        p0 = c[i]
        eseguita = (l[e] <= p0) if verso > 0 else (h[e] >= p0)
        if not eseguita:
            out.append((i, e, e, verso, p0, p0, 0))
            i += 1
            continue
        a = atr[i]
        stop0 = p0 - verso * 2.0 * a
        migliore = p0
        uscita, prezzo, motivo = -1, 0.0, 0
        j = e
        while j < n:
            if verso > 0:
                livello = max(stop0, migliore - 3.0 * a)
                if j > e and o[j] <= livello:
                    uscita, prezzo = j, o[j]
                elif l[j] <= livello:
                    uscita, prezzo = j, livello
            else:
                livello = min(stop0, migliore + 3.0 * a)
                if j > e and o[j] >= livello:
                    uscita, prezzo = j, o[j]
                elif h[j] >= livello:
                    uscita, prezzo = j, livello
            if uscita >= 0:
                motivo = 1 if abs(livello - stop0) < 1e-12 else 2
                break
            migliore = max(migliore, c[j]) if verso > 0 else min(migliore, c[j])
            if j - e + 1 >= 42 and j + 1 < n:
                uscita, prezzo, motivo = j + 1, o[j + 1], 3
                break
            j += 1
        if uscita < 0:
            break
        out.append((i, e, uscita, verso, p0, prezzo, motivo))
        i = uscita
    return out


def operazioni(pan: dict, R: np.ndarray, Ud: np.ndarray) -> tuple:
    sim = pan["simboli"]
    righe, non_eseguite = [], 0
    for j in np.flatnonzero(Ud.any(axis=0)):
        s = sim[j]
        b = tq.quattro_ore(es.ore_di(s))
        if len(b) < tq.N_DON + tq.N_ATR + 2:
            continue
        o, h, l, c = (b[k].to_numpy(float) for k in ("open", "high", "low", "close"))
        blocco = b.index.to_numpy()
        giorno = blocco * 4 // 24 - pan["t0"]
        hh = pd.Series(h).rolling(tq.N_DON).max().shift(1).to_numpy()
        ll = pd.Series(l).rolling(tq.N_DON).min().shift(1).to_numpy()
        cp = np.r_[np.nan, c[:-1]]
        atr = pd.Series(np.nanmax(np.vstack([h - l, np.abs(h - cp), np.abs(l - cp)]), axis=0)).rolling(tq.N_ATR).mean().to_numpy()
        g = np.clip(giorno, 0, Ud.shape[0] - 1)
        nel = (giorno >= 0) & (giorno < Ud.shape[0]) & Ud[g, j] & (giorno + pan["t0"] >= tq.DA) & (giorno + pan["t0"] <= tq.A)
        rk = R[g, j]
        lungo = nel & (c > hh) & (rk <= tq.FILTRO)
        corto = nel & (c < ll) & (rk >= 1 - tq.FILTRO)
        for i, e, u, verso, p0, p1, motivo in _simula(o, h, l, c, lungo, corto, atr):
            if motivo == 0:
                non_eseguite += 1
                continue
            ore_tenuta = (blocco[u] - blocco[e]) * 4
            gi, ge = int(giorno[e]), int(min(giorno[u], pan["funding"].shape[0] - 1))
            f = float(pan["funding"][gi: ge + 1, j].sum()) * ore_tenuta / max(1, (ge - gi + 1) * 24)
            costo = MAKER_ENTRATA + TAKER + m5.scarto(s)
            r = verso * (p1 / p0 - 1) - costo - verso * f
            righe.append({"simbolo": s, "data": sc.data(gi + pan["t0"]), "uscita": sc.data(int(giorno[u]) + pan["t0"]),
                          "annuncio": int((gi + pan["t0"] + 3) // 7), "verso": verso, "r": r, "ore": ore_tenuta,
                          "motivo": {1: "stop", 2: "uscita mobile", 3: "tempo"}[motivo]})
    return pd.DataFrame(righe), non_eseguite


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    R, Ud = tq.rango_funding(pan, ps)
    df, non_eseguite = operazioni(pan, R, Ud)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "operazioni_T6.csv.gz", index=False)
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    sr = tq.prove_fino_alla_trentatreesima()
    e34 = json.loads((QUI / "risultati_trentaquattresima" / "esame.json").read_text())
    sr += [e34["T1"]["portafoglio"]["intero"]["sharpe"], e34["T2"]["portafoglio"]["intero"]["sharpe"],
           json.loads((QUI / "risultati_trentacinquesima" / "esame.json").read_text())["portafoglio"]["intero"]["sharpe"],
           json.loads((QUI / "risultati_trentaseiesima" / "esame.json").read_text())["T5"]["intero"]["sharpe"]]
    tq.P_SOGLIA = 0.01
    e = {"operazioni": tq.esame_operazioni(df), "numero": int(len(df)), "non_eseguite": non_eseguite}
    e["portafoglio"] = te.esame(tq.portafoglio(df), btc, inizio=tq.DA, anni_pieni=se.ANNI_PIENI)
    sr.append(e["portafoglio"]["intero"]["sharpe"])
    i = e["portafoglio"]["intero"]
    e["portafoglio"]["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
    e["portafoglio"]["prove_nel_conto"] = len(sr)
    e["portafoglio"]["esito"] = te.esito(e["portafoglio"], e["portafoglio"]["sharpe_corretto"])
    e["esito"] = "VALIDA" if e["operazioni"]["passa"] and e["portafoglio"]["esito"] == "VALIDA" else "non valida"
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    o, p = e["operazioni"], e["portafoglio"]
    testo = "\n".join([
        "# Programma 6 — risultati della trentasettesima prova (T6: la rottura a 4 ore con il funding, entrata a limite)", "",
        "Regole in `TRENTASETTESIMA.md` (scritte prima).", "",
        f"* Segnali {e['numero'] + non_eseguite}; entrate eseguite {e['numero']} ({100 * e['numero'] / max(1, e['numero'] + non_eseguite):.0f}%).",
        f"* Media netta {100 * o['boot']['media']:+.3f}% a operazione (intervallo {100 * o['boot']['basso']:+.3f}; {100 * o['boot']['alto']:+.3f}, "
        f"p {o['boot']['p']:.4f}); vinte {100 * o['vinte']:.0f}%; tenuta media {o['ore_medie']:.0f} ore; long "
        f"{100 * o['long_short'].get(1, float('nan')):+.3f}%, short {100 * o['long_short'].get(-1, float('nan')):+.3f}%.",
        f"* Portafoglio: Sharpe {p['intero']['sharpe']:.2f}, {100 * p['intero']['annuo']:+.1f}% l'anno; Sharpe corretto "
        f"{p['sharpe_corretto']:.2f} con {len(sr)} prove. T2 (a mercato) per confronto: +0,014% a operazione.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_TRENTASETTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTASETTESIMA FINITA", flush=True)
