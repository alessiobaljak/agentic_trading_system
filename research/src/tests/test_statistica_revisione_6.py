"""Revisione avversaria n. 6 del modulo `statistica` (lente: la matematica).

Ogni test qui smaschera un difetto trovato leggendo il codice ed eseguendolo.
I test che FALLISCONO sono voluti: servono a chi corregge, e devono tornare
verdi dopo la correzione. In fondo ci sono pochi controlli di sanita' che
passano gia' (bootstrap circolare, seme, blocco 1 = bootstrap semplice): sono
le proprieta' verificate e NON difettose, lasciate come guardia.
"""
from __future__ import annotations

from fractions import Fraction

import numpy as np
import pytest

from research.src import statistica as st

# ---------------------------------------------------------------------------
# Difetto 1 - Benjamini-Hochberg: parita' p(k) == k/m*q persa per il floating point
# ---------------------------------------------------------------------------
#
# Il protocollo dice "p(k) <= (k/m) x 0,10". Il codice confronta p[i] con
# `rango / m * q` calcolato in virgola mobile: per alcune coppie (k, m) il
# prodotto viene un pelo SOTTO il valore esatto (es. 7/10*0.1 =
# 0.06999999999999999) e un p-value esattamente sulla soglia viene respinto.
# Con m=10 candidati e p(7) = 0.07 il settimo dovrebbe passare: non passa.


def test_bh_parita_esatta_sulla_soglia_m10_k7():
    p = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.5, 0.6, 0.7]
    # soglie esatte: 0.01, 0.02, ..., 0.07 -> k massimo = 7 (0.07 <= 0.07)
    atteso = [True] * 7 + [False] * 3
    assert st.benjamini_hochberg(p, q=0.1) == atteso


@pytest.mark.parametrize("m,k", [(10, 7), (20, 7), (20, 14), (30, 21), (40, 7)])
def test_bh_parita_esatta_varie_coppie(m, k):
    # Costruisco m p-value in cui il k-esimo e' ESATTAMENTE k/m*q (come float
    # della frazione esatta) e tutti gli altri sono o molto piccoli (prima di k)
    # o 1.0 (dopo k): per definizione passano i primi k.
    soglia = float(Fraction(k, m) * Fraction(1, 10))
    p = [soglia / 10.0] * (k - 1) + [soglia] + [1.0] * (m - k)
    atteso = [True] * k + [False] * (m - k)
    assert st.benjamini_hochberg(p, q=0.1) == atteso


# ---------------------------------------------------------------------------
# Difetto 2 - entrate_casuali: ValueError dipendente dal seme anche se una
# configurazione valida esiste (greedy su permutazione, non "piazzamento")
# ---------------------------------------------------------------------------
#
# Con 5 barre, distanza 2 e 3 ingressi l'unica configurazione e' [0, 2, 4].
# Il greedy pesca a caso: se il primo indice e' 1 (o 3) si blocca a 2 ingressi
# e alza ValueError. Con i semi 0..4 ritorna [0, 2, 4], con il seme 5 (e 8)
# alza. Stessi parametri, esito diverso a seconda del seme: per il tasso del
# caso (molte simulazioni con semi diversi) alcune simulazioni cadono e altre
# no, e chi chiama non puo' "ridurre il numero di trade" come dice la docstring
# senza cambiare il confronto (il protocollo vuole LO STESSO numero di trade).


def test_entrate_casuali_non_deve_fallire_se_la_configurazione_esiste():
    for seme in range(10):
        # Deve riuscire con qualunque seme: l'unica configurazione e' [0, 2, 4]
        assert st.entrate_casuali(5, 3, 2, seme) == [0, 2, 4], f"seme {seme}"


def test_entrate_casuali_copertura_80_per_cento_riesce_con_ogni_seme():
    # 1000 barre, durata 10 -> al massimo 100 ingressi; 80 e' sotto il massimo
    # con margine del 20%, eppure con il greedy riesce solo in 10 semi su 50.
    # Un candidato in posizione l'80% del tempo e' realistico (trend following).
    falliti = []
    for seme in range(50):
        try:
            idx = st.entrate_casuali(1000, 80, 10, seme)
            assert len(idx) == 80
            assert all(b - a >= 10 for a, b in zip(idx, idx[1:]))
        except ValueError:
            falliti.append(seme)
    assert falliti == [], f"semi falliti: {len(falliti)}/50 -> {falliti}"


# ---------------------------------------------------------------------------
# Difetto 3 - bootstrap degenere quando il blocco raggiunge la serie:
# errore 0, "netta" sempre True e p-value al MINIMO per un vantaggio nullo
# ---------------------------------------------------------------------------
#
# Con lunghezza_blocco >= len(serie) il modulo riduce il blocco in silenzio
# alla lunghezza della serie: ogni ricampionamento e' una rotazione circolare
# della serie, la media e' sempre la stessa, errore_standard = 0. Conseguenza
# nelle funzioni a valle:
#  * differenza_nettamente: margine 0 -> QUALSIASI differenza non nulla e'
#    "netta", anche 1e-9;
#  * p_value_bootstrap_vs_caso: tutte le differenze ricampionate sono uguali a
#    quella osservata -> p = 1/(n+1) (il minimo possibile) per un vantaggio
#    di 1e-9. E' l'opposto di prudente: un candidato con pochi trade e
#    posizioni lunghe (blocco in trade >= numero di trade) passerebbe
#    l'asticella con il p-value piu' piccolo ottenibile.
# Misurato (seme 3, 30 trade normali con vantaggio ~0.15 R): blocco 10 -> p=0.23,
# blocco 29 -> p=0.0155, blocco 30 -> p=0.0005, blocco 40 -> p=0.0005.
# La funzione dovrebbe rifiutare (ValueError) o segnalare il caso degenere,
# non restituire il risultato piu' favorevole.


def _serie_candidato_e_caso():
    rng = np.random.default_rng(3)
    caso = rng.normal(0.0, 1.0, 30)
    candidato = caso + 1e-9  # vantaggio di fatto nullo
    return list(candidato), list(caso)


def test_blocco_lungo_quanto_la_serie_non_deve_dare_p_value_minimo():
    candidato, caso = _serie_candidato_e_caso()
    n = 2000
    p = st.p_value_bootstrap_vs_caso(candidato, caso, lunghezza_blocco=30, n=n, seme=0)
    # oggi p == 1/(n+1) == 0.0005: il minimo raggiungibile, per 1e-9 di vantaggio
    assert p > 0.05, f"p={p} per un vantaggio di 1e-9 con blocco = len(serie)"


def test_blocco_piu_lungo_della_serie_non_deve_dare_p_value_minimo():
    candidato, caso = _serie_candidato_e_caso()
    p = st.p_value_bootstrap_vs_caso(candidato, caso, lunghezza_blocco=40, n=2000, seme=0)
    assert p > 0.05, f"p={p} per un vantaggio di 1e-9 con blocco > len(serie)"


def test_blocco_lungo_quanto_la_serie_non_deve_dire_netta_per_1e_9():
    candidato, caso = _serie_candidato_e_caso()
    r = st.differenza_nettamente(candidato, caso, lunghezza_blocco=30, n=2000, seme=0)
    assert abs(r["differenza"] - 1e-9) < 1e-12
    # errore_standard 0 -> margine 0 -> netta True: una differenza di 1e-9 R
    # dichiarata "nettamente" migliore della baseline.
    assert not r["netta"], r


def test_bootstrap_blocco_oltre_la_serie_segnala_il_caso_degenere():
    # Variante piu' stretta: con blocco >= len(serie) il bootstrap non stima
    # nulla (errore 0 per costruzione). Ci si aspetta un rifiuto esplicito.
    with pytest.raises(ValueError):
        st.bootstrap_blocchi([1.0, 2.0, 3.0, 4.0, 5.0], lunghezza_blocco=5, n=100, seme=0)


# ---------------------------------------------------------------------------
# Controlli di sanita' VERIFICATI (passano): guardia per chi corregge
# ---------------------------------------------------------------------------


def test_bootstrap_stesso_seme_stesso_risultato():
    a = st.bootstrap_blocchi([1, 2, 3, 4, 5, 6, 7, 8], 3, n=100, seme=7)
    b = st.bootstrap_blocchi([1, 2, 3, 4, 5, 6, 7, 8], 3, n=100, seme=7)
    assert np.array_equal(a["campioni"], b["campioni"])
    assert a["intervallo_95"] == b["intervallo_95"]


def test_indici_blocchi_sono_circolari_e_contigui():
    rng = np.random.default_rng(0)
    idx = st._indici_blocchi_circolari(10, 4, 500, rng)
    assert idx.shape == (500, 10)
    # dentro ogni blocco di 4 gli indici sono consecutivi modulo 10
    for riga in idx[:50]:
        for inizio in range(0, 8, 4):
            blocco = riga[inizio : inizio + 4]
            assert all((blocco[j + 1] - blocco[j]) % 10 == 1 for j in range(len(blocco) - 1))
    # il wrap-around capita davvero (c'e' un blocco che da 9 passa a 0)
    assert any(((riga[j] == 9) and (riga[j + 1] == 0)) for riga in idx for j in range(0, 9) if (j % 4) != 3)


def test_blocco_uno_e_bootstrap_semplice():
    # Con blocco 1 ogni indice e' pescato uniforme: su molti campioni la
    # frequenza di ogni indice e' ~1/n (qui 1/5 = 0.2, tolleranza 2%).
    rng = np.random.default_rng(1)
    idx = st._indici_blocchi_circolari(5, 1, 20000, rng)
    freq = np.bincount(idx.ravel(), minlength=5) / idx.size
    assert np.allclose(freq, 0.2, atol=0.02)


def test_p_value_unilaterale_correzione():
    # 3 valori su 4 >= osservato -> (3+1)/(4+1) = 0.8; nessuno -> 1/5
    assert st.p_value_unilaterale(2.0, [1.0, 2.0, 3.0, 4.0]) == pytest.approx(0.8)
    assert st.p_value_unilaterale(10.0, [1.0, 2.0, 3.0, 4.0]) == pytest.approx(0.2)
