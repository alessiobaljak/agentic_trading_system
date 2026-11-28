"""Il conto vero con una strategia decisa il lunedì (F5): il ciclo del lunedì, l'età della decisione, il file letto e il passaggio dal
vero PaperF5 al conto vero. Dalle prove di live-path-reviewer del 25 novembre (`reviews/reports/2026-11-25-conto-vero-F5.md`).

Dal 28 novembre 2026 il conto vero esegue di nuovo G1 (decisione del proprietario, `docs/decisioni_del_proprietario.md`): questi test
restano come prova che il codice è generico, con una sottoclasse che ha la strategia, il file e l'età della decisione di F5 com'erano
dal 25 al 28 novembre (`_ContoVeroF5`). Se un giorno il conto vero tornasse a F5, bastano quei tre valori (e i test di guardia)."""
from __future__ import annotations

import tests.conftest  # noqa: F401  (stesso isolamento della suite: prima di ogni import di bot)

import json
import time

import pytest

from bot.portafoglio import conto_vero as cv
from bot.portafoglio import demo_binance as dm
from bot.portafoglio import f5
from tests import test_conto_vero as T
from tests.test_demo_binance import _post
from tests.test_paper_f5 import _Finto

M0 = 20780                                    # lunedì 23 novembre 2026
M1, M2, M3 = M0 + 7, M0 + 14, M0 + 21
assert f5.lunedi_di(M0) == M0 and f5.lunedi_di(M0 + 3) == M0
_ORIGINALE = cv.ContoVeroG1


class _ContoVeroF5(_ORIGINALE):
    """Il conto vero come era dal 25 al 28 novembre 2026: F5, decisa il lunedì alle 00:05 UTC, letta da data/paper_f5.json."""
    STRATEGIA = "F5"
    ETA_MASSIMA_DECISIONE_S = 8 * 86400 + 2 * 3600   # oltre 8 giorni e 2 ore il paper di F5 si è fermato
    QUANDO_DECIDE = "il lunedì alle 00:05 UTC"


FILE_F5 = f5.FILE_STATO                        # data/paper_f5.json, il file del paper di F5
ETA = _ContoVeroF5.ETA_MASSIMA_DECISIONE_S


def _f5(tmp_path, lunedi, pesi=None):
    """Lo stato del paper di F5 con le sole chiavi che il conto vero legge (`ultimo_lunedi`, `pesi`)."""
    (tmp_path / "g1.json").write_text(json.dumps({"ultimo_lunedi": lunedi, "pesi": pesi or {"AUSDT": 0.5, "BUSDT": -0.5},
                                                  "quantita": {}, "lunghi": ["AUSDT"], "corti": ["BUSDT"]}))


def _limiti(finto, da=0):
    return [q for q in _post(finto)[da:] if q.get("type") == "LIMIT"]


def _conto_f5(tmp_path, monkeypatch, finto=None, codice=None, lunedi_nel_file=M0):
    monkeypatch.setattr(cv, "ContoVeroG1", _ContoVeroF5)      # `T._conto` costruisce la sottoclasse di F5
    d, fb, finto = T._conto(tmp_path, monkeypatch, finto, codice=codice)
    assert isinstance(d, _ContoVeroF5)
    _f5(tmp_path, lunedi_nel_file)                      # _conto scrive la decisione di G1 del 24 ottobre: la si sostituisce
    return d, fb, finto


def _giorno(g, ore=0.0, sec=360):
    return g * 86400.0 + ore * 3600 + sec


# ---- P1: accensione a metà settimana, niente fino al lunedì dopo, poi ordini; niente allarmi in settimana ----
def test_p1_accensione_di_mercoledi_aspetta_il_lunedi(tmp_path, monkeypatch):
    d, fb, finto = _conto_f5(tmp_path, monkeypatch)
    d.tick(_giorno(M0 + 2, 12))                         # mercoledì 25, mezzogiorno
    assert T._scritture(finto) == []
    assert fb.get_rtdb("/conto_vero/acceso_dal")["compra_alla_decisione_di_g1_dopo_il"] == "2026-11-23"
    for g in range(M0 + 3, M1):                         # giovedì..domenica alle 00:06 e a mezzogiorno
        d.tick(_giorno(g)); d.tick(_giorno(g, 12))
        assert T._scritture(finto) == []
        assert fb.get_rtdb("/conto_vero/allarmi/decisione_g1") is None
        assert fb.get_rtdb("/conto_vero/allarmi/ordini_vietati") is None
    d.tick(M1 * 86400.0 + 200)                          # lunedì 30 alle 00:03: F5 non ha ancora deciso
    assert T._scritture(finto) == []
    _f5(tmp_path, M1)                                   # F5 decide alle 00:05
    d.tick(_giorno(M1))
    assert {(q["symbol"], q["side"]) for q in _limiti(finto)} == {("AUSDT", "BUY"), ("BUSDT", "SELL")}
    assert fb.get_rtdb("/conto_vero/ribilanciamenti/2026-11-30")["ordini"] == 2


# ---- P2: l'età della decisione: in settimana nessun allarme, oltre 8 giorni e 2 ore allarme e niente ordini nuovi ----
def test_p2_eta_della_decisione_settimanale(tmp_path, monkeypatch):
    d, fb, finto = _conto_f5(tmp_path, monkeypatch, lunedi_nel_file=M0 - 7)
    d.tick(_giorno(M0 - 1, 12))                         # acceso domenica 22
    _f5(tmp_path, M0)
    d.tick(_giorno(M0))                                 # lunedì 23: ribilancio
    n = len(_limiti(finto))
    assert n == 2
    d.tick(_giorno(M0 + 1, 2, 60))                      # martedì 02:01: con le 26 ore di G1 qui ci sarebbe l'allarme
    assert fb.get_rtdb("/conto_vero/allarmi/decisione_g1") is None
    t_limite = M0 * 86400.0 + ETA
    d.tick(t_limite - 60)
    assert fb.get_rtdb("/conto_vero/allarmi/decisione_g1") is None
    d.tick(t_limite + 120)                              # martedì 1° dicembre alle 02:02 senza decisione nuova
    testo = fb.get_rtdb("/conto_vero/allarmi/decisione_g1")["testo"]
    assert "194" in testo and "F5" in testo and "G1" not in testo
    _f5(tmp_path, M1)                                   # F5 riparte e decide (in ritardo): si esegue e l'allarme si toglie
    d.tick(t_limite + 600)
    assert fb.get_rtdb("/conto_vero/allarmi/decisione_g1") is None
    assert len(_limiti(finto)) == n + 2


def test_p2b_decisione_del_lunedi_in_ritardo_di_tre_ore_si_esegue(tmp_path, monkeypatch):
    d, fb, finto = _conto_f5(tmp_path, monkeypatch)
    d.tick(_giorno(M0 + 2, 12))
    d.tick(_giorno(M1, 3))                              # lunedì 30 alle 03:00, F5 non ha ancora deciso (regolamento in ritardo)
    assert fb.get_rtdb("/conto_vero/allarmi/decisione_g1") is None and T._scritture(finto) == []
    _f5(tmp_path, M1)
    d.tick(_giorno(M1, 3, 600))
    assert len(_limiti(finto)) == 2


# ---- P3: «riparti» a metà settimana: conto vuoto fino al lunedì dopo ----
def test_p3_riparti_di_mercoledi_riapre_il_lunedi_dopo(tmp_path, monkeypatch):
    d, fb, finto = _conto_f5(tmp_path, monkeypatch)
    d.tick(_giorno(M0 + 2, 12))
    _f5(tmp_path, M1)
    d.tick(_giorno(M1))                                 # ribilancio del 30
    d.tick(_giorno(M1, 1, 400))                         # dopo l'ora
    fb.proprietario(cv.COMANDO_CHIUDI, True)
    d.tick(_giorno(M1 + 2, 10))                         # mercoledì 2 dicembre: chiudi tutto
    assert d.carica().get("fermo")
    d.tick(_giorno(M1 + 2, 10, 500))                    # conto vuoto
    T._riparti_in_due_passi(fb)
    d.tick(_giorno(M1 + 2, 11))
    st = d.carica()
    assert not st.get("fermo") and st.get("riparti_attende_g1") and st["ultimo_giorno"] == M1
    n = len(_limiti(finto))
    for g in range(M1 + 3, M2):
        d.tick(_giorno(g)); d.tick(_giorno(g, 12))
    assert len(_limiti(finto)) == n                     # vuoto da mercoledì a domenica (con G1: fino alla mezzanotte)
    _f5(tmp_path, M2)
    d.tick(_giorno(M2))
    assert len(_limiti(finto)) == n + 2


# ---- P4 e P5: un blocco (versione non approvata) ----
def test_p4_blocco_tolto_a_meta_settimana_si_aspetta_il_lunedi(tmp_path, monkeypatch):
    codice = [None]
    d, fb, finto = _conto_f5(tmp_path, monkeypatch, codice=lambda: codice[0])
    d.tick(_giorno(M0 + 2, 12))
    _f5(tmp_path, M1)
    d.tick(_giorno(M1))
    n = len(_limiti(finto))
    codice[0] = "nessuna versione approvata dal proprietario"
    d.tick(_giorno(M1 + 1, 10))
    codice[0] = None
    d.tick(_giorno(M1 + 2, 10))
    for g in range(M1 + 3, M2):
        d.tick(_giorno(g))
    assert len(_limiti(finto)) == n
    _f5(tmp_path, M2)
    d.tick(_giorno(M2))
    assert len(_limiti(finto)) == n + 2


def test_p5_blocco_sopra_il_lunedi_salta_la_settimana(tmp_path, monkeypatch):
    """Un blocco attivo alle 00:05 del lunedì: la decisione della settimana non si esegue nemmeno dopo lo sblocco; le posizioni
    della settimana prima restano fino al lunedì dopo (14 giorni con la stessa decisione)."""
    codice = [None]
    d, fb, finto = _conto_f5(tmp_path, monkeypatch, codice=lambda: codice[0])
    d.tick(_giorno(M0 + 2, 12))
    _f5(tmp_path, M1)
    d.tick(_giorno(M1))
    n = len(_limiti(finto))
    codice[0] = "file del codice diversi dalla versione approvata (0123abcd): bot/portafoglio/f5.py"
    d.tick(_giorno(M2 - 1, 12))                         # domenica: commit nuovo, non ancora approvato
    _f5(tmp_path, M2)
    d.tick(_giorno(M2))                                 # lunedì 7 dicembre: bloccato
    codice[0] = None
    d.tick(_giorno(M2, 9))                              # lunedì alle 09:00 il proprietario approva
    for g in range(M2 + 1, M3):
        d.tick(_giorno(g))
    assert len(_limiti(finto)) == n                     # la decisione del 7 dicembre non si esegue mai
    _f5(tmp_path, M3)
    d.tick(_giorno(M3))
    assert len(_limiti(finto)) == n + 2


# ---- P6: di serie il conto vero legge G1 (28 novembre 2026), come il demo; il log d'avvio dice la strategia ----
def test_p6_file_di_serie(tmp_path, monkeypatch):
    assert _ORIGINALE(T._Fb(), verifica_codice=lambda: None).file_g1 == cv.FILE_STRATEGIA == dm.FILE_G1
    assert cv.FILE_STRATEGIA == f5.PaperG1.FILE_DI_SERIE and cv.FILE_STRATEGIA.name == "paper_g1.json"   # il file che scrive PaperG1
    assert dm.DemoG1(T._Fb()).file_g1.name == "paper_g1.json"
    assert FILE_F5.name == "paper_f5.json" and FILE_F5 != cv.FILE_STRATEGIA
    assert dm.DemoG1.STRATEGIA == "G1" and _ORIGINALE.STRATEGIA == "G1" and _ORIGINALE.ETA_MASSIMA_DECISIONE_S == 26 * 3600
    d, fb, finto = _conto_f5(tmp_path, monkeypatch)
    d.tick(_giorno(M0 + 2, 12))
    avvio = fb.get_rtdb("/conto_vero/avvio")
    assert avvio["strategia"] == "F5" and avvio["file_della_decisione"] == "g1.json"   # il file della prova (tmp)
    assert avvio["eta_massima_decisione_ore"] == 194


# ---- P8: dal vero PaperF5 (Binance finto dei suoi test) al conto vero ----
class _VeroF5(T._Vero):
    PREZZI = {f"C{i:02d}USDT": str(10.0 + i) for i in range(30)}


def test_p8_dal_paper_di_f5_vero_al_conto_vero(tmp_path, monkeypatch):
    finto_f5 = _Finto(M0)
    acceso = tmp_path / "paper_f5_acceso"
    acceso.write_text("si")
    p = f5.PaperF5(None, chiedi=finto_f5, file_stato=tmp_path / "g1.json", interruttore=acceso, pausa_s=0.0)
    now = _giorno(M0, 0, 400)
    finto_f5.adesso_ms = int(now * 1000)
    p.tick(now)
    assert p.carica()["ultimo_lunedi"] == M0
    vero = _VeroF5(simboli=tuple(_VeroF5.PREZZI))
    monkeypatch.setenv("DRY_RUN", "false")
    (tmp_path / "conto_vero_acceso").write_text("si")
    (tmp_path / "conto_vero_capitale").write_text("280")
    fb = T._Fb()
    d = _ContoVeroF5(fb, cliente=cv.ClienteVero("chiave", "segreto", http=vero), file_stato=tmp_path / "st.json",
                       file_g1=tmp_path / "g1.json", interruttore=tmp_path / "conto_vero_acceso", file_chiudi=tmp_path / "chiudi",
                       file_capitale=tmp_path / "conto_vero_capitale", verifica_codice=lambda: None)
    T._orologio_del_giro(d)
    d.tick(_giorno(M0 + 2, 12))                         # mercoledì: niente
    assert T._scritture(vero) == []
    # lunedì dopo: il paper decide con il segnale nuovo (funding cambiati), poi il conto vero
    finto_f5.m = M1
    for i, s in enumerate(sorted(finto_f5.funding)):
        finto_f5.funding[s] = 0.0001 * (15 - i)         # segnale capovolto: la banda cambia lato
    p._ultimo_tentativo = 0.0
    now = _giorno(M1, 0, 400)
    finto_f5.adesso_ms = int(now * 1000)
    p.tick(now)
    st_f5 = p.carica()
    assert st_f5["ultimo_lunedi"] == M1
    pesi = st_f5["pesi"]
    assert dm.pesi_fuori_dai_limiti(pesi, somma_massima=cv.SOMMA_PESI_MASSIMA, peso_massimo=cv.PESO_MASSIMO_MONETA) is None
    d.tick(now + 60)
    lati = {q["symbol"]: q["side"] for q in _limiti(vero)}
    attesi = {s: ("BUY" if w > 0 else "SELL") for s, w in pesi.items() if abs(w) * 280 >= 5}
    assert lati == attesi, (lati, attesi)
