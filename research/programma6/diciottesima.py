"""Programma 6, diciottesima prova (DICIOTTESIMA.md): le monete appena quotate. Ogni lunedi' short le monete con eta' fra 7
e 60 giorni (N1) o fra 7 e 180 (N2), a pesi uguali e al massimo il 10% ciascuna; long le 100 piu' scambiate con lo stesso
peso totale, pesi secondo la volatilita'. Dati con le correzioni di ``controllo_zombi``.

Uso: python3 -m research.programma6.diciottesima
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import controllo_zombi as cz
from research.programma6 import ottava as ot
from research.programma6 import quattordicesima as q
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6.motore import TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_diciottesima"
VARIANTI = {"N1": (7, 60), "N2": (7, 180)}
TETTO, MIN_GIOVANI, SCARTO_GIOVANI = 0.10, 3, 0.0010
FASCE = ((7, 30), (30, 60), (60, 120), (120, 180))


def eta_lunedi(pan: dict, lun: np.ndarray) -> np.ndarray:
    """Giorni dalla prima candela alla domenica prima di ogni lunedi' (NaN se la moneta non c'era ancora)."""
    ok = np.isfinite(pan["close"])
    primo = np.where(ok.any(axis=0), ok.argmax(axis=0), ok.shape[0])
    e = (lun[:, None] - 1) - primo[None, :]
    return np.where(e >= 0, e, np.nan).astype(float)


def giovani(pan: dict, lun: np.ndarray, da: int, a: int) -> np.ndarray:
    """Maschera settimane × monete delle giovani ammesse (sezione 2)."""
    C, O, V = pan["close"], pan["open"], pan["quote_volume"]
    eta = eta_lunedi(pan, lun)
    G = np.zeros(eta.shape, bool)
    for k, m in enumerate(lun):
        cand = np.flatnonzero((eta[k] >= da) & (eta[k] <= a))
        if not len(cand):
            continue
        fin = V[max(0, m - 30): m][:, cand]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            med = np.nan_to_num(np.nanmedian(fin, axis=0), nan=0.0)
        amm = (med >= sc.VOLUME_MIN) & np.isfinite(C[m - 1, cand]) & (np.nan_to_num(V[m - 1, cand]) > 0) \
            & np.isfinite(O[m, cand])
        G[k, cand[amm]] = True
    return G


def pesi(G: np.ndarray, U: np.ndarray, sig: np.ndarray) -> np.ndarray:
    W, S = G.shape
    out = np.zeros((W, S))
    for k in range(W):
        gi = np.flatnonzero(G[k])
        vec = np.flatnonzero(U[k] & np.isfinite(sig[k]) & (sig[k] > 0))
        if len(gi) < MIN_GIOVANI or len(vec) < te.MIN_MONETE:
            continue
        w = min(1.0 / len(gi), TETTO)
        out[k, gi] = -w
        inv = 1.0 / sig[k, vec]
        out[k, vec] = w * len(gi) * inv / inv.sum()
    return out


def conto(Wt: np.ndarray, R: np.ndarray, F: np.ndarray, costo: np.ndarray) -> pd.DataFrame:
    """Come ``terza.conto`` ma con il costo per settimana e moneta, e il funding del lato short a parte."""
    Wn, S = Wt.shape
    R0 = np.nan_to_num(R)
    righe, deriva = [], np.zeros(S)
    for w in range(Wn):
        x = Wt[w]
        d = np.abs(x - deriva)
        lordo_i, fund_i, spesa_i = x * R0[w], x * F[w], d * costo[w]
        lordo, spese, fund = lordo_i.sum(), spesa_i.sum(), fund_i.sum()
        netto = lordo - spese - fund
        L, Sh = x > 0, x < 0
        righe.append({"lordo": lordo, "spese": spese, "funding": fund, "netto": netto,
                      "netto_doppio": lordo - 2 * spese - fund, "giro": d.sum(),
                      "long": lordo_i[L].sum() - spesa_i[L].sum() - fund_i[L].sum(),
                      "short": lordo_i[Sh].sum() - spesa_i[Sh].sum() - fund_i[Sh].sum(),
                      "funding_short": fund_i[Sh].sum(), "giovani": int(Sh.sum()), "monete": int((x != 0).sum())})
        deriva = x * (1 + R0[w]) / (1 + netto) if 1 + netto > 0 else np.zeros(S)
    return pd.DataFrame(righe)


def prove_fino_alla_diciassettesima() -> list:
    sr = q.tutte_le_prove()
    ee = json.loads((QUI / "risultati_quattordicesima" / "esame.json").read_text())
    sr += [ee["M1"]["intero"]["sharpe"], ee["M2"]["intero"]["sharpe"],
           json.loads((QUI / "risultati_quindicesima" / "esame.json").read_text())["intero"]["sharpe"],
           json.loads((QUI / "risultati_sedicesima" / "esame.json").read_text())["intero"]["sharpe"]]
    e17 = json.loads((QUI / "risultati_diciassettesima" / "esame.json").read_text())
    sr += [e17["M4"]["intero"]["sharpe"], e17["M5"]["intero"]["sharpe"]]
    return sr


def descrizione(pan: dict, ps: dict, G: np.ndarray, sig: np.ndarray) -> dict:
    """Quanto le giovani fanno meno delle vecchie (lordo, senza costi), per eta' e per anno di quotazione. Solo per capire."""
    lun = ps["lunedi"] - pan["t0"]
    eta = eta_lunedi(pan, lun)
    R = np.nan_to_num(ps["R"])
    vecchie = np.full(len(lun), np.nan)
    for k in range(len(lun)):
        vec = np.flatnonzero(ps["U"][k] & np.isfinite(sig[k]) & (sig[k] > 0))
        if len(vec) >= te.MIN_MONETE:
            inv = 1.0 / sig[k, vec]
            vecchie[k] = (inv / inv.sum()) @ R[k, vec]
    dentro = ps["lunedi"] >= se.INIZIO
    ok = np.isfinite(pan["close"])
    primo = ok.argmax(axis=0)
    anno_q = pd.to_datetime((primo + pan["t0"]) * 86400, unit="s").year.to_numpy()
    out = {"per_eta": {}, "per_anno_di_quotazione": {}}
    for da, a in FASCE:
        m = G & (eta >= da) & (eta < a) & dentro[:, None] & np.isfinite(vecchie)[:, None]
        diff = (vecchie[:, None] - R)[m]
        out["per_eta"][f"{da}-{a}"] = {"monete_settimana": int(m.sum()), "in_meno_a_settimana": float(diff.mean()) if m.any() else float("nan")}
    for y in sorted(set(anno_q[G.any(axis=0)])):
        m = G & (anno_q[None, :] == y) & dentro[:, None] & np.isfinite(vecchie)[:, None]
        if m.any():
            diff = (vecchie[:, None] - R)[m]
            out["per_anno_di_quotazione"][int(y)] = {"monete_settimana": int(m.sum()), "in_meno_a_settimana": float(diff.mean())}
    return out


def esegui(log=print) -> dict:
    pan0 = sc.pannello()
    pan, ps = cz.correggi(pan0, False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    f3 = pd.read_csv(QUI / "risultati_ottava" / "settimane_F3.csv.gz", index_col=0)["netto"]
    m1 = pd.read_csv(QUI / "risultati_quattordicesima" / "settimane_M1.csv.gz", index_col=0)["netto"]
    costo_base = sc.costi_moneta(ps["simboli"])
    RIS.mkdir(exist_ok=True)
    sr = prove_fino_alla_diciassettesima()
    esami = {}
    for nome, (da, a) in VARIANTI.items():
        G = giovani(pan, lun, da, a)
        Wt = pesi(G, ps["U"], sig)
        costo = np.where(G, TAKER + SCARTO_GIOVANI, costo_base[None, :])
        df = conto(Wt, ps["R"], ps["F"], costo)
        df.index = ps["lunedi"]
        df.to_csv(RIS / f"settimane_{nome}.csv.gz")
        e = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        d = df[df.index >= se.INIZIO]
        e["funding_short_annuo"] = float(d["funding_short"].mean() * 52)
        e["giovani_medie"] = float(d["giovani"].mean())
        e["giovani_per_anno"] = {int(y): float(d["giovani"][pd.to_datetime(d.index * 86400, unit="s").year == y].mean())
                                 for y in sorted(set(pd.to_datetime(d.index * 86400, unit="s").year))}
        for n, s in (("F3", f3), ("M1", m1)):
            c = d.index.intersection(s.index)
            e[f"correlazione_{n}"] = float(np.corrcoef(d.loc[c, "netto"], s.loc[c])[0, 1])
        e["descrizione"] = descrizione(pan, ps, G, sig)
        esami[nome] = e
        sr.append(e["intero"]["sharpe"])
        log(f"[diciottesima] {nome}: Sharpe {e['intero']['sharpe']:.2f}")
    for nome, e in esami.items():
        i = e["intero"]
        e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
        e["prove_nel_conto"] = len(sr)
        e["esito"] = te.esito(e, e["sharpe_corretto"])
    (RIS / "esame.json").write_text(json.dumps(esami, ensure_ascii=False, indent=1), encoding="utf-8")
    righe = ["# Programma 6 — risultati della diciottesima prova (le monete appena quotate)", "",
             "Regole in `DICIOTTESIMA.md` (scritte prima). Dal 4 gennaio 2021, ogni lunedì; dati con le correzioni del "
             "controllo del 20 ottobre (`controllo_zombi.py`).", "",
             "| Variante | Rendimento/anno | Sharpe | Intervallo (settimana) | Sharpe corretto | Anni positivi | Ultimo anno | "
             "Lato short | Funding del lato short | Giovani in media | Beta BTC | Correlazione F3, M1 | Esito |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for nome, e in esami.items():
        i = e["intero"]
        anni = sum(1 for x in e["per_anno"].values() if x > 0)
        righe.append(f"| {nome} (età {VARIANTI[nome][0]}-{VARIANTI[nome][1]} giorni) | {100 * i['annuo']:+.1f}% | "
                     f"{i['sharpe']:.2f} | {100 * e['boot']['basso']:+.2f}%; {100 * e['boot']['alto']:+.2f}% | "
                     f"{e['sharpe_corretto']:.2f} | {anni}/{len(e['per_anno'])} | {100 * e['ultimo_anno']:+.1f}% | "
                     f"{100 * e['short_annuo']:+.1f}% | {100 * e['funding_short_annuo']:+.1f}% | {e['giovani_medie']:.1f} | "
                     f"{e['beta_btc']:.2f} | {e['correlazione_F3']:.2f}, {e['correlazione_M1']:.2f} | {e['esito']} |")
    for nome, e in esami.items():
        de = e["descrizione"]
        righe += ["", f"**{nome}, per anno**: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items())
                  + f"; giovani in media per anno: " + ", ".join(f"{a} {v:.1f}" for a, v in e["giovani_per_anno"].items()),
                  f"**{nome}, quanto le giovani fanno meno delle vecchie a settimana (lordo, solo per capire)**: per età "
                  + ", ".join(f"{k} giorni {100 * v['in_meno_a_settimana']:+.2f}% ({v['monete_settimana']})" for k, v in de["per_eta"].items())
                  + "; per anno di quotazione " + ", ".join(f"{k} {100 * v['in_meno_a_settimana']:+.2f}% ({v['monete_settimana']})"
                                                             for k, v in de["per_anno_di_quotazione"].items())]
    righe += ["", f"Sharpe corretto con {len(sr)} prove (serve almeno 0,95)."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_DICIOTTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return esami


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("DICIOTTESIMA FINITA", flush=True)
