/**
 * Shared types mirroring the Firebase schema contract.
 * Keep these in sync with the bot's writers (Firestore + Realtime Database).
 */

// ---- Firestore ----

export interface RiskSettings {
  leverage: number;
  risk_per_trade: number; // fraction, e.g. 0.01 = 1%
  updated_at?: unknown;
  updated_by?: string;
}

export interface StrategyWeight {
  strategy: string;
  regime: string;
  weight: number; // 0..1
  win_rate?: number;
  avg_rr?: number;
  sample_size?: number;
}

export interface StrategyWeightsDoc {
  weights: StrategyWeight[];
}

export interface MemoryReport {
  generated_at?: unknown;
  lookback_days?: number;
  total_trades?: number;
  overall_win_rate?: number;
  win_rate_by_strategy?: Record<string, number>;
  // keys are "strategy|regime"
  win_rate_by_strategy_regime?: Record<string, number>;
  avg_rr_by_strategy?: Record<string, number>;
  pnl_by_asset?: Record<string, number>;
  narrative?: string;
}

export interface Insight {
  week_id: string;
  narrative: string;
  overall_win_rate?: number;
  total_trades?: number;
  created_at?: unknown;
}

export interface ClosedTrade {
  trade_id: string;
  symbol: string;
  strategy: string;
  direction: string;
  entry_price: number;
  exit_price: number;
  pnl: number;
  pnl_pct?: number;
  exit_reason?: string;
  exit_ts?: unknown;
  regime_at_entry?: string;
  is_win?: boolean;
  sentiment_at_entry?: number; // [0..1] al momento dell'ingresso
  fear_greed_at_entry?: number; // 0-100 al momento dell'ingresso
}

// ---- Realtime Database ----

export interface BotStatus {
  state?: string;
  regime?: string;
  dry_run?: boolean;
  updated_at?: number | string;
  heartbeat?: number | string;
  // Optional: the bot may publish the effective (post-safety) risk values.
  effective_leverage?: number;
  effective_risk_per_trade?: number;
  // Fear & Greed corrente (0-100), pubblicato per la vista Sentiment.
  fear_greed?: number;
}

export interface RiskState {
  effective_leverage?: number;
  effective_risk_per_trade?: number;
  reason?: string;
  updated_at?: number | string;
}

export interface Position {
  symbol: string;
  strategy?: string;
  direction?: string;
  entry_price?: number;
  mark_price?: number;
  quantity?: number;
  leverage?: number;
  unrealized_pnl?: number;
  stop_price?: number;
  take_profit_price?: number;
  trailing_active?: boolean;
  scaled_out?: boolean;
  dry_run?: boolean;
  updated_at?: number | string;
  accrued_funding?: number; // funding maturato finora (USDT), gia' scalato dall'uPnL
  held_hours?: number;      // ore da cui la posizione e' aperta
  sentiment_at_entry?: number; // [0..1] sentiment della coin all'ingresso
  fear_greed_at_entry?: number; // 0-100 all'ingresso
  regime_at_entry?: string;     // regime di mercato all'apertura
  confidence_at_entry?: number; // convinzione del segnale all'apertura
  funding_at_entry?: number;    // funding rate della coin all'apertura
  scale_stage?: number;         // quanti TP scaglionati già raggiunti
  // TP scaglionati (scale-out): livelli con quota, multiplo di R e se già raggiunti
  tp_ladder?: { price: number; fraction: number; r?: number; hit?: boolean }[];
}

// ---- helpers ----

/** Coerce a Firestore Timestamp | number(ms or s) | ISO string into epoch ms. */
export function toMillis(value: unknown): number | null {
  if (value == null) return null;
  if (typeof value === 'number') {
    // seconds vs ms heuristic
    return value < 1e12 ? value * 1000 : value;
  }
  if (typeof value === 'string') {
    const t = Date.parse(value);
    return Number.isNaN(t) ? null : t;
  }
  // Firestore Timestamp-like
  if (typeof value === 'object') {
    const v = value as { toMillis?: () => number; seconds?: number; _seconds?: number };
    if (typeof v.toMillis === 'function') return v.toMillis();
    if (typeof v.seconds === 'number') return v.seconds * 1000;
    if (typeof v._seconds === 'number') return v._seconds * 1000;
  }
  return null;
}
