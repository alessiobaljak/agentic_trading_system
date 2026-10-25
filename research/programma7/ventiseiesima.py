"""Programma 7, ventiseiesima prova (VENTISEIESIMA.md): G1N, G1 neutra al mercato: i due lati scalati ogni giorno perche' la somma
dei beta (90 giorni prima, verso la media dell'universo del giorno) sia zero; ordini limite come G1; controllo con il peso fisso.

Uso: python3 -m research.programma7.ventiseiesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import cinquantaseiesima as cs
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma7 import prima as pr
from research.programma7 import ventiquattresima as f5n

QUI = Path(__file__).parent
RIS = QUI / "risultati_ventiseiesima"


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
    log("[ventiseiesima] pesi di G1 fatti; beta giornalieri")
    beta = f5n.beta_delle_monete(pan, Ud, idx)
    WN, a, b, bl, bs = f5n.scala_neutra(W, beta)
    WF = np.where(W > 0, W * f5n.FISSO[0], W * f5n.FISSO[1])
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    conti, ordini = {}, {}
    for nome, Wx in (("G1", W), ("G1N", WN), ("G1 120/80", WF)):
        mercato = te.conto(Wx, R, F, costo)
        spese, n_tot, n_lim, n_senza = cs.spese_a_limite(Wx, R, giorni, pan["simboli"], costo)
        limite = mercato.copy()
        limite["spese"] = spese
        limite["netto"] = limite["lordo"] - limite["spese"] - limite["funding"]
        limite["netto_doppio"] = limite["lordo"] - 2 * limite["spese"] - limite["funding"]
        conti[nome] = pr.per_settimana(limite, giorni)
        ordini[nome] = {"variazioni": n_tot, "a_limite": n_lim}
        log(f"[ventiseiesima] {nome}: conto fatto")
    RIS.mkdir(exist_ok=True)
    for nome, d in conti.items():
        d.to_csv(RIS / f"settimane_{nome.replace(' ', '_').replace('/', '-')}.csv.gz")
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    out = {n: te.esame(d, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI) for n, d in conti.items()}
    out["beta"] = {"long_medio": float(np.nanmean(bl)), "short_medio": float(np.nanmean(bs)), "a_medio": float(a.mean()),
                   "b_medio": float(b.mean()), "giorni_al_limite": int(((a <= f5n.LIMITI[0]) | (a >= f5n.LIMITI[1])).sum())}
    peggiori = conti["G1"].nsmallest(15, "netto").index
    out["quindici_peggiori"] = {n: float(conti[n].loc[peggiori, "netto"].mean()) for n in conti}
    out["correlazione_G1N_G1"] = float(np.corrcoef(conti["G1N"]["netto"], conti["G1"]["netto"])[0, 1])
    out["ordini"] = ordini
    serie = {**ast.serie_nuove(), "88 G1N": conti["G1N"]["netto"], "88 G1 120/80": conti["G1 120/80"]["netto"]}
    rivisto = ast.corretto_rivisto(serie, {"88 G1N": out["G1N"]["intero"], "88 G1 120/80": out["G1 120/80"]["intero"]})
    for n in ("G1N", "G1 120/80"):
        r = rivisto["candidate"][f"88 {n}"]
        out[n]["sharpe_corretto"], out[n]["t"], out[n]["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
        out[n]["esito"] = te.esito(out[n], out[n]["sharpe_corretto"])
        out[n]["regola_del_proprietario"] = bool(out[n]["sharpe_corretto"] >= 0.90 and all(v > 0 for v in out[n]["per_anno"].values())
                                                 and out[n]["t"] > 3)
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    bb = out["beta"]
    righe = ["# Programma 7 — risultati della ventiseiesima prova (G1N: G1 neutra al mercato)", "",
             "Regole in `VENTISEIESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 5 ottobre 2026, con gli ordini limite.", "",
             "| | Sharpe | l'anno | volatilità | discesa | spese l'anno | per anno |", "|---|---|---|---|---|---|---|"]
    for n in ("G1", "G1N", "G1 120/80"):
        i = out[n]["intero"]
        righe.append(f"| {n} | {i['sharpe']:.2f} | {100 * i['annuo']:+.1f}% | {100 * i['volatilita']:.1f}% | {100 * i['discesa_max']:.1f}% | "
                     f"{100 * out[n]['spese_annue']:.1f}% | " + ", ".join(f"{y} {100 * v:+.1f}%" for y, v in out[n]["per_anno"].items()) + " |")
    righe += ["",
              f"* Beta medio del lato long {bb['long_medio']:.2f}, del lato short {bb['short_medio']:.2f}; scalatura media long "
              f"{bb['a_medio']:.2f}, short {bb['b_medio']:.2f}; giorni al limite {bb['giorni_al_limite']}.",
              "* Le 15 settimane peggiori di G1, rifatte: " + ", ".join(f"{n} {100 * v:+.2f}%" for n, v in out["quindici_peggiori"].items())
              + f". Correlazione G1N-G1 {out['correlazione_G1N_G1']:.2f}.",
              *(f"* **{n}**: Sharpe corretto {out[n]['sharpe_corretto']:.2f} ({out[n]['gruppi']} gruppi), t {out[n]['t']:.2f}; esito "
                f"{out[n]['esito']}; regola del proprietario: {'sì' if out[n]['regola_del_proprietario'] else 'no'}." for n in ("G1N", "G1 120/80"))]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_VENTISEIESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTISEIESIMA FINITA", flush=True)
