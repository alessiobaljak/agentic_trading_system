"""Revisione avversaria del motore (research/src/motore.py), lente: sguardo avanti e tempi.

Ogni test qui descrive un modo in cui il motore usa informazione che nel momento
della decisione non poteva avere, oppure etichetta i tempi in modo scorretto.
I test che FALLISCONO sono quelli che smascherano un difetto: si lasciano
cosi' come sono, perche' servono a chi corregge. I conti sono fatti a mano nei
commenti. Candele da 1 ora: ts = i * ORA, close_ts = ts + ORA - 1.
"""

from research.src import motore
from research.src.motore import Candela, Parametri, Posizione, Segnale

ORA = 3_600_000


def candela(i: int, o: float, h: float, l: float, c: float) -> Candela:
    return Candela(ts=i * ORA, open=o, high=h, low=l, close=c, volume=1.0, close_ts=i * ORA + ORA - 1)


def senza_costi(**kw) -> Parametri:
    base = dict(commissione_per_lato=0.0, slippage_per_lato=0.0)
    base.update(kw)
    return Parametri(**base)


def strategia_segnale_alla_barra(k: int, segnale: Segnale):
    def strategia(storia, posizione):
        if posizione is None and len(storia) - 1 == k:
            return segnale
        return None

    return strategia


def posizione_long(entrata: float, stop: float, target: float, quantita: float = 1.0) -> Posizione:
    return Posizione(
        direzione="long",
        entrata=entrata,
        stop=stop,
        target=target,
        quantita=quantita,
        ts_entrata=0,
        entrata_riferimento=entrata,
        rischio_iniziale=quantita * abs(entrata - stop),
        leva_effettiva=1.0,
        prezzo_liquidazione=0.0,
        ridotto=False,
        violazione_liquidazione=False,
    )


# ---------------------------------------------------------------------------
# DIFETTO 1 (sguardo avanti): l'apertura e' il PRIMO prezzo della barra, ma quando
# stop e target sono entrambi toccati il motore decide col solo parametro
# riempimento_intrabarra e ignora il gap in apertura.
#
# Caso A, "target_prima": long entrato a 100, stop 95, target 110. La barra apre
# a 90 (gia' sotto lo stop) e poi sale fino a 112. Lo stop si riempie all'apertura
# a 90, PRIMA che il prezzo possa toccare 110: la posizione non esiste piu'
# quando arriva il target. Il motore invece restituisce "target" a 110: usa
# l'informazione che la barra salira', e trasforma una perdita di 10 in un
# guadagno di 10 (differenza 20 per unita').
# ---------------------------------------------------------------------------


def test_gap_oltre_lo_stop_in_apertura_vince_anche_con_target_prima():
    pos = posizione_long(entrata=100.0, stop=95.0, target=110.0)
    barra = candela(1, 90, 112, 89, 111)
    esito = motore.valuta_uscita_in_barra(pos, barra, barra, barra, senza_costi(riempimento_intrabarra="target_prima"))
    assert esito == ("stop", 90.0), f"atteso stop all'open 90 (il gap viene prima di tutto), ottenuto {esito}"


def test_gap_oltre_lo_stop_in_apertura_vince_anche_con_target_prima_nel_motore():
    candele = [
        candela(0, 100, 101, 99, 100),
        candela(1, 100, 101, 99, 100),  # ingresso long a 100 all'apertura
        candela(2, 90, 112, 89, 111),  # apre a 90 (sotto lo stop 95), poi sale a 112
        candela(3, 111, 112, 110, 111),
    ]
    strategia = strategia_segnale_alla_barra(0, Segnale("long", stop=95.0, target=110.0))
    ris = motore.esegui(candele, None, None, [], strategia, senza_costi(riempimento_intrabarra="target_prima"))
    assert len(ris.trades) == 1
    t = ris.trades[0]
    # quantita' = 1000 * 0.01 / |100 - 95| = 2; stop all'open 90: pnl = 2 * (90 - 100) = -20
    assert t.esito == "stop", f"atteso stop (gap all'apertura), ottenuto {t.esito} con pnl {t.pnl}"
    assert t.uscita == 90.0
    assert t.pnl == -20.0


# Caso B, "stop_prima" (il default del protocollo): long entrato a 100, stop 95,
# target 110. La barra apre a 115 (gia' oltre il target) e poi crolla a 94. Il
# take-profit limit a 110 si riempie all'apertura a 115, prima che il prezzo possa
# scendere a 95. Il motore invece restituisce "stop": sa che la barra scendera'
# e lo usa contro il trade. E' il verso prudente, ma e' comunque un prezzo che
# non poteva essere eseguito: la posizione era gia' chiusa a 115.


def test_gap_oltre_il_target_in_apertura_vince_anche_con_stop_prima():
    pos = posizione_long(entrata=100.0, stop=95.0, target=110.0)
    barra = candela(1, 115, 116, 94, 95)
    esito = motore.valuta_uscita_in_barra(pos, barra, barra, barra, senza_costi(riempimento_intrabarra="stop_prima"))
    assert esito == ("target", 115.0), f"atteso target all'open 115 (il gap viene prima di tutto), ottenuto {esito}"


# ---------------------------------------------------------------------------
# DIFETTO 2 (tempi ambigui risolti a favore del trade): settlement esattamente
# all'apertura della barra di INGRESSO.
#
# Il modulo dichiara: "funding ambiguo contato solo se costo" e lo applica
# all'uscita per segnale (settlement esattamente all'open: si conta solo se
# costo). All'ingresso, pero', un settlement allo stesso istante dell'apertura
# viene contato anche quando e' un INCASSO: il trade riceve un funding per un
# istante in cui non si sa se la posizione era gia' aperta.
#
# Conto: long, quantita' 1000*0.01/|100-90| = 1; settlement a ts della barra 1
# (= istante dell'ingresso) con tasso -0.001; notional = 1 * 100 = 100;
# funding = +1 * (-0.001) * 100 = -0.1 (incasso). Atteso per coerenza con la
# regola del modulo: 0.0 (ambiguo e non e' un costo). Il motore da' -0.1.
# ---------------------------------------------------------------------------


def test_funding_all_istante_dell_ingresso_non_si_incassa():
    candele = [
        candela(0, 100, 101, 99, 100),
        candela(1, 100, 101, 99, 100),  # ingresso all'apertura, settlement nello stesso istante
        candela(2, 100, 101, 99, 100),
        candela(3, 100, 101, 99, 100),
    ]
    funding = [(1 * ORA, -0.001)]
    strategia = strategia_segnale_alla_barra(0, Segnale("long", stop=90.0, target=None))
    ris = motore.esegui(candele, None, None, funding, strategia, senza_costi())
    assert len(ris.trades) == 1
    t = ris.trades[0]
    assert t.funding_pagato == 0.0, f"funding ambiguo a favore del trade contato: {t.funding_pagato}"


# ---------------------------------------------------------------------------
# DIFETTO 3 (tempi): un'uscita per stop/target/liquidazione avvenuta DENTRO la
# barra i riceve ts_uscita = ts di apertura della barra, cioe' un istante in cui
# l'uscita non poteva ancora essere avvenuta (lo stop e' sotto l'open). Nella
# barra di ingresso il trade risulta aperto e chiuso nello stesso istante
# (ts_uscita == ts_entrata), e la curva del capitale mette la perdita all'open.
# L'etichetta onesta e' il close_ts della barra (si sa solo che e' successo
# dentro la barra, e la barra e' chiusa quando lo si registra), come fa gia'
# l'esito "fine_dati".
# ---------------------------------------------------------------------------


def test_ts_uscita_di_uno_stop_dentro_la_barra_non_e_l_apertura():
    candele = [
        candela(0, 100, 101, 99, 100),
        candela(1, 100, 101, 89, 90),  # ingresso a 100 all'open, stop 95 toccato DOPO l'open
        candela(2, 90, 91, 89, 90),
    ]
    strategia = strategia_segnale_alla_barra(0, Segnale("long", stop=95.0, target=None))
    ris = motore.esegui(candele, None, None, [], strategia, senza_costi())
    t = ris.trades[0]
    assert t.esito == "stop"
    assert t.ts_uscita > t.ts_entrata, f"trade aperto e chiuso nello stesso istante: {t.ts_entrata} == {t.ts_uscita}"
    assert t.ts_uscita == candele[1].close_ts


# ---------------------------------------------------------------------------
# Controlli che il motore SUPERA (li lascio come guardia contro regressioni di
# chi corregge i difetti sopra): storia senza barre future, ingresso all'open
# della barra dopo anche col ritardo, "chiudi" eseguito all'open successiva.
# ---------------------------------------------------------------------------


def test_storia_mai_oltre_la_barra_corrente_anche_con_ritardo():
    candele = [candela(i, 100 + i, 101 + i, 99 + i, 100 + i) for i in range(6)]
    massimo_ts_visto = []

    def strategia(storia, posizione):
        massimo_ts_visto.append(max(c.ts for c in storia))
        if posizione is None and len(storia) == 2:
            return Segnale("long", stop=50.0, target=None)
        return None

    ris = motore.esegui(candele, None, None, [], strategia, senza_costi(ritardo_barre=1))
    # alla chiamata k (barra k) il ts massimo visto e' k * ORA
    assert massimo_ts_visto == [k * ORA for k in range(len(massimo_ts_visto))]
    # segnale alla barra 1, ritardo 1 -> ingresso all'open della barra 3 = 103
    assert ris.trades[0].ts_entrata == 3 * ORA
    assert ris.trades[0].entrata == 103.0


def test_chiudi_non_usa_il_close_della_barra_del_segnale():
    candele = [
        candela(0, 100, 101, 99, 100),
        candela(1, 100, 101, 99, 100),
        candela(2, 100, 120, 99, 120),  # qui la strategia dice "chiudi": il close 120 NON e' il prezzo di uscita
        candela(3, 105, 106, 104, 105),  # uscita all'open 105
    ]

    def strategia(storia, posizione):
        if posizione is None and len(storia) == 1:
            return Segnale("long", stop=90.0, target=None)
        if posizione is not None and len(storia) == 3:
            return "chiudi"
        return None

    ris = motore.esegui(candele, None, None, [], strategia, senza_costi())
    t = ris.trades[0]
    assert t.esito == "segnale"
    assert t.uscita == 105.0
    assert t.ts_uscita == 3 * ORA
