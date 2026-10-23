"""Programma 7, quattordicesima prova (QUATTORDICESIMA.md): G12, E4 con l'entrata all'ora dopo l'evento invece che
all'apertura del giorno dopo.

Uso: python3 -m research.programma7.quattordicesima
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma6 import trentaduesima as td
from research.programma6 import ventiseiesima as vs
from research.programma6 import ventunesima as vu

QUI = Path(__file__).parent
RIS = QUI / "risultati_quattordicesima"
ORE = 7 * 24


def operazione(c: pd.DataFrame, cb: pd.DataFrame, f: pd.Series, fb: pd.Series, h_e: int) -> float | None:
    """Short la moneta e long il Bitcoin dall'apertura dell'ora ``h_e`` all'apertura di 168 ore dopo."""
    h1 = h_e + ORE
    if not all(h in x.index for h in (h_e, h1) for x in (c, cb)):
        return None
    rc = c.loc[h1, "open"] / c.loc[h_e, "open"] - 1
    rb = cb.loc[h1, "open"] / cb.loc[h_e, "open"] - 1
    g0, g1 = h_e // 24, h1 // 24
    fc = f[(f.index >= g0) & (f.index < g1)].sum()
    fbb = fb[(fb.index >= g0) & (fb.index < g1)].sum()
    return float(rb - rc - vu.COSTO_MONETA - vu.COSTO_BTC + fc - fbb)


def esegui(log=print) -> dict:
    pan = sc.pannello()
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    ev = [(s, ms) for s, ms, segno in vs.eventi(pan) if segno > 0 and s != "BTCUSDT"]
    e4 = pd.read_csv(QUI.parent / "programma6" / "risultati_ventiseiesima" / "eventi_E4.csv")
    chiave = {(r["simbolo"], r["data"]): r for _, r in e4.iterrows()}
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: td.scarica_ore(x[0], x[1] // 86_400_000), ev))
    jb = pan["simboli"].index("BTCUSDT")
    fb = pd.Series(pan["funding"][:, jb], index=giorni)
    cb = es.ore_di("BTCUSDT")
    righe = []
    for s, ms in ev:
        data = sc.data(ms // 86_400_000)
        if (s, data) not in chiave:          # gli stessi eventi di E4 (volume il giorno dell'evento, prezzi)
            continue
        c = es.ore_di(s)
        if c.empty:
            continue
        h_e = ms // 3_600_000 + 1
        f = pd.Series(pan["funding"][:, pan["simboli"].index(s)], index=giorni)
        r = operazione(c, cb, f, fb, h_e)
        if r is not None:
            righe.append({"data": data, "annuncio": int(chiave[(s, data)]["annuncio"]), "simbolo": s, "ora_evento": int(ms // 3_600_000 % 24),
                          "r7": r, "r7_E4": float(chiave[(s, data)]["r7"])})
    df = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_G12.csv", index=False)
    e = vu.esame(df.assign(reazione=0.0, r1=np.nan, r3=np.nan, r14=np.nan, r28=np.nan))
    d = df["r7"] - df["r7_E4"]
    rng = np.random.default_rng(12)
    boot = np.array([d.sample(len(d), replace=True, random_state=int(rng.integers(1 << 31))).mean() for _ in range(5000)])
    out = {"esame": e, "eventi_E4": int(len(e4)), "E4_stessi_eventi": float(df["r7_E4"].mean()), "differenza": float(d.mean()),
           "differenza_intervallo": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
           "ora_media_evento": float(df["ora_evento"].mean())}
    out["il_bot_cambia"] = bool(e["esito"] == "VALIDA" and out["differenza"] >= 0.01)
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    b = e["boot"]
    testo = "\n".join([
        "# Programma 7 — risultati della quattordicesima prova (G12: il funding al tetto con l'entrata subito)", "",
        "Regole in `QUATTORDICESIMA.md` (scritte prima).", "",
        f"* Eventi: {b['eventi']} (E4: {out['eventi_E4']}); l'evento cade in media alle {out['ora_media_evento']:.1f} UTC.",
        f"* G12: **{100 * b['media']:+.2f}% a evento** (intervallo {100 * b['basso']:+.2f}%; {100 * b['alto']:+.2f}%), p {b['p']:.4f}, "
        f"vinti {100 * e['vinti']:.0f}%, metà {100 * e['prima_meta']:+.2f}% e {100 * e['seconda_meta']:+.2f}%, senza i 5 migliori "
        f"{100 * e['senza_5_migliori']:+.2f}%.",
        f"* E4 sugli stessi eventi: {100 * out['E4_stessi_eventi']:+.2f}%; differenza G12 − E4 {100 * out['differenza']:+.2f} punti "
        f"(intervallo {100 * out['differenza_intervallo'][0]:+.2f}; {100 * out['differenza_intervallo'][1]:+.2f}).",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.2f}%" for a, v in e["per_anno"].items()) + ".", "",
        f"**Esito: {e['esito']}. Per il bot: {'E4 entra all’ora dopo l’evento' if out['il_bot_cambia'] else 'E4 resta all’apertura del giorno dopo'}** "
        "(regola scritta prima: passa l'esame e almeno +1 punto su E4)."]) + "\n"
    (QUI / "RISULTATI_QUATTORDICESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUATTORDICESIMA FINITA", flush=True)
