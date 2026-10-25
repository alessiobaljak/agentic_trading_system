"""Calcolo della prova 22 (`P022_inversione_apertura.md`): regole lì, scritte prima.

    python -m stock.prove.p022     # scrive stock/prove/P022_risultati.md
"""
from __future__ import annotations

from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli
from stock.prove.p001 import (CAPITALE, IB_FISSO, MEZZO_SCARTO, PB, QUI, annuo, carica_serie, comprare_e_tenere,
                              rendimenti_giornalieri, salva_serie)
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.motore import simula
from stock.strategie import inversione as inv
from stock.strategie import ultima_mezzora as um


def operazioni(esecuzioni: pd.DataFrame) -> pd.DataFrame:
    """Ogni ingresso con la sua uscita: lato, giorno e guadagno netto (prezzi con scarto e slittamento, meno le commissioni)."""
    out, aperta = [], None
    for r in esecuzioni.itertuples():
        if r.etichetta == "ingresso":
            aperta = r
        elif aperta is not None:
            segno = np.sign(aperta.quantita)
            netto = segno * (r.prezzo - aperta.prezzo) / aperta.prezzo - \
                (aperta.commissione + r.commissione) / (abs(aperta.quantita) * aperta.prezzo)
            out.append({"giorno": aperta.t.tz_convert(inv.NY).date(), "lato": segno, "uscita": r.etichetta, "netto": netto})
            aperta = None
    return pd.DataFrame(out, columns=["giorno", "lato", "uscita", "netto"])


def media_t(x: pd.Series) -> str:
    if len(x) < 2:
        return "—"
    return f"{x.mean():+.3%} (t {x.mean() / x.std(ddof=1) * np.sqrt(len(x)):.1f}, {len(x)})"


def main():
    cal = alpaca.calendario("2016-01-01", "2024-12-31")
    finestre_prova = [f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))]
    ris = {}
    for s in ("SPY", "QQQ"):
        minuti = archivio.carica(s, "1Min_raw")
        seduta = um.solo_seduta(minuti, cal)
        problemi, _ = controlli.controlla_minuti(minuti, cal)
        esclusi = {date.fromisoformat(p["quando"]) for p in problemi if p["controllo"] == "minuti mancanti"}
        costi = Costi(mezzo_scarto=MEZZO_SCARTO[s], slittamento=0.5 * PB, **IB_FISSO)
        seg = inv.prepara(seduta, cal, esclusi, inv.PRINCIPALE)
        out = {}
        for nome, c in (("costi", costi), ("costi doppi", costi.raddoppiati()), ("senza costi", Costi())):
            r = simula(seduta, inv.strategia(seg), c, capitale=CAPITALE)
            out[nome] = (r, rendimenti_giornalieri(r.valore, CAPITALE))
        var = {}
        for nome, regole in (("senza zone", inv.SENZA_ZONE), ("orario largo", inv.ORARIO_LARGO)):
            sv = inv.prepara(seduta, cal, esclusi, regole)
            r = simula(seduta, inv.strategia(sv), costi, capitale=CAPITALE)
            var[nome] = (annuo(asticella.sharpe(rendimenti_giornalieri(r.valore, CAPITALE))), operazioni(r.esecuzioni))
        salva_serie(f"P022_{s}", out["costi"][1])
        ris[s] = (out, var)
        print(s, f"{out['costi'][0].valore.iloc[-1]:.0f}", flush=True)
    tutte = carica_serie()
    righe = ["# Prova 22 — risultati", "",
             f"Calcolato da `python -m stock.prove.p022` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P022_inversione_apertura.md` (committate prima). Nel conto dell'asticella: {len(tutte)} serie.", "",
             "| | SPY | QQQ |", "|---|---|---|"]
    tab = {}
    for s in ("SPY", "QQQ"):
        out, var = ris[s]
        rc, gc = out["costi"]
        g0, g1 = gc.index.min(), gc.index.max()
        sr_spy = annuo(asticella.sharpe(comprare_e_tenere("SPY", g0, g1)))
        sr_suo = annuo(asticella.sharpe(comprare_e_tenere(s, g0, g1)))
        sr, sr2 = annuo(asticella.sharpe(gc)), annuo(asticella.sharpe(out["costi doppi"][1]))
        ast = asticella.sharpe_corretto(gc, tutte)
        q = [float((1 + gc[(gc.index >= a) & (gc.index < b)]).prod() - 1) for a, b in finestre_prova]
        quota = sum(x > 0 for x in q) / len(q)
        op = operazioni(rc.esecuzioni)
        anni = (1 + gc).groupby(pd.Index([d.year for d in gc.index])).prod() - 1
        passa = sr > max(sr_spy, sr_suo) and ast["sharpe_corretto"] >= 0.95 and sr2 > 0 and quota >= 0.6
        u = op["uscita"].value_counts()
        tab[s] = [f"{len(op)} (acquisti {(op.lato > 0).sum()}, vendite {(op.lato < 0).sum()})",
                  f"{u.get('stop', 0)} / {u.get('obiettivo', 0)} / {u.get('chiusura', 0)}",
                  f"{(op.netto > 0).mean():.0%}" if len(op) else "—",
                  media_t(op.netto),
                  f"{media_t(op.netto[op.lato > 0])} / {media_t(op.netto[op.lato < 0])}",
                  f"{out['senza costi'][0].valore.iloc[-1] / CAPITALE - 1:+.1%} / {rc.valore.iloc[-1] / CAPITALE - 1:+.1%} / "
                  f"{out['costi doppi'][0].valore.iloc[-1] / CAPITALE - 1:+.1%}",
                  f"{annuo(asticella.sharpe(out['senza costi'][1])):.2f}", f"{sr_spy:.2f} / {sr_suo:.2f}", f"{sr:.2f}",
                  f"{ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']})", f"{sr2:.2f}",
                  f"{sum(x > 0 for x in q)} su 32 ({quota:.0%})",
                  " ".join(f"{a}: {v:+.1%}" for a, v in anni.items()),
                  " / ".join(f"{var[n][0]:.2f}, {media_t(var[n][1].netto)}" for n in ("senza zone", "orario largo")),
                  f"**{'passa la ricerca' if passa else 'bocciata'}**"]
    nomi = ["Operazioni", "Uscite: stop / obiettivo / chiusura", "Operazioni in guadagno (con i costi)",
            "Guadagno medio a operazione con i costi (t, numero)", "Solo acquisti / solo vendite (da leggere)",
            "Guadagno senza costi / con i costi / costi doppi", "Sharpe annuo senza costi",
            "Sharpe del tenere lo SPY / lo stesso titolo", "**1.** Sharpe annuo con i costi",
            "**2.** Sharpe corretto (soglia 0,95)", "**3.** Sharpe con i costi doppi (> 0)",
            "**4.** Trimestri in guadagno (60%)", "Anno per anno (da leggere)",
            "Robustezza, Sharpe con i costi e guadagno a operazione: senza zone / orario largo (da leggere)", "**Esito**"]
    for j, nome in enumerate(nomi):
        righe.append(f"| {nome} | " + " | ".join(tab[s][j] for s in ("SPY", "QQQ")) + " |")
    (QUI / "P022_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
