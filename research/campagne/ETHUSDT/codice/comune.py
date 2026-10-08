"""Strumenti comuni della campagna ETHUSDT (protocollo 4.4, Passo 3).

Qui ci sono SOLO cose uguali per tutte le varianti, scritte prima del primo test:
* i parametri del motore, letti da research/config/parametri.yaml e dalla scheda
  della moneta (sezione 7, «Parametri»);
* il caricamento delle serie (last per segnali e stop, mark per le liquidazioni,
  funding), con l'intersezione delle barre di last e mark decisa in Fase 0;
* il filtro dei mesi sotto la liquidita' minima (Fase 0, punto 3);
* la forma comune delle varianti (classe ``Variante``) e le quattro fabbriche che
  il protocollo chiede: la strategia della variante, la baseline (a) (senza la
  condizione d'ingresso), la strategia casuale della (b) e il solo calcolo del
  segnale per le barre vietate;
* ``valuta``: il giro di Fase 2 di una variante sul periodo di costruzione, con le
  baseline (a), (b) e (c) e i numeri del log (sezione 6).

Nessuna strategia sta qui: le idee sono nei file ``idea_*.py``.
"""

from __future__ import annotations

import math
import re
import sys
from dataclasses import replace
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import yaml

RADICE_REPO = Path(__file__).resolve().parents[4]
if str(RADICE_REPO) not in sys.path:
    sys.path.insert(0, str(RADICE_REPO))

from research.src import dati, motore, statistica  # noqa: E402
from research.src.motore import Candela, Parametri, Segnale  # noqa: E402

SIMBOLO = "ETHUSDT"
RIFERIMENTO = "BTCUSDT"
RICERCA = RADICE_REPO / "research"
CARTELLA = RICERCA / "campagne" / SIMBOLO
LAVORO = RICERCA / "data" / "insample" / SIMBOLO / "lavoro"

PRIMO_GIORNO = date(2020, 1, 1)
PERIODI = dati.periodi_campagna(PRIMO_GIORNO)
FINE_COSTRUZIONE_TS: int = PERIODI["fine_costruzione_ts"]
INIZIO_VALIDAZIONE_TS: int = PERIODI["inizio_validazione_ts"]

#: Mesi con volume medio giornaliero sotto la liquidita' minima (Fase 0, punto 3,
#: misurati in fase0_dati.md): nessun segnale da barre di questi mesi apre posizioni.
MESI_ESCLUSI: frozenset = frozenset()

N_SIMULAZIONI = 200
BOOTSTRAP_N = 2000
BOOTSTRAP_SEME = 0
TRADE_MINIMI_COSTRUZIONE = 70


# ---------------------------------------------------------------------------
# Parametri
# ---------------------------------------------------------------------------


def _slippage_scheda() -> float:
    testo = (CARTELLA / "scheda_moneta.md").read_text(encoding="utf-8")
    m = re.search(r"Fascia di slippage[^|]*\|\s*([0-9.]+)%", testo)
    if not m:
        raise ValueError("fascia di slippage non trovata nella scheda")
    return float(m.group(1)) / 100.0


def parametri(moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0,
              riempimento_intrabarra: str = "stop_prima") -> Parametri:
    cfg = yaml.safe_load((RICERCA / "config" / "parametri.yaml").read_text(encoding="utf-8"))
    if cfg.get("stato") != "congelato":
        raise ValueError("parametri.yaml non e' congelato")
    fatti = cfg["fatti"]
    reg = fatti["regole_dimensione_bot"]
    return Parametri(
        commissione_per_lato=float(fatti["commissione_taker_per_lato"]["valore"]),
        slippage_per_lato=_slippage_scheda(),
        rischio_per_trade=float(reg["rischio_per_trade"]),
        leva_max=float(reg["leva_max"]),
        modalita_margine=str(reg["modalita_margine_proposta"]),
        tasso_margine_mantenimento=float(reg["tasso_margine_mantenimento"]),
        margine_minimo_da_liquidazione=float(cfg["regole_esame"]["margine_minimo_da_liquidazione"]),
        capitale_iniziale=float(reg["capitale_iniziale"]),
        riempimento_intrabarra=riempimento_intrabarra,
        moltiplicatore_costi=moltiplicatore_costi,
        ritardo_barre=ritardo_barre,
    )


# ---------------------------------------------------------------------------
# Serie
# ---------------------------------------------------------------------------


class Serie:
    """Le serie allineate di un timeframe: last (segnali e stop), mark, funding, BTC."""

    def __init__(self, tf: str, last: List[Candela], mark: List[Candela], funding: List[Tuple[int, float]],
                 btc: Dict[int, Candela], tolte_last: int, tolte_mark: int) -> None:
        self.tf = tf
        self.ms = dati.durata_intervallo(tf)
        self.last = last
        self.mark = mark
        self.funding = funding
        self.btc = btc
        self.tolte_last = tolte_last
        self.tolte_mark = tolte_mark


_CACHE: Dict[Tuple[str, str], Serie] = {}


def carica(tf: str, periodo: str = "costruzione") -> Serie:
    """Serie del timeframe sul periodo: 'costruzione' (fino a fine costruzione) o 'tutto' (fino al 2023-12-31).

    Le barre si tengono solo se ci sono sia nel last sia nel mark (Fase 0): il motore
    vuole le serie allineate barra per barra. Le barre tolte si contano.
    """
    chiave = (tf, periodo)
    if chiave in _CACHE:
        return _CACHE[chiave]
    if periodo == "costruzione":
        fine = PERIODI["fine_costruzione"]
    elif periodo == "tutto":
        fine = PERIODI["fine_validazione"]
    else:
        raise ValueError(periodo)
    last = dati.carica_candele(SIMBOLO, tf, PRIMO_GIORNO, fine)
    mark = dati.carica_candele(SIMBOLO, tf, PRIMO_GIORNO, fine, tipo="markPriceKlines")
    comuni = {c.ts for c in last} & {c.ts for c in mark}
    last2 = [c for c in last if c.ts in comuni]
    mark2 = [c for c in mark if c.ts in comuni]
    funding = dati.carica_funding(SIMBOLO, PRIMO_GIORNO, fine)
    btc = {c.ts: c for c in dati.carica_candele(RIFERIMENTO, tf, PRIMO_GIORNO, fine)}
    serie = Serie(tf, last2, mark2, funding, btc, len(last) - len(last2), len(mark) - len(mark2))
    _CACHE[chiave] = serie
    return serie


def mese_di(ts: int) -> Tuple[int, int]:
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return d.year, d.month


def anno_di(ts: int) -> int:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year


def barre_mesi_esclusi(candele: Sequence[Candela]) -> List[Tuple[int, int]]:
    """Intervalli (inizio incluso, fine esclusa) delle barre dei mesi esclusi in Fase 0."""
    vietate: List[Tuple[int, int]] = []
    for i, c in enumerate(candele):
        if mese_di(c.ts) in MESI_ESCLUSI:
            if vietate and vietate[-1][1] == i:
                vietate[-1] = (vietate[-1][0], i + 1)
            else:
                vietate.append((i, i + 1))
    return vietate


# ---------------------------------------------------------------------------
# La forma comune delle varianti
# ---------------------------------------------------------------------------


class Variante:
    """Una variante: una regola completa, una direzione.

    Una sottoclasse definisce:
    * ``aggiorna(barra, i)``: aggiorna gli indicatori con la barra chiusa ``i``;
    * ``pronta()``: True quando TUTTI gli indicatori (condizione, filtri, stop e
      target) sono caldi: prima la variante non puo' entrare;
    * ``calcola_segnale(storia)``: direzione, stop e target alla barra corrente,
      SENZA la condizione d'ingresso (e' lo stesso calcolo per la (b));
    * ``condizione(storia)``: la condizione d'ingresso dell'ipotesi con i suoi filtri;
    * ``esci(storia, pos)``: True se l'uscita della variante chiede "chiudi" alla
      chiusura della barra corrente (oltre a stop e target, che fa il motore).

    ``serie`` da' accesso al riferimento BTC (solo barre con ts <= barra corrente)
    e al funding (solo settlement gia' avvenuti). ``passo`` garantisce che ogni
    barra si legga una volta sola, nell'ordine.
    """

    direzione = "long"

    def __init__(self, serie: Serie, **p) -> None:
        self.serie = serie
        self.p = p
        self.n_visti = 0
        self.ultima: Optional[Candela] = None

    # da ridefinire
    def aggiorna(self, barra: Candela, i: int) -> None:  # pragma: no cover
        raise NotImplementedError

    def pronta(self) -> bool:  # pragma: no cover
        raise NotImplementedError

    def calcola_segnale(self, storia) -> Optional[Segnale]:  # pragma: no cover
        raise NotImplementedError

    def condizione(self, storia) -> bool:  # pragma: no cover
        raise NotImplementedError

    def esci(self, storia, pos) -> bool:
        return False

    # comune
    def passo(self, storia) -> None:
        n = len(storia)
        while self.n_visti < n:
            barra = storia[self.n_visti]
            self.aggiorna(barra, self.n_visti)
            self.ultima = barra
            self.n_visti += 1

    def segnale(self, storia) -> Optional[Segnale]:
        if not self.pronta():
            return None
        return self.calcola_segnale(storia)

    def barre_in_posizione(self, storia, pos) -> int:
        """Barre chiuse dall'ingresso (la barra d'ingresso conta 1)."""
        return int((storia[-1].ts - pos.ts_entrata) // self.serie.ms) + 1


def fabbrica(V, kw: dict, serie: Serie) -> Callable[[], Callable]:
    """La strategia della variante (per conta_trade, test e verifiche)."""
    def crea():
        v = V(serie, **kw)

        def strategia(storia, pos):
            v.passo(storia)
            if pos is not None:
                return "chiudi" if v.esci(storia, pos) else None
            if mese_di(storia[-1].ts) in MESI_ESCLUSI:
                return None
            if not v.pronta() or not v.condizione(storia):
                return None
            return v.calcola_segnale(storia)
        return strategia
    return crea


def fabbrica_a(V, kw: dict, serie: Serie) -> Callable[[], Callable]:
    """Baseline (a): la variante senza condizione d'ingresso e senza filtri (sezione 8).

    Entra a ogni barra in cui e' libera, dalla prima barra in cui la variante puo'
    entrare (indicatori caldi), con la stessa direzione, uscita, stop e target. Il
    filtro dei mesi esclusi resta (Fase 0, punto 3: uguale per conta, test e (a)).
    """
    def crea():
        v = V(serie, **kw)

        def strategia(storia, pos):
            v.passo(storia)
            if pos is not None:
                return "chiudi" if v.esci(storia, pos) else None
            if mese_di(storia[-1].ts) in MESI_ESCLUSI:
                return None
            return v.segnale(storia)
        return strategia
    return crea


def fabbrica_casuale(V, kw: dict, serie: Serie) -> Callable[[frozenset], Callable]:
    """Strategia casuale della (b): agli ingressi il segnale della variante, poi la sua uscita."""
    def crea_casuale(ingressi: frozenset):
        v = V(serie, **kw)

        def strategia(storia, pos):
            v.passo(storia)
            if pos is not None:
                return "chiudi" if v.esci(storia, pos) else None
            if (len(storia) - 1) in ingressi:
                return v.segnale(storia)
            return None
        return strategia
    return crea_casuale


def fabbrica_segnale(V, kw: dict, serie: Serie) -> Callable[[], Callable]:
    """Solo il calcolo del segnale (stop e target) senza condizione, per le barre vietate."""
    def crea_segnale():
        v = V(serie, **kw)

        def segnale_alla_barra(storia):
            v.passo(storia)
            return v.segnale(storia)
        return segnale_alla_barra
    return crea_segnale


# ---------------------------------------------------------------------------
# Conteggio e valutazione
# ---------------------------------------------------------------------------


def conta(V, kw: dict, tf: str) -> Dict[str, int]:
    """``conta_trade`` del protocollo sulle regole esatte della variante (solo costruzione)."""
    s = carica(tf, "costruzione")
    return motore.conta_trade(s.last, fabbrica(V, kw, s), FINE_COSTRUZIONE_TS, parametri(),
                              None, s.mark, s.funding)


def _r_ordinati(trades) -> List[float]:
    return [t.r for t in sorted(trades, key=lambda t: t.ts_uscita)]


def _blocco(trades) -> int:
    return statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])


def _metriche(ris, trades) -> Dict[str, object]:
    m = ris.metriche() if ris is not None else None
    r = _r_ordinati(trades)
    per_anno: Dict[str, List[float]] = {}
    for t in trades:
        per_anno.setdefault(str(anno_di(t.ts_uscita)), []).append(t.r)
    migliori = sorted(r)[:-3] if len(r) > 3 else []
    pf = statistica.profit_factor([t.pnl for t in trades])
    curva = [ris.capitale_iniziale] if ris is not None else [1000.0]
    for t in sorted(trades, key=lambda t: t.ts_uscita):
        curva.append(curva[-1] + t.pnl)
    out = {
        "profit_factor": pf,
        "trade": len(trades),
        "r_medio": sum(r) / len(r) if r else 0.0,
        "r_medio_per_anno": {a: sum(v) / len(v) for a, v in sorted(per_anno.items())},
        "trade_per_anno": {a: len(v) for a, v in sorted(per_anno.items())},
        "r_medio_senza_3_migliori": sum(migliori) / len(migliori) if migliori else None,
        "drawdown_max": -statistica.drawdown_max_da_curva(curva),
        "win_rate": statistica.win_rate([t.pnl for t in trades]),
        "rendimento_totale": (curva[-1] - curva[0]) / curva[0],
    }
    if m is not None:
        out.update({
            "rendimento_per_anno": {str(k): v for k, v in m["rendimento_per_anno"].items()},
            "n_ridotti": m["n_ridotti"],
            "n_violazioni_liquidazione": m["n_violazioni_liquidazione"],
            "esiti": m["esiti"],
            "costi_totali": m["costi_totali"],
            "funding_totale": m["funding_totale"],
            "n_buchi_dati": m["n_buchi_dati"],
            "n_segnali_non_validi": m["n_segnali_non_validi"],
        })
    return out


def _sintesi_confronto(c: Dict[str, object]) -> Dict[str, object]:
    chiavi = ("differenza", "errore_standard", "errore_candidato", "errore_minimo", "t", "soglia", "netta",
              "valutabile", "p_value", "n_blocchi", "gradi_liberta", "baseline_media", "baseline_errore_standard")
    return {k: c.get(k) for k in chiavi}


def buy_and_hold_per_anno(candele: Sequence[Candela], p: Parametri) -> Dict[str, Dict[str, float]]:
    per_anno: Dict[int, List[Candela]] = {}
    for c in candele:
        per_anno.setdefault(anno_di(c.ts), []).append(c)
    return {str(a): {"long": motore.buy_and_hold(cs, p, "long"), "short": motore.buy_and_hold(cs, p, "short")}
            for a, cs in sorted(per_anno.items())}


def baseline_b(V, kw: dict, s: Serie, trades, p: Parametri, vietate_extra=()) -> Dict[str, object]:
    """La (b) con simula_baseline_casuale; ritorna il dizionario o {'errore': ...} se non costruibile."""
    vietate_segnale = motore.barre_vietate_segnale_non_valido(s.last, fabbrica_segnale(V, kw, s), p)
    quota = sum(b - a for a, b in vietate_segnale) / len(s.last)
    vietate = list(vietate_segnale) + barre_mesi_esclusi(s.last) + list(vietate_extra)
    durata = motore.durata_media_barre(trades, s.ms)
    try:
        base = motore.simula_baseline_casuale(s.last, fabbrica_casuale(V, kw, s), len(trades), durata, p,
                                              None, s.mark, s.funding, vietate, N_SIMULAZIONI, 0)
    except ValueError as e:
        return {"errore": str(e), "durata_media_barre": durata, "quota_barre_vietate_segnale_non_valido": quota}
    base["durata_media_barre"] = durata
    base["quota_barre_vietate_segnale_non_valido"] = quota
    return base


def valuta(V, kw: dict, tf: str, p: Optional[Parametri] = None, con_a: bool = True) -> Dict[str, object]:
    """Fase 2 sul periodo di costruzione: candidato, (a), (b), (c) e i numeri del log.

    ``p`` serve alle verifiche (costi doppi, ritardo, regola intra-barra opposta):
    candidato e (b) girano con gli stessi parametri.
    """
    p = p or parametri()
    s = carica(tf, "costruzione")
    ris = motore.esegui(s.last, None, s.mark, s.funding, fabbrica(V, kw, s)(), p)
    trades = sorted(ris.trades, key=lambda t: t.ts_uscita)
    out: Dict[str, object] = {"metriche": _metriche(ris, trades)}
    if not trades:
        out["esito"] = "nessun trade"
        return out
    r = _r_ordinati(trades)
    blocco = _blocco(trades)
    out["blocco"] = blocco

    if con_a:
        ris_a = motore.esegui(s.last, None, s.mark, s.funding, fabbrica_a(V, kw, s)(), p)
        trades_a = sorted(ris_a.trades, key=lambda t: t.ts_uscita)
        blocco_a = _blocco(trades_a)
        base_a = statistica.baseline_da_trade(_r_ordinati(trades_a), blocco_a, BOOTSTRAP_N, BOOTSTRAP_SEME)
        cmp_a = statistica.contro_baseline(r, blocco, base_a, BOOTSTRAP_N, BOOTSTRAP_SEME)
        out["baseline_a"] = dict(_sintesi_confronto(cmp_a), media=base_a["media"], n_trade=base_a["n_trade"],
                                 blocco=blocco_a, n_blocchi_baseline=base_a["n_blocchi"],
                                 baseline_valutabile=base_a["valutabile"],
                                 deviazione_standard=base_a["deviazione_standard"])

    base_b = baseline_b(V, kw, s, trades, p)
    if "errore" in base_b:
        out["baseline_b"] = {"valutabile": False, "netta": False, "t": -math.inf, "errore": base_b["errore"],
                             "durata_media_barre": base_b["durata_media_barre"],
                             "quota_barre_vietate_segnale_non_valido": base_b["quota_barre_vietate_segnale_non_valido"]}
        out["percentile_caso"] = None
    else:
        cmp_b = statistica.contro_baseline(r, blocco, base_b, BOOTSTRAP_N, BOOTSTRAP_SEME)
        tps = base_b["trade_per_simulazione"]
        out["baseline_b"] = dict(
            _sintesi_confronto(cmp_b), media=base_b["media"], n_simulazioni=base_b["n_simulazioni"],
            trade_per_simulazione_medio=sum(tps) / len(tps),
            simulazioni_vuote=base_b["simulazioni_vuote"],
            segnali_scartati_per_simulazione_medio=sum(base_b["segnali_non_validi_per_simulazione"]) / N_SIMULAZIONI,
            segnali_senza_barra_per_simulazione_medio=sum(base_b["segnali_senza_barra_per_simulazione"]) / N_SIMULAZIONI,
            durata_media_barre=base_b["durata_media_barre"],
            quota_barre_vietate_segnale_non_valido=base_b["quota_barre_vietate_segnale_non_valido"],
            percentile_90=base_b["percentile_90"],
        )
        out["percentile_caso"] = statistica.percentile_del_candidato(sum(r) / len(r), base_b["valori"])
    out["buy_and_hold_per_anno"] = buy_and_hold_per_anno(s.last, p)
    a_ok = out.get("baseline_a", {}).get("netta", False)
    b_ok = out["baseline_b"].get("netta", False)
    valutabile = out["baseline_b"].get("valutabile", False) and (not con_a or out["baseline_a"].get("valutabile", False))
    out["valutabile"] = bool(valutabile)
    out["candidato"] = bool(a_ok and b_ok and out["metriche"]["r_medio"] > 0)
    out["barre"] = len(s.last)
    out["barre_tolte_intersezione"] = {"last": s.tolte_last, "mark": s.tolte_mark}
    return out
