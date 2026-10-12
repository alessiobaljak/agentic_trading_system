"""Quadro comune delle varianti della campagna LTCUSDT.

Non contiene idee: solo il modo uguale per tutte le varianti di
* caricare le serie (``carica_serie_allineate``, last e mark sugli stessi ts);
* applicare il filtro dei mesi sotto la liquidita' minima (Fase 0, punto 3);
* costruire, da una ``Variante``, le quattro strategie che il protocollo vuole:
  la variante, la baseline (a) (senza condizione d'ingresso), la strategia
  casuale della (b) e il calcolo del solo segnale (per le barre vietate);
* contare i trade (``conta_trade``) e fare il test di Fase 2 con le baseline.

Regole di scrittura delle varianti (per non avere lookahead):
* ``prepara(candele)`` restituisce array numpy in cui il valore all'indice i
  usa SOLO le barre 0..i (finestre mobili che includono la barra i, gia' chiusa
  quando la strategia decide);
* ``entra(i, ind)`` e' la condizione d'ingresso dell'ipotesi alla chiusura della
  barra i; ``segnale(i, ind)`` e' il Segnale (direzione, stop, target) calcolato
  alla chiusura della barra i, SENZA la condizione d'ingresso, oppure None se
  non si puo' calcolare (riscaldamento); ``esci(i, ind, pos)`` dice se chiudere
  all'apertura della barra successiva.
"""
from __future__ import annotations

import json
import math
import pickle
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
import yaml

RADICE_REPO = Path(__file__).resolve().parents[4]
if str(RADICE_REPO) not in sys.path:
    sys.path.insert(0, str(RADICE_REPO))

from research.src import dati, motore, statistica  # noqa: E402
from research.src.motore import Parametri, Segnale  # noqa: E402

SIMBOLO = "LTCUSDT"
PRIMO_GIORNO = date(2020, 1, 1)
PERIODI = dati.periodi_campagna(PRIMO_GIORNO)
CARTELLA_CAMPAGNA = Path(__file__).resolve().parents[1]
CARTELLA_DATI = RADICE_REPO / "research" / "data" / "insample" / SIMBOLO
CARTELLA_CACHE = CARTELLA_DATI / "cache"
SLIPPAGE_PER_LATO = 0.0002  # scheda_moneta.md: fascia 0,0200% per lato
TRADE_MINIMI_COSTRUZIONE = 70
TRADE_MINIMI_VALIDAZIONE = 30


def _config() -> dict:
    return yaml.safe_load((RADICE_REPO / "research" / "config" / "parametri.yaml").read_text(encoding="utf-8"))


def parametri(moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0,
              riempimento_intrabarra: str = "stop_prima") -> Parametri:
    """Parametri del motore da parametri.yaml e dalla scheda (sezione 7)."""
    cfg = _config()
    regole = cfg["fatti"]["regole_dimensione_bot"]
    return Parametri(
        commissione_per_lato=float(cfg["fatti"]["commissione_taker_per_lato"]["valore"]),
        slippage_per_lato=SLIPPAGE_PER_LATO,
        rischio_per_trade=float(regole["rischio_per_trade"]),
        leva_max=float(regole["leva_max"]),
        modalita_margine=str(regole["modalita_margine_proposta"]),
        tasso_margine_mantenimento=float(regole["tasso_margine_mantenimento"]),
        margine_minimo_da_liquidazione=float(cfg["regole_esame"]["margine_minimo_da_liquidazione"]),
        capitale_iniziale=float(regole["capitale_iniziale"]),
        riempimento_intrabarra=riempimento_intrabarra,
        moltiplicatore_costi=moltiplicatore_costi,
        ritardo_barre=ritardo_barre,
    )


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------


@dataclass
class Serie:
    tf: str
    candele: List[motore.Candela]
    mark: List[motore.Candela]
    funding: List[Tuple[int, float]]
    n_tolte_last: int
    n_tolte_mark: int
    fine_ts: int


def _fine_periodo(periodo: str) -> date:
    if periodo == "costruzione":
        return PERIODI["fine_costruzione"]
    if periodo == "validazione":
        return PERIODI["fine_validazione"]
    raise ValueError(periodo)


def carica(tf: str, periodo: str = "costruzione", simbolo: str = SIMBOLO) -> Serie:
    """Last e mark allineati (carica_serie_allineate) e funding, dall'inizio alla fine del periodo.

    In validazione la serie va dall'inizio della costruzione alla fine della
    validazione (indicatori caldi); contano solo i trade entrati dopo la fine
    della costruzione (lo fa chi giudica, non il caricatore).
    """
    fine = _fine_periodo(periodo)
    CARTELLA_CACHE.mkdir(parents=True, exist_ok=True)
    nome = CARTELLA_CACHE / f"{simbolo}_{tf}_{periodo}.pkl"
    if nome.is_file():
        with open(nome, "rb") as f:
            return pickle.load(f)
    al = dati.carica_serie_allineate(simbolo, tf, PRIMO_GIORNO, fine)
    funding = dati.carica_funding(simbolo, PRIMO_GIORNO, fine) if simbolo == SIMBOLO else []
    serie = Serie(tf=tf, candele=al["candele"], mark=al["candele_mark"], funding=funding,
                  n_tolte_last=al["n_tolte_last"], n_tolte_mark=al["n_tolte_mark"],
                  fine_ts=dati.ms_da_data(fine) + dati.MS_GIORNO - 1)
    with open(nome, "wb") as f:
        pickle.dump(serie, f)
    return serie


def mesi_illiquidi() -> List[str]:
    """Mesi (AAAA-MM) con volume medio giornaliero in USDT sotto la soglia (Fase 0, punto 3).

    Il volume viene dalla colonna quote_volume dei file 1d del last, su tutti i
    giorni (volume_usdt_da_zip). Il risultato e' scritto anche in fase0_dati.md.
    """
    soglia = float(_config()["scelte_dati"]["liquidita_minima_usdt_giorno"])
    per_mese: Dict[str, List[float]] = {}
    for percorso in sorted((CARTELLA_DATI / "klines" / "1d").glob("*.zip")):
        for ts, v in dati.volume_usdt_da_zip(percorso).items():
            m = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m")
            per_mese.setdefault(m, []).append(v)
    return sorted(m for m, vs in per_mese.items() if sum(vs) / len(vs) < soglia)


def vietate_liquidita(candele: Sequence[motore.Candela], mesi: Sequence[str]) -> np.ndarray:
    """True alle barre il cui segnale cade in un mese sotto la liquidita' minima."""
    insieme = set(mesi)
    return np.array([datetime.fromtimestamp(c.ts / 1000, tz=timezone.utc).strftime("%Y-%m") in insieme
                     for c in candele], dtype=bool)


def intervalli(maschera: np.ndarray) -> List[Tuple[int, int]]:
    """Da una maschera booleana agli intervalli (inizio incluso, fine esclusa) dei True."""
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
# Varianti e strategie
# ---------------------------------------------------------------------------


class Variante:
    """Una regola completa: idea, timeframe, una direzione, ingresso, uscita, stop, target, filtri."""

    id: str = ""
    tf: str = "1h"
    direzione: str = "long"

    def prepara(self, candele: Sequence[motore.Candela]) -> Dict[str, np.ndarray]:
        raise NotImplementedError

    def entra(self, i: int, ind: Dict[str, np.ndarray]) -> bool:
        raise NotImplementedError

    def segnale(self, i: int, ind: Dict[str, np.ndarray]) -> Optional[Segnale]:
        raise NotImplementedError

    def esci(self, i: int, ind: Dict[str, np.ndarray], pos: motore.Posizione) -> bool:
        return False


def ms_barra(tf: str) -> int:
    return dati.durata_intervallo(tf)


class Contesto:
    """Indicatori e filtro di liquidita' per una serie: calcolati una volta, mai modificati."""

    def __init__(self, variante: Variante, candele: Sequence[motore.Candela], mesi: Sequence[str]):
        self.variante = variante
        self.candele = candele
        self.ind = variante.prepara(candele)
        self.ind["_ts"] = np.array([c.ts for c in candele], dtype=np.int64)
        self.ind["_close_ts"] = np.array([c.close_ts for c in candele], dtype=np.int64)
        self.ind["_ms_barra"] = ms_barra(variante.tf)
        self.vietato_liq = vietate_liquidita(candele, mesi)

    def strategia(self, modo: str, ingressi: frozenset = frozenset()):
        v, ind, viet = self.variante, self.ind, self.vietato_liq

        def strat(storia, pos):
            i = len(storia) - 1
            if pos is None:
                if modo == "variante":
                    if viet[i] or not v.entra(i, ind):
                        return None
                elif modo == "a":
                    if viet[i]:
                        return None
                elif modo == "b":
                    if i not in ingressi:
                        return None
                else:
                    raise ValueError(modo)
                return v.segnale(i, ind)
            return "chiudi" if v.esci(i, ind, pos) else None

        return strat

    def crea_segnale(self):
        v, ind = self.variante, self.ind

        def calcola(storia):
            return v.segnale(len(storia) - 1, ind)

        return calcola


def tempo_in_barre(i: int, ind: Dict[str, np.ndarray], pos: motore.Posizione) -> int:
    """Barre complete trascorse dall'ingresso (all'apertura) alla chiusura della barra i."""
    return int((int(ind["_close_ts"][i]) + 1 - pos.ts_entrata) // int(ind["_ms_barra"]))


# ---------------------------------------------------------------------------
# Stima dei trade e test di Fase 2
# ---------------------------------------------------------------------------


def stima(variante: Variante) -> Dict[str, int]:
    """conta_trade sulle regole esatte della variante, sui dati di costruzione (sezione 8)."""
    s = carica(variante.tf, "costruzione")
    ctx = Contesto(variante, s.candele, mesi_illiquidi())
    return motore.conta_trade(s.candele, lambda: ctx.strategia("variante"), PERIODI["fine_costruzione_ts"],
                              parametri(), candele_mark=s.mark, funding=s.funding)


def _r_ordinati(trades) -> List[float]:
    return [t.r for t in sorted(trades, key=lambda t: t.ts_uscita)]


def _anno(ts: int) -> int:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year


def _r_per_anno(trades) -> Dict[str, float]:
    per: Dict[int, List[float]] = {}
    for t in trades:
        per.setdefault(_anno(t.ts_uscita), []).append(t.r)
    return {str(a): round(float(np.mean(v)), 4) for a, v in sorted(per.items())}


def _n_per_anno(trades) -> Dict[str, int]:
    per: Dict[int, int] = {}
    for t in trades:
        per[_anno(t.ts_uscita)] = per.get(_anno(t.ts_uscita), 0) + 1
    return {str(a): n for a, n in sorted(per.items())}


def _bh_per_anno(candele, p: Parametri, da_ts: int = 0) -> Dict[str, Dict[str, float]]:
    per: Dict[int, list] = {}
    for c in candele:
        if c.ts >= da_ts:
            per.setdefault(_anno(c.ts), []).append(c)
    return {str(a): {"long": round(motore.buy_and_hold(cs, p, "long"), 4),
                     "short": round(motore.buy_and_hold(cs, p, "short"), 4)} for a, cs in sorted(per.items())}


def _pulisci(d: Dict[str, object]) -> Dict[str, object]:
    out = {}
    for k, v in d.items():
        if k == "valori":
            continue
        if isinstance(v, (np.floating, float)):
            v = float(v)
            out[k] = None if not math.isfinite(v) else round(v, 6)
        elif isinstance(v, (np.integer,)):
            out[k] = int(v)
        elif isinstance(v, (list, tuple)) and v and isinstance(v[0], (int, np.integer)) and len(v) > 20:
            out[k + "_media"] = round(float(np.mean(v)), 3)
        else:
            out[k] = v
    return out


def giudica(variante: Variante, moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0,
            riempimento_intrabarra: str = "stop_prima", periodo: str = "costruzione",
            salva_trade: Optional[str] = None) -> Dict[str, object]:
    """Fase 2 (o verifica): la variante contro la (a) e la (b), con le metriche della sezione 6.

    In costruzione la serie finisce alla fine della costruzione. In validazione
    la serie va dall'inizio della costruzione alla fine della validazione: contano
    solo i trade entrati dopo la fine della costruzione, e le barre di costruzione
    sono vietate agli ingressi della (a) e della (b).
    """
    p = parametri(moltiplicatore_costi, ritardo_barre, riempimento_intrabarra)
    s = carica(variante.tf, periodo)
    mesi = mesi_illiquidi()
    ctx = Contesto(variante, s.candele, mesi)
    da_ts = PERIODI["inizio_validazione_ts"] if periodo == "validazione" else 0
    n = len(s.candele)
    primo_valido = int(np.searchsorted(ctx.ind["_ts"], da_ts)) if da_ts else 0

    def dentro(trades):
        return [t for t in trades if t.ts_entrata >= da_ts]

    ris = motore.esegui(s.candele, None, s.mark, s.funding, ctx.strategia("variante"), p)
    trades = dentro(ris.trades)
    out: Dict[str, object] = {"periodo": periodo, "moltiplicatore_costi": moltiplicatore_costi,
                              "ritardo_barre": ritardo_barre, "riempimento_intrabarra": riempimento_intrabarra}
    if salva_trade:
        (CARTELLA_DATI / "trade").mkdir(parents=True, exist_ok=True)
        with open(CARTELLA_DATI / "trade" / f"{salva_trade}.pkl", "wb") as f:
            pickle.dump({"trades": trades, "tf": variante.tf}, f)
    r = _r_ordinati(trades)
    nt = len(trades)
    pnl = [t.pnl for t in trades]
    vinti = sum(x for x in pnl if x > 0)
    persi = -sum(x for x in pnl if x < 0)
    curva = [(0, p.capitale_iniziale)]
    cap = p.capitale_iniziale
    for t in sorted(trades, key=lambda t: t.ts_uscita):
        cap += t.pnl
        curva.append((t.ts_uscita, cap))
    out["metriche"] = {
        "trade": nt,
        "profit_factor": round(vinti / persi, 4) if persi > 0 else None,
        "r_medio": round(float(np.mean(r)), 4) if nt else None,
        "r_medio_per_anno": _r_per_anno(trades),
        "trade_per_anno": _n_per_anno(trades),
        "r_medio_senza_3_migliori": round(float(np.mean(sorted(r)[:-3])), 4) if nt > 3 else None,
        "drawdown_max": round(-motore.drawdown_massimo(curva), 4),
        "rendimento_totale": round((cap - p.capitale_iniziale) / p.capitale_iniziale, 4),
        "win_rate": round(sum(1 for x in pnl if x > 0) / nt, 4) if nt else None,
        "ridotti_tetto_leva": sum(1 for t in trades if t.ridotto),
        "violazioni_liquidazione": sum(1 for t in trades if t.violazione_liquidazione),
        "esiti": {e: sum(1 for t in trades if t.esito == e) for e in ("stop", "target", "segnale", "liquidazione", "fine_dati")},
        "segnali_non_validi": ris.n_segnali_non_validi,
        "buchi_dati": ris.n_buchi_dati,
        "funding_in_buco": ris.n_funding_in_buco,
        "costo_medio_r": round(float(np.mean([(t.commissioni + t.slippage_costo) / t.rischio_iniziale for t in trades])), 4) if nt else None,
        "funding_medio_r": round(float(np.mean([t.funding_pagato / t.rischio_iniziale for t in trades])), 4) if nt else None,
    }
    out["buy_and_hold_per_anno"] = _bh_per_anno(s.candele, p, da_ts)
    if nt < 2:
        out["blocco"] = None
        out["baseline_a"] = {"valutabile": False, "motivo": "meno di 2 trade"}
        out["baseline_b"] = {"valutabile": False, "motivo": "meno di 2 trade"}
        out["percentile_caso"] = None
        return out
    ordinati = sorted(trades, key=lambda t: t.ts_uscita)
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in ordinati], [t.ts_uscita for t in ordinati])
    out["blocco"] = blocco

    # baseline (a): senza condizione d'ingresso, a ogni barra libera (filtro di liquidita' compreso)
    ctx_a = Contesto(variante, s.candele, mesi)
    if da_ts:
        ctx_a.vietato_liq = ctx_a.vietato_liq.copy()
        ctx_a.vietato_liq[:primo_valido] = True
    ris_a = motore.esegui(s.candele, None, s.mark, s.funding, ctx_a.strategia("a"), p)
    tr_a = sorted(dentro(ris_a.trades), key=lambda t: t.ts_uscita)
    if len(tr_a) >= 2:
        blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in tr_a], [t.ts_uscita for t in tr_a])
        base_a = statistica.baseline_da_trade([t.r for t in tr_a], blocco_a)
        cmp_a = statistica.contro_baseline(r, blocco, base_a)
        out["baseline_a"] = dict(_pulisci(cmp_a), media=round(base_a["media"], 6), n_trade=base_a["n_trade"],
                                 blocco_a=blocco_a, n_blocchi_a=base_a["n_blocchi"],
                                 valutabile=bool(cmp_a["valutabile"]))
    else:
        out["baseline_a"] = {"valutabile": False, "motivo": "la (a) ha meno di 2 trade"}

    # baseline (b): entrate casuali con la stessa uscita
    durata = motore.durata_media_barre(trades, ms_barra(variante.tf))
    vietate = motore.barre_vietate_segnale_non_valido(s.candele, ctx.crea_segnale, p)
    viet_liq = intervalli(ctx.vietato_liq)
    extra = [(0, primo_valido)] if primo_valido > 0 else []
    quota_vietate = sum(b - a for a, b in vietate) / n
    try:
        base_b = motore.simula_baseline_casuale(
            s.candele, lambda ingressi: ctx.strategia("b", ingressi), nt, durata, p,
            candele_mark=s.mark, funding=s.funding, barre_vietate=vietate + viet_liq + extra,
            n_simulazioni=200, primo_seme=0)
        cmp_b = statistica.contro_baseline(r, blocco, base_b)
        out["baseline_b"] = dict(_pulisci(cmp_b), media=round(base_b["media"], 6),
                                 n_simulazioni=base_b["n_simulazioni"],
                                 trade_per_simulazione_medio=round(float(np.mean(base_b["trade_per_simulazione"])), 2),
                                 segnali_scartati_per_simulazione_medio=round(float(np.mean(base_b["segnali_non_validi_per_simulazione"])), 3),
                                 simulazioni_vuote=base_b["simulazioni_vuote"],
                                 quota_barre_vietate_segnale_non_valido=round(quota_vietate, 4),
                                 durata_media_barre=durata, percentile_90=round(base_b["percentile_90"], 4),
                                 valutabile=bool(cmp_b["valutabile"]))
        out["percentile_caso"] = round(statistica.percentile_del_candidato(float(np.mean(r)), base_b["valori"]), 2)
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "motivo": str(e)}
        out["percentile_caso"] = None
    return out


def esito_fase2(ris: Dict[str, object]) -> Dict[str, object]:
    a, b = ris["baseline_a"], ris["baseline_b"]
    valutabile = bool(a.get("valutabile")) and bool(b.get("valutabile"))
    r_medio = ris["metriche"]["r_medio"]
    netta_a, netta_b = bool(a.get("netta")), bool(b.get("netta"))
    return {"valutabile": valutabile, "netta_a": netta_a, "netta_b": netta_b,
            "r_medio_positivo": r_medio is not None and r_medio > 0,
            "candidato": valutabile and netta_a and netta_b and r_medio is not None and r_medio > 0,
            "t_b": b.get("t") if valutabile else None}


def scrivi_json(percorso: Path, oggetto) -> None:
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.write_text(json.dumps(oggetto, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
