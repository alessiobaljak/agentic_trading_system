"""Strumenti comuni della campagna ADAUSDT: dati, parametri, filtro di liquidita', fabbriche delle
strategie e valutazione di una variante con le regole della sezione 8 del protocollo.

Niente strategie qui: le varianti stanno in `varianti.py`. Ogni indicatore delle varianti si calcola
una volta sull'intera serie con funzioni CAUSALI (il valore alla barra i usa solo le barre 0..i);
la strategia alla barra i legge solo l'indice i = len(storia) - 1. Le fabbriche creano un'istanza
nuova a ogni esecuzione del motore (sezione 7).
"""
from __future__ import annotations

import math
import multiprocessing as mp
import sys
from dataclasses import replace
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

RADICE = Path(__file__).resolve().parents[4]
if str(RADICE) not in sys.path:
    sys.path.insert(0, str(RADICE))

from research.src import dati, motore, statistica  # noqa: E402
from research.src.motore import Candela, Parametri, Segnale  # noqa: E402

SIMBOLO = "ADAUSDT"
INIZIO = date(2020, 1, 1)
FINE_COSTRUZIONE = date(2022, 10, 18)
FINE_COSTRUZIONE_TS = 1666137599999
FINE_VALIDAZIONE = date(2023, 12, 31)
MESI_ESCLUSI = {(2020, 1), (2020, 3), (2020, 4)}  # fase0_dati.md
TRADE_MINIMI_COSTRUZIONE = 70

# config/parametri.yaml (congelato) e scheda_moneta.md (slippage 0,02%)
PARAM = Parametri(
    commissione_per_lato=0.0005,
    slippage_per_lato=0.0002,
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
N_SIM = 200
BOOT_N, BOOT_SEME = 2000, 0


def anno_ms(ts: int) -> int:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year


def mese_ms(ts: int) -> Tuple[int, int]:
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return d.year, d.month


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------

_CACHE: Dict[Tuple[str, str], Dict[str, object]] = {}


def carica(tf: str, periodo: str = "costruzione") -> Dict[str, object]:
    """Last e mark allineati (carica_serie_allineate), funding e BTCUSDT last sugli stessi ts."""
    chiave = (tf, periodo)
    if chiave in _CACHE:
        return _CACHE[chiave]
    fine = FINE_COSTRUZIONE if periodo == "costruzione" else FINE_VALIDAZIONE
    s = dati.carica_serie_allineate(SIMBOLO, tf, INIZIO, fine)
    candele: List[Candela] = s["candele"]
    funding = dati.carica_funding(SIMBOLO, INIZIO, fine)
    btc = {c.ts: c for c in dati.carica_candele("BTCUSDT", tf, INIZIO, fine)}
    btc_close = np.array([btc[c.ts].close if c.ts in btc else np.nan for c in candele])
    ris = {
        "tf": tf,
        "candele": candele,
        "mark": s["candele_mark"],
        "funding": funding,
        "volume_usdt": np.array([s["volume_usdt"][c.ts] or np.nan for c in candele]),
        "btc_close": btc_close,
        "passo": dati.durata_intervallo(tf),
    }
    _CACHE[chiave] = ris
    return ris


def maschera_esclusi(candele: Sequence[Candela]) -> np.ndarray:
    return np.array([mese_ms(c.ts) in MESI_ESCLUSI for c in candele], dtype=bool)


def intervalli_da_maschera(m: np.ndarray) -> List[Tuple[int, int]]:
    out: List[Tuple[int, int]] = []
    i, n = 0, len(m)
    while i < n:
        if m[i]:
            j = i
            while j < n and m[j]:
                j += 1
            out.append((i, j))
            i = j
        else:
            i += 1
    return out


# ---------------------------------------------------------------------------
# Indicatori causali (valore alla barra i dalle barre 0..i)
# ---------------------------------------------------------------------------


def arrays(candele: Sequence[Candela]) -> Dict[str, np.ndarray]:
    return {
        "o": np.array([c.open for c in candele]),
        "h": np.array([c.high for c in candele]),
        "l": np.array([c.low for c in candele]),
        "c": np.array([c.close for c in candele]),
        "v": np.array([c.volume for c in candele]),
        "ts": np.array([c.ts for c in candele], dtype=np.int64),
    }


def sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        cs = np.cumsum(np.insert(x, 0, 0.0))
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


def true_range(h, l, c) -> np.ndarray:
    pc = np.insert(c[:-1], 0, np.nan)
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    tr[0] = h[0] - l[0]
    return tr


def atr(h, l, c, n: int) -> np.ndarray:
    """ATR di Wilder: media semplice delle prime n, poi (prec*(n-1)+tr)/n."""
    tr = true_range(h, l, c)
    out = np.full(len(tr), np.nan)
    if len(tr) < n:
        return out
    out[n - 1] = tr[:n].mean()
    for i in range(n, len(tr)):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def rsi(c: np.ndarray, n: int) -> np.ndarray:
    d = np.diff(c, prepend=np.nan)
    g = np.where(d > 0, d, 0.0)
    p = np.where(d < 0, -d, 0.0)
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    ag, ap = g[1:n + 1].mean(), p[1:n + 1].mean()
    out[n] = 100.0 if ap == 0 else 100 - 100 / (1 + ag / ap)
    for i in range(n + 1, len(c)):
        ag = (ag * (n - 1) + g[i]) / n
        ap = (ap * (n - 1) + p[i]) / n
        out[i] = 100.0 if ap == 0 else 100 - 100 / (1 + ag / ap)
    return out


def massimo_precedente(x: np.ndarray, n: int) -> np.ndarray:
    """Massimo delle n barre PRIMA della barra i (i-n..i-1)."""
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
    out = np.full(len(c), np.nan)
    out[n:] = c[n:] / c[:-n] - 1.0
    return out


def std_mobile(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = x[i - n + 1:i + 1].std(ddof=1)
    return out


# ---------------------------------------------------------------------------
# Variante: interfaccia e fabbriche
# ---------------------------------------------------------------------------


class Variante:
    """Una regola completa. Le sottoclassi definiscono:

    * ``prepara(D)``: dizionario di array causali calcolati sulla serie D (da ``carica``);
    * ``segnale(i, P)``: il Segnale (direzione, stop, target) emesso alla chiusura della barra i
      SENZA la condizione d'ingresso, o None se non calcolabile (riscaldamento);
    * ``condizione(i, P)``: la condizione d'ingresso dell'ipotesi (con i suoi filtri);
    * ``uscita(i, P, barre_in_posizione)``: True per chiudere all'apertura della barra dopo.
    """

    tf = "1h"
    direzione = "long"

    def __init__(self, **parametri):
        self.p = dict(parametri)

    def prepara(self, D) -> dict:
        raise NotImplementedError

    def segnale(self, i: int, P: dict) -> Optional[Segnale]:
        raise NotImplementedError

    def condizione(self, i: int, P: dict) -> bool:
        raise NotImplementedError

    def uscita(self, i: int, P: dict, barre: int) -> bool:
        return False

    def descrizione(self) -> dict:
        return {"classe": type(self).__name__, "timeframe": self.tf, "direzione": self.direzione, "parametri": self.p}


class Fabbriche:
    """Le funzioni che creano le strategie della variante, della baseline (a), della (b) e il segnale."""

    def __init__(self, var: Variante, D: dict, solo_dopo_ts: Optional[int] = None):
        self.var = var
        self.D = D
        self.P = var.prepara(D)
        self.escl = maschera_esclusi(D["candele"])
        self.idx = {c.ts: k for k, c in enumerate(D["candele"])}
        # in validazione: nessun ingresso su segnali di barre di costruzione
        if solo_dopo_ts is not None:
            ts = np.array([c.close_ts for c in D["candele"]])
            self.escl = self.escl | (ts <= solo_dopo_ts)

    def _uscita(self, i, pos):
        barre = i - self.idx[pos.ts_entrata] + 1
        return "chiudi" if self.var.uscita(i, self.P, barre) else None

    def crea_strategia(self):
        var, P, escl = self.var, self.P, self.escl

        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is None:
                if escl[i] or not var.condizione(i, P):
                    return None
                return var.segnale(i, P)
            return self._uscita(i, pos)

        return strategia

    def crea_a(self):
        var, P, escl = self.var, self.P, self.escl

        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is None:
                if escl[i]:
                    return None
                return var.segnale(i, P)
            return self._uscita(i, pos)

        return strategia

    def crea_casuale(self, ingressi):
        var, P = self.var, self.P

        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is None:
                return var.segnale(i, P) if i in ingressi else None
            return self._uscita(i, pos)

        return strategia

    def crea_segnale(self):
        var, P = self.var, self.P
        return lambda storia: var.segnale(len(storia) - 1, P)

    def barre_vietate(self, parametri: Parametri) -> Tuple[List[Tuple[int, int]], float]:
        v = motore.barre_vietate_segnale_non_valido(self.D["candele"], self.crea_segnale, parametri)
        m = np.zeros(len(self.D["candele"]), dtype=bool)
        for a, b in v:
            m[a:b] = True
        m |= self.escl
        return intervalli_da_maschera(m), float(m.mean())


# ---------------------------------------------------------------------------
# Conta dei trade (una volta per variante, sulle regole registrate)
# ---------------------------------------------------------------------------


def conta(var: Variante) -> Dict[str, int]:
    D = carica(var.tf, "costruzione")
    F = Fabbriche(var, D)
    return motore.conta_trade(D["candele"], F.crea_strategia, FINE_COSTRUZIONE_TS, PARAM,
                              candele_mark=D["mark"], funding=D["funding"])


# ---------------------------------------------------------------------------
# Baseline (b) in parallelo: stessi semi 0..199, a pezzi; i valori per seme sono identici
# ---------------------------------------------------------------------------

_LAVORO = {}


def _pezzo(args):
    primo, n = args
    L = _LAVORO
    r = motore.simula_baseline_casuale(L["candele"], L["crea"], L["n_trade"], L["durata"], L["param"],
                                       None, L["mark"], L["funding"], L["vietate"], n_simulazioni=n, primo_seme=primo)
    return (list(r["valori"]), r["trade_per_simulazione"], r["simulazioni_vuote"],
            r["segnali_non_validi_per_simulazione"], r["segnali_senza_barra_per_simulazione"])


def baseline_b(candele, mark, funding, crea, n_trade, durata, param, vietate, n_sim=N_SIM, processi=4):
    global _LAVORO
    _LAVORO = dict(candele=candele, mark=mark, funding=funding, crea=crea, n_trade=n_trade, durata=durata,
                   param=param, vietate=vietate)
    pezzi = []
    passo = math.ceil(n_sim / processi)
    for k in range(0, n_sim, passo):
        pezzi.append((k, min(passo, n_sim - k)))
    ctx = mp.get_context("fork")
    with ctx.Pool(processi) as pool:
        out = pool.map(_pezzo, pezzi)
    valori = [x for o in out for x in o[0]]
    base = statistica.baseline_casuale(valori)
    base["trade_per_simulazione"] = [x for o in out for x in o[1]]
    base["simulazioni_vuote"] = sum(o[2] for o in out)
    base["segnali_non_validi_per_simulazione"] = [x for o in out for x in o[3]]
    base["segnali_senza_barra_per_simulazione"] = [x for o in out for x in o[4]]
    return base


# ---------------------------------------------------------------------------
# Valutazione (Fase 2) e verifiche
# ---------------------------------------------------------------------------


def _r_per_anno(trades) -> Dict[str, float]:
    per = {}
    for t in trades:
        per.setdefault(anno_ms(t.ts_uscita), []).append(t.r)
    return {str(a): float(np.mean(v)) for a, v in sorted(per.items())}


def _n_per_anno(trades) -> Dict[str, int]:
    per = {}
    for t in trades:
        a = str(anno_ms(t.ts_uscita))
        per[a] = per.get(a, 0) + 1
    return per


def buy_and_hold_per_anno(candele, param) -> Dict[str, Dict[str, float]]:
    per = {}
    for c in candele:
        per.setdefault(anno_ms(c.ts), []).append(c)
    return {str(a): {"long": motore.buy_and_hold(v, param, "long"), "short": motore.buy_and_hold(v, param, "short")}
            for a, v in sorted(per.items())}


def _sintesi_confronto(c: dict) -> dict:
    chiavi = ("differenza", "errore_standard", "errore_candidato", "errore_minimo", "t", "soglia", "netta",
              "valutabile", "p_value", "n_blocchi", "gradi_liberta", "baseline_media", "baseline_errore_standard")
    return {k: c.get(k) for k in chiavi}


def valuta(var: Variante, param: Parametri = PARAM, periodo: str = "costruzione", processi: int = 4,
           extra: bool = True) -> dict:
    """Esegue la variante e le baseline (a) e (b) sullo stesso periodo, con contro_baseline.

    periodo "costruzione": serie fino al 2022-10-18. "validazione": serie dall'inizio al 2023-12-31,
    contano solo i trade entrati dopo la fine della costruzione; la (a) e la (b) solo in validazione.
    """
    D = carica(var.tf, "costruzione" if periodo == "costruzione" else "validazione")
    solo_dopo = None if periodo == "costruzione" else FINE_COSTRUZIONE_TS
    F = Fabbriche(var, D, solo_dopo_ts=solo_dopo)
    candele, mark, funding = D["candele"], D["mark"], D["funding"]

    ris = motore.esegui(candele, None, mark, funding, F.crea_strategia(), param)
    trades = [t for t in ris.trades if solo_dopo is None or t.ts_entrata > solo_dopo]
    out: dict = {"periodo": periodo, "timeframe": var.tf, "direzione": var.direzione}
    if len(trades) == 0:
        out["metriche"] = {"trade": 0}
        return out
    r = [t.r for t in trades]
    met = motore.calcola_metriche(motore.Risultato(trades, ris.curva_capitale, ris.capitale_iniziale,
                                                   ris.capitale_finale))
    migliori = sorted(r, reverse=True)
    out["metriche"] = {
        "profit_factor": met["profit_factor"], "trade": len(trades), "r_medio": float(np.mean(r)),
        "r_medio_per_anno": _r_per_anno(trades), "trade_per_anno": _n_per_anno(trades),
        "r_medio_senza_3_migliori": float(np.mean(migliori[3:])) if len(r) > 3 else None,
        "drawdown_max": met["drawdown_max"] if solo_dopo is None else None,
        "rendimento_totale": float(sum(t.pnl for t in trades) / param.capitale_iniziale),
        "rendimento_per_anno": {str(k): v for k, v in met["rendimento_per_anno"].items()},
        "win_rate": met["win_rate"], "esiti": met["esiti"], "trade_ridotti": met["n_ridotti"],
        "violazioni_liquidazione": met["n_violazioni_liquidazione"],
        "segnali_non_validi": ris.n_segnali_non_validi, "buchi_dati": ris.n_buchi_dati,
        "funding_in_buco": ris.n_funding_in_buco,
        "stop_medio_pct": float(np.mean([abs(t.entrata - t.stop) / t.entrata for t in trades])),
        "stop_oltre_6pct": int(sum(1 for t in trades if abs(t.entrata - t.stop) / t.entrata > 0.06)),
        "durata_media_ore": float(np.mean([(t.ts_uscita - t.ts_entrata) / 3.6e6 for t in trades])),
    }
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    out["blocco"] = blocco

    # baseline (a)
    ris_a = motore.esegui(candele, None, mark, funding, F.crea_a(), param)
    tr_a = [t for t in ris_a.trades if solo_dopo is None or t.ts_entrata > solo_dopo]
    if len(tr_a) >= 2:
        blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in tr_a], [t.ts_uscita for t in tr_a])
        base_a = statistica.baseline_da_trade([t.r for t in tr_a], blocco_a, BOOT_N, BOOT_SEME)
        cmp_a = statistica.contro_baseline(r, blocco, base_a, BOOT_N, BOOT_SEME)
        out["baseline_a"] = dict(_sintesi_confronto(cmp_a), media=base_a["media"], n_trade=base_a["n_trade"],
                                 blocco_a=blocco_a, n_blocchi_a=base_a["n_blocchi"])
    else:
        out["baseline_a"] = {"valutabile": False, "netta": False, "t": -math.inf, "n_trade": len(tr_a)}

    # baseline (b)
    durata = motore.durata_media_barre(trades, D["passo"])
    vietate, quota_vietate = F.barre_vietate(param)
    try:
        base_b = baseline_b(candele, mark, funding, F.crea_casuale, len(trades), durata, param, vietate,
                            processi=processi)
        cmp_b = statistica.contro_baseline(r, blocco, base_b, BOOT_N, BOOT_SEME)
        out["baseline_b"] = dict(
            _sintesi_confronto(cmp_b), media=base_b["media"], n_simulazioni=base_b["n_simulazioni"],
            trade_per_simulazione_medio=float(np.mean(base_b["trade_per_simulazione"])),
            simulazioni_vuote=base_b["simulazioni_vuote"], quota_barre_vietate=quota_vietate,
            segnali_scartati_per_simulazione_medio=float(np.mean(base_b["segnali_non_validi_per_simulazione"])),
            durata_media_barre=durata, percentile_90=base_b["percentile_90"])
        out["percentile_caso"] = statistica.percentile_del_candidato(float(np.mean(r)), base_b["valori"])
        out["_valori_b"] = list(map(float, base_b["valori"]))
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "netta": False, "t": -math.inf, "errore": str(e)}
        out["percentile_caso"] = None
    if extra:
        cand_periodo = [c for c in candele if solo_dopo is None or c.ts > solo_dopo]
        out["buy_and_hold_per_anno"] = buy_and_hold_per_anno(cand_periodo, param)
    a, b = out["baseline_a"], out["baseline_b"]
    out["candidato"] = bool(a.get("netta") and b.get("netta") and out["metriche"]["r_medio"] > 0)
    out["valutabile"] = bool(a.get("valutabile") and b.get("valutabile"))
    out["_trades"] = trades
    return out


def per_log(v: dict) -> dict:
    """Il risultato senza le chiavi interne (trade e valori delle simulazioni)."""
    return {k: val for k, val in v.items() if not k.startswith("_")}
