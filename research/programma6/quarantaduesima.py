"""Programma 6, quarantaduesima prova (QUARANTADUESIMA.md): F6, F5 con l'esposizione secondo l'agitazione delle 13
settimane prima (0,30 / σ, al massimo 2), con il costo del cambio d'esposizione.

Uso: python3 -m research.programma6.quarantaduesima (dopo la quarantunesima)
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import quarantesima as qr
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantaduesima"
SETTIMANE, MINIMO, OBIETTIVO, TETTO, LATI, COSTO = 13, 8, 0.30, 2.0, 2.0, 0.0007


def esposizione(netto: pd.Series) -> pd.Series:
    sigma = netto.rolling(SETTIMANE, min_periods=MINIMO).std().shift(1) * math.sqrt(52)
    return (OBIETTIVO / sigma).clip(upper=TETTO).fillna(1.0)


def gestita(f5: pd.DataFrame) -> pd.DataFrame:
    w = esposizione(f5["netto"])
    cambio = w.diff().abs().fillna(0.0) * LATI * COSTO
    out = pd.DataFrame({"netto": w * f5["netto"] - cambio, "netto_doppio": w * f5["netto_doppio"] - 2 * cambio, "w": w})
    for k in ("lordo", "spese", "funding", "long", "short"):
        out[k] = w * f5[k]
    out["giro"] = w * f5["giro"] + w.diff().abs().fillna(0.0) * LATI
    out["monete"] = f5["monete"]
    return out


def esegui(log=print) -> dict:
    f5 = pd.read_csv(QUI / "risultati_ventiquattresima" / "settimane_F5.csv.gz", index_col=0)
    f6 = gestita(f5)
    RIS.mkdir(exist_ok=True)
    f6.to_csv(RIS / "settimane_F6.csv.gz")
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    sr = qr.prove_fino_alla_trentanovesima()
    sr.append(json.loads((QUI / "risultati_quarantesima" / "esame.json").read_text())["portafoglio"]["intero"]["sharpe"])
    sr.append(json.loads((QUI / "risultati_quarantunesima" / "esame.json").read_text())["portafoglio"]["intero"]["sharpe"])
    e = te.esame(f6, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    e5 = te.esame(f5, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    sr.append(e["intero"]["sharpe"])
    i = e["intero"]
    e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
    e["prove_nel_conto"] = len(sr)
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    w = f6.loc[f6.index >= se.INIZIO, "w"]
    e["esposizione"] = {"media": float(w.mean()), "minima": float(w.min()), "massima": float(w.max()),
                        "settimane_al_tetto": int((w >= TETTO - 1e-12).sum()), "settimane": int(len(w))}
    e["F5_stesse_settimane"] = {k: e5["intero"][k] for k in ("sharpe", "annuo", "volatilita", "discesa_max")}
    e["F5_per_anno"] = e5["per_anno"]
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    x, f = e["esposizione"], e["F5_stesse_settimane"]
    testo = "\n".join([
        "# Programma 6 — risultati della quarantaduesima prova (F6: F5 con l'esposizione secondo l'agitazione)", "",
        "Regole in `QUARANTADUESIMA.md` (scritte prima).", "",
        f"* F6: Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; a costi doppi {100 * 52 * e['costi_doppi']:+.1f}% l'anno.",
        f"* F5 sulle stesse settimane: Sharpe {f['sharpe']:.2f}, {100 * f['annuo']:+.1f}% l'anno, volatilità "
        f"{100 * f['volatilita']:.1f}%, discesa {100 * f['discesa_max']:.1f}%.",
        f"* Esposizione media {x['media']:.2f} (da {x['minima']:.2f} a {x['massima']:.2f}), al tetto {x['settimane_al_tetto']} "
        f"settimane su {x['settimane']}.",
        "* Per anno: F6 " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + "; F5 "
        + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["F5_per_anno"].items()) + ".",
        f"* Sharpe corretto {e['sharpe_corretto']:.2f} con {len(sr)} prove (serve 0,95).", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_QUARANTADUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTADUESIMA FINITA", flush=True)
