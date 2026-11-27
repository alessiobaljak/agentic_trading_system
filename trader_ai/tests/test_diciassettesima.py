"""Diciassettesima revisione del trader AI (`trader_ai/revisioni/2026-11-27-diciassettesima.md`), problemi corretti il 27 novembre
2026: lo stato salvato subito dopo ogni chiusura del programma, prima di rileggere il saldo (213 del revisore, 230 del secondo
cercatore), il fermo tolto scritto nel resoconto (214), le prove che mancavano (215), il comando «chiudi» dopo una chiusura sul conto
non ancora vista (216), il motivo salvato prima di mezzanotte e chiamato dopo (231), lo stop che resta mentre si annulla il limite
(232). Le prove P1-P17 vengono dalle prove del revisore, adattate al comportamento corretto. Nessuna rete: mercato finto dei test."""
import json
import re
from datetime import datetime, timedelta, timezone

import pytest

from trader_ai.avvio import Trader
from trader_ai.conto_simulato import COMMISSIONE_MERCATO, ContoSimulato, scarto
from trader_ai.limiti import Conto, obiettivo_raggiunto
from trader_ai.messaggio import Memoria, blocco_conto
from trader_ai.modello import Esito
from trader_ai.schema import Risposta
from trader_ai.tests.test_avvio import T0, ContoFinto, Orologio, risposta
from trader_ai.tests.test_simulato import MIN, T0_MS, MercatoFinto
from trader_ai.tests.test_simulato import Orologio as OrologioMs

SC, F = scarto("BTCUSDT"), COMMISSIONE_MERCATO
SOTTO = "chiuso per l'obiettivo del giorno, ma dopo la chiusura il guadagno è sotto il 3%: si continua"
FERMO = "obiettivo del giorno raggiunto: chiuso tutto, fermo fino a mezzanotte UTC"
TOLTO = "dopo il fermo il guadagno del giorno è sceso sotto il 3%: fermo tolto, si continua"
LIM = dict(margine_usdt=100, leva=5, stop_prezzo=88500.0, tipo_ordine="limite", prezzo_limite=89500.0)


def r(azione="aspetta", **kw):
    return Risposta(azione=azione, approccio="t", cambio_approccio=False, diario="d", **kw)


def vai(m, o, fino_ms, prezzo):
    t = m.minuti[-1][0] + MIN if m.minuti else T0_MS
    while t < fino_ms - fino_ms % MIN:
        m.minuto(t, prezzo, prezzo, prezzo, prezzo)
        t += MIN
    m.prezzo = prezzo
    o.ms = fino_ms


def diario(tr):
    return [json.loads(x) for x in tr.diario.read_text().splitlines()]


def eventi(tr):
    return [e.get("evento", "") for e in diario(tr)]


def chiamate_diario(tr):
    return [e for e in diario(tr) if e.get("motivo") and "stato" in e]


def sim(tmp_path, prima=None, altre=()):
    m, o = MercatoFinto(), OrologioMs(T0_MS + 10_000)
    c = ContoSimulato(m, tmp_path / "conto_simulato.json", o)
    c.aggiorna(forza=True)
    risposte = [prima or r("apri_lungo", margine_usdt=990, leva=10, stop_prezzo=89000.0), *altre]
    messaggi = []

    def modello(system, utente):
        messaggi.append("\n\n".join(utente))
        return Esito(risposte.pop(0) if risposte else r(), "ok", {"input_tokens": 100, "output_tokens": 10})
    tr = Trader(c, modello, tmp_path / "dati", lambda: datetime.fromtimestamp(o.ms / 1000, timezone.utc))
    tr.passo()
    return tr, c, m, o, messaggi


def soglia_lungo(c):
    p = c.posizioni_tutte()[0]
    q, e, w = p["quantita"], p["entrata"], c.saldo()["portafoglio"]
    return q, (1030 - w + e * q) / (q * (1 - SC) * (1 - F))


def finto(tmp_path, risposte, t=T0, esiti=None):
    c = ContoFinto()
    chiamate = []

    def modello(system, utente):
        chiamate.append("\n\n".join(utente) if isinstance(utente, list) else utente)
        if esiti:
            return esiti.pop(0)
        return Esito(risposte.pop(0) if risposte else risposta(), "ok", {"input_tokens": 5000, "output_tokens": 2000})
    o = Orologio(t)
    return Trader(c, modello, tmp_path, o), c, chiamate, o


def portafoglio(tmp_path, valore):
    f = tmp_path / "conto_simulato.json"
    s = json.loads(f.read_text())
    s["portafoglio"] = valore
    f.write_text(json.dumps(s))
    return f


# --- 207: _annulla_limite nel ramo dell'obiettivo, anche quando solleva un errore --------------------------------------------

def test_P1_annulla_limite_esito_non_letto_poi_riprova(tmp_path):
    """Limite in attesa, conto sopra il 3% senza posizione; l'esito dell'ordine non si legge durante l'annullamento: il passo si
    interrompe. Al passo dopo: limite sparito senza esecuzione, fermo, niente aperto, nessuna operazione, nessuna chiamata."""
    tr, c, m, o, messaggi = sim(tmp_path, prima=r("apri_lungo", **LIM))
    f = portafoglio(tmp_path, 1030.5)
    vai(m, o, T0_MS + 5 * MIN + 10_000, 90000.0)
    vero = c.esito_ordine

    def rotto(cid):
        raise RuntimeError("GET /fapi/v1/fundingRate: 429: pausa")
    c.esito_ordine = rotto
    n = len(messaggi)
    with pytest.raises(RuntimeError, match="non si è potuto leggere"):
        tr.passo()
    s = json.loads(f.read_text())
    st = tr.carica()
    assert s["ordini"] == [] and s["posizione"] is None                              # il limite annullato sul conto
    assert [a["tipo"] for a in s["algo"]] == ["STOP_MARKET"]                         # lo stop resta finché non si sa (232)
    assert st["aperta"]["in_attesa"] and not st.get("fermo_fino")                  # lo stato non lo sa ancora
    c.esito_ordine = vero
    o.ms += 30_000
    tr.passo()
    st = tr.carica()
    assert st["aperta"] is None and st["fermo_fino"] and st["operazioni"] == [] and len(messaggi) == n
    assert FERMO in eventi(tr) and "ordine limite non più sul conto e mai eseguito" in eventi(tr)
    s = json.loads(f.read_text())
    assert s["posizione"] is None and s["algo"] == [] and st.get("estraneo") is None


def test_P2_limite_eseguito_e_chiusura_che_fallisce_poi_protezione(tmp_path):
    """Il limite si esegue dentro l'annullamento e la chiusura a mercato fallisce (pausa): la posizione tiene il suo stop (232;
    prima restava scoperta fino al passo dopo). Al passo dopo: chiusa per l'obiettivo, registrata una volta sola, fermo."""
    tr, c, m, o, messaggi = sim(tmp_path, prima=r("apri_lungo", **LIM))
    f = portafoglio(tmp_path, 1030.5)
    vai(m, o, T0_MS + 20 * MIN + 58_000, 90000.0)
    m.minuto(T0_MS + 20 * MIN, 90000.0, 90000.0, 89400.0, 89990.0)
    c.aggiorna(forza=True)
    o.ms = T0_MS + 21 * MIN + 500
    vero = c.chiudi

    def rotto(pos, cid):
        raise RuntimeError("GET /fapi/v1/premiumIndex: 429: pausa")
    c.chiudi = rotto
    with pytest.raises(RuntimeError, match="pausa"):
        tr.passo()
    s = json.loads(f.read_text())
    assert s["posizione"] is not None and [a["tipo"] for a in s["algo"]] == ["STOP_MARKET"]      # con il suo stop
    assert tr.carica()["aperta"]["in_attesa"]
    c.chiudi = vero
    o.ms += 30_000
    tr.passo()
    s = json.loads(f.read_text())
    st = tr.carica()
    assert s["posizione"] is None and st["aperta"] is None and st["fermo_fino"]
    assert "stop rimesso sul conto" not in eventi(tr) and eventi(tr).count("operazione chiusa") == 1
    assert len(st["operazioni"]) == 1 and st.get("estraneo") is None


def test_P3_limite_eseguito_e_chiuso_dallo_stop_dentro_l_annullamento(tmp_path):
    """Il minuto contato dentro l'annullamento esegue il limite e nello stesso minuto lo stop: la chiusura si registra una volta,
    con il modo dello stop, e il modello si chiama con quel modo (209)."""
    tr, c, m, o, messaggi = sim(tmp_path, prima=r("apri_lungo", **LIM))
    f = portafoglio(tmp_path, 1030.5)
    vai(m, o, T0_MS + 20 * MIN + 58_000, 90000.0)
    m.minuto(T0_MS + 20 * MIN, 90000.0, 90000.0, 88400.0, 88450.0)
    c.aggiorna(forza=True)
    m.prezzo = 90000.0                                         # il mark del passo resta sopra: conto al 3%
    o.ms = T0_MS + 21 * MIN + 500
    n = len(messaggi)
    tr.passo()
    s = json.loads(f.read_text())
    st = tr.carica()
    assert s["posizione"] is None and s["chiuse"][-1]["come"] == "stop"
    assert "il limite si era eseguito e chiuso prima dell'annullamento" in eventi(tr)
    assert len(st["operazioni"]) == 1 and eventi(tr).count("operazione chiusa") == 1
    assert not st.get("fermo_fino") and len(messaggi) == n + 1 and SOTTO in eventi(tr)
    motivo = chiamate_diario(tr)[-1]["motivo"]
    assert motivo.startswith(f"operazione chiusa ({st['operazioni'][-1]['come']}; dopo la chiusura il guadagno")
    assert "chiusa dal programma" not in motivo


def test_P4_limite_che_non_si_annulla_riprova_senza_fermo(tmp_path):
    """Conto finto: l'annullamento non toglie l'ordine limite (come sul demo). Il passo si interrompe ogni volta, niente fermo e
    niente chiamate; quando l'annullamento riesce, fermo."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000,
                                                   obiettivo_prezzo=92000, tipo_ordine="limite", prezzo_limite=89000)])
    tr.passo()
    c.conto = 1030.5
    vero = c.annulla_ordini
    c.annulla_ordini = lambda: None
    n = len(chiamate)
    for k in range(2):
        o.t = T0 + timedelta(minutes=5, seconds=30 * k)
        with pytest.raises(RuntimeError, match="non si è annullato"):
            tr.passo()
        assert tr.carica()["aperta"]["in_attesa"] and not tr.carica().get("fermo_fino") and len(chiamate) == n
        assert [o["tipo"] for o in c.algo] == ["STOP_MARKET"]                      # lo stop del limite resta (232)
    c.annulla_ordini = vero
    o.t += timedelta(seconds=30)
    tr.passo()
    st = tr.carica()
    assert st["fermo_fino"] and st["aperta"] is None and not c.normali and not c.algo and len(chiamate) == n


# --- 208 e 200: la finestra fra la chiusura e il salvataggio ----------------------------------------------------------------

def _saldo_che_si_rompe(c, dopo_chiudi_conto, quale=2):
    stato = {"chiuso": False, "n": 0}
    vero_chiudi, vero_saldo = c.chiudi, c.saldo

    def chiudi(pos, cid):
        e = vero_chiudi(pos, cid)
        c.conto = dopo_chiudi_conto
        stato["chiuso"] = True
        return e

    def saldo():
        if stato["chiuso"]:
            stato["n"] += 1
            if stato["n"] == quale:
                raise RuntimeError("GET /fapi/v1/fundingRate: 429: pausa")
        return vero_saldo()
    c.chiudi, c.saldo = chiudi, saldo
    return vero_chiudi, vero_saldo


@pytest.mark.parametrize("quale", [1, 2])
@pytest.mark.parametrize("dopo, fermo", [(1029.0, False), (1031.0, True)])
def test_P5_lettura_del_saldo_dopo_la_chiusura_che_fallisce(tmp_path, dopo, fermo, quale):
    """Il programma chiude per l'obiettivo e registra; la lettura del saldo DOPO la registrazione (avvio.py:318) fallisce. Corretto:
    la chiusura del programma resta nello stato (modo «obiettivo del giorno (chiusa dal programma)»), si registra una volta."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000)])
    tr.passo()
    c.conto = 1031.0
    vc, vs = _saldo_che_si_rompe(c, dopo, quale)          # 1: la lettura per registrare; 2: quella dopo la registrazione
    o.t = T0 + timedelta(minutes=5)
    with pytest.raises(RuntimeError, match="pausa"):
        tr.passo()
    c.chiudi, c.saldo = vc, vs
    o.t += timedelta(seconds=30)
    tr.passo()
    st = tr.carica()
    print("modi registrati:", [x["come"] for x in st["operazioni"]], "| eventi 'operazione chiusa':",
          eventi(tr).count("operazione chiusa"), "| motivo:", chiamate_diario(tr)[-1]["motivo"] if not fermo else "-")
    assert eventi(tr).count("operazione chiusa") == 1
    assert st["operazioni"][-1]["come"] == "obiettivo del giorno (chiusa dal programma)"


# --- il fermo che si toglie --------------------------------------------------------------------------------------------------

def test_P6_funding_vero_in_ritardo_toglie_il_fermo_una_volta(tmp_path):
    """Conto simulato vero: chiusura al 3% e fermo; il funding delle 10:04 (posizione aperta in quel momento) si pubblica dopo la
    chiusura e porta il guadagno sotto il 3%: fermo tolto una volta, chiamata con il perché, nessuna chiamata in più dopo; il
    funding si applica una volta sola."""
    tr, c, m, o, messaggi = sim(tmp_path)
    q, soglia = soglia_lungo(c)
    vai(m, o, T0_MS + 5 * MIN + 10_000, soglia + 0.5)
    tr.passo()
    st = tr.carica()
    assert st["fermo_fino"] and not c.posizioni_tutte()
    m.pagamenti.append((T0_MS + 4 * MIN, 0.0005, 90000.0))                # pagato dal lungo: circa 4,95
    n = len(messaggi)
    vai(m, o, o.ms + 30_000, m.prezzo)
    tr.passo()
    st = tr.carica()
    assert not st.get("fermo_fino") and not st.get("obiettivo_ora") and eventi(tr).count(TOLTO) == 1
    assert len(messaggi) == n + 1 and chiamate_diario(tr)[-1]["motivo"].startswith("fermo tolto: ")
    assert "richiama" not in st
    for _ in range(3):
        vai(m, o, o.ms + 30_000, m.prezzo)
        tr.passo()
    assert eventi(tr).count(TOLTO) == 1 and len(messaggi) == n + 1
    s = json.loads((tmp_path / "conto_simulato.json").read_text())
    assert s["funding_applicati"].count(T0_MS + 4 * MIN) == 1
    assert [x["cosa"] for x in s["movimenti"]].count("funding") == 1


def test_P7_fermo_tolto_e_passo_interrotto(tmp_path):
    """Fermo tolto e candele che non arrivano: lo stato salvato ha il fermo tolto e il motivo; al passo dopo il modello si chiama
    con il perché, l'evento non si ripete."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000)])
    tr.passo()
    c.conto = 1031.0
    o.t = T0 + timedelta(minutes=5)
    tr.passo()
    assert tr.carica()["fermo_fino"]
    c.conto = 1029.06
    candele = c.candele

    def rotte(*a, **k):
        raise RuntimeError("GET /fapi/v1/klines: 429: pausa")
    c.candele = rotte
    o.t += timedelta(seconds=30)
    n = len(chiamate)
    with pytest.raises(RuntimeError):
        tr.passo()
    st = tr.carica()
    assert not st.get("fermo_fino") and st["richiama"].startswith("fermo tolto: ")
    c.candele = candele
    o.t += timedelta(seconds=30)
    tr.passo()
    st = tr.carica()
    assert len(chiamate) == n + 1 and chiamate_diario(tr)[-1]["motivo"].startswith("fermo tolto: ")
    assert eventi(tr).count(TOLTO) == 1 and "richiama" not in st


def test_P8_fermo_con_funding_positivo_resta(tmp_path):
    """Un funding ricevuto durante il fermo alza il conto: il fermo resta."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000)])
    tr.passo()
    c.conto = 1031.0
    o.t = T0 + timedelta(minutes=5)
    tr.passo()
    c.conto = 1032.0
    n = len(chiamate)
    o.t += timedelta(minutes=20)
    tr.passo()
    assert tr.carica()["fermo_fino"] and len(chiamate) == n and TOLTO not in eventi(tr)


# --- il richiamo: non si ripete, non resta vecchio ------------------------------------------------------------------------

def _chiusa_da_sola(tr, c, o):
    a = tr.carica()["aperta"]
    c.pos, c.algo, c.conto = None, [], 990.0
    c.esiti[a["cid"]] = {"stato": "chiusa", "come": "stop", "entrata": 90000.0, "quantita": a["quantita"],
                         "eseguita_ms": int(T0.timestamp() * 1000), "chiusa_ms": int(T0.timestamp() * 1000) + 240_000,
                         "uscita": 88000.0, "spese_entrata": 0.2, "spese": 0.4, "funding": 0.0, "risultato_prezzo": -9.6,
                         "netto": -10.0}


def test_P9_chiusura_trovata_ed_errore_del_modello_nessun_richiamo_ripetuto(tmp_path):
    esiti = [Esito(risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000), "ok",
                   {"input_tokens": 5000, "output_tokens": 2000}),
             Esito(None, "errore", dettaglio="APIConnectionError: giù")]
    tr, c, chiamate, o = finto(tmp_path, [], esiti=esiti)
    tr.passo()
    _chiusa_da_sola(tr, c, o)
    o.t = T0 + timedelta(minutes=5)
    tr.passo()
    st = tr.carica()
    assert len(chiamate) == 2 and "richiama" not in st and "non è stata letta" in (st.get("ultimo_scarto") or "")
    o.t += timedelta(seconds=30)
    tr.passo()
    assert len(chiamate) == 2


def test_P10_chiusura_trovata_e_tetto_finito(tmp_path):
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000)])
    tr.passo()
    tr.budget.registra(T0, 5.0)
    _chiusa_da_sola(tr, c, o)
    o.t = T0 + timedelta(minutes=5)
    tr.passo()
    st = tr.carica()
    assert len(chiamate) == 1 and "richiama" not in st and chiamate_diario(tr)[-1]["stato"] == "tetto"
    assert chiamate_diario(tr)[-1]["motivo"] == f"operazione chiusa ({st['operazioni'][-1]['come']})"


def test_P11_chiusura_trovata_e_conto_esaurito(tmp_path):
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000)])
    tr.passo()
    _chiusa_da_sola(tr, c, o)
    c.disp = 5.0
    o.t = T0 + timedelta(minutes=5)
    tr.passo()
    st = tr.carica()
    assert st["esaurito"] is True and len(chiamate) == 1 and "richiama" not in st


def test_P12_chiusura_trovata_a_mezzanotte_e_passo_interrotto(tmp_path):
    """La chiusura trovata nel primo passo dopo mezzanotte (chiusa alle 23:59) e il passo interrotto: al passo dopo la
    chiusura non si registra due volte, sta nel resoconto del giorno prima, il modello si chiama con il motivo."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000)])
    tr.passo()
    a = tr.carica()["aperta"]
    c.pos, c.algo, c.conto = None, [], 990.0
    fine = int(datetime(2026, 11, 24, 23, 59, 30, tzinfo=timezone.utc).timestamp() * 1000)
    c.esiti[a["cid"]] = {"stato": "chiusa", "come": "stop", "entrata": 90000.0, "quantita": a["quantita"],
                         "eseguita_ms": int(T0.timestamp() * 1000), "chiusa_ms": fine, "uscita": 88000.0,
                         "spese_entrata": 0.2, "spese": 0.4, "funding": 0.0, "risultato_prezzo": -9.6, "netto": -10.0}
    candele = c.candele

    def rotte(*a, **k):
        raise RuntimeError("GET /fapi/v1/klines: 429: pausa")
    c.candele = rotte
    o.t = datetime(2026, 11, 25, 0, 0, 20, tzinfo=timezone.utc)
    with pytest.raises(RuntimeError):
        tr.passo()
    c.candele = candele
    o.t += timedelta(seconds=30)
    n = len(chiamate)
    tr.passo()
    st = tr.carica()
    assert len(st["operazioni"]) == 1 and eventi(tr).count("operazione chiusa") == 1 and len(chiamate) == n + 1
    assert chiamate_diario(tr)[-1]["motivo"].startswith("operazione chiusa (")
    res = (tr.cartella / "resoconti" / "2026-11-24.md").read_text()
    assert "Operazioni chiuse: 1" in res
    print("eventi 'giorno nuovo':", eventi(tr).count("giorno nuovo"))


# --- il centesimo e «mancano» ---------------------------------------------------------------------------------------------

def test_P13_mancano_zero_se_e_solo_se_raggiunto():
    """Su una griglia di conti a mezzanotte e guadagni intorno al 3%: «mancano 0.00» nel messaggio se e solo se
    obiettivo_raggiunto (la stessa regola per il modello e per il programma)."""
    mem = Memoria([], [], [], None, None, {"giorno": "2026-11-24", "conto": 1000.0}, "2026-11-24")
    ora = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)
    errori = []
    for cm in (1000.0, 999.84, 1000.1333, 1234.567, 987.65, 1016.6666, 1.0e4 / 3):
        for k in range(-300, 301):
            netto = cm * 0.03 + k * 0.00007
            for spese in (0.0, 0.4321):
                c = Conto(cm + netto + spese, cm, cm, None, spese)
                testo = blocco_conto(c, 90000.0, None, mem, "BTCUSDT", {}, ora)
                manca = float(re.search(r"mancano (-?[0-9.]+)", testo).group(1))
                if (manca == 0.0) != obiettivo_raggiunto(c) or manca < 0:
                    errori.append((cm, netto, spese, manca, obiettivo_raggiunto(c)))
    assert errori == []


def test_P14_giro_decidi_usa_lo_stesso_centesimo(tmp_path):
    """giro.decidi con un guadagno di 29,996 (al centesimo 30,00): «obiettivo», nessuna chiamata."""
    from trader_ai.costi import Budget
    from trader_ai.giro import decidi
    b = Budget(tmp_path / "spesa.json")
    chiamate = []
    ris = decidi(T0, "x", b, Conto(1029.996, 1000.0, 1000.0), 90000.0, lambda: chiamate.append(1), 0.1)
    assert ris.stato == "obiettivo" and chiamate == []
    ris = decidi(T0, "x", b, Conto(1029.994, 1000.0, 1000.0), 90000.0,
                 lambda: Esito(r(), "ok", {"input_tokens": 1, "output_tokens": 1}), 0.1)
    assert ris.stato == "ok"


# --- prove aggiunte dopo le mutazioni vive R3, R4, R5 -----------------------------------------------------------------------

LIMITE_F = dict(margine_usdt=100, leva=5, stop_prezzo=88000, obiettivo_prezzo=92000, tipo_ordine="limite", prezzo_limite=89000)


def _dopo(c, nome, dopo):
    vero = getattr(c, nome)

    def f(*a, **k):
        e = vero(*a, **k)
        dopo()
        return e
    setattr(c, nome, f)
    return vero


def test_P15_fermo_resta_con_il_guadagno_che_scende_a_29_998(tmp_path):
    """Durante il fermo il conto scende a +29,998 (al centesimo 30,00): è ancora il 3%, il fermo resta; nessun ciclo
    fermo/sfermo nei passi dopo (mutazione R4)."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000)])
    tr.passo()
    c.conto = 1031.0
    o.t = T0 + timedelta(minutes=5)
    tr.passo()
    assert tr.carica()["fermo_fino"]
    c.conto = 1029.998
    n = len(chiamate)
    for k in range(3):
        o.t += timedelta(seconds=30)
        tr.passo()
    st = tr.carica()
    assert st["fermo_fino"] and TOLTO not in eventi(tr) and eventi(tr).count(FERMO) == 1 and len(chiamate) == n


def test_P16_limite_annullato_con_operazioni_vecchie_in_memoria(tmp_path):
    """Un'operazione già chiusa in memoria, poi un limite in attesa annullato per l'obiettivo e il conto che scende sotto il 3%:
    il motivo dice «nessuna operazione», non il modo dell'operazione vecchia (mutazione R5)."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000),
                                          risposta("chiudi"), risposta("apri_lungo", **LIMITE_F)])
    tr.passo()
    o.t = T0 + timedelta(minutes=15)
    tr.passo()                                                    # il modello chiude: un'operazione in memoria
    o.t += timedelta(seconds=30)
    tr.passo()                                                    # richiamato: mette il limite
    st = tr.carica()
    assert len(st["operazioni"]) == 1 and st["aperta"]["in_attesa"]
    c.conto = 1030.5
    _dopo(c, "annulla_tutto", lambda: setattr(c, "conto", 1029.9))
    o.t += timedelta(minutes=5)
    tr.passo()
    st = tr.carica()
    assert len(st["operazioni"]) == 1 and not st.get("fermo_fino")
    assert chiamate_diario(tr)[-1]["motivo"].startswith(
        "ordine limite annullato dal programma per l'obiettivo del giorno (nessuna operazione); dopo l'annullamento")


def test_P17_limite_annullato_sotto_il_3_e_passo_interrotto(tmp_path):
    """Limite annullato per l'obiettivo, conto sotto il 3%, candele che non arrivano: lo stato salvato ha il motivo; al passo
    dopo il modello si chiama con quello (mutazione R3)."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", **LIMITE_F)])
    tr.passo()
    c.conto = 1030.5
    _dopo(c, "annulla_tutto", lambda: setattr(c, "conto", 1029.9))
    candele = c.candele

    def rotte(*a, **k):
        raise RuntimeError("GET /fapi/v1/klines: 429: pausa")
    c.candele = rotte
    o.t = T0 + timedelta(minutes=5)
    with pytest.raises(RuntimeError):
        tr.passo()
    st = tr.carica()
    assert st["aperta"] is None and (st.get("richiama") or "").startswith("ordine limite annullato dal programma")
    c.candele = candele
    o.t += timedelta(seconds=30)
    n = len(chiamate)
    tr.passo()
    assert len(chiamate) == n + 1 and chiamate_diario(tr)[-1]["motivo"].startswith("ordine limite annullato dal programma")




# --- prove nuove della sessione ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("quando, atteso", [
    (datetime(2026, 11, 24, 23, 59, 40, tzinfo=timezone.utc),
     "non raggiunto; prima, alle 23:59 UTC, il 3% era arrivato ma il fermo si è tolto alle 23:59 UTC (guadagno sceso a +29.06)"),
    (datetime(2026, 11, 25, 0, 0, 10, tzinfo=timezone.utc), "raggiunto alle 23:59 UTC, poi il conto è sceso sotto il 3% (+29.06)")])
def test_214_resoconto_dice_il_fermo_tolto_in_tutti_e_due_i_casi(tmp_path, quando, atteso):
    """Lo stesso funding visto 30 secondi prima o dopo mezzanotte: tutti e due i resoconti dicono che il 3% era arrivato e che poi
    il conto è sceso."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000)])
    tr.passo()
    c.conto = 1031.0
    o.t = datetime(2026, 11, 24, 23, 59, 10, tzinfo=timezone.utc)
    tr.passo()
    c.conto = 1029.06
    o.t = quando
    tr.passo()
    if quando.day == 24:
        o.t = datetime(2026, 11, 25, 0, 0, 10, tzinfo=timezone.utc)
        tr.passo()
    res = (tr.cartella / "resoconti" / "2026-11-24.md").read_text()
    riga = [x for x in res.splitlines() if x.startswith("* Obiettivo")][0]
    assert riga == f"* Obiettivo del 3% (30.00 USDT): {atteso}"
    assert "fermi_tolti" not in tr.carica()                       # il giorno nuovo riparte pulito


def test_214_fermo_tolto_e_poi_3_per_cento_di_nuovo(tmp_path):
    """Fermo tolto alle 10:06, poi il 3% di nuovo alle 10:20: «raggiunto alle 10:20» e il fermo tolto di prima."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000),
                                          risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000)])
    tr.passo()
    c.conto = 1031.0
    o.t = T0 + timedelta(minutes=5)
    tr.passo()
    c.conto = 1029.06
    o.t += timedelta(seconds=30)
    tr.passo()                                                    # fermo tolto: il modello riapre
    assert c.pos is not None and not tr.carica().get("fermo_fino")
    c.conto = 1031.5
    o.t = T0 + timedelta(minutes=19)
    tr.passo()
    assert tr.carica()["fermo_fino"]
    o.t = datetime(2026, 11, 25, 0, 0, 10, tzinfo=timezone.utc)
    tr.passo()
    res = (tr.cartella / "resoconti" / "2026-11-24.md").read_text()
    riga = [x for x in res.splitlines() if x.startswith("* Obiettivo")][0]
    assert riga == ("* Obiettivo del 3% (30.00 USDT): raggiunto alle 10:20 UTC; prima, alle 10:06 UTC, il 3% era arrivato ma il "
                    "fermo si è tolto alle 10:06 UTC (guadagno sceso a +29.06)")


def test_216_chiudi_a_mano_dopo_una_chiusura_sul_conto_non_ancora_vista(tmp_path):
    """L'operazione si chiude da sola sul conto (stop) e il proprietario lancia «chiudi» prima che un passo la veda: si registra
    con l'esito del conto (prima spariva dalla memoria e dal resoconto)."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000)])
    tr.passo()
    _chiusa_da_sola(tr, c, o)
    o.t = T0 + timedelta(minutes=2)
    tr.chiudi_tutto_e_ferma(attesa_blocco_s=1.0)
    st = tr.carica()
    assert st["aperta"] is None and len(st["operazioni"]) == 1
    op = st["operazioni"][0]
    assert op["uscita"] == 88000.0 and op["risultato"] == -10.0 and not op["uscita_stimata"] and op["come"] == "stop iniziale"


def test_216_chiudi_a_mano_con_un_limite_eseguito_e_chiuso_prima(tmp_path):
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", **LIMITE_F)])
    tr.passo()
    a = tr.carica()["aperta"]
    c.normali, c.algo, c.conto = [], [], 995.0
    c.esiti[a["cid"]] = {"stato": "chiusa", "come": "stop", "entrata": 89000.0, "quantita": a["quantita"],
                         "eseguita_ms": int(T0.timestamp() * 1000) + 60_000, "chiusa_ms": int(T0.timestamp() * 1000) + 120_000,
                         "uscita": 88000.0, "spese_entrata": 0.1, "spese": 0.3, "funding": 0.0, "risultato_prezzo": -4.7,
                         "netto": -5.0}
    o.t = T0 + timedelta(minutes=3)
    tr.chiudi_tutto_e_ferma(attesa_blocco_s=1.0)
    st = tr.carica()
    assert st["aperta"] is None and len(st["operazioni"]) == 1 and st["operazioni"][0]["risultato"] == -5.0


def test_216_chiudi_a_mano_con_un_limite_mai_eseguito(tmp_path):
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", **LIMITE_F)])
    tr.passo()
    o.t = T0 + timedelta(minutes=3)
    tr.chiudi_tutto_e_ferma(attesa_blocco_s=1.0)
    st = tr.carica()
    assert st["aperta"] is None and st["operazioni"] == [] and not c.normali and not c.algo


def test_231_motivo_di_ieri_chiamato_dopo_mezzanotte(tmp_path):
    """Ramo «sotto il 3%» alle 23:58:30, candele che non arrivano; il passo dopo è alle 00:08:40: il motivo dice che i numeri del
    3% erano del giorno prima."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000)])
    tr.passo()
    c.conto = 1031.0
    _dopo(c, "chiudi", lambda: setattr(c, "conto", 1029.0))
    candele = c.candele

    def rotte(*a, **k):
        raise RuntimeError("GET /fapi/v1/klines: 429: pausa")
    c.candele = rotte
    o.t = datetime(2026, 11, 24, 23, 58, 30, tzinfo=timezone.utc)
    with pytest.raises(RuntimeError):
        tr.passo()
    assert tr.carica()["richiama_giorno"] == "2026-11-24"
    c.candele = candele
    o.t = datetime(2026, 11, 25, 0, 8, 40, tzinfo=timezone.utc)
    n = len(chiamate)
    tr.passo()
    st = tr.carica()
    assert len(chiamate) == n + 1 and "richiama" not in st and "richiama_giorno" not in st
    assert chiamate_diario(tr)[-1]["motivo"] == (
        "operazione chiusa (obiettivo del giorno (chiusa dal programma); dopo la chiusura il guadagno del giorno è +29.00 USDT, "
        "sotto il 3% (30.00): l'obiettivo non è raggiunto) (numeri del giorno 2026-11-24, prima della mezzanotte UTC: da "
        "mezzanotte il giorno è nuovo)")


def test_231_motivo_dello_stesso_giorno_senza_nota(tmp_path):
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000)])
    tr.passo()
    c.conto = 1031.0
    _dopo(c, "chiudi", lambda: setattr(c, "conto", 1029.0))
    candele = c.candele

    def rotte(*a, **k):
        raise RuntimeError("GET /fapi/v1/klines: 429: pausa")
    c.candele = rotte
    o.t = T0 + timedelta(minutes=5)
    with pytest.raises(RuntimeError):
        tr.passo()
    c.candele = candele
    o.t += timedelta(seconds=30)
    tr.passo()
    assert chiamate_diario(tr)[-1]["motivo"].endswith("l'obiettivo non è raggiunto)")


@pytest.mark.parametrize("quale", [1, 2])
def test_230_protezione_che_chiude_e_saldo_che_non_si_legge(tmp_path, quale):
    """La protezione chiude (stop sparito e prezzo già oltre) e una lettura del saldo dopo la chiusura fallisce (la prima, dentro
    la protezione, che scrive l'errore e va avanti; o la seconda, dopo, che interrompe il passo): al passo dopo l'operazione è
    registrata una volta sola, con il modo del programma, e il modello si chiama per la chiusura."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000)])
    tr.passo()
    c.algo, c.prezzo = [], 87900.0
    stato = {"chiuso": False, "n": 0}
    vero_chiudi, vero_saldo = c.chiudi, c.saldo

    def chiudi(pos, cid):
        stato["chiuso"] = True
        return vero_chiudi(pos, cid)

    def saldo():
        if stato["chiuso"]:
            stato["n"] += 1
            if stato["n"] == quale:
                raise RuntimeError("GET /fapi/v2/account: 429: pausa")
        return vero_saldo()
    c.chiudi, c.saldo = chiudi, saldo
    o.t = T0 + timedelta(minutes=2)
    if quale == 1:
        tr.passo()
        assert "protezione non riuscita" in eventi(tr)
    else:
        with pytest.raises(RuntimeError, match="pausa"):
            tr.passo()
    a = tr.carica()["aperta"]
    assert c.pos is None and c.chiusure == 1
    if quale == 1:                                               # chiusa ma non registrata: il modo del programma resta
        assert a["chiusa_da"] == "chiusa: senza stop valido sul conto"
    else:                                                        # registrata e salvata con il motivo prima della lettura
        assert a is None and tr.carica()["richiama"] == "operazione chiusa (chiusa: senza stop valido sul conto)"
    c.chiudi, c.saldo = vero_chiudi, vero_saldo
    o.t += timedelta(seconds=30)
    n = len(chiamate)
    tr.passo()
    st = tr.carica()
    assert len(st["operazioni"]) == 1 and st["operazioni"][0]["come"] == "chiusa: senza stop valido sul conto"
    assert eventi(tr).count("operazione chiusa") == 1 and c.chiusure == 1
    assert len(chiamate) == n + 1 and chiamate_diario(tr)[-1]["motivo"] == "operazione chiusa (chiusa: senza stop valido sul conto)"


def test_232_annulla_ordini_del_demo_tocca_solo_gli_ordini_normali():
    from trader_ai.conto_demo import ContoDemo
    from trader_ai.tests.test_avvio import _R
    visti = []

    def http(metodo, url, headers, timeout, allow_redirects):
        visti.append((metodo, url.split("?", 1)[0]))
        return _R(200, {"code": 200})
    ContoDemo("k", "s", "BTCUSDT", http).annulla_ordini()
    assert visti == [("DELETE", "https://demo-fapi.binance.com/fapi/v1/allOpenOrders")]          # niente algoOpenOrders


@pytest.mark.parametrize("minimo, eseguito", [(89600.0, False), (89400.0, True)])
def test_232_annulla_ordini_del_simulato_lascia_stop_e_conta_prima_i_minuti(tmp_path, minimo, eseguito):
    """Il conto simulato: prima i minuti chiusi con il limite al suo posto (si esegue se il prezzo lo ha toccato), poi via il solo
    limite; lo stop resta in tutti e due i casi."""
    tr, c, m, o, messaggi = sim(tmp_path, prima=r("apri_lungo", **LIM))
    f = tmp_path / "conto_simulato.json"
    vai(m, o, T0_MS + 3 * MIN + 30_000, 90000.0)
    c.aggiorna(forza=True)
    m.minuto(T0_MS + 3 * MIN, 90000.0, 90000.0, minimo, 90000.0)
    o.ms = T0_MS + 4 * MIN + 500
    c.annulla_ordini()
    s = json.loads(f.read_text())
    assert s["ordini"] == [] and [a["tipo"] for a in s["algo"]] == ["STOP_MARKET"]
    assert (s["posizione"] is not None) is eseguito


def test_213_limite_annullato_e_saldo_che_non_si_legge(tmp_path):
    """Il limite si annulla per l'obiettivo (nessuna operazione) e la lettura del saldo dopo fallisce: lo stato salvato sa già che
    il limite è annullato e perché; al passo dopo il modello si chiama con quel motivo."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", **LIMITE_F)])
    tr.passo()
    c.conto = 1030.5
    rotto = {"si": False}
    vero_saldo = c.saldo

    def saldo():
        if rotto["si"]:
            rotto["si"] = False
            raise RuntimeError("GET /fapi/v2/account: 429: pausa")
        return vero_saldo()
    c.saldo = saldo

    def dopo():
        c.conto, rotto["si"] = 1029.9, True
    _dopo(c, "annulla_tutto", dopo)
    o.t = T0 + timedelta(minutes=5)
    with pytest.raises(RuntimeError, match="pausa"):
        tr.passo()
    st = tr.carica()
    assert st["aperta"] is None and st["richiama"] == (
        "ordine limite annullato dal programma per l'obiettivo del giorno (nessuna operazione)")
    o.t += timedelta(seconds=30)
    n = len(chiamate)
    tr.passo()
    assert len(chiamate) == n + 1 and chiamate_diario(tr)[-1]["motivo"] == (
        "ordine limite annullato dal programma per l'obiettivo del giorno (nessuna operazione)")


def test_230_limite_eseguito_nell_annullamento_chiuso_e_saldo_che_non_si_legge(tmp_path):
    """Il limite si esegue dentro l'annullamento per l'obiettivo, il programma lo chiude a mercato e la lettura del saldo per
    registrare fallisce: lo stato salvato ha già la chiusura del programma; al passo dopo si registra una volta, con quel modo."""
    tr, c, m, o, messaggi = sim(tmp_path, prima=r("apri_lungo", **LIM))
    f = portafoglio(tmp_path, 1030.5)
    vai(m, o, T0_MS + 20 * MIN + 58_000, 90000.0)
    m.minuto(T0_MS + 20 * MIN, 90000.0, 90000.0, 89400.0, 89990.0)
    c.aggiorna(forza=True)
    o.ms = T0_MS + 21 * MIN + 500
    stato = {"chiuso": False}
    vero_chiudi, vero_saldo = c.chiudi, c.saldo

    def chiudi(pos, cid):
        e = vero_chiudi(pos, cid)
        stato["chiuso"] = bool(e)
        return e

    def saldo():
        if stato["chiuso"]:
            stato["chiuso"] = False
            raise RuntimeError("GET /fapi/v1/fundingRate: 429: pausa")
        return vero_saldo()
    c.chiudi, c.saldo = chiudi, saldo
    with pytest.raises(RuntimeError, match="pausa"):
        tr.passo()
    c.chiudi, c.saldo = vero_chiudi, vero_saldo
    a = tr.carica()["aperta"]
    assert json.loads(f.read_text())["posizione"] is None and a["chiusa_da"] == "chiusa: limite eseguito durante l'annullamento"
    o.ms += 30_000
    tr.passo()
    st = tr.carica()
    assert len(st["operazioni"]) == 1 and st["operazioni"][0]["come"] == "chiusa: limite eseguito durante l'annullamento"
    assert eventi(tr).count("operazione chiusa") == 1


def test_216_chiudi_a_mano_con_un_ordine_a_mercato_mai_eseguito(tmp_path):
    """Un ordine a mercato inviato senza risposta e mai eseguito (nessuna posizione): il comando «chiudi» non inventa
    un'operazione chiusa."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000)])
    tr.passo()
    st = tr.carica()
    a = st["aperta"]
    for k in ("eseguita", "stop_iniziale", "spese_entrata", "R"):
        a.pop(k, None)
    a["inviata"] = True
    tr.salva(st)
    c.pos, c.algo = None, []
    o.t = T0 + timedelta(minutes=2)
    tr.chiudi_tutto_e_ferma(attesa_blocco_s=1.0)
    st = tr.carica()
    assert st["aperta"] is None and st["operazioni"] == []


def test_231_fermo_tolto_prima_di_mezzanotte_e_chiamato_dopo(tmp_path):
    """Il fermo si toglie alle 23:59:40 e il passo si interrompe; il passo dopo è alle 00:05: il motivo dice che i numeri del 3%
    erano del giorno prima."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000)])
    tr.passo()
    c.conto = 1031.0
    o.t = datetime(2026, 11, 24, 23, 59, 10, tzinfo=timezone.utc)
    tr.passo()
    c.conto = 1029.06
    candele = c.candele

    def rotte(*a, **k):
        raise RuntimeError("GET /fapi/v1/klines: 429: pausa")
    c.candele = rotte
    o.t = datetime(2026, 11, 24, 23, 59, 40, tzinfo=timezone.utc)
    with pytest.raises(RuntimeError):
        tr.passo()
    c.candele = candele
    o.t = datetime(2026, 11, 25, 0, 5, 0, tzinfo=timezone.utc)
    tr.passo()
    assert chiamate_diario(tr)[-1]["motivo"].startswith("fermo tolto: ")
    assert chiamate_diario(tr)[-1]["motivo"].endswith("(numeri del giorno 2026-11-24, prima della mezzanotte UTC: da mezzanotte il "
                                                     "giorno è nuovo)")


# --- dalla diciottesima revisione (problema 245: prove del revisore Q15-Q18) ---------------------------------------------

def test_Q15_fermo_tolto_chiamata_e_chiusura_del_modello_nello_stesso_passo_poi_mezzanotte(tmp_path):
    """X8: il fermo si toglie alle 23:59:40, il modello si chiama nello stesso passo, apre e il conto rifiuta lo stop (chiusa
    subito). Il passo dopo è alle 00:00:10: il motivo è la chiusura, senza la nota del giorno prima."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000),
                                          risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000)])
    tr.passo()
    c.conto = 1031.0
    o.t = datetime(2026, 11, 24, 23, 59, 10, tzinfo=timezone.utc)
    tr.passo()
    c.conto = 1029.06
    c.rifiuta_stop = True
    o.t = datetime(2026, 11, 24, 23, 59, 40, tzinfo=timezone.utc)
    tr.passo()
    assert tr.carica()["richiama"] == "operazione chiusa (chiusa: stop rifiutato dal conto)"
    c.rifiuta_stop = False
    o.t = datetime(2026, 11, 25, 0, 0, 10, tzinfo=timezone.utc)
    tr.passo()
    assert chiamate_diario(tr)[-1]["motivo"] == "operazione chiusa (chiusa: stop rifiutato dal conto)"


def test_Q16_resoconto_ora_del_3_e_ora_del_fermo_tolto_diverse(tmp_path):
    """X16: 3% alle 10:06, fermo tolto alle 10:20: il resoconto dice tutte e due le ore."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000)])
    tr.passo()
    c.conto = 1031.0
    o.t = T0 + timedelta(minutes=5)
    tr.passo()
    c.conto = 1029.06
    o.t = T0 + timedelta(minutes=19)
    tr.passo()
    o.t = datetime(2026, 11, 25, 0, 0, 10, tzinfo=timezone.utc)
    tr.passo()
    res = (tr.cartella / "resoconti" / "2026-11-24.md").read_text()
    riga = [x for x in res.splitlines() if x.startswith("* Obiettivo")][0]
    assert "alle 10:06 UTC, il 3% era arrivato ma il fermo si è tolto alle 10:20 UTC" in riga


def test_Q17_chiudi_a_mano_limite_eseguito_e_chiuso_con_i_dati_dell_esecuzione(tmp_path):
    """X15: il limite eseguito e chiuso prima del «chiudi» entra in memoria con l'ora d'esecuzione e il rischio (1 R)."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", **LIMITE_F)])
    tr.passo()
    a = tr.carica()["aperta"]
    c.normali, c.algo, c.conto = [], [], 995.0
    c.esiti[a["cid"]] = {"stato": "chiusa", "come": "stop", "entrata": 89000.0, "quantita": a["quantita"],
                         "eseguita_ms": int(T0.timestamp() * 1000) + 60_000, "chiusa_ms": int(T0.timestamp() * 1000) + 120_000,
                         "uscita": 88000.0, "spese_entrata": 0.1, "spese": 0.3, "funding": 0.0, "risultato_prezzo": -4.7,
                         "netto": -5.0}
    o.t = T0 + timedelta(minutes=3)
    tr.chiudi_tutto_e_ferma(attesa_blocco_s=1.0)
    op = tr.carica()["operazioni"][0]
    assert op["eseguita"] == (T0 + timedelta(seconds=60)).isoformat() and op.get("R") and op["come"] == "stop iniziale"


def test_Q18_limite_annullato_sotto_il_3_e_passo_interrotto_motivo_intero(tmp_path):
    """R3 della diciassettesima: il motivo salvato prima della chiamata è quello intero (con il guadagno sotto il 3%), non quello
    provvisorio."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", **LIMITE_F)])
    tr.passo()
    c.conto = 1030.5
    _dopo(c, "annulla_tutto", lambda: setattr(c, "conto", 1029.9))
    candele = c.candele

    def rotte(*a, **k):
        raise RuntimeError("GET /fapi/v1/klines: 429: pausa")
    c.candele = rotte
    o.t = T0 + timedelta(minutes=5)
    with pytest.raises(RuntimeError):
        tr.passo()
    assert tr.carica()["richiama"] == ("ordine limite annullato dal programma per l'obiettivo del giorno (nessuna operazione); "
                                       "dopo l'annullamento il guadagno del giorno è +29.90 USDT, sotto il 3% (30.00): l'obiettivo "
                                       "non è raggiunto")
