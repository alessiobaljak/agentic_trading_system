"""Prova del codice di fase2.py (guida pratica, sezione 4): stampa solo «ok» o l'errore.

La Fase 2 vera non gira: fase2_4 e' sostituita da un risultato finto senza trade (nessun calcolo sui prezzi),
e log e risultati vanno in una cartella di prova fuori dal log della campagna.
"""
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
import fase2  # noqa: E402
from research.src.motore3 import Risultato, metriche  # noqa: E402

PROVA = comune.CARTELLA_DATI / "prova_fase2"


def finta(v, s, a, b, compilata=None):
    ris = Risultato([], a, b, {})
    m = metriche(ris, s)
    import numpy as np
    return {"metriche": m, "p_value": np.float64(0.5), "casuali": {"tenute": 1000, "nota": "finta"},
            "valori_casuali": np.zeros(1000), "esiti": {"supera": np.bool_(False)}, "supera": np.bool_(False),
            "buy_and_hold": np.float64(0.0), "risultato": ris}


try:
    PROVA.mkdir(exist_ok=True)
    comune.LOG = PROVA / "log_prova.jsonl"
    if comune.LOG.exists():
        comune.LOG.unlink()
    fase2.RISULTATI = PROVA / "risultati"
    fase2.AVANZAMENTO = "prova_fase2/avanzamento.txt"
    fase2.fase2_4 = finta
    lotto = comune.leggi_lotto(comune.CAMPAGNA / "codice" / "lotto_01.json")
    fase2.esegui_una(lotto["V-001"])
    voci = comune.voci()
    assert [v["tipo"] for v in voci] == ["registrazione", "risultato"], voci
    assert voci[0]["variante_n"] == 1 and voci[0]["trade_stimati"] == 228
    # ripresa: registrazione senza risultato, con una correzione
    comune.LOG.write_text(comune.LOG.read_text(encoding="utf-8").splitlines()[0] + "\n", encoding="utf-8")
    comune.aggiungi({"id": "V-001", "tipo": "correzione", "testo": "prova"})
    fase2.esegui_una(lotto["V-001"], riprendi=True)
    assert [v["tipo"] for v in comune.voci()] == ["registrazione", "correzione", "risultato"]
    print("ok")
except BaseException:
    traceback.print_exc()
