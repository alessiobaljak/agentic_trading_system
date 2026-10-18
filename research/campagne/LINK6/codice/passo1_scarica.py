"""Passo 1, punto 3: scarica in data/insample/LINKUSDT/ le candele last e mark di tutti i timeframe
ammessi e lo storico del funding, solo fino al 2023-12-31, con il controllo del CHECKSUM di Binance.

Scrive l'avanzamento e l'esito in data/insample/LINKUSDT/passo1_scarico.txt (ultima riga: FINE o ERRORE).
Nessun prezzo viene letto o stampato: solo conteggi di file.
"""
import sys
import time
import traceback
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from research.src import dati  # noqa: E402

SIMBOLO = "LINKUSDT"
TIMEFRAME = ("15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d")
INIZIO = date(2020, 1, 1)  # il mese della prima candela; i mesi assenti (404) non si scrivono
FINE = date(2023, 12, 31)
AVANZAMENTO = dati.RADICE_DEFAULT / "data" / "insample" / SIMBOLO / "passo1_scarico.txt"


def scrivi(riga):
    AVANZAMENTO.parent.mkdir(parents=True, exist_ok=True)
    with AVANZAMENTO.open("a", encoding="utf-8") as f:
        f.write(riga + "\n")


def con_riprova(funzione, *argomenti):
    for attesa in (2, 4, 8, 16, None):
        try:
            return funzione(*argomenti)
        except dati.IntegritaFallita:
            raise
        except Exception as errore:  # errori di rete: si riprova
            if attesa is None:
                raise
            scrivi(f"  riprovo fra {attesa} s dopo: {type(errore).__name__}: {errore}")
            time.sleep(attesa)


def main():
    dati.azzera_checksum_mancanti()
    lavori = [(t, i) for t in ("klines", "markPriceKlines") for i in TIMEFRAME] + [("fundingRate", None)]
    totale = 0
    for tipo, intervallo in lavori:
        n = 0
        for anno, mese in dati.mesi_del_periodo(INIZIO, FINE):
            if con_riprova(dati.scarica_mese, SIMBOLO, tipo, intervallo, anno, mese) is not None:
                n += 1
        totale += n
        scrivi(f"{tipo} {intervallo or '-'}: {n} file")
    scrivi(f"file in totale: {totale}")
    scrivi(f"CHECKSUM mancanti: {len(dati.CHECKSUM_MANCANTI)}")
    for url in dati.CHECKSUM_MANCANTI:
        scrivi(f"  senza CHECKSUM: {url}")
    scrivi("FINE")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        scrivi(traceback.format_exc())
        scrivi("ERRORE")
