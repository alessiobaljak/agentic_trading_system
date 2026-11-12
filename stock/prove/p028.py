"""Calcolo della prova 28 (`P028_tono_delle_notizie.md`): regole lì, scritte prima.

    python -m stock.prove.p028            # su GitHub (azioni-ricerca), dopo che `p028b` ha scaricato tutte le notizie
    python -m stock.prove.p028 --finta    # prova del programma in locale: notizie inventate, solo la variante A, niente file

Le notizie e i prezzi restano nella memoria del lavoro; nel repository vanno solo i risultati.
"""
from __future__ import annotations

import math
import re
import sys
from dataclasses import replace
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli, notizie
from stock.prove.p001 import CAPITALE, IB_FISSO, MEZZO_SCARTO, PB, QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import prepara_titolo, rendimenti, scarti_misurati
from stock.prove.p011 import costi_per
from stock.prove.p027 import DOLLARI_MINIMI, PREZZO_MINIMO, SEDUTE_DOLLARI, scarica
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.portafoglio import simula_conto
from stock.strategie import tono

FINO = date(2024, 12, 31)
NY = ZoneInfo("America/New_York")
SIMBOLO = re.compile(r"[A-Z]{1,5}(\.[A-Z])?")
COSTI_B = Costi(mezzo_scarto=15 * PB, slittamento=5 * PB, **IB_FISSO)
PRESTITO = {"SPY": 0.005, "IWM": 0.01}
# i prezzi «con il simbolo di allora» (asof "-"), in un archivio a parte; la prova locale usa quello che c'è
TIPI = {"raw": "1Day_allora", "az": "azioni_allora", "asof": "-"}
LIQUIDA_DOPO = 5

sr = lambda x: annuo(asticella.sharpe(x))  # noqa: E731
tot = lambda x: (1 + x).prod() - 1  # noqa: E731
dd = lambda x: ((1 + x).cumprod() / (1 + x).cumprod().cummax() - 1).min()  # noqa: E731
t_di = lambda x: x.mean() / x.std(ddof=1) * math.sqrt(len(x)) if len(x) > 2 else float("nan")  # noqa: E731


def decisioni() -> tuple[list[date], dict[date, set[str]]]:
    m = pd.read_csv(QUI / "dati" / "P028_membri.csv.gz", parse_dates=["giorno"])
    giorni = [d.date() for d in m["giorno"]]
    return giorni, {g: set(s.split()) for g, s in zip(giorni, m["simboli"])}


def notizie_finte(membri: dict[date, set[str]]) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    righe = []
    for g, m in membri.items():
        for s in sorted(m):
            for _ in range(int(rng.integers(0, 7))):
                righe.append((datetime(g.year, g.month, int(rng.integers(1, 25)), 15, tzinfo=UTC), [s],
                              str(rng.choice(["beats", "misses", "meeting"]))))
    return pd.DataFrame(righe, columns=["creata", "simboli", "testo"]).assign(creata=lambda d: pd.to_datetime(d["creata"], utc=True))


def con_i_costi(base: dict[str, Costi], f: int) -> dict[str, Costi]:
    return {s: Costi() if f == 0 else c if f == 1 else c.raddoppiati() for s, c in base.items()}


def ritorno(rett: pd.Series, g0: date, g1: date) -> float:
    """Da chiusura a chiusura; se il titolo sparisce per più di 7 giorni (uscito dal listino, simbolo passato ad altri) ci si
    ferma all'ultimo prezzo prima del buco."""
    x = rett.loc[g0:g1]
    buchi = np.flatnonzero(np.diff(pd.to_datetime(pd.Series(x.index)).to_numpy()) > np.timedelta64(7, "D"))
    if len(buchi):
        x = x.iloc[:buchi[0] + 1]
    return float(x.iloc[-1] / x.iloc[0] - 1)


def salti_senza_spiegazione(barre, elenchi, giorni) -> int:
    """Controllo dei dati: giorni in cui un titolo in mano si muove di più del doppio o di meno della metà senza un frazionamento
    quel giorno (un frazionamento che manca nei dati sembra un crollo)."""
    n = 0
    dopo = dict(zip(giorni[:-1], giorni[1:]))
    for g0, scelti in elenchi.items():
        for s in scelti:
            df = barre[s]
            i = pd.Index(controlli.date_ny(df.index))
            dentro = (i > g0) & (i <= dopo[g0])
            mossa = (df["close"] / df["close"].shift(1)).to_numpy()
            n += int((dentro & ((mossa > 2.2) | (mossa < 0.45)) & (df["frazionamento"].to_numpy() == 1.0)).sum())
    return n


def scarto_dei_quinti(giorni, toni, ammessi, rett) -> np.ndarray:
    """Per ogni mese: rendimento medio del mese dopo (da chiusura a chiusura) del quinto più alto meno quello del quinto più basso."""
    out = []
    for k in range(len(giorni) - 1):
        g0, g1 = giorni[k], giorni[k + 1]
        ordine = [s for s in tono.classifica(toni[k], ammessi[g0]) if s in rett and g0 in rett[s].index]
        n = int(tono.QUINTO * len(ordine))
        if n < 5:
            continue
        r = lambda s: ritorno(rett[s], g0, g1)  # noqa: E731
        out.append(np.mean([r(s) for s in ordine[:n]]) - np.mean([r(s) for s in ordine[-n:]]))
    return np.array(out)


def simula(barre, elenchi, fondo, base) -> dict:
    usati = set().union(*[set(v) for v in elenchi.values()]) | {fondo}
    b = {s: barre[s] for s in usati}
    return {nome: simula_conto(b, tono.strategia(elenchi, fondo), con_i_costi({s: base[s] for s in b}, f), capitale=CAPITALE,
                               liquida_dopo=LIQUIDA_DOPO)
            for nome, f in (("costi", 1), ("costi doppi", 2), ("senza costi", 0))}


def variante_a(giorni, membri, toni, finta):
    simboli = sorted(set().union(*membri.values()))
    if not finta:
        scarica(["SPY", "IWM"])                                           # per il confronto con il tenere lo SPY
        scarica(simboli + ["SPY", "IWM"], TIPI["raw"], TIPI["az"], TIPI["asof"])
    barre, rett, senza = {}, {}, []
    for s in simboli + ["SPY"]:
        try:
            barre[s], rett[s], _ = prepara_titolo(s, FINO, TIPI["raw"], TIPI["az"])
        except Exception as e:  # noqa: BLE001 — titolo senza prezzi: si conta
            senza.append(f"{s} ({type(e).__name__})")
    ha = {s: set(controlli.date_ny(df.index)) for s, df in barre.items()}
    ammessi = {g: {s for s in membri[g] if s in ha and g in ha[s]} for g in giorni}
    elenchi = {g: tono.scegli(toni[k], ammessi[g]) for k, g in enumerate(giorni[:-1])}
    base = costi_per(list(barre), scarti_misurati(QUI.parent / "dati" / "ESITO_CONTROLLI_UNIVERSO.md"), 1)
    base["SPY"] = Costi(mezzo_scarto=MEZZO_SCARTO["SPY"], slittamento=0.5 * PB, prestito_annuo=PRESTITO["SPY"], **IB_FISSO)
    nota = f"membri senza prezzi {len(senza)}; salti di prezzo senza spiegazione fra i titoli in mano {salti_senza_spiegazione(barre, elenchi, giorni)}"
    return simula(barre, elenchi, "SPY", base), elenchi, ammessi, rett, nota


def variante_b(giorni, membri, toni):
    candidati = sorted({s for k, g in enumerate(giorni[:-1]) for s in toni[k] if s not in membri[g] and SIMBOLO.fullmatch(s)})
    print(f"B: candidati {len(candidati)}", flush=True)
    scarica(candidati + ["IWM"], TIPI["raw"], TIPI["az"], TIPI["asof"])
    nomi = alpaca.nomi_dei_titoli()
    fondi = {s for s in candidati if tono.e_un_fondo(nomi.get(s, ""))}
    chiusure, dollari = {}, {}
    for s in candidati:
        df = archivio.carica(s, TIPI["raw"])
        if s in fondi or df is None or len(df) <= SEDUTE_DOLLARI:
            continue
        i = pd.Index(controlli.date_ny(df.index))
        chiusure[s] = pd.Series(df["close"].to_numpy(), index=i)
        dollari[s] = pd.Series((df["close"] * df["volume"]).to_numpy(), index=i)

    def comprabile(s: str, g: date) -> bool:
        c = chiusure.get(s)
        if c is None or g not in c.index or c.loc[g] < PREZZO_MINIMO:
            return False
        v = dollari[s].loc[:g].iloc[:-1].iloc[-SEDUTE_DOLLARI:]
        return len(v) == SEDUTE_DOLLARI and float(v.median()) >= DOLLARI_MINIMI
    ammessi = {g: {s for s in toni[k] if s not in membri[g] and comprabile(s, g)} for k, g in enumerate(giorni[:-1])}
    ammessi[giorni[-1]] = set()
    barre, rett, rotti = {}, {}, []
    for s in sorted(set().union(*ammessi.values())) + ["IWM"]:
        try:
            barre[s], rett[s], _ = prepara_titolo(s, FINO, TIPI["raw"], TIPI["az"])
        except Exception as e:  # noqa: BLE001 — titolo con i dati rotti: si conta e resta fuori
            rotti.append(f"{s} ({type(e).__name__})")
    ammessi = {g: {s for s in a if s in barre} for g, a in ammessi.items()}
    elenchi = {g: tono.scegli(toni[k], ammessi[g]) for k, g in enumerate(giorni[:-1])}
    base = {s: COSTI_B for s in barre}
    base["IWM"] = replace(COSTI_B, prestito_annuo=PRESTITO["IWM"])
    nota = (f"candidati fuori dall'indice {len(candidati)}, di cui fondi esclusi {len(fondi)}, senza prezzi "
            f"{len(candidati) - len(fondi) - len(chiusure)}, con i dati rotti {len(rotti)}; salti di prezzo senza spiegazione fra i "
            f"titoli in mano {salti_senza_spiegazione(barre, elenchi, giorni)}")
    return simula(barre, elenchi, "IWM", base), elenchi, ammessi, rett, nota


def tabella(titolo, nome, out, elenchi, ammessi, quinti, nota, miscela, tutte) -> list[str]:
    r = out["costi"]
    primo = r.esecuzioni["giorno"].min()
    g = {k: rendimenti(v.valore[v.valore.index >= primo]) for k, v in out.items()}
    gc = g["costi"]
    a, b = gc.index.min(), gc.index.max()
    spy = comprare_e_tenere("SPY", a, b)
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1)
         for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota = sum(x > 0 for x in q) / len(q)
    sr_c, sr_2 = sr(gc), sr(g["costi doppi"])
    da_sola = sr_c > sr(spy) and ast["sharpe_corretto"] >= 0.95 and sr_2 > 0 and quota >= 0.6
    comuni = miscela.index.intersection(gc.index)
    nuova = tutte[f"P028_miscela_{nome}"]
    corr = float(np.corrcoef(miscela.loc[comuni], gc.loc[comuni])[0, 1])
    spy_c = comprare_e_tenere("SPY", comuni.min(), comuni.max())
    entra = sr(gc.loc[comuni]) > 0 and sr(g["costi doppi"].reindex(comuni).dropna()) > 0 and corr < 0.3 \
        and sr(nuova) > sr(miscela.loc[comuni]) and sr(nuova) > sr(spy_c)
    anni = (1 + gc).groupby(pd.Index([d.year for d in gc.index])).prod() - 1
    con_tono = [len(v) for k, v in ammessi.items() if k in elenchi]
    scelti = [len(v) for v in elenchi.values()]
    return [f"## {titolo}", "",
            f"* Dal {a} al {b}. Titoli ammessi con il tono calcolabile, per mese: mediana {int(np.median(con_tono))}, minimo "
            f"{min(con_tono)}; titoli scelti: mediana {int(np.median(scelti))}; mesi fuori (meno di 25 titoli) "
            f"{sum(1 for x in scelti if x == 0)} su {len(scelti)}. {nota}.",
            f"* Il quinto con il tono più alto meno il quinto più basso, mese dopo, senza costi: **{quinti.mean():+.2%} al mese "
            f"(t {t_di(quinti):.2f})**, mediana {np.median(quinti):+.2%}, su {len(quinti)} mesi.",
            f"* Ordini eseguiti {len(r.esecuzioni)}; senza barra {r.senza_barra}; rifiutati {r.rifiutati}; rimasti in mano dopo l'uscita "
            f"dal listino {len(r.bloccati)}; **chiusi all'ultimo prezzo perché spariti dal listino o con il simbolo cambiato: "
            f"{len(r.liquidati)}**. Costi pagati: commissioni {r.commissioni:,.0f}, scarto e slittamento "
            f"{r.costo_scarto:,.0f} dollari.", "",
            "| | La strategia | Tenere lo SPY |", "|---|---|---|",
            f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(g['senza costi']):+.1%} / {tot(gc):+.1%} / "
            f"{tot(g['costi doppi']):+.1%} | {tot(spy):+.1%} |",
            f"| **1.** Sharpe annuo con i costi | **{sr_c:.2f}** (senza costi {sr(g['senza costi']):.2f}) | {sr(spy):.2f} |",
            f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — |",
            f"| **3.** Sharpe con i costi doppi (> 0) | {sr_2:.2f} | — |",
            f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — |",
            f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(spy):.1%} |",
            f"| Anno per anno | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — |",
            f"| **Esito da sola** | **{'passa la ricerca' if da_sola else 'bocciata'}** | |", "",
            f"**Per entrare nella miscela** (giorni in comune dal {comuni.min()} al {comuni.max()}): Sharpe della parte "
            f"{sr(gc.loc[comuni]):.2f}; correlazione con la miscela {corr:.2f} (soglia 0,3); miscela nuova {sr(nuova):.2f} contro "
            f"{sr(miscela.loc[comuni]):.2f} della miscela e {sr(spy_c):.2f} del tenere lo SPY; perdita massima {dd(nuova):.1%} contro "
            f"{dd(miscela.loc[comuni]):.1%}. **Esito: "
            f"{'entra nella miscela (prima il revisore, poi il periodo chiuso e la misura in avanti)' if entra else 'non entra'}**", ""]


def main(finta: bool = False):
    giorni, membri = decisioni()
    if finta:
        TIPI.update(raw="1Day_raw", az="azioni", asof=None)
        n = notizie_finte(membri)
    else:
        if notizie.mancanti(2016, 2024):
            raise SystemExit(f"mancano {len(notizie.mancanti(2016, 2024))} mesi di notizie: prima `python -m stock.prove.p028b`")
        n = notizie.carica(2016, 2024)
    confini = [datetime(2015, 12, 31, 16, tzinfo=NY)] + [datetime(g.year, g.month, g.day, 16, tzinfo=NY) for g in giorni[:-1]]
    dell_azienda = int(n["simboli"].map(len).between(1, tono.SIMBOLI_MASSIMI).sum())
    toni = tono.toni(n, confini)
    print(f"notizie {len(n)}, dell'azienda {dell_azienda}", flush=True)
    conta = f"Notizie nell'archivio: {len(n):,}; che citano da 1 a 3 simboli: {dell_azienda:,}."
    del n
    risultati = {"grandi": variante_a(giorni, membri, toni, finta)}
    if finta:
        out, elenchi, ammessi, rett, nota = risultati["grandi"]
        g = rendimenti(out["costi"].valore)
        q = scarto_dei_quinti(giorni, toni, ammessi, rett)
        print(f"PROVA LOCALE con notizie inventate (non è il risultato): Sharpe {sr(g):.2f}, senza costi "
              f"{sr(rendimenti(out['senza costi'].valore)):.2f}, ordini {len(out['costi'].esecuzioni)}, scelti "
              f"{np.median([len(v) for v in elenchi.values()])}, quinti {q.mean():+.2%} (t {t_di(q):.2f}, {len(q)} mesi), {nota}")
        return
    risultati["piccole"] = variante_b(giorni, membri, toni)
    miscela = carica_serie()["P025_miscela"]
    for nome, (out, *_resto) in risultati.items():
        r = out["costi"]
        gc = rendimenti(r.valore[r.valore.index >= r.esecuzioni["giorno"].min()])
        salva_serie(f"P028_tono_{nome}", gc)
        comuni = miscela.index.intersection(gc.index)
        salva_serie(f"P028_miscela_{nome}", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    righe = ["# Prova 28 — risultati", "",
             f"Calcolato da `python -m stock.prove.p028` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P028_tono_delle_notizie.md` (committate prima). Nel conto dell'asticella: {len(tutte)} serie. {conta}", ""]
    for nome, titolo in (("grandi", "A — le 500 grandi, coperte con lo SPY"), ("piccole", "B — le aziende piccole, coperte con l'IWM")):
        out, elenchi, ammessi, rett, nota = risultati[nome]
        righe += tabella(titolo, nome, out, elenchi, ammessi, scarto_dei_quinti(giorni, toni, ammessi, rett), nota, miscela, tutte)
    (QUI / "P028_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main("--finta" in sys.argv)
