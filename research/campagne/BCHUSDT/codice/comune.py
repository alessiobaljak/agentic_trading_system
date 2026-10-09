"""Codice comune della campagna BCHUSDT: dati, fabbriche delle strategie, esame.

Niente strategie qui: solo il modo, uguale per tutte le varianti, di
* caricare last e mark allineati (``carica_serie_allineate``) e il funding;
* escludere gli ingressi su segnali di barre dei mesi sotto la liquidita' minima
  (Fase 0, punto 3: stesso filtro per ``conta_trade``, test e baseline (a); le
  stesse barre vanno in ``barre_vietate`` della (b));
* costruire, da una ``Variante``, le quattro fabbriche che il motore vuole:
  la strategia della variante, la baseline (a) (senza condizione d'ingresso e
  senza filtri dell'idea), la strategia casuale della (b) e il calcolo del
  segnale per ``barre_vietate_segnale_non_valido``;
* eseguire l'esame della Fase 2 (sezione 8) e restituire i campi del log.

Una ``Variante`` precalcola i suoi indicatori su tutta la serie che riceve
(``prepara``), ma ognuno deve essere CAUSALE: il valore all'indice i usa solo le
barre 0..i. ``verifica_causalita`` lo controlla tagliando la serie in piu' punti
e confrontando i valori: una variante che non passa non si conta e non si testa.
"""
from __future__ import annotations

import math
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np
import yaml

from research.src import dati, motore, statistica
from research.src.motore import Parametri, Segnale

SIMBOLO = "BCHUSDT"
INIZIO = date(2020, 1, 1)
FINE_COSTRUZIONE = date(2022, 10, 18)
FINE_VALIDAZIONE = date(2023, 12, 31)
FINE_COSTRUZIONE_TS = 1666137599999
INIZIO_VALIDAZIONE_TS = 1666137600000
SLIPPAGE_SCHEDA = 0.0002  # scheda_moneta.md: 0,0200% per lato
RADICE = Path(__file__).resolve().parents[3]  # research/
CARTELLA_DATI = RADICE / "data" / "insample" / SIMBOLO

_CONFIG = yaml.safe_load((RADICE / "config" / "parametri.yaml").read_text(encoding="utf-8"))
_REG = _CONFIG["fatti"]["regole_dimensione_bot"]
_ESAME = _CONFIG["regole_esame"]
LIQUIDITA_MINIMA = float(_CONFIG["scelte_dati"]["liquidita_minima_usdt_giorno"])
N_SIMULAZIONI = int(_ESAME["simulazioni_baseline_casuale"])
PRIMO_SEME = int(_ESAME["semi_baseline_casuale"]["primo"])
N_BOOT = int(_ESAME["bootstrap"]["ricampionamenti"])
SEME_BOOT = int(_ESAME["bootstrap"]["seme"])
TRADE_MINIMI = dict(_ESAME["trade_minimi"])


def parametri(moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0,
              riempimento: str = "stop_prima") -> Parametri:
    """I parametri del motore da parametri.yaml e dalla scheda (sezione 7)."""
    return Parametri(
        commissione_per_lato=float(_CONFIG["fatti"]["commissione_taker_per_lato"]["valore"]),
        slippage_per_lato=SLIPPAGE_SCHEDA,
        rischio_per_trade=float(_REG["rischio_per_trade"]),
        leva_max=float(_REG["leva_max"]),
        modalita_margine=_REG["modalita_margine_proposta"],
        tasso_margine_mantenimento=float(_REG["tasso_margine_mantenimento"]),
        margine_minimo_da_liquidazione=float(_ESAME["margine_minimo_da_liquidazione"]),
        capitale_iniziale=float(_REG["capitale_iniziale"]),
        riempimento_intrabarra=riempimento,
        moltiplicatore_costi=moltiplicatore_costi,
        ritardo_barre=ritardo_barre,
    )


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------

_CACHE: Dict[Tuple[str, str], Dict[str, object]] = {}


def mesi_sotto_liquidita() -> List[Tuple[int, int]]:
    """Mesi con volume medio giornaliero in USDT (candele 1d del last, tutti i giorni) sotto la soglia."""
    volumi: Dict[int, float] = {}
    cartella = CARTELLA_DATI / "klines" / "1d"
    for percorso in sorted(cartella.glob("*.zip")):
        for ts, v in dati.volume_usdt_da_zip(percorso).items():
            if ts <= FINE_VALIDAZIONE_TS_FINE:
                volumi.setdefault(ts, v)
    per_mese: Dict[Tuple[int, int], List[float]] = {}
    for ts, v in volumi.items():
        g = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        per_mese.setdefault((g.year, g.month), []).append(v)
    return sorted(m for m, vs in per_mese.items() if sum(vs) / len(vs) < LIQUIDITA_MINIMA)


FINE_VALIDAZIONE_TS_FINE = dati.ms_da_data(date(2024, 1, 1)) - 1


def carica(tf: str, periodo: str = "costruzione") -> Dict[str, object]:
    """Serie allineate di BCHUSDT sul timeframe ``tf``: costruzione, oppure costruzione + validazione."""
    chiave = (tf, periodo)
    if chiave in _CACHE:
        return _CACHE[chiave]
    fine = FINE_COSTRUZIONE if periodo == "costruzione" else FINE_VALIDAZIONE
    if periodo not in ("costruzione", "validazione"):
        raise ValueError(periodo)
    s = dati.carica_serie_allineate(SIMBOLO, tf, INIZIO, fine)
    funding = dati.carica_funding(SIMBOLO, INIZIO, fine)
    candele = s["candele"]
    esclusi = set(mesi_sotto_liquidita())
    escluso = np.array([(_anno_mese(c.ts) in esclusi) for c in candele], dtype=bool)
    ris = dict(s)
    ris.update({
        "tf": tf,
        "periodo": periodo,
        "funding": funding,
        "escluso": escluso,
        "ms_barra": dati.durata_intervallo(tf),
        "ts": np.array([c.ts for c in candele], dtype=np.int64),
        "open": np.array([c.open for c in candele]),
        "high": np.array([c.high for c in candele]),
        "low": np.array([c.low for c in candele]),
        "close": np.array([c.close for c in candele]),
        "volume": np.array([c.volume for c in candele]),
        "volume_usdt": np.array([s["volume_usdt"].get(c.ts) or np.nan for c in candele]),
    })
    _CACHE[chiave] = ris
    return ris


def _anno_mese(ts: int) -> Tuple[int, int]:
    g = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return g.year, g.month


def anno(ts: int) -> int:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year


def taglia(serie: Dict[str, object], n: int) -> Dict[str, object]:
    """Le prime ``n`` barre della serie (per la verifica di causalita')."""
    t = {}
    for k, v in serie.items():
        if isinstance(v, np.ndarray) and v.shape[:1] == (len(serie["candele"]),):
            t[k] = v[:n]
        elif k in ("candele", "candele_mark"):
            t[k] = v[:n]
        else:
            t[k] = v
    return t


# ---------------------------------------------------------------------------
# Varianti e fabbriche
# ---------------------------------------------------------------------------


class Variante:
    """Una regola completa: timeframe, direzione, ingresso, uscita, stop, target, filtri.

    Le sottoclassi definiscono:
    * ``prepara(serie)`` -> dizionario di array causali (indicatori);
    * ``stop_target(ind, serie, i)`` -> (stop, target o None) calcolato alla chiusura
      della barra i, SENZA la condizione d'ingresso; None se non calcolabile;
    * ``condizione(ind, serie, i)`` -> bool: la condizione d'ingresso dell'ipotesi
      (compresi i filtri dell'idea);
    * ``esci(ind, serie, i, barre_tenute, pos)`` -> bool: uscita a segnale o a tempo
      (chiusura all'apertura della barra dopo).
    ``riscaldamento`` e' il numero di barre prima della prima barra in cui la variante
    puo' entrare (tutti i suoi indicatori calcolabili).
    """

    id: str = ""
    tf: str = "1h"
    direzione: str = "long"
    riscaldamento: int = 0
    nomi_causali: Sequence[str] = ()

    def prepara(self, serie) -> Dict[str, np.ndarray]:
        return {}

    def stop_target(self, ind, serie, i) -> Optional[Tuple[float, Optional[float]]]:
        raise NotImplementedError

    def condizione(self, ind, serie, i) -> bool:
        raise NotImplementedError

    def esci(self, ind, serie, i, barre_tenute, pos) -> bool:
        return False

    def descrizione(self) -> Dict[str, object]:
        return {}


def _segnale(v: Variante, ind, serie, i) -> Optional[Segnale]:
    if i < v.riscaldamento:
        return None
    st = v.stop_target(ind, serie, i)
    if st is None:
        return None
    stop, target = st
    if stop is None or not math.isfinite(stop) or stop <= 0:
        return None
    if target is not None and not math.isfinite(target):
        return None
    return Segnale(v.direzione, float(stop), None if target is None else float(target))


def _barre_tenute(serie, i, pos) -> int:
    return int((serie["ts"][i] - pos.ts_entrata) // serie["ms_barra"]) + 1


def fabbriche(v: Variante, serie, ind=None):
    """(crea_strategia, crea_a, crea_casuale, crea_segnale) per la variante sulla serie."""
    if ind is None:
        ind = v.prepara(serie)
    escluso = serie["escluso"]

    def uscita(i, pos):
        return v.esci(ind, serie, i, _barre_tenute(serie, i, pos), pos)

    def crea_strategia():
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is not None:
                return "chiudi" if uscita(i, pos) else None
            if i < v.riscaldamento or escluso[i]:
                return None
            if not v.condizione(ind, serie, i):
                return None
            return _segnale(v, ind, serie, i)
        return strategia

    def crea_a():
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is not None:
                return "chiudi" if uscita(i, pos) else None
            if i < v.riscaldamento or escluso[i]:
                return None
            return _segnale(v, ind, serie, i)
        return strategia

    def crea_casuale(ingressi):
        def strategia(storia, pos):
            i = len(storia) - 1
            if pos is not None:
                return "chiudi" if uscita(i, pos) else None
            if i in ingressi:
                return _segnale(v, ind, serie, i)
            return None
        return strategia

    def crea_segnale():
        def segnale(storia):
            return _segnale(v, ind, serie, len(storia) - 1)
        return segnale

    return crea_strategia, crea_a, crea_casuale, crea_segnale


def verifica_causalita(v: Variante, serie, tagli: int = 6, seme: int = 12345) -> List[str]:
    """Ricalcola gli indicatori su serie tagliate e li confronta con quelli sull'intera serie.

    Ritorna la lista delle differenze (vuota = causale). Si confrontano tutti gli
    array dell'indicatore all'ultimo indice della serie tagliata e nelle 50 barre
    prima. Controlla anche condizione e stop/target negli stessi punti.
    """
    n = len(serie["candele"])
    pieno = v.prepara(serie)
    rng = np.random.default_rng(seme)
    punti = sorted(set(int(x) for x in rng.integers(max(v.riscaldamento + 60, 100), n - 2, size=tagli)))
    differenze: List[str] = []
    for k in punti:
        corta = taglia(serie, k + 1)
        ind_c = v.prepara(corta)
        for nome, arr in pieno.items():
            if not isinstance(arr, np.ndarray) or arr.shape[:1] != (n,):
                continue
            a = arr[k - 50:k + 1]
            b = ind_c[nome][k - 50:k + 1]
            uguali = np.allclose(a.astype(float), b.astype(float), rtol=1e-9, atol=1e-12, equal_nan=True)
            if not uguali:
                differenze.append(f"{nome} al taglio {k}")
        for j in range(k - 50, k + 1):
            if j < v.riscaldamento:
                continue
            if bool(v.condizione(pieno, serie, j)) != bool(v.condizione(ind_c, corta, j)):
                differenze.append(f"condizione al taglio {k}, barra {j}")
                break
            s1, s2 = v.stop_target(pieno, serie, j), v.stop_target(ind_c, corta, j)
            if (s1 is None) != (s2 is None) or (s1 is not None and not np.allclose(
                    [x if x is not None else np.nan for x in s1], [x if x is not None else np.nan for x in s2],
                    equal_nan=True)):
                differenze.append(f"stop/target al taglio {k}, barra {j}")
                break
    return differenze


# ---------------------------------------------------------------------------
# Conteggio e esame
# ---------------------------------------------------------------------------


def conta(v: Variante) -> Dict[str, int]:
    """La stima dei trade della sezione 8: ``conta_trade`` sui dati di costruzione."""
    serie = carica(v.tf, "costruzione")
    crea_strategia, _, _, _ = fabbriche(v, serie)
    return motore.conta_trade(serie["candele"], crea_strategia, FINE_COSTRUZIONE_TS, parametri(),
                              None, serie["candele_mark"], serie["funding"])


def _intervalli(maschera: np.ndarray) -> List[Tuple[int, int]]:
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


def _quota_vietata(vietate: Sequence[Tuple[int, int]], n: int) -> float:
    m = np.zeros(n, dtype=bool)
    for a, b in vietate:
        m[max(0, a):min(n, b)] = True
    return float(m.mean())


def _riassunto_confronto(c: Dict[str, object]) -> Dict[str, object]:
    chiavi = ("t", "soglia", "netta", "valutabile", "differenza", "errore_standard", "errore_candidato",
              "errore_minimo", "n_blocchi", "p_value", "baseline_media", "baseline_errore_standard")
    out = {}
    for k in chiavi:
        if k in c:
            x = c[k]
            if isinstance(x, (float, np.floating)):
                x = float(x)
                if math.isinf(x):
                    x = "inf" if x > 0 else "-inf"
            out[k] = x
    return out


def _r_ordinati(trades) -> List[float]:
    return [t.r for t in sorted(trades, key=lambda t: (t.ts_uscita, t.ts_entrata))]


def metriche_trade(trades, capitale: float) -> Dict[str, object]:
    tr = sorted(trades, key=lambda t: (t.ts_uscita, t.ts_entrata))
    rs = [t.r for t in tr]
    n = len(rs)
    vinti = sum(t.pnl for t in tr if t.pnl > 0)
    persi = -sum(t.pnl for t in tr if t.pnl < 0)
    pf = vinti / persi if persi > 0 else (math.inf if vinti > 0 else 0.0)
    per_anno: Dict[str, List[float]] = {}
    for t in tr:
        per_anno.setdefault(str(anno(t.ts_uscita)), []).append(t.r)
    curva, cap, picco, dd = [], capitale, capitale, 0.0
    for t in tr:
        cap += t.pnl
        picco = max(picco, cap)
        dd = max(dd, (picco - cap) / picco if picco > 0 else 0.0)
    senza3 = sorted(rs)[:-3] if n > 3 else []
    esiti: Dict[str, int] = {}
    for t in tr:
        esiti[t.esito] = esiti.get(t.esito, 0) + 1
    return {
        "profit_factor": (float(pf) if math.isfinite(pf) else "inf"),
        "trade": n,
        "r_medio": float(np.mean(rs)) if n else 0.0,
        "r_medio_per_anno": {a: round(float(np.mean(v)), 4) for a, v in sorted(per_anno.items())},
        "trade_per_anno": {a: len(v) for a, v in sorted(per_anno.items())},
        "r_medio_senza_3_migliori": float(np.mean(senza3)) if senza3 else None,
        "drawdown_max": -round(dd, 4),
        "rendimento_totale": round((cap - capitale) / capitale, 4),
        "win_rate": round(sum(1 for t in tr if t.pnl > 0) / n, 4) if n else 0.0,
        "n_ridotti": sum(1 for t in tr if t.ridotto),
        "n_violazioni_liquidazione": sum(1 for t in tr if t.violazione_liquidazione),
        "esiti": esiti,
        "funding_totale": round(sum(t.funding_pagato for t in tr), 4),
    }


def buy_and_hold_per_anno(serie, da_ts: int, a_ts: int) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    per_anno: Dict[int, list] = {}
    for c in serie["candele"]:
        if da_ts <= c.ts and c.close_ts <= a_ts:
            per_anno.setdefault(anno(c.ts), []).append(c)
    p = parametri()
    for a, cs in sorted(per_anno.items()):
        out[str(a)] = {"long": round(motore.buy_and_hold(cs, p, "long"), 4),
                       "short": round(motore.buy_and_hold(cs, p, "short"), 4)}
    return out


def esamina(v: Variante, periodo: str = "costruzione", moltiplicatore_costi: float = 1.0,
            ritardo_barre: int = 0, riempimento: str = "stop_prima", con_a: bool = True) -> Dict[str, object]:
    """L'esame della Fase 2 (o di una verifica): candidato, (a), (b), percentile, buy and hold.

    ``periodo`` = "costruzione" oppure "validazione": in validazione la serie va
    dall'inizio della costruzione alla fine della validazione (indicatori caldi),
    contano solo i trade entrati dopo la fine della costruzione e gli ingressi
    casuali della (b) cadono solo nelle barre di validazione.
    """
    serie = carica(v.tf, periodo)
    p = parametri(moltiplicatore_costi, ritardo_barre, riempimento)
    ind = v.prepara(serie)
    crea_strategia, crea_a, crea_casuale, crea_segnale = fabbriche(v, serie, ind)
    candele, mark, funding = serie["candele"], serie["candele_mark"], serie["funding"]
    n = len(candele)
    da_ts = INIZIO_VALIDAZIONE_TS if periodo == "validazione" else 0

    ris = motore.esegui(candele, None, mark, funding, crea_strategia(), p)
    trades = [t for t in ris.trades if t.ts_entrata >= da_ts]
    out: Dict[str, object] = {"metriche": metriche_trade(trades, p.capitale_iniziale),
                              "n_buchi_dati": ris.n_buchi_dati, "n_funding_in_buco": ris.n_funding_in_buco,
                              "segnali_non_validi": ris.n_segnali_non_validi}
    if not trades:
        out["valutabile"] = False
        return out
    rc = _r_ordinati(trades)
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    out["blocco"] = blocco

    # baseline (a)
    if con_a:
        ra_ris = motore.esegui(candele, None, mark, funding, crea_a(), p)
        trades_a = [t for t in ra_ris.trades if t.ts_entrata >= da_ts]
        if len(trades_a) >= 2:
            blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in trades_a], [t.ts_uscita for t in trades_a])
            base_a = statistica.baseline_da_trade(_r_ordinati(trades_a), blocco_a, N_BOOT, SEME_BOOT)
            cmp_a = statistica.contro_baseline(rc, blocco, base_a, N_BOOT, SEME_BOOT)
            out["baseline_a"] = dict(_riassunto_confronto(cmp_a), media=float(base_a["media"]),
                                     n_trade=int(base_a["n_trade"]), blocco_a=int(blocco_a),
                                     n_blocchi_a=int(base_a["n_blocchi"]), valutabile_a=bool(base_a["valutabile"]))
        else:
            out["baseline_a"] = {"valutabile": False, "netta": False, "t": "-inf", "n_trade": len(trades_a)}

    # baseline (b)
    durata = motore.durata_media_barre(trades, serie["ms_barra"])
    vietate = list(motore.barre_vietate_segnale_non_valido(candele, crea_segnale, p))
    vietate += _intervalli(serie["escluso"])
    if periodo == "validazione":
        n_costr = int(np.searchsorted(serie["ts"], INIZIO_VALIDAZIONE_TS))
        vietate.append((0, n_costr))
    try:
        base_b = motore.simula_baseline_casuale(candele, crea_casuale, len(trades), durata, p, None, mark,
                                                funding, vietate, N_SIMULAZIONI, PRIMO_SEME)
        cmp_b = statistica.contro_baseline(rc, blocco, base_b, N_BOOT, SEME_BOOT)
        out["baseline_b"] = dict(
            _riassunto_confronto(cmp_b), media=float(base_b["media"]), n_simulazioni=int(base_b["n_simulazioni"]),
            trade_per_simulazione_medio=round(float(np.mean(base_b["trade_per_simulazione"])), 2),
            simulazioni_vuote=int(base_b["simulazioni_vuote"]),
            segnali_scartati_per_simulazione_medio=round(float(np.mean(base_b["segnali_non_validi_per_simulazione"])), 3),
            quota_barre_vietate=round(_quota_vietata(vietate, n), 4),
            quota_barre_vietate_segnale_non_valido=round(_quota_vietata(
                motore.barre_vietate_segnale_non_valido(candele, crea_segnale, p), n), 4),
            durata_media_barre=int(durata))
        out["percentile_caso"] = statistica.percentile_del_candidato(float(np.mean(rc)), base_b["valori"])
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "netta": False, "t": "-inf", "errore": str(e)}
        out["percentile_caso"] = None

    a_ts = FINE_COSTRUZIONE_TS if periodo == "costruzione" else FINE_VALIDAZIONE_TS_FINE
    out["buy_and_hold_per_anno"] = buy_and_hold_per_anno(serie, da_ts, a_ts)
    va = out.get("baseline_a", {}).get("valutabile", True) if con_a else True
    vb = out["baseline_b"].get("valutabile", False)
    out["valutabile"] = bool(va and vb)
    netta_a = out.get("baseline_a", {}).get("netta", False) if con_a else None
    out["candidato"] = bool(out["valutabile"] and netta_a and out["baseline_b"].get("netta", False)
                            and out["metriche"]["r_medio"] > 0)
    out["_trades"] = trades
    return out
