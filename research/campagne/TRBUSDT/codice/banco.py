"""Banco di prova della campagna TRBUSDT: dati, filtro di liquidita', varianti, baseline e log.

Tutto quello che serve a una variante passa da qui, cosi' conteggio, test, baseline (a)
e (b) usano le STESSE serie, gli stessi parametri e lo stesso funding (sezione 8).

Una variante e' un oggetto ``Variante`` con:
* ``timeframe`` e ``direzione``;
* ``prepara(candele)``: calcola sugli indici della lista le grandezze causali che servono
  (solo barre fino alla i per il valore alla i) e ritorna un contesto;
* ``condizione(ctx, i)``: la condizione d'ingresso dell'ipotesi alla chiusura della barra i;
* ``segnale(ctx, i)``: il Segnale (direzione, stop, target) che la variante emetterebbe
  alla chiusura della barra i SENZA la condizione d'ingresso, o None (riscaldamento);
* ``uscita(ctx, i, pos)``: "chiudi" per un'uscita decisa alla chiusura della barra i, o None.

Il filtro di liquidita' della Fase 0 (mesi sotto 20 milioni di USDT al giorno) vieta gli
ingressi su segnali di barre di quei mesi: per la variante, per conta_trade, per la (a) e
nelle barre vietate della (b).
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
import yaml

from research.src import dati, motore, statistica
from research.src.motore import Candela, Parametri, Segnale

from research.campagne.TRBUSDT.codice import registro
from research.campagne.TRBUSDT.codice.periodi import periodi

SIMBOLO = "TRBUSDT"
RADICE = dati.RADICE_DEFAULT
CARTELLA = Path(__file__).resolve().parent.parent
PERIODI = periodi()
FINE_COSTRUZIONE_TS = PERIODI["fine_costruzione_ts"]
SLIPPAGE = 0.0002  # scheda_moneta.md: fascia 0,0200% per lato

with open(RADICE / "config" / "parametri.yaml", encoding="utf-8") as _f:
    CONFIG = yaml.safe_load(_f)
_REG = CONFIG["fatti"]["regole_dimensione_bot"]
_ESAME = CONFIG["regole_esame"]
TRADE_MINIMI = _ESAME["trade_minimi"]
N_SIM = int(_ESAME["simulazioni_baseline_casuale"])
N_BOOT = int(_ESAME["bootstrap"]["ricampionamenti"])
SEME_BOOT = int(_ESAME["bootstrap"]["seme"])
SOGLIA_LIQUIDITA = float(CONFIG["scelte_dati"]["liquidita_minima_usdt_giorno"])


def parametri(moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0, intrabarra: str = "stop_prima") -> Parametri:
    return Parametri(
        commissione_per_lato=float(CONFIG["fatti"]["commissione_taker_per_lato"]["valore"]),
        slippage_per_lato=SLIPPAGE,
        rischio_per_trade=float(_REG["rischio_per_trade"]),
        leva_max=float(_REG["leva_max"]),
        modalita_margine=_REG["modalita_margine_proposta"],
        tasso_margine_mantenimento=float(_REG["tasso_margine_mantenimento"]),
        margine_minimo_da_liquidazione=float(_ESAME["margine_minimo_da_liquidazione"]),
        capitale_iniziale=float(_REG["capitale_iniziale"]),
        riempimento_intrabarra=intrabarra,
        moltiplicatore_costi=moltiplicatore_costi,
        ritardo_barre=ritardo_barre,
    )


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------

_CACHE: Dict[Tuple[str, str, str], Dict[str, object]] = {}


def mesi_illiquidi() -> List[str]:
    """Mesi 'AAAA-MM' con volume medio giornaliero in USDT (file 1d del last) sotto la soglia."""
    per_mese: Dict[str, List[float]] = {}
    for p in dati._percorsi_presenti(SIMBOLO, "klines", "1d", PERIODI["inizio"], date(2023, 12, 31), RADICE):
        for ts, v in dati.volume_usdt_da_zip(p).items():
            g = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
            per_mese.setdefault(f"{g.year:04d}-{g.month:02d}", []).append(v)
    return sorted(m for m, vs in per_mese.items() if sum(vs) / len(vs) < SOGLIA_LIQUIDITA)


def _mese(ts: int) -> str:
    g = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return f"{g.year:04d}-{g.month:02d}"


def carica(timeframe: str, periodo: str = "costruzione", simbolo: str = SIMBOLO) -> Dict[str, object]:
    """Serie allineate di ``timeframe``: periodo 'costruzione' oppure 'validazione' (dall'inizio
    della costruzione alla fine della validazione, indicatori caldi)."""
    chiave = (simbolo, timeframe, periodo)
    if chiave in _CACHE:
        return _CACHE[chiave]
    fine = PERIODI["fine_costruzione"] if periodo == "costruzione" else PERIODI["fine_validazione"]
    s = dati.carica_serie_allineate(simbolo, timeframe, PERIODI["inizio"], fine, RADICE)
    funding = dati.carica_funding(simbolo, PERIODI["inizio"], fine, RADICE) if simbolo == SIMBOLO else []
    illiquidi = set(mesi_illiquidi()) if simbolo == SIMBOLO else set()
    candele = s["candele"]
    vietato = np.array([_mese(c.ts) in illiquidi for c in candele], dtype=bool)
    ris = {"candele": candele, "mark": s["candele_mark"], "funding": funding, "illiquida": vietato,
           "n_tolte_last": s["n_tolte_last"], "n_tolte_mark": s["n_tolte_mark"]}
    _CACHE[chiave] = ris
    return ris


# ---------------------------------------------------------------------------
# Varianti e fabbriche di strategie
# ---------------------------------------------------------------------------


@dataclass
class Variante:
    id: str
    timeframe: str
    direzione: str
    prepara: Callable[[List[Candela]], object]
    condizione: Callable[[object, int], bool]
    segnale: Callable[[object, int], Optional[Segnale]]
    uscita: Callable[[object, int, object], Optional[str]] = lambda ctx, i, pos: None
    descrizione: Dict[str, object] = field(default_factory=dict)


def _fabbrica(v: Variante, candele: List[Candela], illiquida: np.ndarray, modo: str, ingressi=frozenset()):
    """modo: 'variante' (condizione + filtro di liquidita'), 'a' (ogni barra libera, filtro di
    liquidita'), 'casuale' (solo gli ingressi dati)."""
    ctx = v.prepara(candele)
    ts_indice = {c.ts: k for k, c in enumerate(candele)}

    def strategia(storia, pos):
        i = len(storia) - 1
        if storia[i].ts != candele[i].ts:  # la storia e' la stessa lista: controllo di coerenza
            i = ts_indice[storia[i].ts]
        if pos is not None:
            return v.uscita(ctx, i, pos)
        if modo == "casuale":
            if i not in ingressi:
                return None
        else:
            if illiquida[i]:
                return None
            if modo == "variante" and not v.condizione(ctx, i):
                return None
        return v.segnale(ctx, i)

    return strategia


def crea(v: Variante, dati_tf: Dict[str, object]):
    return lambda: _fabbrica(v, dati_tf["candele"], dati_tf["illiquida"], "variante")


def crea_a(v: Variante, dati_tf: Dict[str, object]):
    return lambda: _fabbrica(v, dati_tf["candele"], dati_tf["illiquida"], "a")


def crea_casuale(v: Variante, dati_tf: Dict[str, object]):
    return lambda ingressi: _fabbrica(v, dati_tf["candele"], dati_tf["illiquida"], "casuale", ingressi)


def crea_segnale(v: Variante, dati_tf: Dict[str, object]):
    candele = dati_tf["candele"]

    def fabbrica():
        ctx = v.prepara(candele)
        return lambda storia: v.segnale(ctx, len(storia) - 1)

    return fabbrica


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
# Conteggio, test, baseline
# ---------------------------------------------------------------------------


def conta(v: Variante, par: Optional[Parametri] = None) -> Dict[str, int]:
    d = carica(v.timeframe)
    par = par or parametri()
    return motore.conta_trade(d["candele"], crea(v, d), FINE_COSTRUZIONE_TS, par, None, d["mark"], d["funding"])


def _ordina_per_uscita(trades):
    return sorted(trades, key=lambda t: (t.ts_uscita, t.ts_entrata))


def _anno(ts: int) -> int:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year


def r_per_anno(trades) -> Dict[str, float]:
    per: Dict[int, List[float]] = {}
    for t in trades:
        per.setdefault(_anno(t.ts_uscita), []).append(t.r)
    return {str(a): round(sum(r) / len(r), 4) for a, r in sorted(per.items())}


def trade_per_anno(trades) -> Dict[str, int]:
    per: Dict[int, int] = {}
    for t in trades:
        per[_anno(t.ts_uscita)] = per.get(_anno(t.ts_uscita), 0) + 1
    return {str(a): n for a, n in sorted(per.items())}


def buy_and_hold_per_anno(candele: List[Candela], par: Parametri) -> Dict[str, Dict[str, float]]:
    per: Dict[int, List[Candela]] = {}
    for c in candele:
        per.setdefault(_anno(c.ts), []).append(c)
    return {str(a): {"long": round(motore.buy_and_hold(cs, par, "long"), 4),
                     "short": round(motore.buy_and_hold(cs, par, "short"), 4)} for a, cs in sorted(per.items())}


def _pulisci(d: Dict[str, object]) -> Dict[str, object]:
    out = {}
    for k, val in d.items():
        if k == "valori" or k.endswith("_per_simulazione"):
            continue
        if isinstance(val, float):
            out[k] = val if math.isfinite(val) else (None if math.isnan(val) else ("inf" if val > 0 else "-inf"))
        elif isinstance(val, (np.floating, np.integer)):
            out[k] = float(val)
        else:
            out[k] = val
    return out


def ms_per_barra(tf: str) -> int:
    return dati.durata_intervallo(tf)


def valuta(v: Variante, par: Optional[Parametri] = None, periodo: str = "costruzione",
           trades_minimi: Optional[int] = None) -> Dict[str, object]:
    """Test di una variante su un periodo: metriche, baseline (a) e (b), contro_baseline.

    In 'validazione' la serie va dall'inizio della costruzione alla fine della validazione e
    contano solo i trade entrati dopo la fine della costruzione; la (b) ha vietate tutte le
    barre di costruzione e la (a) conta solo i suoi trade entrati in validazione.
    """
    par = par or parametri()
    d = carica(v.timeframe, periodo)
    candele, mark, funding = d["candele"], d["mark"], d["funding"]
    ris = motore.esegui(candele, None, mark, funding, crea(v, d)(), par)
    if periodo == "validazione":
        trades = [t for t in ris.trades if t.ts_entrata > FINE_COSTRUZIONE_TS]
    else:
        trades = list(ris.trades)
    trades = _ordina_per_uscita(trades)
    minimo = trades_minimi if trades_minimi is not None else TRADE_MINIMI[periodo]
    out: Dict[str, object] = {"n_trade": len(trades)}
    if not trades:
        out["sotto_minimo"] = True
        return out
    r = [t.r for t in trades]
    pnl = [t.pnl for t in trades]
    # curva del capitale dei soli trade del periodo
    cap0 = par.capitale_iniziale
    curva = [cap0]
    for p in pnl:
        curva.append(curva[-1] + p)
    migliori = sorted(r, reverse=True)[3:]
    metriche = {
        "profit_factor": statistica.profit_factor(pnl),
        "trade": len(trades),
        "r_medio": float(np.mean(r)),
        "r_medio_per_anno": r_per_anno(trades),
        "trade_per_anno": trade_per_anno(trades),
        "r_medio_senza_3_migliori": float(np.mean(migliori)) if migliori else None,
        "drawdown_max": -statistica.drawdown_max_da_curva(curva),
        "rendimento_totale": (curva[-1] - cap0) / cap0,
        "win_rate": statistica.win_rate(pnl),
        "n_ridotti": sum(1 for t in trades if t.ridotto),
        "n_violazioni_liquidazione": sum(1 for t in trades if t.violazione_liquidazione),
        "esiti": {e: sum(1 for t in trades if t.esito == e) for e in ("stop", "target", "segnale", "liquidazione", "fine_dati")},
        "durata_media_barre": motore.durata_media_barre(trades, ms_per_barra(v.timeframe)),
        "funding_totale": sum(t.funding_pagato for t in trades),
        "n_buchi_dati": ris.n_buchi_dati,
        "n_segnali_non_validi": ris.n_segnali_non_validi,
    }
    out["metriche"] = metriche
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    out["blocco"] = blocco
    out["sotto_minimo"] = len(trades) < minimo
    # baseline (a)
    ris_a = motore.esegui(candele, None, mark, funding, crea_a(v, d)(), par)
    trades_a = ris_a.trades
    if periodo == "validazione":
        trades_a = [t for t in trades_a if t.ts_entrata > FINE_COSTRUZIONE_TS]
    trades_a = _ordina_per_uscita(trades_a)
    if trades_a:
        blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in trades_a], [t.ts_uscita for t in trades_a])
        base_a = statistica.baseline_da_trade([t.r for t in trades_a], blocco_a, n=N_BOOT, seme=SEME_BOOT)
        conf_a = statistica.contro_baseline(r, blocco, base_a, n=N_BOOT, seme=SEME_BOOT)
        out["baseline_a"] = {**_pulisci(base_a), "blocco_a": blocco_a, **{f"confronto_{k}": val for k, val in _pulisci(conf_a).items()}}
        out["baseline_a_esito"] = _pulisci(conf_a)
    else:
        out["baseline_a"] = {"valutabile": False, "motivo": "nessun trade della (a)"}
        out["baseline_a_esito"] = {"valutabile": False, "netta": False, "t": "-inf"}
    # baseline (b)
    vietate_segnale = motore.barre_vietate_segnale_non_valido(candele, crea_segnale(v, d), par)
    maschera = np.zeros(len(candele), dtype=bool)
    for a, b in vietate_segnale:
        maschera[a:b] = True
    quota_vietate_segnale = float(maschera.mean())
    maschera |= d["illiquida"]
    if periodo == "validazione":
        maschera |= np.array([c.ts <= FINE_COSTRUZIONE_TS for c in candele], dtype=bool)
    vietate = intervalli_da_maschera(maschera)
    durata = metriche["durata_media_barre"]
    try:
        base_b = motore.simula_baseline_casuale(candele, crea_casuale(v, d), len(trades), durata, par, None, mark,
                                                funding, vietate, n_simulazioni=N_SIM, primo_seme=0)
        if periodo == "validazione":
            pass  # le simulazioni hanno ingressi solo in validazione: i loro trade sono tutti di validazione
        conf_b = statistica.contro_baseline(r, blocco, base_b, n=N_BOOT, seme=SEME_BOOT)
        out["baseline_b"] = {**_pulisci(base_b),
                             "trade_per_simulazione_medio": float(np.mean(base_b["trade_per_simulazione"])),
                             "segnali_scartati_per_simulazione_medio": float(np.mean(base_b["segnali_non_validi_per_simulazione"])),
                             "quota_barre_vietate_segnale_non_valido": quota_vietate_segnale,
                             **{f"confronto_{k}": val for k, val in _pulisci(conf_b).items()}}
        out["baseline_b_esito"] = _pulisci(conf_b)
        out["percentile_caso"] = statistica.percentile_del_candidato(metriche["r_medio"], base_b["valori"])
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "motivo": str(e)}
        out["baseline_b_esito"] = {"valutabile": False, "netta": False, "t": "-inf"}
        out["percentile_caso"] = None
    out["buy_and_hold_per_anno"] = buy_and_hold_per_anno(
        [c for c in candele if (periodo == "costruzione" or c.ts > FINE_COSTRUZIONE_TS)], par)
    ea, eb = out["baseline_a_esito"], out["baseline_b_esito"]
    out["valutabile"] = bool(ea.get("valutabile")) and bool(eb.get("valutabile"))
    out["candidato"] = bool(out["valutabile"] and ea.get("netta") and eb.get("netta") and metriche["r_medio"] > 0
                            and not out["sotto_minimo"])
    return out


# ---------------------------------------------------------------------------
# Log
# ---------------------------------------------------------------------------


def _json_ok(x):
    if isinstance(x, dict):
        return {str(k): _json_ok(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_json_ok(v) for v in x]
    if isinstance(x, (np.floating,)):
        x = float(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, float):
        if math.isnan(x):
            return None
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        return round(x, 6)
    return x


def scrivi(voce: Dict[str, object]) -> Dict[str, object]:
    return registro.aggiungi(_json_ok(voce))


def voce_risultato(id_: str, out: Dict[str, object], previsione_corretta, commento: str) -> Dict[str, object]:
    voce = {"id": id_, "tipo": "risultato"}
    voce.update({k: out.get(k) for k in ("metriche", "blocco", "baseline_a", "baseline_b", "percentile_caso",
                                          "buy_and_hold_per_anno", "valutabile", "candidato")})
    voce["netta_a"] = out.get("baseline_a_esito", {}).get("netta")
    voce["netta_b"] = out.get("baseline_b_esito", {}).get("netta")
    voce["t_b"] = out.get("baseline_b_esito", {}).get("t")
    voce["previsione_corretta"] = previsione_corretta
    voce["commento"] = commento
    return voce
