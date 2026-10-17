"""Test dell'ingresso (e dell'uscita «chiudi») con ORDINE LIMITE nel motore (research/src/motore.py).

Regole: ``research/esperimenti/ordini_limite/regole.md`` (sezioni 4, 4.6, 10); le
scelte dove le regole tacciono sono nella docstring del modulo ``motore``,
sezione «Ordini limite». Ogni test riporta nei commenti il conto fatto a mano.

Candele da 1 ora: ts = i * ORA, close_ts = ts + ORA - 1 (chiusura inclusa).

L'ultima parte e' la PARITA': con ``ingresso="mercato"`` (il predefinito) i trade
devono essere IDENTICI, bit per bit, a quelli del motore prima della modifica.
Si controlla in due modi: (1) le impronte SHA-256 di tutti i campi dei trade, della
curva e dei contatori di tre corse su uno scenario sintetico, calcolate con il
motore di prima (commit 39bb60b2, 13 ott 2026) e scritte qui; (2) se c'e' una
copia del motore di prima (variabile d'ambiente ``MOTORE_PRIMA`` o il percorso
dello scratchpad usato il 13 ott), il confronto campo per campo con quella copia.
"""

import hashlib
import importlib.util
import os
import random
import sys
from pathlib import Path

import pytest

from research.src import motore
from research.src.motore import Candela, Parametri, Segnale

ORA = 3_600_000


def candela(i: int, o: float, h: float, l: float, c: float) -> Candela:
    return Candela(ts=i * ORA, open=o, high=h, low=l, close=c, volume=1.0, close_ts=i * ORA + ORA - 1)


def senza_costi(**kw) -> Parametri:
    """Parametri a costi zero (anche maker): isolano la logica di prezzo dal conto dei costi."""
    base = dict(commissione_per_lato=0.0, slippage_per_lato=0.0, commissione_maker_per_lato=0.0)
    base.update(kw)
    return Parametri(**base)


def limite(**kw) -> Parametri:
    """Ingresso a limite, costi zero, validita' 1, «attraversato» (la regola della prova)."""
    base = dict(ingresso="limite")
    base.update(kw)
    return senza_costi(**base)


def segnale_alla_barra(k: int, segnale: Segnale, chiudi_dopo: int = None):
    """Strategia che emette ``segnale`` alla chiusura della barra k e, se chiesto, «chiudi» alla barra ``chiudi_dopo``."""

    def strategia(storia, posizione):
        i = len(storia) - 1
        if posizione is None and i == k:
            return segnale
        if posizione is not None and chiudi_dopo is not None and i == chiudi_dopo:
            return "chiudi"
        return None

    return strategia


LONG = Segnale("long", stop=98.0, target=None)  # con P = 100: quantita' = 1000 * 0.01 / 2 = 5


# ---------------------------------------------------------------------------
# La funzione pura del riempimento
# ---------------------------------------------------------------------------


def test_riempimento_limite_compra_e_vende():
    # Compra a 100: apertura sotto -> riempito all'apertura ma a 100 (correzione 1: l'ordine in attesa esegue al
    # suo prezzo); low sotto -> 100; low uguale solo con «toccato».
    assert motore.riempimento_limite(100.0, 1, candela(1, 99.0, 101, 98.5, 100), "attraversato") == (100.0, True)
    assert motore.riempimento_limite(100.0, 1, candela(1, 100.5, 101, 99.5, 100), "attraversato") == (100.0, False)
    assert motore.riempimento_limite(100.0, 1, candela(1, 100.5, 101, 100.0, 100.2), "attraversato") is None
    assert motore.riempimento_limite(100.0, 1, candela(1, 100.5, 101, 100.0, 100.2), "toccato") == (100.0, False)
    assert motore.riempimento_limite(100.0, 1, candela(1, 100.0, 101, 100.0, 100.2), "attraversato") is None  # apre A 100: non e' sotto
    # Vende a 100: simmetrico.
    assert motore.riempimento_limite(100.0, -1, candela(1, 101.0, 102, 100.5, 101), "attraversato") == (100.0, True)
    assert motore.riempimento_limite(100.0, -1, candela(1, 99.5, 100.5, 99, 100), "attraversato") == (100.0, False)
    assert motore.riempimento_limite(100.0, -1, candela(1, 99.5, 100.0, 99, 99.8), "attraversato") is None
    assert motore.riempimento_limite(100.0, -1, candela(1, 99.5, 100.0, 99, 99.8), "toccato") == (100.0, False)
    with pytest.raises(ValueError):
        motore.riempimento_limite(100.0, 1, candela(1, 99.0, 101, 98.5, 100), "boh")


# ---------------------------------------------------------------------------
# Ingresso a limite: riempito a P, all'apertura, saltato, toccato/attraversato
# ---------------------------------------------------------------------------


def test_riempito_a_p_dentro_la_barra_long():
    # Segnale alla chiusura della barra 0: P = close 100. Barra 1 apre a 100.5 (non sotto P), low 99.5 < 100:
    # riempito a 100 DENTRO la barra. ts_entrata = apertura della barra 1 (il primo istante possibile).
    # «chiudi» alla barra 1 -> uscita all'apertura della barra 2 = 101: pnl = 5 * 1 = 5, R = 5 / 10 = 0.5.
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100.5, 101, 99.5, 100.8), candela(2, 101, 102, 100.5, 101.5)]
    ris = motore.esegui(candele, None, None, [], segnale_alla_barra(0, LONG, chiudi_dopo=1), limite())
    assert len(ris.trades) == 1
    t = ris.trades[0]
    assert t.ingresso_tipo == "limite" and t.limite_prezzo == 100.0 and t.uscita_tipo == "mercato"
    assert t.entrata == 100.0 and t.ts_entrata == 1 * ORA and t.barre_attesa == 1 and t.ts_segnale == 0
    assert t.quantita == pytest.approx(5.0) and t.rischio_iniziale == pytest.approx(10.0)
    assert t.esito == "segnale" and t.uscita == 101.0 and t.ts_uscita == 2 * ORA
    assert t.pnl == pytest.approx(5.0) and t.r == pytest.approx(0.5)
    assert (ris.n_ordini_limite, ris.n_saltati, ris.n_sostituiti) == (1, 0, 0)
    assert ris.saltati == []


def test_riempito_a_p_dentro_la_barra_short():
    # Short con P = 100, stop 102. Barra 1 apre a 99.5 (non sopra P), high 100.5 > 100: riempito a 100.
    candele = [candela(0, 100, 101, 99, 100), candela(1, 99.5, 100.5, 99, 99.8), candela(2, 99, 99.5, 98, 98.5)]
    strategia = segnale_alla_barra(0, Segnale("short", stop=102.0), chiudi_dopo=1)
    t = motore.esegui(candele, None, None, [], strategia, limite()).trades[0]
    assert t.direzione == "short" and t.entrata == 100.0 and t.limite_prezzo == 100.0
    assert t.uscita == 99.0 and t.pnl == pytest.approx(5.0)  # 5 * (100 - 99)


def test_riempito_all_apertura_se_la_barra_apre_oltre_p():
    # Barra 1 apre a 99 < P = 100: riempito ALL'APERTURA ma a P = 100 (un ordine in attesa esegue al suo prezzo:
    # correzione 1 di risultati.md), ts_entrata = apertura. Short simmetrico: barra apre a 101 > 100 -> riempito a 100.
    candele = [candela(0, 100, 101, 99, 100), candela(1, 99, 100.5, 98.5, 100), candela(2, 100, 101, 99.5, 100.5)]
    t = motore.esegui(candele, None, None, [], segnale_alla_barra(0, LONG, chiudi_dopo=1), limite()).trades[0]
    assert t.entrata == 100.0 and t.limite_prezzo == 100.0 and t.ts_entrata == 1 * ORA and t.barre_attesa == 1
    candele = [candela(0, 100, 101, 99, 100), candela(1, 101, 101.5, 100.5, 101), candela(2, 101, 101.5, 100, 100.5)]
    strategia = segnale_alla_barra(0, Segnale("short", stop=103.0), chiudi_dopo=1)
    t = motore.esegui(candele, None, None, [], strategia, limite()).trades[0]
    assert t.entrata == 100.0 and t.limite_prezzo == 100.0


def test_non_riempito_scade_e_si_conta_saltato():
    # Validita' 1: la barra 1 resta sopra P (low 100.5 > 100): l'ordine scade, nessun trade, SALTATO,
    # e l'elenco dice quale segnale era (per ritrovarlo nella corsa a mercato).
    candele = [candela(0, 100, 101, 99, 100), candela(1, 101, 102, 100.5, 101.5), candela(2, 101.5, 102, 101, 101.8)]
    ris = motore.esegui(candele, None, None, [], segnale_alla_barra(0, LONG), limite())
    assert ris.trades == []
    assert (ris.n_ordini_limite, ris.n_saltati, ris.n_sostituiti) == (1, 1, 0)
    assert ris.saltati == [{"ts_segnale": 0, "direzione": "long", "limite_prezzo": 100.0, "stop": 98.0}]
    assert ris.n_segnali_non_validi == 0 and ris.n_segnali_senza_barra == 0
    # A mercato lo stesso segnale sarebbe entrato a 101 (apertura della barra 1): e' il trade che a limite salta.
    mercato = motore.esegui(candele, None, None, [], segnale_alla_barra(0, LONG), senza_costi())
    assert len(mercato.trades) == 1 and mercato.trades[0].entrata == 101.0 and mercato.trades[0].ts_segnale == 0


def test_toccato_contro_attraversato_con_low_uguale_a_p():
    # Barra 1 con low == P = 100: con «attraversato» (low < P) non si riempie -> saltato; con «toccato» (low <= P) si'.
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100.5, 101, 100.0, 100.8), candela(2, 101, 102, 100.5, 101.5)]
    strategia = segnale_alla_barra(0, LONG, chiudi_dopo=1)
    attraversato = motore.esegui(candele, None, None, [], strategia, limite(limite_condizione="attraversato"))
    toccato = motore.esegui(candele, None, None, [], strategia, limite(limite_condizione="toccato"))
    assert attraversato.trades == [] and attraversato.n_saltati == 1
    assert len(toccato.trades) == 1 and toccato.trades[0].entrata == 100.0 and toccato.n_saltati == 0


def test_validita_due_barre_riempito_nella_seconda():
    # Validita' 2: la barra 1 non scende a P (low 100.2), la barra 2 si' (low 99.8): riempito a 100 nella
    # barra 2, barre_attesa = 2, ts_entrata = apertura della barra 2. Con validita' 1 sarebbe saltato.
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100.5, 101, 100.2, 100.6),
               candela(2, 100.4, 101, 99.8, 100.5), candela(3, 100.5, 101, 100, 100.8)]
    strategia = segnale_alla_barra(0, LONG, chiudi_dopo=2)
    due = motore.esegui(candele, None, None, [], strategia, limite(limite_validita_barre=2))
    assert len(due.trades) == 1
    t = due.trades[0]
    assert t.entrata == 100.0 and t.barre_attesa == 2 and t.ts_entrata == 2 * ORA and t.ts_segnale == 0
    assert t.ts_uscita == 3 * ORA and t.uscita == 100.5
    assert due.n_saltati == 0
    una = motore.esegui(candele, None, None, [], strategia, limite(limite_validita_barre=1))
    assert una.trades == [] and una.n_saltati == 1


def test_un_segnale_nuovo_sostituisce_l_ordine_in_attesa():
    # Validita' 2. Segnale alla barra 0 (P = 100, stop 98): la barra 1 non riempie (low 100.5). Alla chiusura
    # della barra 1 la strategia emette un segnale nuovo (P' = close 102, stop 100): il vecchio e' SOSTITUITO.
    # La barra 2 apre a 101.5 < 102: il nuovo si riempie all'apertura, a P' = 102 (correzione 1).
    candele = [candela(0, 100, 101, 99, 100), candela(1, 101, 102.5, 100.5, 102),
               candela(2, 101.5, 103, 101, 102.5), candela(3, 102.5, 103, 102, 102.8)]

    def strategia(storia, posizione):
        i = len(storia) - 1
        if posizione is None and i == 0:
            return Segnale("long", stop=98.0)
        if posizione is None and i == 1:
            return Segnale("long", stop=100.0)
        if posizione is not None and i == 2:
            return "chiudi"
        return None

    ris = motore.esegui(candele, None, None, [], strategia, limite(limite_validita_barre=2))
    assert (ris.n_ordini_limite, ris.n_saltati, ris.n_sostituiti) == (2, 0, 1)
    assert len(ris.trades) == 1
    t = ris.trades[0]
    assert t.limite_prezzo == 102.0 and t.entrata == 102.0 and t.stop == 100.0 and t.ts_segnale == 1 * ORA
    assert t.barre_attesa == 1  # la prima barra di validita' del NUOVO ordine
    assert t.quantita == pytest.approx(1000 * 0.01 / 2.0)  # sul prezzo del limite 102 e lo stop 100


def test_l_ordine_in_attesa_alla_fine_dei_dati_conta_saltato():
    # Validita' 3, segnale alla barra 0, i dati finiscono alla barra 2 senza riempimento: saltato.
    candele = [candela(0, 100, 101, 99, 100), candela(1, 101, 102, 100.5, 101.5), candela(2, 101.5, 102, 101, 101.8)]
    ris = motore.esegui(candele, None, None, [], segnale_alla_barra(0, LONG), limite(limite_validita_barre=3))
    assert ris.trades == [] and ris.n_saltati == 1 and ris.n_ordini_limite == 1
    assert ris.saltati[0]["ts_segnale"] == 0


# ---------------------------------------------------------------------------
# La barra del riempimento: stop nella stessa barra, niente regole dei gap, funding ambiguo
# ---------------------------------------------------------------------------


def test_stop_nella_stessa_barra_del_riempimento():
    # Riempito a P = 100 dentro la barra 1 (apre 100.5, low 97.5). La barra tocca anche lo stop 98: non si sa
    # se prima o dopo il riempimento -> lo stop scatta (regola peggiore). Uscita a 98 con ts = chiusura della
    # barra 1; ts_entrata = apertura della barra 1: mai aperto e chiuso nello stesso istante.
    # pnl = 5 * (98 - 100) = -10, R = -1.
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100.5, 101, 97.5, 99), candela(2, 99, 100, 98.5, 99.5)]
    ris = motore.esegui(candele, None, None, [], segnale_alla_barra(0, LONG), limite())
    assert len(ris.trades) == 1
    t = ris.trades[0]
    assert t.entrata == 100.0 and t.esito == "stop" and t.uscita == 98.0
    assert t.ts_entrata == 1 * ORA and t.ts_uscita == 2 * ORA - 1
    assert t.pnl == pytest.approx(-10.0) and t.r == pytest.approx(-1.0)


def test_riempimento_all_apertura_con_gap_oltre_lo_stop_apre_e_si_ferma_subito():
    # La barra 1 apre a 97, sotto P = 100 E sotto lo stop 98: l'ordine in attesa si riempie a P = 100
    # (correzione 1 di risultati.md) e l'apertura e' gia' oltre lo stop: la regola dei gap del percorso a
    # mercato esce allo stop all'apertura, a 97, con ts_uscita = chiusura della barra come ogni uscita dentro
    # la barra. E' il caso peggiore per il trade, ed e' quello vero per un ordine in attesa nel libro:
    # perdita 5 * 3 = 15 su un rischio di 10, R = -1.5; nessun saltato, nessun segnale non valido.
    candele = [candela(0, 100, 101, 99, 100), candela(1, 97, 98.5, 96.5, 98), candela(2, 98, 99, 97.5, 98.5)]
    ris = motore.esegui(candele, None, None, [], segnale_alla_barra(0, LONG), limite())
    assert len(ris.trades) == 1 and ris.n_segnali_non_validi == 0
    t = ris.trades[0]
    assert t.entrata == 100.0 and t.esito == "stop" and t.uscita == 97.0 and t.ts_uscita == 1 * ORA + ORA - 1
    assert t.pnl == pytest.approx(-15.0) and t.r == pytest.approx(-1.5)
    assert (ris.n_ordini_limite, ris.n_saltati, ris.n_sostituiti) == (1, 0, 0)


def test_stop_dalla_parte_sbagliata_del_limite_non_mette_l_ordine():
    # Long con stop 101 sopra P = 100: non valido quando l'ordine si mette, nessun ordine.
    candele = [candela(0, 100, 101, 99, 100), candela(1, 99, 100.5, 98.5, 100), candela(2, 100, 101, 99.5, 100.5)]
    ris = motore.esegui(candele, None, None, [], segnale_alla_barra(0, Segnale("long", stop=101.0)), limite())
    assert ris.trades == [] and ris.n_segnali_non_validi == 1 and ris.n_ordini_limite == 0


def test_riempimento_dentro_la_barra_senza_le_regole_dei_gap():
    # Long P = 100, stop 98, target 103. La barra 1 apre a 104 (>= target), scende a 99 (riempie a 100) e
    # chiude a 101. Con le regole dei gap di oggi il target «gia' vero all'apertura» uscirebbe a 104: un
    # prezzo fatto PRIMA dell'ingresso. Per un riempimento dentro la barra i gap non si applicano: il
    # target e' toccato (high 105 >= 103) e si esce a 103, lo stop no (low 99 > 98). pnl = 5 * 3 = 15.
    candele = [candela(0, 100, 101, 99, 100), candela(1, 104, 105, 99, 101), candela(2, 101, 102, 100.5, 101.5)]
    strategia = segnale_alla_barra(0, Segnale("long", stop=98.0, target=103.0))
    t = motore.esegui(candele, None, None, [], strategia, limite()).trades[0]
    assert t.entrata == 100.0 and t.esito == "target" and t.uscita == 103.0 and t.pnl == pytest.approx(15.0)
    # La stessa funzione, chiamata a mano: con apertura_nota (oggi) il target all'apertura, senza no.
    pos = motore._apri_posizione_limite(Segnale("long", 98.0, 103.0), 100.0, 100.0, candele[1], 1000.0, limite(), 0, 1)
    assert motore.valuta_uscita_in_barra(pos, candele[1], candele[1], candele[1], limite()) == ("target", 104.0)
    assert motore.valuta_uscita_in_barra(pos, candele[1], candele[1], candele[1], limite(), apertura_nota=False) == ("target", 103.0)


def test_funding_nella_barra_del_riempimento_dentro_la_barra_e_ambiguo():
    # Settlement dentro la barra 1 (ts + 1000) con tasso -0.001: per un long e' un INCASSO.
    # Riempito a P dentro la barra: non si sa se la posizione era gia' aperta -> l'incasso non si conta.
    # Riempito all'apertura (barra che apre a 99): la posizione era aperta -> incasso contato (come oggi).
    # Un costo (tasso +0.001) si conta in entrambi i casi: 0.001 * 5 * mark_open.
    funding_incasso = [(1 * ORA + 1000, -0.001)]
    funding_costo = [(1 * ORA + 1000, 0.001)]
    dentro = [candela(0, 100, 101, 99, 100), candela(1, 100.5, 101, 99.5, 100.8), candela(2, 101, 102, 100.5, 101.5)]
    apertura = [candela(0, 100, 101, 99, 100), candela(1, 99, 101, 98.5, 100.8), candela(2, 101, 102, 100.5, 101.5)]
    strategia = segnale_alla_barra(0, LONG, chiudi_dopo=1)
    t_dentro = motore.esegui(dentro, None, None, funding_incasso, strategia, limite()).trades[0]
    t_apertura = motore.esegui(apertura, None, None, funding_incasso, strategia, limite()).trades[0]
    assert t_dentro.funding_pagato == pytest.approx(0.0)
    assert t_apertura.funding_pagato == pytest.approx(-0.001 * 5 * 99.0)
    t_dentro_costo = motore.esegui(dentro, None, None, funding_costo, strategia, limite()).trades[0]
    assert t_dentro_costo.funding_pagato == pytest.approx(0.001 * 5 * 100.5)


# ---------------------------------------------------------------------------
# Costi: maker e slippage zero sull'ingresso, taker e slippage sull'uscita; quantita' su P, R sul riempimento
# ---------------------------------------------------------------------------


def test_commissione_maker_e_slippage_zero_sull_ingresso_taker_sull_uscita():
    # Costi veri: taker 0.0005, slippage 0.0002, maker 0.0002. Riempito a P = 100 dentro la barra 1
    # (quantita' 5, nessuno slippage: entrata = 100). «chiudi» -> uscita all'apertura della barra 2 = 101,
    # peggiorata: 101 * (1 - 0.0002) = 100.9798.
    # pnl_lordo = 5 * (101 - 100) = 5
    # commissioni = 5 * (0.0002 * 100 + 0.0005 * 100.9798) = 5 * 0.0704899 = 0.3524495
    # slippage = 5 * (0 + 0.0202) = 0.101
    # pnl = 5 - 0.3524495 - 0.101 = 4.5465505; R = 4.5465505 / 10 = 0.45465505
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100.5, 101, 99.5, 100.8), candela(2, 101, 102, 100.5, 101.5)]
    parametri = Parametri(ingresso="limite")  # costi predefiniti: 0.0005, 0.0002, maker 0.0002
    t = motore.esegui(candele, None, None, [], segnale_alla_barra(0, LONG, chiudi_dopo=1), parametri).trades[0]
    assert t.entrata == 100.0 and t.quantita == pytest.approx(5.0)
    assert t.uscita == pytest.approx(100.9798)
    assert t.commissioni == pytest.approx(0.3524495)
    assert t.slippage_costo == pytest.approx(0.101)
    assert t.pnl == pytest.approx(4.5465505) and t.r == pytest.approx(0.45465505)
    # Il moltiplicatore dei costi raddoppia anche la maker: commissioni 0.7048990 con slippage 0.202.
    doppio = motore.esegui(candele, None, None, [], segnale_alla_barra(0, LONG, chiudi_dopo=1),
                           Parametri(ingresso="limite", moltiplicatore_costi=2.0)).trades[0]
    assert doppio.commissioni == pytest.approx(5 * (0.0004 * 100 + 0.001 * (101 * (1 - 0.0004))))
    assert doppio.slippage_costo == pytest.approx(5 * 101 * 0.0004)
    # Lo stesso segnale a mercato entra all'apertura della barra 1, 100.5 * (1 + 0.0002), con quantita' 4
    # (= 1000 * 0.01 / 2.5) e paga taker sui due lati e slippage sui due lati:
    # slippage = 4 * (0.0201 + 0.0202) = 0.1612; commissioni = 0.0005 * 4 * (100.5201 + 100.9798) = 0.4029998.
    m = motore.esegui(candele, None, None, [], segnale_alla_barra(0, LONG, chiudi_dopo=1), Parametri()).trades[0]
    assert m.entrata == pytest.approx(100.5 * 1.0002) and m.ingresso_tipo == "mercato" and m.limite_prezzo is None
    assert m.slippage_costo == pytest.approx(0.1612) and m.commissioni == pytest.approx(0.4029998)


def test_quantita_sul_prezzo_del_limite_e_rischio_sul_riempimento_vero():
    # P = 100, stop 98: quantita' = 1000 * 0.01 / 2 = 5. La barra 1 apre a 99 (oltre P): riempito all'apertura
    # ma a P = 100 (correzione 1). Rischio iniziale vero = 5 * |100 - 98| = 10 = 1% del capitale. «chiudi» ->
    # uscita a 101 (apertura barra 2): pnl = 5 * 1 = 5, R = 5 / 10 = 0.5. A mercato si entra a 99 (apertura
    # della barra 1) con lo stesso stop: quantita' 10, pnl 10 * 2 = 20, R = 20 / 10 = 2.0.
    candele = [candela(0, 100, 101, 99, 100), candela(1, 99, 100.5, 98.5, 100), candela(2, 101, 102, 100.5, 101.5)]
    t = motore.esegui(candele, None, None, [], segnale_alla_barra(0, LONG, chiudi_dopo=1), limite()).trades[0]
    assert t.entrata == 100.0 and t.quantita == pytest.approx(5.0) and t.rischio_iniziale == pytest.approx(10.0)
    assert t.pnl == pytest.approx(5.0) and t.r == pytest.approx(0.5)
    m = motore.esegui(candele, None, None, [], segnale_alla_barra(0, LONG, chiudi_dopo=1), senza_costi()).trades[0]
    assert m.entrata == 99.0 and m.quantita == pytest.approx(10.0) and m.r == pytest.approx(2.0)


def test_tetto_di_leva_sul_notional_del_riempimento():
    # Stop a 99.9 con P = 100: quantita' teorica 100, notional 100 * 100 > 2000 (leva 2): ridotta a 2000 / 100 = 20.
    # La barra 1 apre a 99.95 (oltre P): riempito a P = 100 (correzione 1).
    candele = [candela(0, 100, 101, 99, 100), candela(1, 99.95, 100.5, 99.92, 100.2), candela(2, 100.2, 101, 100, 100.5)]
    t = motore.esegui(candele, None, None, [], segnale_alla_barra(0, Segnale("long", stop=99.9), chiudi_dopo=1), limite()).trades[0]
    assert t.entrata == 100.0 and t.ridotto and t.quantita == pytest.approx(20.0)


# ---------------------------------------------------------------------------
# Ritardo di una barra, capitale esaurito, parametri sbagliati
# ---------------------------------------------------------------------------


def test_ritardo_di_una_barra_sposta_l_ordine_e_il_suo_prezzo():
    # ritardo_barre = 1: il segnale della barra 0 si vede alla barra 1, l'ordine ha P = close della barra 1
    # (= 102) ed e' valido per la barra 2. ts_segnale resta l'apertura della barra 0; barre_attesa non
    # conta il ritardo.
    candele = [candela(0, 100, 101, 99, 100), candela(1, 101, 102.5, 100.5, 102),
               candela(2, 102.2, 103, 101.5, 102.8), candela(3, 102.8, 103.5, 102, 103)]
    strategia = segnale_alla_barra(0, Segnale("long", stop=99.0), chiudi_dopo=2)
    t = motore.esegui(candele, None, None, [], strategia, limite(ritardo_barre=1)).trades[0]
    assert t.limite_prezzo == 102.0 and t.entrata == 102.0 and t.ts_entrata == 2 * ORA
    assert t.ts_segnale == 0 and t.barre_attesa == 1


def test_capitale_esaurito_non_mette_l_ordine():
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100.5, 101, 99.5, 100.8), candela(2, 101, 102, 100.5, 101.5)]
    ris = motore.esegui(candele, None, None, [], segnale_alla_barra(0, LONG), limite(capitale_iniziale=0.0))
    assert ris.trades == [] and ris.n_segnali_capitale_esaurito == 1 and ris.n_ordini_limite == 0


def test_parametri_sbagliati_alzano_value_error():
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100.5, 101, 99.5, 100.8)]
    for parametri in (Parametri(ingresso="boh"), Parametri(uscita_segnale="boh"), Parametri(limite_condizione="boh"),
                      Parametri(ingresso="limite", limite_validita_barre=0)):
        with pytest.raises(ValueError):
            motore.esegui(candele, None, None, [], segnale_alla_barra(0, LONG), parametri)


def test_con_limite_un_segnale_ogni_barra_rinnova_l_ordine_ogni_barra():
    # Strategia che ripete il segnale a ogni chiusura senza posizione, validita' 2: ogni barra senza
    # riempimento conta un sostituito, e il prezzo del limite insegue la chiusura. Si riempie alla barra 3
    # (apre a 101.8 < P = 102, la chiusura della barra 2), a P = 102 (correzione 1).
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100.5, 101.5, 100.2, 101),
               candela(2, 101.2, 102.5, 101.1, 102), candela(3, 101.8, 102.2, 101.5, 102), candela(4, 102, 103, 101.9, 102.5)]

    def strategia(storia, posizione):
        return Segnale("long", stop=storia[-1].close - 2.0) if posizione is None else None

    ris = motore.esegui(candele, None, None, [], strategia, limite(limite_validita_barre=2))
    assert ris.n_ordini_limite == 3 and ris.n_sostituiti == 2 and ris.n_saltati == 0
    assert len(ris.trades) == 1 and ris.trades[0].limite_prezzo == 102.0 and ris.trades[0].entrata == 102.0
    assert ris.trades[0].esito == "fine_dati"


# ---------------------------------------------------------------------------
# Variante (c): l'uscita «chiudi» con ordine limite
# ---------------------------------------------------------------------------

# Long a mercato all'apertura della barra 1 (= 100), «chiudi» alla chiusura della barra 2 (close 103 = P_u).
BARRE_C = [candela(0, 100, 101, 99, 100), candela(1, 100, 101, 99.5, 100.5), candela(2, 100.5, 103.5, 100, 103)]
STRATEGIA_C = segnale_alla_barra(0, LONG, chiudi_dopo=2)


def test_uscita_a_limite_eseguita_all_apertura():
    # Barra 3 apre a 104 > 103: si esce all'apertura (certa) ma a P = 103 (ordine in attesa: correzione 1),
    # maker, slippage zero, ts = apertura.
    candele = BARRE_C + [candela(3, 104, 105, 103.5, 104.5), candela(4, 104.5, 105, 104, 104.8)]
    parametri = Parametri(uscita_segnale="limite", slippage_per_lato=0.0, commissione_per_lato=0.0005, commissione_maker_per_lato=0.0002)
    ris = motore.esegui(candele, None, None, [], STRATEGIA_C, parametri)
    t = ris.trades[0]
    assert t.esito == "segnale" and t.uscita_tipo == "limite" and t.uscita == 103.0 and t.ts_uscita == 3 * ORA
    assert t.ingresso_tipo == "mercato" and t.entrata == 100.0
    # commissioni: taker sull'ingresso (0.0005 * 100) + maker sull'uscita (0.0002 * 103), per quantita' 5
    assert t.commissioni == pytest.approx(5 * (0.0005 * 100 + 0.0002 * 103))
    assert t.slippage_costo == 0.0
    assert (ris.n_uscite_limite_eseguite, ris.n_uscite_limite_mancate) == (1, 0)


def test_uscita_a_limite_eseguita_dentro_la_barra():
    # Barra 3 apre a 102.5 (non sopra 103), high 103.5 > 103: si esce a 103, ts = chiusura della barra 3.
    candele = BARRE_C + [candela(3, 102.5, 103.5, 102, 103.2), candela(4, 103, 104, 102.5, 103.5)]
    ris = motore.esegui(candele, None, None, [], STRATEGIA_C, senza_costi(uscita_segnale="limite"))
    t = ris.trades[0]
    assert t.esito == "segnale" and t.uscita_tipo == "limite" and t.uscita == 103.0 and t.ts_uscita == 4 * ORA - 1
    assert t.pnl == pytest.approx(15.0)
    assert ris.n_uscite_limite_eseguite == 1
    # Con «toccato» basta high == P: barra 3 con high 103.0.
    candele_tocca = BARRE_C + [candela(3, 102.5, 103.0, 102, 102.8), candela(4, 103, 104, 102.5, 103.5)]
    no = motore.esegui(candele_tocca, None, None, [], STRATEGIA_C, senza_costi(uscita_segnale="limite"))
    si = motore.esegui(candele_tocca, None, None, [], STRATEGIA_C, senza_costi(uscita_segnale="limite", limite_condizione="toccato"))
    assert no.trades[0].uscita_tipo == "mercato" and no.n_uscite_limite_mancate == 1
    assert si.trades[0].uscita_tipo == "limite" and si.trades[0].uscita == 103.0


def test_uscita_a_limite_mancata_esce_a_mercato_la_barra_dopo():
    # Barra 3 resta sotto 103 (high 102.8): mancata; si esce a mercato all'apertura della barra 4 = 102.2,
    # con slippage e taker come oggi: uscita = 102.2 * (1 - 0.0002).
    candele = BARRE_C + [candela(3, 102.5, 102.8, 102, 102.6), candela(4, 102.2, 103, 102, 102.5), candela(5, 102.5, 103, 102, 102.8)]
    parametri = Parametri(uscita_segnale="limite")
    ris = motore.esegui(candele, None, None, [], STRATEGIA_C, parametri)
    t = ris.trades[0]
    assert t.esito == "segnale" and t.uscita_tipo == "mercato" and t.ts_uscita == 4 * ORA
    assert t.uscita == pytest.approx(102.2 * (1 - 0.0002))
    assert (ris.n_uscite_limite_eseguite, ris.n_uscite_limite_mancate) == (0, 1)
    # Identico a quello che fa oggi un «chiudi» emesso alla barra 3 (uscita all'apertura della barra 4).
    oggi = motore.esegui(candele, None, None, [], segnale_alla_barra(0, LONG, chiudi_dopo=3), Parametri()).trades[0]
    assert (t.uscita, t.pnl, t.commissioni, t.slippage_costo) == (oggi.uscita, oggi.pnl, oggi.commissioni, oggi.slippage_costo)


def test_uscita_a_limite_lo_stop_nella_stessa_barra_vince():
    # Barra 3 apre a 102.5, sale a 103.5 (raggiunge il limite) ma scende anche a 97 (sotto lo stop 98):
    # vale lo stop (regola peggiore). Uscita a 98 a mercato.
    candele = BARRE_C + [candela(3, 102.5, 103.5, 97, 99), candela(4, 99, 100, 98, 99.5)]
    ris = motore.esegui(candele, None, None, [], STRATEGIA_C, senza_costi(uscita_segnale="limite"))
    t = ris.trades[0]
    assert t.esito == "stop" and t.uscita_tipo == "mercato" and t.uscita == 98.0
    assert (ris.n_uscite_limite_eseguite, ris.n_uscite_limite_mancate) == (0, 1)


def test_uscita_a_limite_non_tocca_stop_target_e_fine_dati():
    # Con uscita_segnale="limite" un trade che esce per target (o stop, o fine dati) e' identico a oggi.
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100, 101, 99.5, 100.5), candela(2, 100.5, 104, 100, 103.5)]
    strategia = segnale_alla_barra(0, Segnale("long", stop=98.0, target=103.0))
    oggi = motore.esegui(candele, None, None, [], strategia, Parametri()).trades[0]
    c = motore.esegui(candele, None, None, [], strategia, Parametri(uscita_segnale="limite")).trades[0]
    assert c.esito == "target" and c.uscita_tipo == "mercato"
    assert (c.uscita, c.pnl, c.commissioni, c.slippage_costo, c.ts_uscita) == (oggi.uscita, oggi.pnl, oggi.commissioni, oggi.slippage_costo, oggi.ts_uscita)
    # Fine dati nella barra di validita' dell'uscita a limite: chiusura "fine_dati" come oggi, limite mancato.
    corte = BARRE_C + [candela(3, 102.5, 102.8, 102, 102.6)]
    ris = motore.esegui(corte, None, None, [], STRATEGIA_C, senza_costi(uscita_segnale="limite"))
    assert ris.trades[0].esito == "fine_dati" and ris.trades[0].uscita_tipo == "mercato" and ris.n_uscite_limite_mancate == 1


def test_ingresso_e_uscita_a_limite_insieme_maker_sui_due_lati():
    # Ingresso a limite riempito a 100 (barra 1 apre 100.5, low 99.5), «chiudi» alla barra 2, uscita a
    # limite eseguita all'apertura della barra 3 (104 > 103) ma a P_u = 103 (correzione 1): maker sui due
    # lati, slippage zero.
    candele = [candela(0, 100, 101, 99, 100), candela(1, 100.5, 101, 99.5, 100.5), candela(2, 100.5, 103.5, 100, 103),
               candela(3, 104, 105, 103.5, 104.5), candela(4, 104.5, 105, 104, 104.8)]
    parametri = Parametri(ingresso="limite", uscita_segnale="limite")
    t = motore.esegui(candele, None, None, [], STRATEGIA_C, parametri).trades[0]
    assert t.ingresso_tipo == "limite" and t.uscita_tipo == "limite" and t.entrata == 100.0 and t.uscita == 103.0
    assert t.ts_uscita == 3 * ORA
    assert t.commissioni == pytest.approx(0.0002 * 5 * (100 + 103)) and t.slippage_costo == 0.0
    assert t.pnl == pytest.approx(5 * 3 - 0.0002 * 5 * 203)


# ---------------------------------------------------------------------------
# PARITA': con ingresso="mercato" i trade sono IDENTICI a quelli del motore di prima
# ---------------------------------------------------------------------------

CAMPI_PRIMA = (
    "direzione", "ts_entrata", "ts_uscita", "entrata", "uscita", "stop", "target", "quantita", "ridotto",
    "violazione_liquidazione", "esito", "pnl", "pnl_lordo", "commissioni", "slippage_costo", "funding_pagato",
    "rischio_iniziale", "r", "leva_effettiva", "prezzo_liquidazione", "pnl_pct",
)

# Calcolate il 13 ott 2026 con il motore del commit 39bb60b2 (prima degli ordini limite): per ogni corsa
# (numero di trade, repr del capitale finale, SHA-256 della repr di tutti i CAMPI_PRIMA dei trade, della
# curva del capitale e dei contatori). Le corse coprono stop, target, «chiudi», quantita' ridotte dal tetto
# di leva, segnali non validi (col ritardo), gap in apertura, due buchi nei dati con un settlement dentro,
# funding all'apertura e dentro la barra, serie stop sul mark, cross e target_prima.
IMPRONTE_PRIMA = {
    "base": (33, "950.5724175538724", "4d2901a65e2430101b00f42ad1b8a8e6e693d5d3d0d90ba03ca04d7b5a5a23db"),
    "ritardo_e_costi_doppi": (29, "924.1998874272441", "36a4ce7a27b9d440daaa99826b4f1d658145a76704c92257429555db03217c2e"),
    "cross_target_prima_stop_sul_mark": (33, "939.0762367576674", "f91420d9dc4b2f431cbb5670c1c9822ec39189fd0e7f4fbf2aa5010f228578ea"),
}

PERCORSO_MOTORE_PRIMA = Path(
    "/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/motore_prima.py"
)


def serie_di_parita(m):
    """Candele last e mark (300 barre meno 2 buchi, gap in apertura) e funding, dal seme 20261013."""
    rnd = random.Random(20261013)
    prezzo = 100.0
    last, mark, funding = [], [], []
    indice_ts = 0
    for i in range(300):
        if i in (97, 211):  # buco: la barra manca, il tempo passa; un settlement cade nel buco
            funding.append((indice_ts * ORA + 10, 0.0002))
            indice_ts += 1
            continue
        o = prezzo * (1 + rnd.gauss(0, 0.004)) if rnd.random() < 0.2 else prezzo  # gap in apertura una volta su 5
        c = o * (1 + rnd.gauss(0, 0.012))
        h = max(o, c) * (1 + abs(rnd.gauss(0, 0.005)))
        l = min(o, c) * (1 - abs(rnd.gauss(0, 0.005)))
        ts = indice_ts * ORA
        last.append(m.Candela(ts=ts, open=o, high=h, low=l, close=c, volume=1.0, close_ts=ts + ORA - 1))
        f = 1 + rnd.gauss(0, 0.0008)
        mark.append(m.Candela(ts=ts, open=o * f, high=h * f, low=l * f, close=c * f, volume=1.0, close_ts=ts + ORA - 1))
        if indice_ts % 8 == 0:  # settlement all'apertura della barra (il caso normale)
            funding.append((ts, rnd.choice([0.0001, -0.0001, 0.0003])))
        if indice_ts % 50 == 25:  # settlement dentro la barra
            funding.append((ts + 1000, -0.0002))
        prezzo = c
        indice_ts += 1
    return last, mark, funding


def crea_strategia_di_parita(m):
    """Segnali ogni 9 barre (long con o senza target, stop stretto una volta su 4, short una volta su 3), «chiudi» dopo 6 barre."""
    stato = {"barre_aperte": 0}

    def strategia(storia, posizione):
        i = len(storia) - 1
        ultima = storia[-1]
        if posizione is not None:
            stato["barre_aperte"] += 1
            return "chiudi" if stato["barre_aperte"] >= 6 else None
        stato["barre_aperte"] = 0
        if i % 9 != 4:
            return None
        k = i // 9
        if k % 3 == 2:
            return m.Segnale("short", stop=ultima.close * 1.015, target=ultima.close * 0.97)
        stop = ultima.close * (0.999 if k % 4 == 1 else 0.98)  # 0.999: quantita' ridotta dal tetto di leva
        return m.Segnale("long", stop=stop, target=None if k % 2 else ultima.close * 1.025)

    return strategia


def corse_di_parita(m):
    """Le tre corse del confronto: last, mark, funding e {nome: (candele_stop, parametri)}."""
    last, mark, funding = serie_di_parita(m)
    return last, mark, funding, {
        "base": (None, m.Parametri()),
        "ritardo_e_costi_doppi": (None, m.Parametri(ritardo_barre=1, moltiplicatore_costi=2.0)),
        "cross_target_prima_stop_sul_mark": (mark, m.Parametri(modalita_margine="cross", riempimento_intrabarra="target_prima", leva_max=3.0)),
    }


def righe_di_parita(m, nome: str):
    """I trade (solo CAMPI_PRIMA), la curva e i contatori di una corsa, con il modulo ``m``."""
    last, mark, funding, corse = corse_di_parita(m)
    candele_stop, parametri = corse[nome]
    ris = m.esegui(last, candele_stop, mark, funding, crea_strategia_di_parita(m), parametri)
    righe = [tuple(getattr(t, campo) for campo in CAMPI_PRIMA) for t in ris.trades]
    contatori = (ris.capitale_iniziale, ris.capitale_finale, ris.n_segnali_non_validi, ris.n_segnali_senza_barra,
                 ris.n_segnali_capitale_esaurito, ris.n_buchi_dati, ris.n_funding_in_buco)
    return righe, ris.curva_capitale, contatori, ris


def test_lo_scenario_di_parita_copre_i_percorsi_del_motore():
    righe, _, contatori, ris = righe_di_parita(motore, "base")
    esiti = {t.esito for t in ris.trades}
    assert {"stop", "target", "segnale"} <= esiti and len(righe) == 33
    assert any(t.ridotto for t in ris.trades) and any(t.funding_pagato != 0 for t in ris.trades)
    assert ris.n_buchi_dati == 2 and ris.n_funding_in_buco == 1
    assert righe_di_parita(motore, "ritardo_e_costi_doppi")[3].n_segnali_non_validi > 0


@pytest.mark.parametrize("nome", sorted(IMPRONTE_PRIMA))
def test_con_ingresso_a_mercato_i_trade_sono_identici_alle_impronte_di_prima(nome):
    righe, curva, contatori, ris = righe_di_parita(motore, nome)
    testo = repr((righe, curva, contatori))
    impronta = hashlib.sha256(testo.encode("ascii")).hexdigest()
    n_attesi, capitale_atteso, impronta_attesa = IMPRONTE_PRIMA[nome]
    assert len(righe) == n_attesi
    assert repr(ris.capitale_finale) == capitale_atteso
    assert impronta == impronta_attesa, f"{nome}: i trade a mercato non sono piu' identici a quelli del motore di prima"
    # I campi nuovi hanno i valori «a mercato» e i contatori nuovi sono a zero.
    assert all(t.ingresso_tipo == "mercato" and t.limite_prezzo is None and t.barre_attesa == 1 and t.uscita_tipo == "mercato"
               for t in ris.trades)
    assert all(t.ts_segnale is not None and t.ts_segnale < t.ts_entrata for t in ris.trades)
    assert (ris.n_ordini_limite, ris.n_saltati, ris.n_sostituiti, ris.n_uscite_limite_eseguite, ris.n_uscite_limite_mancate) == (0,) * 5
    assert ris.saltati == []


def _carica_motore_prima():
    percorso = Path(os.environ.get("MOTORE_PRIMA", "")) if os.environ.get("MOTORE_PRIMA") else PERCORSO_MOTORE_PRIMA
    if not percorso.is_file():
        pytest.skip(f"copia del motore di prima non trovata ({percorso}): vale il confronto con le impronte")
    spec = importlib.util.spec_from_file_location("motore_prima_ordini_limite", str(percorso))
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = modulo  # i dataclass con annotazioni rimandate vogliono il modulo registrato
    try:
        spec.loader.exec_module(modulo)
    finally:
        sys.modules.pop(spec.name, None)
    return modulo


@pytest.mark.parametrize("nome", sorted(IMPRONTE_PRIMA))
def test_con_ingresso_a_mercato_i_trade_sono_identici_alla_copia_del_motore_di_prima(nome):
    prima = _carica_motore_prima()
    righe_prima, curva_prima, contatori_prima, _ = righe_di_parita(prima, nome)
    righe_dopo, curva_dopo, contatori_dopo, _ = righe_di_parita(motore, nome)
    assert len(righe_dopo) == len(righe_prima)
    for k, (riga_prima, riga_dopo) in enumerate(zip(righe_prima, righe_dopo)):
        for campo, prima_v, dopo_v in zip(CAMPI_PRIMA, riga_prima, riga_dopo):
            assert prima_v == dopo_v, f"{nome}, trade {k}, campo {campo}: prima {prima_v!r}, dopo {dopo_v!r}"
    assert curva_dopo == curva_prima
    assert contatori_dopo == contatori_prima
