"""Passo 0 del protocollo 4, punto 4: scarica in data/insample/ le candele last e mark di tutti i timeframe del
catalogo e lo storico del funding di LINKUSDT e delle 9 monete di controllo, dal 2020-01 al 2023-12, con il CHECKSUM
di Binance. Un file gia' su disco non si riscarica. Esito in research/passo0_4/scarico.json (non in git i dati).
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RADICE_REPO))

from research.src import dati  # noqa: E402

MONETE = ("LINKUSDT", "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "BNBUSDT", "LTCUSDT", "MATICUSDT",
          "BCHUSDT")
TIMEFRAME = ("15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d")
INIZIO, FINE = date(2020, 1, 1), date(2023, 12, 31)
USCITA = Path(__file__).resolve().parent / "scarico.json"


def main() -> None:
    dati.azzera_checksum_mancanti()
    lavori = []
    for s in MONETE:
        for anno, mese in dati.mesi_del_periodo(INIZIO, FINE):
            for tipo in ("klines", "markPriceKlines"):
                for tf in TIMEFRAME:
                    lavori.append((s, tipo, tf, anno, mese))
            lavori.append((s, "fundingRate", None, anno, mese))
    presenti, assenti, errori = [], [], []
    with ThreadPoolExecutor(max_workers=12) as pool:
        futuri = {pool.submit(dati.scarica_mese, s, t, tf, a, m, verifica_checksum=True): (s, t, tf, a, m)
                  for s, t, tf, a, m in lavori}
        for i, fut in enumerate(as_completed(futuri), 1):
            chiave = futuri[fut]
            try:
                (presenti if fut.result() is not None else assenti).append(chiave)
            except Exception as e:  # registrato, non ignorato
                errori.append([*map(str, chiave), repr(e)])
            if i % 500 == 0:
                print(f"{i}/{len(lavori)}", flush=True)
    per_moneta = {}
    for s, t, tf, a, m in assenti:
        per_moneta.setdefault(s, {}).setdefault(f"{t}/{tf}", []).append(f"{a:04d}-{m:02d}")
    USCITA.write_text(json.dumps({"file": len(lavori), "presenti": len(presenti), "assenti": per_moneta,
                                  "errori": errori,
                                  "checksum_mancanti": sorted(getattr(dati, "CHECKSUM_MANCANTI", []))},
                                 indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("fatto", len(presenti), "presenti,", sum(len(v) for d in per_moneta.values() for v in d.values()),
          "assenti,", len(errori), "errori", flush=True)


if __name__ == "__main__":
    main()
