"""Calcolo della prova 3 (`P003_rimbalzo.md`): regole lì, scritte prima.

    python -m stock.prove.p003     # scrive stock/prove/P003_risultati.md
"""
from __future__ import annotations

import re
from datetime import UTC, date, datetime, timedelta

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli
from stock.dati.integrazioni import azioni_complete, valuta_scissioni
from stock.prove.p001 import CAPITALE, IB_FISSO, PB, QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.portafoglio import simula_conto
from stock.strategie.rimbalzo import strategia_rimbalzo, strategia_tenere_i_dieci
from stock.universo.costruisci import RINOMINATI

RADICE = QUI.parent


def scarti_misurati(percorso) -> dict[str, float]:
    """Le mediane dello scarto (in proporzione) dalla tabella dell'esito dei controlli."""
    out = {}
    for riga in open(percorso):
        m = re.match(r"\| (\S+) \|.*\| ([0-9.]+) \([0-9.]+\) punti base su", riga)
        if m:
            out[m.group(1)] = float(m.group(2)) * PB
    return out


def _apertura(simbolo: str, giorno: date, tipo: str) -> float | None:
    df = archivio.carica(simbolo, tipo)
    if df is None:
        df = alpaca.barre(simbolo, "1Day", datetime(2016, 1, 1, 5, tzinfo=UTC), datetime(2025, 1, 1, 5, tzinfo=UTC))
        archivio.salva(df, simbolo, tipo)
    if df.empty:
        return None
    g = pd.Index(controlli.date_ny(df.index))
    i = np.where(g == giorno)[0]
    return float(df["open"].iloc[i[0]]) if len(i) else None


def prepara_titolo(simbolo: str, fino: date, tipo_raw: str = "1Day_raw", tipo_az: str = "azioni"):
    """Le barre al giorno con le colonne dividendo e frazionamento, la chiusura rettificata, e le scissioni senza prezzo."""
    raw = archivio.carica(simbolo, tipo_raw)
    giorni = pd.Index(controlli.date_ny(raw.index))
    raw = raw[giorni <= fino]
    giorni = giorni[giorni <= fino]
    az = azioni_complete(simbolo, archivio.carica(simbolo, tipo_az))
    az, mancanti = valuta_scissioni(az, lambda s, d: _apertura(s, d, tipo_raw))
    div = az[az.tipo == "dividendo"].groupby("data")["importo"].sum() if not az.empty else pd.Series(dtype=float)
    fr = az[az.tipo == "frazionamento"].groupby("data")["rapporto"].prod() if not az.empty else pd.Series(dtype=float)
    df = raw[["open", "high", "low", "close"]].copy()
    df["dividendo"] = pd.Series(giorni.map(lambda d: div.get(d, 0.0)), index=raw.index)
    df["frazionamento"] = pd.Series(giorni.map(lambda d: fr.get(d, 1.0)), index=raw.index)
    rett = pd.Series((raw["close"] * controlli.rettifica(raw, az)).to_numpy(), index=giorni)
    return df, rett, mancanti


def rendimenti(valore: pd.Series) -> pd.Series:
    return valore / valore.shift(1).fillna(CAPITALE) - 1


def main():
    universo = pd.read_csv(RADICE / "universo" / "dieci_di_allora.csv")
    universo["simbolo"] = universo["simbolo"].replace(RINOMINATI)
    simboli = sorted(universo["simbolo"].unique())
    fino = date(2024, 12, 31)
    cal = list(alpaca.calendario("2016-01-01", "2024-12-31").index)
    barre, rett, mancanti = {}, {}, {}
    for s in simboli:
        barre[s], rett[s], m = prepara_titolo(s, fino)
        if m:
            mancanti[s] = m
    scarti = scarti_misurati(RADICE / "dati" / "ESITO_CONTROLLI_UNIVERSO.md")
    peggiore = max(scarti.values())
    senza_misura = [s for s in simboli if s not in scarti]

    def costi_per(fattore: float) -> dict[str, Costi]:
        base = {s: Costi(mezzo_scarto=scarti.get(s, peggiore) / 2, slittamento=0.5 * PB, **IB_FISSO) for s in simboli}
        if fattore == 0:
            return {s: Costi() for s in simboli}
        return base if fattore == 1 else {s: c.raddoppiati() for s, c in base.items()}

    out = {}
    for nome, f in (("costi", 1), ("costi doppi", 2), ("senza costi", 0)):
        out[nome] = simula_conto(barre, strategia_rimbalzo(universo, cal, rett), costi_per(f), capitale=CAPITALE)
        print(nome, f"{out[nome].valore.iloc[-1]:.0f}", flush=True)
    dieci = simula_conto(barre, strategia_tenere_i_dieci(universo, cal), costi_per(1), capitale=CAPITALE)

    # la serie parte dal primo giorno con una posizione (prima il conto è fermo, senza elenco)
    primo = out["costi"].esecuzioni["giorno"].min()
    taglia = lambda v: v[v.index >= primo]  # noqa: E731
    gc = rendimenti(taglia(out["costi"].valore))
    g2 = rendimenti(taglia(out["costi doppi"].valore))
    g0 = rendimenti(taglia(out["senza costi"].valore))
    gd = rendimenti(taglia(dieci.valore))
    salva_serie("P003_rimbalzo", gc)
    tutte = carica_serie()
    sr, sr2 = annuo(asticella.sharpe(gc)), annuo(asticella.sharpe(g2))
    sr_spy = annuo(asticella.sharpe(comprare_e_tenere("SPY", gc.index.min(), gc.index.max())))
    sr_dieci = annuo(asticella.sharpe(gd))
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= a) & (gc.index < b)]).prod() - 1)
         for a, b in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1)))]
    quota = sum(x > 0 for x in q) / len(q)
    r = out["costi"]
    passa = sr > max(sr_spy, sr_dieci) and ast["sharpe_corretto"] >= 0.95 and sr2 > 0 and quota >= 0.6
    tot = lambda v: v.iloc[-1] / CAPITALE - 1  # noqa: E731
    righe = ["# Prova 3 — risultati", "",
             f"Calcolato da `python -m stock.prove.p003` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di `P003_rimbalzo.md` "
             f"(committate prima). Dal {gc.index.min()} al {gc.index.max()} ({len(gc)} giorni). Nel conto dell'asticella: "
             + ", ".join(sorted(tutte)) + ".", "",
             f"* Titoli: {len(simboli)}; senza scarto misurato (si usa il più alto, {peggiore / PB:.2f} punti base): "
             + (", ".join(senza_misura) or "nessuno") + ".",
             "* Scissioni senza prezzo del titolo nuovo (non contate): " + (str(mancanti) if mancanti else "nessuna") + ".",
             f"* Ordini eseguiti {len(r.esecuzioni)}; non eseguiti perché il titolo non aveva la barra {r.senza_barra}; rifiutati "
             f"{r.rifiutati}; titoli rimasti in mano dopo l'uscita dal listino: {r.bloccati or 'nessuno'}.",
             f"* Costi pagati: commissioni {r.commissioni:,.0f}, scarto e slittamento {r.costo_scarto:,.0f} dollari; dividendi e "
             f"scissioni incassati {r.dividendi:,.0f}.", "",
             "| | Rimbalzo | Tenere le 10 | Tenere lo SPY |", "|---|---|---|---|",
             f"| Guadagno totale con i costi | {tot(taglia(r.valore)):+.1%} | {tot(taglia(dieci.valore)):+.1%} | — |",
             f"| Guadagno totale senza costi / costi doppi | {tot(taglia(out['senza costi'].valore)):+.1%} / "
             f"{tot(taglia(out['costi doppi'].valore)):+.1%} | — | — |",
             f"| Sharpe annuo senza costi | {annuo(asticella.sharpe(g0)):.2f} | — | — |",
             f"| **1.** Sharpe annuo con i costi (deve battere le altre due colonne) | {sr:.2f} | {sr_dieci:.2f} | {sr_spy:.2f} |",
             f"| **2.** Sharpe corretto per i tentativi (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}) | — | — |",
             f"| t dello Sharpe (da leggere, contro 3) | {ast['t_sharpe']:.2f} | — | — |",
             f"| **3.** Sharpe annuo con i costi doppi (> 0) | {sr2:.2f} | — | — |",
             f"| **4.** Trimestri in guadagno (almeno 60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — | — |",
             f"| Perdita massima dal picco con i costi | {((1 + gc).cumprod() / (1 + gc).cumprod().cummax() - 1).min():.1%} | "
             f"{((1 + gd).cumprod() / (1 + gd).cumprod().cummax() - 1).min():.1%} | — |",
             f"| **Esito** | **{'passa la ricerca' if passa else 'bocciata'}** | | |"]
    (QUI / "P003_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
