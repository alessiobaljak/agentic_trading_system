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
import time
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


# pesi del punteggio composito (somma 1). Ogni componente e' 0..1, quindi il
# punteggio finale e' leggibile come "quanto questo asset e' adatto, da 0 a 1".
WEIGHTS = {
    "momentum": 0.25,     # trend EMA + spinta RSI
    "social": 0.20,       # sentiment (LunarCrush), neutro quando manca
    "volume": 0.20,       # volume ATTUALE contro la sua media, non il volume assoluto
    "funding": 0.15,      # vicino a zero = neutro; estremo = costo di mantenimento
    "volatility": 0.10,   # ATR nella fascia utile: troppo poca non paga i costi
    "liquidity": 0.10,    # spread stimato dalla fascia di volume
}


def _norm(value: float, lo: float, hi: float) -> float:
    if hi <= lo:
        return 0.0
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


def _bell(value: float, best: float, width: float) -> float:
    """1.0 al valore ideale, decrescente allontanandosi. Serve per le grandezze in
    cui NON vale "piu' e' meglio": la volatilita' utile sta in una fascia, e il
    funding migliore e' quello vicino a zero."""
    if width <= 0:
        return 0.0
    return max(0.0, 1.0 - abs(value - best) / width)


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
        """Punteggio composito 0..1 con i sei fattori, tutti spiegabili.

        Ogni componente e' normalizzata in 0..1 cosi' il totale si legge come
        "quanto questo asset e' adatto", e il dettaglio dice PERCHE'. I componenti
        finiscono su Firebase a ogni scan: nel tempo si puo' verificare se il
        punteggio predice davvero l'esito, invece di darlo per scontato.
        """
        from bot.core.costs import liquidity_spread

        i = snap.ind(settings.ORCHESTRATOR_TIMEFRAME)
        comp: dict[str, float] = {}

        # 1) MOMENTUM: separazione delle EMA + spinta dell'RSI oltre il neutro.
        #    Due segnali dello stesso fenomeno, mediati: l'RSI da solo satura, le
        #    EMA da sole non distinguono un trend appena nato da uno maturo.
        ema_part = 0.0
        if i and i.ema_fast and i.ema_slow and snap.price:
            ema_part = _norm(abs(i.ema_fast - i.ema_slow) / snap.price, 0.0, 0.02)
        rsi_part = _norm(abs((i.rsi if i and i.rsi is not None else 50.0) - 50.0), 0.0, 25.0)
        comp["momentum"] = 0.6 * ema_part + 0.4 * rsi_part

        # 2) SOCIAL: neutro (0.5) quando il dato manca — senza chiave LunarCrush
        #    valeva 0.3, cioe' una PENALITA' silenziosa uguale per tutti.
        comp["social"] = (float(snap.sentiment_score)
                          if snap.sentiment_score is not None else 0.5)

        # 3) VOLUME DI QUALITA': volume corrente / sua media, non il volume assoluto.
        #    Il volume assoluto premia sempre le stesse major; il RAPPORTO dice se
        #    ORA sta succedendo qualcosa. >= 1.5x = attivita' inusuale.
        if i and i.volume and i.volume_sma:
            comp["volume"] = _norm(i.volume / i.volume_sma, 0.5, 2.0)
        else:
            comp["volume"] = _norm(snap.volume_24h or 0.0, 1e6, 5e8)

        # 4) FUNDING: qui "vicino a zero e' meglio". Un funding estremo e' un COSTO
        #    di mantenimento che erode ogni trade tenuto ore. E' l'opposto della
        #    versione precedente, che premiava gli estremi come opportunita': vale
        #    solo per funding_arbitrage, mentre questo punteggio serve a tutte.
        comp["funding"] = _bell(abs(snap.funding_rate or 0.0), 0.0, 0.0015)

        # 5) VOLATILITA' UTILE: una fascia, non "piu' e' meglio". Sotto, il
        #    movimento non paga i costi; sopra, gli stop saltano per rumore.
        atr_pct = (i.atr / snap.price) if (i and i.atr and snap.price) else 0.0
        comp["volatility"] = _bell(atr_pct, settings.ASSET_IDEAL_ATR_PCT,
                                   settings.ASSET_IDEAL_ATR_PCT * 2)

        # 6) LIQUIDITA': lo spread stimato dalla fascia di volume (stesso modello di
        #    costo del gate). Meno spread = piu' punteggio.
        comp["liquidity"] = 1.0 - _norm(liquidity_spread(snap.volume_24h), 0.0, 0.001)

        score = sum(WEIGHTS[k] * comp[k] for k in WEIGHTS)
        return score, comp

    @staticmethod
    def exclusions(snap: AssetSnapshot, recent_stops: int = 0) -> list[str]:
        """Motivi per NON valutare affatto questo asset, o lista vuota.

        Sono esclusioni STRUTTURALI: nessun punteggio, per quanto alto, le supera.
        Il chiamante decide se applicarle — sotto BACKTEST_PARITY restano inerti,
        perche' il gate non le modella e filtrare qui creerebbe una divergenza fra
        i trade validati e quelli eseguiti (la stessa classe di problema che ci ha
        gia' fatto perdere una settimana).

        Nota sul volume minimo: il default e' 0, cioe' DISATTIVATO. Questo sistema
        ha deliberatamente sostituito il filtro netto sul volume con il modello di
        costo (bot/core/costs.py), che allarga lo spread sulle coin sottili e lascia
        che sia il gate a bocciare chi non lo batte. Un pavimento a 100M
        escluderebbe quasi tutto l'universo validato.
        """
        from bot.core.costs import liquidity_spread

        out: list[str] = []
        vol = snap.volume_24h or 0.0
        if settings.ASSET_MIN_VOLUME_24H > 0 and vol < settings.ASSET_MIN_VOLUME_24H:
            out.append(f"volume 24h ${vol / 1e6:.1f}M sotto la soglia")
        if liquidity_spread(vol) > settings.ASSET_MAX_SPREAD:
            out.append("spread stimato oltre la soglia")
        fr = snap.funding_rate
        if fr is not None and not (settings.ASSET_FUNDING_MIN <= fr <= settings.ASSET_FUNDING_MAX):
            out.append(f"funding {fr * 100:+.3f}% fuori dalla fascia sostenibile")
        if recent_stops >= settings.ASSET_BLACKLIST_STOPS:
            out.append(f"{recent_stops} stop recenti: in quarantena")
        return out

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
        # BUDGET DI TEMPO. Con Binance lenta ogni simbolo puo' costare fino a ~20s
        # (timeout 10s piu' un retry): su un universo di oltre cento coin lo scan
        # diventa di ore, e per tutto quel tempo il loop non torna a gestire le
        # posizioni aperte. Cioe' la lentezza della rete si trasformerebbe in stop e
        # take-profit non sorvegliati — un problema molto peggiore di uno scan
        # incompleto. Scaduto il budget si tiene cio' che si e' raccolto.
        budget = float(getattr(settings, "SCAN_MAX_SECONDS", 0) or 0)
        deadline = (time.monotonic() + budget) if budget > 0 else None
        skipped_budget = 0
        # La liquidita' e' ora gestita dal MODELLO DI COSTO (bot/core/costs.py): il gate
        # valida ogni coppia coi suoi costi reali (spread piu' largo sulle sottili), quindi
        # si puo' tradare l'INTERO universo validato. Questo filtro resta solo come "sanity
        # floor" per escludere coin morte/delistate (fill impossibile). Uguale in paper e
        # reale -> parita'. Default basso (config); alzabile via env per i soldi veri.
        min_vol = settings.SCAN_MIN_VOLUME_24H
        skipped_illiquid = 0
        for idx, sym in enumerate(symbols):
            if deadline is not None and time.monotonic() >= deadline:
                skipped_budget = len(symbols) - idx
                break
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
        if skipped_budget:
            # DICHIARATO, mai silenzioso: uno scan troncato che non lo dice si
            # leggerebbe come "ho guardato tutto il mercato" quando non e' vero.
            print(f"[scanner] budget di {budget:.0f}s esaurito: {skipped_budget} coin "
                  f"NON valutate in questo giro (Binance lenta?), "
                  f"{len(results)} valutate")
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
