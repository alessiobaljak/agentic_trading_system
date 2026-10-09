"""Fase 0, punto 2: scarica i dati in-sample di ADAUSDT (last, mark, funding) e il last di BTCUSDT.

Solo fino al 2023-12-31 (il caricatore rifiuta il resto). Nessun elenco di file remoti.
Alla fine registra le impronte (data/insample/<SIMBOLO>/impronte.json) e stampa il riepilogo.
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402

TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO, FINE = date(2020, 1, 1), date(2023, 12, 31)

lavori = []
for tf in TF:
    for anno, mese in dati.mesi_del_periodo(INIZIO, FINE):
        lavori.append(("ADAUSDT", "klines", tf, anno, mese))
        lavori.append(("ADAUSDT", "markPriceKlines", tf, anno, mese))
        lavori.append(("BTCUSDT", "klines", tf, anno, mese))
for anno, mese in dati.mesi_del_periodo(INIZIO, FINE):
    lavori.append(("ADAUSDT", "fundingRate", None, anno, mese))


def uno(l):
    s, tipo, tf, a, m = l
    try:
        p = dati.scarica_mese(s, tipo, tf, a, m)
        return l, (p is not None), None
    except Exception as e:  # noqa: BLE001
        return l, False, repr(e)


with ThreadPoolExecutor(max_workers=16) as ex:
    esiti = list(ex.map(uno, lavori))

mancanti = [list(map(str, l)) for l, ok, err in esiti if not ok and err is None]
errori = [(list(map(str, l)), err) for l, ok, err in esiti if err]
ris = {
    "file_richiesti": len(lavori),
    "file_presenti": sum(1 for _, ok, _ in esiti if ok),
    "mesi_assenti_404": mancanti,
    "errori": errori,
    "checksum_mancanti": list(dati.CHECKSUM_MANCANTI),
}
imp_ada = dati.registra_impronte("ADAUSDT")
imp_btc = dati.registra_impronte("BTCUSDT")
ris["impronte_ADAUSDT"] = len(imp_ada)
ris["impronte_BTCUSDT"] = len(imp_btc)
out = Path(__file__).resolve().parents[4] / "research" / "data" / "insample" / "ADAUSDT" / "scarico.json"
out.write_text(json.dumps(ris, indent=1), encoding="utf-8")
print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in ris.items()}))
print("assenti:", mancanti[:20])
print("errori:", errori[:5])
