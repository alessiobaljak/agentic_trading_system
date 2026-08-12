"""
Regime Detector — classifica il mercato ogni ora in:
  BULL_TRENDING / BEAR_TRENDING / SIDEWAYS / HIGH_UNCERTAINTY

Usa BTC come proxy del mercato (l'asset di riferimento) combinando:
  * direzione e separazione delle EMA 9/21 su 1h (trend)
  * pendenza/forza del trend (MACD histogram)
  * volatilità relativa (ATR/prezzo) per distinguere "high uncertainty"
  * coerenza con il Fear & Greed
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from bot.core.models import AssetSnapshot, Regime


@dataclass
class RegimeAssessment:
    """Lettura RICCA del regime: non solo l'etichetta, ma quanto e' netta.

    `detect()` continua a restituire la sola etichetta ed e' usata IDENTICA da
    backtest e live: cambiarla romperebbe la parita' gate<->paper. Questa e' una
    lettura aggiuntiva, per ora solo osservabilita' — vedi il commento su
    `confidence` per il motivo per cui non tocca ancora la size.
    """
    primary: Regime
    # 0..1: quanto il segnale e' netto. Alta = tutti gli indizi concordano; bassa =
    # siamo vicini a una soglia e domani l'etichetta potrebbe essere un'altra.
    confidence: float
    # secondo regime "sovrapposto" (es. trend con volatilita' alta): non sostituisce
    # il primario, lo qualifica
    secondary: Optional[Regime] = None
    supporting: list[str] = field(default_factory=list)
    conflicting: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "primary_regime": self.primary.value,
            "confidence": round(self.confidence, 3),
            "secondary_regime": self.secondary.value if self.secondary else None,
            "supporting_signals": self.supporting,
            "conflicting_signals": self.conflicting,
        }


class RegimeDetector:
    REF_SYMBOL = "BTCUSDT"
    HIGH_VOL_ATR_PCT = 0.025   # ATR/prezzo > 2.5% su 1h -> alta incertezza
    TREND_SEPARATION = 0.004   # |ema_fast-ema_slow|/prezzo > 0.4% -> trend chiaro

    def detect(self, btc: AssetSnapshot, fear_greed: Optional[int] = None) -> Regime:
        i = btc.ind("1h")
        if not i or None in (i.ema_fast, i.ema_slow, i.atr, i.close) or i.close == 0:
            return Regime.HIGH_UNCERTAINTY

        atr_pct = i.atr / i.close
        separation = abs(i.ema_fast - i.ema_slow) / i.close
        up = i.ema_fast > i.ema_slow
        momentum = i.macd_hist or 0.0

        # volatilità estrema -> incertezza, indipendentemente dalla direzione
        if atr_pct > self.HIGH_VOL_ATR_PCT:
            return Regime.HIGH_UNCERTAINTY

        # trend chiaro: EMA ben separate e momentum coerente
        if separation > self.TREND_SEPARATION:
            if up and momentum >= 0:
                return Regime.BULL_TRENDING
            if (not up) and momentum <= 0:
                return Regime.BEAR_TRENDING
            # EMA dicono una cosa, momentum un'altra -> incertezza
            return Regime.HIGH_UNCERTAINTY

        # EMA vicine, bassa volatilità -> mercato laterale
        # rifinitura col Fear & Greed: valori estremi suggeriscono incertezza
        if fear_greed is not None and (fear_greed <= 15 or fear_greed >= 85):
            return Regime.HIGH_UNCERTAINTY
        return Regime.SIDEWAYS

    # ------------------------------------------------------------------ #
    def detect_detailed(self, btc: AssetSnapshot,
                        fear_greed: Optional[int] = None) -> RegimeAssessment:
        """Stessa etichetta di `detect()`, piu' quanto e' netta e perche'.

        L'etichetta e' presa DA `detect()` e non ricalcolata: due implementazioni
        della stessa classificazione divergerebbero al primo ritocco di una soglia,
        e la dashboard mostrerebbe un regime diverso da quello che opera.

        La confidenza misura la DISTANZA dalle soglie di decisione, normalizzata:
        un ATR appena sopra il limite di volatilita' e un ATR doppio portano alla
        stessa etichetta, ma non sono la stessa cosa. Vicino alla soglia significa
        che una piccola variazione cambierebbe il regime, cioe' che l'etichetta
        vale poco.

        NON influenza ancora size ne' leva. Il prompt di upgrade propone di legarla
        al size_multiplier, ma sarebbe la stessa mossa che ci e' costata cara: agire
        su un numero mai verificato. Prima si misura se predice l'esito — come gia'
        si fa con la confidenza dei segnali in bot/learning/calibration.py — e solo
        dopo la si collega. Il valore viene registrato su ogni trade proprio per
        rendere quella misura possibile.
        """
        primary = self.detect(btc, fear_greed)
        i = btc.ind("1h")
        supporting: list[str] = []
        conflicting: list[str] = []

        if not i or None in (i.ema_fast, i.ema_slow, i.atr, i.close) or i.close == 0:
            return RegimeAssessment(primary, 0.0, None, [],
                                    ["dati 1h insufficienti per classificare"])

        atr_pct = i.atr / i.close
        separation = abs(i.ema_fast - i.ema_slow) / i.close
        up = i.ema_fast > i.ema_slow
        momentum = i.macd_hist or 0.0

        # quanto siamo LONTANI dalle due soglie che decidono l'etichetta, in
        # rapporto alla soglia stessa: 0 = esattamente sul confine, 1 = al doppio.
        def _dist(value: float, threshold: float) -> float:
            if threshold <= 0:
                return 0.0
            return max(0.0, min(1.0, abs(value - threshold) / threshold))

        vol_margin = _dist(atr_pct, self.HIGH_VOL_ATR_PCT)
        sep_margin = _dist(separation, self.TREND_SEPARATION)

        if primary is Regime.HIGH_UNCERTAINTY:
            confidence = vol_margin if atr_pct > self.HIGH_VOL_ATR_PCT else 0.35
            if atr_pct > self.HIGH_VOL_ATR_PCT:
                supporting.append(f"volatilita' 1h {atr_pct * 100:.2f}% sopra la "
                                  f"soglia {self.HIGH_VOL_ATR_PCT * 100:.1f}%")
            else:
                conflicting.append("etichetta di ripiego: EMA e momentum discordi")
        elif primary in (Regime.BULL_TRENDING, Regime.BEAR_TRENDING):
            # trend: conta quanto le EMA sono separate E quanto il momentum e' netto
            mom_norm = min(1.0, abs(momentum) / (i.atr or 1.0))
            confidence = 0.5 + 0.3 * sep_margin + 0.2 * mom_norm
            supporting.append(f"EMA 9/21 separate dello {separation * 100:.2f}% "
                              f"({'rialzo' if up else 'ribasso'})")
            if abs(momentum) > 0:
                supporting.append(f"MACD histogram {'positivo' if momentum > 0 else 'negativo'}")
            else:
                conflicting.append("momentum piatto: trend senza spinta")
            if atr_pct > self.HIGH_VOL_ATR_PCT * 0.8:
                secondary = Regime.HIGH_UNCERTAINTY
                conflicting.append(f"volatilita' {atr_pct * 100:.2f}% vicina alla soglia")
                return RegimeAssessment(primary, min(1.0, confidence), secondary,
                                        supporting, conflicting)
        else:   # SIDEWAYS
            # laterale e' tanto piu' credibile quanto le EMA sono VICINE: qui la
            # distanza dalla soglia gioca al contrario rispetto al trend
            confidence = 0.5 + 0.5 * (1.0 - min(1.0, separation / self.TREND_SEPARATION))
            supporting.append(f"EMA 9/21 vicine ({separation * 100:.2f}%)")
            supporting.append(f"volatilita' contenuta ({atr_pct * 100:.2f}%)")

        if fear_greed is not None:
            if 25 <= fear_greed <= 75:
                supporting.append(f"Fear&Greed neutro ({fear_greed})")
            else:
                conflicting.append(f"Fear&Greed estremo ({fear_greed})")
                confidence *= 0.9
        return RegimeAssessment(primary, max(0.0, min(1.0, confidence)),
                                None, supporting, conflicting)
