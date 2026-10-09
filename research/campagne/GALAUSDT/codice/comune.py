"""Strumenti comuni della campagna GALAUSDT: dati, parametri, strategie, baseline, metriche.

Niente regole di strategia qui: le varianti stanno in ``varianti.py``. Questo file
traduce il protocollo (sezioni 7 e 8) in un'unica procedura usata da TUTTE le varianti:

* ``contesto(tf, periodo)``: candele last e mark allineate (``carica_serie_allineate``),
  funding, BTCUSDT allineato sugli stessi ts, maschera dei mesi sotto la liquidita'
  minima (Fase 0 punto 3: si legge sui file 1d del last con ``volume_usdt_da_zip``).
* ``crea_strategia(variante, ctx, modo)``: la strategia del motore. ``modo`` e'
  "variante" (condizione d'ingresso + filtro dei mesi), "a" (baseline (a): ogni barra
  libera, solo filtro dei mesi), oppure un insieme di ingressi (baseline (b)).
* ``valuta_costruzione(variante)``: test, baseline (a) e (b), confronti, metriche.

Le variabili precalcolate degli indicatori sono CAUSALI: il valore all'indice i usa
solo le barre 0..i (rolling di pandas, ewm con adjust=False). La strategia legge solo
l'indice della barra corrente, ``len(storia) - 1``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import yaml

from research.src import dati, motore, statistica
from research.src.motore import Candela, Parametri, Segnale

SIMBOLO = "GALAUSDT"
INIZIO = date(2021, 9, 1)
FINE_IN_SAMPLE = date(2023, 12, 31)
P = dati.periodi_campagna(INIZIO)
FINE_COSTRUZIONE_TS = int(P["fine_costruzione_ts"])
INIZIO_VALIDAZIONE_TS = int(P["inizio_validazione_ts"])
SLIPPAGE = 0.0005  # scheda_moneta.md: fascia 0,05% per lato (volume medio 2023)
RADICE = Path(__file__).resolve().parents[3]  # research/
CARTELLA_DATI = RADICE / "data" / "insample" / SIMBOLO
MS = {tf: dati.durata_intervallo(tf) for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]}


# ---------------------------------------------------------------------------
# Parametri (config/parametri.yaml + scheda)
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _yaml() -> dict:
    return yaml.safe_load((RADICE / "config" / "parametri.yaml").read_text(encoding="utf-8"))


def parametri(moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0,
              intrabarra: str = "stop_prima") -> Parametri:
    y = _yaml()
    regole = y["fatti"]["regole_dimensione_bot"]
    esame = y["regole_esame"]
    return Parametri(
        commissione_per_lato=float(y["fatti"]["commissione_taker_per_lato"]["valore"]),
        slippage_per_lato=SLIPPAGE,
        rischio_per_trade=float(regole["rischio_per_trade"]),
        leva_max=float(regole["leva_max"]),
        modalita_margine=str(regole["modalita_margine_proposta"]),
        tasso_margine_mantenimento=float(regole["tasso_margine_mantenimento"]),
        margine_minimo_da_liquidazione=float(esame["margine_minimo_da_liquidazione"]),
        capitale_iniziale=float(regole["capitale_iniziale"]),
        riempimento_intrabarra=intrabarra,
        moltiplicatore_costi=moltiplicatore_costi,
        ritardo_barre=ritardo_barre,
    )


# ---------------------------------------------------------------------------
# Liquidita' mensile (Fase 0 punto 3)
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def volume_mensile() -> Dict[Tuple[int, int], float]:
    """Volume medio giornaliero in USDT per mese, dai file 1d del last (tutti i giorni)."""
    out: Dict[Tuple[int, int], float] = {}
    for anno, mese in dati.mesi_del_periodo(INIZIO, FINE_IN_SAMPLE):
        perc = dati.percorso_mese(SIMBOLO, "klines", "1d", anno, mese)
        if not perc.is_file():
            continue
        vol = dati.volume_usdt_da_zip(perc)
        if vol:
            out[(anno, mese)] = sum(vol.values()) / len(vol)
    return out


def mesi_esclusi() -> List[Tuple[int, int]]:
    soglia = float(_yaml()["scelte_dati"]["liquidita_minima_usdt_giorno"])
    return sorted(m for m, v in volume_mensile().items() if v < soglia)


def _mese(ts: int) -> Tuple[int, int]:
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return (d.year, d.month)


# ---------------------------------------------------------------------------
# Contesto dei dati di un timeframe
# ---------------------------------------------------------------------------


@dataclass
class Contesto:
    tf: str
    periodo: str  # "costruzione" o "validazione" (= costruzione + validazione, indicatori caldi)
    candele: List[Candela]
    candele_mark: List[Candela]
    funding: List[Tuple[int, float]]
    df: pd.DataFrame  # colonne open high low close volume ts, piu' btc_close (NaN se manca)
    vietata_mese: np.ndarray  # True se la barra di segnale cade in un mese escluso
    info: Dict[str, object] = field(default_factory=dict)

    @property
    def ms(self) -> int:
        return MS[self.tf]


@lru_cache(maxsize=32)
def contesto(tf: str, periodo: str = "costruzione") -> Contesto:
    if periodo not in ("costruzione", "validazione"):
        raise ValueError(periodo)
    s = dati.carica_serie_allineate(SIMBOLO, tf, INIZIO, FINE_IN_SAMPLE)
    candele, mark = s["candele"], s["candele_mark"]
    funding = dati.carica_funding(SIMBOLO, INIZIO, FINE_IN_SAMPLE)
    if periodo == "costruzione":
        tenere = [k for k, c in enumerate(candele) if c.close_ts <= FINE_COSTRUZIONE_TS]
        candele = [candele[k] for k in tenere]
        mark = [mark[k] for k in tenere]
        funding = [(t, r) for t, r in funding if t <= FINE_COSTRUZIONE_TS]
    btc = {c.ts: c.close for c in dati.carica_candele("BTCUSDT", tf, INIZIO, FINE_IN_SAMPLE)}
    df = pd.DataFrame({
        "ts": [c.ts for c in candele],
        "open": [c.open for c in candele],
        "high": [c.high for c in candele],
        "low": [c.low for c in candele],
        "close": [c.close for c in candele],
        "volume": [c.volume for c in candele],
        "quote_volume": [s["volume_usdt"].get(c.ts) if s["volume_usdt"].get(c.ts) is not None else np.nan
                         for c in candele],
        "btc_close": [btc.get(c.ts, np.nan) for c in candele],
    })
    # ultimo tasso di funding gia' regolato alla chiusura di ogni barra (noto a quell'istante)
    f_ts = np.array([t for t, _ in funding], dtype=np.int64)
    f_r = np.array([r for _, r in funding], dtype=float)
    close_ts = np.array([c.close_ts for c in candele], dtype=np.int64)
    pos = np.searchsorted(f_ts, close_ts, side="right") - 1
    df["funding_ultimo"] = np.where(pos >= 0, f_r[np.clip(pos, 0, None)], np.nan) if len(f_r) else np.nan
    dt = pd.to_datetime(df["ts"], unit="ms", utc=True)
    df["ora"] = dt.dt.hour
    df["minuto"] = dt.dt.minute
    df["giorno_settimana"] = dt.dt.dayofweek  # lunedi' = 0
    df["giorno"] = (df["ts"] // 86_400_000).astype(np.int64)
    esclusi = set(mesi_esclusi())
    vietata = np.array([_mese(c.ts) in esclusi for c in candele], dtype=bool)
    info = {"n_tolte_last": s["n_tolte_last"], "n_tolte_mark": s["n_tolte_mark"],
            "tolte_last": s["tolte_last"], "tolte_mark": s["tolte_mark"],
            "n_btc_mancanti": int(df["btc_close"].isna().sum())}
    return Contesto(tf, periodo, candele, mark, funding, df, vietata, info)


# ---------------------------------------------------------------------------
# Indicatori causali
# ---------------------------------------------------------------------------


def atr(df: pd.DataFrame, n: int) -> np.ndarray:
    prev = df["close"].shift(1)
    tr = pd.concat([df["high"] - df["low"], (df["high"] - prev).abs(), (df["low"] - prev).abs()], axis=1).max(axis=1)
    return tr.rolling(n, min_periods=n).mean().to_numpy()


def sma(x: pd.Series, n: int) -> np.ndarray:
    return x.rolling(n, min_periods=n).mean().to_numpy()


def ema(x: pd.Series, n: int) -> np.ndarray:
    v = x.ewm(span=n, adjust=False).mean().to_numpy()
    v[: n - 1] = np.nan  # riscaldamento
    return v


def rolling_max(x: pd.Series, n: int) -> np.ndarray:
    return x.rolling(n, min_periods=n).max().to_numpy()


def rolling_min(x: pd.Series, n: int) -> np.ndarray:
    return x.rolling(n, min_periods=n).min().to_numpy()


def rolling_std(x: pd.Series, n: int) -> np.ndarray:
    return x.rolling(n, min_periods=n).std(ddof=0).to_numpy()


def rsi(close: pd.Series, n: int) -> np.ndarray:
    d = close.diff()
    su = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    giu = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = su / giu.replace(0, np.nan)
    v = (100 - 100 / (1 + rs)).to_numpy()
    v[np.isnan(v) & (giu.to_numpy() == 0)] = 100.0
    v[:n] = np.nan
    return v


def valido(*valori) -> bool:
    for v in valori:
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return False
        if isinstance(v, (np.floating,)) and np.isnan(v):
            return False
    return True


# ---------------------------------------------------------------------------
# La variante: interfaccia
# ---------------------------------------------------------------------------


class Variante:
    """Una regola completa (regola 6). Le sottoclassi definiscono:

    * ``prepara(df)``: dizionario di array causali;
    * ``segnale(a, i, df)``: il Segnale (direzione, stop, target) che la variante emette
      alla chiusura della barra i SENZA la condizione d'ingresso, o None se non calcolabile;
    * ``condizione(a, i, df)``: la condizione d'ingresso dell'ipotesi (con i suoi filtri);
    * ``esci(a, i, df, barre_tenute, pos)``: True per chiudere all'apertura della barra dopo.
    """

    id: str = ""
    tf: str = "1h"
    direzione: str = "long"
    parametri_numerici: Dict[str, float] = {}

    def __init__(self, **kw):
        self.p = dict(self.parametri_numerici)
        self.p.update(kw)

    def prepara(self, df: pd.DataFrame) -> Dict[str, np.ndarray]:
        raise NotImplementedError

    def segnale(self, a, i, df) -> Optional[Segnale]:
        raise NotImplementedError

    def condizione(self, a, i, df) -> bool:
        raise NotImplementedError

    def esci(self, a, i, df, barre_tenute: int, pos) -> bool:
        return False

    def con_timeframe(self, tf: str) -> "Variante":
        """Copia su un altro timeframe (verifica dei timeframe adiacenti): i parametri in barre
        (chiavi che finiscono con '_barre') si convertono per tenere la stessa durata."""
        nuova = self.__class__(**self.p)
        nuova.id, nuova.direzione = self.id, self.direzione
        rapporto = MS[self.tf] / MS[tf]
        for k, v in self.p.items():
            if k.endswith("_barre"):
                nuova.p[k] = max(1, int(math.floor(v * rapporto + 0.5)))
        nuova.tf = tf
        return nuova


# --- stop e target comuni -------------------------------------------------


def segnale_atr(direzione: str, close: float, atr_v: float, k_stop: float, k_target: Optional[float]) -> Optional[Segnale]:
    """Stop a k_stop ATR dal close della barra di segnale; target a k_target volte la distanza dello stop."""
    if not valido(close, atr_v) or atr_v <= 0:
        return None
    d = k_stop * atr_v
    if direzione == "long":
        stop = close - d
        target = close + k_target * d if k_target else None
        if stop <= 0:
            return None
    else:
        stop = close + d
        target = close - k_target * d if k_target else None
        if target is not None and target <= 0:
            return None
    return Segnale(direzione, stop, target)


# ---------------------------------------------------------------------------
# Strategie per il motore
# ---------------------------------------------------------------------------


def crea_fabbrica(var: Variante, ctx: Contesto, modo, candele: Optional[List[Candela]] = None):
    """Restituisce la funzione SENZA argomenti che crea una strategia nuova (sezione 7)."""
    df = ctx.df if candele is None else ctx.df.iloc[: len(candele)].reset_index(drop=True)
    a = var.prepara(df)
    vietata = ctx.vietata_mese
    ms = ctx.ms

    def crea():
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is not None:
                tenute = int((storia[i].ts - pos.ts_entrata) // ms) + 1
                return "chiudi" if var.esci(a, i, df, tenute, pos) else None
            if modo == "variante":
                if vietata[i] or not var.condizione(a, i, df):
                    return None
            elif modo == "a":
                if vietata[i]:
                    return None
            else:  # insieme di ingressi della (b)
                if i not in modo:
                    return None
            return var.segnale(a, i, df)
        return strategia
    return crea


def crea_casuale_fabbrica(var: Variante, ctx: Contesto):
    df = ctx.df
    a = var.prepara(df)
    ms = ctx.ms

    def crea_casuale(ingressi):
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is not None:
                tenute = int((storia[i].ts - pos.ts_entrata) // ms) + 1
                return "chiudi" if var.esci(a, i, df, tenute, pos) else None
            if i in ingressi:
                return var.segnale(a, i, df)
            return None
        return strategia
    return crea_casuale


def crea_segnale_fabbrica(var: Variante, ctx: Contesto):
    df = ctx.df
    a = var.prepara(df)

    def crea_segnale():
        def segnale_alla_barra(storia):
            return var.segnale(a, len(storia) - 1, df)
        return segnale_alla_barra
    return crea_segnale


def intervalli_da_maschera(maschera: np.ndarray) -> List[Tuple[int, int]]:
    out: List[Tuple[int, int]] = []
    i, n = 0, len(maschera)
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


# ---------------------------------------------------------------------------
# Conteggio dei trade (sezione 8)
# ---------------------------------------------------------------------------


def conta(var: Variante, moltiplicatore_costi: float = 1.0) -> Dict[str, int]:
    ctx = contesto(var.tf, "costruzione")
    return motore.conta_trade(ctx.candele, crea_fabbrica(var, ctx, "variante"), FINE_COSTRUZIONE_TS,
                              parametri(moltiplicatore_costi), None, ctx.candele_mark, ctx.funding)


# ---------------------------------------------------------------------------
# Metriche, baseline e confronti
# ---------------------------------------------------------------------------


def _anno(ts: int) -> int:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year


def metriche_trade(trades: Sequence[motore.Trade], risultato: Optional[motore.Risultato] = None) -> Dict[str, object]:
    ordinati = sorted(trades, key=lambda t: t.ts_uscita)
    r = [t.r for t in ordinati]
    out: Dict[str, object] = {"trade": len(r)}
    if not r:
        return out
    vinti = sum(t.pnl for t in ordinati if t.pnl > 0)
    persi = -sum(t.pnl for t in ordinati if t.pnl < 0)
    out["profit_factor"] = vinti / persi if persi > 0 else (math.inf if vinti > 0 else 0.0)
    out["r_medio"] = float(np.mean(r))
    per_anno: Dict[str, List[float]] = {}
    for t in ordinati:
        per_anno.setdefault(str(_anno(t.ts_uscita)), []).append(t.r)
    out["r_medio_per_anno"] = {k: float(np.mean(v)) for k, v in per_anno.items()}
    out["trade_per_anno"] = {k: len(v) for k, v in per_anno.items()}
    out["r_medio_senza_3_migliori"] = float(np.mean(sorted(r)[:-3])) if len(r) > 3 else float("nan")
    out["win_rate"] = float(np.mean([t.pnl > 0 for t in ordinati]))
    out["pnl_pct_totale"] = float(sum(t.pnl_pct for t in ordinati))
    out["n_ridotti"] = sum(1 for t in ordinati if t.ridotto)
    out["n_violazioni_liquidazione"] = sum(1 for t in ordinati if t.violazione_liquidazione)
    out["esiti"] = {e: sum(1 for t in ordinati if t.esito == e)
                    for e in ("stop", "target", "segnale", "liquidazione", "fine_dati")}
    out["stop_pct_medio"] = float(np.mean([abs(t.entrata - t.stop) / t.entrata for t in ordinati]))
    out["stop_oltre_6pct"] = sum(1 for t in ordinati if abs(t.entrata - t.stop) / t.entrata > 0.06)
    if risultato is not None:
        curva = []
        cap = risultato.capitale_iniziale
        curva.append((0, cap))
        for t in ordinati:
            cap += t.pnl
            curva.append((t.ts_uscita, cap))
        out["drawdown_max"] = motore.drawdown_massimo(curva)
        out["rendimento_totale"] = (cap - risultato.capitale_iniziale) / risultato.capitale_iniziale
        out["n_buchi_dati"] = risultato.n_buchi_dati
        out["n_segnali_non_validi"] = risultato.n_segnali_non_validi
    return out


def buy_and_hold_per_anno(ctx: Contesto, prm: Parametri, da_ts: int = 0) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    per_anno: Dict[int, List[Candela]] = {}
    for c in ctx.candele:
        if c.ts >= da_ts:
            per_anno.setdefault(_anno(c.ts), []).append(c)
    for anno, cc in sorted(per_anno.items()):
        out[str(anno)] = {"long": motore.buy_and_hold(cc, prm, "long"), "short": motore.buy_and_hold(cc, prm, "short")}
    return out


def _riassunto_confronto(c: Dict[str, object]) -> Dict[str, object]:
    chiavi = ("t", "soglia", "netta", "valutabile", "differenza", "errore_standard", "errore_candidato",
              "errore_minimo", "n_blocchi", "p_value", "baseline_media", "baseline_errore_standard")
    return {k: c.get(k) for k in chiavi}


def valuta(var: Variante, periodo: str = "costruzione", moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0,
           intrabarra: str = "stop_prima", con_a: bool = True) -> Dict[str, object]:
    """Il test di una variante con le baseline (a) e (b) della sezione 8, sul periodo dato.

    In "validazione" la serie va dall'inizio della costruzione alla fine della validazione
    (indicatori caldi) e contano solo i trade ENTRATI dal primo istante di validazione; la (b)
    ha vietate anche tutte le barre di costruzione; la (a) conta solo i suoi trade di validazione.
    """
    ctx = contesto(var.tf, periodo)
    prm = parametri(moltiplicatore_costi, ritardo_barre, intrabarra)
    da_ts = INIZIO_VALIDAZIONE_TS if periodo == "validazione" else 0

    ris = motore.esegui(ctx.candele, None, ctx.candele_mark, ctx.funding,
                        crea_fabbrica(var, ctx, "variante")(), prm)
    trades = sorted([t for t in ris.trades if t.ts_entrata >= da_ts], key=lambda t: t.ts_uscita)
    out: Dict[str, object] = {"metriche": metriche_trade(trades, ris)}
    n = len(trades)
    if n == 0:
        out["valutabile"] = False
        return out
    r = [t.r for t in trades]
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    out["blocco"] = blocco

    # baseline (a)
    if con_a:
        ris_a = motore.esegui(ctx.candele, None, ctx.candele_mark, ctx.funding,
                              crea_fabbrica(var, ctx, "a")(), prm)
        ta = sorted([t for t in ris_a.trades if t.ts_entrata >= da_ts], key=lambda t: t.ts_uscita)
        if len(ta) >= 2:
            blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in ta], [t.ts_uscita for t in ta])
            base_a = statistica.baseline_da_trade([t.r for t in ta], blocco_a)
            ca = statistica.contro_baseline(r, blocco, base_a)
            out["baseline_a"] = dict(_riassunto_confronto(ca), media=base_a["media"], n_trade=base_a["n_trade"],
                                     blocco_a=blocco_a, n_blocchi_a=base_a["n_blocchi"])
        else:
            out["baseline_a"] = {"valutabile": False, "netta": False, "t": -math.inf, "n_trade": len(ta)}

    # baseline (b)
    durata = motore.durata_media_barre(trades, ctx.ms)
    vietate_segnale = motore.barre_vietate_segnale_non_valido(ctx.candele, crea_segnale_fabbrica(var, ctx), prm)
    mask = ctx.vietata_mese.copy()
    for lo, hi in vietate_segnale:
        mask[lo:hi] = True
    if periodo == "validazione":
        mask |= np.array([c.ts < da_ts for c in ctx.candele])
    vietate = intervalli_da_maschera(mask)
    quota_vietate_segnale = float(sum(hi - lo for lo, hi in vietate_segnale) / len(ctx.candele))
    try:
        base_b = motore.simula_baseline_casuale(
            ctx.candele, crea_casuale_fabbrica(var, ctx), n, durata, prm, None, ctx.candele_mark, ctx.funding,
            vietate, n_simulazioni=200, primo_seme=0)
        # in validazione le simulazioni entrano solo in validazione: i loro trade sono tutti di validazione
        cb = statistica.contro_baseline(r, blocco, base_b)
        out["baseline_b"] = dict(
            _riassunto_confronto(cb), media=base_b["media"], n_simulazioni=base_b["n_simulazioni"],
            trade_per_simulazione_medio=float(np.mean(base_b["trade_per_simulazione"])),
            simulazioni_vuote=base_b["simulazioni_vuote"],
            segnali_non_validi_per_simulazione_medio=float(np.mean(base_b["segnali_non_validi_per_simulazione"])),
            quota_barre_vietate_segnale_non_valido=quota_vietate_segnale, durata_media_barre=durata)
        out["percentile_caso"] = statistica.percentile_del_candidato(float(np.mean(r)), base_b["valori"])
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "netta": False, "t": -math.inf, "errore": str(e)}
    out["buy_and_hold_per_anno"] = buy_and_hold_per_anno(ctx, prm, da_ts)
    ba, bb = out.get("baseline_a", {}), out["baseline_b"]
    out["valutabile"] = bool(ba.get("valutabile", True) and bb.get("valutabile"))
    out["batte_a_e_b"] = bool(ba.get("netta") and bb.get("netta"))
    out["candidato"] = bool(out["batte_a_e_b"] and out["metriche"]["r_medio"] > 0)
    out["trades_r"] = [round(x, 4) for x in r]
    return out
