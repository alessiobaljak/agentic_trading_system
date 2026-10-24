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


def sharpe_corretto(candidata: pd.Series, tutte: dict[str, pd.Series], rho: float = 0.5) -> dict:
    """Lo Sharpe corretto della `candidata` (rendimenti giornalieri) dato il conto di `tutte` le prove.
    Con meno di 5 gruppi V = 1/T (regola della prova 1, `stock/prove/P001_ultima_mezzora.md`)."""
    g = gruppi(tutte, rho)
    sr_gruppi = [sharpe(pd.DataFrame({k: tutte[k] for k in membri}).mean(axis=1)) for membri in g]
    t = int(candidata.dropna().shape[0])
    v = float(np.var(sr_gruppi, ddof=1)) if len(g) >= 5 else 1.0 / t
    s0 = soglia_per_caso(len(g), v)
    return {"gruppi": len(g), "varianza": v, "soglia_giornaliera": s0,
            "sharpe_corretto": sharpe_probabilistico(candidata, s0),
            "t_sharpe": sharpe(candidata) * math.sqrt(t)}
