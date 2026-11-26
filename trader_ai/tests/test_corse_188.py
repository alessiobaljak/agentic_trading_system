"""Le corse del problema 188 (quindicesima revisione, 26 novembre 2026), scritte dal revisore nel riesame e copiate qui come chiede la
sua condizione 2: un ordine limite che si esegue fra la lettura delle posizioni e quella degli ordini, nel passo e dentro l'esecuzione
di una decisione, sul conto simulato vero (lettura lenta e un secondo programma sullo stesso file) e con l'esito «eseguito» del conto
demo. Il comportamento giusto: la posizione tiene il suo stop, il programma la conosce, il passo dopo non si ferma come davanti a una
posizione d'altri. Nessuna rete; tutto in tmp_path.
"""
import json
from datetime import datetime, timedelta, timezone

import pytest

from trader_ai.avvio import Trader
from trader_ai.conto_demo import ContoDemo
from trader_ai.conto_simulato import ContoSimulato
from trader_ai.modello import Esito
from trader_ai.tests.test_avvio import T0, ContoFinto, Orologio, risposta, stop_sul_conto
from trader_ai.tests.test_simulato import MIN, T0_MS, MercatoFinto

LIMITE = dict(margine_usdt=100, leva=5, stop_prezzo=89000.0, tipo_ordine="limite", prezzo_limite=89500.0)


class Clock:
    def __init__(self, ms):
        self.ms = ms

    def __call__(self):
        return self.ms

    def dt(self):
        return datetime.fromtimestamp(self.ms / 1000, timezone.utc)


class MercatoLento(MercatoFinto):
    def __init__(self, clock):
        super().__init__()
        self.clock, self.ritardo_ms = clock, 0

    def klines(self, intervallo, n=200, inizio_ms=None):
        out = super().klines(intervallo, n, inizio_ms)
        if intervallo == "1m" and self.ritardo_ms:
            self.clock.ms += self.ritardo_ms
            self.ritardo_ms = 0
        return out


def _modello(risposte, chiamate):
    def m(system, utente):
        chiamate.append("\n\n".join(utente) if isinstance(utente, list) else utente)
        return Esito(risposte.pop(0) if risposte else risposta(), "ok", {"input_tokens": 100, "output_tokens": 100})
    return m


def sim(c):
    return json.loads(c.file.read_text())


def stop_nel_file(c):
    return [a["prezzo"] for a in sim(c)["algo"] if a["tipo"] == "STOP_MARKET"]


def eventi(tr):
    return [json.loads(x).get("evento") for x in tr.diario.read_text().splitlines()]


def _prepara_sim(tmp_path, clock, m):
    c = ContoSimulato(m, tmp_path / "conto_simulato.json", clock)
    c.aggiorna(forza=True)
    for i in range(4):                                                 # 10:00-10:03: sopra il limite
        m.minuto(T0_MS + i * MIN, 90000, 90050, 89950, 90000)
    m.minuto(T0_MS + 4 * MIN, 90000, 90000, 89400, 89600)             # 10:04: passa sotto 89.500, non sotto lo stop 89.000
    for i in range(5, 20):                                             # 10:05-10:19: scende fino a 88.500, sotto lo stop
        m.minuto(T0_MS + i * MIN, 89600 - (i - 5) * 70, 89650 - (i - 5) * 70, 89500 - (i - 5) * 70, 89550 - (i - 5) * 70)
    m.prezzo = 90000.0
    chiamate = []
    tr = Trader(c, _modello([risposta("apri_lungo", **LIMITE)], chiamate), tmp_path, clock.dt)
    clock.ms = T0_MS + 30_000
    tr.passo()
    assert tr.carica()["aperta"]["in_attesa"] and stop_nel_file(c) == [89000.0]
    return c, tr, chiamate


def test_188_a_simulato_lettura_lenta(tmp_path):
    clock = Clock(T0_MS)
    m = MercatoLento(clock)
    c, tr, chiamate = _prepara_sim(tmp_path, clock, m)
    clock.ms = T0_MS + 4 * MIN + 57_000                               # 10:04:57, prima lettura lenta di 6 secondi
    m.ritardo_ms = 6_000
    tr.passo()
    st = tr.carica()
    pos = sim(c)["posizione"]
    print("\n[188 a] posizione", pos and (pos["lato"], pos["entrata"]), "| stop sul conto", stop_nel_file(c), "| aperta nel programma",
          st["aperta"] and (st["aperta"]["in_attesa"], st["aperta"]["entrata"]), "| eventi",
          [e for e in eventi(tr) if e and "limite" in e])
    assert pos and pos["entrata"] == 89500.0
    assert st["aperta"] and not st["aperta"]["in_attesa"] and st["aperta"]["entrata"] == 89500.0
    assert stop_nel_file(c) == [89000.0]
    clock.ms += 30_000
    tr.passo()
    assert tr.carica()["estraneo"] is None
    clock.ms += 600_000                                                # dieci minuti dopo: il prezzo passa sotto 89.000
    m.prezzo = 88600.0
    tr.passo()
    st = tr.carica()
    op = st["operazioni"][-1]
    print("[188 a] dopo 10 minuti: posizione", sim(c)["posizione"], "| operazione", op["come"], op["uscita"], op["risultato"],
          "| chiamate", len(chiamate))
    assert sim(c)["posizione"] is None and op["come"] == "stop iniziale" and op["uscita"] < 89000 and not op["uscita_stimata"]
    assert len(st["operazioni"]) == 1


def test_188_b_simulato_altro_processo_fra_le_due_letture(tmp_path):
    clock = Clock(T0_MS)
    m = MercatoFinto()
    c, tr, _ = _prepara_sim(tmp_path, clock, m)
    altro = ContoSimulato(m, c.file, clock)                           # «controlla» lanciato a mano: stesso file
    vero = c.ordini_tutti
    fatto = {"x": False}

    def ordini_tutti():
        if not fatto["x"]:
            fatto["x"] = True
            clock.ms = T0_MS + 5 * MIN + 1_000
            altro.saldo()
            clock.ms = T0_MS + 5 * MIN + 1_100
        return vero()
    c.ordini_tutti = c.ordini_simbolo = ordini_tutti
    clock.ms = T0_MS + 4 * MIN + 59_500
    tr.passo()
    st = tr.carica()
    print("\n[188 b] posizione", bool(sim(c)["posizione"]), "| stop", stop_nel_file(c), "| aperta",
          st["aperta"] and st["aperta"]["in_attesa"])
    assert sim(c)["posizione"] and stop_nel_file(c) == [89000.0] and st["aperta"] and not st["aperta"]["in_attesa"]
    c.ordini_tutti = c.ordini_simbolo = vero
    clock.ms += 30_000
    tr.passo()
    assert tr.carica()["estraneo"] is None


def _filled(metodo, url, headers, timeout, allow_redirects):
    class R:
        status_code = 200
        text = ""

        def json(self):
            return {"status": "FILLED", "executedQty": "0.005", "avgPrice": "89500", "updateTime": 1764000000000, "type": "LIMIT"}
    return R()


def test_188_c_demo_esito_eseguito_con_posizione_aperta(tmp_path):
    e = ContoDemo("k", "s", "BTCUSDT", _filled).esito_ordine("taio1")
    assert e["stato"] == "eseguito"
    c = ContoFinto()
    o = Orologio(T0)
    tr = Trader(c, _modello([risposta("apri_lungo", **LIMITE)], []), tmp_path, o)
    tr.passo()
    cid = tr.carica()["aperta"]["cid"]
    c.esiti[cid] = e
    vero = c.ordini_tutti

    def eseguito_adesso():
        if c.normali:
            c.normali = []
            c.pos = {"lato": "lungo", "quantita": 0.005, "entrata": 89500.0, "leva": 5, "liquidazione": None}
        return vero()
    c.ordini_tutti = eseguito_adesso
    o.t = T0 + timedelta(minutes=4)
    tr._ultimo_controllo_completo = 0.0
    tr.passo()
    st = tr.carica()
    print("\n[188 c] posizione", c.pos is not None, "| stop", stop_sul_conto(c), "| aperta", st["aperta"] and st["aperta"]["in_attesa"],
          "| operazioni", len(st["operazioni"]))
    assert c.pos is not None and stop_sul_conto(c) == [89000.0]
    assert st["aperta"] and not st["aperta"]["in_attesa"] and st["operazioni"] == []
    o.t = T0 + timedelta(minutes=4, seconds=30)
    tr.passo()
    assert tr.carica()["estraneo"] is None and stop_sul_conto(c) == [89000.0]


@pytest.mark.parametrize("stato", ["aperta", "eseguito"])
def test_188_d_esegui_limite_eseguito_mentre_si_rileggono_gli_ordini(tmp_path, stato):
    c = ContoFinto()
    o = Orologio(T0)
    tr = Trader(c, _modello([risposta("apri_lungo", **LIMITE)], []), tmp_path, o)
    tr.passo()
    cid = tr.carica()["aperta"]["cid"]
    c.esiti[cid] = {"stato": stato, "entrata": 89500.0, "quantita": 0.005, "eseguita_ms": int(T0.timestamp() * 1000) + 60_000}
    dentro = {"esegui": False}
    vero_ordini = c.ordini_tutti

    def ordini_tutti():
        if dentro["esegui"] and c.normali:
            c.normali = []
            c.pos = {"lato": "lungo", "quantita": 0.005, "entrata": 89500.0, "leva": 5, "liquidazione": None}
        return vero_ordini()
    c.ordini_tutti = ordini_tutti

    def modello(s, u):
        dentro["esegui"] = True
        return Esito(risposta("modifica", stop_prezzo=89100.0), "ok", {"input_tokens": 1})
    tr.chiama = modello
    o.t = T0 + timedelta(minutes=14)
    tr.passo()
    st = tr.carica()
    print(f"\n[188 d {stato}] scarto: {st.get('ultimo_scarto')} | stop {stop_sul_conto(c)} | aperta "
          f"{st['aperta'] and st['aperta']['in_attesa']} | operazioni {len(st['operazioni'])}")
    assert c.pos is not None and st["aperta"] and not st["aperta"]["in_attesa"] and st["operazioni"] == []
    assert stop_sul_conto(c) == [89100.0]                              # la modifica del modello vale sulla posizione
    o.t = T0 + timedelta(minutes=14, seconds=30)
    c.ordini_tutti = vero_ordini
    tr._ultimo_controllo_completo = 0.0
    tr.passo()
    assert tr.carica()["estraneo"] is None and stop_sul_conto(c) == [89100.0]
