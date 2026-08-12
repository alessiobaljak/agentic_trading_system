"""
Metriche di performance SEGMENTATE + calcolo dei PESI DINAMICI.

Tutto opera su liste di dict (trade serializzati da Firestore) per evitare
dipendenze forti dai modelli durante il job notturno.
"""
from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Iterable

from bot.config import settings
from bot.core.models import Regime, StrategyRegimeWeight

# Mappa win_rate -> peso: <=LOW => 0 (disattivata), >=HIGH => 1 (piena).
WEIGHT_WINRATE_LOW = 0.35
WEIGHT_WINRATE_HIGH = 0.60
# Prior del win-rate per lo shrinkage, SOPRA il bordo alto della rampa (0.60).
# Se il prior fosse ESATTAMENTE sul bordo, qualunque evidenza penalizzerebbe subito
# (1 sola perdita: -40% di peso) e le vittorie non compenserebbero mai. A 0.65 le
# vittorie contano davvero: 1 perdita -> peso ~0.77 (non 0.60); 4 perdite senza
# vittorie -> comunque ~0 (i perdenti veri muoiono lo stesso, solo meno isterico).
PRIOR_WINRATE = 0.65


def _is_win(t: dict) -> bool:
    return bool(t.get("is_win", t.get("pnl", 0) > 0))


# Uscite NON decise dalla strategia: interventi ESTERNI (utente / sistema). Il loro
# esito non descrive l'edge della strategia -> escluse dal learning che ne giudica
# la performance (restano comunque nell'equity e nello storico).
_EXTERNAL_EXITS = {"manual", "kill_switch", "circuit_breaker"}


def _strategy_determined(t: dict) -> bool:
    """True se l'uscita e' stata decisa dalla LOGICA (TP/SL/trailing/time-exit) e non
    da un intervento esterno (chiusura manuale, kill switch, circuit breaker)."""
    return t.get("exit_reason") not in _EXTERNAL_EXITS


def filter_anomalous_trades(trades: list[dict]) -> tuple[list[dict], dict]:
    """Toglie dal learning i trade che NON descrivono l'edge della strategia.

    Ritorna (trade_tenuti, {motivo: quanti}). Il conteggio va sempre loggato: un
    filtro troppo aggressivo si riconosce solo vedendo quanto scarta.

    Cosa si esclude e perche':
      * `external_exit` — chiusura decisa da fuori (manuale, kill switch, circuit
        breaker): l'esito misura l'intervento, non la strategia;
      * `wrong_timeframe` — l'esperienza fatta a 1h non descrive le stesse
        strategie a 15m (SL/TP e durate diversi). Senza campo timeframe il trade
        e' anteriore alla tracciatura: escluso, cosi' al cambio di timeframe il
        learning riparte dal prior invece che avvelenato;
      * `short_duration` — trade chiusi in pochi secondi sono quasi sempre
        artefatti (fill anomalo, dato sporco), non decisioni;
      * `slippage_outlier` — esecuzioni molto peggiori della norma misurano la
        liquidita' di quel momento, non la bonta' del segnale.

    NON implementati per mancanza di sorgente, e vanno detti invece che simulati:
      * finestra ±2h attorno agli eventi macro — manca un calendario economico;
      * giorni con volatilita' BTC oltre il 95esimo percentile — il job gira dove
        Binance non e' raggiungibile;
      * trade con WebSocket disconnesso — la salute dello stream e' pubblicata
        come stato istantaneo, non come storico consultabile a posteriori.
    """
    from statistics import median as _median

    reasons: dict[str, int] = defaultdict(int)
    tf = settings.ORCHESTRATOR_TIMEFRAME
    step1: list[dict] = []
    for t in trades:
        if not _strategy_determined(t):
            reasons["external_exit"] += 1
            continue
        if t.get("timeframe") != tf:
            reasons["wrong_timeframe"] += 1
            continue
        dur = t.get("duration_seconds")
        if dur is not None and float(dur) < settings.LEARNING_MIN_TRADE_SECONDS:
            reasons["short_duration"] += 1
            continue
        step1.append(t)

    # slippage: la soglia si calcola sui trade GIA' filtrati e solo se il dato
    # esiste davvero. In DRY_RUN lo slippage e' spesso 0 -> mediana 0 -> qualunque
    # valore positivo sarebbe "anomalo": in quel caso il filtro si disattiva da se'.
    slips = [abs(float(t.get("slippage") or 0)) for t in step1]
    positive = [s for s in slips if s > 0]
    kept = step1
    if len(positive) >= 10:
        limit = _median(positive) * settings.LEARNING_SLIPPAGE_OUTLIER_MULT
        if limit > 0:
            kept = []
            for t, s in zip(step1, slips):
                if s > limit:
                    reasons["slippage_outlier"] += 1
                else:
                    kept.append(t)
    return kept, dict(reasons)


def win_rate(trades: Iterable[dict]) -> float:
    trades = list(trades)
    if not trades:
        return 0.0
    return sum(_is_win(t) for t in trades) / len(trades)


def win_rate_by_strategy(trades: list[dict]) -> dict[str, float]:
    groups = defaultdict(list)
    for t in trades:
        groups[t.get("strategy", "?")].append(t)
    return {k: win_rate(v) for k, v in groups.items()}


def win_rate_by_strategy_regime(trades: list[dict]) -> dict[str, float]:
    groups = defaultdict(list)
    for t in trades:
        key = f"{t.get('strategy','?')}|{t.get('regime_at_entry','?')}"
        groups[key].append(t)
    return {k: win_rate(v) for k, v in groups.items()}


def avg_rr_by_strategy(trades: list[dict]) -> dict[str, float]:
    """R:R realizzato medio = |avg win pnl_pct| / |avg loss pnl_pct| per strategia."""
    groups = defaultdict(list)
    for t in trades:
        groups[t.get("strategy", "?")].append(t)
    out = {}
    for strat, ts in groups.items():
        wins = [abs(t.get("pnl_pct", 0)) for t in ts if _is_win(t)]
        losses = [abs(t.get("pnl_pct", 0)) for t in ts if not _is_win(t)]
        if wins and losses and mean(losses) > 0:
            out[strat] = mean(wins) / mean(losses)
        elif wins and not losses:
            out[strat] = float(len(wins))  # nessuna perdita
    return out


def pnl_by_asset(trades: list[dict]) -> dict[str, float]:
    out = defaultdict(float)
    for t in trades:
        out[t.get("symbol", "?")] += float(t.get("pnl", 0))
    return dict(out)


def win_rate_by_hour(trades: list[dict]) -> dict[str, float]:
    groups = defaultdict(list)
    for t in trades:
        groups[str(t.get("hour_bucket", -1))].append(t)
    return {k: win_rate(v) for k, v in groups.items()}


def worst_drawdown_conditions(trades: list[dict], n: int = 10) -> list[str]:
    """Cosa avevano in comune i trade più perdenti (insight testuali)."""
    losers = sorted([t for t in trades if t.get("pnl", 0) < 0],
                    key=lambda t: t.get("pnl", 0))[:n]
    if not losers:
        return []
    insights = []
    # regime più frequente tra i peggiori
    regimes = defaultdict(int)
    strategies = defaultdict(int)
    hours = defaultdict(int)
    for t in losers:
        regimes[t.get("regime_at_entry", "?")] += 1
        strategies[t.get("strategy", "?")] += 1
        hours[t.get("hour_bucket", -1)] += 1
    top_regime = max(regimes, key=regimes.get)
    top_strat = max(strategies, key=strategies.get)
    top_hour = max(hours, key=hours.get)
    insights.append(f"{regimes[top_regime]}/{len(losers)} dei peggiori trade in regime '{top_regime}'")
    insights.append(f"{strategies[top_strat]}/{len(losers)} dalla strategia '{top_strat}'")
    insights.append(f"fascia oraria UTC {top_hour} ricorrente tra i peggiori")
    return insights


def confidence_outcome_correlation(trades: list[dict]) -> float | None:
    """Pearson tra confidenza dichiarata all'entrata e PnL% reale."""
    pairs = [(t.get("confidence_at_entry"), t.get("pnl_pct"))
             for t in trades
             if t.get("confidence_at_entry") is not None and t.get("pnl_pct") is not None]
    if len(pairs) < 5:
        return None
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in pairs)
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


# limiti dell'adattamento trailing: il lock resta VICINO al 0.5 validato dal gate
# (deviazione deliberata, guidata dai verdetti B1, mai oltre questi bordi).
TRAILING_KEEP_MIN = 0.35
TRAILING_KEEP_MAX = 0.65
TRAILING_MIN_SAMPLE = 8      # sotto questo campione: NESSUN adattamento (niente dati, niente decisioni)


def compute_trailing_keep(trades: list[dict]) -> dict[str, float]:
    """PROFIT_LOCK_KEEP per-strategia imparato dai VERDETTI trailing del paper (B1).

    Il verdetto dice se il trailing ha tagliato un vincitore ('premature') o evitato
    una perdita ('protected'); knockout_atr dice se il ritracciamento che ci ha
    buttato fuori era RUMORE (<1 ATR) o inversione vera.
      * tanti premature DA RUMORE  -> keep piu' BASSO (lock piu' largo: il rumore
        non ci butta fuori, i protected veri scattano comunque);
      * tanti protected            -> keep piu' ALTO (il lock sta lavorando: stringi).
    Gradualita' col campione (piena forza a ~24 verdetti), bordi [0.35, 0.65]
    attorno al 0.5 validato, solo trade del timeframe corrente. Nessun campione
    sufficiente -> strategia ASSENTE dalla mappa -> si usa il default globale."""
    tf = settings.ORCHESTRATOR_TIMEFRAME
    by: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])   # prem, prot, prem_da_rumore
    for t in trades:
        if t.get("timeframe") != tf or t.get("exit_reason") != "trailing_stop":
            continue
        s = t.get("strategy", "?")
        v = t.get("trailing_verdict")
        if v == "premature":
            by[s][0] += 1
            ko = t.get("trailing_knockout_atr")
            if ko is not None and ko < 1.0:
                by[s][2] += 1
        elif v == "protected":
            by[s][1] += 1
    base = settings.PROFIT_LOCK_KEEP
    out: dict[str, float] = {}
    for s, (prem, prot, noise) in by.items():
        n = prem + prot
        if n < TRAILING_MIN_SAMPLE:
            continue
        prem_ratio = prem / n
        strength = min(1.0, n / 24.0)
        delta = (0.5 - prem_ratio) * 0.3 * strength   # prem>50% -> allenta; prot>50% -> stringe
        if delta < 0 and prem and (noise / prem) < 0.5:
            delta *= 0.5   # prematuri NON da rumore: allentare aiuterebbe poco -> mezzo passo
        out[s] = round(max(TRAILING_KEEP_MIN, min(TRAILING_KEEP_MAX, base + delta)), 3)
    return out


def _winrate_to_weight(wr: float) -> float:
    if wr <= WEIGHT_WINRATE_LOW:
        return 0.0
    if wr >= WEIGHT_WINRATE_HIGH:
        return 1.0
    return (wr - WEIGHT_WINRATE_LOW) / (WEIGHT_WINRATE_HIGH - WEIGHT_WINRATE_LOW)


def compute_weights(trades: list[dict]) -> list[StrategyRegimeWeight]:
    """
    Pesi dinamici per strategia × regime, con SHRINKAGE graduale (niente cliff).

    Il win-rate stimato parte dal PRIOR ottimista (0.65 -> peso 1.0, "tradala") e si
    muove verso l'osservato in proporzione al campione: pochi trade -> resta vicino
    al prior; molti -> si avvicina all'osservato. Cosi' il learning inizia SUBITO
    (anche con 1-2 trade sposta un po') senza reagire al rumore di un campione
    minuscolo. MIN_TRADES_PER_WEIGHT ora e' la FORZA dello shrinkage (pseudo-conteggio),
    non piu' una soglia netta.
    """
    prior_wr = PRIOR_WINRATE
    k = max(1, settings.MIN_TRADES_PER_WEIGHT)   # forza dello shrinkage

    # ANOMALIE: timeframe sbagliato, uscite esterne, durate impossibili, slippage
    # fuori scala. Il conteggio si stampa sempre — un filtro troppo aggressivo si
    # riconosce solo vedendo quanto scarta.
    n_in = len(trades)
    trades, reasons = filter_anomalous_trades(trades)
    if reasons:
        detail = " · ".join(f"{k}: {v}" for k, v in sorted(reasons.items()))
        print(f"[learning] filtrati {n_in - len(trades)}/{n_in} trade ({detail})")

    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for t in trades:
        groups[(t.get("strategy", "?"), t.get("regime_at_entry", "?"))].append(t)

    weights: list[StrategyRegimeWeight] = []
    rr_map = avg_rr_by_strategy(trades)
    for (strat, regime), ts in groups.items():
        try:
            regime_enum = Regime(regime)
        except ValueError:
            continue
        n = len(ts)
        wr = win_rate(ts)
        # win-rate "regolarizzato": media pesata tra osservato (n) e prior (k)
        shrunk = (n * wr + k * prior_wr) / (n + k)
        weight = _winrate_to_weight(shrunk)
        # bonus/malus lieve dal R:R realizzato (solo con un minimo di campione)
        rr = rr_map.get(strat)
        if rr is not None and n >= 3:
            weight = max(0.0, min(1.0, weight * (0.75 + min(rr, 3.0) / 6.0)))
        weights.append(StrategyRegimeWeight(
            strategy=strat, regime=regime_enum, weight=round(weight, 4),
            win_rate=round(wr, 4), avg_rr=rr_map.get(strat), sample_size=n,
        ))
    return weights
