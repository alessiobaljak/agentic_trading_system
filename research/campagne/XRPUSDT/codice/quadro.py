"""Il quadro comune delle varianti di XRPUSDT: dati, strategia, baseline, log.

Una variante e' descritta da una funzione ``prepara(serie)`` che, sulle candele
passate (solo barre chiuse: ogni valore alla barra i usa solo le barre 0..i),
restituisce gli array:

* ``cond``: condizione d'ingresso alla chiusura della barra i (bool);
* ``stop``, ``target``: prezzi di stop e target calcolati alla chiusura della barra i
  (``target`` puo' essere None: nessun target);
* ``uscita``: (facoltativo) True alla chiusura della barra i se la posizione si chiude
  per segnale all'apertura della barra dopo;
* ``warmup``: prima barra in cui tutti gli indicatori della variante esistono.

La variante ha una sola direzione e una tenuta massima in barre (uscita a tempo):
con la posizione aperta da j, alla chiusura della barra j + tenuta - 1 si chiude.

La strategia, la (a) e la (b) si costruiscono qui, sempre allo stesso modo:

* candidato: entra se ``cond[i]`` e la barra non sta in un mese sotto la liquidita' minima;
* (a): entra a ogni barra libera dalla prima in cui la variante puo' entrare (``warmup``),
  stessa uscita, stop e target, stesso filtro dei mesi illiquidi (sezione 8; Fase 0 punto 3);
* (b): ``simula_baseline_casuale`` con ingressi fuori da: barre dove il segnale non e'
  valido (``barre_vietate_segnale_non_valido``, riscaldamento compreso), mesi illiquidi,
  e in validazione tutte le barre di costruzione.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

import numpy as np

from research.src import dati, motore, statistica
from research.src.motore import Candela, Parametri, Segnale

SIMBOLO = "XRPUSDT"
CARTELLA = Path(__file__).resolve().parent.parent
LOG = CARTELLA / "log.jsonl"
INIZIO = date(2020, 1, 1)
FINE_COSTRUZIONE = date(2022, 10, 18)
FINE_COSTRUZIONE_TS = 1666137599999
INIZIO_VALIDAZIONE_TS = 1666137600000
FINE_IN_SAMPLE = date(2023, 12, 31)
TRADE_MINIMI_COSTRUZIONE = 70

MS = {tf: dati.durata_intervallo(tf) for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]}

#: Mesi (anno, mese) sotto la liquidita' minima, da fase0_dati.md. Riempito in Fase 0.
MESI_ILLIQUIDI: frozenset = frozenset()


def parametri(moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0,
              riempimento: str = "stop_prima") -> Parametri:
    """Parametri del motore da config/parametri.yaml e dalla scheda della moneta."""
    return Parametri(
        commissione_per_lato=0.0005,
        slippage_per_lato=0.0002,
        rischio_per_trade=0.01,
        leva_max=2.0,
        modalita_margine="isolated",
        tasso_margine_mantenimento=0.025,
        margine_minimo_da_liquidazione=0.8,
        capitale_iniziale=1000.0,
        riempimento_intrabarra=riempimento,
        moltiplicatore_costi=moltiplicatore_costi,
        ritardo_barre=ritardo_barre,
    )


# ---------------------------------------------------------------------------
# Log
# ---------------------------------------------------------------------------


def adesso() -> str:
    """L'orologio della macchina (lo stesso di ``date -u``), in UTC al secondo."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pulisci(x):
    if isinstance(x, dict):
        return {str(k): _pulisci(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_pulisci(v) for v in x]
    if isinstance(x, np.ndarray):
        return [_pulisci(v) for v in x.tolist()]
    if isinstance(x, (np.floating,)):
        x = float(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, float):
        if math.isnan(x):
            return None
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        return round(x, 6)
    return x


def scrivi_log(voce: Dict) -> None:
    voce = dict(voce)
    voce.setdefault("data", adesso())
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(_pulisci(voce), ensure_ascii=False) + "\n")
        f.flush()


def leggi_log() -> List[Dict]:
    with open(LOG, encoding="utf-8") as f:
        return [json.loads(r) for r in f if r.strip()]


def prossimo_variante_n() -> int:
    n = [v.get("variante_n", 0) for v in leggi_log()
         if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"]
    return (max(n) if n else 0) + 1


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------

_CACHE: Dict = {}


def serie(tf: str, fine: date = FINE_COSTRUZIONE) -> Dict:
    """Last e mark allineati (carica_serie_allineate), funding e BTC sugli stessi ts."""
    chiave = (tf, fine)
    if chiave in _CACHE:
        return _CACHE[chiave]
    al = dati.carica_serie_allineate(SIMBOLO, tf, INIZIO, fine)
    candele = al["candele"]
    funding = dati.carica_funding(SIMBOLO, INIZIO, fine)
    btc = {c.ts: c for c in dati.carica_candele("BTCUSDT", tf, INIZIO, fine)}
    btc_close = np.array([btc[c.ts].close if c.ts in btc else np.nan for c in candele])
    s = {
        "tf": tf,
        "candele": candele,
        "mark": al["candele_mark"],
        "funding": funding,
        "ts": np.array([c.ts for c in candele], dtype=np.int64),
        "open": np.array([c.open for c in candele]),
        "high": np.array([c.high for c in candele]),
        "low": np.array([c.low for c in candele]),
        "close": np.array([c.close for c in candele]),
        "volume": np.array([c.volume for c in candele]),
        "volume_usdt": np.array([al["volume_usdt"].get(c.ts) or np.nan for c in candele], dtype=float),
        "btc_close": btc_close,
        "ms": MS[tf],
    }
    s["permesso"] = permesso_liquidita(s["ts"])
    _CACHE[chiave] = s
    return s


def permesso_liquidita(ts: np.ndarray) -> np.ndarray:
    """False sulle barre dei mesi sotto la liquidita' minima (Fase 0, punto 3)."""
    if not MESI_ILLIQUIDI:
        return np.ones(len(ts), dtype=bool)
    out = np.ones(len(ts), dtype=bool)
    for k, t in enumerate(ts):
        d = datetime.fromtimestamp(int(t) / 1000, tz=timezone.utc)
        if (d.year, d.month) in MESI_ILLIQUIDI:
            out[k] = False
    return out


# ---------------------------------------------------------------------------
# Indicatori causali (il valore alla barra i usa solo le barre 0..i)
# ---------------------------------------------------------------------------


def atr(s: Dict, n: int = 14) -> np.ndarray:
    """ATR di Wilder: media mobile esponenziale 1/n del true range. NaN prima di n barre."""
    h, l, c = s["high"], s["low"], s["close"]
    tr = np.empty(len(c))
    tr[0] = h[0] - l[0]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1])))
    out = np.full(len(c), np.nan)
    if len(c) < n:
        return out
    out[n - 1] = tr[:n].mean()
    for i in range(n, len(c)):
        out[i] = out[i - 1] + (tr[i] - out[i - 1]) / n
    return out


def sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    cs = np.cumsum(np.insert(np.nan_to_num(x, nan=0.0), 0, 0.0))
    out[n - 1:] = (cs[n:] - cs[:-n]) / n
    # se c'e' un NaN dentro la finestra il valore e' NaN
    nan = np.isnan(x).astype(float)
    cn = np.cumsum(np.insert(nan, 0, 0.0))
    bad = (cn[n:] - cn[:-n]) > 0
    out[n - 1:][bad] = np.nan
    return out


def ema(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    a = 2.0 / (n + 1)
    if len(x) < n:
        return out
    out[n - 1] = np.mean(x[:n])
    for i in range(n, len(x)):
        out[i] = out[i - 1] + a * (x[i] - out[i - 1])
    return out


def rolling_max(x: np.ndarray, n: int) -> np.ndarray:
    """Massimo delle n barre fino alla i compresa."""
    out = np.full(len(x), np.nan)
    from numpy.lib.stride_tricks import sliding_window_view
    if len(x) >= n:
        out[n - 1:] = sliding_window_view(x, n).max(axis=1)
    return out


def rolling_min(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    from numpy.lib.stride_tricks import sliding_window_view
    if len(x) >= n:
        out[n - 1:] = sliding_window_view(x, n).min(axis=1)
    return out


def rolling_std(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    from numpy.lib.stride_tricks import sliding_window_view
    if len(x) >= n:
        out[n - 1:] = sliding_window_view(x, n).std(axis=1, ddof=1)
    return out


def rsi(c: np.ndarray, n: int) -> np.ndarray:
    """RSI di Wilder."""
    d = np.diff(c, prepend=np.nan)
    up = np.where(d > 0, d, 0.0)
    dn = np.where(d < 0, -d, 0.0)
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    au, ad = up[1:n + 1].mean(), dn[1:n + 1].mean()
    for i in range(n, len(c)):
        if i > n:
            au = au + (up[i] - au) / n
            ad = ad + (dn[i] - ad) / n
        out[i] = 100.0 if ad == 0 else 100.0 - 100.0 / (1.0 + au / ad)
    return out


def ritardato(x: np.ndarray, k: int) -> np.ndarray:
    """x spostato di k barre in avanti: valore alla barra i = x[i-k]."""
    out = np.full(len(x), np.nan, dtype=float)
    if k < len(x):
        out[k:] = x[:len(x) - k]
    return out


# ---------------------------------------------------------------------------
# Variante e strategie
# ---------------------------------------------------------------------------


@dataclass
class Variante:
    id: str
    tf: str
    direzione: str
    prepara: Callable[[Dict], Dict]
    tenuta: Optional[int]  # barre massime di tenuta; None = nessuna uscita a tempo
    descrizione: Dict = field(default_factory=dict)


class Preparata:
    """Gli array della variante su una serie, e le fabbriche delle tre strategie."""

    def __init__(self, v: Variante, s: Dict, solo_da_ts: Optional[int] = None):
        self.v, self.s = v, s
        p = v.prepara(s)
        n = len(s["candele"])
        self.n = n
        self.cond = np.asarray(p["cond"], dtype=bool)
        self.stop = np.asarray(p["stop"], dtype=float)
        self.target = None if p.get("target") is None else np.asarray(p["target"], dtype=float)
        self.uscita = None if p.get("uscita") is None else np.asarray(p["uscita"], dtype=bool)
        self.warmup = int(p["warmup"])
        self.permesso = s["permesso"].copy()
        # in validazione: ingressi solo se la barra d'ingresso (i + 1) e' dopo la fine della costruzione
        self.primo_segnale = self.warmup
        if solo_da_ts is not None:
            ts = s["ts"]
            k = int(np.searchsorted(ts, solo_da_ts))  # prima barra con ts >= solo_da_ts
            self.primo_segnale = max(self.warmup, k - 1)
        self.indice_ts = {int(t): k for k, t in enumerate(s["ts"])}
        ok = np.isfinite(self.stop)
        if self.target is not None:
            ok &= np.isfinite(self.target)
        self.calcolabile = ok
        self.calcolabile[: self.warmup] = False

    def _segnale(self, i: int) -> Optional[Segnale]:
        if i < self.warmup or not self.calcolabile[i]:
            return None
        t = None if self.target is None else float(self.target[i])
        return Segnale(self.v.direzione, float(self.stop[i]), t)

    def _uscita(self, i: int, pos) -> Optional[str]:
        j = self.indice_ts[pos.ts_entrata]
        if self.v.tenuta is not None and i - j + 1 >= self.v.tenuta:
            return "chiudi"
        if self.uscita is not None and self.uscita[i]:
            return "chiudi"
        return None

    def _fabbrica(self, entra: Callable[[int], bool]):
        def crea():
            def strategia(storia, pos):
                i = len(storia) - 1
                if pos is not None:
                    return self._uscita(i, pos)
                if i < self.primo_segnale or not entra(i):
                    return None
                return self._segnale(i)
            return strategia
        return crea

    def crea_candidato(self):
        return self._fabbrica(lambda i: bool(self.cond[i]) and bool(self.permesso[i]))

    def crea_a(self):
        return self._fabbrica(lambda i: bool(self.permesso[i]))

    def crea_casuale(self, ingressi):
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is not None:
                return self._uscita(i, pos)
            if i in ingressi:
                return self._segnale(i)
            return None
        return strategia

    def crea_segnale(self):
        def f(storia):
            return self._segnale(len(storia) - 1)
        return f

    def barre_vietate(self, par: Parametri) -> List:
        vietate = motore.barre_vietate_segnale_non_valido(self.s["candele"], self.crea_segnale, par)
        quota = sum(b - a for a, b in vietate) / self.n
        extra = []
        if self.primo_segnale > 0:
            extra.append((0, self.primo_segnale))
        k = 0
        while k < self.n:
            if not self.permesso[k]:
                a = k
                while k < self.n and not self.permesso[k]:
                    k += 1
                extra.append((a, k))
            else:
                k += 1
        return vietate + extra, quota


# ---------------------------------------------------------------------------
# Misure
# ---------------------------------------------------------------------------


def _anno(ts):
    return datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc).year


def misure_trade(trades: Sequence[motore.Trade], ris: Optional[motore.Risultato]) -> Dict:
    tr = sorted(trades, key=lambda t: t.ts_uscita)
    r = [t.r for t in tr]
    per_anno = {}
    for t in tr:
        per_anno.setdefault(_anno(t.ts_uscita), []).append(t.r)
    vinti = sum(t.pnl for t in tr if t.pnl > 0)
    persi = -sum(t.pnl for t in tr if t.pnl < 0)
    out = {
        "trade": len(tr),
        "r_medio": float(np.mean(r)) if r else 0.0,
        "profit_factor": (vinti / persi) if persi > 0 else (math.inf if vinti > 0 else 0.0),
        "win_rate": float(np.mean([t.pnl > 0 for t in tr])) if tr else 0.0,
        "r_medio_per_anno": {a: float(np.mean(v)) for a, v in per_anno.items()},
        "trade_per_anno": {a: len(v) for a, v in per_anno.items()},
        "r_medio_senza_3_migliori": float(np.mean(sorted(r)[:-3])) if len(r) > 3 else None,
        "esiti": {e: sum(1 for t in tr if t.esito == e) for e in ("stop", "target", "segnale", "liquidazione", "fine_dati")},
        "n_ridotti": sum(1 for t in tr if t.ridotto),
        "n_violazioni_liquidazione": sum(1 for t in tr if t.violazione_liquidazione),
        "rendimento_totale": sum(t.pnl_pct for t in tr),
        "funding_totale_r": float(sum(t.funding_pagato / t.rischio_iniziale for t in tr if t.rischio_iniziale > 0)),
        "stop_oltre_6pct": sum(1 for t in tr if abs(t.entrata - t.stop) / t.entrata > 0.06),
        "durata_media_ore": float(np.mean([(t.ts_uscita - t.ts_entrata) / 3.6e6 for t in tr])) if tr else 0.0,
    }
    if ris is not None:
        m = motore.calcola_metriche(motore.Risultato(tr, ris.curva_capitale, ris.capitale_iniziale, ris.capitale_finale))
        out["drawdown_max"] = m["drawdown_max"]
        out["rendimento_per_anno"] = m["rendimento_per_anno"]
        out["n_buchi_dati"] = ris.n_buchi_dati
        out["n_funding_in_buco"] = ris.n_funding_in_buco
        out["n_segnali_non_validi"] = ris.n_segnali_non_validi
    return out


def buy_and_hold_per_anno(s: Dict, par: Parametri, da_ts: Optional[int] = None) -> Dict:
    out = {}
    per_anno: Dict[int, List[Candela]] = {}
    for c in s["candele"]:
        if da_ts is not None and c.ts < da_ts:
            continue
        per_anno.setdefault(_anno(c.ts), []).append(c)
    for a, cs in per_anno.items():
        out[a] = {"long": motore.buy_and_hold(cs, par, "long"), "short": motore.buy_and_hold(cs, par, "short")}
    return out


def blocco_di(trades) -> int:
    tr = sorted(trades, key=lambda t: t.ts_uscita)
    return statistica.lunghezza_blocco([t.ts_entrata for t in tr], [t.ts_uscita for t in tr])


def _riassunto_b(base: Dict, quota_vietate: float) -> Dict:
    return {
        "media": base["media"], "errore_standard": base["errore_standard"],
        "errore_minimo_candidato": base["errore_minimo_candidato"], "n_simulazioni": base["n_simulazioni"],
        "trade_per_simulazione_medio": float(np.mean(base["trade_per_simulazione"])),
        "simulazioni_vuote": base["simulazioni_vuote"],
        "segnali_non_validi_medi": float(np.mean(base["segnali_non_validi_per_simulazione"])),
        "quota_barre_vietate_segnale_non_valido": quota_vietate,
        "percentile_90": base["percentile_90"],
    }


def _riassunto_confronto(c: Dict) -> Dict:
    return {k: c[k] for k in ("differenza", "errore_standard", "errore_candidato", "errore_minimo", "t", "soglia",
                              "netta", "valutabile", "p_value", "n_blocchi", "gradi_liberta")}


def valuta(v: Variante, s: Dict, par: Parametri, solo_da_ts: Optional[int] = None) -> Dict:
    """Test completo di una variante su una serie: candidato, (a), (b), confronti e misure.

    ``solo_da_ts``: in validazione, contano solo i trade entrati da quell'istante e la (b)
    entra solo in quelle barre; la (a) idem.
    """
    prep = Preparata(v, s, solo_da_ts)
    c, m, f = s["candele"], s["mark"], s["funding"]
    ris = motore.esegui(c, None, m, f, prep.crea_candidato()(), par)
    trades = [t for t in ris.trades if solo_da_ts is None or t.ts_entrata >= solo_da_ts]
    out = {"metriche": misure_trade(trades, ris)}
    if len(trades) < 2:
        out["esito"] = "troppo_pochi_trade"
        return out
    trades_o = sorted(trades, key=lambda t: t.ts_uscita)
    r = [t.r for t in trades_o]
    b = blocco_di(trades_o)
    out["blocco"] = b
    # (a)
    ris_a = motore.esegui(c, None, m, f, prep.crea_a()(), par)
    ta = sorted([t for t in ris_a.trades if solo_da_ts is None or t.ts_entrata >= solo_da_ts], key=lambda t: t.ts_uscita)
    if len(ta) >= 2:
        ba = blocco_di(ta)
        base_a = statistica.baseline_da_trade([t.r for t in ta], ba, n=2000, seme=0)
        conf_a = statistica.contro_baseline(r, b, base_a, n=2000, seme=0)
        out["baseline_a"] = dict(media=base_a["media"], errore_standard=base_a["errore_standard"],
                                 n_trade=base_a["n_trade"], blocco=ba, n_blocchi_a=base_a["n_blocchi"],
                                 **_riassunto_confronto(conf_a))
    else:
        out["baseline_a"] = {"valutabile": False, "netta": False, "t": -math.inf, "n_trade": len(ta)}
    # (b)
    vietate, quota = prep.barre_vietate(par)
    durata = motore.durata_media_barre(trades_o, s["ms"])
    try:
        base_b = motore.simula_baseline_casuale(c, prep.crea_casuale, len(trades_o), durata, par,
                                                candele_mark=m, funding=f, barre_vietate=vietate,
                                                n_simulazioni=200, primo_seme=0)
        # in validazione: R medi delle simulazioni solo sui trade entrati dopo la costruzione
        conf_b = statistica.contro_baseline(r, b, base_b, n=2000, seme=0)
        out["baseline_b"] = dict(durata_media_barre=durata, **_riassunto_b(base_b, quota), **_riassunto_confronto(conf_b))
        out["percentile_caso"] = statistica.percentile_del_candidato(float(np.mean(r)), base_b["valori"])
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "netta": False, "t": -math.inf, "errore": str(e)}
        out["percentile_caso"] = None
    out["buy_and_hold_per_anno"] = buy_and_hold_per_anno(s, par, solo_da_ts)
    a_ok = out["baseline_a"].get("valutabile", False)
    b_ok = out["baseline_b"].get("valutabile", False)
    out["valutabile"] = bool(a_ok and b_ok)
    out["candidato"] = bool(out["valutabile"] and out["baseline_a"]["netta"] and out["baseline_b"]["netta"]
                            and out["metriche"]["r_medio"] > 0)
    out["t_contro_b"] = out["baseline_b"].get("t", -math.inf) if out["valutabile"] else -math.inf
    return out


def conta(v: Variante, par: Optional[Parametri] = None) -> Dict:
    """conta_trade sulle regole esatte della variante, sui dati di costruzione."""
    par = par or parametri()
    s = serie(v.tf)
    prep = Preparata(v, s)
    return motore.conta_trade(s["candele"], prep.crea_candidato(), FINE_COSTRUZIONE_TS, par,
                              candele_mark=s["mark"], funding=s["funding"])
