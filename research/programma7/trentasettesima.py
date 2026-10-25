"""Programma 7, trentasettesima prova (TRENTASETTESIMA.md): G24, i flussi giornalieri dell'ETF IBIT (quote in circolazione × NAV, dal
file storico pubblico di iShares) come segnale del Bitcoin per le 24 ore dopo; controlli con i flussi mescolati e con il Bitcoin tenuto.

Uso: python3 -m research.programma7.trentasettesima
"""
from __future__ import annotations

import datetime as dt
import json
import re
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentasettesima"
FILE = QUI.parent / "data" / "etf" / "ibit_historical.xml"
URL = ("https://www.blackrock.com/varnish-api/blk-one01-product-data/product-data/api/v1/get-fund-document?appType=PRODUCT_PAGE"
       "&appSubType=ISHARES&targetSite=us-ishares&locale=en_US&portfolioId=333011&component=fundDownload&userType=individual")
FINESTRA = 20
ORA_UTC = 2
TENUTA = 24
PROVE_A_EVENTI = 28
PERMUTAZIONI, SEME = 2000, 2026


def scarica() -> Path:
    if not FILE.exists():
        FILE.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0"})
        with urllib.request.urlopen(req, timeout=120) as r:
            FILE.write_bytes(r.read())
    return FILE


def storico() -> pd.DataFrame:
    """Il foglio «Historical» del file di iShares: data, NAV per quota, quote in circolazione (dal piu' vecchio)."""
    s = scarica().read_bytes().decode("utf-8", "replace")
    m = re.search(r'<ss:Worksheet ss:Name="Historical".*?</ss:Worksheet>', s, re.S)
    righe = []
    for r in re.findall(r"<ss:Row.*?</ss:Row>", m.group(0), re.S):
        celle = [re.sub(r"<[^>]+>", "", x) for x in re.findall(r"<ss:Data[^>]*>(.*?)</ss:Data>", r, re.S)]
        if len(celle) >= 4 and celle[0] != "As Of":
            try:
                data = dt.datetime.strptime(celle[0], "%b %d, %Y").date()
                righe.append({"data": data, "nav": float(celle[1]), "quote": float(celle[3])})
            except ValueError:
                continue
    df = pd.DataFrame(righe).drop_duplicates("data").sort_values("data").reset_index(drop=True)
    df["flusso"] = df["quote"].diff() * df["nav"]
    return df


def segnali(df: pd.DataFrame, finestra: int = FINESTRA) -> pd.DataFrame:
    """Per ogni giorno di borsa con almeno ``finestra`` flussi precedenti: +1, -1 o 0."""
    f = df["flusso"].to_numpy()
    seg = np.zeros(len(df), dtype=int)
    for k in range(len(df)):
        if k < finestra + 1 or not np.isfinite(f[k]):
            continue
        prima = f[k - finestra:k]
        prima = prima[np.isfinite(prima)]
        if len(prima) < finestra:
            continue
        med = float(np.median(prima))
        if f[k] > 0 and f[k] > med:
            seg[k] = 1
        elif f[k] < 0 and f[k] < med:
            seg[k] = -1
    out = df.copy()
    out["segnale"] = seg
    return out


def operazioni(df: pd.DataFrame, c: pd.DataFrame, costo: float, fine: dt.date) -> pd.DataFrame:
    righe = []
    for _, r in df.iterrows():
        g = r["data"] + dt.timedelta(days=1)
        if g > fine:
            continue
        h = int(dt.datetime(g.year, g.month, g.day, ORA_UTC, tzinfo=dt.timezone.utc).timestamp()) // 3600
        if h not in c.index or h + TENUTA not in c.index:
            continue
        r_btc = float(c.loc[h + TENUTA, "open"] / c.loc[h, "open"] - 1)
        righe.append({"data_flusso": str(r["data"]), "giorno": str(g), "segnale": int(r["segnale"]), "r_btc": r_btc,
                      "r": int(r["segnale"]) * r_btc - (2 * costo if r["segnale"] else 0.0)})
    return pd.DataFrame(righe)


def bootstrap(x: np.ndarray, n: int = 10000, seme: int = SEME) -> dict:
    rng = np.random.default_rng(seme)
    medie = rng.choice(x, size=(n, len(x)), replace=True).mean(axis=1)
    return {"eventi": int(len(x)), "media": float(x.mean()), "basso": float(np.quantile(medie, 0.025)), "alto": float(np.quantile(medie, 0.975)),
            "p": float((medie <= 0).mean())}


def esegui(log=print) -> dict:
    c = es.ore_di("BTCUSDT")
    costo = float(sc.costi_moneta(["BTCUSDT"])[0])
    fine = dt.date(2026, 10, 5)
    df = segnali(storico())
    log(f"[trentasettesima] {len(df)} giorni di borsa nel file, dal {df['data'].min()} al {df['data'].max()}")
    op_tutte = operazioni(df, c, costo, fine)
    op = op_tutte[op_tutte["segnale"] != 0].reset_index(drop=True)
    RIS.mkdir(exist_ok=True)
    op[["giorno", "segnale", "r"]].to_csv(RIS / "operazioni_G24.csv", index=False)      # senza i valori dei flussi (file iShares non ridistribuibile)
    b = bootstrap(op["r"].to_numpy())
    anno = op["giorno"].str[:4]
    meta1, meta2 = op[anno == "2024"], op[anno >= "2025"]
    # controllo (a): i flussi mescolati fra i giorni (il segnale ricalcolato con la stessa regola)
    rng = np.random.default_rng(SEME)
    medie_caso = []
    base = df.copy()
    for _ in range(PERMUTAZIONI):
        base["flusso"] = rng.permutation(df["flusso"].to_numpy())
        sg = segnali(base)
        m = sg.merge(op_tutte[["data_flusso", "r_btc"]], left_on=sg["data"].astype(str), right_on="data_flusso", how="inner")
        m = m[m["segnale"] != 0]
        if len(m):
            medie_caso.append(float((m["segnale"] * m["r_btc"] - 2 * costo).mean()))
    medie_caso = np.asarray(medie_caso)
    # controllo (b): il Bitcoin tenuto sempre negli stessi giorni
    tenuto = float(op["r_btc"].mean())
    out = {"operazioni": b, "long": {"n": int((op["segnale"] > 0).sum()), "media": float(op.loc[op["segnale"] > 0, "r"].mean())},
           "short": {"n": int((op["segnale"] < 0).sum()), "media": float(op.loc[op["segnale"] < 0, "r"].mean())},
           "vinte": float((op["r"] > 0).mean()), "prima_meta": float(meta1["r"].mean()) if len(meta1) else None,
           "seconda_meta": float(meta2["r"].mean()) if len(meta2) else None,
           "per_anno": {a: float(x["r"].mean()) for a, x in op.groupby(anno)},
           "giorni_con_segnale": int(len(op)), "giorni_di_borsa_valutati": int(len(op_tutte)),
           "controllo_mescolato": {"permutazioni": int(len(medie_caso)), "quota_almeno_come_veri": float((medie_caso >= b["media"]).mean()),
                                   "media": float(medie_caso.mean())},
           "bitcoin_tenuto_stessi_giorni": tenuto,
           "sharpe_giornaliero": float(op["r"].mean() / op["r"].std(ddof=1) * np.sqrt(365)) if op["r"].std(ddof=1) > 0 else None,
           "costo_per_lato": costo, "soglia_tutte": 0.01 / PROVE_A_EVENTI}
    valida = (b["p"] <= 0.01 and b["media"] > 0 and (out["prima_meta"] or 0) > 0 and (out["seconda_meta"] or 0) > 0 and b["media"] > tenuto)
    out["esito"] = ("VALIDA" if valida and b["p"] <= out["soglia_tutte"] else
                    "passa l'esame scritto ma non la soglia di tutte le prove a eventi" if valida else "non passa")
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None else f"{100 * v:+.2f}%"  # noqa: E731
    cm = out["controllo_mescolato"]
    righe = ["# Programma 7 — risultati della trentasettesima prova (G24: i flussi dell'ETF IBIT come segnale del giorno dopo)", "",
             "Regole in `TRENTASETTESIMA.md` (scritte prima). Perpetuo BTCUSDT a ore; flussi dal file storico pubblico di iShares (non ridistribuito).", "",
             f"* {out['giorni_di_borsa_valutati']} giorni di borsa valutati, **{b['eventi']} con segnale** (long {out['long']['n']}: {pc(out['long']['media'])}; "
             f"short {out['short']['n']}: {pc(out['short']['media'])}).",
             f"* **{pc(b['media'])} a operazione** (intervallo {pc(b['basso'])}; {pc(b['alto'])}, p {b['p']:.3f}), vinte {100 * out['vinte']:.0f}%; 2024 "
             f"{pc(out['prima_meta'])}, 2025-2026 {pc(out['seconda_meta'])}; Sharpe della serie {out['sharpe_giornaliero']:.2f}.",
             "* Per anno: " + ", ".join(f"{a} {pc(v)}" for a, v in out["per_anno"].items()) + ".",
             f"* Controlli: il Bitcoin tenuto negli stessi giorni {pc(tenuto)}; con i flussi mescolati ({cm['permutazioni']} permutazioni) la media è "
             f"{pc(cm['media'])} e nel {100 * cm['quota_almeno_come_veri']:.0f}% dei casi arriva almeno a quella vera.", "",
             f"**Esito: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {out['soglia_tutte']:.5f})."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_TRENTASETTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTASETTESIMA FINITA", flush=True)
