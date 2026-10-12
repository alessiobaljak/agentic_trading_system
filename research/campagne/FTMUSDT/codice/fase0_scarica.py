"""Fase 0 punto 2: scarica i dati in-sample di FTMUSDT (last, mark, funding) e il last di BTCUSDT.

Solo fino al 2023-12-31 (il caricatore rifiuta il resto). Nessun elenco di file remoti:
un URL per mese, un 404 vuol dire mese assente.
"""
from datetime import date

from comune import PRIMO_GIORNO, SIMBOLO, dati

TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
FINE = date(2023, 12, 31)

for tf in TF:
    for tipo in ("klines", "markPriceKlines"):
        p = dati.scarica_periodo(SIMBOLO, tipo, tf, PRIMO_GIORNO, FINE)
        print(SIMBOLO, tipo, tf, len(p), flush=True)
p = dati.scarica_periodo(SIMBOLO, "fundingRate", None, PRIMO_GIORNO, FINE)
print(SIMBOLO, "fundingRate", len(p), flush=True)
for tf in TF:
    p = dati.scarica_periodo("BTCUSDT", "klines", tf, date(2020, 1, 1), FINE)
    print("BTCUSDT klines", tf, len(p), flush=True)
print("CHECKSUM mancanti:", len(dati.CHECKSUM_MANCANTI), sorted(dati.CHECKSUM_MANCANTI)[:20], flush=True)
