"""QUALITA' DI UN BACKTEST — le misure che dicono se un risultato vale qualcosa.

Il PF e il ritorno totale non bastano a decidere. Due strategie con lo stesso
guadagno possono avere profili di rischio opposti, e un risultato costruito su
trenta trade non e' un risultato: e' un aneddoto. Qui stanno le misure che il
report deve SEMPRE riportare, piu' due controlli che il backtest deve superare
prima di essere creduto.

Il piu' importante e' `find_lookahead`, ed e' un controllo di COMPORTAMENTO, non
di codice. Rileggere gli indicatori cercando l'uso del futuro e' un esercizio che
sfugge sempre a qualche caso; rigirare invece lo stesso backtest su dati TRONCATI
e verificare che i trade gia' conclusi siano identici e' una prova: se cambiano,
qualcosa nel passato dipendeva dal futuro, e non c'e' modo che sia un caso.
"""
from __future__ import annotations

import datetime as dt
from collections import defaultdict
from statistics import mean, pstdev
from typing import Optional

# giorni di trading in un anno: le crypto non chiudono mai
DAYS_PER_YEAR = 365.0
RISK_FREE_ANNUAL = 0.04


def daily_returns(trades) -> dict[str, float]:
    """Rendimenti aggregati per GIORNO, dalla data di ingresso del trade.

    Sharpe e Sortino vogliono una serie a passo costante: i trade non lo sono
    (uno dura un'ora, un altro due giorni) e usarli come se fossero osservazioni
    equidistanti gonfia o sgonfia la volatilita' a seconda di quanto si trada.
    Il giorno e' il passo naturale su un mercato aperto 24/7.

    I trade senza timestamp vengono ignorati: attribuirli a un giorno arbitrario
    falserebbe proprio la dispersione che stiamo misurando.
    """
    out: dict[str, float] = defaultdict(float)
    for t in trades:
        ts = float(getattr(t, "entry_ts", 0) or 0)
        if ts <= 0:
            continue
        day = dt.datetime.fromtimestamp(ts, dt.timezone.utc).date().isoformat()
        out[day] += float(t.pnl_pct)
    return dict(out)


def sharpe(trades, risk_free: float = RISK_FREE_ANNUAL) -> Optional[float]:
    """Sharpe ANNUALIZZATO sui rendimenti giornalieri. None se non calcolabile.

    None non e' zero: "non lo so" e "e' pessimo" sono cose diverse, e mostrare 0
    dove manca il dato farebbe scartare strategie che non sono state misurate.
    """
    r = list(daily_returns(trades).values())
    if len(r) < 3:
        return None
    sd = pstdev(r)
    if sd <= 0:
        return None       # nessuna dispersione: il rapporto non ha significato
    excess = mean(r) - risk_free / DAYS_PER_YEAR
    return (excess / sd) * (DAYS_PER_YEAR ** 0.5)


def sortino(trades, risk_free: float = RISK_FREE_ANNUAL) -> Optional[float]:
    """Sortino ANNUALIZZATO: come Sharpe, ma al denominatore solo la volatilita'
    NEGATIVA.

    E' la misura piu' onesta per una strategia asimmetrica come questa: sotto
    scale-out i guadagni arrivano da poche corse lunghe, quindi la deviazione
    standard totale penalizza proprio i giorni buoni — che non sono un rischio.
    """
    r = list(daily_returns(trades).values())
    if len(r) < 3:
        return None
    target = risk_free / DAYS_PER_YEAR
    downside = [min(0.0, x - target) for x in r]
    dd = (sum(d * d for d in downside) / len(downside)) ** 0.5
    if dd <= 0:
        return None       # nessun giorno sotto il target
    return ((mean(r) - target) / dd) * (DAYS_PER_YEAR ** 0.5)


def max_drawdown_dated(trades) -> tuple[float, Optional[str]]:
    """(max drawdown, giorno in cui e' stato toccato il fondo).

    La data non e' un dettaglio estetico: un drawdown concentrato in una settimana
    specifica racconta un evento, uno spalmato su mesi racconta un'erosione. Sono
    due problemi diversi e chiedono risposte diverse.
    """
    rows = sorted(((float(getattr(t, "entry_ts", 0) or 0), float(t.pnl_pct))
                   for t in trades), key=lambda x: x[0])
    peak = equity = dd = 0.0
    when: Optional[float] = None
    for ts, pnl in rows:
        equity += pnl
        peak = max(peak, equity)
        if peak - equity > dd:
            dd, when = peak - equity, ts
    day = (dt.datetime.fromtimestamp(when, dt.timezone.utc).date().isoformat()
           if when else None)
    return dd, day


# --------------------------------------------------------------------------- #
# Semaforo di validazione                                                      #
# --------------------------------------------------------------------------- #
GREEN, YELLOW, RED = "verde", "giallo", "rosso"


def validation_light(*, sharpe_ratio: Optional[float], max_dd: float,
                     n_trades: int, total_return: float,
                     benchmark_return: Optional[float] = None) -> dict:
    """Semaforo: procedi / attenzione / non procedere, coi motivi.

    Ogni criterio vota separatamente e vince il PIU' SEVERO: un Sharpe eccellente
    non compensa trenta trade, perche' non sono la stessa informazione. Con un
    campione piccolo lo Sharpe stesso e' rumore, e mediare i voti significherebbe
    farsi convincere dalla metrica meno affidabile.
    """
    reasons: list[str] = []
    votes: list[str] = []

    def vote(level: str, why: str) -> None:
        votes.append(level)
        reasons.append(why)

    if n_trades < 50:
        vote(RED, f"solo {n_trades} trade: non statisticamente significativo")
    elif n_trades < 100:
        vote(YELLOW, f"{n_trades} trade: campione ancora sottile")
    else:
        vote(GREEN, f"{n_trades} trade")

    if sharpe_ratio is None:
        vote(YELLOW, "Sharpe non calcolabile (troppi pochi giorni operativi)")
    elif sharpe_ratio < 0.5:
        vote(RED, f"Sharpe {sharpe_ratio:.2f} sotto 0.5")
    elif sharpe_ratio < 1.0:
        vote(YELLOW, f"Sharpe {sharpe_ratio:.2f} fra 0.5 e 1.0")
    else:
        vote(GREEN, f"Sharpe {sharpe_ratio:.2f}")

    if max_dd > 0.35:
        vote(RED, f"drawdown {max_dd * 100:.0f}% oltre il 35%")
    elif max_dd > 0.25:
        vote(YELLOW, f"drawdown {max_dd * 100:.0f}% fra 25% e 35%")
    else:
        vote(GREEN, f"drawdown {max_dd * 100:.0f}%")

    if benchmark_return is not None:
        if total_return <= benchmark_return:
            vote(RED, f"sotto il benchmark ({total_return * 100:+.1f}% contro "
                      f"{benchmark_return * 100:+.1f}%): comprare e tenere avrebbe "
                      f"reso di piu', con meno rischio operativo")
        else:
            vote(GREEN, f"batte il benchmark ({total_return * 100:+.1f}% contro "
                        f"{benchmark_return * 100:+.1f}%)")

    level = RED if RED in votes else (YELLOW if YELLOW in votes else GREEN)
    icon = {GREEN: "🟢", YELLOW: "🟡", RED: "🔴"}[level]
    return {"level": level, "icon": icon, "reasons": reasons,
            "passed": level != RED,
            "message": f"{icon} {level.upper()} — " + " · ".join(reasons)}


# --------------------------------------------------------------------------- #
# Look-ahead: un controllo di COMPORTAMENTO                                    #
# --------------------------------------------------------------------------- #
def find_indicator_lookahead(candles: list, cut_frac: float = 0.7,
                             frame_fn=None) -> Optional[str]:
    """Un indicatore legge il futuro? Confronto diretto, colonna per colonna.

    Ogni indicatore causale calcolato su un PREFISSO della serie deve dare gli
    stessi identici valori che da' sulla serie intera: EMA, RSI, ATR guardano solo
    indietro. Se un valore cambia quando si toglie il futuro, quell'indicatore il
    futuro lo stava usando — ed e' il difetto piu' comune e piu' silenzioso che
    esista (basta uno `shift` dimenticato).

    Questo controllo prende anche i look-ahead LIMITATI (uno spostamento di poche
    barre), che il confronto sui trade non vedrebbe: li' il margine di sicurezza
    attorno al taglio li nasconderebbe.
    """
    import pandas as pd

    from bot.core.indicators import compute_indicator_frame

    # iniettabile: cosi' il controllo si prova con un frame VOLUTAMENTE contaminato
    # senza toccare i moduli globali (un monkeypatch qui sarebbe fragile e
    # nasconderebbe proprio il percorso che si vuole verificare)
    frame_fn = frame_fn or compute_indicator_frame
    n = len(candles)
    cut = int(n * cut_frac)
    if cut < 260:
        return None
    full = frame_fn(candles).iloc[:cut]
    part = frame_fn(candles[:cut])
    warm = 200                      # le prime barre non hanno storia sufficiente
    for col in full.columns:
        if col in ("open_time",) or not pd.api.types.is_numeric_dtype(full[col]):
            continue
        a, b = full[col].iloc[warm:], part[col].iloc[warm:]
        if len(a) != len(b):
            continue
        diff = (a.fillna(-1e18) - b.fillna(-1e18)).abs()
        bad = int((diff > 1e-9).sum())
        if bad:
            first = int(diff.idxmax())
            return (f"LOOK-AHEAD nell'indicatore '{col}': {bad} valori cambiano "
                    f"quando si toglie il futuro (primo alla barra {first}). "
                    f"Un indicatore causale non puo' cambiare su un prefisso.")
    return None


def find_lookahead(backtester, strategy_factory, symbol: str, candles: list,
                   cut_frac: float = 0.7, frame_fn=None) -> Optional[str]:
    """Descrizione della violazione trovata, o None se il backtest e' pulito.

    Due controlli, perche' prendono classi diverse di difetto:

    1. GLI INDICATORI (`find_indicator_lookahead`): un valore causale non puo'
       cambiare su un prefisso. Prende anche gli spostamenti di poche barre.
    2. IL COMPORTAMENTO: si rigira lo STESSO backtest su una serie troncata e si
       confrontano i trade gia' conclusi prima del taglio. Prende i look-ahead
       GLOBALI — quelli che normalizzano su tutta la serie e quindi toccano ogni
       singola barra — che nessuna ispezione per colonna troverebbe se il valore
       viene composto dentro la strategia.

    Il secondo controllo ha un limite dichiarato: attorno al taglio serve un
    margine (un trade aperto li' non puo' completarsi con dati che non ci sono),
    quindi da solo non vedrebbe uno spostamento piu' corto del margine. Per questo
    il primo controllo non e' ridondante.
    """
    hit = find_indicator_lookahead(candles, cut_frac, frame_fn)
    if hit:
        return hit
    n = len(candles)
    cut = int(n * cut_frac)
    horizon = 96                     # orizzonte massimo di un trade nel motore
    if cut <= backtester.window + horizon + 10:
        return None                  # serie troppo corta per una prova sensata

    full = backtester.run_strategy(strategy_factory(), symbol, candles)
    part = backtester.run_strategy(strategy_factory(), symbol, candles[:cut])

    # solo i trade CHIUSI prima del taglio: gli altri, nella prova troncata, sono
    # legittimamente diversi perche' i dati per completarli non ci sono.
    safe_ts = float(candles[cut - horizon - 1].open_time.timestamp())
    def _closed_before(st):
        return {round(float(getattr(t, "entry_ts", 0) or 0)): (
                    round(t.entry_price, 10), round(t.exit_price, 10),
                    round(t.pnl_pct, 10))
                for t in st.trades if float(getattr(t, "entry_ts", 0) or 0) <= safe_ts}

    a, b = _closed_before(full), _closed_before(part)
    if a == b:
        return None
    only_full = set(a) - set(b)
    only_part = set(b) - set(a)
    changed = [k for k in set(a) & set(b) if a[k] != b[k]]
    bits = []
    if only_full:
        bits.append(f"{len(only_full)} trade presenti solo con i dati completi")
    if only_part:
        bits.append(f"{len(only_part)} trade presenti solo con i dati troncati")
    if changed:
        k = changed[0]
        bits.append(f"{len(changed)} trade con esito diverso (es. ingresso "
                    f"{a[k][0]} contro {b[k][0]})")
    return ("LOOK-AHEAD: il passato cambia quando si toglie il futuro — "
            + " · ".join(bits))
