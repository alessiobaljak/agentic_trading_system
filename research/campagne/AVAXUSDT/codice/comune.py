"""Codice comune della campagna AVAXUSDT: dati, parametri, fabbriche delle strategie, Fase 2.

Niente strategie qui: solo l'impianto che ogni variante usa allo stesso modo.

Scelte scritte prima del primo test
-----------------------------------
* Dati: ``dati.carica_serie_allineate`` sul timeframe della variante (file nativi), funding
  da ``dati.carica_funding``. Serie dello stop = last (``candele_stop=None``), mark per la
  liquidazione.
* Mesi sotto la liquidita' minima (Fase 0 punto 3): la variante non apre posizioni su
  segnali di barre di quei mesi; lo stesso filtro vale per ``conta_trade``, per il test e
  per la baseline (a); le stesse barre vanno in ``barre_vietate`` della (b).
* Indicatori: ogni variante li calcola UNA volta per serie in array numpy CAUSALI (il
  valore alla barra i usa solo le barre 0..i). La funzione ``verifica_causalita`` li
  ricalcola su serie troncate e controlla che coincidano: una differenza vuol dire che un
  valore usa il futuro. Gli array sono di sola lettura: nessuno stato passa da
  un'esecuzione all'altra, e ogni esecuzione crea comunque una strategia nuova.
* Riscaldamento: la variante non da' segnale (``segnale`` = None) finche' TUTTI i suoi
  indicatori, compresi quelli della condizione d'ingresso, non sono calcolabili. Cosi'
  (a) e (b) partono dalla prima barra in cui la variante puo' entrare.
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import sys
from dataclasses import dataclass, field
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

SIMBOLO = "AVAXUSDT"
CARTELLA = Path(__file__).resolve().parents[1]
CARTELLA_DATI = RADICE_REPO / "research" / "data" / "insample" / SIMBOLO
PRIMO_GIORNO = date(2020, 9, 1)
PER = dati.periodi_campagna(PRIMO_GIORNO)
FINE_IN_SAMPLE = date(2023, 12, 31)

_YAML = yaml.safe_load((RADICE_REPO / "research" / "config" / "parametri.yaml").read_text(encoding="utf-8"))
_F = _YAML["fatti"]["regole_dimensione_bot"]
_E = _YAML["regole_esame"]

SLIPPAGE_SCHEDA = 0.0002  # campagne/AVAXUSDT/scheda_moneta.md: 0,0200% per lato

PARAMETRI = Parametri(
    commissione_per_lato=float(_YAML["fatti"]["commissione_taker_per_lato"]["valore"]),
    slippage_per_lato=SLIPPAGE_SCHEDA,
    rischio_per_trade=float(_F["rischio_per_trade"]),
    leva_max=float(_F["leva_max"]),
    modalita_margine=str(_F["modalita_margine_proposta"]),
    tasso_margine_mantenimento=float(_F["tasso_margine_mantenimento"]),
    margine_minimo_da_liquidazione=float(_E["margine_minimo_da_liquidazione"]),
    capitale_iniziale=float(_F["capitale_iniziale"]),
    riempimento_intrabarra=str(_E["riempimento_intrabarra"]),
)
N_SIM = int(_E["simulazioni_baseline_casuale"])
N_BOOT = int(_E["bootstrap"]["ricampionamenti"])
SEME_BOOT = int(_E["bootstrap"]["seme"])
TRADE_MIN = _E["trade_minimi"]
LIQUIDITA_MINIMA = float(_YAML["scelte_dati"]["liquidita_minima_usdt_giorno"])
STOP_MASSIMO_BOT = float(_F["stop_massimo_bot"])

MS = {tf: dati.durata_intervallo(tf) for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]}


# ---------------------------------------------------------------------------
# Liquidita' (Fase 0 punto 3)
# ---------------------------------------------------------------------------

def volume_giornaliero_usdt() -> Dict[int, float]:
    """{ts del giorno: quote_volume} dai file 1d del last, su tutti i giorni (Fase 0 punto 3)."""
    vol: Dict[int, float] = {}
    for p in sorted((CARTELLA_DATI / "klines" / "1d").glob("*.zip")):
        for ts, v in dati.volume_usdt_da_zip(p).items():
            vol.setdefault(ts, v)
    return vol


def mesi_illiquidi() -> List[Tuple[int, int]]:
    """Mesi con volume medio giornaliero in USDT sotto la soglia (sulle candele 1d del last)."""
    per_mese: Dict[Tuple[int, int], List[float]] = {}
    for ts, v in volume_giornaliero_usdt().items():
        d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        if d.date() > FINE_IN_SAMPLE or d.date() < PRIMO_GIORNO:
            continue
        per_mese.setdefault((d.year, d.month), []).append(v)
    return sorted(m for m, vs in per_mese.items() if sum(vs) / len(vs) < LIQUIDITA_MINIMA)


_MESI_ILLIQUIDI: Optional[set] = None


def _illiquidi() -> set:
    global _MESI_ILLIQUIDI
    if _MESI_ILLIQUIDI is None:
        _MESI_ILLIQUIDI = set(mesi_illiquidi())
    return _MESI_ILLIQUIDI


# ---------------------------------------------------------------------------
# Contesto: una serie caricata (timeframe, periodo) con i suoi riferimenti
# ---------------------------------------------------------------------------

@dataclass
class Contesto:
    tf: str
    periodo: str
    candele: List[Candela]
    mark: List[Candela]
    funding: List[Tuple[int, float]]
    btc: Optional[List[Optional[Candela]]]  # BTCUSDT last allineato per ts (None dove manca)
    illiquido: np.ndarray
    ms: int
    ts: np.ndarray
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray
    v: np.ndarray
    indice_ts: Dict[int, int]
    cache: Dict[str, object] = field(default_factory=dict)
    info: Dict[str, object] = field(default_factory=dict)

    @property
    def n(self) -> int:
        return len(self.candele)


def _costruisci(tf, periodo, candele, mark, funding, btc_lista, info) -> Contesto:
    ill = _illiquidi()
    illiquido = np.array([
        (datetime.fromtimestamp(c.ts / 1000, tz=timezone.utc).year,
         datetime.fromtimestamp(c.ts / 1000, tz=timezone.utc).month) in ill
        for c in candele], dtype=bool)
    btc = None
    if btc_lista is not None:
        per_ts = {c.ts: c for c in btc_lista}
        btc = [per_ts.get(c.ts) for c in candele]
    return Contesto(
        tf=tf, periodo=periodo, candele=candele, mark=mark, funding=funding, btc=btc,
        illiquido=illiquido, ms=MS[tf],
        ts=np.array([c.ts for c in candele], dtype=np.int64),
        o=np.array([c.open for c in candele]), h=np.array([c.high for c in candele]),
        l=np.array([c.low for c in candele]), c=np.array([c.close for c in candele]),
        v=np.array([c.volume for c in candele]),
        indice_ts={c.ts: i for i, c in enumerate(candele)}, info=info,
    )


_CONTESTI: Dict[Tuple[str, str], Contesto] = {}


def contesto(tf: str, periodo: str = "costruzione") -> Contesto:
    """Serie allineate last/mark e funding. ``periodo``: "costruzione" o "completo" (fino al 2023-12-31)."""
    chiave = (tf, periodo)
    if chiave in _CONTESTI:
        return _CONTESTI[chiave]
    if periodo == "costruzione":
        fine = PER["fine_costruzione"]
    elif periodo == "completo":
        fine = FINE_IN_SAMPLE
    else:
        raise ValueError(periodo)
    ser = dati.carica_serie_allineate(SIMBOLO, tf, PRIMO_GIORNO, fine)
    funding = dati.carica_funding(SIMBOLO, PRIMO_GIORNO, fine)
    btc = dati.carica_candele("BTCUSDT", tf, PRIMO_GIORNO, fine)
    info = {"n_tolte_last": ser["n_tolte_last"], "n_tolte_mark": ser["n_tolte_mark"]}
    ctx = _costruisci(tf, periodo, ser["candele"], ser["candele_mark"], funding, btc, info)
    if periodo == "costruzione":
        assert ctx.candele[-1].close_ts <= PER["fine_costruzione_ts"]
    _CONTESTI[chiave] = ctx
    return ctx


def tronca(ctx: Contesto, k: int) -> Contesto:
    """Il contesto con le sole prime k barre (per la verifica di causalita')."""
    ultimo = ctx.candele[k - 1].close_ts
    btc_lista = [b for b in (ctx.btc or [])[:k] if b is not None] if ctx.btc is not None else None
    return _costruisci(ctx.tf, ctx.periodo + f"[:{k}]", ctx.candele[:k], ctx.mark[:k],
                       [(t, r) for t, r in ctx.funding if t <= ultimo], btc_lista, ctx.info)


# ---------------------------------------------------------------------------
# Strumenti causali per gli indicatori
# ---------------------------------------------------------------------------

def ema(x: np.ndarray, n: int) -> np.ndarray:
    """Media esponenziale con alfa 2/(n+1), avviata dalla media semplice dei primi n valori; NaN prima."""
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    a = 2.0 / (n + 1)
    out[n - 1] = np.mean(x[:n])
    for i in range(n, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    cs = np.cumsum(np.insert(x, 0, 0.0))
    out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def massimo_mobile(x: np.ndarray, n: int) -> np.ndarray:
    """Massimo delle ultime n barre, barra corrente compresa; NaN prima."""
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    from numpy.lib.stride_tricks import sliding_window_view
    out[n - 1:] = sliding_window_view(x, n).max(axis=1)
    return out


def minimo_mobile(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    from numpy.lib.stride_tricks import sliding_window_view
    out[n - 1:] = sliding_window_view(x, n).min(axis=1)
    return out


def deviazione_mobile(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    from numpy.lib.stride_tricks import sliding_window_view
    out[n - 1:] = sliding_window_view(x, n).std(axis=1, ddof=0)
    return out


def atr(ctx: Contesto, n: int) -> np.ndarray:
    """ATR di Wilder su n barre (vero range con il close precedente); NaN prima della barra n."""
    h, l, c = ctx.h, ctx.l, ctx.c
    tr = np.empty(len(c))
    tr[0] = h[0] - l[0]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    out[n] = np.mean(tr[1:n + 1])
    for i in range(n + 1, len(c)):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def rsi(c: np.ndarray, n: int) -> np.ndarray:
    """RSI di Wilder su n barre; NaN prima della barra n."""
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    d = np.diff(c)
    su = np.where(d > 0, d, 0.0)
    giu = np.where(d < 0, -d, 0.0)
    ms, mg = np.mean(su[:n]), np.mean(giu[:n])
    out[n] = 100.0 if mg == 0 else 100 - 100 / (1 + ms / mg)
    for i in range(n + 1, len(c)):
        ms = (ms * (n - 1) + su[i - 1]) / n
        mg = (mg * (n - 1) + giu[i - 1]) / n
        out[i] = 100.0 if mg == 0 else 100 - 100 / (1 + ms / mg)
    return out


def funding_ultimo(ctx: Contesto) -> np.ndarray:
    """Tasso dell'ultimo settlement avvenuto entro la chiusura della barra; NaN prima del primo."""
    tss = np.array([t for t, _ in ctx.funding], dtype=np.int64)
    tassi = np.array([r for _, r in ctx.funding])
    close_ts = np.array([c.close_ts for c in ctx.candele], dtype=np.int64)
    pos = np.searchsorted(tss, close_ts, side="right") - 1
    out = np.full(ctx.n, np.nan)
    ok = pos >= 0
    out[ok] = tassi[pos[ok]]
    return out


def btc_close(ctx: Contesto) -> np.ndarray:
    """Close di BTCUSDT sulla stessa barra (stesso ts); NaN dove BTCUSDT manca."""
    return np.array([b.close if b is not None else np.nan for b in ctx.btc])


def ora_utc(ctx: Contesto) -> np.ndarray:
    return (ctx.ts // 3_600_000) % 24


def giorno_settimana(ctx: Contesto) -> np.ndarray:
    """0 = lunedi' ... 6 = domenica, del ts di apertura della barra."""
    return ((ctx.ts // 86_400_000) + 3) % 7


# ---------------------------------------------------------------------------
# Varianti
# ---------------------------------------------------------------------------

class Variante:
    """Una regola completa: timeframe, direzione, ingresso, uscita, stop, target, filtri.

    Le sottoclassi definiscono:
    * ``indicatori(ctx)`` -> dict di array causali (si calcola una volta per contesto);
    * ``riscaldamento(ind)`` -> primo indice in cui TUTTO e' calcolabile;
    * ``condizione(ctx, ind, i)`` -> bool, la condizione d'ingresso con i filtri dell'ipotesi;
    * ``livelli(ctx, ind, i)`` -> (stop, target o None) calcolati alla chiusura della barra i;
    * ``esci(ctx, ind, i, pos, i_entrata)`` -> True per chiudere all'apertura della barra dopo.
    """

    id: str = ""
    tf: str = "1h"
    direzione: str = "long"
    parametri: Dict[str, object] = {}

    def __init__(self, id: str, tf: str, direzione: str, **parametri):
        self.id, self.tf, self.direzione = id, tf, direzione
        self.parametri = dict(parametri)

    def chiave(self) -> str:
        return f"{type(self).__name__}|{self.tf}|{self.direzione}|{json.dumps(self.parametri, sort_keys=True)}"

    def indicatori(self, ctx: Contesto) -> Dict[str, np.ndarray]:
        raise NotImplementedError

    def riscaldamento(self, ind: Dict[str, np.ndarray]) -> int:
        """Primo indice in cui tutti gli array sono finiti (dopo, NaN solo per dati mancanti)."""
        primo = 0
        for a in ind.values():
            a = np.asarray(a, dtype=float)
            finiti = np.flatnonzero(np.isfinite(a))
            if finiti.size == 0:
                return 10**12
            primo = max(primo, int(finiti[0]))
        return primo

    def condizione(self, ctx, ind, i) -> bool:
        raise NotImplementedError

    def livelli(self, ctx, ind, i) -> Optional[Tuple[float, Optional[float]]]:
        raise NotImplementedError

    def esci(self, ctx, ind, i, pos, i_entrata) -> bool:
        return False

    def copia(self, nuovo_id: Optional[str] = None, **modifiche) -> "Variante":
        p = dict(self.parametri)
        p.update(modifiche)
        return type(self)(nuovo_id or self.id, self.tf, self.direzione, **p)


def _indicatori(var: Variante, ctx: Contesto):
    k = "ind|" + var.chiave()
    if k not in ctx.cache:
        ind = var.indicatori(ctx)
        ctx.cache[k] = (ind, var.riscaldamento(ind))
    return ctx.cache[k]


def fabbriche(var: Variante, ctx: Contesto, ritardo_uscita: bool = False):
    """Le funzioni che creano le strategie: variante, baseline (a), casuale (b) e segnale.

    Ogni chiamata a una fabbrica crea una strategia nuova (sezione 7). Gli array degli
    indicatori sono condivisi in sola lettura.
    """
    ind, risc = _indicatori(var, ctx)
    illiquido = ctx.illiquido
    indice_ts = ctx.indice_ts

    def seg(i: int) -> Optional[Segnale]:
        if i < risc:
            return None
        lv = var.livelli(ctx, ind, i)
        if lv is None:
            return None
        stop, target = lv
        if stop is None or not math.isfinite(stop) or (target is not None and not math.isfinite(target)):
            return None
        return Segnale(var.direzione, float(stop), None if target is None else float(target))

    def esci(i, pos) -> bool:
        return bool(var.esci(ctx, ind, i, pos, indice_ts[pos.ts_entrata]))

    def crea():
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is None:
                if illiquido[i] or i < risc:
                    return None
                if var.condizione(ctx, ind, i):
                    return seg(i)
                return None
            return "chiudi" if esci(i, pos) else None
        return strategia

    def crea_a():
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is None:
                if illiquido[i]:
                    return None
                return seg(i)
            return "chiudi" if esci(i, pos) else None
        return strategia

    def crea_casuale(ingressi):
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is None:
                return seg(i) if i in ingressi else None
            return "chiudi" if esci(i, pos) else None
        return strategia

    def crea_segnale():
        return lambda storia: seg(len(storia) - 1)

    return crea, crea_a, crea_casuale, crea_segnale


def verifica_causalita(var: Variante, ctx: Contesto, punti: int = 6) -> List[str]:
    """Ricalcola gli indicatori e le decisioni su serie troncate: devono coincidere con quelli
    sulla serie intera fino alla barra di taglio. Ritorna le differenze (vuota = causale)."""
    ind, _ = _indicatori(var, ctx)
    diff = []
    rng = np.random.default_rng(12345)
    tagli = sorted(set(int(x) for x in rng.integers(ctx.n // 10, ctx.n - 1, size=punti)))
    for k in tagli:
        sub = tronca(ctx, k)
        ind_s = var.indicatori(sub)
        for nome, a in ind.items():
            a = np.asarray(a, dtype=float)[:k]
            b = np.asarray(ind_s[nome], dtype=float)
            if a.shape != b.shape or not np.allclose(a, b, equal_nan=True, rtol=1e-9, atol=1e-12):
                diff.append(f"{nome} al taglio {k}")
    return diff


# ---------------------------------------------------------------------------
# Esecuzione e Fase 2
# ---------------------------------------------------------------------------

def parametri_con(**modifiche) -> Parametri:
    from dataclasses import replace
    return replace(PARAMETRI, **modifiche)


def conta(var: Variante, parametri: Parametri = None) -> Dict[str, int]:
    """``conta_trade`` sui dati di costruzione, regole esatte della variante (sezione 8)."""
    ctx = contesto(var.tf, "costruzione")
    crea, _, _, _ = fabbriche(var, ctx)
    return motore.conta_trade(ctx.candele, crea, PER["fine_costruzione_ts"], parametri or PARAMETRI,
                              None, ctx.mark, ctx.funding)


def esegui(var: Variante, ctx: Contesto, parametri: Parametri = None, quale: str = "variante") -> motore.Risultato:
    crea, crea_a, _, _ = fabbriche(var, ctx)
    fabbrica = crea if quale == "variante" else crea_a
    return motore.esegui(ctx.candele, None, ctx.mark, ctx.funding, fabbrica(), parametri or PARAMETRI)


_LAVORO: Dict[str, object] = {}


def _blocco_simulazioni(primo_seme_e_n):
    primo, n = primo_seme_e_n
    w = _LAVORO
    return motore.simula_baseline_casuale(
        w["candele"], w["crea_casuale"], w["n_trade"], w["durata"], w["parametri"],
        None, w["mark"], w["funding"], w["vietate"], n_simulazioni=n, primo_seme=primo)


def baseline_b(var: Variante, ctx: Contesto, n_trade: int, durata: int, parametri: Parametri,
               vietate_extra: Sequence[Tuple[int, int]] = ()) -> Dict[str, object]:
    """La (b) con ``simula_baseline_casuale``, semi 0..199 divisi in 4 blocchi paralleli.

    Ogni seme da' la stessa simulazione che darebbe una chiamata unica (la tabella delle
    configurazioni non dipende dal seme): si concatenano gli R medi nell'ordine dei semi e
    si ricalcola il numero con ``statistica.baseline_casuale``.
    """
    _, _, crea_casuale, crea_segnale = fabbriche(var, ctx)
    vietate_segnale = motore.barre_vietate_segnale_non_valido(ctx.candele, crea_segnale, parametri)
    vietate = list(vietate_segnale) + intervalli(ctx.illiquido) + list(vietate_extra)
    _LAVORO.clear()
    _LAVORO.update(candele=ctx.candele, crea_casuale=crea_casuale, n_trade=n_trade, durata=durata,
                   parametri=parametri, mark=ctx.mark, funding=ctx.funding, vietate=vietate)
    blocchi = [(s, N_SIM // 4) for s in range(0, N_SIM, N_SIM // 4)]
    with mp.get_context("fork").Pool(4) as pool:
        parti = pool.map(_blocco_simulazioni, blocchi)
    valori = np.concatenate([np.asarray(p["valori"]) for p in parti])
    base = statistica.baseline_casuale(valori)
    base["trade_per_simulazione"] = sum((list(p["trade_per_simulazione"]) for p in parti), [])
    base["simulazioni_vuote"] = sum(int(p["simulazioni_vuote"]) for p in parti)
    base["segnali_non_validi_per_simulazione"] = sum((list(p["segnali_non_validi_per_simulazione"]) for p in parti), [])
    base["segnali_senza_barra_per_simulazione"] = sum((list(p["segnali_senza_barra_per_simulazione"]) for p in parti), [])
    n_vietate_segnale = sum(b - a for a, b in vietate_segnale)
    base["quota_barre_vietate_segnale"] = n_vietate_segnale / ctx.n
    return base


def intervalli(maschera: np.ndarray) -> List[Tuple[int, int]]:
    out = []
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


def _anno(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year


def r_per_anno(trades) -> Dict[str, float]:
    per: Dict[int, List[float]] = {}
    for t in trades:
        per.setdefault(_anno(t.ts_uscita), []).append(t.r)
    return {str(a): round(float(np.mean(v)), 4) for a, v in sorted(per.items())}


def trade_per_anno(trades) -> Dict[str, int]:
    per: Dict[int, int] = {}
    for t in trades:
        per[_anno(t.ts_uscita)] = per.get(_anno(t.ts_uscita), 0) + 1
    return {str(a): v for a, v in sorted(per.items())}


def buy_and_hold_per_anno(ctx: Contesto, da_ts: int = 0) -> Dict[str, Dict[str, float]]:
    per: Dict[int, List[Candela]] = {}
    for c in ctx.candele:
        if c.ts >= da_ts:
            per.setdefault(_anno(c.ts), []).append(c)
    return {str(a): {"long": round(motore.buy_and_hold(cs, PARAMETRI, "long"), 4),
                     "short": round(motore.buy_and_hold(cs, PARAMETRI, "short"), 4)}
            for a, cs in sorted(per.items())}


def _pulisci(d: Dict[str, object]) -> Dict[str, object]:
    out = {}
    for k, v in d.items():
        if k in ("valori", "campioni"):
            continue
        if isinstance(v, (np.floating, float)):
            v = float(v)
            out[k] = None if not math.isfinite(v) else round(v, 6)
        elif isinstance(v, (np.integer,)):
            out[k] = int(v)
        elif isinstance(v, list) and v and isinstance(v[0], (int, np.integer)):
            out[k] = {"media": round(float(np.mean(v)), 2), "minimo": int(min(v)), "massimo": int(max(v))}
        else:
            out[k] = v
    return out


def valuta(var: Variante, periodo: str = "costruzione", parametri: Parametri = None,
           solo_b: bool = False) -> Dict[str, object]:
    """Fase 2 (o validazione): metriche, (a), (b), percentile, per anno. Ritorna la voce di risultato.

    ``periodo`` "costruzione": serie di costruzione. "validazione": serie dall'inizio della
    costruzione alla fine della validazione (indicatori caldi), contano solo i trade entrati
    dopo la fine della costruzione; la (b) estrae ingressi solo fra le barre di validazione.
    """
    parametri = parametri or PARAMETRI
    ctx = contesto(var.tf, "costruzione" if periodo == "costruzione" else "completo")
    ris = esegui(var, ctx, parametri)
    if periodo == "costruzione":
        trades = list(ris.trades)
        da_ts = 0
        vietate_extra: List[Tuple[int, int]] = []
    else:
        da_ts = PER["inizio_validazione_ts"]
        trades = [t for t in ris.trades if t.ts_entrata >= da_ts]
        primo_val = int(np.searchsorted(ctx.ts, da_ts))
        vietate_extra = [(0, primo_val)]
    trades.sort(key=lambda t: t.ts_uscita)
    r = [t.r for t in trades]
    n = len(r)
    out: Dict[str, object] = {"periodo": periodo}
    pnl = [t.pnl for t in trades]
    met = {
        "trade": n,
        "profit_factor": round(statistica.profit_factor(pnl), 4) if n else None,
        "r_medio": round(float(np.mean(r)), 4) if n else None,
        "win_rate": round(statistica.win_rate(pnl), 4) if n else None,
        "r_medio_per_anno": r_per_anno(trades),
        "trade_per_anno": trade_per_anno(trades),
        "r_medio_senza_3_migliori": round(float(np.mean(sorted(r)[:-3])), 4) if n > 3 else None,
        "rendimento_totale": round(sum(pnl) / parametri.capitale_iniziale, 4),
        "rendimento_per_anno": {str(k): round(v, 4) for k, v in motore.rendimento_per_anno(trades, parametri.capitale_iniziale).items()},
        "drawdown_max": round(motore.drawdown_massimo(_curva(trades, parametri.capitale_iniziale)), 4),
        "esiti": {e: sum(1 for t in trades if t.esito == e) for e in ("stop", "target", "segnale", "liquidazione", "fine_dati")},
        "trade_ridotti_leva": sum(1 for t in trades if t.ridotto),
        "violazioni_liquidazione": sum(1 for t in trades if t.violazione_liquidazione),
        "stop_oltre_6_per_cento": sum(1 for t in trades if abs(t.entrata - t.stop) / t.entrata > STOP_MASSIMO_BOT),
        "distanza_stop_mediana_pct": round(float(np.median([abs(t.entrata - t.stop) / t.entrata for t in trades])) * 100, 3) if n else None,
        "costo_medio_r": round(float(np.mean([(t.commissioni + t.slippage_costo + t.funding_pagato) / t.rischio_iniziale for t in trades])), 4) if n else None,
        "durata_media_barre": motore.durata_media_barre(trades, ctx.ms) if n else None,
        "segnali_non_validi": ris.n_segnali_non_validi,
        "buchi_dati": ris.n_buchi_dati,
    }
    out["metriche"] = met
    if n == 0:
        out["valutabile"] = False
        return out
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    out["blocco"] = blocco
    # baseline (a)
    if not solo_b:
        ris_a = esegui(var, ctx, parametri, quale="a")
        ta = sorted([t for t in ris_a.trades if t.ts_entrata >= da_ts], key=lambda t: t.ts_uscita)
        if len(ta) >= 2:
            blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in ta], [t.ts_uscita for t in ta])
            base_a = statistica.baseline_da_trade([t.r for t in ta], blocco_a, n=N_BOOT, seme=SEME_BOOT)
            conf_a = statistica.contro_baseline(r, blocco, base_a, n=N_BOOT, seme=SEME_BOOT)
            out["baseline_a"] = dict(_pulisci(conf_a), media=round(base_a["media"], 6), n_trade=len(ta),
                                     blocco_a=blocco_a, valutabile_a=base_a["valutabile"])
        else:
            out["baseline_a"] = {"valutabile": False, "netta": False, "t": None, "n_trade": len(ta)}
    # baseline (b)
    durata = motore.durata_media_barre(trades, ctx.ms)
    try:
        base_b = baseline_b(var, ctx, n, durata, parametri, vietate_extra)
        conf_b = statistica.contro_baseline(r, blocco, base_b, n=N_BOOT, seme=SEME_BOOT)
        out["baseline_b"] = dict(_pulisci(conf_b), media=round(base_b["media"], 6),
                                 n_simulazioni=base_b["n_simulazioni"],
                                 trade_per_simulazione=_pulisci({"x": base_b["trade_per_simulazione"]})["x"],
                                 simulazioni_vuote=base_b["simulazioni_vuote"],
                                 segnali_scartati_per_simulazione_media=round(float(np.mean(base_b["segnali_non_validi_per_simulazione"])), 2),
                                 quota_barre_vietate_segnale=round(base_b["quota_barre_vietate_segnale"], 4),
                                 durata_media_barre=durata)
        out["percentile_caso"] = round(statistica.percentile_del_candidato(float(np.mean(r)), base_b["valori"]), 1)
        out["_valori_b"] = base_b["valori"]
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "netta": False, "t": None, "errore": str(e)}
    out["buy_and_hold_per_anno"] = buy_and_hold_per_anno(ctx, da_ts)
    a_ok = out.get("baseline_a", {}).get("valutabile", False) if not solo_b else True
    b_ok = out["baseline_b"].get("valutabile", False)
    out["valutabile"] = bool(a_ok and b_ok)
    out["candidato"] = bool(out["valutabile"] and (solo_b or out["baseline_a"]["netta"]) and out["baseline_b"]["netta"]
                            and met["r_medio"] > 0)
    out["_trades"] = trades
    return out


def _curva(trades, cap0):
    curva = [(0, cap0)]
    cap = cap0
    for t in sorted(trades, key=lambda t: t.ts_uscita):
        cap += t.pnl
        curva.append((t.ts_uscita, cap))
    return curva


def per_log(ris: Dict[str, object]) -> Dict[str, object]:
    """La voce di risultato senza i campi interni (trade e valori grezzi)."""
    return {k: v for k, v in ris.items() if not k.startswith("_")}
