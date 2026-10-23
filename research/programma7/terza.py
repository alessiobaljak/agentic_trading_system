"""Programma 7, terza prova (TERZA.md): G4, lo short delle monete nuove di Binance dal 1o giorno di vita contro il Bitcoin,
con le regole di N3 (prova 32) tranne il giorno d'ingresso.

Uso: python3 -m research.programma7.terza
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import trentaduesima as td
from research.programma6 import trentesima as tr

QUI = Path(__file__).parent
RIS = QUI / "risultati_terza"
ETA = 1


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ok = np.isfinite(pan["close"])
    primo = ok.argmax(axis=0) + pan["t0"]
    V = np.nan_to_num(pan["quote_volume"])
    cand = [(s, int(primo[j])) for j, s in enumerate(pan["simboli"])
            if s != "BTCUSDT" and ok[:, j].any() and td.DA <= primo[j] <= td.A]
    log(f"[terza] {len(cand)} monete nuove")
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: td.scarica_ore(x[0], x[1] + ETA), cand))
    jb = pan["simboli"].index("BTCUSDT")
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    fb = pd.Series(pan["funding"][:, jb], index=giorni)
    cb = td.ore("BTCUSDT")
    n3 = pd.read_csv(QUI.parent / "programma6" / "risultati_trentaduesima" / "eventi_N3B.csv").set_index("simbolo")["r"]
    righe, senza_ore = [], 0
    for s, g0 in cand:
        j = pan["simboli"].index(s)
        e = g0 + ETA
        if V[e - 1 - pan["t0"], j] <= 0:
            continue
        c = td.ore(s)
        if c.empty or e * 24 not in c.index:
            senza_ore += 1
            continue
        f = pd.Series(pan["funding"][:, j], index=giorni)
        con, senza = tr.operazione(c, cb, f, fb, e, True), tr.operazione(c, cb, f, fb, e, False)
        if con and senza:
            righe.append({"data": sc.data(e), "annuncio": int((e + 3) // 7), "simbolo": s, "r": con["r"], "fermata": con["fermata"],
                          "giorni": con["giorni"], "r_senza": senza["r"], "r_N3": float(n3.get(s, np.nan))})
    df = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_G4.csv", index=False)
    stesse = df[np.isfinite(df["r_N3"])]
    out = {"con_uscita": tr.esame(df, "r"), "senza_uscita": tr.esame(df, "r_senza"), "fermate": float(df["fermata"].mean()),
           "monete": len(cand), "senza_candele_a_1_ora": senza_ore,
           "confronto_N3": {"eventi": int(len(stesse)), "G4": float(stesse["r"].mean()), "N3": float(stesse["r_N3"].mean()),
                            "correlazione": float(np.corrcoef(stesse["r"], stesse["r_N3"])[0, 1]) if len(stesse) > 2 else None}}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    righe_t = ["# Programma 7 — risultati della terza prova (G4: le monete nuove dal primo giorno)", "",
               "Regole in `TERZA.md` (scritte prima). Short dal 1° giorno di vita contro il Bitcoin, uscita a +30% (candele a 1 ora, "
               "1% di scarto) o dopo 30 giorni.", "",
               f"Monete nuove dal 2021: {len(cand)}; senza le candele a 1 ora all'ingresso: {senza_ore}.", "",
               "| Versione | Eventi (settimane) | Media a evento | Intervallo | p | Mediana | Vinti | Prima metà, seconda metà | "
               "Senza i 5 migliori | Esito |", "|---|---|---|---|---|---|---|---|---|---|"]
    for nome, x in (("con l'uscita a +30% (la regola)", out["con_uscita"]), ("senza l'uscita (per capire)", out["senza_uscita"])):
        b = x["boot"]
        righe_t.append(f"| {nome} | {b['eventi']} ({b['annunci']}) | {100 * b['media']:+.2f}% | {100 * b['basso']:+.2f}%; "
                       f"{100 * b['alto']:+.2f}% | {b['p']:.4f} | {100 * x['mediana']:+.2f}% | {100 * x['vinti']:.0f}% | "
                       f"{100 * x['prima_meta']:+.2f}%, {100 * x['seconda_meta']:+.2f}% | {100 * x['senza_5_migliori']:+.2f}% | "
                       f"{x['esito'] if 'regola' in nome else '—'} |")
    cn = out["confronto_N3"]
    righe_t += ["", f"L'uscita di protezione scatta nel {100 * out['fermate']:.0f}% degli eventi.", "",
                "**Per anno (con l'uscita)**: " + ", ".join(f"{a} {100 * v['media']:+.2f}% ({v['eventi']})"
                                                         for a, v in out["con_uscita"]["per_anno"].items()), "",
                f"**Sulle stesse monete di N3** ({cn['eventi']}): dal 1° giorno {100 * cn['G4']:+.2f}% a evento, dal 7° giorno (N3) "
                f"{100 * cn['N3']:+.2f}%; correlazione {cn['correlazione']:.2f}."]
    testo = "\n".join(righe_t) + "\n"
    (QUI / "RISULTATI_TERZA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TERZA FINITA", flush=True)
