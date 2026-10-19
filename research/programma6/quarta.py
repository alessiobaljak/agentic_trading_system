"""Programma 6, quarta prova (QUARTA.md): la regola congelata I-017c4 del programma 5 (long dopo un crollo di 4 ore,
z4 ≤ −5, 12 ore, pausa 12) sulle monete mai usate, con le candele da 1 ora, costi alti, il caso e l'esame.

Ore: l'ora ``t`` e' la candela che apre al minuto ``60·t``. Segnale alla chiusura di ``t``; ingresso all'apertura di
``t+1``; uscita alla chiusura di ``t+12``. Funding: i regolamenti con minuto in (ingresso, uscita].

Uso: python3 -m research.programma6.quarta
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import dati as d6
from research.programma6 import seconda as sc

RADICE = Path(__file__).resolve().parents[2]
DATI = RADICE / "research" / "data" / "p6h"
QUI = Path(__file__).parent
RIS = QUI / "risultati_quarta"
TAKER, SCARTO = 0.0005, 0.0015
W, K, H, PAUSA = 4, 5.0, 12, 12
VOLUME_MIN, STORIA_MIN = 1e7, 30
CASI = 20
INIZIO = sc.giorno(2021, 1, 1)


def ore(simbolo: str) -> pd.DataFrame:
    """Le candele da 1 ora su una griglia senza buchi (indice = ora dall'epoca; NaN dove manca la candela)."""
    file = sorted((DATI / simbolo / "ore").glob("*.zip"))
    if not file:
        return pd.DataFrame()
    df = pd.concat([m5._csv_da_zip(p, m5.KLINE) for p in file], ignore_index=True)
    df["ora"] = m5._ms(df["open_time"]) // 3_600_000
    df = df.drop_duplicates("ora", keep="last").set_index("ora").sort_index()
    df = df[["open", "high", "low", "close"]].astype(float)
    return df.reindex(np.arange(df.index.min(), df.index.max() + 1))


def z4(close: pd.Series) -> np.ndarray:
    """z del rendimento di 4 ore con la σ oraria delle 720 ore prima (almeno 500), presa 4 ore prima (I-017c4)."""
    lc = np.log(close)
    sigma = lc.diff().rolling(720, min_periods=500).std()
    return ((lc - lc.shift(W)) / (sigma.shift(W) * math.sqrt(W))).to_numpy()


def sfoltisci(cond: np.ndarray, pausa: int) -> np.ndarray:
    scelti, ultimo = [], -10 ** 12
    for t in np.flatnonzero(cond):
        if t - ultimo >= pausa:
            scelti.append(t)
            ultimo = t
    return np.asarray(scelti, dtype=np.int64)


def trade(b: pd.DataFrame, pos: np.ndarray, f_min: np.ndarray, f_tasso: np.ndarray) -> pd.DataFrame:
    """I trade long con segnale alla chiusura delle ore in ``pos`` (posizioni nella griglia); si saltano quelli senza
    l'apertura dell'ora dopo o la chiusura dell'ora t+12."""
    o, c = b["open"].to_numpy(), b["close"].to_numpy()
    ora0 = int(b.index[0])
    pos = pos[pos + H < len(b)]
    ing, usc = o[pos + 1], c[pos + H]
    ok = np.isfinite(ing) & np.isfinite(usc) & (ing > 0)
    pos, ing, usc = pos[ok], ing[ok], usc[ok]
    m_in = (pos + 1 + ora0) * 60
    m_out = (pos + H + 1 + ora0) * 60
    cum = np.concatenate([[0.0], np.cumsum(f_tasso)])
    fund = cum[np.searchsorted(f_min, m_out, "right")] - cum[np.searchsorted(f_min, m_in, "right")]
    lordo = usc / ing - 1
    costi = 2 * (TAKER + SCARTO)
    return pd.DataFrame({"ora": pos + ora0, "minuto": m_in, "lordo": lordo, "funding": fund,
                         "netto": lordo - costi - fund, "netto_doppio": lordo - 2 * costi - fund})


def caso(b: pd.DataFrame, t: pd.DataFrame, f_min, f_tasso, seme: int = 2026) -> pd.DataFrame:
    """Per ogni trade, ``CASI`` ingressi a un'ora presa a caso nello stesso mese, con la stessa tenuta e gli stessi costi."""
    if t.empty:
        return pd.DataFrame()
    rng = np.random.default_rng(seme)
    ora0 = int(b.index[0])
    ore_g = np.arange(len(b)) + ora0
    mese = pd.to_datetime(ore_g * 3600, unit="s").to_period("M").astype(str).to_numpy()
    o, c = b["open"].to_numpy(), b["close"].to_numpy()
    valide = np.zeros(len(b), bool)
    valide[: len(b) - H] = np.isfinite(o[1: len(b) - H + 1]) & np.isfinite(c[H:])
    per_mese = {m: np.flatnonzero(valide & (mese == m)) for m in np.unique(mese)}
    righe = []
    for k, ora in enumerate(t["ora"].to_numpy()):
        cand = per_mese.get(mese[ora - ora0], np.array([], int))
        if not len(cand):
            continue
        scelte = rng.choice(cand, CASI)
        r = trade(b, scelte, f_min, f_tasso)
        r["trade"] = k
        righe.append(r)
    return pd.concat(righe, ignore_index=True) if righe else pd.DataFrame()


def universo_mesi(pan: dict, tocc: set) -> dict:
    """Per ogni mese (AAAA-MM): le monete mai usate con mediana del volume dei 30 giorni prima ≥ 10 milioni e almeno 30
    giorni di candele (QUARTA.md, sezione 3)."""
    import warnings
    C, V = pan["close"], pan["quote_volume"]
    T = C.shape[0]
    ok = np.isfinite(C)
    primo = np.where(ok.any(0), ok.argmax(0), T)
    giorni = np.arange(T) + pan["t0"]
    mesi = pd.to_datetime(giorni * 86400, unit="s").to_period("M")
    out = {}
    for m in pd.unique(mesi):
        r0 = np.flatnonzero(mesi == m)[0]
        if r0 < 1:
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            med = np.nan_to_num(np.nanmedian(V[max(0, r0 - 30): r0], axis=0))
        sel = np.flatnonzero(ok[r0 - 1] & (r0 - primo >= STORIA_MIN) & (med >= VOLUME_MIN))
        out[str(m)] = {pan["simboli"][j] for j in sel if pan["simboli"][j] not in tocc}
    return out


def toccate() -> set:
    from research.programma5.strumenti.scarico import MONETE
    p5 = RADICE / "research" / "programma5"
    return (set(json.loads((p5 / "universo_top100.json").read_text())["scelte"])
            | set(json.loads((p5 / "universo_fase2.json").read_text())["scelte"]) | set(MONETE))


def btc_z4() -> pd.Series:
    """z4 del Bitcoin per ora (dalle ore della prima prova, fatte dai minuti verificati)."""
    b = d6.barre("BTCUSDT", "1h")
    s = pd.Series(b["close"].to_numpy(float), index=(b["minuto"].to_numpy() // 60))
    return pd.Series(z4(s), index=s.index)


def una_moneta(s: str, mesi_ok: set) -> tuple:
    b = ore(s)
    if b.empty or len(b) < 600:
        return pd.DataFrame(), pd.DataFrame()
    fg = _funding(s)
    zz = z4(b["close"])
    mese = pd.to_datetime(b.index.to_numpy() * 3600, unit="s").to_period("M").astype(str).to_numpy()
    nel = np.isin(mese, list(mesi_ok)) & (b.index.to_numpy() * 3600 >= INIZIO * 86400)
    ev = sfoltisci((zz <= -K) & nel, PAUSA)
    t = trade(b, ev, *fg)
    t["simbolo"] = s
    cs = caso(b, t, *fg)
    if len(cs):
        cs["simbolo"] = s
    return t, cs


def _funding(s: str) -> tuple:
    from research.src.dati import funding_da_zip
    righe = []
    for p in sorted((sc.DATI / s / "funding").glob("*.zip")):
        righe += funding_da_zip(p)
    if not righe:
        return np.array([], np.int64), np.array([])
    df = pd.DataFrame(righe, columns=["ts", "ore", "tasso"]).drop_duplicates("ts").sort_values("ts")
    return (df["ts"].to_numpy() // 60_000).astype(np.int64), df["tasso"].to_numpy(float)


def esame(t: pd.DataFrame, cs: pd.DataFrame, bz: pd.Series) -> dict:
    m = t["minuto"].to_numpy()
    e = {"trade": int(len(t)), "monete": int(t["simbolo"].nunique()),
         "netto": m5.bootstrap_giorni(t["netto"].to_numpy(), m, 10000),
         "lordo": float(t["lordo"].mean()), "funding": float(t["funding"].mean()),
         "netto_doppio": float(t["netto_doppio"].mean())}
    rif = cs.groupby(["simbolo", "trade"])["netto"].mean()
    tt = t.reset_index(drop=True).assign(trade=lambda x: x.groupby("simbolo").cumcount())
    caso_t = rif.reindex(pd.MultiIndex.from_arrays([tt["simbolo"], tt["trade"]])).to_numpy()
    diff = tt["netto"].to_numpy() - caso_t
    okd = np.isfinite(diff)
    e["caso"] = float(np.nanmean(caso_t))
    e["differenza"] = m5.bootstrap_giorni(diff[okd], m[okd], 10000)
    anni = pd.to_datetime(m * 60, unit="s").year
    e["per_anno"] = {int(a): {"trade": int((anni == a).sum()), "netto": float(t["netto"][anni == a].mean())}
                     for a in sorted(set(anni))}
    u = t[t["minuto"] >= sc.ULTIMO_ANNO * 1440]
    e["ultimo_anno"] = {"trade": int(len(u)), "netto": float(u["netto"].mean()) if len(u) else float("nan")}
    pm = t.groupby("simbolo")["netto"].agg(["size", "mean"])
    pm5 = pm[pm["size"] >= 5]
    e["monete_5"] = {"monete": int(len(pm5)), "positive": int((pm5["mean"] > 0).sum())}
    g = t.groupby(m // 1440)["netto"].sum()
    e["senza_giorno_migliore"] = float(t["netto"][(m // 1440) != g.idxmax()].mean())
    zb = bz.reindex(t["ora"].to_numpy()).to_numpy()
    propri = t[np.isfinite(zb) & (zb > -3)]
    e["crolli_propri"] = {"trade": int(len(propri)), "netto": float(propri["netto"].mean()) if len(propri) else float("nan"),
                          "intervallo": m5.bootstrap_giorni(propri["netto"].to_numpy(), propri["minuto"].to_numpy(), 10000)
                          if len(propri) >= 5 else {}}
    # capitale, per informazione: il 10% del capitale a trade, rendimento nel giorno d'uscita
    r = pd.Series(0.1 * t["netto"].to_numpy(), index=(t["minuto"].to_numpy() + 60 * H) // 1440).groupby(level=0).sum()
    tutti = pd.Series(0.0, index=np.arange(INIZIO, int(r.index.max()) + 1))
    tutti.loc[r.index[r.index >= INIZIO]] = r[r.index >= INIZIO].to_numpy()
    e["capitale_10"] = sc.numeri(tutti)
    return e


def esito(e: dict) -> str:
    n = e["netto"]
    if not (n["basso"] > 0 and n["p"] <= 0.01):
        return f"netto non sopra zero con p ≤ 0,01 (p {n['p']:.4f})"
    if not e["differenza"]["basso"] > 0:
        return "non supera il caso"
    anni = [a for a in e["per_anno"].values() if a["trade"] > 0]
    if sum(1 for a in anni if a["netto"] > 0) < 4:
        return "positiva in meno di 4 anni"
    if not e["ultimo_anno"]["netto"] > 0:
        return "non positiva nell'ultimo anno"
    if not e["netto_doppio"] > 0:
        return "non positiva a costi doppi"
    mm = e["monete_5"]
    if mm["positive"] < 0.55 * mm["monete"]:
        return "positiva su meno del 55% delle monete"
    if not e["senza_giorno_migliore"] > 0:
        return "non positiva senza il giorno migliore"
    if not e["crolli_propri"]["netto"] > 0:
        return "non positiva sui crolli propri"
    return "CONFERMATA"


def esegui(log=print) -> dict:
    pan = sc.pannello()
    um = universo_mesi(pan, toccate())
    per_moneta = {}
    for mese, ss in um.items():
        for s in ss:
            per_moneta.setdefault(s, set()).add(mese)
    tt, cc = [], []
    for s in sorted(per_moneta):
        if not (DATI / s / "ore").exists():
            log(f"[quarta] manca {s}")
            continue
        t, cs = una_moneta(s, per_moneta[s])
        if len(t):
            tt.append(t)
            cc.append(cs)
    t = pd.concat(tt, ignore_index=True).sort_values("minuto").reset_index(drop=True)
    cs = pd.concat(cc, ignore_index=True)
    RIS.mkdir(exist_ok=True)
    t.to_csv(RIS / "trade.csv.gz", index=False)
    cs.to_csv(RIS / "caso.csv.gz", index=False)
    e = esame(t, cs, btc_z4())
    e["esito"] = esito(e)
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    log(f"[quarta] {e['trade']} trade su {e['monete']} monete: {e['esito']}")
    return e


def rapporto() -> str:
    e = json.loads((RIS / "esame.json").read_text())
    n, d = e["netto"], e["differenza"]
    cp = e["crolli_propri"]
    righe = ["# Programma 6 — risultati della quarta prova (il rimbalzo dopo i crolli, monete mai usate)", "",
             "Regole in `QUARTA.md` (scritte prima). La regola congelata I-017c4 del programma 5: long all'apertura "
             "dell'ora dopo un crollo di 4 ore con z ≤ −5, uscita dopo 12 ore, pausa 12; costi 0,40% andata e ritorno.", "",
             f"* **Trade**: {e['trade']} su {e['monete']} monete, dal 2021-01-01.",
             f"* **Netto medio a trade**: {100 * n['media']:+.3f}% (intervallo {100 * n['basso']:+.3f}; {100 * n['alto']:+.3f}, "
             f"p {n['p']:.4f}); lordo {100 * e['lordo']:+.3f}%, funding {100 * e['funding']:+.3f}%.",
             f"* **Il caso**: {100 * e['caso']:+.3f}% a trade; differenza {100 * d['media']:+.3f}% "
             f"(intervallo {100 * d['basso']:+.3f}; {100 * d['alto']:+.3f}).",
             f"* **A costi doppi**: {100 * e['netto_doppio']:+.3f}%. **Senza il giorno migliore**: "
             f"{100 * e['senza_giorno_migliore']:+.3f}%.",
             f"* **Monete con almeno 5 trade**: {e['monete_5']['positive']} positive su {e['monete_5']['monete']}.",
             f"* **Crolli propri** (Bitcoin non in crollo): {cp['trade']} trade, {100 * cp['netto']:+.3f}%"
             + (f" (intervallo {100 * cp['intervallo']['basso']:+.3f}; {100 * cp['intervallo']['alto']:+.3f})" if cp.get("intervallo") else "")
             + ".",
             f"* **Ultimo anno** (dal 2025-10-01): {e['ultimo_anno']['trade']} trade, {100 * e['ultimo_anno']['netto']:+.3f}%.",
             f"* **Capitale** (10% a trade, per informazione): {100 * e['capitale_10']['annuo']:+.1f}% l'anno, Sharpe "
             f"{e['capitale_10']['sharpe']:.2f}, discesa massima {100 * e['capitale_10']['discesa_max']:.1f}%.", "",
             "| Anno | Trade | Netto a trade |", "|---|---|---|"]
    for a, v in e["per_anno"].items():
        righe.append(f"| {a} | {v['trade']} | {100 * v['netto']:+.3f}% |")
    righe += ["", f"**Esito: {e['esito']}**"]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_QUARTA.md").write_text(testo, encoding="utf-8")
    return testo


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print(rapporto())
    print("QUARTA FINITA", flush=True)
