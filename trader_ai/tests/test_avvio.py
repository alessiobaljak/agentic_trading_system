"""Test del programma (avvio.py) e del collegamento al conto demo (conto_demo.py) con un conto finto: nessuna rete."""
import hashlib
import hmac
from datetime import datetime, timedelta, timezone

import pytest

from trader_ai.avvio import Trader
from trader_ai.conto_demo import ContoDemo, _url, arrotonda, controlla_chiavi
from trader_ai.modello import Esito
from trader_ai.schema import Risposta

T0 = datetime(2026, 11, 24, 10, 1, tzinfo=timezone.utc)


class ContoFinto:
    simbolo = "BTCUSDT"

    def __init__(self):
        self.conto, self.disp, self.prezzo, self.pos = 1000.0, 1000.0, 90000.0, None
        self.condizionati, self.ordini, self.annullati = [], [], 0

    def saldo(self):
        return {"conto": self.conto, "disponibile": self.disp, "portafoglio": self.conto}

    def posizione(self):
        return self.pos

    def mercato(self):
        return {"prezzo": self.prezzo, "funding": 0.0001, "prossimo_funding_ms": 0, "interesse_aperto": 100.0}

    def candele(self, tf, ora_ms=None, n=200):
        passo = {"5m": 5, "15m": 15, "30m": 30}[tf]
        return [{"apertura": 90000.0, "massimo": 90100.0, "minimo": 89900.0, "chiusura": 90000.0 + i, "volume": 5.0,
                 "chiusa": T0 - timedelta(minutes=passo * (60 - i))} for i in range(60)]

    def filtri(self):
        return {"passo_prezzo": 0.1, "passo_quantita": 0.001, "quantita_min": 0.001, "valore_min": 100.0}

    def ordini_condizionati(self):
        return [{"algoId": i, "orderType": t} for i, (t, _) in enumerate(self.condizionati)]

    def prepara(self, leva):
        self.leva = leva

    def apri(self, lato, q, tipo="MARKET", prezzo=None):
        self.ordini.append((lato, q, tipo, prezzo))
        if tipo == "MARKET":
            self.pos = {"lato": lato, "quantita": q, "entrata": self.prezzo, "leva": self.leva, "liquidazione": None}
        return {"avgPrice": str(self.prezzo) if tipo == "MARKET" else "0"}

    def condizionato(self, lato, tipo, prezzo):
        self.condizionati.append((tipo, prezzo))
        return {"algoId": len(self.condizionati)}

    def annulla_condizionato(self, algo_id):
        self.condizionati = [c for i, c in enumerate(self.condizionati) if i != algo_id]

    def annulla_tutto(self):
        self.annullati += 1
        self.condizionati = []

    def chiudi(self, pos):
        self.annulla_tutto()
        self.pos = None


def risposta(azione="aspetta", **kw):
    base = dict(approccio="rottura", cambio_approccio=False, diario="vedo")
    base.update(kw)
    return Risposta(azione=azione, **base)


class Orologio:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


def trader(tmp_path, risposte):
    c = ContoFinto()
    chiamate = []

    def modello(system, utente):
        chiamate.append(utente)
        return Esito(risposte.pop(0) if risposte else risposta(), "ok", {"input_tokens": 5000, "output_tokens": 2000})
    o = Orologio(T0)
    return Trader(c, modello, tmp_path, o), c, chiamate, o


def test_apre_con_stop_e_obiettivo_sul_conto_poi_chiama_a_ogni_candela(tmp_path):
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000,
                                                    obiettivo_prezzo=92000)])
    tr.passo()
    assert len(chiamate) == 1 and c.pos["lato"] == "lungo"
    assert c.ordini[0][1] == pytest.approx(0.005)              # 100 x 5 / 90.000
    assert ("STOP_MARKET", 88000.0) in c.condizionati and ("TAKE_PROFIT_MARKET", 92000.0) in c.condizionati
    o.t = T0 + timedelta(minutes=5)
    tr.passo()
    assert len(chiamate) == 1                                   # stessa candela da 15 minuti
    o.t = T0 + timedelta(minutes=14)
    tr.passo()
    assert len(chiamate) == 2                                   # 10:15 passate


def test_chiusura_sullo_stop_scritta_in_memoria_e_chiamata_subito(tmp_path):
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000)])
    tr.passo()
    c.pos, c.prezzo, c.conto = None, 88000.0, 990.0             # lo stop è scattato sul conto
    o.t = T0 + timedelta(minutes=2)
    tr.passo()
    assert len(chiamate) == 2 and "operazione chiusa (stop)" in chiamate[1]
    st = tr.carica()
    assert st["operazioni"][-1]["come"] == "stop" and st["operazioni"][-1]["risultato"] == -10.0
    assert "-10.00" in chiamate[1]                              # il modello vede la sua operazione persa


def test_obiettivo_del_giorno_chiude_e_ferma_fino_a_mezzanotte(tmp_path):
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000)])
    tr.passo()
    c.conto = 1050.5
    o.t = T0 + timedelta(minutes=20)
    tr.passo()
    assert c.pos is None and len(chiamate) == 1
    o.t = T0 + timedelta(hours=5)
    tr.passo()
    assert len(chiamate) == 1                                   # fermo
    o.t = datetime(2026, 11, 25, 0, 0, 30, tzinfo=timezone.utc)
    tr.passo()
    assert len(chiamate) == 2                                   # giorno nuovo, riparte dal conto di mezzanotte
    assert (tmp_path / "resoconti" / "2026-11-24.md").exists()
    assert tr.carica()["conto_mezzanotte"] == 1050.5


def test_posizione_senza_stop_riceve_lo_stop(tmp_path):
    tr, c, chiamate, o = trader(tmp_path, [])
    c.pos = {"lato": "corto", "quantita": 0.01, "entrata": 90000.0, "leva": 10.0, "liquidazione": None}
    tr.passo()
    assert c.condizionati and c.condizionati[0][0] == "STOP_MARKET" and c.condizionati[0][1] == pytest.approx(98100.0)


def test_decisione_scartata_nessun_ordine_e_il_modello_lo_sa(tmp_path):
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=50, stop_prezzo=88000)])
    tr.passo()
    assert not c.ordini and "leva" in tr.carica()["ultimo_scarto"]
    o.t = T0 + timedelta(minutes=15)
    tr.passo()
    assert "SCARTATA" in chiamate[1]


def test_modifica_mette_il_nuovo_stop_prima_di_togliere_il_vecchio(tmp_path):
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000),
                                           risposta("modifica", stop_prezzo=89500)])
    tr.passo()
    o.t = T0 + timedelta(minutes=15)
    tr.passo()
    assert c.condizionati == [("STOP_MARKET", 89500.0)]


# --- conto_demo --------------------------------------------------------------------------------------------------------

def test_solo_il_conto_demo():
    assert _url("/fapi/v1/order").startswith("https://demo-fapi.binance.com/")
    with pytest.raises(ValueError):
        _url("@fapi.binance.com/fapi/v1/order")


def test_chiavi_mancanti_o_uguali_a_quelle_d_altri_rifiutate():
    with pytest.raises(SystemExit):
        controlla_chiavi({})
    with pytest.raises(SystemExit):
        controlla_chiavi({"TRADER_AI_DEMO_API_KEY": "a", "TRADER_AI_DEMO_API_SECRET": "b", "BINANCE_DEMO_API_KEY": "a"})
    assert controlla_chiavi({"TRADER_AI_DEMO_API_KEY": "a", "TRADER_AI_DEMO_API_SECRET": "b",
                             "BINANCE_DEMO_API_KEY": "x"}) == ("a", "b")


def test_firma_e_ordine_condizionato():
    visti = []

    class R:
        status_code, text = 200, "{}"

        def json(self):
            return {"algoId": 1}

    def http(metodo, url, headers, timeout):
        visti.append((metodo, url, headers))
        return R()
    c = ContoDemo("chiave", "segreto", "BTCUSDT", http)
    c.condizionato("lungo", "STOP_MARKET", 88000.0)
    metodo, url, headers = visti[0]
    assert metodo == "POST" and "/fapi/v1/algoOrder?" in url and headers["X-MBX-APIKEY"] == "chiave"
    q, firma = url.split("?", 1)[1].rsplit("&signature=", 1)
    assert firma == hmac.new(b"segreto", q.encode(), hashlib.sha256).hexdigest()
    for pezzo in ("algoType=CONDITIONAL", "side=SELL", "type=STOP_MARKET", "triggerPrice=88000", "closePosition=true"):
        assert pezzo in q


def test_arrotonda_per_difetto():
    assert arrotonda(0.0056789, 0.001) == 0.005
    assert arrotonda(88000.07, 0.1) == 88000.0
