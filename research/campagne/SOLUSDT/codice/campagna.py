"""Involucro del motore per la campagna SOLUSDT (research/PROTOCOLLO.md, Passo 3).

Qui non ci sono strategie: solo il caricamento dei dati della moneta (con le
tre serie allineate), i parametri congelati di SOLUSDT, l'esecuzione di una
variante nelle sue forme di verifica (ritardo, costi doppi, regola intra-barra
opposta), le tre baseline della sezione 8 e la stima dei trade.

Una strategia e' una FABBRICA ``fabbrica(candele) -> strategia``: riceve l'intera
serie del periodo per precalcolare gli indicatori (ogni valore all'indice i deve
dipendere solo dalle barre <= i: la responsabilita' e' di chi scrive la
strategia, e il test del ritardo di una barra la controlla) e restituisce la
funzione ``strategia(candele[:i+1], posizione)`` che il motore chiama a ogni
barra chiusa.
"""
from __future__ import annotations

import math
from dataclasses import replace
from datetime import date, datetime, timezone
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from research.src import dati, motore, statistica
from research.src.motore import Candela, Parametri, Posizione, Segnale

SIMBOLO = "SOLUSDT"
RIFERIMENTO = "BTCUSDT"

# Parametri congelati (config/parametri.yaml + scheda_moneta.md): slippage 0,01%
# per lato (volume 2023 sopra 1 miliardo), commissione taker 0,05%, rischio 1%,
# leva massima 2, margine isolato, margine di mantenimento 2,5%, capitale 1.000.
PARAMETRI = Parametri(
    commissione_per_lato=0.0005,
    slippage_per_lato=0.0001,
    rischio_per_trade=0.01,
    leva_max=2.0,
    modalita_margine="isolated",
    tasso_margine_mantenimento=0.025,
    margine_minimo_da_liquidazione=0.8,
    capitale_iniziale=1000.0,
    riempimento_intrabarra="stop_prima",
)

# Periodi (log SOLUSDT-001 e SOLUSDT-002): il 2020 e' escluso per liquidita'.
COSTRUZIONE = (date(2021, 1, 1), date(2023, 1, 4))
VALIDAZIONE = (date(2023, 1, 5), date(2023, 12, 31))
INSAMPLE_UTILE = (date(2021, 1, 1), date(2023, 12, 31))

Fabbrica = Callable[[Sequence[Candela]], motore.Strategia]

_cache: Dict[tuple, object] = {}


def giorno(ts: int) -> datetime:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)


def carica(tf: str, periodo: Tuple[date, date], simbolo: str = SIMBOLO):
    """(candele last, candele mark, funding) allineate: solo le barre presenti in entrambe le serie."""
    chiave = (simbolo, tf, periodo)
    if chiave in _cache:
        return _cache[chiave]
    inizio, fine = periodo
    last = dati.carica_candele(simbolo, tf, inizio, fine)
    mark = dati.carica_candele(simbolo, tf, inizio, fine, tipo="markPriceKlines")
    ts_l, ts_m = {c.ts for c in last}, {c.ts for c in mark}
    comuni = ts_l & ts_m
    last2 = [c for c in last if c.ts in comuni]
    mark2 = [c for c in mark if c.ts in comuni]
    funding = dati.carica_funding(simbolo, inizio, fine)
    scartate = (len(last) - len(last2), len(mark) - len(mark2))
    _cache[chiave] = (last2, mark2, funding, scartate)
    return _cache[chiave]


def carica_riferimento(tf: str, periodo: Tuple[date, date]) -> List[Candela]:
    """Candele last di BTCUSDT (riferimento di mercato), senza allineamento al mark."""
    chiave = (RIFERIMENTO, tf, periodo, "solo_last")
    if chiave not in _cache:
        _cache[chiave] = dati.carica_candele(RIFERIMENTO, tf, periodo[0], periodo[1])
    return _cache[chiave]


def esegui(fabbrica: Fabbrica, tf: str, periodo: Tuple[date, date], ritardo: int = 0,
           moltiplicatore_costi: float = 1.0, intrabarra: str = "stop_prima",
           candele: Optional[List[Candela]] = None) -> motore.Risultato:
    """Una corsa del motore con i parametri di SOLUSDT e le forme di verifica della Fase 4."""
    last, mark, funding, _ = carica(tf, periodo)
    if candele is not None:
        last = candele
    p = replace(PARAMETRI, ritardo_barre=ritardo, moltiplicatore_costi=moltiplicatore_costi,
                riempimento_intrabarra=intrabarra)
    return motore.esegui(last, None, mark, funding, fabbrica(last), p)


# ---------------------------------------------------------------------------
# Riassunti
# ---------------------------------------------------------------------------

def riassunto(ris: motore.Risultato, arrotonda: int = 3) -> Dict[str, object]:
    """Le metriche del motore piu' R per anno e durata delle posizioni, pronte per il log."""
    m = ris.metriche()
    tr = ris.trades
    per_anno: Dict[int, List[float]] = {}
    for t in tr:
        per_anno.setdefault(giorno(t.ts_uscita).year, []).append(t.r)
    durate = [max(1, (t.ts_uscita - t.ts_entrata) / 3_600_000) for t in tr]
    out = {
        "trade": m["n_trade"],
        "profit_factor": _arr(m["profit_factor"], arrotonda),
        "r_medio": _arr(m["r_medio"], arrotonda),
        "r_mediano": _arr(float(np.median([t.r for t in tr])) if tr else 0.0, arrotonda),
        "win_rate": _arr(m["win_rate"], arrotonda),
        "rendimento_totale": _arr(m["rendimento_totale"], arrotonda),
        "drawdown_max": _arr(m["drawdown_max"], arrotonda),
        "rendimento_per_anno": {str(k): _arr(v, arrotonda) for k, v in m["rendimento_per_anno"].items()},
        "r_medio_per_anno": {str(k): [len(v), _arr(sum(v) / len(v), arrotonda)] for k, v in sorted(per_anno.items())},
        "durata_media_ore": _arr(sum(durate) / len(durate) if durate else 0.0, 1),
        "durata_max_ore": _arr(max(durate) if durate else 0.0, 1),
        "esiti": m["esiti"],
        "ridotti": m["n_ridotti"],
        "violazioni_liquidazione": m["n_violazioni_liquidazione"],
        "buchi_dati": m["n_buchi_dati"],
        "funding_in_buco": m["n_funding_in_buco"],
        "costi_totali": _arr(m["costi_totali"], 2),
        "funding_totale": _arr(m["funding_totale"], 2),
        "per_direzione": {d: {k: _arr(v, arrotonda) for k, v in s.items()} for d, s in m["per_direzione"].items()},
    }
    return out


def _arr(v, n):
    if isinstance(v, float):
        if math.isinf(v) or math.isnan(v):
            return str(v)
        return round(v, n)
    return v


def r_ordinati(ris: motore.Risultato) -> List[float]:
    return [t.r for t in sorted(ris.trades, key=lambda t: t.ts_uscita)]


def lunghezza_blocco(ris: motore.Risultato, tf: str) -> int:
    """Blocco del bootstrap (sezione 8): trade che cadono nella finestra piu' lunga fra
    la durata massima di una posizione e un giorno; almeno 1 e meno del numero di trade."""
    tr = ris.trades
    if len(tr) < 2:
        return 1
    dur_max_ms = max(t.ts_uscita - t.ts_entrata for t in tr)
    finestra = max(dur_max_ms, 24 * 3_600_000)
    span = max(tr[-1].ts_uscita - tr[0].ts_entrata, 1)
    blocco = math.ceil(len(tr) * finestra / span)
    return max(1, min(blocco, len(tr) - 1))


# ---------------------------------------------------------------------------
# Stima dei trade prima del test (sezione 8)
# ---------------------------------------------------------------------------

def stima_trade(fabbrica: Fabbrica, tf: str, periodo: Tuple[date, date] = COSTRUZIONE,
                durata_attesa_barre: int = 1) -> Dict[str, int]:
    """Conta i segnali sui dati di costruzione senza eseguire il backtest.

    ``grezzi``: barre con un segnale; ``non_sovrapposti``: segnali presi
    assumendo che ogni posizione duri ``durata_attesa_barre`` barre (il
    successivo si accetta solo dopo). Non guarda i risultati.
    """
    last, _, _, _ = carica(tf, periodo)
    strat = fabbrica(last)
    grezzi = 0
    non_sov = 0
    libero_da = 0
    for i in range(len(last)):
        s = strat(last[: i + 1], None)
        if isinstance(s, Segnale):
            grezzi += 1
            if i >= libero_da:
                non_sov += 1
                libero_da = i + 1 + durata_attesa_barre
    return {"grezzi": grezzi, "non_sovrapposti": non_sov, "barre": len(last)}


# ---------------------------------------------------------------------------
# Baseline (sezione 8)
# ---------------------------------------------------------------------------

def buy_and_hold(tf: str, periodo: Tuple[date, date]) -> Dict[str, object]:
    """Baseline (c): buy and hold e il suo opposto, sul periodo e per anno."""
    last, _, _, _ = carica(tf, periodo)
    out = {"long": _arr(motore.buy_and_hold(last, PARAMETRI, "long"), 3),
           "short": _arr(motore.buy_and_hold(last, PARAMETRI, "short"), 3), "per_anno": {}}
    anni: Dict[int, List[Candela]] = {}
    for c in last:
        anni.setdefault(giorno(c.ts).year, []).append(c)
    for a, cc in sorted(anni.items()):
        out["per_anno"][str(a)] = {"long": _arr(motore.buy_and_hold(cc, PARAMETRI, "long"), 3),
                                   "short": _arr(motore.buy_and_hold(cc, PARAMETRI, "short"), 3)}
    return out


def fabbrica_entrate_fisse(indici: Sequence[int], direzione: str, uscita: Callable[[Sequence[Candela], int], Segnale],
                           chiusura: Optional[Callable[[Sequence[Candela], Posizione], bool]] = None) -> Fabbrica:
    """Strategia che entra SOLO agli indici dati con la regola di uscita del candidato.

    ``uscita(candele, i)`` restituisce il Segnale (stop, target) come lo farebbe il
    candidato alla barra i; ``chiusura(candele, pos)`` dice se chiudere a mercato
    (la regola di uscita a tempo del candidato, se c'e').
    """
    insieme = set(indici)

    def fabbrica(candele: Sequence[Candela]) -> motore.Strategia:
        def strategia(cand: Sequence[Candela], pos: Optional[Posizione]):
            i = len(cand) - 1
            if pos is not None:
                if chiusura is not None and chiusura(cand, pos):
                    return "chiudi"
                return None
            if i in insieme:
                return uscita(cand, i)
            return None
        return strategia
    return fabbrica


def baseline_casuale(ris_candidato: motore.Risultato, tf: str, periodo: Tuple[date, date], direzione: str,
                     uscita: Callable[[Sequence[Candela], int], Segnale],
                     chiusura: Optional[Callable[[Sequence[Candela], Posizione], bool]],
                     n_simulazioni: int = 200, seme: int = 1, riscaldamento: int = 0) -> Dict[str, object]:
    """Baseline (b): entrate casuali con la stessa uscita, direzione, numero e durata media dei trade.

    Ritorna la distribuzione degli R medi delle simulazioni, il percentile del
    candidato in quella distribuzione, e il giudizio «nettamente» (bootstrap a
    blocchi) contro la simulazione mediana.
    """
    last, _, _, _ = carica(tf, periodo)
    tr = ris_candidato.trades
    n_trade = len(tr)
    if n_trade == 0:
        return {"errore": "candidato senza trade"}
    durata_ms = sum(t.ts_uscita - t.ts_entrata for t in tr) / n_trade
    durata_barre = max(1, round(durata_ms / (last[1].ts - last[0].ts)))
    medie = []
    serie = []
    for k in range(n_simulazioni):
        idx = statistica.entrate_casuali(len(last) - 1, n_trade, durata_barre, seme + k,
                                         barre_vietate=[(0, riscaldamento)] if riscaldamento else ())
        r = motore.esegui(last, None, carica(tf, periodo)[1], carica(tf, periodo)[2],
                          fabbrica_entrate_fisse(idx, direzione, uscita, chiusura)(last), PARAMETRI)
        rs = r_ordinati(r)
        medie.append(sum(rs) / len(rs) if rs else 0.0)
        serie.append(rs)
    medie_arr = np.array(medie)
    r_cand = r_ordinati(ris_candidato)
    media_cand = sum(r_cand) / len(r_cand)
    percentile_cand = float((medie_arr < media_cand).mean() * 100)
    mediana_idx = int(np.argsort(medie_arr)[len(medie_arr) // 2])
    blocco = lunghezza_blocco(ris_candidato, tf)
    netta = statistica.differenza_nettamente(r_cand, serie[mediana_idx], blocco, 2000, seme)
    return {
        "simulazioni": n_simulazioni,
        "r_medio_candidato": _arr(media_cand, 3),
        "r_medio_caso_media": _arr(float(medie_arr.mean()), 3),
        "r_medio_caso_p50": _arr(float(np.percentile(medie_arr, 50)), 3),
        "r_medio_caso_p90": _arr(float(np.percentile(medie_arr, 90)), 3),
        "r_medio_caso_p95": _arr(float(np.percentile(medie_arr, 95)), 3),
        "percentile_candidato": _arr(percentile_cand, 1),
        "durata_barre": durata_barre,
        "blocco": blocco,
        "nettamente_vs_mediana": {k: (_arr(v, 3) if isinstance(v, float) else v) for k, v in netta.items()},
    }


def nettamente(r_a: Sequence[float], r_b: Sequence[float], blocco: int, seme: int = 1) -> Dict[str, object]:
    d = statistica.differenza_nettamente(list(r_a), list(r_b), blocco, 2000, seme)
    return {k: (_arr(v, 3) if isinstance(v, float) else v) for k, v in d.items()}


# ---------------------------------------------------------------------------
# Indicatori causali (ogni valore all'indice i usa solo barre <= i)
# ---------------------------------------------------------------------------

def arrays(candele: Sequence[Candela]):
    o = np.array([c.open for c in candele]); h = np.array([c.high for c in candele])
    l = np.array([c.low for c in candele]); cl = np.array([c.close for c in candele])
    v = np.array([c.volume for c in candele]); ts = np.array([c.ts for c in candele])
    return o, h, l, cl, v, ts


def atr(h, l, cl, n: int) -> np.ndarray:
    """ATR semplice (media mobile del true range su n barre), NaN finche' non ci sono n barre."""
    prev = np.concatenate([[np.nan], cl[:-1]])
    tr = np.maximum(h - l, np.maximum(np.abs(h - prev), np.abs(l - prev)))
    tr[0] = h[0] - l[0]
    return media_mobile(tr, n)


def media_mobile(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        cs = np.cumsum(np.insert(x, 0, 0.0))
        out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def massimo_precedente(x: np.ndarray, n: int) -> np.ndarray:
    """Massimo delle n barre PRECEDENTI (escluso i), NaN all'inizio."""
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        out[i] = x[i - n:i].max()
    return out


def minimo_precedente(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        out[i] = x[i - n:i].min()
    return out


def deviazione_mobile(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = x[i - n + 1:i + 1].std()
    return out


def ora_utc(ts: np.ndarray) -> np.ndarray:
    return ((ts // 3_600_000) % 24).astype(int)


def giorno_settimana(ts: np.ndarray) -> np.ndarray:
    """0 = lunedi' ... 6 = domenica (UTC)."""
    return ((ts // 86_400_000 + 3) % 7).astype(int)
