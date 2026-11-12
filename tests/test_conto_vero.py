"""G1 sul conto vero di Binance (bot/portafoglio/conto_vero.py), fase 2 del piano (docs/conto_vero.md), con il Binance finto dei test
del demo: solo fapi.binance.com, le quattro condizioni per accendersi, la partenza da vuoto alla mezzanotte, la versione del codice
approvata dal proprietario su Firebase (12 novembre 2026: non più un tag di git), il «riparti» in due passi dalla dashboard, il
tetto del capitale, i filtri veri, i limiti fissati. Nessuna richiesta di rete vera: il finto risponde a tutto."""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
import time
import types
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


class _Fb:
    """Firebase finto fatto come `FirebaseClient`: il database vero (``vero``) e lo specchio in memoria del processo. Quando
    risponde, `leggi_rtdb_davvero` lo dice; con ``muto`` vero le letture danno l'ultimo valore noto (lo specchio) senza la conferma e
    le scritture restano nello specchio (False). ``scritture_ferme``: solo le scritture non arrivano. ``scritti``: i percorsi scritti
    dal bot; il proprietario dalla dashboard scrive con `proprietario` (o con `set_rtdb`, come nei test di prima)."""

    def __init__(self, vero=None):
        self.vero, self.specchio = vero or _InMemoryStore(), _InMemoryStore()
        self.muto = self.scritture_ferme = False
        self.scritti = []

    def get_rtdb(self, percorso):
        if self.muto:
            return self.specchio.get_rtdb(percorso)
        v = self.vero.get_rtdb(percorso)
        self.specchio.set_rtdb(percorso, v)
        return v

    def leggi_rtdb_davvero(self, percorso):
        return (not self.muto), self.get_rtdb(percorso)

    def set_rtdb(self, percorso, valore):
        self.scritti.append(percorso)
        self.specchio.set_rtdb(percorso, valore)
        if self.muto or self.scritture_ferme:
            return False
        self.vero.set_rtdb(percorso, valore)
        return True

    def proprietario(self, percorso, valore):
        self.vero.set_rtdb(percorso, valore)

    def degraded_for(self, now=None):
        return 30.0 if self.muto else 0.0


def _scritture(finto):
    """Tutto quello che non è una lettura: ordini, annulli, leva, margine, modo delle posizioni."""
    return [(m, p, q) for m, p, q in finto.chiamate if m != "GET"]


def _aperture(finto):
    """Gli ordini che possono aprire o aumentare una posizione (non «solo riduzione»)."""
    return [q for q in _post(finto) if q.get("reduceOnly") != "true"]


def _decisione(tmp_path, giorno, pesi=None):
    (tmp_path / "g1.json").write_text(json.dumps({"ultimo_lunedi": giorno, "pesi": pesi or {"AUSDT": 0.5, "BUSDT": -0.5}}))


def _conto(tmp_path, monkeypatch, finto=None, *, acceso=True, dry_run="false", capitale="280", codice=None, pesi=None, fb=None,
           radice=None):
    """Il conto vero dei test. Con ``codice`` (o senza ``radice``) la verifica del codice è finta; con ``radice`` (un repository di
    prova) gira quella vera: il commit approvato letto da Firebase e i confronti di git."""
    monkeypatch.setenv("DRY_RUN", dry_run)
    finto = finto or _Vero()
    fb = fb or _Fb()
    if acceso:
        (tmp_path / "conto_vero_acceso").write_text("si")
    if capitale is not None:
        (tmp_path / "conto_vero_capitale").write_text(capitale)
    _decisione(tmp_path, GIORNO, pesi)
    d = cv.ContoVeroG1(fb, cliente=cv.ClienteVero("chiave", "segreto", http=finto), file_stato=tmp_path / "st.json",
                       file_g1=tmp_path / "g1.json", interruttore=tmp_path / "conto_vero_acceso", file_chiudi=tmp_path / "chiudi",
                       file_capitale=tmp_path / "conto_vero_capitale",
                       **({"radice": radice} if radice is not None and codice is None else
                          {"verifica_codice": codice or (lambda: None)}))
    _orologio_del_giro(d)
    return d, fb, finto


def _conferma_della_dashboard(fb):
    """Il testo che la dashboard scrive al secondo passo del «riparti»: l'ora del fermo pubblicata dal bot, in secondi interi
    (`String(Math.floor(fermo.ora))` in dashboard/app/components/strategie/ComandiContoVero.tsx)."""
    return str(math.floor(fb.get_rtdb("/conto_vero/fermo")["ora"]))


def _riparti_in_due_passi(fb):
    fb.proprietario(cv.COMANDO_RIPARTI, True)
    fb.proprietario(cv.COMANDO_RIPARTI_CONFERMA, _conferma_della_dashboard(fb))


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
    proprietario e fatto approvare (con una versione nuova approvata da lui). La classe usa questi, non quelli del demo."""
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
    assert cv.PERCORSI_DEGLI_ORDINI == ("bot/portafoglio", "bot/execution", "bot/risk", "bot/config.py", "bot/main.py")
    # 12 novembre 2026: la versione la approva il proprietario su Firebase, non un tag di git; «riparti» in due passi, senza file
    assert not hasattr(cv, "TAG_APPROVATO") and not hasattr(cv, "FILE_RIPARTI")
    assert cv.COMANDO_VERSIONE == "/commands/conto_vero_versione_approvata"
    assert (cv.COMANDO_CHIUDI, cv.COMANDO_RIPARTI, cv.COMANDO_RIPARTI_CONFERMA) == (
        "/commands/conto_vero_chiudi_tutto", "/commands/conto_vero_riparti", "/commands/conto_vero_riparti_conferma")
    assert (cv.OGNI_CONTROLLO_CODICE_S, cv.LETTURE_VERSIONE_PRIMA_DELL_ALLARME) == (60, 3)
    for nome in ("LEVA", "CAPITALE_MASSIMO", "VALORE_MASSIMO_PER_ORDINI", "STOP_CONTO", "PAVIMENTO_RIPARTI", "SOMMA_PESI_MASSIMA",
                 "PESO_MASSIMO_MONETA", "ETA_MASSIMA_DECISIONE_S", "COMANDO_CHIUDI", "COMANDO_RIPARTI", "TOLLERANZA_SALDO",
                 "TOLLERANZA_SALDO_MINIMA", "LETTURE_SALDO_SOTTO"):
        assert getattr(cv.ContoVeroG1, nome) == getattr(cv, nome), nome
    # stato, comandi e ramo di Firebase separati da quelli del demo
    assert cv.ContoVeroG1.NOME == "conto_vero" and dm.DemoG1.NOME == "demo_binance"
    assert {cv.COMANDO_CHIUDI, cv.COMANDO_RIPARTI, cv.COMANDO_RIPARTI_CONFERMA, cv.COMANDO_VERSIONE}.isdisjoint(
        {dm.COMANDO_CHIUDI, dm.COMANDO_RIPARTI})
    assert {cv.FILE_STATO, cv.FILE_CHIUDI, cv.FILE_CAPITALE, cv.INTERRUTTORE}.isdisjoint(
        {dm.FILE_STATO, dm.FILE_CHIUDI, dm.FILE_RIPARTI, dm.FILE_CAPITALE, dm.INTERRUTTORE})
    assert cv.ContoVeroG1.FILE_COMANDI_DI_SERIE == (cv.FILE_CHIUDI,)                # nessun file per il «riparti»
    with pytest.raises(TypeError):
        cv.ContoVeroG1(_Fb(), file_riparti=Path("riparti"), verifica_codice=lambda: None)
    assert cv.ContoVeroG1(_Fb(), verifica_codice=lambda: None).file_riparti == Path(os.devnull)


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
        cv.ContoVeroG1(_Fb(), cliente=dm.ClienteDemo("chiave", "segreto", http=_Demo()), verifica_codice=lambda: None)


@pytest.mark.parametrize("manca", ["nessuna", "interruttore", "dry_run", "dry_run_scritto_male", "codice", "capitale"])
def test_senza_una_delle_quattro_condizioni_nessun_ordine(tmp_path, monkeypatch, manca):
    """(a) l'interruttore, (b) DRY_RUN falso, (c) il codice della versione approvata, (d) il capitale: se ne manca una, nessuna
    richiesta di ordine nemmeno alla decisione di G1 dopo l'accensione; con tutte e quattro gli ordini partono (il controllo)."""
    d, fb, finto = _conto(tmp_path, monkeypatch, acceso=manca != "interruttore",
                          dry_run={"dry_run": "true", "dry_run_scritto_male": "treu"}.get(manca, "false"),
                          capitale=None if manca == "capitale" else "280",
                          codice=(lambda: "nessuna versione approvata dal proprietario") if manca == "codice" else None)
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
        assert "niente ordini nuovi" in testo and ("versione approvata" if manca == "codice" else "capitale") in testo


def test_le_chiavi_del_conto_vero_non_si_leggono_da_spento(tmp_path, monkeypatch):
    monkeypatch.setenv("BINANCE_API_KEY", "chiave-di-prova")
    monkeypatch.setenv("BINANCE_API_SECRET", "segreto-di-prova")
    monkeypatch.setenv("DRY_RUN", "true")
    (tmp_path / "acceso").write_text("si")
    d = cv.ContoVeroG1(_Fb(), file_stato=tmp_path / "st.json", file_g1=tmp_path / "g1.json",
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
def test_codice_diverso_dalla_versione_approvata_niente_ordini_nuovi_ma_stop_e_pulsante(tmp_path, monkeypatch, protezione):
    codice = [None]
    finto = _Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto, codice=lambda: codice[0])
    _fino_alla_decisione_dopo(d, tmp_path)             # AUSDT eseguito a limite, BUSDT ancora sul libro
    assert finto.posizioni["AUSDT"] > 0 and len(_aperture(finto)) == 2
    codice[0] = "file del codice diversi dalla versione approvata (0123abcd): bot/risk/hard_limits.py"
    d.tick(DOPO + 120)                                 # il controllo del codice del minuto: blocco
    assert "diversi dalla versione approvata" in fb.get_rtdb("/conto_vero/allarmi/ordini_vietati")["testo"]
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
    codice[0] = "file del codice diversi dalla versione approvata (0123abcd): bot/portafoglio/f5.py"
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
    codice[0] = "nessuna versione approvata dal proprietario"
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
    """Il processo ha in memoria il codice dell'avvio: se allora non era un commit riconoscibile, niente ordini anche quando i file
    tornano uguali."""
    risposte = iter(["file del codice diversi dal commit in esecuzione (0123abcd): bot/main.py"])
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


FILE_DEL_REPO = ("bot/portafoglio/a.py", "bot/execution/b.py", "bot/risk/c.py", "bot/config.py", "bot/main.py",
                 "research/esclusi.py", "docs/note.md")
PERCORSI_DEL_REPO = FILE_DEL_REPO[:5]


def _testa(cartella):
    return subprocess.run(["git", "-C", str(cartella), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()


def _invecchia(cartella):
    """I file del repository di prova con un'ora di ieri: altrimenti sono «cambiati dopo l'avvio del processo» (quello dei test)."""
    ieri = time.time() - 86400
    for f in Path(cartella).rglob("*"):
        if f.is_file() and ".git" not in f.relative_to(cartella).parts:
            os.utime(f, (ieri, ieri))


def _commit(cartella, file_: dict, titolo: str) -> str:
    """Scrive i file, li committa e restituisce l'hash del commit."""
    for p, testo in file_.items():
        f = Path(cartella) / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(testo)
    _git(cartella, "add", ".")
    _git(cartella, "commit", "-q", "-m", titolo)
    _invecchia(cartella)
    return _testa(cartella)


def _repo(cartella, file_=FILE_DEL_REPO) -> str:
    """Un repository di prova con i percorsi degli ordini; restituisce il primo commit."""
    Path(cartella).mkdir(parents=True, exist_ok=True)
    (Path(cartella) / ".gitignore").write_text("ignorati/\n")
    _git(cartella, "init", "-q")
    return _commit(cartella, {p: "x = 1\n" for p in file_}, "primo commit di prova")


def test_il_codice_si_confronta_con_il_commit_approvato(tmp_path):
    """Assente, non valido, non nel repository, diverso, uguale: solo l'ultimo è approvato (None)."""
    primo = _repo(tmp_path)
    assert "non c'è o non è un commit valido" in cv.codice_approvato(tmp_path)                 # nessun commit approvato
    for non_valido in ("", "HEAD", "main", primo[:39], primo + "0", primo.upper(), primo[:39] + "g", "--all", f" {primo[:39]}",
                       123, None, {"commit": primo}):
        assert "non è un commit valido" in cv.codice_approvato(tmp_path, non_valido), non_valido
    assert "non è un commit del repository" in cv.codice_approvato(tmp_path, "0123456789abcdef0123456789abcdef01234567")
    assert cv.codice_approvato(tmp_path, primo) is None
    (tmp_path / "docs" / "note.md").write_text("altro\n")                  # fuori dal percorso degli ordini: niente
    assert cv.codice_approvato(tmp_path, primo) is None
    for p in PERCORSI_DEL_REPO:
        (tmp_path / p).write_text("x = 2\n")
        motivo = cv.codice_approvato(tmp_path, primo)
        assert p in motivo and "diversi dalla versione approvata" in motivo and primo[:8] in motivo, p
        (tmp_path / p).write_text("x = 1\n")
    assert cv.codice_approvato(tmp_path, primo) is None
    (tmp_path / "bot" / "portafoglio" / "nuovo.py").write_text("y = 1\n")  # un file nuovo nel percorso, non nel commit
    assert "nuovo.py" in cv.codice_approvato(tmp_path, primo)
    (tmp_path / "bot" / "portafoglio" / "nuovo.py").unlink()
    secondo = _commit(tmp_path, {"bot/risk/c.py": "x = 3\n"}, "un commit dopo quello approvato")
    assert "bot/risk/c.py" in cv.codice_approvato(tmp_path, primo)          # vale il commit approvato, non l'ultimo
    assert cv.codice_approvato(tmp_path, secondo) is None                   # finché il proprietario non approva quello nuovo
    assert cv.codice_approvato(tmp_path / "non_c_e", primo) is not None     # git che non riesce: non approvato


def test_il_commit_in_memoria_deve_essere_quello_approvato(tmp_path):
    """I file di adesso possono essere già quelli nuovi (il git pull della macchina) mentre il processo esegue ancora i vecchi:
    con ``in_memoria`` (HEAD all'avvio del processo) il commit approvato deve essere uguale anche a quello, nei file del codice."""
    primo = _repo(tmp_path)
    solo_note = _commit(tmp_path, {"docs/note.md": "altro\n"}, "solo documenti")
    assert cv.codice_approvato(tmp_path, solo_note, in_memoria=primo) is None      # commit diversi, stessi file del codice
    assert cv.codice_approvato(tmp_path, primo, in_memoria=solo_note) is None
    nuovo = _commit(tmp_path, {"bot/portafoglio/a.py": "x = 2\n"}, "codice nuovo")
    assert cv.codice_approvato(tmp_path, nuovo) is None                            # i file di adesso sono quelli approvati...
    motivo = cv.codice_approvato(tmp_path, nuovo, in_memoria=primo)               # ...ma il processo esegue ancora i vecchi
    assert "il processo esegue il commit" in motivo and "bot/portafoglio/a.py" in motivo and "serve un riavvio" in motivo
    assert primo[:8] in motivo and nuovo[:8] in motivo
    assert cv.codice_approvato(tmp_path, nuovo, in_memoria=nuovo) is None          # dopo il riavvio
    assert "non si conosce" in cv.codice_approvato(tmp_path, nuovo, in_memoria="non-un-commit")
    # un file caricato fuori dai percorsi degli ordini conta allo stesso modo
    altro = _commit(tmp_path, {"research/esclusi.py": "x = 2\n"}, "elenco nuovo")
    assert cv.codice_approvato(tmp_path, altro, in_memoria=nuovo) is None
    assert "research/esclusi.py" in cv.codice_approvato(tmp_path, altro, caricati=["research/esclusi.py"], in_memoria=nuovo)


def test_il_commit_in_esecuzione_e_head_con_data_e_titolo(tmp_path):
    primo = _repo(tmp_path)
    v = cv.commit_in_esecuzione(tmp_path)
    assert v["commit"] == primo and v["titolo"] == "primo commit di prova" and re.fullmatch(r"\d{4}-\d\d-\d\dT.*", v["data"])
    lungo = _commit(tmp_path, {"docs/note.md": "x\n"}, "t" * 300)
    v = cv.commit_in_esecuzione(tmp_path)
    assert v["commit"] == lungo and v["titolo"] == "t" * cv.TITOLO_MASSIMO
    assert "non letto" in cv.commit_in_esecuzione(tmp_path / "non_c_e")["errore"]
    vero = cv.commit_in_esecuzione()                                         # il repository vero
    assert cv.RE_COMMIT.fullmatch(vero["commit"]) and vero["titolo"]


def test_la_versione_approvata_si_legge_solo_da_una_risposta_vera_di_firebase():
    """Assente, non valida, valida; e mai un commit senza la risposta di Firebase, nemmeno quello rimasto nello specchio."""
    commit = "0123456789abcdef0123456789abcdef01234567"
    fb = _Fb()
    c, motivo, risposto = cv.versione_approvata(fb)
    assert c is None and risposto and "nessuna versione approvata" in motivo
    for non_valida in (commit, {"ora": 1}, {"commit": commit.upper()}, {"commit": commit[:39]}, {"commit": "HEAD"}, {"commit": 7},
                       [commit], True):
        fb.proprietario(cv.COMANDO_VERSIONE, non_valida)
        c, motivo, risposto = cv.versione_approvata(fb)
        assert c is None and risposto and "non è valida" in motivo, non_valida
    fb.proprietario(cv.COMANDO_VERSIONE, {"commit": commit, "ora": 1.7e12})
    assert cv.versione_approvata(fb) == (commit, None, True)
    fb.muto = True                                                          # lo specchio ha ancora il commit: non vale
    assert fb.get_rtdb(cv.COMANDO_VERSIONE)["commit"] == commit
    c, motivo, risposto = cv.versione_approvata(fb)
    assert c is None and risposto is False and "Firebase non risponde" in motivo
    assert cv.versione_approvata(None)[::2] == (None, False)                # senza Firebase

    class SenzaConferma:                                                    # un client che non sa dire se ha risposto: non vale
        def get_rtdb(self, percorso):
            return {"commit": commit, "ora": 1}
    assert cv.versione_approvata(SenzaConferma())[::2] == (None, False)

    class Rotto:
        def leggi_rtdb_davvero(self, percorso):
            raise RuntimeError("rete giù")
    assert cv.versione_approvata(Rotto())[::2] == (None, False)

    class QuasiVero:                                                        # «risposto» deve essere proprio True
        def leggi_rtdb_davvero(self, percorso):
            return 1, {"commit": commit, "ora": 1}
    assert cv.versione_approvata(QuasiVero())[::2] == (None, False)


def test_il_client_di_firebase_dice_se_ha_risposto_davvero(monkeypatch):
    """`FirebaseClient.leggi_rtdb_davvero`: (True, valore) solo se il database ha risposto a questa chiamata; non configurato o in
    errore (False, ultimo valore noto), anche se nel frattempo un'altra lettura è riuscita."""
    from bot.core import firebase_client as fc
    monkeypatch.setattr(fc.settings, "FIREBASE_SERVICE_ACCOUNT", "")
    client = fc.FirebaseClient()
    client._memory.set_rtdb("/commands/x", {"commit": "vecchio"})
    assert client.leggi_rtdb_davvero("/commands/x") == (False, {"commit": "vecchio"})      # non configurato: mai «davvero»

    class Rif:
        def __init__(self, db, percorso):
            self.db, self.percorso = db, percorso

        def get(self):
            if self.percorso in self.db.rotti:
                raise RuntimeError("rete giù")
            return self.db.dati.get(self.percorso)

    class Db:
        def __init__(self):
            self.dati, self.rotti = {"/commands/x": {"commit": "nuovo"}, "/altro": 1}, set()

        def reference(self, percorso):
            return Rif(self, percorso)

    client._db, client._live = Db(), True
    assert client.leggi_rtdb_davvero("/commands/x") == (True, {"commit": "nuovo"})
    client._db.rotti.add("/commands/x")
    assert client.leggi_rtdb_davvero("/commands/x") == (False, {"commit": "nuovo"})         # l'ultimo noto, ma non «davvero»
    assert client.get_rtdb("/altro") == 1 and client.degraded_for() == 0.0                  # un'altra lettura riesce: non basta
    assert client.leggi_rtdb_davvero("/commands/x")[0] is False


def test_i_file_caricati_si_confrontano_tutti_con_il_commit_approvato(tmp_path):
    """Problema 54: anche i file caricati fuori dai percorsi degli ordini (per esempio l'elenco delle monete escluse da G1 in
    research/) si confrontano con il commit approvato; un file caricato che il commit non ha (nuovo o ignorato da git) non è
    approvato."""
    primo = _repo(tmp_path)
    caricati = ["research/esclusi.py", "bot/portafoglio/a.py"]
    assert cv.codice_approvato(tmp_path, primo, caricati=caricati) is None
    (tmp_path / "research" / "esclusi.py").write_text("x = 2\n")
    assert cv.codice_approvato(tmp_path, primo) is None                      # senza i caricati non lo vedrebbe
    assert "research/esclusi.py" in cv.codice_approvato(tmp_path, primo, caricati=caricati)
    (tmp_path / "research" / "esclusi.py").write_text("x = 1\n")
    for nuovo in ("research/nuovo.py", "ignorati/m.py"):
        (tmp_path / nuovo).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / nuovo).write_text("y = 1\n")
        assert "non ha" in cv.codice_approvato(tmp_path, primo, caricati=caricati + [nuovo]), nuovo


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
    """All'avvio: i file caricati e l'ora d'avvio del processo contro HEAD (il commit in esecuzione). Ogni minuto: gli stessi
    file contro il commit approvato letto da Firebase, con il commit in memoria."""
    testa, approvato = "a" * 40, "b" * 40
    chiamate = []
    monkeypatch.setattr(cv, "commit_in_esecuzione", lambda radice: {"commit": testa, "data": "2026-11-12T06:00:00+00:00", "titolo": "t"})
    monkeypatch.setattr(cv, "codice_approvato", lambda **k: chiamate.append(k) or None)
    fb = _Fb()
    fb.proprietario(cv.COMANDO_VERSIONE, {"commit": approvato, "ora": 1.7e12})
    d = cv.ContoVeroG1(fb, file_stato=tmp_path / "st.json", interruttore=tmp_path / "acceso")
    assert len(chiamate) == 1 and "bot/portafoglio/conto_vero.py" in chiamate[0]["caricati"]
    assert chiamate[0]["commit"] == testa and chiamate[0]["nome"] == "il commit in esecuzione" and chiamate[0]["radice"] == cv.RADICE
    assert 0 < chiamate[0]["cambiati_dopo"] <= time.time()                  # problema 61: l'avvio del processo
    assert fb.scritti == []                                                 # il costruttore non scrive e non legge Firebase
    assert d._verifica_codice() is None
    assert "bot/portafoglio/conto_vero.py" in chiamate[1]["caricati"] and chiamate[1].get("cambiati_dopo") is None
    assert chiamate[1]["commit"] == approvato and chiamate[1]["in_memoria"] == testa


def test_file_cambiati_dopo_l_avvio_del_processo_serve_un_riavvio(tmp_path):
    """Problema 61: un file cambiato dopo l'avvio del processo (il git pull della macchina mentre il bot partiva) vuol dire che in
    memoria può esserci la versione di prima: all'avvio non è un commit riconoscibile, anche se ora è uguale a HEAD."""
    primo = _repo(tmp_path)
    avvio = time.time() - 60
    assert cv.codice_approvato(tmp_path, primo, caricati=["research/esclusi.py"], cambiati_dopo=avvio) is None
    os.utime(tmp_path / "research" / "esclusi.py", None)                     # toccato adesso, contenuto uguale al commit
    assert cv.codice_approvato(tmp_path, primo, caricati=["research/esclusi.py"]) is None
    assert "dopo l'avvio" in cv.codice_approvato(tmp_path, primo, caricati=["research/esclusi.py"], cambiati_dopo=avvio)
    _invecchia(tmp_path)
    os.utime(tmp_path / "bot" / "risk" / "c.py", None)                       # anche un file del percorso non caricato
    assert "bot/risk/c.py" in cv.codice_approvato(tmp_path, primo, cambiati_dopo=avvio)
    assert 0 < cv.avvio_del_processo() <= time.time()


def test_l_agente_della_macchina_non_porta_piu_nessun_tag():
    """12 novembre 2026: la versione approvata sta su Firebase; l'agente della macchina non scarica e non sposta tag (un tag lo
    sposta qualunque sessione). Il commit approvato è quello che il bot stava eseguendo: nel repository della macchina c'è già."""
    from scripts import ops_agent as oa
    assert not hasattr(oa, "porta_il_tag") and not hasattr(oa, "TAG_CONTO_VERO")
    testo = (RADICE / "scripts" / "ops_agent.py").read_text(encoding="utf-8")
    assert "refs/tags" not in testo and "conto-vero-approvato" not in testo
    for f in ("bot/portafoglio/conto_vero.py", "bot/main.py", "bot/config.py"):
        assert "conto-vero-approvato" not in (RADICE / f).read_text(encoding="utf-8"), f


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
    alla mezzanotte; resta fermo finché non arriva un «riparti» nuovo in due passi dalla dashboard (la conferma del fermo di prima
    non vale: il fermo dello stato perso ha la sua ora)."""
    finto = _Vero()
    finto.equity, finto.posizioni_vive = "290", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    _fino_alla_decisione_dopo(d, tmp_path)
    d.tick(DOPO + 3700)
    fb.set_rtdb(cv.COMANDO_CHIUDI, True)
    d.tick(DOPO + 3800)
    assert d.carica()["fermo"]["motivo"] == "pulsante della dashboard"
    conferma_di_prima = _conferma_della_dashboard(fb)
    for k in range(3):
        d.tick(DOPO + 3900 + 60 * k)
    if perdita == "cancellato":                        # il segno dell'accensione resta su Firebase
        (tmp_path / "st.json").unlink()
    else:                                              # illeggibile, e dopo un riavvio con Firebase senza tracce: basta il file
        (tmp_path / "st.json").write_text("{rotto")
        d, fb, _ = _conto(tmp_path, monkeypatch, finto)
        _decisione(tmp_path, GIORNO + 1)
    aperture = len(_aperture(finto))
    fb.proprietario(cv.COMANDO_RIPARTI, True)          # una richiesta e una conferma rimaste da prima: non valgono
    fb.proprietario(cv.COMANDO_RIPARTI_CONFERMA, conferma_di_prima)
    for k in range(3):
        d.tick(DOPO + 4200 + 60 * k)
    _decisione(tmp_path, GIORNO + 2)
    d.tick((GIORNO + 2) * 86400.0 + 400)
    assert len(_aperture(finto)) == aperture
    assert "stato del conto vero perso" in d.carica()["fermo"]["motivo"] and "dashboard" in d.carica()["fermo"]["motivo"]
    assert fb.get_rtdb("/conto_vero/allarmi/stato_perso")
    assert _conferma_della_dashboard(fb) != conferma_di_prima
    fb.proprietario(cv.COMANDO_RIPARTI, True)          # la conferma del fermo di prima, anche con una richiesta nuova: niente
    fb.proprietario(cv.COMANDO_RIPARTI_CONFERMA, conferma_di_prima)
    d.tick((GIORNO + 2) * 86400.0 + 460)
    assert d.carica().get("fermo")
    _riparti_in_due_passi(fb)
    d.tick((GIORNO + 2) * 86400.0 + 520)
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


def _fermo_e_vuoto(tmp_path, monkeypatch):
    """Il conto vero acceso, con una posizione, fermato dal comando a file e già vuoto: pronto per il «riparti»."""
    finto = _Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    _fino_alla_decisione_dopo(d, tmp_path)
    (tmp_path / "chiudi").write_text("chiudi 1")
    d.tick(DOPO + 120)
    d.tick(DOPO + 180)
    assert d.carica()["fermo"].get("vuoto")
    return d, fb, finto


@pytest.mark.parametrize("cosa", ["solo_richiesta", "solo_conferma", "conferma_sbagliata", "conferma_numero",
                                  "richiesta_non_booleana", "file", "comando_del_demo"])
def test_riparti_senza_la_conferma_giusta_non_riaccende(tmp_path, monkeypatch, cosa):
    """«Riparti» in due passi (il proprietario, 12 novembre 2026): la richiesta da sola, la conferma da sola, una conferma che non è
    il testo esatto di questo fermo, un file del repository o il comando del demo non riaccendono il conto vero; la richiesta resta
    dov'è (la dashboard mostra il secondo passo). Poi i due passi giusti sì."""
    d, fb, finto = _fermo_e_vuoto(tmp_path, monkeypatch)
    giusta = _conferma_della_dashboard(fb)
    assert giusta == cv.codice_riparti(d.carica()["fermo"]) and re.fullmatch(r"[0-9]{10}", giusta)
    if cosa == "solo_richiesta":
        fb.proprietario(cv.COMANDO_RIPARTI, True)
    elif cosa == "solo_conferma":
        fb.proprietario(cv.COMANDO_RIPARTI_CONFERMA, giusta)
    elif cosa == "conferma_sbagliata":
        fb.proprietario(cv.COMANDO_RIPARTI, True)
        fb.proprietario(cv.COMANDO_RIPARTI_CONFERMA, str(int(giusta) - 1))
    elif cosa == "conferma_numero":                    # il numero, non il testo
        fb.proprietario(cv.COMANDO_RIPARTI, True)
        fb.proprietario(cv.COMANDO_RIPARTI_CONFERMA, int(giusta))
    elif cosa == "richiesta_non_booleana":
        fb.proprietario(cv.COMANDO_RIPARTI, "true")
        fb.proprietario(cv.COMANDO_RIPARTI_CONFERMA, giusta)
    elif cosa == "file":                               # nemmeno se qualcuno rimette un file alla classe
        d.file_riparti = tmp_path / "riparti"
        d.file_riparti.write_text("riparti 1")
    else:
        fb.proprietario(dm.COMANDO_RIPARTI, True)
    prima = (fb.get_rtdb(cv.COMANDO_RIPARTI), fb.get_rtdb(cv.COMANDO_RIPARTI_CONFERMA))
    for k in range(3):
        d.tick(DOPO + 240 + 60 * k)
    assert d.carica().get("fermo") and fb.get_rtdb("/conto_vero/fermo")
    assert (fb.get_rtdb(cv.COMANDO_RIPARTI), fb.get_rtdb(cv.COMANDO_RIPARTI_CONFERMA)) == prima     # niente consumato
    _riparti_in_due_passi(fb)
    d.tick(DOPO + 600)
    assert "fermo" not in d.carica()


def test_riparti_in_due_passi_riaccende_una_volta_sola(tmp_path, monkeypatch):
    """Con la richiesta e la conferma giuste il conto riparte (e riapre alla decisione di G1 dopo); la richiesta si consuma e la
    conferma si toglie; a un secondo fermo la conferma del primo non vale più. Se la richiesta non si può consumare su Firebase,
    niente «riparti» (come il demo)."""
    d, fb, finto = _fermo_e_vuoto(tmp_path, monkeypatch)
    prima = _conferma_della_dashboard(fb)
    _riparti_in_due_passi(fb)
    fb.scritture_ferme = True                          # la richiesta non si consuma: non si riparte
    d.tick(DOPO + 240)
    assert d.carica().get("fermo")
    fb.scritture_ferme = False
    d.tick(DOPO + 300)
    assert "fermo" not in d.carica() and fb.get_rtdb("/conto_vero/fermo") is None
    assert fb.get_rtdb(cv.COMANDO_RIPARTI) is False and fb.get_rtdb(cv.COMANDO_RIPARTI_CONFERMA) is None
    aperture = len(_aperture(finto))
    _decisione(tmp_path, GIORNO + 2)
    t = (GIORNO + 2) * 86400.0 + 400
    d.tick(t)
    assert {q["symbol"] for q in _aperture(finto)[aperture:]} == {"AUSDT", "BUSDT"}
    (tmp_path / "chiudi").write_text("chiudi 2")       # un secondo fermo
    d.tick(t + 120)
    d.tick(t + 180)
    assert d.carica()["fermo"].get("vuoto")
    seconda = _conferma_della_dashboard(fb)
    assert seconda != prima
    fb.proprietario(cv.COMANDO_RIPARTI, True)
    fb.proprietario(cv.COMANDO_RIPARTI_CONFERMA, prima)
    d.tick(t + 240)
    assert d.carica().get("fermo")                     # la conferma del fermo di prima non riaccende
    fb.proprietario(cv.COMANDO_RIPARTI_CONFERMA, seconda)
    d.tick(t + 300)
    assert "fermo" not in d.carica()


def test_all_entrata_nel_fermo_la_richiesta_di_prima_si_toglie(tmp_path, monkeypatch):
    """Una richiesta di «riparti» rimasta vera da prima del fermo si rimette a falso (e la conferma si toglie) all'entrata nel
    fermo; finché quelle scritture non sono confermate il «riparti» non si accetta."""
    finto = _Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    _fino_alla_decisione_dopo(d, tmp_path)
    fb.proprietario(cv.COMANDO_RIPARTI, True)
    fb.proprietario(cv.COMANDO_RIPARTI_CONFERMA, "1234567890")
    fb.scritture_ferme = True
    (tmp_path / "chiudi").write_text("chiudi 1")
    d.tick(DOPO + 120)
    assert d.carica()["fermo"]["riparti_pulito"] is False
    fb.proprietario(cv.COMANDO_RIPARTI_CONFERMA, cv.codice_riparti(d.carica()["fermo"]))   # la conferma giusta, ma non è pulito
    d.tick(DOPO + 180)
    assert d.carica().get("fermo")
    fb.scritture_ferme = False
    d.tick(DOPO + 240)                                 # adesso si pulisce: richiesta e conferma di prima tolte
    assert d.carica()["fermo"]["riparti_pulito"] is True
    assert fb.get_rtdb(cv.COMANDO_RIPARTI) is False and fb.get_rtdb(cv.COMANDO_RIPARTI_CONFERMA) is None
    d.tick(DOPO + 300)
    assert d.carica().get("fermo")


def test_il_codice_del_riparti_e_l_ora_del_fermo_in_secondi_interi():
    assert cv.codice_riparti({"ora": 1794480123.987}) == "1794480123" and cv.codice_riparti({"ora": 1794480123}) == "1794480123"
    for senza in (None, {}, {"ora": None}, {"ora": "ieri"}, {"ora": 0}, {"ora": -5.0}, {"ora": float("nan")}, {"ora": float("inf")},
                  "fermo"):
        assert cv.codice_riparti(senza) is None, senza


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
    fb = _Fb()
    fb.proprietario("/conto_vero/acceso_dal", {"ora": 1.0, "compra_alla_decisione_di_g1_dopo_il": "2026-10-24"})
    fb.muto = True
    d = cv.ContoVeroG1(fb, file_stato=tmp_path / "st.json", interruttore=tmp_path / "acceso", verifica_codice=lambda: None)
    assert d._acceso_su_firebase() is None and d._mai_acceso_detto_da_firebase() is False
    fb.muto = False
    assert d._acceso_su_firebase()["ora"] == 1.0 and d._mai_acceso_detto_da_firebase() is True
    mai = cv.ContoVeroG1(_Fb(), file_stato=tmp_path / "st2.json", interruttore=tmp_path / "acceso", verifica_codice=lambda: None)
    assert mai._acceso_su_firebase() is None and mai._mai_acceso_detto_da_firebase() is True    # ha risposto: mai acceso
    senza = cv.ContoVeroG1(_InMemoryStore(), file_stato=tmp_path / "st3.json", interruttore=tmp_path / "acceso",
                           verifica_codice=lambda: None)
    assert senza._mai_acceso_detto_da_firebase() is False     # un client che non sa dire se ha risposto: non si sa


def test_66_stato_perso_e_firebase_muto_al_primo_giro_non_si_riarma(tmp_path, monkeypatch):
    """Problema 66 (prova r1 della revisione dell'8 novembre 2026): pulsante, conto vuoto, file di stato perso, riavvio con Firebase
    muto proprio al primo giro. Prima il conto si riarmava subito e alla mezzanotte comprava senza «riparti»; ora niente prima
    accensione finché Firebase non risponde, e quando risponde il conto è fermo e aspetta il «riparti»."""
    finto = _Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    _fino_alla_decisione_dopo(d, tmp_path)
    fb.set_rtdb(cv.COMANDO_CHIUDI, True)
    d.tick(DOPO + 120)
    d.tick(DOPO + 180)
    assert d.carica()["fermo"].get("vuoto")
    (tmp_path / "st.json").unlink()                    # lo stato si perde...
    aperture = len(_aperture(finto))
    riavviato = _Fb(vero=fb.vero)                      # ...e il bot riparte: lo stesso database, lo specchio vuoto
    riavviato.muto = True
    d2, _, _ = _conto(tmp_path, monkeypatch, finto, fb=riavviato)
    _decisione(tmp_path, GIORNO + 1)
    d2.tick(DOPO + 300)
    st = d2.carica()
    assert not st.get("acceso_dal") and not st.get("fermo")
    assert "Firebase non risponde" in st["allarmi"]["ordini_vietati"] and "già stato acceso" in st["allarmi"]["ordini_vietati"]
    d2.tick(DOPO + 360)                                # ancora muto: ancora niente
    assert not d2.carica().get("acceso_dal")
    riavviato.muto = False
    d2.tick(DOPO + 420)
    assert "stato del conto vero perso" in d2.carica()["fermo"]["motivo"]
    _decisione(tmp_path, GIORNO + 2)
    d2.tick((GIORNO + 2) * 86400.0 + 400)
    assert len(_aperture(finto)) == aperture           # senza «riparti» non compra
    _riparti_in_due_passi(riavviato)
    d2.tick((GIORNO + 2) * 86400.0 + 460)
    assert "fermo" not in d2.carica()
    _decisione(tmp_path, GIORNO + 3)
    d2.tick((GIORNO + 3) * 86400.0 + 400)
    assert {q["symbol"] for q in _aperture(finto)[aperture:]} == {"AUSDT", "BUSDT"}


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


def test_73_l_errore_di_creazione_arriva_su_firebase(capsys):
    """Revisione dell'8 novembre 2026, problema 73: l'errore di creazione non resta solo nel log. Va in
    `/conto_vero/allarmi/creazione` (la dashboard e lo stato lo mostrano fra gli allarmi del conto vero): si riscrive finché la
    scrittura non è confermata, poi una volta per errore diverso, e si toglie alla prima creazione riuscita."""
    class Rotto:
        errore = "git non risponde"

        def __init__(self, fb):
            raise RuntimeError(self.errore)

    class Buono:
        def __init__(self, fb):
            self.fb = fb
    cv._ULTIMO_ERRORE_DI_CREAZIONE[0] = cv._ERRORE_DI_CREAZIONE_SCRITTO[0] = None
    fb = _Fb()
    fb.scritture_ferme = True                          # Firebase non prende la prima scrittura
    assert cv.crea_conto_vero(fb, classe=Rotto) is None
    assert fb.get_rtdb(cv.ALLARME_DI_CREAZIONE) is None
    fb.scritture_ferme = False
    assert cv.crea_conto_vero(fb, classe=Rotto) is None                       # al giro dopo arriva
    allarme = fb.get_rtdb("/conto_vero/allarmi/creazione")
    assert "non è stato creato" in allarme["testo"] and "RuntimeError: git non risponde" in allarme["testo"] and allarme["ora"] > 0
    scritture = len(fb.scritti)
    for _ in range(3):
        assert cv.crea_conto_vero(fb, classe=Rotto) is None
    assert len(fb.scritti) == scritture                                       # lo stesso errore: una volta sola
    assert capsys.readouterr().out.count("ERRORE nella creazione") == 1
    Rotto.errore = "un altro errore"
    assert cv.crea_conto_vero(fb, classe=Rotto) is None
    assert "un altro errore" in fb.get_rtdb(cv.ALLARME_DI_CREAZIONE)["testo"]
    assert isinstance(cv.crea_conto_vero(fb, classe=Buono), Buono)
    assert fb.get_rtdb(cv.ALLARME_DI_CREAZIONE) is None                       # creato: l'allarme si toglie
    assert cv.crea_conto_vero(None, classe=Rotto) is None                     # senza Firebase non si rompe
    cv._ULTIMO_ERRORE_DI_CREAZIONE[0] = cv._ERRORE_DI_CREAZIONE_SCRITTO[0] = None


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
        "/conto_vero/allarmi": {"ordini_vietati": {"ora": 1.7e9, "testo": "niente ordini nuovi: nessuna versione approvata"}},
        "/conto_vero/fermo": {"ora": 1.7e9, "motivo": "pulsante della dashboard", "chiuse": 38}})))
    assert "$290.00" in acceso and "$182.00" in acceso and "20 long, 18 short" in acceso
    assert "**ALLARME** ordini vietati" in acceso and "nessuna versione approvata" in acceso and "**FERMO**" in acceso
    # problema 73: l'allarme della creazione si vede anche quando il conto vero non ha mai scritto uno stato
    mai_creato = "\n".join(ss.sezione_conto_vero(Fb({"/conto_vero/allarmi": {
        "creazione": {"ora": 1.7e9, "testo": "il conto vero non è stato creato e non gira: RuntimeError: git non risponde"}}})))
    assert "nessuno stato scritto" in mai_creato and "**ALLARME** creazione" in mai_creato and "git non risponde" in mai_creato
    assert "sezione_conto_vero(fb)" in (RADICE / "scripts" / "state_snapshot.py").read_text(encoding="utf-8")


# ---- la versione approvata dal proprietario su Firebase (12 novembre 2026), con il controllo vero e un repository di prova ----
def _approva(fb, commit):
    """Quello che fa il pulsante «Approva questa versione» della dashboard, con l'accesso del proprietario."""
    fb.proprietario(cv.COMANDO_VERSIONE, {"commit": commit, "ora": 1.7e12})


@pytest.mark.parametrize("caso", ["assente", "non_valida", "non_nel_repository", "diversa", "caricato_diverso", "uguale",
                                  "uguale_nei_file"])
def test_gli_ordini_partono_solo_con_la_versione_approvata_dal_proprietario(tmp_path, monkeypatch, caso):
    """La condizione (c) con il controllo vero: il commit approvato su Firebase assente, non valido, non presente nel repository
    della macchina o diverso dal codice in esecuzione → nessun ordine e il motivo scritto; uguale (anche solo nei file del codice)
    → gli ordini partono. In `/conto_vero/versione` il commit in esecuzione, quello approvato letto e se coincidono."""
    repo = tmp_path / "repo"
    primo = _repo(repo)
    testa = primo
    if caso in ("diversa", "caricato_diverso", "uguale_nei_file"):
        testa = _commit(repo, {{"diversa": "bot/risk/c.py", "caricato_diverso": "research/esclusi.py",
                                "uguale_nei_file": "docs/note.md"}[caso]: "x = 2\n"}, "secondo commit di prova")
    if caso == "caricato_diverso":                     # un file fuori dai percorsi degli ordini, ma caricato nel processo
        modulo = types.ModuleType("_prova_esclusi")
        modulo.__file__ = str(repo / "research" / "esclusi.py")
        monkeypatch.setitem(sys.modules, "_prova_esclusi", modulo)
    d, fb, finto = _conto(tmp_path, monkeypatch, radice=repo)
    approvata = {"assente": None, "non_valida": testa[:39] + "G", "non_nel_repository": "0123456789abcdef0123456789abcdef01234567",
                 "uguale": testa}.get(caso, primo)
    if approvata:
        _approva(fb, approvata)
    _fino_alla_decisione_dopo(d, tmp_path)
    versione = fb.get_rtdb("/conto_vero/versione")
    assert versione["commit"] == testa and versione["pulito"] is True and versione["data"].startswith("20")
    assert versione["titolo"] == ("primo commit di prova" if testa == primo else "secondo commit di prova")
    assert cv.COMANDO_VERSIONE not in fb.scritti       # il bot la legge soltanto
    if caso in ("uguale", "uguale_nei_file"):
        assert {q["symbol"] for q in _aperture(finto)} == {"AUSDT", "BUSDT"}
        assert fb.get_rtdb("/conto_vero/allarmi/ordini_vietati") is None
        assert versione["approvata"] == approvata and versione["coincidono"] is True and "blocco" not in versione
        return
    assert _scritture(finto) == []
    testo = fb.get_rtdb("/conto_vero/allarmi/ordini_vietati")["testo"]
    atteso = {"assente": "nessuna versione approvata dal proprietario", "non_valida": "non è valida",
              "non_nel_repository": "non è un commit del repository della macchina",
              "diversa": "bot/risk/c.py", "caricato_diverso": "research/esclusi.py"}[caso]
    assert "niente ordini nuovi" in testo and atteso in testo
    assert versione["coincidono"] is False and atteso in versione["blocco"]
    assert versione.get("approvata") == (approvata if caso in ("non_nel_repository", "diversa", "caricato_diverso") else None)
    # il proprietario approva la versione in esecuzione dalla dashboard: senza riavvio, dal minuto dopo; si compra alla mezzanotte
    _approva(fb, testa)
    d.tick(DOPO + 7200)
    assert fb.get_rtdb("/conto_vero/allarmi/ordini_vietati") is None and _scritture(finto) == []
    assert fb.get_rtdb("/conto_vero/versione")["coincidono"] is True and fb.get_rtdb("/conto_vero/versione")["approvata"] == testa
    _decisione(tmp_path, GIORNO + 2)
    d.tick((GIORNO + 2) * 86400.0 + 400)
    assert {q["symbol"] for q in _aperture(finto)} == {"AUSDT", "BUSDT"}
    assert cv.COMANDO_VERSIONE not in fb.scritti


def test_un_commit_nuovo_dopo_l_avvio_ferma_gli_ordini_fino_al_riavvio_e_all_approvazione(tmp_path, monkeypatch):
    """La macchina scarica un commit che tocca il codice mentre il bot gira la versione approvata: niente ordini nuovi. Approvare
    il commit nuovo senza riavviare non basta (il processo esegue ancora il vecchio); dopo il riavvio la versione in esecuzione è
    quella nuova e, approvata, gli ordini ripartono."""
    repo = tmp_path / "repo"
    primo = _repo(repo)
    finto = _Vero()
    finto.equity = "280"
    d, fb, finto = _conto(tmp_path, monkeypatch, finto, radice=repo)
    _approva(fb, primo)
    _fino_alla_decisione_dopo(d, tmp_path)
    assert len(_aperture(finto)) == 2
    nuovo = _commit(repo, {"bot/portafoglio/a.py": "x = 2\n"}, "codice nuovo")
    d.tick(DOPO + 7200)
    testo = fb.get_rtdb("/conto_vero/allarmi/ordini_vietati")["testo"]
    assert "bot/portafoglio/a.py" in testo and "diversi dalla versione approvata" in testo
    versione = fb.get_rtdb("/conto_vero/versione")
    assert versione["commit"] == primo and versione["coincidono"] is False       # in esecuzione c'è ancora il primo
    _approva(fb, nuovo)                                # approvato il nuovo, ma il processo non è stato riavviato
    d.tick(DOPO + 7300)
    testo = fb.get_rtdb("/conto_vero/allarmi/ordini_vietati")["testo"]
    assert "il processo esegue il commit" in testo and "serve un riavvio" in testo
    _decisione(tmp_path, GIORNO + 2)
    d.tick((GIORNO + 2) * 86400.0 + 400)
    assert len(_aperture(finto)) == 2                  # nessun ordine nuovo
    d2, _, _ = _conto(tmp_path, monkeypatch, finto, fb=fb, radice=repo)          # il riavvio
    _decisione(tmp_path, GIORNO + 2)
    d2.tick((GIORNO + 2) * 86400.0 + 460)
    versione = fb.get_rtdb("/conto_vero/versione")
    assert versione["commit"] == nuovo and versione["titolo"] == "codice nuovo" and versione["coincidono"] is True
    assert fb.get_rtdb("/conto_vero/allarmi/ordini_vietati") is None
    _decisione(tmp_path, GIORNO + 3)
    d2.tick((GIORNO + 3) * 86400.0 + 400)
    assert {q["symbol"] for q in _aperture(finto)[2:]} == {"AUSDT", "BUSDT"}


def test_avvio_con_file_diversi_dal_commit_non_si_puo_approvare(tmp_path, monkeypatch):
    """Se all'avvio i file non sono quelli di HEAD (un file modificato e non committato, o cambiato dopo l'avvio del processo) quello
    che gira non è un commit: niente ordini anche con HEAD approvato, finché non si riavvia; la dashboard lo vede (`pulito` falso)."""
    repo = tmp_path / "repo"
    primo = _repo(repo)
    (repo / "bot" / "main.py").write_text("x = 99\n")
    _invecchia(repo)
    d, fb, finto = _conto(tmp_path, monkeypatch, radice=repo)
    _approva(fb, primo)
    (repo / "bot" / "main.py").write_text("x = 1\n")   # dopo, i file tornano uguali: non basta
    _fino_alla_decisione_dopo(d, tmp_path)
    assert _scritture(finto) == []
    testo = fb.get_rtdb("/conto_vero/allarmi/ordini_vietati")["testo"]
    assert "serve un riavvio" in testo and "bot/main.py" in testo
    versione = fb.get_rtdb("/conto_vero/versione")
    assert versione["commit"] == primo and versione["pulito"] is False and "bot/main.py" in versione["motivo"]
    assert versione["coincidono"] is False


def test_la_versione_si_pubblica_anche_da_spento_senza_richieste_a_binance(tmp_path, monkeypatch):
    """Spento (senza interruttore, `DRY_RUN` vero): la dashboard vede lo stesso la versione in esecuzione e se è approvata, così il
    proprietario la approva prima dell'accensione; nessuna richiesta a Binance. Si riscrive solo quando cambia, e finché la
    scrittura non è arrivata."""
    repo = tmp_path / "repo"
    primo = _repo(repo)
    fb = _Fb()
    fb.scritture_ferme = True
    d, fb, finto = _conto(tmp_path, monkeypatch, acceso=False, dry_run="true", fb=fb, radice=repo)
    d.tick(MEZZOGIORNO)
    assert fb.get_rtdb("/conto_vero/versione") is None
    fb.scritture_ferme = False
    d.tick(MEZZOGIORNO + 60)
    versione = fb.get_rtdb("/conto_vero/versione")
    assert versione["commit"] == primo and versione["pulito"] is True and versione["coincidono"] is False
    assert "nessuna versione approvata" in versione["blocco"] and "approvata" not in versione
    scritture = fb.scritti.count("/conto_vero/versione")
    for k in range(2, 6):
        d.tick(MEZZOGIORNO + 60 * k)
    assert fb.scritti.count("/conto_vero/versione") == scritture             # niente di nuovo: non si riscrive
    _approva(fb, primo)
    d.tick(MEZZOGIORNO + 400)
    assert "approvata" not in fb.get_rtdb("/conto_vero/versione")             # da spento si rilegge ogni 10 minuti (problema 75)
    d.tick(MEZZOGIORNO + 660)
    versione = fb.get_rtdb("/conto_vero/versione")
    assert versione["approvata"] == primo and versione["coincidono"] is True and "blocco" not in versione
    assert finto.chiamate == [] and cv.COMANDO_VERSIONE not in fb.scritti


def test_firebase_muto_niente_ordini_nuovi_anche_con_l_approvazione_nello_specchio(tmp_path, monkeypatch):
    """Se Firebase non risponde non è mai «approvato»: l'ultima approvazione letta (ancora nello specchio in memoria) non vale e
    alla decisione di G1 non parte nessun ordine; dopo tre controlli l'allarme. Quando Firebase torna, l'allarme si spegne e il
    conto ricompra alla decisione di G1 dopo."""
    repo = tmp_path / "repo"
    primo = _repo(repo)
    finto = _Vero()
    finto.equity = "280"
    d, fb, finto = _conto(tmp_path, monkeypatch, finto, radice=repo)
    _approva(fb, primo)
    d.tick(MEZZOGIORNO)
    d.tick(MEZZOGIORNO + 3700)
    assert fb.get_rtdb("/conto_vero/versione")["coincidono"] is True
    fb.muto = True
    assert fb.get_rtdb(cv.COMANDO_VERSIONE)["commit"] == primo               # l'ultimo valore noto è ancora quello approvato
    _decisione(tmp_path, GIORNO + 1)
    d.tick(DOPO)
    assert _scritture(finto) == []
    allarmi = d.carica()["allarmi"]
    assert "Firebase non risponde" in allarmi["ordini_vietati"] and "versione_approvata" not in allarmi
    d.tick(DOPO + 60)
    assert "versione_approvata" not in d.carica()["allarmi"]
    d.tick(DOPO + 120)                                 # il terzo controllo senza risposta: l'allarme
    assert "Firebase non risponde da almeno 3 controlli" in d.carica()["allarmi"]["versione_approvata"]
    assert _scritture(finto) == []
    fb.muto = False
    d.tick(DOPO + 180)
    assert "versione_approvata" not in d.carica()["allarmi"] and "ordini_vietati" not in d.carica()["allarmi"]
    assert fb.get_rtdb("/conto_vero/allarmi/versione_approvata") is None and _scritture(finto) == []
    _decisione(tmp_path, GIORNO + 2)
    d.tick((GIORNO + 2) * 86400.0 + 400)
    assert {q["symbol"] for q in _aperture(finto)} == {"AUSDT", "BUSDT"}


def test_una_sola_lettura_persa_della_versione_si_riprova_subito(tmp_path, monkeypatch):
    """Una lettura persa capita: il controllo riprova una volta, subito, e non ferma gli ordini per quella. Problema 75: se la
    prima lettura ha aspettato oltre ``SECONDA_LETTURA_ENTRO_S`` la seconda non si fa (Firebase che non risponde allunga il giro)."""
    repo = tmp_path / "repo"
    primo = _repo(repo)
    d, fb, finto = _conto(tmp_path, monkeypatch, radice=repo)
    d.orologio = lambda: 1.0e9                         # l'ultima risposta vera è appena letta, ma qui conta la seconda lettura:
    vera, perse, letture = fb.leggi_rtdb_davvero, [1], []
    _approva(fb, primo)

    def con_perse(percorso):
        letture.append(percorso)
        if percorso == cv.COMANDO_VERSIONE and perse:
            perse.pop()
            return False, None
        return vera(percorso)
    fb.leggi_rtdb_davvero = con_perse
    assert d._verifica_codice() is None and perse == [] and d._versione_muta == 0 and len(letture) == 2
    secondi = iter([0.0, 30.0])                        # la prima lettura persa dura 30 s: niente seconda
    d.cronometro = lambda: next(secondi)
    perse.append(1)
    letture.clear()
    assert d._verifica_codice() is None and len(letture) == 1 and d._versione_muta == 1     # vale l'approvazione appena letta
    assert perse == []


def test_74_un_buco_di_firebase_nel_minuto_della_decisione_non_salta_il_giorno(tmp_path, monkeypatch):
    """Problema 74, prova S1 della revisione del 12 novembre 2026: conto acceso e approvato, Firebase muto proprio nel minuto della
    decisione di G1 (due letture perse), poi di nuovo vivo: gli ordini partono lo stesso giorno, perché vale l'approvazione letta
    davvero un minuto prima (con il confronto di git). Prima: zero ordini quel giorno e si ricomprava il giorno dopo."""
    repo = tmp_path / "repo"
    primo = _repo(repo)
    finto = _Vero()
    finto.equity = "280"
    d, fb, finto = _conto(tmp_path, monkeypatch, finto, radice=repo)
    _approva(fb, primo)
    d.tick(MEZZOGIORNO)
    d.tick(MEZZOGIORNO + 3700)
    d.tick(DOPO - 60)                                  # il giro del minuto prima: Firebase risponde
    _decisione(tmp_path, GIORNO + 1)
    fb.muto = True
    d.tick(DOPO)
    assert d._versione_muta == 1 and {q["symbol"] for q in _aperture(finto)} == {"AUSDT", "BUSDT"}
    assert "ordini_vietati" not in d.carica().get("allarmi", {})
    assert fb.get_rtdb("/conto_vero/ribilanciamenti/2026-10-25")["ordini"] == 2


def test_74_un_buco_di_firebase_allo_scadere_dell_ora_non_lascia_il_ribilancio_a_meta(tmp_path, monkeypatch):
    """Problema 74, prova S2: Firebase muto nel minuto in cui scade l'ora degli ordini limite: il resto va a mercato come sempre
    (prima: ordini limite annullati e niente resto a mercato, un lato eseguito e l'altro no fino al giorno dopo)."""
    repo = tmp_path / "repo"
    primo = _repo(repo)
    finto = _Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto, radice=repo)
    _approva(fb, primo)
    _fino_alla_decisione_dopo(d, tmp_path)             # AUSDT eseguito a limite, BUSDT sul libro
    piazzati = d.carica()["ordini"]["piazzati"]
    for k in range(1, 60):                             # un giro al minuto per l'ora degli ordini limite, Firebase vivo
        d.tick(piazzati + 60 * k)
    assert d.carica().get("ordini")
    fb.muto = True                                     # muto proprio nel minuto in cui l'ora scade
    n = len(finto.chiamate)
    d.tick(piazzati + dm.VALIDITA_LIMITE_S)
    mercato = [q for m, p, q in finto.chiamate[n:] if m == "POST" and q.get("type") == "MARKET"]
    assert [(q["symbol"], q.get("reduceOnly")) for q in mercato] == [("BUSDT", None)]
    assert "ordini" not in d.carica() and not [p for p in fb.scritti if p.endswith("scaduti_senza_mercato")]


def test_74_oltre_dieci_minuti_senza_risposta_o_con_la_revoca_niente_ordini(tmp_path, monkeypatch):
    """L'approvazione letta vale senza risposta solo fino a ``APPROVAZIONE_SENZA_RISPOSTA_S``; una risposta vera senza
    approvazione (revocata dal proprietario) vale subito, e dopo la revoca il buco di Firebase non riporta la vecchia; il
    confronto di git si fa anche con l'approvazione ricordata."""
    assert cv.APPROVAZIONE_SENZA_RISPOSTA_S == 600 and cv.SECONDA_LETTURA_ENTRO_S == 5.0
    repo = tmp_path / "repo"
    primo = _repo(repo)
    d, fb, finto = _conto(tmp_path, monkeypatch, radice=repo)
    ora = [1.0e9]
    d.orologio = lambda: ora[0]
    _approva(fb, primo)
    assert d._verifica_codice() is None
    fb.muto = True
    ora[0] += 600
    assert d._verifica_codice() is None and d._approvata == primo
    (repo / "bot" / "risk" / "c.py").write_text("x = 2\n")      # i file cambiano durante il buco: git lo vede lo stesso
    assert "bot/risk/c.py" in d._verifica_codice()
    (repo / "bot" / "risk" / "c.py").write_text("x = 1\n")
    ora[0] += 1
    motivo = d._verifica_codice()
    assert "Firebase non risponde" in motivo and "oltre 10 minuti" in motivo and d._approvata is None
    fb.muto = False
    assert d._verifica_codice() is None
    fb.proprietario(cv.COMANDO_VERSIONE, None)          # revocata
    assert "nessuna versione approvata" in d._verifica_codice()
    fb.muto = True
    ora[0] += 1
    assert "Firebase non risponde" in d._verifica_codice()     # il buco non riporta l'approvazione revocata


def test_75_da_spento_la_versione_si_controlla_ogni_dieci_minuti_e_all_accensione_subito(tmp_path, monkeypatch):
    """Problema 75: da spento niente ordini sono possibili, la versione serve solo alla dashboard: un controllo ogni 10 minuti; tolto
    lo spento, il controllo si fa al giro dopo, senza aspettare. Con Firebase muto `/conto_vero/versione` non si riscrive."""
    repo = tmp_path / "repo"
    primo = _repo(repo)
    d, fb, finto = _conto(tmp_path, monkeypatch, acceso=False, radice=repo)
    letture = []
    vera = fb.leggi_rtdb_davvero
    fb.leggi_rtdb_davvero = lambda p: (letture.append(p), vera(p))[1]
    for k in range(10):
        d.tick(MEZZOGIORNO + 60 * k)
    assert letture.count(cv.COMANDO_VERSIONE) == 1
    d.tick(MEZZOGIORNO + 600)
    assert letture.count(cv.COMANDO_VERSIONE) == 2
    (tmp_path / "conto_vero_acceso").write_text("si")
    d.tick(MEZZOGIORNO + 630)                          # acceso: subito, anche se sono passati 30 secondi
    assert letture.count(cv.COMANDO_VERSIONE) == 3
    d.tick(MEZZOGIORNO + 660)
    assert letture.count(cv.COMANDO_VERSIONE) == 3
    d.tick(MEZZOGIORNO + 690)
    assert letture.count(cv.COMANDO_VERSIONE) == 4     # acceso: ogni minuto
    _approva(fb, primo)
    fb.muto = True
    scritte = fb.scritti.count("/conto_vero/versione")
    d.tick(MEZZOGIORNO + 750)
    assert fb.scritti.count("/conto_vero/versione") == scritte


def test_76_il_fermo_si_riscrive_finche_non_arriva_e_il_riparti_si_puo_fare(tmp_path, monkeypatch):
    """Problema 76, prova S3: le scritture si perdono mentre il conto entra nel fermo e si svuota; tornato Firebase, il fermo arriva
    al primo giro (prima restava solo nel file: la dashboard non mostrava né il fermo né il «Riparti», senza uscita) e il «riparti»
    in due passi funziona. Anche la cancellazione del fermo si riscrive finché non arriva."""
    finto = _Vero()
    finto.equity, finto.posizioni_vive = "280", True
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    _fino_alla_decisione_dopo(d, tmp_path)
    fb.scritture_ferme = True
    (tmp_path / "chiudi").write_text("chiudi 1")
    for k in range(2, 6):
        d.tick(DOPO + 60 * k)
    assert d.carica()["fermo"].get("vuoto") and fb.get_rtdb("/conto_vero/fermo") is None
    fb.scritture_ferme = False
    d.tick(DOPO + 360)
    sul_db = fb.get_rtdb("/conto_vero/fermo")
    assert sul_db and sul_db["ora"] == d.carica()["fermo"]["ora"] and sul_db.get("vuoto")
    _riparti_in_due_passi(fb)
    fb.scritture_ferme = True                          # la cancellazione del fermo dopo il «riparti» si perde...
    d.tick(DOPO + 420)
    assert d.carica().get("fermo")                     # (il «riparti» non si consuma senza scrittura: si riprova)
    fb.scritture_ferme = False
    d.tick(DOPO + 480)
    assert "fermo" not in d.carica() and fb.get_rtdb("/conto_vero/fermo") is None
    fb.scritture_ferme = True
    d._scrivi("fermo", {"ora": 1.0})                   # una scrittura persa...
    fb.scritture_ferme = False
    d.tick(DOPO + 540)
    assert fb.get_rtdb("/conto_vero/fermo") is None    # ...si corregge con lo stato del file (nessun fermo)


def test_77_prima_del_primo_controllo_il_codice_non_vale_approvato(tmp_path, monkeypatch):
    monkeypatch.setattr(cv, "commit_in_esecuzione", lambda radice: {"commit": "a" * 40, "data": "2026-11-12T06:00:00+00:00", "titolo": "t"})
    monkeypatch.setattr(cv, "codice_approvato", lambda **k: None)          # avvio pulito
    d = cv.ContoVeroG1(_Fb(), file_stato=tmp_path / "st.json", interruttore=tmp_path / "acceso")
    assert d._codice_all_avvio is None and d._blocco_del_codice() == "versione approvata non ancora letta"


def test_54_nessun_codice_del_repository_scrive_i_comandi_del_conto_vero():
    """Revisione del 12 novembre 2026, 54 parte ii: la chiave di amministratore di Firebase ignora le regole, e ce l'hanno il bot,
    l'agente della macchina e i flussi di GitHub. Nessun file Python o di shell del repository (fuori dalla dashboard e dai test) e
    nessun flusso di GitHub nomina i quattro comandi del conto vero, salvo il conto vero stesso; lì (e nel demo, da cui eredita) ogni
    scrittura di un comando è il falso o il None che lo consuma, e la versione approvata non si scrive mai. È una guardia contro gli
    errori: chi volesse aggirarla costruendo il percorso a pezzi non lo troverebbe qui (decisione del proprietario, 54)."""
    import ast
    nomi = ("conto_vero_versione_approvata", "conto_vero_riparti", "conto_vero_riparti_conferma", "conto_vero_chiudi_tutto")
    file_ = subprocess.run(["git", "-C", str(RADICE), "ls-files", "--cached", "--others", "--exclude-standard", "--", "*.py", "*.sh",
                            "*.yml", "*.yaml", "*.js", "*.mjs", "*.ts"], capture_output=True, text=True, check=True).stdout.split()
    assert any(f.startswith(".github/workflows/") for f in file_) and "scripts/ops_agent.py" in file_
    trovati = []
    for f in file_:
        if f.startswith(("tests/", "dashboard/")) or f == "bot/portafoglio/conto_vero.py":
            continue
        try:
            testo = (RADICE / f).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        trovati += [f"{f}: {n}" for n in nomi if n in testo]
    assert trovati == []
    # nel conto vero il nome compare solo nelle costanti (e nel file a mano del pulsante)
    testo = (RADICE / "bot" / "portafoglio" / "conto_vero.py").read_text(encoding="utf-8")
    righe = [r.strip() for r in testo.splitlines() if any(n in r for n in nomi) and not r.lstrip().startswith("#")]
    codice = [r for r in righe if not r.startswith(("COMANDO_", "FILE_CHIUDI = ")) and "`" not in r and "«" not in r]
    assert codice == [], codice
    # ogni set_rtdb su un comando, nel conto vero e nel demo: solo False o None, mai la versione approvata
    for f in ("bot/portafoglio/conto_vero.py", "bot/portafoglio/demo_binance.py"):
        albero = ast.parse((RADICE / f).read_text(encoding="utf-8"))
        for nodo in ast.walk(albero):
            if not (isinstance(nodo, ast.Call) and getattr(nodo.func, "attr", None) == "set_rtdb" and nodo.args):
                continue
            dove = ast.unparse(nodo.args[0])
            if "COMANDO" not in dove:
                continue
            assert "VERSIONE" not in dove, (f, dove)
            assert len(nodo.args) == 2 and isinstance(nodo.args[1], ast.Constant) and nodo.args[1].value in (False, None), (f, dove)


def test_72_i_redditi_si_leggono_fino_a_un_minuto_fa(tmp_path, monkeypatch):
    """Revisione dell'8 novembre 2026, problema 72: i redditi si chiedono a Binance fino a ``RITARDO_REDDITI_S`` secondi fa. Una
    riga con l'ora di 30 secondi fa non è ancora chiesta in questo giro (Binance può non averla ancora scritta tutta); entra al
    giro dopo, una volta sola."""
    finto = _Vero()
    finto.equity = "280"
    d, fb, finto = _conto(tmp_path, monkeypatch, finto)
    _fino_alla_decisione_dopo(d, tmp_path)
    t = DOPO + 600
    finto.entrate.append(("FUNDING_FEE", int((t - 30) * 1000), -0.5, "USDT"))
    n = len(finto.chiamate)
    d.tick(t)
    letture = [q for m, p, q in finto.chiamate[n:] if p == "/fapi/v1/income" and "incomeType" not in q]
    assert letture and all(int(q["endTime"]) == int((t - cv.RITARDO_REDDITI_S) * 1000) for q in letture)
    assert d._redditi == 0.0                           # non ancora contata
    d.tick(t + 60)
    assert d._redditi == pytest.approx(-0.5)           # al giro dopo sì
    d.tick(t + 120)
    assert d._redditi == pytest.approx(-0.5)           # e una volta sola


# ---- le regole di Firebase del repository e la dashboard ----
IO = "auth != null && auth.uid === 'REPLACE_WITH_YOUR_FIREBASE_UID'"
SEGNAPOSTO = {"REPLACE_WITH_YOUR_FIREBASE_UID", "REPLACE_WITH_STOCK_FIREBASE_UID"}


def _espressione_regolare(regola: str) -> "re.Pattern":
    """La prima `matches(/.../)` di una regola di Firebase, come espressione regolare di Python."""
    return re.compile(re.search(r"matches\(/(.+?)/\)", regola).group(1))


def test_le_regole_di_firebase_hanno_i_comandi_del_conto_vero_e_nessun_identificativo_vero():
    """`firebase/database.rules.json`: i comandi del conto vero li scrive solo il proprietario, validati; la radice resta chiusa;
    `/azioni` lo scrive solo l'utente delle azioni. Nel repository ci sono solo i due segnaposto, mai un identificativo vero (le
    regole con gli identificativi le pubblica il proprietario dalla console di Firebase)."""
    regole = json.loads((RADICE / "firebase" / "database.rules.json").read_text(encoding="utf-8"))["rules"]
    assert regole[".write"] is False and regole[".read"] == IO
    comandi = regole["commands"]
    for percorso in (cv.COMANDO_CHIUDI, cv.COMANDO_RIPARTI, cv.COMANDO_RIPARTI_CONFERMA, cv.COMANDO_VERSIONE,
                     dm.COMANDO_CHIUDI, dm.COMANDO_RIPARTI):
        assert percorso.startswith("/commands/") and percorso.split("/")[-1] in comandi, percorso
        assert comandi[percorso.split("/")[-1]][".write"].startswith(IO), percorso
    for nome in ("conto_vero_chiudi_tutto", "conto_vero_riparti", "demo_binance_chiudi_tutto", "demo_binance_riparti"):
        assert comandi[nome][".write"] == f"{IO} && newData.isBoolean()", nome
    # la conferma del «riparti»: il testo dell'ora del fermo, e solo con la richiesta già scritta (o per toglierla)
    conferma = comandi["conto_vero_riparti_conferma"][".write"]
    assert "!newData.exists()" in conferma and "newData.isString()" in conferma
    assert "root.child('commands').child('conto_vero_riparti').val() === true" in conferma
    cifre = _espressione_regolare(conferma)
    assert cifre.fullmatch(cv.codice_riparti({"ora": 1794480123.9})) and not cifre.fullmatch("riparti") and not cifre.fullmatch("")
    # la versione approvata: {commit: 40 caratteri esadecimali, ora: numero}, nient'altro
    versione = comandi["conto_vero_versione_approvata"]
    assert versione[".write"] == IO and versione[".validate"] == "newData.hasChildren(['commit', 'ora'])"
    assert versione["$altro"][".validate"] is False and versione["ora"][".validate"] == "newData.isNumber()"
    commit = versione["commit"][".validate"]
    assert "newData.isString()" in commit and "newData.val().length === 40" in commit
    esadecimali = _espressione_regolare(commit)
    buono = "0123456789abcdef0123456789abcdef01234567"
    assert esadecimali.fullmatch(buono) and cv.RE_COMMIT.fullmatch(buono)
    for cattivo in (buono.upper(), buono[:39] + "g", "HEAD~1", buono[:20] + " " + buono[:19]):
        assert not esadecimali.fullmatch(cattivo) and not cv.RE_COMMIT.fullmatch(cattivo), cattivo
    # le azioni: solo l'utente delle azioni scrive sotto /azioni (il blocco pubblicato il 12 novembre 2026)
    assert regole["azioni"] == {".write": "auth != null && auth.uid === 'REPLACE_WITH_STOCK_FIREBASE_UID'"}
    # nessun'altra scrittura aperta: ogni `.write` vero sta sotto /commands o /azioni e nomina un segnaposto
    def scritture(nodo, percorso=""):
        for k, v in nodo.items():
            if k == ".write" and v is not False:
                yield percorso, v
            elif isinstance(v, dict):
                yield from scritture(v, f"{percorso}/{k}")
    for percorso, regola in scritture(regole):
        assert percorso.startswith("/commands/") or percorso == "/azioni", percorso
        assert set(re.findall(r"auth\.uid === '([^']*)'", regola)) & SEGNAPOSTO and "auth != null" in regola, percorso
    for f in ("database.rules.json", "firestore.rules"):
        testo = (RADICE / "firebase" / f).read_text(encoding="utf-8")
        usati = set(re.findall(r"auth\.uid\s*={2,3}\s*'([^']*)'", testo))
        assert usati and usati <= SEGNAPOSTO, (f, usati)
        assert not re.search(r"(?<![A-Za-z0-9])[A-Za-z0-9]{28}(?![A-Za-z0-9])", testo), f    # la forma di un identificativo vero


def test_la_dashboard_scrive_gli_stessi_comandi_che_il_bot_legge():
    """I pulsanti della scheda del conto vero (dashboard/app/components/strategie/ComandiContoVero.tsx) scrivono i percorsi che
    il bot legge e la conferma del «riparti» nel formato che il bot aspetta; il bot pubblica la versione dove la dashboard la legge."""
    comandi = (RADICE / "dashboard" / "app" / "components" / "strategie" / "ComandiContoVero.tsx").read_text(encoding="utf-8")
    for percorso in (cv.COMANDO_CHIUDI, cv.COMANDO_RIPARTI, cv.COMANDO_RIPARTI_CONFERMA, cv.COMANDO_VERSIONE):
        assert f"'{percorso.lstrip('/')}'" in comandi, percorso
    assert "String(Math.floor(" in comandi             # `codice_riparti`: l'ora del fermo in secondi interi, come testo
    assert dm.COMANDO_RIPARTI.lstrip("/") not in comandi and dm.COMANDO_CHIUDI.lstrip("/") not in comandi
    letture = (RADICE / "dashboard" / "app" / "lib" / "strategie.ts").read_text(encoding="utf-8")
    for ramo in ("conto_vero/versione", cv.COMANDO_VERSIONE.lstrip("/"), cv.COMANDO_RIPARTI.lstrip("/"),
                 cv.COMANDO_RIPARTI_CONFERMA.lstrip("/")):
        assert f"'{ramo}'" in letture, ramo
