"""Controllo dopo la prova 40: ci sono le date di pagamento per tutti gli anni? (`P040b_anni_senza_date.md`, scritto prima di guardare)

    python -m stock.prove.p040b           # gira su GitHub (azioni-ricerca): usa i dividendi già scaricati dal lavoro della prova 40

**Non è una prova**: conta i dividendi con la data di pagamento per anno contro quelli dell'archivio (data di stacco), e solo sugli anni
con dati legge la regola della prova 40. Scrive `P040b_risultati.md`.
"""
from __future__ import annotations

import math
from datetime import UTC, datetime

import numpy as np
import pandas as pd

from stock.dati import archivio
from stock.prove import p040
from stock.prove.p001 import QUI
from stock.prove.p035 import sr, tot


def main():
    f = p040.cartella() / "dividendi.csv.gz"
    if not f.exists():
        raise SystemExit("manca la memoria del lavoro della prova 40 (dividendi.csv.gz)")
    div = pd.read_csv(f, dtype={"simbolo": str}, keep_default_na=False, parse_dates=["stacco", "pagamento"])
    con_data = div.groupby(div["pagamento"].dt.year).size()
    stacchi = {}
    for s in sorted(set(div["simbolo"])):
        az = archivio.carica(s, p040.TIPO_AZ)
        if az is None or az.empty:
            continue
        for d in az.loc[az["tipo"] == "dividendo", "data"]:
            y = pd.Timestamp(d).year
            stacchi[y] = stacchi.get(y, 0) + 1
    anni = sorted(set(con_data.index) | set(stacchi))
    righe = [f"| {y} | {int(con_data.get(y, 0))} | {stacchi.get(y, 0)} | "
             f"{'sì' if con_data.get(y, 0) >= 0.5 * max(stacchi.get(y, 0), 1) else '**no**'} |" for y in anni if 2015 <= y <= 2024]
    con = [y for y in anni if 2015 <= y <= 2024 and con_data.get(y, 0) >= 0.5 * max(stacchi.get(y, 0), 1)]
    c = p040.calcola()
    w, r, prezzo, cal = c["w"], c["r"], c["prezzo"], c["calendario"]
    lettura = "nessun anno con dati"
    if con:
        primo_anno = min(con)
        giorni = [g for g in cal if g.year >= primo_anno]
        inizio = giorni[p040.FINESTRA] if len(giorni) > p040.FINESTRA else None
        if inizio is not None:
            rr, ww = r[r.index >= inizio], w[w.index >= inizio]
            s1, s0 = rr[ww == 1], rr[ww == 0]
            d = s1.mean() - s0.mean()
            t = d / math.sqrt(s1.var(ddof=1) / len(s1) + s0.var(ddof=1) / len(s0))
            g = p040.conto(ww, rr, prezzo)
            lettura = (f"dal {inizio} (primo anno con dati {primo_anno}, più 252 giorni per la prima mediana): giorni dentro "
                       f"{len(s1)} su {len(rr)} ({len(s1) / len(rr):.0%}); SPY nei giorni sopra la mediana {s1.mean() * 1e4:+.1f} punti "
                       f"base, negli altri {s0.mean() * 1e4:+.1f}, **differenza {d * 1e4:+.1f} (t {t:.2f})**; la regola con i costi "
                       f"Sharpe {sr(g):.2f} ({tot(g):+.1%}) contro lo SPY {sr(rr):.2f} ({tot(rr):+.1%})")
    testo = ["# Controllo dopo la prova 40 — le date di pagamento anno per anno", "",
             f"Calcolato da `python -m stock.prove.p040b` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con il metodo di "
             "`P040b_anni_senza_date.md` (scritto prima di guardare i dati). **Non è una prova**: la prova 40 resta bocciata.", "",
             "| Anno | Dividendi con la data di pagamento (per anno di pagamento) | Dividendi nell'archivio (per anno di stacco) | Anno con dati |",
             "|---|---|---|---|", *righe, "", f"**Sugli anni con dati (da leggere):** {lettura}."]
    (QUI / "P040b_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[4:]))


if __name__ == "__main__":
    main()
