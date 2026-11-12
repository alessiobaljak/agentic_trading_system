"""Calcolo della prova 27 (`P027_dirigenti_aziende_piccole.md`): regole lì, scritte prima.

    python -m stock.prove.p027                 # scarica i prezzi che mancano (servono le chiavi di Alpaca), calcola, scrive i risultati
    python -m stock.prove.p027 --solo-locali   # prova del programma: solo i titoli già in archivio, niente scarico, niente file

Gira su GitHub (`.github/workflows/azioni_ricerca.yml`): i prezzi restano nella memoria del lavoro, nel repository vanno solo i
risultati. Gli acquisti (dati pubblici della SEC, già filtrati) stanno in `stock/prove/dati/P027_acquisti.csv.gz`.
"""
from __future__ import annotations

import math
import sys
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli
from stock.prove.p001 import CAPITALE, IB_FISSO, PB, QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import prepara_titolo, rendimenti
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.portafoglio import simula_conto
from stock.strategie import dirigenti

DAL, AL = datetime(2015, 11, 1, tzinfo=UTC), datetime(2025, 1, 1, 5, tzinfo=UTC)
FINO = date(2024, 12, 31)
COSTI = Costi(mezzo_scarto=15 * PB, slittamento=5 * PB, **IB_FISSO)
PREZZO_MINIMO, DOLLARI_MINIMI, SEDUTE_DOLLARI, VALORE_MINIMO, SCARTO_MASSIMO = 5.0, 2_000_000.0, 20, 100_000.0, 0.5


def scarica(simboli: list[str], tipo_raw: str = "1Day_raw", tipo_az: str = "azioni", asof: str | None = None) -> None:
    """Barre al giorno non rettificate e azioni societarie dei titoli che mancano in archivio. `asof="-"`: i prezzi di ciò che
    si scambiava con quel simbolo allora (`alpaca.barre_di_piu`), da tenere in un archivio con un altro nome (`tipo_raw`)."""
    mancano = [s for s in simboli if archivio.carica(s, tipo_raw) is None]
    for i in range(0, len(mancano), 40):
        gruppo = mancano[i:i + 40]
        try:
            barre = alpaca.barre_di_piu(gruppo, "1Day", DAL, AL, asof=asof)
        except alpaca.ErroreAlpaca as e:                 # un simbolo che Alpaca non conosce fa fallire il gruppo: uno alla volta
            print(f"gruppo {i}: {str(e)[:100]}; riprovo uno alla volta", flush=True)
            barre = {}
            for s in gruppo:
                try:
                    barre[s] = alpaca.barre(s, "1Day", DAL, AL, asof=asof)
                except alpaca.ErroreAlpaca:
                    barre[s] = pd.DataFrame()
        for s in gruppo:
            archivio.salva(barre.get(s, pd.DataFrame(columns=["open", "high", "low", "close", "volume"])), s, tipo_raw)
        if i % 400 == 0:
            print(f"barre: {i + len(gruppo)} su {len(mancano)}", flush=True)
    senza_azioni = [s for s in simboli if archivio.carica(s, tipo_az) is None]
    con_barre = [s for s in senza_azioni if len(archivio.carica(s, tipo_raw))]
    for i in range(0, len(con_barre), 500):
        az = alpaca.azioni_societarie_di_piu(con_barre[i:i + 500], DAL, AL)
        for s, df in az.items():
            archivio.salva(df, s, tipo_az)
        print(f"azioni societarie: {i + len(az)} su {len(con_barre)}", flush=True)


def eventi_puliti(tr: pd.DataFrame, barre: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, dict]:
    """Dalle operazioni agli eventi della regola; il secondo valore conta quanti restano dopo ogni filtro."""
    chiusure = {s: pd.Series(df["close"].to_numpy(), index=pd.Index(controlli.date_ny(df.index))) for s, df in barre.items()}
    dollari = {s: pd.Series((df["close"] * df["volume"]).to_numpy(), index=pd.Index(controlli.date_ny(df.index))) for s, df in barre.items()}
    conta = {"operazioni": len(tr), "gruppi": tr.groupby(["deposito", "simbolo"]).ngroups}
    tr = tr[tr["simbolo"].isin(chiusure)]
    conta["gruppi con i prezzi"] = tr.groupby(["deposito", "simbolo"]).ngroups

    def chiusura(s, g):
        prima = chiusure[s].loc[:g]
        return float(prima.iloc[-1]) if len(prima) else float("nan")
    rif = np.array([chiusura(s, g) if pd.notna(g) else np.nan for s, g in zip(tr["simbolo"], tr["giorno_op"])])
    tr = tr[np.abs(tr["prezzo"].to_numpy() / rif - 1) <= SCARTO_MASSIMO]
    g = tr.groupby(["deposito", "simbolo"]).agg(valore=("valore", "sum")).reset_index()
    g = g[g["valore"] >= VALORE_MINIMO]
    conta["eventi puliti sopra 100'000"] = len(g)
    tiene = []
    for d, s in zip(g["deposito"], g["simbolo"]):
        c = chiusure[s].loc[:d]
        v = dollari[s].loc[:d]
        v = v[v.index < d].iloc[-SEDUTE_DOLLARI:]
        tiene.append(len(c) > 0 and c.iloc[-1] >= PREZZO_MINIMO and len(v) == SEDUTE_DOLLARI and float(v.median()) >= DOLLARI_MINIMI)
    g = g[tiene]
    conta["eventi comprabili (5 dollari, 2 milioni al giorno)"] = len(g)
    return g.reset_index(drop=True), conta


def main(solo_locali: bool = False):
    tr = pd.read_csv(QUI / "dati" / "P027_acquisti.csv.gz", parse_dates=["deposito", "giorno_op"])
    tr["deposito"], tr["giorno_op"] = tr["deposito"].dt.date, tr["giorno_op"].dt.date
    simboli = sorted(tr["simbolo"].unique())
    if not solo_locali:
        scarica(simboli + ["SPY", "IWM"])
    grezze = {}
    for s in simboli:
        df = archivio.carica(s, "1Day_raw")
        if df is not None and len(df) > SEDUTE_DOLLARI:
            grezze[s] = df
    print(f"titoli con i prezzi: {len(grezze)} su {len(simboli)}", flush=True)
    ev, conta = eventi_puliti(tr, grezze)
    barre, rett, rotti = {}, {}, []
    for s in sorted(ev["simbolo"].unique()):
        try:
            barre[s], rett[s], _ = prepara_titolo(s, FINO)
        except Exception as e:  # noqa: BLE001 — un titolo con i dati rotti si conta e si lascia fuori
            rotti.append(f"{s} ({type(e).__name__})")
    ev = ev[ev["simbolo"].isin(barre)]
    eventi = list(zip(ev["deposito"], ev["simbolo"], ev["valore"]))
    spy_b, spy, _ = prepara_titolo("SPY", FINO)
    cal = sorted(controlli.date_ny(spy_b.index))
    print(f"eventi {len(eventi)} su {len(barre)} titoli", flush=True)
    out = {}
    for nome, c in (("costi", COSTI), ("costi doppi", COSTI.raddoppiati()), ("senza costi", Costi())):
        out[nome] = simula_conto(barre, dirigenti.strategia(eventi, cal), c, capitale=CAPITALE)
        print(nome, f"{out[nome].valore.iloc[-1]:.0f}", flush=True)
    r = out["costi"]
    primo = r.esecuzioni["giorno"].min()
    g = {k: rendimenti(v.valore[v.valore.index >= primo]) for k, v in out.items()}
    gc = g["costi"]
    a, b = gc.index.min(), gc.index.max()
    try:
        _, iwm, _ = prepara_titolo("IWM", FINO)
        g_iwm = comprare_e_tenere("IWM", a, b)
    except Exception:  # noqa: BLE001 — nella prova locale l'IWM può mancare
        iwm, g_iwm = spy, comprare_e_tenere("SPY", a, b)
    g_spy = comprare_e_tenere("SPY", a, b)
    e = r.esecuzioni
    su_iwm, su_spy = [], []
    for s, x in e.groupby("simbolo"):
        ing, usc = x[x.etichetta == "ingresso"], x[x.etichetta == "uscita"]
        for (_, i), (_, u) in zip(ing.iterrows(), usc.iterrows()):
            mio = u["prezzo"] / i["prezzo"] - 1
            su_iwm.append(mio - (iwm[u["giorno"]] / iwm[i["giorno"]] - 1))
            su_spy.append(mio - (spy[u["giorno"]] / spy[i["giorno"]] - 1))
    su_iwm, su_spy = np.array(su_iwm), np.array(su_spy)
    t = lambda x: x.mean() / x.std(ddof=1) * math.sqrt(len(x)) if len(x) > 1 else float("nan")  # noqa: E731
    sr = lambda x: annuo(asticella.sharpe(x))  # noqa: E731
    tot = lambda x: (1 + x).prod() - 1  # noqa: E731
    dd = lambda x: ((1 + x).cumprod() / (1 + x).cumprod().cummax() - 1).min()  # noqa: E731
    if solo_locali:
        print(f"PROVA LOCALE (non è il risultato): eventi {len(eventi)}, ingressi {(e.etichetta == 'ingresso').sum()}, "
              f"Sharpe {sr(gc):.2f}, per evento su IWM {su_iwm.mean():+.2%} (t {t(su_iwm):.1f}); conteggi {conta}; rotti {rotti[:5]}")
        return
    salva_serie("P027_dirigenti_piccole", gc)
    tutte = carica_serie()
    m = tutte["P025_miscela"]
    comuni = m.index.intersection(gc.index)
    nuova = 0.75 * m.loc[comuni] + 0.25 * gc.loc[comuni]
    salva_serie("P027_miscela_nuova", nuova)
    tutte = carica_serie()
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1)
         for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota = sum(x > 0 for x in q) / len(q)
    sr_c, sr_2 = sr(gc), sr(g["costi doppi"])
    da_sola = sr_c > max(sr(g_spy), sr(g_iwm)) and ast["sharpe_corretto"] >= 0.95 and sr_2 > 0 and quota >= 0.6
    corr = float(np.corrcoef(m.loc[comuni], gc.loc[comuni])[0, 1])
    spy_c = comprare_e_tenere("SPY", comuni.min(), comuni.max())
    entra = sr(gc.loc[comuni]) > 0 and sr(g["costi doppi"].reindex(comuni).dropna()) > 0 and corr < 0.3 \
        and sr(nuova) > sr(m.loc[comuni]) and sr(nuova) > sr(spy_c)
    anni = (1 + gc).groupby(pd.Index([d.year for d in gc.index])).prod() - 1
    righe = ["# Prova 27 — risultati", "",
             f"Calcolato da `python -m stock.prove.p027` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P027_dirigenti_aziende_piccole.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Titoli con acquisti: {len(simboli)}; con i prezzi su Alpaca: {len(grezze)} (**senza prezzi: {len(simboli) - len(grezze)}**, "
             "in gran parte aziende sparite o mai quotate in borsa: controllo dei dati).",
             "* Eventi dopo ogni filtro: " + "; ".join(f"{k} {v}" for k, v in conta.items()) + f"; titoli con i dati rotti {len(rotti)}.",
             f"* Ingressi eseguiti {(e.etichetta == 'ingresso').sum()}; senza barra {r.senza_barra}; rifiutati {r.rifiutati}; **rimasti in "
             f"mano dopo l'uscita dal listino: {len(r.bloccati)}** ({', '.join(r.bloccati[:15]) or 'nessuno'}).",
             f"* Costi pagati: commissioni {r.commissioni:,.0f}, scarto e slittamento {r.costo_scarto:,.0f} dollari.", "",
             "| | Acquisti dei dirigenti, aziende piccole | Tenere l'IWM | Tenere lo SPY |", "|---|---|---|---|",
             f"| Guadagno medio per evento, con i costi (t) | rispetto all'IWM {su_iwm.mean():+.2%} ({t(su_iwm):.2f}); rispetto allo SPY "
             f"{su_spy.mean():+.2%} ({t(su_spy):.2f}); eventi {len(su_iwm)}; meglio dell'IWM {np.mean(su_iwm > 0):.0%} | — | — |",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(g['senza costi']):+.1%} / {tot(gc):+.1%} / "
             f"{tot(g['costi doppi']):+.1%} | {tot(g_iwm):+.1%} | {tot(g_spy):+.1%} |",
             f"| **1.** Sharpe annuo con i costi | **{sr_c:.2f}** (senza costi {sr(g['senza costi']):.2f}) | {sr(g_iwm):.2f} | {sr(g_spy):.2f} |",
             f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — | — |",
             f"| **3.** Sharpe con i costi doppi (> 0) | {sr_2:.2f} | — | — |",
             f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — | — |",
             f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(g_iwm):.1%} | {dd(g_spy):.1%} |",
             f"| Anno per anno | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — | — |",
             f"| **Esito da sola** | **{'passa la ricerca' if da_sola else 'bocciata'}** | | |", "",
             f"**Per entrare nella miscela** (giorni in comune dal {comuni.min()} al {comuni.max()}): Sharpe della parte "
             f"{sr(gc.loc[comuni]):.2f}; correlazione con la miscela {corr:.2f} (soglia 0,3); miscela nuova {sr(nuova):.2f} contro "
             f"{sr(m.loc[comuni]):.2f} della miscela e {sr(spy_c):.2f} del tenere lo SPY; perdita massima {dd(nuova):.1%} contro "
             f"{dd(m.loc[comuni]):.1%}. **Esito: {'entra nella miscela (prima il revisore, poi in avanti)' if entra else 'non entra'}**"]
    (QUI / "P027_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main("--solo-locali" in sys.argv)
