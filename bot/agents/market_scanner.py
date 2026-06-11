"""
Market Scanner & Asset Selector (Layer 2).

Ogni 4h scansiona TUTTO l'universo dei perpetual USDT su Binance e calcola per
ogni asset un punteggio composito:
    score = w1*momentum_tecnico + w2*social_momentum + w3*volume + w4*|funding| + w5*volatilità

L'Asset Selector restituisce i 3-5 asset col setup migliore per le strategie
attualmente favorevoli (regime corrente).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from bot.config import settings
from bot.core.models import AssetSnapshot, Regime
from bot.agents.price_agent import PriceAgent
from bot.agents.sentiment_agent import SentimentAgent


@dataclass
class ScanResult:
    symbol: str
    score: float
    components: dict[str, float]
    snapshot: AssetSnapshot


# pesi del punteggio composito (somma ~1)
WEIGHTS = {
    "momentum": 0.30,
    "social": 0.20,
    "volume": 0.20,
    "funding": 0.15,
    "volatility": 0.15,
}


def _norm(value: float, lo: float, hi: float) -> float:
    if hi <= lo:
        return 0.0
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


class MarketScanner:
    def __init__(
        self,
        price_agent: Optional[PriceAgent] = None,
        sentiment_agent: Optional[SentimentAgent] = None,
        max_symbols: int = 60,
    ) -> None:
        self.price = price_agent or PriceAgent()
        self.sentiment = sentiment_agent or SentimentAgent()
        # limita per non saturare i rate limit; i top liquidi sono scansionati comunque
        self.max_symbols = max_symbols

    def _score(self, snap: AssetSnapshot) -> tuple[float, dict[str, float]]:
        i = snap.ind("15m")
        comp: dict[str, float] = {}

        # momentum tecnico: distanza EMA + RSI deviation dal neutro
        momentum = 0.0
        if i and i.ema_fast and i.ema_slow and snap.price:
            sep = (i.ema_fast - i.ema_slow) / snap.price
            momentum = _norm(abs(sep), 0.0, 0.02)
        comp["momentum"] = momentum

        # social momentum
        comp["social"] = float(snap.sentiment_score) if snap.sentiment_score is not None else 0.3

        # volume 24h (log-normalizzato grossolanamente)
        vol = snap.volume_24h or 0.0
        comp["volume"] = _norm(vol, 1e6, 5e8)

        # funding estremo = opportunità
        fr = abs(snap.funding_rate or 0.0)
        comp["funding"] = _norm(fr, 0.0, 0.001)

        # volatilità (ATR/prezzo)
        atr_pct = 0.0
        if i and i.atr and snap.price:
            atr_pct = i.atr / snap.price
        comp["volatility"] = _norm(atr_pct, 0.0, 0.03)

        score = sum(WEIGHTS[k] * comp[k] for k in WEIGHTS)
        return score, comp

    def scan(self, symbols: Optional[list[str]] = None,
             fetch_sentiment: bool = False) -> list[ScanResult]:
        """
        Scansiona l'universo. Di default NON interroga la fonte sentiment per ogni
        simbolo (sarebbero decine di chiamate -> rate limit CoinGecko): il sentiment
        viene preso solo per i pochi asset selezionati, nel loop principale.
        """
        if symbols is None:
            symbols = self.price.list_perpetual_symbols()[: self.max_symbols]
        results: list[ScanResult] = []
        for sym in symbols:
            snap = self.price.build_snapshot(sym)
            if snap is None:
                continue
            if fetch_sentiment:
                sent = self.sentiment.get_sentiment(sym)
                snap.sentiment_score = sent.get("sentiment_score")
                snap.social_volume = sent.get("social_volume")
            score, comp = self._score(snap)
            results.append(ScanResult(symbol=sym, score=score, components=comp, snapshot=snap))
        results.sort(key=lambda r: r.score, reverse=True)
        return results

    def select_assets(
        self, scan_results: list[ScanResult], regime: Regime, top_n: Optional[int] = None
    ) -> list[ScanResult]:
        """
        Seleziona i migliori asset concentrando il capitale dove il segnale è forte.
        top_n default = MAX_OPEN_POSITIONS (3-5).
        """
        top_n = top_n or settings.MAX_OPEN_POSITIONS
        for r in scan_results:
            r.snapshot.regime = regime
        return scan_results[:top_n]
