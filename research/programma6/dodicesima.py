"""Programma 6, dodicesima prova (DODICESIMA.md): K1, la media dei ranghi fra monete di −funding dei 7 giorni prima,
+quota di acquisti a mercato dei 7 giorni prima e +crescita dell'interesse aperto dei 7 giorni prima; long il quinto piu'
alto, short il piu' basso, pesi secondo la volatilita'. Sul passato e' costruzione; la prova e' il paper.

Uso: python3 -m research.programma6.dodicesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import nona as no
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import undicesima as un

QUI = Path(__file__).parent
RIS = QUI / "risultati_dodicesima"


def segnale_k1(pan: dict, ps: dict, pm: dict) -> np.ndarray:
    lun_idx = ps["lunedi"] - pan["t0"]
    parti = [-se.funding_7(pan, lun_idx), no.g1(pan, lun_idx), un.p2(pm, lun_idx)]
    Z = np.stack(parti, axis=2)
    R = te.ranghi(np.where(np.isfinite(Z), Z, np.nan), ps["U"])
    # te.ranghi mette 0 dove manca il dato: per la media servono le maschere dei dati veri
    ok = np.isfinite(Z)
    somma = np.where(ok, R, 0.0).sum(axis=2)
    n = ok.sum(axis=2)
    with np.errstate(all="ignore"):
        k = somma / n
    return np.where(ok[:, :, 0] & (n >= 2), k, np.nan)


def portafoglio_k1(pan: dict, ps: dict, pm: dict, costo: np.ndarray) -> pd.DataFrame:
    lun_idx = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun_idx)
    k = segnale_k1(pan, ps, pm)
    ct = np.where(np.isfinite(sig), k, np.nan)
    Wt = te.pesi_portafoglio(ct, ps["U"], np.nan_to_num(1.0 / sig), True)
    df = te.conto(Wt, ps["R"], ps["F"], costo)
    df.index = ps["lunedi"]
    return df


def esegui(log=print) -> dict:
    pan = sc.pannello()
    pm = un.pannello_metrics(pan)
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    df = portafoglio_k1(pan, ps, pm, sc.costi_moneta(ps["simboli"]))
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "settimane_K1.csv.gz")
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    e = te.esame(df, btc, inizio=un.INIZIO, anni_pieni=un.ANNI_PIENI)
    d = df[df.index >= un.INIZIO]
    e["dal_funding_annuo"] = float(-d["funding"].mean() * 52)
    e["dal_prezzo_annuo"] = float(d["lordo"].mean() * 52)
    sr = sc.sharpe_prove()
    for v in ("C1", "C2", "C3"):
        sr.append(json.loads((te.RIS / f"{v}.json").read_text())["intero"]["sharpe"])
    for v in ("F1", "F2"):
        sr.append(json.loads((se.RIS / f"{v}.json").read_text())["intero"]["sharpe"])
    sr.append(json.loads((ot.RIS / "esame.json").read_text())["cento"]["intero"]["sharpe"])
    nn = json.loads((no.RIS / "esame.json").read_text())
    sr += [nn["G1"]["cento"]["intero"]["sharpe"], nn["G2"]["cento"]["intero"]["sharpe"]]
    sr.append(json.loads((QUI / "risultati_decima" / "esame.json").read_text())["cento"]["intero"]["sharpe"])
    uu = json.loads((un.RIS / "esame.json").read_text())
    sr += [uu["P1"]["intero"]["sharpe"], uu["P2"]["intero"]["sharpe"], e["intero"]["sharpe"]]
    i = e["intero"]
    e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
    e["prove_nel_conto"] = len(sr)
    e["esito_informativo"] = te.esito(e, e["sharpe_corretto"])
    f3 = pd.read_csv(ot.RIS / "settimane_F3.csv.gz", index_col=0)["netto"]
    comuni = d.index.intersection(f3.index)
    e["correlazione_F3"] = float(np.corrcoef(d.loc[comuni, "netto"], f3.loc[comuni])[0, 1])
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    pa = e["per_anno"]
    testo = "\n".join([
        "# Programma 6 — dodicesima prova (K1: denaro che entra, leva che costa poco)", "",
        "Regole in `DODICESIMA.md` (scritte prima del calcolo). **Sul passato è costruzione, non prova**: due dei tre versi "
        "sono stati visti nelle prove 9 e 11. La prova è il paper dal 26 ottobre 2026.", "",
        f"* Dal 3 gennaio 2022: {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, Sharpe {i['sharpe']:.2f}, "
        f"discesa massima {100 * i['discesa_max']:.1f}%; media settimanale {100 * e['boot']['media']:+.3f}% (intervallo "
        f"{100 * e['boot']['basso']:+.3f}; {100 * e['boot']['alto']:+.3f}).",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in pa.items()) + f"; ultimo anno {100 * e['ultimo_anno']:+.1f}%.",
        f"* Dal prezzo {100 * e['dal_prezzo_annuo']:+.1f}% l'anno, dal funding {100 * e['dal_funding_annuo']:+.1f}%; a costi doppi "
        f"{100 * e['costi_doppi']:+.3f}% a settimana; correlazione con F3 {e['correlazione_F3']:.2f}.",
        f"* Sharpe corretto {e['sharpe_corretto']:.2f} con {e['prove_nel_conto']} prove; l'esame della terza prova direbbe: "
        f"{e['esito_informativo']} (solo informazione)."]) + "\n"
    (QUI / "RISULTATI_DODICESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("DODICESIMA FINITA", flush=True)
