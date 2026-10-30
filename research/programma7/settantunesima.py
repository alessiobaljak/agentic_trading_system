"""Programma 7, settantunesima prova (SETTANTUNESIMA.md): QO, il primo flusso di ogni quarto d'ora sui 6 perpetui grandi. Ogni 4 ore la
somma dello squilibrio degli acquisti aggressivi del primo minuto dei 32 quarti d'ora prima; long sopra zero e sopra la mediana dei 30
giorni, short sotto zero e sotto la mediana, per 4 ore; dal novembre 2024. Controllo: lo stesso con il settimo minuto.

Uso: python3 -m research.programma7.settantunesima
"""
from __future__ import annotations

import csv
import io
import json
import time
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import trentesima as tr
from research.programma6 import ventunesima as vu

QUI = Path(__file__).parent
RIS = QUI / "risultati_settantunesima"
DATI = QUI.parent / "data" / "quarti_d_ora"
MONETE = ("BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT")
URL = "https://data.binance.vision/data/futures/um/monthly/klines/{s}/1m/{s}-1m-{m}.zip"
DAL_DATI, DAL, AL = sc.giorno(2024, 10, 1), sc.giorno(2024, 11, 1), sc.giorno(2026, 10, 1)
PASSO, QUARTI, STORIA, SEME = 4, 32, 180, 2026
PROVE_A_EVENTI = 40


def mese(s: str, m: str) -> pd.DataFrame:
    """Di un mese a 1 minuto tiene solo il primo e il settimo minuto di ogni quarto d'ora (volume e acquisti aggressivi) e l'apertura
    di ogni ora; salvato in DATI, lo zip non resta su disco."""
    f = DATI / s / f"{m}.pkl"
    if f.exists():
        return pd.read_pickle(f)
    contenuto = None
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(URL.format(s=s, m=m), headers={"User-Agent": "ricerca/1.0"}), timeout=120) as r:
                contenuto = r.read()
            break
        except Exception:  # noqa: BLE001
            time.sleep(2 ** (k + 1))
    if contenuto is None:
        return pd.DataFrame()
    z = zipfile.ZipFile(io.BytesIO(contenuto))
    righe = []
    for x in csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]))):
        if not x or not x[0].isdigit():
            continue
        mm = int(x[0]) // 60000
        q = mm % 15
        if q in (0, 6) or mm % 60 == 0:
            righe.append((mm, float(x[1]), float(x[5]), float(x[9])))
    d = pd.DataFrame(righe, columns=["minuto", "open", "volume", "acquisti"]).drop_duplicates("minuto").set_index("minuto")
    f.parent.mkdir(parents=True, exist_ok=True)
    d.to_pickle(f)
    return d


def decisioni(d: pd.DataFrame, minuto_del_quarto: int) -> pd.DataFrame:
    """Per ogni decisione (ogni 4 ore) il segnale, la posizione e il rendimento delle 4, 8 e 12 ore dopo."""
    q = d[(d.index % 15) == minuto_del_quarto]
    imb = ((2 * q["acquisti"] - q["volume"]) / q["volume"]).where(q["volume"] > 0)
    inizio_q = (q.index // 15) * 15                       # il quarto d'ora a cui appartiene il minuto
    imb.index = inizio_q
    ore = d[(d.index % 60) == 0]["open"]
    ore.index = ore.index // 60
    h0, h1 = int(np.ceil(d.index.min() / 60 / PASSO) * PASSO), int(d.index.max() // 60)
    righe = []
    for h in range(h0 + 8, h1 - 12, PASSO):
        finestra = imb[(imb.index >= (h - 8) * 60) & (imb.index < h * 60)]
        s = float(finestra.sum()) if finestra.notna().sum() >= QUARTI - 2 else np.nan
        righe.append({"ora": h, "segnale": s, **{f"r{o}": float(ore.get(h + o, np.nan) / ore.get(h, np.nan) - 1) for o in (4, 8, 12)}})
    out = pd.DataFrame(righe).set_index("ora")
    med = out["segnale"].shift(1).rolling(STORIA, min_periods=STORIA).median()
    out["pos"] = np.where((out["segnale"] > 0) & (out["segnale"] > med), 1.0, np.where((out["segnale"] < 0) & (out["segnale"] < med), -1.0, 0.0))
    return out


def conto(out: pd.DataFrame, f: pd.Series) -> pd.DataFrame:
    o = out.copy()
    prima = o["pos"].shift(1).fillna(0.0)
    o["spesa"] = (o["pos"] - prima).abs() * vu.COSTO_BTC / 2
    fund = []
    for h, p in zip(o.index, o["pos"]):
        reg = [x for x in range(h + 1, h + PASSO + 1) if x % 8 == 0]
        fund.append(p * sum(f.get(x // 24, 0.0) for x in reg) / 3)
    o["funding"] = fund
    o["lordo"] = o["pos"] * o["r4"]
    o["netto"] = o["lordo"] - o["spesa"] - o["funding"]
    o["operazione"] = (o["pos"] != 0) | (prima != 0)
    return o


def esegui(log=print) -> dict:
    mesi = sorted({sc.data(g)[:7] for g in range(DAL_DATI, AL)})
    with ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(lambda x: mese(*x), [(s, m) for s in MONETE for m in mesi]))
    pan = sc.pannello()
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    tutte = {}
    for verso, minuto in (("primo", 0), ("settimo", 6)):
        parti = []
        for s in MONETE:
            d = pd.concat([mese(s, m) for m in mesi]).sort_index()
            f = pd.Series(np.nan_to_num(pan["funding"][:, pan["simboli"].index(s)]), index=giorni)
            o = conto(decisioni(d, minuto), f)
            o = o[(o.index // 24 >= DAL) & (o.index // 24 < AL)]
            o["moneta"] = s
            parti.append(o)
        tutte[verso] = pd.concat(parti)
    RIS.mkdir(exist_ok=True)
    out = {}
    for verso, o in tutte.items():
        ev = o[o["operazione"]].copy()
        g = (ev.index // 24).to_numpy()
        ev["data"] = [sc.data(int(x)) for x in g]
        ev["annuncio"] = ((g + 3) // 7).astype(int)
        ev = ev.reset_index()
        ev.to_csv(RIS / f"operazioni_{verso}.csv.gz", index=False)
        e = tr.esame(ev, "netto")
        out[verso] = {"esame": e, "operazioni": int(len(ev)), "lordo": float(ev["lordo"].mean()), "spese": float(ev["spesa"].mean()),
                      "per_moneta": {m: float(x["netto"].mean()) for m, x in ev.groupby("moneta")},
                      "tenute_lorde": {o_: float((ev["pos"] * ev[f"r{o_}"]).mean()) for o_ in (8, 12)},
                      "fuori": float((o["pos"] == 0).mean())}
    # la differenza fra primo e settimo minuto, per settimana
    sett = {v: o.assign(sett=((o.index // 24 + 3) // 7)).groupby("sett")["netto"].sum() for v, o in tutte.items()}
    dd = (sett["primo"] - sett["settimo"].reindex(sett["primo"].index).fillna(0)).to_numpy()
    b = np.random.default_rng(SEME).choice(dd, size=(10000, len(dd)), replace=True).mean(axis=1)
    diff = {"media_settimana": float(dd.mean()), "basso": float(np.quantile(b, 0.025)), "alto": float(np.quantile(b, 0.975)), "p": float((b <= 0).mean())}
    e = out["primo"]["esame"]
    soglia = 0.01 / PROVE_A_EVENTI
    valida = e["esito"] == "VALIDA" and diff["p"] <= 0.05
    esito = ("VALIDA" if valida and e["boot"]["p"] <= soglia else
             "passa l'esame scritto ma non la soglia di tutte le prove a eventi" if valida else
             e["esito"] if e["esito"] != "VALIDA" else "non sopra il controllo del settimo minuto")
    (RIS / "esame.json").write_text(json.dumps({**out, "differenza": diff, "esito": esito}, ensure_ascii=False, indent=1, default=str),
                                    encoding="utf-8")
    pc = lambda v: "—" if v is None or v != v else f"{100 * v:+.3f}%"  # noqa: E731
    p1, p7 = out["primo"], out["settimo"]
    bb = e["boot"]
    testo = "\n".join([
        "# Programma 7 — risultati della settantunesima prova (QO: il primo flusso di ogni quarto d'ora)", "",
        "Regole in `SETTANTUNESIMA.md` (scritte prima). BTC, ETH, XRP, SOL, DOGE e ADA, dal 1° novembre 2024 al 30 settembre 2026 (dopo "
        "lo studio di Kim e Hansen), una decisione ogni 4 ore, costi a mercato.", "",
        f"* **{bb['eventi']} operazioni: {pc(bb['media'])} a operazione** (intervallo {pc(bb['basso'])}; {pc(bb['alto'])}, p "
        f"{bb['p']:.4f}); prima dei costi {pc(p1['lordo'])}, spese {pc(p1['spese'])}; mediana {pc(e['mediana'])}, vinte "
        f"{100 * e['vinti']:.0f}%; metà {pc(e['prima_meta'])} e {pc(e['seconda_meta'])}; senza le 5 migliori {pc(e['senza_5_migliori'])}; "
        f"fuori nel {100 * p1['fuori']:.0f}% delle decisioni.",
        "* Per anno: " + ", ".join(f"{a} {pc(v['media'])} ({v['eventi']})" for a, v in e["per_anno"].items()) + ".",
        "* Per moneta: " + ", ".join(f"{m[:-4]} {pc(v)}" for m, v in p1["per_moneta"].items()) + ".",
        f"* **Controllo, il settimo minuto**: {p7['operazioni']} operazioni, {pc(p7['esame']['boot']['media'])} a operazione (prima dei "
        f"costi {pc(p7['lordo'])}); differenza per settimana {pc(diff['media_settimana'])} (intervallo {pc(diff['basso'])}; "
        f"{pc(diff['alto'])}, p {diff['p']:.3f}).",
        f"* Per capire: le tenute di 8 e 12 ore prima dei costi {pc(p1['tenute_lorde'][8])} e {pc(p1['tenute_lorde'][12])}.", "",
        f"**Esito: {esito}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {soglia:.5f})."]) + "\n"
    (QUI / "RISULTATI_SETTANTUNESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SETTANTUNESIMA FINITA", flush=True)
