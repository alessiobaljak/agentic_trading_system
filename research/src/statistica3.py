"""Le regole statistiche e le verifiche del protocollo 3 (``research/PROTOCOLLO_3.md``,
sezioni 10 e 13: Fase 2, Fase 4, Passi 3, 5 e 6).

* ``entrate_casuali`` (10.1): 1.000 simulazioni con ingressi scelti a caso fra TUTTE le
  candele ammesse del periodo, indipendentemente da quando il candidato e' in posizione;
* ``p_value`` (10.2): (1 + simulazioni con R medio >= candidato) / 1.001;
* ``fase2``: la Fase 2 completa (metriche, entrate casuali, p-value, soglie di
  costruzione, buy and hold e somma degli R per anno);
* ``fase4``: le undici verifiche sui candidati;
* soglie di validazione, vault (con Benjamini-Hochberg) e altre monete.

Lo stesso codice serve alla ricerca e al collaudo del metodo (sezione 13bis).
"""

from __future__ import annotations

import math
from dataclasses import replace
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from research.src.catalogo3 import (Compilata, Serie, TIMEFRAME, TIMEFRAME_FINO_A_1H, TIMEFRAME_MS,
                                    SOLO_FINO_A_1H, VarianteNonValida, compila, normalizza,
                                    sposta_periodi)
from research.src.motore3 import (COSTI_DOPPI, COSTI_NORMALI, Costi, Regole, Risultato, esegui,
                                  metriche, simula_da, test_troncamento)
from research.src.statistica import benjamini_hochberg  # stessa procedura della 10.4

N_SIMULAZIONI = 1000
SEME = 2026

SOGLIE_COSTRUZIONE = {"trade": 150, "r_medio": 0.2, "p_value": 0.023}
SOGLIE_VALIDAZIONE = {"trade": 60, "frazione_di_costruzione": 0.5, "profit_factor": 1.05}
SOGLIE_VAULT = {"trade": 100, "profit_factor": 1.10, "q": 0.10}
SOGLIE_ALTRE_MONETE = {"trade": 100, "profit_factor": 1.10, "p_value": 0.10}


class SimulazioneImpossibile(RuntimeError):
    """Le candele ammesse non bastano per mettere il numero di trade del candidato senza
    sovrapposizioni: STOP, la situazione non e' prevista dal protocollo."""


# ---------------------------------------------------------------------------
# 10.1 entrate casuali e 10.2 p-value
# ---------------------------------------------------------------------------


def entrate_casuali(c: Compilata, n_trade: int, inizio: int, fine: int, regole: Regole = Regole(),
                    costi: Costi = COSTI_NORMALI, n_simulazioni: int = N_SIMULAZIONI,
                    seme: int = SEME, cache: Optional[dict] = None) -> Dict[str, object]:
    """Le entrate casuali della sezione 10.1.

    Per ogni simulazione le candele ammesse del periodo si prendono in un ordine a caso
    (un solo generatore, seme fisso 2026, per tutte le simulazioni in fila). Per ogni
    candela si apre il trade che la variante aprirebbe con un segnale li': stesso tipo di
    ingresso (a mercato, oppure ordine limit con gli stessi k e validita'), stesso stop,
    stesse uscite, stessi costi. Il trade si tiene se non si sovrappone a quelli gia'
    presi; un ordine limit non eseguito, o un trade che non si apre perche' lo stop e'
    troppo vicino, si scarta e si passa alla candela successiva. Ci si ferma quando i
    trade sono tanti quanti quelli del candidato.

    SCELTA: un trade occupa le candele dalla decisione all'uscita (la candela di uscita
    resta libera per una nuova decisione alla sua chiusura, come per il candidato);
    gli ordini limit non eseguiti non occupano tempo.
    """
    if n_trade <= 0:
        raise ValueError("servono almeno un trade del candidato")
    ammesse = np.flatnonzero(c.ammessa[inizio:fine + 1]) + inizio
    if cache is None:
        cache = {}

    def esito(j: int):
        e = cache.get(j)
        if e is None:
            e = simula_da(c, j, regole, costi, fine, forzato=True)
            cache[j] = e
        return e

    rng = np.random.default_rng(seme)
    medie: List[float] = []
    occupato = np.zeros(len(c.serie) + 1, dtype=bool)
    for _ in range(n_simulazioni):
        ordine = rng.permutation(ammesse)
        occupato[:] = False
        presi: List[float] = []
        for j in ordine:
            j = int(j)
            if occupato[j]:
                continue
            e = esito(j)
            if e.tipo != "trade":
                continue
            a, b = j, max(e.libero_da, j + 1)
            if occupato[a:b].any():
                continue
            occupato[a:b] = True
            presi.append(e.trade.r)
            if len(presi) == n_trade:
                break
        if len(presi) < n_trade:
            raise SimulazioneImpossibile(
                f"una simulazione ha trovato solo {len(presi)} trade su {n_trade}")
        medie.append(sum(presi) / n_trade)
    valori = np.asarray(medie)
    return {"valori": valori, "media": float(valori.mean()), "percentile_95": float(np.percentile(valori, 95)),
            "candele_ammesse": int(len(ammesse)), "n_simulazioni": n_simulazioni, "seme": seme}


def p_value(r_candidato: float, valori: Sequence[float], n_simulazioni: int = N_SIMULAZIONI) -> float:
    """10.2: p = (1 + simulazioni con R medio >= candidato) / (n + 1), con n = 1.000."""
    valori = np.asarray(valori, dtype=np.float64)
    if len(valori) != n_simulazioni:
        raise ValueError(f"servono esattamente {n_simulazioni} simulazioni, non {len(valori)}")
    return float((1 + int(np.sum(valori >= r_candidato))) / (n_simulazioni + 1))


# ---------------------------------------------------------------------------
# 10.3 soglie
# ---------------------------------------------------------------------------


def supera_costruzione(m: Dict[str, object], p: Optional[float]) -> Dict[str, bool]:
    s = SOGLIE_COSTRUZIONE
    esiti = {"trade": m["trade"] >= s["trade"], "r_medio": m["r_medio"] >= s["r_medio"],
             "p_value": p is not None and p <= s["p_value"]}
    esiti["supera"] = all(esiti.values())
    return esiti


def supera_validazione(m: Dict[str, object], m_doppi: Dict[str, object], r_costruzione: float) -> Dict[str, bool]:
    s = SOGLIE_VALIDAZIONE
    esiti = {"trade": m["trade"] >= s["trade"], "r_positivo": m["r_medio"] > 0,
             "meta_di_costruzione": m["r_medio"] >= s["frazione_di_costruzione"] * r_costruzione,
             "profit_factor": m["profit_factor"] >= s["profit_factor"], "costi_doppi": m_doppi["r_medio"] > 0}
    esiti["supera"] = all(esiti.values())
    return esiti


def supera_vault(m: Dict[str, object], m_doppi: Dict[str, object]) -> Dict[str, bool]:
    """Le condizioni del vault SENZA l'asticella di Benjamini-Hochberg (si applica a tutti
    i candidati insieme: ``asticella_vault``)."""
    s = SOGLIE_VAULT
    esiti = {"trade": m["trade"] >= s["trade"], "r_positivo": m["r_medio"] > 0,
             "costi_doppi": m_doppi["r_medio"] > 0, "profit_factor": m["profit_factor"] >= s["profit_factor"]}
    esiti["supera_senza_asticella"] = all(esiti.values())
    return esiti


def asticella_vault(p_values: Sequence[float], q: float = SOGLIE_VAULT["q"]) -> List[bool]:
    """10.4: Benjamini-Hochberg al 10% sui p-value del vault di tutti i candidati."""
    return benjamini_hochberg(list(p_values), q=q)


def regge_altra_moneta(m: Dict[str, object], p: Optional[float]) -> Dict[str, bool]:
    s = SOGLIE_ALTRE_MONETE
    esiti = {"trade": m["trade"] >= s["trade"], "r_positivo": m["r_medio"] > 0,
             "profit_factor": m["profit_factor"] >= s["profit_factor"],
             "p_value": p is not None and p <= s["p_value"]}
    esiti["regge"] = all(esiti.values())
    return esiti


# ---------------------------------------------------------------------------
# Fase 2
# ---------------------------------------------------------------------------


def buy_and_hold(serie: Serie, inizio: int, fine: int) -> float:
    """Rendimento del buy and hold dal prezzo di apertura della prima candela del periodo
    alla chiusura dell'ultima (informativo, Fase 2 punto 3)."""
    return float(serie.close[fine] / serie.open[inizio] - 1.0)


def fase2(variante: dict, serie: Serie, inizio: int, fine: int, regole: Regole = Regole(),
          n_simulazioni: int = N_SIMULAZIONI, seme: int = SEME, solo_catalogo: bool = True,
          compilata: Optional[Compilata] = None) -> Dict[str, object]:
    """La Fase 2 completa sul periodo [inizio, fine] (indici della serie)."""
    c = compilata if compilata is not None else compila(variante, serie, solo_catalogo=solo_catalogo)
    ris = esegui(c, regole, COSTI_NORMALI, inizio, fine)
    m = metriche(ris, serie)
    p = None
    casuali = None
    if m["trade"] > 0:
        casuali = entrate_casuali(c, m["trade"], inizio, fine, regole, COSTI_NORMALI, n_simulazioni, seme)
        p = p_value(m["r_medio"], casuali["valori"], n_simulazioni)
    esiti = supera_costruzione(m, p)
    return {"metriche": m, "p_value": p,
            "casuali": None if casuali is None else {k: v for k, v in casuali.items() if k != "valori"},
            "valori_casuali": None if casuali is None else casuali["valori"],
            "esiti": esiti, "supera": esiti["supera"],
            "buy_and_hold": buy_and_hold(serie, inizio, fine),
            "somma_r_strategia": sum(t.r for t in ris.trade), "risultato": ris, "compilata": c}


# ---------------------------------------------------------------------------
# Fase 4
# ---------------------------------------------------------------------------

#: blocchi di stabilita' nel tempo (Fase 4, verifica 3): [inizio, fine] in giorni UTC
BLOCCHI = (("inizio", "2020-06-30"), ("2020-07-01", "2021-03-31"), ("2021-04-01", "2021-12-31"),
           ("2022-01-01", "2022-09-30"))


def _ms(giorno: str) -> int:
    import datetime as _dt
    d = _dt.datetime.strptime(giorno, "%Y-%m-%d").replace(tzinfo=_dt.timezone.utc)
    return int(d.timestamp() * 1000)


def stabilita_blocchi(ris: Risultato) -> Dict[str, object]:
    """Verifica 3: R medio positivo in almeno 3 blocchi su 4 e nessun blocco con piu' del
    50% della somma degli R. SCELTA: un trade sta nel blocco della sua candela di
    ingresso; un blocco senza trade non ha R medio positivo."""
    totale = sum(t.r for t in ris.trade)
    blocchi = []
    for a, b in BLOCCHI:
        da = -math.inf if a == "inizio" else _ms(a)
        a_ = _ms(b) + 24 * 3600 * 1000
        rr = [t.r for t in ris.trade if da <= t.ts_ingresso < a_]
        blocchi.append({"da": a, "a": b, "trade": len(rr), "r_medio": (sum(rr) / len(rr)) if rr else None,
                        "somma_r": sum(rr), "quota": (sum(rr) / totale) if totale > 0 else None})
    positivi = sum(1 for x in blocchi if x["r_medio"] is not None and x["r_medio"] > 0)
    massimo = max((x["quota"] for x in blocchi if x["quota"] is not None), default=None)
    supera = positivi >= 3 and totale > 0 and massimo is not None and massimo <= 0.5
    return {"blocchi": blocchi, "positivi": positivi, "quota_massima": massimo, "supera": supera}


def senza_i_migliori(ris: Risultato, quota: float = 0.05) -> Dict[str, object]:
    """Verifica 4: si tolgono i trade migliori, il 5% del totale. SCELTA: il numero si
    arrotonda per eccesso (150 trade -> 8)."""
    r = sorted((t.r for t in ris.trade), reverse=True)
    k = int(math.ceil(quota * len(r)))
    resto = r[k:]
    media = sum(resto) / len(resto) if resto else 0.0
    return {"tolti": k, "r_medio": media, "supera": bool(resto) and media > 0}


def _arrotonda(valore: float, passo: float) -> float:
    return round(round(valore / passo) * passo, 10)


def mosse_robustezza(variante: dict) -> List[Tuple[str, dict]]:
    """Verifica 1: ogni parametro numerico spostato del 20% in meno e in piu', uno alla
    volta. Arrotondamenti della Fase 4: interi per periodi e numero di candele; 0,1 per
    multipli di ATR e di R; per le soglie di RSI e stocastico si sposta del 20% la
    distanza da 50; per il funding si arrotonda a 0,005%.

    SCELTE: contano anche i parametri fissi del catalogo usati dalla variante (per esempio
    l'ATR 14 dello stop o i periodi del MACD); i multipli di Bollinger e le soglie di
    volume si arrotondano a 0,1; le soglie di ADX e dell'ATR percentile all'intero; la
    percentuale dello stop S3 allo 0,1%. Una mossa che dopo l'arrotondamento lascia il
    valore com'era non si prova; una che rende la variante impossibile (per esempio le
    due medie di E1 uguali) si riporta e non si prova."""
    v = normalizza(variante, solo_catalogo=False)
    mosse: List[Tuple[str, dict]] = []

    def prova(sezione: str, indice: Optional[int], chiave: str, sotto: Optional[int], tipo: str):
        base = v[sezione] if indice is None else v[sezione][indice]
        valore = base[chiave] if sotto is None else base[chiave][sotto]
        for segno, nome in ((-1, "-20%"), (1, "+20%")):
            if tipo == "periodo":
                nuovo = max(1, int(round(valore * (1 + 0.2 * segno))))
            elif tipo == "multiplo":
                nuovo = _arrotonda(valore * (1 + 0.2 * segno), 0.1)
            elif tipo == "da_50":
                nuovo = _arrotonda(50 + (valore - 50) * (1 + 0.2 * segno), 0.1)
            elif tipo == "funding":
                nuovo = _arrotonda(valore * (1 + 0.2 * segno), 0.00005)
            elif tipo == "intero":
                nuovo = int(round(valore * (1 + 0.2 * segno)))
            elif tipo == "percento":
                nuovo = _arrotonda(valore * (1 + 0.2 * segno), 0.001)
            else:
                raise ValueError(tipo)
            if abs(nuovo - valore) < 1e-12:
                continue
            w = normalizza(v, solo_catalogo=False)
            el = w[sezione] if indice is None else w[sezione][indice]
            if sotto is None:
                el[chiave] = nuovo
            else:
                lista = list(el[chiave])
                lista[sotto] = nuovo
                el[chiave] = lista
            etichetta = f"{sezione}{'' if indice is None else f'[{indice}]'}.{chiave}{'' if sotto is None else f'[{sotto}]'} {nome} ({valore} -> {nuovo})"
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
        if cod == "E6":
            prova(sezione, None, "soglie", 0, "da_50")
            prova(sezione, None, "soglie", 1, "da_50")
        if cod == "E8":
            prova(sezione, None, "soglie", 0, "da_50")
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
    return mosse


def timeframe_adiacenti(timeframe: str, variante: dict) -> List[str]:
    """Verifica 2: il timeframe precedente e il successivo dell'elenco; quello piu' lungo
    non si prova se un elemento della variante e' ammesso solo fino a 1h."""
    i = TIMEFRAME.index(timeframe)
    out = []
    if i > 0:
        out.append(TIMEFRAME[i - 1])
    if i < len(TIMEFRAME) - 1:
        succ = TIMEFRAME[i + 1]
        v = normalizza(variante, solo_catalogo=False)
        usati = {v["ingresso"]["codice"], v["stop"]["codice"]} | {u["codice"] for u in v["uscite"]}
        for el in (v["filtro"], v["conferma"]):
            if el:
                usati.add(el["codice"])
        if not (usati & SOLO_FINO_A_1H and succ not in TIMEFRAME_FINO_A_1H):
            out.append(succ)
    return out


def fase4(variante: dict, serie: Serie, inizio: int, fine: int,
          serie_di: Callable[[str], Tuple[Serie, int, int]], regole: Regole = Regole(),
          base: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    """Le undici verifiche della Fase 4 su un candidato (periodo di costruzione).

    ``serie_di(timeframe)`` restituisce la serie di un altro timeframe con gli indici del
    periodo (per la verifica 2). ``base`` e' l'esito della Fase 2, se gia' calcolato.
    """
    v = normalizza(variante)
    if base is None:
        base = fase2(variante, serie, inizio, fine, regole)
    ris0: Risultato = base["risultato"]
    c0: Compilata = base["compilata"]
    r0 = base["metriche"]["r_medio"]
    out: Dict[str, object] = {}

    # 1. robustezza dei parametri
    prove = []
    for etichetta, w in mosse_robustezza(v):
        try:
            cw = compila(w, serie, solo_catalogo=False)
        except VarianteNonValida as e:
            prove.append({"mossa": etichetta, "non_provata": str(e)})
            continue
        m = metriche(esegui(cw, regole, COSTI_NORMALI, inizio, fine), serie)
        prove.append({"mossa": etichetta, "trade": m["trade"], "r_medio": m["r_medio"]})
    provate = [p for p in prove if "r_medio" in p]
    out["1_robustezza"] = {"prove": prove, "supera": bool(provate) and all(p["r_medio"] > 0 for p in provate)}

    # 2. timeframe adiacenti
    prove = []
    for tf in timeframe_adiacenti(v["timeframe"], v):
        s2, a2, b2 = serie_di(tf)
        fattore = TIMEFRAME_MS[v["timeframe"]] / TIMEFRAME_MS[tf]
        try:
            w = sposta_periodi(v, fattore)
            w["timeframe"] = tf
            cw = compila(w, s2, solo_catalogo=False)
        except VarianteNonValida as e:
            prove.append({"timeframe": tf, "non_provata": str(e)})
            continue
        m = metriche(esegui(cw, regole, COSTI_NORMALI, a2, b2), s2)
        prove.append({"timeframe": tf, "trade": m["trade"], "r_medio": m["r_medio"]})
    provate = [p for p in prove if "r_medio" in p]
    out["2_timeframe_adiacenti"] = {"prove": prove,
                                    "supera": bool(provate) and all(p["r_medio"] > 0 for p in provate)}

    # 3. stabilita' nel tempo
    out["3_blocchi"] = stabilita_blocchi(ris0)
    # 4. pochi trade estremi
    out["4_senza_i_migliori"] = senza_i_migliori(ris0)
    # 5. costi doppi
    md = metriche(esegui(c0, regole, COSTI_DOPPI, inizio, fine), serie)
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
        ms = metriche(esegui(c0, replace(regole, scarto_riempimento=0.0005), COSTI_NORMALI, inizio, fine), serie)
        out["8_riempimento_severo"] = {"trade": ms["trade"], "r_medio": ms["r_medio"], "supera": ms["r_medio"] > 0}
    # 9. regola intra-barra opposta (informativa)
    mi = metriche(esegui(c0, replace(regole, intrabarra="target_prima"), COSTI_NORMALI, inizio, fine), serie)
    out["9_intrabarra_opposta"] = {"r_medio": mi["r_medio"], "differenza": mi["r_medio"] - r0}
    # 10. ritardo di una candela (informativa)
    mr = metriche(esegui(c0, replace(regole, ritardo=1), COSTI_NORMALI, inizio, fine), serie)
    out["10_ritardo"] = {"trade": mr["trade"], "r_medio": mr["r_medio"], "differenza": mr["r_medio"] - r0}
    # 11. versione a mercato (solo limit, informativa)
    if limit:
        w = normalizza(v)
        w["tipo_ingresso"] = {"codice": "M"}
        cm = compila(w, serie)
        mm = metriche(esegui(cm, regole, COSTI_NORMALI, inizio, fine), serie)
        out["11_versione_a_mercato"] = {"trade": mm["trade"], "r_medio": mm["r_medio"], "differenza": r0 - mm["r_medio"]}
    decisive = ["1_robustezza", "2_timeframe_adiacenti", "3_blocchi", "4_senza_i_migliori", "5_costi_doppi",
                "6_troncamento", "7_liquidazione"] + (["8_riempimento_severo"] if limit else [])
    out["candidato"] = all(out[k]["supera"] for k in decisive)
    return out
