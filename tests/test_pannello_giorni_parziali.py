"""Il pannello del programma 6 non usa un ultimo giorno pubblicato solo in parte dall'archivio di Binance (10 novembre 2026: l'8
novembre c'era per 232 monete su circa 715 e le decisioni settimanali del lunedi' si facevano su quel giorno a meta')."""
import numpy as np

from research.programma6.seconda import giorni_parziali_in_coda


def _prezzi(conteggi, monete=10):
    c = np.full((len(conteggi), monete), np.nan)
    for i, n in enumerate(conteggi):
        c[i, :n] = 1.0
    return c


def test_ultimo_giorno_a_meta_si_toglie():
    assert giorni_parziali_in_coda(_prezzi([10, 10, 10, 3])) == 1


def test_due_giorni_in_coda_parziali_si_tolgono_entrambi():
    assert giorni_parziali_in_coda(_prezzi([10, 10, 5, 2])) == 2


def test_giorni_completi_e_piccole_differenze_restano():
    assert giorni_parziali_in_coda(_prezzi([10, 10, 10, 10])) == 0
    assert giorni_parziali_in_coda(_prezzi([10, 10, 10, 9])) == 0       # una moneta tolta dal listino non e' un giorno a meta'


def test_monete_nuove_che_entrano_non_contano_come_parziale():
    assert giorni_parziali_in_coda(_prezzi([8, 9, 10, 10])) == 0
