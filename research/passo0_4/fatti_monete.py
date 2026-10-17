"""Passo 0 del protocollo 4, punto 4: i fatti dei dati di LINKUSDT e delle 9 monete di controllo, solo
come conteggi (nessun prezzo, rendimento o misura dell'andamento): prima candela, buchi di last e mark,
candele mark sostituite dal last e candele in coda senza scambi (``dati.serie_4_con_conteggi``),
intervalli del funding, volume medio giornaliero 2023 (sui giorni presenti e sull'anno) con la fascia
di slippage, impronte SHA-256 dei file. Esito in ``research/passo0_4/fatti_monete.json``.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

RADICE_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RADICE_REPO))

from research.src import dati  # noqa: E402
from research.src.controllo4 import MONETE_CONTROLLO  # noqa: E402

TIMEFRAME = ("15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d")
USCITA = Path(__file__).resolve().parent / "fatti_monete.json"
FASCE = ((1_000_000_000, 0.0001), (200_000_000, 0.0002), (50_000_000, 0.0005), (0, 0.0010))


def fascia(volume: float) -> float:
    return next(s for soglia, s in FASCE if volume >= soglia)


def fatti(simbolo: str) -> dict:
    base = dati.fatti_passo1_3(simbolo)
    sostituzioni = {}
    for tf in TIMEFRAME:
        _, cont = dati.serie_4_con_conteggi(simbolo, tf, date(2020, 1, 1), dati.FINE_IN_SAMPLE)
        sostituzioni[tf] = {k: cont[k] for k in ("candele", "mark_sostituite", "giorni_mark_sostituiti",
                                                 "mark_senza_last", "candele_ferme_in_coda_tolte",
                                                 "intervalli_funding_ore")}
    vol = base["volume_medio_giornaliero_2023_usdt"]
    giorni = base["giorni_volume_2023"]
    sull_anno = vol * giorni / 365 if vol is not None else None
    impronte = dati.calcola_impronte(simbolo)
    return {"prima_candela": base["prima_candela"],
            "buchi": {tf: {t: len(base["timeframe"][tf][t]["buchi"]) for t in ("klines", "markPriceKlines")}
                      for tf in TIMEFRAME},
            "buchi_dettaglio_1h": {t: base["timeframe"]["1h"][t]["buchi"] for t in ("klines", "markPriceKlines")},
            "candele_costruzione_validazione": {tf: {t: [base["timeframe"][tf][t]["costruzione"],
                                                         base["timeframe"][tf][t]["validazione"]]
                                                     for t in ("klines", "markPriceKlines")} for tf in TIMEFRAME},
            "serie_4": sostituzioni,
            "intervalli_funding": base["intervalli_funding"],
            "volume_medio_giornaliero_2023_usdt": vol, "giorni_volume_2023": giorni,
            "volume_giornaliero_2023_sull_anno_usdt": sull_anno,
            "fascia_slippage": fascia(sull_anno) if sull_anno is not None else None,
            "file": len(impronte), "impronte": impronte}


def main() -> None:
    out = {}
    for simbolo in ("LINKUSDT", *MONETE_CONTROLLO):
        out[simbolo] = fatti(simbolo)
        x = out[simbolo]
        print(simbolo, x["prima_candela"], round((x["volume_giornaliero_2023_sull_anno_usdt"] or 0) / 1e6),
              x["fascia_slippage"], x["file"], flush=True)
    USCITA.write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
