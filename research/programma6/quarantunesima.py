"""Programma 6, quarantunesima prova (QUARANTUNESIMA.md): U1, lo short dopo l'arrivo su Upbit. Per ogni moneta arrivata sul
mercato in won di Upbit dal 2021 che aveva gia' il perpetuo su Binance da almeno 7 giorni: short la moneta e long il Bitcoin
2 ore dopo la prima ora di Upbit, per 7 giorni, con l'uscita a +30%.

Uso: python3 -m research.programma6.scarico_upbit && python3 -m research.programma6.quarantunesima
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import annunci as an
from research.programma6 import esecuzione as es
from research.programma6 import quarantesima as qr
from research.programma6 import quarta as qa
from research.programma6 import scarico_upbit as su
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import trentaduesima as td
from research.programma6 import trentesima as tr
from research.programma6 import ventunesima as vu

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantunesima"
DA, A = sc.giorno(2021, 1, 1), sc.giorno(2026, 9, 20)
ETA_MIN, ORE_DOPO, ORE_TENUTA, CAMBIO = 7, 2, 168, (900.0, 1700.0)
PROVE_EVENTI = 7
P_SOGLIA = 0.01 / PROVE_EVENTI
QUOTA, MAX_APERTE = 0.05, 20
PRIMO_LUNEDI = sc.giorno(2021, 1, 4)


def multiplo(p: str) -> float:
    if p.startswith("1000000") or p.startswith("1M"):
        return 1e6
    return 1e3 if p.startswith("1000") else 1.0


def ora(testo: str) -> int:
    return int(datetime.fromisoformat(testo).replace(tzinfo=timezone.utc).timestamp() // 3600)


def eventi(pan: dict, quotazioni: list) -> tuple:
    """(eventi ammessi, quanti tolti per motivo)."""
    ok = np.isfinite(pan["close"])
    primo_b = ok.argmax(axis=0) + pan["t0"]
    out, tolti = [], {"senza perpetuo": 0, "perpetuo troppo giovane o dopo": 0, "omonimo": 0, "fuori periodo": 0}
    for x in quotazioni:
        if not x.get("prima_ora"):
            if x.get("primo_mese", "0000") >= su.PRIMO_MESE_UTILE:
                tolti["senza ora d'arrivo"] = tolti.get("senza ora d'arrivo", 0) + 1
            continue
        sigla = x["mercato"].split("-", 1)[1]
        if sigla == "BTC" or sigla in tr.STABILI:
            continue
        hu = ora(x["prima_ora"])
        gu = hu // 24
        if not (DA <= gu <= A):
            tolti["fuori periodo"] += 1
            continue
        p = an.perpetuo(sigla, pan["simboli"])
        if not p or p in sc.ESCLUSI:
            tolti["senza perpetuo"] += 1
            continue
        j = pan["simboli"].index(p)
        if not ok[:, j].any() or primo_b[j] > gu - ETA_MIN:
            tolti["perpetuo troppo giovane o dopo"] += 1
            continue
        g1 = sc.giorno(*map(int, x["primo_giorno"].split("-")))
        chiusura = pan["close"][g1 - pan["t0"], j]
        cambio = x["prezzo_primo_giorno"] / (chiusura / multiplo(p)) if np.isfinite(chiusura) and chiusura > 0 else np.nan
        if not (CAMBIO[0] <= cambio <= CAMBIO[1]):
            tolti["omonimo"] += 1
            continue
        out.append({"simbolo": p, "mercato": x["mercato"], "ora_upbit": hu, "giorno": gu, "eta": int(gu - primo_b[j]),
                    "cambio": float(cambio)})
    return out, tolti


def operazione(c: pd.DataFrame, cb: pd.DataFrame, f: pd.Series, fb: pd.Series, h0: int, ore_tenuta: int,
               protezione: bool) -> dict:
    """Come `trentesima.operazione`, con l'entrata all'ora ``h0`` e la tenuta in ore."""
    h1 = h0 + ore_tenuta
    if h0 not in c.index or h0 not in cb.index or not (np.isfinite(c.loc[h0, "open"]) and np.isfinite(cb.loc[h0, "open"])):
        return {}
    p0, b0 = c.loc[h0, "open"], cb.loc[h0, "open"]
    tratto = c[(c.index >= h0) & (c.index < h1)].dropna(subset=["open"])
    uscita_h, pc, fermata = None, None, False
    if protezione:
        su_ = tratto.index[tratto["high"].to_numpy() >= p0 * (1 + tr.STOP)]
        if len(su_):
            uscita_h, pc, fermata = int(su_[0]), p0 * (1 + tr.STOP) * (1 + tr.SCARTO_STOP), True
    if uscita_h is None:
        if h1 in c.index and np.isfinite(c.loc[h1, "open"]):
            uscita_h, pc = h1, c.loc[h1, "open"]
        elif len(tratto):
            uscita_h, pc = int(tratto.index[-1]) + 1, tratto["close"].iloc[-1]
        else:
            return {}
    bb = cb[(cb.index <= uscita_h)].dropna(subset=["close"])
    pb = cb.loc[uscita_h, "open"] if (not fermata and uscita_h in cb.index and np.isfinite(cb.loc[uscita_h, "open"])) \
        else bb["close"].iloc[-1]
    e, gu = h0 // 24, uscita_h // 24
    fc = f[(f.index >= e) & (f.index <= gu)].sum()
    fbb = fb[(fb.index >= e) & (fb.index <= gu)].sum()
    r = (pb / b0 - 1) - (pc / p0 - 1) - vu.COSTO_MONETA - vu.COSTO_BTC + fc - fbb
    return {"r": float(r), "fermata": fermata, "uscita_h": int(uscita_h)}


def reazione(c: pd.DataFrame, cb: pd.DataFrame, hu: int, h0: int) -> float:
    """Dalla apertura 24 ore prima della prima ora di Upbit all'entrata: la moneta meno il Bitcoin."""
    a = hu - 24
    if not all(h in x.index and np.isfinite(x.loc[h, "open"]) for x in (c, cb) for h in (a, h0)):
        return float("nan")
    return float((c.loc[h0, "open"] / c.loc[a, "open"] - 1) - (cb.loc[h0, "open"] / cb.loc[a, "open"] - 1))


def portafoglio(df: pd.DataFrame) -> pd.DataFrame:
    """Il 5% a operazione, al massimo 20 aperte; la settimana somma le operazioni chiuse (dal lunedi')."""
    d = df.sort_values(["ora", "simbolo"]).reset_index(drop=True)
    aperte, tenute = [], []
    for k, x in d.iterrows():
        aperte = [u for u in aperte if u > x["ora"]]
        if len(aperte) >= MAX_APERTE:
            continue
        aperte.append(x["uscita_h"])
        tenute.append(k)
    t = d.loc[tenute]
    lun = ((t["uscita_h"].to_numpy() // 24 + 3) // 7) * 7 - 3
    costo = vu.COSTO_MONETA + vu.COSTO_BTC
    sett = pd.Series(QUOTA * t["r"].to_numpy(), index=lun).groupby(level=0).sum()
    sett_d = pd.Series(QUOTA * (t["r"].to_numpy() - costo), index=lun).groupby(level=0).sum()
    tutte = np.arange(PRIMO_LUNEDI, A + 14, 7)
    out = pd.DataFrame({"netto": sett.reindex(tutte).fillna(0.0), "netto_doppio": sett_d.reindex(tutte).fillna(0.0)})
    for k in ("lordo", "spese", "funding", "giro", "long", "short"):
        out[k] = 0.0
    out["monete"] = 1
    return out


def esame_eventi(df: pd.DataFrame, col: str) -> dict:
    d = df[np.isfinite(df[col])].sort_values("ora")
    e = {"boot": vu.bootstrap_annunci(d, col)}
    meta = len(d) // 2
    e["prima_meta"], e["seconda_meta"] = float(d[col].iloc[:meta].mean()), float(d[col].iloc[meta:].mean())
    e["senza_5_migliori"] = float(d[col].sort_values(ascending=False).iloc[5:].mean())
    e["vinti"], e["mediana"] = float((d[col] > 0).mean()), float(d[col].median())
    e["per_anno"] = {a: {"eventi": int(len(g)), "media": float(g[col].mean())} for a, g in d.groupby(d["data"].str[:4])}
    e["passa"] = bool(e["boot"]["p"] <= P_SOGLIA and e["prima_meta"] > 0 and e["seconda_meta"] > 0 and e["senza_5_migliori"] > 0)
    return e


def esegui(log=print) -> dict:
    pan = sc.pannello()
    quotazioni = json.loads((su.DATI / "quotazioni.json").read_text())
    ev, tolti = eventi(pan, quotazioni)
    log(f"[quarantunesima] {len(ev)} eventi ammessi; tolti {tolti}")
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: td.scarica_ore(x["simbolo"], x["giorno"] - 1), ev))
    jb = pan["simboli"].index("BTCUSDT")
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    fb = pd.Series(pan["funding"][:, jb], index=giorni)
    cb = es.ore_di("BTCUSDT")
    righe, senza_ore = [], 0
    for x in ev:
        s = x["simbolo"]
        c = qa.ore(s)
        h0 = x["ora_upbit"] + ORE_DOPO
        if c.empty or h0 not in c.index or not np.isfinite(c.loc[h0, "open"]):
            c = es.ore_di(s)
        f = pd.Series(pan["funding"][:, pan["simboli"].index(s)], index=giorni)
        o = operazione(c, cb, f, fb, h0, ORE_TENUTA, True)
        if not o:
            senza_ore += 1
            continue
        riga = {**x, "ora": h0, "data": sc.data(h0 // 24), "annuncio": int((h0 // 24 + 3) // 7), "r": o["r"],
                "fermata": o["fermata"], "uscita_h": o["uscita_h"], "reazione": reazione(c, cb, x["ora_upbit"], h0)}
        for n, ore_n in (("r1", 24), ("r3", 72), ("r7_senza", 168), ("r14", 336)):
            oo = operazione(c, cb, f, fb, h0, ore_n, False)
            riga[n] = oo["r"] if oo else np.nan
        righe.append(riga)
    df = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_U1.csv", index=False)
    e = {"eventi": esame_eventi(df, "r"), "ammessi": len(ev), "tolti": tolti, "senza_candele_a_1_ora": senza_ore,
         "fermate": float(df["fermata"].mean()), "reazione_media": float(df["reazione"].mean()),
         "reazione_mediana": float(df["reazione"].median()),
         "altri_orizzonti": {n: float(df[n].mean()) for n in ("r1", "r3", "r7_senza", "r14")},
         "sovrapposti_a_N3": int((df["eta"] < tr.ETA + tr.GIORNI).sum())}
    sr = qr.prove_fino_alla_trentanovesima()
    sr.append(json.loads((QUI / "risultati_quarantesima" / "esame.json").read_text())["portafoglio"]["intero"]["sharpe"])
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    p = te.esame(portafoglio(df), btc, inizio=PRIMO_LUNEDI, anni_pieni=se.ANNI_PIENI)
    sr.append(p["intero"]["sharpe"])
    i = p["intero"]
    p["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
    p["prove_nel_conto"] = len(sr)
    p["esito"] = te.esito(p, p["sharpe_corretto"])
    e["portafoglio"] = p
    e["esito"] = "VALIDA" if e["eventi"]["passa"] and p["esito"] == "VALIDA" else "non valida"
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    v, b = e["eventi"], e["eventi"]["boot"]
    testo = "\n".join([
        "# Programma 6 — risultati della quarantunesima prova (U1: lo short dopo l'arrivo su Upbit)", "",
        "Regole in `QUARANTUNESIMA.md` (scritte prima).", "",
        f"* Mercati in won di Upbit di oggi: {len(quotazioni)}; eventi ammessi {len(ev)} (tolti: "
        + ", ".join(f"{k} {n}" for k, n in tolti.items()) + f"); senza le candele a 1 ora all'entrata {senza_ore}.",
        f"* {b['eventi']} eventi in {b['annunci']} settimane: media netta {100 * b['media']:+.2f}% a evento (intervallo "
        f"{100 * b['basso']:+.2f}; {100 * b['alto']:+.2f}, p {b['p']:.4f}, soglia {P_SOGLIA:.4f}); mediana "
        f"{100 * v['mediana']:+.2f}%; vinti {100 * v['vinti']:.0f}%; metà {100 * v['prima_meta']:+.2f}% e "
        f"{100 * v['seconda_meta']:+.2f}%; senza i 5 migliori {100 * v['senza_5_migliori']:+.2f}%.",
        "* Per anno: " + ", ".join(f"{a} {100 * x['media']:+.2f}% ({x['eventi']})" for a, x in v["per_anno"].items()) + ".",
        f"* Uscita di protezione nel {100 * e['fermate']:.0f}% degli eventi. Prima reazione (24 ore prima → entrata, contro il "
        f"Bitcoin): media {100 * e['reazione_media']:+.1f}%, mediana {100 * e['reazione_mediana']:+.1f}%.",
        "* Senza l'uscita di protezione: " + ", ".join(f"{n} {100 * x:+.2f}%" for n, x in e["altri_orizzonti"].items())
        + f". Eventi su monete con meno di {tr.ETA + tr.GIORNI} giorni di perpetuo (dentro N3): {e['sovrapposti_a_N3']}.",
        f"* Portafoglio (5% a operazione, al massimo 20): Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, "
        f"volatilità {100 * i['volatilita']:.1f}%, discesa {100 * i['discesa_max']:.1f}%; Sharpe corretto "
        f"{p['sharpe_corretto']:.2f} con {len(sr)} prove; esito del portafoglio: {p['esito']}.",
        "* Portafoglio per anno: " + ", ".join(f"{a} {100 * x:+.1f}%" for a, x in p["per_anno"].items()) + ".", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_QUARANTUNESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTUNESIMA FINITA", flush=True)
