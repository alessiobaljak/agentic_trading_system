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


#: solo per i test: se e' una funzione, riceve la lista [(candela della decisione, trade)] di ogni
#: simulazione TENUTA dalle entrate casuali, nell'ordine
_OSSERVATORE = None


class SimulazioneImpossibile(RuntimeError):
    """Le candele ammesse non bastano per mettere il numero di trade del candidato senza
    sovrapposizioni: STOP, la situazione non e' prevista dal protocollo."""


# ---------------------------------------------------------------------------
# 10.1 entrate casuali e 10.2 p-value
# ---------------------------------------------------------------------------


#: le fasce di larghezza dello stop della 10.1 (correzione 1 del collaudo, 17 ottobre 2026)
FASCE_LARGHEZZA = 5


def larghezza_stop(t) -> float:
    """La larghezza dello stop di un trade: distanza fra prezzo d'ingresso e stop ÷ prezzo d'ingresso,
    arrotondata a 12 decimali (con lo stop S3 tutte le larghezze sono la stessa percentuale, e senza
    arrotondamento le differenze dell'ultima cifra dividerebbero trade uguali in fasce diverse)."""
    return round(abs(t.prezzo_ingresso - t.stop_iniziale) / t.prezzo_ingresso, 12)


def entrate_casuali(c: Compilata, n_trade: int, inizio: int, fine: int, regole: Regole = Regole(),
                    costi: Costi = COSTI_NORMALI, n_simulazioni: int = N_SIMULAZIONI,
                    seme: int = SEME, cache: Optional[dict] = None, giri_taratura: int = 256,
                    passi_taratura: int = 24, giri_massimi: int = 4_000_000,
                    larghezze_candidato: Optional[Sequence[float]] = None,
                    fasce: int = FASCE_LARGHEZZA) -> Dict[str, object]:
    """Le entrate casuali della sezione 10.1: una strategia che entra a caso, con la stessa
    larghezza di stop del candidato.

    Ogni simulazione e' una strategia che, quando e' senza posizione e senza ordine in attesa,
    a ogni candela ammessa del periodo entra con probabilita' q x peso, indipendentemente dai
    prezzi futuri e da quando il candidato e' in posizione; poi il trade va come lo farebbe la
    variante con un segnale li' (stesso tipo di ingresso, stesso stop, stesse uscite, stessi
    costi) e la strategia torna libera alla sua uscita, come il candidato. Cosi' i trade non
    si sovrappongono e la scelta di un ingresso non dipende mai da come finira' il trade.

    Il peso (correzione 1 del collaudo, approvata il 17 ottobre 2026) fa si' che i trade della
    strategia abbiano la stessa distribuzione di larghezza dello stop (``larghezza_stop``) dei
    trade del candidato: le larghezze del candidato si dividono in ``fasce`` (5) ai loro quantili;
    il peso di una candela e' la quota del candidato nella fascia del trade che si aprirebbe li'
    diviso la quota di quella fascia fra i trade di tutte le candele ammesse, riportato a un
    massimo di 1; una candela in cui non si apre un trade (ordine non eseguito, stop troppo
    vicino) ha peso 1. Le larghezze del candidato, se non si passano, vengono dal candidato stesso
    (``esegui`` con le stesse regole e gli stessi costi sul periodo). Senza il peso un trade con lo
    stop largo, che paga meno costi e meno regole prudenti per ogni R, faceva sembrare migliore
    del caso un candidato che non prevede niente (collaudo del 16 ottobre).

    q si tara perche' la strategia faccia in media tanti trade quanti il candidato; si tengono
    solo le simulazioni che ne fanno esattamente tanti (10.1: «stesso numero di trade»), finche'
    sono 1.000. Un solo generatore, seme fisso 2026, per la taratura e le simulazioni, in fila.

    Correzione del 16 ottobre 2026, prima di qualunque prova del collaudo: la prima versione
    prendeva le candele in un ordine a caso e teneva un trade solo se ci stava fra quelli gia'
    presi; cosi' teneva piu' spesso i trade brevi (soprattutto stop) e faceva sembrare il caso
    peggiore di quanto e'. ``SimulazioneImpossibile`` vuol dire che nemmeno una strategia che
    entra appena e' libera arriva al numero di trade del candidato, oppure che in ``giri_massimi``
    giri nessuna simulazione ne ha fatti esattamente tanti.
    """
    import bisect

    if n_trade <= 0:
        raise ValueError("servono almeno un trade del candidato")
    if fasce < 1:
        raise ValueError("servono almeno una fascia")
    ammesse = [int(x) for x in np.flatnonzero(c.ammessa[inizio:fine + 1]) + inizio]
    if not ammesse:
        raise SimulazioneImpossibile("nessuna candela ammessa nel periodo")
    if cache is None:
        cache = {}
    n_amm = len(ammesse)
    # per ogni candela ammessa (posizione p): l'esito di un ingresso li', e la posizione della prima
    # candela ammessa alla cui chiusura la strategia e' di nuovo libera
    e_trade = np.zeros(n_amm, dtype=bool)
    e_r = np.zeros(n_amm)
    e_larg = np.zeros(n_amm)
    succ = np.zeros(n_amm, dtype=np.int64)
    esiti = []
    for p, j in enumerate(ammesse):
        e = cache.get(j)
        if e is None:
            e = simula_da(c, j, regole, costi, fine, forzato=True)
            cache[j] = e
        esiti.append(e)
        if e.tipo == "trade":
            e_trade[p] = True
            e_r[p] = e.trade.r
            e_larg[p] = larghezza_stop(e.trade)
        succ[p] = bisect.bisect_left(ammesse, max(e.libero_da, j + 1))

    # il peso di ogni candela: stessa distribuzione di larghezza dello stop del candidato
    if larghezze_candidato is None:
        larghezze_candidato = [larghezza_stop(t) for t in esegui(c, regole, costi, inizio, fine).trade]
    larg_c = np.asarray(larghezze_candidato, dtype=np.float64)
    peso = np.ones(n_amm)
    quote = None
    fascia_p = np.full(n_amm, -1, dtype=np.int64)  # la fascia del trade di ogni candela (-1: nessun trade)
    quota_c = w = None
    if len(larg_c) and fasce > 1 and e_trade.any():
        tagli = np.quantile(larg_c, np.arange(1, fasce) / fasce)
        fascia_c = np.searchsorted(tagli, larg_c, side="right")
        fascia_p[e_trade] = np.searchsorted(tagli, e_larg[e_trade], side="right")
        quota_c = np.bincount(fascia_c, minlength=fasce) / len(larg_c)
        quota_a = np.bincount(fascia_p[e_trade], minlength=fasce) / int(e_trade.sum())
        if np.any((quota_c > 0) & (quota_a == 0)):
            raise SimulazioneImpossibile("una fascia di larghezza dello stop del candidato non ha nessuna candela ammessa")
        w = np.where(quota_a > 0, quota_c / np.where(quota_a > 0, quota_a, 1.0), 0.0)
        w = w / w.max()
        peso[e_trade] = w[fascia_p[e_trade]]
        quote = {"candidato": quota_c.tolist(), "candele_ammesse": quota_a.tolist(), "tagli": tagli.tolist()}

    rng = np.random.default_rng(seme)
    registra = _OSSERVATORE is not None
    per_fascia = np.zeros(max(fasce, 1))

    def giri(q: float, quanti: int, con_peso: bool = True):
        """``quanti`` strategie che entrano a caso, fatte avanzare insieme (per diradamento: un salto
        geometrico con probabilita' q, poi l'ingresso con probabilita' ``peso``): trade e somma degli
        R di ognuna (e, solo per i test, le posizioni dei trade)."""
        pos = np.zeros(quanti, dtype=np.int64)
        conta = np.zeros(quanti, dtype=np.int64)
        somma = np.zeros(quanti)
        vive = np.arange(quanti)
        tracce = [[] for _ in range(quanti)] if registra else None
        while len(vive):
            if q < 1.0:
                pos[vive] += rng.geometric(q, size=len(vive)) - 1
            dentro = pos[vive] < n_amm
            vive = vive[dentro]
            if not len(vive):
                break
            pv = pos[vive]
            if con_peso:
                entra = rng.random(len(vive)) < peso[pv]
                fermi = vive[~entra]
                pos[fermi] += 1
                vive_e, pv = vive[entra], pv[entra]
            else:
                vive_e = vive
            t = e_trade[pv]
            conta[vive_e] += t
            somma[vive_e] += np.where(t, e_r[pv], 0.0)
            if w is not None:
                per_fascia[:] += np.bincount(fascia_p[pv[t]], minlength=fasce)
            if registra:
                for k, pp, tt in zip(vive_e.tolist(), pv.tolist(), t.tolist()):
                    if tt:
                        tracce[k].append(pp)
            pos[vive_e] = succ[pv]
        return conta, somma, tracce

    massimo = int(giri(1.0, 1, con_peso=False)[0][0])
    if massimo < n_trade:
        raise SimulazioneImpossibile(
            f"una strategia che entra appena e' libera fa {massimo} trade nel periodo, meno dei "
            f"{n_trade} del candidato")
    def tara_q() -> float:
        """Taratura di q: la media dei trade per giro deve essere n_trade (bisezione su log q)."""
        basso, alto = math.log(1e-7), 0.0
        for _ in range(passi_taratura):
            medio = 0.5 * (basso + alto)
            conta, _, _ = giri(math.exp(medio), giri_taratura)
            if conta.mean() < n_trade:
                basso = medio
            else:
                alto = medio
        return math.exp(0.5 * (basso + alto))

    q = tara_q()
    if w is not None:
        # i trade che stanno nel periodo senza sovrapporsi non sono un campione neutro delle candele (i
        # trade lunghi ci stanno meno spesso): tre giri di prova misurano le quote ottenute per fascia
        # e correggono i pesi, poi si ritara q
        for _ in range(3):
            per_fascia[:] = 0.0
            conta, _, _ = giri(q, 1024)
            ottenute = per_fascia / max(per_fascia.sum(), 1.0)
            correzione = np.where((ottenute > 0) & (quota_c > 0), quota_c / np.where(ottenute > 0, ottenute, 1.0), 1.0)
            w = w * correzione
            w = w / w.max()
            peso[e_trade] = w[fascia_p[e_trade]]
            q = tara_q()
        quote["pesi"] = w.tolist()
    medie: List[float] = []
    fatti = 0
    lotto = 4096
    while len(medie) < n_simulazioni:
        if fatti >= giri_massimi:
            raise SimulazioneImpossibile(
                f"dopo {fatti} giri solo {len(medie)} simulazioni con esattamente {n_trade} trade")
        conta, somma, tracce = giri(q, lotto)
        fatti += lotto
        for k in np.flatnonzero(conta == n_trade):
            if len(medie) == n_simulazioni:
                break
            medie.append(float(somma[k]) / n_trade)
            if registra:
                _OSSERVATORE([(ammesse[pp], esiti[pp].trade) for pp in tracce[k]])
    valori = np.asarray(medie)
    return {"valori": valori, "media": float(valori.mean()), "percentile_95": float(np.percentile(valori, 95)),
            "candele_ammesse": n_amm, "n_simulazioni": n_simulazioni, "seme": seme,
            "probabilita_ingresso": q, "giri": fatti, "trade_massimi": massimo, "fasce": fasce,
            "quote_larghezza": quote}


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
        casuali = entrate_casuali(c, m["trade"], inizio, fine, regole, COSTI_NORMALI, n_simulazioni, seme,
                                  larghezze_candidato=[larghezza_stop(t) for t in ris.trade])
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
    """Al multiplo di ``passo`` piu' vicino, con le meta' lontano da zero."""
    x = valore / passo
    n = math.floor(abs(x) + 0.5 + 1e-9) * (1 if x >= 0 else -1)
    return round(n * passo, 10)


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
                nuovo = max(1, int(math.floor(valore * (1 + 0.2 * segno) + 0.5)))
            elif tipo == "multiplo":
                nuovo = _arrotonda(valore * (1 + 0.2 * segno), 0.1)
            elif tipo == "da_50":
                nuovo = _arrotonda(50 + (valore - 50) * (1 + 0.2 * segno), 0.1)
            elif tipo == "funding":
                nuovo = _arrotonda(valore * (1 + 0.2 * segno), 0.00005)
            elif tipo == "intero":
                nuovo = int(math.floor(valore * (1 + 0.2 * segno) + 0.5))
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
        if cod in ("E6", "E8"):
            # la soglia della direzione della variante; l'altra solo se la usa l'uscita U4
            # (il segnale opposto e' l'ingresso nell'altra direzione)
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
