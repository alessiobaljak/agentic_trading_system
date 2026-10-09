"""Quadro comune delle varianti di MATICUSDT: dati, strategie, baseline e misure del log.

Una variante e' descritta da un oggetto ``Regole`` costruito su una ``Serie`` (gli array
del timeframe, calcolati una volta su tutte le barre passate al motore, ma CAUSALI: il valore
all'indice i usa solo le barre 0..i). Il motore chiama la strategia alla chiusura della barra
i con le barre 0..i: la strategia legge gli array all'indice ``len(storia) - 1``.

Da ``Regole`` si costruiscono, sempre con una fabbrica che crea un'istanza nuova
(sezione 7):
* la strategia della variante (``crea``): ingresso se la barra non e' vietata dal filtro di
  liquidita' della Fase 0, la condizione d'ingresso e' vera e il segnale (stop, target) si
  puo' calcolare; uscita con la sua uscita (tempo massimo e/o uscita a segnale);
* la baseline (a) (``crea_a``): stessa direzione, uscita, stop e target, senza la condizione
  d'ingresso e senza filtri dell'ipotesi; il filtro di liquidita' della Fase 0 resta
  (fase0_dati.md: vale anche per la (a));
* la strategia casuale della (b) (``crea_casuale(ingressi)``): alla chiusura delle barre in
  ``ingressi`` emette il segnale della variante, poi esce con la sua uscita;
* il calcolo del segnale senza condizione (``crea_segnale``) per
  ``barre_vietate_segnale_non_valido``.

I parametri del motore si leggono da ``config/parametri.yaml`` e dalla scheda (slippage
0,02% per lato).
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
import yaml

RADICE_REPO = Path(__file__).resolve().parents[4]
if str(RADICE_REPO) not in sys.path:
    sys.path.insert(0, str(RADICE_REPO))

from research.src import dati, motore, statistica  # noqa: E402
from research.src.motore import Candela, Parametri, Segnale  # noqa: E402

SIMBOLO = "MATICUSDT"
INIZIO = date(2020, 10, 1)
FINE_COSTRUZIONE = date(2023, 1, 8)
FINE_VALIDAZIONE = date(2023, 12, 31)
FINE_COSTRUZIONE_TS = 1673222399999
INIZIO_VALIDAZIONE_TS = 1673222400000
SLIPPAGE_SCHEDA = 0.0002
MESI_ILLIQUIDI = {(2020, 10), (2020, 11), (2020, 12), (2021, 1)}  # fase0_dati.md
TRADE_MINIMI_COSTRUZIONE = 70
TRADE_MINIMI_VALIDAZIONE = 30


def _yaml() -> dict:
    return yaml.safe_load((RADICE_REPO / "research" / "config" / "parametri.yaml").read_text(encoding="utf-8"))


_P = _yaml()
_R = _P["fatti"]["regole_dimensione_bot"]
_E = _P["regole_esame"]
N_SIMULAZIONI = int(_E["simulazioni_baseline_casuale"])
PRIMO_SEME = int(_E["semi_baseline_casuale"]["primo"])
BOOT_N = int(_E["bootstrap"]["ricampionamenti"])
BOOT_SEME = int(_E["bootstrap"]["seme"])


def parametri(moltiplicatore_costi: float = 1.0, ritardo: int = 0, intrabarra: str = "stop_prima") -> Parametri:
    """Parametri del motore da parametri.yaml e dalla scheda della moneta."""
    return Parametri(
        commissione_per_lato=float(_P["fatti"]["commissione_taker_per_lato"]["valore"]),
        slippage_per_lato=SLIPPAGE_SCHEDA,
        rischio_per_trade=float(_R["rischio_per_trade"]),
        leva_max=float(_R["leva_max"]),
        modalita_margine=_R["modalita_margine_proposta"],
        tasso_margine_mantenimento=float(_R["tasso_margine_mantenimento"]),
        margine_minimo_da_liquidazione=float(_E["margine_minimo_da_liquidazione"]),
        capitale_iniziale=float(_R["capitale_iniziale"]),
        riempimento_intrabarra=intrabarra,
        moltiplicatore_costi=moltiplicatore_costi,
        ritardo_barre=ritardo,
    )


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------


@dataclass
class Serie:
    tf: str
    periodo: str
    candele: List[Candela]
    mark: List[Candela]
    funding: List[Tuple[int, float]]
    ms_barra: int
    ts: np.ndarray
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray
    v: np.ndarray  # volume in moneta base
    qv: np.ndarray  # volume in USDT (quote_volume)
    btc_c: np.ndarray  # close di BTCUSDT sullo stesso ts (nan se manca)
    btc_o: np.ndarray
    vietato: np.ndarray  # True: barra di segnale in un mese sotto la liquidita' minima
    indice_di_ts: Dict[int, int] = field(default_factory=dict)

    @property
    def n(self) -> int:
        return len(self.candele)


_CACHE: Dict[Tuple[str, str], Serie] = {}


def carica(tf: str, periodo: str = "costruzione") -> Serie:
    """Last e mark allineati (``carica_serie_allineate``), funding e BTCUSDT, fino alla fine del periodo.

    ``periodo`` = "costruzione" (fino al 2023-01-08) oppure "validazione" (dall'inizio al
    2023-12-31: indicatori caldi; contano solo i trade entrati dopo la costruzione).
    """
    chiave = (tf, periodo)
    if chiave in _CACHE:
        return _CACHE[chiave]
    fine = FINE_COSTRUZIONE if periodo == "costruzione" else FINE_VALIDAZIONE
    if periodo not in ("costruzione", "validazione"):
        raise ValueError(periodo)
    s = dati.carica_serie_allineate(SIMBOLO, tf, INIZIO, fine)
    candele, mark = s["candele"], s["candele_mark"]
    funding = dati.carica_funding(SIMBOLO, INIZIO, fine)
    btc = {c.ts: c for c in dati.carica_candele("BTCUSDT", tf, INIZIO, fine)}
    ts = np.array([c.ts for c in candele], dtype=np.int64)
    mesi = [(datetime.fromtimestamp(t / 1000, tz=timezone.utc).year,
             datetime.fromtimestamp(t / 1000, tz=timezone.utc).month) for t in ts]
    serie = Serie(
        tf=tf, periodo=periodo, candele=candele, mark=mark, funding=funding,
        ms_barra=dati.durata_intervallo(tf), ts=ts,
        o=np.array([c.open for c in candele]), h=np.array([c.high for c in candele]),
        l=np.array([c.low for c in candele]), c=np.array([c.close for c in candele]),
        v=np.array([c.volume for c in candele]),
        qv=np.array([s["volume_usdt"][c.ts] if s["volume_usdt"][c.ts] is not None else np.nan for c in candele]),
        btc_c=np.array([btc[t].close if t in btc else np.nan for t in ts]),
        btc_o=np.array([btc[t].open if t in btc else np.nan for t in ts]),
        vietato=np.array([m in MESI_ILLIQUIDI for m in mesi]),
    )
    serie.indice_di_ts = {int(t): i for i, t in enumerate(ts)}
    _CACHE[chiave] = serie
    return serie


# ---------------------------------------------------------------------------
# Indicatori causali (valore all'indice i calcolato con le barre 0..i)
# ---------------------------------------------------------------------------


def sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        cs = np.cumsum(np.insert(x.astype(float), 0, 0.0))
        out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def ema(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    a = 2.0 / (n + 1)
    out[n - 1] = x[:n].mean()
    for i in range(n, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def true_range(s: Serie) -> np.ndarray:
    prev = np.concatenate([[np.nan], s.c[:-1]])
    tr = np.maximum(s.h - s.l, np.maximum(np.abs(s.h - prev), np.abs(s.l - prev)))
    tr[0] = s.h[0] - s.l[0]
    return tr


def atr(s: Serie, n: int) -> np.ndarray:
    """ATR di Wilder: media mobile esponenziale con alfa 1/n del true range."""
    tr = true_range(s)
    out = np.full(len(tr), np.nan)
    if len(tr) < n:
        return out
    out[n - 1] = tr[:n].mean()
    for i in range(n, len(tr)):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def rsi(c: np.ndarray, n: int) -> np.ndarray:
    """RSI di Wilder."""
    d = np.diff(c, prepend=np.nan)
    su = np.where(d > 0, d, 0.0)
    giu = np.where(d < 0, -d, 0.0)
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    ms, mg = su[1:n + 1].mean(), giu[1:n + 1].mean()
    for i in range(n, len(c)):
        if i > n:
            ms = (ms * (n - 1) + su[i]) / n
            mg = (mg * (n - 1) + giu[i]) / n
        out[i] = 100.0 if mg == 0 else 100.0 - 100.0 / (1.0 + ms / mg)
    return out


def massimo_precedente(x: np.ndarray, n: int) -> np.ndarray:
    """Massimo delle n barre PRIMA della barra i (i esclusa)."""
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        out[i] = x[i - n:i].max()
    return out


def minimo_precedente(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        out[i] = x[i - n:i].min()
    return out


def rendimento(c: np.ndarray, n: int) -> np.ndarray:
    """c[i] / c[i-n] - 1."""
    out = np.full(len(c), np.nan)
    out[n:] = c[n:] / c[:-n] - 1.0
    return out


def dev_std_mobile(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = x[i - n + 1:i + 1].std(ddof=1)
    return out


def ora_utc(s: Serie) -> np.ndarray:
    return ((s.ts // 3_600_000) % 24).astype(int)


def minuto_del_giorno(s: Serie) -> np.ndarray:
    return ((s.ts // 60_000) % 1440).astype(int)


def giorno_settimana(s: Serie) -> np.ndarray:
    """0 = lunedi' (il 1970-01-01 era un giovedi')."""
    return (((s.ts // 86_400_000) + 3) % 7).astype(int)


# ---------------------------------------------------------------------------
# Regole di una variante e fabbriche delle strategie
# ---------------------------------------------------------------------------


@dataclass
class Regole:
    """Una variante completa: direzione, condizione d'ingresso, stop/target e uscita.

    * ``ingresso[i]``: la condizione d'ingresso dell'ipotesi (con i suoi filtri) alla chiusura di i;
    * ``stop[i]``, ``target[i]``: livelli calcolati alla chiusura di i (target nan = nessun target);
      nan in ``stop`` vuol dire segnale non calcolabile (riscaldamento);
    * ``tenuta``: numero massimo di barre in posizione (``None`` = nessun limite);
    * ``uscita[i]``: uscita a segnale alla chiusura di i (``None`` = nessuna).
    """

    serie: Serie
    direzione: str
    ingresso: np.ndarray
    stop: np.ndarray
    target: Optional[np.ndarray] = None
    tenuta: Optional[int] = None
    uscita: Optional[np.ndarray] = None
    descrizione: str = ""

    def __post_init__(self) -> None:
        n = self.serie.n
        self._ingresso = [bool(x) for x in np.nan_to_num(self.ingresso.astype(float), nan=0.0)]
        self._stop = [float(x) for x in self.stop]
        self._target = [float(x) for x in self.target] if self.target is not None else [math.nan] * n
        self._uscita = [bool(x) for x in self.uscita] if self.uscita is not None else None
        self._vietato = [bool(x) for x in self.serie.vietato]
        self._idx = self.serie.indice_di_ts
        for nome, arr in (("ingresso", self.ingresso), ("stop", self.stop)):
            if len(arr) != n:
                raise ValueError(f"{nome}: lunghezza {len(arr)} invece di {n}")

    def segnale(self, i: int) -> Optional[Segnale]:
        st = self._stop[i]
        if math.isnan(st):
            return None
        tg = self._target[i]
        return Segnale(self.direzione, st, None if math.isnan(tg) else tg)

    def _gestisci(self, i: int, pos) -> Optional[str]:
        k = self._idx[pos.ts_entrata]
        if self.tenuta is not None and i - k + 1 >= self.tenuta:
            return "chiudi"
        if self._uscita is not None and self._uscita[i]:
            return "chiudi"
        return None

    def crea(self) -> Callable:
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is None:
                if self._vietato[i] or not self._ingresso[i]:
                    return None
                return self.segnale(i)
            return self._gestisci(i, pos)
        return strategia

    def crea_a(self) -> Callable:
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is None:
                if self._vietato[i]:
                    return None
                return self.segnale(i)
            return self._gestisci(i, pos)
        return strategia

    def crea_casuale(self, ingressi: frozenset) -> Callable:
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is None:
                return self.segnale(i) if i in ingressi else None
            return self._gestisci(i, pos)
        return strategia

    def crea_segnale(self) -> Callable:
        def calcolo(storia):
            return self.segnale(len(storia) - 1)
        return calcolo


# ---------------------------------------------------------------------------
# Esecuzione, baseline e misure
# ---------------------------------------------------------------------------


def _intervalli_da_maschera(maschera: Sequence[bool]) -> List[Tuple[int, int]]:
    out: List[Tuple[int, int]] = []
    for i, m in enumerate(maschera):
        if m:
            if out and out[-1][1] == i:
                out[-1] = (out[-1][0], i + 1)
            else:
                out.append((i, i + 1))
    return out


def conta(fabbrica_regole: Callable[[Serie], Regole], tf: str) -> Dict[str, int]:
    """La stima dei trade della sezione 8 (``conta_trade``) sui dati di costruzione."""
    s = carica(tf, "costruzione")
    reg = fabbrica_regole(s)
    return motore.conta_trade(s.candele, reg.crea, FINE_COSTRUZIONE_TS, parametri(),
                              candele_mark=s.mark, funding=s.funding)


def _anno(ts_ms: int) -> int:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).year


def _r_per_anno(trades) -> Dict[str, Dict[str, float]]:
    per: Dict[int, List[float]] = {}
    for t in trades:
        per.setdefault(_anno(t.ts_uscita), []).append(t.r)
    return {str(a): {"r_medio": round(float(np.mean(v)), 4), "trade": len(v)} for a, v in sorted(per.items())}


def _buy_and_hold_per_anno(s: Serie, da_ts: int, a_ts: int) -> Dict[str, Dict[str, float]]:
    p = parametri()
    out = {}
    anni = sorted({_anno(int(t)) for t in s.ts if da_ts <= t <= a_ts})
    for a in anni:
        cand = [c for c in s.candele if da_ts <= c.ts <= a_ts and _anno(c.ts) == a]
        if len(cand) < 2:
            continue
        out[str(a)] = {"long": round(motore.buy_and_hold(cand, p, "long"), 4),
                       "short": round(motore.buy_and_hold(cand, p, "short"), 4)}
    return out


def _sintesi_confronto(c: Dict[str, object]) -> Dict[str, object]:
    chiavi = ("t", "soglia", "netta", "valutabile", "differenza", "errore_standard", "errore_minimo",
              "errore_candidato", "n_blocchi", "p_value", "baseline_media", "baseline_errore_standard")
    out = {}
    for k in chiavi:
        v = c.get(k)
        if isinstance(v, float):
            v = None if math.isinf(v) or math.isnan(v) else round(v, 5)
        out[k] = v
    return out


def valuta(fabbrica_regole: Callable[[Serie], Regole], tf: str, periodo: str = "costruzione",
           moltiplicatore_costi: float = 1.0, ritardo: int = 0, intrabarra: str = "stop_prima",
           con_baseline_a: bool = True) -> Dict[str, object]:
    """Il risultato completo di una variante (sezione 6), su costruzione o validazione.

    In validazione la serie va dall'inizio alla fine del 2023 e contano solo i trade
    entrati dopo la costruzione; le barre di costruzione sono vietate alla (b).
    """
    s = carica(tf, periodo)
    p = parametri(moltiplicatore_costi, ritardo, intrabarra)
    reg = fabbrica_regole(s)
    ris = motore.esegui(s.candele, None, s.mark, s.funding, reg.crea(), p)
    trades = sorted(ris.trades, key=lambda t: t.ts_uscita)
    if periodo == "validazione":
        trades = [t for t in trades if t.ts_entrata > FINE_COSTRUZIONE_TS]
        da_ts, a_ts = INIZIO_VALIDAZIONE_TS, int(s.ts[-1])
    else:
        da_ts, a_ts = int(s.ts[0]), int(s.ts[-1])
    out: Dict[str, object] = {"timeframe": tf, "periodo": periodo, "moltiplicatore_costi": moltiplicatore_costi,
                              "ritardo_barre": ritardo, "intrabarra": intrabarra}
    n = len(trades)
    rs = [t.r for t in trades]
    pnl = [t.pnl for t in trades]
    vinti = sum(x for x in pnl if x > 0)
    persi = -sum(x for x in pnl if x < 0)
    # drawdown e rendimento sui soli trade del periodo, capitale che parte da 1000
    cap = p.capitale_iniziale
    curva = [(da_ts, cap)]
    for t in trades:
        cap += t.pnl
        curva.append((t.ts_uscita, cap))
    metriche = {
        "trade": n,
        "profit_factor": (round(vinti / persi, 4) if persi > 0 else None),
        "r_medio": round(float(np.mean(rs)), 5) if n else None,
        "r_medio_per_anno": _r_per_anno(trades),
        "r_medio_senza_3_migliori": round(float(np.mean(sorted(rs)[:-3])), 5) if n > 3 else None,
        "win_rate": round(sum(1 for x in pnl if x > 0) / n, 4) if n else None,
        "rendimento_totale": round((cap - p.capitale_iniziale) / p.capitale_iniziale, 4),
        "drawdown_max": round(-motore.drawdown_massimo(curva), 4),
        "rendimento_per_anno": {str(a): round(v, 4) for a, v in motore.rendimento_per_anno(trades, p.capitale_iniziale).items()},
        "trade_ridotti_tetto_leva": sum(1 for t in trades if t.ridotto),
        "violazioni_liquidazione": sum(1 for t in trades if t.violazione_liquidazione),
        "esiti": {e: sum(1 for t in trades if t.esito == e) for e in ("stop", "target", "segnale", "liquidazione", "fine_dati")},
        "segnali_non_validi": ris.n_segnali_non_validi,
        "buchi_dati": ris.n_buchi_dati,
        "funding_in_buco": ris.n_funding_in_buco,
        "costi_medi_in_r": round(float(np.mean([(t.commissioni + t.slippage_costo + t.funding_pagato) / t.rischio_iniziale for t in trades])), 4) if n else None,
        "durata_media_barre": motore.durata_media_barre(trades, s.ms_barra) if n else None,
    }
    out["metriche"] = metriche
    out["buy_and_hold_per_anno"] = _buy_and_hold_per_anno(s, da_ts, a_ts)
    out["_trades"] = trades
    if n < 2:
        out["valutabile"] = False
        return out
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    out["blocco"] = blocco

    # baseline (a)
    if con_baseline_a:
        ris_a = motore.esegui(s.candele, None, s.mark, s.funding, reg.crea_a(), p)
        ta = sorted(ris_a.trades, key=lambda t: t.ts_uscita)
        if periodo == "validazione":
            ta = [t for t in ta if t.ts_entrata > FINE_COSTRUZIONE_TS]
        if len(ta) >= 2:
            blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in ta], [t.ts_uscita for t in ta])
            base_a = statistica.baseline_da_trade([t.r for t in ta], blocco_a, n=BOOT_N, seme=BOOT_SEME)
            conf_a = statistica.contro_baseline(rs, blocco, base_a, n=BOOT_N, seme=BOOT_SEME)
            out["baseline_a"] = dict(_sintesi_confronto(conf_a), media=round(base_a["media"], 5),
                                     n_trade=base_a["n_trade"], blocco_a=blocco_a, n_blocchi_a=base_a["n_blocchi"],
                                     valutabile_a=base_a["valutabile"])
        else:
            out["baseline_a"] = {"valutabile": False, "netta": False, "t": None, "n_trade": len(ta)}

    # baseline (b)
    vietate_segnale = motore.barre_vietate_segnale_non_valido(s.candele, reg.crea_segnale, p)
    maschera = list(s.vietato)
    if periodo == "validazione":
        maschera = [m or (int(t) <= FINE_COSTRUZIONE_TS) for m, t in zip(maschera, s.ts)]
    vietate = list(vietate_segnale) + _intervalli_da_maschera(maschera)
    durata = motore.durata_media_barre(trades, s.ms_barra)
    n_vietate = int(np.sum(_maschera_da_intervalli(vietate, s.n)))
    try:
        base_b = motore.simula_baseline_casuale(
            s.candele, reg.crea_casuale, n, durata, p, candele_mark=s.mark, funding=s.funding,
            barre_vietate=vietate, n_simulazioni=N_SIMULAZIONI, primo_seme=PRIMO_SEME)
        conf_b = statistica.contro_baseline(rs, blocco, base_b, n=BOOT_N, seme=BOOT_SEME)
        out["baseline_b"] = dict(
            _sintesi_confronto(conf_b), media=round(base_b["media"], 5), n_simulazioni=base_b["n_simulazioni"],
            trade_per_simulazione_medio=round(float(np.mean(base_b["trade_per_simulazione"])), 1),
            simulazioni_vuote=base_b["simulazioni_vuote"],
            segnali_scartati_per_simulazione_medio=round(float(np.mean(base_b["segnali_non_validi_per_simulazione"])), 2),
            quota_barre_vietate_segnale_non_valido=round(int(np.sum(_maschera_da_intervalli(vietate_segnale, s.n))) / s.n, 4),
            quota_barre_vietate_totale=round(n_vietate / s.n, 4), distanza_ingressi=durata)
        out["percentile_caso"] = round(statistica.percentile_del_candidato(float(np.mean(rs)), base_b["valori"]), 2)
        out["_b"] = base_b
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "netta": False, "t": None, "errore": str(e)}
    a_ok = out.get("baseline_a", {}).get("valutabile", False) if con_baseline_a else True
    b_ok = out["baseline_b"].get("valutabile", False)
    out["valutabile"] = bool(a_ok and b_ok)
    out["candidato"] = bool(out["valutabile"] and out.get("baseline_a", {}).get("netta", False)
                            and out["baseline_b"].get("netta", False) and metriche["r_medio"] > 0)
    return out


def _maschera_da_intervalli(intervalli: Sequence[Tuple[int, int]], n: int) -> np.ndarray:
    m = np.zeros(n, dtype=bool)
    for a, b in intervalli:
        m[max(0, a):min(n, b)] = True
    return m


def per_log(risultato: Dict[str, object]) -> Dict[str, object]:
    """Il risultato senza gli oggetti interni (trade, simulazioni), pronto per il log."""
    return {k: v for k, v in risultato.items() if not k.startswith("_")}
