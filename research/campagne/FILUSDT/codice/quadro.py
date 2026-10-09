"""Quadro comune delle varianti della campagna FILUSDT.

Ogni variante e' descritta da una ``Variante``: timeframe, direzione e quattro funzioni che,
date le serie caricate (``Serie``), restituiscono array numpy lunghi quanto le barre:

* ``ingresso(s)``  -> bool: condizione d'ingresso dell'ipotesi alla CHIUSURA della barra i;
* ``stop(s)``      -> float: prezzo dello stop se si entrasse alla barra dopo (NaN = non calcolabile);
* ``target(s)``    -> float o None: prezzo del target (NaN = nessun target);
* ``uscita(s)``    -> bool o None: condizione d'uscita «chiudi» alla chiusura della barra i;
* ``barre_max``    -> uscita a tempo dopo N barre in posizione (None = nessuna).

Tutti gli array si calcolano con dati fino alla barra i compresa (indicatori causali): la
strategia legge l'elemento i quando il motore le passa le barre 0..i, quindi non vede il futuro.
Le serie del test di validazione partono dall'inizio della costruzione (indicatori caldi) e gli
indicatori causali coincidono, sulle barre comuni, con quelli della costruzione.

Il filtro di liquidita' della Fase 0 (mesi sotto 20 milioni di USDT al giorno) vale per la
variante, per ``conta_trade`` e per la baseline (a); le stesse barre vanno vietate alla (b).
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

import comune
from research.src import dati, motore, statistica
from research.src.motore import Segnale

MS = {"15m": 900_000, "30m": 1_800_000, "1h": 3_600_000, "2h": 7_200_000, "4h": 14_400_000,
      "6h": 21_600_000, "8h": 28_800_000, "12h": 43_200_000, "1d": 86_400_000}

FILE_MESI_ESCLUSI = comune.CARTELLA_CAMPAGNA / "mesi_esclusi.json"


def mesi_esclusi() -> List[str]:
    """I mesi 'AAAA-MM' sotto la liquidita' minima, scritti in Fase 0."""
    return json.loads(FILE_MESI_ESCLUSI.read_text())["mesi_esclusi"]


# ---------------------------------------------------------------------------
# Serie
# ---------------------------------------------------------------------------


@dataclass
class Serie:
    tf: str
    candele: list
    mark: list
    funding: list
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray
    v_usdt: np.ndarray
    ts: np.ndarray
    close_ts: np.ndarray
    ammessa: np.ndarray  # barra in un mese liquido
    indice_ts: Dict[int, int]
    btc_c: Optional[np.ndarray] = None  # close di BTCUSDT sugli stessi ts (NaN se manca)
    extra: Dict[str, object] = field(default_factory=dict)


_CACHE: Dict[Tuple[str, str], Serie] = {}


def carica(tf: str, periodo: str = "costruzione") -> Serie:
    """Serie allineate di FILUSDT dall'inizio della costruzione alla fine del periodo indicato."""
    chiave = (tf, periodo)
    if chiave in _CACHE:
        return _CACHE[chiave]
    p = comune.PERIODI
    fine = p["fine_costruzione"] if periodo == "costruzione" else p["fine_validazione"]
    ris = dati.carica_serie_allineate(comune.SIMBOLO, tf, p["inizio"], fine)
    candele, mark = ris["candele"], ris["candele_mark"]
    funding = dati.carica_funding(comune.SIMBOLO, p["inizio"], fine)
    ts = np.array([c.ts for c in candele], dtype=np.int64)
    esclusi = set(mesi_esclusi())
    ammessa = np.array([datetime.fromtimestamp(t / 1000, tz=timezone.utc).strftime("%Y-%m") not in esclusi
                        for t in ts], dtype=bool)
    vol = np.array([np.nan if ris["volume_usdt"].get(int(t)) is None else ris["volume_usdt"][int(t)] for t in ts])
    btc = dati.carica_candele("BTCUSDT", tf, p["inizio"], fine)
    btc_per_ts = {b.ts: b.close for b in btc}
    btc_c = np.array([btc_per_ts.get(int(t), np.nan) for t in ts])
    s = Serie(
        tf=tf, candele=candele, mark=mark, funding=funding,
        o=np.array([c.open for c in candele]), h=np.array([c.high for c in candele]),
        l=np.array([c.low for c in candele]), c=np.array([c.close for c in candele]),
        v_usdt=vol, ts=ts, close_ts=np.array([c.close_ts for c in candele], dtype=np.int64),
        ammessa=ammessa, indice_ts={int(t): i for i, t in enumerate(ts)}, btc_c=btc_c,
        extra={"n_tolte_last": ris["n_tolte_last"], "n_tolte_mark": ris["n_tolte_mark"]},
    )
    _CACHE[chiave] = s
    return s


# ---------------------------------------------------------------------------
# Indicatori causali (il valore i usa solo le barre 0..i)
# ---------------------------------------------------------------------------


def sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(x.size, np.nan)
    if n <= x.size:
        cs = np.cumsum(np.insert(x.astype(float), 0, 0.0))
        out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def ema(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(x.size, np.nan)
    if n > x.size:
        return out
    a = 2.0 / (n + 1)
    out[n - 1] = x[:n].mean()
    for i in range(n, x.size):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def atr(s: Serie, n: int) -> np.ndarray:
    """ATR di Wilder su n barre."""
    pc = np.concatenate([[np.nan], s.c[:-1]])
    tr = np.nanmax(np.vstack([s.h - s.l, np.abs(s.h - pc), np.abs(s.l - pc)]), axis=0)
    out = np.full(tr.size, np.nan)
    if n < tr.size:
        out[n] = tr[1:n + 1].mean()
        for i in range(n + 1, tr.size):
            out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def rsi(x: np.ndarray, n: int) -> np.ndarray:
    """RSI di Wilder su n barre."""
    d = np.diff(x, prepend=np.nan)
    su = np.where(d > 0, d, 0.0)
    giu = np.where(d < 0, -d, 0.0)
    out = np.full(x.size, np.nan)
    if n >= x.size:
        return out
    ms, mg = su[1:n + 1].mean(), giu[1:n + 1].mean()
    for i in range(n, x.size):
        if i > n:
            ms = (ms * (n - 1) + su[i]) / n
            mg = (mg * (n - 1) + giu[i]) / n
        out[i] = 100.0 if mg == 0 else 100.0 - 100.0 / (1.0 + ms / mg)
    return out


def massimo_precedente(x: np.ndarray, n: int) -> np.ndarray:
    """Massimo delle n barre PRIMA della barra i (esclusa la i)."""
    out = np.full(x.size, np.nan)
    for i in range(n, x.size):
        out[i] = x[i - n:i].max()
    return out


def minimo_precedente(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(x.size, np.nan)
    for i in range(n, x.size):
        out[i] = x[i - n:i].min()
    return out


def rendimento(x: np.ndarray, n: int) -> np.ndarray:
    """x[i] / x[i-n] - 1."""
    out = np.full(x.size, np.nan)
    out[n:] = x[n:] / x[:-n] - 1.0
    return out


def dev_std_mobile(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(x.size, np.nan)
    for i in range(n - 1, x.size):
        out[i] = x[i - n + 1:i + 1].std(ddof=1)
    return out


def acquisti_taker_usdt(s: Serie) -> np.ndarray:
    """Volume in USDT degli acquisti aggressivi (colonna taker_buy_quote_volume, indice 10) per barra.

    Letto dagli stessi file mensili del last; NaN dove manca.
    """
    per_ts: Dict[int, float] = {}
    cartella = comune.CARTELLA_DATI / "klines" / s.tf
    for p in sorted(cartella.glob("*.zip")):
        for riga in dati.righe_csv_da_zip(p):
            ts = dati.normalizza_ts(riga[0])
            if ts not in per_ts and len(riga) > 10 and riga[10].strip():
                per_ts[ts] = float(riga[10])
    return np.array([per_ts.get(int(t), np.nan) for t in s.ts])


def ora_utc(s: Serie) -> np.ndarray:
    return (s.ts // 3_600_000) % 24


def giorno_settimana(s: Serie) -> np.ndarray:
    """0 = lunedi' (il 1970-01-01 era giovedi')."""
    return ((s.ts // 86_400_000) + 3) % 7


# ---------------------------------------------------------------------------
# Variante e strategie
# ---------------------------------------------------------------------------


@dataclass
class Variante:
    id: str
    tf: str
    direzione: str
    ingresso: Callable[[Serie], np.ndarray]
    stop: Callable[[Serie], np.ndarray]
    target: Optional[Callable[[Serie], np.ndarray]] = None
    uscita: Optional[Callable[[Serie], np.ndarray]] = None
    barre_max: Optional[int] = None
    descrizione: str = ""


@dataclass
class Calcolata:
    """Gli array della variante su una serie (calcolati una volta, letti dalle strategie)."""
    v: Variante
    s: Serie
    ingresso: np.ndarray
    stop: np.ndarray
    target: np.ndarray
    uscita: np.ndarray


def calcola(v: Variante, s: Serie) -> Calcolata:
    n = len(s.candele)
    ing = np.asarray(v.ingresso(s), dtype=bool)
    st = np.asarray(v.stop(s), dtype=float)
    tg = np.full(n, np.nan) if v.target is None else np.asarray(v.target(s), dtype=float)
    us = np.zeros(n, dtype=bool) if v.uscita is None else np.asarray(v.uscita(s), dtype=bool)
    for nome, arr in (("ingresso", ing), ("stop", st), ("target", tg), ("uscita", us)):
        if arr.shape != (n,):
            raise ValueError(f"{v.id}: {nome} ha forma {arr.shape}, attesa ({n},)")
    return Calcolata(v, s, ing, st, tg, us)


def _segnale(k: Calcolata, i: int) -> Optional[Segnale]:
    st = k.stop[i]
    if not math.isfinite(st) or st <= 0:
        return None
    tg = k.target[i]
    return Segnale(k.v.direzione, float(st), float(tg) if math.isfinite(tg) else None)


def _decidi_uscita(k: Calcolata, i: int, pos) -> Optional[str]:
    if k.uscita[i]:
        return "chiudi"
    if k.v.barre_max is not None:
        idx = k.s.indice_ts.get(pos.ts_entrata)
        if idx is not None and i - idx + 1 >= k.v.barre_max:
            return "chiudi"
    return None


def fabbrica_strategia(k: Calcolata, solo_ingressi: Optional[frozenset] = None, ogni_barra: bool = False):
    """Restituisce la FUNZIONE che crea la strategia (istanza nuova a ogni chiamata, sezione 7).

    * normale: entra se ingresso[i] e la barra e' in un mese liquido;
    * ``ogni_barra`` (baseline a): entra a ogni barra libera in un mese liquido col segnale valido;
    * ``solo_ingressi`` (baseline b): entra solo alle barre indicate (le barre vietate le esclude
      gia' la scelta casuale).
    """
    def crea():
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is not None:
                return _decidi_uscita(k, i, pos)
            if solo_ingressi is not None:
                entra = i in solo_ingressi
            elif ogni_barra:
                entra = bool(k.s.ammessa[i])
            else:
                entra = bool(k.ingresso[i] and k.s.ammessa[i])
            return _segnale(k, i) if entra else None
        return strategia
    return crea


def fabbrica_casuale(k: Calcolata):
    def crea_casuale(ingressi: frozenset):
        return fabbrica_strategia(k, solo_ingressi=ingressi)()
    return crea_casuale


def fabbrica_segnale(k: Calcolata):
    def crea_segnale():
        def segnale(storia):
            return _segnale(k, len(storia) - 1)
        return segnale
    return crea_segnale


def intervalli_da_maschera(vietata: np.ndarray) -> List[Tuple[int, int]]:
    out: List[Tuple[int, int]] = []
    i, n = 0, vietata.size
    while i < n:
        if vietata[i]:
            j = i
            while j < n and vietata[j]:
                j += 1
            out.append((i, j))
            i = j
        else:
            i += 1
    return out


# ---------------------------------------------------------------------------
# Conteggio, test, baseline
# ---------------------------------------------------------------------------


def conta(v: Variante, moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0,
          riempimento: str = "stop_prima") -> Dict[str, int]:
    s = carica(v.tf, "costruzione")
    k = calcola(v, s)
    return motore.conta_trade(s.candele, fabbrica_strategia(k), comune.PERIODI["fine_costruzione_ts"],
                              comune.parametri(moltiplicatore_costi, ritardo_barre, riempimento),
                              candele_mark=s.mark, funding=s.funding)


def _anno(ts: int) -> int:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year


def _r_per_anno(trades) -> Dict[str, float]:
    per: Dict[int, List[float]] = {}
    for t in trades:
        per.setdefault(_anno(t.ts_uscita), []).append(t.r)
    return {str(a): float(np.mean(r)) for a, r in sorted(per.items())}


def _n_per_anno(trades) -> Dict[str, int]:
    per: Dict[int, int] = {}
    for t in trades:
        per[_anno(t.ts_uscita)] = per.get(_anno(t.ts_uscita), 0) + 1
    return {str(a): n for a, n in sorted(per.items())}


def _buy_and_hold_per_anno(s: Serie, da_indice: int, parametri) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    per: Dict[int, list] = {}
    for c in s.candele[da_indice:]:
        per.setdefault(_anno(c.ts), []).append(c)
    for a, cc in sorted(per.items()):
        out[str(a)] = {"long": motore.buy_and_hold(cc, parametri, "long"),
                       "short": motore.buy_and_hold(cc, parametri, "short")}
    return out


def _confronto_compatto(ris: Dict[str, object]) -> Dict[str, object]:
    chiavi = ("differenza", "errore_standard", "errore_candidato", "errore_minimo", "t", "soglia", "netta",
              "valutabile", "p_value", "n_blocchi", "baseline_media", "baseline_errore_standard")
    return {c: ris.get(c) for c in chiavi}


def esegui_test(v: Variante, periodo: str = "costruzione", moltiplicatore_costi: float = 1.0,
                ritardo_barre: int = 0, riempimento: str = "stop_prima", con_baseline_a: bool = True,
                n_simulazioni: int = 200) -> Dict[str, object]:
    """Il test della Fase 2 (o di una verifica) sul periodo indicato, con baseline (a) e (b).

    In validazione la serie va dall'inizio della costruzione alla fine della validazione e contano
    solo i trade ENTRATI dopo la fine della costruzione; alla (b) si vietano tutte le barre di
    costruzione, alla (a) contano solo i suoi trade entrati in validazione.
    """
    s = carica(v.tf, periodo)
    k = calcola(v, s)
    par = comune.parametri(moltiplicatore_costi, ritardo_barre, riempimento)
    fine_c = comune.PERIODI["fine_costruzione_ts"]
    if periodo == "validazione":
        primo = int(np.searchsorted(s.ts, fine_c + 1))
        filtro = lambda tr: [t for t in tr if t.ts_entrata > fine_c]
    else:
        primo = 0
        filtro = lambda tr: list(tr)

    ris = motore.esegui(s.candele, None, s.mark, s.funding, fabbrica_strategia(k)(), par)
    trades = sorted(filtro(ris.trades), key=lambda t: t.ts_uscita)
    n = len(trades)
    out: Dict[str, object] = {"periodo": periodo, "trade": n}
    if n == 0:
        out["valutabile"] = False
        return out
    r = np.array([t.r for t in trades])
    vinti = sum(t.pnl for t in trades if t.pnl > 0)
    persi = -sum(t.pnl for t in trades if t.pnl < 0)
    curva = [(trades[0].ts_entrata, par.capitale_iniziale)]
    cap = par.capitale_iniziale
    for t in trades:
        cap += t.pnl
        curva.append((t.ts_uscita, cap))
    migliori = np.sort(r)[::-1]
    metriche = {
        "profit_factor": (vinti / persi) if persi > 0 else math.inf,
        "trade": n,
        "r_medio": float(r.mean()),
        "r_mediano": float(np.median(r)),
        "win_rate": float(np.mean(r > 0)),
        "r_medio_per_anno": _r_per_anno(trades),
        "trade_per_anno": _n_per_anno(trades),
        "r_medio_senza_3_migliori": float(migliori[3:].mean()) if n > 3 else None,
        "drawdown_max": motore.drawdown_massimo(curva),
        "rendimento_totale": (cap - par.capitale_iniziale) / par.capitale_iniziale,
        "rendimento_per_anno": {str(a): x for a, x in motore.rendimento_per_anno(trades, par.capitale_iniziale).items()},
        "n_ridotti": sum(1 for t in trades if t.ridotto),
        "n_violazioni_liquidazione": sum(1 for t in trades if t.violazione_liquidazione),
        "esiti": {e: sum(1 for t in trades if t.esito == e) for e in ("stop", "target", "segnale", "liquidazione", "fine_dati")},
        "funding_totale_r": float(sum(t.funding_pagato / t.rischio_iniziale for t in trades)),
        "costi_medi_r": float(np.mean([(t.commissioni + t.slippage_costo + t.funding_pagato) / t.rischio_iniziale for t in trades])),
        "stop_medio_pct": float(np.mean([abs(t.entrata - t.stop) / t.entrata for t in trades])),
        "quota_stop_oltre_6pct": float(np.mean([abs(t.entrata - t.stop) / t.entrata > 0.06 for t in trades])),
        "n_buchi_dati": ris.n_buchi_dati,
        "n_segnali_non_validi": ris.n_segnali_non_validi,
    }
    out["metriche"] = metriche
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    out["blocco"] = blocco
    out["durata_media_barre"] = motore.durata_media_barre(trades, MS[v.tf])

    # Baseline (a): la variante senza condizione d'ingresso, a ogni barra libera (mesi liquidi).
    if con_baseline_a:
        ris_a = motore.esegui(s.candele, None, s.mark, s.funding, fabbrica_strategia(k, ogni_barra=True)(), par)
        tr_a = sorted(filtro(ris_a.trades), key=lambda t: t.ts_uscita)
        if len(tr_a) >= 2:
            blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in tr_a], [t.ts_uscita for t in tr_a])
            base_a = statistica.baseline_da_trade([t.r for t in tr_a], blocco_a)
            conf_a = statistica.contro_baseline(r, blocco, base_a)
            out["baseline_a"] = dict(_confronto_compatto(conf_a), media=base_a["media"], n_trade=base_a["n_trade"],
                                     blocco_a=blocco_a, n_blocchi_a=base_a["n_blocchi"], valutabile_a=base_a["valutabile"])
        else:
            out["baseline_a"] = {"valutabile": False, "netta": False, "t": -math.inf, "motivo": "meno di 2 trade nella (a)"}

    # Baseline (b): entrate casuali con la stessa uscita (simula_baseline_casuale).
    vietata = ~s.ammessa.copy()
    vietate_segnale = motore.barre_vietate_segnale_non_valido(s.candele, fabbrica_segnale(k), par)
    for a, b in vietate_segnale:
        vietata[a:b] = True
    n_vietate_segnale = int(sum(b - a for a, b in vietate_segnale))
    if periodo == "validazione":
        vietata[:primo] = True
    try:
        base_b = motore.simula_baseline_casuale(
            s.candele, fabbrica_casuale(k), n, out["durata_media_barre"], par, candele_mark=s.mark,
            funding=s.funding, barre_vietate=intervalli_da_maschera(vietata), n_simulazioni=n_simulazioni)
        conf_b = statistica.contro_baseline(r, blocco, base_b)
        out["baseline_b"] = dict(
            _confronto_compatto(conf_b), media=base_b["media"], n_simulazioni=base_b["n_simulazioni"],
            trade_per_simulazione_medio=float(np.mean(base_b["trade_per_simulazione"])),
            simulazioni_vuote=base_b["simulazioni_vuote"],
            segnali_non_validi_per_simulazione_medio=float(np.mean(base_b["segnali_non_validi_per_simulazione"])),
            quota_barre_vietate_segnale_non_valido=n_vietate_segnale / len(s.candele),
            quota_barre_vietate_totale=float(vietata.mean()))
        out["percentile_caso"] = statistica.percentile_del_candidato(float(r.mean()), base_b["valori"])
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "netta": False, "t": -math.inf, "motivo": str(e)}
        out["percentile_caso"] = None
    out["buy_and_hold_per_anno"] = _buy_and_hold_per_anno(s, primo, par)
    va = out.get("baseline_a", {}).get("valutabile", True) if con_baseline_a else True
    vb = out["baseline_b"].get("valutabile", False)
    out["valutabile"] = bool(va and vb)
    out["candidato"] = bool(out["valutabile"] and out.get("baseline_a", {}).get("netta", False)
                            and out["baseline_b"].get("netta", False) and metriche["r_medio"] > 0)
    out["_trades"] = trades
    return out
