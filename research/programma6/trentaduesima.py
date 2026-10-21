"""Programma 6, trentaduesima prova (TRENTADUESIMA.md): la regola N3 (`trentesima.operazione`) sulle monete nuove dei
perpetui di Binance dal 2021: short a 7 giorni dalla prima candela contro il Bitcoin, uscita a +30% (candele a 1 ora) o dopo
30 giorni.

Uso: python3 -m research.programma6.trentaduesima
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import esecuzione as es
from research.programma6 import quarta as qa
from research.programma6 import scarico_giorni as sg
from research.programma6 import seconda as sc
from research.programma6 import trentesima as tr

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentaduesima"
DA, A = sc.giorno(2021, 1, 1), sc.giorno(2026, 9, 10)


def _mesi(e: int) -> list:
    return sorted({sc.data(g)[:7] for g in range(e, e + tr.GIORNI + 2)})


def scarica_ore(simbolo: str, e: int) -> None:
    """Le candele mensili a 1 ora dei mesi della tenuta, se mancano (nella cartella di `quarta.ore`)."""
    for m in _mesi(e):
        chiave = f"data/futures/um/monthly/klines/{simbolo}/1h/{simbolo}-1h-{m}.zip"
        try:
            sg._scarica(chiave, qa.DATI / simbolo / "ore")
        except Exception:
            pass


def ore(simbolo: str) -> pd.DataFrame:
    d = es.ore_di(simbolo)
    return d[["open", "high", "close"]] if not d.empty else d


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ok = np.isfinite(pan["close"])
    primo = ok.argmax(axis=0) + pan["t0"]
    V = np.nan_to_num(pan["quote_volume"])
    cand = [(s, int(primo[j])) for j, s in enumerate(pan["simboli"])
            if s != "BTCUSDT" and ok[:, j].any() and DA <= primo[j] <= A]
    log(f"[trentaduesima] {len(cand)} monete nuove")
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: scarica_ore(x[0], x[1] + tr.ETA), cand))
    jb = pan["simboli"].index("BTCUSDT")
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    fb = pd.Series(pan["funding"][:, jb], index=giorni)
    cb = ore("BTCUSDT")
    righe, senza_ore = [], 0
    for s, g0 in cand:
        j = pan["simboli"].index(s)
        e = g0 + tr.ETA
        if V[e - 1 - pan["t0"], j] <= 0:
            continue
        c = ore(s)
        if c.empty or e * 24 not in c.index:
            senza_ore += 1
            continue
        f = pd.Series(pan["funding"][:, j], index=giorni)
        con, senza = tr.operazione(c, cb, f, fb, e, True), tr.operazione(c, cb, f, fb, e, False)
        if con and senza:
            righe.append({"data": sc.data(e), "annuncio": int((e + 3) // 7), "simbolo": s, "r": con["r"], "fermata": con["fermata"],
                          "giorni": con["giorni"], "r_senza": senza["r"]})
    df = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_N3B.csv", index=False)
    out = {"con_uscita": tr.esame(df, "r"), "senza_uscita": tr.esame(df, "r_senza"), "fermate": float(df["fermata"].mean()),
           "monete": len(cand), "senza_candele_a_1_ora": senza_ore}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    righe_t = ["# Programma 6 — risultati della trentaduesima prova (la regola N3 sul passato di Binance)", "",
               "Regole in `TRENTADUESIMA.md` (scritte prima, con la riserva: l'idea dell'uscita era nata su questi dati). Short "
               "all'età di 7 giorni contro il Bitcoin, uscita a +30% (candele a 1 ora, 1% di scarto) o dopo 30 giorni.", "",
               f"Monete nuove dal 2021: {len(cand)}; senza le candele a 1 ora all'ingresso: {senza_ore}.", "",
               "| Versione | Eventi (settimane) | Media a evento | Intervallo | p | Mediana | Vinti | Prima metà, seconda metà | "
               "Senza i 5 migliori | Esito |", "|---|---|---|---|---|---|---|---|---|---|"]
    for nome, x in (("con l'uscita a +30% (la regola)", out["con_uscita"]), ("senza l'uscita (per capire)", out["senza_uscita"])):
        b = x["boot"]
        righe_t.append(f"| {nome} | {b['eventi']} ({b['annunci']}) | {100 * b['media']:+.2f}% | {100 * b['basso']:+.2f}%; "
                       f"{100 * b['alto']:+.2f}% | {b['p']:.4f} | {100 * x['mediana']:+.2f}% | {100 * x['vinti']:.0f}% | "
                       f"{100 * x['prima_meta']:+.2f}%, {100 * x['seconda_meta']:+.2f}% | {100 * x['senza_5_migliori']:+.2f}% | "
                       f"{x['esito'] if 'regola' in nome else '—'} |")
    righe_t += ["", f"L'uscita di protezione scatta nel {100 * out['fermate']:.0f}% degli eventi.", "",
                "**Per anno (con l'uscita)**: " + ", ".join(f"{a} {100 * v['media']:+.2f}% ({v['eventi']})"
                                                         for a, v in out["con_uscita"]["per_anno"].items())]
    testo = "\n".join(righe_t) + "\n"
    (QUI / "RISULTATI_TRENTADUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTADUESIMA FINITA", flush=True)
