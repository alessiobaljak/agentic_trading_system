"""Il catalogo delle strategie del protocollo 3 (``research/PROTOCOLLO_3.md``, sezione 7).

Una variante e' un dizionario con gli elementi della sezione 7.1, scritti con i codici
del catalogo e i valori ammessi. Questo modulo:

* controlla che la variante usi solo elementi e valori del catalogo (``normalizza``);
* calcola gli indicatori della sezione 7.2 con le formule scritte nel protocollo;
* calcola, candela per candela, il segnale d'ingresso, il filtro, la conferma, il
  riscaldamento (7.8) e i livelli che servono al motore (ATR della candela del segnale,
  minimi e massimi per lo stop S2, segnale opposto per U4): ``compila``.

Il motore (``research/src/motore3.py``) non sa niente di indicatori: legge solo gli
array prodotti qui. Cosi' la stessa variante e' descritta da DATI (il dizionario), e lo
stesso codice serve alla ricerca, alle entrate casuali e al rigioco del bot.

Forma di una variante (esempio, la V-021 della sezione 7.9)::

    {"timeframe": "4h", "direzione": "long",
     "filtro": {"codice": "F1", "n": 200, "lato": "sopra"},
     "ingresso": {"codice": "E6", "n": 14, "soglie": [30, 70]},
     "conferma": None,
     "tipo_ingresso": {"codice": "L", "k": 0.25, "validita": 3},
     "stop": {"codice": "S1", "k": 1.5},
     "uscite": [{"codice": "U1", "k": 2}, {"codice": "U2", "n": 12}]}

Le scelte che il protocollo lascia aperte (per esempio il primo valore delle medie di
Wilder) sono scritte nei commenti con l'etichetta ``SCELTA`` e riassunte in
``research/collaudo_3/regole.md``: si approvano allo STOP del Passo 0.

Il modulo e' puro: non legge file, non usa la rete, non conosce date.
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# timeframe
# ---------------------------------------------------------------------------

MINUTO_MS = 60_000
TIMEFRAME_MS: Dict[str, int] = {
    "15m": 15 * MINUTO_MS,
    "30m": 30 * MINUTO_MS,
    "1h": 60 * MINUTO_MS,
    "2h": 120 * MINUTO_MS,
    "4h": 240 * MINUTO_MS,
    "6h": 360 * MINUTO_MS,
    "8h": 480 * MINUTO_MS,
    "12h": 720 * MINUTO_MS,
    "1d": 1440 * MINUTO_MS,
}
#: l'elenco ordinato della sezione 7.1 (serve alla verifica dei timeframe adiacenti)
TIMEFRAME = tuple(TIMEFRAME_MS)
GIORNO_MS = 24 * 60 * MINUTO_MS
ORA_MS = 60 * MINUTO_MS


class VarianteNonValida(ValueError):
    """La variante usa un elemento o un valore che il catalogo non ammette."""


# ---------------------------------------------------------------------------
# il catalogo (sezioni 7.2-7.7): valori ammessi
# ---------------------------------------------------------------------------

#: E1: le quattro coppie di medie ammesse
COPPIE_E1 = (("EMA", 9, 20), ("EMA", 20, 50), ("EMA", 50, 200), ("SMA", 50, 200))
VALORI = {
    "E2_n": (20, 50, 100, 200),
    "E3_n": (20, 55),
    "bollinger_k": (2.0, 2.5),
    "rsi_n": (7, 14, 21),
    "E6_soglie": ((30, 70), (20, 80)),
    "funding_soglie_alte": (0.0003, 0.0005),
    "funding_soglie_basse": (0.0, -0.0001),
    "volume_soglie": (1.5, 2.0),
    "F1_n": (50, 100, 200),
    "S1_k": (1.0, 1.5, 2.0, 3.0),
    "S2_n": (5, 10, 20),
    "S3_pct": (0.01, 0.02, 0.03),
    "U1_k": (1.5, 2.0, 3.0),
    "U2_n": (6, 12, 24, 48),
    "U3_k": (2.0, 3.0),
    "L_k": (0.25, 0.5),
    "L_validita": (1, 3),
}
#: i parametri fissi del catalogo (non si scelgono; la Fase 4 li sposta)
FISSI = {
    "atr": 14,
    "macd": (12, 26, 9),
    "stocastico": (14, 3, 3),
    "stocastico_soglie": (20, 80),
    "adx": 14,
    "adx_soglie": (20, 25),
    "atr_percentile_finestra": 500,
    "atr_percentile_soglie": (30, 70),
    "bollinger_n": 20,
    "volume_n": 20,
    "C3_rsi": 14,
    "rsi_meta": 50,
    "F4_soglie": (0.0, 0.0003),
}
#: elementi ammessi solo fino a 1h (7.2, 7.3, 7.4, 7.6)
SOLO_FINO_A_1H = {"E10", "F5", "F7", "U2s"}
TIMEFRAME_FINO_A_1H = ("15m", "30m", "1h")
#: le quattro famiglie di uscite (7.1, punto 8): al massimo una per famiglia
FAMIGLIA_USCITA = {"U1": "target", "U2": "tempo", "U2s": "tempo", "U3": "trailing", "U4": "segnale_opposto"}
#: sessioni (7.2), in minuti dall'inizio del giorno UTC: [inizio, fine)
SESSIONI = {"asia": (0, 8 * 60), "europa": (7 * 60, 16 * 60), "usa": (13 * 60, 21 * 60)}


def _uguale(a: float, b: float) -> bool:
    return abs(float(a) - float(b)) <= 1e-12


def _in(valore, ammessi) -> bool:
    return any(_uguale(valore, a) for a in ammessi)


def _numero(diz: dict, chiave: str, dove: str) -> float:
    if chiave not in diz:
        raise VarianteNonValida(f"{dove}: manca '{chiave}'")
    v = diz[chiave]
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise VarianteNonValida(f"{dove}: '{chiave}' deve essere un numero, non {v!r}")
    return float(v)


def _intero(diz: dict, chiave: str, dove: str) -> int:
    v = _numero(diz, chiave, dove)
    if v != int(v) or v < 1:
        raise VarianteNonValida(f"{dove}: '{chiave}' deve essere un intero positivo, non {diz[chiave]!r}")
    return int(v)


def _scelta(diz: dict, chiave: str, ammessi: Sequence[str], dove: str) -> str:
    v = diz.get(chiave)
    if v not in ammessi:
        raise VarianteNonValida(f"{dove}: '{chiave}' deve essere uno fra {list(ammessi)}, non {v!r}")
    return v


def _chiavi(diz: dict, ammesse: Sequence[str], dove: str) -> None:
    if not isinstance(diz, dict):
        raise VarianteNonValida(f"{dove}: deve essere un dizionario, non {diz!r}")
    extra = set(diz) - set(ammesse)
    if extra:
        raise VarianteNonValida(f"{dove}: chiavi non previste {sorted(extra)}")


# ---------------------------------------------------------------------------
# normalizzazione: la variante con TUTTI i parametri scritti (anche i fissi)
# ---------------------------------------------------------------------------


def normalizza(variante: dict, solo_catalogo: bool = True) -> dict:
    """Controlla la variante e la restituisce con tutti i parametri espliciti.

    Con ``solo_catalogo=True`` (la ricerca) ogni valore deve essere del catalogo e i
    parametri fissi, se scritti, devono avere il valore fisso. Con ``False`` (solo le
    verifiche della Fase 4: robustezza e timeframe adiacenti) i valori numerici possono
    uscire dal catalogo, ma la struttura resta quella della sezione 7.1.
    """
    _chiavi(variante, ("timeframe", "direzione", "filtro", "ingresso", "conferma",
                       "tipo_ingresso", "stop", "uscite"), "variante")
    v = copy.deepcopy(variante)
    tf = _scelta(v, "timeframe", TIMEFRAME, "variante")
    _scelta(v, "direzione", ("long", "short"), "variante")
    out = {"timeframe": tf, "direzione": v["direzione"]}
    out["filtro"] = None if v.get("filtro") is None else _filtro(v["filtro"], solo_catalogo)
    if v.get("ingresso") is None:
        raise VarianteNonValida("variante: il segnale di ingresso e' obbligatorio (7.3)")
    out["ingresso"] = _ingresso(v["ingresso"], solo_catalogo)
    out["conferma"] = None if v.get("conferma") is None else _conferma(v["conferma"], solo_catalogo)
    if v.get("tipo_ingresso") is None:
        raise VarianteNonValida("variante: il tipo di ingresso e' obbligatorio (7.1, punto 6)")
    out["tipo_ingresso"] = _tipo_ingresso(v["tipo_ingresso"], solo_catalogo)
    if v.get("stop") is None:
        raise VarianteNonValida("variante: lo stop e' obbligatorio (7.6)")
    out["stop"] = _stop(v["stop"], solo_catalogo)
    uscite = v.get("uscite")
    if not isinstance(uscite, list) or not 1 <= len(uscite) <= 2:
        raise VarianteNonValida("variante: servono da una a due uscite (7.1, punto 8)")
    out["uscite"] = [_uscita(u, solo_catalogo) for u in uscite]
    famiglie = [FAMIGLIA_USCITA[u["codice"]] for u in out["uscite"]]
    if len(set(famiglie)) != len(famiglie):
        raise VarianteNonValida("variante: due uscite della stessa famiglia (target, tempo, trailing, segnale opposto)")
    usati = {out["ingresso"]["codice"], out["stop"]["codice"]} | {u["codice"] for u in out["uscite"]}
    if out["filtro"]:
        usati.add(out["filtro"]["codice"])
    if out["conferma"]:
        usati.add(out["conferma"]["codice"])
    if tf not in TIMEFRAME_FINO_A_1H and usati & SOLO_FINO_A_1H:
        raise VarianteNonValida(f"variante: {sorted(usati & SOLO_FINO_A_1H)} sono ammessi solo fino a 1h")
    return out


def _fisso(d: dict, chiave: str, valore, solo_catalogo: bool, dove: str):
    """Un parametro fisso: assente -> valore del catalogo; presente -> controllato."""
    if chiave not in d:
        return valore
    letto = d[chiave]
    if isinstance(valore, tuple):
        if not isinstance(letto, (list, tuple)) or len(letto) != len(valore):
            raise VarianteNonValida(f"{dove}: '{chiave}' deve avere {len(valore)} valori")
        letto = tuple(float(x) if not float(x).is_integer() else int(x) for x in letto)
        if solo_catalogo and any(not _uguale(a, b) for a, b in zip(letto, valore)):
            raise VarianteNonValida(f"{dove}: '{chiave}' e' fisso a {valore}")
        return letto
    x = _numero(d, chiave, dove)
    if solo_catalogo and not _uguale(x, valore):
        raise VarianteNonValida(f"{dove}: '{chiave}' e' fisso a {valore}")
    return int(x) if float(x).is_integer() and isinstance(valore, int) else x


def _filtro(f: dict, sc: bool) -> dict:
    dove = "filtro"
    if not isinstance(f, dict):
        raise VarianteNonValida(f"{dove}: deve essere un dizionario")
    cod = f.get("codice")
    if cod == "F1":
        _chiavi(f, ("codice", "n", "lato"), dove)
        n = _intero(f, "n", dove)
        if sc and n not in VALORI["F1_n"]:
            raise VarianteNonValida(f"F1: n deve essere in {VALORI['F1_n']}")
        return {"codice": "F1", "n": n, "lato": _scelta(f, "lato", ("sopra", "sotto"), dove)}
    if cod == "F2":
        _chiavi(f, ("codice", "regime", "n", "soglia"), dove)
        reg = _scelta(f, "regime", ("tendenza", "laterale"), dove)
        soglia = 25 if reg == "tendenza" else 20
        return {"codice": "F2", "regime": reg, "n": _fisso(f, "n", FISSI["adx"], sc, dove),
                "soglia": _fisso(f, "soglia", soglia, sc, dove)}
    if cod == "F3":
        _chiavi(f, ("codice", "regime", "atr", "finestra", "soglia"), dove)
        reg = _scelta(f, "regime", ("alta", "bassa"), dove)
        soglia = 70 if reg == "alta" else 30
        return {"codice": "F3", "regime": reg, "atr": _fisso(f, "atr", FISSI["atr"], sc, dove),
                "finestra": _fisso(f, "finestra", FISSI["atr_percentile_finestra"], sc, dove),
                "soglia": _fisso(f, "soglia", soglia, sc, dove)}
    if cod == "F4":
        _chiavi(f, ("codice", "lato", "soglia"), dove)
        lato = _scelta(f, "lato", ("sopra", "sotto"), dove)
        soglia = 0.0003 if lato == "sopra" else 0.0
        return {"codice": "F4", "lato": lato, "soglia": _fisso(f, "soglia", soglia, sc, dove)}
    if cod == "F5":
        _chiavi(f, ("codice", "sessione"), dove)
        return {"codice": "F5", "sessione": _scelta(f, "sessione", tuple(SESSIONI), dove)}
    if cod == "F6":
        _chiavi(f, ("codice", "giorni"), dove)
        return {"codice": "F6", "giorni": _scelta(f, "giorni", ("feriali", "fine_settimana"), dove)}
    if cod == "F7":
        _chiavi(f, ("codice", "lato"), dove)
        return {"codice": "F7", "lato": _scelta(f, "lato", ("sopra", "sotto"), dove)}
    raise VarianteNonValida(f"filtro: codice sconosciuto {cod!r} (7.4)")


def _ingresso(e: dict, sc: bool) -> dict:
    dove = "ingresso"
    if not isinstance(e, dict):
        raise VarianteNonValida(f"{dove}: deve essere un dizionario")
    cod = e.get("codice")
    if cod == "E1":
        _chiavi(e, ("codice", "media", "veloce", "lenta"), dove)
        media = _scelta(e, "media", ("EMA", "SMA"), dove)
        veloce, lenta = _intero(e, "veloce", dove), _intero(e, "lenta", dove)
        if sc and (media, veloce, lenta) not in COPPIE_E1:
            raise VarianteNonValida(f"E1: coppia non ammessa; ammesse {COPPIE_E1}")
        if veloce >= lenta:
            raise VarianteNonValida("E1: la media veloce deve avere il periodo piu' corto")
        return {"codice": "E1", "media": media, "veloce": veloce, "lenta": lenta}
    if cod == "E2":
        _chiavi(e, ("codice", "media", "n"), dove)
        n = _intero(e, "n", dove)
        if sc and n not in VALORI["E2_n"]:
            raise VarianteNonValida(f"E2: n deve essere in {VALORI['E2_n']}")
        return {"codice": "E2", "media": _scelta(e, "media", ("EMA", "SMA"), dove), "n": n}
    if cod == "E3":
        _chiavi(e, ("codice", "n"), dove)
        n = _intero(e, "n", dove)
        if sc and n not in VALORI["E3_n"]:
            raise VarianteNonValida(f"E3: n deve essere in {VALORI['E3_n']}")
        return {"codice": "E3", "n": n}
    if cod in ("E4", "E5"):
        _chiavi(e, ("codice", "k", "n"), dove)
        k = _numero(e, "k", dove)
        if sc and not _in(k, VALORI["bollinger_k"]):
            raise VarianteNonValida(f"{cod}: k deve essere in {VALORI['bollinger_k']}")
        return {"codice": cod, "k": k, "n": _fisso(e, "n", FISSI["bollinger_n"], sc, dove)}
    if cod == "E6":
        _chiavi(e, ("codice", "n", "soglie"), dove)
        n = _intero(e, "n", dove)
        if sc and n not in VALORI["rsi_n"]:
            raise VarianteNonValida(f"E6: n deve essere in {VALORI['rsi_n']}")
        s = e.get("soglie")
        if not isinstance(s, (list, tuple)) or len(s) != 2:
            raise VarianteNonValida("E6: 'soglie' deve essere [bassa, alta]")
        s = (float(s[0]), float(s[1]))
        if sc and not any(_uguale(s[0], a) and _uguale(s[1], b) for a, b in VALORI["E6_soglie"]):
            raise VarianteNonValida(f"E6: soglie ammesse {VALORI['E6_soglie']}")
        return {"codice": "E6", "n": n, "soglie": [s[0], s[1]]}
    if cod == "E7":
        _chiavi(e, ("codice", "n", "meta"), dove)
        n = _intero(e, "n", dove)
        if sc and n not in VALORI["rsi_n"]:
            raise VarianteNonValida(f"E7: n deve essere in {VALORI['rsi_n']}")
        return {"codice": "E7", "n": n, "meta": _fisso(e, "meta", FISSI["rsi_meta"], sc, dove)}
    if cod == "E8":
        _chiavi(e, ("codice", "parametri", "soglie"), dove)
        return {"codice": "E8", "parametri": list(_fisso(e, "parametri", FISSI["stocastico"], sc, dove)),
                "soglie": list(_fisso(e, "soglie", FISSI["stocastico_soglie"], sc, dove))}
    if cod == "E9":
        _chiavi(e, ("codice", "parametri"), dove)
        return {"codice": "E9", "parametri": list(_fisso(e, "parametri", FISSI["macd"], sc, dove))}
    if cod == "E10":
        _chiavi(e, ("codice",), dove)
        return {"codice": "E10"}
    if cod == "E11":
        _chiavi(e, ("codice", "soglia", "lato"), dove)
        s = _numero(e, "soglia", dove)
        if sc and not (_in(s, VALORI["funding_soglie_alte"]) or _in(s, VALORI["funding_soglie_basse"])):
            raise VarianteNonValida("E11: soglia non del catalogo")
        # SCELTA: una soglia del catalogo >= +0,03% e' "alta" (funding sopra), le altre "basse"
        # (sotto). Il lato, una volta scritto, resta: spostando la soglia nella verifica di
        # robustezza (+0,03% -> +0,025%) la strategia non diventa un'altra.
        derivato = "sopra" if s >= 0.0003 - 1e-12 else "sotto"
        lato = e.get("lato", derivato)
        if lato not in ("sopra", "sotto"):
            raise VarianteNonValida("E11: 'lato' deve essere 'sopra' o 'sotto'")
        if sc and lato != derivato:
            raise VarianteNonValida(f"E11: con la soglia {s} il lato e' '{derivato}'")
        return {"codice": "E11", "soglia": s, "lato": lato}
    if cod == "E12":
        _chiavi(e, ("codice", "soglia", "n"), dove)
        s = _numero(e, "soglia", dove)
        if sc and not _in(s, VALORI["volume_soglie"]):
            raise VarianteNonValida(f"E12: soglia deve essere in {VALORI['volume_soglie']}")
        return {"codice": "E12", "soglia": s, "n": _fisso(e, "n", FISSI["volume_n"], sc, dove)}
    raise VarianteNonValida(f"ingresso: codice sconosciuto {cod!r} (7.3)")


def _conferma(c: dict, sc: bool) -> dict:
    dove = "conferma"
    if not isinstance(c, dict):
        raise VarianteNonValida(f"{dove}: deve essere un dizionario")
    cod = c.get("codice")
    if cod == "C1":
        _chiavi(c, ("codice", "soglia", "n"), dove)
        s = _numero(c, "soglia", dove)
        if sc and not _in(s, VALORI["volume_soglie"]):
            raise VarianteNonValida(f"C1: soglia deve essere in {VALORI['volume_soglie']}")
        return {"codice": "C1", "soglia": s, "n": _fisso(c, "n", FISSI["volume_n"], sc, dove)}
    if cod == "C2":
        _chiavi(c, ("codice",), dove)
        return {"codice": "C2"}
    if cod == "C3":
        _chiavi(c, ("codice", "n", "meta"), dove)
        return {"codice": "C3", "n": _fisso(c, "n", FISSI["C3_rsi"], sc, dove),
                "meta": _fisso(c, "meta", FISSI["rsi_meta"], sc, dove)}
    raise VarianteNonValida(f"conferma: codice sconosciuto {cod!r} (7.5)")


def _tipo_ingresso(t: dict, sc: bool) -> dict:
    dove = "tipo_ingresso"
    if not isinstance(t, dict):
        raise VarianteNonValida(f"{dove}: deve essere un dizionario")
    cod = t.get("codice")
    if cod == "M":
        _chiavi(t, ("codice",), dove)
        return {"codice": "M"}
    if cod == "L":
        _chiavi(t, ("codice", "k", "validita", "atr"), dove)
        k = _numero(t, "k", dove)
        val = _intero(t, "validita", dove)
        if sc and not _in(k, VALORI["L_k"]):
            raise VarianteNonValida(f"L: k deve essere in {VALORI['L_k']}")
        if sc and val not in VALORI["L_validita"]:
            raise VarianteNonValida(f"L: validita' deve essere in {VALORI['L_validita']}")
        if k <= 0:
            raise VarianteNonValida("L: k deve essere positivo")
        return {"codice": "L", "k": k, "validita": val, "atr": _fisso(t, "atr", FISSI["atr"], sc, dove)}
    raise VarianteNonValida(f"tipo_ingresso: codice sconosciuto {cod!r} (7.7)")


def _stop(s: dict, sc: bool) -> dict:
    dove = "stop"
    if not isinstance(s, dict):
        raise VarianteNonValida(f"{dove}: deve essere un dizionario")
    cod = s.get("codice")
    if cod == "S1":
        _chiavi(s, ("codice", "k", "atr"), dove)
        k = _numero(s, "k", dove)
        if sc and not _in(k, VALORI["S1_k"]):
            raise VarianteNonValida(f"S1: k deve essere in {VALORI['S1_k']}")
        if k <= 0:
            raise VarianteNonValida("S1: k deve essere positivo")
        return {"codice": "S1", "k": k, "atr": _fisso(s, "atr", FISSI["atr"], sc, dove)}
    if cod == "S2":
        _chiavi(s, ("codice", "n"), dove)
        n = _intero(s, "n", dove)
        if sc and n not in VALORI["S2_n"]:
            raise VarianteNonValida(f"S2: n deve essere in {VALORI['S2_n']}")
        return {"codice": "S2", "n": n}
    if cod == "S3":
        _chiavi(s, ("codice", "pct"), dove)
        p = _numero(s, "pct", dove)
        if sc and not _in(p, VALORI["S3_pct"]):
            raise VarianteNonValida(f"S3: pct deve essere in {VALORI['S3_pct']} (frazioni: 0.01 = 1%)")
        if not 0 < p < 1:
            raise VarianteNonValida("S3: pct deve stare fra 0 e 1")
        return {"codice": "S3", "pct": p}
    raise VarianteNonValida(f"stop: codice sconosciuto {cod!r} (7.6)")


def _uscita(u: dict, sc: bool) -> dict:
    dove = "uscita"
    if not isinstance(u, dict):
        raise VarianteNonValida(f"{dove}: deve essere un dizionario")
    cod = u.get("codice")
    if cod == "U1":
        _chiavi(u, ("codice", "k"), dove)
        k = _numero(u, "k", dove)
        if sc and not _in(k, VALORI["U1_k"]):
            raise VarianteNonValida(f"U1: k deve essere in {VALORI['U1_k']}")
        if k <= 0:
            raise VarianteNonValida("U1: k deve essere positivo")
        return {"codice": "U1", "k": k}
    if cod == "U2":
        _chiavi(u, ("codice", "n"), dove)
        n = _intero(u, "n", dove)
        if sc and n not in VALORI["U2_n"]:
            raise VarianteNonValida(f"U2: n deve essere in {VALORI['U2_n']}")
        return {"codice": "U2", "n": n}
    if cod == "U2s":
        _chiavi(u, ("codice",), dove)
        return {"codice": "U2s"}
    if cod == "U3":
        _chiavi(u, ("codice", "k", "atr"), dove)
        k = _numero(u, "k", dove)
        if sc and not _in(k, VALORI["U3_k"]):
            raise VarianteNonValida(f"U3: k deve essere in {VALORI['U3_k']}")
        if k <= 0:
            raise VarianteNonValida("U3: k deve essere positivo")
        return {"codice": "U3", "k": k, "atr": _fisso(u, "atr", FISSI["atr"], sc, dove)}
    if cod == "U4":
        _chiavi(u, ("codice",), dove)
        return {"codice": "U4"}
    raise VarianteNonValida(f"uscita: codice sconosciuto {cod!r} (7.6)")


# ---------------------------------------------------------------------------
# indicatori (7.2): array numpy, NaN dove l'indicatore non e' ancora definito
# ---------------------------------------------------------------------------


def _vuoto(n: int) -> np.ndarray:
    return np.full(n, np.nan, dtype=np.float64)


def ema(x: np.ndarray, n: int) -> np.ndarray:
    """EMA = alfa x chiusura + (1 - alfa) x EMA precedente, alfa = 2/(n+1); primo valore =
    media dei primi n valori (7.2). Se ``x`` comincia con NaN (per esempio la linea del
    MACD), si parte dal primo valore definito."""
    x = np.asarray(x, dtype=np.float64)
    out = _vuoto(len(x))
    finiti = np.flatnonzero(np.isfinite(x))
    if len(finiti) == 0:
        return out
    f = int(finiti[0])
    if len(x) - f < n:
        return out
    a = 2.0 / (n + 1.0)
    v = float(np.mean(x[f:f + n]))
    out[f + n - 1] = v
    for i in range(f + n, len(x)):
        v = a * x[i] + (1.0 - a) * v
        out[i] = v
    return out


def _finestre(x: np.ndarray, n: int) -> np.ndarray:
    return np.lib.stride_tricks.sliding_window_view(x, n)


def sma(x: np.ndarray, n: int) -> np.ndarray:
    """Media semplice degli ultimi n valori, candela corrente compresa (7.2)."""
    x = np.asarray(x, dtype=np.float64)
    out = _vuoto(len(x))
    if len(x) >= n:
        out[n - 1:] = _finestre(x, n).mean(axis=1)
    return out


def deviazione_popolazione(x: np.ndarray, n: int) -> np.ndarray:
    """Deviazione standard di popolazione degli ultimi n valori (Bollinger, 7.2)."""
    x = np.asarray(x, dtype=np.float64)
    out = _vuoto(len(x))
    if len(x) >= n:
        out[n - 1:] = _finestre(x, n).std(axis=1, ddof=0)
    return out


def _wilder(x: np.ndarray, n: int, primo: int) -> np.ndarray:
    """Media di Wilder (alfa = 1/n) dei valori ``x[primo:]``.

    SCELTA: il primo valore e' la media semplice dei primi n valori (il metodo di Wilder
    originale), all'indice ``primo + n - 1``; poi media = (media precedente x (n-1) + x)/n.
    """
    out = _vuoto(len(x))
    if len(x) - primo < n:
        return out
    v = float(np.mean(x[primo:primo + n]))
    out[primo + n - 1] = v
    for i in range(primo + n, len(x)):
        v = (v * (n - 1) + x[i]) / n
        out[i] = v
    return out


def rsi(close: np.ndarray, n: int) -> np.ndarray:
    """RSI di Wilder (7.2): medie dei rialzi e dei ribassi di chiusura con alfa = 1/n.

    SCELTA: le variazioni partono dalla seconda candela; se la media dei ribassi e' zero
    l'RSI vale 100 (50 se anche quella dei rialzi e' zero)."""
    c = np.asarray(close, dtype=np.float64)
    d = np.zeros(len(c))
    d[1:] = np.diff(c)
    rialzi = np.where(d > 0, d, 0.0)
    ribassi = np.where(d < 0, -d, 0.0)
    mr = _wilder(rialzi, n, 1)
    mb = _wilder(ribassi, n, 1)
    out = _vuoto(len(c))
    ok = np.isfinite(mr) & np.isfinite(mb)
    with np.errstate(divide="ignore", invalid="ignore"):
        rs = mr / mb
        valore = 100.0 - 100.0 / (1.0 + rs)
    valore = np.where(mb == 0, np.where(mr == 0, 50.0, 100.0), valore)
    out[ok] = valore[ok]
    return out


def vero_range(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
    """Vero range (7.2): il massimo fra massimo - minimo, massimo - chiusura precedente,
    chiusura precedente - minimo. SCELTA: la prima candela non ha chiusura precedente e
    resta NaN (le medie di Wilder partono dalla seconda)."""
    h, l, c = (np.asarray(a, dtype=np.float64) for a in (high, low, close))
    tr = _vuoto(len(h))
    if len(h) > 1:
        cp = c[:-1]
        tr[1:] = np.maximum.reduce([h[1:] - l[1:], h[1:] - cp, cp - l[1:]])
    return tr


def atr(high, low, close, n: int = 14) -> np.ndarray:
    """ATR di Wilder (7.2): media con alfa = 1/n del vero range."""
    return _wilder(np.nan_to_num(vero_range(high, low, close)), n, 1)


def adx(high, low, close, n: int = 14) -> np.ndarray:
    """ADX(n) di Wilder (7.2).

    +DM = rialzo del massimo se maggiore del ribasso del minimo e positivo, altrimenti 0;
    -DM al contrario; vero range, +DM e -DM lisciati con Wilder (alfa = 1/n); +DI e -DI
    = 100 x DM lisciato / vero range lisciato; DX = 100 x |+DI - -DI| / (+DI + -DI) (0 se
    la somma e' zero); ADX = media di Wilder del DX. SCELTA: primo valore di ogni media =
    media semplice dei primi n valori (metodo di Wilder)."""
    h, l, c = (np.asarray(a, dtype=np.float64) for a in (high, low, close))
    m = len(h)
    pdm = np.zeros(m)
    mdm = np.zeros(m)
    if m > 1:
        su = h[1:] - h[:-1]
        giu = l[:-1] - l[1:]
        pdm[1:] = np.where((su > giu) & (su > 0), su, 0.0)
        mdm[1:] = np.where((giu > su) & (giu > 0), giu, 0.0)
    tr = np.nan_to_num(vero_range(h, l, c))
    s_tr = _wilder(tr, n, 1)
    s_p = _wilder(pdm, n, 1)
    s_m = _wilder(mdm, n, 1)
    with np.errstate(divide="ignore", invalid="ignore"):
        pdi = np.where(s_tr > 0, 100.0 * s_p / s_tr, 0.0)
        mdi = np.where(s_tr > 0, 100.0 * s_m / s_tr, 0.0)
        somma = pdi + mdi
        dx = np.where(somma > 0, 100.0 * np.abs(pdi - mdi) / somma, 0.0)
    dx = np.where(np.isfinite(s_tr), dx, np.nan)
    finiti = np.flatnonzero(np.isfinite(dx))
    if len(finiti) == 0:
        return _vuoto(m)
    return _wilder(np.nan_to_num(dx), n, int(finiti[0]))


def stocastico(high, low, close, k: int = 14, lk: int = 3, ld: int = 3) -> Tuple[np.ndarray, np.ndarray]:
    """Stocastico (14, 3, 3) (7.2): %K grezzo = 100 x (chiusura - minimo dei minimi delle
    ultime k candele) / (massimo dei massimi - minimo dei minimi), candela corrente
    compresa; %K = SMA(lk) del grezzo; %D = SMA(ld) del %K. SCELTA: se massimo = minimo il
    grezzo vale 50."""
    h, l, c = (np.asarray(a, dtype=np.float64) for a in (high, low, close))
    m = len(c)
    grezzo = _vuoto(m)
    if m >= k:
        mx = _finestre(h, k).max(axis=1)
        mn = _finestre(l, k).min(axis=1)
        cc = c[k - 1:]
        with np.errstate(divide="ignore", invalid="ignore"):
            g = np.where(mx > mn, 100.0 * (cc - mn) / (mx - mn), 50.0)
        grezzo[k - 1:] = g
    pk = _sma_con_nan(grezzo, lk)
    pd_ = _sma_con_nan(pk, ld)
    return pk, pd_


def _sma_con_nan(x: np.ndarray, n: int) -> np.ndarray:
    """SMA che parte dal primo valore definito di ``x``."""
    out = _vuoto(len(x))
    finiti = np.flatnonzero(np.isfinite(x))
    if len(finiti) == 0:
        return out
    f = int(finiti[0])
    if len(x) - f >= n:
        out[f + n - 1:] = _finestre(x[f:], n).mean(axis=1)
    return out


def macd(close, veloce: int = 12, lenta: int = 26, segnale: int = 9) -> Tuple[np.ndarray, np.ndarray]:
    """MACD (12, 26, 9) (7.2): linea = EMA(12) - EMA(26); segnale = EMA(9) della linea
    (primo valore = media dei primi 9 valori della linea)."""
    linea = ema(close, veloce) - ema(close, lenta)
    return linea, ema(linea, segnale)


def donchian(high, low, n: int) -> Tuple[np.ndarray, np.ndarray]:
    """Canale di Donchian(n) (7.2): massimo dei massimi e minimo dei minimi delle n candele
    precedenti, ESCLUSA quella corrente."""
    h, l = np.asarray(high, dtype=np.float64), np.asarray(low, dtype=np.float64)
    su, giu = _vuoto(len(h)), _vuoto(len(h))
    if len(h) > n:
        su[n:] = _finestre(h, n).max(axis=1)[:-1]
        giu[n:] = _finestre(l, n).min(axis=1)[:-1]
    return su, giu


def volume_relativo(volume, n: int = 20) -> np.ndarray:
    """Volume della candela / media dei volumi delle n candele PRECEDENTI (7.2)."""
    v = np.asarray(volume, dtype=np.float64)
    out = _vuoto(len(v))
    if len(v) > n:
        media = _finestre(v, n).mean(axis=1)[:-1]
        with np.errstate(divide="ignore", invalid="ignore"):
            out[n:] = np.where(media > 0, v[n:] / media, np.nan)
    return out


def atr_percentile(atr_: np.ndarray, close: np.ndarray, finestra: int = 500) -> np.ndarray:
    """Posizione (0-100) di ATR/chiusura fra gli stessi valori delle ``finestra`` candele
    precedenti (7.2). SCELTA: percentuale dei valori precedenti STRETTAMENTE minori del
    valore corrente; definita solo se tutti i valori precedenti sono definiti."""
    x = np.asarray(atr_, dtype=np.float64) / np.asarray(close, dtype=np.float64)
    out = _vuoto(len(x))
    if len(x) <= finestra:
        return out
    prec = _finestre(x, finestra)[:-1]  # prec[j] = x[j : j+finestra], valori prima di j+finestra
    cur = x[finestra:]
    ok = np.isfinite(prec).all(axis=1) & np.isfinite(cur)
    conta = (prec < cur[:, None]).sum(axis=1)
    val = 100.0 * conta / finestra
    out[finestra:] = np.where(ok, val, np.nan)
    return out


def inizio_giorno(ts: np.ndarray) -> np.ndarray:
    return (np.asarray(ts, dtype=np.int64) // GIORNO_MS) * GIORNO_MS


def minuto_del_giorno(ts: np.ndarray) -> np.ndarray:
    return (np.asarray(ts, dtype=np.int64) % GIORNO_MS) // MINUTO_MS


def vwap_giornaliero(ts, high, low, close, volume) -> np.ndarray:
    """VWAP dall'inizio del giorno UTC (7.2): somma di (prezzo tipico x volume) / somma dei
    volumi, candela corrente compresa; prezzo tipico = (massimo + minimo + chiusura)/3."""
    ts = np.asarray(ts, dtype=np.int64)
    tp = (np.asarray(high) + np.asarray(low) + np.asarray(close)) / 3.0
    v = np.asarray(volume, dtype=np.float64)
    giorno = inizio_giorno(ts)
    out = _vuoto(len(ts))
    num = 0.0
    den = 0.0
    corrente = None
    for i in range(len(ts)):
        if giorno[i] != corrente:
            corrente = giorno[i]
            num = 0.0
            den = 0.0
        num += tp[i] * v[i]
        den += v[i]
        out[i] = num / den if den > 0 else np.nan
    return out


def giorno_completo(ts: np.ndarray, durata: int) -> np.ndarray:
    """Vero se dall'inizio del giorno UTC fino alla candela corrente non manca nessuna
    candela (serve a VWAP, range asiatico e uscita a fine giornata)."""
    ts = np.asarray(ts, dtype=np.int64)
    giorno = inizio_giorno(ts)
    out = np.zeros(len(ts), dtype=bool)
    contate = 0
    corrente = None
    for i in range(len(ts)):
        if giorno[i] != corrente:
            corrente = giorno[i]
            contate = 0
        contate += 1
        attese = (ts[i] - giorno[i]) // durata + 1
        out[i] = contate == attese
    return out


def range_asiatico(ts, high, low, durata: int) -> Tuple[np.ndarray, np.ndarray]:
    """Massimo e minimo delle candele che aprono fra 00:00 e 08:00 UTC dello stesso giorno
    (7.2), noti dalla prima candela che apre alle 08:00 o dopo. Prima: NaN."""
    ts = np.asarray(ts, dtype=np.int64)
    giorno = inizio_giorno(ts)
    minuto = minuto_del_giorno(ts)
    su, giu = _vuoto(len(ts)), _vuoto(len(ts))
    corrente = None
    mx = -np.inf
    mn = np.inf
    for i in range(len(ts)):
        if giorno[i] != corrente:
            corrente = giorno[i]
            mx, mn = -np.inf, np.inf
        if minuto[i] < 8 * 60:
            mx = max(mx, high[i])
            mn = min(mn, low[i])
        elif np.isfinite(mx):
            su[i], giu[i] = mx, mn
    return su, giu


def funding_regolato(ts_candele, durata: int, ts_funding, tassi) -> np.ndarray:
    """Ultimo tasso di funding regolato alla CHIUSURA della candela (7.2): l'ultimo
    regolamento T con T <= apertura + durata - 1 ms."""
    ts_candele = np.asarray(ts_candele, dtype=np.int64)
    ts_funding = np.asarray(ts_funding, dtype=np.int64)
    tassi = np.asarray(tassi, dtype=np.float64)
    out = _vuoto(len(ts_candele))
    if len(ts_funding) == 0:
        return out
    pos = np.searchsorted(ts_funding, ts_candele + durata - 1, side="right") - 1
    ok = pos >= 0
    out[ok] = tassi[pos[ok]]
    return out


def prima_candela_dopo_regolamento(ts_candele, ts_funding) -> np.ndarray:
    """Vero per la candela che e' la prima a iniziare a un regolamento T o dopo:
    T in (apertura della candela precedente, apertura della candela]. SCELTA: una candela
    che inizia esattamente a T conta come "la prima dopo" (9.5: gli eventi all'istante T
    si considerano subito dopo T)."""
    ts_candele = np.asarray(ts_candele, dtype=np.int64)
    ts_funding = np.asarray(ts_funding, dtype=np.int64)
    out = np.zeros(len(ts_candele), dtype=bool)
    if len(ts_funding) == 0 or len(ts_candele) == 0:
        return out
    # numero di regolamenti con T <= apertura
    fino = np.searchsorted(ts_funding, ts_candele, side="right")
    out[1:] = fino[1:] > fino[:-1]
    # la prima candela dei dati: vale se un regolamento cade esattamente alla sua apertura
    out[0] = bool(len(ts_funding) and np.any(ts_funding == ts_candele[0]))
    return out


def incrocio_su(a: np.ndarray, b) -> np.ndarray:
    """"Incrocia verso l'alto" (7.2): alla chiusura precedente a <= b, a quella attuale
    a > b. ``b`` puo' essere un array o un numero."""
    a = np.asarray(a, dtype=np.float64)
    b = np.broadcast_to(np.asarray(b, dtype=np.float64), a.shape)
    out = np.zeros(len(a), dtype=bool)
    if len(a) > 1:
        with np.errstate(invalid="ignore"):
            out[1:] = (a[:-1] <= b[:-1]) & (a[1:] > b[1:])
    return out


def incrocio_giu(a: np.ndarray, b) -> np.ndarray:
    """"Verso il basso": l'opposto (a >= b prima, a < b ora)."""
    a = np.asarray(a, dtype=np.float64)
    b = np.broadcast_to(np.asarray(b, dtype=np.float64), a.shape)
    out = np.zeros(len(a), dtype=bool)
    if len(a) > 1:
        with np.errstate(invalid="ignore"):
            out[1:] = (a[:-1] >= b[:-1]) & (a[1:] < b[1:])
    return out


# ---------------------------------------------------------------------------
# la serie di prezzi su cui si compila
# ---------------------------------------------------------------------------


@dataclass
class Serie:
    """Candele last price di un timeframe, con mark price e funding.

    ``ts`` e' l'ora di apertura in millisecondi UTC (9.1). Le candele mark hanno gli stessi
    ``ts`` (il caricatore le allinea). ``funding_ts`` e ``funding_tasso`` sono i
    regolamenti, in ordine di tempo.
    """

    timeframe: str
    ts: np.ndarray
    open: np.ndarray
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray
    volume: np.ndarray
    mark_open: np.ndarray
    mark_high: np.ndarray
    mark_low: np.ndarray
    mark_close: np.ndarray
    funding_ts: np.ndarray
    funding_tasso: np.ndarray

    def __post_init__(self) -> None:
        if self.timeframe not in TIMEFRAME_MS:
            raise ValueError(f"timeframe sconosciuto {self.timeframe!r}")
        self.ts = np.asarray(self.ts, dtype=np.int64)
        for nome in ("open", "high", "low", "close", "volume", "mark_open", "mark_high",
                     "mark_low", "mark_close"):
            arr = np.asarray(getattr(self, nome), dtype=np.float64)
            if arr.shape != self.ts.shape:
                raise ValueError(f"{nome}: lunghezza diversa da ts")
            setattr(self, nome, arr)
        self.funding_ts = np.asarray(self.funding_ts, dtype=np.int64)
        self.funding_tasso = np.asarray(self.funding_tasso, dtype=np.float64)
        if len(self.ts) > 1 and np.any(np.diff(self.ts) <= 0):
            raise ValueError("ts deve essere strettamente crescente")
        if len(self.funding_ts) > 1 and np.any(np.diff(self.funding_ts) <= 0):
            raise ValueError("funding_ts deve essere strettamente crescente")
        if len(self.ts) and np.any(self.ts % self.durata != 0):
            raise ValueError("le candele devono aprire su multipli del timeframe")

    @property
    def durata(self) -> int:
        return TIMEFRAME_MS[self.timeframe]

    def __len__(self) -> int:
        return len(self.ts)

    def fino_a(self, indice: int) -> "Serie":
        """La serie troncata: solo le candele fino a ``indice`` compreso, e il funding
        regolato fino alla chiusura di quella candela (test di troncamento, 9.8)."""
        k = indice + 1
        limite = self.ts[indice] + self.durata - 1 if k > 0 else -1
        nf = int(np.searchsorted(self.funding_ts, limite, side="right"))
        return Serie(self.timeframe, self.ts[:k], self.open[:k], self.high[:k], self.low[:k],
                     self.close[:k], self.volume[:k], self.mark_open[:k], self.mark_high[:k],
                     self.mark_low[:k], self.mark_close[:k], self.funding_ts[:nf],
                     self.funding_tasso[:nf])

    def inizi_dei_tratti(self) -> np.ndarray:
        """Indici delle candele che iniziano un tratto senza buchi: la prima, e ogni
        candela dopo una o piu' candele mancanti (9.6)."""
        if len(self.ts) == 0:
            return np.zeros(0, dtype=np.int64)
        salti = np.flatnonzero(np.diff(self.ts) != self.durata) + 1
        return np.concatenate([[0], salti]).astype(np.int64)


# ---------------------------------------------------------------------------
# compilazione: dalla variante agli array che legge il motore
# ---------------------------------------------------------------------------


@dataclass
class Compilata:
    """Gli array di una variante su una serie. Tutti lunghi quanto la serie.

    * ``segnale[t]``: alla chiusura di t sono veri filtro, ingresso e conferma, e il
      riscaldamento e' completo (9.2, punto 5);
    * ``ammessa[t]``: riscaldamento completo e fuori dai buchi (7.8, 9.6): le candele fra
      cui si scelgono le entrate casuali (10.1);
    * ``opposto[t]``: il segnale di ingresso della direzione opposta, senza filtro ne'
      conferma (U4);
    * ``atr_stop``, ``atr_limite``, ``atr_trailing``: l'ATR usato da S1, L e U3;
    * ``estremo_s2[t]``: minimo (long) o massimo (short) delle ultime n candele, compresa
      t (S2);
    * ``fine_giornata[t]``: la candela t inizia alle 21:00 UTC o dopo (U2s).
    """

    variante: dict
    serie: Serie
    segnale: np.ndarray
    ammessa: np.ndarray
    opposto: np.ndarray
    atr_stop: Optional[np.ndarray]
    atr_limite: Optional[np.ndarray]
    atr_trailing: Optional[np.ndarray]
    estremo_s2: Optional[np.ndarray]
    fine_giornata: np.ndarray
    riscaldamento: int
    dettagli: Dict[str, np.ndarray] = field(default_factory=dict)

    @property
    def long(self) -> bool:
        return self.variante["direzione"] == "long"


def riscaldamento(variante: dict) -> int:
    """Candele di riscaldamento della variante (7.8): una candela t puo' dare un segnale
    solo se dall'inizio del tratto senza buchi sono passate almeno ``w`` candele.

    * indicatori ricorsivi (EMA, RSI, ATR, ADX, MACD): 3 volte il periodo piu' lungo;
    * gli altri (SMA, Bollinger, Donchian, volume relativo, stocastico, minimo/massimo di
      S2): il periodo pieno, cioe' le candele che servono perche' l'indicatore sia
      definito alla candela del segnale e, per gli incroci, anche a quella precedente;
    * ATR percentile: il riscaldamento dell'ATR (3 x 14) piu' le 500 candele della finestra.

    SCELTA: per il MACD conta il periodo piu' lungo delle due medie (26), quindi 78 candele."""
    ricorsivi: List[int] = []
    pieni: List[int] = [1]  # gli incroci guardano anche la candela precedente
    v = variante
    for el in (v.get("filtro"), v["ingresso"], v.get("conferma")):
        if not el:
            continue
        cod = el["codice"]
        if cod in ("F1", "F2", "E6", "E7", "C3"):
            ricorsivi.append(int(el["n"]))
        elif cod == "F3":
            pieni.append(3 * int(el["atr"]) + int(el["finestra"]))
        elif cod == "E1":
            (ricorsivi if el["media"] == "EMA" else pieni).append(int(el["lenta"]))
        elif cod == "E2":
            (ricorsivi if el["media"] == "EMA" else pieni).append(int(el["n"]))
        elif cod in ("E3", "E4", "E5", "E12", "C1"):
            pieni.append(int(el["n"]))
        elif cod == "E8":
            k, lk, ld = (int(x) for x in el["parametri"])
            pieni.append(k + lk + ld - 2)
        elif cod == "E9":
            veloce, lenta, sig = (int(x) for x in el["parametri"])
            ricorsivi.append(max(veloce, lenta))
            pieni.append(lenta + sig - 1)
    if v["stop"]["codice"] == "S1":
        ricorsivi.append(int(v["stop"]["atr"]))
    if v["stop"]["codice"] == "S2":
        pieni.append(int(v["stop"]["n"]) - 1)
    if v["tipo_ingresso"]["codice"] == "L":
        ricorsivi.append(int(v["tipo_ingresso"]["atr"]))
    for u in v["uscite"]:
        if u["codice"] == "U3":
            ricorsivi.append(int(u["atr"]))
    w_ricorsivi = 3 * max(ricorsivi) if ricorsivi else 0
    return int(max(w_ricorsivi, max(pieni)))


class _Cache:
    """Gli indicatori gia' calcolati su una serie (una variante ne usa pochi)."""

    def __init__(self, s: Serie):
        self.s = s
        self._d: Dict[Tuple, np.ndarray] = {}

    def get(self, chiave: Tuple, calcolo):
        if chiave not in self._d:
            self._d[chiave] = calcolo()
        return self._d[chiave]

    def ema(self, n):
        return self.get(("ema", n), lambda: ema(self.s.close, n))

    def sma(self, n):
        return self.get(("sma", n), lambda: sma(self.s.close, n))

    def media(self, tipo, n):
        return self.ema(n) if tipo == "EMA" else self.sma(n)

    def rsi(self, n):
        return self.get(("rsi", n), lambda: rsi(self.s.close, n))

    def atr(self, n):
        return self.get(("atr", n), lambda: atr(self.s.high, self.s.low, self.s.close, n))

    def adx(self, n):
        return self.get(("adx", n), lambda: adx(self.s.high, self.s.low, self.s.close, n))

    def bollinger(self, n, k):
        mid = self.sma(n)
        sd = self.get(("sd", n), lambda: deviazione_popolazione(self.s.close, n))
        return mid - k * sd, mid + k * sd

    def volrel(self, n):
        return self.get(("volrel", n), lambda: volume_relativo(self.s.volume, n))

    def funding(self):
        return self.get(("funding",), lambda: funding_regolato(self.s.ts, self.s.durata,
                                                                self.s.funding_ts, self.s.funding_tasso))

    def giorno_completo(self):
        return self.get(("giorno_completo",), lambda: giorno_completo(self.s.ts, self.s.durata))


def _condizione_ingresso(e: dict, long: bool, k: _Cache, s: Serie, det: Dict[str, np.ndarray]) -> np.ndarray:
    """La condizione del segnale di ingresso (7.3) alla chiusura di ogni candela."""
    cod = e["codice"]
    c = s.close
    if cod == "E1":
        a, b = k.media(e["media"], e["veloce"]), k.media(e["media"], e["lenta"])
        return incrocio_su(a, b) if long else incrocio_giu(a, b)
    if cod == "E2":
        m = k.media(e["media"], e["n"])
        return incrocio_su(c, m) if long else incrocio_giu(c, m)
    if cod == "E3":
        su, giu = donchian(s.high, s.low, e["n"])
        det["donchian_su"], det["donchian_giu"] = su, giu
        with np.errstate(invalid="ignore"):
            return (c > su) if long else (c < giu)
    if cod == "E4":
        giu, su = k.bollinger(e["n"], e["k"])
        with np.errstate(invalid="ignore"):
            return (c > su) if long else (c < giu)
    if cod == "E5":
        giu, su = k.bollinger(e["n"], e["k"])
        out = np.zeros(len(c), dtype=bool)
        with np.errstate(invalid="ignore"):
            dentro = (c >= giu) & (c <= su)
            if long:
                out[1:] = (c[:-1] < giu[:-1]) & dentro[1:]
            else:
                out[1:] = (c[:-1] > su[:-1]) & dentro[1:]
        return out
    if cod == "E6":
        r = k.rsi(e["n"])
        return incrocio_su(r, e["soglie"][0]) if long else incrocio_giu(r, e["soglie"][1])
    if cod == "E7":
        r = k.rsi(e["n"])
        return incrocio_su(r, e["meta"]) if long else incrocio_giu(r, e["meta"])
    if cod == "E8":
        pk, pd_ = k.get(("stoc",) + tuple(e["parametri"]),
                        lambda: stocastico(s.high, s.low, s.close, *[int(x) for x in e["parametri"]]))
        with np.errstate(invalid="ignore"):
            if long:
                return incrocio_su(pk, pd_) & (pk < e["soglie"][0])
            return incrocio_giu(pk, pd_) & (pk > e["soglie"][1])
    if cod == "E9":
        linea, sig = k.get(("macd",) + tuple(e["parametri"]),
                           lambda: macd(s.close, *[int(x) for x in e["parametri"]]))
        return incrocio_su(linea, sig) if long else incrocio_giu(linea, sig)
    if cod == "E10":
        su, giu = k.get(("asia",), lambda: range_asiatico(s.ts, s.high, s.low, s.durata))
        minuto = minuto_del_giorno(s.ts)
        finestra = (minuto >= 8 * 60) & (minuto < 16 * 60) & k.giorno_completo()
        with np.errstate(invalid="ignore"):
            oltre = (c > su) if long else (c < giu)
        cand = finestra & oltre
        # al massimo un segnale al giorno: la PRIMA chiusura oltre il range
        out = np.zeros(len(c), dtype=bool)
        giorno = inizio_giorno(s.ts)
        visto = None
        for i in np.flatnonzero(cand):
            if giorno[i] != visto:
                out[i] = True
                visto = giorno[i]
        return out
    if cod == "E11":
        prima = k.get(("prima_dopo_regolamento",), lambda: prima_candela_dopo_regolamento(s.ts, s.funding_ts))
        f = k.funding()
        with np.errstate(invalid="ignore"):
            oltre = (f > e["soglia"]) if e["lato"] == "sopra" else (f < e["soglia"])
        return prima & oltre
    if cod == "E12":
        vr = k.volrel(e["n"])
        with np.errstate(invalid="ignore"):
            return (vr > e["soglia"]) & ((c > s.open) if long else (c < s.open))
    raise VarianteNonValida(cod)


def _condizione_filtro(f: dict, long: bool, k: _Cache, s: Serie) -> np.ndarray:
    cod = f["codice"]
    c = s.close
    with np.errstate(invalid="ignore"):
        if cod == "F1":
            m = k.ema(f["n"])
            return (c > m) if f["lato"] == "sopra" else (c < m)
        if cod == "F2":
            a = k.adx(f["n"])
            return (a > f["soglia"]) if f["regime"] == "tendenza" else (a < f["soglia"])
        if cod == "F3":
            p = k.get(("atrpct", f["atr"], f["finestra"]),
                      lambda: atr_percentile(k.atr(f["atr"]), c, f["finestra"]))
            return (p > f["soglia"]) if f["regime"] == "alta" else (p < f["soglia"])
        if cod == "F4":
            fu = k.funding()
            return (fu > f["soglia"]) if f["lato"] == "sopra" else (fu < f["soglia"])
        if cod == "F5":
            a, b = SESSIONI[f["sessione"]]
            m = minuto_del_giorno(s.ts)
            return (m >= a) & (m < b)
        if cod == "F6":
            # 1970-01-01 era un giovedi': (giorni + 3) % 7 -> 0 = lunedi'
            g = ((np.asarray(s.ts, dtype=np.int64) // GIORNO_MS) + 3) % 7
            feriale = g < 5
            return feriale if f["giorni"] == "feriali" else ~feriale
        if cod == "F7":
            vw = k.get(("vwap",), lambda: vwap_giornaliero(s.ts, s.high, s.low, c, s.volume))
            ok = k.giorno_completo()
            return ((c > vw) if f["lato"] == "sopra" else (c < vw)) & ok
    raise VarianteNonValida(cod)


def _condizione_conferma(cf: dict, long: bool, k: _Cache, s: Serie) -> np.ndarray:
    cod = cf["codice"]
    c = s.close
    with np.errstate(invalid="ignore"):
        if cod == "C1":
            return k.volrel(cf["n"]) > cf["soglia"]
        if cod == "C2":
            return (c > s.open) if long else (c < s.open)
        if cod == "C3":
            r = k.rsi(cf["n"])
            return (r > cf["meta"]) if long else (r < cf["meta"])
    raise VarianteNonValida(cod)


def _ammesse(s: Serie, w: int) -> np.ndarray:
    """Vero dove sono passate almeno ``w`` candele dall'inizio del tratto senza buchi
    (7.8, 9.6): la candela t e' ammessa se t - inizio >= w."""
    out = np.zeros(len(s), dtype=bool)
    inizi = list(s.inizi_dei_tratti()) + [len(s)]
    for a, b in zip(inizi[:-1], inizi[1:]):
        if a + w < b:
            out[a + w:b] = True
    return out


def compila(variante: dict, serie: Serie, solo_catalogo: bool = True) -> Compilata:
    """Calcola gli array della variante sulla serie (la variante viene normalizzata)."""
    v = normalizza(variante, solo_catalogo=solo_catalogo)
    if v["timeframe"] != serie.timeframe:
        raise VarianteNonValida(f"la variante e' su {v['timeframe']}, la serie su {serie.timeframe}")
    long = v["direzione"] == "long"
    k = _Cache(serie)
    det: Dict[str, np.ndarray] = {}
    ingresso = _condizione_ingresso(v["ingresso"], long, k, serie, det)
    opposto = _condizione_ingresso(v["ingresso"], not long, k, serie, {})
    filtro = np.ones(len(serie), dtype=bool) if not v["filtro"] else _condizione_filtro(v["filtro"], long, k, serie)
    conferma = (np.ones(len(serie), dtype=bool) if not v["conferma"]
                else _condizione_conferma(v["conferma"], long, k, serie))
    w = riscaldamento(v)
    ammessa = _ammesse(serie, w)
    segnale = ingresso & filtro & conferma & ammessa
    opposto = opposto & ammessa
    atr_stop = k.atr(v["stop"]["atr"]) if v["stop"]["codice"] == "S1" else None
    atr_limite = k.atr(v["tipo_ingresso"]["atr"]) if v["tipo_ingresso"]["codice"] == "L" else None
    atr_tr = None
    for u in v["uscite"]:
        if u["codice"] == "U3":
            atr_tr = k.atr(u["atr"])
    estremo = None
    if v["stop"]["codice"] == "S2":
        n = v["stop"]["n"]
        estremo = _vuoto(len(serie))
        if len(serie) >= n:
            if long:
                estremo[n - 1:] = _finestre(serie.low, n).min(axis=1)
            else:
                estremo[n - 1:] = _finestre(serie.high, n).max(axis=1)
    fine_giornata = minuto_del_giorno(serie.ts) >= 21 * 60
    det.update({"ingresso": ingresso, "filtro": filtro, "conferma": conferma})
    return Compilata(v, serie, segnale, ammessa, opposto, atr_stop, atr_limite, atr_tr, estremo,
                     fine_giornata, w, det)


def sposta_periodi(variante: dict, fattore: float) -> dict:
    """La stessa variante con tutti i periodi moltiplicati per ``fattore`` e arrotondati
    all'intero (Fase 4, verifica 2: timeframe adiacenti). Orari, soglie e multipli non
    cambiano. La variante restituita va compilata con ``solo_catalogo=False``."""
    v = normalizza(variante, solo_catalogo=False)
    # SCELTA: arrotondamento all'intero piu' vicino, con le meta' per eccesso (EMA 9 da 1h a 2h -> 5)
    r = lambda n: max(1, int(math.floor(n * fattore + 0.5)))  # noqa: E731

    def periodi(el: Optional[dict]) -> Optional[dict]:
        if not el:
            return el
        el = dict(el)
        for chiave in ("n", "veloce", "lenta", "atr", "finestra", "validita"):
            if chiave in el and not isinstance(el[chiave], str):
                el[chiave] = r(el[chiave])
        if el["codice"] in ("E8", "E9"):
            el["parametri"] = [r(x) for x in el["parametri"]]
        return el

    v["filtro"] = periodi(v["filtro"])
    v["ingresso"] = periodi(v["ingresso"])
    v["conferma"] = periodi(v["conferma"])
    v["stop"] = periodi(v["stop"])
    v["tipo_ingresso"] = periodi(v["tipo_ingresso"])
    v["uscite"] = [periodi(u) for u in v["uscite"]]
    if v["ingresso"]["codice"] == "E1" and v["ingresso"]["veloce"] >= v["ingresso"]["lenta"]:
        raise VarianteNonValida("timeframe adiacente: le due medie di E1 coincidono dopo l'arrotondamento")
    return v
