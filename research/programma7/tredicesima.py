"""Programma 7, tredicesima prova (TREDICESIMA.md): G11, G1 con il segnale dalla media dei ranghi di −funding dei 7 giorni e
dell'ultimo giorno.

Uso: python3 -m research.programma7.tredicesima
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

QUI = Path(__file__).parent
RIS = QUI / "risultati_tredicesima"


def segnale_fresco(pan: dict, idx: np.ndarray, U: np.ndarray) -> np.ndarray:
    """Media dei ranghi (fra le monete dell'universo) di −funding dei 7 giorni e di −funding dell'ultimo giorno."""
    f7 = -se.funding_7(pan, idx)
    f1 = -np.round(pan["funding"][idx - 1], 12)
    Z = np.stack([f7, f1], axis=2)
    ok = np.isfinite(Z)
    R = te.ranghi(np.where(ok, Z, np.nan), U)
    n = ok.sum(axis=2)
    with np.errstate(all="ignore"):
        s = np.where(ok, R, 0.0).sum(axis=2) / n
    return np.where(ok.all(axis=2), s, np.nan)


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    W = vq.pesi_banda(np.where(np.isfinite(sig), segnale_fresco(pan, idx, Ud), np.nan), Ud, sig)
    R, F = sc.rendimenti(pan)[idx], np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    g = te.conto(W, R, F, costo)
    g["spese"] = cs.spese_a_limite(W, R, giorni, pan["simboli"], costo)[0]
    g["netto"] = g["lordo"] - g["spese"] - g["funding"]
    g["netto_doppio"] = g["lordo"] - 2 * g["spese"] - g["funding"]
    sett = pr.per_settimana(g, giorni)
    RIS.mkdir(exist_ok=True)
    sett.to_csv(RIS / "settimane_G11.csv.gz")
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    e = te.esame(sett, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    g1 = pd.read_csv(QUI / "risultati_prima" / "settimane_G1.csv.gz", index_col=0)
    e1 = te.esame(g1, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    e["G1"] = {k: e1["intero"][k] for k in ("sharpe", "annuo", "discesa_max")} | {"spese_annue": e1["spese_annue"]}
    e["movimenti"] = pr.movimenti(W)
    c = sett.index.intersection(g1.index)
    e["correlazione_G1"] = float(np.corrcoef(sett.loc[c, "netto"], g1.loc[c, "netto"])[0, 1])
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "57 G1": g1["netto"], "69 G11": sett["netto"]}, {"69 G11": e["intero"]})
    r = rivisto["candidate"]["69 G11"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, q, mv = e["intero"], e["G1"], e["movimenti"]
    testo = "\n".join([
        "# Programma 7 — risultati della tredicesima prova (G11: G1 con il funding fresco)", "",
        "Regole in `TREDICESIMA.md` (scritte prima).", "",
        f"* Operazioni: {mv['entrate_al_giorno']:.1f} entrate e {mv['uscite_al_giorno']:.1f} uscite al giorno; una posizione dura in media "
        f"{mv['durata_media_giorni']:.1f} giorni.",
        f"* G11: Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno.",
        f"* G1 sulle stesse settimane: Sharpe {q['sharpe']:.2f}, {100 * q['annuo']:+.1f}% l'anno, discesa {100 * q['discesa_max']:.1f}%, spese "
        f"{100 * q['spese_annue']:.1f}%; correlazione {e['correlazione_G1']:.2f}.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Sharpe corretto {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}.", "",
        f"**Esito: {e['esito']}** (per la riserva di `TREDICESIMA.md`, se passasse non sarebbe una scoperta indipendente da F5)."]) + "\n"
    (QUI / "RISULTATI_TREDICESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TREDICESIMA FINITA", flush=True)
