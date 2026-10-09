"""Fase 0, punto 2: scarica i dati in-sample di DOGEUSDT (e le candele last di BTCUSDT come riferimento).

Solo fino al 2023-12-31 (il caricatore rifiuta il resto). Mesi dal primo mese di dati della
scheda (2020-07). Il CHECKSUM remoto si controlla a ogni file (scarico di rete). Un errore di
rete su un mese si riprova fino a 5 volte; tutto si scrive in data/insample/DOGEUSDT/scarico.txt.
"""
import sys
import time
import traceback
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402

TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO, FINE = date(2020, 7, 1), date(2023, 12, 31)
LOG = Path(__file__).resolve().parents[4] / "research" / "data" / "insample" / "DOGEUSDT" / "scarico.txt"


def scrivi(t):
    with open(LOG, "a") as f:
        f.write(t + "\n")


def mese(simbolo, tipo, tf, a, m):
    for prova in range(5):
        try:
            return dati.scarica_mese(simbolo, tipo, tf, a, m)
        except dati.IntegritaFallita:
            raise
        except Exception as e:  # rete
            scrivi(f"errore {simbolo} {tipo} {tf} {a}-{m:02d} prova {prova}: {e!r}")
            time.sleep(2 ** prova)
    raise RuntimeError(f"scarico fallito {simbolo} {tipo} {tf} {a}-{m:02d}")


lavori = [("DOGEUSDT", t, tf) for tf in TF for t in ("klines", "markPriceKlines")]
lavori += [("DOGEUSDT", "fundingRate", None)] + [("BTCUSDT", "klines", tf) for tf in TF]
dati.azzera_checksum_mancanti()
try:
    for simbolo, tipo, tf in lavori:
        n = sum(1 for a, m in dati.mesi_del_periodo(INIZIO, FINE) if mese(simbolo, tipo, tf, a, m) is not None)
        scrivi(f"{simbolo} {tipo} {tf}: {n} file")
    scrivi(f"CHECKSUM mancanti: {len(dati.CHECKSUM_MANCANTI)} {dati.CHECKSUM_MANCANTI}")
    scrivi("FINE")
except Exception:
    scrivi(traceback.format_exc())
    scrivi("FALLITO")
