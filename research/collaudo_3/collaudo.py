"""Il collaudo del metodo del protocollo 3 (``research/PROTOCOLLO_3.md``, sezione 13bis).

Uso (dalla radice del repository)::

    python3 research/collaudo_3/collaudo.py stima        # tempo di calcolo stimato (prima del lancio)
    python3 research/collaudo_3/collaudo.py a            # prova A: prezzi rimescolati
    python3 research/collaudo_3/collaudo.py b            # prova B: vantaggio inserito apposta
    python3 research/collaudo_3/collaudo.py impronte     # impronte SHA-256 degli strumenti

Le regole che il testo lascia aperte sono in ``research/collaudo_3/regole.md``, committato prima
del primo calcolo. Gli esiti grezzi vanno in ``research/collaudo_3/esiti/giro<N>/`` (una riga JSON
per prova), il riepilogo in ``research/collaudo_3/esiti.md``.

Il collaudo usa solo le candele del periodo di costruzione (fino al 2022-09-30), con la direzione
di ogni candela girata a caso (dal secondo giro, correzione 2): nessun dato di validazione o del
vault, nessuna variante consumata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

RADICE = Path(__file__).resolve().parents[2]
if str(RADICE) not in sys.path:
    sys.path.insert(0, str(RADICE))

from research.src import catalogo3 as cat  # noqa: E402
from research.src import dati  # noqa: E402
from research.src.motore3 import Regole, esegui, metriche, stima_trade  # noqa: E402
from research.src.statistica3 import SimulazioneImpossibile, fase2, fase4  # noqa: E402

CARTELLA = Path(__file__).resolve().parent
#: il giro del collaudo: il primo (16 ott) usava le candele rimescolate e le ampiezze 0 / 0,3 / 0,6;
#: dal secondo valgono le correzioni approvate il 17 ottobre 2026 (PROTOCOLLO_3.md, appendice 3); il terzo
#: rifa' A e B dopo la correzione del caricatore per i buchi del solo mark (appendice 3, punto 6)
GIRO = 3
ESITI = CARTELLA / "esiti" / f"giro{GIRO}"
INIZIO = date(2020, 1, 1)
FINE = date(2022, 9, 30)
N_SERIE = 30
SEME_A = 2026
N_VARIANTI_A = 100
TRADE_MINIMI = 150
AMPIEZZE_B = (0.0, 0.6, 1.2)
AMPIEZZA_RISERVA_B = 1.8
#: con questa ampiezza almeno 20 serie su 30 devono arrivare a 0,35 R, altrimenti si fa la riserva
AMPIEZZA_GUIDA_B = 1.2
CANDELE_VANTAGGIO = 12
CANDELE_RITORNO = 240

STRUMENTI = ("research/src/catalogo3.py", "research/src/motore3.py", "research/src/statistica3.py",
             "research/src/statistica.py", "research/src/dati.py", "research/src/guardiano.py",
             "research/config/parametri_3.yaml", "research/collaudo_3/collaudo.py",
             "research/collaudo_3/regole.md")


# ---------------------------------------------------------------------------
# 13bis.1 le serie senza vantaggio
# ---------------------------------------------------------------------------

_CACHE_VERE: Dict[str, cat.Serie] = {}


def serie_vera(tf: str) -> cat.Serie:
    """Le candele vere di BTCUSDT del periodo di costruzione (last, mark, funding)."""
    if tf not in _CACHE_VERE:
        _CACHE_VERE[tf] = dati.serie_3("BTCUSDT", tf, INIZIO, FINE)
    return _CACHE_VERE[tf]


def senza_direzione(s: cat.Serie, seme: int) -> cat.Serie:
    """13bis.1 (correzione 2 del collaudo): ogni candela dalla seconda si scompone nei suoi movimenti
    relativi, in logaritmo (salto dalla chiusura precedente all'apertura, chiusura, massimo e minimo
    sull'apertura, e le quattro candele mark sull'apertura del last); con il seme, ogni candela si
    gira o no, alla pari: cambiano segno salto e chiusura, e massimo e minimo si scambiano cambiati
    di segno (mark compreso). Le candele restano al loro posto, con il loro volume; il prezzo riparte
    dal primo prezzo vero; funding vero."""
    o, h, l, c = s.open, s.high, s.low, s.close
    g = np.log(o[1:] / c[:-1])
    b = np.log(c[1:] / o[1:])
    u = np.log(h[1:] / o[1:])
    d = np.log(l[1:] / o[1:])
    mo, mh, ml, mc = (np.log(x[1:] / o[1:]) for x in (s.mark_open, s.mark_high, s.mark_low, s.mark_close))
    gira = np.random.default_rng(seme).random(len(g)) < 0.5
    g2, b2 = np.where(gira, -g, g), np.where(gira, -b, b)
    u2, d2 = np.where(gira, -d, u), np.where(gira, -u, d)
    mo2, mc2 = np.where(gira, -mo, mo), np.where(gira, -mc, mc)
    mh2, ml2 = np.where(gira, -ml, mh), np.where(gira, -mh, ml)
    log_c = np.log(c[0]) + np.cumsum(g2 + b2)
    log_o = np.concatenate([[np.log(c[0])], log_c[:-1]]) + g2
    n_o = np.concatenate([[o[0]], np.exp(log_o)])
    n_c = np.concatenate([[c[0]], np.exp(log_c)])
    n_h = np.concatenate([[h[0]], np.exp(log_o + u2)])
    n_l = np.concatenate([[l[0]], np.exp(log_o + d2)])
    m_o = np.concatenate([[s.mark_open[0]], np.exp(log_o + mo2)])
    m_h = np.concatenate([[s.mark_high[0]], np.exp(log_o + mh2)])
    m_l = np.concatenate([[s.mark_low[0]], np.exp(log_o + ml2)])
    m_c = np.concatenate([[s.mark_close[0]], np.exp(log_o + mc2)])
    return cat.Serie(s.timeframe, s.ts.copy(), n_o, n_h, n_l, n_c, s.volume.copy(), m_o, m_h, m_l, m_c,
                     s.funding_ts.copy(), s.funding_tasso.copy())


def rimescola(s: cat.Serie, seme: int) -> cat.Serie:
    """Il primo giro del collaudo (16 ott): l'ordine delle candele mescolato. Resta per rileggere quel
    giro; dal secondo giro le serie sono ``senza_direzione``."""
    o, h, l, c = s.open, s.high, s.low, s.close
    salto = o[1:] / c[:-1]
    corpo = c[1:] / o[1:]
    su = h[1:] / o[1:]
    giu = l[1:] / o[1:]
    vol = s.volume[1:]
    mo, mh, ml, mc = (x[1:] / o[1:] for x in (s.mark_open, s.mark_high, s.mark_low, s.mark_close))
    perm = np.random.default_rng(seme).permutation(len(salto))
    salto, corpo, su, giu, vol = salto[perm], corpo[perm], su[perm], giu[perm], vol[perm]
    mo, mh, ml, mc = mo[perm], mh[perm], ml[perm], mc[perm]
    chiusure = c[0] * np.cumprod(salto * corpo)
    aperture = np.concatenate([[c[0]], chiusure[:-1]]) * salto
    return cat.Serie(s.timeframe, s.ts.copy(), np.concatenate([[o[0]], aperture]),
                     np.concatenate([[h[0]], aperture * su]), np.concatenate([[l[0]], aperture * giu]),
                     np.concatenate([[c[0]], chiusure]), np.concatenate([[s.volume[0]], vol]),
                     np.concatenate([[s.mark_open[0]], aperture * mo]), np.concatenate([[s.mark_high[0]], aperture * mh]),
                     np.concatenate([[s.mark_low[0]], aperture * ml]), np.concatenate([[s.mark_close[0]], aperture * mc]),
                     s.funding_ts.copy(), s.funding_tasso.copy())


def serie_rimescolata(tf: str, numero: int) -> cat.Serie:
    """La serie senza vantaggio ``numero`` (da 1 a 30) del timeframe: seme = numero. Dal secondo giro
    e' la serie con la direzione girata a caso (13bis.1, correzione 2); nel primo era l'ordine mescolato."""
    if not 1 <= numero <= N_SERIE:
        raise ValueError(numero)
    if GIRO == 1:
        return rimescola(serie_vera(tf), numero)
    return senza_direzione(serie_vera(tf), numero)


# ---------------------------------------------------------------------------
# 13bis.2 prova A: varianti finte estratte dal catalogo
# ---------------------------------------------------------------------------

_FILTRI = {
    "F1": lambda r: {"codice": "F1", "n": int(r.choice(cat.VALORI["F1_n"])), "lato": str(r.choice(["sopra", "sotto"]))},
    "F2": lambda r: {"codice": "F2", "regime": str(r.choice(["tendenza", "laterale"]))},
    "F3": lambda r: {"codice": "F3", "regime": str(r.choice(["alta", "bassa"]))},
    "F4": lambda r: {"codice": "F4", "lato": str(r.choice(["sopra", "sotto"]))},
    "F5": lambda r: {"codice": "F5", "sessione": str(r.choice(list(cat.SESSIONI)))},
    "F6": lambda r: {"codice": "F6", "giorni": str(r.choice(["feriali", "fine_settimana"]))},
    "F7": lambda r: {"codice": "F7", "lato": str(r.choice(["sopra", "sotto"]))},
}


def _e1(r):
    m, a, b = cat.COPPIE_E1[int(r.integers(len(cat.COPPIE_E1)))]
    return {"codice": "E1", "media": m, "veloce": a, "lenta": b}


def _e6(r):
    s = cat.VALORI["E6_soglie"][int(r.integers(2))]
    return {"codice": "E6", "n": int(r.choice(cat.VALORI["rsi_n"])), "soglie": [s[0], s[1]]}


_INGRESSI = {
    "E1": _e1,
    "E2": lambda r: {"codice": "E2", "media": str(r.choice(["EMA", "SMA"])), "n": int(r.choice(cat.VALORI["E2_n"]))},
    "E3": lambda r: {"codice": "E3", "n": int(r.choice(cat.VALORI["E3_n"]))},
    "E4": lambda r: {"codice": "E4", "k": float(r.choice(cat.VALORI["bollinger_k"]))},
    "E5": lambda r: {"codice": "E5", "k": float(r.choice(cat.VALORI["bollinger_k"]))},
    "E6": _e6,
    "E7": lambda r: {"codice": "E7", "n": int(r.choice(cat.VALORI["rsi_n"]))},
    "E8": lambda r: {"codice": "E8"},
    "E9": lambda r: {"codice": "E9"},
    "E10": lambda r: {"codice": "E10"},
    "E11": lambda r: {"codice": "E11", "soglia": float(r.choice(list(cat.VALORI["funding_soglie_alte"]) + list(cat.VALORI["funding_soglie_basse"])))},
    "E12": lambda r: {"codice": "E12", "soglia": float(r.choice(cat.VALORI["volume_soglie"]))},
}
_CONFERME = {
    "C1": lambda r: {"codice": "C1", "soglia": float(r.choice(cat.VALORI["volume_soglie"]))},
    "C2": lambda r: {"codice": "C2"},
    "C3": lambda r: {"codice": "C3"},
}
_STOP = {
    "S1": lambda r: {"codice": "S1", "k": float(r.choice(cat.VALORI["S1_k"]))},
    "S2": lambda r: {"codice": "S2", "n": int(r.choice(cat.VALORI["S2_n"]))},
    "S3": lambda r: {"codice": "S3", "pct": float(r.choice(cat.VALORI["S3_pct"]))},
}


def estrai_variante(r: np.random.Generator) -> dict:
    """Una variante finta completa, con le estrazioni descritte in ``regole.md`` (punto A.1)."""
    tf = str(r.choice(cat.TIMEFRAME))
    corto = tf in cat.TIMEFRAME_FINO_A_1H
    direzione = str(r.choice(["long", "short"]))
    filtri = ["nessuno"] + [f for f in _FILTRI if corto or f not in cat.SOLO_FINO_A_1H]
    scelto = str(r.choice(filtri))
    filtro = None if scelto == "nessuno" else _FILTRI[scelto](r)
    ingressi = [e for e in _INGRESSI if corto or e not in cat.SOLO_FINO_A_1H]
    ingresso = _INGRESSI[str(r.choice(ingressi))](r)
    scelta_c = str(r.choice(["nessuna"] + list(_CONFERME)))
    conferma = None if scelta_c == "nessuna" else _CONFERME[scelta_c](r)
    if str(r.choice(["M", "L"])) == "M":
        tipo = {"codice": "M"}
    else:
        tipo = {"codice": "L", "k": float(r.choice(cat.VALORI["L_k"])), "validita": int(r.choice(cat.VALORI["L_validita"]))}
    stop = _STOP[str(r.choice(list(_STOP)))](r)
    quante = int(r.choice([1, 2]))
    famiglie = list(r.choice(["target", "tempo", "trailing", "segnale_opposto"], size=quante, replace=False))
    uscite = []
    for f in famiglie:
        if f == "target":
            uscite.append({"codice": "U1", "k": float(r.choice(cat.VALORI["U1_k"]))})
        elif f == "tempo":
            if corto and str(r.choice(["U2", "U2s"])) == "U2s":
                uscite.append({"codice": "U2s"})
            else:
                uscite.append({"codice": "U2", "n": int(r.choice(cat.VALORI["U2_n"]))})
        elif f == "trailing":
            uscite.append({"codice": "U3", "k": float(r.choice(cat.VALORI["U3_k"]))})
        else:
            uscite.append({"codice": "U4"})
    v = {"timeframe": tf, "direzione": direzione, "filtro": filtro, "ingresso": ingresso, "conferma": conferma,
         "tipo_ingresso": tipo, "stop": stop, "uscite": uscite}
    cat.normalizza(v)  # deve essere una variante del catalogo
    return v


def _fase2_a(argomenti) -> dict:
    numero, variante, serie_n = argomenti
    t0 = time.time()
    s = serie_rimescolata(variante["timeframe"], serie_n)
    try:
        es = fase2(variante, s, 0, len(s) - 1)
    except SimulazioneImpossibile as e:
        return {"prova": "A", "numero": numero, "serie": serie_n, "variante": variante,
                "impossibile": str(e), "secondi": round(time.time() - t0, 1)}
    m = es["metriche"]
    riga = {"prova": "A", "numero": numero, "serie": serie_n, "variante": variante,
            "trade": m["trade"], "r_medio": m["r_medio"], "profit_factor": m["profit_factor"],
            "p_value": es["p_value"], "supera_fase2": es["supera"], "esiti": es["esiti"],
            "media_casuali": es["casuali"]["media"] if es["casuali"] else None,
            "secondi": round(time.time() - t0, 1)}
    if es["supera"]:
        def serie_di(tf):
            ss = serie_rimescolata(tf, serie_n)
            return ss, 0, len(ss) - 1
        f4 = fase4(variante, s, 0, len(s) - 1, serie_di, base=es)
        riga["fase4"] = _riassunto_fase4(f4)
    return riga


def _riassunto_fase4(f4: dict) -> dict:
    out = {"candidato": f4["candidato"]}
    for k, v in f4.items():
        if isinstance(v, dict):
            out[k] = {kk: vv for kk, vv in v.items() if kk in ("supera", "r_medio", "differenza", "positivi",
                                                                   "quota_massima", "violazioni", "trade")}
    return out


def prova_a(processi: int) -> None:
    """13bis.2. Una variante finta per cui le entrate casuali non trovano posto per tanti trade
    quanti i suoi (``SimulazioneImpossibile``) non ha un p-value: si riporta a parte e si
    sostituisce con le estrazioni successive dello stesso generatore (regole.md, A.2)."""
    ESITI.mkdir(exist_ok=True)
    uscita = ESITI / "prova_a.jsonl"
    estrazioni = ESITI / "prova_a_estrazioni.jsonl"
    rng = np.random.default_rng(SEME_A)
    stato = {"numero": 0}

    def estrai(quante: int, fe) -> List[Tuple[int, dict, int]]:
        lavori: List[Tuple[int, dict, int]] = []
        while len(lavori) < quante:
            stato["numero"] += 1
            numero = stato["numero"]
            v = estrai_variante(rng)
            serie_n = (numero % N_SERIE) + 1
            s = serie_rimescolata(v["timeframe"], serie_n)
            c = cat.compila(v, s)
            st = stima_trade(c, Regole(), 0, len(s) - 1)
            tenuta = st["trade"] >= TRADE_MINIMI
            fe.write(json.dumps({"numero": numero, "serie": serie_n, "trade_stimati": st["trade"],
                                 "tenuta": tenuta, "variante": v}) + "\n")
            fe.flush()
            if tenuta:
                lavori.append((numero, v, serie_n))
        return lavori

    valide = 0
    with estrazioni.open("w", encoding="utf-8") as fe, uscita.open("w", encoding="utf-8") as fu, \
            ProcessPoolExecutor(processi) as ex:
        da_fare = N_VARIANTI_A
        while da_fare > 0:
            lavori = estrai(da_fare, fe)
            print(f"prova A: estratte finora {stato['numero']}, in prova {len(lavori)}", flush=True)
            impossibili = 0
            for riga in ex.map(_fase2_a, lavori):
                fu.write(json.dumps(riga) + "\n")
                fu.flush()
                if "impossibile" in riga:
                    impossibili += 1
                    print(f"A {riga['numero']}: entrate casuali impossibili ({riga['impossibile']})", flush=True)
                    continue
                valide += 1
                print(f"A {riga['numero']}: trade {riga['trade']} p {riga['p_value']} supera {riga['supera_fase2']} "
                      f"({riga['secondi']} s)", flush=True)
            da_fare = impossibili
    print(f"prova A: {valide} varianti con la Fase 2 completa, {stato['numero']} estratte in tutto", flush=True)


# ---------------------------------------------------------------------------
# 13bis.3 prova B: il vantaggio inserito apposta
# ---------------------------------------------------------------------------

B1 = {"timeframe": "1h", "direzione": "long", "filtro": None, "ingresso": {"codice": "E9"}, "conferma": None,
      "tipo_ingresso": {"codice": "M"}, "stop": {"codice": "S1", "k": 1.5},
      "uscite": [{"codice": "U1", "k": 2}, {"codice": "U2", "n": 12}]}
B2 = dict(B1, direzione="short")
B3 = dict(B1, tipo_ingresso={"codice": "L", "k": 0.25, "validita": 1})
REGOLE_B = {"B1": B1, "B2": B2, "B3": B3}


def pianta_vantaggio(s: cat.Serie, regola: dict, ampiezza: float) -> Tuple[cat.Serie, List[int]]:
    """13bis.3, punto 2: costruisce la serie con il vantaggio una candela dopo l'altra.

    Alla chiusura di ogni candela t si calcolano, sulla serie gia' costruita, MACD(12, 26, 9) e
    ATR(14) con le stesse formule di ``catalogo3``; se c'e' un segnale della regola (incrocio
    nella sua direzione, a riscaldamento completo), le candele da t+1 a t+12 si spostano nella
    direzione della regola fino a ampiezza x 1,5 x ATR(14) di t (la distanza dello stop), in
    parti uguali, e poi lo spostamento torna indietro in parti uguali in 240 candele. Lo
    spostamento si somma su apertura, massimo, minimo e chiusura, last e mark."""
    v = cat.normalizza(regola)
    long = v["direzione"] == "long"
    segno = 1.0 if long else -1.0
    k_stop = v["stop"]["k"]
    n = len(s)
    spost = np.zeros(n + CANDELE_VANTAGGIO + CANDELE_RITORNO + 2)
    o, h, l, c = s.open.copy(), s.high.copy(), s.low.copy(), s.close.copy()
    mo, mh, ml, mc = s.mark_open.copy(), s.mark_high.copy(), s.mark_low.copy(), s.mark_close.copy()
    ammessa = cat._ammesse(s, cat.riscaldamento(v))
    a12, a26, a9 = 2.0 / 13.0, 2.0 / 27.0, 2.0 / 10.0
    e12 = e26 = sig = atr = None
    linee: List[float] = []
    trs: List[float] = []
    prec_linea = prec_sig = None
    segnali: List[int] = []
    for t in range(n):
        d = spost[t]
        o[t] += d; h[t] += d; l[t] += d; c[t] += d
        mo[t] += d; mh[t] += d; ml[t] += d; mc[t] += d
        # EMA come catalogo3.ema: primo valore = media dei primi n, poi a*x + (1-a)*v
        if t == 11:
            e12 = float(np.mean(c[0:12]))
        elif t > 11:
            e12 = a12 * c[t] + (1.0 - a12) * e12
        if t == 25:
            e26 = float(np.mean(c[0:26]))
        elif t > 25:
            e26 = a26 * c[t] + (1.0 - a26) * e26
        linea = (e12 - e26) if t >= 25 else None
        if linea is not None:
            linee.append(linea)
            if len(linee) == 9:
                sig = float(np.mean(np.asarray(linee[:9])))
            elif len(linee) > 9:
                sig = a9 * linea + (1.0 - a9) * sig
        # ATR di Wilder come catalogo3.atr: vero range dalla seconda candela, primo valore media di 14
        if t >= 1:
            tr = max(h[t] - l[t], h[t] - c[t - 1], c[t - 1] - l[t])
            trs.append(tr)
            if len(trs) == 14:
                atr = float(np.mean(np.asarray(trs[:14])))
            elif len(trs) > 14:
                atr = (atr * 13 + tr) / 14
        s_cur = sig if (linea is not None and len(linee) >= 9) else None
        incrocio = False
        if prec_linea is not None and prec_sig is not None and s_cur is not None:
            if long:
                incrocio = prec_linea <= prec_sig and linea > s_cur
            else:
                incrocio = prec_linea >= prec_sig and linea < s_cur
        prec_linea, prec_sig = linea, s_cur
        if incrocio and ammessa[t] and atr is not None and ampiezza > 0:
            segnali.append(t)
            dist = ampiezza * k_stop * atr * segno
            j = np.arange(1, CANDELE_VANTAGGIO + 1)
            spost[t + 1:t + 1 + CANDELE_VANTAGGIO] += dist * j / CANDELE_VANTAGGIO
            m = np.arange(1, CANDELE_RITORNO + 1)
            a0 = t + 1 + CANDELE_VANTAGGIO
            spost[a0:a0 + CANDELE_RITORNO] += dist * (1.0 - m / CANDELE_RITORNO)
        elif incrocio and ammessa[t]:
            segnali.append(t)
    nuova = cat.Serie(s.timeframe, s.ts.copy(), o, h, l, c, s.volume.copy(), mo, mh, ml, mc,
                      s.funding_ts.copy(), s.funding_tasso.copy())
    return nuova, segnali


def _fase2_b(argomenti) -> dict:
    nome, serie_n, ampiezza = argomenti
    t0 = time.time()
    regola = REGOLE_B[nome]
    base = serie_rimescolata("1h", serie_n)
    s, piantati = pianta_vantaggio(base, regola, ampiezza)
    c = cat.compila(regola, s)
    trovati = [int(i) for i in np.flatnonzero(c.segnale)]
    es = fase2(regola, s, 0, len(s) - 1, compilata=c)
    m = es["metriche"]
    return {"prova": "B", "regola": nome, "serie": serie_n, "ampiezza": ampiezza, "trade": m["trade"],
            "r_medio": m["r_medio"], "p_value": es["p_value"], "supera_fase2": es["supera"],
            "media_casuali": es["casuali"]["media"] if es["casuali"] else None,
            "esecuzione": m.get("esecuzione"), "segnali_piantati": len(piantati),
            "segnali_uguali": trovati == piantati,
            "segnali_diversi": len(set(trovati) ^ set(piantati)),
            "secondi": round(time.time() - t0, 1)}


def prova_b(processi: int) -> None:
    ESITI.mkdir(exist_ok=True)
    uscita = ESITI / "prova_b.jsonl"
    lavori = [(nome, n, p) for nome in REGOLE_B for p in AMPIEZZE_B for n in range(1, N_SERIE + 1)]
    righe = []
    with uscita.open("w", encoding="utf-8") as fu, ProcessPoolExecutor(processi) as ex:
        for riga in ex.map(_fase2_b, lavori):
            righe.append(riga)
            fu.write(json.dumps(riga) + "\n")
            fu.flush()
            print(f"B {riga['regola']} serie {riga['serie']} P {riga['ampiezza']}: R {riga['r_medio']:.3f} "
                  f"p {riga['p_value']} supera {riga['supera_fase2']} ({riga['secondi']} s)", flush=True)
        # la riserva una volta sola, per le regole in cui con l'ampiezza guida meno di 20 serie arrivano a 0,35 R
        riserva = []
        for nome in REGOLE_B:
            arrivate = sum(1 for r in righe if r["regola"] == nome and r["ampiezza"] == AMPIEZZA_GUIDA_B
                           and r["r_medio"] >= 0.35)
            if arrivate < 20:
                riserva += [(nome, n, AMPIEZZA_RISERVA_B) for n in range(1, N_SERIE + 1)]
        for riga in ex.map(_fase2_b, riserva):
            fu.write(json.dumps(riga) + "\n")
            fu.flush()
            print(f"B riserva {riga['regola']} serie {riga['serie']}: R {riga['r_medio']:.3f} supera {riga['supera_fase2']}",
                  flush=True)


# ---------------------------------------------------------------------------
# stima del tempo e impronte
# ---------------------------------------------------------------------------


def stima() -> None:
    """Il tempo di calcolo stimato su un campione (13bis: oltre 24 ore, STOP)."""
    rng = np.random.default_rng(12345)  # seme del solo campione di stima, non quello della prova
    tempi = {}
    for tf in ("15m", "1h", "4h", "1d"):
        s = serie_rimescolata(tf, 1)
        dur = []
        for _ in range(2):
            while True:
                v = estrai_variante(rng)
                v["timeframe"] = tf
                try:
                    c = cat.compila(v, s)
                except cat.VarianteNonValida:
                    continue
                if stima_trade(c)["trade"] >= TRADE_MINIMI:
                    break
            t0 = time.time()
            fase2(v, s, 0, len(s) - 1, compilata=c)
            dur.append(time.time() - t0)
        tempi[tf] = sum(dur) / len(dur)
        print(f"{tf}: {tempi[tf]:.1f} s per Fase 2", flush=True)
    s = serie_rimescolata("1h", 1)
    t0 = time.time()
    fase2(B1, s, 0, len(s) - 1)
    b = time.time() - t0
    media_a = sum(tempi.values()) / len(tempi)
    totale = (N_VARIANTI_A * media_a + 3 * 4 * N_SERIE * b) / 3600
    print(f"prova B: {b:.1f} s per Fase 2; stima totale su un processo: {totale:.1f} ore", flush=True)


def impronte() -> Dict[str, str]:
    out = {}
    for rel in STRUMENTI:
        p = RADICE / rel
        out[rel] = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "mancante"
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("azione", choices=["stima", "a", "b", "impronte"])
    ESITI.mkdir(parents=True, exist_ok=True)
    ap.add_argument("--processi", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    a = ap.parse_args()
    if a.azione == "stima":
        stima()
    elif a.azione == "a":
        prova_a(a.processi)
    elif a.azione == "b":
        prova_b(a.processi)
    else:
        print(json.dumps(impronte(), indent=2))


if __name__ == "__main__":
    main()
