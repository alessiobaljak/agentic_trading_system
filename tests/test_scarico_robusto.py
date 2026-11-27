"""Lo scarico delle candele giornaliere del paper delle candidate non si ferma tutto a un solo intoppo di rete, e uno scarico
incompleto si vede (audit del 26 novembre 2026, raccolta-3).

Il 20 e il 26 novembre 2026 lo scarico si era fermato a meta' (il 26 per una ``http.client.IncompleteRead`` in ``_leggi``,
che riprovava solo su ``OSError``), ``paper/aggiorna.sh`` lo nascondeva con «|| true» e il pannello toglieva senza dirlo
l'ultimo giorno. Qui niente rete e niente ``research/data``: urlopen, ``uno`` e i passi dello script sono finti.
"""
import http.client
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

import pytest

from research.programma5.strumenti import scarico as p5
from research.programma6 import scarico_giorni as sg

REPO = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# (1) _leggi riprova anche sulle letture incomplete, come _prendi
# ---------------------------------------------------------------------------

class _Risposta:
    def __init__(self, dati=b"", errore=None):
        self.dati, self.errore = dati, errore

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        if self.errore is not None:
            raise self.errore
        return self.dati


def _finto_urlopen(monkeypatch, risposte):
    chiamate = []

    def urlopen(req, timeout=None):
        chiamate.append(req.full_url)
        return risposte[min(len(chiamate), len(risposte)) - 1]

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(time, "sleep", lambda s: None)
    return chiamate


def test_leggi_riprova_su_lettura_incompleta(monkeypatch):
    # il 26 novembre: IncompleteRead(16384 bytes read) leggendo l'elenco di una moneta, e tutto lo scarico era caduto
    pagina = "<ListBucketResult><Key>data/x/AUSDT-1d-2026-11-24.zip</Key></ListBucketResult>".encode()
    chiamate = _finto_urlopen(monkeypatch, [_Risposta(errore=http.client.IncompleteRead(b"x" * 16384)), _Risposta(pagina)])
    assert p5.elenca("data/x/") == ["data/x/AUSDT-1d-2026-11-24.zip"]
    assert len(chiamate) == 2


def test_leggi_rinuncia_dopo_i_tentativi(monkeypatch):
    chiamate = _finto_urlopen(monkeypatch, [_Risposta(errore=http.client.IncompleteRead(b""))])
    with pytest.raises(http.client.IncompleteRead):
        p5._leggi("https://esempio/elenco", tentativi=3)
    assert len(chiamate) == 3


# ---------------------------------------------------------------------------
# (2) l'errore di una moneta non ferma le altre; l'esito alla fine
# ---------------------------------------------------------------------------

def _imp(s: str, ultimo: str) -> dict:
    nome = f"{s}-1d-{ultimo}.zip"
    return {"giorni": {"file": 10, "primo": f"{s}-1d-2020-01.zip", "ultimo": nome, "sha256": "0"},
            "funding": {"file": 1, "primo": "", "ultimo": "", "sha256": "0"}}


@pytest.fixture
def cartella(monkeypatch, tmp_path):
    monkeypatch.setattr(sg, "QUI", tmp_path)            # mai il file vero del repository
    monkeypatch.delenv("P6_IMPRONTE", raising=False)
    monkeypatch.setenv("P6_FILI", "1")
    return tmp_path


def test_un_errore_non_ferma_le_altre(cartella, monkeypatch, capsys):
    tre = ("AAAUSDT", "BBBUSDT", "CCCUSDT")
    prima = {s: _imp(s, "2026-11-23") for s in tre}
    (cartella / "scarico_giorni.json").write_text(json.dumps(prima))

    def uno(s, premio=False):
        if s == "AAAUSDT":
            raise http.client.IncompleteRead(b"x" * 16384)
        return _imp(s, "2026-11-24")

    monkeypatch.setattr(sg, "uno", uno)
    codice = sg.main(list(tre))
    imp = json.loads((cartella / "scarico_giorni.json").read_text())
    assert imp["BBBUSDT"]["giorni"]["ultimo"] == "BBBUSDT-1d-2026-11-24.zip"     # le monete dopo l'errore si scaricano
    assert imp["CCCUSDT"]["giorni"]["ultimo"] == "CCCUSDT-1d-2026-11-24.zip"
    assert imp["AAAUSDT"] == prima["AAAUSDT"]                                    # resta l'impronta di prima
    es = imp["_esito"]
    assert (es["giorno"], es["attive"], es["senza_ultimo_giorno"], es["per_errore"]) == ("2026-11-24", 3, 1, 1)
    assert es["monete_senza"] == ["AAAUSDT"] and es["errori"]["AAAUSDT"].startswith("IncompleteRead")
    assert codice == 2
    out = capsys.readouterr()
    assert "[giorni] AAAUSDT: ERRORE IncompleteRead" in out.out
    assert "Traceback" in out.err                                                # il registro ha il traceback
    assert out.out.strip().splitlines()[-1].startswith("[giorni] esito: 3 monete attive, 1 senza il giorno 2026-11-24")
    assert sg.riga_paper(imp, codice).startswith("Scarico incompleto: 1 moneta senza il giorno 2026-11-24 (1 per un errore")


def test_scarico_completo(cartella, monkeypatch):
    (cartella / "scarico_giorni.json").write_text(json.dumps({"AAAUSDT": _imp("AAAUSDT", "2026-11-23"),
                                                               "_esito": {"senza_ultimo_giorno": 5}}))
    monkeypatch.setattr(sg, "uno", lambda s, premio=False: _imp(s, "2026-11-24"))
    assert sg.main(["AAAUSDT", "BBBUSDT"]) == 0
    imp = json.loads((cartella / "scarico_giorni.json").read_text())
    assert imp["_esito"]["senza_ultimo_giorno"] == 0 and imp["_esito"]["attive"] == 2   # l'esito vecchio e' riscritto
    assert sg.riga_paper(imp, 0) == ""


def test_troppi_errori_di_fila_saltano_le_altre(cartella, monkeypatch):
    # rete giu' per tutte: dopo ERRORI_DI_FILA errori le monete rimaste si saltano invece di aspettare i tentativi di ognuna
    simboli = [f"M{i:02d}USDT" for i in range(sg.ERRORI_DI_FILA + 5)]
    (cartella / "scarico_giorni.json").write_text(json.dumps({s: _imp(s, "2026-11-23") for s in simboli}))
    chiamate = []

    def uno(s, premio=False):
        chiamate.append(s)
        raise OSError("rete giu'")

    monkeypatch.setattr(sg, "uno", uno)
    assert sg.main(simboli) == 2
    assert len(chiamate) == sg.ERRORI_DI_FILA
    imp = json.loads((cartella / "scarico_giorni.json").read_text())
    es = imp["_esito"]
    assert es["saltate"] == 5 and len(es["errori"]) == sg.ERRORI_DI_FILA
    # l'ultimo giorno non avanza per nessuna, quindi nessuna «manca»: la riga per PAPER.md c'e' lo stesso
    assert es["senza_ultimo_giorno"] == 0
    riga = sg.riga_paper(imp, 2)
    assert riga.startswith("Scarico incompleto (10 monete con un errore dello scarico, ultimo giorno scaricato 2026-11-23")
    assert "5 saltate dopo 10 errori di fila" in riga


def test_ultimo_giorno():
    assert sg.ultimo_giorno({"ultimo": "BTCUSDT-1d-2026-11-24.zip"}) == date(2026, 11, 24)
    assert sg.ultimo_giorno({"ultimo": "1000000BOBUSDT-1d-2026-11-24.zip"}) == date(2026, 11, 24)
    assert sg.ultimo_giorno({"ultimo": "EOSUSDT-1d-2025-05.zip"}) == date(2025, 5, 31)
    assert sg.ultimo_giorno({"ultimo": "XUSDT-1d-2025-12.zip"}) == date(2025, 12, 31)
    assert sg.ultimo_giorno({"ultimo": "XUSDT-1d-2024-02.zip"}) == date(2024, 2, 29)
    assert sg.ultimo_giorno({"ultimo": ""}) is None and sg.ultimo_giorno(None) is None


def test_esito_quali_monete_sono_attive():
    imp = {"OKUSDT": _imp("OKUSDT", "2026-11-24"),
           "MANCAUSDT": _imp("MANCAUSDT", "2026-11-23"),       # scaricata ora, l'archivio non ha ancora il 24
           "TOLTAUSDT": _imp("TOLTAUSDT", "2026-11-21"),       # scaricata ora, l'archivio non ha i suoi ultimi giorni: tolta
           "ERRUSDT": _imp("ERRUSDT", "2026-11-20"),           # errore oggi (e nei giorni prima)
           "FERMAUSDT": _imp("FERMAUSDT", "2026-11-22"),       # non scaricata in questo giro
           "VECCHIAUSDT": _imp("VECCHIAUSDT", "2024-05"),      # tolta dal listino nel 2024
           "_esito": {"vecchio": True}}
    es = sg.esito(imp, {"ERRUSDT": "OSError: x", "NUOVAUSDT": "OSError: y"}, fatte=["OKUSDT", "MANCAUSDT", "TOLTAUSDT"])
    assert es["giorno"] == "2026-11-24"
    assert es["attive"] == 5                                    # OK, MANCA, ERR, FERMA e la nuova mai scaricata
    assert es["monete_senza"] == ["ERRUSDT", "FERMAUSDT", "MANCAUSDT", "NUOVAUSDT"]
    assert (es["per_errore"], es["assenti_nell_archivio"], es["non_scaricate"]) == (2, 1, 1)


def test_riga_per_paper():
    es = {"giorno": "2026-11-24", "senza_ultimo_giorno": 141, "per_errore": 141, "assenti_nell_archivio": 0,
          "non_scaricate": 0, "errori": {f"S{i}USDT": "IncompleteRead" for i in range(141)}, "saltate": 0}
    assert sg.riga_paper({"_esito": es}, 2) == (
        "Scarico incompleto: 141 monete senza il giorno 2026-11-24 (141 per un errore dello scarico; elenco in "
        "`research/programma6/scarico_giorni.json`, voce `_esito`).")
    # l'archivio a meta' pubblicazione (8 novembre: il giorno c'era per 232 monete su circa 715)
    es2 = {**es, "senza_ultimo_giorno": 483, "per_errore": 0, "assenti_nell_archivio": 483, "errori": {}}
    assert sg.riga_paper({"_esito": es2}, 2).startswith("Scarico incompleto: 483 monete senza il giorno 2026-11-24 (483 "
                                                         "assenti nell'archivio;")
    vuoto = {**es, "senza_ultimo_giorno": 0, "per_errore": 0, "errori": {}}
    assert sg.riga_paper({"_esito": vuoto}, 0) == ""


def test_riga_per_paper_se_lo_scarico_e_caduto():
    # codice diverso da 0 e 2: l'esito nel file e' del giro prima; le monete senza l'ultimo giorno dalle impronte scritte
    imp = {"AUSDT": _imp("AUSDT", "2026-11-18"), "BUSDT": _imp("BUSDT", "2026-11-17"), "CUSDT": _imp("CUSDT", "2026-11-17"),
           "_esito": {"giorno": "2026-11-17", "senza_ultimo_giorno": 0, "errori": {}, "saltate": 0}}
    riga = sg.riga_paper(imp, 1)
    assert riga.startswith("Scarico incompleto: 2 monete senza il giorno 2026-11-18 (lo scarico delle candele giornaliere "
                           "si è fermato prima della fine, codice 1")
    assert sg.riga_paper({}, 1).startswith("Scarico incompleto (lo scarico delle candele giornaliere si è fermato")
    assert sg.riga_paper({}, 0).startswith("Scarico incompleto (")          # nessun esito scritto: non si tace


def test_aggiungi_riga_in_fondo(tmp_path):
    f = tmp_path / "scarico_giorni.json"
    f.write_text(json.dumps({"AUSDT": _imp("AUSDT", "2026-11-24"), "BUSDT": _imp("BUSDT", "2026-11-23"),
                             "_esito": sg.esito({"AUSDT": _imp("AUSDT", "2026-11-24"), "BUSDT": _imp("BUSDT", "2026-11-23")},
                                                {"BUSDT": "IncompleteRead: x"}, ["AUSDT"])}))
    paper = tmp_path / "PAPER.md"
    paper.write_text("# Programma 6\n\nDati fino al **2026-11-23**.\n", encoding="utf-8")
    riga = sg.aggiungi_riga(str(f), 2, str(paper))
    assert paper.read_text(encoding="utf-8").splitlines()[-1] == riga
    assert riga.startswith("Scarico incompleto: 1 moneta senza il giorno 2026-11-24")
    assert sg.aggiungi_riga(str(tmp_path / "manca.json"), 1).startswith("Scarico incompleto (")


# ---------------------------------------------------------------------------
# (3) paper/aggiorna.sh controlla l'esito e scrive la riga in fondo a PAPER.md, senza fermarsi
# ---------------------------------------------------------------------------

FINTO_PYTHON = """#!/bin/bash
# python3 finto: scarico, buchi e paper finti; la riga dello scarico incompleto e' quella vera (PYTHONPATH sul repository)
case "$*" in
  *"scarico_giorni --riga"*) PYTHONPATH="$REPO_VERO" exec "$PYTHON_VERO" "$@" ;;
  *"research.programma6.scarico_giorni"*)
    [ -n "$FINTO_JSON" ] && cp "$FINTO_JSON" "$P6_IMPRONTE/scarico_giorni.json"
    echo "[giorni] finto"; exit "${FINTO_CODICE:-0}" ;;
  *"research.programma6.buchi_archivio"*) exit 0 ;;
  *"research.programma6.paper.aggiorna"*)
    printf '# Programma 6 — il paper delle candidate\\n\\nDati fino al **2026-11-23**.\\n' > research/programma6/paper/PAPER.md
    exit 0 ;;
  *) echo "python3 finto: comando inatteso: $*" >&2; exit 99 ;;
esac
"""


def _aggiorna_sh(tmp_path, imp_finto, codice: int):
    radice = tmp_path / "repo"
    (radice / "research/programma6/paper").mkdir(parents=True)
    shutil.copy(REPO / "research/programma6/paper/aggiorna.sh", radice / "research/programma6/paper/aggiorna.sh")
    (radice / "research/programma6/paper/PAPER.md").write_text("vecchio\n", encoding="utf-8")
    cestino = tmp_path / "bin"
    cestino.mkdir()
    (cestino / "python3").write_text(FINTO_PYTHON)
    (cestino / "python3").chmod(0o755)
    finto_json = tmp_path / "finto.json"
    if imp_finto is not None:
        finto_json.write_text(json.dumps(imp_finto))
    env = {**os.environ, "PATH": f"{cestino}:{os.environ.get('PATH', '/usr/bin:/bin')}", "REPO_VERO": str(REPO),
           "PYTHON_VERO": sys.executable, "FINTO_JSON": str(finto_json) if imp_finto is not None else "",
           "FINTO_CODICE": str(codice)}
    vero = (REPO / "research/programma6/paper/PAPER.md").read_bytes()
    r = subprocess.run(["bash", str(radice / "research/programma6/paper/aggiorna.sh"), str(tmp_path / "impronte")],
                       env=env, capture_output=True, text=True, timeout=120)
    assert (REPO / "research/programma6/paper/PAPER.md").read_bytes() == vero      # il PAPER.md vero non si tocca
    return r, (radice / "research/programma6/paper/PAPER.md").read_text(encoding="utf-8"), radice


def _imp_con_esito(n_senza: int) -> dict:
    imp = {f"A{i:03d}USDT": _imp(f"A{i:03d}USDT", "2026-11-24") for i in range(10)}
    imp.update({f"Z{i:03d}USDT": _imp(f"Z{i:03d}USDT", "2026-11-23") for i in range(n_senza)})
    imp["_esito"] = sg.esito(imp, {s: "IncompleteRead: x" for s in imp if s.startswith("Z")},
                             [s for s in imp if s.startswith("A")])
    return imp


def test_aggiorna_sh_scrive_lo_scarico_incompleto_in_fondo(tmp_path):
    r, paper, radice = _aggiorna_sh(tmp_path, _imp_con_esito(3), 2)
    assert r.returncode == 0, r.stderr
    righe = paper.splitlines()
    assert righe[0] == "# Programma 6 — il paper delle candidate"                # rigenerato, poi la riga in fondo
    assert righe[-1].startswith("Scarico incompleto: 3 monete senza il giorno 2026-11-24 (3 per un errore dello scarico")
    assert (radice / "research/programma6/scarico_giorni.json").exists()          # le impronte copiate come prima


def test_aggiorna_sh_scarico_completo_nessuna_riga(tmp_path):
    r, paper, _ = _aggiorna_sh(tmp_path, _imp_con_esito(0), 0)
    assert r.returncode == 0, r.stderr
    assert paper.startswith("# Programma 6") and "Scarico incompleto" not in paper


def test_aggiorna_sh_scarico_caduto_non_ferma_il_resto(tmp_path):
    # lo scarico cade (codice 1) dopo aver scritto le impronte di una parte delle monete, senza esito
    imp = {f"A{i:03d}USDT": _imp(f"A{i:03d}USDT", "2026-11-24") for i in range(6)}
    imp.update({f"Z{i:03d}USDT": _imp(f"Z{i:03d}USDT", "2026-11-23") for i in range(4)})
    r, paper, _ = _aggiorna_sh(tmp_path, imp, 1)
    assert r.returncode == 0, r.stderr
    assert paper.startswith("# Programma 6")                                       # il paper si rigenera lo stesso
    assert paper.splitlines()[-1].startswith("Scarico incompleto: 4 monete senza il giorno 2026-11-24 (lo scarico delle "
                                             "candele giornaliere si è fermato prima della fine, codice 1")
