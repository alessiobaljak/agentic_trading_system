"""
Costruzione dell'input strutturato per l'orchestratore LLM.

REGOLA DI SICUREZZA: in questo prompt NON entrano MAI gli hard limit di sicurezza
(5x / 3% / circuit breaker). L'LLM decide COSA fare (asset/strategia/direzione/
size_multiplier); i limiti assoluti sono applicati dopo, dal RiskManager, e l'LLM
non li conosce né può ragionarci sopra.
"""
from __future__ import annotations

import json
from typing import Optional

from bot.core.models import AssetSnapshot, MemoryReport, Regime

SYSTEM_PROMPT = """\
Sei l'orchestratore di un sistema di trading algoritmico su crypto futures.
Ricevi lo stato di mercato di alcuni asset selezionati, segnali di strategie,
il contesto (sentiment, fear&greed, funding, eventi macro), il REPORT DI MEMORIA
del motore di apprendimento e gli ultimi trade.

Il tuo compito: scegliere AL PIÙ una decisione di trade per ciclo, oppure nessuna
(stai flat) se non c'è un setup chiaro. Privilegia le strategie che il report di
memoria indica come performanti NEL REGIME CORRENTE. Sii prudente quando la
correlazione tra confidenza dichiarata ed esito reale è bassa.

Rispondi ESCLUSIVAMENTE con un JSON valido di questa forma:
{
  "asset": "BTCUSDT",
  "strategy": "trend_following",
  "direction": "long" | "short",
  "size_multiplier": 0.0-1.0,
  "confidence": 0-100,
  "reasoning": "spiegazione sintetica"
}
Se decidi di restare flat, usa size_multiplier=0 e confidence=0.
NON inventare nomi di strategie o asset non presenti nell'input.
"""


def _asset_brief(a: AssetSnapshot) -> dict:
    i15 = a.ind("15m")
    i1h = a.ind("1h")
    def d(ind):
        if not ind:
            return None
        return {
            "ema_fast": ind.ema_fast, "ema_slow": ind.ema_slow, "rsi": ind.rsi,
            "macd_hist": ind.macd_hist, "bb_upper": ind.bb_upper, "bb_lower": ind.bb_lower,
            "atr": ind.atr, "vwap": ind.vwap, "close": ind.close,
        }
    return {
        "symbol": a.symbol, "price": a.price, "funding_rate": a.funding_rate,
        "sentiment": a.sentiment_score, "fear_greed": a.fear_greed,
        "regime": a.regime.value if a.regime else None,
        "ind_15m": d(i15), "ind_1h": d(i1h),
    }


def build_user_message(
    assets: list[AssetSnapshot],
    signals: list[dict],
    regime: Regime,
    memory_report: Optional[MemoryReport],
    recent_trades: list[dict],
    macro_events: Optional[list[dict]] = None,
) -> str:
    payload = {
        "current_regime": regime.value,
        "assets": [_asset_brief(a) for a in assets],
        "strategy_signals": signals,           # segnali grezzi delle strategie attive
        "macro_events_next_4h": macro_events or [],
        "memory_report": memory_report.model_dump(mode="json") if memory_report else None,
        "recent_trades": recent_trades[:20],
    }
    return json.dumps(payload, default=str, ensure_ascii=False)
