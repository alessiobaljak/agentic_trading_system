"""Revisione avversaria n. 5 del motore (research/src/motore.py): CASI LIMITE.

Lente: serie vuote o con una barra, stop uguale all'entrata, gap oltre stop e
liquidazione, serie stop/mark disallineate o con duplicati, segnale sull'ultima
barra, ritardo oltre la fine, funding fuori dai dati o dentro un buco di dati,
ricucitura con buco o sovrapposizione.

I test che FALLISCONO smascherano un difetto e vanno lasciati cosi' finche' il
motore non viene corretto: ognuno spiega nel commento il conto fatto a mano e
che cosa ci si aspetta. Quelli che passano documentano un caso limite gestito
bene, cosi' chi corregge non lo rompe.

Candele da 1 ora: ts = i * ORA, close_ts = ts + ORA - 1 (chiusura inclusa).
"""

import pytest

from research.src import motore
from research.src.motore import Candela, Parametri, Segnale

ORA = 3_600_000


def candela(i: int, o: float, h: float, l: float, c: float) -> Candela:
    return Candela(ts=i * ORA, open=o, high=h, low=l, close=c, volume=1.0, close_ts=i * ORA + ORA - 1)


def senza_costi(**kw) -> Parametri:
    base = dict(commissione_per_lato=0.0, slippage_per_lato=0.0)
    base.update(kw)
    return Parametri(**base)


def segnale_alla_barra(k: int, segnale: Segnale):
    def strategia(storia, posizione):
        if posizione is None and len(storia) - 1 == k:
            return segnale
        return None

    return strategia


# ---------------------------------------------------------------------------
# DIFETTO 1 (media): un gap oltre la liquidazione fa perdere piu' del margine
# isolato e manda il capitale sotto zero.
# ---------------------------------------------------------------------------


def test_gap_oltre_la_liquidazione_long_isolated_non_perde_piu_del_margine():
    # Capitale 1000, rischio 1%, leva_max 2, isolated, mmr 0.01.
    # Segnale long alla barra 0 con stop 99.9; ingresso all'open della barra 1 = 100.
    # quantita' teorica = 1000 * 0.01 / 0.1 = 100 -> notional 10000 > tetto 2000:
    # RIDOTTA a 20, notional 2000, leva effettiva 2, margine isolato = 2000 / 2 = 1000.
    # Prezzo di liquidazione = 100 * (1 - 1/2 + 0.01) = 51.
    # La barra 2 APRE a 30: sotto lo stop E sotto la liquidazione. Il motore applica
    # "stop al gap, all'open" perche' lo stop e' piu' vicino della liquidazione, e
    # perde 20 * (100 - 30) = 1400 > margine 1000: capitale finale -400.
    # In isolated la perdita non puo' superare il margine (la posizione viene
    # liquidata al prezzo di liquidazione, perdita 20 * 49 = 980): il capitale non
    # puo' andare sotto zero.
    candele = [
        candela(0, 100, 101, 99.95, 100),
        candela(1, 100, 100.5, 99.95, 100),
        candela(2, 30, 35, 25, 30),
        candela(3, 30, 31, 29, 30),
    ]
    ris = motore.esegui(candele, None, None, [], segnale_alla_barra(0, Segnale("long", stop=99.9)), senza_costi())
    t = ris.trades[0]
    assert t.ridotto and t.leva_effettiva == 2.0 and t.prezzo_liquidazione == pytest.approx(51.0)
    margine = t.quantita * t.entrata / t.leva_effettiva  # 1000
    assert -t.pnl <= margine + 1e-9, f"perdita {-t.pnl} oltre il margine isolato {margine}"
    assert ris.capitale_finale >= 0.0, f"capitale sotto zero: {ris.capitale_finale}"
    assert ris.metriche()["drawdown_max"] <= 1.0


def test_gap_oltre_la_liquidazione_short_isolated_non_perde_piu_del_margine():
    # Short alla barra 0 con stop 100.1, ingresso all'open della barra 1 = 100.
    # quantita' = 10 / 0.1 = 100 -> ridotta a 20 (tetto 2000); leva 2; margine 1000.
    # Liquidazione short = 100 * (1 + 1/2 - 0.01) = 149. La barra 2 apre a 200:
    # il motore chiude allo stop a 200 e perde 20 * 100 = 2000 -> capitale -1000.
    candele = [
        candela(0, 100, 100.05, 99, 100),
        candela(1, 100, 100.05, 99, 100),
        candela(2, 200, 210, 190, 200),
        candela(3, 200, 210, 190, 200),
    ]
    ris = motore.esegui(candele, None, None, [], segnale_alla_barra(0, Segnale("short", stop=100.1)), senza_costi())
    t = ris.trades[0]
    assert t.prezzo_liquidazione == pytest.approx(149.0)
    margine = t.quantita * t.entrata / t.leva_effettiva
    assert -t.pnl <= margine + 1e-9, f"perdita {-t.pnl} oltre il margine isolato {margine}"
    assert ris.capitale_finale >= 0.0


# ---------------------------------------------------------------------------
# DIFETTO 2 (bassa): a capitale esaurito i segnali si contano come "non validi",
# lo stesso contatore dello stop dalla parte sbagliata.
# ---------------------------------------------------------------------------


def test_capitale_esaurito_non_si_confonde_con_segnale_non_valido():
    # Stessa serie del difetto 1 (capitale -400 dopo il primo trade). Alla barra 4
    # arriva un segnale long con stop 29 < open 30 della barra 5: e' un segnale
    # VALIDO, ma il capitale e' esaurito. Il motore lo conta in n_segnali_non_validi:
    # chi legge il report crede che la strategia abbia emesso uno stop sbagliato.
    candele = [
        candela(0, 100, 101, 99.95, 100),
        candela(1, 100, 100.5, 99.95, 100),
        candela(2, 30, 35, 25, 30),
        candela(3, 30, 31, 29, 30),
        candela(4, 30, 31, 29, 30),
        candela(5, 30, 31, 29, 30),
        candela(6, 30, 31, 29, 30),
    ]

    def strategia(storia, posizione):
        k = len(storia) - 1
        if posizione is None and k == 0:
            return Segnale("long", stop=99.9)
        if posizione is None and k == 4:
            return Segnale("long", stop=29.0)
        return None

    ris = motore.esegui(candele, None, None, [], strategia, senza_costi())
    assert ris.n_segnali_non_validi == 0, "un segnale con stop dalla parte giusta non e' 'non valido'"


# ---------------------------------------------------------------------------
# DIFETTO 3 (media): un settlement che cade in un buco della serie (barra
# mancante) viene perso in silenzio, anche con la posizione aperta.
# ---------------------------------------------------------------------------


def test_funding_in_un_buco_di_dati_non_viene_perso_in_silenzio():
    # carica_candele (research/src/dati.py) dichiara che "un mese senza file e'
    # saltato": le serie possono avere buchi. Qui manca la barra 3 (ts = 3*ORA).
    # Long aperto alla barra 1 (open 100, stop 90: quantita' = 1000 * 0.01 / 10 = 1)
    # e tenuto fino a fine dati. Settlement a 3*ORA con tasso +0.001: costo atteso
    # 1 * 100 * 0.001 = 0.1. Il motore (prima della correzione) cercava la barra
    # che contiene il settlement, non la trovava e non addebitava nulla: 0.
    # Accettabile: contarlo (sull'ultimo mark disponibile) oppure rifiutare la
    # serie con un buco (ValueError). Non accettabile: perderlo senza dirlo.
    # NOTA del correttore: il conto originale del revisore diceva "quantita' 10"
    # e costo 1.0, ma con stop a 10 dall'apertura la quantita' e' 1: atteso 0.1.
    # Il motore ora lo addebita sull'ultimo mark disponibile (close della barra 2
    # = 100) e lo dichiara nei contatori n_buchi_dati e n_funding_in_buco.
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100, 101, 99, 100), candela(2, 100, 101, 99, 100)]
    candele += [candela(4, 100, 101, 99, 100), candela(5, 100, 101, 99, 100)]
    try:
        ris = motore.esegui(candele, None, None, [(3 * ORA, 0.001)], segnale_alla_barra(0, Segnale("long", stop=90.0)), senza_costi())
    except ValueError:
        return  # la serie con un buco viene rifiutata: va bene
    assert ris.trades[0].quantita == pytest.approx(1.0)
    assert ris.trades[0].funding_pagato == pytest.approx(0.1)
    assert ris.n_buchi_dati == 1 and ris.n_funding_in_buco == 1
    assert ris.metriche()["n_funding_in_buco"] == 1


# ---------------------------------------------------------------------------
# DIFETTO 4 (bassa): lo stop si riempie al prezzo della serie stop (mark), su cui
# nessuno scambia, invece che sul last price.
# ---------------------------------------------------------------------------


def test_stop_scattato_sulla_serie_stop_si_riempie_sul_last_price():
    # Serie dei segnali (last): barra 1 open 100, low 99.5. Serie stop (mark): barra 1
    # apre a 90 (gap sul mark, non sul last). Long con stop 95 entra a 100 all'open
    # della barra 1. Lo stop SCATTA sul mark (90 <= 95), giusto; ma il riempimento
    # avviene a 90 = open della serie stop, un prezzo a cui il last non e' mai
    # arrivato (minimo 99.5). Un ordine stop scatta sul mark e si riempie a mercato
    # sul last: l'uscita non puo' essere sotto il minimo del last della barra.
    # Perdita del motore: 10 * (100 - 90) = 100; perdita massima possibile sul
    # last: 10 * (100 - 99.5) = 5.
    segnali = [candela(0, 100, 101, 99, 100), candela(1, 100, 101, 99.5, 100), candela(2, 100, 101, 99, 100)]
    stop = [candela(0, 100, 101, 99, 100), candela(1, 90, 101, 89, 100), candela(2, 100, 101, 99, 100)]
    ris = motore.esegui(segnali, stop, None, [], segnale_alla_barra(0, Segnale("long", stop=95.0)), senza_costi())
    t = ris.trades[0]
    assert t.esito == "stop"
    assert t.uscita >= segnali[1].low, f"uscita {t.uscita} sotto il minimo del last price {segnali[1].low}"


# ---------------------------------------------------------------------------
# DIFETTO 5 (bassa): serie stop con ts duplicati accettata in silenzio (vince
# l'ultima barra letta).
# ---------------------------------------------------------------------------


def test_serie_stop_con_ts_duplicati_viene_rifiutata():
    # Due barre con ts = 1*ORA nella serie stop: la prima innocua (low 99), la seconda
    # con low 80 che tocca lo stop a 90. allinea_serie costruisce un dict per ts e
    # tiene l'ULTIMA: il trade chiude per stop senza che nessuno se ne accorga.
    # Una serie con duplicati e' un errore nei dati e va dichiarato (ValueError).
    segnali = [candela(0, 100, 101, 99, 100), candela(1, 100, 101, 99, 100), candela(2, 100, 101, 99, 100)]
    stop = [candela(0, 100, 101, 99, 100), candela(1, 100, 101, 99, 100), candela(1, 100, 101, 80, 100), candela(2, 100, 101, 99, 100)]
    with pytest.raises(ValueError):
        motore.esegui(segnali, stop, None, [], segnale_alla_barra(0, Segnale("long", stop=90.0)), senza_costi())


# ---------------------------------------------------------------------------
# DIFETTO 6 (bassa): ricuci_serie con la seconda serie che inizia PRIMA della
# prima scarta tutta la prima serie senza dirlo.
# ---------------------------------------------------------------------------


def test_ricuci_serie_rifiuta_una_seconda_serie_che_precede_la_prima():
    # serie_prima: barre 3 e 4; serie_dopo: barre 0 e 1. La cucitura e' a 0 e TUTTE
    # le barre della prima (ts >= 0) vengono scartate: il risultato ha 2 barre e
    # nessun avviso. E' un errore di chi chiama (serie invertite) e va sollevato.
    prima = [candela(3, 1000, 1100, 900, 1000), candela(4, 1000, 1100, 900, 1000)]
    dopo = [candela(0, 1.0, 1.1, 0.9, 1.0), candela(1, 1.0, 1.1, 0.9, 1.0)]
    with pytest.raises(ValueError):
        motore.ricuci_serie(prima, dopo, 1 / 1000, 1000)


def test_ricuci_serie_con_buco_lo_conserva_senza_riempirlo():
    # Caso documentato (passa): prima = barre 0,1; dopo = barre 5,6. La cucitura e'
    # alla barra 5 e il buco (2,3,4) resta un buco: il motore non inventa barre.
    prima = [candela(0, 1000, 1100, 900, 1000), candela(1, 1000, 1100, 900, 1000)]
    dopo = [candela(5, 1.0, 1.1, 0.9, 1.0), candela(6, 1.0, 1.1, 0.9, 1.0)]
    cucita, ts = motore.ricuci_serie(prima, dopo, 1 / 1000, 1000)
    assert ts == 5 * ORA
    assert [c.ts // ORA for c in cucita] == [0, 1, 5, 6]
    assert cucita[0].open == pytest.approx(1.0) and cucita[0].volume == pytest.approx(1000.0)


# ---------------------------------------------------------------------------
# DIFETTO 7 (bassa): calcola_quantita, funzione pura esposta, esplode con
# ZeroDivisionError se stop == prezzo di riferimento.
# ---------------------------------------------------------------------------


def test_calcola_quantita_con_stop_uguale_al_prezzo_dichiara_l_errore():
    # Nel motore il caso e' filtrato prima (segnale non valido), ma la funzione e'
    # pubblica e documentata come pura: chi la usa da sola (es. per stimare i trade,
    # sezione 8) riceve una divisione per zero invece di un errore parlante.
    with pytest.raises(ValueError):
        motore.calcola_quantita(1000.0, 100.0, 100.0, 100.0, senza_costi())


# ---------------------------------------------------------------------------
# Casi limite gestiti bene (passano): li fissiamo perche' chi corregge non li rompa.
# ---------------------------------------------------------------------------


def test_stop_uguale_all_entrata_nel_motore_e_segnale_non_valido():
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100, 101, 99, 100), candela(2, 100, 101, 99, 100)]
    ris = motore.esegui(candele, None, None, [], segnale_alla_barra(0, Segnale("long", stop=100.0)), senza_costi())
    assert ris.trades == [] and ris.n_segnali_non_validi == 1


def test_serie_vuota_e_serie_con_una_barra():
    vuoto = motore.esegui([], None, None, [], segnale_alla_barra(0, Segnale("long", stop=90.0)), senza_costi())
    assert vuoto.trades == [] and vuoto.curva_capitale == [] and vuoto.metriche()["drawdown_max"] == 0.0
    # Una barra sola: il segnale alla barra 0 non ha una barra dopo in cui entrare.
    uno = motore.esegui([candela(0, 100, 101, 99, 100)], None, None, [], segnale_alla_barra(0, Segnale("long", stop=90.0)), senza_costi())
    assert uno.trades == [] and uno.n_segnali_senza_barra == 1
    assert uno.curva_capitale == [(0, 1000.0), (ORA - 1, 1000.0)]


def test_segnale_sull_ultima_barra_e_ritardo_oltre_la_fine_si_contano():
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100, 101, 99, 100)]
    ultima = motore.esegui(candele, None, None, [], segnale_alla_barra(1, Segnale("long", stop=90.0)), senza_costi())
    assert ultima.trades == [] and ultima.n_segnali_senza_barra == 1
    # Segnale alla barra 0 con ritardo 1: ingresso alla barra 2, che non esiste.
    ritardo = motore.esegui(candele, None, None, [], segnale_alla_barra(0, Segnale("long", stop=90.0)), senza_costi(ritardo_barre=1))
    assert ritardo.trades == [] and ritardo.n_segnali_senza_barra == 1


def test_funding_fuori_dall_intervallo_dei_dati_non_si_applica():
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100, 101, 99, 100), candela(2, 100, 101, 99, 100)]
    ris = motore.esegui(candele, None, None, [(-ORA, 0.01), (10 * ORA, 0.01)], segnale_alla_barra(0, Segnale("long", stop=90.0)), senza_costi())
    assert ris.trades[0].funding_pagato == 0.0


def test_serie_mark_con_ts_diverso_solleva_errore():
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100, 101, 99, 100)]
    mark = [candela(0, 100, 101, 99, 100), Candela(ts=ORA + 1, open=100, high=101, low=99, close=100, volume=1, close_ts=2 * ORA)]
    with pytest.raises(ValueError):
        motore.esegui(candele, None, mark, [], segnale_alla_barra(0, Segnale("long", stop=90.0)), senza_costi())
