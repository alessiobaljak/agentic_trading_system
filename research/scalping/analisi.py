"""Scalping sulla volatilita': cosa fa il prezzo dopo un'esplosione, e nei momenti agitati.

Regole in ``research/scalping/regole.md`` (commit 71576ba5, prima dello scarico e dei calcoli). Candele da 1 minuto
2020-2022 scaricate da ``scarica.py``. Scrive ``risultati.json``.

Uso: python3 -m research.scalping.analisi
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from research.src import dati
from research.src.controllo4 import MONETE_CONTROLLO

QUI = Path(__file__).resolve().parent
MONETE = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT")
INIZIO, FINE = date(2020, 1, 1), date(2022, 12, 31)
LIVELLI = (4, 8, 16)
ORIZZONTI = (1, 3, 5, 15, 30, 60)
PAUSA = 60
SEME = 2026
N_BOOT = 2000
TAKER, MAKER = 0.0005, 0.0002


def costi(simbolo: str) -> dict:
    """I costi di un giro in %, come in regole.md."""
    s = MONETE_CONTROLLO[simbolo]
    return {"mercato": 100 * 2 * (TAKER + s), "limite_mercato": 100 * (MAKER + TAKER + s),
            "limite_limite": 100 * 2 * MAKER}


def griglia(simbolo: str) -> pd.DataFrame:
    """Le candele da 1 minuto su una griglia di minuti senza buchi (i minuti mancanti restano vuoti)."""
    cc = dati.carica_candele(simbolo, "1m", INIZIO, FINE)
    df = pd.DataFrame({"ts": [c.ts for c in cc], "open": [c.open for c in cc], "high": [c.high for c in cc],
                       "low": [c.low for c in cc], "close": [c.close for c in cc]})
    del cc
    df["minuto"] = df["ts"] // 60_000
    df = df.drop_duplicates("minuto").set_index("minuto")
    tutto = np.arange(df.index.min(), df.index.max() + 1)
    return df.reindex(tutto)


def blocchi_giorno(valori: np.ndarray, giorni: np.ndarray, rng: np.random.Generator) -> dict:
    """Media e intervallo al 95% con bootstrap a blocchi di giorni."""
    ok = np.isfinite(valori)
    v, g = valori[ok], giorni[ok]
    if len(v) < 10:
        return {"n": int(len(v)), "media": float("nan"), "basso": float("nan"), "alto": float("nan")}
    unici, inv = np.unique(g, return_inverse=True)
    somme = np.bincount(inv, weights=v)
    conti = np.bincount(inv)
    medie = np.empty(N_BOOT)
    for b in range(N_BOOT):
        idx = rng.integers(0, len(unici), len(unici))
        medie[b] = somme[idx].sum() / conti[idx].sum()
    return {"n": int(len(v)), "giorni": int(len(unici)), "media": float(v.mean()),
            "basso": float(np.percentile(medie, 2.5)), "alto": float(np.percentile(medie, 97.5))}


def verdetto(ci: dict, costo: float) -> str:
    if not np.isfinite(ci["media"]):
        return "troppo pochi eventi"
    if ci["basso"] > costo:
        return "continua più del costo"
    if ci["alto"] < -costo:
        return "torna indietro più del costo"
    if ci["basso"] > 0:
        return "continua, ma non paga un giro"
    if ci["alto"] < 0:
        return "torna indietro, ma non paga un giro"
    return "nessuna direzione"


#: i movimenti di ogni evento, per livello e orizzonte, per mettere insieme le monete (giorni di calendario comuni:
#: gli eventi di monete diverse nello stesso giorno sono legati, e il bootstrap li ricampiona insieme)
GREZZI: dict = {}


def esplosioni(df: pd.DataFrame, simbolo: str, rng: np.random.Generator) -> dict:
    c = df["close"].to_numpy(float)
    o = df["open"].to_numpy(float)
    hi = df["high"].to_numpy(float)
    lo = df["low"].to_numpy(float)
    minuti = df.index.to_numpy()
    n = len(c)
    lc = np.log(c)
    r5 = lc - np.roll(lc, 5)
    r5[:5] = np.nan
    # una finestra di 5 minuti vale solo se i suoi 6 minuti ci sono tutti
    presenti = pd.Series(np.isfinite(c).astype(float)).rolling(6).sum().to_numpy()
    r5[presenti < 6] = np.nan
    metro = pd.Series(np.abs(r5)).rolling(1440, min_periods=1000).median().shift(1).to_numpy()
    giorno = minuti // 1440
    anno = pd.to_datetime(minuti * 60, unit="s").year.to_numpy()

    def avanti(t_idx: np.ndarray, segno: np.ndarray) -> dict:
        out = {}
        e = t_idx + 1
        valido = e < n
        entrata = np.where(valido, o[np.minimum(e, n - 1)], np.nan)
        for h in ORIZZONTI:
            j = t_idx + h
            fine = np.where(j < n, c[np.minimum(j, n - 1)], np.nan)
            out[f"h{h}"] = segno * (fine / entrata - 1) * 100
        mfe, mae = np.full(len(t_idx), np.nan), np.full(len(t_idx), np.nan)
        for k, t in enumerate(t_idx):
            if t + 15 >= n or not np.isfinite(entrata[k]):
                continue
            h15, l15 = hi[t + 1:t + 16], lo[t + 1:t + 16]
            if segno[k] > 0:
                mfe[k] = (np.nanmax(h15) / entrata[k] - 1) * 100
                mae[k] = (1 - np.nanmin(l15) / entrata[k]) * 100
            else:
                mfe[k] = (1 - np.nanmin(l15) / entrata[k]) * 100
                mae[k] = (np.nanmax(h15) / entrata[k] - 1) * 100
        out["mfe15"], out["mae15"] = mfe, mae
        return out

    ris = {"minuti": int(np.isfinite(c).sum()), "livelli": {}}
    eventi_4 = None
    cs = costi(simbolo)
    for m in LIVELLI:
        cand = np.flatnonzero(np.isfinite(r5) & np.isfinite(metro) & (metro > 0) & (np.abs(r5) > m * metro))
        scelti, ultimo = [], -10 ** 9
        for t in cand:
            if t - ultimo > PAUSA:
                scelti.append(t)
                ultimo = t
        t_idx = np.asarray(scelti, dtype=np.int64)
        if m == 4:
            eventi_4 = t_idx
        segno = np.sign(r5[t_idx])
        av = avanti(t_idx, segno)
        g = giorno[t_idx]
        liv = {"eventi": int(len(t_idx)), "per_anno": {int(a): int((anno[t_idx] == a).sum()) for a in (2020, 2021, 2022)},
               "orizzonti": {}}
        for h in ORIZZONTI:
            v = av[f"h{h}"]
            GREZZI.setdefault((m, h), []).append((v, g, np.full(len(v), cs["mercato"]), segno, anno[t_idx]))
            ci = blocchi_giorno(v, g, rng)
            liv["orizzonti"][h] = {
                **ci, "verdetto_mercato": verdetto(ci, cs["mercato"]),
                "verdetto_costi_doppi": verdetto(ci, 2 * cs["mercato"]),
                "quota_oltre_costo_mercato": float(np.nanmean(np.abs(v) > cs["mercato"])),
                "per_anno": {int(a): blocchi_giorno(v[anno[t_idx] == a], g[anno[t_idx] == a], rng)["media"]
                             for a in (2020, 2021, 2022)},
                "salita": blocchi_giorno(v[segno > 0], g[segno > 0], rng),
                "discesa": blocchi_giorno(v[segno < 0], g[segno < 0], rng)}
        liv["mfe15_mediana"] = float(np.nanmedian(av["mfe15"])) if len(t_idx) else float("nan")
        liv["mae15_mediana"] = float(np.nanmedian(av["mae15"])) if len(t_idx) else float("nan")
        ris["livelli"][m] = liv
    # il caso: minuti senza evento di livello 4 nei 60 minuti prima, tanti quanti gli eventi di livello 4, per anno
    vietati = np.zeros(n, dtype=bool)
    for t in (eventi_4 if eventi_4 is not None else []):
        vietati[t:min(n, t + PAUSA + 1)] = True
    caso_t, caso_s = [], []
    for a in (2020, 2021, 2022):
        quanti = int((anno[eventi_4] == a).sum()) if eventi_4 is not None else 0
        pool = np.flatnonzero((anno == a) & ~vietati & np.isfinite(c) & np.isfinite(metro))
        if quanti and len(pool):
            caso_t.append(rng.choice(pool, size=min(quanti, len(pool)), replace=False))
            caso_s.append(rng.choice([-1.0, 1.0], size=min(quanti, len(pool))))
    if caso_t:
        t_idx = np.sort(np.concatenate(caso_t))
        segno = np.concatenate(caso_s)
        av = avanti(t_idx, segno)
        ris["caso"] = {h: blocchi_giorno(av[f"h{h}"], giorno[t_idx], rng) for h in ORIZZONTI}
    return ris


def fondo(df: pd.DataFrame, simbolo: str, rng: np.random.Generator) -> dict:
    """Analisi B: ogni 5 minuti, il rendimento dei 5 dopo con il segno dei 5 prima, per decili di volatilita'."""
    c = df["close"].to_numpy(float)
    minuti = df.index.to_numpy()
    lr1 = np.diff(np.log(c), prepend=np.nan)
    vol60 = pd.Series(lr1).rolling(60, min_periods=55).std().to_numpy()
    # percentile della volatilita' fra le ore dei 30 giorni prima: si calcola sulle ore (fine di ogni ora)
    fine_ora = np.flatnonzero((minuti % 60) == 59)
    vo = pd.Series(vol60[fine_ora])
    pct = vo.rolling(720, min_periods=240).apply(lambda w: float(np.mean(w[:-1] < w[-1])), raw=True).to_numpy()
    pct_minuto = np.full(len(c), np.nan)
    pct_minuto[fine_ora] = pct
    pct_minuto = pd.Series(pct_minuto).ffill(limit=59).to_numpy()
    blocchi = np.arange(10, len(c) - 5, 5)
    prima = np.log(c[blocchi] / c[blocchi - 5])
    dopo = (c[blocchi + 5] / c[blocchi] - 1) * 100
    v = np.sign(prima) * dopo
    p = pct_minuto[blocchi]
    g = minuti[blocchi] // 1440
    cs = costi(simbolo)
    out = {}
    for d in range(10):
        sel = np.isfinite(p) & (p >= d / 10) & (p < (d + 1) / 10 + (1e-9 if d == 9 else 0)) & np.isfinite(v)
        ci = blocchi_giorno(v[sel], g[sel], rng)
        out[f"D{d + 1}"] = {**ci, "verdetto_mercato": verdetto(ci, cs["mercato"]),
                            "verdetto_limite_limite": verdetto(ci, cs["limite_limite"]),
                            "movimento_assoluto_medio": float(np.nanmean(np.abs(dopo[sel]))) if sel.any() else float("nan")}
    return out


def main() -> int:
    rng = np.random.default_rng(SEME)
    out = {"versioni": {"python": sys.version.split()[0], "numpy": np.__version__, "pandas": pd.__version__},
           "costi": {s: costi(s) for s in MONETE}, "monete": {}}
    for s in MONETE:
        df = griglia(s)
        out["monete"][s] = {"esplosioni": esplosioni(df, s, rng), "fondo": fondo(df, s, rng)}
        del df
        print(f"[scalping] {s} fatto", flush=True)
    # tutte le monete insieme: il movimento meno il costo a mercato della moneta, per la continuazione e per il
    # ritorno indietro (regole.md, «Come si legge»)
    insieme = {}
    for m in LIVELLI:
        insieme[m] = {}
        for h in ORIZZONTI:
            v = np.concatenate([x[0] for x in GREZZI[(m, h)]])
            g = np.concatenate([x[1] for x in GREZZI[(m, h)]])
            k = np.concatenate([x[2] for x in GREZZI[(m, h)]])
            cont = blocchi_giorno(v - k, g, rng)
            inv = blocchi_giorno(-v - k, g, rng)
            lordo = blocchi_giorno(v, g, rng)
            sg = np.concatenate([x[3] for x in GREZZI[(m, h)]])
            an = np.concatenate([x[4] for x in GREZZI[(m, h)]])
            per_direzione = {nome: {"movimento": blocchi_giorno(v[sel], g[sel], rng),
                                    "per_anno": {int(a): blocchi_giorno(v[sel & (an == a)], g[sel & (an == a)], rng)
                                                 for a in (2020, 2021, 2022)},
                                    "ritorno_dopo_costo": blocchi_giorno(-v[sel] - k[sel], g[sel], rng),
                                    "continuazione_dopo_costo": blocchi_giorno(v[sel] - k[sel], g[sel], rng)}
                             for nome, sel in (("salita", sg > 0), ("discesa", sg < 0))}
            insieme[m][h] = {"movimento": lordo, "continuazione_dopo_costo": cont, "ritorno_dopo_costo": inv,
                             "per_direzione": per_direzione,
                             "verdetto": ("continua più del costo" if cont["basso"] > 0 else
                                          "torna indietro più del costo" if inv["basso"] > 0 else
                                          "continua, ma non paga un giro" if lordo["basso"] > 0 else
                                          "torna indietro, ma non paga un giro" if lordo["alto"] < 0 else
                                          "nessuna direzione")}
    out["tutte_le_monete"] = insieme
    (QUI / "risultati.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float),
                                        encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
