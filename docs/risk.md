# Risk Management

Due livelli nettamente separati: **parametri regolabili** dall'utente e **limiti
hardcoded** che nessuno può superare.

## Parametri regolabili (dashboard → Firebase `user_risk_settings` → bot)
| Parametro | Range UI | Hard cap |
|-----------|----------|----------|
| `leverage` | 1x–5x | 5x |
| `risk_per_trade` | 0.5%–3% | 3% |

Sizing ATR-based. Kelly Criterion suggerito dopo 100+ trade
(`MIN_TRADES_FOR_KELLY`), ma l'utente può sempre sovrascrivere entro il cap.
Il bot rilegge `user_risk_settings/current` **prima di ogni nuovo trade**
(`TradingBot.read_user_risk`).

## Limiti hardcoded (`bot/risk/hard_limits.py`)
Mai su Firebase, mai nel prompt LLM:
- `MAX_LEVERAGE = 5`, `MAX_RISK_PER_TRADE = 0.03`
- Circuit breakers:
  - daily loss > 5% → **stop totale** per il giorno (`halted_for_day`)
  - 3 SL consecutivi → **pausa 4h**
  - evento macro high-impact → **flat ±2h**
  - volatilità > 3σ → **size dimezzata** (e leva ridotta a scaglioni)

## Logica di precedenza (`RiskManager.resolve_effective_params`)
Per ogni trade:
```
1) parti dal valore utente (Firebase)
2) applica le riduzioni di sicurezza del sistema (volatilità)
3) applica gli hard cap assoluti
4) effettivo = min(valore_utente, safety_system, HARD_CAP)
```
La leva può inoltre essere scalata dal `size_multiplier` dell'orchestratore, e il
nozionale è limitato da `equity * leva`.

Esempio: utente 5x, volatilità 3.5σ → `safety_leverage_cap=2x` → **leva effettiva
2x** (il minimo). Se l'utente mettesse 10x dalla dashboard, l'UI lo clampa a 5x e
comunque il bot lo limiterebbe a 5x (difesa in profondità).

## Final gate (`RiskManager.final_gate`) — l'ultimo cancello
È l'**ultimo** controllo prima dell'invio dell'ordine. Idempotente e difensivo:
1. ri-clampa leva/size agli hard cap (anche se già fatto)
2. blocca se un circuit breaker è attivo
3. blocca quantità/nozionale nulli

`ExecutionEngine.open_position` accetta **solo** `EffectiveRiskParams` con
`approved=True`: non esiste percorso che invii ordini bypassando il gate. I test
in `tests/test_risk.py` lo verificano (è un gate di sicurezza del progetto).

## Correlation guard (`bot/risk/correlation_guard.py`)
Correlazione rolling 24h tra le posizioni aperte: massimo
`MAX_CORRELATED_POSITIONS=3` posizioni con correlazione > `0.85`.
