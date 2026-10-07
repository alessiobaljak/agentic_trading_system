"""Codice comune della campagna ETHUSDT: caricamento, indicatori causali, uscite,
baseline e statistica. Niente strategie qui dentro: quelle stanno in strategie.py.

Tutto cio' che calcola un indicatore alla barra i usa SOLO barre <= i (barre chiuse):
la strategia riceve dal motore ``candele[:i+1]`` e legge l'indice ``len-1``.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
import yaml

QUI = Path(__file__).resolve().parent
REPO = QUI.parent.parent.parent.parent
sys.path.insert(0, str(REPO))
from research.src import dati, motore, statistica  # noqa: E402
from research.src.motore import Candela, Parametri, Posizione, Segnale  # noqa: E402

RADICE = dati.RADICE_DEFAULT
SIMBOLO = "ETHUSDT"
RIFERIMENTO = "BTCUSDT"

# Periodi fissati nel log (ETHUSDT-N003) prima di caricare i prezzi.
INIZIO_DATI = date(2020, 1, 1)
FINE_COSTRUZIONE = date(2022, 10, 19)
INIZIO_VALIDAZIONE = date(2022, 10, 20)
FINE_IN_SAMPLE = date(2023, 12, 31)

_PARAMETRI_YAML = yaml.safe_load((RADICE / "config" / "parametri.yaml").read_text(encoding="utf-8"))
_BOT = _PARAMETRI_YAML["fatti"]["regole_dimensione_bot"]
SLIPPAGE_ETH = 0.0001  # fascia della scheda: volume medio 2023 oltre 1 miliardo -> 0,01 % per lato
STOP_MASSIMO_BOT = float(_BOT["stop_massimo_bot"])

MS_ORA = 3_600_000
MS_GIORNO = 24 * MS_ORA


def parametri_motore(moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0,
                     riempimento: str = "stop_prima") -> Parametri:
    """I parametri del motore secondo parametri.yaml e la scheda della moneta."""
    return Parametri(
        commissione_per_lato=float(_PARAMETRI_YAML["fatti"]["commissione_taker_per_lato"]["valore"]),
        slippage_per_lato=SLIPPAGE_ETH,
        rischio_per_trade=float(_BOT["rischio_per_trade"]),
        leva_max=float(_BOT["leva_max"]),
        modalita_margine=str(_BOT["modalita_margine_proposta"]),
        tasso_margine_mantenimento=float(_BOT["tasso_margine_mantenimento"]),
        margine_minimo_da_liquidazione=float(_PARAMETRI_YAML["regole_esame"]["margine_minimo_da_liquidazione"]),
        capitale_iniziale=float(_BOT["capitale_iniziale"]),
        riempimento_intrabarra=riempimento,  # type: ignore[arg-type]
        moltiplicatore_costi=moltiplicatore_costi,
        ritardo_barre=ritardo_barre,
    )


# ---------------------------------------------------------------------------
# Caricamento
# ---------------------------------------------------------------------------

_CACHE: Dict[Tuple, object] = {}


def _carica_15m(simbolo: str, tipo: str, inizio: date, fine: date) -> List[Candela]:
    chiave = ("15m", simbolo, tipo, inizio, fine)
    if chiave not in _CACHE:
        _CACHE[chiave] = dati.carica_candele(simbolo, "15m", inizio, fine, RADICE, tipo=tipo)
    return _CACHE[chiave]  # type: ignore[return-value]


def candele(intervallo: str, inizio: date = INIZIO_DATI, fine: date = FINE_IN_SAMPLE,
            simbolo: str = SIMBOLO, tipo: str = "klines") -> List[Candela]:
    """Candele last (o mark) di ``intervallo`` fra le date, aggregate dalle 15m (solo gruppi completi)."""
    chiave = (intervallo, simbolo, tipo, inizio, fine)
    if chiave not in _CACHE:
        base = _carica_15m(simbolo, tipo, inizio, fine)
        _CACHE[chiave] = base if intervallo == "15m" else dati.aggrega_candele(base, intervallo, solo_complete=True)
    return _CACHE[chiave]  # type: ignore[return-value]


def funding(inizio: date = INIZIO_DATI, fine: date = FINE_IN_SAMPLE) -> List[Tuple[int, float]]:
    chiave = ("funding", inizio, fine)
    if chiave not in _CACHE:
        _CACHE[chiave] = dati.carica_funding(SIMBOLO, inizio, fine, RADICE)
    return _CACHE[chiave]  # type: ignore[return-value]


@dataclass
class Serie:
    """Le tre serie allineate di un timeframe, piu' il funding e il riferimento BTC."""

    intervallo: str
    last: List[Candela]
    mark: List[Candela]
    funding: List[Tuple[int, float]]
    btc: Optional[List[Candela]] = None
    # array numpy per gli indicatori, allineati a ``last``
    open: np.ndarray = field(default_factory=lambda: np.zeros(0))
    high: np.ndarray = field(default_factory=lambda: np.zeros(0))
    low: np.ndarray = field(default_factory=lambda: np.zeros(0))
    close: np.ndarray = field(default_factory=lambda: np.zeros(0))
    volume: np.ndarray = field(default_factory=lambda: np.zeros(0))
    ts: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=np.int64))
    btc_close: Optional[np.ndarray] = None

    def __post_init__(self) -> None:
        self.open = np.array([c.open for c in self.last])
        self.high = np.array([c.high for c in self.last])
        self.low = np.array([c.low for c in self.last])
        self.close = np.array([c.close for c in self.last])
        self.volume = np.array([c.volume for c in self.last])
        self.ts = np.array([c.ts for c in self.last], dtype=np.int64)
        if self.btc is not None:
            # BTC allineata per ts: dove manca la barra BTC si ripete l'ultimo close noto (causale).
            per_ts = {c.ts: c.close for c in self.btc}
            out = np.full(len(self.last), np.nan)
            ultimo = np.nan
            for i, t in enumerate(self.ts):
                if int(t) in per_ts:
                    ultimo = per_ts[int(t)]
                out[i] = ultimo
            self.btc_close = out


def serie(intervallo: str, inizio: date, fine: date, con_btc: bool = False) -> Serie:
    """Serie allineate (last, mark, funding, BTC) di un periodo. Il mark si allinea ai ts del last."""
    last = candele(intervallo, inizio, fine)
    mark_tutte = candele(intervallo, inizio, fine, tipo="markPriceKlines")
    per_ts = {c.ts: c for c in mark_tutte}
    # Dove manca la candela mark si usa quella last (il motore vuole serie allineate).
    mark = [per_ts.get(c.ts, c) for c in last]
    btc = candele(intervallo, inizio, fine, simbolo=RIFERIMENTO) if con_btc else None
    return Serie(intervallo, last, mark, funding(inizio, fine), btc)


def flusso_taker(s: Serie, inizio: date, fine: date) -> Tuple[np.ndarray, np.ndarray]:
    """(quote_volume, taker_buy_quote_volume) per barra di ``s``, sommati dalle 15m (colonne 7 e 10 dei CSV).

    Dati del secondo lotto (I-13): si leggono dagli stessi zip gia' scaricati, senza rete.
    """
    chiave = ("taker", s.intervallo, inizio, fine)
    if chiave not in _CACHE:
        durata = dati.durata_intervallo(s.intervallo)
        per_barra: Dict[int, List[float]] = {}
        for anno, mese in dati.mesi_del_periodo(inizio, fine):
            p = dati.percorso_mese(SIMBOLO, "klines", "15m", anno, mese, RADICE)
            if not p.is_file():
                continue
            for r in dati.righe_csv_da_zip(p):
                ts = dati.normalizza_ts(r[0])
                b = per_barra.setdefault(ts // durata * durata, [0.0, 0.0])
                b[0] += float(r[7])
                b[1] += float(r[10])
        q = np.array([per_barra.get(int(t), [np.nan, np.nan])[0] for t in s.ts])
        tb = np.array([per_barra.get(int(t), [np.nan, np.nan])[1] for t in s.ts])
        _CACHE[chiave] = (q, tb)
    return _CACHE[chiave]  # type: ignore[return-value]


def premio_sul_mark(s: Serie) -> np.ndarray:
    """close last / close mark - 1, per barra (I-14). NaN dove la candela mark manca (si e' usata la last)."""
    mark_close = np.array([c.close for c in s.mark])
    presenti = np.array([m is not l for m, l in zip(s.mark, s.last)])
    out = s.close / mark_close - 1.0
    out[~presenti] = np.nan
    return out


def indice_prima_barra(s: Serie, giorno: date) -> int:
    """Indice della prima barra che apre da ``giorno`` (UTC) in poi."""
    return int(np.searchsorted(s.ts, dati.ms_da_data(giorno)))


# ---------------------------------------------------------------------------
# Indicatori causali (il valore in i usa solo barre <= i)
# ---------------------------------------------------------------------------


def media_mobile(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        c = np.cumsum(np.insert(x, 0, 0.0))
        out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def dev_standard_mobile(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        c1 = np.cumsum(np.insert(x, 0, 0.0))
        c2 = np.cumsum(np.insert(x * x, 0, 0.0))
        m = (c1[n:] - c1[:-n]) / n
        v = (c2[n:] - c2[:-n]) / n - m * m
        out[n - 1:] = np.sqrt(np.maximum(v, 0.0))
    return out


def atr(s: Serie, n: int = 14) -> np.ndarray:
    """ATR semplice (media a n barre del true range)."""
    prev_close = np.concatenate(([s.close[0]], s.close[:-1]))
    tr = np.maximum(s.high - s.low, np.maximum(np.abs(s.high - prev_close), np.abs(s.low - prev_close)))
    return media_mobile(tr, n)


def rendimenti(close: np.ndarray) -> np.ndarray:
    r = np.full(len(close), np.nan)
    r[1:] = close[1:] / close[:-1] - 1.0
    return r


def rendimento_a(close: np.ndarray, n: int) -> np.ndarray:
    r = np.full(len(close), np.nan)
    r[n:] = close[n:] / close[:-n] - 1.0
    return r


def massimo_precedente(x: np.ndarray, n: int) -> np.ndarray:
    """Massimo delle n barre PRECEDENTI (esclusa la corrente)."""
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        out[i] = x[i - n:i].max()
    return out


def minimo_precedente(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        out[i] = x[i - n:i].min()
    return out


def rsi(close: np.ndarray, n: int = 2) -> np.ndarray:
    """RSI di Wilder a n periodi (media esponenziale 1/n di guadagni e perdite)."""
    out = np.full(len(close), np.nan)
    if len(close) <= n:
        return out
    delta = np.diff(close)
    su = np.where(delta > 0, delta, 0.0)
    giu = np.where(delta < 0, -delta, 0.0)
    ms, mg = su[:n].mean(), giu[:n].mean()
    for i in range(n, len(delta)):
        ms = (ms * (n - 1) + su[i]) / n
        mg = (mg * (n - 1) + giu[i]) / n
        out[i + 1] = 100.0 if mg == 0 else 100.0 - 100.0 / (1.0 + ms / mg)
    return out


def percentile_mobile(x: np.ndarray, n: int, q: float) -> np.ndarray:
    """q-esimo percentile delle n barre PRECEDENTI (esclusa la corrente)."""
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        out[i] = np.percentile(x[i - n:i], q)
    return out


def ora_utc(ts_ms: int) -> int:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).hour


def giorno_settimana(ts_ms: int) -> int:
    """0 = lunedi' ... 6 = domenica (UTC)."""
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).weekday()


# ---------------------------------------------------------------------------
# Uscita comune e costruzione della strategia per il motore
# ---------------------------------------------------------------------------


@dataclass
class Uscita:
    """I mattoni dell'uscita, dichiarati prima del test (vedi ipotesi.md)."""

    k_atr: float = 2.0
    h_barre: int = 24
    rr_target: Optional[float] = None
    # funzione (indice barra, posizione) -> True se la regola dell'idea chiede di chiudere
    chiusura_segnale: Optional[Callable[[int, Posizione], bool]] = None


def costruisci_strategia(
    s: Serie,
    segnali: np.ndarray,
    uscita: Uscita,
    atr_serie: np.ndarray,
    da_indice: int,
    a_indice: Optional[int] = None,
) -> motore.Strategia:
    """Strategia per ``motore.esegui`` da un array di segnali (+1 long, -1 short, 0 niente).

    ``segnali[i]`` e' letto alla chiusura della barra i (solo barre <= i lo hanno
    prodotto); l'ingresso avviene all'apertura di i+1 per opera del motore. Lo stop
    e' a ``k_atr`` ATR dal close della barra del segnale. Si entra solo per
    ``da_indice <= i < a_indice`` (periodo del test; le barre prima servono al
    riscaldamento). La chiusura per durata avviene quando la posizione ha visto
    ``h_barre`` barre chiuse dopo l'ingresso.
    """
    ts_di = {int(t): i for i, t in enumerate(s.ts)}
    fine = len(s.ts) if a_indice is None else a_indice

    def strategia(cands: Sequence[Candela], pos: Optional[Posizione]):
        i = len(cands) - 1
        if pos is not None:
            i_entrata = ts_di.get(int(pos.ts_entrata))
            if i_entrata is not None and i - i_entrata + 1 >= uscita.h_barre:
                return "chiudi"
            if uscita.chiusura_segnale is not None and uscita.chiusura_segnale(i, pos):
                return "chiudi"
            if i >= fine:
                return "chiudi"
            return None
        if i < da_indice or i >= fine:
            return None
        sgn = int(segnali[i])
        if sgn == 0:
            return None
        a = atr_serie[i]
        if not np.isfinite(a) or a <= 0:
            return None
        c = s.close[i]
        dist = uscita.k_atr * a
        if sgn > 0:
            stop, target = c - dist, (c + uscita.rr_target * dist if uscita.rr_target else None)
            return Segnale("long", stop, target)
        stop, target = c + dist, (c - uscita.rr_target * dist if uscita.rr_target else None)
        return Segnale("short", stop, target)

    return strategia


def esegui(s: Serie, strategia: motore.Strategia, parametri: Optional[Parametri] = None) -> motore.Risultato:
    return motore.esegui(s.last, s.last, s.mark, s.funding, strategia, parametri or parametri_motore())


def stima_trade(segnali: np.ndarray, h_barre: int, da_indice: int, a_indice: int) -> int:
    """Stima dei trade dai SOLI segnali: un segnale conta se dista dal precedente contato almeno h_barre."""
    n, ultimo = 0, -10**9
    for i in range(da_indice, a_indice):
        if segnali[i] != 0 and i - ultimo >= h_barre + 1:
            n += 1
            ultimo = i
    return n


# ---------------------------------------------------------------------------
# Metriche, baseline e statistica
# ---------------------------------------------------------------------------


def riassunto(ris: motore.Risultato, s: Serie) -> Dict[str, object]:
    m = motore.calcola_metriche(ris)
    tr = ris.trades
    out = {
        "n_trade": m["n_trade"], "profit_factor": _arrotonda(m["profit_factor"]),
        "win_rate": round(m["win_rate"], 3), "r_medio": round(m["r_medio"], 4),
        "rendimento_totale": round(m["rendimento_totale"], 4),
        "drawdown_max": round(m["drawdown_max"], 4),
        "rendimento_per_anno": {str(k): round(v, 4) for k, v in m["rendimento_per_anno"].items()},
        "n_ridotti": m["n_ridotti"], "n_violazioni_liquidazione": m["n_violazioni_liquidazione"],
        "esiti": m["esiti"], "funding_totale": round(m["funding_totale"], 2),
        "costi_totali": round(m["costi_totali"], 2),
        "pnl_lordo_prezzo": round(sum(t.pnl_lordo for t in tr), 2),
        "pnl_netto": round(m["pnl_totale"], 2),
        "n_buchi_dati": m["n_buchi_dati"],
    }
    if tr:
        stop_pct = [abs(t.stop - t.entrata) / t.entrata for t in tr]
        out["stop_medio_pct"] = round(float(np.mean(stop_pct)), 4)
        out["n_stop_oltre_6pct"] = int(sum(1 for x in stop_pct if x > STOP_MASSIMO_BOT))
        durate = [(t.ts_uscita - t.ts_entrata) for t in tr]
        out["durata_media_ore"] = round(float(np.mean(durate)) / MS_ORA, 1)
        out["durata_max_ore"] = round(float(np.max(durate)) / MS_ORA, 1)
        out["r_per_anno"] = r_per_anno(tr)
    return out


def _arrotonda(x: float) -> float:
    return round(x, 3) if math.isfinite(x) else x


def r_per_anno(trades: Sequence[motore.Trade]) -> Dict[str, Dict[str, float]]:
    per: Dict[str, List[float]] = {}
    for t in trades:
        a = str(datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc).year)
        per.setdefault(a, []).append(t.r)
    return {a: {"n": len(v), "r_medio": round(float(np.mean(v)), 4), "somma_r": round(float(np.sum(v)), 2)} for a, v in sorted(per.items())}


def serie_r(ris: motore.Risultato) -> List[float]:
    return [t.r for t in sorted(ris.trades, key=lambda t: t.ts_uscita)]


def lunghezza_blocco(ris: motore.Risultato) -> int:
    """Trade che cadono nella durata massima di una posizione (almeno un giorno), minore di n."""
    tr = sorted(ris.trades, key=lambda t: t.ts_uscita)
    n = len(tr)
    if n < 3:
        return 1
    finestra = max(max(t.ts_uscita - t.ts_entrata for t in tr), MS_GIORNO)
    uscite = np.array([t.ts_uscita for t in tr])
    conteggi = [int(np.searchsorted(uscite, u, side="right") - np.searchsorted(uscite, u - finestra, side="left")) for u in uscite]
    blocco = max(1, int(np.ceil(np.percentile(conteggi, 95))))
    return min(blocco, max(1, n // 4))  # mai degenere: al piu' un quarto della serie


def baseline_ogni_barra(s: Serie, direzione: int, uscita: Uscita, atr_serie: np.ndarray,
                        da_indice: int, a_indice: int, parametri: Optional[Parametri] = None) -> motore.Risultato:
    """Baseline (a): stesso effetto senza condizione, ingresso a ogni barra libera."""
    segnali = np.full(len(s.ts), direzione, dtype=int)
    return esegui(s, costruisci_strategia(s, segnali, uscita, atr_serie, da_indice, a_indice), parametri)


def baseline_casuale(s: Serie, direzione: int, uscita: Uscita, atr_serie: np.ndarray,
                     da_indice: int, a_indice: int, n_trade: int, durata_media_barre: int,
                     n_strategie: int = 200, seme: int = 0, parametri: Optional[Parametri] = None,
                     ) -> Dict[str, object]:
    """Baseline (b): ``n_strategie`` strategie a entrate casuali con la stessa uscita e direzione.

    Ritorna gli R medi di ogni strategia casuale, il percentile dell'osservato
    (calcolato da chi chiama) e le serie di R della strategia casuale mediana.
    """
    n_barre = a_indice - da_indice
    r_medi: List[float] = []
    serie_per: List[List[float]] = []
    for k in range(n_strategie):
        idx = statistica.entrate_casuali(n_barre, n_trade, max(1, durata_media_barre), seme + k)
        segnali = np.zeros(len(s.ts), dtype=int)
        for j in idx:
            segnali[da_indice + j] = direzione
        ris = esegui(s, costruisci_strategia(s, segnali, uscita, atr_serie, da_indice, a_indice), parametri)
        r = serie_r(ris)
        r_medi.append(float(np.mean(r)) if r else 0.0)
        serie_per.append(r)
    ordine = int(np.argsort(r_medi)[len(r_medi) // 2])
    return {"r_medi": r_medi, "serie_mediana": serie_per[ordine],
            "pf_mediano": float(np.median([statistica.profit_factor(x) if x else 0.0 for x in serie_per]))}


def percentile_di(valore: float, distribuzione: Sequence[float]) -> float:
    d = np.asarray(distribuzione)
    return float((d < valore).mean() * 100.0)


def confronto_netto(r_candidato: Sequence[float], r_baseline: Sequence[float], blocco: int, seme: int = 0) -> Dict[str, object]:
    blocco = max(1, min(blocco, len(r_candidato) - 1 if len(r_candidato) > 1 else 1, len(r_baseline) - 1 if len(r_baseline) > 1 else 1))
    d = statistica.differenza_nettamente(list(r_candidato), list(r_baseline), blocco, n=2000, seme=seme)
    return {"differenza": round(float(d["differenza"]), 4),
            "errore_standard": (round(float(d["errore_standard"]), 4) if math.isfinite(d["errore_standard"]) else "inf"),
            "netta": bool(d["netta"]), "segno": int(d["segno"]), "degenere": bool(d["degenere"]), "blocco": blocco}


def buy_and_hold(s: Serie, da_indice: int, a_indice: int) -> Dict[str, float]:
    p = parametri_motore()
    tratto = s.last[da_indice:a_indice]
    return {"long": round(motore.buy_and_hold(tratto, p, "long"), 4), "short": round(motore.buy_and_hold(tratto, p, "short"), 4)}
