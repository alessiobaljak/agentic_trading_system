"""Passo 1, punto 2: scarica in data/insample/BTCUSDT, solo fino al 2023-12-31, le candele last e mark di
tutti i timeframe del catalogo e lo storico del funding, con il controllo del CHECKSUM di Binance.

Si parte dal 2019-09 (i futures su BTCUSDT esistono da settembre 2019, sezione 15): i mesi che l'archivio
non ha (404) si segnano come assenti. Avanzamento ed esito in data/insample/BTCUSDT/passo1_scarico.txt.
Un file gia' su disco non si riscarica: il comando si puo' rilanciare.
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))

from research.src import dati  # noqa: E402

SIMBOLO = "BTCUSDT"
TIMEFRAME = ("15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d")
INIZIO = date(2019, 9, 1)
FINE = date(2023, 12, 31)
USCITA = dati.RADICE_DEFAULT / "data" / "insample" / SIMBOLO / "passo1_scarico.txt"


def main() -> None:
    USCITA.parent.mkdir(parents=True, exist_ok=True)
    dati.azzera_checksum_mancanti()
    lavori = []
    for anno, mese in dati.mesi_del_periodo(INIZIO, FINE):
        for tipo in ("klines", "markPriceKlines"):
            for tf in TIMEFRAME:
                lavori.append((tipo, tf, anno, mese))
        lavori.append(("fundingRate", None, anno, mese))
    presenti, assenti, errori = [], [], []
    with open(USCITA, "w", encoding="utf-8") as out:
        out.write(f"file da controllare: {len(lavori)}\n")
        out.flush()
        with ThreadPoolExecutor(max_workers=8) as pool:
            futuri = {pool.submit(dati.scarica_mese, SIMBOLO, t, tf, a, m): (t, tf, a, m) for t, tf, a, m in lavori}
            for i, fut in enumerate(as_completed(futuri), 1):
                chiave = futuri[fut]
                try:
                    p = fut.result()
                    (presenti if p is not None else assenti).append(chiave)
                except Exception as e:  # registrato, non ignorato
                    errori.append((chiave, repr(e)))
                if i % 50 == 0:
                    out.write(f"{i}/{len(lavori)}\n")
                    out.flush()
        assenti_per_serie = {}
        for t, tf, a, m in sorted(assenti, key=lambda x: (x[0], str(x[1]), x[2], x[3])):
            assenti_per_serie.setdefault(f"{t}/{tf}", []).append(f"{a:04d}-{m:02d}")
        out.write(json.dumps({
            "presenti": len(presenti),
            "assenti": assenti_per_serie,
            "errori": errori,
            "checksum_mancanti": list(dati.CHECKSUM_MANCANTI),
        }, indent=1) + "\n")
        out.write("FINE\n" if not errori else "FINE CON ERRORI\n")


if __name__ == "__main__":
    main()
