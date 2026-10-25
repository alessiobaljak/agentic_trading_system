"""Programma 7, ventinovesima prova (VENTINOVESIMA.md): N3B2, la seconda tranche delle monete nuove di Binance: short contro il
Bitcoin dall'apertura del 37° giorno di vita, uscita a +30% o dopo 30 giorni (le stesse monete e le stesse regole della prova 32).

Uso: python3 -m research.programma7.ventinovesima
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import quarantunesima as qu
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import trentaduesima as td
from research.programma6 import trentesima as tr

QUI = Path(__file__).parent
RIS = QUI / "risultati_ventinovesima"
EVENTI = QUI.parent / "programma6" / "risultati_trentaduesima" / "eventi_N3B.csv"
ETA2 = tr.ETA + tr.GIORNI                       # il 37° giorno: il giorno dopo la fine della prima tranche
PROVE_A_EVENTI = 25


def esegui(log=print) -> dict:
    pan = sc.pannello()
    n3 = pd.read_csv(EVENTI)
    n3["g0"] = n3["data"].map(lambda d: sc.giorno(*map(int, d.split("-")))) - tr.ETA
    coppie = [(s, int(g0) + ETA2) for s, g0 in zip(n3["simbolo"], n3["g0"])]
    log(f"[ventinovesima] {len(coppie)} monete nuove; scarico le candele a 1 ora dal 37° giorno")
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: td.scarica_ore(x[0], x[1]), coppie))
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    jb = pan["simboli"].index("BTCUSDT")
    fb = pd.Series(pan["funding"][:, jb], index=giorni)
    cb = td.ore("BTCUSDT")
    V = pan["quote_volume"]
    righe, scartati = [], {"senza_volume": 0, "senza_candele": 0}
    for (s, e), r1 in zip(coppie, n3["r"]):
        j = pan["simboli"].index(s)
        k = e - 1 - pan["t0"]
        if k < 0 or k >= V.shape[0] or not np.nan_to_num(V[k, j]) > 0:
            scartati["senza_volume"] += 1
            continue
        c = td.ore(s)
        if c.empty or e * 24 not in c.index:
            scartati["senza_candele"] += 1
            continue
        f = pd.Series(pan["funding"][:, j], index=giorni)
        con, senza = tr.operazione(c, cb, f, fb, e, True), tr.operazione(c, cb, f, fb, e, False)
        if con and senza:
            righe.append({"data": sc.data(e), "annuncio": int((e + 3) // 7), "simbolo": s, "r": con["r"], "fermata": con["fermata"],
                          "giorni": con["giorni"], "r_senza": senza["r"], "r_prima_tranche": float(r1)})
    df = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_N3B2.csv", index=False)
    e2, es = tr.esame(df, "r"), tr.esame(df, "r_senza")
    soglia = 0.01 / PROVE_A_EVENTI
    ev = pd.DataFrame({"simbolo": df["simbolo"], "ora": df["data"].map(lambda d: sc.giorno(*map(int, d.split("-"))) * 24),
                       "r": df["r"]})
    ev["uscita_h"] = ev["ora"] + np.round(df["giorni"].to_numpy() * 24).astype(int)
    port = qu.portafoglio(ev)
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    p = te.esame(port, btc, inizio=qu.PRIMO_LUNEDI, anni_pieni=(2021, 2022, 2023, 2024, 2025))
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "91 N3B2": port["netto"]}, {"91 N3B2": p["intero"]})
    rr = rivisto["candidate"]["91 N3B2"]
    p["sharpe_corretto"], p["t"], p["gruppi"] = rr["corretto_con_aggiunta"], rr["t"], rivisto["gruppi"]
    p["esito"] = te.esito(p, p["sharpe_corretto"])
    out = {"monete": len(coppie), "operazioni": len(df), "scartati": scartati, "con_uscita": e2, "senza_uscita": es,
           "fermate": float(df["fermata"].mean()), "prima_tranche_stesse_monete": float(df["r_prima_tranche"].mean()),
           "correlazione_con_prima_tranche": float(df["r"].corr(df["r_prima_tranche"])), "portafoglio": p, "soglia_tutte": soglia}
    out["esito"] = ("VALIDA" if e2["esito"] == "VALIDA" and e2["boot"]["p"] <= soglia else
                    "passa l'esame scritto (p ≤ 0,01) ma non la soglia di tutte le prove a eventi" if e2["esito"] == "VALIDA" else e2["esito"])
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    b, i = e2["boot"], p["intero"]
    pc = lambda x: f"{100 * x:+.2f}%"  # noqa: E731
    righe_t = ["# Programma 7 — risultati della ventinovesima prova (N3B2: la seconda tranche delle monete nuove, dal 37° giorno)", "",
               "Regole in `VENTINOVESIMA.md` (scritte prima).", "",
               f"* {len(coppie)} monete nuove; operazioni {len(df)} (scartate: senza volume {scartati['senza_volume']}, senza candele "
               f"{scartati['senza_candele']}).",
               f"* **{b['eventi']} operazioni in {b['annunci']} settimane: {pc(b['media'])} a operazione** (intervallo {pc(b['basso'])}; "
               f"{pc(b['alto'])}, p {b['p']:.4f}); mediana {pc(e2['mediana'])}, vinte {100 * e2['vinti']:.0f}%; metà {pc(e2['prima_meta'])} e "
               f"{pc(e2['seconda_meta'])}; senza le 5 migliori {pc(e2['senza_5_migliori'])}; uscita a +30% nel {100 * out['fermate']:.0f}%.",
               f"* Senza l'uscita: {pc(es['boot']['media'])} (p {es['boot']['p']:.4f}). La prima tranche (N3) sulle stesse monete: "
               f"{pc(out['prima_tranche_stesse_monete'])}; correlazione fra le due tranche {out['correlazione_con_prima_tranche']:.2f}.",
               "* Per anno: " + ", ".join(f"{a} {pc(v['media'])} ({v['eventi']})" for a, v in e2["per_anno"].items()) + ".",
               f"* Portafoglio (5% a operazione, al massimo 20): Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, discesa "
               f"{100 * i['discesa_max']:.1f}%; Sharpe corretto {p['sharpe_corretto']:.2f} ({p['gruppi']} gruppi), t {p['t']:.2f}.", "",
               f"**Esito: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {soglia:.5f}). **Portafoglio: {p['esito']}**."]
    testo = "\n".join(righe_t) + "\n"
    (QUI / "RISULTATI_VENTINOVESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTINOVESIMA FINITA", flush=True)
