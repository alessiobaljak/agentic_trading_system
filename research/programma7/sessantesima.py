"""Programma 7, sessantesima prova (SESSANTESIMA.md): RRE, l'inclinazione delle opzioni al contrario sull'Ether. Ogni giorno, dalle
operazioni di Deribit fra le 16 e le 24 UTC con scadenza fra 7 e 60 giorni (almeno 10 per parte): mediana della volatilita' implicita
delle opzioni d'acquisto con delta 0,15-0,35 meno quella delle opzioni di vendita. Short l'Ether il giorno dopo se sopra la mediana
dei 90 giorni prima, long se sotto. Si salva solo l'inclinazione di ogni giorno.

Uso: python3 -m research.programma7.sessantesima
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma7 import cinquantanovesima as rr
from research.programma7 import prima as g1

QUI = Path(__file__).parent
RADICE = QUI.parents[1]
RIS = QUI / "risultati_sessantesima"
DATI = RADICE / "research" / "data" / "deribit_rr_eth"
URL = ("https://history.deribit.com/api/v2/public/get_last_trades_by_currency_and_time?currency=ETH&kind=option"
       "&start_timestamp={a}&end_timestamp={b}&count=10000&sorting=asc")
DAL, AL = sc.giorno(2021, 4, 1), sc.giorno(2026, 10, 25)
ORA_DA, ORE = 16, 8
MIN_G, MAX_G, MINIMO = 7, 60, 10


def inclinazione_giorno(g: int) -> float:
    """L'inclinazione del giorno g, scaricando le operazioni a pagine senza salvarle."""
    a = (g * 1440 + ORA_DA * 60) * 60_000
    b, inizio, calls, puts = a + ORE * 3_600_000, a, [], []
    while True:
        d = rr._get(URL.format(a=inizio, b=b))
        if not d or "result" not in d:
            return np.nan
        tr = d["result"]["trades"]
        for x in tr:
            try:
                _, scad, k, tipo = x["instrument_name"].split("-")
                dt = datetime(2000 + int(scad[-2:]), rr.MESI[scad[-5:-2]], int(scad[:-5]), 8, tzinfo=timezone.utc)
            except (ValueError, KeyError):
                continue
            giorni = (dt.timestamp() * 1000 - x["timestamp"]) / 86_400_000
            if not (MIN_G <= giorni <= MAX_G) or not x.get("iv") or not x.get("index_price"):
                continue
            s, kk, sig, t = float(x["index_price"]), float(k), float(x["iv"]) / 100, giorni / 365
            d1 = (math.log(s / kk) + 0.5 * sig * sig * t) / (sig * math.sqrt(t))
            if tipo == "C" and rr.DELTA_BASSO <= rr._n(d1) <= rr.DELTA_ALTO:
                calls.append(float(x["iv"]))
            elif tipo == "P" and -rr.DELTA_ALTO <= rr._n(d1) - 1 <= -rr.DELTA_BASSO:
                puts.append(float(x["iv"]))
        if not d["result"].get("has_more") or not tr:
            break
        inizio = tr[-1]["timestamp"] + 1
    if len(calls) < MINIMO or len(puts) < MINIMO:
        return np.nan
    return float(np.median(calls) - np.median(puts))


def serie() -> pd.Series:
    f = DATI / "inclinazione.csv"
    fatto = pd.read_csv(f, index_col=0).iloc[:, 0] if f.exists() else pd.Series(dtype=float)
    DATI.mkdir(parents=True, exist_ok=True)
    for n, g in enumerate(range(DAL, AL + 1)):
        if g in fatto.index:
            continue
        fatto.loc[g] = inclinazione_giorno(g)
        if n % 50 == 0:
            fatto.sort_index().to_frame("inclinazione").to_csv(f)
            print(f"[sessantesima] {sc.data(g)}", flush=True)
    fatto = fatto.sort_index()
    fatto.to_frame("inclinazione").to_csv(f)
    return fatto


def esegui(log=print) -> dict:
    s = serie()
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    j = pan["simboli"].index("ETHUSDT")
    costo = float(sc.costi_moneta(["ETHUSDT"])[0])
    giorni = np.arange(DAL + rr.FINESTRA + 1, AL + 1, dtype=np.int64)
    R = sc.rendimenti(pan)[giorni - pan["t0"], j]
    Fd = np.nan_to_num(pan["funding"][giorni - pan["t0"], j])
    eth = pd.Series(ps["R"][:, ps["simboli"].index("ETHUSDT")], index=ps["lunedi"])
    out = {"giorni_mancanti": int(s.isna().sum()), "giorni": int(len(s))}
    seg = []
    for nome, solo_short in (("RRE", False), ("RRE solo short", True)):
        pos, prima, righe = 0.0, 0.0, []
        for g, r, f in zip(giorni, R, Fd):
            oggi = s.get(int(g) - 1, np.nan)
            storia = s.reindex(np.arange(g - 1 - rr.FINESTRA, g - 1)).dropna()
            if np.isfinite(oggi) and len(storia) >= rr.VALIDI:
                z = oggi - float(storia.median())
                pos = -1.0 if z > 0 else (0.0 if solo_short else 1.0)
                if not solo_short:
                    seg.append((int(g), z))
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
        out[nome] = te.esame(sett, eth, inizio=int(sett.index.min()), anni_pieni=(2022, 2023, 2024, 2025))
        out[nome]["cambi_l_anno"] = float(d["giro"].gt(0).sum() / len(d) * 365)
        if nome == "RRE":
            sett_r = sett
    e = out["RRE"]
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "122 RRE": sett_r["netto"]}, {"122 RRE": e["intero"]})
    r = rivisto["candidate"]["122 RRE"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    sg = pd.DataFrame(seg, columns=["giorno", "z"]).set_index("giorno")
    re_ = pd.Series(sc.rendimenti(pan)[:, j], index=np.arange(pan["t0"], pan["t0"] + pan["close"].shape[0]))
    e["correlazione_giorno_dopo"] = float(sg["z"].corr(pd.Series(re_.reindex(sg.index).to_numpy(), index=sg.index)))
    anni = e.get("per_anno", {})
    e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(v > 0 for v in anni.values()))
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, so = e["intero"], out["RRE solo short"]["intero"]
    testo = "\n".join([
        "# Programma 7 — risultati della sessantesima prova (RRE: l'inclinazione delle opzioni al contrario, sull'Ether)", "",
        "Regole in `SESSANTESIMA.md` (scritte prima). Operazioni di Deribit sulle opzioni dell'Ether fra le 16 e le 24 UTC, dal 1° aprile 2021.", "",
        f"* Giorni con l'inclinazione: {out['giorni'] - out['giorni_mancanti']} su {out['giorni']}; cambi di verso {e['cambi_l_anno']:.0f} l'anno.",
        f"* **RRE (short sopra la mediana dei 90 giorni, long sotto): Sharpe {i['sharpe']:.2f}**, {100 * i['annuo']:+.1f}% l'anno, volatilità "
        f"{100 * i['volatilita']:.1f}%, discesa {100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Solo short (fuori sotto la mediana): Sharpe {so['sharpe']:.2f}, {100 * so['annuo']:+.1f}% l'anno.",
        f"* Correlazione fra il segnale e l'Ether del giorno dopo {e['correlazione_giorno_dopo']:.3f} (sul Bitcoin, prova 121: −0,117).",
        f"* Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}; regola del proprietario: "
        f"{'sì' if e['regola_proprietario'] else 'no'}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_SESSANTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SESSANTESIMA FINITA", flush=True)
