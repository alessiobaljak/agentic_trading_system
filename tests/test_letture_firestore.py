"""IL CONTATORE DELLE LETTURE FIRESTORE (28 set 2026).

Il 28 settembre alle 06:18 UTC la quota gratuita di Firestore (50.000 letture
al giorno) si e' esaurita (ops 0331/0332: «429 Quota exceeded»): 8k letture il
20 set, 39k il 26, quota finita il 28, e nessuno le contava. Qui si verifica
che il client le conti (get_doc = 1, query = i documenti tornati, almeno 1,
il RTDB no), con l'etichetta del chiamante (`chi=` o il nome della funzione),
che l'anello tenga le ultime 24 ore, che il bot stampi la riga ogni ora, che
il controllo la pubblichi e che l'anomalia `LETTURE_FIRESTORE` scatti alle
soglie dichiarate (giallo 25.000, rosso 40.000).
"""
from __future__ import annotations

import inspect
import time

from bot.core import firebase_client as fc
from bot.core.firebase_client import FirebaseClient, kw_chi, riga_letture
from bot.learning import controllo as c
from tests.test_controllo import NOW, _doc, _fb


def _leggi_tre(fb):
    """Tre letture da una funzione con un nome riconoscibile (etichetta inferita)."""
    fb.get_doc("a", "1")
    fb.get_doc("a", "2")
    return fb.query_collection("a")


# --------------------------------------------------------------------------- #
# 1. il conteggio                                                             #
# --------------------------------------------------------------------------- #
def test_get_doc_vale_uno_e_la_query_vale_i_documenti_tornati_minimo_uno():
    fb = FirebaseClient()
    assert fb.letture() == {"totale": 0, "ultime_24h": 0, "per_chiamante": []}
    fb.get_doc("x", "manca", chi="prova")                     # anche un doc assente costa 1
    assert fb.letture()["totale"] == 1
    for i in range(5):
        fb.set_doc("trades", f"t{i}", {"trade_id": f"t{i}", "exit_ts": float(i)})
    assert len(fb.query_collection("trades", order_by="exit_ts", chi="prova")) == 5
    assert fb.letture()["totale"] == 6
    assert fb.query_collection("vuota", chi="prova") == []
    assert fb.letture()["totale"] == 7                        # query vuota: 1 lettura
    assert fb.query_collection("trades", order_by="exit_ts", limit=2, chi="prova")
    assert fb.letture()["totale"] == 9
    assert fb.count_collection("trades", chi="prova") == 5
    assert fb.get_doc_field("trades", "t1", ["exit_ts"], chi="prova") == {"exit_ts": 1.0}
    assert fb.get_doc_field("trades", "manca", ["exit_ts"], chi="prova") is None
    assert fb.list_doc_ids("trades", chi="prova") and fb.letture()["totale"] == 17
    # le scritture e il Realtime DB NON contano
    fb.set_rtdb("/bot_status/heartbeat", 1.0)
    assert fb.get_rtdb("/bot_status/heartbeat") == 1.0
    fb.set_doc("x", "y", {"a": 1})
    assert fb.letture()["totale"] == 17
    assert fb.letture()["per_chiamante"] == [{"chi": "prova", "n": 17}]


def test_query_con_max_value_filtra_lato_server_e_in_memoria():
    fb = FirebaseClient()
    for i in range(10):
        fb.set_doc("segnali_rifiutati", f"s{i}", {"id": f"s{i}", "ts": float(i * 100)})
    docs = fb.query_collection("segnali_rifiutati", order_by="ts", min_value=200.0,
                               max_value=500.0, chi="prova")
    assert [d["id"] for d in docs] == ["s5", "s4", "s3", "s2"]      # decrescente, estremi compresi


def test_etichetta_esplicita_o_nome_della_funzione_chiamante():
    fb = FirebaseClient()
    _leggi_tre(fb)
    fb.get_doc("b", "1", chi="registro")
    fb.get_doc("b", "2", chi="registro")
    per = {r["chi"]: r["n"] for r in fb.letture()["per_chiamante"]}
    assert per == {"_leggi_tre": 3, "registro": 2}
    # kw_chi: l'etichetta va solo ai client che contano; un finto senza `letture`
    # riceve un dict vuoto e la sua `get_doc(coll, id)` non si rompe
    assert kw_chi(fb, "x") == {"chi": "x"}
    assert kw_chi(object(), "x") == {}


def test_l_anello_tiene_le_ultime_24_ore_e_il_top_8():
    cont = fc.ContatoreLetture()
    t0 = 1_790_000_000.0                       # un'ora tonda qualunque
    cont.conta(100, "vecchio", now=t0 - 30 * 3600)    # 30 ore fa: fuori dalle 24 h
    cont.conta(7, "limite", now=t0 - 23 * 3600)       # 23 ore fa: dentro
    for i in range(10):
        cont.conta(i + 1, f"c{i}", now=t0 - i * 600)
    r = cont.riepilogo(now=t0)
    assert r["totale"] == 100 + 7 + 55
    assert r["ultime_24h"] == 7 + 55
    assert len(r["per_chiamante"]) == 8                        # top 8, i piu' grandi prima
    assert r["per_chiamante"][0] == {"chi": "c9", "n": 10}
    assert {x["chi"] for x in r["per_chiamante"]} == {"c9", "c8", "c7", "c6", "c5", "c4", "limite", "c3"}
    # 24 ore dopo l'anello si e' svuotato ma il totale resta
    r2 = cont.riepilogo(now=t0 + 25 * 3600)
    assert r2["ultime_24h"] == 0 and r2["totale"] == 162


def test_la_riga_di_log_oraria():
    r = {"totale": 5000, "ultime_24h": 4321,
         "per_chiamante": [{"chi": "registro", "n": 1440}, {"chi": "trade", "n": 300}]}
    assert riga_letture(r) == ("[firebase] letture ultime 24 h: 4321 (registro 1440 · trade 300) "
                               "— quota gratuita 50000/giorno")
    assert riga_letture({"ultime_24h": 0, "per_chiamante": []}).startswith("[firebase] letture ultime 24 h: 0 —")


# --------------------------------------------------------------------------- #
# 2. il bot: stampa oraria (sul sorgente) e chiamanti etichettati              #
# --------------------------------------------------------------------------- #
def test_il_bot_stampa_il_contatore_nel_ramo_orario():
    from bot.main import TradingBot
    run = inspect.getsource(TradingBot.run)
    blocco = run[run.index("if now - self.last_orario >= 3600:"):run.index("self.last_orario = now")]
    assert "self._manutenzione_oraria(now)" in blocco
    # la manutenzione viene PRIMA del controllo orario (la verifica della cache
    # dev'essere gia' fatta quando il controllo la pubblica)
    assert blocco.index("self._manutenzione_oraria(now)") < blocco.index("self.refresh_weights(now, orario=True)")
    man = inspect.getsource(TradingBot._manutenzione_oraria)
    assert "print(riga_letture(self.fb.letture(now)))" in man
    assert "self.logger.manutenzione(now)" in man
    assert "rifiutati.chiudi_scaduti(self.fb, now)" in man


def test_i_chiamanti_principali_portano_la_loro_etichetta():
    """Le letture del bot si leggono per famiglia nel riepilogo: registro, pesi,
    trade, controllo, rifiutati (sul sorgente, come tests/test_referti.py)."""
    from bot.learning import adaptation, rifiutati, trade_logger
    src_ad = inspect.getsource(adaptation.AdaptationEngine)
    assert src_ad.count('kw_chi(self.fb, "registro")') >= 6
    assert 'campo("strategy_registry", "validated", ["updated_at"], **kw_chi(self.fb, "registro"))' in src_ad
    assert 'kw_chi(self.fb, CHI)' in inspect.getsource(trade_logger.TradeLogger) and trade_logger.CHI == "trade"
    assert rifiutati.CHI == "rifiutati" and 'kw_chi(fb, CHI)' in inspect.getsource(rifiutati.valuta_pendenti)
    assert 'kw_chi(fb, "controllo")' in inspect.getsource(c.carica_dati)
    # il registro non passa piu' dal client interno `_fs`: usa get_doc_field
    assert 'getattr(self.fb, "_fs"' not in inspect.getsource(adaptation.AdaptationEngine.registro_cambiato)


def test_registro_cambiato_legge_un_solo_campo_e_conta_una_lettura():
    from bot.learning.adaptation import AdaptationEngine
    fb = FirebaseClient()
    fb.set_doc("strategy_registry", "validated", {"updated_at": 10.0, "validated": [], "pairs": "{}"})
    ad = AdaptationEngine(fb)
    prima = fb.letture()["totale"]
    assert ad.registro_cambiato() is False
    fb.set_doc("strategy_registry", "validated", {"updated_at": 11.0, "validated": [], "pairs": "{}"})
    assert ad.registro_cambiato() is True
    assert fb.letture()["totale"] == prima + 2
    assert {r["chi"] for r in fb.letture()["per_chiamante"]} >= {"registro"}


# --------------------------------------------------------------------------- #
# 3. il controllo: campi, anomalia, stampa                                    #
# --------------------------------------------------------------------------- #
def test_il_controllo_pubblica_le_letture_solo_dal_bot():
    fb = _fb()
    doc = _doc(fb)
    s = doc["salute"]
    assert isinstance(s["letture_firestore_24h"], int) and s["letture_firestore_24h"] > 0
    assert s["letture_per_chiamante"] and {"chi", "n"} == set(s["letture_per_chiamante"][0])
    assert any(r["chi"] == "controllo" for r in s["letture_per_chiamante"])
    assert s["cache_trade"] is None                            # non passata: null, non zero
    # da ops sarebbero le letture di un processo appena nato: null
    ops = _doc(fb, generato_da="ops")["salute"]
    assert ops["letture_firestore_24h"] is None and ops["letture_per_chiamante"] is None


def test_anomalia_letture_firestore_alle_soglie():
    def _con(letture):
        s = {"letture_firestore_24h": letture, "heartbeat_eta_s": 10, "posizioni_aperte": 0}
        lista = c.anomalie(s, {}, {}, {}, NOW)
        return {a["codice"]: a for a in lista}.get("LETTURE_FIRESTORE")
    assert _con(None) is None and _con(24_999) is None and _con(25_000) is None
    g = _con(25_001)
    assert g["gravita"] == "giallo" and g["famiglia"] == "sistema" and g["soglia"] == 25_000
    assert g["testo"] == ("letture Firestore nelle ultime 24 h: 25.001 (quota gratuita 50.000): "
                          "valutare il piano a consumo (Blaze) se resta sopra")
    r = _con(40_001)
    assert r["gravita"] == "rosso" and r["soglia"] == 40_000 and r["valore"] == 40_001
    assert c.LETTURE_GIALLO == 25_000 and c.LETTURE_ROSSO == 40_000 and fc.QUOTA_LETTURE_GIORNO == 50_000


def test_anomalia_cache_trade_disallineata_e_info():
    s = {"heartbeat_eta_s": 10, "posizioni_aperte": 0,
         "cache_trade": {"firestore": 150, "cache": 148, "allineata": False, "verificata_at": NOW}}
    lista = {a["codice"]: a for a in c.anomalie(s, {}, {}, {}, NOW)}
    a = lista["CACHE_TRADE_DISALLINEATA"]
    assert a["gravita"] == "info" and a["famiglia"] == "sistema"
    assert "150" in a["testo"] and "148" in a["testo"] and "ricaricata" in a["testo"]
    assert c.semaforo(list(lista.values()), "sistema") == "verde"      # le info non colorano
    s["cache_trade"]["allineata"] = True
    assert "CACHE_TRADE_DISALLINEATA" not in {a["codice"] for a in c.anomalie(s, {}, {}, {}, NOW)}


def test_scripts_controllo_stampa_le_letture(capsys):
    from scripts.controllo import stampa
    doc = _doc(_fb())
    doc["salute"]["letture_firestore_24h"] = 12345
    doc["salute"]["letture_per_chiamante"] = [{"chi": "registro", "n": 1440}, {"chi": "trade", "n": 200}]
    doc["salute"]["cache_trade"] = {"firestore": 54, "cache": 54, "allineata": True, "verificata_at": NOW}
    stampa(doc)
    out = capsys.readouterr().out
    assert "LETTURE FIRESTORE DEL BOT (ultime 24 h, quota gratuita 50.000/giorno):" in out
    assert "  12345 (registro 1440 · trade 200)" in out
    assert "cache trade: 54 in memoria contro 54 su Firestore (allineata" in out
    doc["salute"]["letture_firestore_24h"] = None
    stampa(doc)
    assert "non misurate in questo documento" in capsys.readouterr().out


def test_il_contatore_regge_i_thread():
    cont = fc.ContatoreLetture()
    import threading
    def _batti():
        for _ in range(500):
            cont.conta(1, "t", now=time.time())
    th = [threading.Thread(target=_batti) for _ in range(4)]
    for t in th:
        t.start()
    for t in th:
        t.join()
    assert cont.riepilogo()["totale"] == 2000
