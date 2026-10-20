"""Programma 6, ventisettesima prova (VENTISETTESIMA.md): E4 su Gate.io. Al primo regolamento con la distanza dal precedente
piu' corta di quella di prima (al massimo 8 ore) e il tasso positivo: short la moneta e long il Bitcoin di Gate.io per 7
giorni dall'apertura del giorno dopo. Decide l'insieme degli eventi senza un passaggio di Binance sulla stessa moneta nei 7
giorni prima o dopo.

Uso: python3 -m research.programma6.ventisettesima
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import annunci as an
from research.programma6 import seconda as sc
from research.programma6 import ventiseiesima as vs
from research.programma6 import ventunesima as vu

QUI = Path(__file__).parent
RIS = QUI / "risultati_ventisettesima"
DATI = QUI.parents[1] / "research" / "data" / "gate"
MAX_ORE, P_SOGLIA, MIN_INDIPENDENTI = 8, 0.01, 30


def _leggi(cartella: str, nome: str) -> list:
    righe = []
    for f in sorted((DATI / cartella).glob(f"*/{nome}-*.csv.gz")):
        righe += [r.split(",") for r in gzip.decompress(f.read_bytes()).decode().split() if r]
    return righe


def contratti() -> list:
    return sorted({f.name.rsplit("-", 1)[0] for f in (DATI / "funding_applies").glob("*/*.csv.gz")})


def eventi_contratto(righe: list) -> list:
    """(secondi, tasso) dei regolamenti dove la distanza dal precedente si accorcia (quella di prima ≤ 8 ore)."""
    if len(righe) < 3:
        return []
    d = pd.DataFrame([(int(r[0]), float(r[1])) for r in righe], columns=["ts", "tasso"]).drop_duplicates("ts").sort_values("ts")
    ts, tasso = d["ts"].to_numpy(), d["tasso"].to_numpy()
    sp = np.diff(ts)
    out = []
    for k in range(2, len(ts)):
        if sp[k - 1] < sp[k - 2] <= MAX_ORE * 3600:
            out.append((int(ts[k]), float(tasso[k])))
    return out


def candele(righe: list) -> pd.DataFrame:
    """Giorno dall'epoca → apertura, chiusura, volume (colonne di Gate.io: t, v, c, h, l, o)."""
    if not righe:
        return pd.DataFrame()
    d = pd.DataFrame([(int(r[0]) // 86400, float(r[1]), float(r[2]), float(r[5])) for r in righe],
                     columns=["giorno", "volume", "close", "open"]).drop_duplicates("giorno", keep="last")
    return d.set_index("giorno").sort_index()


def funding_giorni(righe: list) -> pd.Series:
    if not righe:
        return pd.Series(dtype=float)
    d = pd.DataFrame([(int(r[0]), float(r[1])) for r in righe], columns=["ts", "tasso"]).drop_duplicates("ts")
    tenuta = (d["ts"].to_numpy() // 60 - 1) // 1440          # come seconda.funding_giorni (secondi invece di ms)
    return pd.Series(d["tasso"].to_numpy(), index=tenuta).groupby(level=0).sum()


def esegui(log=print) -> dict:
    nomi = contratti()
    log(f"[ventisettesima] {len(nomi)} contratti")
    btc_c, btc_f = candele(_leggi("candlesticks_1d", "BTC_USDT")), funding_giorni(_leggi("funding_applies", "BTC_USDT"))
    pan = sc.pannello()
    eb = {}
    for s, ms, _ in vs.eventi(pan):
        eb.setdefault(s, []).append(ms // 1000)
    righe = []
    for nome in nomi:
        if nome == "BTC_USDT":
            continue
        fr = _leggi("funding_applies", nome)
        ev = [(t, r) for t, r in eventi_contratto(fr) if r > 0]
        if not ev:
            continue
        c, f = candele(_leggi("candlesticks_1d", nome)), funding_giorni(fr)
        perp = an.perpetuo(nome.split("_")[0], pan["simboli"])
        for t, _ in ev:
            g = t // 86400
            e = g + 1
            if g not in c.index or c.loc[g, "volume"] <= 0 or e not in c.index or e not in btc_c.index:
                continue
            r = {"data": sc.data(g), "annuncio": int((g + 3) // 7), "simbolo": nome,
                 "binance_vicino": bool(perp and any(abs(t - x) <= 7 * 86400 for x in eb.get(perp, [])))}
            for k in (vu.GIORNI,) + vu.ALTRI:
                x = e + k
                pc = c["close"][c.index < x].iloc[-1] if x not in c.index else c.loc[x, "open"]
                pb = btc_c["close"][btc_c.index < x].iloc[-1] if x not in btc_c.index else btc_c.loc[x, "open"]
                rc, rb = pc / c.loc[e, "open"] - 1, pb / btc_c.loc[e, "open"] - 1
                fc = f[(f.index >= e) & (f.index < x)].sum()
                fb = btc_f[(btc_f.index >= e) & (btc_f.index < x)].sum()
                r[f"r{k}"] = float(rb - rc - vu.COSTO_MONETA - vu.COSTO_BTC + fc - fb) if x <= btc_c.index.max() else float("nan")
            r["reazione"] = float((btc_c.loc[e, "open"] / btc_c.loc[g, "open"]) - (c.loc[e, "open"] / c.loc[g, "open"])) \
                if g in btc_c.index else float("nan")
            righe.append(r)
    df = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_gate.csv", index=False)
    ind = df[~df["binance_vicino"]]
    out = {"tutti": vu.esame(df), "indipendenti": vu.esame(ind)}
    decide = "indipendenti" if len(ind) >= MIN_INDIPENDENTI else "tutti"
    e = out[decide]
    es = "CONFERMATA"
    if not e["boot"]["p"] <= P_SOGLIA:
        es = f"media non sopra zero con p ≤ 0,01 (p {e['boot']['p']:.4f})"
    elif not (e["prima_meta"] > 0 and e["seconda_meta"] > 0):
        es = "non positiva in tutte e due le metà"
    elif not e["senza_5_migliori"] > 0:
        es = "non positiva senza i 5 eventi migliori"
    out["decide"], out["esito"] = decide, es
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    righe_t = ["# Programma 6 — risultati della ventisettesima prova (E4 su Gate.io)", "",
               "Regole in `VENTISETTESIMA.md` (scritte prima). Short la moneta e long il Bitcoin di Gate.io per 7 giorni "
               "dall'apertura del giorno dopo il primo regolamento con l'intervallo più corto e il tasso positivo; eventi in "
               "`risultati_ventisettesima/eventi_gate.csv`.", "",
               "| Insieme | Eventi (settimane) | Media a 7 giorni | Intervallo | p | Prima metà, seconda metà | Senza i 5 migliori | "
               "Vinti | A 1, 3, 14, 28 giorni |", "|---|---|---|---|---|---|---|---|---|"]
    for nome in ("indipendenti", "tutti"):
        x = out[nome]
        b = x["boot"]
        righe_t.append(f"| {nome}{' (decide)' if nome == decide else ''} | {b['eventi']} ({b['annunci']}) | {100 * b['media']:+.2f}% | "
                       f"{100 * b['basso']:+.2f}%; {100 * b['alto']:+.2f}% | {b['p']:.4f} | {100 * x['prima_meta']:+.2f}%, "
                       f"{100 * x['seconda_meta']:+.2f}% | {100 * x['senza_5_migliori']:+.2f}% | {100 * x['vinti']:.0f}% | "
                       + ", ".join(f"{100 * v:+.2f}%" for v in x["altri_orizzonti"].values()) + " |")
    for nome in ("indipendenti", "tutti"):
        righe_t += ["", f"**{nome}, per anno (media a 7 giorni)**: " + ", ".join(f"{a} {100 * v:+.2f}%" for a, v in out[nome]["per_anno"].items())]
    righe_t += ["", f"**Esito della conferma: {es}**"]
    testo = "\n".join(righe_t) + "\n"
    (QUI / "RISULTATI_VENTISETTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTISETTESIMA FINITA", flush=True)
