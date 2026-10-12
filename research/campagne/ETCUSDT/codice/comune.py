"""Strumenti comuni della campagna ETCUSDT: parametri, dati, indicatori, varianti ed esame.

Tutto passa dagli strumenti di research/src (motore, dati, statistica): qui c'e' solo
la colla. Regole fisse di questo file, scritte prima del primo test:

* Gli indicatori si calcolano UNA volta sulla lista di candele passata al motore e
  sono CAUSALI: il valore all'indice i usa solo le barre 0..i. La strategia legge
  l'indice i = len(storia) - 1 (la barra appena chiusa).
* Una variante e' definita da: timeframe, direzione, riscaldamento (prima barra in
  cui gli indicatori esistono), condizione d'ingresso, calcolo di stop e target,
  uscita (barre massime e/o uscita su condizione). La baseline (a) e' la stessa
  variante senza condizione d'ingresso e senza filtri, che entra a ogni barra libera
  dal riscaldamento in poi; la (b) entra a caso con lo stesso calcolo di stop,
  target e uscita (motore.simula_baseline_casuale).
* Mesi sotto la liquidita' minima (Fase 0, punto 3): nessun ingresso su segnali di
  barre di quei mesi, per la variante, per conta_trade e per la (a); le stesse barre
  vanno fra le barre vietate della (b).
"""
from __future__ import annotations

import json
import math
import pickle
import sys
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from research.src import dati, motore, statistica  # noqa: E402
from research.src.motore import Candela, Parametri, Segnale  # noqa: E402
import registro  # noqa: E402

SIMBOLO = "ETCUSDT"
CARTELLA = Path(__file__).resolve().parent.parent
CARTELLA_DATI = RADICE_REPO / "research" / "data" / "insample" / SIMBOLO
CACHE = CARTELLA_DATI / "cache"
USCITE = CARTELLA_DATI / "uscite"

PERIODI = dati.periodi_campagna(date(2020, 1, 1))
FINE_COSTRUZIONE_TS = PERIODI["fine_costruzione_ts"]
INIZIO_VALIDAZIONE_TS = PERIODI["inizio_validazione_ts"]

# parametri.yaml (congelato) e scheda_moneta.md: slippage 0,05% per lato
PARAMETRI = Parametri(
    commissione_per_lato=0.0005,
    slippage_per_lato=0.0005,
    rischio_per_trade=0.01,
    leva_max=2.0,
    modalita_margine="isolated",
    tasso_margine_mantenimento=0.025,
    margine_minimo_da_liquidazione=0.8,
    capitale_iniziale=1000.0,
    riempimento_intrabarra="stop_prima",
    moltiplicatore_costi=1.0,
    ritardo_barre=0,
)
N_SIM_B = 200
BOOT_N, BOOT_SEME = 2000, 0
TRADE_MINIMI_COSTRUZIONE = 70
TRADE_MINIMI_VALIDAZIONE = 30

MS = {tf: dati.durata_intervallo(tf) for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]}


def stampa(*args) -> None:
    """Stampa e copia in data/insample/ETCUSDT/uscite/ultima.txt (i comandi non usano redirezioni)."""
    USCITE.mkdir(parents=True, exist_ok=True)
    testo = " ".join(str(a) for a in args)
    print(testo, flush=True)
    with open(USCITE / "ultima.txt", "a", encoding="utf-8") as f:
        f.write(testo + "\n")


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------


def mesi_esclusi() -> List[str]:
    """I mesi sotto la liquidita' minima, scritti in Fase 0 (codice/mesi_esclusi.json)."""
    with open(Path(__file__).resolve().parent / "mesi_esclusi.json", encoding="utf-8") as f:
        return json.load(f)["mesi_esclusi"]


def _mese(ts: int) -> str:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m")


@dataclass
class Serie:
    tf: str
    periodo: str
    candele: List[Candela]
    mark: List[Candela]
    funding: List[Tuple[int, float]]
    volume_usdt: Dict[int, Optional[float]]
    vietate_liquidita: List[bool]  # True: barra di un mese escluso, niente ingressi

    @property
    def n(self) -> int:
        return len(self.candele)


def carica(tf: str, periodo: str = "costruzione") -> Serie:
    """Last e mark allineati (carica_serie_allineate) e funding, dal 2020-01-01.

    periodo 'costruzione': fino a fine_costruzione; 'validazione': fino al 2023-12-31
    (la validazione gira da inizio costruzione, contano i trade entrati dopo).
    """
    CACHE.mkdir(parents=True, exist_ok=True)
    fine = PERIODI["fine_costruzione"] if periodo == "costruzione" else PERIODI["fine_validazione"]
    percorso = CACHE / f"{tf}_{periodo}.pkl"
    if percorso.is_file():
        with open(percorso, "rb") as f:
            al, funding = pickle.load(f)
    else:
        al = dati.carica_serie_allineate(SIMBOLO, tf, PERIODI["inizio"], fine)
        funding = dati.carica_funding(SIMBOLO, PERIODI["inizio"], fine)
        with open(percorso, "wb") as f:
            pickle.dump((al, funding), f)
    esclusi = set(mesi_esclusi())
    vietate = [_mese(c.ts) in esclusi for c in al["candele"]]
    return Serie(tf, periodo, al["candele"], al["candele_mark"], funding, al["volume_usdt"], vietate)


def colonne_klines(tf: str, periodo: str, colonna: int) -> Dict[int, float]:
    """Una colonna grezza dei CSV klines di ETCUSDT ({ts: valore}), es. 9 = taker_buy_volume."""
    fine = PERIODI["fine_costruzione"] if periodo == "costruzione" else PERIODI["fine_validazione"]
    percorso_cache = CACHE / f"col{colonna}_{tf}_{periodo}.pkl"
    if percorso_cache.is_file():
        with open(percorso_cache, "rb") as f:
            return pickle.load(f)
    valori: Dict[int, float] = {}
    for anno, mese in dati.mesi_del_periodo(PERIODI["inizio"], fine):
        p = dati.percorso_mese(SIMBOLO, "klines", tf, anno, mese, dati.RADICE_DEFAULT)
        if not p.is_file():
            continue
        for riga in dati.righe_csv_da_zip(p):
            ts = dati.normalizza_ts(riga[0])
            if ts not in valori and len(riga) > colonna and riga[colonna].strip():
                valori[ts] = float(riga[colonna])
    with open(percorso_cache, "wb") as f:
        pickle.dump(valori, f)
    return valori


def btc_allineato(serie: Serie) -> List[Optional[Candela]]:
    """Candele last di BTCUSDT sugli stessi ts della serie di ETCUSDT (None dove mancano)."""
    fine = PERIODI["fine_costruzione"] if serie.periodo == "costruzione" else PERIODI["fine_validazione"]
    percorso = CACHE / f"btc_{serie.tf}_{serie.periodo}.pkl"
    if percorso.is_file():
        with open(percorso, "rb") as f:
            btc = pickle.load(f)
    else:
        btc = dati.carica_candele("BTCUSDT", serie.tf, PERIODI["inizio"], fine)
        with open(percorso, "wb") as f:
            pickle.dump(btc, f)
    per_ts = {c.ts: c for c in btc}
    return [per_ts.get(c.ts) for c in serie.candele]


# ---------------------------------------------------------------------------
# Indicatori causali (valore all'indice i: solo barre 0..i; NaN nel riscaldamento)
# ---------------------------------------------------------------------------


def arr(candele: Sequence[Candela], campo: str) -> np.ndarray:
    return np.array([getattr(c, campo) for c in candele], dtype=float)


def sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        c = np.cumsum(np.insert(x, 0, 0.0))
        out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def ema(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    a = 2.0 / (n + 1)
    out[n - 1] = np.mean(x[:n])
    for i in range(n, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def true_range(h: np.ndarray, l: np.ndarray, c: np.ndarray) -> np.ndarray:
    pc = np.concatenate([[np.nan], c[:-1]])
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    tr[0] = h[0] - l[0]
    return tr


def atr(h: np.ndarray, l: np.ndarray, c: np.ndarray, n: int) -> np.ndarray:
    """ATR di Wilder."""
    tr = true_range(h, l, c)
    out = np.full(len(tr), np.nan)
    if len(tr) < n:
        return out
    out[n - 1] = np.mean(tr[:n])
    for i in range(n, len(tr)):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def rsi(c: np.ndarray, n: int) -> np.ndarray:
    """RSI di Wilder."""
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    d = np.diff(c)
    g = np.where(d > 0, d, 0.0)
    p = np.where(d < 0, -d, 0.0)
    ag, ap = np.mean(g[:n]), np.mean(p[:n])
    out[n] = 100.0 if ap == 0 else 100 - 100 / (1 + ag / ap)
    for i in range(n + 1, len(c)):
        ag = (ag * (n - 1) + g[i - 1]) / n
        ap = (ap * (n - 1) + p[i - 1]) / n
        out[i] = 100.0 if ap == 0 else 100 - 100 / (1 + ag / ap)
    return out


def massimo_precedente(x: np.ndarray, n: int) -> np.ndarray:
    """Massimo delle n barre PRIMA di i (escluso i): per i rotture di canale."""
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        out[i] = np.max(x[i - n:i])
    return out


def minimo_precedente(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        out[i] = np.min(x[i - n:i])
    return out


def rendimento(c: np.ndarray, n: int) -> np.ndarray:
    """c[i] / c[i-n] - 1."""
    out = np.full(len(c), np.nan)
    out[n:] = c[n:] / c[:-n] - 1
    return out


def deviazione_mobile(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = np.std(x[i - n + 1:i + 1], ddof=1)
    return out


def a_lista(x: np.ndarray) -> list:
    return [None if (v is None or (isinstance(v, float) and math.isnan(v))) else float(v) for v in x.tolist()]


# ---------------------------------------------------------------------------
# Varianti
# ---------------------------------------------------------------------------


@dataclass
class Variante:
    """Una regola completa (regola 6). Le funzioni ricevono gli indicatori preparati."""

    id: str
    tf: str
    direzione: str
    prepara: Callable[[Serie], dict]  # indicatori causali; deve contenere 'riscaldamento'
    ingresso: Callable[[dict, int], bool]  # condizione d'ingresso dell'ipotesi (con i suoi filtri)
    segnale: Callable[[dict, int], Optional[Tuple[float, Optional[float]]]]  # (stop, target) o None
    max_barre: Optional[int] = None  # uscita a tempo: "chiudi" dopo tante barre tenute
    uscita: Optional[Callable[[dict, int, object], bool]] = None  # uscita su condizione
    descrizione: dict = field(default_factory=dict)


def _fabbriche(var: Variante, serie: Serie, ind: dict):
    ms = MS[var.tf]
    risc = ind["riscaldamento"]
    vietate = serie.vietate_liquidita

    def esce(i: int, storia, pos) -> bool:
        tenute = (storia[i].close_ts + 1 - pos.ts_entrata) // ms
        if var.max_barre is not None and tenute >= var.max_barre:
            return True
        return bool(var.uscita is not None and var.uscita(ind, i, pos))

    def crea_strategia(con_condizione: bool = True):
        def crea():
            def strategia(storia, pos):
                i = len(storia) - 1
                if pos is not None:
                    return "chiudi" if esce(i, storia, pos) else None
                if i < risc or vietate[i]:
                    return None
                if con_condizione and not var.ingresso(ind, i):
                    return None
                s = var.segnale(ind, i)
                if s is None:
                    return None
                return Segnale(var.direzione, s[0], s[1])
            return strategia
        return crea

    def crea_casuale(ingressi):
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is not None:
                return "chiudi" if esce(i, storia, pos) else None
            if i not in ingressi or i < risc:
                return None
            s = var.segnale(ind, i)
            if s is None:
                return None
            return Segnale(var.direzione, s[0], s[1])
        return strategia

    def crea_segnale():
        def segnale(storia):
            i = len(storia) - 1
            if i < risc:
                return None
            s = var.segnale(ind, i)
            if s is None:
                return None
            return Segnale(var.direzione, s[0], s[1])
        return segnale

    return crea_strategia, crea_casuale, crea_segnale


def intervalli(maschera: Sequence[bool]) -> List[Tuple[int, int]]:
    out: List[Tuple[int, int]] = []
    for i, v in enumerate(maschera):
        if v:
            if out and out[-1][1] == i:
                out[-1] = (out[-1][0], i + 1)
            else:
                out.append((i, i + 1))
    return out


def conta(var: Variante, serie: Optional[Serie] = None) -> Dict[str, int]:
    serie = serie or carica(var.tf, "costruzione")
    ind = var.prepara(serie)
    crea_strategia, _, _ = _fabbriche(var, serie, ind)
    return motore.conta_trade(serie.candele, crea_strategia(True), FINE_COSTRUZIONE_TS, PARAMETRI,
                              candele_mark=serie.mark, funding=serie.funding)


def _ordina_per_uscita(trades):
    return sorted(trades, key=lambda t: (t.ts_uscita, t.ts_entrata))


def _metriche(trades, ris=None) -> dict:
    ordinati = _ordina_per_uscita(trades)
    r = [t.r for t in ordinati]
    n = len(r)
    per_anno: Dict[str, List[float]] = {}
    for t in ordinati:
        per_anno.setdefault(str(datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc).year), []).append(t.r)
    vinti = sum(t.pnl for t in trades if t.pnl > 0)
    persi = -sum(t.pnl for t in trades if t.pnl < 0)
    senza3 = sorted(r)[:-3] if n > 3 else []
    m = {
        "trade": n,
        "profit_factor": (vinti / persi) if persi > 0 else (math.inf if vinti > 0 else 0.0),
        "r_medio": float(np.mean(r)) if n else 0.0,
        "r_medio_per_anno": {a: float(np.mean(v)) for a, v in per_anno.items()},
        "trade_per_anno": {a: len(v) for a, v in per_anno.items()},
        "r_medio_senza_3_migliori": float(np.mean(senza3)) if senza3 else None,
        "win_rate": sum(1 for x in r if x > 0) / n if n else 0.0,
        "r_mediano": float(np.median(r)) if n else 0.0,
    }
    if ris is not None:
        mm = motore.calcola_metriche(ris)
        m.update({
            "drawdown_max": mm["drawdown_max"],
            "rendimento_totale": mm["rendimento_totale"],
            "rendimento_per_anno": {str(k): v for k, v in mm["rendimento_per_anno"].items()},
            "n_ridotti_tetto_leva": mm["n_ridotti"],
            "n_violazioni_liquidazione": mm["n_violazioni_liquidazione"],
            "esiti": mm["esiti"],
            "n_buchi_dati": mm["n_buchi_dati"],
            "n_funding_in_buco": mm["n_funding_in_buco"],
            "funding_totale": mm["funding_totale"],
            "costi_totali": mm["costi_totali"],
        })
    return m


def buy_and_hold_per_anno(serie: Serie, solo_dopo_ts: Optional[int] = None) -> dict:
    per_anno: Dict[str, List[Candela]] = {}
    for c in serie.candele:
        if solo_dopo_ts is not None and c.ts < solo_dopo_ts:
            continue
        per_anno.setdefault(str(datetime.fromtimestamp(c.ts / 1000, tz=timezone.utc).year), []).append(c)
    return {a: {"long": motore.buy_and_hold(cs, PARAMETRI, "long"), "short": motore.buy_and_hold(cs, PARAMETRI, "short")}
            for a, cs in per_anno.items()}


def _riassunto_confronto(c: dict) -> dict:
    chiavi = ["differenza", "errore_standard", "errore_candidato", "errore_minimo", "soglia", "t", "netta",
              "valutabile", "n_blocchi", "p_value", "baseline_media", "baseline_errore_standard"]
    return {k: c.get(k) for k in chiavi}


def esame(var: Variante, parametri: Parametri = PARAMETRI, periodo: str = "costruzione",
          serie: Optional[Serie] = None) -> dict:
    """Candidato, baseline (a) e (b), percentile, buy and hold: il risultato della sezione 6.

    periodo 'validazione': la serie va dall'inizio della costruzione alla fine della
    validazione, contano solo i trade entrati dopo la fine della costruzione, e la (b)
    entra a caso solo nelle barre di validazione (le barre di costruzione sono vietate).
    """
    serie = serie or carica(var.tf, periodo)
    ind = var.prepara(serie)
    crea_strategia, crea_casuale, crea_segnale = _fabbriche(var, serie, ind)
    kw = dict(candele_mark=serie.mark, funding=serie.funding)
    ms = MS[var.tf]

    def filtra(trades):
        if periodo == "validazione":
            return [t for t in trades if t.ts_entrata > FINE_COSTRUZIONE_TS]
        return list(trades)

    ris = motore.esegui(serie.candele, None, serie.mark, serie.funding, crea_strategia(True)(), parametri)
    trades = _ordina_per_uscita(filtra(ris.trades))
    out: dict = {"metriche": _metriche(trades, ris if periodo == "costruzione" else None)}
    if periodo == "validazione":
        out["metriche"]["n_ridotti_tetto_leva"] = sum(1 for t in trades if t.ridotto)
        out["metriche"]["n_violazioni_liquidazione"] = sum(1 for t in trades if t.violazione_liquidazione)
        vinti = sum(t.pnl for t in trades if t.pnl > 0)
        out["metriche"]["rendimento_trade_validazione"] = sum(t.pnl_pct for t in trades)
    out["buy_and_hold_per_anno"] = buy_and_hold_per_anno(serie, INIZIO_VALIDAZIONE_TS if periodo == "validazione" else None)
    n = len(trades)
    if n < 2:
        out["valutabile"] = False
        out["commento_tecnico"] = "meno di 2 trade"
        return out
    r = [t.r for t in trades]
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    out["blocco"] = blocco

    # baseline (a): stessa variante senza condizione d'ingresso e senza filtri
    if periodo == "costruzione":
        ris_a = motore.esegui(serie.candele, None, serie.mark, serie.funding, crea_strategia(False)(), parametri)
        ta = _ordina_per_uscita(ris_a.trades)
        if len(ta) >= 2:
            blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in ta], [t.ts_uscita for t in ta])
            base_a = statistica.baseline_da_trade([t.r for t in ta], blocco_a, n=BOOT_N, seme=BOOT_SEME)
            ca = statistica.contro_baseline(r, blocco, base_a, n=BOOT_N, seme=BOOT_SEME)
            out["baseline_a"] = {"media": base_a["media"], "errore_standard": base_a["errore_standard"],
                                 "n_trade": base_a["n_trade"], "blocco_a": blocco_a, "n_blocchi_a": base_a["n_blocchi"],
                                 "valutabile_a": base_a["valutabile"], **_riassunto_confronto(ca)}
        else:
            out["baseline_a"] = {"valutabile": False, "netta": False, "t": -math.inf, "n_trade": len(ta)}

    # baseline (b): entrate casuali con la stessa uscita
    durata = motore.durata_media_barre(trades, ms)
    vietate_segnale = motore.barre_vietate_segnale_non_valido(serie.candele, crea_segnale, parametri)
    maschera = list(serie.vietate_liquidita)
    if periodo == "validazione":
        maschera = [m or (c.ts <= FINE_COSTRUZIONE_TS) for m, c in zip(maschera, serie.candele)]
    vietate = vietate_segnale + intervalli(maschera)
    quota_vietate_segnale = sum(b - a for a, b in vietate_segnale) / serie.n
    try:
        base_b = motore.simula_baseline_casuale(serie.candele, crea_casuale, n, durata, parametri, candele_mark=serie.mark,
                                                funding=serie.funding, barre_vietate=vietate, n_simulazioni=N_SIM_B,
                                                primo_seme=0)
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "netta": False, "t": -math.inf, "errore": str(e)}
        out["valutabile"] = False
        return out
    cb = statistica.contro_baseline(r, blocco, base_b, n=BOOT_N, seme=BOOT_SEME)
    out["baseline_b"] = {"media": base_b["media"], "errore_standard": base_b["errore_standard"],
                         "n_simulazioni": base_b["n_simulazioni"],
                         "trade_per_simulazione_medio": float(np.mean(base_b["trade_per_simulazione"])),
                         "simulazioni_vuote": base_b["simulazioni_vuote"],
                         "segnali_non_validi_per_simulazione_medio": float(np.mean(base_b["segnali_non_validi_per_simulazione"])),
                         "quota_barre_vietate_segnale_non_valido": quota_vietate_segnale,
                         "durata_media_barre": durata,
                         **_riassunto_confronto(cb)}
    out["percentile_caso"] = statistica.percentile_del_candidato(float(np.mean(r)), base_b["valori"])
    va = out.get("baseline_a", {}).get("valutabile", True)
    out["valutabile"] = bool(cb["valutabile"] and (va if periodo == "costruzione" else True))
    if periodo == "costruzione":
        out["candidato"] = bool(out["baseline_a"].get("netta") and cb["netta"] and out["metriche"]["r_medio"] > 0)
    return out


def trade_di(var: Variante, parametri: Parametri = PARAMETRI, periodo: str = "costruzione"):
    serie = carica(var.tf, periodo)
    ind = var.prepara(serie)
    crea_strategia, _, _ = _fabbriche(var, serie, ind)
    ris = motore.esegui(serie.candele, None, serie.mark, serie.funding, crea_strategia(True)(), parametri)
    return serie, ind, ris


def prossimo_numero_variante() -> int:
    return 1 + sum(1 for v in registro.voci() if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante")
