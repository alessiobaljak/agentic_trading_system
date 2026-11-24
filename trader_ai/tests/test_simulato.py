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

    pausa_fino = 0.0

    def klines(self, intervallo, n=200, inizio_ms=None):
        if intervallo == "1m":
            return [[a, o, h, l, c, 1.0, a + MIN - 1] for a, o, h, l, c in self.minuti
                    if inizio_ms is None or a >= inizio_ms][:n]
        passo = {"5m": 5, "15m": 15, "30m": 30}[intervallo] * MIN
        return [[T0_MS - passo * (60 - i), 90000, 90100, 89900, 90000 + i, 5.0, T0_MS - passo * (59 - i) - 1] for i in range(60)]

    def klines_mark(self, n=1000, inizio_ms=None):
        return self.klines("1m", n, inizio_ms)

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
    c.aggiorna(forza=True)        # primo aggiornamento: fissa il punto di partenza dei minuti
    return c, m, o


def avanza(c, m, o, apertura, massimo, minimo, chiusura):
    """Il minuto dopo quello di adesso (il minuto in cui parte un ordine non conta)."""
    inizio = o.ms - o.ms % MIN + MIN
    m.minuto(inizio - MIN, 90000, 90000, 90000, 90000) if not any(x[0] == inizio - MIN for x in m.minuti) else None
    m.minuto(inizio, apertura, massimo, minimo, chiusura)
    o.ms = inizio + MIN + 10_000
    c.aggiorna(forza=True)


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


# --- ottava revisione: 152, 153, 154, 155 --------------------------------------------------------------------------------

def test_due_programmi_sullo_stesso_conto_non_si_sovrascrivono(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1")
    c.condizionato("lungo", "STOP_MARKET", 88000.0, "tais1")
    altro = ContoSimulato(m, tmp_path / "conto_simulato.json", o)      # il comando «chiudi» lanciato a mano
    altro.chiudi({"lato": "lungo", "quantita": 0.01}, "taix1")
    avanza(c, m, o, 90000, 90010, 89990, 90000)                       # il servizio continua con il suo oggetto
    assert c.posizioni_tutte() == [] and c.ordini_tutti() == []
    assert any(x.get("come") == "chiusa a mercato" for x in c.s["movimenti"])


def test_dopo_2500_minuti_di_fermo_si_recupera_tutto(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1")
    c.condizionato("lungo", "STOP_MARKET", 88000.0, "tais1")
    inizio = T0_MS + MIN
    for i in range(2500):
        basso = 87000.0 if i == 1100 else 89900.0
        alto = 99000.0 if i > 1100 else 90100.0                       # dopo lo stop il prezzo vola: non deve contare
        m.minuto(inizio + i * MIN, 90000, alto, basso, 90000)
    o.ms = inizio + 2500 * MIN + 5_000
    c.aggiorna(forza=True)
    assert c.posizioni_tutte() == [] and c.s["ultimo_minuto_ms"] == inizio + 2500 * MIN
    stop = [x for x in c.s["movimenti"] if x.get("come") == "stop" and x["cosa"] == "risultato"]
    assert stop and stop[0]["importo"] < 0


def test_minuti_mancanti_nessuna_decisione(tmp_path):
    c, m, o = conto(tmp_path)
    o.ms = T0_MS + 10 * MIN
    with pytest.raises(RuntimeError, match="mancanti"):
        c.aggiorna(forza=True)


def test_funding_pubblicato_in_ritardo_applicato_una_volta(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1")
    avanza(c, m, o, 90000, 90010, 89990, 90000)
    m.pagamenti.append((T0_MS + 40_000, 0.0002, 90000.0))             # pubblicato dopo il controllo
    avanza(c, m, o, 90000, 90010, 89990, 90000)
    avanza(c, m, o, 90000, 90010, 89990, 90000)
    f = [x for x in c.s["movimenti"] if x["cosa"] == "funding"]
    assert len(f) == 1 and f[0]["importo"] == pytest.approx(-0.01 * 90000 * 0.0002)


def test_il_minuto_in_cui_parte_l_ordine_non_conta(tmp_path):
    c, m, o = conto(tmp_path)
    o.ms = T0_MS + 30_000                                             # ordine a metà minuto
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1")
    c.condizionato("lungo", "STOP_MARKET", 88000.0, "tais1")
    m.minuto(T0_MS, 90000, 90100, 87000, 90000)                       # il minimo di 87.000 era PRIMA dell'ordine
    o.ms = T0_MS + MIN + 5_000
    c.aggiorna(forza=True)
    assert c.posizioni_tutte() != []


def test_limite_solo_toccato_non_si_esegue(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1", "LIMIT", 89500.0)
    avanza(c, m, o, 90000, 90100, 89500, 89600)
    assert c.posizioni_tutte() == []


def test_pausa_dopo_troppe_richieste():
    visti = []

    class R:
        status_code, text, headers = 429, "", {}

    def http(url, timeout):
        visti.append(url)
        return R()
    mp = MercatoPubblico("BTCUSDT", http)
    for _ in range(3):
        with pytest.raises(RuntimeError):
            mp.mercato()
    assert len(visti) == 1


# --- nona revisione: 163 --------------------------------------------------------------------------------------------------

def test_obiettivo_messo_a_meta_minuto_non_conta_i_prezzi_di_prima(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1")
    c.condizionato("lungo", "STOP_MARKET", 88000.0, "tais1")
    avanza(c, m, o, 90000, 90010, 89990, 90000)
    o.ms += 20_000                                                     # a metà del minuto dopo si mette un obiettivo
    c.condizionato("lungo", "TAKE_PROFIT_MARKET", 90500.0, "tait1")
    inizio = o.ms - o.ms % MIN
    m.minuto(inizio, 90000, 90600, 89990, 90000)                       # il 90.600 era prima dell'obiettivo
    o.ms = inizio + MIN + 5_000
    c.aggiorna(forza=True)
    assert c.posizioni_tutte() != []
    avanza(c, m, o, 90000, 90600, 89990, 90000)                        # al minuto dopo sì
    assert c.posizioni_tutte() == [] and c.s["movimenti"][-2]["come"] == "obiettivo"


def test_nel_minuto_del_limite_eseguito_l_obiettivo_non_conta(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1", "LIMIT", 89500.0)
    c.condizionato("lungo", "STOP_MARKET", 88000.0, "tais1")
    c.condizionato("lungo", "TAKE_PROFIT_MARKET", 90500.0, "tait1")
    avanza(c, m, o, 90000, 90600, 89400, 90000)                        # esegue il limite e tocca anche 90.600
    assert c.posizioni_tutte() != []                                   # l'ordine dei prezzi nel minuto non si sa


# --- decima revisione: 167 -----------------------------------------------------------------------------------------------

def test_stop_spostato_a_meta_minuto_il_vecchio_vale_fino_alla_fine_del_minuto(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1")
    c.condizionato("lungo", "STOP_MARKET", 89500.0, "tais1")
    avanza(c, m, o, 90000, 90010, 89990, 90000)
    o.ms += 30_000                                                     # a metà minuto lo stop passa da 89.500 a 89.700
    vecchio = [x for x in c.ordini_tutti() if x["_algo"]][0]
    c.condizionato("lungo", "STOP_MARKET", 89700.0, "tais2")
    c.annulla_condizionato(vecchio)
    inizio = o.ms - o.ms % MIN
    m.minuto(inizio, 90000, 90010, 89400, 89900)                       # il minimo tocca tutti e due gli stop
    o.ms = inizio + MIN + 5_000
    c.aggiorna(forza=True)
    assert c.posizioni_tutte() == []
    uscita = [x for x in c.s["movimenti"] if x.get("come") == "stop" and x["cosa"] == "risultato"][0]["prezzo"]
    assert uscita == pytest.approx(89700 * 0.9999)                     # il più vicino al prezzo


def test_stop_rimesso_a_meta_minuto_conta_subito(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1")
    avanza(c, m, o, 90000, 90010, 89990, 90000)                        # per un minuto senza stop (dopo un riavvio)
    o.ms += 30_000
    c.condizionato("lungo", "STOP_MARKET", 89500.0, "tais1")           # la protezione lo rimette a metà minuto
    inizio = o.ms - o.ms % MIN
    m.minuto(inizio, 90000, 90010, 89400, 89900)
    o.ms = inizio + MIN + 5_000
    c.aggiorna(forza=True)
    assert c.posizioni_tutte() == []


def test_stop_spostato_nel_minuto_del_limite_eseguito(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1", "LIMIT", 89500.0)
    c.condizionato("lungo", "STOP_MARKET", 88000.0, "tais1")
    m.minuto(T0_MS, 90000, 90010, 89990, 90000)
    o.ms = T0_MS + MIN + 30_000                                        # nel minuto dopo, a metà, lo stop sale a 89.300
    vecchio = [x for x in c.ordini_tutti() if x["_algo"]][0]
    c.condizionato("lungo", "STOP_MARKET", 89300.0, "tais2")
    c.annulla_condizionato(vecchio)
    m.minuto(T0_MS + MIN, 90000, 90010, 89200, 89900)                  # esegue il limite e scende sotto lo stop nuovo
    o.ms = T0_MS + 2 * MIN + 5_000
    c.aggiorna(forza=True)
    assert c.posizioni_tutte() == []


# --- undicesima revisione: 170, 171 ------------------------------------------------------------------------------------

def _sposta_stop(c, nuovo):
    vecchio = [x for x in c.ordini_tutti() if x["_algo"]][0]
    c.condizionato("lungo", "STOP_MARKET", nuovo, "tais9")
    c.annulla_condizionato(vecchio)


def test_stop_allargato_nei_primi_secondi_il_minuto_chiuso_conta_il_vecchio(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1")
    c.condizionato("lungo", "STOP_MARKET", 89500.0, "tais1")
    avanza(c, m, o, 90000, 90010, 89990, 90000)
    vecchio = [x for x in c.ordini_tutti() if x["_algo"]][0]           # letto durante il minuto
    inizio = o.ms - o.ms % MIN                                         # il minuto in corso, con lo stop a 89.500
    m.minuto(inizio, 90000, 90010, 89400, 89900)                       # tocca 89.500
    o.ms = inizio + MIN + 2_000                                        # 2 secondi dopo la chiusura del minuto
    c.condizionato("lungo", "STOP_MARKET", 89000.0, "tais9")           # lo stop si allarga, ma prima si conta il minuto chiuso
    c.annulla_condizionato(vecchio)
    assert c.posizioni_tutte() == []
    assert [x for x in c.s["movimenti"] if x.get("come") == "stop" and x["cosa"] == "risultato"][0]["prezzo"] == \
        pytest.approx(89500 * 0.9999)


def test_stop_stretto_nei_primi_secondi_non_conta_nel_minuto_prima(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1")
    c.condizionato("lungo", "STOP_MARKET", 89000.0, "tais1")
    avanza(c, m, o, 90000, 90010, 89990, 90000)
    inizio = o.ms - o.ms % MIN
    m.minuto(inizio, 90000, 90010, 89400, 89900)                       # 89.400: sotto lo stop nuovo, non sotto il vecchio
    o.ms = inizio + MIN + 2_000
    _sposta_stop(c, 89300.0)                                           # nasce DOPO quel minuto
    assert c.posizioni_tutte() != []


def test_stop_allargato_a_meta_minuto_il_vecchio_vale_fino_alla_fine(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1")
    c.condizionato("lungo", "STOP_MARKET", 89500.0, "tais1")
    avanza(c, m, o, 90000, 90010, 89990, 90000)
    o.ms += 30_000
    _sposta_stop(c, 89000.0)                                           # allargato a metà minuto
    inizio = o.ms - o.ms % MIN
    m.minuto(inizio, 90000, 90010, 89400, 89900)                       # tocca il vecchio (89.500), non il nuovo
    o.ms = inizio + MIN + 5_000
    c.aggiorna(forza=True)
    assert c.posizioni_tutte() == []
