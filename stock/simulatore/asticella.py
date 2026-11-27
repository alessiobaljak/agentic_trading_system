"""L'asticella: lo Sharpe corretto per i tentativi (Bailey e López de Prado, «The Deflated Sharpe Ratio»,
Journal of Portfolio Management 2014), come `research/programma6/ASTICELLA.md` per le crypto.

Gli Sharpe qui sono «per periodo» (per giorno), non annui: la formula è scritta così.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform

GAMMA = 0.5772156649015329  # costante di Eulero-Mascheroni


def sharpe(r: pd.Series) -> float:
    r = r.dropna()
    return float(r.mean() / r.std(ddof=1)) if len(r) > 1 and r.std(ddof=1) > 0 else float("nan")


def soglia_per_caso(n_gruppi: int, varianza: float) -> float:
    """Lo Sharpe atteso del migliore fra N prove senza vantaggio (sezione 3 del lavoro del 2014)."""
    if n_gruppi <= 1:
        return 0.0
    z = stats.norm.ppf
    return math.sqrt(varianza) * ((1 - GAMMA) * z(1 - 1 / n_gruppi) + GAMMA * z(1 - 1 / (n_gruppi * math.e)))


def sharpe_probabilistico(r: pd.Series, soglia: float) -> float:
    """La probabilità che lo Sharpe vero sia sopra `soglia`, tenendo conto della lunghezza, dell'asimmetria
    e delle code della serie (Bailey e López de Prado 2012, formula del PSR)."""
    r = r.dropna()
    t = len(r)
    sr = sharpe(r)
    g3 = float(stats.skew(r))
    g4 = float(stats.kurtosis(r, fisher=False))
    den = math.sqrt(max(1 - g3 * sr + (g4 - 1) / 4 * sr ** 2, 1e-12))
    return float(stats.norm.cdf((sr - soglia) * math.sqrt(t - 1) / den))


def gruppi(serie: dict[str, pd.Series], rho: float = 0.5) -> list[list[str]]:
    """Gruppi di prove simili: legame medio con la distanza √((1−ρ)/2), tagliato alla correlazione `rho`."""
    nomi = list(serie)
    if len(nomi) == 1:
        return [nomi]
    df = pd.DataFrame(serie)
    c = df.corr().fillna(0).to_numpy()
    d = np.sqrt(np.clip((1 - c) / 2, 0, None))
    np.fill_diagonal(d, 0)
    z = linkage(squareform(d, checks=False), method="average")
    etichette = fcluster(z, t=math.sqrt((1 - rho) / 2), criterion="distance")
    out: dict[int, list[str]] = {}
    for n, e in zip(nomi, etichette):
        out.setdefault(int(e), []).append(n)
    return list(out.values())


T_PERDENTI = -3.0   # le prove che perdono di sicuro (LEZIONI_DALLE_CRYPTO.md punto 2, research/programma6/ASTICELLA.md sezione 5)
SOGLIA = 0.80       # la soglia dell'esame dalla prova 54 (decisione del proprietario del 27 novembre 2026, METODO.md sezione 1)


def sharpe_corretto(candidata: pd.Series, tutte: dict[str, pd.Series], rho: float = 0.5) -> dict:
    """Lo Sharpe corretto della `candidata` (rendimenti giornalieri) dato il conto di `tutte` le prove.
    Con meno di 5 gruppi V = 1/T (regola della prova 1, `stock/prove/P001_ultima_mezzora.md`).

    Dal 27 novembre 2026 (`METODO.md`, sezione 1, e l'audit `AUDIT_2026-11-27.md`): un gruppo con il t dello Sharpe sotto −3 (Sharpe
    giornaliero della sua serie media × √giorni) conta nel numero dei gruppi ma non nella varianza V, come promettono
    `LEZIONI_DALLE_CRYPTO.md` e il metodo delle crypto; fino a qui il codice lo aveva dimenticato. «sharpe_corretto» è il valore
    dell'esame; «sharpe_corretto_tutti» è quello di prima (tutti i gruppi nella varianza) e si riporta accanto."""
    g = gruppi(tutte, rho)
    medie = [pd.DataFrame({k: tutte[k] for k in membri}).mean(axis=1) for membri in g]
    sr_gruppi = [sharpe(m) for m in medie]
    t_gruppi = [s * math.sqrt(int(m.dropna().shape[0])) for s, m in zip(sr_gruppi, medie)]
    t = int(candidata.dropna().shape[0])
    v_tutti = float(np.var(sr_gruppi, ddof=1)) if len(g) >= 5 else 1.0 / t
    nella_v = [s for s, tg in zip(sr_gruppi, t_gruppi) if not tg < T_PERDENTI]
    v = float(np.var(nella_v, ddof=1)) if len(nella_v) >= 5 else 1.0 / t
    s0, s0_tutti = soglia_per_caso(len(g), v), soglia_per_caso(len(g), v_tutti)
    return {"gruppi": len(g), "gruppi_perdenti": len(g) - len(nella_v), "varianza": v, "soglia_giornaliera": s0,
            "sharpe_corretto": sharpe_probabilistico(candidata, s0),
            "varianza_tutti": v_tutti, "sharpe_corretto_tutti": sharpe_probabilistico(candidata, s0_tutti),
            "t_sharpe": sharpe(candidata) * math.sqrt(t)}
