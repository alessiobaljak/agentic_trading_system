"""Test delle correzioni del controllo del 26 novembre 2026 (`trader_ai/revisioni/2026-11-26-controllo-istruzioni-e-dati.md`):
ordine limite in attesa (2.1), limite eseguito e chiuso fra due controlli e stop rimasti (2.2), cache da un'ora (2.3), uscite vere
(2.4), risposte non lette (2.5), resoconto dal conto (2.6), richiamo dopo un «chiudi» (2.10), scheda delle operazioni e memoria
stabile (3.1, 3.4, 3.6), calendario (3.11), ricostruzione della memoria (ripara.py). Nessuna rete."""
import json
from datetime import datetime, timedelta, timezone

import pytest

from trader_ai import calendario
from trader_ai.avvio import Trader
from trader_ai.costi import costo_dollari
from trader_ai.limiti import Conto, Posizione, controlla
from trader_ai.messaggio import Memoria, blocco_stabile, blocco_variabile, scheda
from trader_ai.modello import Esito
from trader_ai.operazioni import escursione, netto_a, pareggio, un_r
from trader_ai.ripara import ricostruisci
from trader_ai.schema import Risposta
from trader_ai.tests.test_avvio import T0, ContoFinto, Orologio, risposta, stop_sul_conto
from trader_ai.tests.test_simulato import T0_MS, avanza, conto


def trader_con(tmp_path, risposte, c=None, esiti=None):
    c = c or ContoFinto()
    chiamate = []

    def modello(system, utente):
        chiamate.append("\n\n".join(utente) if isinstance(utente, list) else utente)
        if esiti:
            return esiti.pop(0)
        return Esito(risposte.pop(0) if risposte else risposta(), "ok", {"input_tokens": 5000, "output_tokens": 2000})
    o = Orologio(T0)
    return Trader(c, modello, tmp_path, o), c, chiamate, o


LIMITE = dict(margine_usdt=100, leva=5, stop_prezzo=88000, obiettivo_prezzo=92000, tipo_ordine="limite", prezzo_limite=89000)


# --- 2.1: un ordine limite in attesa non è un'operazione aperta ---------------------------------------------------------

def test_limite_in_attesa_nel_messaggio_non_e_un_operazione_aperta(tmp_path):
    tr, c, chiamate, o = trader_con(tmp_path, [risposta("apri_corto", margine_usdt=100, leva=5, stop_prezzo=91500,
                                                        tipo_ordine="limite", prezzo_limite=91000)])
    tr.passo()
    assert c.pos is None and tr.carica()["aperta"]["in_attesa"]
    o.t = T0 + timedelta(minutes=14)
    tr.passo()
    ultimo = chiamate[-1]
    assert "ordine limite IN ATTESA, non eseguito: nessuna posizione e nessun risultato" in ultimo
    assert "posizione aperta" not in ultimo and "risultato adesso" not in ultimo


def test_modifica_con_limite_in_attesa_controlla_lo_stop_sul_prezzo_limite():
    # il caso delle 14:45 del 25 novembre: corto a 58.450 in attesa, stop spostato a 57.720 (sotto il limite) e accettato
    attesa = Posizione("corto", 0.04, 58450.0, 5, 58520.0, 57700.0, in_attesa=True)
    c = Conto(946.0, 478.0, 946.0, attesa)
    motivo = controlla(Risposta(azione="modifica", stop_prezzo=57720.0, approccio="a", cambio_approccio=False, diario="d"),
                       c, 57368.0)
    assert motivo and "dalla parte sbagliata del prezzo limite 58450" in motivo
    assert controlla(Risposta(azione="modifica", stop_prezzo=58600.0, approccio="a", cambio_approccio=False, diario="d"),
                     c, 57368.0) is None
    aprire = controlla(Risposta(azione="apri_lungo", margine_usdt=50, leva=5, stop_prezzo=57000.0, approccio="a",
                                cambio_approccio=False, diario="d"), c, 57368.0)
    assert "ordine limite in attesa" in aprire and "chiudi" in aprire


def test_prezzo_limite_con_ordine_a_mercato_scartato():
    r = Risposta(azione="apri_lungo", margine_usdt=50, leva=5, stop_prezzo=88000.0, prezzo_limite=89000.0, approccio="a",
                 cambio_approccio=False, diario="d")
    assert "tipo_ordine" in controlla(r, Conto(1000.0, 1000.0, 1000.0), 90000.0)


def test_diario_lungo_non_butta_la_decisione():
    r = Risposta(azione="aspetta", approccio="a" * 400, cambio_approccio=False, diario="x" * 1200)
    assert len(r.diario) == 1200                                      # prima: oltre 600 caratteri la decisione si perdeva


# --- 2.2 e 2.4: limite eseguito e chiuso fra due controlli; uscite dal conto ---------------------------------------------

def test_limite_eseguito_e_chiuso_fra_due_controlli_entra_in_memoria_e_chiama_subito(tmp_path):
    tr, c, chiamate, o = trader_con(tmp_path, [risposta("apri_lungo", **LIMITE)])
    tr.passo()
    cid = tr.carica()["aperta"]["cid"]
    # fra due controlli: il limite si esegue a 89.000 e lo stop lo chiude a 87.991,2; il conto lo racconta
    c.normali, c.algo, c.conto = [], [], 979.0
    c.esiti[cid] = {"stato": "chiusa", "entrata": 89000.0, "quantita": 0.005, "eseguita_ms": int(T0.timestamp() * 1000) + 120_000,
                    "chiusa_ms": int(T0.timestamp() * 1000) + 180_000, "uscita": 87991.2, "come": "stop",
                    "spese_entrata": 0.089, "spese": 0.309, "funding": 0.0, "risultato_prezzo": -5.044, "netto": -5.353}
    o.t = T0 + timedelta(minutes=4)
    tr.passo()
    st = tr.carica()
    op = st["operazioni"][-1]
    assert op["uscita"] == 87991.2 and op["come"] == "stop iniziale" and op["risultato"] == -5.35 and not op["uscita_stimata"]
    assert op["n"] == 1 and op["tipo"] == "limite" and op["stop_iniziale"] == 88000
    assert len(chiamate) == 2 and "operazione chiusa (stop iniziale)" in chiamate[-1]
    assert st["aperta"] is None and stop_sul_conto(c) == []


def test_limite_sparito_senza_esecuzione_toglie_anche_gli_stop(tmp_path):
    tr, c, chiamate, o = trader_con(tmp_path, [risposta("apri_lungo", **LIMITE)])
    tr.passo()
    assert stop_sul_conto(c) == [88000.0]
    c.normali = []                                                    # annullato fuori dal programma, mai eseguito
    o.t = T0 + timedelta(minutes=4)
    tr.passo()
    assert tr.carica()["aperta"] is None and stop_sul_conto(c) == [] and tr.carica()["operazioni"] == []


def test_stop_rimasto_di_un_lungo_non_chiude_il_corto_dopo(tmp_path):
    # la prova del controllo: lo stop di un lungo a 89.200 rimasto sul conto chiudeva «allo stop» un corto aperto dopo
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.condizionato("lungo", "STOP_MARKET", 89200.0, "tais1")          # rimasto da un'operazione di prima
    c.apri("corto", 0.01, "taio2", "MARKET")
    c.condizionato("corto", "STOP_MARKET", 90500.0, "tais2")
    avanza(c, m, o, 90000, 90010, 89990, 90009)                       # minuto tranquillo
    assert c.posizioni_tutte() and c.posizioni_tutte()[0]["lato"] == "corto"


def test_esito_ordine_del_conto_simulato(tmp_path):
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1", "LIMIT", 89500.0)
    assert c.esito_ordine("taio1") == {"stato": "in_attesa"} and c.esito_ordine("taio9") is None
    c.condizionato("lungo", "STOP_MARKET", 89000.0, "tais1")
    avanza(c, m, o, 90000, 90100, 89400, 89600)                       # eseguito a 89.500
    e = c.esito_ordine("taio1")
    assert e["stato"] == "aperta" and e["entrata"] == 89500.0 and e["spese_entrata"] == pytest.approx(0.01 * 89500 * 0.0002)
    avanza(c, m, o, 89600, 89700, 88900, 89000)                       # scatta lo stop a 89.000
    e = c.esito_ordine("taio1")
    assert e["stato"] == "chiusa" and e["come"] == "stop" and e["uscita"] == pytest.approx(89000 * 0.9999)
    atteso = (89000 * 0.9999 - 89500) * 0.01 - 0.01 * 89500 * 0.0002 - 0.01 * 89000 * 0.9999 * 0.0005
    assert e["netto"] == pytest.approx(atteso)
    assert c.saldo()["conto"] == pytest.approx(1000 + atteso)          # il netto dell'operazione è quello del conto


def test_candela_in_corso_segnata(tmp_path):
    c, m, o = conto(tmp_path)
    m.minuto(T0_MS, 90000, 90050, 89950, 90020)
    o.ms = T0_MS + 30_000                                             # a metà del minuto
    cs = c.candele("1m", o.ms, inizio_ms=T0_MS)
    assert len(cs) == 1 and cs[0]["in_corso"] and cs[0]["aperta"] == datetime.fromtimestamp(T0_MS / 1000, timezone.utc)


# --- 2.5 e 2.10 -----------------------------------------------------------------------------------------------------------

def test_risposta_non_letta_il_modello_lo_sa(tmp_path):
    tr, c, chiamate, o = trader_con(tmp_path, [], esiti=[Esito(None, "fuori_schema", {"input_tokens": 10}, "diario troppo lungo"),
                                                         Esito(risposta(), "ok", {"input_tokens": 10})])
    tr.passo()
    assert "non è stata letta (fuori_schema" in tr.carica()["ultimo_scarto"]
    o.t = T0 + timedelta(minutes=14)
    tr.passo()
    assert "NON è stata eseguita" in chiamate[-1] and "non è stata letta" in chiamate[-1]


def test_dopo_un_chiudi_del_modello_si_richiama_subito(tmp_path):
    tr, c, chiamate, o = trader_con(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000),
                                               risposta("chiudi")])
    tr.passo()
    o.t = T0 + timedelta(minutes=14)
    tr.passo()                                                        # il modello chiude
    assert c.pos is None and len(chiamate) == 2
    o.t = T0 + timedelta(minutes=14, seconds=30)
    tr.passo()                                                        # richiamato subito, non alla candela dopo
    assert len(chiamate) == 3 and "operazione chiusa (chiusa da te)" in chiamate[-1]


def test_operazione_chiusa_mentre_il_modello_pensa_si_registra_e_si_richiama(tmp_path):
    tr, c, chiamate, o = trader_con(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000)])
    tr.passo()
    vero = c.posizioni_tutte

    def chiusa_mentre_pensa():
        if len(chiamate) >= 2:                                        # lo stop scatta mentre il modello decide
            c.pos, c.algo = None, []
        return vero()
    c.posizioni_tutte = chiusa_mentre_pensa
    tr.chiama = lambda s, u: (chiamate.append(u), Esito(risposta("modifica", stop_prezzo=89000), "ok", {"input_tokens": 1}))[1]
    o.t = T0 + timedelta(minutes=14)
    tr.passo()
    st = tr.carica()
    assert st["aperta"] is None and len(st["operazioni"]) == 1 and st["richiama"]
    assert "mentre decidevi la tua operazione si è chiusa" in st["ultimo_scarto"]


# --- 2.3: costi della cache da un'ora --------------------------------------------------------------------------------------

def test_costo_della_cache_da_un_ora_senza_contare_due_volte():
    u = {"input_tokens": 1000, "output_tokens": 100, "cache_read_input_tokens": 2000, "cache_creation_input_tokens": 3000,
         "cache_creation": {"ephemeral_5m_input_tokens": 1000, "ephemeral_1h_input_tokens": 2000}}
    assert costo_dollari(u) == pytest.approx((1000 * 4 + 100 * 20 + 2000 * 0.2 + 1000 * 5 + 2000 * 8) / 1e6)
    senza = {"input_tokens": 0, "cache_creation_input_tokens": 1000}
    assert costo_dollari(senza) == pytest.approx(1000 * 8 / 1e6)         # senza dettaglio: il prezzo più alto


# --- 3.x: conti, scheda, memoria stabile --------------------------------------------------------------------------------

def test_netto_pareggio_e_un_r():
    # lungo 0,01 BTC a 90.000 a mercato: commissione d'entrata 0,45; uscita allo stop 89.000 con scarto e commissione
    netto = netto_a("lungo", 90000.0, 0.01, 89000.0, 0.45, 0.0, "BTCUSDT")
    atteso = (89000 * 0.9999 - 90000) * 0.01 - 89000 * 0.9999 * 0.01 * 0.0005 - 0.45
    assert netto == pytest.approx(atteso) and un_r("lungo", 90000.0, 0.01, 89000.0, 0.45, "BTCUSDT") == pytest.approx(-atteso)
    p = pareggio("corto", 90000.0, 0.01, 0.45, 0.1, "BTCUSDT")
    assert netto_a("corto", 90000.0, 0.01, p, 0.45, 0.1, "BTCUSDT") == pytest.approx(0.0, abs=1e-9)


def test_escursione_esclude_i_prezzi_prima_dell_esecuzione():
    t0 = datetime(2026, 11, 25, 7, 46, tzinfo=timezone.utc)
    c1 = [{"aperta": t0 + timedelta(minutes=i), "massimo": h, "minimo": lo} for i, (h, lo) in
          enumerate([(59500, 58800), (59000, 58700), (59200, 58900)])]
    es = int(t0.timestamp() * 1000)
    # corto da limite a 58.890 eseguito nel primo minuto: il minimo 58.800 di quel minuto può essere venuto prima
    fav, contro = escursione(c1, "corto", 58890.0, es, None, da_limite=True)
    assert fav == pytest.approx(190.0) and contro == pytest.approx(610.0)
    fav, contro = escursione(c1, "corto", 58890.0, es + 20_000, None, da_limite=False)
    assert fav == pytest.approx(190.0) and contro == pytest.approx(310.0)     # a mercato il primo minuto non conta


def _op(**kw):
    base = {"n": 7, "aperta": "2026-11-25T14:09:09+00:00", "tipo": "limite", "eseguita": "2026-11-25T15:01:00+00:00",
            "chiusa": "2026-11-25T15:01:00+00:00", "lato": "corto", "leva": 5, "quantita": 0.04, "entrata": 58450.0,
            "uscita": 58525.85, "come": "stop iniziale", "stop_iniziale": 58520.0, "obiettivo_iniziale": 57700.0,
            "spostamenti": [{"ora": "2026-11-25T14:45:00+00:00", "campo": "stop", "da": 58660.0, "a": 58520.0,
                             "prima_dell_esecuzione": True}],
            "atr15": 490.0, "spese": 1.64, "funding": 0.0, "risultato_prezzo": -3.03, "risultato": -4.67, "R": 4.67, "r": -1.0,
            "favore_r": 0.0, "contro_r": 1.1, "motivo": "rifiuto della resistenza", "approccio": "corto sui rifiuti"}
    base.update(kw)
    return base


def test_scheda_dice_i_fatti_dell_operazione():
    s = scheda(_op())
    for pezzo in ("#7 25/11 14:09, eseguito 15:01", "entrata 58450.0 (limite)", "stop iniziale 58520.0 (0.12%, 0.14 ATR15)",
                  "prima dell'esecuzione l'avevi spostato 1 volta, da 58660.0", "uscita 58525.8: stop iniziale",
                  "-4.67 netti (-1.00 R); prezzo -3.03, spese -1.64, funding +0.00", "-1.10 R contro",
                  "motivo all'apertura: rifiuto della resistenza"):
        assert pezzo in s, pezzo


def test_memoria_stabile_non_cambia_con_ora_e_prezzo():
    lezione = {"ora": "2026-11-25T17:05:00+00:00", "testo": "nel range gli stop stretti saltano", "dopo": 9, "giorno_netto": -47.9,
               "fissata": True}
    nuova = {**lezione, "testo": "nuova", "fissata": False}
    m = Memoria([_op()], [lezione, nuova], ["25/11 17:00 nota"], "a", None, {"giorno": "2026-11-25", "conto": 1000.0}, "2026-11-25")
    a = blocco_stabile(m)
    assert a == blocco_stabile(m) and "nel range gli stop stretti saltano" in a and "nuova" not in a
    assert "#7" in a and "oggi (25/11): 1 operazioni" in a
    c5 = [{"apertura": 1.0, "massimo": 1.0, "minimo": 1.0, "chiusura": 1.0, "volume": 1.0,
           "aperta": datetime(2026, 11, 25, 17, 0, tzinfo=timezone.utc) + timedelta(minutes=5 * i),
           "chiusa": datetime(2026, 11, 25, 17, 5, tzinfo=timezone.utc) + timedelta(minutes=5 * i)} for i in range(30)]
    v = blocco_variabile(datetime(2026, 11, 25, 19, 31, tzinfo=timezone.utc), "candela", "BTCUSDT", {"5m": c5},
                         {"prezzo": 1.0}, Conto(950.0, 950.0, 1000.0), None, m, "bastano")
    assert "nuova" in v and "lezioni scritte dopo l'ultima operazione chiusa" in v


def test_calendario_festa_usa_e_orari_d_inverno():
    giorno_del_ringraziamento = datetime(2026, 11, 26, 15, 0, tzinfo=timezone.utc)
    assert "chiusa tutto il giorno (festa: Ringraziamento)" in calendario.borsa_usa(giorno_del_ringraziamento)
    lunedi = datetime(2026, 11, 30, 15, 0, tzinfo=timezone.utc)
    assert calendario.borsa_usa(lunedi) == "a New York è lunedì 30/11 10:00: borsa aperta fino alle 21:00 UTC"
    assert calendario.fascia(lunedi) == "13-17 UTC" and "lunedì 30/11 15:00 UTC" in calendario.riga_orari(lunedi)
    # all'una UTC del 27 a New York è ancora il 26 (festa): lo dice con l'ora di New York (revisione, punto M3)
    notte = calendario.borsa_usa(datetime(2026, 11, 27, 1, 0, tzinfo=timezone.utc))
    assert notte.startswith("a New York è giovedì 26/11 20:00: borsa chiusa tutto il giorno (festa: Ringraziamento)")
    assert "prossima apertura venerdì 27/11 alle 14:30 UTC, chiusura anticipata alle 18:00 UTC" in notte


# --- 2.6: il resoconto dal conto -----------------------------------------------------------------------------------------

def test_resoconto_usa_il_conto_non_la_somma_delle_operazioni(tmp_path):
    tr, c, chiamate, o = trader_con(tmp_path, [])
    tr.passo()
    st = tr.carica()
    st["operazioni"] = [_op(chiusa="2026-11-24T15:01:00+00:00", giorno_prima=-5.0, rischio_pct=0.5)]   # una sola registrata
    st["discesa_max_giorno"] = 60.0
    testo = tr.resoconto(st, "2026-11-24", 946.39, 60429.4).read_text()
    assert "da 1000.00 a 946.39 USDT, -53.61" in testo and "Discesa massima nel giorno" in testo
    assert "Aperture con il giorno in perdita: 1 (leva media 5.0, margine medio -, rischio medio 0.5% del conto)" in testo


# --- ripara.py: la memoria di prima, rifatta dal conto ----------------------------------------------------------------

def test_ricostruzione_della_memoria_dal_conto_e_dal_diario():
    ms = lambda h, m: int(datetime(2026, 11, 25, h, m, tzinfo=timezone.utc).timestamp() * 1000)  # noqa: E731
    iso = lambda h, m: datetime(2026, 11, 25, h, m, tzinfo=timezone.utc).isoformat()           # noqa: E731
    storia = {"chiuse": [{"lato": "corto", "quantita": 0.04, "entrata": 58450.0, "leva": 5, "margine": 467.6,
                          "aperta_ms": ms(15, 1), "chiusa_ms": ms(15, 1), "da_limite": True}],
              "movimenti": [{"cosa": "commissione", "importo": -0.4676, "come": "limite eseguito"},
                            {"cosa": "risultato", "importo": -3.034, "prezzo": 58525.85, "come": "stop"},
                            {"cosa": "commissione", "importo": -1.1705, "come": "stop"}],
              "funding_applicati": []}
    diario = [{"ora": iso(14, 9), "evento": "aperta", "lato": "corto", "leva": 5, "entrata": 58450.0, "stop": 58660.0,
               "obiettivo": 57700.0, "approccio": "corto sui rifiuti", "margine": 470.0, "in_attesa": True},
              {"ora": iso(14, 9), "risposta": {"diario": "rifiuto della resistenza"}},
              {"ora": iso(14, 45), "evento": "modificata", "stop": 58520.0, "obiettivo": 57700.0}]
    ops, rapporto = ricostruisci([], storia, diario, "BTCUSDT")
    assert rapporto == {"corrette": 0, "aggiunte": 1, "lasciate": 0}
    op = ops[0]
    assert op["n"] == 1 and op["uscita"] == 58525.85 and op["stop_iniziale"] == 58520.0
    assert op["come"] == "stop spostato da te prima dell'esecuzione"            # revisione, punto B2
    assert op["risultato"] == pytest.approx(-3.034 - 1.6381, abs=0.01) and op["motivo"] == "rifiuto della resistenza"
    assert op["spostamenti"][0]["prima_dell_esecuzione"] and op["r"] == pytest.approx(-1.0, abs=0.02)


def test_la_ricostruzione_parte_da_sola_una_volta(tmp_path):
    tr, c, chiamate, o = trader_con(tmp_path, [])
    tr.salva({"operazioni": [{"aperta": "2026-11-24T09:00:00+00:00", "chiusa": "2026-11-24T09:30:00+00:00", "lato": "lungo",
                              "leva": 5, "entrata": 90000.0, "uscita": 89000.0, "come": "stop", "risultato": -5.0,
                              "approccio": "a"}], "note": [], "oi": [[1, 2]], "giorno": "2026-11-24", "conto_mezzanotte": 1000.0})
    tr.passo()
    st = tr.carica()
    assert st["versione_memoria"] == 7 and "oi" not in st and st["operazioni"][0]["n"] == 1 and st["prossimo_n"] == 2
    assert any("memoria ricostruita" in json.loads(x).get("evento", "") for x in tr.diario.read_text().splitlines())


# --- quindicesima revisione (26 novembre 2026): 188, 189, 190, 192, 193 e i punti del messaggio -----------------------------

def test_limite_eseguito_fra_la_lettura_delle_posizioni_e_quella_degli_ordini_non_perde_lo_stop(tmp_path):
    """Problema 188: le posizioni lette prima dell'esecuzione, gli ordini dopo. Prima si cancellava lo stop della posizione."""
    tr, c, chiamate, o = trader_con(tmp_path, [risposta("apri_lungo", **LIMITE)])
    tr.passo()
    cid = tr.carica()["aperta"]["cid"]
    vero = c.posizioni_tutte
    letture = []

    def posizioni_poi_esecuzione():
        p = vero()
        if not letture:                                               # la prima lettura vede ancora niente...
            letture.append(1)
            c.normali = []                                            # ...e subito dopo il limite si esegue
            c.pos = {"lato": "lungo", "quantita": 0.005, "entrata": 89000.0, "leva": 5, "liquidazione": None}
            c.esiti[cid] = {"stato": "aperta", "entrata": 89000.0, "quantita": 0.005,
                            "eseguita_ms": int(T0.timestamp() * 1000) + 60_000}
        return p
    c.posizioni_tutte = posizioni_poi_esecuzione
    o.t = T0 + timedelta(minutes=5)
    tr._ultimo_controllo_completo = 0.0
    tr.passo()
    st = tr.carica()
    assert st["aperta"] and not st["aperta"]["in_attesa"] and st["aperta"]["entrata"] == 89000.0
    assert stop_sul_conto(c) == [88000.0] and c.pos is not None


def test_esito_non_letto_non_vale_mai_eseguito(tmp_path):
    """Problema 189: un errore di lettura non cancella niente; al passo dopo l'operazione si registra una volta."""
    tr, c, chiamate, o = trader_con(tmp_path, [risposta("apri_lungo", **LIMITE)])
    tr.passo()
    cid = tr.carica()["aperta"]["cid"]
    c.normali, c.algo = [], []
    guasto = {"si": True}
    vero = c.esito_ordine

    def esito(x):
        if guasto["si"]:
            raise RuntimeError("rete")
        return vero(x)
    c.esito_ordine = esito
    o.t = T0 + timedelta(minutes=4)
    tr.passo()
    assert tr.carica()["aperta"]["in_attesa"] and tr.carica()["operazioni"] == []
    guasto["si"] = False
    c.esiti[cid] = {"stato": "chiusa", "entrata": 89000.0, "quantita": 0.005, "eseguita_ms": int(T0.timestamp() * 1000) + 60_000,
                    "chiusa_ms": int(T0.timestamp() * 1000) + 120_000, "uscita": 87991.2, "come": "stop", "spese_entrata": 0.089,
                    "spese": 0.309, "funding": 0.0, "risultato_prezzo": -5.044, "netto": -5.353}
    o.t = T0 + timedelta(minutes=5)
    tr.passo()
    o.t = T0 + timedelta(minutes=6)
    tr.passo()
    assert len(tr.carica()["operazioni"]) == 1 and tr.carica()["aperta"] is None


def test_ricostruzione_rimandata_se_il_conto_non_si_legge(tmp_path):
    """Problema 190: senza il conto la versione non sale; si riprova al passo dopo."""
    tr, c, chiamate, o = trader_con(tmp_path, [])
    tr.salva({"operazioni": [], "note": [], "giorno": "2026-11-24", "conto_mezzanotte": 1000.0})
    c.storia = lambda: (_ for _ in ()).throw(RuntimeError("rete"))
    tr.passo()
    assert tr.carica().get("versione_memoria", 0) < 7 and tr.carica()["tentativi_ripara"] == 1
    c.storia = lambda: {"chiuse": [], "movimenti": [], "funding_applicati": []}
    o.t = T0 + timedelta(minutes=1)
    tr.passo()
    assert tr.carica()["versione_memoria"] == 7 and "tentativi_ripara" not in tr.carica()


def test_limite_gia_oltre_il_prezzo_e_un_ordine_a_mercato(tmp_path):
    """Problema 193: il limite si esegue subito; con lo stop rifiutato si chiude subito, mai una posizione senza stop."""
    c, m, o = conto(tmp_path)
    risposte = [Risposta(azione="apri_lungo", margine_usdt=100, leva=5, stop_prezzo=89990.0, tipo_ordine="limite",
                         prezzo_limite=90500.0, approccio="t", cambio_approccio=False, diario="d")]
    ora = lambda: datetime.fromtimestamp(o.ms / 1000, timezone.utc)      # noqa: E731
    tr = Trader(c, lambda s, u: Esito(risposte.pop(0) if risposte else None, "ok" if risposte else "fuori_schema",
                                      {"input_tokens": 1}), tmp_path, ora)
    tr.passo()
    st = tr.carica()
    assert c.posizioni_tutte() and st["aperta"]["tipo"] == "mercato" and "già oltre il prezzo" in st["aperta"]["nota"]
    assert [a for a in c.ordini_tutti() if a["_algo"]], "la posizione deve avere il suo stop"


def test_limite_che_incrocia_controlla_lo_stop_sul_prezzo_di_adesso():
    r = Risposta(azione="apri_lungo", margine_usdt=100, leva=5, stop_prezzo=90100.0, tipo_ordine="limite", prezzo_limite=90500.0,
                 approccio="a", cambio_approccio=False, diario="d")
    assert "prezzo di adesso" in controlla(r, Conto(1000.0, 1000.0, 1000.0), 90000.0)


def test_chiudi_rifiutato_poi_lo_stop_resta_stop(tmp_path):
    """Problema 192: «chiusa da te» solo se la chiusura è riuscita."""
    tr, c, chiamate, o = trader_con(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000),
                                               risposta("chiudi")])
    tr.passo()
    vero = c.chiudi
    c.chiudi = lambda pos, cid: (_ for _ in ()).throw(RuntimeError("rifiutata"))
    o.t = T0 + timedelta(minutes=14)
    tr.passo()
    assert "chiusa_da" not in tr.carica()["aperta"]
    c.chiudi = vero
    c.pos, c.algo, c.prezzo, c.conto = None, [], 88000.0, 990.0          # poi lo stop
    o.t = T0 + timedelta(minutes=15)
    tr.passo()
    assert tr.carica()["operazioni"][-1]["come"] == "stop iniziale"


def test_annullare_un_limite_non_e_un_operazione_chiusa(tmp_path):
    """Punto B5: il richiamo dopo un annullamento non parla di operazione chiusa."""
    tr, c, chiamate, o = trader_con(tmp_path, [risposta("apri_lungo", **LIMITE), risposta("chiudi")])
    tr.passo()
    o.t = T0 + timedelta(minutes=14)
    tr.passo()
    o.t = T0 + timedelta(minutes=14, seconds=30)
    tr.passo()
    assert "ordine limite annullato da te (nessuna operazione)" in chiamate[-1] and "operazione chiusa (" not in chiamate[-1]


def test_funding_della_posizione_aperta_nel_messaggio(tmp_path):
    """Punto M1: il funding già pagato entra nei conti della posizione."""
    tr, c, chiamate, o = trader_con(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000)])
    tr.passo()
    cid = tr.carica()["aperta"]["cid"]
    c.esiti[cid] = {"stato": "aperta", "entrata": 90000.0, "quantita": 0.005, "eseguita_ms": int(T0.timestamp() * 1000),
                    "funding": -0.9}
    o.t = T0 + timedelta(minutes=14)
    tr.passo()
    assert "funding -0.90" in chiamate[-1]


def test_stop_spostato_dalla_parte_del_guadagno_detto_bene():
    s = scheda(_op(lato="lungo", entrata=60000.0, stop_iniziale=59800.0, uscita=60100.0, come="stop spostato da te",
                   spostamenti=[{"campo": "stop", "da": 59800.0, "a": 60100.0, "prima_dell_esecuzione": False}]))
    assert "oltre l'entrata, dalla parte del guadagno" in s


def test_obiettivo_di_un_limite_gia_superato_all_esecuzione_chiude_a_mercato(tmp_path):
    """R7-03: il limite si esegue e il prezzo passa l'obiettivo prima del passo: si chiude a mercato come obiettivo."""
    tr, c, chiamate, o = trader_con(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000,
                                                        obiettivo_prezzo=89300, tipo_ordine="limite", prezzo_limite=89000)])
    tr.passo()
    assert [x for x in c.algo if x["tipo"] == "TAKE_PROFIT_MARKET"] == []          # all'invio solo lo stop
    c.normali, c.prezzo = [], 89500.0                                              # eseguito, poi oltre l'obiettivo
    c.pos = {"lato": "lungo", "quantita": 0.005, "entrata": 89000.0, "leva": 5, "liquidazione": None}
    vero = c.condizionato

    def rifiuta_obiettivo(lato, tipo, prezzo, cid):
        if tipo == "TAKE_PROFIT_MARKET":
            raise RuntimeError('{"code":-2021,"msg":"Order would immediately trigger."}')
        return vero(lato, tipo, prezzo, cid)
    c.condizionato = rifiuta_obiettivo
    o.t = T0 + timedelta(minutes=3)
    tr.passo()
    st = tr.carica()
    assert c.pos is None and st["operazioni"][-1]["come"] == "obiettivo" and "operazione chiusa (obiettivo)" in chiamate[-1]


def test_modifica_dell_obiettivo_con_limite_in_attesa_resta_nello_stato(tmp_path):
    tr, c, chiamate, o = trader_con(tmp_path, [risposta("apri_lungo", **LIMITE), risposta("modifica", obiettivo_prezzo=93000)])
    tr.passo()
    o.t = T0 + timedelta(minutes=14)
    tr.passo()
    a = tr.carica()["aperta"]
    assert a["obiettivo"] == 93000 and [x for x in c.algo if x["tipo"] == "TAKE_PROFIT_MARKET"] == []
    assert a["spostamenti"][-1] == {**a["spostamenti"][-1], "campo": "obiettivo", "a": 93000, "prima_dell_esecuzione": True}


def test_modifica_senza_stop_accettato_chiude_e_richiama(tmp_path):
    """R7-05: anche una chiusura per stop rifiutati durante una modifica richiama subito il modello."""
    tr, c, chiamate, o = trader_con(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000),
                                               risposta("modifica", stop_prezzo=88500)])
    tr.passo()
    c.rifiuta_stop = True
    o.t = T0 + timedelta(minutes=14)
    tr.passo()
    assert c.pos is None and tr.carica()["richiama"].startswith("operazione chiusa (")
    o.t = T0 + timedelta(minutes=14, seconds=30)
    tr.passo()
    assert len(chiamate) == 3


def test_scarto_detto_anche_dopo_il_tetto(tmp_path):
    """R7-07: senza chiamata (tetto finito) lo scarto di prima resta da dire."""
    tr, c, chiamate, o = trader_con(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=95000)])
    tr.passo()
    assert "dalla parte sbagliata" in tr.carica()["ultimo_scarto"]
    tr.budget.registra(T0, 100.0)                                                  # tetto finito
    o.t = T0 + timedelta(minutes=14)
    tr.passo()
    assert "dalla parte sbagliata" in tr.carica()["ultimo_scarto"]


def test_l_ora_in_testa_al_diario_non_si_ripete(tmp_path):
    tr, c, chiamate, o = trader_con(tmp_path, [risposta(diario="10:00: la 15m chiude a 90000")])
    tr.passo()
    assert tr.carica()["note"][-1] == "24/11 10:01 la 15m chiude a 90000"


def test_chiusura_nell_ultimo_minuto_entra_nel_resoconto_del_suo_giorno(tmp_path):
    """S6: il resoconto di ieri si scrive dopo le chiusure trovate nel passo di mezzanotte."""
    tr, c, chiamate, o = trader_con(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000)])
    o.t = datetime(2026, 11, 24, 23, 50, tzinfo=timezone.utc)
    tr.passo()
    cid = tr.carica()["aperta"]["cid"]
    c.pos, c.algo, c.conto = None, [], 990.0
    c.esiti[cid] = {"stato": "chiusa", "entrata": 90000.0, "quantita": 0.005, "eseguita_ms": int(o.t.timestamp() * 1000),
                    "chiusa_ms": int(datetime(2026, 11, 24, 23, 59, 30, tzinfo=timezone.utc).timestamp() * 1000),
                    "uscita": 88000.0, "come": "stop", "spese_entrata": 0.22, "spese": 0.44, "funding": 0.0,
                    "risultato_prezzo": -10.0, "netto": -10.44}
    o.t = datetime(2026, 11, 25, 0, 0, 20, tzinfo=timezone.utc)
    tr.passo()
    testo = (tmp_path / "resoconti" / "2026-11-24.md").read_text()
    assert "Operazioni chiuse: 1" in testo and "-10.44" in testo


def test_annullare_nel_minuto_dopo_l_esecuzione_trova_la_posizione(tmp_path):
    """S7: il conto simulato conta i minuti chiusi prima di annullare: un limite eseguito non sparisce."""
    c, m, o = conto(tmp_path)
    c.prepara(5)
    c.apri("lungo", 0.01, "taio1", "LIMIT", 89500.0)
    m.minuto(T0_MS, 90000, 90010, 89990, 90000)
    m.minuto(T0_MS + 60_000, 90000, 90010, 89400, 89600)                           # il limite si esegue in questo minuto
    o.ms = T0_MS + 2 * 60_000 + 500                                                # mezzo secondo dopo
    c.annulla_tutto()
    assert c.posizioni_tutte() and c.posizioni_tutte()[0]["entrata"] == 89500.0
