"""Le correzioni del 28 novembre 2026 nel conto vero e nel demo (decisione del proprietario del 28 novembre, `docs/decisioni_del_proprietario.md`,
e revisioni del 27 novembre: `reviews/reports/2026-11-27-bot.md`, `2026-11-27-bot-bis.md`, `audits/reports/2026-11-27-F5_CONTO_VERO.md`):

* il conto vero esegue di nuovo G1: il file del paper di G1, l'età della decisione di 26 ore, i testi (problema 183);
* il capitale non si scrive più a mano: il saldo USDT del portafoglio dei future letto da Binance, al massimo il tetto del codice;
* le chiusure intere sotto il valore minimo partono con «solo riduzione» (audit di F5, problema Alto 2); le riduzioni sotto il minimo
  si saltano come le aperture (problema 269, 28 novembre);
* 211 (`telefono` solo a invio riuscito), 213 (l'inversione su una moneta che si può solo ridurre), 219 (il 429 che dura), 220 (il
  limite di uno all'ora per tipo, e mai per il fermo), nel bot e nel monitor.

Ogni test fallirebbe con il codice di prima. Nessuna richiesta di rete vera: i Binance finti dei test del demo e del conto vero."""
from __future__ import annotations

import tests.conftest  # noqa: F401  (stesso isolamento della suite: prima di ogni import di bot)

import json
import threading
from urllib.parse import parse_qs, urlparse

import pytest

from bot.portafoglio import conto_vero as cv
from bot.portafoglio import demo_binance as dm
from bot.portafoglio import f5
from scripts import monitor
from scripts import state_snapshot as ss
from tests import test_conto_vero as T
from tests.test_demo_binance import _Demo, _Risposta, _attese, _demo_semplice, _post, _sempre
from tests.test_portafoglio_audit import _VeroStati, _avvisi, _di, _errore, _ordini_di

T0 = 20750 * 86400.0 + 400                       # 24 ottobre 2026, 00:06:40 UTC: la decisione di G1 del giorno nel file
G2 = (T.GIORNO + 2) * 86400.0 + 400              # la decisione di G1 di due giorni dopo l'accensione


def _limiti(finto, da=0):
    return {q["symbol"]: (q["side"], q["quantity"]) for q in _post(finto)[da:] if q["type"] == "LIMIT"}


def _primo_ribilancio(d, tmp_path, finto):
    """Acceso a mezzogiorno, la decisione del giorno dopo, poi il resto a mercato dopo l'ora (con ``posizioni_vive`` le posizioni
    vere: AUSDT eseguito a limite, BUSDT a mercato)."""
    T._fino_alla_decisione_dopo(d, tmp_path)
    d.tick(T.DOPO + 3700)


# ---------------------------------------------------------------------------------------------------------------------------------
# il conto vero esegue G1 (problema 183: i testi)
# ---------------------------------------------------------------------------------------------------------------------------------
def test_g1_di_serie_il_file_del_paper_di_g1_e_26_ore():
    d = cv.ContoVeroG1(T._Fb(), verifica_codice=lambda: None)
    assert d.file_g1 == dm.FILE_G1 == f5.PaperG1.FILE_DI_SERIE and d.STRATEGIA == "G1"
    assert d.ETA_MASSIMA_DECISIONE_S == dm.ETA_MASSIMA_DECISIONE_S == 26 * 3600
    assert cv.CAPITALE_MASSIMO == 300.0                                    # il tetto resta: 250 USDT stanno sotto


def test_g1_testi_del_log_dell_avvio_e_dell_allarme_della_decisione(tmp_path, monkeypatch, capsys):
    d, fb, finto = T._conto(tmp_path, monkeypatch)
    d.tick(T.MEZZOGIORNO)
    out = capsys.readouterr().out
    assert "acceso: ordini solo dalla prima decisione di G1 dopo quella del 2026-10-24 (la mezzanotte UTC, alle 00:05)" in out
    avvio = fb.get_rtdb("/conto_vero/avvio")
    assert avvio["strategia"] == "G1" and avvio["eta_massima_decisione_ore"] == 26 and "saldo USDT" in avvio["capitale"]
    d.tick(T.GIORNO * 86400.0 + 27 * 3600)                                # nessuna decisione nuova: 27 ore dopo
    testo = fb.get_rtdb("/conto_vero/allarmi/decisione_g1")["testo"]
    assert "la decisione di G1 è del 2026-10-24, 27 ore fa (oltre 26)" in testo and "F5" not in testo


def test_g1_la_versione_pubblicata_dice_la_strategia(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    T._repo(repo)
    d, fb, finto = T._conto(tmp_path, monkeypatch, acceso=False, dry_run="true", radice=repo)
    d.tick(T.MEZZOGIORNO)
    assert fb.get_rtdb("/conto_vero/versione")["strategia"] == "G1"


def test_g1_il_titolo_dello_stato_e_il_capitale_della_fase():
    fb = T._Fb()
    fb.set_rtdb("/conto_vero/stato", {"stato": "acceso", "equity": 301.0, "capitale_iniziale": 300.0, "aggiornato": T.MEZZOGIORNO,
                                      "capitale_della_fase": {"capitale": 300.0, "saldo_usdt_letto": 412.5, "tetto": 300.0,
                                                              "limitato_dal_tetto": True}})
    righe = ss.sezione_conto_vero(fb)
    assert righe[0].startswith("## G1 sul conto vero di Binance")
    assert ("- capitale della fase: $300.00, dal saldo USDT dei future letto da Binance ($412.50; tetto $300; **limitato dal "
            "tetto**)") in righe


# ---------------------------------------------------------------------------------------------------------------------------------
# il capitale dal saldo USDT del portafoglio dei future (il proprietario, 28 novembre 2026)
# ---------------------------------------------------------------------------------------------------------------------------------
def test_saldo_usdt_e_la_riga_usdt_del_portafoglio():
    conto = {"totalWalletBalance": "999", "assets": [{"asset": "BNB", "walletBalance": "5"},
                                                     {"asset": "USDT", "walletBalance": "251.37", "availableBalance": "100"}]}
    assert dm.saldo_usdt(conto) == 251.37                                  # non il totale, non il margine disponibile
    for rotto in ({}, {"assets": []}, {"assets": [{"asset": "USDT", "walletBalance": "abc"}]},
                  {"assets": [{"asset": "USDT", "walletBalance": "nan"}]}, {"assets": [{"asset": "USDT"}]}, None, {"assets": "x"}):
        assert dm.saldo_usdt(rotto) is None, rotto


def test_capitale_saldo_sotto_il_tetto_si_usa_tutto(tmp_path, monkeypatch):
    """Nessun numero scritto a mano: 250 USDT nel portafoglio, il conto lavora con 250."""
    finto = T._Vero()
    finto.equity = "250"
    d, fb, finto = T._conto(tmp_path, monkeypatch, finto, capitale=None)
    T._fino_alla_decisione_dopo(d, tmp_path)
    assert _limiti(finto) == {"AUSDT": ("BUY", "1.249"), "BUSDT": ("SELL", "2.499")}      # 0,5 × 250 USDT ai prezzi mark
    cr = fb.get_rtdb("/conto_vero/conto_ridotto")
    assert cr["capitale"] == 250.0 and cr["saldo_usdt_letto"] == 250.0 and cr["limitato_dal_tetto"] is False
    assert cr["tetto"] == 300.0 and cr["limite_del_file"] is None and cr["perche"] == "prima fase"


def test_capitale_saldo_sopra_il_tetto_si_lavora_con_il_tetto(tmp_path, monkeypatch, capsys):
    finto = T._Vero()                                                      # 10.000 USDT nel portafoglio
    d, fb, finto = T._conto(tmp_path, monkeypatch, finto, capitale=None)
    T._fino_alla_decisione_dopo(d, tmp_path)
    assert _limiti(finto) == {"AUSDT": ("BUY", "1.499"), "BUSDT": ("SELL", "2.999")}      # 0,5 × 300, non × 10.000
    cr = fb.get_rtdb("/conto_vero/conto_ridotto")
    assert cr["capitale"] == 300.0 and cr["saldo_usdt_letto"] == 10000.0 and cr["limitato_dal_tetto"] is True
    assert "saldo del portafoglio USDT 10,000.00 sopra il tetto di 300: il conto vero lavora con 300 USDT" in capsys.readouterr().out
    d.tick(T.DOPO + 3700)                                                  # la valutazione dell'ora scrive lo stato
    stato = fb.get_rtdb("/conto_vero/stato")
    assert stato["capitale_della_fase"]["limitato_dal_tetto"] is True and stato["capitale_della_fase"]["capitale"] == 300.0


def test_capitale_il_file_e_solo_un_limite_piu_basso_e_un_numero_nuovo_fa_una_fase_nuova(tmp_path, monkeypatch):
    finto = T._Vero()
    d, fb, finto = T._conto(tmp_path, monkeypatch, finto, capitale="250")
    _primo_ribilancio(d, tmp_path, finto)
    cr = fb.get_rtdb("/conto_vero/conto_ridotto")
    assert cr["capitale"] == 250.0 and cr["limite_del_file"] == 250.0 and cr["limitato_dal_tetto"] is True
    (tmp_path / "conto_vero_capitale").write_text("200")
    d.tick(T.DOPO + 4000)
    assert fb.get_rtdb("/conto_vero/capitale_in_attesa")["perche"] == "numero nuovo nel file (200)"
    n = len(_post(finto))
    assert _limiti(finto, n) == {}                                         # niente a metà giornata
    T._decisione(tmp_path, T.GIORNO + 2)
    d.tick(G2)
    assert fb.get_rtdb("/conto_vero/conto_ridotto")["capitale"] == 200.0
    assert _limiti(finto, n) == {"AUSDT": ("BUY", "0.999"), "BUSDT": ("SELL", "1.999")}


@pytest.mark.parametrize("saldo", ["manca", "0", "-5", "abc", "nan"])
def test_capitale_saldo_letto_male_o_a_zero_niente_ordini(tmp_path, monkeypatch, saldo):
    finto = T._Vero()
    finto.saldo_usdt = saldo
    d, fb, finto = T._conto(tmp_path, monkeypatch, finto, capitale=None)
    T._fino_alla_decisione_dopo(d, tmp_path)
    assert T._scritture(finto) == []
    assert "il saldo del portafoglio USDT dei future non si legge o è zero" in fb.get_rtdb("/conto_vero/allarmi/ordini_vietati")["testo"]
    assert fb.get_rtdb("/conto_vero/conto_ridotto") is None


def test_capitale_saldo_che_non_si_legge_piu_dopo_l_accensione_niente_ordini_nuovi(tmp_path, monkeypatch):
    finto = T._Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = T._conto(tmp_path, monkeypatch, finto, capitale=None)
    _primo_ribilancio(d, tmp_path, finto)
    finto.saldo_usdt = "manca"
    n = len(_post(finto))
    T._decisione(tmp_path, T.GIORNO + 2, {"AUSDT": 0.6, "BUSDT": -0.4})
    d.tick(G2)
    assert not [q for q in _post(finto)[n:] if q.get("reduceOnly") != "true"]      # nessun ordine che apra
    assert "saldo del portafoglio USDT" in fb.get_rtdb("/conto_vero/allarmi/ordini_vietati")["testo"]


def test_capitale_prelievo_dopo_l_accensione_fase_nuova_alla_decisione_dopo(tmp_path, monkeypatch):
    """Il proprietario preleva 100 USDT dopo l'accensione: niente stop (il valore del bot non conta i prelievi), niente ordini nuovi
    dalla terza lettura del saldo sotto il valore, e alla decisione di G1 dopo il bot chiude tutto, rilegge il saldo (180) e riparte
    da zero con quello (prima restava bloccato finché non si scriveva un capitale nuovo, e nemmeno quello lo sbloccava)."""
    _attese(monkeypatch)
    finto = T._Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = T._conto(tmp_path, monkeypatch, finto, capitale=None)
    _primo_ribilancio(d, tmp_path, finto)
    assert finto.posizioni["AUSDT"] > 0 > finto.posizioni["BUSDT"]
    finto.equity = "180"
    finto.entrate.append(T._riga("TRANSFER", -100.0, dopo_s=3750))
    for k in range(3):                                                     # tre letture di fila, a un minuto (problema 64)
        d.tick(T.DOPO + 3800 + 60 * k)
    st = d.carica()
    assert "fermo" not in st and st["prelievo"]["saldo"] == 180.0
    assert st["capitale_in_attesa"] == 300.0 and st["fase_nuova"]["perche"] == "prelievo"
    vietati = fb.get_rtdb("/conto_vero/allarmi/ordini_vietati")["testo"]
    assert "un prelievo?" in vietati and "rilegge il saldo di Binance e riparte da zero" in vietati
    n = len(_post(finto))
    d.tick(T.DOPO + 7200)                                                  # a metà giornata niente
    assert _post(finto)[n:] == []
    T._decisione(tmp_path, T.GIORNO + 2)
    d.tick(G2)
    nuovi = _post(finto)[n:]
    chiusure = [(q["symbol"], q["side"]) for q in nuovi if q["type"] == "MARKET" and q.get("reduceOnly") == "true"]
    assert sorted(chiusure) == [("AUSDT", "SELL"), ("BUSDT", "BUY")]       # prima si chiude tutto
    assert _limiti(finto, n) == {"AUSDT": ("BUY", "0.899"), "BUSDT": ("SELL", "1.799")}   # poi 0,5 × 180
    cr = fb.get_rtdb("/conto_vero/conto_ridotto")
    assert cr["capitale"] == 180.0 and cr["perche"] == "prelievo" and cr["saldo_usdt_letto"] == 180.0
    st = d.carica()
    assert not {"prelievo", "saldo_sotto", "fase_nuova", "capitale_in_attesa", "fermo"} & set(st)
    assert fb.get_rtdb("/conto_vero/allarmi/ordini_vietati") is None


def test_capitale_dopo_chiudi_tutto_e_riparti_la_fase_resta_e_non_si_rilegge(tmp_path, monkeypatch):
    """Dopo un fermo e «riparti» il capitale non si rilegge: la fase resta (le perdite sono già nel valore del bot e il pavimento del 65%
    resta sul capitale di partenza, decisione dell'8 novembre 2026); si riapre alla decisione di G1 dopo con il valore del bot."""
    finto = T._Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = T._conto(tmp_path, monkeypatch, finto, capitale=None)
    _primo_ribilancio(d, tmp_path, finto)
    dal = fb.get_rtdb("/conto_vero/conto_ridotto")["dal"]
    fb.proprietario(cv.COMANDO_CHIUDI, True)
    d.tick(T.DOPO + 4000)
    d.tick(T.DOPO + 4100)                                                  # conto vuoto
    T._riparti_in_due_passi(fb)
    d.tick(T.DOPO + 4200)
    assert not d.carica().get("fermo")
    finto.equity = "290"                                                   # (un versamento di 10: non si usa da solo)
    n = len(_post(finto))
    T._decisione(tmp_path, T.GIORNO + 2)
    d.tick(G2)
    cr = fb.get_rtdb("/conto_vero/conto_ridotto")
    assert cr["dal"] == dal and cr["capitale"] == 280.0                    # la stessa fase
    assert _limiti(finto, n) == {"AUSDT": ("BUY", "1.399"), "BUSDT": ("SELL", "2.799")}


# ---------------------------------------------------------------------------------------------------------------------------------
# le chiusure intere sotto il valore minimo: «solo riduzione» (audit di F5 del 27 novembre, problema Alto 2); le riduzioni no (269)
# ---------------------------------------------------------------------------------------------------------------------------------
F = {"A": (0.01, 0.001, 0.001, 5.0)}


def test_minimo_ordini_del_giorno_le_chiusure_partono_riduzioni_aperture_e_aumenti_no():
    assert dm.ordini_del_giorno({}, {"A": 0.03}, {"A": 100.0}, 280.0, F) == [("A", "SELL", 0.03, 100.0, True)]   # 3 USDT: chiude
    assert dm.ordini_del_giorno({"A": 0.025}, {"A": 0.1}, {"A": 100.0}, 280.0, F) == []            # riduce per 2,8 USDT: no (269)
    assert dm.ordini_del_giorno({"A": 0.01}, {"A": 0.1}, {"A": 100.0}, 280.0, F) == [("A", "SELL", 0.072, 100.0, True)]   # riduce per 7,2 USDT: sì
    assert dm.sotto_il_minimo({"A": 0.025}, {"A": 0.1}, {"A": 100.0}, 280.0, F)["variazioni"] == 1   # la riduzione piccola resta «sotto»
    assert dm.ordini_del_giorno({"A": 0.01}, {}, {"A": 100.0}, 280.0, F) == []                     # apre per 2,8 USDT: no
    assert dm.ordini_del_giorno({"A": 0.03}, {"A": 0.06}, {"A": 100.0}, 280.0, F) == []            # aumenta per 2,4 USDT: no
    assert dm.ordini_del_giorno({}, {"A": 0.0004}, {"A": 100.0}, 280.0, F) == []                   # sotto la quantità minima: no
    assert dm.sotto_il_minimo({}, {"A": 0.03}, {"A": 100.0}, 280.0, F)["variazioni"] == 0          # la chiusura non è più «sotto»
    assert dm.sotto_il_minimo({"A": 0.01}, {}, {"A": 100.0}, 280.0, F)["variazioni"] == 1


def test_minimo_demo_chiude_la_posizione_sotto_il_minimo_anche_con_il_resto_a_mercato(tmp_path):
    finto = _Demo()
    finto.posizioni = {"AUSDT": 0.03, "BUSDT": 0.0}                       # 3 USDT di AUSDT, il resto di un'altra decisione
    d, fb = _demo_semplice(tmp_path, finto, pesi={"BUSDT": -0.5})
    d.tick(T0)
    o = _ordini_di(finto, "AUSDT")
    assert [(q["side"], q["type"], q["quantity"], q.get("reduceOnly")) for q in o] == [("SELL", "LIMIT", "0.03", "true")]
    assert fb.get_rtdb("/demo_binance/ribilanciamenti/2026-10-24")["sotto_il_minimo"]["variazioni"] == 0
    n = len(finto.chiamate)
    d.tick(T0 + 3601)                                                      # il finto non muove la posizione: resto a mercato
    m = [q for q in _ordini_di(finto, "AUSDT", n) if q["type"] == "MARKET"]
    assert [(q["side"], q["quantity"], q.get("reduceOnly")) for q in m] == [("SELL", "0.03", "true")]


def test_minimo_conto_vero_chiude_la_posizione_sotto_il_minimo_e_non_apre_sotto_il_minimo(tmp_path, monkeypatch):
    finto = T._Vero(simboli=("AUSDT", "BUSDT", "CUSDT"))
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = T._conto(tmp_path, monkeypatch, finto, capitale=None)
    _primo_ribilancio(d, tmp_path, finto)
    finto.posizioni["AUSDT"] = 0.03                                        # ne restano 3 USDT
    n = len(_post(finto))
    T._decisione(tmp_path, T.GIORNO + 2, {"BUSDT": -0.5, "CUSDT": 0.009})  # CUSDT: 2,5 USDT da aprire
    d.tick(G2)
    nuovi = [q for q in _post(finto)[n:] if q["type"] == "LIMIT"]
    assert [(q["symbol"], q["side"], q["quantity"], q.get("reduceOnly")) for q in nuovi if q["symbol"] == "AUSDT"] == [
        ("AUSDT", "SELL", "0.03", "true")]
    assert not [q for q in nuovi if q["symbol"] == "CUSDT"]                # l'apertura sotto il minimo si salta come prima
    # sotto il minimo: CUSDT (2,5 USDT da aprire) e il resto di BUSDT sotto un passo; non la chiusura di AUSDT, che parte
    assert fb.get_rtdb("/conto_vero/ribilanciamenti/2026-10-26")["sotto_il_minimo"]["variazioni"] == 2


# ---------------------------------------------------------------------------------------------------------------------------------
# 213: l'inversione su una moneta che si può solo ridurre (conto vero; il demo è in tests/test_portafoglio_audit.py)
# ---------------------------------------------------------------------------------------------------------------------------------
def test_213_conto_vero_moneta_non_in_trading_chiude_con_solo_riduzione_e_non_apre(tmp_path, monkeypatch):
    finto = _VeroStati()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = T._conto(tmp_path, monkeypatch, finto, capitale=None)
    _primo_ribilancio(d, tmp_path, finto)
    corto = -finto.posizioni["BUSDT"]
    assert corto == pytest.approx(2.799)
    finto.stati["BUSDT"] = "SETTLING"
    n = len(_post(finto))
    T._decisione(tmp_path, T.GIORNO + 2, {"AUSDT": 0.5, "BUSDT": 0.3})    # da corto a lungo
    d.tick(G2)
    b = [q for q in _post(finto)[n:] if q["symbol"] == "BUSDT"]
    assert [(q["side"], q["type"], q["quantity"], q.get("reduceOnly")) for q in b] == [("BUY", "LIMIT", "2.799", "true")]
    rif = fb.get_rtdb("/conto_vero/ribilanciamenti/2026-10-26")["rifiutati"]
    assert [r["simbolo"] for r in rif] == ["BUSDT"] and "sola riduzione" in rif[0]["errore"] and rif[0]["peso"] == 0.3
    assert "BUSDT" in fb.get_rtdb("/conto_vero/allarmi/ordini_rifiutati")["testo"]
    d.tick(G2 + 3700)                                                      # il limite non eseguito: il resto chiude, non apre
    m = [q for q in _post(finto)[n:] if q["symbol"] == "BUSDT" and q["type"] == "MARKET"]
    assert [(q["side"], q["quantity"], q.get("reduceOnly")) for q in m] == [("BUY", "2.799", "true")]
    assert finto.posizioni["BUSDT"] == pytest.approx(0.0)                  # chiuso, mai lungo


class _VeroSoloRiduzione(T._Vero):
    """Il conto vero finto in cui una moneta si può solo ridurre senza che l'exchangeInfo lo dica: ogni ordine su ``bloccata`` senza
    «solo riduzione» risponde -4140."""
    bloccata = None

    def __call__(self, metodo, url, headers=None, timeout=None):
        u = urlparse(url)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        if (metodo == "POST" and u.path == "/fapi/v1/order" and q.get("symbol") == self.bloccata
                and q.get("reduceOnly") != "true"):
            self.chiamate.append((metodo, u.path, q))
            return _errore(-4140, "Invalid symbol status for opening position.")
        return super().__call__(metodo, url, headers, timeout)


def test_213_conto_vero_inversione_rifiutata_con_4140_subito_la_chiusura_solo_riduzione(tmp_path, monkeypatch):
    finto = _VeroSoloRiduzione()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = T._conto(tmp_path, monkeypatch, finto, capitale=None)
    _primo_ribilancio(d, tmp_path, finto)
    finto.bloccata = "BUSDT"
    n = len(_post(finto))
    T._decisione(tmp_path, T.GIORNO + 2, {"AUSDT": 0.5, "BUSDT": 0.3})
    d.tick(G2)
    b = [q for q in _post(finto)[n:] if q["symbol"] == "BUSDT"]
    assert [(q["side"], q.get("reduceOnly")) for q in b] == [("BUY", None), ("BUY", "true")]   # l'inversione, poi la chiusura
    assert b[1]["quantity"] == "2.799" and b[1]["newClientOrderId"].startswith("g1c-")
    rif = fb.get_rtdb("/conto_vero/ribilanciamenti/2026-10-26")["rifiutati"]
    assert rif[0]["simbolo"] == "BUSDT" and rif[0]["chiusa_con_solo_riduzione"] == pytest.approx(2.799)
    assert [o for o in d.carica()["ordini"]["lista"] if o["simbolo"] == "BUSDT"][0]["solo_riduzione"] is True


# ---------------------------------------------------------------------------------------------------------------------------------
# 211: `telefono` nell'allarme solo dopo un invio riuscito
# ---------------------------------------------------------------------------------------------------------------------------------
def _vecchia_poi_nuova_poi_vecchia(d, tmp_path):
    """La decisione di G1 vecchia (allarme acceso), aggiornata (spento) e di nuovo vecchia (riacceso), tutto entro un'ora."""
    t = 20750 * 86400.0 + 27 * 3600
    d.tick(t)
    (tmp_path / "g1.json").write_text(json.dumps({"ultimo_lunedi": 20751, "pesi": {"AUSDT": 0.5, "BUSDT": -0.5}}))
    d.tick(t + 600)
    (tmp_path / "g1.json").write_text(json.dumps({"ultimo_lunedi": 20750, "pesi": {"AUSDT": 0.5, "BUSDT": -0.5}}))
    d.tick(t + 1200)
    return t


@pytest.mark.parametrize("riuscito", [True, False])
def test_211_telefono_solo_a_invio_riuscito_e_un_invio_fallito_non_conta_per_l_ora(tmp_path, riuscito):
    d, fb = _demo_semplice(tmp_path, _Demo())
    mandati = []

    def avvisa(testo):
        mandati.append(testo)
        return riuscito
    d.avvisa = avvisa
    t = 20750 * 86400.0 + 27 * 3600
    d.tick(t)
    al = fb.get_rtdb("/demo_binance/allarmi/decisione_g1")
    assert (al.get("telefono") == t) if riuscito else ("telefono" not in al)
    mandati.clear()
    altro = tmp_path / "altro"
    altro.mkdir()
    d2, fb2 = _demo_semplice(altro, _Demo())
    d2.avvisa = avvisa
    _vecchia_poi_nuova_poi_vecchia(d2, altro)
    assert len(_di(mandati, "decisione g1")) == (1 if riuscito else 2)    # fallito: riacceso entro l'ora si rimanda
    if not riuscito:
        assert "telefono" not in fb2.get_rtdb("/demo_binance/allarmi/decisione_g1")


@pytest.mark.parametrize("riuscito", [True, False])
def test_211_il_fermo_ha_telefono_solo_se_l_invio_e_riuscito(tmp_path, riuscito):
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    d.avvisa = lambda testo: riuscito
    d.tick(T0)
    (tmp_path / "chiudi").write_text("chiudi 1")
    d.file_chiudi = tmp_path / "chiudi"
    d.tick(T0 + 3700)
    fermo = fb.get_rtdb("/demo_binance/fermo")
    assert fermo["motivo"] == "comando chiudi tutto"
    assert (fermo.get("telefono") == T0 + 3700) if riuscito else ("telefono" not in fermo)
    assert (d.carica()["fermo"].get("telefono") == T0 + 3700) if riuscito else ("telefono" not in d.carica()["fermo"])


@pytest.mark.parametrize("riuscito", [True, False])
def test_211_con_il_filo_vero_il_segno_arriva_al_giro_dopo(tmp_path, monkeypatch, riuscito):
    """Con `avviso_telegram` (il filo vero) e il notificatore finto: l'esito torna dal filo e il giro dopo segna `telefono`, solo se
    Telegram ha accettato (`send` vero)."""
    from bot.execution import notifier
    monkeypatch.setattr(notifier.TelegramNotifier, "send", lambda self, testo: riuscito)
    d, fb = _demo_semplice(tmp_path, _Demo())
    assert d.avvisa is dm.avviso_telegram
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    t = 20750 * 86400.0 + 27 * 3600
    d.tick(t)
    for filo in threading.enumerate():
        if filo.name == "avviso_telegram":
            filo.join(timeout=5)
    d.tick(t + 60)
    al = fb.get_rtdb("/demo_binance/allarmi/decisione_g1")
    assert (al.get("telefono") == t) if riuscito else ("telefono" not in al)
    assert ("decisione_g1" in d._telefonati) is riuscito


# ---------------------------------------------------------------------------------------------------------------------------------
# 219: un 429 che dura oltre 30 minuti va al telefono una volta (bot e monitor)
# ---------------------------------------------------------------------------------------------------------------------------------
def test_219_bot_un_429_che_dura_oltre_mezz_ora_va_al_telefono_una_volta(tmp_path, monkeypatch):
    assert dm.LIMITE_429_AL_TELEFONO_S == 1800 == monitor.LIMITE_429_S
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    _attese(monkeypatch)
    avvisi = _avvisi(d)
    _sempre(d, finto, "GET", "/fapi/v2/account", _Risposta({"code": -1003, "msg": "Too many requests"}, 429))
    t, primo = T0, None
    while t < T0 + 1800:                                                   # ogni 2 minuti e un secondo (l'attesa di un 429)
        d.tick(t)
        t += 121
    assert avvisi == []                                                    # meno di 30 minuti: solo su Firebase
    al = fb.get_rtdb("/demo_binance/allarmi/limiti_binance")
    assert al["dal"] == T0 and al["codice"] == 429 and "telefono" not in al
    for _ in range(10):
        d.tick(t)
        primo = primo or (t if avvisi else None)
        t += 121
    assert len(_di(avvisi, "limiti 429")) == 1 and "minuti (dalle" in avvisi[0]
    al = fb.get_rtdb("/demo_binance/allarmi/limiti_binance")
    assert al["telefono"] == primo and al["dal"] == T0
    d._cliente.http = finto                                                # Binance risponde: la serie finisce
    d.tick(t)
    assert fb.get_rtdb("/demo_binance/allarmi/limiti_binance") is None and d._limiti_dal is None


def test_219_monitor_manda_il_429_che_dura_oltre_mezz_ora():
    fb, tg = T._Fb(), _Telegram()
    ora = 1_795_737_600.0
    fb.set_rtdb("/demo_binance/allarmi/limiti_binance", {"ora": ora, "testo": "Binance limita", "codice": 429, "dal": ora - 600})
    assert monitor.avvisa_allarmi(fb, tg, now=ora) == 0                    # da 10 minuti: no
    fb.set_rtdb("/demo_binance/allarmi/limiti_binance", {"ora": ora + 1300, "testo": "Binance limita", "codice": 429,
                                                         "dal": ora - 600})
    assert monitor.avvisa_allarmi(fb, tg, now=ora + 1300) == 1             # da 31 minuti: sì
    assert monitor.avvisa_allarmi(fb, tg, now=ora + 2200) == 0             # una volta finché resta acceso
    # senza `dal` (il bot di prima): da quando il monitor l'ha visto la prima volta
    fb2, tg2 = T._Fb(), _Telegram()
    fb2.set_rtdb("/conto_vero/allarmi/limiti_binance", {"ora": ora, "testo": "Binance limita", "codice": 429})
    assert monitor.avvisa_allarmi(fb2, tg2, now=ora) == 0
    assert fb2.get_rtdb(monitor.NODO_429_VISTI) == {"conto_vero-allarmi-limiti_binance": ora}
    assert monitor.avvisa_allarmi(fb2, tg2, now=ora + 900) == 0
    assert monitor.avvisa_allarmi(fb2, tg2, now=ora + 1800) == 1
    fb2.set_rtdb("/conto_vero/allarmi/limiti_binance", None)               # spento: esce dalla memoria
    monitor.avvisa_allarmi(fb2, tg2, now=ora + 2000)
    assert not fb2.get_rtdb(monitor.NODO_429_VISTI)


# ---------------------------------------------------------------------------------------------------------------------------------
# 220: il limite di uno all'ora per tipo di avviso, e mai per il fermo (bot e monitor)
# ---------------------------------------------------------------------------------------------------------------------------------
def test_220_bot_il_fermo_va_sempre_al_telefono_gli_altri_una_volta_all_ora(tmp_path):
    d, fb = _demo_semplice(tmp_path, _Demo())
    avvisi = _avvisi(d)
    assert dm.SEMPRE_AL_TELEFONO == ("fermo", "stop")
    assert d._telefono("stop", "primo stop", T0) and d._telefono("stop", "secondo stop", T0 + 60)
    assert d._telefono("fermo", "pulsante", T0 + 120) and d._telefono("fermo", "pulsante di nuovo", T0 + 180)
    assert d._telefono("pesi", "a", T0) and not d._telefono("pesi", "b", T0 + 60)
    assert len(avvisi) == 5


def test_220_bot_due_fermi_nella_stessa_ora_tutti_e_due_al_telefono(tmp_path):
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    avvisi = _avvisi(d)
    d.tick(T0)
    d.file_chiudi, d.file_riparti = tmp_path / "chiudi", tmp_path / "riparti"
    d.file_chiudi.write_text("chiudi 1")
    d.tick(T0 + 60)                                                        # primo fermo
    d.tick(T0 + 130)                                                       # conto vuoto
    d.file_riparti.write_text("riparti 1")
    d.tick(T0 + 200)
    assert not d.carica().get("fermo")
    d.file_chiudi.write_text("chiudi 2")
    d.tick(T0 + 300)                                                       # secondo fermo, dentro l'ora
    assert len(_di(avvisi, "fermo")) == 2


def test_220_monitor_il_limite_per_tipo_il_418_mandato_non_toglie_il_429_che_dura():
    fb, tg = T._Fb(), _Telegram()
    ora = 1_795_737_600.0
    fb.set_rtdb("/demo_binance/allarmi/limiti_binance", {"ora": ora, "testo": "indirizzo bloccato (418)", "codice": 418,
                                                         "telefono": ora})
    assert monitor.avvisa_allarmi(fb, tg, now=ora + 60) == 0               # mandato dal bot
    assert fb.get_rtdb(monitor.NODO_TELEFONO_DEL_BOT) == {"demo_binance-allarmi-limiti_binance-418": ora}
    fb.set_rtdb("/demo_binance/allarmi/limiti_binance", None)
    monitor.avvisa_allarmi(fb, tg, now=ora + 120)
    fb.set_rtdb("/demo_binance/allarmi/limiti_binance", {"ora": ora + 2000, "testo": "Binance limita da 31 minuti", "codice": 429,
                                                         "dal": ora + 140})
    assert monitor.avvisa_allarmi(fb, tg, now=ora + 2000) == 1             # un altro tipo: il limite del 418 non lo tocca
    # lo stesso tipo entro l'ora invece resta fuori, come nel bot
    fb.set_rtdb("/demo_binance/allarmi/limiti_binance", {"ora": ora + 2100, "testo": "indirizzo bloccato (418)", "codice": 418})
    fb.set_rtdb(monitor.NODO_AVVISATI, None)
    assert monitor.avvisa_allarmi(fb, tg, now=ora + 2100) == 0


class _Telegram:
    def __init__(self, esito: bool = True) -> None:
        self.messaggi, self.esito = [], esito

    def send(self, testo: str) -> bool:
        self.messaggi.append(testo)
        return self.esito

    def bot_offline(self) -> None:
        self.messaggi.append("BOT OFFLINE")


# --- Le tre prove del revisore del 28 novembre 2026 (problema 270, reviews/reports/2026-11-28-conto-vero-G1.md): la fase nuova
# del prelievo non scavalca un motivo duro, il saldo tornato alla decisione non apre una fase nuova, il pavimento con il prelievo.
# Cadono con le mutazioni M1, M3 e M4 del revisore.


G3 = (T.GIORNO + 3) * 86400.0 + 400


def _prelievo(tmp_path, monkeypatch, motivo):
    _attese(monkeypatch)
    finto = T._Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = T._conto(tmp_path, monkeypatch, finto, capitale=None, codice=lambda: motivo[0])
    T._fino_alla_decisione_dopo(d, tmp_path)
    d.tick(T.DOPO + 3700)
    finto.equity = "180"
    finto.entrate.append(T._riga("TRANSFER", -100.0, dopo_s=3750))
    for k in range(3):
        d.tick(T.DOPO + 3800 + 60 * k)
    assert d.carica()["fase_nuova"]["perche"] == "prelievo"
    return d, fb, finto


def test_prelievo_e_versione_non_approvata_alla_decisione_niente_fase_nuova(tmp_path, monkeypatch):   # M1, M4
    motivo = [None]
    d, fb, finto = _prelievo(tmp_path, monkeypatch, motivo)
    motivo[0] = "nessuna versione approvata dal proprietario"
    d.tick(T.DOPO + 4200)
    n = len(_post(finto))
    T._decisione(tmp_path, T.GIORNO + 2)
    d.tick(G2)
    d.tick(G2 + 60)
    assert _post(finto)[n:] == []
    assert d.carica().get("blocco_duro") is True
    motivo[0] = None
    d.tick(G2 + 4000)
    d.tick(G2 + 4100)
    assert [q for q in _post(finto)[n:] if q.get("reduceOnly") != "true"] == []
    T._decisione(tmp_path, T.GIORNO + 3)
    d.tick(G3)
    assert [q for q in _post(finto)[n:] if q.get("reduceOnly") != "true"]
    assert fb.get_rtdb("/conto_vero/conto_ridotto")["capitale"] == 180.0


def test_prelievo_poi_fermo_sotto_il_pavimento_riparti_rifiutato(tmp_path, monkeypatch):   # M3
    d, fb, finto = _prelievo(tmp_path, monkeypatch, [None])
    fb.proprietario(cv.COMANDO_CHIUDI, True)
    d.tick(T.DOPO + 4200)
    d.tick(T.DOPO + 4300)
    assert d.carica().get("fermo")
    finto.entrate.append(T._riga("REALIZED_PNL", -110.0, dopo_s=4250))
    finto.equity = "70"
    for k in range(3):
        d.tick(T.DOPO + 4400 + 60 * k)
    st = d.carica()
    assert st.get("capitale_in_attesa") == 300.0 and st["fase_nuova"]["perche"] == "prelievo"
    T._riparti_in_due_passi(fb)
    d.tick(T.DOPO + 4700)
    d.tick(T.DOPO + 4800)
    assert d.carica().get("fermo")
    assert "non sopra il 65%" in fb.get_rtdb("/conto_vero/allarmi/riparti")["testo"]


def test_b_saldo_tornato_alla_decisione_niente_fase_nuova(tmp_path, monkeypatch):
    motivo = [None]
    d, fb, finto = _prelievo(tmp_path, monkeypatch, motivo)
    finto.equity = "280"                               # il saldo torna (versamento) proprio alla decisione
    n = len(_post(finto))
    T._decisione(tmp_path, T.GIORNO + 2)
    d.tick(G2)
    nuovi = _post(finto)[n:]
    st = d.carica()
    d.tick(G2 + 60)
    st = d.carica()
    assert "capitale_in_attesa" not in st and "fase_nuova" not in st
    assert fb.get_rtdb("/conto_vero/conto_ridotto")["capitale"] == 280.0


# 274 (riesame del 28 novembre, reviews/reports/2026-11-28-conto-vero-G1-bis.md): il resto a mercato segue la regola delle sole
# chiusure intere; cade se `demo_binance.py` torna a esentare anche le riduzioni.
def test_minimo_il_resto_a_mercato_di_una_riduzione_sotto_il_minimo_si_salta(tmp_path):
    """269: la riduzione da circa 2.000 a circa 1.000 USDT corti parte a limite; se dopo l'ora ne mancano 2,6 USDT (sotto i 5), il
    resto a mercato si salta come all'apertura: parte a mercato solo la chiusura intera."""
    finto = _Demo()
    finto.posizioni = {"AUSDT": 0.0, "BUSDT": -40.0}
    d, fb = _demo_semplice(tmp_path, finto, pesi={"BUSDT": -0.1})          # obiettivo −19,997: si compra 20,002 «solo riduzione»
    d.tick(T0)
    o = _ordini_di(finto, "BUSDT")
    assert [(q["side"], q["type"], q["quantity"], q.get("reduceOnly")) for q in o] == [("BUY", "LIMIT", "20.002", "true")]
    finto.posizioni["BUSDT"] = -20.05                                      # eseguito in parte: ne mancano 0,052 (2,6 USDT)
    n = len(finto.chiamate)
    d.tick(T0 + 3601)
    assert not [q for q in _ordini_di(finto, "BUSDT", n) if q["type"] == "MARKET"]
