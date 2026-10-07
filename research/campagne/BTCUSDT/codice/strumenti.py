"""Strumenti della campagna BTCUSDT: indicatori, strategie, esecuzione, baseline, log.

Tutto cio' che serve per provare una variante secondo le sezioni 7 e 8 del
protocollo, costruito SOPRA il motore e la statistica di research/src (che non
si toccano).

Indicatori senza lookahead
--------------------------
``Serie(tf)`` carica le candele del timeframe sull'intero in-sample e
precalcola gli indicatori come array numpy, dove il valore all'indice ``i``
usa SOLO candele con indice <= i (barre gia' chiuse). La strategia, chiamata
dal motore con ``candele[:i+1]``, risale all'indice globale dal ``ts``
dell'ultima candela chiusa e legge l'indicatore li'. Quando il motore gira sul
periodo di costruzione, gli indicatori delle prime barre usano solo prezzi
precedenti dello stesso periodo; sul periodo di validazione usano la coda
della costruzione (prezzi passati: lecito, non sono risultati).

Fabbrica di strategie
---------------------
``strategia_da_regole(serie, entra, uscita)``: ``entra(i)`` ritorna
'long', 'short' o None guardando l'indice globale ``i``; ``uscita`` e' un
dizionario con ``stop_atr`` (stop a k ATR dal close del segnale), ``atr_n``,
``target_atr`` (opzionale), ``max_barre`` (uscita a tempo all'apertura della
barra dopo), ``chiudi_su_opposto`` (uscita quando ``entra`` da' la direzione
opposta), ``chiudi`` (funzione (i, pos) -> bool, opzionale) e ``stop_pct``
(alternativa allo stop in ATR: frazione del close del segnale).

Baseline (sezione 8)
--------------------
(a) ``baseline_incondizionata``: la stessa uscita e direzione su OGNI barra
    ammessa quando si e' flat (l'effetto "su barre qualsiasi, senza la
    condizione dell'ipotesi");
(b) ``baseline_casuale``: entrate casuali (``statistica.entrate_casuali``)
    con la stessa uscita, direzione, numero di trade e durata media del
    candidato, ripetute su piu' semi: distribuzione dell'R medio e serie di R
    della simulazione mediana per il confronto «nettamente»;
(c) buy and hold del periodo (e il suo opposto per gli short).

Blocco del bootstrap: in numero di trade, = ceil(durata massima di una
posizione (almeno 1 giorno) / distanza media fra gli ingressi), almeno 1 e al
massimo n-1 (se tocca il massimo si dichiara ``blocco_ridotto``).
"""
from __future__ import annotations

import json
import math
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

QUI = Path(__file__).resolve().parent
RADICE_REPO = QUI.parents[3]
for p in (str(RADICE_REPO), str(QUI)):
    if p not in sys.path:
        sys.path.insert(0, p)

import dati_btc as d  # noqa: E402
from log import aggiungi  # noqa: E402
from research.src import statistica as st  # noqa: E402
from research.src.motore import Candela, Posizione, Segnale, Trade, buy_and_hold, calcola_metriche, esegui  # noqa: E402

RISULTATI = QUI / "risultati"
GIORNO_MS = 86_400_000


# ---------------------------------------------------------------------------
# Serie e indicatori
# ---------------------------------------------------------------------------


def _rolling_apply(arr: np.ndarray, n: int, fn) -> np.ndarray:
    """fn sulla finestra [i-n+1, i] (NaN finche' la finestra non e' piena)."""
    out = np.full(arr.shape, np.nan)
    if n <= 0 or arr.size < n:
        return out
    finestre = np.lib.stride_tricks.sliding_window_view(arr, n)
    out[n - 1 :] = fn(finestre, axis=1)
    return out


def sma(arr: np.ndarray, n: int) -> np.ndarray:
    return _rolling_apply(arr, n, np.mean)


def rolling_std(arr: np.ndarray, n: int) -> np.ndarray:
    return _rolling_apply(arr, n, lambda w, axis: np.std(w, axis=axis, ddof=1))


def rolling_max(arr: np.ndarray, n: int) -> np.ndarray:
    return _rolling_apply(arr, n, np.max)


def rolling_min(arr: np.ndarray, n: int) -> np.ndarray:
    return _rolling_apply(arr, n, np.min)


def ema(arr: np.ndarray, n: int) -> np.ndarray:
    out = np.full(arr.shape, np.nan)
    if arr.size < n:
        return out
    alpha = 2.0 / (n + 1)
    out[n - 1] = arr[:n].mean()
    for i in range(n, arr.size):
        out[i] = alpha * arr[i] + (1 - alpha) * out[i - 1]
    return out


def shift(arr: np.ndarray, k: int = 1) -> np.ndarray:
    """arr spostato in avanti di k: out[i] = arr[i-k] (NaN all'inizio)."""
    out = np.full(arr.shape, np.nan)
    if k < arr.size:
        out[k:] = arr[: arr.size - k]
    return out


class Serie:
    """Candele di un timeframe sull'intero in-sample, con indicatori causali precalcolati."""

    def __init__(self, tf: str):
        x = d.carica(tf)
        self.tf = tf
        self.last: List[Candela] = x["last"]
        self.mark: List[Candela] = x["mark"]
        self.funding: List[Tuple[int, float]] = x["funding"]
        self.ts = np.array([c.ts for c in self.last], dtype=np.int64)
        self.o = np.array([c.open for c in self.last])
        self.h = np.array([c.high for c in self.last])
        self.l = np.array([c.low for c in self.last])
        self.c = np.array([c.close for c in self.last])
        self.v = np.array([c.volume for c in self.last])
        self.idx: Dict[int, int] = {int(t): i for i, t in enumerate(self.ts)}
        self.durata_ms = int(self.last[0].close_ts - self.last[0].ts + 1)
        self.n = len(self.last)
        self._cache: Dict[str, np.ndarray] = {}
        # ora UTC di apertura e giorno della settimana (0 = lunedi')
        dt = [datetime.fromtimestamp(int(t) / 1000, tz=timezone.utc) for t in self.ts]
        self.ora = np.array([x.hour for x in dt])
        self.minuto = np.array([x.minute for x in dt])
        self.giorno_settimana = np.array([x.weekday() for x in dt])
        self.giorno = np.array([x.toordinal() for x in dt])

    # --- indicatori (tutti causali: il valore in i usa solo <= i) ---
    def true_range(self) -> np.ndarray:
        if "tr" not in self._cache:
            prev_c = shift(self.c, 1)
            tr = np.maximum(self.h - self.l, np.maximum(np.abs(self.h - prev_c), np.abs(self.l - prev_c)))
            tr[0] = self.h[0] - self.l[0]
            self._cache["tr"] = tr
        return self._cache["tr"]

    def atr(self, n: int = 14) -> np.ndarray:
        """ATR di Wilder (media mobile esponenziale 1/n del true range)."""
        k = f"atr{n}"
        if k not in self._cache:
            tr = self.true_range()
            out = np.full(self.n, np.nan)
            if self.n >= n:
                out[n - 1] = tr[:n].mean()
                for i in range(n, self.n):
                    out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
            self._cache[k] = out
        return self._cache[k]

    def rsi(self, n: int = 14) -> np.ndarray:
        k = f"rsi{n}"
        if k not in self._cache:
            delta = np.diff(self.c, prepend=self.c[0])
            su = np.where(delta > 0, delta, 0.0)
            giu = np.where(delta < 0, -delta, 0.0)
            out = np.full(self.n, np.nan)
            if self.n > n:
                ms, mg = su[1 : n + 1].mean(), giu[1 : n + 1].mean()
                out[n] = 100.0 if mg == 0 else 100 - 100 / (1 + ms / mg)
                for i in range(n + 1, self.n):
                    ms = (ms * (n - 1) + su[i]) / n
                    mg = (mg * (n - 1) + giu[i]) / n
                    out[i] = 100.0 if mg == 0 else 100 - 100 / (1 + ms / mg)
            self._cache[k] = out
        return self._cache[k]

    def rendimento(self, n: int = 1) -> np.ndarray:
        """close[i] / close[i-n] - 1."""
        return self.c / shift(self.c, n) - 1

    def max_precedente(self, n: int) -> np.ndarray:
        """Massimo dei high delle n barre PRIMA di i (esclusa i)."""
        return shift(rolling_max(self.h, n), 1)

    def min_precedente(self, n: int) -> np.ndarray:
        return shift(rolling_min(self.l, n), 1)

    def funding_ultimo(self) -> np.ndarray:
        """Tasso dell'ultimo settlement avvenuto entro la CHIUSURA della barra i (NaN prima del primo)."""
        k = "fund_ultimo"
        if k not in self._cache:
            ts_f = np.array([t for t, _ in self.funding], dtype=np.int64)
            tassi = np.array([r for _, r in self.funding])
            close_ts = self.ts + self.durata_ms - 1
            pos = np.searchsorted(ts_f, close_ts, side="right") - 1
            out = np.where(pos >= 0, tassi[np.maximum(pos, 0)], np.nan)
            self._cache[k] = out
        return self._cache[k]

    def funding_settlement_nella_barra(self) -> np.ndarray:
        """True se un settlement cade all'apertura della barra i (ts del settlement == ts della barra)."""
        ts_f = {t for t, _ in self.funding}
        return np.array([int(t) in ts_f for t in self.ts])

    def indice_globale(self, candele: Sequence[Candela]) -> int:
        return self.idx[int(candele[-1].ts)]


# ---------------------------------------------------------------------------
# Fabbrica di strategie
# ---------------------------------------------------------------------------

Entra = Callable[[int], Optional[str]]


def strategia_da_regole(serie: Serie, entra: Entra, uscita: Dict[str, object]):
    """Strategia per il motore: ingresso da ``entra(i)``, uscita dalle regole in ``uscita``."""
    stop_atr = uscita.get("stop_atr")
    stop_pct = uscita.get("stop_pct")
    atr_n = int(uscita.get("atr_n", 14))
    target_atr = uscita.get("target_atr")
    target_pct = uscita.get("target_pct")
    max_barre = uscita.get("max_barre")
    chiudi_su_opposto = bool(uscita.get("chiudi_su_opposto", False))
    chiudi_custom = uscita.get("chiudi")
    atr = serie.atr(atr_n) if (stop_atr is not None or target_atr is not None) else None
    durata = serie.durata_ms

    def strategia(candele: Sequence[Candela], pos: Optional[Posizione]):
        i = serie.idx[int(candele[-1].ts)]
        if pos is not None:
            barre = (int(candele[-1].ts) - pos.ts_entrata) // durata + 1  # barre con posizione aperta, questa inclusa
            if max_barre is not None and barre >= int(max_barre):
                return "chiudi"
            if chiudi_su_opposto:
                e = entra(i)
                if e is not None and e != pos.direzione:
                    return "chiudi"
            if chiudi_custom is not None and chiudi_custom(i, pos):
                return "chiudi"
            return None
        direzione = entra(i)
        if direzione is None:
            return None
        prezzo = serie.c[i]
        lato = 1 if direzione == "long" else -1
        if stop_atr is not None:
            a = atr[i]
            if not np.isfinite(a) or a <= 0:
                return None
            stop = prezzo - lato * float(stop_atr) * a
        elif stop_pct is not None:
            stop = prezzo * (1 - lato * float(stop_pct))
        else:
            raise ValueError("serve stop_atr o stop_pct")
        target = None
        if target_atr is not None:
            target = prezzo + lato * float(target_atr) * atr[i]
        elif target_pct is not None:
            target = prezzo * (1 + lato * float(target_pct))
        if stop <= 0:
            return None
        return Segnale(direzione, stop, target)  # type: ignore[arg-type]

    return strategia


# ---------------------------------------------------------------------------
# Esecuzione su un periodo
# ---------------------------------------------------------------------------


def periodo_nome(periodo: Tuple[date, date]) -> str:
    if periodo == d.COSTRUZIONE:
        return "costruzione"
    if periodo == d.VALIDAZIONE:
        return "validazione"
    return f"{periodo[0]}..{periodo[1]}"


def esegui_su_periodo(serie: Serie, strategia, periodo: Tuple[date, date], parametri=None):
    parametri = parametri or d.parametri()
    last = d.fetta(serie.last, *periodo)
    mark = d.fetta(serie.mark, *periodo)
    fund = d.fetta_funding(serie.funding, *periodo)
    return esegui(last, None, mark, fund, strategia, parametri), last


def r_serie(trades: Sequence[Trade]) -> List[float]:
    return [t.r for t in sorted(trades, key=lambda t: t.ts_uscita)]


def durate_barre(trades: Sequence[Trade], durata_ms: int) -> List[int]:
    return [max(1, int(math.ceil((t.ts_uscita - t.ts_entrata + 1) / durata_ms))) for t in trades]


def lunghezza_blocco(trades: Sequence[Trade], durata_ms: int, n_barre_periodo: int) -> Tuple[int, bool]:
    """Blocco in trade: durata massima di una posizione (>= 1 giorno) / distanza media fra ingressi."""
    n = len(trades)
    if n < 2:
        return 1, False
    dur_max_ms = max(max(t.ts_uscita - t.ts_entrata + 1 for t in trades), GIORNO_MS)
    distanza_media_ms = (n_barre_periodo * durata_ms) / n
    blocco = max(1, int(math.ceil(dur_max_ms / distanza_media_ms)))
    ridotto = False
    if blocco >= n:
        blocco, ridotto = n - 1, True
    return blocco, ridotto


def metriche_compatte(ris, last: Sequence[Candela], durata_ms: int) -> Dict[str, object]:
    m = calcola_metriche(ris)
    trades = ris.trades
    dur = durate_barre(trades, durata_ms) if trades else [0]
    stop_pct = [abs(t.stop - t.entrata) / t.entrata for t in trades]
    return {
        "n_trade": m["n_trade"],
        "profit_factor": None if math.isinf(m["profit_factor"]) else round(m["profit_factor"], 4),
        "win_rate": round(m["win_rate"], 4),
        "r_medio": round(m["r_medio"], 4),
        "r_mediano": round(float(np.median([t.r for t in trades])), 4) if trades else None,
        "rendimento_totale": round(m["rendimento_totale"], 4),
        "drawdown_max": round(m["drawdown_max"], 4),
        "rendimento_per_anno": {str(a): round(v, 4) for a, v in m["rendimento_per_anno"].items()},
        "r_medio_per_anno": r_medio_per_anno(trades),
        "n_trade_per_anno": n_per_anno(trades),
        "esiti": m["esiti"],
        "n_ridotti": m["n_ridotti"],
        "n_violazioni_liquidazione": m["n_violazioni_liquidazione"],
        "n_segnali_non_validi": m["n_segnali_non_validi"],
        "costi_totali": round(m["costi_totali"], 2),
        "funding_totale": round(m["funding_totale"], 2),
        "durata_barre": {"media": round(float(np.mean(dur)), 1), "max": int(max(dur)), "mediana": float(np.median(dur))},
        "stop_pct": {"medio": round(float(np.mean(stop_pct)), 4) if stop_pct else None, "quota_oltre_6pct": round(float(np.mean([s > 0.06 for s in stop_pct])), 3) if stop_pct else None},
        "per_direzione": {k: {"n": v["n"], "r_medio": round(v["r_medio"], 4)} for k, v in m["per_direzione"].items()},
        "n_buchi_dati": m["n_buchi_dati"],
    }


def _anno(ts_ms: int) -> int:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).year


def r_medio_per_anno(trades: Sequence[Trade]) -> Dict[str, float]:
    per: Dict[int, List[float]] = {}
    for t in trades:
        per.setdefault(_anno(t.ts_uscita), []).append(t.r)
    return {str(a): round(float(np.mean(v)), 4) for a, v in sorted(per.items())}


def n_per_anno(trades: Sequence[Trade]) -> Dict[str, int]:
    per: Dict[int, int] = {}
    for t in trades:
        per[_anno(t.ts_uscita)] = per.get(_anno(t.ts_uscita), 0) + 1
    return {str(a): v for a, v in sorted(per.items())}


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------


def baseline_incondizionata(serie: Serie, direzione_di: Callable[[int], Optional[str]], uscita: Dict[str, object], periodo, parametri=None, ammessa: Optional[Callable[[int], bool]] = None):
    """(a) stessa uscita su ogni barra (quando flat): ``direzione_di(i)`` da' la direzione da usare."""
    def entra(i: int):
        if ammessa is not None and not ammessa(i):
            return None
        return direzione_di(i)
    strat = strategia_da_regole(serie, entra, {**uscita, "chiudi_su_opposto": False})
    ris, last = esegui_su_periodo(serie, strat, periodo, parametri)
    return ris


def baseline_casuale(serie: Serie, trades_candidato: Sequence[Trade], uscita: Dict[str, object], periodo, parametri=None, n_sim: int = 100, seme: int = 0, barre_vietate=(), direzione_fissa: Optional[str] = None):
    """(b) entrate casuali con stessa uscita/direzione/numero/durata media; ritorna le simulazioni."""
    parametri = parametri or d.parametri()
    last = d.fetta(serie.last, *periodo)
    n_barre = len(last)
    n_trade = len(trades_candidato)
    if n_trade == 0:
        return {"r_medi": [], "serie_mediana": [], "n_sim": 0}
    dur = durate_barre(trades_candidato, serie.durata_ms)
    durata_media = max(1, int(round(float(np.mean(dur)))))
    # direzione: quella del candidato, trade per trade in ordine casuale se mista
    direzioni = [t.direzione for t in trades_candidato]
    offset = serie.idx[int(last[0].ts)]
    uscita_b = {**uscita, "chiudi_su_opposto": False}
    r_medi: List[float] = []
    serie_r: List[List[float]] = []
    n_trade_sim: List[int] = []
    for s in range(n_sim):
        indici = st.entrate_casuali(n_barre, n_trade, durata_media, seme + s, barre_vietate)
        rng = np.random.default_rng(seme + s)
        dirs = list(direzioni)
        rng.shuffle(dirs)
        mappa = {offset + k: (direzione_fissa or dirs[j]) for j, k in enumerate(indici)}
        strat = strategia_da_regole(serie, lambda i, mappa=mappa: mappa.get(i), uscita_b)
        ris = esegui(last, None, d.fetta(serie.mark, *periodo), d.fetta_funding(serie.funding, *periodo), strat, parametri)
        rs = r_serie(ris.trades)
        r_medi.append(float(np.mean(rs)) if rs else 0.0)
        serie_r.append(rs)
        n_trade_sim.append(len(rs))
    ordine = int(np.argsort(r_medi)[len(r_medi) // 2])
    return {"r_medi": r_medi, "serie_mediana": serie_r[ordine], "n_sim": n_sim, "n_trade_medio": float(np.mean(n_trade_sim)), "durata_media_barre": durata_media}


def confronto_baseline(r_cand: Sequence[float], r_base: Sequence[float], blocco: int) -> Dict[str, object]:
    if len(r_cand) < 2 or len(r_base) < 2:
        return {"netta": False, "degenere": True, "differenza": None}
    b = min(blocco, len(r_cand) - 1, len(r_base) - 1)
    out = st.differenza_nettamente(list(r_cand), list(r_base), max(1, b))
    return {k: (round(v, 4) if isinstance(v, float) and math.isfinite(v) else (None if isinstance(v, float) else v)) for k, v in out.items() if k != "campioni"}


def percentile_tra_casuali(valore: float, r_medi: Sequence[float]) -> Optional[float]:
    if not r_medi:
        return None
    return round(float(np.mean([x < valore for x in r_medi])) * 100, 1)


# ---------------------------------------------------------------------------
# Stima dei trade (solo segnali, mai risultati)
# ---------------------------------------------------------------------------


def stima_trade(serie: Serie, entra: Entra, periodo, occupazione_barre: int) -> Dict[str, int]:
    """Conta i segnali in costruzione: grezzi e non sovrapposti (occupazione dichiarata)."""
    last = d.fetta(serie.last, *periodo)
    i0, i1 = serie.idx[int(last[0].ts)], serie.idx[int(last[-1].ts)]
    grezzi = 0
    netti = 0
    libero_da = i0
    for i in range(i0, i1 + 1):
        e = entra(i)
        if e is None:
            continue
        grezzi += 1
        if i >= libero_da:
            netti += 1
            libero_da = i + 1 + max(1, occupazione_barre)
    return {"segnali_grezzi": grezzi, "trade_stimati": netti, "occupazione_barre": occupazione_barre}


# ---------------------------------------------------------------------------
# Log e salvataggio
# ---------------------------------------------------------------------------


def registra(voce: Dict[str, object]) -> Dict[str, object]:
    return aggiungi(voce)


def salva_risultato(id_: str, contenuto: Dict[str, object]) -> Path:
    RISULTATI.mkdir(exist_ok=True)
    p = RISULTATI / f"{id_}.json"
    p.write_text(json.dumps(contenuto, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    return p


def esamina(serie: Serie, entra: Entra, uscita: Dict[str, object], periodo, parametri=None, n_sim_caso: int = 100, con_baseline: bool = True, direzione_di=None, ammessa=None) -> Dict[str, object]:
    """Esegue la variante e, se richiesto, le tre baseline; ritorna un dizionario da log."""
    parametri = parametri or d.parametri()
    strat = strategia_da_regole(serie, entra, uscita)
    ris, last = esegui_su_periodo(serie, strat, periodo, parametri)
    m = metriche_compatte(ris, last, serie.durata_ms)
    out: Dict[str, object] = {"periodo": periodo_nome(periodo), "metriche": m}
    rc = r_serie(ris.trades)
    blocco, ridotto = lunghezza_blocco(ris.trades, serie.durata_ms, len(last))
    out["blocco_bootstrap"] = {"trade": blocco, "ridotto": ridotto}
    if con_baseline and ris.trades:
        bh_long = buy_and_hold(last, parametri, "long")
        out["baseline_c_buy_and_hold"] = {"long": round(bh_long, 4), "short": round(buy_and_hold(last, parametri, "short"), 4)}
        dir_fn = direzione_di or (lambda i: entra(i))
        if direzione_di is not None:
            ris_a = baseline_incondizionata(serie, direzione_di, uscita, periodo, parametri, ammessa)
            ra = r_serie(ris_a.trades)
            out["baseline_a_incondizionata"] = {"n_trade": len(ra), "r_medio": round(float(np.mean(ra)), 4) if ra else None, "confronto": confronto_baseline(rc, ra, blocco)}
        caso = baseline_casuale(serie, ris.trades, uscita, periodo, parametri, n_sim=n_sim_caso, barre_vietate=())
        out["baseline_b_casuale"] = {
            "n_sim": caso["n_sim"],
            "r_medio_caso_mediano": round(float(np.median(caso["r_medi"])), 4),
            "r_medio_caso_p90": round(st.percentile(caso["r_medi"], 90), 4),
            "percentile_del_candidato": percentile_tra_casuali(m["r_medio"], caso["r_medi"]),
            "confronto_con_sim_mediana": confronto_baseline(rc, caso["serie_mediana"], blocco),
        }
    return out, ris
