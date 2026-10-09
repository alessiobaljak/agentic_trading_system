"""J2 (1 ott 2026): il backlog in dashboard senza copie a mano. Il lettore di
`docs/backlog.md`, il documento pubblicato e l'aggancio dopo il giro del gate."""
import inspect
import os

from bot.learning.backlog_doc import GRUPPO_SI, TESTO_MAX, leggi_backlog
import scripts.report_giornaliero as rg

FINTO = """# Backlog

**Aggiornato il 2 ottobre 2026, 09:00 ora italiana.** Testo.

| Gruppo | Voci | Cosa le sblocca |
|---|---|---|
| **0. Aspettano il tuo sì** | X1 | una tua risposta |
| **2. Dopo le letture** | K9 | il numero delle letture |

---

## 0. Aspettano il tuo sì

### X1. Una proposta
Perché in **tre** righe, con `codice`.
Seconda riga.

## 2. Dopo le letture

### K9. La leva
Testo K9.

---

### K10. Altra
Testo K10.

## Note finali
### Z9. Fuori dai gruppi
non conta
"""


def test_legge_gruppi_voci_e_cosa_serve():
    d = leggi_backlog(FINTO)
    assert d["aggiornato"] == "2 ottobre 2026, 09:00 ora italiana"
    assert [g["numero"] for g in d["gruppi"]] == [0, 2]
    assert d["gruppi"][1]["cosa_serve"] == "il numero delle letture"
    assert [v["sigla"] for v in d["gruppi"][1]["voci"]] == ["K9", "K10"]
    assert d["n_voci"] == 3
    assert [v["sigla"] for v in d["aspetta_si"]] == ["X1"] and GRUPPO_SI == 0
    # il markdown sparisce, le righe si uniscono
    assert d["aspetta_si"][0]["testo"] == "Perché in tre righe, con codice. Seconda riga."


def test_file_vuoto_o_malformato_non_solleva():
    for t in (None, "", "testo libero\n### A1. senza gruppo"):
        d = leggi_backlog(t)
        assert d["gruppi"] == [] and d["aspetta_si"] == [] and d["n_voci"] == 0


def test_testo_troppo_lungo_si_tronca():
    d = leggi_backlog("## 0. Si\n### A1. T\n" + "x " * 2000)
    assert len(d["aspetta_si"][0]["testo"]) == TESTO_MAX


def test_il_backlog_vero_si_legge():
    radice = os.path.join(os.path.dirname(__file__), "..")
    with open(os.path.join(radice, "docs", "backlog.md"), encoding="utf-8") as f:
        d = leggi_backlog(f.read())
    nomi = {g["numero"]: g["nome"] for g in d["gruppi"]}
    assert nomi.get(0, "").startswith("Aspettano il tuo s")
    assert d["n_voci"] >= 10 and d["aggiornato"]
    assert all(g["cosa_serve"] for g in d["gruppi"])


def test_doc_backlog_senza_file_lo_dice(tmp_path):
    d = rg.doc_backlog(str(tmp_path), now=1.0)
    assert d["meta"]["errore"] and d["gruppi"] == [] and d["meta"]["generato_at"] == 1.0


def test_pubblica_scrive_firestore_e_rtdb(monkeypatch):
    scritti = {}

    class Fb:
        def set_doc(self, c, d, data):
            scritti[(c, d)] = data

        def set_rtdb(self, p, data):
            scritti[p] = data

    import bot.core.firebase_client as fc
    monkeypatch.setattr(fc, "get_firebase", lambda: Fb())
    assert rg.main(["--pubblica"]) == 0
    assert scritti[("dashboard", "backlog")]["n_voci"] >= 10
    assert scritti["/backlog"]["meta"]["fonte"] == "docs/backlog.md"


def test_la_discovery_pubblica_dopo_ogni_giro_in_un_processo_a_parte():
    import scripts.discover_strategies as d
    src = inspect.getsource(d)
    assert "pubblica_dashboard_dopo_il_giro()" in src.split('if __name__ == "__main__":')[-1]
    corpo = inspect.getsource(d.pubblica_dashboard_dopo_il_giro)
    assert "subprocess.run" in corpo and "timeout=" in corpo and "TRADING_BOT_TEST_MODE" in corpo
    # nei test non parte niente
    d.pubblica_dashboard_dopo_il_giro()


def test_la_data_con_l_apostrofo_si_legge():
    # «Aggiornato l'8 ottobre»: fino al 9 ott 2026 la data si perdeva e il test sul backlog vero falliva
    for testo, atteso in (("**Aggiornato l'8 ottobre 2026, 07:40 ora italiana.**", "8 ottobre 2026, 07:40 ora italiana"),
                          ("**Aggiornato l’11 ottobre 2026.**", "11 ottobre 2026"),
                          ("**Aggiornato il 9 ottobre 2026.**", "9 ottobre 2026")):
        assert leggi_backlog(testo + "\n")["aggiornato"] == atteso
