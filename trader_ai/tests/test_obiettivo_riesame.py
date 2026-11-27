"""Riesame della sedicesima revisione (`trader_ai/revisioni/2026-11-26-sedicesima.md`, sezione «### Riesame»), problemi corretti il
27 novembre 2026: il limite in attesa che si esegue mentre il programma lo annulla per l'obiettivo (207 del revisore, 211 del
secondo cercatore), lo stato salvato prima della chiamata dopo una chiusura (208 e 200), il motivo della chiamata (209), il
centesimo come regola sola (210 del revisore, 208 del secondo cercatore), il funding pagato dopo il fermo (210 del secondo
cercatore) e i casi senza test (211 del revisore). Conto simulato vero o conto finto dei test, mercato finto, nessuna rete. Le prove
A1-A5, B1, C1, D1, E1, E2 e F1 vengono dalle prove del revisore, con le asserzioni del comportamento corretto."""
import json
from datetime import datetime, timedelta, timezone

import pytest

from trader_ai.avvio import Trader
from trader_ai.conto_simulato import COMMISSIONE_MERCATO, ContoSimulato, scarto
from trader_ai.limiti import Conto, obiettivo_raggiunto
from trader_ai.modello import Esito
from trader_ai.schema import Risposta
from trader_ai.tests.test_avvio import T0, ContoFinto, Orologio, risposta
from trader_ai.tests.test_simulato import MIN, T0_MS, MercatoFinto
from trader_ai.tests.test_simulato import Orologio as OrologioMs

SC, F = scarto("BTCUSDT"), COMMISSIONE_MERCATO
SOTTO = "chiuso per l'obiettivo del giorno, ma dopo la chiusura il guadagno è sotto il 3%: si continua"
FERMO = "obiettivo del giorno raggiunto: chiuso tutto, fermo fino a mezzanotte UTC"
TOLTO = "dopo il fermo il guadagno del giorno è sceso sotto il 3%: fermo tolto, si continua"


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
    """Conto simulato vero; alle 10:00:10 del 24 novembre il modello apre (di base: lungo, leva 10, 990 di margine)."""
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
    """Prezzo mark a cui il guadagno dopo le spese di chiusura (commissione e scarto d'uscita) arriva a 30."""
    p = c.posizioni_tutte()[0]
    q, e, w = p["quantita"], p["entrata"], c.saldo()["portafoglio"]
    return q, (1030 - w + e * q) / (q * (1 - SC) * (1 - F))


def finto(tmp_path, risposte, t=T0):
    c = ContoFinto()
    chiamate = []

    def modello(system, utente):
        chiamate.append("\n\n".join(utente) if isinstance(utente, list) else utente)
        return Esito(risposte.pop(0) if risposte else risposta(), "ok", {"input_tokens": 5000, "output_tokens": 2000})
    o = Orologio(t)
    return Trader(c, modello, tmp_path, o), c, chiamate, o


def dopo_il_metodo(c, nome, dopo):
    vero = getattr(c, nome)

    def f(*a, **k):
        e = vero(*a, **k)
        dopo()
        return e
    setattr(c, nome, f)


def chiusura_con_prezzo_contro(c, m, prezzo):
    vero = c.chiudi

    def chiudi(pos, cid):
        m.prezzo = prezzo
        return vero(pos, cid)
    c.chiudi = chiudi
    return vero


# --- il ramo «sotto il 3%» -----------------------------------------------------------------------------------------------

def test_A1_sotto_il_3_con_il_tetto_finito(tmp_path):
    """Sotto il 3% dopo la chiusura e tetto di spesa finito: nessuna chiamata, nessun fermo, niente aperto; a mezzanotte «non
    raggiunto» e l'ora del tetto."""
    tr, c, m, o, messaggi = sim(tmp_path)
    q, soglia = soglia_lungo(c)
    vai(m, o, T0_MS + 5 * MIN + 10_000, soglia + 0.5)
    tr.budget.registra(datetime.fromtimestamp(o.ms / 1000, timezone.utc), 5.0)          # 5 dollari già spesi oggi
    vero = chiusura_con_prezzo_contro(c, m, soglia + 0.5 - 10.0)                        # 10 dollari contro durante la chiusura
    n = len(messaggi)
    tr.passo()
    c.chiudi = vero
    st = tr.carica()
    incassato = c.saldo()["conto"] - 1000
    assert 28 < incassato < 29.5 and not c.posizioni_tutte()
    assert not st.get("fermo_fino") and not st.get("obiettivo_ora") and SOTTO in eventi(tr)
    assert len(messaggi) == n and "richiama" not in st
    riga = chiamate_diario(tr)[-1]
    assert riga["stato"] == "tetto" and "sotto il 3%" in riga["motivo"] and st["tetto_dalle"].startswith("2026-11-24T10:05")
    vai(m, o, T0_MS + 15 * MIN + 10_000, 90000.0)
    tr.passo()
    assert len(messaggi) == n and not c.posizioni_tutte() and not tr.carica().get("fermo_fino")
    vai(m, o, T0_MS + 14 * 3600_000 + 30_000, 90000.0)                                 # 00:00:30 del 25
    tr.passo()
    res = (tr.cartella / "resoconti" / "2026-11-24.md").read_text()
    assert "* Obiettivo del 3% (30.00 USDT): non raggiunto" in res and "Tetto di spesa finito alle 10:05 UTC" in res


def test_A2_sotto_il_3_con_il_conto_esaurito(tmp_path):
    """Sotto il 3% dopo la chiusura e il disponibile non basta più per l'ordine minimo: fermo per conto esaurito, nessuna
    chiamata."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000)])
    tr.passo()
    assert c.pos is not None
    c.conto = 1031.0

    def dopo():
        c.conto, c.disp = 1029.0, 5.0
    dopo_il_metodo(c, "chiudi", dopo)
    o.t = T0 + timedelta(minutes=5)
    n = len(chiamate)
    tr.passo()
    st = tr.carica()
    assert c.pos is None and not st.get("fermo_fino") and st.get("esaurito") is True and len(chiamate) == n
    assert SOTTO in eventi(tr) and "FERMO: il conto non basta più per l'ordine minimo" in eventi(tr)


def test_A3_sotto_il_3_con_un_richiamo_in_sospeso(tmp_path):
    """Un richiamo rimasto nello stato e il ramo sotto il 3% nello stesso passo: vale il motivo della chiusura (il richiamo si
    perde, come per ogni altra chiusura trovata nel passo)."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000)])
    tr.passo()
    st = tr.carica()
    st["richiama"] = "operazione chiusa (chiusa da te)"
    tr.salva(st)
    c.conto = 1031.0

    def dopo():
        c.conto = 1029.0
    dopo_il_metodo(c, "chiudi", dopo)
    o.t = T0 + timedelta(minutes=5)
    tr.passo()
    motivo = chiamate_diario(tr)[-1]["motivo"]
    assert motivo == ("operazione chiusa (obiettivo del giorno (chiusa dal programma); dopo la chiusura il guadagno del giorno è "
                      "+29.00 USDT, sotto il 3% (30.00): l'obiettivo non è raggiunto)")
    assert "richiama" not in tr.carica()


LIMITE = dict(margine_usdt=100, leva=5, stop_prezzo=88000, obiettivo_prezzo=92000, tipo_ordine="limite", prezzo_limite=89000)


def test_A4_limite_in_attesa_e_obiettivo_fermo(tmp_path):
    """Obiettivo raggiunto con un ordine limite in attesa (conto sopra il 3% senza posizione: un funding arrivato in ritardo):
    il limite si annulla, nessuna operazione, fermo fino a mezzanotte."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", **LIMITE)])
    tr.passo()
    assert tr.carica()["aperta"]["in_attesa"] and c.normali and c.algo
    c.conto = 1030.5
    o.t = T0 + timedelta(minutes=5)
    n = len(chiamate)
    tr.passo()
    st = tr.carica()
    assert "ordine limite annullato: obiettivo del giorno raggiunto" in eventi(tr) and FERMO in eventi(tr)
    assert st["fermo_fino"] and st["obiettivo_ora"] and st["aperta"] is None and not c.normali and not c.algo
    assert st["operazioni"] == [] and len(chiamate) == n


def test_A5_limite_in_attesa_e_conto_che_scende_durante_l_annullamento(tmp_path):
    """Come A4, ma il conto scende sotto il 3% mentre il programma annulla: niente fermo, il modello si chiama e il motivo non dice
    «operazione chiusa», perché nessuna operazione c'è stata (problema 209)."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", **LIMITE)])
    tr.passo()
    c.conto = 1030.5

    def dopo():
        c.conto = 1029.9
    dopo_il_metodo(c, "annulla_tutto", dopo)
    o.t = T0 + timedelta(minutes=5)
    n = len(chiamate)
    tr.passo()
    st = tr.carica()
    assert not st.get("fermo_fino") and len(chiamate) == n + 1 and st["operazioni"] == [] and st["aperta"] is None
    assert chiamate_diario(tr)[-1]["motivo"] == (
        "ordine limite annullato dal programma per l'obiettivo del giorno (nessuna operazione); dopo l'annullamento il guadagno "
        "del giorno è +29.90 USDT, sotto il 3% (30.00): l'obiettivo non è raggiunto")
    assert "richiama" not in st


# --- 207: il limite che si esegue mentre il programma lo annulla per l'obiettivo ---------------------------------------------

@pytest.mark.parametrize("chiusura_minuto, fermo", [(89990.0, True), (89400.0, False)])
def test_B1_limite_eseguito_durante_l_annullamento_si_chiude_subito(tmp_path, chiusura_minuto, fermo):
    """Limite in attesa (lungo a 89.500, stop a 88.500) e conto sopra il 3% senza posizione (portafoglio a 1.030,50: come un
    funding arrivato in ritardo). Il minuto 10:20 scende a 89.400 e si conta solo dentro l'annullamento: il limite si esegue lì.
    Prima la posizione restava aperta senza stop e il trader si fermava («non è solo del trader»); adesso si chiude subito a
    mercato, si registra, e il fermo c'è solo se dopo la chiusura il 3% c'è ancora."""
    tr, c, m, o, messaggi = sim(tmp_path, prima=r("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88500.0,
                                                   tipo_ordine="limite", prezzo_limite=89500.0))
    f = tmp_path / "conto_simulato.json"
    s = json.loads(f.read_text())
    assert s["posizione"] is None and len(s["ordini"]) == 1 and [a["tipo"] for a in s["algo"]] == ["STOP_MARKET"]
    s["portafoglio"] = 1030.5
    f.write_text(json.dumps(s))
    vai(m, o, T0_MS + 20 * MIN + 58_000, 90000.0)                                       # 10:00-10:19 a 90.000; ore 10:20:58
    m.minuto(T0_MS + 20 * MIN, 90000.0, 90000.0, 89400.0, chiusura_minuto)               # il minuto 10:20 passa sotto il limite
    c.aggiorna(forza=True)                                                               # contati i minuti fino alle 10:20
    o.ms = T0_MS + 21 * MIN + 500                                                        # 10:21:00,5
    n = len(messaggi)
    tr.passo()
    s = json.loads(f.read_text())
    st = tr.carica()
    assert s["posizione"] is None and s["algo"] == [] and s["ordini"] == []              # niente resta aperto senza stop
    assert s["chiuse"][-1]["cid"].startswith("taio") and st["aperta"] is None
    assert "il limite si era eseguito mentre lo annullavo: chiudo a mercato" in eventi(tr)
    op = st["operazioni"][-1]
    assert op["come"] == "chiusa: limite eseguito durante l'annullamento" and op["n"] == 1
    assert (round(c.saldo()["conto"] - 1000, 2) >= 30.0) is fermo                      # 89.990: in guadagno; 89.400: in perdita
    if fermo:
        assert st["fermo_fino"] and st["obiettivo_ora"] and len(messaggi) == n and FERMO in eventi(tr)
    else:
        assert not st.get("fermo_fino") and len(messaggi) == n + 1 and SOTTO in eventi(tr)
        assert chiamate_diario(tr)[-1]["motivo"].startswith("operazione chiusa (chiusa: limite eseguito durante l'annullamento; ")
    o.ms += 30_000
    tr.passo()
    assert tr.carica().get("estraneo") is None and "FERMO: il conto non è solo del trader, non tocco niente" not in eventi(tr)


def test_B2_limite_eseguito_durante_l_annullamento_sotto_il_3(tmp_path):
    """Come B1, con il portafoglio appena sopra il 3%: le spese della posizione aperta e chiusa nell'annullamento lo portano sotto.
    Niente fermo e il modello si chiama, con il modo vero dell'operazione."""
    tr, c, m, o, messaggi = sim(tmp_path, prima=r("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88500.0,
                                                   tipo_ordine="limite", prezzo_limite=89500.0))
    f = tmp_path / "conto_simulato.json"
    s = json.loads(f.read_text())
    s["portafoglio"] = 1030.001
    f.write_text(json.dumps(s))
    vai(m, o, T0_MS + 20 * MIN + 58_000, 90000.0)                                       # 10:00-10:19 sopra il limite
    m.minuto(T0_MS + 20 * MIN, 90000.0, 90000.0, 89400.0, 89000.0)
    c.aggiorna(forza=True)                                                               # il minuto 10:20 non è ancora contato
    m.prezzo = 89000.0                                                                   # il mark sotto il limite: si perde
    assert json.loads(f.read_text())["posizione"] is None
    o.ms = T0_MS + 21 * MIN + 500
    n = len(messaggi)
    tr.passo()
    st = tr.carica()
    assert json.loads(f.read_text())["posizione"] is None and not st.get("fermo_fino") and SOTTO in eventi(tr)
    assert len(messaggi) == n + 1
    assert chiamate_diario(tr)[-1]["motivo"].startswith(
        "operazione chiusa (chiusa: limite eseguito durante l'annullamento; dopo la chiusura il guadagno del giorno è ")


# --- 208 e 200: lo stato si salva prima della chiamata ----------------------------------------------------------------------

def test_C1_errore_nel_passo_dopo_la_chiusura_sotto_il_3(tmp_path):
    """Dopo la chiusura sotto il 3% il passo si interrompe prima della chiamata (le candele non arrivano, come con una pausa per
    troppe richieste). Lo stato salvato ha già la chiusura del programma e il motivo: al passo dopo il modello si chiama con il
    perché e la stessa operazione non si registra una seconda volta."""
    tr, c, m, o, messaggi = sim(tmp_path)
    q, soglia = soglia_lungo(c)
    vai(m, o, T0_MS + 5 * MIN + 10_000, soglia + 0.5)
    vero = chiusura_con_prezzo_contro(c, m, soglia + 0.5 - 10.0)
    candele = c.candele

    def rotte(*a, **k):
        raise RuntimeError("GET /fapi/v1/klines: 429: pausa")
    c.candele = rotte
    with pytest.raises(RuntimeError):
        tr.passo()
    c.chiudi, c.candele = vero, candele
    st = tr.carica()
    assert not c.posizioni_tutte() and st["aperta"] is None and SOTTO in eventi(tr)
    assert len(st["operazioni"]) == 1 and st["operazioni"][-1]["come"] == "obiettivo del giorno (chiusa dal programma)"
    attesa = st["richiama"]
    assert attesa.startswith("operazione chiusa (obiettivo del giorno (chiusa dal programma); dopo la chiusura il guadagno del "
                             "giorno è +") and attesa.endswith("sotto il 3% (30.00): l'obiettivo non è raggiunto)")
    o.ms += 30_000
    n = len(messaggi)
    tr.passo()
    st = tr.carica()
    assert len(st["operazioni"]) == 1 and st["operazioni"][-1]["come"] == "obiettivo del giorno (chiusa dal programma)"
    assert len(messaggi) == n + 1 and chiamate_diario(tr)[-1]["motivo"] == attesa
    assert eventi(tr).count("operazione chiusa") == 1 and "richiama" not in st


def test_chiusura_trovata_nel_passo_e_passo_interrotto(tmp_path):
    """Problema 200: l'operazione si è chiusa da sola fra due passi; il passo che la registra si interrompe prima della chiamata.
    Al passo dopo non si registra due volte e il modello si chiama per la chiusura."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000)])
    tr.passo()
    a = tr.carica()["aperta"]
    c.pos, c.algo, c.conto = None, [], 990.0
    c.esiti[a["cid"]] = {"stato": "chiusa", "come": "stop", "entrata": 90000.0, "quantita": a["quantita"],
                         "eseguita_ms": int(T0.timestamp() * 1000), "chiusa_ms": int(T0.timestamp() * 1000) + 240_000,
                         "uscita": 88000.0, "spese_entrata": 0.2, "spese": 0.4, "funding": 0.0, "risultato_prezzo": -9.6,
                         "netto": -10.0}
    candele = c.candele

    def rotte(*a, **k):
        raise RuntimeError("GET /fapi/v1/klines: 429: pausa")
    c.candele = rotte
    o.t = T0 + timedelta(minutes=5)
    n = len(chiamate)
    with pytest.raises(RuntimeError):
        tr.passo()
    st = tr.carica()
    assert st["aperta"] is None and len(st["operazioni"]) == 1 and st["richiama"] == f"operazione chiusa ({st['operazioni'][0]['come']})"
    c.candele = candele
    o.t += timedelta(seconds=30)
    tr.passo()
    st = tr.carica()
    assert len(st["operazioni"]) == 1 and eventi(tr).count("operazione chiusa") == 1 and "richiama" not in st
    assert len(chiamate) == n + 1 and chiamate_diario(tr)[-1]["motivo"] == f"operazione chiusa ({st['operazioni'][0]['come']})"


# --- 209: il motivo della chiamata ------------------------------------------------------------------------------------------

def test_D1_motivo_dopo_una_chiusura_sul_conto(tmp_path):
    """L'operazione si chiude da sola sul conto (il suo obiettivo) a +30,50; nello stesso passo il programma «chiude tutto» (non
    c'è niente) e intanto il conto scende a +29,95 (un funding in ritardo). Il motivo dice il modo vero: «obiettivo»."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000,
                                                   obiettivo_prezzo=93000)])
    tr.passo()
    a = tr.carica()["aperta"]
    c.pos, c.algo, c.conto = None, [], 1030.5
    c.esiti[a["cid"]] = {"stato": "chiusa", "come": "obiettivo", "entrata": 90000.0, "quantita": a["quantita"],
                         "eseguita_ms": int(T0.timestamp() * 1000), "chiusa_ms": int(T0.timestamp() * 1000) + 240_000,
                         "uscita": 93000.0, "spese_entrata": 0.5, "spese": 1.0, "funding": 0.0, "risultato_prezzo": 31.5,
                         "netto": 30.5}

    def dopo():
        c.conto = 1029.95
    dopo_il_metodo(c, "chiudi", dopo)
    o.t = T0 + timedelta(minutes=5)
    tr.passo()
    st = tr.carica()
    assert st["operazioni"][-1]["come"] == "obiettivo" and not st.get("fermo_fino")
    assert chiamate_diario(tr)[-1]["motivo"] == ("operazione chiusa (obiettivo; dopo la chiusura il guadagno del giorno è +29.95 "
                                                 "USDT, sotto il 3% (30.00): l'obiettivo non è raggiunto)")


def test_niente_da_chiudere_e_conto_che_scende(tmp_path):
    """Il conto è al 3% senza niente aperto (il modello ha chiuso al passo prima) e scende mentre il programma annulla gli ordini:
    il motivo non dice «operazione chiusa» per un'operazione che non c'è, ma tiene il richiamo che c'era."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000), risposta("chiudi")])
    tr.passo()
    c.conto = 1030.2
    o.t = T0 + timedelta(minutes=15)
    tr.passo()                                                            # sotto il 3% dopo le spese: il modello chiude
    st = tr.carica()
    assert not st.get("fermo_fino") and c.pos is None and st["richiama"] == f"operazione chiusa ({st['operazioni'][-1]['come']})"
    c.conto = 1030.5

    def dopo():
        c.conto = 1029.5
    dopo_il_metodo(c, "chiudi", dopo)
    o.t += timedelta(seconds=30)
    n = len(chiamate)
    tr.passo()
    st = tr.carica()
    assert not st.get("fermo_fino") and len(chiamate) == n + 1
    assert chiamate_diario(tr)[-1]["motivo"] == (f"operazione chiusa (chiusa da te); adesso il guadagno del giorno è +29.50 USDT, "
                                                 f"sotto il 3% (30.00): l'obiettivo non è raggiunto")


# --- 210: il centesimo, una regola sola ---------------------------------------------------------------------------------------

def test_obiettivo_raggiunto_al_centesimo():
    assert obiettivo_raggiunto(Conto(1029.9951, 0.0, 1000.0))
    assert not obiettivo_raggiunto(Conto(1029.9949, 0.0, 1000.0))
    assert obiettivo_raggiunto(Conto(1030.5, 0.0, 1000.0, None, 0.5049))         # dopo le spese di chiusura: 29,9951
    assert not obiettivo_raggiunto(Conto(1030.5, 0.0, 1000.0, None, 0.5051))     # 29,9949


def test_E1_incassato_fra_29_995_e_30_e_raggiunto_al_centesimo(tmp_path):
    """Chiusura del programma con incassati circa 29,998: al centesimo 30,00, raggiunto, fermo."""
    tr, c, m, o, messaggi = sim(tmp_path)
    q, soglia = soglia_lungo(c)
    vai(m, o, T0_MS + 5 * MIN + 10_000, soglia + 0.03)
    vero = chiusura_con_prezzo_contro(c, m, soglia + 0.03 - 0.05)
    tr.passo()
    c.chiudi = vero
    incassato = c.saldo()["conto"] - 1000
    st = tr.carica()
    assert 29.995 <= incassato < 30 and st["fermo_fino"] and st["obiettivo_ora"]


def test_E2_stesso_guadagno_con_la_chiusura_sul_conto_ferma_uguale(tmp_path):
    """Lo stesso guadagno (+29,998) arrivato con la chiusura dell'operazione sul conto (il suo obiettivo): al centesimo è il 3%,
    come in E1, quindi fermo e nessuna chiamata (prima: niente fermo e «mancano 0.00»)."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000,
                                                   obiettivo_prezzo=93000)])
    tr.passo()
    a = tr.carica()["aperta"]
    c.pos, c.algo, c.conto = None, [], 1029.998
    c.esiti[a["cid"]] = {"stato": "chiusa", "come": "obiettivo", "entrata": 90000.0, "quantita": a["quantita"],
                         "eseguita_ms": int(T0.timestamp() * 1000), "chiusa_ms": int(T0.timestamp() * 1000) + 240_000,
                         "uscita": 93000.0, "spese_entrata": 0.5, "spese": 1.0, "funding": 0.0, "risultato_prezzo": 31.0,
                         "netto": 29.998}
    o.t = T0 + timedelta(minutes=5)
    n = len(chiamate)
    tr.passo()
    st = tr.carica()
    assert st.get("fermo_fino") and st.get("obiettivo_ora") and len(chiamate) == n and FERMO in eventi(tr)


def test_mancano_al_centesimo_mai_zero_se_manca_qualcosa(tmp_path):
    """Conto a mezzanotte 999,84 (obiettivo 29,9952, al centesimo 30,00) e guadagno 29,9948 (al centesimo 29,99): non raggiunto,
    e il messaggio dice «mancano 0.01», non «0.00»."""
    c = ContoFinto()
    c.conto = c.disp = 999.84
    chiamate = []

    def modello(system, utente):
        chiamate.append("\n\n".join(utente))
        return Esito(risposta(), "ok", {"input_tokens": 5000, "output_tokens": 2000})
    o = Orologio(T0)
    tr = Trader(c, modello, tmp_path, o)
    tr.passo()
    assert tr.carica()["conto_mezzanotte"] == 999.84
    c.conto = 999.84 + 29.9948
    o.t = T0 + timedelta(minutes=15)
    tr.passo()
    assert not tr.carica().get("fermo_fino") and "30.00: mancano 0.01" in chiamate[-1]


# --- 210 del secondo cercatore: il funding pagato dopo il fermo -------------------------------------------------------------

def test_funding_dopo_il_fermo_toglie_il_fermo(tmp_path):
    """Chiusura al 3% (+31,00), fermo; un funding pagato dopo porta il guadagno a +29,06: il fermo si toglie e il modello si
    chiama con il perché. A mezzanotte: «non raggiunto»."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000)])
    tr.passo()
    c.conto = 1031.0                                                      # +30,41 dopo le spese di chiusura
    o.t = T0 + timedelta(minutes=5)
    tr.passo()
    assert tr.carica()["fermo_fino"] and c.pos is None
    o.t += timedelta(seconds=30)
    n = len(chiamate)
    tr.passo()                                                            # il conto non è sceso: resta fermo
    assert tr.carica()["fermo_fino"] and len(chiamate) == n
    c.conto = 1029.06
    o.t += timedelta(seconds=30)
    tr.passo()
    st = tr.carica()
    assert not st.get("fermo_fino") and not st.get("obiettivo_ora") and TOLTO in eventi(tr) and len(chiamate) == n + 1
    assert chiamate_diario(tr)[-1]["motivo"] == ("fermo tolto: dopo la chiusura per l'obiettivo del giorno il conto è sceso e il "
                                                 "guadagno del giorno è +29.06 USDT, sotto il 3% (30.00): l'obiettivo non è "
                                                 "raggiunto")
    assert "richiama" not in st
    o.t = datetime(2026, 11, 25, 0, 0, 30, tzinfo=timezone.utc)
    tr.passo()
    res = (tr.cartella / "resoconti" / "2026-11-24.md").read_text()
    assert "* Obiettivo del 3% (30.00 USDT): non raggiunto" in res


def test_fermo_non_si_toglie_con_qualcosa_di_aperto(tmp_path):
    """Il fermo si toglie solo con il conto senza niente di aperto: con un ordine del trader nello stato (qui messo a mano: nel
    fermo non si apre niente) il conto sotto il 3% non basta."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000)])
    tr.passo()
    c.conto = 1031.0
    o.t = T0 + timedelta(minutes=5)
    tr.passo()
    st = tr.carica()
    assert st["fermo_fino"] and c.pos is None
    st["aperta"] = {"aperta": o.t.isoformat(), "lato": "lungo", "quantita": 0.001, "entrata": 89000.0, "leva": 5, "stop": 88000.0,
                    "in_attesa": True, "cid": "taio1", "tipo": "limite", "conto_prima": 1031.0}
    tr.salva(st)
    c.normali.append({"symbol": "BTCUSDT", "clientOrderId": "taio1"})
    c.conto = 1029.06
    o.t += timedelta(seconds=30)
    n = len(chiamate)
    tr.passo()
    assert tr.carica()["fermo_fino"] and len(chiamate) == n and TOLTO not in eventi(tr)


def test_resoconto_dice_se_il_conto_scende_dopo_il_3(tmp_path):
    """Fermo alle 23:59 con +31,00; il funding pagato dopo arriva nei secondi prima di mezzanotte e il passo che lo vede è quello
    di mezzanotte: il resoconto dice «raggiunto», ma anche che il conto è poi sceso sotto il 3%."""
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=990, leva=1, stop_prezzo=80000)])
    tr.passo()
    c.conto = 1031.0
    o.t = datetime(2026, 11, 24, 23, 59, 10, tzinfo=timezone.utc)
    tr.passo()
    assert tr.carica()["obiettivo_ora"].startswith("2026-11-24T23:59")
    c.conto = 1029.06
    o.t = datetime(2026, 11, 25, 0, 0, 10, tzinfo=timezone.utc)
    tr.passo()
    res = (tr.cartella / "resoconti" / "2026-11-24.md").read_text()
    assert "* Obiettivo del 3% (30.00 USDT): raggiunto alle 23:59 UTC, poi il conto è sceso sotto il 3% (+29.06)" in res
    assert not tr.carica().get("fermo_fino")


# --- nessuna posizione senza stop dopo il ramo «sotto il 3%» ----------------------------------------------------------------

def test_F1_la_nuova_operazione_dello_stesso_passo_ha_il_suo_stop(tmp_path):
    tr, c, m, o, messaggi = sim(tmp_path, altre=[r("apri_corto", margine_usdt=900, leva=10, stop_prezzo=90500.0)])
    q, soglia = soglia_lungo(c)
    vai(m, o, T0_MS + 5 * MIN + 10_000, soglia + 0.5)
    vero = chiusura_con_prezzo_contro(c, m, soglia + 0.5 - 10.0)
    tr.passo()
    c.chiudi = vero
    s = json.loads((tmp_path / "conto_simulato.json").read_text())
    st = tr.carica()
    assert s["posizione"]["lato"] == "corto" and st["aperta"]["lato"] == "corto"
    stop = [a for a in s["algo"] if a["tipo"] == "STOP_MARKET"]
    assert len(stop) == 1 and stop[0]["prezzo"] == 90500.0 and stop[0]["lato"] == "corto"
    cid = [x for x in diario(tr) if x.get("evento") == "aperta"][-1]["cid"]
    assert cid.startswith("taio") and s["chiuse"][-1]["cid"] != cid                      # nome nuovo, non quello di prima
