"""Programma 6, quinta prova (QUINTA.md): lo short dopo il crollo della sola moneta (z4 ≤ −5 con il Bitcoin sopra −3),
12 ore, sulle 100 monete del programma 5, con le ore fatte dai minuti verificati (``research/data/p6``).

Uso: python3 -m research.programma6.quinta
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import dati as d6
from research.programma6 import quarta as qa
from research.programma6 import seconda as sc

QUI = Path(__file__).parent
RIS = QUI / "risultati_quinta"
BTC_MAX = -3.0


def ore_p6(simbolo: str) -> pd.DataFrame:
    b = d6.barre(simbolo, "1h")
    if b.empty:
        return b
    out = b[["open", "high", "low", "close"]].astype(float).copy()
    out.index = (b["minuto"].to_numpy() // 60).astype(np.int64)
    return out


def a_short(t: pd.DataFrame) -> pd.DataFrame:
    """Lo stesso trade della quarta prova, dal lato short: incassa il ribasso e il funding positivo."""
    if t.empty:
        return t
    costi = 2 * (qa.TAKER + qa.SCARTO)
    t = t.copy()
    t["lordo"] = -t["lordo"]
    t["funding"] = -t["funding"]
    t["netto"] = t["lordo"] - costi - t["funding"]
    t["netto_doppio"] = t["lordo"] - 2 * costi - t["funding"]
    return t


def una_moneta(s: str, mesi_ok: set, bz: pd.Series) -> tuple:
    b = ore_p6(s)
    if b.empty or len(b) < 600:
        return pd.DataFrame(), pd.DataFrame()
    fg = qa._funding(s)
    zz = qa.z4(b["close"])
    zb = bz.reindex(b.index.to_numpy()).to_numpy()
    mese = pd.to_datetime(b.index.to_numpy() * 3600, unit="s").to_period("M").astype(str).to_numpy()
    nel = np.isin(mese, list(mesi_ok)) & (b.index.to_numpy() * 3600 >= qa.INIZIO * 86400)
    ev = qa.sfoltisci((zz <= -qa.K) & np.isfinite(zb) & (zb > BTC_MAX) & nel, qa.PAUSA)
    t = a_short(qa.trade(b, ev, *fg))
    t["simbolo"] = s
    cs = a_short(qa.caso(b, t, *fg))
    if len(cs):
        cs["simbolo"] = s
    return t, cs


def esame(t: pd.DataFrame, cs: pd.DataFrame) -> dict:
    m = t["minuto"].to_numpy()
    e = {"trade": int(len(t)), "monete": int(t["simbolo"].nunique()),
         "netto": m5.bootstrap_giorni(t["netto"].to_numpy(), m, 10000),
         "lordo": float(t["lordo"].mean()), "funding_incassato": float(-t["funding"].mean()),
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
    e["giorni_distinti"] = int(len(g))
    e["quota_5_giorni_migliori"] = float(g.sort_values(ascending=False).head(5).sum() / g.sum()) if g.sum() > 0 else float("nan")
    r = pd.Series(0.1 * t["netto"].to_numpy(), index=(t["minuto"].to_numpy() + 60 * qa.H) // 1440).groupby(level=0).sum()
    tutti = pd.Series(0.0, index=np.arange(qa.INIZIO, int(r.index.max()) + 1))
    tutti.loc[r.index[r.index >= qa.INIZIO]] = r[r.index >= qa.INIZIO].to_numpy()
    e["capitale_10"] = sc.numeri(tutti)
    return e


def esito(e: dict) -> str:
    if e["trade"] < 100:
        return "meno di 100 trade"
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
    return "CONFERMATA"


def esegui(log=print) -> dict:
    p5 = qa.RADICE / "research" / "programma5"
    cento = json.loads((p5 / "universo_top100.json").read_text())["scelte"]
    pan = sc.pannello()
    um = qa.universo_mesi(pan, set())
    bz = qa.btc_z4()
    tt, cc = [], []
    for s in cento:
        if s == "BTCUSDT":
            continue
        mesi = {m for m, ss in um.items() if s in ss}
        t, cs = una_moneta(s, mesi, bz)
        if len(t):
            tt.append(t)
            cc.append(cs)
    t = pd.concat(tt, ignore_index=True).sort_values("minuto").reset_index(drop=True)
    cs = pd.concat(cc, ignore_index=True)
    RIS.mkdir(exist_ok=True)
    t.to_csv(RIS / "trade.csv.gz", index=False)
    cs.to_csv(RIS / "caso.csv.gz", index=False)
    e = esame(t, cs)
    e["esito"] = esito(e)
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    log(f"[quinta] {e['trade']} trade su {e['monete']} monete: {e['esito']}")
    return e


def rapporto() -> str:
    e = json.loads((RIS / "esame.json").read_text())
    n, d = e["netto"], e["differenza"]
    righe = ["# Programma 6 — risultati della quinta prova (short dopo il crollo della sola moneta)", "",
             "Regole in `QUINTA.md` (scritte prima): short all'apertura dell'ora dopo un crollo di 4 ore della moneta "
             "(z ≤ −5) con il Bitcoin sopra −3, uscita dopo 12 ore, pausa 12; costi 0,40% andata e ritorno; le 100 monete "
             "del programma 5, dal 2021-01-01.", "",
             f"* **Trade**: {e['trade']} su {e['monete']} monete, in {e['giorni_distinti']} giorni diversi.",
             f"* **Netto medio a trade**: {100 * n['media']:+.3f}% (intervallo {100 * n['basso']:+.3f}; {100 * n['alto']:+.3f}, "
             f"p {n['p']:.4f}); lordo {100 * e['lordo']:+.3f}%, funding incassato {100 * e['funding_incassato']:+.3f}%.",
             f"* **Il caso**: {100 * e['caso']:+.3f}% a trade; differenza {100 * d['media']:+.3f}% "
             f"(intervallo {100 * d['basso']:+.3f}; {100 * d['alto']:+.3f}).",
             f"* **A costi doppi**: {100 * e['netto_doppio']:+.3f}%. **Senza il giorno migliore**: "
             f"{100 * e['senza_giorno_migliore']:+.3f}%. Quota dei 5 giorni migliori: {100 * e['quota_5_giorni_migliori']:.0f}%.",
             f"* **Monete con almeno 5 trade**: {e['monete_5']['positive']} positive su {e['monete_5']['monete']}.",
             f"* **Ultimo anno** (dal 2025-10-01): {e['ultimo_anno']['trade']} trade, {100 * e['ultimo_anno']['netto']:+.3f}%.",
             f"* **Capitale** (10% a trade, per informazione): {100 * e['capitale_10']['annuo']:+.1f}% l'anno, Sharpe "
             f"{e['capitale_10']['sharpe']:.2f}, discesa massima {100 * e['capitale_10']['discesa_max']:.1f}%.", "",
             "| Anno | Trade | Netto a trade |", "|---|---|---|"]
    for a, v in e["per_anno"].items():
        righe.append(f"| {a} | {v['trade']} | {100 * v['netto']:+.3f}% |")
    righe += ["", f"**Esito: {e['esito']}**"]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_QUINTA.md").write_text(testo, encoding="utf-8")
    return testo


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print(rapporto())
    print("QUINTA FINITA", flush=True)
