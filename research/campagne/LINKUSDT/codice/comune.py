"""Strumenti comuni della campagna LINKUSDT: dati, parametri, esecuzione delle varianti e delle baseline.

Nessuna strategia qui: solo il modo, uguale per tutte le varianti, di
* caricare last e mark allineati (``dati.carica_serie_allineate``) e il funding;
* applicare il filtro dei mesi sotto la liquidita' minima (Fase 0 punto 3);
* costruire, da una variante, le tre strategie che il protocollo chiede: la
  variante, la baseline (a) (senza condizione d'ingresso e senza filtri, ma con
  il filtro dei mesi illiquidi, uguale per tutte) e la strategia casuale della
  baseline (b);
* contare i trade (``conta_trade``), eseguire il test, calcolare le baseline e
  le metriche del log.

Una variante e' una funzione ``prepara(candele, extra) -> Prep`` che calcola
gli indicatori SOLO con barre chiuse (il valore all'indice i usa le barre 0..i)
e restituisce tre funzioni dell'indice della barra chiusa:
* ``entra(i)``: la condizione d'ingresso dell'ipotesi (con i suoi filtri);
* ``segnale(i)``: il Segnale (direzione, stop, target) che la variante emette
  alla barra i SENZA la condizione d'ingresso, oppure None se non calcolabile;
* ``esci(i, ie)``: True se alla chiusura della barra i la posizione entrata
  all'apertura della barra ie va chiusa (uscita all'apertura della barra dopo).
Gli indici sono quelli della lista ``candele`` passata a ``prepara``.
"""
from __future__ import annotations

import json
import math
import pickle
import sys
from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))

from research.src import dati, motore, statistica  # noqa: E402
from research.src.motore import Candela, Parametri, Segnale  # noqa: E402

SIMBOLO = "LINKUSDT"
CARTELLA_DATI = RADICE_REPO / "research" / "data" / "insample" / SIMBOLO
INIZIO = date(2020, 1, 1)
FINE = date(2023, 12, 31)
_P = dati.periodi_campagna(INIZIO)
FINE_COSTRUZIONE_TS = int(_P["fine_costruzione_ts"])
INIZIO_VALIDAZIONE_TS = int(_P["inizio_validazione_ts"])
FINE_COSTRUZIONE = _P["fine_costruzione"]

LIQUIDITA_MINIMA = 20_000_000
TRADE_MINIMI_COSTRUZIONE = 70
TRADE_MINIMI_VALIDAZIONE = 30
N_SIMULAZIONI = 200
N_BOOT, SEME_BOOT = 2000, 0

# Parametri del motore: config/parametri.yaml (rischio, leva, commissione, margine
# di mantenimento, capitale) e scheda della moneta (slippage 0,02% per lato).
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
)

MS_TF = {tf: dati.durata_intervallo(tf) for tf in ("15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d")}


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------


def _cache(nome: str) -> Path:
    c = CARTELLA_DATI / "cache"
    c.mkdir(parents=True, exist_ok=True)
    return c / nome


def serie(tf: str, simbolo: str = SIMBOLO) -> Dict[str, object]:
    """Last e mark allineati dal 2020-01-01 al 2023-12-31 (carica_serie_allineate), con cache locale."""
    p = _cache(f"serie_{simbolo}_{tf}.pkl")
    if p.is_file():
        return pickle.loads(p.read_bytes())
    s = dati.carica_serie_allineate(simbolo, tf, INIZIO, FINE)
    p.write_bytes(pickle.dumps(s))
    return s


def candele_last(tf: str, simbolo: str) -> List[Candela]:
    """Solo il last (per BTCUSDT, riferimento di mercato: non ha mark scaricato)."""
    p = _cache(f"last_{simbolo}_{tf}.pkl")
    if p.is_file():
        return pickle.loads(p.read_bytes())
    c = dati.carica_candele(simbolo, tf, INIZIO, FINE)
    p.write_bytes(pickle.dumps(c))
    return c


def funding() -> List[tuple]:
    return dati.carica_funding(SIMBOLO, INIZIO, FINE)


def taker_buy_quote(tf: str) -> Dict[int, float]:
    """{ts: volume in USDT degli acquisti aggressivi (taker buy quote volume, colonna 10 dei klines)}."""
    p = _cache(f"taker_{tf}.pkl")
    if p.is_file():
        return pickle.loads(p.read_bytes())
    out: Dict[int, float] = {}
    for pz in sorted((CARTELLA_DATI / "klines" / tf).glob("*.zip")):
        for r in dati.righe_csv_da_zip(pz):
            ts = dati.normalizza_ts(r[0])
            if ts not in out and len(r) > 10 and r[10].strip():
                out[ts] = float(r[10])
    p.write_bytes(pickle.dumps(out))
    return out


def volume_giornaliero_usdt() -> Dict[int, float]:
    """Volume in USDT di ogni giorno del last (file 1d, volume_usdt_da_zip)."""
    out: Dict[int, float] = {}
    for pz in sorted((CARTELLA_DATI / "klines" / "1d").glob("*.zip")):
        for ts, v in dati.volume_usdt_da_zip(pz).items():
            out.setdefault(ts, v)
    return out


def _mese(ts: int) -> str:
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return f"{d.year:04d}-{d.month:02d}"


def mesi_illiquidi() -> List[str]:
    """Mesi con volume medio giornaliero in USDT sotto 20 milioni (Fase 0 punto 3)."""
    per_mese: Dict[str, List[float]] = {}
    for ts, v in volume_giornaliero_usdt().items():
        per_mese.setdefault(_mese(ts), []).append(v)
    return sorted(m for m, vs in per_mese.items() if sum(vs) / len(vs) < LIQUIDITA_MINIMA)


def liquida(candele: List[Candela]) -> List[bool]:
    """True per le barre il cui segnale puo' aprire una posizione (barra fuori dai mesi illiquidi)."""
    vietati = set(mesi_illiquidi())
    return [_mese(c.ts) not in vietati for c in candele]


def intervalli_da_maschera(ok: List[bool]) -> List[tuple]:
    """Intervalli (inizio incluso, fine esclusa) delle barre con ok False."""
    out: List[tuple] = []
    for i, v in enumerate(ok):
        if not v:
            if out and out[-1][1] == i:
                out[-1] = (out[-1][0], i + 1)
            else:
                out.append((i, i + 1))
    return out


def fino_a_costruzione(lista: List[Candela]) -> List[Candela]:
    return [c for c in lista if c.close_ts <= FINE_COSTRUZIONE_TS]


# ---------------------------------------------------------------------------
# Varianti e strategie
# ---------------------------------------------------------------------------


@dataclass
class Prep:
    entra: Callable[[int], bool]
    segnale: Callable[[int], Optional[Segnale]]
    esci: Callable[[int, int], bool]


def _indice_ts(candele: List[Candela]) -> Dict[int, int]:
    return {c.ts: i for i, c in enumerate(candele)}


def fabbrica(prep: Prep, candele: List[Candela], liq: List[bool], modo: str):
    """La funzione senza argomenti che crea la strategia ('variante' o 'a')."""
    idx = _indice_ts(candele)

    def crea():
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is not None:
                return "chiudi" if prep.esci(i, idx[pos.ts_entrata]) else None
            if not liq[i]:
                return None
            if modo == "variante" and not prep.entra(i):
                return None
            return prep.segnale(i)
        return strategia
    return crea


def fabbrica_casuale(prep: Prep, candele: List[Candela]):
    """crea_casuale(ingressi) per simula_baseline_casuale: segnale della variante agli ingressi, poi la sua uscita."""
    idx = _indice_ts(candele)

    def crea_casuale(ingressi):
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is not None:
                return "chiudi" if prep.esci(i, idx[pos.ts_entrata]) else None
            if i in ingressi:
                return prep.segnale(i)
            return None
        return strategia
    return crea_casuale


def fabbrica_segnale(prep: Prep):
    def crea_segnale():
        return lambda storia: prep.segnale(len(storia) - 1)
    return crea_segnale


# ---------------------------------------------------------------------------
# Metriche
# ---------------------------------------------------------------------------


def _anno(ts: int) -> int:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year


def metriche_trade(trades: List[motore.Trade], capitale: float = 1000.0) -> Dict[str, object]:
    tr = sorted(trades, key=lambda t: t.ts_uscita)
    r = [t.r for t in tr]
    n = len(r)
    vinti = sum(t.pnl for t in tr if t.pnl > 0)
    persi = -sum(t.pnl for t in tr if t.pnl < 0)
    pf = vinti / persi if persi > 0 else (math.inf if vinti > 0 else 0.0)
    cap, picco, dd = capitale, capitale, 0.0
    for t in tr:
        cap += t.pnl
        picco = max(picco, cap)
        dd = max(dd, (picco - cap) / picco if picco > 0 else 0.0)
    per_anno: Dict[int, List[float]] = {}
    for t in tr:
        per_anno.setdefault(_anno(t.ts_uscita), []).append(t.r)
    senza3 = sorted(r)[:-3] if n > 3 else []
    return {
        "trade": n,
        "profit_factor": pf,
        "r_medio": sum(r) / n if n else 0.0,
        "r_medio_per_anno": {a: sum(v) / len(v) for a, v in sorted(per_anno.items())},
        "trade_per_anno": {a: len(v) for a, v in sorted(per_anno.items())},
        "r_medio_senza_3_migliori": sum(senza3) / len(senza3) if senza3 else None,
        "drawdown_max": -dd,
        "rendimento_totale": (cap - capitale) / capitale,
        "win_rate": sum(1 for t in tr if t.pnl > 0) / n if n else 0.0,
        "ridotti": sum(1 for t in tr if t.ridotto),
        "violazioni_liquidazione": sum(1 for t in tr if t.violazione_liquidazione),
        "esiti": {e: sum(1 for t in tr if t.esito == e) for e in ("stop", "target", "segnale", "liquidazione", "fine_dati")},
        "durata_media_ore": (sum(t.ts_uscita - t.ts_entrata for t in tr) / n / 3_600_000) if n else 0.0,
    }


def buy_and_hold_per_anno(candele: List[Candela], da_ts: int, a_ts: int) -> Dict[int, Dict[str, float]]:
    per: Dict[int, List[Candela]] = {}
    for c in candele:
        if da_ts <= c.ts and c.close_ts <= a_ts:
            per.setdefault(_anno(c.ts), []).append(c)
    return {a: {"long": motore.buy_and_hold(cs, PARAMETRI, "long"), "short": motore.buy_and_hold(cs, PARAMETRI, "short")}
            for a, cs in sorted(per.items())}


def _riassunto_confronto(c: Dict[str, object]) -> Dict[str, object]:
    chiavi = ("t", "soglia", "netta", "valutabile", "differenza", "errore_standard", "errore_candidato",
              "errore_minimo", "n_blocchi", "p_value", "baseline_media", "baseline_errore_standard")
    return {k: c.get(k) for k in chiavi}


# ---------------------------------------------------------------------------
# Esecuzione completa di una variante (costruzione o validazione)
# ---------------------------------------------------------------------------


@dataclass
class Contesto:
    tf: str
    candele: List[Candela]
    mark: List[Candela]
    funding: List[tuple]
    liq: List[bool]
    extra: Dict[str, object]


def contesto(tf: str, periodo: str, extra_fn: Optional[Callable[[str], Dict[str, object]]] = None) -> Contesto:
    s = serie(tf)
    c, m = s["candele"], s["candele_mark"]
    f = funding()
    if periodo == "costruzione":
        n = sum(1 for x in c if x.close_ts <= FINE_COSTRUZIONE_TS)
        c, m = c[:n], m[:n]
        f = [(t, r) for t, r in f if t <= FINE_COSTRUZIONE_TS]
    elif periodo != "completo":
        raise ValueError(periodo)
    extra = extra_fn(tf) if extra_fn else {}
    return Contesto(tf, c, m, f, liq=liquida(c), extra=extra)


def conta(ctx: Contesto, prepara, parametri: Parametri = PARAMETRI) -> Dict[str, int]:
    prep = prepara(ctx.candele, ctx.extra)
    return motore.conta_trade(ctx.candele, fabbrica(prep, ctx.candele, ctx.liq, "variante"),
                              FINE_COSTRUZIONE_TS, parametri, candele_mark=ctx.mark, funding=ctx.funding)


def valuta(ctx: Contesto, prepara, periodo: str, parametri: Parametri = PARAMETRI,
           con_a: bool = True) -> Dict[str, object]:
    """Test di una variante con le baseline (a) e (b) sul periodo ('costruzione' o 'validazione').

    In costruzione ``ctx`` e' il contesto di costruzione; in validazione il contesto
    completo, e contano solo i trade entrati dopo la fine della costruzione (la (b)
    estrae gli ingressi solo fra le barre di validazione).
    """
    c, m, f = ctx.candele, ctx.mark, ctx.funding
    prep = prepara(c, ctx.extra)
    ris = motore.esegui(c, None, m, f, fabbrica(prep, c, ctx.liq, "variante")(), parametri)
    if periodo == "validazione":
        dentro = lambda t: t.ts_entrata > FINE_COSTRUZIONE_TS  # noqa: E731
        da_ts = INIZIO_VALIDAZIONE_TS
        a_ts = c[-1].close_ts
    else:
        dentro = lambda t: True  # noqa: E731
        da_ts, a_ts = c[0].ts, c[-1].close_ts
    trades = sorted([t for t in ris.trades if dentro(t)], key=lambda t: t.ts_uscita)
    out: Dict[str, object] = {"metriche": metriche_trade(trades), "buy_and_hold_per_anno": buy_and_hold_per_anno(c, da_ts, a_ts),
                              "n_segnali_non_validi": ris.n_segnali_non_validi, "n_buchi_dati": ris.n_buchi_dati,
                              "n_funding_in_buco": ris.n_funding_in_buco}
    n = len(trades)
    if n < 2:
        out["valutabile"] = False
        out["baseline_a"] = out["baseline_b"] = {"valutabile": False, "t": "-inf", "netta": False}
        return out
    r = [t.r for t in trades]
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    out["blocco"] = blocco

    # baseline (a)
    if con_a:
        ris_a = motore.esegui(c, None, m, f, fabbrica(prep, c, ctx.liq, "a")(), parametri)
        tr_a = sorted([t for t in ris_a.trades if dentro(t)], key=lambda t: t.ts_uscita)
        if len(tr_a) >= 2:
            blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in tr_a], [t.ts_uscita for t in tr_a])
            base_a = statistica.baseline_da_trade([t.r for t in tr_a], blocco_a, n=N_BOOT, seme=SEME_BOOT)
            ca = statistica.contro_baseline(r, blocco, base_a, n=N_BOOT, seme=SEME_BOOT)
            out["baseline_a"] = dict(_riassunto_confronto(ca), media=base_a["media"], n_trade=base_a["n_trade"],
                                     blocco_a=blocco_a, n_blocchi_a=base_a["n_blocchi"], valutabile_a=base_a["valutabile"])
        else:
            out["baseline_a"] = {"valutabile": False, "t": "-inf", "netta": False, "n_trade": len(tr_a)}

    # baseline (b)
    vietate = motore.barre_vietate_segnale_non_valido(c, fabbrica_segnale(prep), parametri)
    mask = [True] * len(c)
    for a, b in vietate:
        for k in range(a, b):
            mask[k] = False
    quota_vietate_segnale = 1 - sum(mask) / len(mask)
    for k, ok in enumerate(ctx.liq):
        if not ok:
            mask[k] = False
    if periodo == "validazione":
        for k, x in enumerate(c):
            if x.ts <= FINE_COSTRUZIONE_TS:
                mask[k] = False
    durata = motore.durata_media_barre(trades, MS_TF[ctx.tf])
    try:
        base_b = motore.simula_baseline_casuale(c, fabbrica_casuale(prep, c), n, durata, parametri,
                                                candele_mark=m, funding=f, barre_vietate=intervalli_da_maschera(mask),
                                                n_simulazioni=N_SIMULAZIONI, primo_seme=0)
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "t": "-inf", "netta": False, "errore": str(e)}
        out["valutabile"] = False
        return out
    cb = statistica.contro_baseline(r, blocco, base_b, n=N_BOOT, seme=SEME_BOOT)
    tps = base_b["trade_per_simulazione"]
    out["baseline_b"] = dict(_riassunto_confronto(cb), media=base_b["media"], n_simulazioni=base_b["n_simulazioni"],
                             trade_per_simulazione_medio=sum(tps) / len(tps), durata_media_barre=durata,
                             quota_barre_vietate_segnale_non_valido=quota_vietate_segnale,
                             segnali_scartati_per_simulazione_medio=sum(base_b["segnali_non_validi_per_simulazione"]) / len(base_b["segnali_non_validi_per_simulazione"]),
                             simulazioni_vuote=base_b["simulazioni_vuote"])
    out["percentile_caso"] = statistica.percentile_del_candidato(out["metriche"]["r_medio"], base_b["valori"])
    va = out.get("baseline_a", {}).get("valutabile", True)
    out["valutabile"] = bool(cb["valutabile"]) and bool(va)
    out["candidato"] = bool(out["valutabile"] and cb["netta"] and out.get("baseline_a", {}).get("netta", False)
                            and out["metriche"]["r_medio"] > 0)
    return out


def scrivi_json(percorso: Path, oggetto) -> None:
    from registro import _pulisci  # noqa: E402
    percorso.write_text(json.dumps(_pulisci(oggetto), ensure_ascii=False, indent=1))
