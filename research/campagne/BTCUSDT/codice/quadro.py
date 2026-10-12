"""Il banco di prova comune a tutte le varianti della campagna BTCUSDT.

Una variante si descrive con quattro pezzi, tutti funzioni delle sole barre chiuse:

* ``prepara(candele, extra)``: calcola una volta gli indicatori CAUSALI (ogni valore
  alla barra i usa solo le barre 0..i) e restituisce un dizionario ts -> valori;
* ``condizione(stato, storia)``: True/False se la condizione d'ingresso (con i filtri)
  vale alla chiusura della barra; None se non si puo' ancora calcolare (riscaldamento);
* ``segnale(stato, storia)``: il Segnale (direzione, stop, target) che la variante
  emetterebbe, SENZA la condizione d'ingresso; None se non calcolabile;
* ``uscita(stato, storia, pos)``: "chiudi" o None, l'uscita oltre stop e target.

Da qui si costruiscono, sempre con fabbriche nuove a ogni esecuzione (sezione 7):
la strategia della variante, la baseline (a) (entra a ogni barra libera), la
strategia casuale della (b) e il calcolo del segnale per le barre vietate.

Gli indicatori sono precalcolati per velocita' ma letti per ``ts`` della barra
appena chiusa: la strategia non puo' leggere un valore di una barra futura perche'
il ts che usa e' quello di ``storia[-1]``. La causalita' del calcolo stesso la
verifica il controllo positivo (lookahead dichiarato) e, per ogni candidato, il test
del ritardo.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Callable, Dict, List, Optional

import numpy as np

from comune import PERIODI, PRIMO_GIORNO, SIMBOLO, dati, motore, parametri
from research.src import statistica

MS = {"15m": 900_000, "30m": 1_800_000, "1h": 3_600_000, "2h": 7_200_000, "4h": 14_400_000,
      "6h": 21_600_000, "8h": 28_800_000, "12h": 43_200_000, "1d": 86_400_000}

# Mesi sotto la liquidita' minima (Fase 0): nessuno per BTCUSDT (fase0_dati.md).
MESI_ESCLUSI: List[str] = []


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------

_CACHE: Dict[tuple, tuple] = {}


def carica(tf: str, fine: date):
    """Candele last e mark allineate (intersezione delle barre) e funding, da PRIMO_GIORNO a ``fine``."""
    chiave = (tf, fine)
    if chiave in _CACHE:
        return _CACHE[chiave]
    last = dati.carica_candele(SIMBOLO, tf, PRIMO_GIORNO, fine)
    mark = dati.carica_candele(SIMBOLO, tf, PRIMO_GIORNO, fine, tipo="markPriceKlines")
    comuni = {c.ts for c in last} & {c.ts for c in mark}
    last = [c for c in last if c.ts in comuni]
    mark = [c for c in mark if c.ts in comuni]
    # I settlement nei file hanno fino a 47 ms di ritardo sull'ora piena (fase0_dati.md):
    # si riportano al minuto, cosi' il motore riconosce i settlement all'apertura di una
    # barra (momenti ambigui, sezione 7) invece di attribuirli alla barra intera.
    funding = [(t - t % 60_000, r) for t, r in dati.carica_funding(SIMBOLO, PRIMO_GIORNO, fine)]
    _CACHE[chiave] = (last, mark, funding)
    return _CACHE[chiave]


def costruzione(tf: str):
    return carica(tf, PERIODI["fine_costruzione"])


def tutto_insample(tf: str):
    return carica(tf, PERIODI["fine_validazione"])


def extra_csv(tf: str, fine: date) -> Dict[int, tuple]:
    """ts -> (quote_volume, taker_buy_volume, taker_buy_quote_volume, count) dai CSV klines."""
    fuori: Dict[int, tuple] = {}
    for anno, mese in dati.mesi_del_periodo(PRIMO_GIORNO, fine):
        p = dati.percorso_mese(SIMBOLO, "klines", tf, anno, mese)
        if not p.is_file():
            continue
        for r in dati.righe_csv_da_zip(p):
            ts = dati.normalizza_ts(r[0])
            fuori.setdefault(ts, (float(r[7]), float(r[9]), float(r[10]), float(r[8])))
    return fuori


def mese_escluso(ts: int) -> bool:
    if not MESI_ESCLUSI:
        return False
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return f"{d.year:04d}-{d.month:02d}" in MESI_ESCLUSI


# ---------------------------------------------------------------------------
# La variante
# ---------------------------------------------------------------------------


@dataclass
class Variante:
    id: str
    tf: str
    direzione: str
    prepara: Callable
    condizione: Callable
    segnale: Callable
    uscita: Callable
    descrizione: Dict = field(default_factory=dict)

    # -- fabbriche: un'istanza nuova a ogni esecuzione del motore -----------------
    def _stato(self, candele):
        return self.prepara(candele)

    def fabbrica(self, candele) -> Callable[[], motore.Strategia]:
        def crea():
            stato = self._stato(candele)

            def strategia(storia, pos):
                if pos is not None:
                    return self.uscita(stato, storia, pos)
                if mese_escluso(storia[-1].ts):
                    return None
                c = self.condizione(stato, storia)
                if not c:
                    return None
                return self.segnale(stato, storia)
            return strategia
        return crea

    def fabbrica_a(self, candele) -> Callable[[], motore.Strategia]:
        """Baseline (a): senza condizione d'ingresso e filtri, entra a ogni barra libera
        da quando la variante puo' entrare (la sua condizione e' calcolabile)."""
        def crea():
            stato = self._stato(candele)

            def strategia(storia, pos):
                if pos is not None:
                    return self.uscita(stato, storia, pos)
                if mese_escluso(storia[-1].ts):
                    return None
                if self.condizione(stato, storia) is None:
                    return None
                return self.segnale(stato, storia)
            return strategia
        return crea

    def fabbrica_casuale(self, candele) -> Callable[[frozenset], motore.Strategia]:
        def crea(ingressi):
            stato = self._stato(candele)

            def strategia(storia, pos):
                if pos is not None:
                    return self.uscita(stato, storia, pos)
                if len(storia) - 1 in ingressi:
                    return self.segnale(stato, storia)
                return None
            return strategia
        return crea

    def fabbrica_segnale(self, candele):
        """Per le barre vietate della (b): il segnale dove la variante potrebbe entrare."""
        def crea():
            stato = self._stato(candele)

            def calcola(storia):
                if mese_escluso(storia[-1].ts):
                    return None
                if self.condizione(stato, storia) is None:
                    return None
                return self.segnale(stato, storia)
            return calcola
        return crea


# ---------------------------------------------------------------------------
# Metriche e confronto
# ---------------------------------------------------------------------------


def _anno(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year


def metriche_trade(trades, ris: Optional[motore.Risultato] = None) -> Dict:
    trades = sorted(trades, key=lambda t: t.ts_uscita)
    r = [t.r for t in trades]
    n = len(r)
    pf = statistica.profit_factor([t.pnl for t in trades])
    per_anno: Dict[str, List[float]] = {}
    for t in trades:
        per_anno.setdefault(str(_anno(t.ts_uscita)), []).append(t.r)
    senza3 = sorted(r)[:-3] if n > 3 else []
    m = {
        "profit_factor": round(pf, 4) if math.isfinite(pf) else "inf",
        "trade": n,
        "r_medio": round(float(np.mean(r)), 4) if n else 0.0,
        "r_medio_per_anno": {a: round(float(np.mean(v)), 4) for a, v in sorted(per_anno.items())},
        "trade_per_anno": {a: len(v) for a, v in sorted(per_anno.items())},
        "r_medio_senza_3_migliori": round(float(np.mean(senza3)), 4) if senza3 else None,
        "win_rate": round(statistica.win_rate([t.pnl for t in trades]), 4),
        "esiti": {e: sum(1 for t in trades if t.esito == e) for e in ("stop", "target", "segnale", "liquidazione", "fine_dati")},
        "ridotti_tetto_leva": sum(1 for t in trades if t.ridotto),
        "violazioni_liquidazione": sum(1 for t in trades if t.violazione_liquidazione),
        "stop_oltre_6_per_cento": sum(1 for t in trades if abs(t.entrata - t.stop) / t.entrata > 0.06),
        "durata_media_ore": round(float(np.mean([(t.ts_uscita - t.ts_entrata) / 3_600_000 for t in trades])), 2) if n else 0.0,
    }
    if ris is not None:
        mm = motore.calcola_metriche(ris)
        m["drawdown_max"] = round(mm["drawdown_max"], 4)
        m["rendimento_totale"] = round(mm["rendimento_totale"], 4)
        m["rendimento_per_anno"] = {str(a): round(v, 4) for a, v in mm["rendimento_per_anno"].items()}
        m["buchi_dati"] = mm["n_buchi_dati"]
        m["segnali_non_validi"] = mm["n_segnali_non_validi"]
    return m


def buy_and_hold_per_anno(candele, par) -> Dict:
    anni: Dict[int, list] = {}
    for c in candele:
        anni.setdefault(_anno(c.ts), []).append(c)
    return {str(a): {"long": round(motore.buy_and_hold(cs, par, "long"), 4),
                     "short": round(motore.buy_and_hold(cs, par, "short"), 4)} for a, cs in sorted(anni.items())}


def _ridotto(d: Dict, chiavi) -> Dict:
    out = {}
    for k in chiavi:
        v = d.get(k)
        if isinstance(v, float):
            v = round(v, 5) if math.isfinite(v) else ("inf" if v > 0 else "-inf")
        out[k] = v
    return out


CHIAVI_CONFRONTO = ("differenza", "errore_standard", "errore_candidato", "errore_minimo", "t", "soglia", "netta",
                    "valutabile", "n_blocchi", "p_value", "baseline_media", "baseline_errore_standard")


def valuta_costruzione(v: Variante, par=None, tf: Optional[str] = None, n_sim: int = 200) -> Dict:
    """Test di una variante sui dati di costruzione: metriche, baseline (a) e (b), contesto."""
    par = par or parametri()
    tf = tf or v.tf
    candele, mark, funding = costruzione(tf)
    ris = motore.esegui(candele, None, mark, funding, v.fabbrica(candele)(), par)
    trades = sorted(ris.trades, key=lambda t: t.ts_uscita)
    out: Dict = {"metriche": metriche_trade(trades, ris)}
    out["buy_and_hold_per_anno"] = buy_and_hold_per_anno(candele, par)
    if len(trades) < 2:
        out["commento_motore"] = "meno di 2 trade"
        return out
    r = [t.r for t in trades]
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    out["blocco"] = blocco

    # baseline (a)
    ris_a = motore.esegui(candele, None, mark, funding, v.fabbrica_a(candele)(), par)
    ta = sorted(ris_a.trades, key=lambda t: t.ts_uscita)
    if len(ta) >= 2:
        blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in ta], [t.ts_uscita for t in ta])
        base_a = statistica.baseline_da_trade([t.r for t in ta], blocco_a)
        cmp_a = statistica.contro_baseline(r, blocco, base_a)
        out["baseline_a"] = dict(media=round(base_a["media"], 5), n_trade=base_a["n_trade"], blocco=blocco_a,
                                 **_ridotto(cmp_a, CHIAVI_CONFRONTO))
    else:
        out["baseline_a"] = {"valutabile": False, "motivo": "meno di 2 trade nella (a)", "t": "-inf", "netta": False}

    # baseline (b)
    durata = motore.durata_media_barre(trades, MS[tf])
    vietate = motore.barre_vietate_segnale_non_valido(candele, v.fabbrica_segnale(candele), par)
    n_vietate = sum(b - a for a, b in vietate)
    try:
        base_b = motore.simula_baseline_casuale(candele, v.fabbrica_casuale(candele), len(trades), durata, par,
                                                None, mark, funding, vietate, n_simulazioni=n_sim)
        cmp_b = statistica.contro_baseline(r, blocco, base_b)
        tps = base_b["trade_per_simulazione"]
        out["baseline_b"] = dict(media=round(base_b["media"], 5), n_simulazioni=base_b["n_simulazioni"],
                                 trade_per_simulazione_medio=round(float(np.mean(tps)), 2),
                                 simulazioni_vuote=base_b["simulazioni_vuote"],
                                 segnali_scartati_per_simulazione_medio=round(float(np.mean(base_b["segnali_non_validi_per_simulazione"])), 3),
                                 quota_barre_vietate_segnale=round(n_vietate / len(candele), 4),
                                 durata_media_barre=durata,
                                 **_ridotto(cmp_b, CHIAVI_CONFRONTO))
        out["percentile_caso"] = round(statistica.percentile_del_candidato(float(np.mean(r)), base_b["valori"]), 2)
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "motivo": str(e), "t": "-inf", "netta": False,
                             "durata_media_barre": durata, "quota_barre_vietate_segnale": round(n_vietate / len(candele), 4)}
    a_ok = out["baseline_a"].get("valutabile") and out["baseline_a"].get("netta")
    b_ok = out["baseline_b"].get("valutabile") and out["baseline_b"].get("netta")
    out["candidato"] = bool(a_ok and b_ok and float(np.mean(r)) > 0)
    out["valutabile"] = bool(out["baseline_a"].get("valutabile") and out["baseline_b"].get("valutabile"))
    return out


def conta(v: Variante, par=None, tf: Optional[str] = None) -> Dict:
    """La stima dei trade (sezione 8): conta_trade, una volta, sulle regole registrate."""
    par = par or parametri()
    tf = tf or v.tf
    candele, mark, funding = costruzione(tf)
    return motore.conta_trade(candele, v.fabbrica(candele), PERIODI["fine_costruzione_ts"], par,
                              None, mark, funding)


# ---------------------------------------------------------------------------
# Aiuti per gli indicatori (causali)
# ---------------------------------------------------------------------------


def arr(candele, campo):
    return np.array([getattr(c, campo) for c in candele], dtype=float)


def sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(x.size, np.nan)
    if x.size >= n:
        c = np.cumsum(np.insert(x, 0, 0.0))
        out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def ema(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(x.size, np.nan)
    if x.size < n:
        return out
    a = 2.0 / (n + 1)
    out[n - 1] = x[:n].mean()
    for i in range(n, x.size):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def atr(candele, n: int) -> np.ndarray:
    h, l, c = arr(candele, "high"), arr(candele, "low"), arr(candele, "close")
    tr = np.empty(h.size)
    tr[0] = h[0] - l[0]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    out = np.full(h.size, np.nan)
    if h.size >= n:
        out[n - 1] = tr[:n].mean()
        for i in range(n, h.size):  # media di Wilder
            out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def rsi(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(x.size, np.nan)
    if x.size <= n:
        return out
    d = np.diff(x)
    su, giu = np.maximum(d, 0), np.maximum(-d, 0)
    ms, mg = su[:n].mean(), giu[:n].mean()
    out[n] = 100 if mg == 0 else 100 - 100 / (1 + ms / mg)
    for i in range(n + 1, x.size):
        ms = (ms * (n - 1) + su[i - 1]) / n
        mg = (mg * (n - 1) + giu[i - 1]) / n
        out[i] = 100 if mg == 0 else 100 - 100 / (1 + ms / mg)
    return out


def massimo_precedente(x: np.ndarray, n: int) -> np.ndarray:
    """Massimo delle n barre PRIMA della barra i (esclusa la barra i)."""
    out = np.full(x.size, np.nan)
    for i in range(n, x.size):
        out[i] = x[i - n:i].max()
    return out


def minimo_precedente(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(x.size, np.nan)
    for i in range(n, x.size):
        out[i] = x[i - n:i].min()
    return out


def per_ts(candele, **serie) -> Dict[int, Dict[str, float]]:
    """ts -> {nome: valore} per ogni barra."""
    nomi = list(serie)
    return {c.ts: {k: float(serie[k][i]) for k in nomi} for i, c in enumerate(candele)}


def barre_tenute(storia, pos, ms_barra: int) -> int:
    """Barre chiuse da quando la posizione e' aperta (1 alla chiusura della barra d'ingresso)."""
    return (storia[-1].ts - pos.ts_entrata) // ms_barra + 1


def nan(x) -> bool:
    return x is None or (isinstance(x, float) and math.isnan(x))
