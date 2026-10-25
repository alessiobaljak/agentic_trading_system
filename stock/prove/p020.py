"""Calcolo della prova 20 (`P020_notizie_prima_candela.md`): regole lì, scritte prima.

    python -m stock.prove.p020     # scrive stock/prove/P020_risultati.md
"""
from __future__ import annotations

import bisect
import math
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli
from stock.dati.archivio import cartella_dati
from stock.prove.p001 import CAPITALE, IB_FISSO, PB, QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import RADICE, scarti_misurati
from stock.prove.p011 import membri_dell_indice
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.motore import simula
from stock.strategie import prima_candela as pc

NY = "America/New_York"
SALTO = 0.02
QUOTA = 0.10
MASSIMO = 10


def chiusure_e_frazionamenti(s):
    raw = archivio.carica(s, "1Day_raw")
    if raw is None or raw.empty:
        return None, {}
    c = pd.Series(raw["close"].to_numpy(), index=pd.Index(controlli.date_ny(raw.index)))
    az = archivio.carica(s, "azioni")
    fr = {}
    if az is not None and not az.empty:
        f = az[az["tipo"] == "frazionamento"]
        fr = dict(zip(f["data"], f["rapporto"]))
    return c, fr


def operazioni(cal, membri):
    """Per ogni evento in gioco: (giorno, simbolo, salto). Il salto si vede alla prima barra delle 9:30. Si legge ogni giorno una
    volta: per ogni evento si guarda prima il giorno del deposito (o il primo di borsa dopo), poi, se lì non salta, il giorno dopo."""
    ev = pd.read_csv(cartella_dati() / "eventi" / "comunicati.csv", parse_dates=["deposito"])
    candidati: dict[date, list[tuple[int, str]]] = {}
    for n, (s, d) in enumerate(zip(ev["simbolo"], ev["deposito"].dt.date)):
        k = bisect.bisect_left(cal, d)
        if 0 < k < len(cal):
            candidati.setdefault(cal[k], []).append((n, s))
    cache_ch: dict[str, tuple] = {}
    fatti: set[int] = set()
    out = []
    secondo: dict[date, list[tuple[int, str]]] = {}
    for g in cal:
        lista = candidati.get(g, []) + secondo.pop(g, [])
        if not lista:
            continue
        f = cartella_dati() / "eventi" / "minuti" / f"{g}.csv.gz"
        m = pd.read_csv(f, index_col="t", parse_dates=["t"]) if f.exists() else pd.DataFrame()
        prime = m.groupby("simbolo").head(1) if not m.empty else m
        prime = prime[[t.tz_convert(NY).strftime("%H:%M") == "09:30" for t in prime.index]] if not prime.empty else prime
        aperture = dict(zip(prime["simbolo"], prime["open"])) if not prime.empty else {}
        dentro = set(membri(g))
        j = cal.index(g)
        for n, s in lista:
            if n in fatti:
                continue
            primo_giorno = candidati.get(g) is not None and (n, s) in candidati[g]
            if s not in dentro or s not in aperture:
                fatti.add(n)
                continue
            if s not in cache_ch:
                cache_ch[s] = chiusure_e_frazionamenti(s)
            ch, fr = cache_ch[s]
            if ch is None or cal[j - 1] not in ch.index:
                fatti.add(n)
                continue
            salto = aperture[s] / (ch[cal[j - 1]] / fr.get(g, 1.0)) - 1
            if abs(salto) >= SALTO:
                out.append((g, s, float(salto)))
                fatti.add(n)
            elif primo_giorno and j + 1 < len(cal):
                secondo.setdefault(cal[j + 1], []).append((n, s))
            else:
                fatti.add(n)
    return out


def main():
    membri, _ = membri_dell_indice()
    cal_df = alpaca.calendario("2016-01-01", "2024-12-31")
    cal = sorted(cal_df.index)
    ops = operazioni(cal, membri)
    print("operazioni in gioco:", len(ops), flush=True)
    scarti = scarti_misurati(RADICE / "dati" / "ESITO_CONTROLLI_UNIVERSO.md")
    per_giorno: dict[date, list] = {}
    for g, s, x in ops:
        per_giorno.setdefault(g, []).append((s, x))

    def costi_di(s, f):
        c = (Costi(mezzo_scarto=scarti[s] / 2, slittamento=0.5 * PB, **IB_FISSO) if s in scarti
             else Costi(mezzo_scarto=5 * PB, slittamento=2 * PB, **IB_FISSO))
        return Costi() if f == 0 else c if f == 1 else c.raddoppiati()

    def gira(fattore, multiplo):
        valore = CAPITALE
        giornalieri, per_op = {}, []
        for g in cal:
            lista = sorted(per_giorno.get(g, []), key=lambda x: -abs(x[1]))[:MASSIMO]
            if not lista:
                giornalieri[g] = 0.0
                continue
            f = cartella_dati() / "eventi" / "minuti" / f"{g}.csv.gz"
            m = pd.read_csv(f, index_col="t", parse_dates=["t"])
            guadagno = 0.0
            for s, _ in lista:
                b = m[m["simbolo"] == s][["open", "high", "low", "close", "volume", "vwap"]].sort_index()
                seg = pc.prepara(b, cal_df, set(), 5)
                if not (seg["direzione"] != 0).any():
                    continue
                capitale = QUOTA * valore
                r = simula(b, pc.strategia(seg, multiplo=multiplo), costi_di(s, fattore), capitale=capitale)
                e = r.esecuzioni
                if e.empty:
                    continue
                guadagno += r.valore.iloc[-1] - capitale
                per_op.append(r.valore.iloc[-1] / capitale - 1)
            giornalieri[g] = guadagno / valore
            valore += guadagno
        return pd.Series(giornalieri), np.array(per_op)

    g, pe = gira(1, 10.0)
    g2, _ = gira(2, 10.0)
    g0, pe0 = gira(0, 10.0)
    varianti = {m: annuo(asticella.sharpe(gira(1, m)[0])) for m in (5.0, 20.0, None)}
    g = g[g.index >= min(per_giorno)]
    g2, g0 = g2.loc[g.index], g0.loc[g.index]
    salva_serie("P020_notizie", g)
    tutte = carica_serie()
    sr, sr2 = annuo(asticella.sharpe(g)), annuo(asticella.sharpe(g2))
    sr_spy = annuo(asticella.sharpe(comprare_e_tenere("SPY", g.index.min(), g.index.max())))
    ast = asticella.sharpe_corretto(g, tutte)
    q = [float((1 + g[(g.index >= a) & (g.index < b)]).prod() - 1)
         for a, b in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1)))]
    quota = sum(x > 0 for x in q) / len(q)
    tot = lambda v: (1 + v).prod() - 1  # noqa: E731
    t_op = pe.mean() / pe.std(ddof=1) * math.sqrt(len(pe))
    anni = (1 + g).groupby(pd.Index([d.year for d in g.index])).prod() - 1
    # il tenere l'indice a pesi uguali (come la prova 11), sugli stessi giorni
    from stock.prove.p003 import rendimenti
    from stock.prove.p011 import carica_tutti, costi_per
    from stock.simulatore.portafoglio import simula_conto
    from stock.strategie.rimbalzo import strategia_tenere_l_indice
    _, simboli = membri_dell_indice()
    barre_g, _, _ = carica_tutti(simboli, date(2024, 12, 31))
    tutto = simula_conto(barre_g, strategia_tenere_l_indice(membri, cal), costi_per(list(barre_g), scarti, 1), capitale=CAPITALE)
    gt = rendimenti(tutto.valore[tutto.valore.index >= g.index.min()])
    sr_tutto = annuo(asticella.sharpe(gt))
    passa = sr > max(sr_spy, sr_tutto) and ast["sharpe_corretto"] >= 0.95 and sr2 > 0 and quota >= 0.6
    righe = ["# Prova 20 — risultati", "",
             f"Calcolato da `python -m stock.prove.p020` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P020_notizie_prima_candela.md` (committate prima). Dal {g.index.min()} al {g.index.max()}. Nel conto: {len(tutte)} serie.", "",
             f"* Comunicati sui risultati delle aziende dell'S&P 500: 22'929; giorni in gioco (salto all'apertura di almeno il 2%): {len(ops)}; "
             f"operazioni eseguite {len(pe)}.", "",
             "| | Azioni con notizie | Tenere lo SPY |", "|---|---|---|",
             f"| Per operazione con i costi (t) | {pe.mean() * 100:+.3f}% ({t_op:.2f}); in guadagno {np.mean(pe > 0):.0%}; senza costi {pe0.mean() * 100:+.3f}% | — |",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(g0):+.1%} / {tot(g):+.1%} / {tot(g2):+.1%} | — |",
             f"| Sharpe annuo senza costi | {annuo(asticella.sharpe(g0)):.2f} | — |",
             f"| **1.** Sharpe annuo con i costi | {sr:.2f} | {sr_spy:.2f} (indice a pesi uguali: {sr_tutto:.2f}) |",
             f"| **2.** Sharpe corretto per i tentativi (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}) | — |",
             f"| t dello Sharpe (da leggere, contro 3) | {ast['t_sharpe']:.2f} | — |",
             f"| **3.** Sharpe annuo con i costi doppi (> 0) | {sr2:.2f} | — |",
             f"| **4.** Trimestri in guadagno (almeno 60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — |",
             f"| Anni in guadagno (da leggere) | {(anni > 0).sum()} su {len(anni)} | — |",
             f"| Robustezza, Sharpe con i costi: obiettivo 5R / 20R / nessuno (da leggere) | {' / '.join(f'{varianti[m]:.2f}' for m in (5.0, 20.0, None))} | — |",
             f"| Perdita massima dal picco con i costi | {((1 + g).cumprod() / (1 + g).cumprod().cummax() - 1).min():.1%} | — |",
             f"| **Esito** | **{'passa la ricerca' if passa else 'bocciata'}** | |"]
    (QUI / "P020_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
