"""G1 sul conto vero di Binance (bot/portafoglio/conto_vero.py), fase 2 del piano (docs/conto_vero.md), con il Binance finto dei test
del demo: solo fapi.binance.com, le quattro condizioni per accendersi, la partenza da vuoto alla mezzanotte, il tag del codice
approvato, il tetto del capitale, i filtri veri, i limiti fissati. Nessuna richiesta di rete vera: il finto risponde a tutto."""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
import requests

from bot.core.firebase_client import _InMemoryStore
from bot.portafoglio import conto_vero as cv
from bot.portafoglio import demo_binance as dm
from tests.test_demo_binance import _Demo, _Risposta, _post

RADICE = Path(__file__).resolve().parents[1]
GIORNO = 20750                                  # 2026-10-24
MEZZOGIORNO = GIORNO * 86400.0 + 12 * 3600
DOPO = (GIORNO + 1) * 86400.0 + 400             # la decisione di G1 del giorno dopo (00:06 UTC)


class _Vero(_Demo):
    """Il Binance finto del demo, all'indirizzo del conto vero (il finto controlla l'indirizzo di ogni richiesta). In più: gli utili non
    realizzati (il saldo è il valore del conto meno questi) e i redditi del conto senza il tipo (tutte le righe di /fapi/v1/income)."""
    HOST = "fapi.binance.com"

    def __init__(self, simboli=("AUSDT", "BUSDT")):
        super().__init__(simboli)
        self.non_realizzato = 0.0
        self.redditi_rotti = False                     # /fapi/v1/income senza il tipo risponde con un errore (prova q7)

    def __call__(self, metodo, url, headers=None, timeout=None):
        u = urlparse(url)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        if u.path == "/fapi/v1/income" and "incomeType" not in q:
            assert u.hostname == self.HOST
            self.chiamate.append((metodo, u.path, q))
            if self.redditi_rotti:
                return _Risposta({"code": -1127, "msg": "More than 7 days between startTime and endTime."}, 400)
            righe = [{"incomeType": t, "time": ms, "income": str(v), "asset": val, "tranId": i}
                     for i, (t, ms, v, val) in enumerate(self.entrate) if int(q["startTime"]) <= ms <= int(q["endTime"])]
            righe.sort(key=lambda x: x["time"])
            return _Risposta(righe[: int(q["limit"])])
        r = super().__call__(metodo, url, headers, timeout)
        if u.path == "/fapi/v2/account":
            r.dati["totalWalletBalance"] = str(float(self.equity) - self.non_realizzato)
        return r


def _scritture(finto):
    """Tutto quello che non è una lettura: ordini, annulli, leva, margine, modo delle posizioni."""
    return [(m, p, q) for m, p, q in finto.chiamate if m != "GET"]


def _aperture(finto):
    """Gli ordini che possono aprire o aumentare una posizione (non «solo riduzione»)."""
    return [q for q in _post(finto) if q.get("reduceOnly") != "true"]


def _decisione(tmp_path, giorno, pesi=None):
    (tmp_path / "g1.json").write_text(json.dumps({"ultimo_lunedi": giorno, "pesi": pesi or {"AUSDT": 0.5, "BUSDT": -0.5}}))


def _conto(tmp_path, monkeypatch, finto=None, *, acceso=True, dry_run="false", capitale="280", codice=None, pesi=None):
    monkeypatch.setenv("DRY_RUN", dry_run)
    finto = finto or _Vero()
    fb = _InMemoryStore()
    if acceso:
        (tmp_path / "conto_vero_acceso").write_text("si")
    if capitale is not None:
        (tmp_path / "conto_vero_capitale").write_text(capitale)
    _decisione(tmp_path, GIORNO, pesi)
    d = cv.ContoVeroG1(fb, cliente=cv.ClienteVero("chiave", "segreto", http=finto), file_stato=tmp_path / "st.json",
                       file_g1=tmp_path / "g1.json", interruttore=tmp_path / "conto_vero_acceso", file_chiudi=tmp_path / "chiudi",
                       file_riparti=tmp_path / "riparti", file_capitale=tmp_path / "conto_vero_capitale",
                       verifica_codice=codice or (lambda: None))
    _orologio_del_giro(d)
    return d, fb, finto


def _orologio_del_giro(d, dopo_s=1.0):
    """L'ora vera nei test: quella del giro più ``dopo_s`` secondi (in produzione `time.time`, e il giro parte con `time.time()`)."""
    ora, giro = [0.0], d.tick

    def tick(now):
        ora[0] = now
        giro(now)
    d.tick = tick
    d.orologio = lambda: ora[0] + dopo_s


def _fino_alla_decisione_dopo(d, tmp_path, pesi=None):
    """Acceso a mezzogiorno (nel file la decisione di G1 di oggi), un'ora dopo, poi la decisione di G1 del giorno dopo."""
    d.tick(MEZZOGIORNO)
    d.tick(MEZZOGIORNO + 3700)
    _decisione(tmp_path, GIORNO + 1, pesi)
    d.tick(DOPO)


def test_i_limiti_del_conto_vero_sono_fissati():
    """Il test di guardia dei limiti (fase 2, punto 6): cambiarne uno fa fallire questo test, e il cambio va spiegato al
    proprietario e fatto approvare (con un tag nuovo). La classe usa questi, non quelli del demo."""
    assert cv.LEVA == 5
    assert cv.CAPITALE_MASSIMO == 300.0
    assert cv.VALORE_MASSIMO_PER_ORDINI == 600.0
    assert cv.STOP_CONTO == 0.35
    assert cv.PAVIMENTO_RIPARTI == 0.65
    assert cv.SOMMA_PESI_MASSIMA == 2.0
    assert cv.PESO_MASSIMO_MONETA == 0.60
    assert cv.ETA_MASSIMA_DECISIONE_S == 26 * 3600
    assert (cv.TOLLERANZA_SALDO, cv.TOLLERANZA_SALDO_MINIMA, cv.LETTURE_SALDO_SOTTO) == (0.005, 1.0, 3)          # problema 64
    assert (cv.RITARDO_REDDITI_S, cv.SOVRAPPOSIZIONE_REDDITI_S, cv.ERRORI_REDDITI_PRIMA_DELL_ALLARME) == (60, 900, 3)
    assert cv.TAG_APPROVATO == "conto-vero-approvato"
    assert cv.PERCORSI_DEGLI_ORDINI == ("bot/portafoglio", "bot/execution", "bot/risk", "bot/config.py", "bot/main.py")
    for nome in ("LEVA", "CAPITALE_MASSIMO", "VALORE_MASSIMO_PER_ORDINI", "STOP_CONTO", "PAVIMENTO_RIPARTI", "SOMMA_PESI_MASSIMA",
                 "PESO_MASSIMO_MONETA", "ETA_MASSIMA_DECISIONE_S", "COMANDO_CHIUDI", "TOLLERANZA_SALDO",
                 "TOLLERANZA_SALDO_MINIMA", "LETTURE_SALDO_SOTTO"):
        assert getattr(cv.ContoVeroG1, nome) == getattr(cv, nome), nome
    # stato, comandi e ramo di Firebase separati da quelli del demo
    assert cv.ContoVeroG1.NOME == "conto_vero" and dm.DemoG1.NOME == "demo_binance"
    assert cv.COMANDO_CHIUDI not in {dm.COMANDO_CHIUDI, dm.COMANDO_RIPARTI}
    assert cv.COMANDO_RIPARTI is None and cv.ContoVeroG1.COMANDO_RIPARTI is None    # problema 60: «riparti» solo dal file
    assert {cv.FILE_STATO, cv.FILE_CHIUDI, cv.FILE_RIPARTI, cv.FILE_CAPITALE, cv.INTERRUTTORE}.isdisjoint(
        {dm.FILE_STATO, dm.FILE_CHIUDI, dm.FILE_RIPARTI, dm.FILE_CAPITALE, dm.INTERRUTTORE})


def test_solo_l_indirizzo_vero(monkeypatch):
    assert cv._url("/fapi/v1/order") == "https://fapi.binance.com/fapi/v1/order"
    for altro in ("https://demo-fapi.binance.com", "http://fapi.binance.com", "https://fapi.binance.com.esempio.org",
                  "https://api.binance.com"):
        monkeypatch.setattr(cv, "VERO", altro)
        with pytest.raises(ValueError):
            cv._url("/fapi/v1/order")
    monkeypatch.setattr(cv, "VERO", "https://fapi.binance.com")
    with pytest.raises(ValueError):
        cv._url("@esempio.org/fapi/v1/order")
    finto = _Vero()                                    # il finto rifiuta ogni indirizzo che non sia fapi.binance.com
    cv.ClienteVero("chiave", "segreto", http=finto).chiedi("GET", "/fapi/v1/time")
    assert finto.chiamate == [("GET", "/fapi/v1/time", {})]
    assert dm.ClienteDemo._url("/fapi/v1/time").startswith("https://demo-fapi.binance.com/")   # il demo resta sul demo
    with pytest.raises(TypeError):                     # il conto vero non accetta il cliente del demo
        cv.ContoVeroG1(_InMemoryStore(), cliente=dm.ClienteDemo("chiave", "segreto", http=_Demo()), verifica_codice=lambda: None)


@pytest.mark.parametrize("manca", ["nessuna", "interruttore", "dry_run", "dry_run_scritto_male", "codice", "capitale"])
def test_senza_una_delle_quattro_condizioni_nessun_ordine(tmp_path, monkeypatch, manca):
    """(a) l'interruttore, (b) DRY_RUN falso, (c) il codice del tag, (d) il capitale: se ne manca una, nessuna richiesta di ordine
    nemmeno alla decisione di G1 dopo l'accensione; con tutte e quattro gli ordini partono (il controllo)."""
    d, fb, finto = _conto(tmp_path, monkeypatch, acceso=manca != "interruttore",
                          dry_run={"dry_run": "true", "dry_run_scritto_male": "treu"}.get(manca, "false"),
                          capitale=None if manca == "capitale" else "280",
                          codice=(lambda: "manca il tag conto-vero-approvato") if manca == "codice" else None)
    _fino_alla_decisione_dopo(d, tmp_path)
    assert fb.get_rtdb("/demo_binance") is None        # niente sul ramo del demo
    if manca == "nessuna":
        assert {q["symbol"] for q in _aperture(finto)} == {"AUSDT", "BUSDT"}
        assert fb.get_rtdb("/conto_vero/allarmi/ordini_vietati") is None
        return
    assert _scritture(finto) == []
    if manca in ("interruttore", "dry_run", "dry_run_scritto_male"):
        assert finto.chiamate == []                    # spento del tutto: nemmeno una lettura
        stato = fb.get_rtdb("/conto_vero/stato")
        assert stato["stato"].startswith("spento:") and stato["acceso"] is False
        assert ("interruttore" if manca == "interruttore" else "DRY_RUN") in stato["stato"]
    else:
        testo = fb.get_rtdb("/conto_vero/allarmi/ordini_vietati")["testo"]
        assert "niente ordini nuovi" in testo and ("tag" if manca == "codice" else "capitale") in testo


def test_le_chiavi_del_conto_vero_non_si_leggono_da_spento(tmp_path, monkeypatch):
    monkeypatch.setenv("BINANCE_API_KEY", "chiave-di-prova")
    monkeypatch.setenv("BINANCE_API_SECRET", "segreto-di-prova")
    monkeypatch.setenv("DRY_RUN", "true")
    (tmp_path / "acceso").write_text("si")
    d = cv.ContoVeroG1(_InMemoryStore(), file_stato=tmp_path / "st.json", file_g1=tmp_path / "g1.json",
                       interruttore=tmp_path / "acceso", file_capitale=tmp_path / "capitale", verifica_codice=lambda: None)
    d.tick(MEZZOGIORNO)
    assert d._cliente is None
    monkeypatch.setenv("DRY_RUN", "false")             # senza girare (niente rete): le chiavi sono quelle di bot/config.py
    c = d.cliente()
    assert isinstance(c, cv.ClienteVero) and c.chiave == "chiave-di-prova"
    config = (RADICE / "bot" / "config.py").read_text(encoding="utf-8")
    assert f'os.getenv("{cv.CHIAVE_ENV}"' in config and f'os.getenv("{cv.SEGRETO_ENV}"' in config


def test_parte_vuoto_e_compra_solo_alla_decisione_di_g1_dopo(tmp_path, monkeypatch):
    """Acceso a metà giornata con la decisione di G1 di oggi nel file: niente fino alla decisione dopo (la mezzanotte); poi gli
    ordini limite per un conto di 280 USDT, anche se il portafoglio dei future ne ha 10.000."""
    d, fb, finto = _conto(tmp_path, monkeypatch)
    d.tick(MEZZOGIORNO)
    d.tick(MEZZOGIORNO + 3700)
    assert _scritture(finto) == []
    assert fb.get_rtdb("/conto_vero/acceso_dal")["compra_alla_decisione_di_g1_dopo_il"] == "2026-10-24"
    _decisione(tmp_path, GIORNO + 1)
    d.tick(DOPO)
    ordini = {q["symbol"]: (q["side"], q["type"], q["quantity"]) for q in _post(finto)}
    assert ordini == {"AUSDT": ("BUY", "LIMIT", "1.399"), "BUSDT": ("SELL", "LIMIT", "2.799")}    # 0,5 × 280 USDT ai prezzi mark
    assert [q["leverage"] for m, p, q in finto.chiamate if p == "/fapi/v1/leverage"] == ["5", "5"]
    assert [q["marginType"] for q in _post(finto, "/fapi/v1/marginType")] == ["CROSSED", "CROSSED"]
    assert fb.get_rtdb("/conto_vero/conto_ridotto")["capitale"] == 280.0
    assert fb.get_rtdb("/conto_vero/ribilanciamenti/2026-10-25")["ordini"] == 2
    stato = fb.get_rtdb("/conto_vero/stato")             # problema 63: niente testi del demo
    assert stato["valore_vero_del_conto"] == 10000.0 and "valore_vero_del_conto_demo" not in stato


def test_la_leva_e_quella_della_classe_del_conto_vero(tmp_path, monkeypatch):
    """Il codice ereditato dal demo usa la leva della classe: cambiata quella, cambia quella mandata a Binance."""
    monkeypatch.setattr(cv.ContoVeroG1, "LEVA", 3)
    d, _, finto = _conto(tmp_path, monkeypatch)
    _fino_alla_decisione_dopo(d, tmp_path)
    assert [q["leverage"] for m, p, q in finto.chiamate if p == "/fapi/v1/leverage"] == ["3", "3"]


def test_pesi_oltre_il_200_per_cento_niente_ordini(tmp_path, monkeypatch):
    """Il conto vero non ha eventi: la somma dei pesi si ferma al 200% (il demo arriva al 250%)."""
    pesi = {"AUSDT": 0.6, "BUSDT": 0.55, "CUSDT": -0.6, "BTCUSDT": -0.55}
    assert dm.pesi_fuori_dai_limiti(pesi) is None      # il demo li eseguirebbe
    d, fb, finto = _conto(tmp_path, monkeypatch, _Vero(simboli=("AUSDT", "BUSDT", "CUSDT", "BTCUSDT")), pesi=pesi)
    _fino_alla_decisione_dopo(d, tmp_path, pesi)
    assert _aperture(finto) == []
    assert "oltre il 200%" in fb.get_rtdb("/conto_vero/allarmi/pesi")["testo"]


@pytest.mark.parametrize("protezione", ["pulsante", "stop"])
def test_codice_diverso_dal_tag_niente_ordini_nuovi_ma_stop_e_pulsante(tmp_path, monkeypatch, protezione):
    codice = [None]
    finto = _Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto, codice=lambda: codice[0])
    _fino_alla_decisione_dopo(d, tmp_path)             # AUSDT eseguito a limite, BUSDT ancora sul libro
    assert finto.posizioni["AUSDT"] > 0 and len(_aperture(finto)) == 2
    codice[0] = "file del codice diversi dal tag conto-vero-approvato: bot/risk/hard_limits.py"
    d.tick(DOPO + 120)                                 # il controllo del codice del minuto: blocco
    assert "diversi dal tag" in fb.get_rtdb("/conto_vero/allarmi/ordini_vietati")["testo"]
    _decisione(tmp_path, GIORNO + 2)
    t = (GIORNO + 2) * 86400.0 + 400
    d.tick(t)                                          # la decisione nuova di G1 non si esegue
    assert len(_aperture(finto)) == 2
    if protezione == "pulsante":
        fb.set_rtdb(dm.COMANDO_CHIUDI, True)           # il pulsante del demo non tocca il conto vero
        d.tick(t + 60)
        assert not [q for q in _post(finto) if q["type"] == "MARKET"]
        fb.set_rtdb(cv.COMANDO_CHIUDI, True)
    else:
        finto.equity, finto.non_realizzato = "150", -130.0     # una perdita non realizzata: sotto il 65% dei 280 di partenza
    d.tick(t + 120)
    chiusure = [q for q in _post(finto) if q["type"] == "MARKET"]
    assert [(q["symbol"], q["side"], q.get("reduceOnly")) for q in chiusure] == [("AUSDT", "SELL", "true")]
    motivo = d.carica()["fermo"]["motivo"]
    assert motivo == "pulsante della dashboard" if protezione == "pulsante" else motivo.startswith("stop sul conto")
    assert len(_aperture(finto)) == 2                  # nessun ordine nuovo che apra


def test_blocco_a_meta_ribilancio_gli_ordini_limite_vivono_la_loro_ora(tmp_path, monkeypatch):
    """Problema 56 (prova p2): un blocco arrivato a metà ribilancio non annulla gli ordini limite già messi: vivono la loro ora come
    in G1; dopo l'ora quelli non eseguiti si annullano e il resto a mercato non parte."""
    codice = [None]
    finto = _Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto, codice=lambda: codice[0])
    _fino_alla_decisione_dopo(d, tmp_path)             # AUSDT eseguito a limite, BUSDT sul libro
    codice[0] = "file del codice diversi dal tag conto-vero-approvato: bot/portafoglio/f5.py"
    n = len(finto.chiamate)
    d.tick(DOPO + 120)
    d.tick(DOPO + 1800)
    assert [c for c in finto.chiamate[n:] if c[0] != "GET"] == []
    assert any(o["symbol"] == "BUSDT" and not o.get("chiuso") for o in finto.ordini.values())
    d.tick(DOPO + 3700)                                # dopo l'ora: annullati, niente resto a mercato
    assert [(m, p, q.get("symbol")) for m, p, q in finto.chiamate[n:] if m != "GET"] == [
        ("DELETE", "/fapi/v1/allOpenOrders", "AUSDT"), ("DELETE", "/fapi/v1/allOpenOrders", "BUSDT")]
    assert "ordini" not in d.carica()


def test_dopo_un_blocco_si_riparte_alla_decisione_di_g1_dopo(tmp_path, monkeypatch):
    """Ogni riaccensione aspetta la mezzanotte: tolto il blocco a metà giornata, niente fino alla decisione dopo."""
    codice = [None]
    d, fb, finto = _conto(tmp_path, monkeypatch, codice=lambda: codice[0])
    _fino_alla_decisione_dopo(d, tmp_path)
    assert len(_aperture(finto)) == 2
    codice[0] = "manca il tag conto-vero-approvato"
    d.tick(DOPO + 7200)
    _decisione(tmp_path, GIORNO + 2)
    d.tick((GIORNO + 2) * 86400.0 + 400)
    codice[0] = None
    d.tick((GIORNO + 2) * 86400.0 + 12 * 3600)         # sbloccato a metà giornata, con la decisione di oggi nel file
    d.tick((GIORNO + 2) * 86400.0 + 13 * 3600)
    assert len(_aperture(finto)) == 2 and fb.get_rtdb("/conto_vero/allarmi/ordini_vietati") is None
    _decisione(tmp_path, GIORNO + 3)
    d.tick((GIORNO + 3) * 86400.0 + 400)
    assert {q["symbol"] for q in _aperture(finto)[2:]} == {"AUSDT", "BUSDT"}


def test_codice_non_approvato_all_avvio_serve_un_riavvio(tmp_path, monkeypatch):
    """Il processo ha in memoria il codice dell'avvio: se allora non era quello del tag, niente ordini anche quando i file tornano
    uguali al tag."""
    risposte = iter(["file del percorso degli ordini diversi dal tag conto-vero-approvato: bot/main.py"])
    d, fb, finto = _conto(tmp_path, monkeypatch, codice=lambda: next(risposte, None))
    _fino_alla_decisione_dopo(d, tmp_path)
    assert _scritture(finto) == []
    assert "serve un riavvio" in fb.get_rtdb("/conto_vero/allarmi/ordini_vietati")["testo"]


@pytest.mark.parametrize("capitale,saldo,atteso", [("300", "10000", None), ("280", "280", None),
                                                   ("301", "10000", "fuori dai limiti"), ("1e3", "10000", "fuori dai limiti"),
                                                   ("0", "10000", "fuori dai limiti"), ("-5", "10000", "fuori dai limiti"),
                                                   ("abc", "10000", "non numerico"), ("280", "200", "oltre il saldo vero")])
def test_capitale_oltre_300_o_oltre_il_saldo_rifiutato(tmp_path, monkeypatch, capitale, saldo, atteso):
    finto = _Vero()
    finto.equity = saldo
    d, fb, finto = _conto(tmp_path, monkeypatch, finto, capitale=capitale)
    _fino_alla_decisione_dopo(d, tmp_path)
    if atteso is None:                                 # fino a 300 e fino al saldo: gli ordini partono
        assert {q["symbol"] for q in _aperture(finto)} == {"AUSDT", "BUSDT"}
        return
    assert _scritture(finto) == []
    assert atteso in fb.get_rtdb("/conto_vero/allarmi/ordini_vietati")["testo"]


def _riga(tipo, importo, dopo_s=600):
    return (tipo, int((DOPO + dopo_s) * 1000), importo, "USDT")


def test_un_versamento_non_cambia_il_valore_del_conto(tmp_path, monkeypatch):
    """Problema 58 (prova p4b): 250 USDT versati non diventano posizioni: il valore è il capitale più i redditi, non il saldo."""
    finto = _Vero()
    finto.equity = "280"
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    _fino_alla_decisione_dopo(d, tmp_path)
    finto.equity = "530"
    finto.entrate.append(_riga("TRANSFER", 250.0))
    n = len(_post(finto))
    _decisione(tmp_path, GIORNO + 2)
    d.tick((GIORNO + 2) * 86400.0 + 400)
    limite = {q["symbol"]: q["quantity"] for q in _post(finto)[n:] if q["type"] == "LIMIT"}
    assert limite == {"AUSDT": "1.399", "BUSDT": "2.799"}           # ancora su 280, non su 530
    assert fb.get_rtdb("/conto_vero/stato")["equity"] == 280.0
    assert fb.get_rtdb("/conto_vero/movimenti_non_contati")["movimenti"] == {"TRANSFER USDT": 250.0}


def test_un_prelievo_non_fa_scattare_lo_stop_ma_ferma_gli_ordini_nuovi(tmp_path, monkeypatch):
    finto = _Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    _fino_alla_decisione_dopo(d, tmp_path)
    finto.equity = "100"                               # 180 USDT prelevati
    finto.entrate.append(_riga("TRANSFER", -180.0))
    for k in range(3):                                 # tre letture di fila (problema 64)
        d.tick(DOPO + 600 + 60 * k)
    assert "fermo" not in d.carica()                   # prima il prelievo valeva come una perdita del 64%: stop
    _decisione(tmp_path, GIORNO + 2)
    d.tick((GIORNO + 2) * 86400.0 + 400)
    assert len(_aperture(finto)) == 2
    assert "sotto il valore del bot" in fb.get_rtdb("/conto_vero/allarmi/ordini_vietati")["testo"]


def test_i_redditi_del_conto_fanno_il_valore_e_oltre_600_niente_ordini(tmp_path, monkeypatch):
    finto = _Vero()
    finto.equity = "280"
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    _fino_alla_decisione_dopo(d, tmp_path)
    finto.entrate += [_riga("REALIZED_PNL", -50.0), _riga("FUNDING_FEE", 2.0), _riga("COMMISSION", -0.5), _riga("WELCOME_BONUS", 5.0)]
    finto.equity = "236.5"
    n = len(_post(finto))
    _decisione(tmp_path, GIORNO + 2)
    d.tick((GIORNO + 2) * 86400.0 + 400)
    assert fb.get_rtdb("/conto_vero/stato")["equity"] == 231.5      # 280 − 50 + 2 − 0,5; il premio non conta
    assert {q["symbol"]: q["quantity"] for q in _post(finto)[n:] if q["type"] == "LIMIT"} == {"AUSDT": "1.157", "BUSDT": "2.314"}
    finto.entrate.append(_riga("REALIZED_PNL", 400.0, dopo_s=86400 + 3600))
    finto.equity = "636.5"
    m = len(_post(finto))
    _decisione(tmp_path, GIORNO + 3)
    d.tick((GIORNO + 3) * 86400.0 + 400)
    assert not [q for q in _post(finto)[m:] if q["type"] == "LIMIT"]
    assert "oltre 600" in fb.get_rtdb("/conto_vero/allarmi/ordini_vietati")["testo"]


class _VeroFiltri(_Vero):
    """exchangeInfo del conto vero con un passo di quantità che si può cambiare da un giorno all'altro."""
    passo = "0.01"

    def __call__(self, metodo, url, headers=None, timeout=None):
        u = urlparse(url)
        if u.path != "/fapi/v1/exchangeInfo":
            return super().__call__(metodo, url, headers, timeout)
        assert u.hostname == self.HOST
        self.chiamate.append((metodo, u.path, {}))
        return _Risposta({"symbols": [{"symbol": s, "filters": [
            {"filterType": "PRICE_FILTER", "tickSize": "0.01"},
            {"filterType": "LOT_SIZE", "stepSize": self.passo, "minQty": self.passo},
            {"filterType": "MIN_NOTIONAL", "notional": "5"}]} for s in self.simboli]})


def test_filtri_dal_vero_exchange_info_riletti_ogni_giorno(tmp_path, monkeypatch):
    """I filtri vengono dall'exchangeInfo di fapi.binance.com a ogni ribilancio, non dalla copia fissa del demo (qui resa molto
    più severa: se valesse, nessun ordine partirebbe)."""
    severi = {"passo": 1.0, "quantita_minima": 1.0, "valore_minimo": 1000.0}
    monkeypatch.setattr(dm, "filtri_veri", lambda *a, **k: {"AUSDT": severi, "BUSDT": severi})
    d, fb, finto = _conto(tmp_path, monkeypatch, _VeroFiltri())
    _fino_alla_decisione_dopo(d, tmp_path)
    assert {q["symbol"]: q["quantity"] for q in _post(finto)} == {"AUSDT": "1.39", "BUSDT": "2.79"}
    assert fb.get_rtdb("/conto_vero/filtri")["da"] == "fapi.binance.com"
    n = len(_post(finto))
    finto.passo = "0.1"                                # il giorno dopo Binance cambia il passo
    _decisione(tmp_path, GIORNO + 2)
    d.tick((GIORNO + 2) * 86400.0 + 400)
    assert {q["symbol"]: q["quantity"] for q in _post(finto)[n:] if q["type"] == "LIMIT"} == {"AUSDT": "1.3", "BUSDT": "2.7"}


def test_ribilancio_senza_capitale_fissato_o_con_eventi_rifiutato(tmp_path, monkeypatch):
    """La seconda difesa dopo le condizioni: il ribilancio del conto vero non parte senza un capitale fissato fino a 300 USDT
    (il demo senza capitale lavora sul conto intero) e non tocca mai le operazioni a eventi."""
    d, _, finto = _conto(tmp_path, monkeypatch)
    c = d.cliente()
    c.blocco = None
    pesi = {"AUSDT": 0.5, "BUSDT": -0.5}
    for st in ({}, {"conto_ridotto": {"capitale": 1000.0}}):
        with pytest.raises(RuntimeError, match="capitale fissato"):
            d.ribilancia(c, st, pesi, GIORNO, MEZZOGIORNO)
    with pytest.raises(RuntimeError, match="eventi"):
        d.ribilancia(c, {"conto_ridotto": {"capitale": 280.0}}, pesi, GIORNO, MEZZOGIORNO, solo={"AUSDT"})
    assert finto.chiamate == []
    assert not d.eventi_accesi() and d.eventi_aperti() == {}


def test_il_cliente_col_blocco_rifiuta_gli_ordini_che_aprono():
    finto = _Vero()
    c = cv.ClienteVero("chiave", "segreto", http=finto)
    assert c.blocco                                    # nasce chiuso
    apre = {"symbol": "AUSDT", "side": "BUY", "type": "LIMIT", "timeInForce": "GTC", "quantity": "1", "price": "100"}
    with pytest.raises(RuntimeError, match="passano solo le chiusure"):
        c.chiedi("POST", "/fapi/v1/order", apre, firmata=True)
    with pytest.raises(RuntimeError, match="passano solo le chiusure"):
        c.chiedi("POST", "/fapi/v1/batchOrders", {"batchOrders": "[]"}, firmata=True)
    assert finto.chiamate == []                        # non è partito niente
    c.chiedi("POST", "/fapi/v1/order", {"symbol": "AUSDT", "side": "SELL", "type": "MARKET", "quantity": "1",
                                        "reduceOnly": "true"}, firmata=True)
    c.chiedi("DELETE", "/fapi/v1/allOpenOrders", {"symbol": "AUSDT"}, firmata=True)
    assert [(m, p) for m, p, _ in finto.chiamate] == [("POST", "/fapi/v1/order"), ("DELETE", "/fapi/v1/allOpenOrders")]
    c.blocco = None
    c.chiedi("POST", "/fapi/v1/order", apre, firmata=True)
    assert len(finto.chiamate) == 3


def _git(cartella, *argomenti):
    subprocess.run(["git", "-C", str(cartella), "-c", "user.name=prova", "-c", "user.email=prova@esempio.org",
                    "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false", *argomenti], check=True, capture_output=True)


def test_il_codice_si_confronta_con_il_tag(tmp_path):
    for p in ("bot/portafoglio/a.py", "bot/execution/b.py", "bot/risk/c.py", "bot/config.py", "bot/main.py", "docs/note.md"):
        f = tmp_path / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x = 1\n")
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "primo")
    assert cv.codice_approvato(tmp_path).startswith("manca il tag conto-vero-approvato")
    _git(tmp_path, "tag", cv.TAG_APPROVATO)
    assert cv.codice_approvato(tmp_path) is None
    (tmp_path / "docs" / "note.md").write_text("altro\n")                  # fuori dal percorso degli ordini: niente
    assert cv.codice_approvato(tmp_path) is None
    for p in ("bot/portafoglio/a.py", "bot/execution/b.py", "bot/risk/c.py", "bot/config.py", "bot/main.py"):
        (tmp_path / p).write_text("x = 2\n")
        assert p in cv.codice_approvato(tmp_path), p
        (tmp_path / p).write_text("x = 1\n")
    assert cv.codice_approvato(tmp_path) is None
    (tmp_path / "bot" / "portafoglio" / "nuovo.py").write_text("y = 1\n")  # un file nuovo nel percorso, non nel tag
    assert "nuovo.py" in cv.codice_approvato(tmp_path)
    (tmp_path / "bot" / "portafoglio" / "nuovo.py").unlink()
    (tmp_path / "bot" / "risk" / "c.py").write_text("x = 3\n")             # un commit dopo il tag: vale il tag
    _git(tmp_path, "commit", "-q", "-a", "-m", "dopo")
    assert "bot/risk/c.py" in cv.codice_approvato(tmp_path)
    assert cv.codice_approvato(tmp_path / "non_c_e") is not None            # git che non riesce: non approvato


def _repo_con_il_tag(tmp_path, file_=("bot/portafoglio/a.py", "bot/execution/b.py", "bot/risk/c.py", "bot/config.py",
                                         "bot/main.py", "research/esclusi.py", "docs/note.md")):
    for p in file_:
        f = tmp_path / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x = 1\n")
    (tmp_path / ".gitignore").write_text("ignorati/\n")
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "primo")
    _git(tmp_path, "tag", cv.TAG_APPROVATO)


def test_il_tag_copre_tutti_i_file_caricati_nel_processo(tmp_path):
    """Problema 54: anche i file caricati fuori dai percorsi degli ordini (per esempio l'elenco delle monete escluse da G1 in
    research/) si confrontano con il tag; un file caricato che il tag non ha (nuovo o ignorato da git) non è approvato."""
    _repo_con_il_tag(tmp_path)
    caricati = ["research/esclusi.py", "bot/portafoglio/a.py"]
    assert cv.codice_approvato(tmp_path, caricati=caricati) is None
    (tmp_path / "research" / "esclusi.py").write_text("x = 2\n")
    assert cv.codice_approvato(tmp_path) is None                             # senza i caricati non lo vedrebbe
    assert "research/esclusi.py" in cv.codice_approvato(tmp_path, caricati=caricati)
    (tmp_path / "research" / "esclusi.py").write_text("x = 1\n")
    for nuovo in ("research/nuovo.py", "ignorati/m.py"):
        (tmp_path / nuovo).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / nuovo).write_text("y = 1\n")
        assert "che il tag" in cv.codice_approvato(tmp_path, caricati=caricati + [nuovo]), nuovo


def test_i_file_caricati_sono_quelli_del_repository_senza_l_ambiente_python(tmp_path, monkeypatch):
    import sys
    import types
    for nome, rel in (("_prova_bot_a", "bot/a.py"), ("_prova_venv", ".venv/lib/python3.11/site-packages/x.py"),
                      ("_prova_fuori", "../altrove.py")):
        m = types.ModuleType(nome)
        m.__file__ = str(tmp_path / "radice" / rel)
        monkeypatch.setitem(sys.modules, nome, m)
    assert cv.file_caricati(tmp_path / "radice") == ["bot/a.py"]
    import bot.portafoglio.f5  # noqa: F401  (carica research/programma6/esclusi.py, come il bot)
    veri = cv.file_caricati()
    assert "bot/portafoglio/conto_vero.py" in veri and "research/programma6/esclusi.py" in veri


def test_il_conto_vero_controlla_i_file_caricati_all_avvio_e_dopo(tmp_path, monkeypatch):
    chiamate = []
    monkeypatch.setattr(cv, "codice_approvato", lambda **k: chiamate.append(k) or None)
    d = cv.ContoVeroG1(_InMemoryStore(), file_stato=tmp_path / "st.json", interruttore=tmp_path / "acceso")
    assert len(chiamate) == 1 and "bot/portafoglio/conto_vero.py" in chiamate[0]["caricati"]
    assert 0 < chiamate[0]["cambiati_dopo"] <= time.time()                  # problema 61: l'avvio del processo
    d._verifica_codice()
    assert "bot/portafoglio/conto_vero.py" in chiamate[1]["caricati"] and chiamate[1].get("cambiati_dopo") is None


def test_file_cambiati_dopo_l_avvio_del_processo_serve_un_riavvio(tmp_path):
    """Problema 61: un file cambiato dopo l'avvio del processo (il git pull della macchina mentre il bot partiva) vuol dire che in
    memoria può esserci la versione di prima: all'avvio non è approvato, anche se ora è uguale al tag."""
    _repo_con_il_tag(tmp_path)
    vecchio = time.time() - 3600
    for f in tmp_path.rglob("*.py"):
        os.utime(f, (vecchio, vecchio))
    avvio = time.time() - 60
    assert cv.codice_approvato(tmp_path, caricati=["research/esclusi.py"], cambiati_dopo=avvio) is None
    os.utime(tmp_path / "research" / "esclusi.py", None)                     # toccato adesso, contenuto uguale al tag
    assert cv.codice_approvato(tmp_path, caricati=["research/esclusi.py"]) is None
    assert "dopo l'avvio" in cv.codice_approvato(tmp_path, caricati=["research/esclusi.py"], cambiati_dopo=avvio)
    os.utime(tmp_path / "research" / "esclusi.py", (vecchio, vecchio))
    os.utime(tmp_path / "bot" / "risk" / "c.py", None)                       # anche un file del percorso non caricato
    assert "bot/risk/c.py" in cv.codice_approvato(tmp_path, cambiati_dopo=avvio)
    assert 0 < cv.avvio_del_processo() <= time.time()


def test_la_macchina_scarica_sposta_e_toglie_il_tag(tmp_path, monkeypatch):
    """Problema 55: l'agente della macchina porta il solo tag del codice approvato, forzato; un errore non lo ferma."""
    from scripts import ops_agent as oa
    assert oa.TAG_CONTO_VERO == cv.TAG_APPROVATO
    origine, lavoro, macchina = tmp_path / "origine.git", tmp_path / "lavoro", tmp_path / "macchina"
    subprocess.run(["git", "init", "-q", "--bare", str(origine)], check=True)
    lavoro.mkdir()
    _git(lavoro, "init", "-q")
    (lavoro / "a.py").write_text("x = 1\n")
    _git(lavoro, "add", ".")
    _git(lavoro, "commit", "-q", "-m", "primo")
    _git(lavoro, "push", "-q", str(origine), "HEAD:refs/heads/principale")
    subprocess.run(["git", "clone", "-q", "-b", "principale", str(origine), str(macchina)], check=True)
    monkeypatch.setattr(oa, "APP_DIR", str(macchina))

    def tag_qui():
        r = subprocess.run(["git", "-C", str(macchina), "rev-parse", "-q", "--verify", f"refs/tags/{cv.TAG_APPROVATO}"],
                           capture_output=True, text=True)
        return r.stdout.strip() or None

    def testa():
        return subprocess.run(["git", "-C", str(lavoro), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()

    assert oa.porta_il_tag() is True and tag_qui() is None                 # nessun tag sul repository: niente
    _git(lavoro, "tag", cv.TAG_APPROVATO)
    _git(lavoro, "push", "-q", str(origine), f"refs/tags/{cv.TAG_APPROVATO}")
    assert oa.porta_il_tag() is True and tag_qui() == testa()
    (lavoro / "a.py").write_text("x = 2\n")
    _git(lavoro, "commit", "-q", "-a", "-m", "secondo")
    _git(lavoro, "push", "-q", str(origine), "HEAD:refs/heads/principale")
    _git(lavoro, "tag", "-f", cv.TAG_APPROVATO)
    _git(lavoro, "push", "-q", "-f", str(origine), f"refs/tags/{cv.TAG_APPROVATO}")
    assert oa.porta_il_tag() is True and tag_qui() == testa()             # spostato dal proprietario: si sposta anche qui
    _git(lavoro, "push", "-q", str(origine), f":refs/tags/{cv.TAG_APPROVATO}")
    assert oa.porta_il_tag() is True and tag_qui() is None                 # tolto: si toglie
    monkeypatch.setattr(oa, "APP_DIR", str(tmp_path / "non_c_e"))
    assert oa.porta_il_tag() is False                                      # errore: non blocca


def test_l_agente_porta_il_tag_dopo_il_pull_del_branch(monkeypatch):
    from scripts import ops_agent as oa
    chiamate = []
    monkeypatch.setattr(oa, "_git", lambda *a: (chiamate.append(a), (0, "claude/ramo\n"))[1])
    monkeypatch.setattr(oa, "rebase_in_progress", lambda d: False)
    monkeypatch.setattr(oa, "pending", lambda: [])
    monkeypatch.setattr(oa, "push_pending", lambda b: True)
    monkeypatch.setattr(oa, "heartbeat_due", lambda *a, **k: False)
    assert oa.main() == 0
    i = chiamate.index(("merge", "--ff-only", "origin/claude/ramo"))
    rif = f"refs/tags/{cv.TAG_APPROVATO}"
    assert ("fetch", "--no-tags", "origin", f"+{rif}:{rif}") in chiamate[i:]


@pytest.mark.parametrize("come", ["interruttore", "dry_run"])
@pytest.mark.parametrize("protezione", ["stop", "file", "firebase"])
def test_spento_con_le_posizioni_restano_le_protezioni_fino_al_conto_vuoto(tmp_path, monkeypatch, come, protezione):
    """Problema 53 (prove p1 e p1b): tolto l'interruttore o rimesso DRY_RUN vero con le posizioni aperte, niente ordini nuovi ma
    stop, pulsante a file e pulsante della dashboard chiudono (solo ordini «solo riduzione»); a conto vuoto nessuna richiesta."""
    finto = _Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    _fino_alla_decisione_dopo(d, tmp_path)             # AUSDT eseguito a limite: una posizione aperta
    assert finto.posizioni["AUSDT"] > 0
    if come == "interruttore":
        (tmp_path / "conto_vero_acceso").unlink()
    else:
        monkeypatch.setenv("DRY_RUN", "true")
    aperture = len(_aperture(finto))
    t = DOPO + 120
    n = len(finto.chiamate)
    d.tick(t)
    assert len(finto.chiamate) > n                     # le letture del conto continuano
    if protezione == "stop":
        finto.equity, finto.non_realizzato = "150", -130.0
    elif protezione == "file":
        (tmp_path / "chiudi").write_text("chiudi adesso")
    else:
        fb.set_rtdb(cv.COMANDO_CHIUDI, True)
    d.tick(t + 60)
    chiusure = [q for q in _post(finto) if q["type"] == "MARKET"]
    assert [(q["symbol"], q["side"], q.get("reduceOnly")) for q in chiusure] == [("AUSDT", "SELL", "true")]
    assert len(_aperture(finto)) == aperture
    assert "niente ordini nuovi" in fb.get_rtdb("/conto_vero/allarmi/ordini_vietati")["testo"]
    d.tick(t + 120)                                    # da fermo: Binance dice il conto vuoto
    n = len(finto.chiamate)
    for k in range(3, 8):
        d.tick(t + 60 * k)
    d.tick(t + 6 * 3600)
    assert len(finto.chiamate) == n                    # poi nessuna richiesta
    assert "conto vuoto" in fb.get_rtdb("/conto_vero/stato")["stato"]


def test_spento_e_svuotato_da_binance_poi_nessuna_richiesta(tmp_path, monkeypatch):
    """Problema 53: senza interruttore, se il proprietario chiude da Binance posizioni e ordini (senza il pulsante), al controllo del
    minuto il conto è vuoto e da lì nessuna richiesta."""
    finto = _Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    _fino_alla_decisione_dopo(d, tmp_path)
    scritture = len(_scritture(finto))
    (tmp_path / "conto_vero_acceso").unlink()
    d.tick(DOPO + 120)
    finto.posizioni = {s: 0.0 for s in finto.posizioni}
    for o in finto.ordini.values():
        o["chiuso"] = True
    d.tick(DOPO + 180)
    d.tick(DOPO + 240)
    n = len(finto.chiamate)
    d.tick(DOPO + 300)
    d.tick(DOPO + 5 * 3600)
    assert len(finto.chiamate) == n and len(_scritture(finto)) == scritture
    assert "conto vuoto" in fb.get_rtdb("/conto_vero/stato")["stato"]


@pytest.mark.parametrize("perdita", ["cancellato", "illeggibile"])
def test_stato_perso_dopo_un_fermo_si_riparte_solo_con_un_riparti_nuovo(tmp_path, monkeypatch, perdita):
    """Problema 57 (prova p3c): il pulsante della dashboard ferma il conto, poi il file di stato si perde: il conto vero non riapre
    alla mezzanotte; resta fermo finché non arriva un «riparti» nuovo dal file (il testo vecchio del file non vale)."""
    finto = _Vero()
    finto.equity, finto.posizioni_vive = "290", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    (tmp_path / "riparti").write_text("riparti vecchio")
    _fino_alla_decisione_dopo(d, tmp_path)
    d.tick(DOPO + 3700)
    fb.set_rtdb(cv.COMANDO_CHIUDI, True)
    d.tick(DOPO + 3800)
    assert d.carica()["fermo"]["motivo"] == "pulsante della dashboard"
    for k in range(3):
        d.tick(DOPO + 3900 + 60 * k)
    if perdita == "cancellato":                        # il segno dell'accensione resta su Firebase
        (tmp_path / "st.json").unlink()
    else:                                              # illeggibile, e dopo un riavvio con Firebase senza tracce: basta il file
        (tmp_path / "st.json").write_text("{rotto")
        d, fb, _ = _conto(tmp_path, monkeypatch, finto)
        _decisione(tmp_path, GIORNO + 1)
    aperture = len(_aperture(finto))
    for k in range(3):
        d.tick(DOPO + 4200 + 60 * k)
    _decisione(tmp_path, GIORNO + 2)
    d.tick((GIORNO + 2) * 86400.0 + 400)
    assert len(_aperture(finto)) == aperture
    assert "stato del conto vero perso" in d.carica()["fermo"]["motivo"]
    assert fb.get_rtdb("/conto_vero/allarmi/stato_perso")
    (tmp_path / "riparti").write_text("riparti del 26 ottobre")
    d.tick((GIORNO + 2) * 86400.0 + 500)
    assert "fermo" not in d.carica()
    assert fb.get_rtdb("/conto_vero/allarmi/stato_perso") is None             # problema 68: si spegne al «riparti»
    _decisione(tmp_path, GIORNO + 3)
    d.tick((GIORNO + 3) * 86400.0 + 400)
    assert {q["symbol"] for q in _aperture(finto)[aperture:]} == {"AUSDT", "BUSDT"}


@pytest.mark.parametrize("estraneo", ["posizione", "ordine"])
def test_prima_accensione_con_il_conto_non_vuoto_niente_ordini(tmp_path, monkeypatch, estraneo):
    """Problema 59 (prova p5): alla prima accensione il conto dei future dev'essere vuoto; una posizione o un ordine non del bot non
    si chiude da solo: niente ordini e allarme finché il proprietario non lo svuota, poi si aspetta la mezzanotte."""
    finto = _Vero(simboli=("AUSDT", "BUSDT", "CUSDT"))
    finto.equity = "280"
    if estraneo == "posizione":
        finto.posizioni["CUSDT"] = 10.0
    else:
        finto.ordini[99] = {"symbol": "CUSDT", "type": "LIMIT", "side": "BUY", "quantity": "10", "orderId": 99}
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    _fino_alla_decisione_dopo(d, tmp_path)
    assert _scritture(finto) == []
    assert "il conto non è vuoto" in fb.get_rtdb("/conto_vero/allarmi/conto_non_vuoto")["testo"]
    if estraneo == "posizione":
        finto.posizioni["CUSDT"] = 0.0                 # il proprietario lo svuota
    else:
        finto.ordini[99]["chiuso"] = True
    d.tick(DOPO + 3600)
    assert fb.get_rtdb("/conto_vero/allarmi/conto_non_vuoto") is None and _scritture(finto) == []
    _decisione(tmp_path, GIORNO + 2)
    d.tick((GIORNO + 2) * 86400.0 + 400)
    assert {q["symbol"] for q in _aperture(finto)} == {"AUSDT", "BUSDT"}


def test_riparti_del_conto_vero_solo_dal_file(tmp_path, monkeypatch):
    """Problema 60: finché le regole di Firebase non sono pubblicate il conto vero non si riaccende da Firebase."""
    finto = _Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    _fino_alla_decisione_dopo(d, tmp_path)
    (tmp_path / "chiudi").write_text("chiudi 1")
    d.tick(DOPO + 120)
    d.tick(DOPO + 180)
    assert d.carica()["fermo"].get("vuoto")
    fb.set_rtdb("/commands/conto_vero_riparti", True)
    fb.set_rtdb(dm.COMANDO_RIPARTI, True)
    d.tick(DOPO + 240)
    d.tick(DOPO + 300)
    assert d.carica().get("fermo") and fb.get_rtdb("/commands/conto_vero_riparti") is True
    (tmp_path / "riparti").write_text("riparti 1")
    d.tick(DOPO + 360)
    assert "fermo" not in d.carica()


def test_guasto_di_rete_nel_primo_ribilancio_niente_chiusure_e_riaperture(tmp_path, monkeypatch):
    """Problema 62 (prova p9): la risposta di un ordine si perde nel primo ribilancio; al tentativo dopo il conto ridotto c'è già
    (lo stato si salva dopo `parti_da_zero`) e AUSDT, già eseguito, non si richiude e riapre."""
    finto = _Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    d.tick(MEZZOGIORNO)
    d.tick(MEZZOGIORNO + 3700)
    _decisione(tmp_path, GIORNO + 1)
    finto.guasti_dopo["BUSDT"] = requests.ConnectionError("risposta persa")
    d.tick(DOPO)
    assert finto.posizioni["AUSDT"] > 0
    n = len(finto.chiamate)
    d.tick(DOPO + 1900)
    assert [q for m, p, q in finto.chiamate[n:] if m == "POST" and p == "/fapi/v1/order" and q["symbol"] == "AUSDT"] == []
    assert d.carica()["conto_ridotto"]["capitale"] == 280.0


def test_dry_run_scritto_male_avvisa_una_volta(tmp_path, monkeypatch, capsys):
    """Problema 63: l'avviso di un DRY_RUN scritto male una volta, non a ogni giro (e vale vero: spento)."""
    d, fb, finto = _conto(tmp_path, monkeypatch, dry_run="treu")
    for k in range(4):
        d.tick(MEZZOGIORNO + 60 * k)
    assert capsys.readouterr().out.count("ATTENZIONE: DRY_RUN") == 1 and finto.chiamate == []


def test_il_vecchio_bot_non_si_dice_live_con_dry_run_falso():
    """Problema 63: etichette e riconciliatore del vecchio bot seguono il suo esecutore (bloccato in prova), non DRY_RUN."""
    testo = (RADICE / "bot" / "main.py").read_text(encoding="utf-8")
    assert "dry_run=settings.DRY_RUN" not in testo and testo.count('dry_run=getattr(self.executor, "dry_run", True)') == 4
    assert 'if not getattr(self.executor, "dry_run", True) and self.reconciler.start():' in testo


def test_redditi_della_stessa_ora_letti_in_due_volte_si_contano_tutti(tmp_path, monkeypatch):
    """Problema 64 (prova q4): due righe di funding delle 08:00, la seconda scritta da Binance un minuto dopo: si contano tutte e due,
    una volta sola, e il valore del bot resta uguale al saldo."""
    finto = _Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    _fino_alla_decisione_dopo(d, tmp_path)
    ore8 = int((DOPO + 7 * 3600) * 1000)
    finto.entrate.append(("FUNDING_FEE", ore8, -0.5, "USDT"))
    finto.equity = "279.5"
    d.tick(ore8 / 1000 + 61)
    finto.entrate.append(("FUNDING_FEE", ore8, -0.4, "USDT"))
    finto.equity = "279.1"
    for k in range(1, 5):
        d.tick(ore8 / 1000 + 61 + 60 * k)
    assert d._redditi == pytest.approx(-0.9)
    assert d._valori(279.1, 279.1)[0] == pytest.approx(279.1)                 # il valore del bot uguale al saldo
    _decisione(tmp_path, GIORNO + 2)
    d.tick((GIORNO + 2) * 86400.0 + 400)
    assert fb.get_rtdb("/conto_vero/allarmi/ordini_vietati") is None


def test_saldo_sotto_il_valore_ferma_solo_oltre_la_tolleranza_e_in_tre_letture(tmp_path, monkeypatch):
    """Problema 64: 1 USDT sotto (nella tolleranza dello 0,5%, 1,40 con 280) non ferma niente; 10 sotto per due letture nemmeno;
    10 sotto per tre letture di fila sì."""
    finto = _Vero()
    finto.equity = "280"
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    _fino_alla_decisione_dopo(d, tmp_path)
    finto.equity = "279"
    for k in range(4):
        d.tick(DOPO + 600 + 60 * k)
    assert fb.get_rtdb("/conto_vero/allarmi/ordini_vietati") is None
    finto.equity = "270"
    d.tick(DOPO + 900)
    d.tick(DOPO + 960)
    assert fb.get_rtdb("/conto_vero/allarmi/ordini_vietati") is None
    finto.equity = "280"
    d.tick(DOPO + 1020)
    finto.equity = "270"
    for k in range(3):
        d.tick(DOPO + 1080 + 60 * k)
    assert "3 letture di fila" in fb.get_rtdb("/conto_vero/allarmi/ordini_vietati")["testo"]


def test_redditi_che_non_si_leggono_danno_l_allarme(tmp_path, monkeypatch):
    """Problema 64 (prova q7): dopo tre letture fallite di fila l'allarme `redditi`; alla lettura buona si spegne."""
    finto = _Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    _fino_alla_decisione_dopo(d, tmp_path)
    finto.redditi_rotti = True
    d.tick(DOPO + 600)
    d.tick(DOPO + 660)
    assert fb.get_rtdb("/conto_vero/allarmi/redditi") is None
    d.tick(DOPO + 720)
    assert "non si leggono da 3 letture" in fb.get_rtdb("/conto_vero/allarmi/redditi")["testo"]
    finto.redditi_rotti = False
    d.tick(DOPO + 780)
    assert fb.get_rtdb("/conto_vero/allarmi/redditi") is None


class _VeroChiusure(_Vero):
    """Alla prima chiusura a mercato le righe dei redditi delle chiusure, con l'ora vera di quando avvengono (prova q5)."""
    ora_chiusure_ms = None

    def __call__(self, metodo, url, headers=None, timeout=None):
        r = super().__call__(metodo, url, headers, timeout)
        if (metodo == "POST" and "/fapi/v1/order" in url and "reduceOnly=true" in url and "MARKET" in url
                and self.ora_chiusure_ms and not any(t == "REALIZED_PNL" for t, *_ in self.entrate)):
            self.entrate += [("REALIZED_PNL", self.ora_chiusure_ms, 30.0, "USDT"), ("COMMISSION", self.ora_chiusure_ms, -0.2, "USDT")]
            self.non_realizzato, self.equity = 0.0, "309.8"
        return r


def test_redditi_delle_chiusure_restano_alla_fase_di_prima(tmp_path, monkeypatch):
    """Problema 65 (prova q5): con un capitale nuovo le chiusure della fase vecchia avvengono qualche secondo dopo l'inizio del giro;
    i loro redditi (+30 realizzati, −0,2 di commissioni) non entrano nella fase nuova, che parte dall'ora vera dopo le chiusure."""
    monkeypatch.setattr(dm, "ATTESA_DOPO_CHIUSURA_S", 0.0)
    finto = _VeroChiusure()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    _fino_alla_decisione_dopo(d, tmp_path)
    finto.non_realizzato, finto.equity = 30.0, "310"
    (tmp_path / "conto_vero_capitale").write_text("290")
    d.tick(DOPO + 3800)
    _decisione(tmp_path, GIORNO + 2)
    t = (GIORNO + 2) * 86400.0 + 400
    finto.ora_chiusure_ms = int((t + 5) * 1000)
    _orologio_del_giro(d, dopo_s=6.0)                  # le chiusure 5 secondi dopo l'inizio del giro; l'ora vera dopo: t + 6
    for k in range(3):
        d.tick(t + 61 * k)
    assert d.carica()["conto_ridotto"]["capitale"] == 290.0
    assert d._redditi == 0.0
    assert fb.get_rtdb("/conto_vero/allarmi/ordini_vietati") is None


def test_firebase_muto_alla_prima_lettura_si_rilegge(tmp_path):
    """Problema 66: con Firebase muto la prima risposta vuota non vale «mai acceso» per tutto il processo."""
    class _FbMuto:
        def __init__(self):
            self.dati, self.muto = {}, 30.0

        def get_rtdb(self, k):
            return None if self.muto else self.dati.get(k)

        def set_rtdb(self, k, v):
            self.dati[k] = v
            return True

        def degraded_for(self):
            return self.muto

    fb = _FbMuto()
    fb.dati["/conto_vero/acceso_dal"] = {"ora": 1.0, "compra_alla_decisione_di_g1_dopo_il": "2026-10-24"}
    d = cv.ContoVeroG1(fb, file_stato=tmp_path / "st.json", interruttore=tmp_path / "acceso", verifica_codice=lambda: None)
    assert d._acceso_su_firebase() is None
    fb.muto = 0.0
    assert d._acceso_su_firebase()["ora"] == 1.0


def test_il_tag_tolto_si_riconosce_senza_il_testo_inglese_di_git(monkeypatch):
    """Problema 67: la scomparsa del tag da `git ls-remote --exit-code` (2 = non c'è), con git in un'altra lingua; un errore di rete
    non toglie il tag."""
    from scripts import ops_agent as oa
    chiamate = []

    def git(*a):
        chiamate.append(a)
        if a[0] == "fetch":
            return 128, "fatale: impossibile trovare il riferimento remoto"
        return {"ls-remote": (2, ""), "rev-parse": (0, "abc\n")}.get(a[0], (0, ""))
    monkeypatch.setattr(oa, "_git", git)
    assert oa.porta_il_tag() is True and ("tag", "-d", cv.TAG_APPROVATO) in chiamate
    chiamate.clear()
    monkeypatch.setattr(oa, "_git", lambda *a: (chiamate.append(a), (128, "rete giù"))[1])
    assert oa.porta_il_tag() is False and not [c for c in chiamate if c[0] == "tag"]


def test_prima_accensione_lo_stop_non_chiude_le_posizioni_non_del_bot(tmp_path, monkeypatch):
    """Problema 69 (prova q8): prima della prima accensione, con una posizione del proprietario che perde il 41%, lo stop del bot non
    la chiude (come il ribilancio, problema 59); il pulsante sì, perché è un comando suo."""
    finto = _Vero(simboli=("AUSDT", "BUSDT", "CUSDT"))
    finto.equity, finto.posizioni_vive = "280", True
    finto.posizioni["CUSDT"] = 10.0
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    d.tick(MEZZOGIORNO)
    d.tick(MEZZOGIORNO + 3700)
    finto.non_realizzato, finto.equity = -115.0, "165"
    d.tick(MEZZOGIORNO + 3800)
    d.tick(MEZZOGIORNO + 7400)
    assert _scritture(finto) == [] and "fermo" not in d.carica()
    assert fb.get_rtdb("/conto_vero/allarmi/conto_non_vuoto")
    (tmp_path / "chiudi").write_text("chiudi tutto")
    d.tick(MEZZOGIORNO + 7500)
    assert [(q["symbol"], q.get("reduceOnly")) for q in _post(finto) if q["type"] == "MARKET"] == [("CUSDT", "true")]


def test_il_bot_crea_e_fa_girare_il_conto_vero_accanto_al_demo():
    testo = (RADICE / "bot" / "main.py").read_text(encoding="utf-8")
    assert "self.conto_vero = crea_conto_vero(self.fb)" in testo
    assert "ContoVeroG1(" not in testo                 # mai creato direttamente: un errore fermerebbe demo e paper (problema 71)
    i, j = testo.index("self.demo_g1.tick(time.time())"), testo.index("self.conto_vero.tick(time.time())")
    assert 0 < j - i < 400                             # subito dopo il demo, con il suo try/except
    assert "if self.conto_vero is None:" in testo[i:j]  # si riprova a ogni giro
    assert 'print(f"[conto_vero] errore: {exc}")' in testo[j:j + 200]


def test_71_un_errore_nella_creazione_non_ferma_il_bot(capsys):
    """Revisione dell'8 novembre 2026, problema 71: un errore nel costruttore del conto vero non deve far fallire l'avvio del bot
    (demo e paper restano accesi); si scrive una volta per errore e si riprova."""
    class Rotto:
        def __init__(self, fb):
            raise RuntimeError("git non risponde")
    cv._ULTIMO_ERRORE_DI_CREAZIONE[0] = None
    assert cv.crea_conto_vero(None, classe=Rotto) is None
    assert cv.crea_conto_vero(None, classe=Rotto) is None
    assert capsys.readouterr().out.count("ERRORE nella creazione") == 1
    class Buono:
        def __init__(self, fb):
            self.fb = fb
    assert isinstance(cv.crea_conto_vero("fb", classe=Buono), Buono)
    assert cv._ULTIMO_ERRORE_DI_CREAZIONE[0] is None


def test_sezione_del_conto_vero_nello_stato():
    from scripts import state_snapshot as ss

    class Fb:
        def __init__(self, d):
            self.d = d

        def get_rtdb(self, k):
            return self.d.get(k)

    assert "spento" in ss.sezione_conto_vero(Fb({}))[1]
    spento = "\n".join(ss.sezione_conto_vero(Fb({"/conto_vero/stato": {
        "stato": "spento: manca l'interruttore ops/conto_vero_acceso", "acceso": False, "aggiornato": 1.7e9}})))
    assert "spento: manca l'interruttore ops/conto_vero_acceso" in spento
    acceso = "\n".join(ss.sezione_conto_vero(Fb({
        "/conto_vero/stato": {"stato": "acceso", "equity": 290.0, "capitale_iniziale": 280.0, "rendimento": 0.0357, "long": 20,
                              "short": 18, "stop_a": 182.0, "dal_massimo": -0.01, "aggiornato": 1.7e9},
        "/conto_vero/allarmi": {"ordini_vietati": {"ora": 1.7e9, "testo": "niente ordini nuovi: manca il tag conto-vero-approvato"}},
        "/conto_vero/fermo": {"ora": 1.7e9, "motivo": "pulsante della dashboard", "chiuse": 38}})))
    assert "$290.00" in acceso and "$182.00" in acceso and "20 long, 18 short" in acceso
    assert "**ALLARME** ordini vietati" in acceso and "manca il tag" in acceso and "**FERMO**" in acceso
    assert "sezione_conto_vero(fb)" in (RADICE / "scripts" / "state_snapshot.py").read_text(encoding="utf-8")
