"""TETTO DI PERDITA PER COIN AL GIORNO.

21 settembre 2026: tre short consecutivi su USELESSUSDT, -1,74% del conto in
quaranta minuti da una coin sola. Due cause misurate lo stesso giorno: il
rischio per trade dipende dalla volatilita' della coin (stop largo -> 0,9%,
stretto -> 0,2%, backlog A3), e piu' strategie gemelle sulla stessa coin si
mettono in fila dopo ogni stop (E4). Il cooldown di un'ora frena la fila; questo
tetto la chiude: persa una frazione dell'equity su una coin nel giorno, quella
coin non si riapre fino a mezzanotte UTC.

E' una regola di PORTAFOGLIO, non del gate: il gate valida una coppia alla volta
con 10.000$ fissi e non puo' vedere due stop sulla stessa coin colpire lo stesso
conto. Diverge nella direzione sicura (meno trade), com'e' gia' per la
correlazione. Funzione pura, cosi' si testa con tre numeri.
"""
from __future__ import annotations

import datetime as dt


def _ts(v) -> float:
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return dt.datetime.fromisoformat(str(v)).timestamp()
    except (TypeError, ValueError):
        return 0.0


def perdita_oggi(trades: list[dict], symbol: str, now: float) -> float:
    """Somma delle PERDITE (in valuta, positiva) dei trade di `symbol` chiusi da
    mezzanotte UTC. Le vincite non compensano: il tetto e' su quanto si e'
    perso, non sul netto — altrimenti una vincita da 5 permetterebbe altri
    cinque stop da 1."""
    inizio = dt.datetime.fromtimestamp(now, dt.timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0).timestamp()
    tot = 0.0
    for t in trades:
        if t.get("symbol") != symbol:
            continue
        if _ts(t.get("exit_ts")) < inizio:
            continue
        pnl = float(t.get("pnl", 0) or 0)
        if pnl < 0:
            tot += -pnl
    return tot


def coin_bloccata(trades: list[dict], symbol: str, now: float, equity: float,
                  cap: float) -> str | None:
    """Motivo del blocco, o None se la coin si puo' operare."""
    if cap <= 0 or equity <= 0:
        return None
    persa = perdita_oggi(trades, symbol, now)
    if persa / equity >= cap:
        return (f"{symbol}: persi {persa:.2f} oggi = {persa / equity * 100:.2f}% "
                f"dell'equity, tetto {cap * 100:.2f}% per coin al giorno")
    return None
