"""Test del programma (avvio.py) e del collegamento al conto demo (conto_demo.py) con un conto finto che si comporta come Binance
dove serve (rifiuto di uno stop che scatterebbe subito, ordini d'altri, posizioni su altri simboli): nessuna rete."""
import hashlib
import hmac
from datetime import datetime, timedelta, timezone

import pytest

from trader_ai.avvio import Trader
from trader_ai.conto_demo import ContoDemo, LimiteBinance, _url, arrotonda, controlla_chiavi
from trader_ai.costi import TETTO_GIORNO_DOLLARI, Budget
from trader_ai.giro import decidi
from trader_ai.limiti import LEVA_MAX, OBIETTIVO_GIORNO_USDT, Conto
from trader_ai.modello import Esito
from trader_ai.schema import Risposta

T0 = datetime(2026, 11, 24, 10, 1, tzinfo=timezone.utc)


class ContoFinto:
    simbolo = "BTCUSDT"

    def __init__(self):
        self.conto, self.disp, self.prezzo, self.pos = 1000.0, 1000.0, 90000.0, None
        self.algo, self.normali, self.altri = [], [], []        # ordini condizionati, normali, posizioni d'altri simboli
        self.doppio, self.rifiuta_stop, self.prezzo_all_ordine = False, False, None
        self.ordini, self.chiusure = [], 0

    def saldo(self):
        return {"conto": self.conto, "disponibile": self.disp, "portafoglio": self.conto}

    def modo_doppio(self):
        return self.doppio

    def posizioni_tutte(self):
        mie = [{"simbolo": "BTCUSDT", **self.pos}] if self.pos else []
        return mie + self.altri

    def ordini_tutti(self):
        return [{**o, "_algo": False} for o in self.normali] + [{**o, "_algo": True} for o in self.algo]

    def mercato(self):
        p = self.prezzo
        if self.prezzo_all_ordine is not None and self.ordini == [] and getattr(self, "_letto", False):
            p = self.prezzo_all_ordine                          # il prezzo si muove mentre il modello pensa
        self._letto = True
        return {"prezzo": p, "funding": 0.0001, "prossimo_funding_ms": 0, "interesse_aperto": 100.0}

    def candele(self, tf, ora_ms=None, n=200):
        passo = {"5m": 5, "15m": 15, "30m": 30}[tf]
        return [{"apertura": 90000.0, "massimo": 90100.0, "minimo": 89900.0, "chiusura": 90000.0 + i, "volume": 5.0,
                 "chiusa": T0 - timedelta(minutes=passo * (60 - i))} for i in range(60)]

    def filtri(self):
        return {"passo_prezzo": 0.1, "passo_quantita": 0.001, "passo_quantita_limite": 0.001, "quantita_min": 0.001,
                "valore_min": 100.0}

    def prepara(self, leva):
        self.leva = leva

    def apri(self, lato, q, cid, tipo="MARKET", prezzo=None):
        self.ordini.append((lato, q, tipo, prezzo, cid))
        if tipo == "MARKET":
            self.pos = {"lato": lato, "quantita": q, "entrata": self.prezzo, "leva": self.leva, "liquidazione": None}
            return {"avgPrice": str(self.prezzo), "executedQty": str(q)}
        self.normali.append({"symbol": "BTCUSDT", "clientOrderId": cid})
        return {"avgPrice": "0"}

    def condizionato(self, lato, tipo, prezzo, cid):
        mark = self.mercato()["prezzo"]
        scatterebbe = (prezzo >= mark if lato == "lungo" else prezzo <= mark) if tipo == "STOP_MARKET" else False
        if self.rifiuta_stop or scatterebbe:
            raise RuntimeError('POST /fapi/v1/algoOrder: 400 {"code":-2021,"msg":"Order would immediately trigger."}')
        self.algo.append({"symbol": "BTCUSDT", "algoId": len(self.algo) + 100, "clientAlgoId": cid, "tipo": tipo,
                          "prezzo": prezzo})
        return {"algoId": len(self.algo) + 100}

    def annulla_condizionato(self, ordine):
        self.algo = [o for o in self.algo if o["algoId"] != ordine["algoId"]]

    def annulla_tutto(self):
        self.algo, self.normali = [], [o for o in self.normali if not str(o.get("clientOrderId", "")).startswith("tai")]

    def chiudi(self, pos, cid):
        if pos:
            self.chiusure += 1
            self.pos = None
        self.annulla_tutto()


def risposta(azione="aspetta", **kw):
    base = dict(approccio="rottura", cambio_approccio=False, diario="vedo")
    base.update(kw)
    return Risposta(azione=azione, **base)


class Orologio:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


def trader(tmp_path, risposte, c=None):
    c = c or ContoFinto()
    chiamate = []

    def modello(system, utente):
        chiamate.append(utente)
        return Esito(risposte.pop(0) if risposte else risposta(), "ok", {"input_tokens": 5000, "output_tokens": 2000})
    o = Orologio(T0)
    return Trader(c, modello, tmp_path, o), c, chiamate, o


def stop_sul_conto(c):
    return [o["prezzo"] for o in c.algo if o["tipo"] == "STOP_MARKET"]


APRI = dict(margine_usdt=100, leva=5, stop_prezzo=88000, obiettivo_prezzo=92000)


def test_apre_con_stop_e_obiettivo_sul_conto_poi_chiama_a_ogni_candela(tmp_path):
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", **APRI)])
    tr.passo()
    assert len(chiamate) == 1 and c.pos["lato"] == "lungo"
    assert c.ordini[0][1] == pytest.approx(0.005) and c.ordini[0][4].startswith("tai")
    assert stop_sul_conto(c) == [88000.0] and [x["prezzo"] for x in c.algo if x["tipo"] == "TAKE_PROFIT_MARKET"] == [92000.0]
    o.t = T0 + timedelta(minutes=5)
    tr.passo()
    assert len(chiamate) == 1
    o.t = T0 + timedelta(minutes=14)
    tr.passo()
    assert len(chiamate) == 2


def test_chiusura_sullo_stop_scritta_in_memoria_e_chiamata_subito(tmp_path):
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", **APRI)])
    tr.passo()
    c.pos, c.prezzo, c.conto, c.algo = None, 88000.0, 990.0, []
    o.t = T0 + timedelta(minutes=2)
    tr.passo()
    assert len(chiamate) == 2 and "operazione chiusa (stop)" in chiamate[1]
    st = tr.carica()
    assert st["operazioni"][-1]["come"] == "stop" and st["operazioni"][-1]["risultato"] == -10.0
    assert "-10.00" in chiamate[1]


def test_obiettivo_del_giorno_chiude_e_ferma_fino_a_mezzanotte(tmp_path):
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", **APRI)])
    tr.passo()
    c.conto = 1050.5
    o.t = T0 + timedelta(minutes=20)
    tr.passo()
    assert c.pos is None and len(chiamate) == 1
    assert tr.carica()["operazioni"][-1]["come"] == "obiettivo del giorno"
    o.t = T0 + timedelta(hours=5)
    tr.passo()
    assert len(chiamate) == 1
    o.t = datetime(2026, 11, 25, 0, 0, 30, tzinfo=timezone.utc)
    tr.passo()
    assert len(chiamate) == 2
    assert (tmp_path / "resoconti" / "2026-11-24.md").exists()
    assert tr.carica()["conto_mezzanotte"] == 1050.5


# --- problema 95: il conto deve essere solo del trader ----------------------------------------------------------------

@pytest.mark.parametrize("sporca", [
    lambda c: c.altri.append({"simbolo": "ETHUSDT", "lato": "lungo", "quantita": 1, "entrata": 3000, "leva": 5,
                              "liquidazione": None}),
    lambda c: c.normali.append({"symbol": "BTCUSDT", "clientOrderId": "web_123"}),
    lambda c: setattr(c, "pos", {"lato": "lungo", "quantita": 0.01, "entrata": 90000, "leva": 5, "liquidazione": None}),
    lambda c: setattr(c, "doppio", True),
])
def test_conto_non_solo_del_trader_fermo_senza_toccare_niente(tmp_path, sporca):
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", **APRI)])
    sporca(c)
    prima = (list(c.algo), list(c.normali), dict(c.pos) if c.pos else None)
    for i in range(3):
        o.t = T0 + timedelta(minutes=15 * i)
        tr.passo()
    assert not chiamate and not c.ordini and c.chiusure == 0
    assert (list(c.algo), list(c.normali), dict(c.pos) if c.pos else None) == prima
    assert "FERMO" in (tmp_path / "diario.jsonl").read_text()


# --- problema 96: mai una posizione senza stop ------------------------------------------------------------------------

def test_prezzo_mosso_mentre_il_modello_pensa_nessun_ordine(tmp_path):
    c = ContoFinto()
    c.prezzo_all_ordine = 87900.0                               # sotto lo stop proposto (88000)
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", **APRI)], c)
    tr.passo()
    assert not c.ordini and c.pos is None and "prezzo di adesso" in tr.carica()["ultimo_scarto"]


def test_stop_rifiutato_dopo_l_apertura_chiude_subito(tmp_path):
    c = ContoFinto()
    c.rifiuta_stop = True
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", **APRI)], c)
    tr.passo()
    assert c.pos is None and c.chiusure == 1
    assert tr.carica()["operazioni"][-1]["come"] == "chiusa: stop rifiutato da Binance"


def test_stop_sparito_con_prezzo_oltre_chiude_e_il_passo_continua(tmp_path):
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", **APRI)])
    tr.passo()
    c.algo, c.prezzo = [], 87000.0                              # lo stop non c'è più e il prezzo l'ha superato
    o.t = T0 + timedelta(minutes=1)
    tr.passo()
    assert c.pos is None and c.chiusure == 1 and len(chiamate) == 2   # chiamato subito dopo la chiusura


def test_stop_sparito_viene_rimesso(tmp_path):
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", **APRI)])
    tr.passo()
    c.algo = [x for x in c.algo if x["tipo"] != "STOP_MARKET"]
    o.t = T0 + timedelta(minutes=1)
    tr.passo()
    assert stop_sul_conto(c) == [88000.0] and c.pos is not None


def test_modifica_toglie_il_vecchio_e_mette_il_nuovo_stop(tmp_path):
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", **APRI), risposta("modifica", stop_prezzo=89500)])
    tr.passo()
    o.t = T0 + timedelta(minutes=15)
    tr.passo()
    assert stop_sul_conto(c) == [89500.0]


def test_modifica_con_stop_nuovo_rifiutato_chiude(tmp_path):
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", **APRI), risposta("modifica", stop_prezzo=89500)])
    tr.passo()
    c.rifiuta_stop = True
    o.t = T0 + timedelta(minutes=15)
    tr.passo()
    assert c.pos is None and c.chiusure == 1


# --- problema 102: ordini limite e risposte perse --------------------------------------------------------------------

def test_ordine_limite_in_attesa_poi_eseguito_riceve_lo_stop(tmp_path):
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", tipo_ordine="limite", prezzo_limite=89500, **APRI)])
    tr.passo()
    assert c.pos is None and not c.algo and tr.carica()["aperta"]["in_attesa"]
    c.normali = []
    c.pos = {"lato": "lungo", "quantita": 0.005, "entrata": 89500.0, "leva": 5, "liquidazione": None}
    o.t = T0 + timedelta(minutes=1)
    tr.passo()
    assert stop_sul_conto(c) == [88000.0]


def test_ordine_limite_sparito_libera_l_operazione(tmp_path):
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", tipo_ordine="limite", prezzo_limite=89500, **APRI)])
    tr.passo()
    c.normali = []
    o.t = T0 + timedelta(minutes=1)
    tr.passo()
    assert tr.carica()["aperta"] is None and not tr.carica()["operazioni"]


# --- conto esaurito, chiusura a mano ---------------------------------------------------------------------------------

def test_conto_esaurito_si_ferma_senza_chiamare(tmp_path):
    c = ContoFinto()
    c.conto = c.disp = 5.0
    tr, c, chiamate, o = trader(tmp_path, [], c)
    tr.passo()
    assert not chiamate and "ordine minimo" in (tmp_path / "diario.jsonl").read_text()


def test_chiudi_a_mano_e_riparti(tmp_path):
    tr, c, chiamate, o = trader(tmp_path, [risposta("apri_lungo", **APRI)])
    tr.passo()
    tr.chiudi_tutto_e_ferma()
    assert c.pos is None and not c.algo
    o.t = T0 + timedelta(minutes=30)
    tr.passo()
    assert len(chiamate) == 1
    tr.riparti()
    tr.passo()
    assert len(chiamate) == 2


# --- problema 97: tetto contato anche senza token --------------------------------------------------------------------

def test_chiamata_senza_token_dichiarati_conta_il_massimo(tmp_path):
    b = Budget(tmp_path / "s.json")
    conto = Conto(1000.0, 1000.0, 1000.0)
    decidi(T0, "t", b, conto, 90000.0, lambda: Esito(None, "fuori_schema"), 0.4)
    assert b.speso(T0) == pytest.approx(0.4)
    decidi(T0, "t", b, conto, 90000.0, lambda: Esito(None, "ok", {"input_tokens": 1000, "output_tokens": 100}), 0.4)
    assert b.speso(T0) == pytest.approx(0.4 + 0.006)


def test_valori_fissati_dal_proprietario():
    assert LEVA_MAX == 10 and OBIETTIVO_GIORNO_USDT == 50 and TETTO_GIORNO_DOLLARI == 5.0


# --- conto_demo ------------------------------------------------------------------------------------------------------

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


class _R:
    def __init__(self, codice=200, corpo=None, headers=None):
        self.status_code, self._c, self.headers = codice, corpo or {"algoId": 1}, headers or {}
        self.text = str(self._c)

    def json(self):
        return self._c


def test_firma_ordine_condizionato_e_niente_reindirizzamenti():
    visti = []

    def http(metodo, url, headers, timeout, allow_redirects):
        visti.append((metodo, url, headers, allow_redirects))
        return _R()
    c = ContoDemo("chiave", "segreto", "BTCUSDT", http)
    c.condizionato("lungo", "STOP_MARKET", 88000.0, "tais1")
    metodo, url, headers, redir = visti[0]
    assert metodo == "POST" and "/fapi/v1/algoOrder?" in url and headers["X-MBX-APIKEY"] == "chiave" and redir is False
    q, firma = url.split("?", 1)[1].rsplit("&signature=", 1)
    assert firma == hmac.new(b"segreto", q.encode(), hashlib.sha256).hexdigest()
    for pezzo in ("algoType=CONDITIONAL", "side=SELL", "type=STOP_MARKET", "triggerPrice=88000", "closePosition=true",
                  "clientAlgoId=tais1"):
        assert pezzo in q


def test_troppe_richieste_pausa_senza_altre_richieste():
    visti = []

    def http(metodo, url, headers, timeout, allow_redirects):
        visti.append(url)
        return _R(429, {"code": -1003}, {"Retry-After": "5"})
    c = ContoDemo("k", "s", "BTCUSDT", http)
    with pytest.raises(LimiteBinance):
        c.mercato()
    with pytest.raises(LimiteBinance):
        c.mercato()
    assert len(visti) == 1                                      # la seconda non parte


def test_arrotonda_per_difetto():
    assert arrotonda(0.0056789, 0.001) == 0.005
    assert arrotonda(88000.07, 0.1) == 88000.0
