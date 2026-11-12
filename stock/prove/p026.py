"""Calcolo della prova 26 (`P026_tendenza_altre_classi.md`): regole lì, scritte prima.

    python -m stock.prove.p026            # scrive stock/prove/P026_risultati.md
"""
from __future__ import annotations

from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.dati import archivio, controlli, yahoo
from stock.prove.p001 import CAPITALE, IB_FISSO, PB, QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import rendimenti
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.portafoglio import simula_conto
from stock.strategie.tendenza import SEDUTE, strategia_classi

FONDI = ["TLT", "IEF", "GLD", "DBC", "EFA", "EEM"]
COSTI = Costi(mezzo_scarto=2.5 * PB, slittamento=1 * PB, **IB_FISSO)


def carica_fondi(dal: str, al: str, tipo: str = "p026"):
    """Le barre di Yahoo (scaricate una volta, tenute fuori dal repository) e le chiusure rettificate per giorno."""
    cartella = archivio.cartella_dati() / "yahoo" / tipo
    cartella.mkdir(parents=True, exist_ok=True)
    barre, rett = {}, {}
    for s in FONDI:
        f = cartella / f"{s}.csv.gz"
        if f.exists():
            df = pd.read_csv(f, index_col=0)
            df.index = pd.to_datetime(df.index, utc=True).tz_convert("America/New_York")
        else:
            df = yahoo.prezzi(s, dal, al)
            df.to_csv(f)
        barre[s] = df[["open", "high", "low", "close", "dividendo", "frazionamento"]]
        rett[s] = pd.Series(df["rettificata"].to_numpy(), index=pd.Index(df.index.date))
    return barre, rett


def perdita_massima(g: pd.Series) -> float:
    v = (1 + g).cumprod()
    return float((v / v.cummax() - 1).min())


def esamina(barre, rett, cal, fino_a: date | None = None):
    out, diario = {}, []
    for nome, c in (("costi", COSTI), ("costi doppi", COSTI.raddoppiati()), ("senza costi", Costi())):
        r = simula_conto(barre, strategia_classi(FONDI, cal, rett, diario if nome == "costi" else None), c, capitale=CAPITALE)
        primo = r.esecuzioni["giorno"].min()
        out[nome] = (r, rendimenti(r.valore[r.valore.index >= primo]))
    return out, diario


def main():
    spy = archivio.carica("SPY", "1Day_raw")
    cal = sorted(d for d in controlli.date_ny(spy.index) if d <= date(2024, 12, 31))
    barre, rett = carica_fondi("2015-01-02", "2024-12-31")
    mancanti = {s: len(set(c for c in cal if c >= date(2015, 1, 2)) - set(rett[s].index)) for s in FONDI}
    out, diario = esamina(barre, rett, cal)
    parte, parte2, parte0 = out["costi"][1], out["costi doppi"][1], out["senza costi"][1]
    tutte = carica_serie()
    m = tutte["P025_miscela"]
    comuni = m.index.intersection(parte.index)
    m, p, p2 = m.loc[comuni], parte.loc[comuni], parte2.loc[comuni]
    nuova = 0.75 * m + 0.25 * p
    salva_serie("P026_tendenza_classi", parte)
    salva_serie("P026_miscela_nuova", nuova)
    tutte = carica_serie()
    a, b = comuni.min(), comuni.max()
    tenere = comprare_e_tenere("SPY", a, b)
    sr = lambda x: annuo(asticella.sharpe(x))  # noqa: E731
    corr = float(np.corrcoef(m, p)[0, 1])
    c1 = sr(p) > 0 and sr(p2) > 0
    c2 = corr < 0.3
    c3 = sr(nuova) > sr(m) and sr(nuova) > sr(tenere)
    ast = asticella.sharpe_corretto(nuova, tutte)
    anni = lambda x: " ".join(f"{y}: {v:+.1%}" for y, v in ((1 + x).groupby(pd.Index([d.year for d in x.index])).prod() - 1).items())  # noqa: E731
    tot = lambda x: (1 + x).prod() - 1  # noqa: E731
    soli = []
    for s in FONDI:                         # da leggere: ogni fondo da solo, senza costi, segnale di fine mese applicato dal mese dopo
        r = rett[s]
        g = r.pct_change()
        seg = (r / r.shift(SEDUTE) - 1 > 0)
        mesi = pd.PeriodIndex(pd.to_datetime(r.index), freq="M")
        ultimo = pd.Series(seg.to_numpy(), index=mesi).groupby(level=0).last()
        dentro = pd.Series([bool(ultimo.get(mm - 1, False)) for mm in mesi], index=r.index)
        x = (g * dentro).loc[a:b].dropna()
        soli.append(f"{s} {sr(x):.2f} (tenerlo {sr(g.loc[a:b].dropna()):.2f})")
    r = out["costi"][0]
    righe = ["# Prova 26 — risultati", "",
             f"Calcolato da `python -m stock.prove.p026` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P026_tendenza_altre_classi.md` (committate prima). Giorni in comune con la miscela della prova 25: dal {a} al {b} "
             f"({len(comuni)}). Nel conto dell'asticella: {len(tutte)} serie. Giorni di borsa senza il prezzo di Yahoo: {mancanti}. "
             f"Ordini eseguiti dalla parte nuova: {len(r.esecuzioni)}; costi pagati {r.commissioni + r.costo_scarto:,.0f} dollari; "
             f"decisioni {len(diario)}, fondi dentro in media {np.mean([len(d['dentro']) for d in diario]):.1f} su 6.", "",
             "| | Parte nuova (tendenza sulle altre classi) | Miscela della prova 25 | Miscela nuova (3/4 + 1/4) | Tenere lo SPY |",
             "|---|---|---|---|---|",
             f"| Guadagno totale | {tot(p):+.1%} | {tot(m):+.1%} | {tot(nuova):+.1%} | {tot(tenere):+.1%} |",
             f"| Sharpe annuo con i costi | {sr(p):.2f} (costi doppi {sr(p2):.2f}; senza costi {sr(parte0.loc[comuni]):.2f}) | {sr(m):.2f} | **{sr(nuova):.2f}** | {sr(tenere):.2f} |",
             f"| Perdita massima dal picco | {perdita_massima(p):.1%} | {perdita_massima(m):.1%} | {perdita_massima(nuova):.1%} | {perdita_massima(tenere):.1%} |",
             f"| Anno per anno | {anni(p)} | {anni(m)} | {anni(nuova)} | — |", "",
             f"* **1.** Sharpe della parte sopra zero, anche con i costi doppi: {sr(p):.2f} e {sr(p2):.2f} → {'sì' if c1 else 'no'}.",
             f"* **2.** Correlazione con la miscela sotto 0,3: {corr:.2f} → {'sì' if c2 else 'no'}.",
             f"* **3.** La miscela nuova ha lo Sharpe più alto della miscela ({sr(m):.2f}) e del tenere lo SPY ({sr(tenere):.2f}): "
             f"{sr(nuova):.2f} → {'sì' if c3 else 'no'}.",
             f"* Da leggere: Sharpe corretto della miscela nuova {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}).",
             "* Da leggere, ogni fondo da solo con la regola (senza costi, conto semplice): " + ", ".join(soli) + ".", "",
             f"**Esito: {'entra nella miscela (prima il revisore e il periodo chiuso)' if c1 and c2 and c3 else 'non entra nella miscela: bocciata'}**"]
    (QUI / "P026_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
