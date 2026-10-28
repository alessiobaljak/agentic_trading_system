"""Programma 7, cinquantanovesima prova (CINQUANTANOVESIMA.md): RR, l'inclinazione delle opzioni sul Bitcoin. Ogni giorno, dalle
operazioni di Deribit fra le 22 e le 24 UTC con scadenza fra 20 e 45 giorni: mediana della volatilita' implicita delle opzioni
d'acquisto con delta 0,15-0,35 meno quella delle opzioni di vendita con delta -0,35/-0,15. Long il Bitcoin il giorno dopo se sopra la
mediana dei 90 giorni prima, short se sotto.

Uso: python3 -m research.programma7.cinquantanovesima
"""
from __future__ import annotations

import json
import math
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma7 import prima as g1

QUI = Path(__file__).parent
RADICE = QUI.parents[1]
RIS = QUI / "risultati_cinquantanovesima"
DATI = RADICE / "research" / "data" / "deribit_rr"
URL = ("https://history.deribit.com/api/v2/public/get_last_trades_by_currency_and_time?currency=BTC&kind=option"
       "&start_timestamp={a}&end_timestamp={b}&count=10000&sorting=asc")
DAL, AL = sc.giorno(2021, 4, 1), sc.giorno(2026, 10, 25)
MIN_G, MAX_G, DELTA_BASSO, DELTA_ALTO, MINIMO, FINESTRA, VALIDI = 20, 45, 0.15, 0.35, 5, 90, 45
MESI = {m: i + 1 for i, m in enumerate(("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"))}


def _get(url: str):
    for k in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ricerca/1.0"}), timeout=60) as r:
                return json.load(r)
        except Exception:  # noqa: BLE001
            time.sleep(2 * (k + 1))
    return None


def operazioni(g: int) -> list:
    """Le operazioni sulle opzioni del Bitcoin fra le 22 e le 24 UTC del giorno g (in cache)."""
    f = DATI / f"{sc.data(g)}.json"
    if f.exists() and f.stat().st_size > 2:
        return json.loads(f.read_text())
    a = (g * 1440 + 22 * 60) * 60_000
    out, inizio = [], a
    while True:
        d = _get(URL.format(a=inizio, b=a + 7_200_000))
        if not d or "result" not in d:
            break
        tr = d["result"]["trades"]
        out += [{k: x[k] for k in ("timestamp", "instrument_name", "iv", "index_price", "amount")} for x in tr]
        if not d["result"].get("has_more") or not tr:
            break
        inizio = tr[-1]["timestamp"] + 1
    DATI.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(out))
    return out


def _n(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def inclinazione(tr: list) -> float:
    calls, puts = [], []
    for x in tr:
        try:
            _, scad, k, tipo = x["instrument_name"].split("-")
            dt = datetime(2000 + int(scad[-2:]), MESI[scad[-5:-2]], int(scad[:-5]), 8, tzinfo=timezone.utc)
        except (ValueError, KeyError):
            continue
        giorni = (dt.timestamp() * 1000 - x["timestamp"]) / 86_400_000
        if not (MIN_G <= giorni <= MAX_G) or not x.get("iv") or not x.get("index_price"):
            continue
        s, kk, sig, t = float(x["index_price"]), float(k), float(x["iv"]) / 100, giorni / 365
        d1 = (math.log(s / kk) + 0.5 * sig * sig * t) / (sig * math.sqrt(t))
        if tipo == "C" and DELTA_BASSO <= _n(d1) <= DELTA_ALTO:
            calls.append(float(x["iv"]))
        elif tipo == "P" and -DELTA_ALTO <= _n(d1) - 1 <= -DELTA_BASSO:
            puts.append(float(x["iv"]))
    if len(calls) < MINIMO or len(puts) < MINIMO:
        return np.nan
    return float(np.median(calls) - np.median(puts))


def esegui(log=print) -> dict:
    giorni_rr = np.arange(DAL, AL + 1)
    rr = {}
    for n, g in enumerate(giorni_rr):
        rr[int(g)] = inclinazione(operazioni(int(g)))
        if n % 200 == 0:
            log(f"[cinquantanovesima] {sc.data(int(g))}: inclinazione {rr[int(g)]:.2f}" if np.isfinite(rr[int(g)]) else
                f"[cinquantanovesima] {sc.data(int(g))}: manca")
    s = pd.Series(rr)
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    j = pan["simboli"].index("BTCUSDT")
    costo = float(sc.costi_moneta(["BTCUSDT"])[0])
    giorni = np.arange(DAL + FINESTRA + 1, AL + 1, dtype=np.int64)
    R = sc.rendimenti(pan)[giorni - pan["t0"], j]
    Fd = np.nan_to_num(pan["funding"][giorni - pan["t0"], j])
    out = {"giorni_mancanti": int(s.isna().sum()), "giorni": int(len(s))}
    righe_seg = []
    for nome, solo_long in (("RR", False), ("RR solo long", True)):
        pos, prima, righe = 0.0, 0.0, []
        for g, r, f in zip(giorni, R, Fd):
            oggi = s.get(int(g) - 1, np.nan)
            storia = s.reindex(np.arange(g - 1 - FINESTRA, g - 1)).dropna()
            if np.isfinite(oggi) and len(storia) >= VALIDI:
                z = oggi - float(storia.median())
                pos = 1.0 if z > 0 else (0.0 if solo_long else -1.0)
                if not solo_long:
                    righe_seg.append((int(g), z))
            giro = abs(pos - prima)
            lordo, spese, fund = pos * r, giro * costo, pos * f
            righe.append({"lordo": lordo, "spese": spese, "funding": fund, "netto": lordo - spese - fund,
                          "netto_doppio": lordo - 2 * spese - fund, "giro": giro, "long": max(pos, 0.0), "short": max(-pos, 0.0),
                          "monete": 1})
            prima = pos
        d = pd.DataFrame(righe)
        sett = g1.per_settimana(d, giorni)
        RIS.mkdir(exist_ok=True)
        sett.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
        btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
        out[nome] = te.esame(sett, btc, inizio=int(sett.index.min()), anni_pieni=(2022, 2023, 2024, 2025))
        out[nome]["cambi_l_anno"] = float(d["giro"].gt(0).sum() / len(d) * 365)
        if nome == "RR":
            sett_rr = sett
    e = out["RR"]
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "121 RR": sett_rr["netto"]}, {"121 RR": e["intero"]})
    r = rivisto["candidate"]["121 RR"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    seg = pd.DataFrame(righe_seg, columns=["giorno", "z"]).set_index("giorno")
    rb = pd.Series(sc.rendimenti(pan)[:, j], index=np.arange(pan["t0"], pan["t0"] + pan["close"].shape[0]))
    seg["r1"] = rb.reindex(seg.index).to_numpy()
    seg["r7"] = [float(np.prod(1 + rb.reindex(np.arange(g, g + 7)).fillna(0).to_numpy()) - 1) for g in seg.index]
    e["correlazione_giorno_dopo"] = float(seg["z"].corr(seg["r1"]))
    e["correlazione_settimana_dopo"] = float(seg["z"].corr(seg["r7"]))
    anni = e.get("per_anno", {})
    e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(v > 0 for v in anni.values()))
    s.to_frame("inclinazione").to_csv(RIS / "inclinazione.csv.gz")
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, lo = e["intero"], out["RR solo long"]["intero"]
    testo = "\n".join([
        "# Programma 7 — risultati della cinquantanovesima prova (RR: l'inclinazione delle opzioni sul Bitcoin, ogni giorno)", "",
        "Regole in `CINQUANTANOVESIMA.md` (scritte prima). Operazioni di Deribit fra le 22 e le 24 UTC, dal 1° aprile 2021.", "",
        f"* Giorni con l'inclinazione: {out['giorni'] - out['giorni_mancanti']} su {out['giorni']}; cambi di verso {e['cambi_l_anno']:.0f} l'anno.",
        f"* **RR (long sopra la mediana dei 90 giorni, short sotto): Sharpe {i['sharpe']:.2f}**, {100 * i['annuo']:+.1f}% l'anno, volatilità "
        f"{100 * i['volatilita']:.1f}%, discesa {100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Solo long (fuori sotto la mediana): Sharpe {lo['sharpe']:.2f}, {100 * lo['annuo']:+.1f}% l'anno, discesa {100 * lo['discesa_max']:.1f}%.",
        f"* Correlazione fra il segnale e il Bitcoin del giorno dopo {e['correlazione_giorno_dopo']:.3f}, della settimana dopo "
        f"{e['correlazione_settimana_dopo']:.3f}.",
        f"* Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}; regola del proprietario: "
        f"{'sì' if e['regola_proprietario'] else 'no'}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_CINQUANTANOVESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CINQUANTANOVESIMA FINITA", flush=True)
