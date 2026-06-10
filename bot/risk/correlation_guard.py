"""
Correlation Guard — limita il numero di posizioni fortemente correlate.

Calcola la correlazione rolling 24h tra i rendimenti degli asset con posizione
aperta e blocca l'apertura se si supererebbe il massimo di posizioni correlate
oltre soglia (config: CORRELATION_THRESHOLD=0.85, MAX_CORRELATED_POSITIONS=3).
"""
from __future__ import annotations

import numpy as np

from bot.config import settings


class CorrelationGuard:
    def __init__(
        self,
        threshold: float = settings.CORRELATION_THRESHOLD,
        max_correlated: int = settings.MAX_CORRELATED_POSITIONS,
    ) -> None:
        self.threshold = threshold
        self.max_correlated = max_correlated

    @staticmethod
    def _returns(prices: list[float]) -> np.ndarray:
        arr = np.asarray(prices, dtype=float)
        if arr.size < 3:
            return np.array([])
        return np.diff(arr) / arr[:-1]

    def correlation(self, prices_a: list[float], prices_b: list[float]) -> float:
        ra, rb = self._returns(prices_a), self._returns(prices_b)
        n = min(ra.size, rb.size)
        if n < 3:
            return 0.0
        ra, rb = ra[-n:], rb[-n:]
        if ra.std() == 0 or rb.std() == 0:
            return 0.0
        return float(np.corrcoef(ra, rb)[0, 1])

    def can_open(
        self,
        candidate: str,
        candidate_prices: list[float],
        open_positions: dict[str, list[float]],
    ) -> tuple[bool, str]:
        """
        Ritorna (ok, motivo). `open_positions` = {symbol: serie prezzi 24h}.
        Blocca se aprendo la candidata si avrebbero > max_correlated posizioni
        con correlazione > soglia rispetto ad essa.
        """
        correlated = 0
        details = []
        for sym, prices in open_positions.items():
            if sym == candidate:
                continue
            corr = abs(self.correlation(candidate_prices, prices))
            if corr > self.threshold:
                correlated += 1
                details.append(f"{sym}={corr:.2f}")
        # +1 includerebbe la candidata stessa nel cluster
        if correlated + 1 > self.max_correlated:
            return False, (f"Troppe posizioni correlate >{self.threshold} "
                           f"({', '.join(details)})")
        return True, "ok"
