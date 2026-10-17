"""Le verifiche della Fase 4 cambiate o nuove nel protocollo 4 (``research/PROTOCOLLO_4.md``, Fase 4,
verifiche 1, 3, 3bis e 4). Il resto delle regole statistiche e' quello del protocollo 3
(``statistica3``), che qui non cambia.

* ``mosse_robustezza_4`` (verifica 1): come ``statistica3.mosse_robustezza``, ma se dopo
  l'arrotondamento il valore non cambia si sposta di un passo dell'arrotondamento nella stessa
  direzione; uno spostamento che da' un valore non valido si riporta e non si prova.
* ``stabilita_blocchi_4`` (verifica 3): quattro blocchi di circa 8 mesi, per LINKUSDT dal 2020-01-17.
* ``mercati_forti`` (verifica 3bis): i semestri di forte rialzo e di forte ribasso.
* ``senza_i_migliori_4`` (verifica 4): tolto il 5% dei trade migliori dal candidato e da ognuna
  delle sue entrate casuali, il vantaggio sul caso deve restare almeno a meta'.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from research.src import statistica3 as st3
from research.src.catalogo3 import Compilata, Serie, normalizza
from research.src.motore3 import COSTI_NORMALI, Costi, Regole, Risultato

#: regole e costi della ricerca su LINKUSDT (sezioni 6 e 9.4): slippage 0,02% a lato; margine di
#: mantenimento 1%, il piu' alto dei livelli di Binance fino a 20.000 USDT di valore della posizione
#: (tabella pubblica letta il 17 ottobre 2026: 0,5% fino a 10.000, 1% oltre)
REGOLE_LINK = Regole(mmr=0.01)
COSTI_LINK = Costi(slippage=0.0002)
COSTI_DOPPI_LINK = Costi(taker=0.0010, maker=0.0004, slippage=0.0004)

# ---------------------------------------------------------------------------
# Verifica 1 — robustezza dei parametri, con il passo fisso
# ---------------------------------------------------------------------------

#: il passo dell'arrotondamento di ogni tipo di parametro (Fase 4, verifica 1)
PASSI = {"periodo": 1, "intero": 1, "multiplo": 0.1, "da_50": 0.1, "funding": 0.00005, "percento": 0.001}


def _sposta(valore: float, tipo: str, segno: int) -> Tuple[float, bool]:
    """Il valore spostato del 20% (segno -1 o +1) e arrotondato; se l'arrotondamento lo lascia
    com'era, di un passo nella direzione dello spostamento (per un valore negativo il −20% va verso
    lo zero; per lo zero, che il 20% non sposta, la direzione e' il segno). Il secondo valore dice
    se il passo fisso e' servito."""
    fattore = 1 + 0.2 * segno
    if tipo == "da_50":
        grezzo = 50 + (valore - 50) * fattore
    else:
        grezzo = valore * fattore
    if tipo in ("periodo", "intero"):
        nuovo = int(math.floor(grezzo + 0.5))
    else:
        nuovo = st3._arrotonda(grezzo, PASSI[tipo])
    if abs(nuovo - valore) < 1e-12:
        direzione = 1 if grezzo > valore + 1e-15 else -1 if grezzo < valore - 1e-15 else segno
        nuovo = valore + direzione * PASSI[tipo]
        nuovo = int(round(nuovo)) if tipo in ("periodo", "intero") else round(nuovo, 10)
        return nuovo, True
    return nuovo, False


def _valido(tipo: str, valore: float) -> bool:
    if tipo in ("periodo",):
        return valore >= 1
    if tipo in ("multiplo", "percento"):
        return valore > 0
    if tipo == "da_50":
        return 0 < valore < 100
    return True


def mosse_robustezza_4(variante: dict) -> Tuple[List[Tuple[str, dict]], List[str]]:
    """Le mosse della verifica 1 e l'elenco delle mosse non provate perche' danno un valore non
    valido. Stessi parametri e stessi arrotondamenti di ``statistica3.mosse_robustezza`` (le sue
    scelte dichiarate valgono anche qui)."""
    v = normalizza(variante, solo_catalogo=False)
    mosse: List[Tuple[str, dict]] = []
    non_provate: List[str] = []

    def prova(sezione: str, indice: Optional[int], chiave: str, sotto: Optional[int], tipo: str):
        base = v[sezione] if indice is None else v[sezione][indice]
        valore = base[chiave] if sotto is None else base[chiave][sotto]
        for segno, nome in ((-1, "-20%"), (1, "+20%")):
            nuovo, fisso = _sposta(valore, tipo, segno)
            etichetta = (f"{sezione}{'' if indice is None else f'[{indice}]'}.{chiave}"
                         f"{'' if sotto is None else f'[{sotto}]'} {nome}{' (passo fisso)' if fisso else ''} "
                         f"({valore} -> {nuovo})")
            if not _valido(tipo, nuovo):
                non_provate.append(etichetta + ": valore non valido")
                continue
            w = normalizza(v, solo_catalogo=False)
            el = w[sezione] if indice is None else w[sezione][indice]
            if sotto is None:
                el[chiave] = nuovo
            else:
                lista = list(el[chiave])
                lista[sotto] = nuovo
                el[chiave] = lista
            try:
                normalizza(w, solo_catalogo=False)
            except (ValueError, KeyError) as errore:
                non_provate.append(f"{etichetta}: variante impossibile ({errore})")
                continue
            mosse.append((etichetta, w))

    for sezione in ("filtro", "ingresso", "conferma", "tipo_ingresso", "stop"):
        el = v.get(sezione)
        if not el:
            continue
        cod = el["codice"]
        for chiave in ("n", "veloce", "lenta", "atr", "finestra", "validita"):
            if chiave in el:
                prova(sezione, None, chiave, None, "periodo")
        if cod in ("E8", "E9"):
            for j in range(3):
                prova(sezione, None, "parametri", j, "periodo")
        if cod in ("E4", "E5", "S1", "L"):
            prova(sezione, None, "k", None, "multiplo")
        if cod in ("E6", "E8"):
            usa_opposto = any(u["codice"] == "U4" for u in v["uscite"])
            if v["direzione"] == "long" or usa_opposto:
                prova(sezione, None, "soglie", 0, "da_50")
            if v["direzione"] == "short" or usa_opposto:
                prova(sezione, None, "soglie", 1, "da_50")
        if cod in ("E12", "C1"):
            prova(sezione, None, "soglia", None, "multiplo")
        if cod in ("E11", "F4"):
            prova(sezione, None, "soglia", None, "funding")
        if cod in ("F2", "F3"):
            prova(sezione, None, "soglia", None, "intero")
        if cod == "S3":
            prova(sezione, None, "pct", None, "percento")
    for j, u in enumerate(v["uscite"]):
        if "n" in u:
            prova("uscite", j, "n", None, "periodo")
        if "atr" in u:
            prova("uscite", j, "atr", None, "periodo")
        if "k" in u:
            prova("uscite", j, "k", None, "multiplo")
    return mosse, non_provate


# ---------------------------------------------------------------------------
# Verifica 3 — stabilita' nel tempo, blocchi di circa 8 mesi
# ---------------------------------------------------------------------------

BLOCCHI_4 = (("inizio", "2020-09-30"), ("2020-10-01", "2021-05-31"), ("2021-06-01", "2022-01-31"),
             ("2022-02-01", "2022-09-30"))


def stabilita_blocchi_4(ris: Risultato) -> Dict[str, object]:
    """Verifica 3 con i blocchi del protocollo 4; stesse regole di ``statistica3.stabilita_blocchi``."""
    vecchi = st3.BLOCCHI
    try:
        st3.BLOCCHI = BLOCCHI_4
        return st3.stabilita_blocchi(ris)
    finally:
        st3.BLOCCHI = vecchi


# ---------------------------------------------------------------------------
# Verifica 3bis — mercati in forte rialzo e in forte ribasso
# ---------------------------------------------------------------------------

SOGLIA_MERCATO_FORTE = 0.30
TRADE_MINIMI_GRUPPO = 30


def _semestre(ms: int) -> str:
    d = datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc)
    return f"{d.year}H{1 if d.month <= 6 else 2}"


def variazioni_semestrali(serie_1d: Serie) -> Dict[str, float]:
    """Per ogni semestre solare presente nella serie giornaliera: chiusura dell'ultima candela
    del semestre ÷ apertura della prima − 1."""
    out: Dict[str, Tuple[float, float]] = {}
    for ts, op, cl in zip(serie_1d.ts, serie_1d.open, serie_1d.close):
        k = _semestre(int(ts))
        if k not in out:
            out[k] = (float(op), float(cl))
        else:
            out[k] = (out[k][0], float(cl))
    return {k: cl / op - 1 for k, (op, cl) in out.items()}


def mercati_forti(ris: Risultato, serie_1d: Serie) -> Dict[str, object]:
    """Verifica 3bis: in ciascuno dei due gruppi (semestri di forte rialzo, +30% o piu'; di forte
    ribasso, −30% o meno) che ha almeno 30 trade, l'R medio e' positivo. Un gruppo con meno di 30
    trade non decide; se nessuno dei due ne ha 30, la verifica e' superata ("non applicabile")."""
    var = variazioni_semestrali(serie_1d)
    gruppi = {"forte_rialzo": [], "forte_ribasso": []}
    for t in ris.trade:
        v = var.get(_semestre(t.ts_ingresso))
        if v is None:
            continue
        if v >= SOGLIA_MERCATO_FORTE:
            gruppi["forte_rialzo"].append(t.r)
        elif v <= -SOGLIA_MERCATO_FORTE:
            gruppi["forte_ribasso"].append(t.r)
    esito = {}
    decisi = 0
    supera = True
    for nome, rr in gruppi.items():
        decide = len(rr) >= TRADE_MINIMI_GRUPPO
        r_medio = (sum(rr) / len(rr)) if rr else None
        if decide:
            decisi += 1
            supera = supera and r_medio > 0
        esito[nome] = {"trade": len(rr), "r_medio": r_medio, "decide": decide}
    esito["semestri"] = {k: round(v, 4) for k, v in sorted(var.items())}
    esito["non_applicabile"] = decisi == 0
    esito["supera"] = supera
    return esito


# ---------------------------------------------------------------------------
# Verifica 4 — pochi trade estremi, contro il caso tolto allo stesso modo
# ---------------------------------------------------------------------------

QUOTA_MIGLIORI = 0.05


def _togli_migliori(rr: Sequence[float], quota: float = QUOTA_MIGLIORI) -> List[float]:
    r = sorted(rr, reverse=True)
    k = int(math.ceil(quota * len(r)))
    return r[k:]


def entrate_casuali_con_trade(c: Compilata, n_trade: int, inizio: int, fine: int, regole: Regole = Regole(),
                              costi: Costi = COSTI_NORMALI, **kw) -> Tuple[dict, List[List[float]]]:
    """``statistica3.entrate_casuali`` con, in piu', gli R dei trade di ogni simulazione tenuta, in
    ordine. Stesso generatore e stesso seme: le simulazioni (e quindi ``valori``) sono le stesse di
    una chiamata normale; l'osservatore registra soltanto."""
    raccolti: List[List[float]] = []
    vecchio = st3._OSSERVATORE
    st3._OSSERVATORE = lambda lista: raccolti.append([float(t.r) for _, t in lista])
    try:
        cas = st3.entrate_casuali(c, n_trade, inizio, fine, regole, costi, **kw)
    finally:
        st3._OSSERVATORE = vecchio
    return cas, raccolti


def senza_i_migliori_4(ris: Risultato, trade_casuali: Sequence[Sequence[float]],
                       quota: float = QUOTA_MIGLIORI) -> Dict[str, object]:
    """Verifica 4: si tolgono i trade migliori, il 5% (per eccesso), dal candidato e da ognuna delle
    sue entrate casuali. Supera se l'R medio del candidato senza i migliori resta positivo e il suo
    vantaggio sulla media delle entrate casuali senza i migliori e' almeno la meta' di quello con
    tutti i trade (che deve essere positivo)."""
    rr = [t.r for t in ris.trade]
    if not rr or not trade_casuali:
        return {"supera": False, "motivo": "nessun trade o nessuna entrata casuale"}
    intero = sum(rr) / len(rr)
    tolti = _togli_migliori(rr, quota)
    r_tolti = (sum(tolti) / len(tolti)) if tolti else float("nan")
    casuali_intere = float(np.mean([sum(s) / len(s) for s in trade_casuali]))
    casuali_tolte = float(np.mean([np.mean(_togli_migliori(s, quota)) for s in trade_casuali]))
    vantaggio = intero - casuali_intere
    vantaggio_tolti = r_tolti - casuali_tolte
    supera = bool(r_tolti > 0 and vantaggio > 0 and vantaggio_tolti >= 0.5 * vantaggio)
    return {"trade_tolti": len(rr) - len(tolti), "r_medio": intero, "r_medio_senza_migliori": r_tolti,
            "casuali_r_medio": casuali_intere, "casuali_r_medio_senza_migliori": casuali_tolte,
            "vantaggio": vantaggio, "vantaggio_senza_migliori": vantaggio_tolti, "supera": supera}


# ---------------------------------------------------------------------------
# Fase 2 e Fase 4 complete per LINKUSDT (costi e margine della moneta)
# ---------------------------------------------------------------------------

def fase2_4(variante: dict, serie: Serie, inizio: int, fine: int, regole: Regole = REGOLE_LINK,
            costi: Costi = COSTI_LINK, n_simulazioni: int = st3.N_SIMULAZIONI, seme: int = st3.SEME,
            solo_catalogo: bool = True, compilata: Optional[Compilata] = None) -> Dict[str, object]:
    """La Fase 2 completa (``statistica3.fase2``) con i costi e il margine di LINKUSDT. Stesse chiavi
    nel risultato."""
    from research.src.catalogo3 import compila
    from research.src.motore3 import esegui, metriche
    c = compilata if compilata is not None else compila(variante, serie, solo_catalogo=solo_catalogo)
    ris = esegui(c, regole, costi, inizio, fine)
    m = metriche(ris, serie)
    p = None
    casuali = None
    if m["trade"] > 0:
        casuali = st3.entrate_casuali(c, m["trade"], inizio, fine, regole, costi, n_simulazioni, seme,
                                      larghezze_candidato=[st3.larghezza_stop(t) for t in ris.trade])
        p = st3.p_value(m["r_medio"], casuali["valori"], n_simulazioni)
    esiti = st3.supera_costruzione(m, p)
    return {"metriche": m, "p_value": p,
            "casuali": None if casuali is None else {k: v for k, v in casuali.items() if k != "valori"},
            "valori_casuali": None if casuali is None else casuali["valori"],
            "esiti": esiti, "supera": esiti["supera"],
            "buy_and_hold": st3.buy_and_hold(serie, inizio, fine),
            "somma_r_strategia": sum(t.r for t in ris.trade), "risultato": ris, "compilata": c}


def fase4_4(variante: dict, serie: Serie, inizio: int, fine: int, serie_di, serie_giornaliera: Serie,
            regole: Regole = REGOLE_LINK, costi: Costi = COSTI_LINK, costi_doppi: Costi = COSTI_DOPPI_LINK,
            base: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    """Le verifiche della Fase 4 del protocollo 4 fatte dalla sessione di ricerca (tutte tranne la 12,
    che esegue il coordinamento): 1, 3, 3bis e 4 nella forma nuova, le altre come nel protocollo 3,
    con i costi e il margine di LINKUSDT. ``serie_di(timeframe)`` da' la serie di un altro timeframe
    con gli indici del periodo (verifica 2); ``serie_giornaliera`` le candele giornaliere di LINKUSDT
    della costruzione (verifica 3bis)."""
    from dataclasses import replace

    from research.src.catalogo3 import TIMEFRAME_MS, VarianteNonValida, compila, sposta_periodi
    from research.src.motore3 import esegui, metriche, test_troncamento
    v = normalizza(variante)
    if base is None:
        base = fase2_4(variante, serie, inizio, fine, regole, costi)
    ris0: Risultato = base["risultato"]
    c0: Compilata = base["compilata"]
    r0 = base["metriche"]["r_medio"]
    out: Dict[str, object] = {}

    # 1. robustezza dei parametri (con il passo fisso)
    mosse, non_provate = mosse_robustezza_4(v)
    prove = [{"mossa": e, "non_provata": "valore non valido"} for e in non_provate]
    for etichetta, w in mosse:
        try:
            cw = compila(w, serie, solo_catalogo=False)
        except VarianteNonValida as e:
            prove.append({"mossa": etichetta, "non_provata": str(e)})
            continue
        m = metriche(esegui(cw, regole, costi, inizio, fine), serie)
        prove.append({"mossa": etichetta, "trade": m["trade"], "r_medio": m["r_medio"]})
    provate = [p for p in prove if "r_medio" in p]
    out["1_robustezza"] = {"prove": prove, "supera": bool(provate) and all(p["r_medio"] > 0 for p in provate)}

    # 2. timeframe adiacenti
    prove = []
    for tf in st3.timeframe_adiacenti(v["timeframe"], v):
        s2, a2, b2 = serie_di(tf)
        fattore = TIMEFRAME_MS[v["timeframe"]] / TIMEFRAME_MS[tf]
        try:
            w = sposta_periodi(v, fattore)
            w["timeframe"] = tf
            cw = compila(w, s2, solo_catalogo=False)
        except VarianteNonValida as e:
            prove.append({"timeframe": tf, "non_provata": str(e)})
            continue
        m = metriche(esegui(cw, regole, costi, a2, b2), s2)
        prove.append({"timeframe": tf, "trade": m["trade"], "r_medio": m["r_medio"]})
    provate = [p for p in prove if "r_medio" in p]
    out["2_timeframe_adiacenti"] = {"prove": prove,
                                    "supera": bool(provate) and all(p["r_medio"] > 0 for p in provate)}

    # 3. stabilita' nel tempo (blocchi di circa 8 mesi) e 3bis. mercati forti
    out["3_blocchi"] = stabilita_blocchi_4(ris0)
    out["3bis_mercati_forti"] = mercati_forti(ris0, serie_giornaliera)
    # 4. pochi trade estremi, contro il caso tolto allo stesso modo
    _, trade_casuali = entrate_casuali_con_trade(
        c0, len(ris0.trade), inizio, fine, regole, costi,
        larghezze_candidato=[st3.larghezza_stop(t) for t in ris0.trade])
    out["4_senza_i_migliori"] = senza_i_migliori_4(ris0, trade_casuali)
    # 5. costi doppi
    md = metriche(esegui(c0, regole, costi_doppi, inizio, fine), serie)
    out["5_costi_doppi"] = {"r_medio": md["r_medio"], "supera": md["r_medio"] > 0}
    # 6. troncamento
    diff = test_troncamento(v, serie, inizio, fine)
    out["6_troncamento"] = {"differenze": diff, "supera": not diff}
    # 7. liquidazione
    viol = base["metriche"]["violazioni_liquidazione"]
    out["7_liquidazione"] = {"violazioni": viol, "supera": viol == 0}
    limit = v["tipo_ingresso"]["codice"] == "L"
    # 8. riempimento severo (solo limit)
    if limit:
        ms = metriche(esegui(c0, replace(regole, scarto_riempimento=0.0005), costi, inizio, fine), serie)
        out["8_riempimento_severo"] = {"trade": ms["trade"], "r_medio": ms["r_medio"], "supera": ms["r_medio"] > 0}
    # 9. regola intra-barra opposta (informativa)
    mi = metriche(esegui(c0, replace(regole, intrabarra="target_prima"), costi, inizio, fine), serie)
    out["9_intrabarra_opposta"] = {"r_medio": mi["r_medio"], "differenza": mi["r_medio"] - r0}
    # 10. ritardo di una candela (informativa)
    mr = metriche(esegui(c0, replace(regole, ritardo=1), costi, inizio, fine), serie)
    out["10_ritardo"] = {"trade": mr["trade"], "r_medio": mr["r_medio"], "differenza": mr["r_medio"] - r0}
    # 11. versione a mercato (solo limit, informativa)
    if limit:
        w = normalizza(v)
        w["tipo_ingresso"] = {"codice": "M"}
        cm = compila(w, serie)
        mm = metriche(esegui(cm, regole, costi, inizio, fine), serie)
        out["11_versione_a_mercato"] = {"trade": mm["trade"], "r_medio": mm["r_medio"], "differenza": r0 - mm["r_medio"]}
    decisive = ["1_robustezza", "2_timeframe_adiacenti", "3_blocchi", "3bis_mercati_forti", "4_senza_i_migliori",
                "5_costi_doppi", "6_troncamento", "7_liquidazione"] + (["8_riempimento_severo"] if limit else [])
    out["decisive_superate"] = all(out[k]["supera"] for k in decisive)
    out["manca"] = "12_monete_di_controllo (la esegue il coordinamento, regola 10)"
    return out
