"""
Learning Loop notturno (eseguito da GitHub Action alle 02:00 UTC).

Passi:
  1. Legge i trade degli ultimi 30/60/90 giorni da Firebase.
  2. Calcola metriche di performance segmentate (metrics.py).
  3. Genera un memory_report strutturato (JSON) per ciascuna finestra.
  4. Calcola i PESI DINAMICI per strategia × regime.
  5. Salva memory_report + pesi su Firebase.
  6. (Settimanale) genera un insight narrativo via Claude -> memoria a lungo termine (RAG).

Esegui:  python -m bot.learning.learning_loop
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Optional

from bot.config import settings
from bot.core.firebase_client import get_firebase
from bot.core.models import MemoryReport
from bot.learning import metrics
from bot.learning.adaptation import AdaptationEngine
from bot.learning.trade_logger import TradeLogger


class LearningLoop:
    def __init__(self, firebase=None) -> None:
        self.fb = firebase or get_firebase()
        self.logger = TradeLogger(self.fb)
        self.adaptation = AdaptationEngine(self.fb)

    def build_report(self, lookback_days: int) -> MemoryReport:
        since_ts = time.time() - lookback_days * 86400
        trades = self.logger.all_since(since_ts)
        # solo il timeframe CORRENTE e solo esiti DETERMINATI DALLA STRATEGIA (no
        # kill_switch/manuali/circuit-breaker): metriche e narrativa devono
        # descrivere il sistema che gira ora e NON far giudicare la strategia da
        # chiusure esterne — stesso filtro dei pesi in compute_weights.
        tf = settings.ORCHESTRATOR_TIMEFRAME
        trades = [t for t in trades
                  if t.get("timeframe") == tf and metrics._strategy_determined(t)]

        report = MemoryReport(
            lookback_days=lookback_days,
            total_trades=len(trades),
            overall_win_rate=metrics.win_rate(trades),
            win_rate_by_strategy=metrics.win_rate_by_strategy(trades),
            win_rate_by_strategy_regime=metrics.win_rate_by_strategy_regime(trades),
            avg_rr_by_strategy=metrics.avg_rr_by_strategy(trades),
            pnl_by_asset=metrics.pnl_by_asset(trades),
            win_rate_by_hour=metrics.win_rate_by_hour(trades),
            worst_drawdown_conditions=metrics.worst_drawdown_conditions(trades),
            confidence_outcome_correlation=metrics.confidence_outcome_correlation(trades),
            weights=metrics.compute_weights(trades),
        )
        return report

    def run(self) -> dict[int, MemoryReport]:
        """Genera i report per tutte le finestre e salva pesi (da quella a 30g)."""
        reports: dict[int, MemoryReport] = {}
        for days in settings.LEARNING_LOOKBACK_DAYS:
            report = self.build_report(days)
            self.fb.set_doc("memory", str(days), report.model_dump(mode="json"))
            reports[days] = report
            print(f"[learning] report {days}g: {report.total_trades} trade, "
                  f"win_rate={report.overall_win_rate:.2%}, "
                  f"{len(report.weights)} pesi")

        # i pesi operativi derivano dalla finestra principale (30g). MAI azzerare
        # il doc con una lista vuota (es. 0 trade dopo un cambio timeframe): il
        # refresh orario del bot fa lo stesso, i due writer restano coerenti.
        primary = reports.get(30) or next(iter(reports.values()))
        if primary.weights:
            self.adaptation.save_weights(primary.weights)

        # auto-analisi narrativa (settimanale, opzionale via Claude)
        narrative = self._maybe_narrative(primary)
        if narrative:
            primary.narrative = narrative
            self.fb.set_doc("memory", "30", primary.model_dump(mode="json"))
            self._save_weekly_insight(narrative, primary)

        return reports

    # ------------------------------------------------------------------ #
    def _maybe_narrative(self, report: MemoryReport) -> Optional[str]:
        """Solo di domenica (o se forzato) genera il commento dell'orchestratore."""
        if not settings.ANTHROPIC_API_KEY:
            return None
        if datetime.now(timezone.utc).weekday() != 6:  # 6 = domenica
            return None
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            resp = client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=400,
                messages=[{
                    "role": "user",
                    "content": (
                        "Sei l'orchestratore di un trading system. Analizza questo report "
                        "settimanale e spiega in 4-6 frasi quali strategie hanno funzionato in "
                        "quali regimi e come hai adattato i pesi. Report JSON:\n\n"
                        + report.model_dump_json()
                    ),
                }],
            )
            return resp.content[0].text.strip()
        except Exception as exc:  # noqa: BLE001
            print(f"[learning] narrativa fallita: {exc}")
            return None

    def _save_weekly_insight(self, narrative: str, report: MemoryReport) -> None:
        """Salva l'insight come memoria a lungo termine (RAG)."""
        week_id = datetime.now(timezone.utc).strftime("%Y-W%W")
        self.fb.set_doc("insights", week_id, {
            "week_id": week_id,
            "narrative": narrative,
            "overall_win_rate": report.overall_win_rate,
            "total_trades": report.total_trades,
            "created_at": time.time(),
        })


def main() -> None:
    print(f"[learning] avvio learning loop @ {datetime.now(timezone.utc).isoformat()}")
    LearningLoop().run()
    print("[learning] completato")


if __name__ == "__main__":
    main()
