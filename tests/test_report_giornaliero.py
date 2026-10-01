"""IL REPORT GIORNALIERO (1 ott 2026): struttura fissa di nove sezioni, sempre
presenti anche senza dati; una sezione rotta non ferma le altre; pubblicazione."""
import time
from datetime import datetime, timedelta

import pytest

from bot.core.tempo import fuso, giorno_locale
from bot.learning import report as rp
import scripts.report_giornaliero as rg

NOW = datetime(2026, 10, 2, 8, 0, tzinfo=fuso()).timestamp()      # 08:00 ora italiana
IERI = "2026-10-01"


def _t(pnl, ore_fa, **kw):
    ex = NOW - ore_fa * 3600
    t = {"symbol": "AUSDT", "strategy": "gen_a", "direction": "long", "entry_price": 10.0,
         "orig_stop": 9.0, "size": 1.0, "pnl": pnl, "gross_pnl_usdt": pnl + 0.1,
         "total_cost_usdt": 0.1, "exit_ts": ex, "entry_ts": ex - 3600, "exit_reason": "stop_loss"}
    t.update(kw)
    return t


def _vuoto(**kw):
    base = dict(trades=[], controllo=None, gate=None, portafoglio=None, backlog=None, specs=None,
                capito=None, testo_letture=None, commit=None, spesa_ieri=None, r1=None, now=NOW)
    base.update(kw)
    return rp.costruisci_report(**base)


def test_nove_sezioni_sempre_nello_stesso_ordine_anche_senza_dati():
    rep = _vuoto()
    assert [s["id"] for s in rep["sezioni"]] == [sid for sid, _ in rp.SEZIONI]
    assert len(rep["sezioni"]) == 9
    assert rep["meta"]["giorno"] == IERI and rep["meta"]["oggi"] == "2026-10-02"
    for s in rep["sezioni"]:
        assert s["titolo"] and isinstance(s["righe"], list)


def test_il_paper_ieri_conta_per_data_di_uscita_in_ora_italiana():
    trades = [_t(-1.0, 10), _t(2.0, 20), _t(1.0, 40),      # ieri, ieri, l'altro ieri
              _t(5.0, 1),                                  # oggi: non conta in «ieri»
              _t(3.0, 12, esplorativa=True)]               # esplorativa: solo sul conto
    rep = _vuoto(trades=trades)
    paper = rep["sezioni"][1]
    ieri = paper["tabella"]["righe"][0]
    assert ieri[0] == "ieri" and ieri[1] == 2 and ieri[3] == "+1.00"
    assert "Sul conto" in paper["righe"][0] and "3 trade" in paper["righe"][0]


def test_periodi():
    p = rp.periodi([_t(1, 10), _t(1, 24 * 8 + 10), _t(1, 1)], IERI)
    assert len(p["ieri"]) == 1 and len(p["7g"]) == 1 and len(p["tutto"]) == 2


def test_una_sezione_rotta_non_ferma_le_altre(monkeypatch):
    monkeypatch.setattr(rp, "sez_gate", lambda *a, **k: 1 / 0)
    rep = _vuoto()
    gate = rep["sezioni"][2]
    assert gate["id"] == "gate" and "ZeroDivisionError" in gate["errore"]
    assert all(not s["errore"] for s in rep["sezioni"] if s["id"] in ("paper", "imparato"))


def test_capito_avvisa_se_non_c_e_niente_di_nuovo():
    testo = "# x\n\n## 2026-09-28\n* vecchia nota\n\n## 2026-09-20\n* piu' vecchia\n"
    s = rp.sez_capito(testo, IERI, "2026-10-02")
    assert "ATTENZIONE" in s["righe"][0] and s["righe"][1] == "vecchia nota"
    s2 = rp.sez_capito("## 2026-10-02\n* oggi\n  continua\n", IERI, "2026-10-02")
    assert s2["righe"] == ["Note del 2026-10-02:", "oggi continua"]


def test_cambiato_toglie_i_commit_automatici():
    c = [{"hash": "a", "at": NOW, "titolo": "ops: risposte e battito"},
         {"hash": "b", "at": NOW, "titolo": "state snapshot [skip ci]"},
         {"hash": "c", "at": NOW, "titolo": "J2: il backlog in dashboard"}]
    s = rp.sez_cambiato(c)
    assert len(s["righe"]) == 1 and "J2" in s["righe"][0]
    assert rp.sez_cambiato(None)["errore"]
    assert "Nessuna modifica" in rp.sez_cambiato([c[0]])["righe"][0]


def test_letture_e_attesa():
    testo = ("| Data | Cosa | Regola |\n|---|---|---|\n| 2026-10-07 | fuori campione | r |\n"
             "| 2026-09-01 | vecchia | r |\n")
    s = rp.sez_attesa({"aspetta_si": [{"sigla": "X1", "titolo": "proposta"}], "gruppi": []},
                      testo, "2026-10-02")
    assert "X1. proposta" in s["righe"][0]
    assert s["tabella"]["righe"] == [["2026-10-07", "fuori campione", "r"]]


def test_i_file_veri_del_repo_si_leggono():
    capito = rg._leggi_testo(rg.RADICE, "docs", "capito.md")
    let = rg._leggi_testo(rg.RADICE, "docs", "letture.md")
    assert rp.note_capito(capito) and rp.letture(let)


def test_commit_recenti_dal_repo():
    c = rg.commit_recenti(ore=24 * 365)
    assert c is None or (c and {"hash", "at", "titolo"} <= set(c[0]))


def test_pubblica_scrive_ultimo_e_storia(monkeypatch):
    scritti = {}

    class Fb:
        def set_doc(self, c, d, data):
            scritti[(c, d)] = data

        def set_rtdb(self, p, data):
            scritti[p] = data

        def get_doc(self, c, d):
            return None

        def get_rtdb(self, p):
            return None

        def query_collection(self, c, order_by=None):
            return [_t(-1.0, 10)]

    import bot.core.firebase_client as fc
    monkeypatch.setattr(fc, "get_firebase", lambda: Fb())
    assert rg.main(["--pubblica"]) == 0
    rep = scritti[("dashboard", "report_giornaliero")]
    assert len(rep["sezioni"]) == 9 and scritti["/report_giornaliero"]["meta"]["giorno"]
    assert ("report_giornaliero", rep["meta"]["giorno"]) in scritti
