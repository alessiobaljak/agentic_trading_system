"""
Market Scanner & Asset Selector (Layer 2).

Ogni 4h scansiona le crypto più LIQUIDE (perpetual USDT ordinati per volume 24h,
fino a SCAN_MAX_SYMBOLS) e calcola per ogni asset un punteggio composito:
    score = w1*momentum_tecnico + w2*social_momentum + w3*volume + w4*|funding| + w5*volatilità

L'Asset Selector restituisce i 3-5 asset col setup migliore per le strategie
attualmente favorevoli (regime corrente).
"""
from __future__ import annotations

import os
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
        max_symbols: Optional[int] = None,
    ) -> None:
        self.price = price_agent or PriceAgent()
        self.sentiment = sentiment_agent or SentimentAgent()
        # quante crypto scansionare per ciclo, ORDINATE PER VOLUME (le più liquide).
        # Cap per non saturare i rate limit Binance; alzabile via env SCAN_MAX_SYMBOLS.
        self.max_symbols = max_symbols or int(os.getenv("SCAN_MAX_SYMBOLS", "100"))

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
            # le N crypto più liquide per VOLUME (non i primi N in ordine d'API)
            symbols = self.price.list_perpetual_symbols_by_volume()[: self.max_symbols]
        results: list[ScanResult] = []
        # La liquidita' e' ora gestita dal MODELLO DI COSTO (bot/core/costs.py): il gate
        # valida ogni coppia coi suoi costi reali (spread piu' largo sulle sottili), quindi
        # si puo' tradare l'INTERO universo validato. Questo filtro resta solo come "sanity
        # floor" per escludere coin morte/delistate (fill impossibile). Uguale in paper e
        # reale -> parita'. Default basso (config); alzabile via env per i soldi veri.
        min_vol = settings.SCAN_MIN_VOLUME_24H
        skipped_illiquid = 0
        for sym in symbols:
            snap = self.price.build_snapshot(sym)
            if snap is None:
                continue
            # filtro liquidità: scarta i listing illiquidi (volume 24h sotto soglia).
            # Tiene fuori la spazzatura appena quotata e accorcia lo scan.
            if min_vol > 0 and (snap.volume_24h or 0.0) < min_vol:
                skipped_illiquid += 1
                continue
            if fetch_sentiment:
                sent = self.sentiment.get_sentiment(sym)
                snap.sentiment_score = sent.get("sentiment_score")
                snap.social_volume = sent.get("social_volume")
            score, comp = self._score(snap)
            results.append(ScanResult(symbol=sym, score=score, components=comp, snapshot=snap))
        if skipped_illiquid:
            print(f"[scanner] {skipped_illiquid} coin scartate per liquidità "
                  f"(< {min_vol:,.0f} vol 24h), {len(results)} valutate")
        results.sort(key=lambda r: r.score, reverse=True)
        return results

    def select_assets(
        self, scan_results: list[ScanResult], regime: Regime, top_n: Optional[int] = None
    ) -> list[ScanResult]:
        """
        Restituisce l'universo di VALUTAZIONE: le migliori `top_n` crypto per
        punteggio, su cui l'orchestratore cercherà un segnale a ogni ciclo.
        NB: questo NON è il numero di posizioni aperte (cap = MAX_OPEN_POSITIONS):
        si valutano molte crypto, se ne aprono al massimo 5. Default = SELECT_UNIVERSE.
        """
        top_n = top_n or settings.SELECT_UNIVERSE
        for r in scan_results:
            r.snapshot.regime = regime
        return scan_results[:top_n]
