"""Programma 7, quindicesima prova (QUINDICESIMA.md): G13, short (contro il Bitcoin) dei perpetui dall'annuncio di chiusura
dei future fino a un'ora prima della chiusura, con l'uscita di protezione a +30%.

Uso: python3 -m research.programma7.quindicesima
"""
from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import annunci as an
from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma6 import trentaduesima as td
from research.programma6 import trentesima as tr
from research.programma6 import ventunesima as vu

QUI = Path(__file__).parent
RIS = QUI / "risultati_quindicesima"
ENTRO = 21
TITOLO = re.compile(r"Binance Futures Will Delist (.+?)(?: \(20\d\d-\d\d-\d\d\))?$")


def sigle_del_titolo(titolo: str) -> list:
    """Le sigle dei contratti nel titolo di un annuncio di chiusura dei future ([] se «Multiple» o senza sigle)."""
    m = TITOLO.match(titolo.strip())
    if not m or "Multiple" in m.group(1):
        return []
    t = re.sub(r"USD[ⓈS]?-?(?:M|Margined)|USDT-Margined|Perpetual|Contracts?|Quarterly|Delivery", " ", m.group(1))
    out = []
    for p in re.split(r",\s*|\s*&\s*|\s+and\s+|\s+", t):
        p = p.strip()
        if re.fullmatch(r"[A-Z0-9]{2,20}", p):
            out.append(p[:-4] if p.endswith("USDT") else p)
    return [x for x in out if not x.endswith("USDC") and not x.endswith("BUSD")]


def operazione(c: pd.DataFrame, cb: pd.DataFrame, f: pd.Series, fb: pd.Series, h_e: int, h_u: int, protezione: bool) -> dict:
    """Short la moneta e long il Bitcoin dall'apertura dell'ora ``h_e`` all'apertura dell'ora ``h_u`` (o all'uscita a +30%)."""
    if not all(h in c.index for h in (h_e, h_u)) or h_e not in cb.index:
        return {}
    p0, b0 = c.loc[h_e, "open"], cb.loc[h_e, "open"]
    tratto = c[(c.index >= h_e) & (c.index < h_u)]
    uscita_h, pc, fermata = h_u, c.loc[h_u, "open"], False
    if protezione:
        su = tratto.index[tratto["high"].to_numpy() >= p0 * (1 + tr.STOP)]
        if len(su):
            uscita_h, pc, fermata = int(su[0]), p0 * (1 + tr.STOP) * (1 + tr.SCARTO_STOP), True
    bb = cb[cb.index <= uscita_h]
    if bb.empty:
        return {}
    pb = cb.loc[uscita_h, "open"] if uscita_h in cb.index else bb["close"].iloc[-1]
    g0, g1 = h_e // 24, uscita_h // 24
    fc = f[(f.index >= g0) & (f.index <= g1)].sum()
    fbb = fb[(fb.index >= g0) & (fb.index <= g1)].sum()
    r = (pb / b0 - 1) - (pc / p0 - 1) - vu.COSTO_MONETA - vu.COSTO_BTC + fc - fbb
    return {"r": float(r), "fermata": fermata, "ore": int(uscita_h - h_e)}


def esegui(log=print) -> dict:
    pan = sc.pannello()
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    annunci = [x for x in an._carica("notizie", "rimozioni", "quotazioni") if TITOLO.match(x["titolo"].strip())]
    multipli = sum(1 for x in annunci if not sigle_del_titolo(x["titolo"]))
    ev = []
    for x in annunci:
        for sg in sigle_del_titolo(x["titolo"]):
            p = an.perpetuo(sg, pan["simboli"])
            if p and p != "BTCUSDT":
                ev.append((p, int(x["ms"]), int(x["id"])))
    log(f"[quindicesima] {len(annunci)} annunci ({multipli} senza sigle nel titolo), {len(ev)} contratti")
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: td.scarica_ore(x[0], x[1] // 86_400_000), ev))
    jb = pan["simboli"].index("BTCUSDT")
    fb = pd.Series(pan["funding"][:, jb], index=giorni)
    cb = es.ore_di("BTCUSDT")
    righe, scartati = [], {"senza_candele": 0, "troppo_vicina": 0, "chiusura_non_trovata": 0}
    for s, ms, ident in ev:
        c = es.ore_di(s)
        h_e = ms // 3_600_000 + 1
        dopo = c.index[c.index >= h_e] if not c.empty else []
        if len(dopo) == 0:
            scartati["senza_candele"] += 1
            continue
        ultima = int(dopo.max())
        if ultima // 24 > ms // 86_400_000 + ENTRO:
            scartati["chiusura_non_trovata"] += 1
            continue
        h_u = ultima - 1
        if h_u - h_e < 3:
            scartati["troppo_vicina"] += 1
            continue
        f = pd.Series(pan["funding"][:, pan["simboli"].index(s)], index=giorni)
        con, senza = operazione(c, cb, f, fb, h_e, h_u, True), operazione(c, cb, f, fb, h_e, h_u, False)
        if con and senza:
            righe.append({"data": sc.data(ms // 86_400_000), "annuncio": int((ms // 86_400_000 + 3) // 7), "simbolo": s, "id": ident,
                          "r": con["r"], "fermata": con["fermata"], "ore": con["ore"], "r_senza": senza["r"],
                          "ore_alla_chiusura": int(h_u - h_e)})
    df = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_G13.csv", index=False)
    out = {"con_uscita": tr.esame(df, "r"), "senza_uscita": tr.esame(df, "r_senza"), "fermate": float(df["fermata"].mean()),
           "annunci": len(annunci), "annunci_senza_sigle": multipli, "contratti": len(ev), "scartati": scartati,
           "ore_medie_alla_chiusura": float(df["ore_alla_chiusura"].mean())}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    righe_t = ["# Programma 7 — risultati della quindicesima prova (G13: vendere i perpetui annunciati in chiusura)", "",
               "Regole in `QUINDICESIMA.md` (scritte prima).", "",
               f"Annunci di chiusura dei future: {len(annunci)} ({multipli} senza sigle nel titolo, non usati); contratti {len(ev)}; "
               f"senza candele {scartati['senza_candele']}, chiusura non trovata entro 21 giorni {scartati['chiusura_non_trovata']}, chiusura troppo vicina "
               f"{scartati['troppo_vicina']}; dall'entrata alla chiusura in "
               f"media {out['ore_medie_alla_chiusura'] / 24:.1f} giorni.", "",
               "| Versione | Eventi (settimane) | Media a evento | Intervallo | p | Mediana | Vinti | Prima metà, seconda metà | "
               "Senza i 5 migliori | Esito |", "|---|---|---|---|---|---|---|---|---|---|"]
    for nome, x in (("con l'uscita a +30% (la regola)", out["con_uscita"]), ("senza l'uscita (per capire)", out["senza_uscita"])):
        b = x["boot"]
        righe_t.append(f"| {nome} | {b['eventi']} ({b['annunci']}) | {100 * b['media']:+.2f}% | {100 * b['basso']:+.2f}%; "
                       f"{100 * b['alto']:+.2f}% | {b['p']:.4f} | {100 * x['mediana']:+.2f}% | {100 * x['vinti']:.0f}% | "
                       f"{100 * x['prima_meta']:+.2f}%, {100 * x['seconda_meta']:+.2f}% | {100 * x['senza_5_migliori']:+.2f}% | "
                       f"{x['esito'] if 'regola' in nome else '—'} |")
    righe_t += ["", f"L'uscita a +30% scatta nel {100 * out['fermate']:.0f}% degli eventi.", "",
                "**Per anno (con l'uscita)**: " + ", ".join(f"{a} {100 * v['media']:+.2f}% ({v['eventi']})"
                                                         for a, v in out["con_uscita"]["per_anno"].items())]
    testo = "\n".join(righe_t) + "\n"
    (QUI / "RISULTATI_QUINDICESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUINDICESIMA FINITA", flush=True)
