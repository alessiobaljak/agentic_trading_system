"""L'archivio di Firebase e della macchina (`scripts/esporta_storia.py`, 18 ott 2026).

Il repository e' pubblico: la cosa che conta di piu' e' che niente di riservato finisca
nell'archivio. Poi che il tetto delle letture lasci fuori le collection meno importanti
e non i trade, e che senza Firebase lo script non scriva niente.
"""
import gzip
import json
import os
import tarfile

from bot.core.firebase_client import FirebaseClient
from scripts import esporta_storia as es


def _leggi_gz(percorso):
    with open(percorso, "rb") as f:
        return json.loads(gzip.decompress(f.read()).decode("utf-8"))


def test_oscura_toglie_segreti_e_indirizzi_ma_tiene_le_misure():
    dati = {
        "api_key": "abc123",
        "telegram": {"chat_id": 123456789, "bot_token": "777:XYZ"},
        "spesa": {"tokens_in": 1200, "tokens_out": 300},
        "nota": "scritto da qualcuno@example.com, token=ghp_" + "a" * 30,
        "utenti": {"qualcuno@example.com": {"ruolo": "proprietario"}},
        "pnl": -1.5,
    }
    out = es.oscura(dati)
    testo = json.dumps(out)
    assert out["api_key"] == "[OSCURATO]"
    assert out["telegram"]["bot_token"] == "[OSCURATO]"
    assert out["telegram"]["chat_id"] == "[OSCURATO]"
    assert out["spesa"] == {"tokens_in": 1200, "tokens_out": 300}
    assert out["pnl"] == -1.5
    assert "example.com" not in testo and "ghp_" not in testo and "abc123" not in testo


def _fb_con_dati():
    fb = FirebaseClient()   # senza credenziali: lo specchio in memoria (conftest)
    assert not fb.is_live
    fb.set_doc("trades", "t1", {"symbol": "BTCUSDT", "pnl": 1.0})
    fb.set_doc("trades", "t2", {"symbol": "ETHUSDT", "pnl": -2.0})
    fb.set_doc("strategy_registry", "validated", {"pairs_json": "[]"})
    fb.set_doc("zeta_misure", "a", {"x": 1})
    fb.set_doc("zeta_misure", "b", {"x": 2})
    fb.set_doc("zeta_misure", "c", {"x": 3})
    fb.set_rtdb("/account/equity", 825.59)
    fb.set_rtdb("/user_settings/secret_word", "segreto")
    return fb


def test_esporta_scrive_firestore_rtdb_e_macchina_con_l_indice(tmp_path):
    fb = _fb_con_dati()
    dati = tmp_path / "data"
    (dati / "selettore").mkdir(parents=True)
    (dati / "selettore" / "voti.jsonl").write_text(
        json.dumps({"coppia": "X", "password": "p"}) + "\n", encoding="utf-8")
    (dati / "tuning.env").write_text("OPTIMIZER_X=1\n", encoding="utf-8")
    (dati / "gate_backup_1.json").write_text(json.dumps({"ok": 1}), encoding="utf-8")
    uscita = tmp_path / "archivio"

    indice = es.esporta(fb, str(uscita), str(dati), tetto_letture=1000)

    scritti = {f["file"] for f in indice["file"]}
    assert {"firestore/trades.json.gz", "firestore/strategy_registry.json.gz",
            "firestore/zeta_misure.json.gz", "rtdb/account.json.gz",
            "rtdb/user_settings.json.gz", "macchina/selettore.tar.gz",
            "macchina/file_sciolti.tar.gz"} <= scritti
    assert _leggi_gz(uscita / "firestore" / "trades.json.gz")["t2"]["pnl"] == -2.0
    assert _leggi_gz(uscita / "rtdb" / "user_settings.json.gz") == {"secret_word": "[OSCURATO]"}
    # il file .env resta fuori, con il motivo
    assert any(f["file"] == "data/tuning.env" for f in indice["fuori"])
    with tarfile.open(uscita / "macchina" / "selettore.tar.gz") as tar:
        riga = tar.extractfile("selettore/voti.jsonl").read().decode("utf-8")
    assert json.loads(riga) == {"coppia": "X", "password": "[OSCURATO]"}
    with tarfile.open(uscita / "macchina" / "file_sciolti.tar.gz") as tar:
        assert tar.getnames() == ["gate_backup_1.json"]
    # l'indice su disco e' quello ritornato, con le impronte
    su_disco = json.loads((uscita / "INDICE.json").read_text(encoding="utf-8"))
    assert su_disco["file"] == indice["file"]
    assert all(len(f["sha256"]) == 64 for f in su_disco["file"])


def test_il_tetto_delle_letture_lascia_fuori_le_meno_importanti_non_i_trade(tmp_path):
    fb = _fb_con_dati()
    # trades (2) e strategy_registry (1) passano; zeta_misure (3) no
    indice = es.esporta(fb, str(tmp_path / "a"), None, tetto_letture=8)
    scritti = {f["file"] for f in indice["file"]}
    assert "firestore/trades.json.gz" in scritti
    assert "firestore/strategy_registry.json.gz" in scritti
    assert "firestore/zeta_misure.json.gz" not in scritti
    assert any(f["file"] == "firestore/zeta_misure.json.gz" for f in indice["fuori"])
    assert "RIMASTI FUORI" in es.riepilogo(indice, "a")


def test_senza_firebase_non_scrive_niente(tmp_path, capsys):
    uscita = tmp_path / "mai"
    assert es.main(["--uscita", str(uscita)]) == 0
    assert not os.path.exists(uscita)
    assert "niente da esportare" in capsys.readouterr().out
