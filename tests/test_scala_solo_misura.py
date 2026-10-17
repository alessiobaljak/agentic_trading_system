"""La colonna 0,8/1,6/2,4 nella tabella «R medi incassati per scala» (4 ott 2026,
domanda del proprietario): e' SOLO una misura. Il gate non la prova (non sta fra
le candidate), il bot non la opera; il modello semplificato la calcola come le
altre."""
from bot.execution.exit_logic import SCALE_LADDER_CANDIDATES
from scripts import mfe_report as m


def test_la_scala_e_solo_misura_e_non_una_candidata_del_gate():
    assert (0.8, 1.6, 2.4) in m.SCALE_SOLO_MISURA
    assert all(c not in SCALE_LADDER_CANDIDATES for c in m.SCALE_SOLO_MISURA)


def test_banked_r_sulla_scala_stretta():
    fracs = (0.3, 0.3, 0.4)
    # un «quasi» da 0,81R (SYRUP del 4 ott): con 0,8 incassa il primo gradino,
    # con 1/1.5/2.5 e' una perdita piena
    assert m.banked_r(0.81, (0.8, 1.6, 2.4), fracs) == 0.8 * 0.3
    assert m.banked_r(0.81, (1.0, 1.5, 2.5), fracs) == -1.0
    assert m.banked_r(0.5, (0.8, 1.6, 2.4), fracs) == -1.0
