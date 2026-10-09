"""Test delle regole della versione 4.5 che vivono nel codice: la soglia del trasferimento (Passo 6)."""
import pytest
from scipy.stats import binom

from research.src.statistica import monete_richieste_trasferimento


def test_la_soglia_cresce_con_le_monete():
    k80 = monete_richieste_trasferimento(80, 0.02)
    k150 = monete_richieste_trasferimento(150, 0.02)
    k300 = monete_richieste_trasferimento(300, 0.02)
    assert 2 <= k80 <= k150 <= k300
    assert k300 > k80


def test_il_numero_e_il_piu_piccolo_sotto_il_livello():
    for n, p in [(80, 0.01), (80, 0.02), (150, 0.03), (40, 0.05)]:
        k = monete_richieste_trasferimento(n, p)
        assert binom.sf(k - 1, n, p) < 0.05
        if k > 2:
            assert binom.sf(k - 2, n, p) >= 0.05


def test_mai_sotto_il_minimo_e_non_si_sa_con_poche_monete():
    assert monete_richieste_trasferimento(5, 0.001) == 2
    assert monete_richieste_trasferimento(2, 0.5) == 3  # neanche 2 su 2 basta: «non si sa»
    assert monete_richieste_trasferimento(0, 0.02) == 1


def test_valori_non_validi():
    with pytest.raises(ValueError):
        monete_richieste_trasferimento(10, 1.5)
    with pytest.raises(ValueError):
        monete_richieste_trasferimento(10, 0.02, livello=0)
