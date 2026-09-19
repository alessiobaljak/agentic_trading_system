"""
Diagnostica: quanti segnali AVREBBERO dovuto generare le strategie validate
negli ultimi giorni? Serve a capire se lo "zero trade" del live e' il mercato
tranquillo (corretto) o un bug che sopprime i segnali.

Per ogni coin validata fa girare le sue strategie validate (stessi params del
bot) sulle candele recenti e conta i trade (ingressi). Sola lettura.

SUL TIMEFRAME, che il 19 settembre ha quasi prodotto una conclusione sbagliata.
Questo script nasceva con `--interval 1h` fisso mentre il bot gira a
ORCHESTRATOR_TIMEFRAME (15m). Su candele quattro volte piu' larghe i segnali sono
molti di meno, quindi il conto degli "attesi" tornava piu' basso del vero — e messo
accanto ai trade davvero aperti dal paper sembrava dire «il numero torna, nessun
segnale viene soppresso». Una diagnostica che misura una scala diversa da quella su
cui il sistema opera non e' imprecisa: risponde a un'altra domanda, e la risposta
sembra quella giusta. Ora il default E' il timeframe del bot, e se qualcuno lo
cambia a mano lo script lo dice in testa al report.

La voce in lista bianca (`frequenza`) non puo' passare argomenti — per scelta, vedi
`ops/README.md` — quindi il default deve essere gia' quello giusto: qui il default
non e' una comodita', e' l'unica cosa che verra' mai eseguita.

Uso sulla VPS:
    BACKTEST_ALLOW_SYNTHETIC=false .venv/bin/python -m scripts.signal_frequency --days 7
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date, timedelta

from backtesting.data_loader import load_candles
from backtesting.engine import Backtester
from bot.config import settings
from bot.core.indicators import compute_indicator_frame
from bot.learning.adaptation import AdaptationEngine
from bot.strategies import get_all_strategies

ORE_PER_CANDELA = {"5m": 1 / 12, "15m": 0.25, "30m": 0.5, "1h": 1.0, "4h": 4.0}


def main() -> int:
    ap = argparse.ArgumentParser(description="Frequenza di segnali attesa (recente).")
    ap.add_argument("--days", type=int, default=7, help="giorni recenti da valutare")
    ap.add_argument("--limit", type=int, default=200, help="quante coin validate")
    ap.add_argument("--interval", default=settings.ORCHESTRATOR_TIMEFRAME,
                    help="default: il timeframe su cui gira il bot")
    args = ap.parse_args()

    adaptation = AdaptationEngine()
    adaptation.load_params()
    adaptation.load_generated()
    coins = sorted(adaptation.validated_coins())[: args.limit]
    if not coins:
        print("Nessuna coin validata nel registro.")
        return 1

    # warmup: l'engine salta le prime 200 candele (indicatori). Il buffer va scalato
    # col timeframe, altrimenti a 15m (200 candele = ~2 giorni) se ne caricano otto
    # di troppo e a 4h non bastano: in entrambi i casi la finestra contata non e'
    # quella dichiarata, e il conto degli attesi esce sbagliato in silenzio.
    ore = ORE_PER_CANDELA.get(args.interval, 1.0)
    warmup_days = max(2, round(200 * ore / 24) + 2)
    start = (date.today() - timedelta(days=args.days + warmup_days)).isoformat()
    engine = Backtester(interval_hours=ore)
    print(f"Conto i trade attesi negli ultimi ~{args.days}g su {len(coins)} coin "
          f"({args.interval}, da {start})...")
    if args.interval != settings.ORCHESTRATOR_TIMEFRAME:
        print(f"ATTENZIONE: il bot opera a {settings.ORCHESTRATOR_TIMEFRAME}, questo "
              f"conto e' a {args.interval}. I due numeri NON sono confrontabili: "
              f"candele piu' larghe danno meno segnali.")
    print()

    per_coin: dict[str, int] = defaultdict(int)
    per_strat: dict[str, int] = defaultdict(int)
    total = 0
    for n, sym in enumerate(coins, 1):
        try:
            candles = load_candles(sym, interval=args.interval, start=start, allow_synthetic=False)
        except Exception as exc:  # noqa: BLE001
            print(f"  {sym}: candele non caricate ({exc})")
            continue
        if len(candles) < 250:
            continue
        frame = compute_indicator_frame(candles)
        strategies = get_all_strategies(adaptation.params_for(sym))
        strategies += adaptation.generated_strategies_for(sym)
        for strat in strategies:
            if not adaptation.is_enabled(sym, strat.name):
                continue
            stats = engine.run_strategy(strat, sym, candles, frame=frame)
            k = len(stats.trades)
            if k:
                per_coin[sym] += k
                per_strat[strat.name] += k
                total += k

    print(f"{'='*56}")
    print(f"TRADE ATTESI negli ultimi ~{args.days} giorni: {total}  "
          f"(~{total/max(args.days,1):.1f}/giorno)")
    print(f"\nPer coin (attive):")
    for sym, k in sorted(per_coin.items(), key=lambda x: -x[1]):
        print(f"  {sym:<14} {k}")
    print(f"\nPer strategia:")
    for s, k in sorted(per_strat.items(), key=lambda x: -x[1]):
        print(f"  {s:<18} {k}")
    print(f"\nLettura: se questo totale e' ~0, il mercato e' tranquillo e lo zero-trade")
    print(f"del live e' CORRETTO. Se e' alto (molti/giorno) ma il live non apre, allora")
    print(f"c'e' qualcosa nel percorso live che sopprime i segnali -> bug da cacciare.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
