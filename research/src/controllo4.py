"""Le verifiche sulle monete di controllo del protocollo 4 (``research/PROTOCOLLO_4.md``, sezione 4bis,
regola 10, Fase 3 punto 4, Fase 4 verifica 12, sezione 10.3 e Passo 3). Strumento del COORDINAMENTO: la
sessione di ricerca non lo usa, perche' il caricatore le rifiuta i dati delle monete di controllo.

* ``verifica_12``: la variante, senza modifiche, su ognuna delle 9 monete, sul periodo di costruzione,
  con le sue entrate casuali. Supera se batte la media delle proprie entrate casuali su almeno 7 monete
  su 9 (una moneta con meno di 30 trade conta come non superata) e se la media fra le monete dell'R
  medio e' positiva dopo i costi.
* ``controllo_fase3``: la variante nata dalla Fase 3 e quella da cui differisce, sul periodo di
  costruzione. Supera se la media fra le monete dell'R medio e' piu' alta di almeno 0,05 R.
* ``validazione_controllo``: il candidato sul periodo di validazione. Contano le monete con almeno 20
  trade, almeno 5; la media fra queste del vantaggio sulle entrate casuali e' di almeno 0,1 R e la
  media dell'R medio e' positiva dopo i costi. A costi doppi si riporta.

Le funzioni ``*_su_serie`` ricevono le serie gia' costruite (le usa anche il collaudo, sulle serie
senza direzione); le altre caricano i dati veri con ``dati.serie_4``. I dettagli che il testo lascia
aperti sono SCELTE dichiarate in ``research/collaudo_4/regole.md`` e qui, funzione per funzione.
"""

from __future__ import annotations

from datetime import date
from typing import Callable, Dict, Mapping, Optional

import numpy as np

from research.src import dati
from research.src import statistica3 as st3
from research.src.catalogo3 import Serie, compila, normalizza
from research.src.motore3 import COSTI_DOPPI, Costi, Regole, esegui, metriche

#: le monete di controllo e lo slippage per lato della loro fascia di volume 2023 (sezione 4bis)
MONETE_CONTROLLO: Dict[str, float] = {
    "BTCUSDT": 0.0001, "ETHUSDT": 0.0001, "SOLUSDT": 0.0001, "XRPUSDT": 0.0002, "DOGEUSDT": 0.0002,
    "BNBUSDT": 0.0002, "LTCUSDT": 0.0002, "MATICUSDT": 0.0002, "BCHUSDT": 0.0002,
}
#: margine di mantenimento di ogni moneta: il piu' alto dei livelli di Binance fino a 20.000 USDT di
#: valore della posizione (capitale 10.000 x leva 2; tabella pubblica letta il 17 ottobre 2026,
#: ``research/passo0_4/livelli_margine.json``)
MARGINE_CONTROLLO: Dict[str, float] = {
    "BTCUSDT": 0.004, "ETHUSDT": 0.004, "SOLUSDT": 0.005, "XRPUSDT": 0.005, "DOGEUSDT": 0.0065,
    "BNBUSDT": 0.006, "LTCUSDT": 0.01, "MATICUSDT": 0.007, "BCHUSDT": 0.01,
}
TRADE_MINIMI_12 = 30
MONETE_CHE_BATTONO_12 = 7
MIGLIORAMENTO_FASE3 = 0.05
TRADE_MINIMI_VALIDAZIONE = 20
MONETE_MINIME_VALIDAZIONE = 5
VANTAGGIO_MINIMO_VALIDAZIONE = 0.1

INIZIO_DATI = date(2020, 1, 1)


def costi_moneta(simbolo: str, doppi: bool = False) -> Costi:
    s = MONETE_CONTROLLO[simbolo]
    if doppi:
        return Costi(taker=COSTI_DOPPI.taker, maker=COSTI_DOPPI.maker, slippage=2 * s)
    return Costi(slippage=s)


def regole_moneta(simbolo: str) -> Regole:
    return Regole(mmr=MARGINE_CONTROLLO[simbolo])


def _intervallo(serie: Serie, da_ms: Optional[int], a_ms: int):
    """Indici [a, b] delle candele con apertura in [da_ms, a_ms]; None se vuoto."""
    ts = np.asarray(serie.ts)
    a = 0 if da_ms is None else int(np.searchsorted(ts, da_ms))
    b = int(np.searchsorted(ts, a_ms, side="right")) - 1
    return (a, b) if b >= a else None


def _una_moneta(variante: dict, serie: Serie, simbolo: str, da_ms: Optional[int], a_ms: int,
                con_casuali: bool, doppi: bool = False, seme: int = st3.SEME,
                n_simulazioni: int = st3.N_SIMULAZIONI) -> Dict[str, object]:
    out: Dict[str, object] = {"simbolo": simbolo}
    rng = _intervallo(serie, da_ms, a_ms)
    if rng is None:
        out.update(trade=0, r_medio=None, motivo="nessuna candela nel periodo")
        return out
    a, b = rng
    c = compila(variante, serie, solo_catalogo=False)
    regole = regole_moneta(simbolo)
    ris = esegui(c, regole, costi_moneta(simbolo), a, b)
    m = metriche(ris, serie)
    out.update(trade=m["trade"], r_medio=m["r_medio"] if m["trade"] else None,
               profit_factor=m["profit_factor"] if m["trade"] else None,
               violazioni_liquidazione=m.get("violazioni_liquidazione"))
    if doppi and m["trade"]:
        md = metriche(esegui(c, regole, costi_moneta(simbolo, doppi=True), a, b), serie)
        out["r_medio_costi_doppi"] = md["r_medio"]
    if con_casuali and m["trade"]:
        try:
            cas = st3.entrate_casuali(c, m["trade"], a, b, regole, costi_moneta(simbolo), n_simulazioni, seme,
                                      larghezze_candidato=[st3.larghezza_stop(t) for t in ris.trade])
            out["media_casuali"] = float(np.mean(cas["valori"]))
            out["p_value"] = st3.p_value(m["r_medio"], cas["valori"], n_simulazioni)
        except st3.SimulazioneImpossibile as errore:
            out["media_casuali"] = None
            out["casuali_impossibili"] = str(errore)
    return out


def verifica_12_su_serie(variante: dict, serie: Mapping[str, Serie], fine_ms: int, **kw) -> Dict[str, object]:
    """Verifica 12 su serie date (una per moneta, del timeframe della variante), dal loro inizio a
    ``fine_ms`` (apertura dell'ultima candela ammessa). SCELTA: la media dell'R medio e' fra le monete
    con almeno 30 trade."""
    v = normalizza(variante, solo_catalogo=False)
    monete = {}
    for simbolo, s in serie.items():
        x = _una_moneta(v, s, simbolo, None, fine_ms, con_casuali=True, **kw)
        x["batte"] = bool(x["trade"] >= TRADE_MINIMI_12 and x.get("media_casuali") is not None
                          and x["r_medio"] > x["media_casuali"])
        monete[simbolo] = x
    contano = [x for x in monete.values() if x["trade"] >= TRADE_MINIMI_12]
    battono = sum(1 for x in monete.values() if x["batte"])
    media = float(np.mean([x["r_medio"] for x in contano])) if contano else None
    supera = bool(battono >= MONETE_CHE_BATTONO_12 and media is not None and media > 0)
    return {"monete": monete, "battono": battono, "media_r": media, "supera": supera}


def controllo_fase3_su_serie(nuova: dict, vecchia: dict, serie_nuova: Mapping[str, Serie],
                             serie_vecchia: Mapping[str, Serie], fine_ms: int) -> Dict[str, object]:
    """Fase 3, punto 4, su serie date (una per moneta e per variante: con lo stesso timeframe sono le
    stesse). SCELTA: la media fra le monete si calcola sulle monete in cui tutte e due le varianti
    hanno almeno 30 trade, e servono almeno 5 monete cosi'."""
    nv, vv = normalizza(nuova, solo_catalogo=False), normalizza(vecchia, solo_catalogo=False)
    monete = {}
    for simbolo in serie_nuova:
        x = _una_moneta(nv, serie_nuova[simbolo], simbolo, None, fine_ms, con_casuali=False)
        y = _una_moneta(vv, serie_vecchia[simbolo], simbolo, None, fine_ms, con_casuali=False)
        monete[simbolo] = {"nuova": x, "vecchia": y}
    contano = [k for k, d in monete.items() if d["nuova"]["trade"] >= TRADE_MINIMI_12
               and d["vecchia"]["trade"] >= TRADE_MINIMI_12]
    if len(contano) < MONETE_MINIME_VALIDAZIONE:
        return {"monete": monete, "monete_che_contano": contano, "differenza": None, "supera": False,
                "motivo": f"meno di {MONETE_MINIME_VALIDAZIONE} monete con almeno {TRADE_MINIMI_12} trade per tutte e due"}
    media_n = float(np.mean([monete[k]["nuova"]["r_medio"] for k in contano]))
    media_v = float(np.mean([monete[k]["vecchia"]["r_medio"] for k in contano]))
    diff = media_n - media_v
    return {"monete": monete, "monete_che_contano": contano, "media_nuova": media_n, "media_vecchia": media_v,
            "differenza": diff, "supera": bool(diff >= MIGLIORAMENTO_FASE3)}


def validazione_controllo_su_serie(variante: dict, serie: Mapping[str, Serie], inizio_ms: int, fine_ms: int,
                                   **kw) -> Dict[str, object]:
    """Validazione sulle monete di controllo (10.3), su serie date che contengono anche la storia prima
    di ``inizio_ms`` (gli indicatori arrivano gia' calcolati, come in costruzione)."""
    v = normalizza(variante, solo_catalogo=False)
    monete = {}
    for simbolo, s in serie.items():
        x = _una_moneta(v, s, simbolo, inizio_ms, fine_ms, con_casuali=True, doppi=True, **kw)
        x["conta"] = bool(x["trade"] >= TRADE_MINIMI_VALIDAZIONE and x.get("media_casuali") is not None)
        if x["conta"]:
            x["vantaggio"] = x["r_medio"] - x["media_casuali"]
        monete[simbolo] = x
    contano = [x for x in monete.values() if x["conta"]]
    if len(contano) < MONETE_MINIME_VALIDAZIONE:
        return {"monete": monete, "monete_che_contano": len(contano), "supera": False,
                "motivo": f"meno di {MONETE_MINIME_VALIDAZIONE} monete con almeno {TRADE_MINIMI_VALIDAZIONE} trade"}
    vantaggio = float(np.mean([x["vantaggio"] for x in contano]))
    media_r = float(np.mean([x["r_medio"] for x in contano]))
    doppi = [x.get("r_medio_costi_doppi") for x in contano if x.get("r_medio_costi_doppi") is not None]
    return {"monete": monete, "monete_che_contano": len(contano), "vantaggio_medio": vantaggio, "media_r": media_r,
            "media_r_costi_doppi": float(np.mean(doppi)) if doppi else None,
            "supera": bool(vantaggio >= VANTAGGIO_MINIMO_VALIDAZIONE and media_r > 0)}


# ---------------------------------------------------------------------------
# Sui dati veri (coordinamento)
# ---------------------------------------------------------------------------

def serie_vere(timeframe: str, fine: date, caricatore: Callable = dati.serie_4) -> Dict[str, Serie]:
    """Le serie vere delle 9 monete di controllo, dal 2020-01-01 a ``fine`` (al massimo 2023-12-31)."""
    return {s: caricatore(s, timeframe, INIZIO_DATI, fine) for s in MONETE_CONTROLLO}


def verifica_12(variante: dict) -> Dict[str, object]:
    v = normalizza(variante, solo_catalogo=False)
    fine_ms = dati.ms_da_data(dati.INIZIO_VALIDAZIONE_3) - 1
    return verifica_12_su_serie(v, serie_vere(v["timeframe"], dati.FINE_COSTRUZIONE_3), fine_ms)


def controllo_fase3(nuova: dict, vecchia: dict) -> Dict[str, object]:
    nv, vv = normalizza(nuova, solo_catalogo=False), normalizza(vecchia, solo_catalogo=False)
    fine_ms = dati.ms_da_data(dati.INIZIO_VALIDAZIONE_3) - 1
    serie_n = serie_vere(nv["timeframe"], dati.FINE_COSTRUZIONE_3)
    serie_v = serie_n if vv["timeframe"] == nv["timeframe"] else serie_vere(vv["timeframe"], dati.FINE_COSTRUZIONE_3)
    return controllo_fase3_su_serie(nv, vv, serie_n, serie_v, fine_ms)


def validazione_controllo(variante: dict) -> Dict[str, object]:
    v = normalizza(variante, solo_catalogo=False)
    serie = serie_vere(v["timeframe"], dati.FINE_IN_SAMPLE)
    inizio_ms = dati.ms_da_data(dati.INIZIO_VALIDAZIONE_3)
    fine_ms = dati.ms_da_data(date(2024, 1, 1)) - 1
    return validazione_controllo_su_serie(v, serie, inizio_ms, fine_ms)
