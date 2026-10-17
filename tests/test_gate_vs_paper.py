"""Ripartizione del PnL per fascia di mfe_r (scripts/gate_vs_paper).

Il punto del report e' mostrare CHI fa il risultato: sotto scale-out un trade che
si ferma al primo gradino incassa una briciola, uno che corre fino all'ultimo vale
dieci volte tanto. Se le fasce fossero classificate male, il confronto gate<->paper
direbbe l'opposto del vero — questi test bloccano i confini.
"""
from scripts.gate_vs_paper import _bucket_labels, _bucket_of

MULTS = (1.5, 3.0, 5.0)


def test_bucket_labels_cover_ladder():
    labels = _bucket_labels(MULTS)
    # un gradino in piu' delle soglie: sotto il primo, gli intervalli, e la coda
    assert len(labels) == len(MULTS) + 1
    assert labels[0].startswith("< 1.5R")
    assert labels[-1].startswith(">= 5R")


def test_bucket_boundaries_are_inclusive_below():
    # il gradino si riempie QUANDO il prezzo lo tocca: mfe == soglia -> fascia sopra
    assert _bucket_of(1.49, MULTS) == 0
    assert _bucket_of(1.5, MULTS) == 1
    assert _bucket_of(2.99, MULTS) == 1
    assert _bucket_of(3.0, MULTS) == 2
    assert _bucket_of(5.0, MULTS) == 3
    assert _bucket_of(12.0, MULTS) == 3


def test_bucket_of_handles_zero_and_negative_mfe():
    # un trade andato subito contro ha mfe 0 (o negativo per arrotondamenti):
    # deve finire nella fascia "nessun gradino", non fuori dall'array
    assert _bucket_of(0.0, MULTS) == 0
    assert _bucket_of(-0.3, MULTS) == 0


def test_bucket_of_with_single_rung_ladder():
    # scala degenere a un solo gradino: due fasce, nessun IndexError
    assert _bucket_of(0.5, (2.0,)) == 0
    assert _bucket_of(2.0, (2.0,)) == 1
    assert len(_bucket_labels((2.0,))) == 2
