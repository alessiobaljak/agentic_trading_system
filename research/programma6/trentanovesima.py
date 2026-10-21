"""Programma 6, trentanovesima prova (TRENTANOVESIMA.md): T8, la tendenza del giorno (chiusura sopra o sotto la media dei 50
giorni) e il ritracciamento a 4 ore (RSI sotto 35 per i long, sopra 65 per gli short), con il funding che toglie i casi
affollati; stop 2 ATR, uscita mobile 3 ATR, al massimo 42 candele. Monete, costi ed esame come la prova 34.

Uso: python3 -m research.programma6.trentanovesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import trentacinquesima as tc
from research.programma6 import trentaquattresima as tq
from research.programma6.motore import TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentanovesima"
GIORNI_MEDIA, RSI_LONG, RSI_SHORT = 50, 35.0, 65.0


def tendenza(pan: dict) -> np.ndarray:
    """Giorni × monete: +1 se la chiusura del giorno e' sopra la media dei 50 giorni, −1 se sotto (si usa dal giorno dopo)."""
    C = pd.DataFrame(pan["close"])
    m = C.rolling(GIORNI_MEDIA, min_periods=GIORNI_MEDIA).mean()
    return np.where(C > m, 1.0, np.where(C < m, -1.0, 0.0))


def operazioni(pan: dict, R: np.ndarray, Ud: np.ndarray) -> pd.DataFrame:
    sim = pan["simboli"]
    tend = tendenza(pan)
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
        rr = tc.rsi(c)
        prima = np.r_[np.nan, rr[:-1]]
        g = np.clip(giorno, 0, Ud.shape[0] - 1)
        ieri = np.clip(giorno - 1, 0, Ud.shape[0] - 1)
        nel = (giorno >= 1) & (giorno < Ud.shape[0]) & Ud[g, j] & (giorno + pan["t0"] >= tq.DA) & (giorno + pan["t0"] <= tq.A)
        t_ieri = tend[ieri, j]
        rk = np.nan_to_num(R[g, j], nan=0.5)
        lungo = nel & (t_ieri > 0) & (rr <= RSI_LONG) & (prima > RSI_LONG) & (rk < 1 - tq.FILTRO)
        corto = nel & (t_ieri < 0) & (rr >= RSI_SHORT) & (prima < RSI_SHORT) & (rk > tq.FILTRO)
        for i, e, u, verso, p0, p1, motivo in tq._simula(o, h, l, c, lungo, corto, atr):
            ore_tenuta = (blocco[u] - blocco[e]) * 4
            gi, ge = int(giorno[e]), int(min(giorno[u], pan["funding"].shape[0] - 1))
            f = float(pan["funding"][gi: ge + 1, j].sum()) * ore_tenuta / max(1, (ge - gi + 1) * 24)
            r = verso * (p1 / p0 - 1) - 2 * (TAKER + m5.scarto(s)) - verso * f
            righe.append({"simbolo": s, "data": sc.data(gi + pan["t0"]), "uscita": sc.data(int(giorno[u]) + pan["t0"]),
                          "annuncio": int((gi + pan["t0"] + 3) // 7), "verso": verso, "r": r, "ore": ore_tenuta,
                          "motivo": {1: "stop", 2: "uscita mobile", 3: "tempo"}[motivo]})
    return pd.DataFrame(righe)


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    R, Ud = tq.rango_funding(pan, ps)
    df = operazioni(pan, R, Ud)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "operazioni_T8.csv.gz", index=False)
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    sr = tq.prove_fino_alla_trentatreesima()
    e34 = json.loads((QUI / "risultati_trentaquattresima" / "esame.json").read_text())
    sr += [e34["T1"]["portafoglio"]["intero"]["sharpe"], e34["T2"]["portafoglio"]["intero"]["sharpe"],
           json.loads((QUI / "risultati_trentacinquesima" / "esame.json").read_text())["portafoglio"]["intero"]["sharpe"],
           json.loads((QUI / "risultati_trentaseiesima" / "esame.json").read_text())["T5"]["intero"]["sharpe"],
           json.loads((QUI / "risultati_trentasettesima" / "esame.json").read_text())["portafoglio"]["intero"]["sharpe"]]
    tq.P_SOGLIA = 0.01
    e = {"operazioni": tq.esame_operazioni(df), "numero": int(len(df))}
    e["portafoglio"] = te.esame(tq.portafoglio(df), btc, inizio=tq.DA, anni_pieni=se.ANNI_PIENI)
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
        "# Programma 6 — risultati della trentanovesima prova (T8: tendenza del giorno e ritracciamento a 4 ore)", "",
        "Regole in `TRENTANOVESIMA.md` (scritte prima).", "",
        f"* {e['numero']} operazioni; media netta {100 * o['boot']['media']:+.3f}% (intervallo {100 * o['boot']['basso']:+.3f}; "
        f"{100 * o['boot']['alto']:+.3f}, p {o['boot']['p']:.4f}); vinte {100 * o['vinte']:.0f}%; tenuta media {o['ore_medie']:.0f} ore.",
        f"* Long {100 * o['long_short'].get(1, float('nan')):+.3f}%, short {100 * o['long_short'].get(-1, float('nan')):+.3f}%; uscite: "
        f"stop {100 * m.get('stop', 0):.0f}%, mobile {100 * m.get('uscita mobile', 0):.0f}%, tempo {100 * m.get('tempo', 0):.0f}%.",
        f"* Metà: {100 * o['prima_meta']:+.3f}%, {100 * o['seconda_meta']:+.3f}%; senza le 5 migliori {100 * o['senza_5_migliori']:+.3f}%.",
        f"* Portafoglio: Sharpe {p['intero']['sharpe']:.2f}, {100 * p['intero']['annuo']:+.1f}% l'anno, discesa "
        f"{100 * p['intero']['discesa_max']:.1f}%; Sharpe corretto {p['sharpe_corretto']:.2f} con {len(sr)} prove.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_TRENTANOVESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTANOVESIMA FINITA", flush=True)
