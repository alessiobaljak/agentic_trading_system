"""Quadro comune della campagna DOGEUSDT: dati, parametri, varianti, test e baseline.

Una variante e' un oggetto con:
* ``tf`` (timeframe), ``direzione`` ("long" o "short");
* ``prepara(d)``: calcola gli indicatori (CAUSALI: il valore alla barra i usa solo barre <= i)
  sugli array della serie intera ``d`` (costruzione e validazione insieme, cosi' in
  validazione gli indicatori sono gia' caldi); imposta ``primo_indice`` (prima barra in cui
  la variante puo' entrare: riscaldamento degli indicatori dell'ingresso e dei livelli);
* ``livelli(i)``: (stop, target) calcolati alla chiusura della barra i, oppure None se non
  si possono calcolare. E' il «segnale senza la condizione d'ingresso» della sezione 8;
* ``condizione(i)``: la condizione d'ingresso dell'ipotesi (con i suoi filtri);
* ``esci(i, barre_tenute)``: True se alla chiusura della barra i la posizione va chiusa
  (uscita a tempo o su segnale; l'uscita e' la stessa per variante, (a) e (b)).

Il filtro di liquidita' della Fase 0 (mesi sotto 20 milioni di USDT al giorno) e' uguale per
``conta_trade``, il test e la (a): nessun ingresso su segnali di barre di quei mesi; le stesse
barre vanno fra le vietate della (b).

Ogni esecuzione del motore crea un'istanza nuova della strategia (sezione 7): le fabbriche
qui sotto restituiscono funzioni nuove a ogni chiamata, e lo stato di una strategia sta solo
nella posizione che il motore le passa.
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import replace
from datetime import date, datetime, timezone
from functools import lru_cache
from pathlib import Path

import numpy as np

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))

from research.src import dati, motore, statistica  # noqa: E402
from research.src.motore import Parametri, Segnale  # noqa: E402

SIMBOLO = "DOGEUSDT"
INIZIO = date(2020, 7, 1)
FINE = date(2023, 12, 31)
PERIODI = dati.periodi_campagna(INIZIO)
FINE_COSTR_TS = PERIODI["fine_costruzione_ts"]
INIZIO_VALID_TS = PERIODI["inizio_validazione_ts"]
SOGLIA_LIQUIDITA = 20_000_000
TRADE_MINIMI_COSTRUZIONE = 70
TRADE_MINIMI_VALIDAZIONE = 30

#: config/parametri.yaml (congelato) e fascia di slippage della scheda (0,02% per lato)
PARAMETRI = Parametri(
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
STOP_MASSIMO_BOT = 0.06
TF_MS = {tf: dati.durata_intervallo(tf) for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]}


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------


@lru_cache(maxsize=None)
def mesi_illiquidi() -> frozenset:
    """Mesi (anno, mese) con volume medio giornaliero in USDT sotto la soglia (candele 1d del last)."""
    per_mese = {}
    for anno, mese in dati.mesi_del_periodo(INIZIO, FINE):
        p = dati.percorso_mese(SIMBOLO, "klines", "1d", anno, mese, dati.RADICE_DEFAULT)
        if not p.is_file():
            continue
        vol = dati.volume_usdt_da_zip(p)
        if vol:
            per_mese[(anno, mese)] = sum(vol.values()) / len(vol)
    return frozenset(k for k, v in per_mese.items() if v < SOGLIA_LIQUIDITA)


def _anno_mese(ts: int):
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return d.year, d.month


@lru_cache(maxsize=None)
def serie(tf: str) -> dict:
    """Serie allineate last/mark di DOGEUSDT sul timeframe, intere (costruzione + validazione), e gli array."""
    s = dati.carica_serie_allineate(SIMBOLO, tf, INIZIO, FINE)
    c = s["candele"]
    illiq = mesi_illiquidi()
    d = {
        "tf": tf,
        "candele": c,
        "mark": s["candele_mark"],
        "ts": np.array([x.ts for x in c], dtype=np.int64),
        "open": np.array([x.open for x in c]),
        "high": np.array([x.high for x in c]),
        "low": np.array([x.low for x in c]),
        "close": np.array([x.close for x in c]),
        "volume": np.array([x.volume for x in c]),
        "vol_usdt": np.array([s["volume_usdt"].get(x.ts) or np.nan for x in c]),
        "illiquida": np.array([_anno_mese(x.ts) in illiq for x in c]),
        "n_costr": int(sum(1 for x in c if x.close_ts <= FINE_COSTR_TS)),
        "n_tolte_last": s["n_tolte_last"],
        "n_tolte_mark": s["n_tolte_mark"],
    }
    return d


@lru_cache(maxsize=None)
def funding() -> list:
    return dati.carica_funding(SIMBOLO, INIZIO, FINE)


@lru_cache(maxsize=None)
def btc(tf: str) -> dict:
    c = dati.carica_candele("BTCUSDT", tf, INIZIO, FINE)
    return {x.ts: x for x in c}


# ---------------------------------------------------------------------------
# Indicatori causali (il valore in i usa solo barre <= i)
# ---------------------------------------------------------------------------


def atr(d, n):
    h, l, c = d["high"], d["low"], d["close"]
    pc = np.concatenate([[np.nan], c[:-1]])
    tr = np.nanmax(np.vstack([h - l, np.abs(h - pc), np.abs(l - pc)]), axis=0)
    out = np.full(len(c), np.nan)
    if len(c) < n:
        return out
    out[n - 1] = tr[:n].mean()
    for i in range(n, len(c)):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n  # media di Wilder
    return out


def sma(x, n):
    out = np.full(len(x), np.nan)
    cs = np.cumsum(np.insert(x, 0, 0.0))
    out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def ema(x, n):
    out = np.full(len(x), np.nan)
    a = 2.0 / (n + 1)
    if len(x) < n:
        return out
    out[n - 1] = x[:n].mean()
    for i in range(n, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def rolling_max(x, n):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = x[i - n + 1:i + 1].max()
    return out


def rolling_min(x, n):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = x[i - n + 1:i + 1].min()
    return out


def rolling_std(x, n):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = x[i - n + 1:i + 1].std(ddof=1)
    return out


def rsi(c, n):
    """RSI di Wilder."""
    delta = np.diff(c, prepend=np.nan)
    up = np.where(delta > 0, delta, 0.0)
    dn = np.where(delta < 0, -delta, 0.0)
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    au, ad = up[1:n + 1].mean(), dn[1:n + 1].mean()
    out[n] = 100.0 if ad == 0 else 100 - 100 / (1 + au / ad)
    for i in range(n + 1, len(c)):
        au = (au * (n - 1) + up[i]) / n
        ad = (ad * (n - 1) + dn[i]) / n
        out[i] = 100.0 if ad == 0 else 100 - 100 / (1 + au / ad)
    return out


def primo_finito(*arrays):
    """Primo indice in cui tutti gli array sono finiti (fine del riscaldamento)."""
    ok = np.ones(len(arrays[0]), dtype=bool)
    for a in arrays:
        ok &= np.isfinite(a)
    idx = np.flatnonzero(ok)
    return int(idx[0]) if idx.size else len(arrays[0])


# ---------------------------------------------------------------------------
# Strategie per il motore
# ---------------------------------------------------------------------------


class Base:
    """Base delle varianti: uscita a tempo dopo ``barre`` barre (se impostata) e livelli in ATR."""

    tf = "1h"
    direzione = "long"
    barre = None  # uscita a tempo (barre tenute), None = nessuna
    stop_atr = None
    target_atr = None
    n_atr = 14

    def prepara(self, d):
        self.d = d
        self.ms = TF_MS[self.tf]
        self.c = d["close"]
        self.a = atr(d, self.n_atr)
        self.primo_indice = self.riscaldamento()

    def riscaldamento(self):
        return primo_finito(self.a)

    def livelli(self, i):
        a = self.a[i]
        if not np.isfinite(a) or a <= 0:
            return None
        c = self.c[i]
        s = 1 if self.direzione == "long" else -1
        stop = c - s * self.stop_atr * a
        target = None if self.target_atr is None else c + s * self.target_atr * a
        if stop <= 0 or (target is not None and target <= 0):
            return None
        return stop, target

    def condizione(self, i):
        raise NotImplementedError

    def esci(self, i, barre_tenute):
        return self.barre is not None and barre_tenute >= self.barre


def _fabbrica(v, modo, ingressi=frozenset(), da_indice=0):
    """Crea la strategia: modo 'variante', 'a' (senza condizione d'ingresso) o 'casuale'."""
    d = v.d
    ts = d["ts"]
    illiq = d["illiquida"]
    ms = v.ms

    def strategia(storia, pos):
        i = len(storia) - 1
        if pos is not None:
            tenute = (int(ts[i]) - pos.ts_entrata) // ms + 1
            return "chiudi" if v.esci(i, tenute) else None
        if modo == "casuale":
            if i not in ingressi:
                return None
        else:
            if i < da_indice or illiq[i]:
                return None
            if modo == "variante" and not v.condizione(i):
                return None
        lv = v.livelli(i)
        if lv is None:
            return None
        return Segnale(v.direzione, lv[0], lv[1])

    return strategia


def crea_variante(v):
    return lambda: _fabbrica(v, "variante", da_indice=v.primo_indice)


def crea_a(v):
    return lambda: _fabbrica(v, "a", da_indice=v.primo_indice)


def crea_casuale(v):
    return lambda ingressi: _fabbrica(v, "casuale", ingressi=ingressi)


def crea_segnale(v):
    def f():
        def segnale(storia):
            i = len(storia) - 1
            lv = v.livelli(i)
            return None if lv is None else Segnale(v.direzione, lv[0], lv[1])
        return segnale
    return f


# ---------------------------------------------------------------------------
# Esecuzioni
# ---------------------------------------------------------------------------


def _tagli(d, periodo):
    if periodo == "costruzione":
        n = d["n_costr"]
        return d["candele"][:n], d["mark"][:n], [(t, r) for t, r in funding() if t <= FINE_COSTR_TS]
    return d["candele"], d["mark"], list(funding())


def conta(v):
    d = serie(v.tf)
    v.prepara(d)
    cand, mark, fund = _tagli(d, "costruzione")
    return motore.conta_trade(cand, crea_variante(v), FINE_COSTR_TS, PARAMETRI, candele_mark=mark, funding=fund)


def _intervalli_da_maschera(maschera):
    out = []
    i = 0
    n = len(maschera)
    while i < n:
        if maschera[i]:
            j = i
            while j < n and maschera[j]:
                j += 1
            out.append((i, j))
            i = j
        else:
            i += 1
    return out


def anno(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year


def metriche_trade(trades, capitale_iniziale=1000.0):
    tr = sorted(trades, key=lambda t: t.ts_uscita)
    r = [t.r for t in tr]
    n = len(r)
    vinti = sum(t.pnl for t in tr if t.pnl > 0)
    persi = -sum(t.pnl for t in tr if t.pnl < 0)
    pf = vinti / persi if persi > 0 else (math.inf if vinti > 0 else 0.0)
    per_anno = {}
    for t in tr:
        per_anno.setdefault(anno(t.ts_uscita), []).append(t.r)
    curva = [(tr[0].ts_entrata if tr else 0, capitale_iniziale)]
    cap = capitale_iniziale
    for t in tr:
        cap += t.pnl
        curva.append((t.ts_uscita, cap))
    senza3 = sorted(r)[:-3] if n > 3 else []
    return {
        "trade": n,
        "profit_factor": pf,
        "r_medio": float(np.mean(r)) if n else 0.0,
        "r_mediano": float(np.median(r)) if n else 0.0,
        "win_rate": sum(1 for x in r if x > 0) / n if n else 0.0,
        "r_medio_per_anno": {a: float(np.mean(v)) for a, v in sorted(per_anno.items())},
        "trade_per_anno": {a: len(v) for a, v in sorted(per_anno.items())},
        "r_medio_senza_3_migliori": float(np.mean(senza3)) if senza3 else None,
        "drawdown_max": -motore.drawdown_massimo(curva),
        "rendimento_totale": (cap - capitale_iniziale) / capitale_iniziale,
        "rendimento_per_anno": motore.rendimento_per_anno(tr, capitale_iniziale),
        "trade_ridotti_tetto_leva": sum(1 for t in tr if t.ridotto),
        "violazioni_liquidazione": sum(1 for t in tr if t.violazione_liquidazione),
        "stop_oltre_6_per_cento": sum(1 for t in tr if abs(t.entrata - t.stop) / t.entrata > STOP_MASSIMO_BOT),
        "esiti": {e: sum(1 for t in tr if t.esito == e) for e in ("stop", "target", "segnale", "liquidazione", "fine_dati")},
        "funding_totale_in_r": float(sum(t.funding_pagato / t.rischio_iniziale for t in tr)) if n else 0.0,
        "costi_medi_in_r": float(np.mean([(t.commissioni + t.slippage_costo + t.funding_pagato) / t.rischio_iniziale for t in tr])) if n else 0.0,
    }


def buy_and_hold_per_anno(d, n_fine, parametri):
    out = {}
    cand = d["candele"][:n_fine]
    anni = sorted({anno(c.ts) for c in cand})
    for a in anni:
        pezzo = [c for c in cand if anno(c.ts) == a]
        out[a] = {"long": motore.buy_and_hold(pezzo, parametri, "long"),
                  "short": motore.buy_and_hold(pezzo, parametri, "short")}
    return out


def btc_durante(trades, direzione, tf):
    """Contesto per «e' solo il mercato»: rendimento di BTC (nella direzione) durante i trade."""
    b = btc(tf)
    s = 1 if direzione == "long" else -1
    vals = []
    for t in trades:
        e = b.get(t.ts_entrata)
        dentro = b.get(t.ts_uscita - TF_MS[tf] + 1)  # uscita dentro la barra: ts_uscita = chiusura
        all_apertura = b.get(t.ts_uscita)            # uscita all'apertura: ts_uscita = apertura
        if e is None or (dentro is None and all_apertura is None):
            continue
        fine = dentro.close if dentro is not None else all_apertura.open
        vals.append(s * (fine / e.open - 1))
    return {"n": len(vals), "medio": float(np.mean(vals)) if vals else None,
            "quota_a_favore": float(np.mean([x > 0 for x in vals])) if vals else None}


def valuta(v, periodo="costruzione", parametri=PARAMETRI, n_sim=200):
    """Test completo di una variante: candidato, (a), (b), metriche. Ritorna (dizionario, trades)."""
    d = serie(v.tf)
    v.prepara(d)
    cand, mark, fund = _tagli(d, periodo)
    ris = motore.esegui(cand, None, mark, fund, crea_variante(v)(), parametri)
    if periodo == "costruzione":
        trades = ris.trades
    else:
        trades = [t for t in ris.trades if t.ts_entrata > FINE_COSTR_TS]
    trades = sorted(trades, key=lambda t: t.ts_uscita)
    out = {"metriche": metriche_trade(trades, parametri.capitale_iniziale)}
    out["metriche"]["segnali_non_validi"] = ris.n_segnali_non_validi
    out["metriche"]["buchi_dati"] = ris.n_buchi_dati
    out["metriche"]["funding_in_buco"] = ris.n_funding_in_buco
    if len(trades) < 2:
        return out, trades
    r = [t.r for t in trades]
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    out["blocco"] = blocco

    # baseline (a): senza condizione d'ingresso e senza filtri, dalla prima barra in cui la variante puo' entrare
    ris_a = motore.esegui(cand, None, mark, fund, crea_a(v)(), parametri)
    ta = sorted(ris_a.trades, key=lambda t: t.ts_uscita)
    if periodo != "costruzione":
        ta = [t for t in ta if t.ts_entrata > FINE_COSTR_TS]
    if len(ta) >= 2:
        blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in ta], [t.ts_uscita for t in ta])
        base_a = statistica.baseline_da_trade([t.r for t in ta], blocco_a)
        cmp_a = statistica.contro_baseline(r, blocco, base_a)
        out["baseline_a"] = {"media": base_a["media"], "errore_standard": base_a["errore_standard"],
                             "n_trade": base_a["n_trade"], "blocco_a": blocco_a, "n_blocchi_a": base_a["n_blocchi"],
                             **{k: cmp_a[k] for k in ("t", "soglia", "netta", "valutabile", "differenza",
                                                      "errore_candidato", "errore_minimo", "n_blocchi", "p_value")}}
    else:
        out["baseline_a"] = {"valutabile": False, "netta": False, "t": -math.inf, "n_trade": len(ta)}

    # baseline (b): entrate casuali con la stessa uscita
    n = len(cand)
    vietate = motore.barre_vietate_segnale_non_valido(cand, crea_segnale(v), parametri)
    vietate += _intervalli_da_maschera(d["illiquida"][:n])
    vietate.append((0, v.primo_indice))
    if periodo != "costruzione":
        vietate.append((0, d["n_costr"]))
    maschera = np.zeros(n, dtype=bool)
    for lo, hi in vietate:
        maschera[max(0, lo):min(n, hi)] = True
    durata = motore.durata_media_barre(trades, TF_MS[v.tf])
    try:
        base_b = motore.simula_baseline_casuale(cand, crea_casuale(v), len(trades), durata, parametri,
                                                candele_mark=mark, funding=fund, barre_vietate=vietate,
                                                n_simulazioni=n_sim)
        cmp_b = statistica.contro_baseline(r, blocco, base_b)
        out["baseline_b"] = {"media": base_b["media"], "errore_standard": base_b["errore_standard"],
                             "n_simulazioni": base_b["n_simulazioni"],
                             "trade_per_simulazione_medio": float(np.mean(base_b["trade_per_simulazione"])),
                             "simulazioni_vuote": base_b["simulazioni_vuote"],
                             "segnali_scartati_per_simulazione_medio": float(np.mean(base_b["segnali_non_validi_per_simulazione"])),
                             "quota_barre_vietate": float(maschera.mean()),
                             "durata_media_barre": durata,
                             **{k: cmp_b[k] for k in ("t", "soglia", "netta", "valutabile", "differenza",
                                                      "errore_candidato", "errore_minimo", "n_blocchi", "p_value")}}
        out["percentile_caso"] = statistica.percentile_del_candidato(float(np.mean(r)), base_b["valori"])
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "netta": False, "t": -math.inf, "errore": str(e)}
    n_fine = n if periodo == "costruzione" else len(d["candele"])
    out["buy_and_hold_per_anno"] = buy_and_hold_per_anno(d, n_fine, parametri) if periodo == "costruzione" else None
    out["btc_durante_i_trade"] = btc_durante(trades, v.direzione, v.tf)
    a_ok = out["baseline_a"].get("valutabile", False)
    b_ok = out["baseline_b"].get("valutabile", False)
    out["valutabile"] = bool(a_ok and b_ok)
    out["candidato"] = bool(out["valutabile"] and out["baseline_a"]["netta"] and out["baseline_b"]["netta"]
                            and out["metriche"]["r_medio"] > 0)
    return out, trades
