"""Programma 7, sessantunesima prova (SESSANTUNESIMA.md): RRB, l'inclinazione delle opzioni sul Bitcoin nel verso della letteratura,
con la misura larga della prova 122 (operazioni fra le 16 e le 24 UTC, scadenze 7-60 giorni, almeno 10 per parte). Long il Bitcoin il
giorno dopo se sopra la mediana dei 90 giorni prima, short se sotto.

Uso: python3 -m research.programma7.sessantunesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma7 import cinquantanovesima as rr
from research.programma7 import prima as g1
from research.programma7 import sessantesima as eth

QUI = Path(__file__).parent
RIS = QUI / "risultati_sessantunesima"
DATI = QUI.parents[1] / "research" / "data" / "deribit_rr_btc_larga"


def esegui(log=print) -> dict:
    # la stessa misura della prova 122, sulle opzioni del Bitcoin
    eth.URL = eth.URL.replace("currency=ETH", "currency=BTC")
    eth.DATI = DATI
    s = eth.serie()
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    j = pan["simboli"].index("BTCUSDT")
    costo = float(sc.costi_moneta(["BTCUSDT"])[0])
    giorni = np.arange(eth.DAL + rr.FINESTRA + 1, eth.AL + 1, dtype=np.int64)
    R = sc.rendimenti(pan)[giorni - pan["t0"], j]
    Fd = np.nan_to_num(pan["funding"][giorni - pan["t0"], j])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    out = {"giorni_mancanti": int(s.isna().sum()), "giorni": int(len(s))}
    seg = []
    for nome, solo_long in (("RRB", False), ("RRB solo long", True)):
        pos, prima, righe = 0.0, 0.0, []
        for g, r, f in zip(giorni, R, Fd):
            oggi = s.get(int(g) - 1, np.nan)
            storia = s.reindex(np.arange(g - 1 - rr.FINESTRA, g - 1)).dropna()
            if np.isfinite(oggi) and len(storia) >= rr.VALIDI:
                z = oggi - float(storia.median())
                pos = 1.0 if z > 0 else (0.0 if solo_long else -1.0)
                if not solo_long:
                    seg.append((int(g), z))
            giro = abs(pos - prima)
            lordo, spese, fund = pos * r, giro * costo, pos * f
            righe.append({"lordo": lordo, "spese": spese, "funding": fund, "netto": lordo - spese - fund,
                          "netto_doppio": lordo - 2 * spese - fund, "giro": giro, "long": max(pos, 0.0), "short": max(-pos, 0.0),
                          "monete": 1})
            prima = pos
        d = pd.DataFrame(righe)
        sett = g1.per_settimana(d, giorni)
        RIS.mkdir(exist_ok=True)
        sett.to_csv(RIS / f"settimane_{nome.replace(' ', '_')}.csv.gz")
        out[nome] = te.esame(sett, btc, inizio=int(sett.index.min()), anni_pieni=(2022, 2023, 2024, 2025))
        out[nome]["cambi_l_anno"] = float(d["giro"].gt(0).sum() / len(d) * 365)
        if nome == "RRB":
            sett_r = sett
    e = out["RRB"]
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "123 RRB": sett_r["netto"]}, {"123 RRB": e["intero"]})
    r = rivisto["candidate"]["123 RRB"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    sg = pd.DataFrame(seg, columns=["giorno", "z"]).set_index("giorno")
    rb = pd.Series(sc.rendimenti(pan)[:, j], index=np.arange(pan["t0"], pan["t0"] + pan["close"].shape[0]))
    e["correlazione_giorno_dopo"] = float(sg["z"].corr(pd.Series(rb.reindex(sg.index).to_numpy(), index=sg.index)))
    anni = e.get("per_anno", {})
    e["regola_proprietario"] = bool(e["sharpe_corretto"] >= 0.90 and e["t"] > 3 and anni and all(v > 0 for v in anni.values()))
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, lo = e["intero"], out["RRB solo long"]["intero"]
    testo = "\n".join([
        "# Programma 7 — risultati della sessantunesima prova (RRB: l'inclinazione sul Bitcoin, verso della letteratura, misura larga)", "",
        "Regole in `SESSANTUNESIMA.md` (scritte prima). Operazioni di Deribit sulle opzioni del Bitcoin fra le 16 e le 24 UTC, dal 1° aprile 2021.", "",
        f"* Giorni con l'inclinazione: {out['giorni'] - out['giorni_mancanti']} su {out['giorni']}; cambi di verso {e['cambi_l_anno']:.0f} l'anno.",
        f"* **RRB (long sopra la mediana dei 90 giorni, short sotto): Sharpe {i['sharpe']:.2f}**, {100 * i['annuo']:+.1f}% l'anno, volatilità "
        f"{100 * i['volatilita']:.1f}%, discesa {100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Solo long: Sharpe {lo['sharpe']:.2f}, {100 * lo['annuo']:+.1f}% l'anno.",
        f"* Correlazione fra il segnale e il Bitcoin del giorno dopo {e['correlazione_giorno_dopo']:.3f}.",
        f"* Sharpe corretto con l'aggiunta {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}; regola del proprietario: "
        f"{'sì' if e['regola_proprietario'] else 'no'}.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_SESSANTUNESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SESSANTUNESIMA FINITA", flush=True)
