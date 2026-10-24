"""Calcolo della prova 1 (`P001_ultima_mezzora.md`): regole lì, scritte prima.

    python -m stock.prove.p001     # scrive stock/prove/P001_risultati.md
"""
from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli
from stock.dati.integrazioni import azioni_complete
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.motore import simula
from stock.strategie import ultima_mezzora as um

NY = "America/New_York"
QUI = Path(__file__).resolve().parent
CAPITALE = 100_000.0
PB = 1e-4
MEZZO_SCARTO = {"SPY": 0.37 / 2 * PB, "QQQ": 0.56 / 2 * PB}     # stock/dati/ESITO_CONTROLLI.md
IB_FISSO = dict(per_azione=0.005, minima=1.0, massima_percentuale=0.01)   # da verificare sul listino


def rendimenti_giornalieri(valore: pd.Series, capitale: float) -> pd.Series:
    giorni = pd.Index(valore.index.tz_convert(NY).date)
    v = pd.Series(valore.to_numpy(), index=giorni).groupby(level=0).last()
    return v / v.shift(1).fillna(capitale) - 1


def comprare_e_tenere_spy(dal: date, al: date) -> pd.Series:
    raw = archivio.carica("SPY", "1Day_raw")
    az = azioni_complete("SPY", archivio.carica("SPY", "azioni"))
    rett = raw["close"] * controlli.rettifica(raw, az)
    s = pd.Series(rett.to_numpy(), index=pd.Index(controlli.date_ny(raw.index)))
    s = s[(s.index >= dal) & (s.index <= al)]
    return s.pct_change().dropna()


def salva_serie(nome: str, g: pd.Series) -> None:
    """I rendimenti giornalieri con i costi di ogni prova: servono al conto dell'asticella delle prove dopo.
    Sono risultati nostri, non prezzi: si committano."""
    (QUI / "serie").mkdir(exist_ok=True)
    g.rename("rendimento").rename_axis("giorno").to_csv(QUI / "serie" / f"{nome}.csv")


def carica_serie() -> dict[str, pd.Series]:
    out = {}
    for f in sorted((QUI / "serie").glob("*.csv")):
        x = pd.read_csv(f, index_col=0)["rendimento"]
        x.index = pd.to_datetime(x.index).date
        out[f.stem] = x
    return out


def comprare_e_tenere(simbolo: str, dal: date, al: date) -> pd.Series:
    raw = archivio.carica(simbolo, "1Day_raw")
    az = azioni_complete(simbolo, archivio.carica(simbolo, "azioni"))
    rett = raw["close"] * controlli.rettifica(raw, az)
    s = pd.Series(rett.to_numpy(), index=pd.Index(controlli.date_ny(raw.index)))
    s = s[(s.index >= dal) & (s.index <= al)]
    return s.pct_change().dropna()


def annuo(sr_giorno: float) -> float:
    return sr_giorno * np.sqrt(252)


def main():
    cal = alpaca.calendario("2016-01-01", "2024-12-31")
    finestre_prova = [f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))]
    risultati, serie = {}, {}
    for s in ("SPY", "QQQ"):
        minuti = archivio.carica(s, "1Min_raw")
        seduta = um.solo_seduta(minuti, cal)
        problemi, _ = controlli.controlla_minuti(minuti, cal)
        esclusi = {date.fromisoformat(p["quando"]) for p in problemi if p["controllo"] == "minuti mancanti"}
        seg = um.prepara(seduta, cal, esclusi)
        costi = Costi(mezzo_scarto=MEZZO_SCARTO[s], slittamento=0.5 * PB, **IB_FISSO)
        out = {}
        for nome, c in (("costi", costi), ("costi doppi", costi.raddoppiati()), ("senza costi", Costi())):
            r = simula(seduta, um.strategia(seg), c, capitale=CAPITALE)
            g = rendimenti_giornalieri(r.valore, CAPITALE)
            out[nome] = {"r": r, "g": g}
            print(s, nome, f"{r.valore.iloc[-1]:.0f}", flush=True)
        risultati[s] = {"out": out, "esclusi": sorted(esclusi), "segnali": int((~np.isnan(seg["direzione"])).sum()),
                        "zero": int((seg["direzione"] == 0).sum())}
        serie[s] = out["costi"]["g"]
        salva_serie(f"P001_{s}", out["costi"]["g"])
    g0 = min(x.index.min() for x in serie.values())
    g1 = max(x.index.max() for x in serie.values())
    bh = comprare_e_tenere_spy(g0, g1)
    sr_bh = annuo(asticella.sharpe(bh))
    righe = ["# Prova 1 — risultati", "",
             f"Calcolato da `python -m stock.prove.p001` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             "`P001_ultima_mezzora.md` (committate prima). Periodo dal {} al {}.".format(g0, g1), "",
             f"**L'asticella:** comprare e tenere lo SPY (con i dividendi), Sharpe annuo **{sr_bh:.2f}** sugli stessi giorni.", "",
             "| | SPY | QQQ |", "|---|---|---|"]
    tab = {}
    for s in ("SPY", "QQQ"):
        R = risultati[s]
        o = R["out"]
        rc, gc = o["costi"]["r"], o["costi"]["g"]
        q = []
        for a, b in finestre_prova:
            x = gc[(gc.index >= a) & (gc.index < b)]
            q.append(float((1 + x).prod() - 1))
        ast = asticella.sharpe_corretto(gc, serie)
        uscite = rc.esecuzioni[rc.esecuzioni.etichetta == "ingresso"]
        tab[s] = {
            "Operazioni (giorni con ingresso)": f"{len(uscite)}",
            "Ordini rifiutati": f"{rc.rifiutati}",
            "Segnali a zero (niente operazione)": f"{R['zero']}",
            "Giorni esclusi": ", ".join(map(str, R["esclusi"])) or "nessuno",
            "Guadagno totale, senza costi": f"{o['senza costi']['r'].valore.iloc[-1] / CAPITALE - 1:+.1%}",
            "Guadagno totale, con i costi": f"{rc.valore.iloc[-1] / CAPITALE - 1:+.1%}",
            "Guadagno totale, costi doppi": f"{o['costi doppi']['r'].valore.iloc[-1] / CAPITALE - 1:+.1%}",
            "Costi pagati (commissioni + scarto)": f"{rc.commissioni:,.0f} + {rc.costo_scarto:,.0f} dollari",
            "Sharpe annuo, senza costi": f"{annuo(asticella.sharpe(o['senza costi']['g'])):.2f}",
            "**1.** Sharpe annuo con i costi (contro {:.2f})".format(sr_bh): f"{annuo(asticella.sharpe(gc)):.2f}",
            "**2.** Sharpe corretto per i tentativi (soglia 0,95)": f"{ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']})",
            "t dello Sharpe (da leggere, contro 3)": f"{ast['t_sharpe']:.2f}",
            "**3.** Sharpe annuo, costi doppi (deve essere > 0)": f"{annuo(asticella.sharpe(o['costi doppi']['g'])):.2f}",
            "**4.** Trimestri in guadagno (almeno 60%)": f"{sum(x > 0 for x in q)} su {len(q)} ({sum(x > 0 for x in q) / len(q):.0%})",
            "Perdita massima dal picco, con i costi": f"{((1 + gc).cumprod() / (1 + gc).cumprod().cummax() - 1).min():.1%}",
        }
        passa = (annuo(asticella.sharpe(gc)) > sr_bh and ast["sharpe_corretto"] >= 0.95
                 and asticella.sharpe(o["costi doppi"]["g"]) > 0 and sum(x > 0 for x in q) / len(q) >= 0.6)
        tab[s]["**Esito**"] = "**passa la ricerca**" if passa else "**bocciata**"
    for k in tab["SPY"]:
        righe.append(f"| {k} | {tab['SPY'][k]} | {tab['QQQ'][k]} |")
    (QUI / "P001_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
