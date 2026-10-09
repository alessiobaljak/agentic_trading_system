"""Fase 0, punto 2: scarico dei dati in-sample di XRPUSDT (last, mark, funding) e di BTCUSDT (solo last).

Solo i mesi dal 2020-01 al 2023-12: il caricatore rifiuta da solo le date oltre il 2023-12-31.
I file si costruiscono per nome (nessun elenco remoto). Stampa i mesi mancanti e i CHECKSUM mancanti.
"""
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import date

from research.src import dati

TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO, FINE = date(2020, 1, 1), date(2023, 12, 31)

lavori = []
for tf in TF:
    lavori.append(("XRPUSDT", "klines", tf))
    lavori.append(("XRPUSDT", "markPriceKlines", tf))
    lavori.append(("BTCUSDT", "klines", tf))
lavori.append(("XRPUSDT", "fundingRate", None))


def fai(lavoro):
    simbolo, tipo, tf = lavoro
    esito = {}
    for anno, mese in dati.mesi_del_periodo(INIZIO, FINE):
        for tentativo in range(4):
            try:
                p = dati.scarica_mese(simbolo, tipo, tf, anno, mese)
                break
            except dati.IntegritaFallita:
                raise
            except Exception as e:  # rete: riprova
                if tentativo == 3:
                    raise
        esito[f"{anno:04d}-{mese:02d}"] = p is not None
    mancanti = [k for k, v in esito.items() if not v]
    return f"{simbolo}/{tipo}/{tf}", mancanti


with ThreadPoolExecutor(max_workers=8) as ex:
    risultati = list(ex.map(fai, lavori))

uscita = json.dumps({"mesi_mancanti": dict(risultati), "checksum_mancanti": dati.CHECKSUM_MANCANTI}, indent=1)
(dati.RADICE_DEFAULT / "data" / "insample" / "XRPUSDT" / "scarico.json").write_text(uscita + "\n")
print(uscita)
