"""LA RIVALUTAZIONE COMPLETA UNA VOLTA AL GIORNO — dove vanno le 2h29 di un giro.

23 set 2026, misurato: 2h29 a giro, di cui il 77% e' rivalutare ~430 spec note su
200 coin. Ma una conferma o un fallimento contano SOLO alla chiusura della
finestra dei 7 giorni, che si chiude a mezzanotte UTC: sette giri su otto
rifanno un conto che non puo' cambiare nulla. Queste sono le proprieta' che
rendono il risparmio sicuro — e la piu' importante e' che una terza conferma
NON aspetti un giorno.
"""
import time

from scripts import discover_strategies as d

SETTE_GIORNI = 7 * 86400


def _reg(pairs):
    return {"pairs": pairs}


def test_nel_giro_giornaliero_si_rivaluta_tutto_come_prima():
    existing = {"gen_a": {"id": "gen_a"}, "gen_b": {"id": "gen_b"}}
    reg = _reg({"X|gen_a": {"generated": True, "pass_count": 0}})
    scelte, diag = d.specs_da_rivalutare(existing, reg, cap=500, completa=True)
    assert [s["id"] for s in scelte] == ["gen_a", "gen_b"]
    assert diag["reeval_modalita"] == "completa"


def test_negli_altri_giri_solo_chi_puo_cambiare_stato_adesso():
    """Una coppia con una conferma e la finestra in chiusura (o scaduta) si
    rivaluta ogni giro: la terza conferma resta a tre ore di distanza. Una con
    la finestra aperta da due giorni no: il suo verdetto non puo' arrivare oggi."""
    now = time.time()
    existing = {"gen_scade": {"id": "gen_scade"}, "gen_aperta": {"id": "gen_aperta"},
                "gen_zero": {"id": "gen_zero"}}
    reg = _reg({
        "X|gen_scade": {"generated": True, "pass_count": 2, "window_start": now - SETTE_GIORNI + 3600},
        "X|gen_aperta": {"generated": True, "pass_count": 2, "window_start": now - 2 * 86400},
        "X|gen_zero": {"generated": True, "pass_count": 0, "window_start": now - SETTE_GIORNI},
    })
    scelte, diag = d.specs_da_rivalutare(existing, reg, cap=500, completa=False, now=now)
    assert [s["id"] for s in scelte] == ["gen_scade"]
    assert diag["reeval_modalita"] == "solo urgenti"


def test_una_finestra_gia_scaduta_e_urgente_finche_non_ripassa():
    now = time.time()
    reg = {"X|gen_v": {"generated": True, "pass_count": 2, "window_start": now - 10 * 86400}}
    assert d.spec_urgenti(reg, now) == {"gen_v"}


def test_il_giro_giornaliero_e_il_primo_dopo_mezzanotte_utc():
    from datetime import datetime, timezone

    assert d.giro_giornaliero(datetime(2026, 9, 23, 0, 12, tzinfo=timezone.utc).timestamp())
    assert d.giro_giornaliero(datetime(2026, 9, 23, 2, 50, tzinfo=timezone.utc).timestamp())
    assert not d.giro_giornaliero(datetime(2026, 9, 23, 3, 5, tzinfo=timezone.utc).timestamp())
    assert not d.giro_giornaliero(datetime(2026, 9, 23, 23, 0, tzinfo=timezone.utc).timestamp())


def test_le_candidate_nuove_non_sono_toccate_e_la_passata_mirata_resta_completa():
    """La scoperta non rallenta (nuove e semi ogni giro), e una passata con
    --symbols (conferme mirate, passata a 1h) rivaluta sempre tutto: la' le
    spec sono poche e il tempo non e' il problema."""
    import inspect

    src = inspect.getsource(d.main)
    assert "or bool(args.symbols)" in src
    assert "completa=_completa, now=_ora" in src
    assert d.REEVAL_DAILY is True and d.REEVAL_HOUR_MAX == 3
