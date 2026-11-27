"""Il 3% contato dopo le spese di chiusura (versione 8; il proprietario, 26 novembre 2026: «sì alle tre decisioni, procedi»), con il
conto SIMULATO vero (conto_simulato.py), il programma vero (avvio.Trader) e il mercato finto dei test; nessuna rete.

Prove della sedicesima revisione (`trader_ai/revisioni/2026-11-26-sedicesima.md`): problema 203 (i test di prima non prendevano un
errore sulle spese fino a circa 1 USDT, né `giro.decidi` sul conto prima delle spese), problema 204 (il programma si fermava fino a
mezzanotte anche quando, dopo la chiusura, il guadagno vero restava sotto il 3%: adesso si continua, come ha detto il proprietario
«non si deve fermare finché non ha raggiunto il 3%»), problema 206 (diario e lezioni con il guadagno dopo le spese)."""
import json
import re
from datetime import datetime, timezone

import pytest

import trader_ai.avvio as avvio
from trader_ai.avvio import Trader
from trader_ai.conto_simulato import COMMISSIONE_MERCATO, ContoSimulato, scarto
from trader_ai.limiti import guadagno_netto, obiettivo_raggiunto
from trader_ai.modello import Esito
from trader_ai.ripara import lezioni_dal_diario
from trader_ai.schema import Risposta
from trader_ai.tests.test_simulato import MIN, T0_MS, MercatoFinto
from trader_ai.tests.test_simulato import Orologio as OrologioMs

SC, F = scarto("BTCUSDT"), COMMISSIONE_MERCATO


def r(azione="aspetta", **kw):
    return Risposta(azione=azione, approccio="t", cambio_approccio=False, diario="d", **kw)


def vai(m, o, fino_ms, prezzo):
    """Minuti piatti al prezzo dato fino al minuto prima di `fino_ms` (il minuto in corso non è chiuso); il mark è `prezzo`."""
    t = m.minuti[-1][0] + MIN if m.minuti else T0_MS
    while t < fino_ms - fino_ms % MIN:
        m.minuto(t, prezzo, prezzo, prezzo, prezzo)
        t += MIN
    m.prezzo = prezzo
    o.ms = fino_ms


def prepara(tmp_path, lato, monkeypatch, altre=()):
    """Alle 10:00:10 del 24 novembre il modello apre (leva 10, 990 di margine: circa 0,11 BTC); 1.000 USDT a mezzanotte."""
    m, o = MercatoFinto(), OrologioMs(T0_MS + 10_000)
    c = ContoSimulato(m, tmp_path / "conto_simulato.json", o)
    c.aggiorna(forza=True)
    apri = r("apri_lungo" if lato == "lungo" else "apri_corto", margine_usdt=990, leva=10,
             stop_prezzo=89000.0 if lato == "lungo" else 91000.0)
    risposte, messaggi, conti = [apri, *altre], [], []

    def modello(system, utente):
        messaggi.append("\n\n".join(utente))
        return Esito(risposte.pop(0) if risposte else r(), "ok", {"input_tokens": 100, "output_tokens": 10})
    tr = Trader(c, modello, tmp_path / "dati", lambda: datetime.fromtimestamp(o.ms / 1000, timezone.utc))
    vero = avvio.decidi

    def spia(*a, **k):                                                       # il Conto che arriva a giro.decidi
        conti.append(a[3])
        return vero(*a, **k)
    monkeypatch.setattr(avvio, "decidi", spia)
    tr.passo()
    assert c.posizioni_tutte()
    return tr, c, m, o, messaggi, conti


def soglie(c, lato):
    """Prezzo mark a cui il guadagno del giorno arriva a 30 USDT: prima delle spese (come fino alla versione 7) e dopo le spese di
    chiusura (commissione e scarto d'uscita, dalle costanti del conto simulato)."""
    p = c.posizioni_tutte()[0]
    q, e, w = p["quantita"], p["entrata"], c.saldo()["portafoglio"]
    if lato == "lungo":
        return q, e + (1030 - w) / q, (1030 - w + e * q) / (q * (1 - SC - (1 - SC) * F))
    return q, e - (1030 - w) / q, (w + e * q - 1030) / (q * (1 + SC + (1 + SC) * F))


def spese_attese(q, prezzo, lato):
    u = prezzo * (1 - SC) if lato == "lungo" else prezzo * (1 + SC)
    return q * (abs(u - prezzo) + u * F)


def eventi(tr, inizio=""):
    return [e for e in (json.loads(x) for x in tr.diario.read_text().splitlines()) if e.get("evento", "").startswith(inizio)]


def righe_chiamate(tr):
    return [e for e in (json.loads(x) for x in tr.diario.read_text().splitlines()) if e.get("motivo") and "stato" in e]


def resoconto(tr, giorno="2026-11-24"):
    return (tr.cartella / "resoconti" / f"{giorno}.md").read_text()


@pytest.mark.parametrize("lato", ["lungo", "corto"])
def test_soglia_dopo_le_spese_e_guadagno_incassato(tmp_path, monkeypatch, lato):
    tr, c, m, o, messaggi, conti = prepara(tmp_path, lato, monkeypatch, altre=[r(lezione="lezione nella fascia")])
    q, lordo, netto = soglie(c, lato)
    verso = 1 if lato == "lungo" else -1
    assert verso * (netto - lordo) > 0
    # 1) nella fascia (sopra il 3% prima delle spese, sotto dopo): il programma NON chiude (fino alla versione 7 chiudeva)
    mezzo = (lordo + netto) / 2
    vai(m, o, T0_MS + 5 * MIN + 10_000, mezzo)
    tr.passo()
    assert c.saldo()["conto"] >= 1030 and c.posizioni_tutte() and not tr.carica().get("fermo_fino")
    # 2) mezzo dollaro di prezzo prima della soglia vera (circa 0,055 USDT di conto): ancora niente
    vai(m, o, T0_MS + 6 * MIN + 10_000, netto - verso * 0.5)
    tr.passo()
    assert c.posizioni_tutte() and not tr.carica().get("fermo_fino")
    # 3) candela delle 10:15 nella fascia: il modello si chiama, con il conto che toglie le spese (giro.decidi compreso)
    vai(m, o, T0_MS + 15 * MIN + 10_000, mezzo)
    n = len(messaggi)
    tr.passo()
    assert len(messaggi) == n + 1
    cn = conti[-1]
    spese = spese_attese(q, mezzo, lato)
    assert cn.spese_chiusura == pytest.approx(spese, abs=1e-9) and not obiettivo_raggiunto(cn)
    netto_giorno = c.saldo()["conto"] - spese - 1000
    assert guadagno_netto(cn) == pytest.approx(netto_giorno, abs=1e-9)
    riga = re.search(r"da mezzanotte UTC ([+-]\d+\.\d\d), ([+-]\d+\.\d\d) se chiudi adesso \(spese di chiusura tolte\);"
                     r".*contato dopo le spese di chiusura\) 30\.00: mancano (\d+\.\d\d)", messaggi[-1])
    assert riga, messaggi[-1][:2000]
    assert riga.group(2) == f"{netto_giorno:+.2f}" and riga.group(3) == f"{max(0.0, 30 - netto_giorno):.2f}"
    uscita = re.search(r"uscita a mercato circa (\d+\.\d\d)", messaggi[-1])
    assert uscita and uscita.group(1) == f"{spese:.2f}"
    # la riga del diario della chiamata e la lezione dicono il giorno dopo le spese, come il messaggio (problema 206)
    ultima = righe_chiamate(tr)[-1]
    assert ultima["guadagno_netto"] == round(netto_giorno, 2) and ultima["guadagno_giorno"] > ultima["guadagno_netto"]
    lezione = tr.carica()["lezioni"][-1]
    assert lezione["testo"] == "lezione nella fascia" and lezione["giorno_netto"] == round(netto_giorno, 2)
    # 4) mezzo dollaro dopo la soglia vera: chiude, fermo fino a mezzanotte, e il guadagno INCASSATO è almeno il 3%
    vai(m, o, T0_MS + 16 * MIN + 10_000, netto + verso * 0.5)
    previsto = c.saldo()["conto"] - spese_attese(q, netto + verso * 0.5, lato) - 1000
    tr.passo()
    st = tr.carica()
    incassato = c.saldo()["conto"] - 1000
    ev = eventi(tr, "obiettivo del giorno raggiunto")[-1]
    assert not c.posizioni_tutte() and st["fermo_fino"] == "2026-11-25T00:00:00+00:00"
    assert st["operazioni"][-1]["come"] == "obiettivo del giorno (chiusa dal programma)"
    assert 30 <= incassato < 30.1 and incassato == pytest.approx(previsto, abs=1e-6)
    assert ev["guadagno"] == round(incassato, 2) and ev["guadagno_previsto"] == round(previsto, 2)
    assert ev["conto"] == pytest.approx(1000 + incassato, abs=1e-9)
    # 5) fermo fino a mezzanotte: nessuna chiamata e niente aperto, anche a ogni candela
    n = len(messaggi)
    for ore in range(1, 14):
        vai(m, o, T0_MS + ore * 3600_000 + 15 * MIN + 10_000, 90000.0)
        tr.passo()
    vai(m, o, T0_MS + 13 * 3600_000 + 59 * MIN + 50_000, 90000.0)          # 23:59:50
    tr.passo()
    assert len(messaggi) == n and not c.posizioni_tutte() and tr.carica()["fermo_fino"]
    # 6) mezzanotte: resoconto con «raggiunto» e il conto sopra il 3%, fermo tolto, chiamate di nuovo
    vai(m, o, T0_MS + 14 * 3600_000 + 30_000, 90000.0)                       # 00:00:30 del 25 novembre
    tr.passo()
    st = tr.carica()
    res = resoconto(tr)
    assert "* Obiettivo del 3% (30.00 USDT): raggiunto alle 10:16 UTC" in res
    assert f"da 1000.00 a {1000 + incassato:.2f} USDT, {incassato:+.2f} ({incassato / 10:+.2f}%)" in res
    assert st["giorno"] == "2026-11-25" and st["fermo_fino"] is None and st["conto_mezzanotte"] == pytest.approx(1000 + incassato)
    assert len(messaggi) == n + 1                                            # la prima candela del giorno nuovo


def test_prezzo_che_scende_fra_controllo_e_chiusura_si_continua_fino_al_3(tmp_path, monkeypatch):
    """Il 3% si controlla al prezzo letto; la chiusura a mercato legge il prezzo di nuovo. 10 dollari di BTC contro nel frattempo
    (con 0,11 BTC) lasciano il guadagno sotto il 3%: niente fermo, il modello si chiama subito e il giorno continua. Quando poi il
    3% c'è davvero dopo la chiusura, il programma si ferma fino a mezzanotte."""
    tr, c, m, o, messaggi, conti = prepara(tmp_path, "lungo", monkeypatch,
                                           altre=[r("apri_lungo", margine_usdt=900, leva=10, stop_prezzo=89000.0)])
    q, lordo, netto = soglie(c, "lungo")
    vai(m, o, T0_MS + 5 * MIN + 10_000, netto + 0.5)
    previsto = c.saldo()["conto"] - spese_attese(q, netto + 0.5, "lungo") - 1000
    p, w = c.posizioni_tutte()[0], c.saldo()["portafoglio"]
    u = (netto + 0.5 - 10.0) * (1 - SC)                                      # l'uscita vera, dopo il salto
    incassato = w + (u - p["entrata"]) * q - u * q * F - 1000
    vero = c.chiudi

    def chiudi_dopo_un_salto(pos, cid):
        m.prezzo = netto + 0.5 - 10.0                                        # il mark è sceso di 10 dollari nel frattempo
        return vero(pos, cid)
    c.chiudi = chiudi_dopo_un_salto
    n = len(messaggi)
    tr.passo()
    c.chiudi = vero
    st = tr.carica()
    assert 28 < incassato < 29.5 and previsto >= 30
    assert not st.get("fermo_fino") and not st.get("obiettivo_ora") and not eventi(tr, "obiettivo del giorno raggiunto")
    ev = eventi(tr, "chiuso per l'obiettivo del giorno, ma dopo la chiusura il guadagno è sotto il 3%")[-1]
    assert ev["guadagno"] == round(incassato, 2) and ev["guadagno_previsto"] == round(previsto, 2)
    assert st["operazioni"][-1]["come"] == "obiettivo del giorno (chiusa dal programma)"
    # il modello si chiama subito, con il perché, e la sua apertura nuova si esegue: il giorno continua
    assert len(messaggi) == n + 1
    chiamata = righe_chiamate(tr)[-1]
    assert chiamata["motivo"] == (f"operazione chiusa (obiettivo del giorno (chiusa dal programma); dopo la chiusura il guadagno del "
                                  f"giorno è {incassato:+.2f} USDT, sotto il 3% (30.00): l'obiettivo non è raggiunto)")
    assert f"mancano {30 - incassato:.2f}" in messaggi[-1]
    assert c.posizioni_tutte() and tr.carica()["aperta"]["lato"] == "lungo"
    # il prezzo sale: il 3% c'è dopo le spese -> chiude, e questa volta il guadagno incassato arriva al 3%: fermo
    q2 = c.posizioni_tutte()[0]["quantita"]
    e2, w2 = c.posizioni_tutte()[0]["entrata"], c.saldo()["portafoglio"]
    soglia2 = (1030 - w2 + e2 * q2) / (q2 * (1 - SC - (1 - SC) * F))
    vai(m, o, T0_MS + 7 * MIN + 10_000, soglia2 + 0.5)
    tr.passo()
    st = tr.carica()
    incassato = c.saldo()["conto"] - 1000
    assert not c.posizioni_tutte() and st["fermo_fino"] == "2026-11-25T00:00:00+00:00" and 30 <= incassato < 30.1
    vai(m, o, T0_MS + 14 * 3600_000 + 30_000, 90000.0)                       # 00:00:30 del 25 novembre: resoconto
    tr.passo()
    assert "* Obiettivo del 3% (30.00 USDT): raggiunto alle 10:07 UTC" in resoconto(tr)


@pytest.mark.parametrize("salto, fermo", [(0.0, True), (0.1, False)])
def test_il_3_per_cento_dopo_la_chiusura_si_conta_al_centesimo(tmp_path, monkeypatch, salto, fermo):
    """Al controllo il guadagno dopo le spese è circa 30,003. Chiusura allo stesso prezzo: incassati 30,003, che al centesimo fanno
    30,00 → raggiunto, fermo. Il mark scende di 10 centesimi durante la chiusura: incassati circa 29,992, cioè 29,99 → non raggiunto,
    si continua."""
    tr, c, m, o, messaggi, conti = prepara(tmp_path, "lungo", monkeypatch)
    q, lordo, netto = soglie(c, "lungo")
    vai(m, o, T0_MS + 5 * MIN + 10_000, netto + 0.03)
    vero = c.chiudi

    def chiudi(pos, cid):
        m.prezzo = netto + 0.03 - salto
        return vero(pos, cid)
    c.chiudi = chiudi
    tr.passo()
    c.chiudi = vero
    st = tr.carica()
    ev = (eventi(tr, "obiettivo del giorno raggiunto") or eventi(tr, "chiuso per l'obiettivo del giorno"))[-1]
    assert not c.posizioni_tutte() and ev["guadagno_previsto"] == 30.0
    assert bool(st.get("fermo_fino")) is fermo and bool(st.get("obiettivo_ora")) is fermo
    assert ev["guadagno"] == (30.0 if fermo else 29.99)


def test_niente_spese_senza_posizione_e_con_limite_in_attesa(tmp_path):
    """Senza posizione, o con un ordine limite non ancora eseguito, non c'è niente da chiudere: spese di chiusura zero."""
    from trader_ai.tests.test_avvio import ContoFinto
    c = ContoFinto()
    tr = Trader(c, lambda s, u: Esito(r(), "ok", {"input_tokens": 1}), tmp_path,
                lambda: datetime(2026, 11, 24, 10, 1, tzinfo=timezone.utc))
    st = {"conto_mezzanotte": 1000.0}
    s = {"conto": 1030.0, "disponibile": 1000.0}
    assert tr._conto(st, s, None, 90000.0).spese_chiusura == 0.0
    st["aperta"] = {"in_attesa": True, "lato": "lungo", "quantita": 0.11, "entrata": 89000.0, "leva": 10, "stop": 88000.0}
    cn = tr._conto(st, s, None, 90000.0)
    assert cn.posizione.in_attesa and cn.spese_chiusura == 0.0 and obiettivo_raggiunto(cn)


def test_stop_scattato_nel_minuto_che_si_chiude_durante_la_chiusura(tmp_path, monkeypatch):
    """Il controllo vede il 3% vero al prezzo di adesso, ma il minuto in corso (non ancora contato) è sceso sotto lo stop spostato
    dal modello: la chiusura arriva dopo la fine del minuto e il conto simulato conta prima lo stop. Il guadagno resta molto sotto
    il 3%: niente fermo, il modello si chiama per la chiusura allo stop, il resoconto dice «non raggiunto»."""
    tr, c, m, o, messaggi, conti = prepara(tmp_path, "lungo", monkeypatch, altre=[r("modifica", stop_prezzo=90300.0)])
    q, lordo, netto = soglie(c, "lungo")
    vai(m, o, T0_MS + 15 * MIN + 10_000, lordo - 10)
    tr.passo()                                                               # 10:15:10: il modello sposta lo stop a 90.300
    algo = json.loads((tmp_path / "conto_simulato.json").read_text())["algo"]
    assert [a["prezzo"] for a in algo if a["tipo"] == "STOP_MARKET"] == [90300.0]
    vai(m, o, T0_MS + 16 * MIN, lordo - 10)
    m.minuto(T0_MS + 16 * MIN, lordo - 10, 90400.0, 90290.0, netto + 5.0)        # il minuto 10:16: giù fino a 90.290, poi su
    o.ms = T0_MS + 16 * MIN + 59_500                                         # 10:16:59,5: il minuto non è ancora chiuso
    vero = c.chiudi

    def chiudi_dopo_la_fine_del_minuto(pos, cid):
        o.ms = T0_MS + 17 * MIN + 300                                        # 10:17:00,3
        return vero(pos, cid)
    c.chiudi = chiudi_dopo_la_fine_del_minuto
    n = len(messaggi)
    tr.passo()
    c.chiudi = vero
    st = tr.carica()
    incassato = c.saldo()["conto"] - 1000
    assert incassato < 25 and st["operazioni"][-1]["come"] == "stop spostato da te"
    assert not st.get("fermo_fino") and not st.get("obiettivo_ora")
    assert len(messaggi) == n + 1 and righe_chiamate(tr)[-1]["motivo"].startswith("operazione chiusa (stop spostato da te; ")
    vai(m, o, T0_MS + 14 * 3600_000 + 30_000, 90000.0)                       # 00:00:30 del 25 novembre: resoconto
    tr.passo()
    res = resoconto(tr)
    assert "* Obiettivo del 3% (30.00 USDT): non raggiunto" in res and f"{incassato:+.2f} ({incassato / 10:+.2f}%)" in res


def test_lezioni_dal_diario_con_il_guadagno_dopo_le_spese():
    """La ricostruzione delle lezioni usa il guadagno dopo le spese quando la riga del diario lo ha (dalla versione 8)."""
    righe = [{"ora": "2026-11-26T10:00:00+00:00", "guadagno_giorno": 33.0, "guadagno_netto": 27.0,
              "risposta": {"cambio_approccio": True, "perche": "nuovo"}},
             {"ora": "2026-11-25T10:00:00+00:00", "guadagno_giorno": -5.0, "risposta": {"cambio_approccio": True, "perche": "vecchio"}}]
    assert [x["giorno_netto"] for x in lezioni_dal_diario(righe, [])] == [27.0, -5.0]
