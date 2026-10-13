#!/usr/bin/env python3
"""Prova degli ordini limite: le corse della sezione 5 di ``regole.md`` per ogni strategia.

Per ogni strategia (sezione 3) e per ogni periodo (costruzione, validazione, intero
2020-2023) fa, con il codice della campagna sul branch principale e il
``research/src`` di oggi:

* **M**: esecuzione a mercato come nella campagna, con la baseline (b)-M; i numeri
  devono riprodurre quelli del log della campagna (parita', sezione 5 punto 1).
  Se la parita' fallisce la strategia si FERMA: nessun numero di L.
* **L**: la regola della sezione 4 (ordine limite alla chiusura della barra di
  segnale, valido una barra, «attraversato», maker 0,02%, scarto zero) con la
  baseline (b)-L: stessi ingressi casuali della (b)-M, eseguiti con la regola limite.
* le varianti della sezione 4.6, solo in L e senza baseline: (a) «toccato»,
  (b) validita' di due barre, (c) anche le uscite «chiudi» a limite.

Ogni strategia gira in un processo a parte (i moduli delle campagne si chiamano tutti
``comune``/``varianti``). Uso:

    python research/esperimenti/ordini_limite/prova.py BTCUSDT-V10        # una strategia
    python research/esperimenti/ordini_limite/prova.py --tutte --processi 4
    python research/esperimenti/ordini_limite/prova.py --riassunto        # tabelle in risultati.md

Gli esiti vanno in ``esiti/<STRATEGIA>.json`` (tracciati), i log in ``esiti/<STRATEGIA>.log``.
Nessuna strategia viene promossa: la prova misura costi, trade saltati e lordo.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import math
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

QUI = Path(__file__).resolve().parent
RADICE = QUI.parents[2]
sys.path.insert(0, str(RADICE))

from research.src import motore, statistica  # noqa: E402
from research.src.motore import Parametri  # noqa: E402

ESITI = QUI / "esiti"
REGOLE = QUI / "regole.md"
N_SIM = 200
PRIMO_SEME = 0
BOOT_N = 2000
BOOT_SEME = 0
MAKER = 0.0002  # regole.md 4.5: commissione maker per lato, livello base dei futures USDⓈ-M
PERIODI = ("costruzione", "validazione", "intero")

STRATEGIE = ["BTCUSDT-V10", "BNBUSDT-045", "ADAUSDT-037", "BTCUSDT-V35", "ETCUSDT-033",
             "SOLUSDT-023", "AVAXUSDT-V-12", "FILUSDT-016", "DYDXUSDT-008"]

FILE_IMPRONTE = {
    "motore.py": RADICE / "research" / "src" / "motore.py",
    "dati.py": RADICE / "research" / "src" / "dati.py",
    "statistica.py": RADICE / "research" / "src" / "statistica.py",
    "parametri.yaml": RADICE / "research" / "config" / "parametri.yaml",
    "prova.py": Path(__file__).resolve(),
    "regole.md": REGOLE,
}

# ---------------------------------------------------------------------------
# Parita' M: i numeri del log di ogni campagna (copiati con le cifre del log).
# Una stringa con d decimali e' un numero arrotondato: tolleranza 0,6 x 10^-d.
# Una stringa con 10 decimali o piu' e' il numero intero del log: tolleranza relativa 1e-9.
# Fonte: research/campagne/<SIMBOLO>/log.jsonl (riga indicata), vedi la sezione 4 di risultati.md.
# ---------------------------------------------------------------------------
PARITA: Dict[str, Dict[str, Dict[str, object]]] = {
    "BTCUSDT-V10": {
        "costruzione": {"fonte": "log riga 26 (BTCUSDT-V10)", "trade": 300, "r_medio": "0.1488", "profit_factor": "1.3615",
                        "b_media": "-0.30645", "t": "2.35384", "p_value": "0.00994", "durata": 10, "tps": "288.33"},
        "validazione": {"fonte": "log riga 203 (BTCUSDT-V10-VAL)", "trade": 136, "r_medio": "0.048", "profit_factor": "1.128",
                        "b_media": "-0.56998", "t": "1.69024", "p_value": "0.047815252205714295", "durata": 9, "tps": "130.16"},
    },
    "BNBUSDT-045": {
        "costruzione": {"fonte": "log riga 190 (BNBUSDT-045)", "trade": 74, "r_medio": "0.138052", "profit_factor": "2.758430",
                        "b_media": "-0.047778", "t": "3.963275", "p_value": "0.000308", "durata": 4, "tps": "73.905"},
        "validazione": {"fonte": "log riga 236 (BNBUSDT-045-validazione)", "trade": 32, "r_medio": "0.047296",
                        "profit_factor": "1.489735", "b_media": "-0.092328", "t": "2.138675", "p_value": "0.030576",
                        "durata": 3, "tps": "31.935"},
    },
    "ADAUSDT-037": {
        "costruzione": {"fonte": "log riga 109 (ADAUSDT-037)", "trade": 178, "r_medio": "0.25200700651574104",
                        "profit_factor": "1.423727484579257", "b_media": "-0.1370904272244546", "t": "2.5116379195444236",
                        "p_value": "0.007926403244850366", "durata": 50, "tps": "175.54"},
        "validazione": {"fonte": "log riga 152 (ADAUSDT-037-V06)", "trade": 82, "r_medio": "0.6240172173607658",
                        "profit_factor": "2.146539846549591", "b_media": "-0.31187733743050644", "t": "2.2848421361158127",
                        "p_value": "0.0138509429924179", "durata": 43, "tps": "80.585"},
    },
    "BTCUSDT-V35": {
        "costruzione": {"fonte": "log riga 77 (BTCUSDT-V35)", "trade": 141, "r_medio": "0.0454", "profit_factor": "1.3326",
                        "b_media": "-0.12083", "t": "3.57732", "p_value": "0.00024", "durata": 1, "tps": "140.44"},
    },
    "ETCUSDT-033": {
        "costruzione": {"fonte": "log riga 71 (ETCUSDT-033)", "trade": 124, "r_medio": "0.017702628898496067",
                        "profit_factor": "1.1461138850678347", "b_media": "-0.08953153608616223", "t": "3.6221673028569312",
                        "p_value": "0.00021280151378073067", "durata": 1, "tps": "123.645"},
    },
    "SOLUSDT-023": {
        "costruzione": {"fonte": "log riga 95 (SOLUSDT-023)", "trade": 193, "r_medio": "0.0170", "profit_factor": "1.1462",
                        "b_media": "-0.04629", "t": "2.77889", "p_value": "0.00329", "durata": 1, "tps": "192.1"},
    },
    "AVAXUSDT-V-12": {
        "costruzione": {"fonte": "log riga 54 (AVAXUSDT-V12) e risultati/V-12.json", "trade": 376, "r_medio": "0.0072",
                        "profit_factor": "1.0528", "b_media": "-0.055999", "t": "3.523072", "p_value": "0.000268",
                        "durata": 1, "tps": "372.37"},
    },
    "FILUSDT-016": {
        "costruzione": {"fonte": "log riga 37 (FILUSDT-016)", "trade": 426, "r_medio": "0.067279", "profit_factor": "1.135196",
                        "b_media": "-0.080667", "t": "2.350746", "p_value": "0.010302", "durata": 7, "tps": "412.5"},
    },
    "DYDXUSDT-008": {
        "costruzione": {"fonte": "log riga 27 (DYDXUSDT-008)", "trade": 161, "r_medio": "0.060413258867768826",
                        "profit_factor": "1.3409425715852454", "b_media": "-0.03837480627129526", "t": "2.2168935870928923",
                        "p_value": "0.016264800244890458", "durata": 3, "tps": "159.33"},
        "validazione": {"fonte": "log riga 121 (DYDXUSDT-008-VAL)", "trade": 83, "r_medio": "-0.17752228756173585",
                        "profit_factor": "0.4310616459825442", "b_media": "-0.05284820531076887", "t": "-1.959243109934988",
                        "p_value": "0.9675382187608197", "durata": 3, "tps": "82.095"},
    },
}


# ---------------------------------------------------------------------------
# Utilita'
# ---------------------------------------------------------------------------
def adesso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blocco in iter(lambda: f.read(1 << 20), b""):
            h.update(blocco)
    return h.hexdigest()


def impronte() -> Dict[str, str]:
    return {nome: sha256_file(p) for nome, p in FILE_IMPRONTE.items()}


def commit_corrente() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=RADICE, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # pragma: no cover
        return "?"


def pulito(x):
    """Rende serializzabile in JSON (numpy, inf, nan, tuple)."""
    if isinstance(x, dict):
        return {str(k): pulito(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [pulito(v) for v in x]
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating, float)):
        x = float(x)
        if math.isnan(x):
            return None
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        return x
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, np.ndarray):
        return [pulito(v) for v in x.tolist()]
    return x


def _anno(ts: int) -> str:
    return str(datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year)


def confronta_parita(atteso: Dict[str, object], trovato: Dict[str, object]) -> List[Dict[str, object]]:
    """Confronta i numeri rifatti con quelli del log: lista delle differenze (vuota = parita')."""
    differenze = []
    for chiave, valore in atteso.items():
        if chiave == "fonte":
            continue
        mio = trovato.get(chiave)
        if isinstance(valore, int):
            ok = mio == valore
            differenze_rel = None
            toll = 0
        else:
            s = str(valore)
            decimali = len(s.split(".")[1]) if "." in s else 0
            v = float(s)
            if decimali >= 10:
                toll = abs(v) * 1e-9 + 1e-12
            else:
                toll = 0.6 * 10 ** (-decimali)
            ok = mio is not None and abs(float(mio) - v) <= toll
        if not ok:
            differenze.append({"chiave": chiave, "atteso": valore, "trovato": mio, "tolleranza": toll})
    return differenze


# ---------------------------------------------------------------------------
# Il quadro di una strategia su un periodo: dati, fabbriche, parametri, filtri
# ---------------------------------------------------------------------------
@dataclasses.dataclass
class Quadro:
    candele: list
    mark: list
    funding: list
    ms: int
    fabbrica: Callable[[], object]
    fabbrica_casuale: Callable[[frozenset], object]
    fabbrica_segnale: Callable[[], object]
    par: Parametri
    vietate_extra: List[Tuple[int, int]]
    filtro_ts: Callable[[int], bool]  # True se un ingresso a quel ts (apertura della barra d'ingresso) e' nel periodo
    note: Dict[str, object]


def _cartella_codice(nome: str) -> Path:
    return RADICE / "research" / "campagne" / nome.split("-")[0] / "codice"


def _btc(nome: str, periodo: str) -> Quadro:
    import comune  # noqa: F401  (campagna BTCUSDT)
    import quadro
    import varianti
    vid = nome.split("-", 1)[1]
    v = varianti.TUTTE[vid]()
    par = comune.parametri()
    if periodo == "costruzione":
        candele, mark, funding = quadro.costruzione(v.tf)
    else:
        candele, mark, funding = quadro.tutto_insample(v.tf)
    inizio_v = int(comune.PERIODI["inizio_validazione_ts"])
    extra: List[Tuple[int, int]] = []
    filtro = (lambda ts: True)
    if periodo == "validazione":
        primo = next(i for i, c in enumerate(candele) if c.ts >= inizio_v)
        extra = [(0, primo)]
        filtro = (lambda ts: ts >= inizio_v)
    return Quadro(candele, mark, list(funding), quadro.MS[v.tf], v.fabbrica(candele), v.fabbrica_casuale(candele),
                  v.fabbrica_segnale(candele), par, extra, filtro,
                  {"tf": v.tf, "direzione": v.direzione, "serie": "file nativi " + v.tf, "mesi_esclusi": "nessuno"})


def _bnb(nome: str, periodo: str) -> Quadro:
    import comune as C
    import varianti
    v = varianti.i03("1h", nome, max_barre=12, solo_fine_settimana=True)
    d = C.carica("1h", "costruzione" if periodo == "costruzione" else "intero")
    candele, mark, funding = d["candele"], d["mark"], d["funding"]
    p = C.parametri()
    ctx = C.contesto(v, candele)
    extra = C.intervalli(ctx.esclusi)
    filtro = (lambda ts: True)
    if periodo == "validazione":
        da = int(C.INIZIO_VALIDAZIONE_TS)
        primo = next(i for i, c in enumerate(candele) if c.ts >= da)
        extra = extra + [(0, primo)]
        filtro = (lambda ts: ts >= da)
    return Quadro(candele, mark, list(funding), int(d["ms_barra"]), C.fabbrica(v, candele), C.fabbrica_casuale(v, candele),
                  C.fabbrica_segnale(v, candele), p, extra, filtro,
                  {"tf": "1h", "direzione": v.direzione, "serie": "file nativi 1h", "mesi_esclusi": str(C.MESI_ESCLUSI)})


def _ada(nome: str, periodo: str) -> Quadro:
    import comune as C
    import varianti
    var = varianti.VARIANTI[nome]
    D = C.carica(var.tf, "costruzione" if periodo == "costruzione" else "validazione")
    solo_dopo = int(C.FINE_COSTRUZIONE_TS) if periodo == "validazione" else None
    F = C.Fabbriche(var, D, solo_dopo_ts=solo_dopo)
    extra = C.intervalli_da_maschera(F.escl)
    filtro = (lambda ts: ts > solo_dopo) if solo_dopo is not None else (lambda ts: True)
    return Quadro(D["candele"], D["mark"], list(D["funding"]), int(D["passo"]), F.crea_strategia, F.crea_casuale,
                  F.crea_segnale, C.PARAM, extra, filtro,
                  {"tf": var.tf, "direzione": var.direzione, "serie": "file nativi " + var.tf,
                   "mesi_esclusi": str(sorted(C.MESI_ESCLUSI))})


def _etc(nome: str, periodo: str) -> Quadro:
    import comune as C
    import varianti
    var = varianti._r1()[0]
    serie = C.carica(var.tf, "costruzione" if periodo == "costruzione" else "validazione")
    ind = var.prepara(serie)
    crea_strategia, crea_casuale, crea_segnale = C._fabbriche(var, serie, ind)
    maschera = list(serie.vietate_liquidita)
    filtro = (lambda ts: True)
    if periodo == "validazione":
        fine_c = int(C.FINE_COSTRUZIONE_TS)
        maschera = [m or (c.ts <= fine_c) for m, c in zip(maschera, serie.candele)]
        filtro = (lambda ts: ts > fine_c)
    return Quadro(serie.candele, serie.mark, list(serie.funding), int(C.MS[var.tf]), crea_strategia(True), crea_casuale,
                  crea_segnale, C.PARAMETRI, C.intervalli(maschera), filtro,
                  {"tf": var.tf, "direzione": var.direzione, "serie": "file nativi " + var.tf,
                   "mesi_esclusi": str(C.mesi_esclusi())})


def _sol(nome: str, periodo: str) -> Quadro:
    import comune as C
    import varianti
    tf, costr = varianti.VARIANTI[nome]
    s = C.carica(tf, "costruzione" if periodo == "costruzione" else "validazione")
    escl = C.mesi_esclusi_barre(s.last)
    filtro = (lambda ts: True)
    if periodo == "validazione":
        fine_c = int(C.FINE_COSTRUZIONE_TS)
        escl = escl | np.array([c.ts <= fine_c for c in s.last])
        filtro = (lambda ts: ts > fine_c)
    return Quadro(s.last, s.mark, list(s.funding), int(C.ms_tf(tf)), C.fabbrica(s, costr), C.fabbrica_casuale(s, costr),
                  C.fabbrica_segnale(s, costr), C.PARAMETRI, C.come_intervalli(escl), filtro,
                  {"tf": tf, "direzione": "short", "serie": "30m aggregati dai 15m (come la campagna)",
                   "mesi_esclusi": str(sorted(C.MESI_ESCLUSI))})


def _avax(nome: str, periodo: str) -> Quadro:
    import comune as C
    import varianti
    var = varianti.VARIANTI["V-12"]
    ctx = C.contesto(var.tf, "costruzione" if periodo == "costruzione" else "completo")
    crea, _crea_a, crea_casuale, crea_segnale = C.fabbriche(var, ctx)
    extra = C.intervalli(ctx.illiquido)
    filtro = (lambda ts: True)
    if periodo == "validazione":
        da = int(C.PER["inizio_validazione_ts"])
        primo = int(np.searchsorted(ctx.ts, da))
        extra = extra + [(0, primo)]
        filtro = (lambda ts: ts >= da)
    return Quadro(ctx.candele, ctx.mark, list(ctx.funding), int(ctx.ms), crea, crea_casuale, crea_segnale, C.PARAMETRI,
                  extra, filtro, {"tf": var.tf, "direzione": var.direzione, "serie": "file nativi " + var.tf,
                                  "mesi_esclusi": str(C.mesi_illiquidi())})


def _fil(nome: str, periodo: str) -> Quadro:
    import comune as C
    import quadro as Q
    import varianti
    v = varianti.TUTTE[nome]()
    s = Q.carica(v.tf, "costruzione" if periodo == "costruzione" else "validazione")
    k = Q.calcola(v, s)
    par = C.parametri()
    vietata = ~s.ammessa.copy()
    filtro = (lambda ts: True)
    if periodo == "validazione":
        fine_c = int(C.PERIODI["fine_costruzione_ts"])
        primo = int(np.searchsorted(s.ts, fine_c + 1))
        vietata[:primo] = True
        filtro = (lambda ts: ts > fine_c)
    return Quadro(s.candele, s.mark, list(s.funding), int(Q.MS[v.tf]), Q.fabbrica_strategia(k), Q.fabbrica_casuale(k),
                  Q.fabbrica_segnale(k), par, Q.intervalli_da_maschera(vietata), filtro,
                  {"tf": v.tf, "direzione": v.direzione, "serie": "file nativi " + v.tf, "mesi_esclusi": str(Q.mesi_esclusi())})


def _dydx(nome: str, periodo: str) -> Quadro:
    import comune as C
    import varianti
    crea_spec = varianti.CREA["I08_long"]
    fine = C.FINE_COSTRUZIONE if periodo == "costruzione" else C.FINE_VALIDAZIONE
    ctx = C.contesto("1h", fine)
    par = C.parametri()
    maschera = ctx.vietata_liquidita.copy()
    filtro = (lambda ts: True)
    if periodo == "validazione":
        da = int(C.INIZIO_VALIDAZIONE_TS)
        maschera |= ctx.ts < da
        filtro = (lambda ts: ts >= da)
    return Quadro(ctx.candele, ctx.candele_mark, list(ctx.funding), int(ctx.ms), C.fabbrica(ctx, crea_spec),
                  C.fabbrica_casuale(ctx, crea_spec), C.fabbrica_segnale(ctx, crea_spec), par,
                  C.intervalli_da_maschera(maschera), filtro,
                  {"tf": "1h", "direzione": "long", "serie": "file nativi 1h", "mesi_esclusi": str(C.mesi_illiquidi())})


ADATTATORI = {"BTCUSDT": _btc, "BNBUSDT": _bnb, "ADAUSDT": _ada, "ETCUSDT": _etc, "SOLUSDT": _sol,
              "AVAXUSDT": _avax, "FILUSDT": _fil, "DYDXUSDT": _dydx}


# ---------------------------------------------------------------------------
# Le corse
# ---------------------------------------------------------------------------
def parametri_limite(par: Parametri, **cambi) -> Parametri:
    """I parametri della regola della sezione 4 a partire da quelli (a mercato) della campagna."""
    base = dict(ingresso="limite", limite_validita_barre=1, limite_condizione="attraversato",
                commissione_maker_per_lato=MAKER)
    base.update(cambi)
    return dataclasses.replace(par, **base)


def trade_compatto(t) -> Dict[str, object]:
    return {"ts_segnale": t.ts_segnale, "ts_entrata": t.ts_entrata, "ts_uscita": t.ts_uscita, "dir": t.direzione,
            "entrata": t.entrata, "uscita": t.uscita, "stop": t.stop, "esito": t.esito, "r": t.r,
            "lordo_r": t.pnl_lordo / t.rischio_iniziale if t.rischio_iniziale > 0 else 0.0,
            "costo_r": (t.commissioni + t.slippage_costo) / t.rischio_iniziale if t.rischio_iniziale > 0 else 0.0,
            "funding_r": t.funding_pagato / t.rischio_iniziale if t.rischio_iniziale > 0 else 0.0,
            "pnl": t.pnl, "ingresso": t.ingresso_tipo, "limite": t.limite_prezzo, "attesa": t.barre_attesa,
            "uscita_tipo": t.uscita_tipo, "ridotto": t.ridotto}


def misure(trades, ris, saltati, ms: int, a_limite: bool) -> Dict[str, object]:
    """Le misure della sezione 6 su una corsa (trade gia' filtrati per periodo e ordinati per uscita)."""
    n = len(trades)
    r = np.array([t.r for t in trades], dtype=float)
    lordo = np.array([t.pnl_lordo / t.rischio_iniziale for t in trades], dtype=float)
    comm = np.array([t.commissioni / t.rischio_iniziale for t in trades], dtype=float)
    slip = np.array([t.slippage_costo / t.rischio_iniziale for t in trades], dtype=float)
    fund = np.array([t.funding_pagato / t.rischio_iniziale for t in trades], dtype=float)
    pnl = [t.pnl for t in trades]
    per_anno: Dict[str, List[int]] = {}
    for k, t in enumerate(trades):
        per_anno.setdefault(_anno(t.ts_uscita), []).append(k)
    n_saltati = len(saltati)
    m = {
        "trade": n,
        "saltati": n_saltati,
        "segnali": n + n_saltati,
        "tasso_esecuzione": (n / (n + n_saltati)) if (n + n_saltati) else None,
        "ordini_limite_totali_serie": ris.n_ordini_limite,
        "sostituiti_totali_serie": ris.n_sostituiti,
        "uscite_limite_eseguite_totali_serie": ris.n_uscite_limite_eseguite,
        "uscite_limite_mancate_totali_serie": ris.n_uscite_limite_mancate,
        "segnali_non_validi_totali_serie": ris.n_segnali_non_validi,
        "r_medio": float(r.mean()) if n else None,
        "r_lordo_medio": float(lordo.mean()) if n else None,
        "costo_medio_r": float((comm + slip).mean()) if n else None,
        "commissioni_medie_r": float(comm.mean()) if n else None,
        "slippage_medio_r": float(slip.mean()) if n else None,
        "funding_medio_r": float(fund.mean()) if n else None,
        "costi_totali_usdt": float(sum(t.commissioni + t.slippage_costo for t in trades)),
        "pnl_lordo_totale_usdt": float(sum(t.pnl_lordo for t in trades)),
        "pnl_netto_totale_usdt": float(sum(pnl)),
        "profit_factor": statistica.profit_factor(pnl) if n else None,
        "r_medio_senza_3_migliori": float(np.sort(r)[:-3].mean()) if n > 3 else None,
        "win_rate": statistica.win_rate(pnl) if n else None,
        "esiti": {e: sum(1 for t in trades if t.esito == e) for e in ("stop", "target", "segnale", "liquidazione", "fine_dati")},
        "ridotti_tetto_leva": sum(1 for t in trades if t.ridotto),
        "r_medio_per_anno": {a: float(r[idx].mean()) for a, idx in sorted(per_anno.items())},
        "r_lordo_medio_per_anno": {a: float(lordo[idx].mean()) for a, idx in sorted(per_anno.items())},
        "costo_medio_r_per_anno": {a: float((comm + slip)[idx].mean()) for a, idx in sorted(per_anno.items())},
        "trade_per_anno": {a: len(idx) for a, idx in sorted(per_anno.items())},
        "durata_media_barre": motore.durata_media_barre(trades, ms) if n else None,
    }
    if a_limite:
        attese = [t.barre_attesa for t in trades]
        m["barre_attesa_media"] = float(np.mean(attese)) if n else None
        m["riempiti_oltre_prima_barra"] = sum(1 for t in trades if t.barre_attesa > 1)
        m["uscite_a_limite"] = sum(1 for t in trades if t.uscita_tipo == "limite")
        m["saltati_per_anno"] = {}
        for s in saltati:
            a = _anno(s["ts_segnale"])
            m["saltati_per_anno"][a] = m["saltati_per_anno"].get(a, 0) + 1
    return m


def corsa(q: Quadro, par: Parametri):
    ris = motore.esegui(q.candele, None, q.mark, q.funding, q.fabbrica(), par)
    trades = sorted([t for t in ris.trades if q.filtro_ts(t.ts_entrata)], key=lambda t: t.ts_uscita)
    saltati = [s for s in ris.saltati if q.filtro_ts(int(s["ts_segnale"]) + q.ms)]
    return ris, trades, saltati


def baseline_b(q: Quadro, par: Parametri, n_trade: int, durata: int, vietate: Sequence[Tuple[int, int]]):
    return motore.simula_baseline_casuale(q.candele, q.fabbrica_casuale, n_trade, durata, par, None, q.mark, q.funding,
                                          list(vietate), n_simulazioni=N_SIM, primo_seme=PRIMO_SEME)


def riassunto_b(base: Dict[str, object], cmp_: Dict[str, object], r_medio: float) -> Dict[str, object]:
    tps = base.get("trade_per_simulazione", [])
    return {
        "media": base["media"], "errore_standard": base["errore_standard"], "percentile_90": base.get("percentile_90"),
        "n_simulazioni": base["n_simulazioni"], "simulazioni_vuote": base.get("simulazioni_vuote"),
        "trade_per_simulazione_medio": float(np.mean(tps)) if len(tps) else None,
        "trade_per_simulazione_min": int(min(tps)) if len(tps) else None,
        "segnali_non_validi_per_simulazione_medio": float(np.mean(base.get("segnali_non_validi_per_simulazione", [0]))),
        "percentile_candidato": statistica.percentile_del_candidato(r_medio, base["valori"]),
        "confronto": {k: cmp_.get(k) for k in ("differenza", "errore_standard", "errore_minimo", "t", "soglia", "netta",
                                               "p_value", "valutabile", "n_blocchi")},
    }


def esegui_periodo(nome: str, periodo: str, log: Callable[[str], None]) -> Dict[str, object]:
    t0 = time.time()
    q = ADATTATORI[nome.split("-")[0]](nome, periodo)
    log(f"[{periodo}] barre {len(q.candele)}, funding {len(q.funding)}, vietate extra {sum(b - a for a, b in q.vietate_extra)} "
        f"({len(q.vietate_extra)} intervalli); note {q.note}; caricamento {time.time() - t0:.0f}s")
    out: Dict[str, object] = {"periodo": periodo, "n_barre": len(q.candele), "n_funding": len(q.funding), "note": q.note,
                              "parametri_M": pulito(dataclasses.asdict(q.par)),
                              "parametri_L": pulito(dataclasses.asdict(parametri_limite(q.par)))}

    # ---- M: esecuzione a mercato, come nella campagna ---------------------------------------
    t1 = time.time()
    ris_m, tr_m, salt_m = corsa(q, q.par)
    mis_m = misure(tr_m, ris_m, salt_m, q.ms, a_limite=False)
    out["M"] = {"misure": mis_m, "secondi_corsa": round(time.time() - t1, 1)}
    log(f"[{periodo}] M: trade {mis_m['trade']}, R {mis_m['r_medio']}, PF {mis_m['profit_factor']}, "
        f"costo {mis_m['costo_medio_r']}, {out['M']['secondi_corsa']}s")
    if len(tr_m) < 2:
        out["M"]["commento"] = "meno di 2 trade: nessuna baseline"
        out["stato"] = "troppo pochi trade in M"
        return out
    r_m = [t.r for t in tr_m]
    blocco_m = statistica.lunghezza_blocco([t.ts_entrata for t in tr_m], [t.ts_uscita for t in tr_m])
    durata_m = motore.durata_media_barre(tr_m, q.ms)
    t1 = time.time()
    vietate_segnale = motore.barre_vietate_segnale_non_valido(q.candele, q.fabbrica_segnale, q.par)
    vietate = list(vietate_segnale) + list(q.vietate_extra)
    quota_vietate_segnale = sum(b - a for a, b in vietate_segnale) / len(q.candele)
    out["M"].update({"blocco": blocco_m, "durata_media_barre": durata_m,
                     "quota_barre_vietate_segnale": quota_vietate_segnale,
                     "secondi_barre_vietate": round(time.time() - t1, 1)})
    t1 = time.time()
    base_bm = baseline_b(q, q.par, len(tr_m), durata_m, vietate)
    cmp_bm = statistica.contro_baseline(r_m, blocco_m, base_bm, BOOT_N, BOOT_SEME)
    out["M"]["baseline_b"] = riassunto_b(base_bm, cmp_bm, float(np.mean(r_m)))
    out["M"]["secondi_baseline"] = round(time.time() - t1, 1)
    log(f"[{periodo}] (b)-M: media {base_bm['media']:.6f}, t {cmp_bm['t']:.6f}, p {cmp_bm['p_value']:.6g}, "
        f"tps {np.mean(base_bm['trade_per_simulazione']):.2f}, {out['M']['secondi_baseline']}s")

    # ---- parita' con il log della campagna ----------------------------------------------------
    attesi = PARITA.get(nome, {}).get(periodo)
    if attesi is not None:
        trovati = {"trade": mis_m["trade"], "r_medio": mis_m["r_medio"], "profit_factor": mis_m["profit_factor"],
                   "b_media": base_bm["media"], "t": cmp_bm["t"], "p_value": cmp_bm["p_value"], "durata": durata_m,
                   "tps": float(np.mean(base_bm["trade_per_simulazione"]))}
        differenze = confronta_parita(attesi, trovati)
        out["parita"] = {"fonte": attesi["fonte"], "attesi": attesi, "trovati": pulito(trovati),
                         "differenze": pulito(differenze), "passata": not differenze}
        log(f"[{periodo}] PARITA' {'PASSATA' if not differenze else 'FALLITA: ' + json.dumps(pulito(differenze))}")
        if differenze:
            out["stato"] = "parita' fallita: STOP (regole.md, sezione 5 punto 1)"
            out["M"]["trade_elenco"] = [trade_compatto(t) for t in tr_m]
            return out
    else:
        out["parita"] = {"fonte": None, "nota": "nessun numero di campagna per questo periodo: non si confronta"}

    # ---- L: la regola della sezione 4 -------------------------------------------------------------
    par_l = parametri_limite(q.par)
    t1 = time.time()
    ris_l, tr_l, salt_l = corsa(q, par_l)
    mis_l = misure(tr_l, ris_l, salt_l, q.ms, a_limite=True)
    out["L"] = {"misure": mis_l, "secondi_corsa": round(time.time() - t1, 1)}
    log(f"[{periodo}] L: trade {mis_l['trade']}, saltati {mis_l['saltati']}, tasso {mis_l['tasso_esecuzione']}, "
        f"R {mis_l['r_medio']}, lordo {mis_l['r_lordo_medio']}, costo {mis_l['costo_medio_r']}, {out['L']['secondi_corsa']}s")
    if len(tr_l) >= 2:
        r_l = [t.r for t in tr_l]
        blocco_l = statistica.lunghezza_blocco([t.ts_entrata for t in tr_l], [t.ts_uscita for t in tr_l])
        out["L"]["blocco"] = blocco_l
        t1 = time.time()
        # (b)-L: STESSI ingressi casuali della (b)-M (stesso n, stessa distanza, stesse barre vietate, stessi semi),
        # eseguiti con la regola limite: anche il caso salta i trade e risparmia i costi.
        base_bl = baseline_b(q, par_l, len(tr_m), durata_m, vietate)
        cmp_bl = statistica.contro_baseline(r_l, blocco_l, base_bl, BOOT_N, BOOT_SEME)
        out["L"]["baseline_b"] = riassunto_b(base_bl, cmp_bl, float(np.mean(r_l)))
        out["L"]["secondi_baseline"] = round(time.time() - t1, 1)
        log(f"[{periodo}] (b)-L: media {base_bl['media']:.6f}, t {cmp_bl['t']:.6f}, p {cmp_bl['p_value']:.6g}, "
            f"tps {np.mean(base_bl['trade_per_simulazione']):.2f}, {out['L']['secondi_baseline']}s")
    else:
        out["L"]["commento"] = "meno di 2 trade in L: nessuna baseline"

    # ---- i trade di M che in L saltano, e il confronto segnale per segnale -------------------------
    m_per_segnale = {t.ts_segnale: t for t in tr_m}
    l_per_segnale = {t.ts_segnale: t for t in tr_l}
    saltati_ts = {int(s["ts_segnale"]) for s in salt_l}
    comuni = [ts for ts in m_per_segnale if ts in l_per_segnale]
    saltati_in_m = [m_per_segnale[ts] for ts in saltati_ts if ts in m_per_segnale]
    solo_m = [ts for ts in m_per_segnale if ts not in l_per_segnale and ts not in saltati_ts]
    solo_l = [ts for ts in l_per_segnale if ts not in m_per_segnale]
    out["confronto_segnali"] = {
        "segnali_in_M": len(m_per_segnale), "segnali_in_L_eseguiti": len(l_per_segnale),
        "comuni": len(comuni), "saltati_in_L_presenti_in_M": len(saltati_in_m),
        "saltati_in_L_assenti_in_M": len(saltati_ts) - len(saltati_in_m),
        "solo_in_M": len(solo_m), "solo_in_L": len(solo_l),
        "r_medio_M_dei_saltati": float(np.mean([t.r for t in saltati_in_m])) if saltati_in_m else None,
        "r_lordo_medio_M_dei_saltati": float(np.mean([t.pnl_lordo / t.rischio_iniziale for t in saltati_in_m])) if saltati_in_m else None,
        "r_medio_M_dei_comuni": float(np.mean([m_per_segnale[ts].r for ts in comuni])) if comuni else None,
        "r_medio_L_dei_comuni": float(np.mean([l_per_segnale[ts].r for ts in comuni])) if comuni else None,
        "r_lordo_medio_M_dei_comuni": float(np.mean([m_per_segnale[ts].pnl_lordo / m_per_segnale[ts].rischio_iniziale for ts in comuni])) if comuni else None,
        "r_lordo_medio_L_dei_comuni": float(np.mean([l_per_segnale[ts].pnl_lordo / l_per_segnale[ts].rischio_iniziale for ts in comuni])) if comuni else None,
    }
    log(f"[{periodo}] saltati presenti in M {len(saltati_in_m)}: R medio in M {out['confronto_segnali']['r_medio_M_dei_saltati']}; "
        f"comuni {len(comuni)}, solo M {len(solo_m)}, solo L {len(solo_l)}")

    # ---- varianti della sezione 4.6, solo in L, senza baseline --------------------------------------
    out["varianti"] = {}
    for etichetta, cambi in (("a_toccato", {"limite_condizione": "toccato"}),
                             ("b_validita_2_barre", {"limite_validita_barre": 2}),
                             ("c_uscite_segnale_a_limite", {"uscita_segnale": "limite"})):
        t1 = time.time()
        ris_v, tr_v, salt_v = corsa(q, parametri_limite(q.par, **cambi))
        mis_v = misure(tr_v, ris_v, salt_v, q.ms, a_limite=True)
        out["varianti"][etichetta] = {"cambi": cambi, "misure": mis_v, "secondi_corsa": round(time.time() - t1, 1),
                                      "trade_elenco": [trade_compatto(t) for t in tr_v]}
        log(f"[{periodo}] variante {etichetta}: trade {mis_v['trade']}, saltati {mis_v['saltati']}, tasso {mis_v['tasso_esecuzione']}, "
            f"R {mis_v['r_medio']}, lordo {mis_v['r_lordo_medio']}, costo {mis_v['costo_medio_r']}")

    out["M"]["trade_elenco"] = [trade_compatto(t) for t in tr_m]
    out["L"]["trade_elenco"] = [trade_compatto(t) for t in tr_l]
    out["L"]["saltati_elenco"] = pulito(salt_l)
    out["stato"] = "completo"
    out["secondi_periodo"] = round(time.time() - t0, 1)
    return out


def esegui_strategia(nome: str, periodi: Sequence[str]) -> int:
    ESITI.mkdir(parents=True, exist_ok=True)
    log_path = ESITI / f"{nome}.log"
    json_path = ESITI / f"{nome}.json"

    def log(msg: str) -> None:
        riga = f"{adesso()} {nome} {msg}"
        print(riga, flush=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(riga + "\n")

    sys.path.insert(0, str(_cartella_codice(nome)))
    esito: Dict[str, object] = {"strategia": nome, "campagna": nome.split("-")[0], "inizio": adesso(),
                                "commit": commit_corrente(), "impronte": impronte(), "python": sys.version.split()[0],
                                "numpy": np.__version__, "n_simulazioni": N_SIM, "semi": [PRIMO_SEME, PRIMO_SEME + N_SIM - 1],
                                "bootstrap": [BOOT_N, BOOT_SEME], "periodi": {}}
    log(f"inizio; commit {esito['commit'][:12]}; impronte " + ", ".join(f"{k} {v[:12]}" for k, v in esito["impronte"].items()))
    codice = 0
    for periodo in periodi:
        try:
            esito["periodi"][periodo] = esegui_periodo(nome, periodo, log)
            if not str(esito["periodi"][periodo].get("stato", "")).startswith("completo"):
                codice = 2
                log(f"[{periodo}] FERMO: {esito['periodi'][periodo].get('stato')}")
                if "parita" in str(esito["periodi"][periodo].get("stato", "")):
                    esito["stato"] = "parita' fallita"
                    break
        except Exception as e:  # il file degli esiti deve dire cosa e' successo
            esito["periodi"][periodo] = {"periodo": periodo, "stato": "errore", "errore": repr(e),
                                         "traceback": traceback.format_exc()}
            log(f"[{periodo}] ERRORE {e!r}\n{traceback.format_exc()}")
            codice = 1
            break
        finally:
            esito["fine"] = adesso()
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(pulito(esito), f, ensure_ascii=False, indent=1)
    if "stato" not in esito:
        esito["stato"] = "completo" if codice == 0 else "incompleto"
    esito["fine"] = adesso()
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(pulito(esito), f, ensure_ascii=False, indent=1)
    log(f"fine: {esito['stato']}")
    return codice


# ---------------------------------------------------------------------------
# Tutte le strategie, in processi separati
# ---------------------------------------------------------------------------
def esegui_tutte(nomi: Sequence[str], processi: int, periodi: Sequence[str]) -> int:
    ESITI.mkdir(parents=True, exist_ok=True)
    coda = list(nomi)
    attivi: Dict[str, subprocess.Popen] = {}
    codici: Dict[str, int] = {}
    env = dict(os.environ, PYTHONPATH=str(RADICE), OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    while coda or attivi:
        while coda and len(attivi) < processi:
            nome = coda.pop(0)
            uscita = open(ESITI / f"{nome}.out", "a", encoding="utf-8")
            attivi[nome] = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), nome, "--periodi", ",".join(periodi)],
                                            cwd=RADICE, env=env, stdout=uscita, stderr=subprocess.STDOUT)
            print(f"{adesso()} avviata {nome} (pid {attivi[nome].pid})", flush=True)
        time.sleep(5)
        for nome, p in list(attivi.items()):
            if p.poll() is not None:
                codici[nome] = p.returncode
                print(f"{adesso()} finita {nome}: codice {p.returncode}", flush=True)
                del attivi[nome]
    print(json.dumps(codici, indent=1))
    return 0 if all(c == 0 for c in codici.values()) else 1


# ---------------------------------------------------------------------------
# Il riassunto per risultati.md
# ---------------------------------------------------------------------------
def _f(x, d: int = 4) -> str:
    if x is None:
        return "—"
    if isinstance(x, str):
        return x
    return f"{x:+.{d}f}" if d else f"{x:.0f}"


def _p(x) -> str:
    return "—" if x is None else f"{100 * x:.0f}%"


def _mediana(valori: Sequence[Optional[float]]) -> Optional[float]:
    v = [x for x in valori if x is not None]
    return float(np.median(v)) if v else None


def riassunto() -> str:
    esiti = {}
    for nome in STRATEGIE:
        p = ESITI / f"{nome}.json"
        if p.is_file():
            with open(p, encoding="utf-8") as f:
                esiti[nome] = json.load(f)
    righe: List[str] = []
    righe.append("## 3. Impronte al lancio\n")
    righe.append("| Strategia | Commit | motore.py | dati.py | statistica.py | parametri.yaml | prova.py | regole.md | Inizio | Fine | Stato |")
    righe.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for nome, e in esiti.items():
        imp = e.get("impronte", {})
        righe.append(f"| {nome} | {e.get('commit', '?')[:12]} | " + " | ".join(imp.get(k, '?')[:12] for k in
                     ("motore.py", "dati.py", "statistica.py", "parametri.yaml", "prova.py", "regole.md")) +
                     f" | {e.get('inizio', '')} | {e.get('fine', '')} | {e.get('stato', '')} |")
    righe.append("")
    righe.append("## 4. Parità M (sezione 5, punto 1)\n")
    righe.append("| Strategia | Periodo | Fonte | Trade | R medio | PF | (b) media | t | p | Esito |")
    righe.append("|---|---|---|---|---|---|---|---|---|---|")
    for nome, e in esiti.items():
        for periodo, pe in e.get("periodi", {}).items():
            pa = pe.get("parita") or {}
            if not pa.get("fonte"):
                continue
            a, t = pa["attesi"], pa["trovati"]
            righe.append(f"| {nome} | {periodo} | {a['fonte']} | {a['trade']} / {t['trade']} | {a['r_medio']} / {t['r_medio']:.6g} | "
                         f"{a['profit_factor']} / {t['profit_factor']:.6g} | {a['b_media']} / {t['b_media']:.6g} | {a['t']} / {t['t']:.6g} | "
                         f"{a['p_value']} / {t['p_value']:.6g} | {'PASSATA' if pa['passata'] else 'FALLITA: ' + ', '.join(d['chiave'] for d in pa['differenze'])} |")
    righe.append("\nOgni cella: numero del log della campagna / numero rifatto oggi. Tolleranza: metà dell'ultima cifra del log.\n")

    for periodo in PERIODI:
        righe.append(f"## 5.{PERIODI.index(periodo) + 1}. Le corse — periodo «{periodo}»\n")
        righe.append("| Strategia | M trade | L eseguiti / saltati | tasso | R netto M / L | R lordo M / L | costo M / L | risparmio | R in M dei saltati | t vs (b): M / L | PF M / L | senza 3 M / L |")
        righe.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for nome, e in esiti.items():
            pe = e.get("periodi", {}).get(periodo)
            if not pe or "L" not in pe:
                stato = (pe or {}).get("stato", "non eseguito")
                righe.append(f"| {nome} | {stato} | | | | | | | | | | |")
                continue
            m, l = pe["M"]["misure"], pe["L"]["misure"]
            cb_m = (pe["M"].get("baseline_b") or {}).get("confronto", {})
            cb_l = (pe["L"].get("baseline_b") or {}).get("confronto", {})
            cs = pe.get("confronto_segnali", {})
            risparmio = (m["costo_medio_r"] - l["costo_medio_r"]) if (m["costo_medio_r"] is not None and l["costo_medio_r"] is not None) else None
            righe.append(f"| {nome} | {m['trade']} | {l['trade']} / {l['saltati']} | {_p(l['tasso_esecuzione'])} | "
                         f"{_f(m['r_medio'])} / {_f(l['r_medio'])} | {_f(m['r_lordo_medio'])} / {_f(l['r_lordo_medio'])} | "
                         f"{_f(m['costo_medio_r'])} / {_f(l['costo_medio_r'])} | {_f(risparmio)} | {_f(cs.get('r_medio_M_dei_saltati'))} ({cs.get('saltati_in_L_presenti_in_M', 0)}) | "
                         f"{_f(cb_m.get('t'), 2)} / {_f(cb_l.get('t'), 2)} | {_f(m['profit_factor'], 3)} / {_f(l['profit_factor'], 3)} | "
                         f"{_f(m['r_medio_senza_3_migliori'])} / {_f(l['r_medio_senza_3_migliori'])} |")
        righe.append("")
        righe.append(f"Varianti della sezione 4.6, periodo «{periodo}», solo in L (si riportano, non decidono):\n")
        righe.append("| Strategia | (a) toccato: eseguiti/saltati, tasso, R netto, lordo, costo | (b) due barre: eseguiti/saltati, tasso, R netto, lordo, costo | (c) uscite a limite: eseguiti, uscite a limite, R netto, lordo, costo |")
        righe.append("|---|---|---|---|")
        for nome, e in esiti.items():
            pe = e.get("periodi", {}).get(periodo)
            if not pe or "varianti" not in pe:
                continue
            v = pe["varianti"]
            a, b, c = v["a_toccato"]["misure"], v["b_validita_2_barre"]["misure"], v["c_uscite_segnale_a_limite"]["misure"]
            righe.append(f"| {nome} | {a['trade']}/{a['saltati']}, {_p(a['tasso_esecuzione'])}, {_f(a['r_medio'])}, {_f(a['r_lordo_medio'])}, {_f(a['costo_medio_r'])} | "
                         f"{b['trade']}/{b['saltati']}, {_p(b['tasso_esecuzione'])}, {_f(b['r_medio'])}, {_f(b['r_lordo_medio'])}, {_f(b['costo_medio_r'])} | "
                         f"{c['trade']}, {c.get('uscite_a_limite')}, {_f(c['r_medio'])}, {_f(c['r_lordo_medio'])}, {_f(c['costo_medio_r'])} |")
        righe.append("")

    # per anno, periodo intero
    righe.append("## 6. R medio per anno (periodo intero 2020-2023), M / L\n")
    anni = ["2020", "2021", "2022", "2023"]
    righe.append("| Strategia | " + " | ".join(f"{a}: R netto M / L (trade M / L)" for a in anni) + " |")
    righe.append("|---|" + "---|" * len(anni))
    for nome, e in esiti.items():
        pe = e.get("periodi", {}).get("intero")
        if not pe or "L" not in pe:
            continue
        m, l = pe["M"]["misure"], pe["L"]["misure"]
        celle = []
        for a in anni:
            if a in m["trade_per_anno"] or a in l["trade_per_anno"]:
                celle.append(f"{_f(m['r_medio_per_anno'].get(a))} / {_f(l['r_medio_per_anno'].get(a))} "
                             f"({m['trade_per_anno'].get(a, 0)} / {l['trade_per_anno'].get(a, 0)})")
            else:
                celle.append("—")
        righe.append(f"| {nome} | " + " | ".join(celle) + " |")
    righe.append("")

    # soglie E1-E3 sulle mediane (periodo intero)
    righe.append("## 7. Le soglie E1, E2, E3 (sezione 7), sulle mediane delle strategie — periodo intero\n")
    tassi, risparmi, diff_lordo, nomi_ok = [], [], [], []
    for nome, e in esiti.items():
        pe = e.get("periodi", {}).get("intero")
        if not pe or "L" not in pe:
            continue
        m, l = pe["M"]["misure"], pe["L"]["misure"]
        if l["tasso_esecuzione"] is None or m["costo_medio_r"] is None or l["costo_medio_r"] is None:
            continue
        nomi_ok.append(nome)
        tassi.append(l["tasso_esecuzione"])
        risparmi.append(m["costo_medio_r"] - l["costo_medio_r"])
        diff_lordo.append((l["r_lordo_medio"] or 0.0) - (m["r_lordo_medio"] or 0.0))
    med_tasso, med_risp, med_diff = _mediana(tassi), _mediana(risparmi), _mediana(diff_lordo)
    righe.append(f"Strategie con L completa: {len(nomi_ok)} su {len(STRATEGIE)} ({', '.join(nomi_ok)}).\n")
    if nomi_ok:
        e1 = med_tasso >= 0.70
        non_eseguibile = med_tasso < 0.50
        e2 = med_risp >= 0.04
        e3 = med_diff >= -0.5 * med_risp
        righe.append(f"* **E1, eseguibile**: tasso di esecuzione mediano {100 * med_tasso:.1f}% (soglia 70%; sotto il 50% «non eseguibile») → {'vale' if e1 else 'cade'}{' — NON ESEGUIBILE' if non_eseguibile else ''}.")
        righe.append(f"* **E2, i costi scendono**: risparmio mediano del costo medio {med_risp:+.4f} R (soglia 0,04 R) → {'vale' if e2 else 'cade'}.")
        righe.append(f"* **E3, il lordo regge**: differenza mediana del lordo L − M {med_diff:+.4f} R, contro −0,5 × risparmio = {-0.5 * med_risp:+.4f} R → {'vale' if e3 else 'cade'}.")
        if non_eseguibile:
            esito = "non eseguibile"
        elif not e1:
            esito = "non eseguibile (E1 cade, tasso fra 50% e 70%)"
        elif not e3:
            esito = "non conviene"
        elif e2:
            esito = "conviene"
        else:
            esito = "conviene poco"
        righe.append(f"\n**Esito secondo le soglie scritte prima: «{esito}».**\n")
        righe.append("Mediane per strategia (periodo intero): tasso, risparmio, differenza del lordo:\n")
        for nome, t_, r_, d_ in zip(nomi_ok, tassi, risparmi, diff_lordo):
            righe.append(f"* {nome}: tasso {100 * t_:.1f}%, risparmio {r_:+.4f} R, lordo L − M {d_:+.4f} R")
        righe.append("")
    # informazione: quante strategie in L battono nettamente la (b)-L con R netto > 0 in validazione
    righe.append("## 8. Informazione, non promozione: in validazione, strategie con R netto > 0 che battono nettamente la (b)-L\n")
    conta, dettagli = 0, []
    for nome, e in esiti.items():
        pe = e.get("periodi", {}).get("validazione")
        if not pe or "L" not in pe:
            continue
        l = pe["L"]["misure"]
        cb = (pe["L"].get("baseline_b") or {}).get("confronto", {})
        m = pe["M"]["misure"]
        cbm = (pe["M"].get("baseline_b") or {}).get("confronto", {})
        ok = bool(l["r_medio"] is not None and l["r_medio"] > 0 and cb.get("netta"))
        conta += ok
        dettagli.append(f"* {nome}: M R {_f(m['r_medio'])} t {_f(cbm.get('t'), 2)} netta {cbm.get('netta')}; "
                        f"L R {_f(l['r_medio'])} t {_f(cb.get('t'), 2)} netta {cb.get('netta')} → {'sì' if ok else 'no'}")
    righe.append(f"{conta} strategie." + "\n")
    righe.extend(dettagli)
    righe.append("")
    return "\n".join(righe)


MARCATORE = "<!-- da qui in poi il testo e' generato da prova.py --riassunto: non modificare a mano -->"


def scrivi_riassunto() -> None:
    testo = riassunto()
    p = QUI / "risultati.md"
    vecchio = p.read_text(encoding="utf-8")
    testa = vecchio.split(MARCATORE)[0].rstrip() + "\n\n"
    p.write_text(testa + MARCATORE + "\n\n" + testo, encoding="utf-8")
    print(f"scritto {p} ({len(testo)} caratteri generati)")


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("strategia", nargs="?", help="una delle strategie della sezione 3")
    ap.add_argument("--tutte", action="store_true", help="tutte le strategie, in processi separati")
    ap.add_argument("--processi", type=int, default=4)
    ap.add_argument("--periodi", default=",".join(PERIODI), help="costruzione,validazione,intero")
    ap.add_argument("--riassunto", action="store_true", help="scrive le tabelle in risultati.md dagli esiti")
    args = ap.parse_args(argv)
    periodi = [p.strip() for p in args.periodi.split(",") if p.strip()]
    for p in periodi:
        if p not in PERIODI:
            ap.error(f"periodo sconosciuto: {p}")
    if args.riassunto:
        scrivi_riassunto()
        return 0
    if args.tutte:
        return esegui_tutte(STRATEGIE, args.processi, periodi)
    if not args.strategia:
        ap.error("serve una strategia, --tutte o --riassunto")
    if args.strategia not in STRATEGIE:
        ap.error(f"strategia sconosciuta: {args.strategia} (ammesse: {', '.join(STRATEGIE)})")
    return esegui_strategia(args.strategia, periodi)


if __name__ == "__main__":
    sys.exit(main())
