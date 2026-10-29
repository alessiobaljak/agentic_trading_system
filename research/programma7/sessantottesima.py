"""Programma 7, sessantottesima prova (SESSANTOTTESIMA.md): TE, le emissioni nuove di Tether su Tron e il Bitcoin: long il perpetuo del
Bitcoin dall'ora dopo un'emissione di almeno 500 milioni, per 24 ore; controllo in ore lontane dalle emissioni.

Uso: python3 -m research.programma7.sessantottesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma6 import trentesima as tr
from research.programma6 import ventunesima as vu
from research.programma7 import quarantunesima as lv

QUI = Path(__file__).parent
RIS = QUI / "risultati_sessantottesima"
DATI = QUI.parent / "data" / "tether" / "tron_issue.json"
DAL, AL = sc.giorno(2021, 1, 1), sc.giorno(2026, 10, 1)
SOGLIA, PICCOLA, ORA_MS, ORE, PAUSA, LONTANO = 5e8, 1e8, 3_600_000, 24, 24, 48
CONTROLLI, SEME = 20, 2026
PROVE_A_EVENTI = 39


def eventi_tether() -> list:
    """Le ore (dall'epoca) in cui la somma delle emissioni entro un'ora dalla prima arriva a 500 milioni; al massimo una ogni 24 ore."""
    em = sorted(json.loads(DATI.read_text()), key=lambda x: x["ms"])
    out, i = [], 0
    while i < len(em):
        t0, somma, quando = em[i]["ms"], 0.0, None
        j = i
        while j < len(em) and em[j]["ms"] - t0 <= ORA_MS:
            somma += em[j]["importo"]
            if quando is None and somma >= SOGLIA:
                quando = em[j]["ms"]
            j += 1
        if quando is not None:
            h = int(quando // ORA_MS)
            if DAL <= h // 24 < AL - 4 and (not out or h - out[-1][0] >= PAUSA):
                out.append((h, somma))
        i = j
    return out


def lungo(c: pd.DataFrame, f: pd.Series, h0: int, ore: int) -> float:
    h1 = h0 + ore
    if not all(h in c.index and np.isfinite(c.loc[h, "open"]) for h in (h0, h1)):
        return np.nan
    reg = [h for h in range(h0 + 1, h1 + 1) if h % 8 == 0]
    return float(c.loc[h1, "open"] / c.loc[h0, "open"] - 1 - vu.COSTO_BTC - sum(f.get(h // 24, 0.0) for h in reg) / 3)


def esegui(log=print) -> dict:
    pan = sc.pannello()
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    S = list(pan["simboli"])
    fb = pd.Series(np.nan_to_num(pan["funding"][:, S.index("BTCUSDT")]), index=giorni)
    fe = pd.Series(np.nan_to_num(pan["funding"][:, S.index("ETHUSDT")]), index=giorni)
    lv.scarica_ore("BTCUSDT", DAL * 24, AL * 24)
    lv.scarica_ore("ETHUSDT", DAL * 24, AL * 24)
    cb, ce = es.ore_di("BTCUSDT"), es.ore_di("ETHUSDT")
    ev_t = eventi_tether()
    tutte = np.array(sorted(int(x["ms"] // ORA_MS) for x in json.loads(DATI.read_text()) if x["importo"] >= PICCOLA))
    righe = []
    for h, somma in ev_t:
        r = lungo(cb, fb, h + 1, ORE)
        if np.isfinite(r):
            g = h // 24
            righe.append({"data": sc.data(g), "annuncio": int((g + 3) // 7), "ora": h, "importo": somma, "r": r,
                          **{f"r{o}": lungo(cb, fb, h + 1, o) for o in (1, 4, 72)}, "ether": lungo(ce, fe, h + 1, ORE)})
    ev = pd.DataFrame(righe)
    rng = np.random.default_rng(SEME)
    cr = []
    for h, _ in ev_t:
        cand = np.r_[np.arange(h - 60 * 24, h - 7 * 24 + 1), np.arange(h + 7 * 24, h + 60 * 24 + 1)]
        cand = cand[(cand // 24 >= DAL) & (cand // 24 < AL - 4)]
        pos = np.searchsorted(tutte, cand)
        vicino = np.minimum(np.abs(cand - tutte[np.clip(pos - 1, 0, len(tutte) - 1)]), np.abs(cand - tutte[np.clip(pos, 0, len(tutte) - 1)]))
        cand = cand[vicino >= LONTANO]
        for x in rng.choice(cand, size=min(CONTROLLI, len(cand)), replace=False):
            r = lungo(cb, fb, int(x) + 1, ORE)
            if np.isfinite(r):
                cr.append({"data": sc.data(int(x) // 24), "r": r})
    co = pd.DataFrame(cr)
    RIS.mkdir(exist_ok=True)
    ev.to_csv(RIS / "eventi_TE.csv", index=False)
    co.to_csv(RIS / "controllo_TE.csv", index=False)
    e = tr.esame(ev, "r")
    b = np.random.default_rng(SEME).choice(ev["r"].to_numpy(), size=(10000, len(ev)), replace=True).mean(axis=1) - co["r"].mean()
    diff = {"media": float(ev["r"].mean() - co["r"].mean()), "basso": float(np.quantile(b, 0.025)), "alto": float(np.quantile(b, 0.975)),
            "p": float((b <= 0).mean())}
    grandi = ev["importo"] >= 1e9
    out = {"eventi_trovati": len(ev_t), "eventi": int(len(ev)), "esame": e, "controllo": {"ore": int(len(co)), "media": float(co["r"].mean())},
           "differenza_con_controllo": diff, "tenute": {o: float(ev[f"r{o}"].mean()) for o in (1, 4, 72)},
           "miliardo": {"eventi": int(grandi.sum()), "media": float(ev.loc[grandi, "r"].mean())}, "ether": float(ev["ether"].mean()),
           "soglia_tutte": 0.01 / PROVE_A_EVENTI}
    valida = e["esito"] == "VALIDA" and diff["p"] <= 0.05
    out["esito"] = ("VALIDA" if valida and e["boot"]["p"] <= out["soglia_tutte"] else
                    "passa l'esame scritto ma non la soglia di tutte le prove a eventi" if valida else
                    e["esito"] if e["esito"] != "VALIDA" else "non sopra il controllo")
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None or v != v else f"{100 * v:+.2f}%"  # noqa: E731
    bb = e["boot"]
    testo = "\n".join([
        "# Programma 7 — risultati della sessantottesima prova (TE: le emissioni nuove di Tether e il Bitcoin)", "",
        "Regole in `SESSANTOTTESIMA.md` (scritte prima). Long il perpetuo del Bitcoin per 24 ore dall'ora dopo un'emissione di Tether su "
        "Tron di almeno 500 milioni, dal 2021 al settembre 2026, costi a mercato e funding.", "",
        f"* **{bb['eventi']} emissioni** (trovate {len(ev_t)}): **{pc(bb['media'])} a operazione** (intervallo {pc(bb['basso'])}; "
        f"{pc(bb['alto'])}, p {bb['p']:.4f}); mediana {pc(e['mediana'])}, vinte {100 * e['vinti']:.0f}%; metà {pc(e['prima_meta'])} e "
        f"{pc(e['seconda_meta'])}; senza le 5 migliori {pc(e['senza_5_migliori'])}.",
        "* Per anno: " + ", ".join(f"{a} {pc(v['media'])} ({v['eventi']})" for a, v in e["per_anno"].items()) + ".",
        f"* **Controllo** ({out['controllo']['ore']} ore lontane dalle emissioni): {pc(out['controllo']['media'])}; differenza "
        f"{pc(diff['media'])} (intervallo {pc(diff['basso'])}; {pc(diff['alto'])}, p {diff['p']:.3f}).",
        "* Per capire: tenute di " + ", ".join(f"{o} ore {pc(v)}" for o, v in out["tenute"].items()) + f"; emissioni da almeno un "
        f"miliardo {pc(out['miliardo']['media'])} ({out['miliardo']['eventi']}); l'Ether nelle stesse 24 ore {pc(out['ether'])}.", "",
        f"**Esito: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {out['soglia_tutte']:.5f})."]) + "\n"
    (QUI / "RISULTATI_SESSANTOTTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SESSANTOTTESIMA FINITA", flush=True)
