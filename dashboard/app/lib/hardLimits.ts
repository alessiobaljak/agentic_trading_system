/**
 * Single source of truth for the dashboard's hard safety caps.
 *
 * These MUST mirror the bot's hardcoded limits in `bot/risk/hard_limits.py`:
 *   MAX_LEVERAGE       = 5
 *   MAX_RISK_PER_TRADE = 0.03 (3%)
 *
 * The UI must NEVER allow sending values above these. We clamp on the client
 * before writing to Firestore. The bot enforces the same caps server-side as the
 * final authority — this is purely a UX guardrail, not a security boundary.
 */

export const MAX_LEVERAGE = 5;
export const MIN_LEVERAGE = 1;

export const MAX_RISK_PER_TRADE = 0.03; // 3% (fraction)
export const MIN_RISK_PER_TRADE = 0.005; // 0.5% (fraction)

/** Clamp a number into [min, max]. Non-finite input falls back to min. */
export function clamp(value: number, min: number, max: number): number {
  if (!Number.isFinite(value)) return min;
  return Math.min(Math.max(value, min), max);
}

/** Clamp a requested leverage into the allowed [1..5] range. */
export function clampLeverage(value: number): number {
  return clamp(value, MIN_LEVERAGE, MAX_LEVERAGE);
}

/** Clamp a requested risk-per-trade fraction into the allowed [0.5%..3%] range. */
export function clampRiskPerTrade(value: number): number {
  return clamp(value, MIN_RISK_PER_TRADE, MAX_RISK_PER_TRADE);
}
