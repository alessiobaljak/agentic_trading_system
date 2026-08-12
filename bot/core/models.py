"""
Modelli dati condivisi (Pydantic v2).

Sono il "contratto" comune tra agenti, strategie, orchestratore, risk manager,
execution e learning. Ogni modulo importa da qui per garantire coerenza.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# --------------------------------------------------------------------------- #
# Enums                                                                        #
# --------------------------------------------------------------------------- #
class Regime(str, Enum):
    """Classificazione del regime di mercato (aggiornata ogni ora)."""
    BULL_TRENDING = "bull_trending"
    BEAR_TRENDING = "bear_trending"
    SIDEWAYS = "sideways"
    HIGH_UNCERTAINTY = "high_uncertainty"


class Direction(str, Enum):
    LONG = "long"
    SHORT = "short"


class ExitReason(str, Enum):
    TAKE_PROFIT = "take_profit"
    STOP_LOSS = "stop_loss"
    TRAILING_STOP = "trailing_stop"
    SCALE_OUT = "scale_out"
    TIME_EXIT = "time_exit"
    MANUAL = "manual"
    KILL_SWITCH = "kill_switch"
    CIRCUIT_BREAKER = "circuit_breaker"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# --------------------------------------------------------------------------- #
# Market data                                                                  #
# --------------------------------------------------------------------------- #
class Candle(BaseModel):
    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: Optional[datetime] = None


class IndicatorSnapshot(BaseModel):
    """Valori di TUTTI gli indicatori per un asset a un dato istante/timeframe."""
    timeframe: str
    ema_fast: Optional[float] = None      # EMA 9
    ema_slow: Optional[float] = None      # EMA 21
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_mid: Optional[float] = None
    bb_lower: Optional[float] = None
    atr: Optional[float] = None
    vwap: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None
    volume_sma: Optional[float] = None
    adx: Optional[float] = None            # forza del trend (0-100)
    stoch_k: Optional[float] = None        # stocastico %K (0-100)
    stoch_d: Optional[float] = None        # stocastico %D (0-100)


class AssetSnapshot(BaseModel):
    """Stato completo di un asset usato da strategie e orchestratore."""
    symbol: str
    price: float
    mark_price: Optional[float] = None
    funding_rate: Optional[float] = None   # es. 0.0001 = 0.01%
    open_interest: Optional[float] = None
    volume_24h: Optional[float] = None
    # indicatori per timeframe: {"15m": IndicatorSnapshot, ...}
    indicators: dict[str, IndicatorSnapshot] = Field(default_factory=dict)
    # dati esterni
    sentiment_score: Optional[float] = None      # LunarCrush, normalizzato
    social_volume: Optional[float] = None
    fear_greed: Optional[int] = None             # 0-100
    regime: Optional[Regime] = None
    timestamp: datetime = Field(default_factory=_utcnow)

    def ind(self, timeframe: str) -> Optional[IndicatorSnapshot]:
        return self.indicators.get(timeframe)


# --------------------------------------------------------------------------- #
# Strategie / orchestratore                                                    #
# --------------------------------------------------------------------------- #
class StrategySignal(BaseModel):
    """Segnale grezzo emesso da una singola strategia."""
    strategy: str
    symbol: str
    direction: Direction
    confidence: float = Field(ge=0, le=100)   # 0-100
    reasoning: str = ""
    suggested_stop: Optional[float] = None     # prezzo SL suggerito
    suggested_target: Optional[float] = None   # prezzo TP suggerito
    regime: Optional[Regime] = None
    timestamp: datetime = Field(default_factory=_utcnow)


class OrchestratorDecision(BaseModel):
    """
    Output dell'orchestratore LLM, validato Pydantic.
    È ciò che viene passato al risk manager e poi all'execution.
    """
    asset: str
    strategy: str
    direction: Direction
    size_multiplier: float = Field(ge=0, le=1.0)  # frazione della size base
    confidence: float = Field(ge=0, le=100)
    reasoning: str = ""
    # confidenza aggiustata dai pesi del learning (riempita dall'adaptation layer)
    adjusted_confidence: Optional[float] = None
    # SL/TP suggeriti DALLA STRATEGIA (gli stessi del backtest GATE 1). Se presenti,
    # il risk manager li usa invece di ricalcolarli coi default fissi 1.5ATR/2.0RR,
    # così il paper replica esattamente lo stop/target validato out-of-sample.
    suggested_stop: Optional[float] = None
    suggested_target: Optional[float] = None
    timestamp: datetime = Field(default_factory=_utcnow)

    @field_validator("size_multiplier")
    @classmethod
    def _clamp_mult(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


# --------------------------------------------------------------------------- #
# Risk                                                                         #
# --------------------------------------------------------------------------- #
class RiskSettings(BaseModel):
    """
    Parametri REGOLABILI dall'utente, letti da Firebase `user_risk_settings`.
    NB: questi sono le *richieste* dell'utente, non i valori effettivi.
    Gli hard cap vengono applicati dopo, nel risk manager.
    """
    leverage: float = 2.0
    risk_per_trade: float = 0.01   # frazione (0.01 = 1%)
    updated_at: datetime = Field(default_factory=_utcnow)
    updated_by: str = "default"


class EffectiveRiskParams(BaseModel):
    """Risultato della logica di precedenza: i valori realmente applicati."""
    leverage: float
    risk_per_trade: float           # rischio RICHIESTO (impostazione utente x alloc)
    # rischio EFFETTIVO: quanto si perde davvero allo stop, in frazione dell'equity.
    # Diverge da `risk_per_trade` quando il cap per-posizione limita il nozionale, ed
    # e' il caso normale: e' l'unico numero che dice quanto si sta rischiando davvero.
    risk_effective_pct: float = 0.0
    capped_by_position_limit: bool = False
    notional: float                 # valore nozionale della posizione
    quantity: float                 # quantità nell'asset
    stop_price: float
    take_profit_price: float
    # tracciabilità della decisione (cosa ha clampato cosa)
    user_leverage: float
    user_risk_per_trade: float
    safety_leverage_cap: float
    safety_risk_cap: float
    notes: list[str] = Field(default_factory=list)
    approved: bool = True
    reject_reason: Optional[str] = None


# --------------------------------------------------------------------------- #
# Trade logging                                                                #
# --------------------------------------------------------------------------- #
class ClosedTrade(BaseModel):
    """
    Record completo di un trade CHIUSO, salvato su Firestore `trades`.
    Contiene TUTTO ciò che serve al learning loop per segmentare la performance.
    """
    trade_id: str
    symbol: str
    strategy: str
    direction: Direction
    # timeframe del sistema quando il trade e' stato aperto: il learning pesa SOLO
    # i trade del timeframe corrente (l'esperienza a 1h non descrive il 15m).
    # "" = trade storico precedente all'introduzione del campo (escluso dai pesi).
    timeframe: str = ""

    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float

    size: float                     # quantità
    notional: float
    leverage: float
    pnl: float                      # PnL in USDT (netto fee/slippage stimato)
    pnl_pct: float                  # PnL % sul capitale a rischio
    slippage: float = 0.0
    exit_reason: ExitReason

    # livelli CONFIGURATI all'apertura (stop base e take-profit ORIGINALI, non lo
    # stop alzato dal profit-lock). Servono al controfattuale sul trailing stop:
    # dopo un'uscita trailing, il prezzo avrebbe poi raggiunto questo TP? Se sì il
    # trailing ha tagliato un vincitore; se no ha protetto un'inversione.
    take_profit_price: Optional[float] = None
    stop_price: Optional[float] = None

    # scale-out: quanti TP scaglionati sono stati raggiunti prima della chiusura
    # (0 = nessuno, es. uscito allo SL prima del TP1) e il PnL netto gia' incassato
    # dalle fette. Servono a capire se/quanto lo scale-out ha lavorato sul trade.
    scale_stage_reached: int = 0
    realized_partial: float = 0.0
    # massima escursione FAVOREVOLE raggiunta, in unita' di R: dice quanto lontano e'
    # arrivato il prezzo prima di tornare. Da questo unico numero si sa quali gradini
    # avrebbe colpito QUALUNQUE scala di TP -> rende decidibile la taratura, senza
    # dover provare scale diverse ne' sacrificare trade per esplorare.
    mfe_r: float = 0.0

    # contesto all'ENTRATA (fondamentale per il learning)
    regime_at_entry: Regime
    indicators_at_entry: dict[str, IndicatorSnapshot] = Field(default_factory=dict)
    sentiment_at_entry: Optional[float] = None
    fear_greed_at_entry: Optional[int] = None
    funding_at_entry: Optional[float] = None
    confidence_at_entry: Optional[float] = None
    # quanto era NETTA la classificazione di regime all'ingresso (0..1). Registrato
    # per poter misurare se predice l'esito: solo dopo quella verifica ha senso
    # legarlo a size o leva. Vedi RegimeDetector.detect_detailed.
    regime_confidence_at_entry: Optional[float] = None

    @property
    def duration_seconds(self) -> float:
        return (self.exit_time - self.entry_time).total_seconds()

    @property
    def hour_bucket(self) -> int:
        """Fascia oraria d'entrata (UTC) per la segmentazione."""
        return self.entry_time.astimezone(timezone.utc).hour

    @property
    def is_win(self) -> bool:
        return self.pnl > 0


# --------------------------------------------------------------------------- #
# Learning / memoria                                                           #
# --------------------------------------------------------------------------- #
class StrategyRegimeWeight(BaseModel):
    """Peso dinamico di una strategia in uno specifico regime."""
    strategy: str
    regime: Regime
    weight: float = Field(ge=0.0, le=1.0, default=1.0)
    win_rate: Optional[float] = None
    avg_rr: Optional[float] = None
    sample_size: int = 0


class MemoryReport(BaseModel):
    """
    Report generato dal learning loop notturno e dato in pasto all'orchestratore.
    """
    generated_at: datetime = Field(default_factory=_utcnow)
    lookback_days: int = 30
    total_trades: int = 0
    overall_win_rate: float = 0.0
    # metriche segmentate
    win_rate_by_strategy: dict[str, float] = Field(default_factory=dict)
    win_rate_by_strategy_regime: dict[str, float] = Field(default_factory=dict)  # "strat|regime"
    avg_rr_by_strategy: dict[str, float] = Field(default_factory=dict)
    pnl_by_asset: dict[str, float] = Field(default_factory=dict)
    win_rate_by_hour: dict[str, float] = Field(default_factory=dict)
    # condizioni dei peggiori drawdown (insight testuali)
    worst_drawdown_conditions: list[str] = Field(default_factory=list)
    # correlazione confidenza dichiarata <-> esito reale (Pearson, -1..1)
    confidence_outcome_correlation: Optional[float] = None
    # pesi calcolati per strategia x regime
    weights: list[StrategyRegimeWeight] = Field(default_factory=list)
    # commento testuale dell'orchestratore (auto-analisi)
    narrative: str = ""
