"""Il quadro comune della campagna 1000SHIBUSDT: dati, varianti, conteggio, test e baseline.

Niente strategie qui: solo il modo, uguale per tutte le varianti, di
* caricare last e mark allineati (``carica_serie_allineate``), il funding e il filtro
  di liquidita' della Fase 0 (mesi sotto 20 milioni di USDT al giorno: niente ingressi
  su segnali di barre di quei mesi);
* trasformare una ``Variante`` (indicatori causali, condizione d'ingresso, segnale con
  stop e target, uscita) nelle tre fabbriche che il motore vuole: la strategia, la
  strategia casuale della (b) e il calcolo del segnale senza condizione; piu' la (a);
* contare i trade (``conta_trade``) e fare il test della Fase 2 con le baseline.

Gli indicatori si calcolano UNA volta sulla lista di candele che il motore ricevera'
(calcolo causale: il valore all'indice i usa solo le barre 0..i); la strategia legge
l'indice ``len(storia) - 1``. ``verifica_causalita`` lo controlla ricalcolando gli
indicatori su serie troncate. Ogni esecuzione del motore crea un'istanza nuova.
"""
from __future__ import annotations

import json
import math
import pickle
import sys
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

import numpy as np

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))

import yaml  # noqa: E402

from research.src import dati, motore, statistica  # noqa: E402
from research.src.motore import Candela, Parametri, Segnale  # noqa: E402

SIMBOLO = "1000SHIBUSDT"
CARTELLA_DATI = RADICE_REPO / "research" / "data" / "insample" / SIMBOLO
CARTELLA_BTC = RADICE_REPO / "research" / "data" / "insample" / "BTCUSDT"
CARTELLA_CAMPAGNA = RADICE_REPO / "research" / "campagne" / SIMBOLO
INIZIO = date(2021, 5, 1)
PERIODI = dati.periodi_campagna(INIZIO)
FINE_COSTRUZIONE = PERIODI["fine_costruzione"]
FINE_COSTRUZIONE_TS = PERIODI["fine_costruzione_ts"]
INIZIO_VALIDAZIONE_TS = PERIODI["inizio_validazione_ts"]
SLIPPAGE = 0.0002  # scheda_moneta.md: fascia 0,0200% per lato
LIQUIDITA_MINIMA = 20_000_000
MS = {tf: dati.durata_intervallo(tf) for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]}


def parametri(moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0,
              riempimento: str = "stop_prima") -> Parametri:
    """I parametri del motore da config/parametri.yaml e dalla scheda della moneta (sezione 7)."""
    cfg = yaml.safe_load((RADICE_REPO / "research" / "config" / "parametri.yaml").read_text(encoding="utf-8"))
    dim = cfg["fatti"]["regole_dimensione_bot"]
    return Parametri(
        commissione_per_lato=float(cfg["fatti"]["commissione_taker_per_lato"]["valore"]),
        slippage_per_lato=SLIPPAGE,
        rischio_per_trade=float(dim["rischio_per_trade"]),
        leva_max=float(dim["leva_max"]),
        modalita_margine=dim["modalita_margine_proposta"],
        tasso_margine_mantenimento=float(dim["tasso_margine_mantenimento"]),
        margine_minimo_da_liquidazione=float(cfg["regole_esame"]["margine_minimo_da_liquidazione"]),
        capitale_iniziale=float(dim["capitale_iniziale"]),
        riempimento_intrabarra=riempimento,
        moltiplicatore_costi=moltiplicatore_costi,
        ritardo_barre=ritardo_barre,
    )


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------


def _anno_mese(ts: int):
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return d.year, d.month


def mesi_illiquidi(fine: date = date(2023, 12, 31)) -> Dict[tuple, float]:
    """Volume medio giornaliero in USDT per mese, dai file 1d del last, su tutti i giorni."""
    vol: Dict[int, float] = {}
    for p in sorted((CARTELLA_DATI / "klines" / "1d").glob("*.zip")):
        for ts, v in dati.volume_usdt_da_zip(p).items():
            vol.setdefault(ts, v)
    per_mese: Dict[tuple, List[float]] = {}
    for ts, v in vol.items():
        if ts < dati.ms_da_data(INIZIO) or ts >= dati.ms_da_data(fine) + dati.MS_GIORNO:
            continue
        per_mese.setdefault(_anno_mese(ts), []).append(v)
    return {k: sum(v) / len(v) for k, v in sorted(per_mese.items())}


@dataclass
class Serie:
    tf: str
    candele: List[Candela]
    mark: List[Candela]
    funding: List[tuple]
    liquida: np.ndarray  # True se la barra e' in un mese con liquidita' sufficiente
    info: Dict[str, object]
    btc: Optional[Dict[int, Candela]] = None  # candele last di BTCUSDT per ts (solo riferimento)


def carica(tf: str, fino_a: date = FINE_COSTRUZIONE, con_btc: bool = False) -> Serie:
    """Last e mark allineati, funding e filtro di liquidita', dall'inizio a ``fino_a`` compreso."""
    chiave = CARTELLA_DATI / f"cache_{tf}_{fino_a.isoformat()}_{int(con_btc)}.pkl"
    if chiave.is_file():
        with open(chiave, "rb") as f:
            return pickle.load(f)
    s = dati.carica_serie_allineate(SIMBOLO, tf, INIZIO, fino_a)
    candele, mark = s["candele"], s["candele_mark"]
    funding = dati.carica_funding(SIMBOLO, INIZIO, fino_a)
    medie = mesi_illiquidi()
    liquida = np.array([medie.get(_anno_mese(c.ts), 0.0) >= LIQUIDITA_MINIMA for c in candele])
    btc = None
    if con_btc:
        btc = {c.ts: c for c in dati.carica_candele("BTCUSDT", tf, INIZIO, fino_a)}
    info = {k: s[k] for k in ("n_tolte_last", "n_tolte_mark", "n_volume_mancante")}
    info["volume_usdt"] = s["volume_usdt"]
    serie = Serie(tf, candele, mark, funding, liquida, info, btc)
    with open(chiave, "wb") as f:
        pickle.dump(serie, f)
    return serie


# ---------------------------------------------------------------------------
# Indicatori causali (il valore all'indice i usa solo le barre 0..i)
# ---------------------------------------------------------------------------


def arr(candele, campo):
    return np.array([getattr(c, campo) for c in candele], dtype=float)


def media_mobile(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        c = np.cumsum(np.insert(x, 0, 0.0))
        out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def media_esponenziale(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    a = 2.0 / (n + 1)
    out[n - 1] = np.mean(x[:n])
    for i in range(n, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def atr(candele, n: int = 14) -> np.ndarray:
    h, l, c = arr(candele, "high"), arr(candele, "low"), arr(candele, "close")
    tr = np.empty(len(c))
    tr[0] = h[0] - l[0]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1])))
    # media di Wilder
    out = np.full(len(c), np.nan)
    if len(c) > n:
        out[n] = np.mean(tr[1:n + 1])
        for i in range(n + 1, len(c)):
            out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def rsi(close: np.ndarray, n: int) -> np.ndarray:
    d = np.diff(close, prepend=np.nan)
    su = np.where(d > 0, d, 0.0)
    giu = np.where(d < 0, -d, 0.0)
    out = np.full(len(close), np.nan)
    if len(close) <= n:
        return out
    ms, mg = np.mean(su[1:n + 1]), np.mean(giu[1:n + 1])
    for i in range(n, len(close)):
        if i > n:
            ms = (ms * (n - 1) + su[i]) / n
            mg = (mg * (n - 1) + giu[i]) / n
        out[i] = 100.0 if mg == 0 else 100 - 100 / (1 + ms / mg)
    return out


def massimo_mobile(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = np.max(x[i - n + 1:i + 1])
    return out


def minimo_mobile(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = np.min(x[i - n + 1:i + 1])
    return out


def ritardato(x: np.ndarray, k: int = 1) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if k < len(x):
        out[k:] = x[:-k]
    return out


def deviazione_mobile(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = np.std(x[i - n + 1:i + 1], ddof=1)
    return out


def ora_utc(candele) -> np.ndarray:
    return np.array([datetime.fromtimestamp(c.ts / 1000, tz=timezone.utc).hour for c in candele])


def giorno_settimana(candele) -> np.ndarray:
    return np.array([datetime.fromtimestamp(c.ts / 1000, tz=timezone.utc).weekday() for c in candele])


def funding_ultimo(candele, funding) -> np.ndarray:
    """Ultimo tasso di funding con settlement <= chiusura della barra (noto alla chiusura)."""
    ts_f = [t for t, _ in funding]
    tassi = [r for _, r in funding]
    import bisect
    out = np.full(len(candele), np.nan)
    for i, c in enumerate(candele):
        k = bisect.bisect_right(ts_f, c.close_ts) - 1
        if k >= 0:
            out[i] = tassi[k]
    return out


# ---------------------------------------------------------------------------
# Varianti
# ---------------------------------------------------------------------------


@dataclass
class Variante:
    """Una regola completa (regola 6). Le funzioni ricevono l'indice della barra e gli indicatori.

    * ``prepara(serie_candele, serie) -> dict``: indicatori causali;
    * ``ingresso(i, ind) -> bool``: condizione d'ingresso dell'ipotesi e filtri;
    * ``segnale(i, ind, candele) -> Segnale | None``: stop e target (None se non calcolabile);
    * ``esci(i, ind, candele, pos, barre_in_posizione) -> bool``: uscita a segnale (oltre stop e target);
    * ``riscaldamento``: barre dall'inizio in cui la variante non puo' entrare (indicatori).
    """

    id: str
    tf: str
    direzione: str
    prepara: Callable
    ingresso: Callable
    segnale: Callable
    esci: Callable
    riscaldamento: int
    descrizione: Dict[str, object] = field(default_factory=dict)
    con_btc: bool = False


def _barre_in_posizione(pos, candele_i, tf) -> int:
    return int((candele_i.close_ts + 1 - pos.ts_entrata) // MS[tf])


class Fabbriche:
    """Le fabbriche del motore per una variante su una serie (un'istanza nuova a ogni chiamata)."""

    def __init__(self, v: Variante, serie: Serie, candele: List[Candela]):
        self.v = v
        self.serie = serie
        self.candele = candele
        self.ind = v.prepara(candele, serie)
        self.liquida = serie.liquida[: len(candele)]

    def _segnale(self, i):
        if i < self.v.riscaldamento:
            return None
        return self.v.segnale(i, self.ind, self.candele)

    def _gestione(self, i, pos):
        b = _barre_in_posizione(pos, self.candele[i], self.v.tf)
        return "chiudi" if self.v.esci(i, self.ind, self.candele, pos, b) else None

    def crea(self):
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is not None:
                return self._gestione(i, pos)
            if not self.liquida[i] or i < self.v.riscaldamento:
                return None
            if self.v.ingresso(i, self.ind):
                return self._segnale(i)
            return None
        return strategia

    def crea_a(self):
        """Baseline (a): senza condizione d'ingresso e senza filtri, a ogni barra libera."""
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is not None:
                return self._gestione(i, pos)
            if not self.liquida[i]:
                return None
            return self._segnale(i)
        return strategia

    def crea_casuale(self, ingressi):
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is not None:
                return self._gestione(i, pos)
            if i in ingressi:
                return self._segnale(i)
            return None
        return strategia

    def crea_segnale(self):
        def calcola(storia):
            return self._segnale(len(storia) - 1)
        return calcola

    def barre_vietate(self, parametri_motore, prima_ammessa: int = 0):
        """Segnale non valido (riscaldamento compreso), mesi illiquidi e barre prima di ``prima_ammessa``."""
        vietate = list(motore.barre_vietate_segnale_non_valido(self.candele, self.crea_segnale, parametri_motore))
        corrente = None
        for i, ok in enumerate(self.liquida):
            if not ok:
                if corrente is None:
                    corrente = i
            elif corrente is not None:
                vietate.append((corrente, i))
                corrente = None
        if corrente is not None:
            vietate.append((corrente, len(self.liquida)))
        if prima_ammessa > 0:
            vietate.append((0, prima_ammessa))
        return sorted(vietate)


def verifica_causalita(v: Variante, serie: Serie, punti: int = 6) -> List[str]:
    """Ricalcola gli indicatori su serie troncate e confronta: lista vuota = causale."""
    candele = serie.candele
    pieno = v.prepara(candele, serie)
    problemi = []
    rng = np.random.default_rng(1)
    for k in sorted(rng.integers(v.riscaldamento + 5, len(candele) - 5, size=punti)):
        tronco = v.prepara(candele[: k + 1], serie)
        for nome, valori in pieno.items():
            if not isinstance(valori, np.ndarray) or valori.shape[:1] != (len(candele),):
                continue
            a, b = valori[k], tronco[nome][k]
            if not ((np.isnan(a) and np.isnan(b)) or np.isclose(a, b, rtol=1e-9, atol=1e-12)):
                problemi.append(f"{nome}[{k}]: pieno {a} tronco {b}")
    return problemi


# ---------------------------------------------------------------------------
# Conteggio e test
# ---------------------------------------------------------------------------


def candele_costruzione(serie: Serie) -> int:
    """Numero di barre della serie che chiudono entro la fine della costruzione."""
    return sum(1 for c in serie.candele if c.close_ts <= FINE_COSTRUZIONE_TS)


def conta(v: Variante) -> Dict[str, int]:
    serie = carica(v.tf, con_btc=v.con_btc)
    n = candele_costruzione(serie)
    candele, mark = serie.candele[:n], serie.mark[:n]
    fab = Fabbriche(v, serie, candele)
    return motore.conta_trade(candele, fab.crea, FINE_COSTRUZIONE_TS, parametri(), candele_mark=mark,
                              funding=serie.funding)


def _r_ordinati(trades):
    t = sorted(trades, key=lambda x: x.ts_uscita)
    return [x.r for x in t], t


def _anno(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year


def buy_and_hold_per_anno(candele, par) -> Dict[str, Dict[str, float]]:
    per_anno: Dict[int, list] = {}
    for c in candele:
        per_anno.setdefault(_anno(c.ts), []).append(c)
    return {str(a): {"long": round(motore.buy_and_hold(cs, par, "long"), 4),
                     "short": round(motore.buy_and_hold(cs, par, "short"), 4)} for a, cs in per_anno.items()}


def _pulisci_confronto(c: Dict[str, object]) -> Dict[str, object]:
    out = {}
    for k in ("differenza", "errore_standard", "errore_candidato", "errore_minimo", "baseline_media",
              "baseline_errore_standard", "t", "soglia", "p_value", "netta", "valutabile", "n_blocchi"):
        if k in c:
            x = c[k]
            if isinstance(x, (bool, np.bool_)):
                out[k] = bool(x)
            elif isinstance(x, (int, np.integer)):
                out[k] = int(x)
            else:
                x = float(x)
                out[k] = None if math.isnan(x) else (x if math.isinf(x) else round(x, 5))
    return out


def esame(v: Variante, par: Optional[Parametri] = None, periodo: str = "costruzione",
          tf_serie: Optional[str] = None, n_simulazioni: int = 200) -> Dict[str, object]:
    """Il test della Fase 2 (o una verifica): candidato, (a), (b), percentile, contesto.

    ``periodo`` = "costruzione" usa le barre fino alla fine della costruzione; "validazione"
    carica fino al 2023-12-31, esegue sulla serie intera (indicatori caldi) e tiene solo i
    trade ENTRATI dopo la fine della costruzione; la (b) estrae ingressi solo nelle barre di
    validazione e la (a) conta solo i suoi trade entrati in validazione.
    """
    par = par or parametri()
    if periodo == "costruzione":
        serie = carica(v.tf, con_btc=v.con_btc)
        n = candele_costruzione(serie)
    else:
        serie = carica(v.tf, fino_a=date(2023, 12, 31), con_btc=v.con_btc)
        n = len(serie.candele)
    candele, mark = serie.candele[:n], serie.mark[:n]
    funding = [(t, r) for t, r in serie.funding if t <= candele[-1].close_ts]
    fab = Fabbriche(v, serie, candele)

    ris = motore.esegui(candele, None, mark, funding, fab.crea(), par)
    trades = ris.trades
    prima_valid = 0
    if periodo == "validazione":
        trades = [t for t in trades if t.ts_entrata >= INIZIO_VALIDAZIONE_TS]
        prima_valid = next(i for i, c in enumerate(candele) if c.ts >= INIZIO_VALIDAZIONE_TS)
    r, ordinati = _r_ordinati(trades)
    out: Dict[str, object] = {"id": v.id, "periodo": periodo, "tf": v.tf}
    if len(trades) < 2:
        out["metriche"] = {"trade": len(trades)}
        out["valutabile"] = False
        return out

    vinti = sum(t.pnl for t in trades if t.pnl > 0)
    persi = -sum(t.pnl for t in trades if t.pnl < 0)
    r_anno: Dict[str, list] = {}
    for t in ordinati:
        r_anno.setdefault(str(_anno(t.ts_uscita)), []).append(t.r)
    senza3 = sorted(r)[:-3] if len(r) > 3 else []
    # curva del capitale dei soli trade del periodo
    cap = par.capitale_iniziale
    curva = [(ordinati[0].ts_entrata, cap)]
    for t in ordinati:
        cap += t.pnl
        curva.append((t.ts_uscita, cap))
    rend_anno: Dict[str, float] = {}
    cap = par.capitale_iniziale
    for t in ordinati:
        a = str(_anno(t.ts_uscita))
        rend_anno.setdefault(a, 0.0)
        rend_anno[a] += t.pnl / par.capitale_iniziale
    metriche = {
        "profit_factor": round(vinti / persi, 4) if persi > 0 else None,
        "trade": len(trades),
        "r_medio": round(float(np.mean(r)), 5),
        "r_medio_per_anno": {a: round(float(np.mean(x)), 4) for a, x in r_anno.items()},
        "trade_per_anno": {a: len(x) for a, x in r_anno.items()},
        "r_medio_senza_3_migliori": round(float(np.mean(senza3)), 5) if senza3 else None,
        "drawdown_max": round(-motore.drawdown_massimo(curva), 4),
        "rendimento_totale": round(sum(t.pnl for t in trades) / par.capitale_iniziale, 4),
        "rendimento_per_anno_su_capitale_iniziale": {a: round(x, 4) for a, x in rend_anno.items()},
        "win_rate": round(sum(1 for t in trades if t.pnl > 0) / len(trades), 4),
        "esiti": {e: sum(1 for t in trades if t.esito == e) for e in ("stop", "target", "segnale", "liquidazione", "fine_dati")},
        "trade_ridotti_tetto_leva": sum(1 for t in trades if t.ridotto),
        "violazioni_liquidazione": sum(1 for t in trades if t.violazione_liquidazione),
        "stop_oltre_6_per_cento": sum(1 for t in trades if abs(t.entrata - t.stop) / t.entrata > 0.06),
        "durata_media_barre": motore.durata_media_barre(trades, MS[v.tf]),
        "buchi_dati": ris.n_buchi_dati,
        "funding_in_buco": ris.n_funding_in_buco,
        "costo_medio_r": round(float(np.mean([(t.commissioni + t.slippage_costo) / t.rischio_iniziale for t in trades])), 4),
    }
    out["metriche"] = metriche
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in ordinati], [t.ts_uscita for t in ordinati])
    out["blocco"] = blocco

    # baseline (a): senza condizione d'ingresso e senza filtri, una posizione alla volta
    ris_a = motore.esegui(candele, None, mark, funding, fab.crea_a(), par)
    trades_a = ris_a.trades
    if periodo == "validazione":
        trades_a = [t for t in trades_a if t.ts_entrata >= INIZIO_VALIDAZIONE_TS]
    r_a, ord_a = _r_ordinati(trades_a)
    if len(r_a) >= 2:
        blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in ord_a], [t.ts_uscita for t in ord_a])
        base_a = statistica.baseline_da_trade(r_a, blocco_a, n=2000, seme=0)
        conf_a = statistica.contro_baseline(r, blocco, base_a, n=2000, seme=0)
        out["baseline_a"] = dict(_pulisci_confronto(conf_a), media=round(base_a["media"], 5),
                                 n_trade=base_a["n_trade"], blocco_a=blocco_a,
                                 n_blocchi_a=base_a["n_blocchi"], valutabile_a=base_a["valutabile"])
    else:
        out["baseline_a"] = {"valutabile": False, "netta": False, "t": -math.inf, "n_trade": len(r_a)}

    # baseline (b): entrate casuali con la stessa uscita (sempre simula_baseline_casuale)
    durata = motore.durata_media_barre(trades, MS[v.tf])
    vietate = fab.barre_vietate(par, prima_ammessa=prima_valid)
    n_vietate = sum(b - a for a, b in vietate)
    try:
        base_b = motore.simula_baseline_casuale(candele, fab.crea_casuale, len(trades), durata, par,
                                                candele_mark=mark, funding=funding, barre_vietate=vietate,
                                                n_simulazioni=n_simulazioni, primo_seme=0)
        conf_b = statistica.contro_baseline(r, blocco, base_b, n=2000, seme=0)
        out["baseline_b"] = dict(
            _pulisci_confronto(conf_b), media=round(base_b["media"], 5),
            n_simulazioni=base_b["n_simulazioni"],
            trade_per_simulazione_medio=round(float(np.mean(base_b["trade_per_simulazione"])), 2),
            quota_barre_vietate=round(n_vietate / len(candele), 4),
            segnali_scartati_per_simulazione_medio=round(float(np.mean(base_b["segnali_non_validi_per_simulazione"])), 3),
            simulazioni_vuote=base_b["simulazioni_vuote"])
        out["percentile_caso"] = round(statistica.percentile_del_candidato(float(np.mean(r)), base_b["valori"]), 2)
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "netta": False, "t": -math.inf, "errore": str(e)}
        out["percentile_caso"] = None
    if periodo == "validazione":
        out["buy_and_hold_per_anno"] = buy_and_hold_per_anno([c for c in candele if c.ts >= INIZIO_VALIDAZIONE_TS], par)
    else:
        out["buy_and_hold_per_anno"] = buy_and_hold_per_anno(candele, par)
    a_ok = out["baseline_a"].get("valutabile", False)
    b_ok = out["baseline_b"].get("valutabile", False)
    out["valutabile"] = bool(a_ok and b_ok)
    out["candidato"] = bool(a_ok and b_ok and out["baseline_a"]["netta"] and out["baseline_b"]["netta"]
                            and metriche["r_medio"] > 0)
    out["_trades"] = [(t.ts_entrata, t.ts_uscita, t.r, t.esito) for t in ordinati]
    return out


def salva(nome: str, oggetto) -> Path:
    p = CARTELLA_DATI / "risultati" / f"{nome}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(oggetto, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return p
