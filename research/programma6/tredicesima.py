"""Programma 6, tredicesima prova (TREDICESIMA.md): long o short il Bitcoin secondo il terzo in cui cade il funding
medio del mercato (media fra le 100 monete dell'universo della somma del funding dei 7 giorni prima) rispetto alle 52
settimane prima.

Uso: python3 -m research.programma6.tredicesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te

QUI = Path(__file__).parent
RIS = QUI / "risultati_tredicesima"


def posizioni(media: np.ndarray) -> np.ndarray:
    """+1, −1 o 0 per settimana, dal terzo della media del mercato fra le 52 settimane prima (almeno 26)."""
    out = np.zeros(len(media))
    for w in range(len(media)):
        prima = media[max(0, w - 52): w]
        prima = prima[np.isfinite(prima)]
        if len(prima) < 26 or not np.isfinite(media[w]):
            continue
        basso, alto = np.quantile(prima, [1 / 3, 2 / 3])
        out[w] = 1.0 if media[w] <= basso else (-1.0 if media[w] >= alto else 0.0)
    return out


def esegui() -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun_idx = ps["lunedi"] - pan["t0"]
    S7 = se.funding_7(pan, lun_idx)
    with np.errstate(all="ignore"):
        media = np.array([np.nanmean(np.where(ps["U"][w], S7[w], np.nan)) if ps["U"][w].any() else np.nan
                          for w in range(len(lun_idx))])
    pos = posizioni(media)
    jb = ps["simboli"].index("BTCUSDT")
    S = len(ps["simboli"])
    Wt = np.zeros((len(pos), S))
    Wt[:, jb] = pos
    df = te.conto(Wt, ps["R"], ps["F"], sc.costi_moneta(ps["simboli"]))
    df.index = ps["lunedi"]
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    RIS.mkdir(exist_ok=True)
    df.assign(posizione=pos, funding_mercato=media).to_csv(RIS / "settimane.csv.gz")
    e = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    b = btc[btc.index >= se.INIZIO]
    e["btc_sharpe"] = float(b.mean() / b.std(ddof=1) * np.sqrt(52))
    d = df[df.index >= se.INIZIO]
    p = pd.Series(pos, index=ps["lunedi"])[d.index]
    e["settimane_long"] = int((p > 0).sum())
    e["settimane_short"] = int((p < 0).sum())
    e["settimane_fuori"] = int((p == 0).sum())
    e["long_annuo"] = float(d["netto"][p > 0].sum() / len(d) * 52)
    e["short_annuo"] = float(d["netto"][p < 0].sum() / len(d) * 52)
    sr = sc.sharpe_prove()
    # tutte le prove del programma 6 fino alla dodicesima, piu' questa (34 in tutto)
    sr += [json.loads((te.RIS / f"{v}.json").read_text())["intero"]["sharpe"] for v in ("C1", "C2", "C3")]
    sr += [json.loads((se.RIS / f"{v}.json").read_text())["intero"]["sharpe"] for v in ("F1", "F2")]
    sr.append(json.loads((QUI / "risultati_ottava" / "esame.json").read_text())["cento"]["intero"]["sharpe"])
    nn = json.loads((QUI / "risultati_nona" / "esame.json").read_text())
    sr += [nn["G1"]["cento"]["intero"]["sharpe"], nn["G2"]["cento"]["intero"]["sharpe"]]
    sr.append(json.loads((QUI / "risultati_decima" / "esame.json").read_text())["cento"]["intero"]["sharpe"])
    uu = json.loads((QUI / "risultati_undicesima" / "esame.json").read_text())
    sr += [uu["P1"]["intero"]["sharpe"], uu["P2"]["intero"]["sharpe"]]
    sr.append(json.loads((QUI / "risultati_dodicesima" / "esame.json").read_text())["intero"]["sharpe"])
    sr.append(e["intero"]["sharpe"])
    i = e["intero"]
    e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
    e["prove_nel_conto"] = len(sr)
    es = te.esito(e, e["sharpe_corretto"])
    if es in ("VALIDA", "niente in più del Bitcoin"):
        es = "VALIDA" if i["sharpe"] > e["btc_sharpe"] and es == "VALIDA" else (es if es != "VALIDA" else "non batte il Bitcoin in Sharpe")
    e["esito"] = es
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    pa = e["per_anno"]
    testo = "\n".join([
        "# Programma 6 — risultati della tredicesima prova (il funding del mercato per il Bitcoin)", "",
        "Regole in `TREDICESIMA.md` (scritte prima). Dal 4 gennaio 2021.", "",
        f"* {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, **Sharpe {i['sharpe']:.2f}** (Bitcoin sempre "
        f"comprato {e['btc_sharpe']:.2f}), discesa massima {100 * i['discesa_max']:.1f}%; media settimanale "
        f"{100 * e['boot']['media']:+.3f}% (intervallo {100 * e['boot']['basso']:+.3f}; {100 * e['boot']['alto']:+.3f}).",
        f"* Settimane long {e['settimane_long']}, short {e['settimane_short']}, fuori {e['settimane_fuori']}; dalla parte long "
        f"{100 * e['long_annuo']:+.1f}% l'anno, dalla parte short {100 * e['short_annuo']:+.1f}%.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in pa.items()) + f"; ultimo anno {100 * e['ultimo_anno']:+.1f}%.",
        f"* Sharpe corretto {e['sharpe_corretto']:.2f} con {e['prove_nel_conto']} prove.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_TREDICESIMA.md").write_text(testo, encoding="utf-8")
    print(testo)
    return e


if __name__ == "__main__":
    esegui()
