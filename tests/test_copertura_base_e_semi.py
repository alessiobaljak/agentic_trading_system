"""COPERTURA: via le strategie base dal giro, piu' semi sulle coin scoperte.

21 set 2026, dal comando `gate`: 56 coppie validate su 26 coin, universo 165,
copertura 15,8% contro un obiettivo del 35%. Le 8 strategie scritte a mano
avevano 0 validate su 1312 valutazioni e occupavano il 61% delle coppie vive e
una fetta di un giro che dura 2h22 su 3h. I semi di mutazione (con precedenza
alle coin NON coperte) erano 10 su ~100 candidate.
"""
import inspect

from scripts import discover_strategies as d
from scripts import optimize as o


def test_le_base_si_saltano_per_default_ma_si_possono_riaccendere():
    """Default nel CODICE, non solo nella unit: il timer sulla VPS non va toccato."""
    src = inspect.getsource(o)
    assert 'os.getenv("OPTIMIZER_SKIP_BASE", "true")' in src


def test_saltare_le_base_non_salta_la_manutenzione_del_registro():
    """La pulizia delle stantie, il purge e la timeline vivono in update_registry:
    saltando la valutazione si deve chiamarla lo stesso, altrimenti le coppie base
    restano nel registro per sempre e la timeline si ferma."""
    src = inspect.getsource(o.main)
    i = src.index("if SKIP_BASE and not args.reset_registry:")
    blocco = src[i:i + 900]
    assert "update_registry(fb, out, summary_passed)" in blocco
    assert "return 0" in blocco
    # e viene PRIMA della valutazione parallela
    assert i < src.index("parallel_map(")


def test_un_reset_esplicito_non_viene_saltato():
    src = inspect.getsource(o.main)
    assert "if SKIP_BASE and not args.reset_registry:" in src


def test_i_semi_sono_trenta_e_vengono_da_una_manopola():
    assert d.SEEDS == 30
    assert 'os.getenv("DISCOVERY_SEEDS", "30")' in inspect.getsource(d)
    src = inspect.getsource(d.main)
    assert "bases[:SEEDS]" in src and "bases[:10]" not in src


def test_i_semi_danno_ancora_precedenza_alle_coin_non_coperte():
    """Alzare il numero non serve se l'ordine non mette prima le coin scoperte:
    la copertura crescerebbe dove c'e' gia'."""
    src = inspect.getsource(d.mutation_seeds)
    assert "estendono[:limit] + resto[" in src
