"""Programma 6, trentesima prova (TRENTESIMA.md): N3 su Gate.io. Short le monete appena quotate (eta' 7 giorni) non ancora
perpetuo su Binance, long il Bitcoin di Gate.io; uscita a +30% (candele a 1 ora, 1% di scarto) o dopo 30 giorni.

Uso: python3 -m research.programma6.trentesima
"""
from __future__ import annotations

import gzip
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import annunci as an
from research.programma6 import scarico_gate as sg
from research.programma6 import seconda as sc
from research.programma6 import tipi_gate as tg
from research.programma6 import ventisettesima as vt
from research.programma6 import ventunesima as vu

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentesima"
ETA, GIORNI, STOP, SCARTO_STOP, P_SOGLIA = 7, 30, 0.30, 0.01, 0.01
DA, A = sc.giorno(2023, 2, 1), sc.giorno(2026, 7, 31)
# le monete stabili (TRENTESIMA.md, sezione 4)
STABILI = ("USDC", "FDUSD", "TUSD", "BUSD", "USDP", "DAI", "USD1", "USDE", "PYUSD", "RLUSD", "USDD", "USDS", "USDG",
           "EURC", "EURI", "XUSD")


def _mese(g: int) -> str:
    return pd.Timestamp(g * 86400, unit="s").strftime("%Y%m")


def ore(nome: str, mesi: list) -> pd.DataFrame:
    """Ora dall'epoca → apertura, massimo, chiusura (colonne di Gate.io: t, v, c, h, l, o)."""
    righe = []
    for m in mesi:
        f = vt.DATI / "candlesticks_1h" / m / f"{nome}-{m}.csv.gz"
        if f.exists():
            righe += [r.split(",") for r in gzip.decompress(f.read_bytes()).decode().split() if r]
    if not righe:
        return pd.DataFrame()
    d = pd.DataFrame([(int(r[0]) // 3600, float(r[2]), float(r[3]), float(r[5])) for r in righe],
                     columns=["ora", "close", "high", "open"]).drop_duplicates("ora", keep="last")
    return d.set_index("ora").sort_index()


def candidati(pan: dict) -> list:
    """(nome, giorno della prima candela) dei contratti nuovi ammessi (sezione 2)."""
    primi = {}
    for f in (vt.DATI / "candlesticks_1d").glob("*/*.csv.gz"):
        nome = f.name.rsplit("-", 1)[0]
        if nome not in primi or f.parent.name < primi[nome].parent.name:
            primi[nome] = f
    ok = np.isfinite(pan["close"])
    primo_b = ok.argmax(axis=0) + pan["t0"]
    tipi = tg.carica()
    out = []
    for nome, f in primi.items():
        if f.parent.name <= "202301" or nome == "BTC_USDT":
            continue
        righe = [r.split(",") for r in gzip.decompress(f.read_bytes()).decode().split() if r]
        g0 = min(int(r[0]) // 86400 for r in righe)
        if not (DA <= g0 <= A):
            continue
        sigla = nome.split("_")[0]
        if f"{sigla}USDT" in sc.ESCLUSI or not tg.moneta(nome, tipi) or sigla in STABILI:
            continue
        p = an.perpetuo(sigla, pan["simboli"])
        if p and primo_b[pan["simboli"].index(p)] <= g0 + ETA:
            continue
        out.append((nome, g0))
    return sorted(out, key=lambda x: x[1])


def scarica_ore(cand: list) -> None:
    chiavi = set()
    for nome, g0 in cand:
        for g in range(g0 + ETA, g0 + ETA + GIORNI + 2, 10):
            chiavi.add(f"futures_usdt/candlesticks_1h/{_mese(g)}/{nome}-{_mese(g)}.csv.gz")
        chiavi.add(f"futures_usdt/candlesticks_1h/{_mese(g0 + ETA + GIORNI + 1)}/{nome}-{_mese(g0 + ETA + GIORNI + 1)}.csv.gz")
    for m in sorted({k.split("/")[2] for k in chiavi}):
        chiavi.add(f"futures_usdt/candlesticks_1h/{m}/BTC_USDT-{m}.csv.gz")

    def una(k):
        try:
            return sg.scarica(k)
        except Exception:
            return None                                   # il mese puo' mancare (moneta tolta prima)
    with ThreadPoolExecutor(max_workers=32) as ex:
        list(ex.map(una, sorted(chiavi)))


def operazione(c: pd.DataFrame, cb: pd.DataFrame, f: pd.Series, fb: pd.Series, e: int, protezione: bool) -> dict:
    """Short la moneta e long il Bitcoin dall'apertura del giorno ``e``; con ``protezione`` l'uscita a +30%."""
    h0, h1 = e * 24, (e + GIORNI) * 24
    if h0 not in c.index or h0 not in cb.index:
        return {}
    p0, b0 = c.loc[h0, "open"], cb.loc[h0, "open"]
    tratto = c[(c.index >= h0) & (c.index < h1)]
    uscita_h, pc, fermata = None, None, False
    if protezione:
        su = tratto.index[tratto["high"].to_numpy() >= p0 * (1 + STOP)]
        if len(su):
            uscita_h, pc, fermata = int(su[0]), p0 * (1 + STOP) * (1 + SCARTO_STOP), True
    if uscita_h is None:
        if h1 in c.index:
            uscita_h, pc = h1, c.loc[h1, "open"]
        elif len(tratto):
            uscita_h, pc = int(tratto.index[-1]) + 1, tratto["close"].iloc[-1]     # serie finita prima: l'ultimo prezzo
        else:
            return {}
    bb = cb[cb.index <= uscita_h]
    pb = cb.loc[uscita_h, "open"] if (not fermata and uscita_h in cb.index) else bb["close"].iloc[-1]
    gu = uscita_h // 24
    fc = f[(f.index >= e) & (f.index <= gu)].sum()
    fbb = fb[(fb.index >= e) & (fb.index <= gu)].sum()
    r = (pb / b0 - 1) - (pc / p0 - 1) - vu.COSTO_MONETA - vu.COSTO_BTC + fc - fbb
    return {"r": float(r), "fermata": fermata, "giorni": float((uscita_h - h0) / 24)}


def esame(df: pd.DataFrame, col: str) -> dict:
    d = df[np.isfinite(df[col])].sort_values("data")
    e = {"boot": vu.bootstrap_annunci(d, col)}
    meta = len(d) // 2
    e["prima_meta"], e["seconda_meta"] = float(d[col].iloc[:meta].mean()), float(d[col].iloc[meta:].mean())
    e["senza_5_migliori"] = float(d[col].sort_values(ascending=False).iloc[5:].mean())
    e["vinti"], e["mediana"] = float((d[col] > 0).mean()), float(d[col].median())
    e["per_anno"] = {a: {"eventi": int(len(g)), "media": float(g[col].mean())} for a, g in d.groupby(d["data"].str[:4])}
    es = "VALIDA"
    if not e["boot"]["p"] <= P_SOGLIA:
        es = f"media non sopra zero con p ≤ 0,01 (p {e['boot']['p']:.4f})"
    elif not (e["prima_meta"] > 0 and e["seconda_meta"] > 0):
        es = "non positiva in tutte e due le metà"
    elif not e["senza_5_migliori"] > 0:
        es = "non positiva senza i 5 eventi migliori"
    e["esito"] = es
    return e


def esegui(log=print) -> dict:
    pan = sc.pannello()
    cand = candidati(pan)
    log(f"[trentesima] {len(cand)} contratti nuovi ammessi; scarico le candele a 1 ora")
    scarica_ore(cand)
    mesi_tutti = sorted({p.name for p in (vt.DATI / "candlesticks_1h").iterdir()})
    cb = ore("BTC_USDT", mesi_tutti)
    fb = vt.funding_giorni(vt._leggi("funding_applies", "BTC_USDT"))
    righe = []
    for nome, g0 in cand:
        e = g0 + ETA
        cd = vt.candele(vt._leggi("candlesticks_1d", nome))
        if (e - 1) not in cd.index or cd.loc[e - 1, "volume"] <= 0:
            continue
        mesi = sorted({_mese(g) for g in range(e, e + GIORNI + 2)})
        c = ore(nome, mesi)
        if c.empty:
            continue
        f = vt.funding_giorni(vt._leggi("funding_applies", nome))
        con, senza = operazione(c, cb, f, fb, e, True), operazione(c, cb, f, fb, e, False)
        if not con or not senza:
            continue
        righe.append({"data": sc.data(e), "annuncio": int((e + 3) // 7), "simbolo": nome, "r": con["r"], "fermata": con["fermata"],
                      "giorni": con["giorni"], "r_senza": senza["r"]})
    df = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_N3.csv", index=False)
    out = {"con_uscita": esame(df, "r"), "senza_uscita": esame(df, "r_senza"), "fermate": float(df["fermata"].mean()),
           "contratti_ammessi": len(cand)}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    righe_t = ["# Programma 6 — risultati della trentesima prova (N3: monete nuove short con l'uscita, su Gate.io)", "",
               "Regole in `TRENTESIMA.md` (scritte prima). Short all'età di 7 giorni, long il Bitcoin, uscita a +30% (candele a 1 "
               "ora, 1% di scarto) o dopo 30 giorni; monete nuove di Gate.io non ancora perpetuo su Binance; eventi in "
               "`risultati_trentesima/eventi_N3.csv`.", "",
               "| Versione | Eventi (settimane) | Media a evento | Intervallo | p | Mediana | Vinti | Prima metà, seconda metà | "
               "Senza i 5 migliori | Esito |", "|---|---|---|---|---|---|---|---|---|---|"]
    for nome, x in (("con l'uscita a +30% (la regola)", out["con_uscita"]), ("senza l'uscita (per capire)", out["senza_uscita"])):
        b = x["boot"]
        righe_t.append(f"| {nome} | {b['eventi']} ({b['annunci']}) | {100 * b['media']:+.2f}% | {100 * b['basso']:+.2f}%; "
                       f"{100 * b['alto']:+.2f}% | {b['p']:.4f} | {100 * x['mediana']:+.2f}% | {100 * x['vinti']:.0f}% | "
                       f"{100 * x['prima_meta']:+.2f}%, {100 * x['seconda_meta']:+.2f}% | {100 * x['senza_5_migliori']:+.2f}% | "
                       f"{x['esito'] if 'regola' in nome else '—'} |")
    righe_t += ["", f"L'uscita di protezione scatta nel {100 * out['fermate']:.0f}% degli eventi.", "",
                "**Per anno (con l'uscita)**: " + ", ".join(f"{a} {100 * v['media']:+.2f}% ({v['eventi']})"
                                                         for a, v in out["con_uscita"]["per_anno"].items())]
    testo = "\n".join(righe_t) + "\n"
    (QUI / "RISULTATI_TRENTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTESIMA FINITA", flush=True)
