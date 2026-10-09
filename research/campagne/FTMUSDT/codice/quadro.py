"""Il quadro comune delle varianti di FTMUSDT: dati, strategia, baseline (a) e (b), metriche.

Una variante si descrive con un oggetto ``Variante``:
* ``tf``, ``direzione``;
* ``prepara(serie)``: calcola UNA volta, sulle barre della serie, gli indicatori
  causali (ogni valore all'indice i usa solo le barre 0..i) e li restituisce in un
  dizionario ``ctx``; ``ctx`` e' di sola lettura, quindi ogni istanza della
  strategia (sezione 7, «un'istanza nuova a ogni esecuzione») parte dallo stesso
  stato;
* ``condizione(ctx, i)``: la condizione d'ingresso dell'ipotesi e i suoi filtri,
  alla chiusura della barra i;
* ``segnale(ctx, i)``: il Segnale (direzione, stop, target) alla barra i SENZA la
  condizione, oppure None se non si puo' calcolare (riscaldamento);
* ``uscita(ctx, i, pos)``: "chiudi" o None, con la posizione aperta.

Lo stesso ``segnale`` e la stessa ``uscita`` servono alla variante, alla baseline (a)
(ingresso a ogni barra libera, senza condizione e senza filtri dell'ipotesi, ma con
il filtro dei mesi illiquidi della Fase 0) e alla (b) (ingressi casuali).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timezone
from typing import Callable, Dict, List, Optional, Sequence

import numpy as np

from comune import PARAMETRI, PERIODI, SIMBOLO, dati, motore
from research.src import statistica

MS = {"15m": 900_000, "30m": 1_800_000, "1h": 3_600_000, "2h": 7_200_000, "4h": 14_400_000,
      "6h": 21_600_000, "8h": 28_800_000, "12h": 43_200_000, "1d": 86_400_000}

FINE_IN_SAMPLE = date(2023, 12, 31)


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------

@dataclass
class Serie:
    tf: str
    candele: List[motore.Candela]
    mark: List[motore.Candela]
    funding: List[tuple]
    o: np.ndarray = field(default=None)
    h: np.ndarray = field(default=None)
    l: np.ndarray = field(default=None)
    c: np.ndarray = field(default=None)
    v: np.ndarray = field(default=None)
    ts: np.ndarray = field(default=None)
    illiquida: np.ndarray = field(default=None)  # True se la barra di segnale cade in un mese sotto la soglia

    def __post_init__(self):
        self.o = np.array([x.open for x in self.candele])
        self.h = np.array([x.high for x in self.candele])
        self.l = np.array([x.low for x in self.candele])
        self.c = np.array([x.close for x in self.candele])
        self.v = np.array([x.volume for x in self.candele])
        self.ts = np.array([x.ts for x in self.candele], dtype=np.int64)
        mesi = mesi_illiquidi()
        self.illiquida = np.array([_mese(t) in mesi for t in self.ts], dtype=bool)


def _mese(ts_ms: int) -> str:
    d = datetime.fromtimestamp(int(ts_ms) / 1000, tz=timezone.utc)
    return f"{d.year:04d}-{d.month:02d}"


_MESI_ILLIQUIDI: Optional[set] = None


def mesi_illiquidi() -> set:
    """Mesi con volume medio giornaliero in USDT (quote_volume dei file 1d del last) sotto 20 milioni."""
    global _MESI_ILLIQUIDI
    if _MESI_ILLIQUIDI is None:
        vol = volumi_giornalieri()
        per_mese: Dict[str, List[float]] = {}
        for t, v in vol.items():
            per_mese.setdefault(_mese(t), []).append(v)
        _MESI_ILLIQUIDI = {m for m, vs in per_mese.items() if sum(vs) / len(vs) < 20_000_000}
    return _MESI_ILLIQUIDI


def volumi_giornalieri() -> Dict[int, float]:
    percorsi = dati._percorsi_presenti(SIMBOLO, "klines", "1d", PERIODI["inizio"], FINE_IN_SAMPLE, dati.RADICE_DEFAULT)
    vol: Dict[int, float] = {}
    for p in percorsi:
        for t, v in dati.volume_usdt_da_zip(p).items():
            vol.setdefault(t, v)
    return vol


_CACHE: Dict[tuple, Serie] = {}


def carica(tf: str, periodo: str = "costruzione") -> Serie:
    """Serie allineata last/mark e funding: ``costruzione`` (fino alla fine della costruzione) o ``validazione``
    (dall'inizio della costruzione alla fine della validazione, indicatori gia' caldi)."""
    chiave = (tf, periodo)
    if chiave in _CACHE:
        return _CACHE[chiave]
    fine = PERIODI["fine_costruzione"] if periodo == "costruzione" else PERIODI["fine_validazione"]
    s = dati.carica_serie_allineate(SIMBOLO, tf, PERIODI["inizio"], fine)
    funding = dati.carica_funding(SIMBOLO, PERIODI["inizio"], fine)
    serie = Serie(tf, s["candele"], s["candele_mark"], funding)
    _CACHE[chiave] = serie
    return serie


def carica_btc(tf: str) -> Dict[int, float]:
    """Close del last di BTCUSDT per ts (solo riferimento di mercato)."""
    cand = dati.carica_candele("BTCUSDT", tf, date(2020, 1, 1), FINE_IN_SAMPLE)
    return {x.ts: x.close for x in cand}


# ---------------------------------------------------------------------------
# Variante e strategie
# ---------------------------------------------------------------------------

@dataclass
class Variante:
    id: str
    tf: str
    direzione: str
    prepara: Callable[[Serie], dict]
    condizione: Callable[[dict, int], bool]
    segnale: Callable[[dict, int], Optional[motore.Segnale]]
    uscita: Callable[[dict, int, motore.Posizione], Optional[str]]


def barre_tenute(ctx: dict, i: int, pos: motore.Posizione) -> int:
    """Barre chiuse dall'ingresso: l'ingresso e' all'apertura di una barra, alla chiusura della barra i
    la posizione e' stata aperta per (chiusura i + 1 - ingresso) / durata barre."""
    s: Serie = ctx["serie"]
    return int(round((int(s.ts[i]) + MS[s.tf] - pos.ts_entrata) / MS[s.tf]))


def _fabbriche(var: Variante, serie: Serie):
    ctx = var.prepara(serie)
    ctx["serie"] = serie

    def crea_strategia():
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is not None:
                return var.uscita(ctx, i, pos)
            if serie.illiquida[i]:
                return None
            if var.condizione(ctx, i):
                return var.segnale(ctx, i)
            return None
        return strategia

    def crea_a():
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is not None:
                return var.uscita(ctx, i, pos)
            if serie.illiquida[i]:
                return None
            return var.segnale(ctx, i)
        return strategia

    def crea_casuale(ingressi):
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is not None:
                return var.uscita(ctx, i, pos)
            if i in ingressi:
                return var.segnale(ctx, i)
            return None
        return strategia

    def crea_segnale():
        def f(storia):
            return var.segnale(ctx, len(storia) - 1)
        return f

    return ctx, crea_strategia, crea_a, crea_casuale, crea_segnale


def intervalli_illiquidi(serie: Serie) -> List[tuple]:
    out = []
    for i, x in enumerate(serie.illiquida):
        if x:
            if out and out[-1][1] == i:
                out[-1] = (out[-1][0], i + 1)
            else:
                out.append((i, i + 1))
    return out


def conta(var: Variante) -> Dict[str, int]:
    """La stima dei trade (sezione 8): una volta sola per variante, sulle regole registrate."""
    serie = carica(var.tf, "costruzione")
    _, crea_strategia, _, _, _ = _fabbriche(var, serie)
    return motore.conta_trade(serie.candele, crea_strategia, PERIODI["fine_costruzione_ts"], PARAMETRI,
                              candele_mark=serie.mark, funding=serie.funding)


# ---------------------------------------------------------------------------
# Metriche
# ---------------------------------------------------------------------------

def _anno(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year


def metriche_trade(ris: motore.Risultato) -> dict:
    trades = sorted(ris.trades, key=lambda t: t.ts_uscita)
    m = motore.calcola_metriche(ris)
    r = [t.r for t in trades]
    per_anno: Dict[int, List[float]] = {}
    for t in trades:
        per_anno.setdefault(_anno(t.ts_uscita), []).append(t.r)
    migliori = sorted(r, reverse=True)[3:]
    return {
        "profit_factor": m["profit_factor"], "trade": len(trades), "r_medio": float(np.mean(r)) if r else 0.0,
        "r_medio_per_anno": {a: float(np.mean(v)) for a, v in sorted(per_anno.items())},
        "trade_per_anno": {a: len(v) for a, v in sorted(per_anno.items())},
        "r_medio_senza_3_migliori": float(np.mean(migliori)) if migliori else 0.0,
        "drawdown_max": -m["drawdown_max"], "rendimento_totale": m["rendimento_totale"],
        "rendimento_per_anno": m["rendimento_per_anno"], "win_rate": m["win_rate"],
        "n_ridotti": m["n_ridotti"], "n_violazioni_liquidazione": m["n_violazioni_liquidazione"],
        "esiti": m["esiti"], "n_buchi_dati": m["n_buchi_dati"], "n_funding_in_buco": m["n_funding_in_buco"],
        "funding_totale": m["funding_totale"], "costi_totali": m["costi_totali"],
    }


def buy_and_hold_per_anno(serie: Serie, solo_da_ts: int = 0) -> dict:
    out = {}
    per_anno: Dict[int, List[motore.Candela]] = {}
    for x in serie.candele:
        if x.ts >= solo_da_ts:
            per_anno.setdefault(_anno(x.ts), []).append(x)
    for a, cs in sorted(per_anno.items()):
        out[a] = {"long": motore.buy_and_hold(cs, PARAMETRI, "long"), "short": motore.buy_and_hold(cs, PARAMETRI, "short")}
    return out


def mercato_btc(trades: Sequence[motore.Trade], tf: str) -> dict:
    """Contesto «e' solo il mercato»: rendimento di BTCUSDT nella direzione del trade, sullo stesso intervallo."""
    btc = carica_btc(tf)
    ts_ord = sorted(btc)
    import bisect
    def prezzo(ts):
        k = bisect.bisect_right(ts_ord, ts) - 1
        return btc[ts_ord[k]] if k >= 0 else None
    rb, rr = [], []
    for t in trades:
        p0, p1 = prezzo(t.ts_entrata - 1), prezzo(t.ts_uscita - MS[tf] + 1)
        if p0 and p1:
            rb.append((p1 / p0 - 1) * (1 if t.direzione == "long" else -1))
            rr.append(t.r)
    if len(rb) < 3:
        return {}
    corr = float(np.corrcoef(rb, rr)[0, 1]) if np.std(rb) > 0 and np.std(rr) > 0 else 0.0
    return {"btc_rendimento_medio_nella_direzione": float(np.mean(rb)),
            "quota_trade_con_btc_a_favore": float(np.mean(np.array(rb) > 0)),
            "correlazione_r_con_btc": corr}


# ---------------------------------------------------------------------------
# Il test di Fase 2 (costruzione)
# ---------------------------------------------------------------------------

def test_costruzione(var: Variante, parametri: motore.Parametri = PARAMETRI, con_b: bool = True) -> dict:
    serie = carica(var.tf, "costruzione")
    ctx, crea_strategia, crea_a, crea_casuale, crea_segnale = _fabbriche(var, serie)
    ris = motore.esegui(serie.candele, None, serie.mark, serie.funding, crea_strategia(), parametri)
    trades = sorted(ris.trades, key=lambda t: t.ts_uscita)
    out = {"metriche": metriche_trade(ris)}
    if not trades:
        return out
    r = [t.r for t in trades]
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    out["blocco"] = blocco

    # Baseline (a)
    ris_a = motore.esegui(serie.candele, None, serie.mark, serie.funding, crea_a(), parametri)
    ta = sorted(ris_a.trades, key=lambda t: t.ts_uscita)
    if len(ta) >= 2:
        blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in ta], [t.ts_uscita for t in ta])
        base_a = statistica.baseline_da_trade([t.r for t in ta], blocco_a)
        conf_a = statistica.contro_baseline(r, blocco, base_a)
        out["baseline_a"] = {"media": base_a["media"], "errore_standard": base_a["errore_standard"],
                             "n_trade": base_a["n_trade"], "blocco_a": blocco_a, "n_blocchi_a": base_a["n_blocchi"],
                             **_conf(conf_a)}
    else:
        out["baseline_a"] = {"valutabile": False, "netta": False, "t": -math.inf, "n_trade": len(ta)}

    # Baseline (b)
    if con_b:
        durata = motore.durata_media_barre(trades, MS[var.tf])
        vietate_segnale = motore.barre_vietate_segnale_non_valido(serie.candele, crea_segnale, parametri)
        n_vietate = sum(b - a for a, b in vietate_segnale)
        vietate = vietate_segnale + intervalli_illiquidi(serie)
        try:
            base_b = motore.simula_baseline_casuale(serie.candele, crea_casuale, len(trades), durata, parametri,
                                                    candele_mark=serie.mark, funding=serie.funding,
                                                    barre_vietate=vietate, n_simulazioni=200, primo_seme=0)
            conf_b = statistica.contro_baseline(r, blocco, base_b)
            out["baseline_b"] = {"media": base_b["media"], "errore_standard": base_b["errore_standard"],
                                 "n_simulazioni": base_b["n_simulazioni"],
                                 "trade_per_simulazione_medio": float(np.mean(base_b["trade_per_simulazione"])),
                                 "simulazioni_vuote": base_b["simulazioni_vuote"],
                                 "segnali_non_validi_per_simulazione_medio": float(np.mean(base_b["segnali_non_validi_per_simulazione"])),
                                 "quota_barre_vietate_segnale_non_valido": n_vietate / len(serie.candele),
                                 "durata_media_barre": durata, **_conf(conf_b)}
            out["percentile_caso"] = statistica.percentile_del_candidato(float(np.mean(r)), base_b["valori"])
        except ValueError as e:
            out["baseline_b"] = {"valutabile": False, "netta": False, "t": -math.inf, "errore": str(e)}
    out["buy_and_hold_per_anno"] = buy_and_hold_per_anno(serie)
    out["mercato_btc"] = mercato_btc(trades, var.tf)
    return out


def _conf(c: dict) -> dict:
    chiavi = ("differenza", "errore_standard", "errore_minimo", "errore_candidato", "n_blocchi", "t", "soglia",
              "p_value", "netta", "valutabile")
    d = {k: c[k] for k in chiavi if k in c}
    d["errore_standard_differenza"] = d.pop("errore_standard", None)
    return d


def candidato(out: dict) -> bool:
    a, b = out.get("baseline_a", {}), out.get("baseline_b", {})
    return bool(a.get("netta") and b.get("netta") and out["metriche"]["r_medio"] > 0)
