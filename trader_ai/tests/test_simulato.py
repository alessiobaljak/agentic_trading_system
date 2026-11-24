"""Test del conto simulato (conto_simulato.py) con un mercato finto: spese, scarto, stop, obiettivo, limite, liquidazione,
funding, salvataggio; e il programma (avvio.Trader) che gira sul conto simulato senza saperlo."""
from datetime import datetime, timedelta, timezone

import pytest

from trader_ai.avvio import Trader
from trader_ai.conto_simulato import ContoSimulato, MercatoPubblico, liquidazione
from trader_ai.modello import Esito
from trader_ai.schema import Risposta

T0_MS = int(datetime(2026, 11, 24, 10, 0, tzinfo=timezone.utc).timestamp() * 1000)
MIN = 60_000


class MercatoFinto:
    simbolo = "BTCUSDT"

    def __init__(self):
        self.prezzo = 90000.0
        self.minuti = []          # (apertura_ms, apertura, massimo, minimo, chiusura)
        self.pagamenti = []       # (ms, tasso, prezzo)

    def minuto(self, inizio_ms, apertura, massimo, minimo, chiusura):
        self.minuti.append((inizio_ms, apertura, massimo, minimo, chiusura))
        self.prezzo = chiusura

    def klines(self, intervallo, n=200, inizio_ms=None):
        if intervallo == "1m":
            return [[a, o, h, l, c, 1.0, a + MIN - 1] for a, o, h, l, c in self.minuti if inizio_ms is None or a >= inizio_ms]
        passo = {"5m": 5, "15m": 15, "30m": 30}[intervallo] * MIN
        return [[T0_MS - passo * (60 - i), 90000, 90100, 89900, 90000 + i, 5.0, T0_MS - passo * (59 - i) - 1] for i in range(60)]

    def mercato(self):
        return {"prezzo": self.prezzo, "funding": 0.0001, "prossimo_funding_ms": T0_MS + 8 * 3600_000, "interesse_aperto": 100.0}

    def funding_da(self, inizio_ms):
        return [{"fundingTime": t, "fundingRate": str(r), "markPrice": str(p)} for t, r, p in self.pagamenti if t >= inizio_ms]

    def filtri(self):
        return {"passo_prezzo": 0.1, "passo_quantita": 0.001, "passo_quantita_limite": 0.001, "quantita_min": 0.001,
                "valore_min": 100.0}


class Orologio:
    def __init__(self, ms):
        self.ms = ms

    def __call__(self):
        return self.ms


def conto(tmp_path):
    m, o = MercatoFinto(), Orologio(T0_MS)
    c = ContoSimulato(m, tmp_path / "conto_simulato.json", o)
    c.aggiorna()                  # primo aggiornamento: fissa il punto di partenza dei minuti
    return c, m, o


def avanza(c, m, o, apertura, massimo, minimo, chiusura):
    inizio = o.ms - o.ms % MIN
    m.minuto(inizio, apertura, massimo, minimo, chiusura)
    o.ms = inizio + MIN + 10_000
    c.aggiorna()


def test_apertura_a_mercato_con_scarto_e_commissione(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    e = c.apri("lungo", 0.01, "taio1")
    assert float(e["avgPrice"]) == pytest.approx(90000 * 1.0001)
    s = c.saldo()
    assert s["portafoglio"] == pytest.approx(1000 - 0.01 * 90009 * 0.0005)
    assert s["disponibile"] == pytest.approx(s["portafoglio"] - 0.01 * 90009 / 5)


def test_stop_toccato_dal_minimo_della_candela(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1")
    c.condizionato("lungo", "STOP_MARKET", 88000.0, "tais1")
    c.condizionato("lungo", "TAKE_PROFIT_MARKET", 92000.0, "tait1")
    avanza(c, m, o, 90000, 92500, 87900, 89000)               # tocca stop e obiettivo: vale lo stop
    assert c.posizioni_tutte() == [] and c.ordini_tutti() == []
    assert c.s["movimenti"][-2]["come"] == "stop"
    risultato = c.s["movimenti"][-2]["importo"]
    assert risultato == pytest.approx((88000 * 0.9999 - 90009) * 0.01)


def test_candela_che_apre_oltre_lo_stop_esce_all_apertura(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(2)
    c.apri("corto", 0.01, "taio1")
    c.condizionato("corto", "STOP_MARKET", 91000.0, "tais1")
    avanza(c, m, o, 91500, 91600, 91400, 91500)
    assert c.s["movimenti"][-2]["prezzo"] == pytest.approx(91500 * 1.0001)


def test_obiettivo(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1")
    c.condizionato("lungo", "STOP_MARKET", 88000.0, "tais1")
    c.condizionato("lungo", "TAKE_PROFIT_MARKET", 91000.0, "tait1")
    avanza(c, m, o, 90000, 91200, 89900, 91100)
    assert c.posizioni_tutte() == [] and c.s["movimenti"][-2]["come"] == "obiettivo"


def test_liquidazione_prima_dello_stop_troppo_lontano_perde_tutto_il_margine(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(10)
    c.apri("lungo", 0.01, "taio1")
    liq = liquidazione("lungo", 90009, 10)
    c.condizionato("lungo", "STOP_MARKET", liq - 500, "tais1")   # stop oltre la liquidazione
    prima = c.s["portafoglio"]
    avanza(c, m, o, 90000, 90000, liq - 1000, liq - 800)
    assert c.posizioni_tutte() == [] and c.s["movimenti"][-1]["cosa"] == "liquidazione"
    assert c.s["portafoglio"] == pytest.approx(prima - 0.01 * 90009 / 10)


def test_ordine_limite_eseguito_quando_il_prezzo_lo_tocca(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1", "LIMIT", 89500.0)
    assert c.posizioni_tutte() == [] and c.saldo()["disponibile"] == pytest.approx(1000 - 0.01 * 89500 / 5)
    avanza(c, m, o, 90000, 90100, 89400, 89600)
    p = c.posizioni_tutte()[0]
    assert p["entrata"] == 89500.0 and c.s["movimenti"][-1]["importo"] == pytest.approx(-0.01 * 89500 * 0.0002)


def test_stop_che_scatterebbe_subito_rifiutato(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1")
    with pytest.raises(RuntimeError, match="-2021"):
        c.condizionato("lungo", "STOP_MARKET", 90500.0, "tais1")


def test_funding_pagato_dal_lungo(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1")
    m.pagamenti.append((T0_MS + 30_000, 0.0001, 90000.0))
    avanza(c, m, o, 90000, 90010, 89990, 90000)
    f = [x for x in c.s["movimenti"] if x["cosa"] == "funding"]
    assert len(f) == 1 and f[0]["importo"] == pytest.approx(-0.01 * 90000 * 0.0001)


def test_margine_insufficiente(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(1)
    with pytest.raises(RuntimeError, match="-2019"):
        c.apri("lungo", 0.02, "taio1")                        # 1.800 USDT con leva 1 su 1.000


def test_stato_salvato_e_riletto(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1")
    c2 = ContoSimulato(m, tmp_path / "conto_simulato.json", o)
    assert c2.posizioni_tutte()[0]["quantita"] == 0.01


def test_solo_pagine_pubbliche_senza_chiave():
    visti = []

    class R:
        status_code, text = 200, ""

        def json(self):
            return {"markPrice": "1", "lastFundingRate": "0", "nextFundingTime": 0, "openInterest": "1"}

    def http(url, timeout):
        visti.append(url)
        return R()
    MercatoPubblico("BTCUSDT", http).mercato()
    assert all(u.startswith("https://fapi.binance.com/fapi/v1/") for u in visti) and len(visti) == 2


def test_il_programma_gira_sul_conto_simulato(tmp_path):
    c, m, o = conto(tmp_path)
    ora = lambda: datetime.fromtimestamp(o.ms / 1000, timezone.utc)
    risposte = [Risposta(azione="apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000, obiettivo_prezzo=92000,
                         approccio="t", cambio_approccio=False, diario="d")]
    tr = Trader(c, lambda s, u: Esito(risposte.pop(0) if risposte else None, "ok" if risposte else "fuori_schema",
                                      {"input_tokens": 100}), tmp_path, ora)
    tr.passo()
    assert c.posizioni_tutte() and len(c.ordini_tutti()) == 2           # stop e obiettivo sul conto simulato
    avanza(c, m, o, 90000, 90050, 87500, 87800)                         # scatta lo stop
    tr.passo()
    st = tr.carica()
    assert c.posizioni_tutte() == [] and st["operazioni"][-1]["come"] == "stop"
    assert st["operazioni"][-1]["risultato"] < 0
