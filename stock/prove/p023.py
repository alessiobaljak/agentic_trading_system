"""Calcolo della prova 23 (`P023_giornata_sulle_azioni.md`): regole lì, scritte prima.

    python -m stock.prove.p023     # scrive stock/prove/P023_risultati.md

Ogni titolo si simula da solo, con un posto da 10'000 dollari, solo nei giorni in cui è fra le 10 di allora (più 25 giorni di borsa
prima di ogni tratto, che servono alle regole per guardare indietro e dove non si opera). I risultati di ogni titolo si salvano in
`$STOCK_DATI_DIR/calcoli/p023/` (fuori dal repository): un calcolo interrotto riparte dai titoli mancanti.
"""
from __future__ import annotations

import pickle
from datetime import UTC, date, datetime
from multiprocessing import Pool

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli
from stock.dati.integrazioni import azioni_complete
from stock.prove.p001 import IB_FISSO, PB, QUI, annuo, carica_serie, comprare_e_tenere, rendimenti_giornalieri, salva_serie
from stock.prove.p003 import CAPITALE, prepara_titolo, scarti_misurati
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.motore import simula
from stock.simulatore.portafoglio import simula_conto
from stock.strategie import inversione as inv
from stock.strategie import prima_candela as pc
from stock.strategie import ultima_mezzora as um
from stock.strategie import zona_di_rumore as zr
from stock.strategie.rimbalzo import strategia_tenere_i_dieci
from stock.universo.costruisci import RINOMINATI

RADICE = QUI.parent
POSTO = 10_000.0
MARGINE = 25                  # giorni di borsa prima di ogni tratto
DOPO_FRAZIONAMENTO = 5
REGOLE = {
    "ultima mezz'ora": (lambda b, c, e: um.prepara(b, c, e), um.strategia),
    "zona di rumore": (lambda b, c, e: zr.prepara(b, c, e), zr.strategia),
    "prima candela 5 min": (lambda b, c, e: pc.prepara(b, c, e, 5), pc.strategia),
    "prima candela 15 min": (lambda b, c, e: pc.prepara(b, c, e, 15), pc.strategia),
    "inversione": (lambda b, c, e: inv.prepara(b, c, e, inv.PRINCIPALE), inv.strategia),
}
SERIE = {"ultima mezz'ora": "P023_ultima_mezzora", "zona di rumore": "P023_zona_di_rumore",
         "prima candela 5 min": "P023_prima_candela_5m", "prima candela 15 min": "P023_prima_candela_15m",
         "inversione": "P023_inversione"}


def cartella():
    d = archivio.cartella_dati() / "calcoli" / "p023"
    d.mkdir(parents=True, exist_ok=True)
    return d


def universo() -> pd.DataFrame:
    u = pd.read_csv(RADICE / "universo" / "dieci_di_allora.csv")
    u["simbolo"] = u["simbolo"].replace(RINOMINATI)
    return u


def calcola_titolo(arg):
    s, mesi, mezzo_scarto = arg
    f = cartella() / f"{s}.pkl"
    if f.exists():
        return s
    cal = alpaca.calendario("2016-01-01", "2024-12-31")
    giorni = list(cal.index)
    dentro = [d for d in giorni if f"{d:%Y-%m}" in mesi]
    # i giorni da simulare: quelli dentro più i MARGINE giorni prima di ognuno
    pos = {d: i for i, d in enumerate(giorni)}
    tenere = set()
    for d in dentro:
        tenere.update(giorni[max(0, pos[d] - MARGINE):pos[d] + 1])
    minuti = archivio.carica(s, "1Min_raw")
    seduta = um.solo_seduta(minuti, cal)
    gs = pd.Index(seduta.index.tz_convert(um.NY).date)
    seduta = seduta[gs.isin(tenere)]
    problemi, _ = controlli.controlla_minuti(minuti, cal)
    esclusi = {date.fromisoformat(p["quando"]) for p in problemi if p["controllo"] == "minuti mancanti"}
    n_mancanti = len(esclusi & set(dentro))
    az = azioni_complete(s, archivio.carica(s, "azioni"))
    frazionamenti = sorted(az[az.tipo == "frazionamento"]["data"]) if not az.empty else []
    for d in frazionamenti:
        d = pd.Timestamp(d).date()
        if d in pos:
            esclusi.update(giorni[pos[d]:pos[d] + DOPO_FRAZIONAMENTO + 1])
    esclusi |= set(giorni) - set(dentro)
    costi = Costi(mezzo_scarto=mezzo_scarto, slittamento=0.5 * PB, **IB_FISSO)
    out = {"dentro": len(dentro), "minuti mancanti": n_mancanti, "frazionamenti": len(frazionamenti)}
    for nome, (prepara, strategia) in REGOLE.items():
        seg = prepara(seduta, cal, esclusi)
        for cn, c in (("costi", costi), ("costi doppi", costi.raddoppiati()), ("senza costi", Costi())):
            r = simula(seduta, strategia(seg), c, capitale=POSTO)
            g = rendimenti_giornalieri(r.valore, POSTO)
            out[(nome, cn)] = g[g.index.isin(dentro)]
            if cn == "costi":
                out[(nome, "ordini")] = len(r.esecuzioni)
    with open(f, "wb") as fh:
        pickle.dump(out, fh)
    print(s, "fatto", flush=True)
    return s


def main():
    u = universo()
    simboli = sorted(u["simbolo"].unique())
    scarti = scarti_misurati(RADICE / "dati" / "ESITO_CONTROLLI_UNIVERSO.md")
    scarti.setdefault("META", scarti.get("FB"))
    mesi = {s: set(u.loc[u.simbolo == s, "mese"]) for s in simboli}
    with Pool(4) as p:
        list(p.imap_unordered(calcola_titolo, [(s, mesi[s], scarti[s] / 2) for s in simboli]))
    ris = {s: pickle.load(open(cartella() / f"{s}.pkl", "rb")) for s in simboli}

    cal = alpaca.calendario("2016-01-01", "2024-12-31")
    giorni = [d for d in cal.index if f"{d:%Y-%m}" in set(u["mese"])]
    indice = pd.Index(giorni)

    def conto(nome, cn):
        tab = pd.DataFrame({s: ris[s][(nome, cn)].reindex(indice) for s in simboli}).fillna(0.0)
        return tab.sum(axis=1) / 10, tab

    # tenere le stesse 10 a pesi uguali (come la prova 3), sugli stessi giorni
    fino = date(2024, 12, 31)
    barre = {s: prepara_titolo(s, fino)[0] for s in simboli}
    costi_t = {s: Costi(mezzo_scarto=scarti[s] / 2, slittamento=0.5 * PB, **IB_FISSO) for s in simboli}
    dieci = simula_conto(barre, strategia_tenere_i_dieci(u, list(cal.index)), costi_t, capitale=CAPITALE)
    v = dieci.valore[dieci.valore.index >= giorni[0]]
    gd = (v / v.shift(1) - 1).dropna()

    finestre_prova = [f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))]
    risultati = {}
    for nome in REGOLE:
        gc, tab = conto(nome, "costi")
        salva_serie(SERIE[nome], gc)
        risultati[nome] = (gc, tab)
    tutte = carica_serie()
    righe = ["# Prova 23 — risultati", "",
             f"Calcolato da `python -m stock.prove.p023` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P023_giornata_sulle_azioni.md` (committate prima). {len(simboli)} titoli, dal {giorni[0]} al {giorni[-1]} "
             f"({len(giorni)} giorni). Nel conto dell'asticella: {len(tutte)} serie.", "",
             "* Giorni esclusi per minuti mancanti (titolo-giorni dentro l'elenco): "
             + ", ".join(f"{s} {ris[s]['minuti mancanti']}" for s in simboli if ris[s]["minuti mancanti"]) + ".",
             f"* Tenere lo SPY: Sharpe {annuo(asticella.sharpe(comprare_e_tenere('SPY', giorni[0], giorni[-1]))):.2f}; tenere le "
             f"10 di allora a pesi uguali: Sharpe {annuo(asticella.sharpe(gd)):.2f}.", ""]
    sr_spy = annuo(asticella.sharpe(comprare_e_tenere("SPY", giorni[0], giorni[-1])))
    sr_dieci = annuo(asticella.sharpe(gd))
    colonne = list(REGOLE)
    righe += ["| | " + " | ".join(colonne) + " |", "|---" * (len(colonne) + 1) + "|"]
    celle = {}
    for nome in colonne:
        gc, tab = risultati[nome]
        g2, _ = conto(nome, "costi doppi")
        g0, _ = conto(nome, "senza costi")
        sr, sr2, sr0 = (annuo(asticella.sharpe(x)) for x in (gc, g2, g0))
        ast = asticella.sharpe_corretto(gc, tutte)
        q = [float((1 + gc[(gc.index >= a) & (gc.index < b)]).prod() - 1) for a, b in finestre_prova]
        quota = sum(x > 0 for x in q) / len(q)
        attivi = tab.to_numpy().ravel()
        attivi = attivi[attivi != 0]
        t = attivi.mean() / attivi.std(ddof=1) * np.sqrt(len(attivi)) if len(attivi) > 1 else float("nan")
        contributo = tab.sum().sort_values()
        anni = (1 + gc).groupby(pd.Index([d.year for d in gc.index])).prod() - 1
        passa = sr > max(sr_spy, sr_dieci) and ast["sharpe_corretto"] >= 0.95 and sr2 > 0 and quota >= 0.6
        tot = lambda x: (1 + x).prod() - 1  # noqa: E731
        celle[nome] = [
            f"{sum(ris[s][(nome, 'ordini')] for s in simboli)}",
            f"{attivi.mean():+.3%} (t {t:.1f}, {len(attivi)})" if len(attivi) else "—",
            f"{tot(g0):+.1%} / {tot(gc):+.1%} / {tot(g2):+.1%}",
            f"{sr0:.2f}", f"{sr:.2f}", f"{ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']})", f"{sr2:.2f}",
            f"{sum(x > 0 for x in q)} su 32 ({quota:.0%})",
            f"{(anni > 0).sum()} su {len(anni)}",
            ", ".join(f"{s} {contributo[s] / 10:+.1%}" for s in list(contributo.index[-3:])[::-1]) + "; peggiori: "
            + ", ".join(f"{s} {contributo[s] / 10:+.1%}" for s in contributo.index[:3]),
            f"**{'passa la ricerca' if passa else 'bocciata'}**"]
    nomi = ["Ordini eseguiti (con i costi)", "Guadagno medio di un posto nei giorni con operazioni, con i costi (t, giorni)",
            "Guadagno senza costi / con i costi / costi doppi", "Sharpe annuo senza costi",
            f"**1.** Sharpe annuo con i costi (tenere lo SPY {sr_spy:.2f}, le 10 {sr_dieci:.2f})",
            "**2.** Sharpe corretto (soglia 0,95)", "**3.** Sharpe con i costi doppi (> 0)", "**4.** Trimestri in guadagno (60%)",
            "Anni in guadagno (da leggere)", "Titoli migliori; peggiori (somma dei rendimenti giornalieri / 10, da leggere)",
            "**Esito**"]
    for j, n in enumerate(nomi):
        righe.append(f"| {n} | " + " | ".join(celle[c][j] for c in colonne) + " |")
    (QUI / "P023_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
