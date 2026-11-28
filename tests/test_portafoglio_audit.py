"""Le correzioni del 27 novembre 2026 nel paper, nel demo e nel conto vero (audit del 26 novembre 2026, bot/portafoglio/):

* ordini-3: la finestra degli ordini limite del paper parte dopo la lettura dei prezzi, non dall'inizio del giro;
* ordini-5: le monete che il demo non può avere si saltano con il motivo, restano fra gli obiettivi e stanno fuori dallo scarto;
* ordini-4: l'allarme `ordini_rifiutati` (oltre l'1% del conto o per due decisioni di fila) e i resti a mercato rifiutati;
* ordini-1: una lettura a ogni ora piena per il demo e per il paper di G1;
* salute-6: gli allarmi nuovi del demo e del conto vero al telefono, una volta;
* salute-10: cryptography fissata nei requisiti.

Ogni test fallirebbe con il codice di prima. Nessuna richiesta di rete vera: i Binance finti dei test del demo e del conto vero."""
from __future__ import annotations

import json
import re
import threading
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

from bot.core.firebase_client import _InMemoryStore
from bot.portafoglio import demo_binance as dm
from bot.portafoglio import f5
from tests import test_conto_vero as T
from tests.test_demo_binance import _Demo, _Risposta, _attese, _demo_semplice, _post, _rifiutata, _sempre
from tests.test_paper_f5 import _Finto

RADICE = Path(__file__).resolve().parents[1]
T0 = 20750 * 86400.0 + 400                       # 24 ottobre 2026, 00:06:40 UTC: la decisione di G1 del giorno nel file


def _rispondi(finto, avanti, metodo, url, headers, timeout):
    """Il pezzo comune dei due Binance finti qui sotto: un rifiuto che dura per moneta e percorso (``rifiuti``) e lo stato delle
    monete nell'exchangeInfo (``stati``)."""
    u = urlparse(url)
    q = {k: v[0] for k, v in parse_qs(u.query).items()}
    rifiuto = finto.rifiuti.get((u.path, q.get("symbol")))
    if rifiuto is not None and metodo == "POST" and (u.path != "/fapi/v1/order" or q.get("type") in rifiuto[1]):
        assert u.hostname == finto.HOST
        finto.chiamate.append((metodo, u.path, q))
        return rifiuto[0]
    r = avanti(metodo, url, headers, timeout)
    if u.path == "/fapi/v1/exchangeInfo" and finto.stati:
        for x in r.dati["symbols"]:
            if x["symbol"] in finto.stati:
                x["status"] = finto.stati[x["symbol"]]
    return r


class _DemoStati(_Demo):
    """Il demo finto con lo stato delle monete nell'exchangeInfo e i rifiuti che durano: ``rifiuti[(percorso, simbolo)] = (risposta,
    tipi d'ordine)`` (per gli ordini solo quei tipi, per il margine sempre)."""

    def __init__(self, simboli=("AUSDT", "BUSDT"), stati=None):
        super().__init__(simboli)
        self.stati, self.rifiuti = dict(stati or {}), {}

    def __call__(self, metodo, url, headers=None, timeout=None):
        return _rispondi(self, super().__call__, metodo, url, headers, timeout)


class _VeroStati(T._Vero):
    def __init__(self, simboli=("AUSDT", "BUSDT"), stati=None):
        super().__init__(simboli)
        self.stati, self.rifiuti = dict(stati or {}), {}

    def __call__(self, metodo, url, headers=None, timeout=None):
        return _rispondi(self, super().__call__, metodo, url, headers, timeout)


def _errore(codice, msg):
    return _Risposta({"code": codice, "msg": msg}, 400)


def _decide(tmp_path, giorno, pesi=None):
    (tmp_path / "g1.json").write_text(json.dumps({"ultimo_lunedi": giorno, "pesi": pesi or {"AUSDT": 0.5, "BUSDT": -0.5}}))


def _avvisi(d):
    mandati = []
    d.avvisa = mandati.append
    return mandati


def _di(avvisi, tipo):
    return [a for a in avvisi if f"allarme {tipo}" in a]


# ---------------------------------------------------------------------------------------------------------------------------------
# ordini-3: la finestra degli ordini limite del paper
# ---------------------------------------------------------------------------------------------------------------------------------
def test_ordini_3_inizio_della_finestra_al_primo_minuto_pieno_dopo_il_prezzo():
    assert f5.inizio_della_finestra_ms(100.0) == 120_000
    assert f5.inizio_della_finestra_ms(120.0) == 120_000           # alla lettura esatta di un minuto pieno: quel minuto
    assert f5.inizio_della_finestra_ms(120.001) == 180_000


def test_ordini_3_la_finestra_degli_ordini_limite_non_parte_prima_della_lettura_dei_prezzi(tmp_path):
    """Il giro parte alle 00:06 (``now``), lo scarico dei dati dura 245 secondi, i prezzi arrivano alle 00:10:05: la finestra degli
    ordini limite parte alle 00:11 (il primo minuto pieno dopo), dura un'ora e il controllo prende le candele da lì; il funding resta
    da ``now``. Con il codice di prima la finestra partiva alle 00:06, cioè prima del prezzo."""
    m = f5.lunedi_di(20750)
    finto = _Finto(m)
    orologio, letti = [0.0], []

    def chiedi(percorso, p):
        if percorso == "/fapi/v1/klines":
            orologio[0] += 245 / 30                             # 30 monete: 245 secondi di scarico in tutto
        if percorso == "/fapi/v1/premiumIndex":
            letti.append(orologio[0])
        if percorso == "/fapi/v1/markPriceKlines":
            candele.append(int(p["startTime"]))
        return finto(percorso, p)

    candele = []
    fb = _InMemoryStore()
    (tmp_path / "acceso").write_text("si")
    p = f5.PaperG1(fb, chiedi=chiedi, file_stato=tmp_path / "g1.json", interruttore=tmp_path / "acceso", pausa_s=0.0)
    p.cronometro = lambda: orologio[0]
    now = (m + 2) * 86400.0 + 360                               # 00:06 UTC
    finto.adesso_ms = int(now * 1000)
    p.tick(now)
    st = p.carica()
    prezzi_alle = now + letti[-1]                               # l'ultima lettura dei prezzi del giro è quella del ribilancio
    assert prezzi_alle == pytest.approx(now + 245)
    o = st["ordini"]
    assert o["da_ms"] >= prezzi_alle * 1000                     # mai prima della lettura dei prezzi
    assert o["da_ms"] == ((m + 2) * 86400 + 660) * 1000         # 00:11:00, il primo minuto pieno dopo le 00:10:05
    assert o["fino_ms"] == o["da_ms"] + f5.VALIDITA_LIMITE_MS
    assert st["funding_fino_ms"] == int(now * 1000)             # il funding resta dall'inizio del giro
    rib = fb.get_rtdb("/paper_g1/ribilanciamenti/" + time.strftime("%Y-%m-%d", time.gmtime((m + 2) * 86400)))
    assert rib["prezzi_letti"] == pytest.approx(prezzi_alle, abs=0.1) and rib["ordini_limite_dal"] * 1000 == o["da_ms"]
    p.tick(now + 3700)                                          # 01:07:40: la finestra (fino alle 01:11) non è finita
    assert p.carica().get("ordini") and candele == []
    p.tick(now + 4300)                                          # 01:17: si controlla, con le candele dalle 00:11
    assert "ordini" not in p.carica() and candele and set(candele) == {o["da_ms"]}


# ---------------------------------------------------------------------------------------------------------------------------------
# ordini-1: la lettura di ogni ora
# ---------------------------------------------------------------------------------------------------------------------------------
def test_ordini_1_lettura_di_ogni_ora_del_paper_di_g1(tmp_path):
    """A ogni ora piena il paper di G1 scrive in /paper_g1/ore/{giorno}/{HH} equity, quantità e prezzi mark del mercato vero; una
    volta per ora, anche dopo un riavvio. Gli altri paper no."""
    assert f5.PaperG1.LETTURA_ORARIA and not (f5.PaperF5.LETTURA_ORARIA or f5.PaperG11.LETTURA_ORARIA or f5.PaperG1N.LETTURA_ORARIA)
    m = f5.lunedi_di(20750)
    finto = _Finto(m)
    fb = _InMemoryStore()
    (tmp_path / "acceso").write_text("si")

    def paper():
        return f5.PaperG1(fb, chiedi=finto, file_stato=tmp_path / "g1.json", interruttore=tmp_path / "acceso", pausa_s=0.0)

    p = paper()
    giorno = (m + 2) * 86400.0
    data = time.strftime("%Y-%m-%d", time.gmtime(giorno))
    finto.adesso_ms = int((giorno + 360) * 1000)
    p.tick(giorno + 360)                                        # il primo ribilancio (senza stato: niente lettura prima)
    assert fb.get_rtdb(f"/paper_g1/ore/{data}/00") is None
    st = p.carica()
    finto.adesso_ms = int((giorno + 3610) * 1000)
    p.tick(giorno + 3610)                                       # 01:00:10
    lettura = fb.get_rtdb(f"/paper_g1/ore/{data}/01")
    assert lettura["ora"] == giorno + 3610
    assert lettura["quantita"] == {s: pytest.approx(q) for s, q in st["quantita"].items() if q}
    assert lettura["prezzi"] == {s: finto.prezzo[s] for s in st["quantita"]}
    assert lettura["equity"] == pytest.approx(p._equity(st, finto.prezzo), abs=1e-3)
    assert "funding_totale" in lettura and "costi_totali" in lettura
    p.tick(giorno + 3610 + 1800)                                # la stessa ora: niente lettura nuova
    p2 = paper()                                                # un riavvio nella stessa ora: la lettura c'è già
    p2.tick(giorno + 3610 + 2000)
    assert fb.get_rtdb(f"/paper_g1/ore/{data}/01")["ora"] == giorno + 3610
    p2.tick(giorno + 7205)
    assert fb.get_rtdb(f"/paper_g1/ore/{data}/02")["ora"] == giorno + 7205


def test_ordini_1_lettura_di_ogni_ora_del_demo_solo_letture(tmp_path):
    """Il demo scrive in /demo_binance/ore/{giorno}/{HH} equity, valore vero, quantità e prezzi mark del demo, al primo giro dopo
    l'ora piena e una volta per ora (anche dopo un riavvio); la lettura non manda niente a Binance. Il conto vero non la fa."""
    finto = _Demo()
    finto.posizioni_vive = True
    d, fb = _demo_semplice(tmp_path, finto)
    d.tick(T0)                                                  # la lettura delle 00 viene prima del ribilancio
    l0 = fb.get_rtdb("/demo_binance/ore/2026-10-24/00")
    assert l0 == {"ora": T0, "equity": 10000.0, "saldo": 10000.0, "valore_vero": 10000.0, "quantita": {}, "prezzi": {},
                  "ordini_in_corso": 0}
    d.tick(T0 + 3601)                                           # 01:06:41: AUSDT eseguito a limite; la lettura prima del resto
    l1 = fb.get_rtdb("/demo_binance/ore/2026-10-24/01")
    assert l1["quantita"] == {"AUSDT": 49.998} and l1["prezzi"] == {"AUSDT": 100.003, "BUSDT": 50.007}
    assert l1["ordini_in_corso"] == 2
    d.tick(T0 + 3700)
    d2, _ = _demo_semplice(tmp_path, finto)                    # un riavvio nella stessa ora
    d2.fb = fb
    d2.tick(T0 + 3800)
    assert fb.get_rtdb("/demo_binance/ore/2026-10-24/01")["ora"] == T0 + 3601
    scritture = len([c for c in finto.chiamate if c[0] != "GET"])
    d2.tick(T0 + 7200)                                          # 02:06:40: solo la lettura e la valutazione, nessun ordine
    assert len([c for c in finto.chiamate if c[0] != "GET"]) == scritture
    assert fb.get_rtdb("/demo_binance/ore/2026-10-24/02")["quantita"] == {"AUSDT": 49.998, "BUSDT": -99.986}


def test_ordini_1_il_conto_vero_non_fa_la_lettura_di_ogni_ora(tmp_path, monkeypatch):
    d, fb, finto = T._conto(tmp_path, monkeypatch)
    T._fino_alla_decisione_dopo(d, tmp_path)
    assert fb.get_rtdb("/conto_vero/ribilanciamenti/2026-10-25")["ordini"] == 2 and fb.get_rtdb("/conto_vero/ore") is None


# ---------------------------------------------------------------------------------------------------------------------------------
# ordini-5: le monete che il demo non può avere
# ---------------------------------------------------------------------------------------------------------------------------------
def test_ordini_5_moneta_non_in_trading_si_salta_con_il_motivo_e_i_pesi_non_cambiano(tmp_path):
    finto = _DemoStati(stati={"BUSDT": "SETTLING"})
    finto.posizioni_vive = True
    d, fb = _demo_semplice(tmp_path, finto)
    d.tick(T0)
    assert {q["symbol"] for q in _post(finto)} == {"AUSDT"}                       # niente ordine né margine per BUSDT
    assert [q["symbol"] for q in _post(finto, "/fapi/v1/marginType")] == ["AUSDT"]
    assert _post(finto)[0]["quantity"] == "49.998"                               # AUSDT come con tutti e due i pesi
    rib = fb.get_rtdb("/demo_binance/ribilanciamenti/2026-10-24")
    assert rib["rifiutati"] == [] and rib["monete_mancanti_sul_demo"] == ["BUSDT"]
    assert rib["non_disponibili_sul_demo"] == [{"simbolo": "BUSDT", "motivo": "stato SETTLING nell'exchangeInfo del demo",
                                                "peso": -0.5}]
    st = d.carica()
    assert st["obiettivi"]["BUSDT"] == pytest.approx(-5000 / 50.007)            # resta fra gli obiettivi: i pesi non cambiano
    assert st["non_disponibili"]["BUSDT"]["peso"] == -0.5
    d.tick(T0 + 3601)
    c = fb.get_rtdb("/demo_binance/confronto")
    assert c["non_disponibili_sul_demo"] == {"BUSDT": -0.5} and c["peso_non_disponibili"] == 0.5
    assert c["differenze"] == [] and c["scarto_totale"] < 0.001 and c["monete"] == 1   # prima: −50% di scarto su BUSDT
    assert fb.get_rtdb("/demo_binance/allarmi/ordini_rifiutati") is None


@pytest.mark.parametrize("dove,codice,msg", [("/fapi/v1/marginType", -1121, "Invalid symbol."),
                                              ("/fapi/v1/order", -4140, "Invalid symbol status for opening position.")])
def test_ordini_5_rifiutata_dal_demo_si_salta_poi_si_riprova_dopo_una_settimana(tmp_path, dove, codice, msg):
    finto = _DemoStati()
    finto.rifiuti[(dove, "BUSDT")] = (_errore(codice, msg), {"LIMIT", "MARKET"})
    d, fb = _demo_semplice(tmp_path, finto)
    avvisi = _avvisi(d)
    d.tick(T0)                                                  # la prima volta: rifiutata, ricordata, allarme (50% del conto)
    rib = fb.get_rtdb("/demo_binance/ribilanciamenti/2026-10-24")
    assert [(r["simbolo"], r["peso"]) for r in rib["rifiutati"]] == [("BUSDT", pytest.approx(-0.5, abs=1e-3))]
    al = fb.get_rtdb("/demo_binance/allarmi/ordini_rifiutati")
    assert f"{codice} {msg}" in al["testo"] and "si salta per 7 giorni" in al["testo"]
    assert al["monete"][0]["simbolo"] == "BUSDT" and al["monete"][0]["decisioni_di_fila"] == 1
    assert d.carica()["memoria_non_disponibili"]["BUSDT"]["codice"] == codice
    d.tick(T0 + 3601)
    n = len(finto.chiamate)
    _decide(tmp_path, 20751)
    d.tick(T0 + 86400)                                          # il giorno dopo: niente richiesta per BUSDT
    assert not [q for m_, p, q in finto.chiamate[n:] if m_ == "POST" and q.get("symbol") == "BUSDT"]
    rib = fb.get_rtdb("/demo_binance/ribilanciamenti/2026-10-25")
    assert rib["rifiutati"] == [] and rib["non_disponibili_sul_demo"][0]["simbolo"] == "BUSDT"
    assert "rifiutata dal demo" in rib["non_disponibili_sul_demo"][0]["motivo"] and "BUSDT" in rib["monete_mancanti_sul_demo"]
    assert fb.get_rtdb("/demo_binance/allarmi/ordini_rifiutati") is None   # nessun rifiuto vero: l'allarme si toglie
    d.tick(T0 + 86400 + 3601)
    n = len(finto.chiamate)
    _decide(tmp_path, 20757)
    d.tick(T0 + 7 * 86400)                                      # una settimana dopo il rifiuto: si riprova una volta
    assert [q for m_, p, q in finto.chiamate[n:] if m_ == "POST" and p == dove and q.get("symbol") == "BUSDT"]
    assert fb.get_rtdb("/demo_binance/allarmi/ordini_rifiutati") is None   # già nota: niente allarme di nuovo
    assert d.carica()["memoria_non_disponibili"]["BUSDT"]["visto"] == T0 + 7 * 86400
    assert len(_di(avvisi, "ordini rifiutati")) == 1


def test_ordini_4_e_5_dati_nuovi_rotti_nello_stato_non_fermano_il_ribilancio(tmp_path, capsys):
    """Il codice resta sul disco fino al riavvio approvato e deve reggere anche un riavvio da solo: con la memoria delle monete non
    disponibili o i rifiuti dello stato scritti male, il ribilancio va come prima (nessuna moneta saltata), lo stato si salva e il
    resto a mercato dopo l'ora si chiude."""
    finto = _DemoStati()
    finto.rifiuti[("/fapi/v1/order", "BUSDT")] = (_rifiutata(), {"LIMIT"})
    d, fb = _demo_semplice(tmp_path, finto)
    (tmp_path / "st.json").write_text(json.dumps({"memoria_non_disponibili": {"BUSDT": {"visto": "rotto"}},
                                                  "rifiuti": {"decisione": "x", "ordini": "rotto", "di_fila": {"BUSDT": "rotto"}}}))
    d.tick(T0)
    st = d.carica()
    assert st["ultimo_giorno"] == 20750 and [o["simbolo"] for o in st["ordini"]["lista"]] == ["AUSDT"]
    assert [q["symbol"] for q in _post(finto, "/fapi/v1/marginType")] == ["AUSDT", "BUSDT"]    # BUSDT non saltata
    assert "monete non disponibili non calcolate" in capsys.readouterr().out
    d.tick(T0 + 3601)
    assert "ordini" not in d.carica()


# ---------------------------------------------------------------------------------------------------------------------------------
# ordini-4: l'allarme degli ordini rifiutati e i resti a mercato rifiutati
# ---------------------------------------------------------------------------------------------------------------------------------
def test_ordini_4_allarme_oltre_l_1_per_cento_poi_si_toglie(tmp_path):
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    finto.guasti[("POST", "/fapi/v1/order", "BUSDT")] = _rifiutata()      # un rifiuto qualunque, una volta
    d.tick(T0)
    al = fb.get_rtdb("/demo_binance/allarmi/ordini_rifiutati")
    assert al["monete"] == [{"simbolo": "BUSDT", "errore": "-1000 An unknown error occurred while processing the request.",
                             "peso": pytest.approx(-0.5, abs=1e-3), "decisioni_di_fila": 1, "dove": "ordini"}]
    assert al["decisione"] == "2026-10-24" and al["peso_totale"] == pytest.approx(0.5, abs=1e-3)
    assert "BUSDT -50.00%" in al["testo"] and "1 decisione" in al["testo"]
    assert d.carica().get("memoria_non_disponibili") == {}                # un rifiuto qualunque non vuol dire «non disponibile»
    d.tick(T0 + 3601)
    _decide(tmp_path, 20751)
    d.tick(T0 + 86400)                                           # la decisione dopo senza rifiuti: l'allarme si toglie
    assert fb.get_rtdb("/demo_binance/allarmi/ordini_rifiutati") is None


def test_ordini_4_rifiuto_piccolo_solo_dalla_seconda_decisione_di_fila(tmp_path):
    """CUSDT pesa lo 0,5% (sotto l'1%): rifiutata a una decisione niente allarme; a due decisioni di fila sì; una decisione senza
    rifiuto in mezzo azzera il conto."""
    pesi = {"AUSDT": 0.5, "BUSDT": -0.5, "CUSDT": 0.005}
    finto = _DemoStati(("AUSDT", "BUSDT", "CUSDT"))
    rifiuto = (_rifiutata(), {"LIMIT"})
    finto.rifiuti[("/fapi/v1/order", "CUSDT")] = rifiuto
    d, fb = _demo_semplice(tmp_path, finto, pesi=pesi)
    d.tick(T0)
    assert fb.get_rtdb("/demo_binance/ribilanciamenti/2026-10-24")["rifiutati"][0]["peso"] == 0.005
    assert fb.get_rtdb("/demo_binance/allarmi/ordini_rifiutati") is None
    for g in (20751, 20752):                                     # 25 ottobre di nuovo rifiutata, 26 ottobre eseguita
        if g == 20752:
            finto.rifiuti.pop(("/fapi/v1/order", "CUSDT"))
        d.tick((g - 1) * 86400.0 + 400 + 3601)
        _decide(tmp_path, g, pesi)
        d.tick(g * 86400.0 + 400)
        if g == 20751:
            al = fb.get_rtdb("/demo_binance/allarmi/ordini_rifiutati")
            assert al["monete"][0]["simbolo"] == "CUSDT" and al["monete"][0]["decisioni_di_fila"] == 2
            assert "2 decisioni di fila" in al["testo"]
    assert fb.get_rtdb("/demo_binance/allarmi/ordini_rifiutati") is None
    finto.rifiuti[("/fapi/v1/order", "CUSDT")] = rifiuto
    d.tick(20752 * 86400.0 + 400 + 3601)
    _decide(tmp_path, 20753, pesi)
    d.tick(20753 * 86400.0 + 400)                                # rifiutata di nuovo, ma dopo una decisione buona: niente allarme
    assert fb.get_rtdb("/demo_binance/allarmi/ordini_rifiutati") is None


def test_ordini_4_resto_a_mercato_rifiutato_scritto_e_con_l_allarme(tmp_path):
    finto = _DemoStati()
    d, fb = _demo_semplice(tmp_path, finto)
    avvisi = _avvisi(d)
    d.tick(T0)                                                   # BUSDT non si esegue a limite (il finto esegue solo AUSDT)
    assert fb.get_rtdb("/demo_binance/allarmi/ordini_rifiutati") is None
    finto.rifiuti[("/fapi/v1/order", "BUSDT")] = (_errore(-2019, "Margin is insufficient."), {"MARKET"})
    d.tick(T0 + 3601)                                            # il resto a mercato di BUSDT è rifiutato
    resti = fb.get_rtdb("/demo_binance/ribilanciamenti/2026-10-24/resti_rifiutati")
    assert [(r["simbolo"], r["peso"]) for r in resti] == [("BUSDT", pytest.approx(-0.5, abs=1e-3))]
    assert "Margin is insufficient" in resti[0]["errore"]
    al = fb.get_rtdb("/demo_binance/allarmi/ordini_rifiutati")
    assert "resto a mercato" in al["testo"] and al["monete"][0]["dove"] == "resti"
    assert len(_di(avvisi, "ordini rifiutati")) == 1


def test_ordini_4_e_5_il_conto_vero_non_salta_e_l_allarme_conta_le_decisioni(tmp_path, monkeypatch):
    """Sul conto vero ogni rifiuto è vero: la moneta si riprova a ogni decisione (niente «non disponibile») e l'allarme dice le
    decisioni di fila; al telefono una volta, con il nome del conto vero."""
    finto = _VeroStati()
    finto.rifiuti[("/fapi/v1/order", "BUSDT")] = (_errore(-4140, "Invalid symbol status for opening position."), {"LIMIT"})
    d, fb, finto = T._conto(tmp_path, monkeypatch, finto)
    avvisi = _avvisi(d)
    T._fino_alla_decisione_dopo(d, tmp_path)
    rib = fb.get_rtdb("/conto_vero/ribilanciamenti/2026-10-25")
    assert [r["simbolo"] for r in rib["rifiutati"]] == ["BUSDT"] and "non_disponibili_sul_demo" not in rib
    assert fb.get_rtdb("/conto_vero/allarmi/ordini_rifiutati")["monete"][0]["decisioni_di_fila"] == 1
    d.tick(T.DOPO + 3700)
    T._decisione(tmp_path, T.GIORNO + 2)
    d.tick((T.GIORNO + 2) * 86400.0 + 400)
    assert len([q for q in _post(finto) if q["symbol"] == "BUSDT" and q["type"] == "LIMIT"]) == 2
    al = fb.get_rtdb("/conto_vero/allarmi/ordini_rifiutati")
    assert al["decisione"] == "2026-10-26" and "2 decisioni di fila" in al["testo"] and "si salta" not in al["testo"]
    mandati = _di(avvisi, "ordini rifiutati")
    assert len(mandati) == 1 and mandati[0].startswith("<b>CONTO VERO di Binance (G1)</b>")


# ---------------------------------------------------------------------------------------------------------------------------------
# salute-6: gli allarmi al telefono, una volta
# ---------------------------------------------------------------------------------------------------------------------------------
def test_salute_6_lo_stop_e_il_conto_non_vuoto_al_telefono_una_volta(tmp_path):
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    avvisi = _avvisi(d)
    d.tick(T0)
    finto.posizioni = {"AUSDT": 50.0, "BUSDT": -100.0}            # le chiusure non svuotano il conto (posizioni ferme)
    finto.equity = "6400"
    d.tick(T0 + 61)                                              # −36%: lo stop
    stop = _di(avvisi, "stop")
    assert len(stop) == 1 and "stop sul conto: -36.0%" in stop[0] and stop[0].startswith("<b>Demo di Binance (G1)</b>")
    assert fb.get_rtdb("/demo_binance/fermo")["telefono"] == T0 + 61
    for k in range(2, 9):                                        # da fermo ogni minuto: allarme dal terzo tentativo
        d.tick(T0 + 61 * k)
    assert len(_di(avvisi, "stop")) == 1
    non_vuoto = _di(avvisi, "fermo conto non vuoto")
    assert len(non_vuoto) == 1 and "AUSDT" in non_vuoto[0]
    assert fb.get_rtdb("/demo_binance/allarme")["telefono"] and "dopo 8 tentativi" in fb.get_rtdb("/demo_binance/allarme")["testo"]


def test_salute_6_il_blocco_418_al_telefono_una_volta_per_blocco(tmp_path, monkeypatch):
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    _attese(monkeypatch)
    avvisi = _avvisi(d)
    bloccato = _Risposta({"code": -1003, "msg": "Way too many requests; IP banned until 1792800700000."}, 418,
                         headers={"Retry-After": "300"})
    finto.guasti[("GET", "/fapi/v2/account", None)] = bloccato
    d.tick(T0)
    assert len(_di(avvisi, "blocco 418")) == 1 and "bloccato da Binance (418)" in _di(avvisi, "blocco 418")[0]
    assert fb.get_rtdb("/demo_binance/allarmi/limiti_binance")["telefono"] == T0
    finto.guasti[("GET", "/fapi/v2/account", None)] = bloccato
    d.tick(T0 + 301)                                             # ancora bloccato: niente di nuovo
    assert len(_di(avvisi, "blocco 418")) == 1
    d.tick(T0 + 602)                                             # un giro buono: l'allarme si toglie
    assert fb.get_rtdb("/demo_binance/allarmi/limiti_binance") is None
    finto.guasti[("GET", "/fapi/v2/account", None)] = bloccato
    d.tick(T0 + 3700)                                            # un blocco nuovo, oltre l'ora: di nuovo al telefono
    assert len(_di(avvisi, "blocco 418")) == 2


def test_salute_6_un_429_che_dura_non_va_al_telefono(tmp_path, monkeypatch):
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    _attese(monkeypatch)
    avvisi = _avvisi(d)
    _sempre(d, finto, "GET", "/fapi/v2/account", _Risposta({"code": -1003, "msg": "Too many requests"}, 429))
    d.tick(T0)
    assert fb.get_rtdb("/demo_binance/allarmi/limiti_binance") and avvisi == []


def test_salute_6_errori_ripetuti_allarme_e_telefono_una_volta(tmp_path):
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    avvisi = _avvisi(d)
    _sempre(d, finto, "GET", "/fapi/v2/account", _Risposta({"code": -1001, "msg": "Internal error <b>"}, 500))
    for k in range(2):
        d.tick(T0 + 61 * k)
    assert fb.get_rtdb("/demo_binance/allarmi/errori_ripetuti") is None   # due errori: non ancora
    for k in range(2, 6):
        d.tick(T0 + 61 * k)
    al = fb.get_rtdb("/demo_binance/allarmi/errori_ripetuti")
    assert al["dove"] == ["protezioni"] and "protezioni: in errore a ogni giro" in al["testo"] and al["telefono"] == T0 + 122
    mandati = _di(avvisi, "errori ripetuti")
    assert len(mandati) == 1 and "&lt;b&gt;" in mandati[0] and "Internal error <b>" not in mandati[0]   # HTML tolto
    d._cliente.http = finto                                      # Binance torna a rispondere
    d.tick(T0 + 61 * 6)
    assert fb.get_rtdb("/demo_binance/allarmi/errori_ripetuti") is None


def test_salute_6_un_allarme_va_al_telefono_quando_si_accende_non_quando_cambia(tmp_path):
    """Un allarme del demo (qui la decisione di G1 vecchia) va al telefono quando si accende; il testo che cambia a ogni ora no; dopo
    che si è spento e riacceso, sì (oltre l'ora). ``telefono`` nell'allarme dice quando l'ha mandato il bot."""
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    avvisi = _avvisi(d)
    d.tick(20750 * 86400.0 + 27 * 3600)
    d.tick(20750 * 86400.0 + 28 * 3600)                          # il testo cambia («28 ore fa»): niente di nuovo
    assert len(_di(avvisi, "decisione g1")) == 1
    assert fb.get_rtdb("/demo_binance/allarmi/decisione_g1")["telefono"] == 20750 * 86400.0 + 27 * 3600
    _decide(tmp_path, 20751)
    d.tick(20751 * 86400.0 + 400)
    assert fb.get_rtdb("/demo_binance/allarmi/decisione_g1") is None
    d.tick(20752 * 86400.0 + 3 * 3600)                           # di nuovo vecchia: si riaccende
    assert len(_di(avvisi, "decisione g1")) == 2


def test_salute_6_il_conto_vero_manda_i_suoi_allarmi_al_telefono(tmp_path, monkeypatch):
    d, fb, finto = T._conto(tmp_path, monkeypatch, codice=lambda: "file del codice diversi dalla versione approvata")
    avvisi = _avvisi(d)
    d.tick(T.MEZZOGIORNO)
    d.tick(T.MEZZOGIORNO + 60)
    vietati = _di(avvisi, "ordini vietati")
    assert len(vietati) == 1 and vietati[0].startswith("<b>CONTO VERO di Binance (G1)</b>")
    assert fb.get_rtdb("/conto_vero/allarmi/ordini_vietati")["telefono"] == T.MEZZOGIORNO


def test_salute_6_l_avviso_usa_il_notificatore_in_un_filo_e_non_solleva(monkeypatch):
    from bot.execution import notifier
    mandati = []
    monkeypatch.setattr(notifier.TelegramNotifier, "send", lambda self, testo: mandati.append(testo))
    dm.avviso_telegram("nei test")                               # nei test non parte niente
    assert mandati == [] and not [t for t in threading.enumerate() if t.name == "avviso_telegram"]
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    def aspetta():
        for t in threading.enumerate():
            if t.name == "avviso_telegram":
                t.join(timeout=5)

    dm.avviso_telegram("<b>prova</b>")
    aspetta()
    assert mandati == ["<b>prova</b>"]

    def rotto(self, testo):
        raise RuntimeError("Telegram giù")
    monkeypatch.setattr(notifier.TelegramNotifier, "send", rotto)
    dm.avviso_telegram("niente")                                 # non solleva, nemmeno nel filo
    aspetta()


# ---------------------------------------------------------------------------------------------------------------------------------
# salute-10: la libreria della firma nei requisiti
# ---------------------------------------------------------------------------------------------------------------------------------
def test_salute_10_cryptography_fissata_nei_requisiti():
    righe = [r.strip() for r in (RADICE / "requirements.txt").read_text(encoding="utf-8").splitlines()]
    assert [r for r in righe if re.fullmatch(r"cryptography==\d+\.\d+\.\d+", r)]


# ---------------------------------------------------------------------------------------------------------------------------------
# Revisione del 27 novembre 2026 (reviews/reports/2026-11-27-bot.md), problema 210: sulle monete che il demo salta si saltano solo
# le aperture e gli aumenti; le chiusure e le riduzioni partono sempre, con «solo riduzione» (demo_binance.py, ``and not riduce``).
# Prima nessun test lo provava: i test qui sopra partono tutti da un conto vuoto. Le prove S1, S2, S4 del revisore.
# ---------------------------------------------------------------------------------------------------------------------------------
def _ordini_di(finto, simbolo, da=0):
    return [q for m_, p, q in finto.chiamate[da:] if m_ == "POST" and p == "/fapi/v1/order" and q.get("symbol") == simbolo]


def test_210_chiusura_su_una_moneta_in_settling_parte_con_solo_riduzione(tmp_path):
    """Una posizione tenuta (corta) su una moneta passata in SETTLING e l'obiettivo zero: parte l'ordine che la chiude, con
    «solo riduzione», e la moneta non finisce fra le saltate."""
    finto = _DemoStati(stati={"BUSDT": "SETTLING"})
    finto.posizioni = {"AUSDT": 0.0, "BUSDT": -100.0}
    d, fb = _demo_semplice(tmp_path, finto, pesi={"AUSDT": 0.5})
    d.tick(T0)
    o = _ordini_di(finto, "BUSDT")
    assert len(o) == 1 and o[0]["side"] == "BUY" and o[0]["type"] == "LIMIT" and o[0].get("reduceOnly") == "true", finto.chiamate
    assert float(o[0]["quantity"]) == pytest.approx(100.0)
    rib = fb.get_rtdb("/demo_binance/ribilanciamenti/2026-10-24")
    assert rib["non_disponibili_sul_demo"] == [] and rib["rifiutati"] == []


def test_210_riduzione_dallo_stesso_lato_su_una_moneta_in_settling_parte_con_solo_riduzione(tmp_path):
    """Da −150 a circa −40 su una moneta in SETTLING: è una riduzione dallo stesso lato, parte con «solo riduzione»."""
    finto = _DemoStati(stati={"BUSDT": "SETTLING"})
    finto.posizioni = {"AUSDT": 0.0, "BUSDT": -150.0}
    d, fb = _demo_semplice(tmp_path, finto, pesi={"AUSDT": 0.5, "BUSDT": -0.2})
    d.tick(T0)
    o = _ordini_di(finto, "BUSDT")
    assert len(o) == 1 and o[0]["side"] == "BUY" and o[0].get("reduceOnly") == "true"
    assert float(o[0]["quantity"]) == pytest.approx(150.0 - 0.2 * 10000 / 50.007, abs=0.01)
    assert fb.get_rtdb("/demo_binance/ribilanciamenti/2026-10-24")["non_disponibili_sul_demo"] == []


def test_210_chiusura_dopo_un_4140_ricordato_parte_con_solo_riduzione(tmp_path):
    """Un aumento del corto rifiutato con -4140 mette la moneta nella memoria delle non disponibili; il giorno dopo l'obiettivo è
    zero e la moneta è ancora nella memoria: la chiusura parte lo stesso, con «solo riduzione»."""
    finto = _DemoStati()
    finto.posizioni = {"AUSDT": 0.0, "BUSDT": -100.0}
    finto.rifiuti[("/fapi/v1/order", "BUSDT")] = (_errore(-4140, "Invalid symbol status for opening position."), {"LIMIT"})
    d, fb = _demo_semplice(tmp_path, finto, pesi={"AUSDT": 0.5, "BUSDT": -0.58})    # aumenta il corto: rifiutato, ricordato
    d.tick(T0)
    assert d.carica()["memoria_non_disponibili"]["BUSDT"]["codice"] == -4140
    d.tick(T0 + 3601)
    finto.rifiuti.clear()
    n = len(finto.chiamate)
    _decide(tmp_path, 20751, {"AUSDT": 0.5})
    assert "BUSDT" in d.carica()["memoria_non_disponibili"]                          # ancora «non disponibile» al giro dopo
    d.tick(T0 + 86400)
    o = _ordini_di(finto, "BUSDT", n)
    assert len(o) == 1 and o[0]["side"] == "BUY" and o[0].get("reduceOnly") == "true"
    assert fb.get_rtdb("/demo_binance/ribilanciamenti/2026-10-25")["non_disponibili_sul_demo"] == []


def test_213_l_inversione_su_una_moneta_non_disponibile_chiude_con_solo_riduzione_e_non_apre(tmp_path):
    """Problema 213, corretto il 28 novembre 2026 (prima questo test descriveva il difetto: l'inversione si saltava intera e il corto
    restava aperto, senza allarme). `ordini_del_giorno` dà ancora un ordine solo (100 per chiudere + 60 per aprire); sulla moneta che
    si può solo ridurre il ribilancio manda solo la chiusura, con «solo riduzione», e niente apertura nel verso nuovo; la moneta resta
    fra le saltate. Dopo l'ora il resto a mercato chiude quello che manca e non apre (senza il segno ``solo_riduzione`` sarebbe un
    acquisto di 160 senza «solo riduzione»)."""
    assert dm.ordini_del_giorno({"B": 0.3}, {"B": -100.0}, {"B": 50.0}, 10000.0, {"B": (0.01, 0.001, 0.001, 5.0)}) == [
        ("B", "BUY", pytest.approx(160.0), 50.0, False)]                              # 100 per chiudere + 60 per aprire, un ordine
    finto = _DemoStati(stati={"BUSDT": "SETTLING"})
    finto.posizioni = {"AUSDT": 0.0, "BUSDT": -100.0}
    d, fb = _demo_semplice(tmp_path, finto, pesi={"AUSDT": 0.5, "BUSDT": 0.3})
    d.tick(T0)
    o = _ordini_di(finto, "BUSDT")
    assert len(o) == 1 and o[0]["side"] == "BUY" and o[0]["type"] == "LIMIT" and o[0].get("reduceOnly") == "true", o
    assert float(o[0]["quantity"]) == pytest.approx(100.0)                            # solo la chiusura del corto
    rib = fb.get_rtdb("/demo_binance/ribilanciamenti/2026-10-24")
    assert [x["simbolo"] for x in rib["non_disponibili_sul_demo"]] == ["BUSDT"]       # l'apertura del lungo saltata
    assert [x for x in d.carica()["ordini"]["lista"] if x["simbolo"] == "BUSDT"][0]["solo_riduzione"] is True
    n = len(finto.chiamate)
    d.tick(T0 + 3601)                                                                # dopo l'ora: il limite non eseguito
    m = [q for q in _ordini_di(finto, "BUSDT", n) if q["type"] == "MARKET"]
    assert len(m) == 1 and m[0]["side"] == "BUY" and m[0].get("reduceOnly") == "true"
    assert float(m[0]["quantity"]) == pytest.approx(100.0)                            # chiude e non apre


# ---------------------------------------------------------------------------------------------------------------------------------
# Revisione del 27 novembre 2026, problema 216: i ripieghi. La lettura di ogni ora (demo e paper di G1) in errore non ferma il
# ribilancio; con un limite di Binance ferma il giro del demo come per le protezioni; un telefono che solleva non ferma le chiusure.
# Le prove S5, S5b e S7 del revisore, più quella del paper.
# ---------------------------------------------------------------------------------------------------------------------------------
def test_216_lettura_dell_ora_del_demo_in_errore_non_ferma_il_ribilancio(tmp_path, monkeypatch, capsys):
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)

    def rotta(c, st, now):
        raise ValueError("lettura rotta")
    monkeypatch.setattr(d, "lettura_oraria", rotta)
    d.tick(T0)
    assert d.carica()["ultimo_giorno"] == 20750 and _post(finto)                    # il ribilancio è partito
    assert "lettura dell'ora non riuscita, si riprova fra 5 minuti" in capsys.readouterr().out
    assert d._protezioni_ferme_fino <= T0                                            # le protezioni non aspettano


def test_216_lettura_dell_ora_del_demo_con_un_429_ferma_il_giro_come_le_protezioni(tmp_path, monkeypatch):
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    chiamate = []

    def limite(c, st, now):
        chiamate.append(now)
        raise dm.LimiteBinance("429 troppe richieste", 60, codice=429)
    monkeypatch.setattr(d, "lettura_oraria", limite)
    d.tick(T0)
    assert chiamate == [T0] and not _post(finto)                                     # niente ordini in questo giro
    assert d._protezioni_ferme_fino == T0 + 60                                       # e niente richieste per l'attesa chiesta
    al = fb.get_rtdb("/demo_binance/allarmi/limiti_binance")
    assert al["codice"] == 429 and "lettura dell'ora" in al["testo"] and "telefono" not in al
    assert d.carica().get("ultimo_giorno") is None
    n = len(finto.chiamate)
    d.tick(T0 + 30)                                                                  # durante l'attesa: nessuna richiesta
    assert len(finto.chiamate) == n
    monkeypatch.setattr(d, "lettura_oraria", lambda c, st, now: None)
    d.tick(T0 + 61)                                                                  # dopo l'attesa: il giro riparte
    assert d.carica()["ultimo_giorno"] == 20750 and _post(finto)
    assert fb.get_rtdb("/demo_binance/allarmi/limiti_binance") is None


def test_216_un_telefono_che_solleva_dentro_chiudi_tutto_non_ferma_le_chiusure(tmp_path):
    """Il pulsante a file del demo con Telegram che solleva: il fermo si scrive e le chiusure a mercato («solo riduzione») partono."""
    finto = _Demo()
    finto.posizioni_vive = True
    d, fb = _demo_semplice(tmp_path, finto)
    d.tick(T0)
    d.tick(T0 + 3601)

    def esplode(testo):
        raise RuntimeError("telegram giù")
    d.avvisa = esplode
    (tmp_path / "chiudi").write_text("chiudi 1")
    d.file_chiudi = tmp_path / "chiudi"
    n = len(finto.chiamate)
    d.tick(T0 + 3700)
    assert d.carica().get("fermo")
    chiusure = [q for m_, p, q in finto.chiamate[n:] if m_ == "POST" and p == "/fapi/v1/order" and q.get("type") == "MARKET"
                and q.get("reduceOnly") == "true"]
    assert {q["symbol"] for q in chiusure} == {"AUSDT", "BUSDT"}
    assert fb.get_rtdb("/demo_binance/fermo")["chiuse"] == 2


def test_216_lettura_dell_ora_del_paper_in_errore_non_ferma_il_ribilancio(tmp_path, monkeypatch, capsys):
    """Il paper di G1 (f5.py, ``tick``): una lettura di ogni ora che solleva si scrive nel log e si riprova dopo 5 minuti; il
    ribilancio del giorno parte lo stesso."""
    m = f5.lunedi_di(20750)
    finto = _Finto(m)
    fb = _InMemoryStore()
    (tmp_path / "acceso").write_text("si")
    p = f5.PaperG1(fb, chiedi=finto, file_stato=tmp_path / "g1.json", interruttore=tmp_path / "acceso", pausa_s=0.0)
    now = (m + 2) * 86400.0 + 360
    finto.adesso_ms = int(now * 1000)
    p.tick(now)                                                 # il primo ribilancio (senza stato: niente lettura prima)
    assert p.carica()["ultimo_lunedi"] == m + 2
    chiamate = []

    def rotta(st, adesso):
        chiamate.append(adesso)
        raise ValueError("lettura rotta")
    monkeypatch.setattr(p, "lettura_oraria", rotta)
    p._ultimo_tentativo = 0.0
    now = (m + 3) * 86400.0 + 360
    finto.adesso_ms = int(now * 1000)
    p.tick(now)
    assert chiamate == [now]
    assert p.carica()["ultimo_lunedi"] == m + 3                 # il ribilancio del giorno è partito
    assert fb.get_rtdb("/paper_g1/ribilanciamenti/" + time.strftime("%Y-%m-%d", time.gmtime((m + 3) * 86400)))
    assert p._lettura_riprova_dopo == now + f5.ATTESA_LETTURA_S
    assert "lettura dell'ora non riuscita, si riprova fra 5 minuti" in capsys.readouterr().out
