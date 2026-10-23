"""Programma 7, sesta prova (SESTA.md): G5, lo short (contro il Bitcoin) il giorno dopo una salita di almeno +30% in un giorno,
con le uscite e i costi di N3.

Uso: python3 -m research.programma7.sesta
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import trentaduesima as td
from research.programma6 import trentesima as tr

QUI = Path(__file__).parent
RIS = QUI / "risultati_sesta"
SALITA, ETA_MIN, VOLUME_MIN, DISTANZA = 0.30, 30, 2e6, 30
DA, A = sc.giorno(2021, 1, 4), sc.giorno(2026, 9, 10)


def eventi(r: np.ndarray, vivo_da: np.ndarray, vol_med: np.ndarray, giorni: np.ndarray, salita: float = SALITA) -> list:
    """[(colonna, giorno d'ingresso)]: il giorno dopo una salita di almeno ``salita``, per monete con almeno ETA_MIN giorni di
    vita e volume sufficiente, al massimo una volta ogni DISTANZA giorni per moneta."""
    out = []
    for j in range(r.shape[1]):
        ultimo = -10 ** 9
        for t in np.flatnonzero(r[:, j] >= salita):
            g = int(giorni[t])
            if not (DA <= g + 1 <= A) or g - vivo_da[j] < ETA_MIN or not vol_med[t, j] >= VOLUME_MIN or g + 1 - ultimo < DISTANZA:
                continue
            out.append((j, g + 1))
            ultimo = g + 1
    return out


def esegui(log=print) -> dict:
    pan = sc.pannello()
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    ok = np.isfinite(pan["close"])
    vivo_da = ok.argmax(axis=0) + pan["t0"]
    r = sc.rendimenti(pan)
    V = pd.DataFrame(np.nan_to_num(pan["quote_volume"]))
    vol_med = V.rolling(30, min_periods=20).median().shift(1).to_numpy()
    escludi = {pan["simboli"].index(s) for s in ("BTCUSDT",) if s in pan["simboli"]}
    ev = [(j, e) for j, e in eventi(r, vivo_da, vol_med, giorni) if j not in escludi]
    log(f"[sesta] {len(ev)} eventi")
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: td.scarica_ore(pan["simboli"][x[0]], x[1]), ev))
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    jb = pan["simboli"].index("BTCUSDT")
    fb = pd.Series(pan["funding"][:, jb], index=giorni)
    cb = td.ore("BTCUSDT")
    righe, senza_ore = [], 0
    for j, e in ev:
        s = pan["simboli"][j]
        c = td.ore(s)
        if c.empty or e * 24 not in c.index:
            senza_ore += 1
            continue
        f = pd.Series(pan["funding"][:, j], index=giorni)
        con, senza = tr.operazione(c, cb, f, fb, e, True), tr.operazione(c, cb, f, fb, e, False)
        k = np.searchsorted(ps["lunedi"], e - ((e + 3) % 7))
        fra_le_100 = bool(k < len(ps["lunedi"]) and ps["lunedi"][k] == e - ((e + 3) % 7) and ps["U"][k, j])
        if con and senza:
            righe.append({"data": sc.data(e), "annuncio": int((e + 3) // 7), "simbolo": s, "salita": float(r[e - 1 - pan["t0"], j]),
                          "r": con["r"], "fermata": con["fermata"], "giorni": con["giorni"], "r_senza": senza["r"],
                          "fra_le_100": fra_le_100})
    df = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_G5.csv", index=False)
    out = {"con_uscita": tr.esame(df, "r"), "senza_uscita": tr.esame(df, "r_senza"), "fermate": float(df["fermata"].mean()),
           "eventi_trovati": len(ev), "senza_candele_a_1_ora": senza_ore,
           "fra_le_100": {"eventi": int(df["fra_le_100"].sum()), "media": float(df.loc[df["fra_le_100"], "r"].mean())},
           "fuori": {"eventi": int((~df["fra_le_100"]).sum()), "media": float(df.loc[~df["fra_le_100"], "r"].mean())}}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    righe_t = ["# Programma 7 — risultati della sesta prova (G5: short dopo le grandi salite di un giorno)", "",
               "Regole in `SESTA.md` (scritte prima). Short contro il Bitcoin all'apertura del giorno dopo una salita di almeno +30%, "
               "uscita a +30% (candele a 1 ora, 1% di scarto) o dopo 30 giorni (le uscite di N3).", "",
               f"Eventi trovati: {len(ev)}; senza le candele a 1 ora all'ingresso: {senza_ore}.", "",
               "| Versione | Eventi (settimane) | Media a evento | Intervallo | p | Mediana | Vinti | Prima metà, seconda metà | "
               "Senza i 5 migliori | Esito |", "|---|---|---|---|---|---|---|---|---|---|"]
    for nome, x in (("con l'uscita a +30% (la regola)", out["con_uscita"]), ("senza l'uscita (per capire)", out["senza_uscita"])):
        b = x["boot"]
        righe_t.append(f"| {nome} | {b['eventi']} ({b['annunci']}) | {100 * b['media']:+.2f}% | {100 * b['basso']:+.2f}%; "
                       f"{100 * b['alto']:+.2f}% | {b['p']:.4f} | {100 * x['mediana']:+.2f}% | {100 * x['vinti']:.0f}% | "
                       f"{100 * x['prima_meta']:+.2f}%, {100 * x['seconda_meta']:+.2f}% | {100 * x['senza_5_migliori']:+.2f}% | "
                       f"{x['esito'] if 'regola' in nome else '—'} |")
    righe_t += ["", f"L'uscita di protezione scatta nel {100 * out['fermate']:.0f}% degli eventi. Fra le 100 più scambiate: "
                f"{out['fra_le_100']['eventi']} eventi, {100 * out['fra_le_100']['media']:+.2f}%; fuori: {out['fuori']['eventi']}, "
                f"{100 * out['fuori']['media']:+.2f}%.", "",
                "**Per anno (con l'uscita)**: " + ", ".join(f"{a} {100 * v['media']:+.2f}% ({v['eventi']})"
                                                         for a, v in out["con_uscita"]["per_anno"].items())]
    testo = "\n".join(righe_t) + "\n"
    (QUI / "RISULTATI_SESTA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SESTA FINITA", flush=True)
