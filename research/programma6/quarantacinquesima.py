"""Programma 6, quarantacinquesima prova (QUARANTACINQUESIMA.md): gli indicatori per decidere quando entrare.
I1: F5 con le entrate nuove solo se la tendenza e' d'accordo (chiusura della domenica sopra o sotto la media dei 20 giorni).
I2: N3 con l'entrata alla prima chiusura sotto il minimo dei 5 giorni prima, fra il 7° e il 37° giorno d'eta'.

Uso: python3 -m research.programma6.quarantacinquesima
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import ottava as ot
from research.programma6 import quarantesima as qr
from research.programma6 import quarantunesima as qu
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import trentaduesima as td
from research.programma6 import trentesima as tr
from research.programma6 import ventiquattresima as vq

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantacinquesima"
GIORNI_MEDIA, GIORNI_MINIMO, ULTIMO_GIORNO = 20, 5, 37
P_SOGLIA = 0.01 / 10


def tendenza_domenica(pan: dict, lun: np.ndarray) -> np.ndarray:
    """Settimane × monete: +1 se la chiusura della domenica e' sopra la media dei 20 giorni, −1 se sotto, 0 se manca."""
    C = pan["close"]
    m = pd.DataFrame(C).rolling(GIORNI_MEDIA, min_periods=GIORNI_MEDIA).mean().to_numpy()
    out = np.zeros((len(lun), C.shape[1]))
    for k, x in enumerate(lun):
        d = x - 1
        if d >= 0:
            out[k] = np.nan_to_num(np.sign(C[d] - m[d]))
    return out


def pesi_banda_tendenza(ct: np.ndarray, U: np.ndarray, sig: np.ndarray, tend: np.ndarray) -> np.ndarray:
    """Come `ventiquattresima.pesi_banda`, ma una moneta entra long solo con la tendenza su, short solo con la tendenza giu'."""
    W, S = ct.shape
    out = np.zeros((W, S))
    lunghi, corti = set(), set()
    for k in range(W):
        idx = np.flatnonzero(U[k] & np.isfinite(ct[k]) & np.isfinite(sig[k]) & (sig[k] > 0))
        if len(idx) < te.MIN_MONETE:
            lunghi, corti = set(), set()
            continue
        pr = pd.Series(ct[k, idx]).rank(pct=True).to_numpy()
        rango = dict(zip(idx.tolist(), pr))
        lunghi = {j for j in lunghi if rango.get(j, 0) >= 1 - vq.RESTA} | \
                 {j for j, p in rango.items() if p > 1 - vq.ENTRA and tend[k, j] > 0}
        corti = {j for j in corti if rango.get(j, 1) <= vq.RESTA} | \
                {j for j, p in rango.items() if p <= vq.ENTRA and tend[k, j] < 0}
        for lato, segno in ((sorted(lunghi), 1.0), (sorted(corti), -1.0)):
            if lato:
                inv = 1.0 / sig[k, lato]
                out[k, lato] = segno * inv / inv.sum()
    return out


def prima_rottura(pan: dict, j: int, g0: int) -> int:
    """Il giorno (dall'epoca) della prima chiusura sotto il minimo dei 5 giorni prima, fra il 7° e il 37° giorno d'eta'; −1."""
    C, L, t0 = pan["close"][:, j], pan["low"][:, j], pan["t0"]
    for d in range(g0 + tr.ETA, g0 + ULTIMO_GIORNO + 1):
        k = d - t0
        if k >= len(C) or k - GIORNI_MINIMO < 0:
            break
        minimo = np.nanmin(L[k - GIORNI_MINIMO: k]) if np.isfinite(L[k - GIORNI_MINIMO: k]).any() else np.nan
        if np.isfinite(C[k]) and np.isfinite(minimo) and C[k] < minimo:
            return d
    return -1


def prove_fino_alla_quarantaquattresima() -> list:
    sr = qr.prove_fino_alla_trentanovesima()
    for f in ("risultati_quarantesima", "risultati_quarantunesima"):
        sr.append(json.loads((QUI / f / "esame.json").read_text())["portafoglio"]["intero"]["sharpe"])
    sr.append(json.loads((QUI / "risultati_quarantaduesima" / "esame.json").read_text())["intero"]["sharpe"])
    e43 = json.loads((QUI / "risultati_quarantatreesima" / "esame.json").read_text())
    sr += [e43[k]["portafoglio"]["intero"]["sharpe"] for k in ("Q1", "Q2")]
    sr.append(json.loads((QUI / "risultati_quarantaquattresima" / "esame.json").read_text())["intero"]["sharpe"])
    return sr


def i1(pan: dict, ps: dict) -> tuple:
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    ct = np.where(np.isfinite(sig), -se.funding_7(pan, lun), np.nan)
    costo = sc.costi_moneta(ps["simboli"])
    tend = tendenza_domenica(pan, lun)
    con = te.conto(pesi_banda_tendenza(ct, ps["U"], sig, tend), ps["R"], ps["F"], costo)
    f5 = te.conto(vq.pesi_banda(ct, ps["U"], sig), ps["R"], ps["F"], costo)
    con.index = f5.index = ps["lunedi"]
    return con, f5


def i2(pan: dict, log=print) -> tuple:
    ok = np.isfinite(pan["close"])
    primo = ok.argmax(axis=0) + pan["t0"]
    V = np.nan_to_num(pan["quote_volume"])
    cand = [(s, int(primo[j])) for j, s in enumerate(pan["simboli"])
            if s != "BTCUSDT" and ok[:, j].any() and td.DA <= primo[j] <= td.A]
    segnali, senza_rottura = [], 0
    for s, g0 in cand:
        j = pan["simboli"].index(s)
        if V[g0 + tr.ETA - 1 - pan["t0"], j] <= 0:
            continue
        d = prima_rottura(pan, j, g0)
        if d < 0:
            senza_rottura += 1
            continue
        segnali.append((s, g0, d + 1))
    log(f"[quarantacinquesima] I2: {len(cand)} monete nuove, {len(segnali)} con la rottura, {senza_rottura} senza")
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: td.scarica_ore(x[0], x[2]), segnali))
    jb = pan["simboli"].index("BTCUSDT")
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    fb = pd.Series(pan["funding"][:, jb], index=giorni)
    cb = td.ore("BTCUSDT")
    righe, senza_ore = [], 0
    for s, g0, e in segnali:
        c = td.ore(s)
        if c.empty or e * 24 not in c.index:
            senza_ore += 1
            continue
        f = pd.Series(pan["funding"][:, pan["simboli"].index(s)], index=giorni)
        o = tr.operazione(c, cb, f, fb, e, True)
        if not o:
            senza_ore += 1
            continue
        righe.append({"data": sc.data(e), "annuncio": int((e + 3) // 7), "simbolo": s, "r": o["r"], "fermata": o["fermata"],
                      "giorni": o["giorni"], "attesa": int(e - (g0 + tr.ETA)), "ora": e * 24,
                      "uscita_h": int(e * 24 + round(o["giorni"] * 24))})
    return pd.DataFrame(righe), {"monete": len(cand), "con_rottura": len(segnali), "senza_rottura": senza_rottura,
                                 "senza_ore": senza_ore}


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    sr = prove_fino_alla_quarantaquattresima()
    RIS.mkdir(exist_ok=True)
    con, f5 = i1(pan, ps)
    con.to_csv(RIS / "settimane_I1.csv.gz")
    e1 = te.esame(con, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    e5 = te.esame(f5, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    sr.append(e1["intero"]["sharpe"])
    df, conti = i2(pan, log)
    df.to_csv(RIS / "eventi_I2.csv", index=False)
    e2 = {"eventi": qu.esame_eventi(df, "r", P_SOGLIA), **conti, "fermate": float(df["fermata"].mean()),
          "attesa_media": float(df["attesa"].mean())}
    e2["portafoglio"] = te.esame(qu.portafoglio(df), btc, inizio=qu.PRIMO_LUNEDI, anni_pieni=se.ANNI_PIENI)
    sr.append(e2["portafoglio"]["intero"]["sharpe"])
    for p in (e1, e2["portafoglio"]):
        i = p["intero"]
        p["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
        p["prove_nel_conto"] = len(sr)
        p["esito"] = te.esito(p, p["sharpe_corretto"])
    e2["esito"] = "VALIDA" if e2["eventi"]["passa"] and e2["portafoglio"]["esito"] == "VALIDA" else "non valida"
    e1["F5_stesse_settimane"] = {k: e5["intero"][k] for k in ("sharpe", "annuo", "volatilita", "discesa_max")}
    e1["F5_per_anno"] = e5["per_anno"]
    n3 = json.loads((QUI / "risultati_trentaduesima" / "esame.json").read_text())["con_uscita"]
    n3p = json.loads((QUI / "risultati_trentatreesima" / "esame.json").read_text())["N3 a portafoglio"]["intero"]
    out = {"I1": e1, "I2": e2}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, f = e1["intero"], e1["F5_stesse_settimane"]
    v, b, p = e2["eventi"], e2["eventi"]["boot"], e2["portafoglio"]
    testo = "\n".join([
        "# Programma 6 — risultati della quarantacinquesima prova (gli indicatori per decidere quando entrare)", "",
        "Regole in `QUARANTACINQUESIMA.md` (scritte prima).", "",
        "## I1 — F5 con la tendenza d'accordo", "",
        f"* I1: Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e1['spese_annue']:.1f}% l'anno.",
        f"* F5 sulle stesse settimane: Sharpe {f['sharpe']:.2f}, {100 * f['annuo']:+.1f}% l'anno, discesa {100 * f['discesa_max']:.1f}%.",
        "* Per anno: I1 " + ", ".join(f"{a} {100 * x:+.1f}%" for a, x in e1["per_anno"].items()) + "; F5 "
        + ", ".join(f"{a} {100 * x:+.1f}%" for a, x in e1["F5_per_anno"].items()) + ".",
        f"* Sharpe corretto {e1['sharpe_corretto']:.2f} con {len(sr)} prove.", "", f"**Esito I1: {e1['esito']}**", "",
        "## I2 — N3 con l'entrata sulla prima rottura verso il basso", "",
        f"* Monete nuove {e2['monete']}: con la rottura fra il 7° e il 37° giorno {e2['con_rottura']}, senza "
        f"{e2['senza_rottura']}; senza le candele a 1 ora {e2['senza_ore']}; attesa media {e2['attesa_media']:.1f} giorni dopo il 7°.",
        f"* {b['eventi']} operazioni: media netta {100 * b['media']:+.2f}% (intervallo {100 * b['basso']:+.2f}; "
        f"{100 * b['alto']:+.2f}, p {b['p']:.4f}, soglia {P_SOGLIA:.4f}); mediana {100 * v['mediana']:+.2f}%; vinte "
        f"{100 * v['vinti']:.0f}%; metà {100 * v['prima_meta']:+.2f}% e {100 * v['seconda_meta']:+.2f}%; senza le 5 migliori "
        f"{100 * v['senza_5_migliori']:+.2f}%; uscite di protezione {100 * e2['fermate']:.0f}%.",
        "* Per anno: " + ", ".join(f"{a} {100 * x['media']:+.2f}% ({x['eventi']})" for a, x in v["per_anno"].items()) + ".",
        f"* N3 (prova 32) per confronto: {100 * n3['boot']['media']:+.2f}% a operazione su {n3['boot']['eventi']}; a "
        f"portafoglio Sharpe {n3p['sharpe']:.2f}, discesa {100 * n3p['discesa_max']:.1f}%.",
        f"* Portafoglio I2 (5% a operazione): Sharpe {p['intero']['sharpe']:.2f}, {100 * p['intero']['annuo']:+.1f}% l'anno, "
        f"discesa {100 * p['intero']['discesa_max']:.1f}%; Sharpe corretto {p['sharpe_corretto']:.2f}; esito del portafoglio: "
        f"{p['esito']}.", "", f"**Esito I2: {e2['esito']}**"]) + "\n"
    (QUI / "RISULTATI_QUARANTACINQUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTACINQUESIMA FINITA", flush=True)
