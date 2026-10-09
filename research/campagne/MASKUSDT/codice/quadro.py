"""Codice comune della campagna MASKUSDT: dati, filtro di liquidita', esecuzione di una variante.

Nessuna strategia qui: solo il modo, uguale per tutte le varianti, di
* caricare last e mark allineati (``carica_serie_allineate``) e il funding;
* tagliare il periodo di costruzione (candele che chiudono entro ``fine_costruzione_ts``);
* applicare il filtro dei mesi sotto la liquidita' minima (Fase 0, punto 3): una
  variante non apre posizioni su segnali di barre di quei mesi; per la (b) le
  stesse barre sono vietate;
* costruire, da una ``Variante``, la strategia del test, quella della baseline (a)
  (senza condizione d'ingresso e senza filtri della variante, ma con il filtro di
  liquidita' che vale per tutti), la strategia casuale della (b) e il calcolo del
  segnale per ``barre_vietate_segnale_non_valido``;
* calcolare il risultato con le funzioni di ``src/`` e i nomi del log (sezione 6).

Una ``Variante`` e' un oggetto con:
* ``tf`` (timeframe), ``direzione``;
* ``prepara(candele, contesto)`` -> stato (array di indicatori calcolati UNA volta,
  causali: il valore alla barra i usa solo barre <= i);
* ``segnale(st, i)`` -> ``Segnale`` o None (stop e target alla chiusura della barra
  i, SENZA la condizione d'ingresso; None durante il riscaldamento di QUALUNQUE
  indicatore della variante, cosi' la (a) parte dalla prima barra in cui la
  variante puo' entrare e la (b) non entra nel riscaldamento);
* ``condizione(st, i)`` -> bool (la condizione d'ingresso dell'ipotesi, filtri compresi);
* ``uscita(st, i, pos, k)`` -> "chiudi" o None (k = barre chiuse dall'ingresso,
  contando la barra d'ingresso come 1).
"""
from __future__ import annotations

import bisect
import math
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import yaml

RADICE_REPO = Path(__file__).resolve().parents[4]
if str(RADICE_REPO) not in sys.path:
    sys.path.insert(0, str(RADICE_REPO))

from research.src import dati, motore, statistica  # noqa: E402
from research.src.motore import Parametri, Segnale  # noqa: E402

SIMBOLO = "MASKUSDT"
INIZIO = date(2021, 8, 1)
FINE = date(2023, 12, 31)
PERIODI = dati.periodi_campagna(INIZIO)
FINE_COSTRUZIONE_TS = PERIODI["fine_costruzione_ts"]
INIZIO_VALIDAZIONE_TS = PERIODI["inizio_validazione_ts"]
SLIPPAGE_SCHEDA = 0.0005  # campagne/MASKUSDT/scheda_moneta.md: 0.0500% per lato
SOGLIA_LIQUIDITA = 20_000_000
TRADE_MINIMI_COSTRUZIONE = 70
MS_TF = {tf: dati.durata_intervallo(tf) for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]}


def parametri(moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0,
              riempimento: str = "stop_prima") -> Parametri:
    """Parametri del motore da config/parametri.yaml e dalla scheda (sezione 7)."""
    cfg = yaml.safe_load((RADICE_REPO / "research" / "config" / "parametri.yaml").read_text())
    rd = cfg["fatti"]["regole_dimensione_bot"]
    return Parametri(
        commissione_per_lato=float(cfg["fatti"]["commissione_taker_per_lato"]["valore"]),
        slippage_per_lato=SLIPPAGE_SCHEDA,
        rischio_per_trade=float(rd["rischio_per_trade"]),
        leva_max=float(rd["leva_max"]),
        modalita_margine=rd["modalita_margine_proposta"],
        tasso_margine_mantenimento=float(rd["tasso_margine_mantenimento"]),
        margine_minimo_da_liquidazione=float(cfg["regole_esame"]["margine_minimo_da_liquidazione"]),
        capitale_iniziale=float(rd["capitale_iniziale"]),
        riempimento_intrabarra=riempimento,
        moltiplicatore_costi=moltiplicatore_costi,
        ritardo_barre=ritardo_barre,
    )


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------

def mese(ts: int) -> str:
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return f"{d.year:04d}-{d.month:02d}"


def mesi_illiquidi() -> Dict[str, float]:
    """Volume medio giornaliero in USDT per mese, dalle candele 1d del last (tutti i giorni)."""
    volumi: Dict[int, float] = {}
    for p in dati._percorsi_presenti(SIMBOLO, "klines", "1d", INIZIO, FINE, dati.RADICE_DEFAULT):
        for ts, v in dati.volume_usdt_da_zip(p).items():
            volumi.setdefault(ts, v)
    per_mese: Dict[str, List[float]] = {}
    for ts, v in volumi.items():
        if ts < dati.ms_da_data(INIZIO) or ts >= dati.ms_da_data(date(2024, 1, 1)):
            continue
        per_mese.setdefault(mese(ts), []).append(v)
    return {m: float(np.mean(v)) for m, v in sorted(per_mese.items())}


_CACHE: Dict[str, dict] = {}


def carica(tf: str) -> dict:
    """Serie allineate dell'intero in-sample per ``tf``, il funding, BTC allineato e i mesi esclusi."""
    if tf in _CACHE:
        return _CACHE[tf]
    s = dati.carica_serie_allineate(SIMBOLO, tf, INIZIO, FINE)
    funding = dati.carica_funding(SIMBOLO, INIZIO, FINE)
    btc = {c.ts: c for c in dati.carica_candele("BTCUSDT", tf, INIZIO, FINE)}
    vol_mese = mesi_illiquidi()
    esclusi = {m for m, v in vol_mese.items() if v < SOGLIA_LIQUIDITA}
    d = {"tf": tf, "serie": s, "funding": funding, "btc": btc, "volume_mese": vol_mese, "mesi_esclusi": esclusi}
    _CACHE[tf] = d
    return d


@dataclass
class Periodo:
    """Le candele di un periodo di test, con il contesto per gli indicatori."""
    tf: str
    candele: list
    mark: list
    funding: list
    btc: list  # candela BTC con lo stesso ts, o None
    volume_usdt: list
    permesse: np.ndarray  # True se un segnale a quella barra puo' aprire (filtro liquidita')
    da_indice: int = 0  # in validazione: prima barra i cui segnali contano (entrate dopo la costruzione)
    nome: str = "costruzione"

    @property
    def ms_barra(self) -> int:
        return MS_TF[self.tf]


def periodo(tf: str, nome: str = "costruzione") -> Periodo:
    d = carica(tf)
    s = d["serie"]
    if nome == "costruzione":
        n = sum(1 for c in s["candele"] if c.close_ts <= FINE_COSTRUZIONE_TS)
        fund = [(t, r) for t, r in d["funding"] if t <= FINE_COSTRUZIONE_TS]
    else:
        raise ValueError("la validazione si costruisce solo dopo la Fase 5")
    candele = s["candele"][:n]
    mark = s["candele_mark"][:n]
    permesse = np.array([mese(c.ts) not in d["mesi_esclusi"] for c in candele], dtype=bool)
    return Periodo(tf=tf, candele=candele, mark=mark, funding=fund,
                   btc=[d["btc"].get(c.ts) for c in candele],
                   volume_usdt=[s["volume_usdt"].get(c.ts) for c in candele],
                   permesse=permesse, nome=nome)


def periodo_validazione(tf: str) -> Periodo:
    """Serie dall'inizio della costruzione alla fine della validazione; i segnali contano dopo la costruzione."""
    d = carica(tf)
    s = d["serie"]
    candele, mark = s["candele"], s["candele_mark"]
    da = next(i for i, c in enumerate(candele) if c.close_ts > FINE_COSTRUZIONE_TS)
    permesse = np.array([mese(c.ts) not in d["mesi_esclusi"] for c in candele], dtype=bool)
    # i segnali delle barre di costruzione non aprono: contano solo i trade entrati dopo la fine della costruzione
    # (un segnale alla chiusura dell'ultima barra di costruzione entra all'apertura della prima di validazione)
    permesse[: max(0, da - 1)] = False
    return Periodo(tf=tf, candele=candele, mark=mark, funding=list(d["funding"]),
                   btc=[d["btc"].get(c.ts) for c in candele],
                   volume_usdt=[s["volume_usdt"].get(c.ts) for c in candele],
                   permesse=permesse, da_indice=da, nome="validazione")


# ---------------------------------------------------------------------------
# Strategie costruite da una variante
# ---------------------------------------------------------------------------

def _barre_dall_ingresso(ts_arr: List[int], ts_entrata: int, i: int) -> int:
    return i - bisect.bisect_left(ts_arr, ts_entrata) + 1


def fabbriche(var, per: Periodo):
    """Le quattro fabbriche: test, baseline (a), casuale (b), segnale senza condizione."""
    st = var.prepara(per.candele, per)
    ts_arr = [c.ts for c in per.candele]
    permesse = per.permesse

    def _crea(con_condizione: bool):
        def crea():
            def strategia(storia, pos):
                i = len(storia) - 1
                if pos is None:
                    if not permesse[i]:
                        return None
                    if con_condizione and not var.condizione(st, i):
                        return None
                    return var.segnale(st, i)
                return var.uscita(st, i, pos, _barre_dall_ingresso(ts_arr, pos.ts_entrata, i))
            return strategia
        return crea

    def crea_casuale(ingressi):
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is None:
                if i in ingressi:
                    return var.segnale(st, i)
                return None
            return var.uscita(st, i, pos, _barre_dall_ingresso(ts_arr, pos.ts_entrata, i))
        return strategia

    def crea_segnale():
        def calcolo(storia):
            return var.segnale(st, len(storia) - 1)
        return calcolo

    return _crea(True), _crea(False), crea_casuale, crea_segnale


def vietate_liquidita(permesse: np.ndarray) -> List[tuple]:
    out = []
    i = 0
    n = len(permesse)
    while i < n:
        if not permesse[i]:
            j = i
            while j < n and not permesse[j]:
                j += 1
            out.append((i, j))
            i = j
        else:
            i += 1
    return out


def conta(var) -> Dict[str, int]:
    """``conta_trade`` sulle regole esatte della variante (una volta sola per variante)."""
    per = periodo(var.tf)
    crea, _, _, _ = fabbriche(var, per)
    return motore.conta_trade(per.candele, crea, FINE_COSTRUZIONE_TS, parametri(),
                              candele_mark=per.mark, funding=per.funding)


def _anno(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year


def _metriche(ris, trades) -> dict:
    m = motore.calcola_metriche(ris)
    r = [t.r for t in trades]
    per_anno: Dict[str, list] = {}
    for t in trades:
        per_anno.setdefault(str(_anno(t.ts_uscita)), []).append(t.r)
    senza3 = sorted(r)[:-3] if len(r) > 3 else []
    stop_pct = [abs(t.entrata - t.stop) / t.entrata for t in trades]
    return {
        "profit_factor": m["profit_factor"], "trade": m["n_trade"], "r_medio": m["r_medio"],
        "r_medio_per_anno": {a: float(np.mean(v)) for a, v in sorted(per_anno.items())},
        "trade_per_anno": {a: len(v) for a, v in sorted(per_anno.items())},
        "r_medio_senza_3_migliori": float(np.mean(senza3)) if senza3 else None,
        "drawdown_max": -m["drawdown_max"], "rendimento_totale": m["rendimento_totale"],
        "rendimento_per_anno": {str(k): v for k, v in m["rendimento_per_anno"].items()},
        "win_rate": m["win_rate"], "esiti": m["esiti"], "n_ridotti": m["n_ridotti"],
        "n_violazioni_liquidazione": m["n_violazioni_liquidazione"],
        "n_segnali_non_validi": m["n_segnali_non_validi"], "n_buchi_dati": m["n_buchi_dati"],
        "n_funding_in_buco": m["n_funding_in_buco"], "funding_totale": m["funding_totale"],
        "stop_pct_mediana": float(np.median(stop_pct)) if stop_pct else None,
        "stop_oltre_6pct": int(sum(1 for s in stop_pct if s > 0.06)),
    }


def buy_and_hold_per_anno(per: Periodo) -> dict:
    p = parametri()
    out = {}
    anni = sorted({_anno(c.ts) for c in per.candele[per.da_indice:]})
    for a in anni:
        cs = [c for c in per.candele[per.da_indice:] if _anno(c.ts) == a]
        out[str(a)] = {"long": motore.buy_and_hold(cs, p, "long"), "short": motore.buy_and_hold(cs, p, "short")}
    return out


def _riassunto_b(b: dict) -> dict:
    tps = b["trade_per_simulazione"]
    return {
        "media": b["media"], "errore_standard": b["errore_standard"],
        "errore_minimo_candidato": b["errore_minimo_candidato"], "n_simulazioni": b["n_simulazioni"],
        "percentile_90": b["percentile_90"], "trade_per_simulazione_medio": float(np.mean(tps)),
        "simulazioni_vuote": b["simulazioni_vuote"],
        "segnali_non_validi_medi": float(np.mean(b["segnali_non_validi_per_simulazione"])),
        "segnali_senza_barra_medi": float(np.mean(b["segnali_senza_barra_per_simulazione"])),
    }


def _confronto_log(c: dict) -> dict:
    chiavi = ["t", "soglia", "netta", "valutabile", "differenza", "errore_standard", "errore_candidato",
              "errore_minimo", "n_blocchi", "p_value", "baseline_media", "baseline_errore_standard"]
    return {k: c.get(k) for k in chiavi}


def valuta(var, per: Optional[Periodo] = None, moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0,
           riempimento: str = "stop_prima", con_a: bool = True) -> dict:
    """Il test di una variante: candidato, baseline (a), baseline (b), confronti (sezione 8).

    In validazione (``per.nome == 'validazione'``) contano solo i trade entrati dopo la fine
    della costruzione, e gli ingressi casuali della (b) cadono solo nelle barre di validazione.
    """
    per = per or periodo(var.tf)
    par = parametri(moltiplicatore_costi, ritardo_barre, riempimento)
    crea, crea_a, crea_casuale, crea_segnale = fabbriche(var, per)
    ris = motore.esegui(per.candele, None, per.mark, per.funding, crea(), par)
    trades = [t for t in ris.trades if t.ts_entrata >= per.candele[per.da_indice].ts]
    out: Dict[str, object] = {"periodo": per.nome, "tf": var.tf, "moltiplicatore_costi": moltiplicatore_costi,
                              "ritardo_barre": ritardo_barre, "riempimento_intrabarra": riempimento}
    if len(trades) != len(ris.trades):
        # in validazione i segnali delle barre di costruzione non aprono (``permesse``): non deve succedere
        raise RuntimeError("trade entrati prima dell'inizio del periodo giudicato")
    out["metriche"] = _metriche(ris, trades)
    if len(trades) < 2:
        out["valutabile"] = False
        out["motivo"] = "meno di 2 trade"
        return out
    r = [t.r for t in trades]
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    out["blocco"] = blocco
    if con_a:
        ris_a = motore.esegui(per.candele, None, per.mark, per.funding, crea_a(), par)
        ta = [t for t in ris_a.trades if t.ts_entrata >= per.candele[per.da_indice].ts]
        if len(ta) >= 2:
            blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in ta], [t.ts_uscita for t in ta])
            base_a = statistica.baseline_da_trade([t.r for t in ta], blocco_a)
            ca = statistica.contro_baseline(r, blocco, base_a)
            out["baseline_a"] = dict(_confronto_log(ca), media=base_a["media"], n_trade=base_a["n_trade"],
                                     blocco_a=blocco_a, n_blocchi_a=base_a["n_blocchi"],
                                     valutabile_a=base_a["valutabile"])
        else:
            out["baseline_a"] = {"valutabile": False, "netta": False, "t": "-inf", "n_trade": len(ta)}
    # baseline (b)
    vietate_segnale = motore.barre_vietate_segnale_non_valido(per.candele, crea_segnale, par)
    vietate = list(vietate_segnale) + vietate_liquidita(per.permesse)
    if per.da_indice > 0:
        vietate.append((0, per.da_indice - 1))
    n_vietate_segnale = sum(b - a for a, b in vietate_segnale)
    durata = motore.durata_media_barre(trades, per.ms_barra)
    try:
        base_b = motore.simula_baseline_casuale(
            per.candele, crea_casuale, len(trades), durata, par, candele_mark=per.mark,
            funding=per.funding, barre_vietate=vietate, n_simulazioni=200, primo_seme=0)
        cb = statistica.contro_baseline(r, blocco, base_b)
        out["baseline_b"] = dict(_confronto_log(cb), **_riassunto_b(base_b),
                                 durata_media_barre=durata,
                                 quota_barre_vietate_segnale_non_valido=n_vietate_segnale / len(per.candele))
        out["percentile_caso"] = statistica.percentile_del_candidato(float(np.mean(r)), base_b["valori"])
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "netta": False, "t": "-inf", "errore": str(e)}
        out["percentile_caso"] = None
    out["buy_and_hold_per_anno"] = buy_and_hold_per_anno(per)
    va = out.get("baseline_a", {}).get("valutabile", True) if con_a else True
    vb = out["baseline_b"].get("valutabile", False)
    out["valutabile"] = bool(va and vb)
    na = out.get("baseline_a", {}).get("netta", False) if con_a else None
    nb = out["baseline_b"].get("netta", False)
    out["candidato"] = bool(na and nb and out["metriche"]["r_medio"] > 0) if con_a else None
    return out
