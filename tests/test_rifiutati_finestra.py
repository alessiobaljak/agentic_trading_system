"""LA FINESTRA DELL'OMBRA DEI RIFIUTATI (28 set 2026).

`valuta_pendenti` leggeva a ogni candela tutti i documenti di ~17 giorni
(finestra dimensionata sul 4h + un giorno per qualunque segnale): ~5.300
letture al giorno il 28 set, ~24.000 una settimana dopo, per valutarne una
manciata. Qui si verifica che la finestra sia (orizzonte + margine + 2) barre
del timeframe PIU' LUNGO fra quelli dei segnali (15m: 106 barre, ~26 h; 1h:
~106 h), che le letture per giro abbiano un tetto, che i timeframe visti fra
i pendenti allarghino la finestra, e che la passata giornaliera
`chiudi_scaduti` segni «scaduto» chi e' in attesa da piu' di 5 giorni
leggendo solo la fetta fra il 5° e l'8° giorno.
"""
from __future__ import annotations

import inspect

from bot.config import settings
from bot.core.firebase_client import FirebaseClient
from bot.learning import rifiutati
from tests.test_rifiutati_ombra import T0, TF, _piatte, _registra


def _fb() -> FirebaseClient:
    return FirebaseClient()


def test_finestra_per_timeframe():
    rifiutati._TF_VISTI.clear()
    assert settings.ORCHESTRATOR_TIMEFRAME == "15m"
    assert rifiutati._finestra_pendenti_s(96, 8) == 106 * 900             # ~26,5 ore
    assert rifiutati._finestra_pendenti_s(96, 8, timeframes={"1h"}) == 106 * 3600
    assert rifiutati._finestra_pendenti_s(96, 8, timeframes={"5m", "1h"}) == 106 * 3600
    assert rifiutati._finestra_pendenti_s(96, 8, timeframes={"5m"}) == 106 * 900   # mai sotto il bot
    assert rifiutati._finestra_pendenti_s(96, 8) < 2 * 86400                # non piu' i 17 giorni


def test_i_timeframe_visti_fra_i_pendenti_allargano_la_finestra(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    rifiutati._TF_VISTI.clear()
    fb = _fb()
    _registra(fb, symbol="AUSDT", timeframe="1h", now=T0 + 30)
    assert rifiutati._finestra_pendenti_s(96, 8) == 106 * 900
    rifiutati.valuta_pendenti(fb, lambda s, tf, l: [], T0 + 3600)
    assert "1h" in rifiutati._TF_VISTI
    assert rifiutati._finestra_pendenti_s(96, 8) == 106 * 3600
    rifiutati._TF_VISTI.clear()


def test_la_query_ha_la_finestra_il_tetto_e_l_etichetta(monkeypatch):
    rifiutati._TF_VISTI.clear()
    visto = {}

    class _Fb:
        def letture(self): return {}
        def query_collection(self, coll, **kw):
            visto.update(kw); visto["coll"] = coll
            return []
    now = T0 + 50 * TF
    assert rifiutati.valuta_pendenti(_Fb(), lambda *a: [], now) == 0
    assert visto["coll"] == rifiutati.COLLECTION and visto["chi"] == "rifiutati"
    assert visto["limit"] == rifiutati.MAX_LETTURE_GIRO == 200
    assert visto["min_value"] == now - 106 * 900
    rifiutati.valuta_pendenti(_Fb(), lambda *a: [], now, max_letture=7, timeframes={"1h"})
    assert visto["limit"] == 7 and visto["min_value"] == now - 106 * 3600
    # le letture si contano sotto «rifiutati» (client vero)
    fb = _fb()
    _registra(fb, now=T0 + 30)
    rifiutati.valuta_pendenti(fb, lambda *a: [], T0 + TF)
    assert {r["chi"] for r in fb.letture()["per_chiamante"]} == {"rifiutati"}


def test_un_segnale_fuori_finestra_resta_in_attesa_finche_la_passata_lo_chiude(monkeypatch):
    """Un pendente piu' vecchio della finestra non viene piu' letto dal giro
    (era il costo), e non resta in attesa per sempre: lo chiude `chiudi_scaduti`."""
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    rifiutati._TF_VISTI.clear()
    fb = _fb()
    vecchio = _registra(fb, symbol="AUSDT", now=T0 + 30)
    now = T0 + 6 * 86400                                           # sei giorni dopo
    chiamate = []
    rifiutati.valuta_pendenti(fb, lambda s, tf, l: chiamate.append(s) or [], now)
    assert chiamate == [] and fb.get_doc(rifiutati.COLLECTION, vecchio)["stato"] == "in_attesa"
    assert rifiutati.chiudi_scaduti(fb, now) == 1
    d = fb.get_doc(rifiutati.COLLECTION, vecchio)
    assert d["stato"] == "scaduto" and d["valutato_at"] == now and d["scaduto_da"] == "passata_giornaliera"


def test_chiudi_scaduti_legge_solo_la_fetta_dal_quinto_all_ottavo_giorno(capsys):
    rifiutati._TF_VISTI.clear()
    fb = _fb()
    now = T0 + 20 * 86400
    g = 86400
    recente = _registra(fb, symbol="RUSDT", now=now - 2 * g)          # 2 giorni: non tocca
    sei = _registra(fb, symbol="SUSDT", now=now - 6 * g)              # 6 giorni: scade
    sette = _registra(fb, symbol="TUSDT", now=now - 7 * g - 3600)     # 7 giorni e un'ora: scade
    dieci = _registra(fb, symbol="DUSDT", now=now - 10 * g)           # 10 giorni: fuori dalla fetta
    valutato = _registra(fb, symbol="VUSDT", now=now - 6 * g)
    doc = fb.get_doc(rifiutati.COLLECTION, valutato)
    doc.update({"stato": "valutato", "esito": "tp"})
    fb.set_doc(rifiutati.COLLECTION, valutato, doc)
    prima = fb.letture()["totale"]
    assert rifiutati.chiudi_scaduti(fb, now) == 2
    assert fb.letture()["totale"] - prima == 3                         # sei, sette, valutato: la fetta
    stati = {k: fb.get_doc(rifiutati.COLLECTION, v)["stato"]
             for k, v in {"recente": recente, "sei": sei, "sette": sette, "dieci": dieci,
                          "valutato": valutato}.items()}
    assert stati == {"recente": "in_attesa", "sei": "scaduto", "sette": "scaduto",
                     "dieci": "in_attesa", "valutato": "valutato"}
    assert "2 segnali in attesa da piu' di 5 giorni segnati scaduti" in capsys.readouterr().out
    # il riassunto li conta fra gli scaduti, non fra i pendenti
    r = rifiutati.riassunto(fb, giorni=30, now=now)["per_motivo"]["cooldown"]
    assert r["scaduti"] == 2 and r["in_attesa"] == 2 and r["valutati"] == 1
    # una seconda passata lo stesso giorno non ha niente da fare
    assert rifiutati.chiudi_scaduti(fb, now) == 0


def test_chiudi_scaduti_fail_open(capsys):
    class _Rotto:
        def query_collection(self, *a, **k): raise RuntimeError("giu'")
    assert rifiutati.chiudi_scaduti(_Rotto(), T0) == 0
    assert "passata degli scaduti saltata" in capsys.readouterr().out
    assert rifiutati.SCADENZA_S == 5 * 86400


def test_il_bot_chiama_la_passata_una_volta_al_giorno_e_passa_i_timeframe():
    from bot.main import TradingBot
    man = inspect.getsource(TradingBot._manutenzione_oraria)
    assert 'now - getattr(self, "_scaduti_at", 0.0) >= 86400' in man
    assert "rifiutati.chiudi_scaduti(self.fb, now)" in man
    run = inspect.getsource(TradingBot.run)
    assert "timeframes=self._timeframes_in_uso()" in run
    tf = inspect.getsource(TradingBot._timeframes_in_uso)
    assert "_generated_specs" in tf and "_esplorative_specs" in tf


def test_timeframes_in_uso_dalle_spec_in_ram():
    import types
    from bot.main import TradingBot
    b = types.SimpleNamespace(adaptation=types.SimpleNamespace(
        _generated_specs={"gen_a": {"timeframe": "1h"}, "gen_b": {"timeframe": None}, "gen_c": "rotta"},
        _esplorative_specs={"gen_d": {"timeframe": "15m"}}))
    assert TradingBot._timeframes_in_uso(b) == {"1h", "15m"}
    assert TradingBot._timeframes_in_uso(types.SimpleNamespace(adaptation=None)) == set()
