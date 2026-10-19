"""Programma 6: le finestre che avanzano, la scelta in ogni finestra, l'esame (METODO.md, sezioni 2-6).

1. ``trade_famiglia``: per ogni combinazione della famiglia e ogni moneta, tutti i trade su tutto il periodo (i segnali
   si calcolano una volta per valori, tempo e moneta).
2. ``avanza``: per ogni trimestre di prova dal 2021-01, la scelta sui 12 mesi prima (solo trade gia' chiusi), e i trade
   della combinazione scelta con ingresso nel trimestre.
3. ``esame``: netto, intervallo, anni, monete, costi doppi, rendimento del capitale con il rischio dell'1% a trade e il
   tetto di leva 5, Sharpe annuo; ``sharpe_corretto`` (Deflated Sharpe Ratio) e ``pbo`` (validazione combinatoria
   simmetrica).
"""
from __future__ import annotations

import itertools
import math
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy import stats

from research.programma5.strumenti import motore5 as m5
from research.programma6 import dati
from research.programma6 import motore as mo
from research.programma6.famiglie import FAMIGLIE, INGRESSI, TEMPI, combinazioni

RISCHIO, LEVA_MAX = 0.01, 5.0


def _minuto(a: int, m: int) -> int:
    return int(datetime(a, m, 1, tzinfo=timezone.utc).timestamp() // 60)


def trimestri(dal=(2021, 1), al=(2026, 10)) -> list:
    """Gli inizi dei trimestri di prova (in minuti) e la fine dell'ultimo (i dati finiscono a ottobre 2026)."""
    out = []
    a, m = dal
    while (a, m) <= al:
        out.append(_minuto(a, m))
        m += 3
        if m > 12:
            a, m = a + 1, m - 12
    return out


def trade_famiglia(famiglia: str, monete, log=print) -> tuple:
    """(combinazioni, DataFrame dei trade con la colonna ``k`` = indice della combinazione)."""
    funz, _, _ = FAMIGLIE[famiglia]
    combo = combinazioni(famiglia)
    parti = []
    for s in monete:
        for tf in TEMPI:
            b = dati.barre(s, tf)
            if b.empty or len(b) < 1000:
                continue
            a = mo.atr(b)
            cache = {}
            slip = m5.scarto(s)
            for k, cmb in enumerate(combo):
                if cmb["tf"] != tf:
                    continue
                chiave = tuple(sorted(cmb["segnali"].items()))
                if chiave not in cache:
                    cache[chiave] = funz(b, **cmb["segnali"])
                u, ing = cmb["uscita"], cmb["ingresso"]
                t = mo.simula(b, a, cache[chiave], u["stop_k"], u["tp_k"], u["trail_k"], u["max_barre"],
                              ing["limite_k"], ing["validita"], slip)
                if not len(t["R"]):
                    continue
                parti.append(pd.DataFrame({"k": k, "simbolo": s, "minuto": t["minuto_in"], "uscita": t["minuto_out"],
                                           "direzione": t["direzione"], "R": t["R"], "netto": t["netto"],
                                           "netto_doppio": t["netto_doppio"], "frazione_stop": t["frazione_stop"],
                                           "motivo": t["motivo"]}))
        log(f"[{famiglia}] {s}")
    tutti = pd.concat(parti, ignore_index=True) if parti else pd.DataFrame()
    if len(tutti):
        tutti = tutti[np.isfinite(tutti["R"])]
    return combo, tutti


def vicini(combo: list) -> list:
    """Per ogni combinazione, gli indici delle combinazioni a un passo in una sola dimensione della griglia."""
    def pos(c):
        f = c["famiglia"]
        griglia = FAMIGLIE[f][1]
        p = tuple(griglia[k].index(c["segnali"][k]) for k in griglia)
        return p + (c["iu"], TEMPI.index(c["tf"]), c["ii"])
    P = [pos(c) for c in combo]
    indice = {p: i for i, p in enumerate(P)}
    out = []
    for p in P:
        v = []
        for d in range(len(p)):
            for passo in (-1, 1):
                q = list(p)
                q[d] += passo
                if tuple(q) in indice:
                    v.append(indice[tuple(q)])
        out.append(v)
    return out


def scegli(tr: pd.DataFrame, combo: list, vic: list, da: int, a: int, min_trade: int = 100) -> int:
    """La combinazione scelta sulla finestra [da, a) con i trade chiusi prima di ``a`` (METODO.md, sezione 4); -1 se
    nessuna."""
    w = tr[(tr["minuto"] >= da) & (tr["uscita"] < a)]
    if w.empty:
        return -1
    g = w.groupby("k")
    n = g.size()
    media = g["R"].mean()
    per_moneta = w.groupby(["k", "simbolo"])["R"].agg(["size", "mean"])
    per_moneta = per_moneta[per_moneta["size"] >= 5]
    quota_pos = per_moneta.groupby(level=0)["mean"].apply(lambda x: (x > 0).mean())
    validi = {k for k in n.index if n[k] >= min_trade and quota_pos.get(k, 0.0) >= 0.5}
    migliore, punteggio = -1, 0.0
    for k in validi:
        vv = [media[k]] + [media[j] for j in vic[k] if j in media.index]
        s = float(np.mean(vv))
        if s > punteggio:
            migliore, punteggio = k, s
    return migliore


def avanza(tr: pd.DataFrame, combo: list, mesi_costruzione: int = 12) -> tuple:
    """(trade dei trimestri di prova, scelte)."""
    vic = vicini(combo)
    inizi = trimestri()
    fine = int(tr["uscita"].max()) + 1 if len(tr) else 0
    scelte, presi = [], []
    for i, inizio in enumerate(inizi):
        prossimo = inizi[i + 1] if i + 1 < len(inizi) else fine
        a, m = datetime.fromtimestamp(inizio * 60, tz=timezone.utc).year, datetime.fromtimestamp(inizio * 60, tz=timezone.utc).month
        da = _minuto(a - mesi_costruzione // 12, m)
        k = scegli(tr, combo, vic, da, inizio)
        scelte.append({"da": inizio, "combinazione": k})
        if k >= 0:
            presi.append(tr[(tr["k"] == k) & (tr["minuto"] >= inizio) & (tr["minuto"] < prossimo)])
    out = pd.concat(presi, ignore_index=True) if presi else pd.DataFrame()
    return out, scelte


def rendimento_capitale(t: pd.DataFrame, col: str = "netto") -> pd.Series:
    """Rendimento giornaliero del capitale (somma sui trade chiusi nel giorno; rischio 1% a trade, tetto di leva 5)."""
    leva = np.minimum(LEVA_MAX, RISCHIO / t["frazione_stop"].to_numpy())
    r = pd.Series(leva * t[col].to_numpy(), index=t["uscita"].to_numpy() // 1440)
    return r.groupby(level=0).sum()


def esame(t: pd.DataFrame, n_boot: int = 10000) -> dict:
    if t.empty:
        return {"trade": 0}
    m = t["minuto"].to_numpy()
    e = {"trade": int(len(t)), "R": m5.bootstrap_giorni(t["R"].to_numpy(), m, n_boot),
         "netto": m5.bootstrap_giorni(t["netto"].to_numpy(), m, n_boot),
         "netto_doppio": float(t["netto_doppio"].mean())}
    anni = pd.to_datetime(m * 60, unit="s").year
    e["per_anno"] = {int(a): {"trade": int((anni == a).sum()), "R": float(t["R"][anni == a].mean()),
                              "netto": float(t["netto"][anni == a].mean())} for a in sorted(set(anni))}
    e["per_moneta"] = {s: {"trade": int(len(g)), "R": float(g["R"].mean())} for s, g in t.groupby("simbolo")}
    giorni = rendimento_capitale(t)
    tutti = pd.Series(0.0, index=np.arange(giorni.index.min(), giorni.index.max() + 1))
    tutti.loc[giorni.index] = giorni.to_numpy()
    e["capitale"] = {"rendimento_totale": float(tutti.sum()), "rendimento_annuo": float(tutti.mean() * 365),
                     "sharpe_annuo": float(tutti.mean() / tutti.std() * math.sqrt(365)) if tutti.std() > 0 else 0.0,
                     "peggior_discesa": float((tutti.cumsum() - tutti.cumsum().cummax()).min()),
                     "giorni": int(len(tutti)), "asimmetria": float(stats.skew(tutti)),
                     "curtosi": float(stats.kurtosis(tutti, fisher=False))}
    giorni_d = rendimento_capitale(t, "netto_doppio")
    e["capitale"]["rendimento_totale_costi_doppi"] = float(giorni_d.sum())
    ultimo = _minuto(2025, 10)
    u = t[t["minuto"] >= ultimo]
    e["ultimo_anno"] = {"trade": int(len(u)), "R": float(u["R"].mean()) if len(u) else float("nan")}
    return e


def sharpe_corretto(sr_annuo: float, giorni: int, asimmetria: float, curtosi: float, sr_prove: list) -> float:
    """Deflated Sharpe Ratio (Bailey e Lopez de Prado 2014) con lo Sharpe giornaliero; ``sr_prove``: gli Sharpe annui
    di tutte le famiglie provate (per la varianza fra le prove e il loro numero)."""
    sr = sr_annuo / math.sqrt(365)
    N = max(2, len(sr_prove))
    var = float(np.var([x / math.sqrt(365) for x in sr_prove], ddof=1)) if len(sr_prove) > 1 else 0.0
    g = 0.5772156649
    sr0 = math.sqrt(var) * ((1 - g) * stats.norm.ppf(1 - 1 / N) + g * stats.norm.ppf(1 - 1 / (N * math.e)))
    den = math.sqrt(max(1e-12, 1 - asimmetria * sr + (curtosi - 1) / 4 * sr * sr))
    return float(stats.norm.cdf((sr - sr0) * math.sqrt(giorni - 1) / den))


def pbo(tr: pd.DataFrame, n_combo: int, blocchi: int = 16) -> float:
    """Probabilita' di sovra-adattamento (CSCV, Bailey et al. 2015) sulla matrice mesi × combinazioni (R medio a trade
    del mese per combinazione; mesi senza trade = 0)."""
    mese = (pd.to_datetime(tr["minuto"] * 60, unit="s").dt.year * 12 + pd.to_datetime(tr["minuto"] * 60, unit="s").dt.month)
    M = tr.assign(mese=mese.to_numpy()).groupby(["mese", "k"])["R"].sum().unstack(fill_value=0.0)
    M = M.reindex(columns=range(n_combo), fill_value=0.0).to_numpy()
    T = (len(M) // blocchi) * blocchi
    if T < blocchi:
        return float("nan")
    parti = np.array_split(M[-T:], blocchi)
    logit = []
    for scelta in itertools.combinations(range(blocchi), blocchi // 2):
        dentro = np.vstack([parti[i] for i in scelta]).sum(axis=0)
        fuori = np.vstack([parti[i] for i in range(blocchi) if i not in scelta]).sum(axis=0)
        best = int(np.argmax(dentro))
        rango = (stats.rankdata(fuori)[best]) / (len(fuori) + 1)
        logit.append(math.log(rango / (1 - rango)))
    return float(np.mean(np.array(logit) <= 0))
