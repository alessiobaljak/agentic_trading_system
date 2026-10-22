"""Programma 6, quarantasettesima prova (QUARANTASETTESIMA.md): O1 e O2, long il perpetuo (BTC, ETH) per la settimana se
il premio delle opzioni della domenica (DVOL² − volatilita' realizzata dei 30 giorni²) e' sopra la sua mediana delle 52
domeniche prima, altrimenti niente. Trimestri dell'esame sugli anni pieni 2023-2025 (il 2022 e' a meta').

Uso: python3 -m research.programma6.scarico_dvol && python3 -m research.programma6.quarantasettesima
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import quarantacinquesima as qc
from research.programma6 import scarico_dvol as sd
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6.motore import TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantasettesima"
A = sc.giorno(2026, 10, 5)
COSTO, SETTIMANE_MEDIANA = TAKER + 0.0001, 52


def premio(pan: dict, j: int, dvol: pd.Series) -> pd.Series:
    """Giorno → DVOL² − (volatilita' realizzata dei 30 giorni, all'anno, in punti)²."""
    C = pd.Series(pan["close"][:, j], index=np.arange(pan["close"].shape[0]) + pan["t0"])
    rv = np.log(C).diff().rolling(30, min_periods=30).std() * math.sqrt(365) * 100
    return (dvol.reindex(C.index) ** 2 - rv ** 2).dropna()


def settimane(pan: dict, j: int, pr: pd.Series) -> pd.DataFrame:
    O, F, t0 = pan["open"][:, j], pan["funding"][:, j], pan["t0"]
    domeniche = pr[((pr.index + 3) % 7) == 6]
    righe, w_prima = [], 0.0
    for k in range(SETTIMANE_MEDIANA, len(domeniche)):
        m = int(domeniche.index[k]) + 1
        if m > A or m - t0 + 7 >= len(O):
            break
        soglia = float(np.median(domeniche.iloc[k - SETTIMANE_MEDIANA: k].to_numpy()))
        w = 1.0 if domeniche.iloc[k] > soglia else 0.0
        i = m - t0
        tenuta = O[i + 7] / O[i] - 1
        fund = float(F[i: i + 7].sum())
        spese = abs(w - w_prima) * COSTO
        righe.append({"lunedi": m, "w": w, "lordo": w * tenuta, "spese": spese, "funding": w * fund,
                      "netto": w * (tenuta - fund) - spese, "netto_doppio": w * (tenuta - fund) - 2 * spese,
                      "giro": abs(w - w_prima), "long": w * (tenuta - fund), "short": 0.0, "monete": 1,
                      "tenuta_sempre": tenuta - fund})
        w_prima = w
    return pd.DataFrame(righe).set_index("lunedi")


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    sr = qc.prove_fino_alla_quarantaquattresima()
    e45 = json.loads((QUI / "risultati_quarantacinquesima" / "esame.json").read_text())
    sr += [e45["I1"]["intero"]["sharpe"], e45["I2"]["portafoglio"]["intero"]["sharpe"]]
    e46 = json.loads((QUI / "risultati_quarantaseiesima" / "esame.json").read_text())
    sr += [e["intero"]["sharpe"] for e in e46.values()]
    RIS.mkdir(exist_ok=True)
    esami = {}
    for nome, moneta, simbolo in (("O1", "BTC", "BTCUSDT"), ("O2", "ETH", "ETHUSDT")):
        dvol = pd.Series({int(k): v for k, v in json.loads((sd.DATI / f"{moneta}.json").read_text()).items()})
        df = settimane(pan, pan["simboli"].index(simbolo), premio(pan, pan["simboli"].index(simbolo), dvol))
        df.to_csv(RIS / f"settimane_{nome}.csv.gz")
        inizio = int(df.index.min())
        e = te.esame(df, btc, inizio=inizio)
        tenuto = df.assign(netto=df["tenuta_sempre"], netto_doppio=df["tenuta_sempre"])
        e["tenuta_sempre"] = te.numeri_settimana(tenuto["netto"])
        e["quota_in_posizione"] = float(df["w"].mean())
        e["da"] = sc.data(inizio)
        sr.append(e["intero"]["sharpe"])
        esami[nome] = e
    for e in esami.values():
        i = e["intero"]
        e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
        e["prove_nel_conto"] = len(sr)
        e["esito"] = te.esito(e, e["sharpe_corretto"])
    (RIS / "esame.json").write_text(json.dumps(esami, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    righe = ["# Programma 6 — risultati della quarantasettesima prova (la paura nelle opzioni)", "",
             "Regole in `QUARANTASETTESIMA.md` (scritte prima).", ""]
    for nome, e in esami.items():
        i, t = e["intero"], e["tenuta_sempre"]
        righe += [f"## {nome} ({'Bitcoin' if nome == 'O1' else 'Ether'}), dal {e['da']}", "",
                  f"* In posizione {100 * e['quota_in_posizione']:.0f}% delle settimane. Sharpe {i['sharpe']:.2f}, "
                  f"{100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa {100 * i['discesa_max']:.1f}%; più "
                  f"del Bitcoin {100 * e['extra_btc_annuo']:+.1f}% l'anno.",
                  f"* La moneta tenuta sempre: Sharpe {t['sharpe']:.2f}, {100 * t['annuo']:+.1f}% l'anno, discesa {100 * t['discesa_max']:.1f}%.",
                  "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
                  f"* Sharpe corretto {e['sharpe_corretto']:.2f} con {len(sr)} prove.", "", f"**Esito {nome}: {e['esito']}**", ""]
    testo = "\n".join(righe)
    (QUI / "RISULTATI_QUARANTASETTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return esami


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTASETTESIMA FINITA", flush=True)
