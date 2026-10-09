"""Codice comune della campagna DYDXUSDT: dati, indicatori, strategie, baseline e metriche.

Nessuna strategia vive qui: solo i mattoni per eseguire una variante come chiede il protocollo
(sezioni 6, 7 e 8). Le varianti stanno in ``varianti.py``.

Scelte scritte prima del primo test (regola 9: le regole di esecuzione non cambiano dopo):

* Serie: last e mark da ``carica_serie_allineate`` sul timeframe della variante (file nativi);
  stop sul last (``candele_stop=None``); funding storico vero da ``carica_funding``.
* Parametri del motore da ``config/parametri.yaml`` e dalla scheda: commissione 0,05% per lato,
  slippage 0,02% per lato, rischio 1%, leva massima 2, margine isolated, mantenimento 0,025,
  margine dalla liquidazione 0,8, capitale 1000, stop prima del target.
* Filtro di liquidita' (Fase 0 punto 3): nessuna posizione si apre su segnali di barre che cadono
  in un mese sotto 20 milioni di USDT al giorno (media dei ``quote_volume`` dei file 1d del last);
  stesso filtro per ``conta_trade``, il test e la (a); le stesse barre vietate alla (b).
* Indicatori: calcolati una volta su tutta la serie passata al motore, in modo CAUSALE (il valore
  alla barra i usa solo barre fino a i). La strategia li legge all'indice della sua ultima barra
  chiusa, controllando che il ``ts`` coincida. Per la validazione la serie va dall'inizio della
  costruzione alla fine della validazione (indicatori caldi) e contano i trade entrati dopo la fine
  della costruzione. I buchi di dati (barre tolte dall'allineamento) non si riempiono: gli
  indicatori trattano le barre presenti come consecutive (le barre tolte sono dichiarate in Fase 0).
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

RADICE_REPO = Path(__file__).resolve().parents[4]
if str(RADICE_REPO) not in sys.path:
    sys.path.insert(0, str(RADICE_REPO))

from research.src import dati, motore, statistica  # noqa: E402
from research.src.motore import Candela, Parametri, Segnale  # noqa: E402

SIMBOLO = "DYDXUSDT"
INIZIO = date(2021, 9, 1)
FINE_COSTRUZIONE = date(2023, 4, 19)
FINE_VALIDAZIONE = date(2023, 12, 31)
_P = dati.periodi_campagna(INIZIO)
assert _P["fine_costruzione"] == FINE_COSTRUZIONE
FINE_COSTRUZIONE_TS = int(_P["fine_costruzione_ts"])
INIZIO_VALIDAZIONE_TS = int(_P["inizio_validazione_ts"])

LIQUIDITA_MINIMA = 20_000_000
TRADE_MINIMI_COSTRUZIONE = 70
TRADE_MINIMI_VALIDAZIONE = 30
N_SIMULAZIONI = 200
N_BOOT = 2000
SEME_BOOT = 0
STOP_MASSIMO_BOT = 0.06

MS_TF = {tf: dati.durata_intervallo(tf) for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]}


def parametri(moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0,
              riempimento_intrabarra: str = "stop_prima") -> Parametri:
    return Parametri(
        commissione_per_lato=0.0005,
        slippage_per_lato=0.0002,
        rischio_per_trade=0.01,
        leva_max=2.0,
        modalita_margine="isolated",
        tasso_margine_mantenimento=0.025,
        margine_minimo_da_liquidazione=0.8,
        capitale_iniziale=1000.0,
        riempimento_intrabarra=riempimento_intrabarra,
        moltiplicatore_costi=moltiplicatore_costi,
        ritardo_barre=ritardo_barre,
    )


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------

def mesi_illiquidi() -> Dict[Tuple[int, int], float]:
    """{(anno, mese): volume medio giornaliero in USDT} per i mesi sotto la soglia, dai file 1d del last."""
    medie = volume_medio_mensile()
    return {k: v for k, v in medie.items() if v < LIQUIDITA_MINIMA}


def volume_medio_mensile() -> Dict[Tuple[int, int], float]:
    per_mese: Dict[Tuple[int, int], List[float]] = {}
    for anno, mese in dati.mesi_del_periodo(INIZIO, FINE_VALIDAZIONE):
        p = dati.percorso_mese(SIMBOLO, "klines", "1d", anno, mese)
        if not p.is_file():
            continue
        for ts, v in dati.volume_usdt_da_zip(p).items():
            g = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
            per_mese.setdefault((g.year, g.month), []).append(v)
    return {k: float(np.mean(v)) for k, v in sorted(per_mese.items())}


_CACHE: Dict[Tuple[str, date], "Contesto"] = {}


@dataclass
class Contesto:
    """Le serie di un timeframe su un periodo, con gli array numpy e gli indicatori in cache."""

    tf: str
    fine: date
    candele: List[Candela]
    candele_mark: List[Candela]
    funding: List[Tuple[int, float]]
    tolte_last: int
    tolte_mark: int
    volume_usdt: np.ndarray
    ts: np.ndarray
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray
    vietata_liquidita: np.ndarray
    cache: Dict[str, np.ndarray] = field(default_factory=dict)
    btc: Optional[np.ndarray] = None  # close di BTCUSDT allineato ai ts (NaN se manca)

    @property
    def n(self) -> int:
        return len(self.candele)

    @property
    def ms(self) -> int:
        return MS_TF[self.tf]

    def indice_di(self, ts: int) -> int:
        return int(np.searchsorted(self.ts, ts))


def contesto(tf: str, fine: date = FINE_COSTRUZIONE) -> Contesto:
    chiave = (tf, fine)
    if chiave in _CACHE:
        return _CACHE[chiave]
    s = dati.carica_serie_allineate(SIMBOLO, tf, INIZIO, fine)
    candele = s["candele"]
    funding = dati.carica_funding(SIMBOLO, INIZIO, fine)
    illiquidi = mesi_illiquidi()
    ts = np.array([c.ts for c in candele], dtype=np.int64)
    viet = np.zeros(len(candele), dtype=bool)
    for k, c in enumerate(candele):
        g = datetime.fromtimestamp(c.ts / 1000, tz=timezone.utc)
        if (g.year, g.month) in illiquidi:
            viet[k] = True
    vol = np.array([np.nan if s["volume_usdt"].get(c.ts) is None else s["volume_usdt"][c.ts] for c in candele])
    btc_candele = dati.carica_candele("BTCUSDT", tf, INIZIO, fine)
    btc_map = {b.ts: b.close for b in btc_candele}
    btc = np.array([btc_map.get(c.ts, np.nan) for c in candele], dtype=float)
    ctx = Contesto(
        tf=tf, fine=fine, candele=candele, candele_mark=s["candele_mark"], funding=funding,
        tolte_last=s["n_tolte_last"], tolte_mark=s["n_tolte_mark"], volume_usdt=vol, ts=ts,
        o=np.array([c.open for c in candele]), h=np.array([c.high for c in candele]),
        l=np.array([c.low for c in candele]), c=np.array([c.close for c in candele]),
        vietata_liquidita=viet, btc=btc,
    )
    _CACHE[chiave] = ctx
    return ctx


# ---------------------------------------------------------------------------
# Indicatori causali (valore alla barra i con le sole barre 0..i)
# ---------------------------------------------------------------------------

def sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if n <= len(x):
        cs = np.cumsum(np.insert(x, 0, 0.0))
        out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def ema(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if n > len(x):
        return out
    a = 2.0 / (n + 1)
    out[n - 1] = np.mean(x[:n])
    for i in range(n, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def true_range(ctx: Contesto) -> np.ndarray:
    prev = np.concatenate([[np.nan], ctx.c[:-1]])
    tr = np.maximum(ctx.h - ctx.l, np.maximum(np.abs(ctx.h - prev), np.abs(ctx.l - prev)))
    tr[0] = ctx.h[0] - ctx.l[0]
    return tr


def atr(ctx: Contesto, n: int) -> np.ndarray:
    """ATR di Wilder: media semplice delle prime n, poi (prec*(n-1)+tr)/n."""
    chiave = f"atr{n}"
    if chiave in ctx.cache:
        return ctx.cache[chiave]
    tr = true_range(ctx)
    out = np.full(ctx.n, np.nan)
    if n <= ctx.n:
        out[n - 1] = tr[:n].mean()
        for i in range(n, ctx.n):
            out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    ctx.cache[chiave] = out
    return out


def rsi(x: np.ndarray, n: int) -> np.ndarray:
    """RSI di Wilder."""
    out = np.full(len(x), np.nan)
    d = np.diff(x)
    if len(d) < n:
        return out
    g = np.where(d > 0, d, 0.0)
    p = np.where(d < 0, -d, 0.0)
    ag, ap = g[:n].mean(), p[:n].mean()
    def val(ag, ap):
        return 100.0 if ap == 0 else 100.0 - 100.0 / (1 + ag / ap)
    out[n] = val(ag, ap)
    for i in range(n + 1, len(x)):
        ag = (ag * (n - 1) + g[i - 1]) / n
        ap = (ap * (n - 1) + p[i - 1]) / n
        out[i] = val(ag, ap)
    return out


def rendimento(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    out[n:] = x[n:] / x[:-n] - 1.0
    return out


def massimo_precedente(x: np.ndarray, n: int) -> np.ndarray:
    """Massimo delle n barre PRIMA della barra i (esclusa la i)."""
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        out[i] = x[i - n:i].max()
    return out


def minimo_precedente(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        out[i] = x[i - n:i].min()
    return out


def deviazione(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = x[i - n + 1:i + 1].std(ddof=0)
    return out


def quota_acquisti_taker(ctx: Contesto) -> np.ndarray:
    """Quota del volume in USDT comprata dai taker (colonna taker_buy_quote_volume / quote_volume).

    Letta dagli stessi file klines del timeframe; NaN se la riga non ha le colonne o il volume e' zero.
    """
    if "quota_taker" in ctx.cache:
        return ctx.cache["quota_taker"]
    per_ts: Dict[int, float] = {}
    for anno, mese in dati.mesi_del_periodo(INIZIO, ctx.fine):
        p = dati.percorso_mese(SIMBOLO, "klines", ctx.tf, anno, mese)
        if not p.is_file():
            continue
        for riga in dati.righe_csv_da_zip(p):
            ts = dati.normalizza_ts(riga[0])
            if ts in per_ts or len(riga) < 11:
                continue
            q, tb = float(riga[7]), float(riga[10])
            per_ts[ts] = tb / q if q > 0 else float("nan")
    out = np.array([per_ts.get(int(t), np.nan) for t in ctx.ts], dtype=float)
    ctx.cache["quota_taker"] = out
    return out


def funding_ultimo(ctx: Contesto) -> np.ndarray:
    """Ultimo tasso di funding regolato entro la CHIUSURA della barra i (NaN prima del primo)."""
    if "funding_ultimo" in ctx.cache:
        return ctx.cache["funding_ultimo"]
    f_ts = np.array([t for t, _ in ctx.funding], dtype=np.int64)
    f_v = np.array([r for _, r in ctx.funding], dtype=float)
    chiusure = np.array([c.close_ts for c in ctx.candele], dtype=np.int64)
    idx = np.searchsorted(f_ts, chiusure, side="right") - 1
    out = np.where(idx >= 0, f_v[np.clip(idx, 0, None)], np.nan)
    ctx.cache["funding_ultimo"] = out
    return out


# ---------------------------------------------------------------------------
# Varianti
# ---------------------------------------------------------------------------

@dataclass
class Spec:
    """Una variante pronta per il motore su un contesto.

    ``segnale(i)``: il Segnale (direzione, stop, target) che la variante emetterebbe alla chiusura
    della barra i SENZA la condizione d'ingresso, o None se non calcolabile (riscaldamento).
    ``condizione(i)``: la condizione d'ingresso dell'ipotesi (filtri compresi).
    ``esci(i, pos)``: True se alla chiusura della barra i la posizione aperta va chiusa (uscita
    all'apertura della barra dopo).
    """

    segnale: Callable[[int], Optional[Segnale]]
    condizione: Callable[[int], bool]
    esci: Callable[[int, motore.Posizione], bool]


def barre_in_posizione(ctx: Contesto, i: int, pos: motore.Posizione) -> int:
    """Barre chiuse da quando la posizione e' entrata, contate in tempo (ingresso all'apertura)."""
    return int((ctx.candele[i].close_ts + 1 - pos.ts_entrata) // ctx.ms)


def _indice(ctx: Contesto, storia) -> int:
    i = len(storia) - 1
    if storia[-1].ts != ctx.candele[i].ts:
        raise RuntimeError("la storia non coincide con il contesto: indici sfasati")
    return i


def fabbrica(ctx: Contesto, crea_spec: Callable[[Contesto], Spec], con_condizione: bool = True):
    """La funzione SENZA argomenti che crea la strategia della variante (o della (a) senza condizione)."""
    def crea():
        spec = crea_spec(ctx)

        def strategia(storia, pos):
            i = _indice(ctx, storia)
            if pos is not None:
                return "chiudi" if spec.esci(i, pos) else None
            if ctx.vietata_liquidita[i]:
                return None
            if con_condizione and not spec.condizione(i):
                return None
            return spec.segnale(i)
        return strategia
    return crea


def fabbrica_casuale(ctx: Contesto, crea_spec: Callable[[Contesto], Spec]):
    """crea_casuale(ingressi): alle barre in ``ingressi`` il segnale della variante, poi la sua uscita."""
    def crea_casuale(ingressi):
        spec = crea_spec(ctx)

        def strategia(storia, pos):
            i = _indice(ctx, storia)
            if pos is not None:
                return "chiudi" if spec.esci(i, pos) else None
            if i in ingressi:
                return spec.segnale(i)
            return None
        return strategia
    return crea_casuale


def fabbrica_segnale(ctx: Contesto, crea_spec: Callable[[Contesto], Spec]):
    def crea_segnale():
        spec = crea_spec(ctx)

        def segnale(storia):
            return spec.segnale(_indice(ctx, storia))
        return segnale
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
# Conteggio, test e baseline
# ---------------------------------------------------------------------------

def conta(tf: str, crea_spec, par: Optional[Parametri] = None) -> Dict[str, int]:
    ctx = contesto(tf, FINE_COSTRUZIONE)
    par = par or parametri()
    return motore.conta_trade(ctx.candele, fabbrica(ctx, crea_spec), FINE_COSTRUZIONE_TS, par,
                              candele_stop=None, candele_mark=ctx.candele_mark, funding=ctx.funding)


def _esegui(ctx: Contesto, crea, par: Parametri) -> motore.Risultato:
    return motore.esegui(ctx.candele, None, ctx.candele_mark, list(ctx.funding), crea(), par)


def _per_anno_r(trades) -> Dict[str, float]:
    gruppi: Dict[str, List[float]] = {}
    for t in trades:
        a = str(datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc).year)
        gruppi.setdefault(a, []).append(t.r)
    return {a: float(np.mean(v)) for a, v in sorted(gruppi.items())}


def _trade_per_anno(trades) -> Dict[str, int]:
    gruppi: Dict[str, int] = {}
    for t in trades:
        a = str(datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc).year)
        gruppi[a] = gruppi.get(a, 0) + 1
    return dict(sorted(gruppi.items()))


def buy_and_hold_per_anno(ctx: Contesto, par: Parametri, da_ts: int = 0) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    anni = sorted({datetime.fromtimestamp(c.ts / 1000, tz=timezone.utc).year for c in ctx.candele if c.ts >= da_ts})
    for a in anni:
        cs = [c for c in ctx.candele if c.ts >= da_ts and datetime.fromtimestamp(c.ts / 1000, tz=timezone.utc).year == a]
        out[str(a)] = {"long": motore.buy_and_hold(cs, par, "long"), "short": motore.buy_and_hold(cs, par, "short")}
    return out


def _sintesi_confronto(c: Dict) -> Dict:
    chiavi = ["differenza", "errore_standard", "errore_candidato", "errore_minimo", "baseline_media",
              "baseline_errore_standard", "t", "soglia", "netta", "valutabile", "n_blocchi", "p_value"]
    return {k: c.get(k) for k in chiavi}


def valuta(tf: str, crea_spec, par: Optional[Parametri] = None, periodo: str = "costruzione",
           n_simulazioni: int = N_SIMULAZIONI) -> Dict:
    """Test di una variante con le baseline (a) e (b) della sezione 8 sul periodo indicato.

    ``periodo`` = "costruzione" (serie fino al 2023-04-19) oppure "validazione" (serie fino al
    2023-12-31, contano solo i trade entrati dopo la fine della costruzione; la (b) entra solo
    nelle barre di validazione; la (a) conta i suoi trade entrati in validazione).
    """
    par = par or parametri()
    fine = FINE_COSTRUZIONE if periodo == "costruzione" else FINE_VALIDAZIONE
    ctx = contesto(tf, fine)
    da_ts = 0 if periodo == "costruzione" else INIZIO_VALIDAZIONE_TS

    def nel_periodo(trades):
        return sorted([t for t in trades if t.ts_entrata >= da_ts], key=lambda t: t.ts_uscita)

    ris = _esegui(ctx, fabbrica(ctx, crea_spec), par)
    trades = nel_periodo(ris.trades)
    out: Dict = {"periodo": periodo, "timeframe": tf, "moltiplicatore_costi": par.moltiplicatore_costi,
                 "ritardo_barre": par.ritardo_barre, "riempimento_intrabarra": par.riempimento_intrabarra}
    met = motore.calcola_metriche(motore.Risultato(trades, ris.curva_capitale if periodo == "costruzione" else
                                                   _curva(trades, par), par.capitale_iniziale,
                                                   par.capitale_iniziale + sum(t.pnl for t in trades),
                                                   ris.n_segnali_non_validi, ris.n_segnali_senza_barra,
                                                   ris.n_segnali_capitale_esaurito, ris.n_buchi_dati,
                                                   ris.n_funding_in_buco))
    r = [t.r for t in trades]
    stop_pct = [abs(t.entrata - t.stop) / t.entrata for t in trades]
    out["metriche"] = {
        "trade": len(trades),
        "profit_factor": met["profit_factor"],
        "r_medio": float(np.mean(r)) if r else None,
        "r_medio_per_anno": _per_anno_r(trades),
        "trade_per_anno": _trade_per_anno(trades),
        "r_medio_senza_3_migliori": float(np.mean(sorted(r)[:-3])) if len(r) > 3 else None,
        "drawdown_max": met["drawdown_max"],
        "rendimento_totale": met["rendimento_totale"],
        "rendimento_per_anno": {str(k): v for k, v in met["rendimento_per_anno"].items()},
        "win_rate": met["win_rate"],
        "esiti": met["esiti"],
        "n_ridotti": met["n_ridotti"],
        "n_violazioni_liquidazione": met["n_violazioni_liquidazione"],
        "n_segnali_non_validi": met["n_segnali_non_validi"],
        "n_buchi_dati": met["n_buchi_dati"],
        "n_funding_in_buco": met["n_funding_in_buco"],
        "funding_totale": met["funding_totale"],
        "costi_totali": met["costi_totali"],
        "stop_medio_pct": float(np.mean(stop_pct)) if stop_pct else None,
        "quota_stop_oltre_6pct": float(np.mean([s > STOP_MASSIMO_BOT for s in stop_pct])) if stop_pct else None,
    }
    out["buy_and_hold_per_anno"] = buy_and_hold_per_anno(ctx, par, da_ts)
    if len(trades) < 2:
        out["valutabile"] = False
        out["motivo"] = "meno di 2 trade"
        return out
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    out["blocco"] = blocco

    # (a): senza condizione d'ingresso, filtro di liquidita' tenuto, entra a ogni barra libera
    ris_a = _esegui(ctx, fabbrica(ctx, crea_spec, con_condizione=False), par)
    trades_a = nel_periodo(ris_a.trades)
    if len(trades_a) >= 2:
        blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in trades_a], [t.ts_uscita for t in trades_a])
        base_a = statistica.baseline_da_trade([t.r for t in trades_a], blocco_a, n=N_BOOT, seme=SEME_BOOT)
        conf_a = statistica.contro_baseline(r, blocco, base_a, n=N_BOOT, seme=SEME_BOOT)
        out["baseline_a"] = dict(_sintesi_confronto(conf_a), media=base_a["media"], n_trade=base_a["n_trade"],
                                 blocco=blocco_a, n_blocchi_a=base_a["n_blocchi"],
                                 valutabile_a=base_a["valutabile"])
    else:
        out["baseline_a"] = {"valutabile": False, "netta": False, "t": -math.inf, "motivo": "la (a) ha meno di 2 trade"}

    # (b): entrate casuali con la stessa uscita
    durata = motore.durata_media_barre(trades, ctx.ms)
    maschera = np.zeros(ctx.n, dtype=bool)
    for a, b in motore.barre_vietate_segnale_non_valido(ctx.candele, fabbrica_segnale(ctx, crea_spec), par):
        maschera[a:b] = True
    quota_segnale_non_valido = float(maschera[ctx.ts >= da_ts].mean())
    maschera |= ctx.vietata_liquidita
    if periodo == "validazione":
        maschera |= ctx.ts < da_ts
    vietate = intervalli_da_maschera(maschera)
    try:
        base_b = motore.simula_baseline_casuale(
            ctx.candele, fabbrica_casuale(ctx, crea_spec), len(trades), durata, par,
            candele_stop=None, candele_mark=ctx.candele_mark, funding=ctx.funding,
            barre_vietate=vietate, n_simulazioni=n_simulazioni, primo_seme=0)
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "netta": False, "t": -math.inf, "motivo": str(e)}
        out["valutabile"] = False
        return out
    conf_b = statistica.contro_baseline(r, blocco, base_b, n=N_BOOT, seme=SEME_BOOT)
    tps = base_b["trade_per_simulazione"]
    out["baseline_b"] = dict(
        _sintesi_confronto(conf_b), media=base_b["media"], n_simulazioni=base_b["n_simulazioni"],
        trade_per_simulazione_medio=float(np.mean(tps)), durata_media_barre=durata,
        quota_barre_vietate_segnale_non_valido=quota_segnale_non_valido,
        quota_barre_vietate_totale=float(maschera[ctx.ts >= da_ts].mean()),
        segnali_scartati_per_simulazione_medio=float(np.mean(base_b["segnali_non_validi_per_simulazione"])),
        simulazioni_vuote=base_b["simulazioni_vuote"], percentile_90=base_b["percentile_90"])
    out["percentile_caso"] = statistica.percentile_del_candidato(float(np.mean(r)), base_b["valori"])
    a_ok = out["baseline_a"].get("valutabile", False)
    b_ok = out["baseline_b"].get("valutabile", False)
    out["valutabile"] = bool(a_ok and b_ok)
    out["candidato"] = bool(out["baseline_a"].get("netta") and out["baseline_b"].get("netta")
                            and out["metriche"]["r_medio"] > 0)
    out["_r"] = r
    out["_trades"] = trades
    out["_base_b_valori"] = base_b["valori"]
    return out


def _curva(trades, par: Parametri):
    cap = par.capitale_iniziale
    curva = [(trades[0].ts_entrata if trades else 0, cap)]
    for t in trades:
        cap += t.pnl
        curva.append((t.ts_uscita, cap))
    return curva


def pubblico(ris: Dict) -> Dict:
    """Il risultato senza i campi interni (liste di trade e valori grezzi)."""
    return {k: v for k, v in ris.items() if not k.startswith("_")}
