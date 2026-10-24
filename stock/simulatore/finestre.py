"""Le finestre che avanzano (`METODO.md`, sezione 4) e la difesa del periodo chiuso.

Le regole si scelgono su `mesi_scelta` mesi e si provano sui `mesi_prova` dopo; poi si avanza di
`passo` mesi. Il periodo chiuso (dal 1 gennaio 2025, approvato dal proprietario il 24 ottobre 2026)
non entra in nessuna finestra di ricerca.
"""
from __future__ import annotations

from datetime import date

import pandas as pd


class PeriodoChiuso(ValueError):
    pass


def controlla_periodo(fine: date, chiuso_dal: date) -> None:
    if pd.Timestamp(fine) >= pd.Timestamp(chiuso_dal):
        raise PeriodoChiuso(f"{fine} entra nel periodo chiuso (dal {chiuso_dal}): non si guarda")


def finestre(inizio: date, fine: date, chiuso_dal: date, mesi_scelta: int = 12, mesi_prova: int = 3,
             passo: int = 3) -> list[dict]:
    """Elenco di finestre {scelta: (da, a), prova: (da, a)}, con `a` escluso. `fine` (esclusa) non
    può superare l'inizio del periodo chiuso. L'ultima prova che non sta tutta prima di `fine` non
    si fa."""
    controlla_periodo(pd.Timestamp(fine) - pd.Timedelta(days=1), chiuso_dal)
    out = []
    t = pd.Timestamp(inizio)
    fine = pd.Timestamp(fine)
    while True:
        s_a = t + pd.DateOffset(months=mesi_scelta)
        p_a = s_a + pd.DateOffset(months=mesi_prova)
        if p_a > fine:
            break
        out.append({"scelta": (t.date(), s_a.date()), "prova": (s_a.date(), p_a.date())})
        t = t + pd.DateOffset(months=passo)
    return out
