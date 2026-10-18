"""Passo 1: quanta parte della costruzione resta ammessa ai segnali, per timeframe e riscaldamento.

Dalla correzione della sezione 9.6 (17 ottobre 2026, appendice 3, punto 6) un buco solo nel mark non toglie
la candela last: il mark mancante si sostituisce con il last (dati.serie_3_con_conteggi, che conta le
candele sostituite). Restano buchi del motore solo le candele last mancanti. Si contano solo candele (nessun prezzo, nessun risultato): quante candele della costruzione hanno
almeno w candele dall'inizio del loro tratto senza buchi, per alcuni riscaldamenti tipici del catalogo
(42 = ATR 14; 60 = EMA 20; 150 = EMA 50; 300 = EMA 100; 600 = EMA 200; 542 = ATR percentile).
Esito in data/insample/BTCUSDT/passo1_tratti.json.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))

from research.src import dati  # noqa: E402

TIMEFRAME = ("15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d")
RISCALDAMENTI = (42, 60, 150, 300, 542, 600)
USCITA = dati.RADICE_DEFAULT / "data" / "insample" / "BTCUSDT" / "passo1_tratti.json"


def main() -> None:
    out = {}
    for tf in TIMEFRAME:
        s, conteggi = dati.serie_3_con_conteggi("BTCUSDT", tf, date(2020, 1, 1), date(2022, 9, 30))
        ts = np.asarray(s.ts)
        inizi = s.inizi_dei_tratti()
        pos = np.arange(len(ts)) - inizi[np.searchsorted(inizi, np.arange(len(ts)), side="right") - 1]
        out[tf] = {
            "candele": int(len(ts)),
            "mark_sostituite": conteggi["mark_sostituite"],
            "giorni_mark_sostituiti": conteggi["giorni_mark_sostituiti"],
            "mark_senza_last": conteggi["mark_senza_last"],
            "tratti": [datetime.fromtimestamp(int(ts[i]) / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
                       for i in inizi],
            "quota_ammessa_pct": {str(w): round(100 * float(np.mean(pos >= w)), 1) for w in RISCALDAMENTI},
        }
    USCITA.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
