"""Versione 9 (28 novembre 2026): quando richiamarlo lo decide il modello (la sveglia: un prezzo sopra, un prezzo sotto, un tempo
massimo da 1 a 240 minuti), più le chiamate quando un suo limite si esegue e a mezzanotte UTC; senza sveglia le candele da 15 minuti.
E la ripartenza da 1.000 USDT (il proprietario: «per favore riparti da 1000 USD»). Conto finto o conto simulato vero, nessuna rete."""
import json
from datetime import datetime, timedelta, timezone

import pytest

from trader_ai import sveglia
from trader_ai.avvio import Trader
from trader_ai.conto_simulato import ContoSimulato
from trader_ai.modello import Esito
from trader_ai.schema import Risposta, Sveglia
from trader_ai.tests.test_avvio import T0, ContoFinto, Orologio, _eseguito, risposta
from trader_ai.tests.test_simulato import MIN, T0_MS, MercatoFinto
from trader_ai.tests.test_simulato import Orologio as OrologioMs

LIMITE = dict(margine_usdt=100, leva=5, stop_prezzo=88000, tipo_ordine="limite", prezzo_limite=89500)


def finto(tmp_path, risposte, t=T0):
    c = ContoFinto()
    chiamate = []

    def modello(system, utente):
        chiamate.append("\n\n".join(utente) if isinstance(utente, list) else utente)
        return Esito(risposte.pop(0) if risposte else risposta(), "ok", {"input_tokens": 5000, "output_tokens": 2000})
    o = Orologio(t)
    return Trader(c, modello, tmp_path, o), c, chiamate, o


def motivi(tr):
    return [json.loads(x)["motivo"] for x in tr.diario.read_text().splitlines() if '"stato"' in x and '"motivo"' in x]


def sv(**k):
    return Sveglia(**{"entro_minuti": 60, **k})


# --- le regole, una per una -----------------------------------------------------------------------------------------------

def test_nuova_sveglia_tempo_fra_1_e_240_e_prezzi_gia_superati():
    s, note = sveglia.nuova(T0, 90000.0, sv(sopra=90500.0, sotto=89500.0, entro_minuti=30))
    assert s == {"sopra": 90500.0, "sotto": 89500.0, "minuti": 30, "messa": T0.isoformat(),
                 "entro": (T0 + timedelta(minutes=30)).isoformat()} and note == []
    s, note = sveglia.nuova(T0, 90000.0, sv(sopra=89900.0, sotto=90100.0, entro_minuti=500))
    assert s["sopra"] is None and s["sotto"] is None and s["minuti"] == 240
    assert note == ["entro_minuti 500 portato a 240 (va da 1 a 240)", "«sopra» 89900 non messa: il prezzo era già 90000",
                    "«sotto» 90100 non messa: il prezzo era già 90000"]
    assert sveglia.nuova(T0, 90000.0, sv(entro_minuti=0))[0]["minuti"] == 1
    assert sveglia.nuova(T0, 90000.0, None) == (None, [])


def test_motivo_con_la_sveglia():
    s, _ = sveglia.nuova(T0, 90000.0, sv(sopra=90500.0, sotto=89500.0, entro_minuti=30))
    m = sveglia.motivo
    assert m(T0 + timedelta(minutes=15), T0, None, s, 90000.0) is None                  # niente candela da 15 minuti
    assert m(T0 + timedelta(minutes=2), T0, None, s, 90500.0) == "la tua sveglia: il prezzo è salito a 90500 (avevi chiesto sopra 90500)"
    assert m(T0 + timedelta(minutes=2), T0, None, s, 89499.5) == "la tua sveglia: il prezzo è sceso a 89499.5 (avevi chiesto sotto 89500)"
    assert m(T0 + timedelta(seconds=40), T0, None, s, 89000.0) is None                  # almeno un minuto fra due chiamate
    assert m(T0 + timedelta(minutes=30), T0, None, s, 90000.0) == "la tua sveglia: sono passati i 30 minuti che avevi chiesto"
    assert m(T0 + timedelta(seconds=40), T0, "stop iniziale", s, 90000.0) == "operazione chiusa (stop iniziale)"
    assert m(T0, None, None, s, 90000.0) == "primo avvio"
    # senza sveglia, la regola di prima
    assert m(T0 + timedelta(minutes=14), T0, None, None, 89000.0) == "candela da 15 minuti chiusa"   # 10:01 -> 10:15
    assert m(T0 + timedelta(minutes=5), T0, None, None, 89000.0) is None


# --- il programma ---------------------------------------------------------------------------------------------------------

def test_prezzo_della_sveglia_e_niente_candele(tmp_path):
    tr, c, chiamate, o = finto(tmp_path, [risposta(sveglia=sv(sotto=89900.0, entro_minuti=120))])
    tr.passo()
    assert tr.carica()["sveglia"]["sotto"] == 89900.0
    for minuti in (15, 30, 45):                                  # le candele da 15 minuti non chiamano più
        o.t = T0 + timedelta(minutes=minuti)
        tr.passo()
    assert len(chiamate) == 1
    c.prezzo = 89850.0
    o.t = T0 + timedelta(minutes=46)
    tr.passo()
    assert len(chiamate) == 2 and motivi(tr)[-1] == "la tua sveglia: il prezzo è sceso a 89850 (avevi chiesto sotto 89900)"
    assert tr.carica()["sveglia"] is None                         # la seconda risposta non aveva sveglia: di nuovo le candele


def test_tempo_della_sveglia(tmp_path):
    tr, c, chiamate, o = finto(tmp_path, [risposta(sveglia=sv(entro_minuti=30))])
    tr.passo()
    o.t = T0 + timedelta(minutes=29, seconds=30)
    tr.passo()
    assert len(chiamate) == 1
    o.t = T0 + timedelta(minutes=30)
    tr.passo()
    assert len(chiamate) == 2 and motivi(tr)[-1] == "la tua sveglia: sono passati i 30 minuti che avevi chiesto"


def test_sveglia_di_un_minuto(tmp_path):
    tr, c, chiamate, o = finto(tmp_path, [risposta(sveglia=sv(entro_minuti=1)), risposta(sveglia=sv(entro_minuti=1))])
    tr.passo()
    o.t = T0 + timedelta(seconds=30)
    tr.passo()
    assert len(chiamate) == 1
    o.t = T0 + timedelta(minutes=1)
    tr.passo()
    assert len(chiamate) == 2


def test_prezzo_gia_superato_il_modello_lo_sa(tmp_path):
    tr, c, chiamate, o = finto(tmp_path, [risposta(sveglia=sv(sopra=89000.0, entro_minuti=20))])
    tr.passo()
    assert tr.carica()["sveglia"]["sopra"] is None and tr.carica()["nota_sveglia"] == "«sopra» 89000 non messa: il prezzo era già 90000"
    o.t = T0 + timedelta(minutes=20)
    tr.passo()
    assert "la tua sveglia di prima: «sopra» 89000 non messa: il prezzo era già 90000" in chiamate[-1]
    assert "nota_sveglia" not in tr.carica()


def test_limite_eseguito_chiama_subito(tmp_path):
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", **LIMITE, sveglia=sv(entro_minuti=240))])
    tr.passo()
    assert tr.carica()["aperta"]["in_attesa"]
    o.t = T0 + timedelta(minutes=3)
    tr.passo()
    assert len(chiamate) == 1
    _eseguito(c)
    o.t = T0 + timedelta(minutes=4)
    tr.passo()
    assert len(chiamate) == 2 and motivi(tr)[-1] == "il tuo ordine limite si è eseguito a 89500"


def test_mezzanotte_chiama_con_la_sveglia(tmp_path):
    tr, c, chiamate, o = finto(tmp_path, [risposta(sveglia=sv(entro_minuti=240))], t=datetime(2026, 11, 24, 22, 30, tzinfo=timezone.utc))
    tr.passo()
    o.t = datetime(2026, 11, 25, 0, 0, 20, tzinfo=timezone.utc)
    tr.passo()
    assert len(chiamate) == 2 and motivi(tr)[-1] == "mezzanotte UTC: giorno nuovo, obiettivo nuovo"


def test_chiusura_chiama_subito_anche_con_la_sveglia(tmp_path):
    tr, c, chiamate, o = finto(tmp_path, [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000,
                                                   sveglia=sv(entro_minuti=240))])
    tr.passo()
    c.pos, c.algo, c.conto = None, [], 990.0
    o.t = T0 + timedelta(seconds=40)
    tr.passo()
    assert len(chiamate) == 2 and motivi(tr)[-1].startswith("operazione chiusa (")


def test_risposta_non_letta_torna_alle_candele(tmp_path):
    tr, c, chiamate, o = finto(tmp_path, [risposta(sveglia=sv(entro_minuti=240))])
    tr.passo()
    tr.chiama = lambda s, u: Esito(None, "errore", dettaglio="giù")
    o.t = T0 + timedelta(minutes=240)
    tr.passo()
    assert tr.carica()["sveglia"] is None
    tr.chiama = lambda s, u: Esito(risposta(), "ok", {"input_tokens": 10})
    o.t = T0 + timedelta(minutes=254)                              # 14:15: candela chiusa dopo la chiamata delle 14:01
    tr.passo()
    assert motivi(tr)[-1] == "candela da 15 minuti chiusa"


def test_chiamate_rimaste_senza_l_ora_dell_ultima(tmp_path):
    tr, c, chiamate, o = finto(tmp_path, [risposta(sveglia=sv(entro_minuti=30))])
    tr.passo()
    assert "rimaste oggi con il costo medio di oggi, questa compresa; mezzanotte UTC fra 13 h 59" in chiamate[0]
    assert "l'ultima verso" not in chiamate[0]


def test_la_sveglia_arriva_dallo_schema_e_dalle_istruzioni():
    from pathlib import Path
    r = Risposta.model_validate_json(json.dumps({"azione": "aspetta", "approccio": "a", "cambio_approccio": False, "diario": "d",
                                                 "sveglia": {"sotto": 59000, "entro_minuti": 45}}))
    assert r.sveglia.sotto == 59000 and r.sveglia.entro_minuti == 45 and r.sveglia.sopra is None
    testo = (Path(__file__).resolve().parents[1] / "istruzioni.md").read_text()
    assert "`sveglia`" in testo and "da 1 a 240" in testo and "a ogni candela da 15 minuti chiusa, qualunque" not in testo


# --- ripartire da 1.000 USDT ------------------------------------------------------------------------------------------------

def vai(m, o, fino_ms, prezzo):
    t = m.minuti[-1][0] + MIN if m.minuti else T0_MS
    while t < fino_ms - fino_ms % MIN:
        m.minuto(t, prezzo, prezzo, prezzo, prezzo)
        t += MIN
    m.prezzo = prezzo
    o.ms = fino_ms


def _sim(tmp_path):
    m, o = MercatoFinto(), OrologioMs(T0_MS + 10_000)
    c = ContoSimulato(m, tmp_path / "conto_simulato.json", o)
    c.aggiorna(forza=True)
    tr = Trader(c, lambda s, u: Esito(risposta("apri_lungo", margine_usdt=500, leva=5, stop_prezzo=89000.0), "ok",
                                      {"input_tokens": 10}), tmp_path / "dati",
                lambda: datetime.fromtimestamp(o.ms / 1000, timezone.utc))
    return tr, c, m, o


def test_azzera_riparte_da_1000_e_tiene_la_memoria(tmp_path):
    tr, c, m, o = _sim(tmp_path)
    tr.passo()
    assert c.posizioni_tutte()
    with pytest.raises(SystemExit, match="prima «chiudi»"):
        tr.azzera(attesa_blocco_s=1.0)
    vai(m, o, T0_MS + 5 * MIN + 10_000, 89500.0)
    tr.chiudi_tutto_e_ferma(attesa_blocco_s=1.0)
    prima = c.saldo()["conto"]
    assert prima < 1000 and len(tr.carica()["operazioni"]) == 1
    st = tr.carica()
    st["conto_mezzanotte"] = 990.0                                  # come in un giorno partito da un altro conto
    tr.salva(st)
    assert tr.azzera(attesa_blocco_s=1.0) == pytest.approx(prima)
    s = c.saldo()
    st = tr.carica()
    assert s["conto"] == 1000.0 and s["portafoglio"] == 1000.0
    assert st["inizio"] == {"giorno": "2026-11-24", "ora": "2026-11-24T10:05:10+00:00", "conto": 1000.0,
                            "prima": {"giorno": "2026-11-24", "conto": 1000.0, "fine": round(prima, 2)}}
    assert st["conto_mezzanotte"] == 1000.0 and len(st["operazioni"]) == 1 and st.get("sveglia") is None
    assert "ripartito da 1000 USDT" in tr.diario.read_text()
    mov = json.loads((tmp_path / "conto_simulato.json").read_text())["movimenti"][-1]
    assert mov["cosa"] == "azzeramento" and mov["importo"] == pytest.approx(1000 - prima, abs=1e-6)
    # il messaggio dopo la ripartenza
    tr.riparti()
    vai(m, o, T0_MS + 21 * MIN + 10_000, 89500.0)
    visti = []
    tr.chiama = lambda s_, u: (visti.append("\n\n".join(u)), Esito(risposta(), "ok", {"input_tokens": 10}))[1]
    tr.passo()
    assert visti and "il conto è ripartito da 1000 USDT quel giorno" in visti[0]
    assert "dall'inizio, anche prima della ripartenza" in visti[0]
    assert "dall'inizio della prova (24/11, 1000 USDT): +0.00 (+0.0%)" in visti[0]
    # il giorno della ripartenza: «oggi» è dalla ripartenza, non dalla mezzanotte (problema 269)
    assert "dalla ripartenza delle 10:05 UTC +0.00" in visti[0] and "del conto alla ripartenza, 1000.00" in visti[0]
    riga_oggi = [x for x in visti[0].splitlines() if x.startswith("oggi (24/11, dalla ripartenza)")]
    assert len(riga_oggi) == 1 and "-16.41" not in riga_oggi[0]                    # l'operazione chiusa prima non c'è
    # a mezzanotte il resoconto dice la ripartenza e conta da quell'ora (l'operazione di prima non c'è)
    vai(m, o, T0_MS + 14 * 3600_000 + 30_000, 89500.0)
    tr.chiama = lambda s_, u: Esito(risposta(), "ok", {"input_tokens": 10})
    tr.passo()
    res = (tr.cartella / "resoconti" / "2026-11-24.md").read_text()
    assert f"Ripartito da 1000 USDT alle 10:05 UTC (prima il conto era a {prima:.2f})" in res
    assert "* Conto: da 1000.00 a 1000.00 USDT, +0.00" in res and "* Operazioni chiuse: nessuna" in res


def test_azzera_rifiuta_con_qualcosa_di_aperto(tmp_path):
    tr, c, m, o = _sim(tmp_path)
    tr.passo()
    tr.f_fermo.parent.mkdir(parents=True, exist_ok=True)
    tr.f_fermo.write_text("x")                                       # fermo a mano, ma la posizione è ancora aperta
    portafoglio = c.saldo()["portafoglio"]
    with pytest.raises(SystemExit, match="ancora qualcosa di aperto"):
        tr.azzera(attesa_blocco_s=1.0)
    assert c.posizioni_tutte() and c.saldo()["portafoglio"] == portafoglio and "prima" not in (tr.carica().get("inizio") or {})


def test_azzera_solo_con_il_trader_fermo_a_mano(tmp_path):
    tr, c, m, o = _sim(tmp_path)
    with pytest.raises(SystemExit, match="il trader deve essere fermo a mano"):
        tr.azzera(attesa_blocco_s=1.0)
    assert not tr.diario.exists() or "ripartito" not in tr.diario.read_text()


def test_azzera_rifiuta_con_un_operazione_non_registrata(tmp_path):
    """«chiudi» con il blocco occupato chiude sul conto ma non registra: «azzera» non deve farla sparire (problema 268)."""
    tr, c, m, o = _sim(tmp_path)
    tr.passo()
    vai(m, o, T0_MS + 5 * MIN + 10_000, 89500.0)
    c.chiudi(c.posizioni_tutte()[0], "taix1")                          # chiusa sul conto, lo stato non lo sa ancora
    tr.f_fermo.write_text("x")
    assert not c.posizioni_tutte() and tr.carica()["aperta"]
    with pytest.raises(SystemExit, match="rilancia «chiudi», poi «azzera»"):
        tr.azzera(attesa_blocco_s=1.0)
    assert c.saldo()["portafoglio"] != 1000.0


def test_operazione_aperta_con_la_sveglia_niente_raffica(tmp_path):
    """Prova del revisore della diciannovesima (problema 274): con un'operazione a mercato aperta e la sveglia, i passi senza eventi
    non chiamano."""
    rr = [risposta("apri_lungo", margine_usdt=100, leva=5, stop_prezzo=88000, sveglia=sv(entro_minuti=240))]
    tr, c, chiamate, o = finto(tmp_path, rr)
    tr.passo()
    assert c.pos is not None
    for k in range(1, 21):                                          # dieci minuti, un passo ogni 30 secondi
        o.t = T0 + timedelta(seconds=30 * k)
        tr.passo()
    assert len(chiamate) == 1


def test_azzera_solo_sul_conto_simulato(tmp_path):
    tr, c, chiamate, o = finto(tmp_path, [])
    with pytest.raises(SystemExit, match="solo il conto simulato"):
        tr.azzera(attesa_blocco_s=1.0)
