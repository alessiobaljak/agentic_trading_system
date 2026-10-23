"""Programma 7, settima prova (SETTIMA.md): G6, K2 decisa ogni giorno con gli ordini limite, e G1 + G6 a rischio uguale.

Uso: python3 -m research.programma7.settima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import cinquantaseiesima as cs
from research.programma6 import dodicesima as do
from research.programma6 import ottava as ot
from research.programma6 import quindicesima as qd
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import undicesima as un
from research.programma6 import ventiquattresima as vq
from research.programma7 import prima as pr

QUI = Path(__file__).parent
RIS = QUI / "risultati_settima"
INIZIO = sc.giorno(2022, 1, 3)


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    giorni = np.arange(INIZIO, pr.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    k = do.segnale_k1(pan, {"lunedi": giorni, "U": Ud}, un.pannello_metrics(pan))
    W = vq.pesi_banda(np.where(np.isfinite(sig), k, np.nan), Ud, sig)
    R, F = sc.rendimenti(pan)[idx], np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    g = te.conto(W, R, F, costo)
    spese, n_tot, n_lim, n_senza = cs.spese_a_limite(W, R, giorni, pan["simboli"], costo)
    g["spese"] = spese
    g["netto"] = g["lordo"] - g["spese"] - g["funding"]
    g["netto_doppio"] = g["lordo"] - 2 * g["spese"] - g["funding"]
    g6 = pr.per_settimana(g, giorni)
    g1 = pd.read_csv(QUI / "risultati_prima" / "settimane_G1.csv.gz", index_col=0)
    insieme = qd.combina({"G1": g1, "G6": g6})
    RIS.mkdir(exist_ok=True)
    g6.to_csv(RIS / "settimane_G6.csv.gz")
    insieme.to_csv(RIS / "settimane_G1_G6.csv.gz")
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    k2 = pd.read_csv(QUI.parent / "programma6" / "risultati_controllo_parita" / "settimane_K2.csv.gz", index_col=0)
    k2 = k2[(k2.index >= INIZIO) & (k2.index < pr.FINE)]
    out = {"G6": te.esame(g6, btc, inizio=INIZIO, anni_pieni=(2022, 2023, 2024, 2025)),
           "G1 + G6": te.esame(insieme, btc, inizio=INIZIO, anni_pieni=(2022, 2023, 2024, 2025))}
    ek2 = te.esame(k2, btc, inizio=INIZIO, anni_pieni=(2022, 2023, 2024, 2025))
    out["G6"]["K2_settimanale"] = {x: ek2["intero"][x] for x in ("sharpe", "annuo", "discesa_max")} | {"spese_annue": ek2["spese_annue"]}
    out["G6"]["movimenti"] = pr.movimenti(W)
    out["G6"]["ordini"] = {"variazioni": n_tot, "eseguite_con_il_limite": n_lim, "senza_candele_a_1_ora": n_senza}
    c = g6.index.intersection(g1.index)
    out["G6"]["correlazione_G1"] = float(np.corrcoef(g6.loc[c, "netto"], g1.loc[c, "netto"])[0, 1])
    nuove = {**ast.serie_nuove(), "57 G1": g1["netto"], "63 G6": g6["netto"], "63 G1+G6": insieme["netto"]}
    rivisto = ast.corretto_rivisto(nuove, {"63 G6": out["G6"]["intero"], "63 G1+G6": out["G1 + G6"]["intero"]})
    for n, ch in (("G6", "63 G6"), ("G1 + G6", "63 G1+G6")):
        r = rivisto["candidate"][ch]
        out[n]["sharpe_corretto"], out[n]["t"], out[n]["gruppo"] = r["corretto_con_aggiunta"], r["t"], r["gruppo"]
        out[n]["esito"] = te.esito(out[n], out[n]["sharpe_corretto"])
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    mv, q = out["G6"]["movimenti"], out["G6"]["K2_settimanale"]
    righe = ["# Programma 7 — risultati della settima prova (G6: K2 decisa ogni giorno; G1 + G6)", "",
             "Regole in `SETTIMA.md` (scritte prima). Dal 3 gennaio 2022.", "",
             f"* G6 opera ogni giorno: {mv['entrate_al_giorno']:.1f} entrate e {mv['uscite_al_giorno']:.1f} uscite al giorno, una "
             f"posizione dura in media {mv['durata_media_giorni']:.1f} giorni; correlazione con G1 {out['G6']['correlazione_G1']:.2f}.",
             f"* K2 settimanale sulle stesse settimane: Sharpe {q['sharpe']:.2f}, {100 * q['annuo']:+.1f}% l'anno, discesa "
             f"{100 * q['discesa_max']:.1f}%, spese {100 * q['spese_annue']:.1f}%.", "",
             "| Strategia | Sharpe | l'anno | volatilità | discesa | spese l'anno | Sharpe corretto | t | Esito |", "|---|---|---|---|---|---|---|---|---|"]
    for n in ("G6", "G1 + G6"):
        i = out[n]["intero"]
        righe.append(f"| {n} | {i['sharpe']:.2f} | {100 * i['annuo']:+.1f}% | {100 * i['volatilita']:.1f}% | {100 * i['discesa_max']:.1f}% | "
                     f"{100 * out[n]['spese_annue']:.1f}% | {out[n]['sharpe_corretto']:.2f} | {out[n]['t']:.2f} | {out[n]['esito']} |")
    righe += [""] + [f"* {n} per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in out[n]["per_anno"].items()) for n in ("G6", "G1 + G6")]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_SETTIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SETTIMA FINITA", flush=True)
