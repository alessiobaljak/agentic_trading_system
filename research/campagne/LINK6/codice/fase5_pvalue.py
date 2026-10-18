"""Fase 5: i p-value delle varianti provate confrontati con quelli del caso (distribuzione uniforme).

Uso: python3 research/campagne/LINK6/codice/fase5_pvalue.py

Legge solo le voci `risultato` del log: nessun calcolo nuovo sui prezzi. Se fra le varianti ci fosse un vantaggio
vero, i p-value sarebbero spostati verso lo zero; senza vantaggio sarebbero circa uniformi fra 0 e 1.
"""
import sys
from pathlib import Path

from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402

p = [v["metriche"]["p_value"] for v in comune.voci()
     if v.get("tipo") == "risultato" and str(v.get("id", "")).startswith("V-")]
n = len(p)
ks = stats.kstest(p, "uniform")
sotto_010 = sum(1 for x in p if x < 0.10)
sotto_0023 = sum(1 for x in p if x <= 0.023)
print(f"varianti con p-value: {n}")
print(f"p-value medio: {sum(p) / n:.3f} (atteso senza vantaggio: 0,500)")
print(f"sotto 0,10: {sotto_010} (attesi per caso {0.10 * n:.1f}); "
      f"probabilita' di almeno {sotto_010} per caso: {stats.binom.sf(sotto_010 - 1, n, 0.10):.3f}")
print(f"0,023 o meno: {sotto_0023} (attesi per caso {0.023 * n:.2f}); "
      f"probabilita' di almeno {sotto_0023} per caso: {stats.binom.sf(sotto_0023 - 1, n, 0.023):.3f}")
print(f"test di Kolmogorov-Smirnov contro l'uniforme: statistica {ks.statistic:.3f}, p {ks.pvalue:.3f}")
