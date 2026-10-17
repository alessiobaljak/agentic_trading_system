"""Il giro COMPLETO del gate deve girare una volta al giorno anche se il timer
deriva (26 set 2026): per giorni la discovery e' partita alle 03:30-03:48 UTC,
fuori dalla finestra 00-02:59, e il giro completo (intorno, varianti, tutte le
spec) non e' mai partito."""
import time

from scripts import discover_strategies as d


def _t(h):
    # un istante alle `h` UTC di un giorno qualunque
    return 1_758_844_800.0 + h * 3600  # 2026-09-26 00:00 UTC + h


def test_prima_delle_tre_e_completo_comunque():
    assert d.giro_giornaliero(_t(1), ultimo_completo_at=_t(0))


def test_alle_tre_e_quaranta_non_e_completo_se_l_ultimo_e_recente():
    assert not d.giro_giornaliero(_t(3.8), ultimo_completo_at=_t(-2))   # 5,8 h fa


def test_alle_tre_e_quaranta_e_completo_se_l_ultimo_e_di_ieri():
    assert d.giro_giornaliero(_t(3.8), ultimo_completo_at=_t(3.8) - 21 * 3600)


def test_di_giorno_non_e_completo_anche_se_l_ultimo_e_di_ieri():
    # 26 set: il completo partito alle 09:04 UTC ha superato le 3 ore di giorno.
    # Fra le 8 e le 24 UTC si aspetta la notte, salvo oltre 30 ore dall'ultimo.
    assert not d.giro_giornaliero(_t(9), ultimo_completo_at=_t(9) - 21 * 3600)
    assert d.giro_giornaliero(_t(9), ultimo_completo_at=_t(9) - 31 * 3600)
    assert d.giro_giornaliero(_t(7.5), ultimo_completo_at=_t(7.5) - 21 * 3600)


def test_senza_memoria_di_un_giro_completo_e_completo():
    assert d.giro_giornaliero(_t(15), ultimo_completo_at=None)


def test_l_istante_si_legge_dal_documento_del_giro():
    class FB:
        def __init__(self, doc): self.doc = doc
        def get_doc(self, c, k): return self.doc
    assert d.ultimo_giro_completo_at(FB({"completa_at": 123.0})) == 123.0
    assert d.ultimo_giro_completo_at(FB({})) is None
    class Rotto:
        def get_doc(self, c, k): raise RuntimeError("giu'")
    assert d.ultimo_giro_completo_at(Rotto()) is None


def test_il_main_usa_la_regola_e_scrive_completa_at():
    import inspect
    src = inspect.getsource(d.main)
    assert "ultimo_giro_completo_at(fb)" in src
    assert "giro_giornaliero(_ora, _ultimo_completo)" in src
    assert '"completa_at": (time.time() if (_completa and not args.symbols)' in src
