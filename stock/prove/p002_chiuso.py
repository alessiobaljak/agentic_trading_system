"""La prova 2 nel periodo chiuso, per QQQ (`P002_zona_di_rumore.md`, ultima sezione; sì del proprietario del 24
ottobre 2026: «sì, apri il periodo chiuso per QQQ»). Si lancia UNA volta.

I prezzi del periodo chiuso stanno in tipi d'archivio a parte (`*_chiuso`), per non mischiarli con la ricerca.
Novembre e dicembre 2024 servono solo alla fascia dei 14 giorni e alla chiusura di ieri: le decisioni partono dal
2 gennaio 2025.

    python -m stock.prove.p002_chiuso     # scrive stock/prove/P002_chiuso.md
"""
from __future__ import annotations

from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli
from stock.dati.integrazioni import azioni_complete
from stock.dati.yahoo import eventi
from stock.dati.integrazioni import confronta_dividendi
from stock.prove.p001 import CAPITALE, IB_FISSO, MEZZO_SCARTO, PB, QUI, annuo, rendimenti_giornalieri, salva_serie
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.motore import simula
from stock.strategie import ultima_mezzora as um
from stock.strategie import zona_di_rumore as zr

INIZIO_DATI = datetime(2024, 11, 1, 4, tzinfo=UTC)
FINE = datetime(2026, 10, 1, 3, 59, tzinfo=UTC)      # fino al 30 settembre 2026 compreso (la barra del 1 ottobre è alle 04:00 UTC)
PRIMO = date(2025, 1, 2)
ULTIMO = date(2026, 9, 30)
TRIMESTRI = [(date(2025, 1, 1), date(2025, 4, 1)), (date(2025, 4, 1), date(2025, 7, 1)), (date(2025, 7, 1), date(2025, 10, 1)),
             (date(2025, 10, 1), date(2026, 1, 1)), (date(2026, 1, 1), date(2026, 4, 1)), (date(2026, 4, 1), date(2026, 7, 1)),
             (date(2026, 7, 1), date(2026, 10, 1))]


def scarica(simbolo: str) -> None:
    if archivio.carica(simbolo, "1Min_raw_chiuso") is None:
        archivio.salva(alpaca.barre(simbolo, "1Min", INIZIO_DATI, FINE), simbolo, "1Min_raw_chiuso")
    if archivio.carica(simbolo, "1Day_raw_chiuso") is None:
        archivio.salva(alpaca.barre(simbolo, "1Day", INIZIO_DATI, FINE), simbolo, "1Day_raw_chiuso")
        archivio.salva(alpaca.azioni_societarie(simbolo, INIZIO_DATI, FINE), simbolo, "azioni_chiuso")


def tenere(simbolo: str) -> pd.Series:
    raw = archivio.carica(simbolo, "1Day_raw_chiuso")
    az = azioni_complete(simbolo, archivio.carica(simbolo, "azioni_chiuso"))
    rett = raw["close"] * controlli.rettifica(raw, az)
    s = pd.Series(rett.to_numpy(), index=pd.Index(controlli.date_ny(raw.index)))
    s = s[(s.index >= date(2024, 12, 31)) & (s.index <= ULTIMO)]
    return s.pct_change().dropna()


def main():
    cal = alpaca.calendario("2024-11-01", "2026-09-30")
    controlli_testo = []
    for s in ("QQQ", "SPY"):
        scarica(s)
        raw = archivio.carica(s, "1Day_raw_chiuso")
        az = archivio.carica(s, "azioni_chiuso")
        mi = archivio.carica(s, "1Min_raw_chiuso")
        p_min, riep = controlli.controlla_minuti(mi, cal)
        p = (controlli.controlla_barre(raw) + controlli.controlla_giorni(raw, cal) + controlli.controlla_salti(raw, az)
             + controlli.controlla_cadenza_dividendi(az) + controlli.controlla_barre(mi) + p_min)
        div_y, fr_y = eventi(s, "2024-11-01", "2026-09-30")
        diff = confronta_dividendi(az, div_y, fr_y)
        controlli_testo.append(f"* {s}: {len(raw)} giorni, {riep['dentro']} minuti di seduta; problemi: "
                               + ("; ".join(f"{x['quando']} {x['controllo']} ({x['dettaglio']})" for x in p) or "nessuno")
                               + "; dividendi Alpaca/Yahoo: "
                               + ("; ".join(f"{d['data']} {d['tipo']}" for d in diff) or "uguali"))
    print("\n".join(controlli_testo), flush=True)

    minuti = archivio.carica("QQQ", "1Min_raw_chiuso")
    seduta = um.solo_seduta(minuti, cal)
    problemi, _ = controlli.controlla_minuti(minuti, cal)
    esclusi = {date.fromisoformat(p["quando"]) for p in problemi if p["controllo"] == "minuti mancanti"}
    seg = zr.prepara(seduta, cal, esclusi)
    prima = np.array(seduta.index.tz_convert("America/New_York").date) < PRIMO
    for k in ("decisione", "uscita"):
        seg[k] = seg[k] & ~prima
    costi = Costi(mezzo_scarto=MEZZO_SCARTO["QQQ"], slittamento=0.5 * PB, **IB_FISSO)
    out = {}
    for nome, c in (("costi", costi), ("costi doppi", costi.raddoppiati()), ("senza costi", Costi())):
        r = simula(seduta, zr.strategia(seg), c, capitale=CAPITALE)
        g = rendimenti_giornalieri(r.valore, CAPITALE)
        out[nome] = {"r": r, "g": g[(g.index >= PRIMO) & (g.index <= ULTIMO)]}
    gc = out["costi"]["g"]
    salva_serie("P002_QQQ_chiuso", gc)
    sr = annuo(asticella.sharpe(gc))
    sr2 = annuo(asticella.sharpe(out["costi doppi"]["g"]))
    sr_spy, sr_qqq = annuo(asticella.sharpe(tenere("SPY"))), annuo(asticella.sharpe(tenere("QQQ")))
    q = [float((1 + gc[(gc.index >= a) & (gc.index < b)]).prod() - 1) for a, b in TRIMESTRI]
    e = out["costi"]["r"].esecuzioni
    tot = lambda n: out[n]["r"].valore.iloc[-1] / CAPITALE - 1  # noqa: E731
    c1, c2, c3 = sr > max(sr_spy, sr_qqq), sr2 > 0, sum(x > 0 for x in q) >= 4
    righe = ["# Prova 2 — il periodo chiuso (QQQ)", "",
             f"Calcolato UNA volta da `python -m stock.prove.p002_chiuso` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC, dopo il sì del "
             "proprietario del 24 ottobre 2026. Regole ed esame scritti prima (`P002_zona_di_rumore.md`). Giorni dal "
             f"{gc.index.min()} al {gc.index.max()} ({len(gc)}).", "",
             "## I controlli dei prezzi del periodo", ""] + controlli_testo + ["",
             "## Il risultato", "",
             "| | QQQ |", "|---|---|",
             f"| Giorni con almeno un ordine eseguito | {e['t'].dt.tz_convert('America/New_York').dt.date.nunique()} |",
             f"| Ordini eseguiti / rifiutati | {len(e)} / {out['costi']['r'].rifiutati} |",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot('senza costi'):+.1%} / {tot('costi'):+.1%} / {tot('costi doppi'):+.1%} |",
             f"| Sharpe annuo senza costi | {annuo(asticella.sharpe(out['senza costi']['g'])):.2f} |",
             f"| Sharpe annuo del comprare e tenere lo SPY / QQQ | {sr_spy:.2f} / {sr_qqq:.2f} |",
             f"| **1.** Sharpe annuo con i costi (deve battere tutti e due) | {sr:.2f} → {'sì' if c1 else 'no'} |",
             f"| **2.** Sharpe annuo con i costi doppi (> 0) | {sr2:.2f} → {'sì' if c2 else 'no'} |",
             f"| **3.** Trimestri in guadagno (almeno 4 su 7) | {sum(x > 0 for x in q)} su 7 ({', '.join(f'{x:+.1%}' for x in q)}) → {'sì' if c3 else 'no'} |",
             f"| Perdita massima dal picco, con i costi | {((1 + gc).cumprod() / (1 + gc).cumprod().cummax() - 1).min():.1%} |",
             f"| **Esito** | **{'passa il periodo chiuso' if c1 and c2 and c3 else 'bocciata nel periodo chiuso'}** |"]
    (QUI / "P002_chiuso.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
