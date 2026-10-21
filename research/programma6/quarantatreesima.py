"""Programma 6, quarantatreesima prova (QUARANTATREESIMA.md): entrare 5 minuti dopo l'annuncio di Binance, per 24 ore,
contro il Bitcoin, con l'uscita di protezione al 30%. Q1: long dopo la quotazione a pronti di una moneta che ha gia' il
perpetuo; Q2: short dopo l'etichetta di monitoraggio o la rimozione (eventi della prova 21, con la riserva).

Uso: python3 -m research.programma6.quarantatreesima
"""
from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import annunci as an
from research.programma6 import quarantesima as qr
from research.programma6 import quarantunesima as qu
from research.programma6 import scarico_giorni as sg
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventunesima as vu
from research.programma6.motore import TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantatreesima"
MINUTI = QUI.parents[1] / "research" / "data" / "p6m"
DA_MS, A_MS = sc.giorno(2021, 1, 1) * 86_400_000, (sc.giorno(2026, 10, 10) + 1) * 86_400_000
RITARDO, DURATA, ETA_MIN, STOP, SCARTO_STOP = 5, 1440, 3, 0.30, 0.01
COSTO_MONETA = 2 * (TAKER + 0.0030)
PROVE_EVENTI = 9
P_SOGLIA = 0.01 / PROVE_EVENTI


def eventi_q1() -> list:
    """(ms, annuncio, sigla) delle quotazioni a pronti (anche HODLer, Launchpool, Megadrop)."""
    out = []
    for x in an._carica("quotazioni"):
        t = x["titolo"]
        if not (DA_MS <= x["ms"] < A_MS):
            continue
        lista = re.match(r"^Binance Will List ", t) and "Leveraged Token" not in t and "Futures" not in t and "Margin" not in t
        if not (lista or re.match(r"^Introducing .+ on Binance (HODLer Airdrops|Launchpool|Megadrop)", t)):
            continue
        testa = t.split(" with ")[0].split(" on Binance")[0]
        out += [(x["ms"], x["id"], s) for s in re.findall(r"\(([A-Z0-9]{1,15})\)", testa)]
    return out


def eventi_q2() -> list:
    return [x for x in an.eventi_monitoraggio() + an.eventi_rimozione() if DA_MS <= x[0] < A_MS]


def ammessi(pan: dict, eventi: list) -> tuple:
    ok = np.isfinite(pan["close"])
    primo = ok.argmax(axis=0) + pan["t0"]
    V = np.nan_to_num(pan["quote_volume"])
    out, tolti, visti = [], {"senza perpetuo": 0, "perpetuo troppo giovane o dopo": 0, "volume zero": 0}, set()
    for ms, annuncio, sigla in eventi:
        p = an.perpetuo(sigla, pan["simboli"])
        if not p or p == "BTCUSDT" or p in sc.ESCLUSI:
            tolti["senza perpetuo"] += 1
            continue
        if (annuncio, p) in visti:
            continue
        j = pan["simboli"].index(p)
        g = ms // 86_400_000
        if not ok[:, j].any() or primo[j] > g - ETA_MIN:
            tolti["perpetuo troppo giovane o dopo"] += 1
            continue
        if V[g - 1 - pan["t0"], j] <= 0:
            tolti["volume zero"] += 1
            continue
        visti.add((annuncio, p))
        out.append({"ms": int(ms), "annuncio": annuncio, "simbolo": p, "giorno": int(g), "eta": int(g - primo[j])})
    return out, tolti


def scarica_minuti(simbolo: str, g: int) -> None:
    for d in (g - 1, g, g + 1, g + 2):
        chiave = f"data/futures/um/daily/klines/{simbolo}/1m/{simbolo}-1m-{sc.data(d)}.zip"
        try:
            sg._scarica(chiave, MINUTI / simbolo)
        except Exception:
            pass


def minuti(simbolo: str, g: int) -> pd.DataFrame:
    """Le candele a 1 minuto dei giorni g-1 … g+2 (indice = minuto dall'epoca)."""
    parti = []
    for d in (g - 1, g, g + 1, g + 2):
        f = MINUTI / simbolo / f"{simbolo}-1m-{sc.data(d)}.zip"
        if f.exists():
            parti.append(m5._csv_da_zip(f, m5.KLINE))
    if not parti:
        return pd.DataFrame()
    df = pd.concat(parti, ignore_index=True)
    df["minuto"] = m5._ms(df["open_time"]) // 60_000
    df = df.drop_duplicates("minuto").set_index("minuto").sort_index()
    return df[["open", "high", "low", "close"]].astype(float)


def _apertura(x: pd.DataFrame, m: int) -> float:
    return float(x.loc[m, "open"]) if m in x.index else float("nan")


def funding_ore(F: np.ndarray, t0: int, j: int, m0: int, m1: int) -> float:
    """Il funding delle ore tenute: quello del giorno diviso 24 per ogni ora (anche frazioni)."""
    tot, m = 0.0, m0
    while m < m1:
        g = m // 1440
        fine = min(m1, (g + 1) * 1440)
        k = g - t0
        if 0 <= k < F.shape[0]:
            tot += float(F[k, j]) * (fine - m) / 1440
        m = fine
    return tot


def operazione(c: pd.DataFrame, cb: pd.DataFrame, fund: tuple, m0: int, durata: int, verso: int,
               protezione: bool = True) -> dict:
    """Verso sulla moneta e verso opposto sul Bitcoin dall'apertura del minuto m0 per `durata` minuti; `fund` =
    (funding giornaliero, t0, colonna della moneta, colonna del Bitcoin)."""
    p0, b0 = _apertura(c, m0), _apertura(cb, m0)
    if not (np.isfinite(p0) and np.isfinite(b0)):
        return {}
    m1 = m0 + durata
    tratto = c[(c.index >= m0) & (c.index < m1)]
    uscita, pc, fermata = None, None, False
    if protezione:
        if verso > 0:
            giu = tratto.index[tratto["low"].to_numpy() <= p0 * (1 - STOP)]
            if len(giu):
                uscita, pc, fermata = int(giu[0]), p0 * (1 - STOP) * (1 - SCARTO_STOP), True
        else:
            su = tratto.index[tratto["high"].to_numpy() >= p0 * (1 + STOP)]
            if len(su):
                uscita, pc, fermata = int(su[0]), p0 * (1 + STOP) * (1 + SCARTO_STOP), True
    if uscita is None:
        if m1 in c.index:
            uscita, pc = m1, float(c.loc[m1, "open"])
        elif len(tratto):
            uscita, pc = int(tratto.index[-1]) + 1, float(tratto["close"].iloc[-1])
        else:
            return {}
    bb = cb[cb.index <= uscita]
    pb = float(cb.loc[uscita, "open"]) if (not fermata and uscita in cb.index) else float(bb["close"].iloc[-1])
    F, t0, j, jb = fund
    fc, fb = funding_ore(F, t0, j, m0, uscita), funding_ore(F, t0, jb, m0, uscita)
    r = verso * ((pc / p0 - 1) - (pb / b0 - 1)) - COSTO_MONETA - vu.COSTO_BTC - verso * (fc - fb)
    return {"r": float(r), "fermata": fermata, "uscita": int(uscita)}


def movimento(c: pd.DataFrame, cb: pd.DataFrame, a: int, b: int, verso: int) -> float:
    pa, pb_, ba, bb = _apertura(c, a), _apertura(c, b), _apertura(cb, a), _apertura(cb, b)
    return float(verso * ((pb_ / pa - 1) - (bb / ba - 1)))


def tabella(pan: dict, ev: list, verso: int) -> pd.DataFrame:
    jb = pan["simboli"].index("BTCUSDT")
    righe = []
    for x in ev:
        s, g = x["simbolo"], x["giorno"]
        c, cb = minuti(s, g), minuti("BTCUSDT", g)
        if c.empty or cb.empty:
            continue
        ma = x["ms"] // 60_000
        m0 = ma + RITARDO
        fund = (pan["funding"], pan["t0"], pan["simboli"].index(s), jb)
        o = operazione(c, cb, fund, m0, DURATA, verso)
        if not o:
            continue
        r1 = operazione(c, cb, fund, ma + 1, DURATA, verso)
        riga = {**x, "data": sc.data(g), "ora": m0 // 60, "uscita_h": o["uscita"] // 60, "r": o["r"], "fermata": o["fermata"],
                "persi_5_minuti": movimento(c, cb, ma, m0, verso), "ora_prima": movimento(c, cb, ma - 60, ma, verso),
                "r_dopo_1_minuto": r1["r"] if r1 else np.nan}
        for n, d in (("r_1_ora", 60), ("r_4_ore", 240)):
            oo = operazione(c, cb, fund, m0, d, verso, protezione=False)
            riga[n] = oo["r"] if oo else np.nan
        righe.append(riga)
    return pd.DataFrame(righe)


def portafoglio(df: pd.DataFrame) -> pd.DataFrame:
    d = df.sort_values(["ora", "simbolo"]).reset_index(drop=True)
    aperte, tenute = [], []
    for k, x in d.iterrows():
        aperte = [u for u in aperte if u > x["ora"]]
        if len(aperte) >= qu.MAX_APERTE:
            continue
        aperte.append(x["uscita_h"])
        tenute.append(k)
    t = d.loc[tenute]
    lun = ((t["uscita_h"].to_numpy() // 24 + 3) // 7) * 7 - 3
    costo = COSTO_MONETA + vu.COSTO_BTC
    sett = pd.Series(qu.QUOTA * t["r"].to_numpy(), index=lun).groupby(level=0).sum()
    sett_d = pd.Series(qu.QUOTA * (t["r"].to_numpy() - costo), index=lun).groupby(level=0).sum()
    tutte = np.arange(qu.PRIMO_LUNEDI, sc.giorno(2026, 10, 10) + 7, 7)
    out = pd.DataFrame({"netto": sett.reindex(tutte).fillna(0.0), "netto_doppio": sett_d.reindex(tutte).fillna(0.0)})
    for k in ("lordo", "spese", "funding", "giro", "long", "short"):
        out[k] = 0.0
    out["monete"] = 1
    return out


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    sr = qr.prove_fino_alla_trentanovesima()
    for f, ch in (("risultati_quarantesima", "portafoglio"), ("risultati_quarantunesima", "portafoglio")):
        sr.append(json.loads((QUI / f / "esame.json").read_text())[ch]["intero"]["sharpe"])
    sr.append(json.loads((QUI / "risultati_quarantaduesima" / "esame.json").read_text())["intero"]["sharpe"])
    RIS.mkdir(exist_ok=True)
    out, tabelle = {}, {}
    for nome, f, verso in (("Q1", eventi_q1, 1), ("Q2", eventi_q2, -1)):
        ev, tolti = ammessi(pan, f())
        log(f"[quarantatreesima] {nome}: {len(ev)} eventi ammessi; tolti {tolti}")
        with ThreadPoolExecutor(max_workers=8) as ex:
            list(ex.map(lambda x: scarica_minuti(x["simbolo"], x["giorno"]), ev))
            list(ex.map(lambda g: scarica_minuti("BTCUSDT", g), sorted({x["giorno"] for x in ev})))
        df = tabella(pan, ev, verso)
        df.to_csv(RIS / f"eventi_{nome}.csv", index=False)
        tabelle[nome] = df
        e = {"eventi": qu.esame_eventi(df, "r", P_SOGLIA), "ammessi": len(ev), "tolti": tolti,
             "senza_minuti": len(ev) - len(df), "fermate": float(df["fermata"].mean()),
             "descrittivi": {k: float(df[k].mean()) for k in ("persi_5_minuti", "ora_prima", "r_dopo_1_minuto", "r_1_ora", "r_4_ore")},
             "mediane": {k: float(df[k].median()) for k in ("persi_5_minuti", "ora_prima")}}
        e["portafoglio"] = te.esame(portafoglio(df), btc, inizio=qu.PRIMO_LUNEDI, anni_pieni=se.ANNI_PIENI)
        sr.append(e["portafoglio"]["intero"]["sharpe"])
        out[nome] = e
    for nome, e in out.items():
        p = e["portafoglio"]
        i = p["intero"]
        p["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
        p["prove_nel_conto"] = len(sr)
        p["esito"] = te.esito(p, p["sharpe_corretto"])
        e["esito"] = "VALIDA" if e["eventi"]["passa"] and p["esito"] == "VALIDA" else "non valida"
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    righe = ["# Programma 6 — risultati della quarantatreesima prova (entrare 5 minuti dopo l'annuncio)", "",
             "Regole in `QUARANTATREESIMA.md` (scritte prima). Q1: long dopo la quotazione a pronti; Q2: short dopo l'etichetta "
             "di monitoraggio o la rimozione (con la riserva: eventi della prova 21). Per 24 ore, contro il Bitcoin.", ""]
    for nome, e in out.items():
        v, b, p, d = e["eventi"], e["eventi"]["boot"], e["portafoglio"], e["descrittivi"]
        righe += [f"## {nome}", "",
                  f"* Eventi ammessi {e['ammessi']} (tolti: " + ", ".join(f"{k} {n}" for k, n in e["tolti"].items())
                  + f"); senza le candele a 1 minuto {e['senza_minuti']}.",
                  f"* {b['eventi']} eventi in {b['annunci']} annunci: media netta {100 * b['media']:+.2f}% a evento (intervallo "
                  f"{100 * b['basso']:+.2f}; {100 * b['alto']:+.2f}, p {b['p']:.4f}, soglia {P_SOGLIA:.4f}); mediana "
                  f"{100 * v['mediana']:+.2f}%; vinti {100 * v['vinti']:.0f}%; metà {100 * v['prima_meta']:+.2f}% e "
                  f"{100 * v['seconda_meta']:+.2f}%; senza i 5 migliori {100 * v['senza_5_migliori']:+.2f}%.",
                  "* Per anno: " + ", ".join(f"{a} {100 * x['media']:+.2f}% ({x['eventi']})" for a, x in v["per_anno"].items()) + ".",
                  f"* Nei 5 minuti persi il movimento nel verso è {100 * d['persi_5_minuti']:+.2f}% (mediana "
                  f"{100 * e['mediane']['persi_5_minuti']:+.2f}%); nell'ora prima dell'annuncio {100 * d['ora_prima']:+.2f}% (mediana "
                  f"{100 * e['mediane']['ora_prima']:+.2f}%).",
                  f"* Entrando dopo 1 minuto: {100 * d['r_dopo_1_minuto']:+.2f}%; tenendo 1 ora {100 * d['r_1_ora']:+.2f}%, 4 ore "
                  f"{100 * d['r_4_ore']:+.2f}% (con i costi, senza protezione). Uscite di protezione {100 * e['fermate']:.0f}%.",
                  f"* Portafoglio (5% a operazione): Sharpe {p['intero']['sharpe']:.2f}, {100 * p['intero']['annuo']:+.1f}% l'anno, "
                  f"discesa {100 * p['intero']['discesa_max']:.1f}%; Sharpe corretto {p['sharpe_corretto']:.2f} con {len(sr)} prove; "
                  f"esito del portafoglio: {p['esito']}.", "", f"**Esito {nome}: {e['esito']}**", ""]
    testo = "\n".join(righe)
    (QUI / "RISULTATI_QUARANTATREESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTATREESIMA FINITA", flush=True)
