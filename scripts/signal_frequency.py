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
from datetime import date, datetime, timedelta, timezone

from backtesting.data_loader import load_candles
from backtesting.engine import Backtester
from bot.config import settings
from bot.core.indicators import compute_indicator_frame
from bot.learning.adaptation import AdaptationEngine
from bot.strategies import get_all_strategies

ORE_PER_CANDELA = {"5m": 1 / 12, "15m": 0.25, "30m": 0.5, "1h": 1.0, "4h": 4.0}


def selezionati_una_per_coin(
        intervalli: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """QUALI di questi trade il bot avrebbe aperto (non solo quanti).

    Serve il dettaglio, non il totale, perche' il confronto col paper va fatto
    GIORNO PER GIORNO: il 19 settembre la sonda applicava le 47 coppie validate di
    oggi a tutti e sette i giorni, mentre il bot ne aveva 35 il 17 e 43 il 18 — e il
    paper girava solo da 2,7 giorni dei 7. Sul totale della settimana quel
    disallineamento gonfia gli attesi e fa sembrare che il bot ne apra la meta'.
    Sull'ULTIMO giorno, in cui l'insieme era quasi quello di oggi, il confronto e'
    onesto e la risposta arriva subito invece che fra una settimana.
    """
    libera_da = float("-inf")
    presi: list[tuple[float, float]] = []
    for apre, chiude in sorted(intervalli):
        if apre >= libera_da:
            presi.append((apre, chiude))
            libera_da = chiude
    return presi


def apribili_una_per_coin(intervalli: list[tuple[float, float]]) -> int:
    """Quanti di questi trade il BOT avrebbe potuto davvero aprire.

    Il conto grezzo somma i trade di ogni strategia per conto suo: su ORCAUSDT, che
    ha sei strategie validate, sei segnali sovrapposti contano sei. Il bot invece
    tiene UNA posizione per moneta (`decide_all`: «vincolo conto reale, 1
    posizione/coin»), quindi mentre una e' aperta le altre cinque non entrano.

    Senza questa riga il numero grezzo veniva messo accanto ai trade veri del paper
    e la differenza sembrava un difetto da cacciare. Puo' esserlo — ma prima va
    tolto cio' che e' il comportamento voluto, altrimenti si insegue un fantasma.

    `intervalli`: (apertura, chiusura) in epoch. Si scorre in ordine di apertura e
    si prende il trade solo se la moneta e' libera in quel momento — esattamente
    cio' che fa il bot.
    """
    return len(selezionati_una_per_coin(intervalli))


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
    # (apertura, chiusura) per moneta: serve al conto col vincolo di una posizione
    finestre: dict[str, list[tuple[float, float]]] = defaultdict(list)
    senza_orario = 0
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
                for t in stats.trades:
                    apre = float(getattr(t, "entry_ts", 0) or 0)
                    if apre <= 0:
                        senza_orario += 1
                        continue
                    barre = int(getattr(t, "bars_held", 0) or 0)
                    finestre[sym].append((apre, apre + barre * ore * 3600))

    scelti = [t for v in finestre.values() for t in selezionati_una_per_coin(v)]
    apribili = len(scelti)
    print(f"{'='*56}")
    print(f"SEGNALI GREZZI negli ultimi ~{args.days} giorni: {total}  "
          f"(~{total/max(args.days,1):.1f}/giorno)")
    print(f"DI CUI APRIBILI dal bot:            {apribili}  "
          f"(~{apribili/max(args.days,1):.1f}/giorno)")
    print("  Il grezzo somma ogni strategia per conto suo; il bot tiene UNA")
    print("  posizione per moneta, quindi i segnali sovrapposti sulla stessa coin")
    print("  non entrano. E' il secondo numero che va confrontato col paper.")
    if senza_orario:
        print(f"  ({senza_orario} trade senza orario d'ingresso: esclusi dal secondo "
              f"conto, quindi e' un limite INFERIORE)")

    # GIORNO PER GIORNO: il totale della settimana NON e' confrontabile col paper,
    # perche' qui girano le coppie validate di OGGI su giorni in cui il registro ne
    # aveva meno (35 il 17 settembre, 43 il 18) e in cui il paper magari non girava
    # ancora. Il confronto onesto e' sugli ULTIMI giorni, e per farlo serve la
    # ripartizione — non la media.
    per_giorno: dict[str, int] = defaultdict(int)
    for apre, _ in scelti:
        per_giorno[datetime.fromtimestamp(apre, timezone.utc).strftime("%Y-%m-%d")] += 1
    if per_giorno:
        print("\nAPRIBILI giorno per giorno (UTC):")
        for giorno in sorted(per_giorno):
            print(f"  {giorno}   {per_giorno[giorno]}")
        print("  Confronta gli ULTIMI giorni coi trade veri del paper: i primi della")
        print("  finestra usano le coppie validate di oggi su un registro che allora")
        print("  ne aveva meno, quindi sovrastimano.")
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
