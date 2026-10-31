"""Programma 7, settantanovesima prova (SETTANTANOVESIMA.md): FS, il funding che diventa negativo dopo una settimana positiva. Long la
moneta e short il Bitcoin dall'apertura del giorno, 7 giorni, uscita a -30%; controllo con i giorni a funding negativo senza la settimana
positiva prima.

Uso: python3 -m research.programma7.settantanovesima
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import trentesima as tr
from research.programma6 import ventunesima as vu
from research.programma7 import prima as g1
from research.programma7 import quarantunesima as lv

QUI = Path(__file__).parent
RIS = QUI / "risultati_settantanovesima"
DAL, AL = se.INIZIO, sc.giorno(2026, 9, 20)
GIORNI, STOP, SCARTO, PAUSA, CONTROLLI, SEME = 7, 0.30, 0.01, 14, 20, 2026
PROVE_A_EVENTI = 44


def operazione(c: pd.DataFrame, cb: pd.DataFrame, f: pd.Series, fb: pd.Series, g0: int, giorni: int = GIORNI, copertura: bool = True) -> dict:
    """Long la moneta (e short il Bitcoin) dall'apertura del giorno g0; uscita a -30% (minimo orario) o dopo ``giorni``."""
    h0, h1 = g0 * 24, (g0 + giorni) * 24
    if h0 not in c.index or h0 not in cb.index or not np.isfinite(c.loc[h0, "open"]):
        return {}
    p0, b0 = c.loc[h0, "open"], cb.loc[h0, "open"]
    tratto = c[(c.index >= h0) & (c.index < h1)]
    giu = tratto.index[tratto["low"].to_numpy() <= p0 * (1 - STOP)]
    if len(giu):
        uh, pc, fermata = int(giu[0]), p0 * (1 - STOP) * (1 - SCARTO), True
    elif h1 in c.index and np.isfinite(c.loc[h1, "open"]):
        uh, pc, fermata = h1, c.loc[h1, "open"], False
    elif len(tratto.dropna()):
        t2 = tratto.dropna()
        uh, pc, fermata = int(t2.index[-1]) + 1, t2["close"].iloc[-1], False
    else:
        return {}
    gu = (uh - 1) // 24
    fc = f[(f.index >= g0) & (f.index <= gu)].sum()
    r = (pc / p0 - 1) - vu.COSTO_MONETA - fc
    if copertura:
        pb = cb.loc[uh, "open"] if (not fermata and uh in cb.index) else cb[cb.index <= uh]["close"].iloc[-1]
        r += -(pb / b0 - 1) - vu.COSTO_BTC + fb[(fb.index >= g0) & (fb.index <= gu)].sum()
    return {"r": float(r), "fermata": fermata}


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    t0, S = pan["t0"], list(pan["simboli"])
    giorni = np.arange(DAL, AL, dtype=np.int64)
    idx = giorni - t0
    Ud = g1.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    F = pan["funding"]
    jb = S.index("BTCUSDT")
    ieri = F[idx - 1]
    prima_pos = np.all(np.stack([F[idx - k] > 0 for k in range(2, 9)]), axis=0)
    prima_neg_non_tutti = ~prima_pos
    evento = Ud & (ieri < 0) & prima_pos
    controllo_cand = Ud & (ieri < 0) & prima_neg_non_tutti
    evento[:, jb] = controllo_cand[:, jb] = False
    ev, ultimo = [], {}
    for k, j in zip(*np.nonzero(evento)):
        g, s = int(giorni[k]), S[j]
        if g - ultimo.get(s, -10 ** 9) < PAUSA:
            continue
        ultimo[s] = g
        ev.append((s, g, float(ieri[k, j])))
    rng = np.random.default_rng(SEME)
    cand_per_moneta: dict = {}
    for k, j in zip(*np.nonzero(controllo_cand)):
        cand_per_moneta.setdefault(S[j], []).append(int(giorni[k]))
    controlli = []
    for s, g, _ in ev:
        c = np.array(cand_per_moneta.get(s, []))
        c = c[(np.abs(c - g) >= 30) & (np.abs(c - g) <= 365)]
        if len(c):
            controlli += [(s, int(x)) for x in rng.choice(c, size=min(CONTROLLI, len(c)), replace=False)]
    log(f"[settantanovesima] {len(ev)} eventi, {len(controlli)} controlli")
    serve = sorted({(s, g) for s, g, _ in ev} | set(controlli))
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: lv.scarica_ore(x[0], (x[1] - 1) * 24, (x[1] + 15) * 24), serve))
    lv.scarica_ore("BTCUSDT", DAL * 24, (AL + 20) * 24)
    cb = es.ore_di("BTCUSDT")
    tutti = np.arange(F.shape[0]) + t0
    fb = pd.Series(np.nan_to_num(F[:, jb]), index=tutti)
    ore: dict = {}

    def candele(s):
        if s not in ore:
            ore[s] = es.ore_di(s)
        return ore[s]
    righe = []
    for s, g, fi in ev:
        f = pd.Series(np.nan_to_num(F[:, S.index(s)]), index=tutti)
        c = candele(s)
        op = operazione(c, cb, f, fb, g)
        if not op:
            continue
        righe.append({"data": sc.data(g), "annuncio": int((g + 3) // 7), "simbolo": s, "funding_ieri": fi, **op,
                      "r3": operazione(c, cb, f, fb, g, 3).get("r", np.nan), "r14": operazione(c, cb, f, fb, g, 14).get("r", np.nan),
                      "senza_copertura": operazione(c, cb, f, fb, g, copertura=False).get("r", np.nan)})
    d = pd.DataFrame(righe)
    cr = []
    for s, g in controlli:
        op = operazione(candele(s), cb, pd.Series(np.nan_to_num(F[:, S.index(s)]), index=tutti), fb, g)
        if op:
            cr.append({"simbolo": s, "r": op["r"]})
    co = pd.DataFrame(cr)
    RIS.mkdir(exist_ok=True)
    d.to_csv(RIS / "eventi_FS.csv", index=False)
    co.to_csv(RIS / "controllo_FS.csv", index=False)
    e = tr.esame(d, "r")
    pm = co.groupby("simbolo")["r"].mean()
    diff = (d.set_index("simbolo")["r"] - pm.reindex(d["simbolo"]).to_numpy()).to_numpy()
    diff = diff[np.isfinite(diff)]
    b = np.random.default_rng(SEME).choice(diff, size=(10000, len(diff)), replace=True).mean(axis=1)
    dd = {"media": float(diff.mean()), "basso": float(np.quantile(b, 0.025)), "alto": float(np.quantile(b, 0.975)), "p": float((b <= 0).mean())}
    soglia = 0.01 / PROVE_A_EVENTI
    valida = e["esito"] == "VALIDA" and dd["p"] <= 0.05
    esito = ("VALIDA" if valida and e["boot"]["p"] <= soglia else
             "passa l'esame scritto ma non la soglia di tutte le prove a eventi" if valida else
             e["esito"] if e["esito"] != "VALIDA" else "non sopra il controllo")
    profondi = d["funding_ieri"] <= d["funding_ieri"].quantile(0.25)
    out = {"eventi": int(len(d)), "esame": e, "controllo": {"operazioni": int(len(co)), "media": float(co["r"].mean())}, "differenza": dd,
           "tre_giorni": float(d["r3"].mean()), "quattordici_giorni": float(d["r14"].mean()), "senza_copertura": float(d["senza_copertura"].mean()),
           "fermate": float(d["fermata"].mean()), "quarto_piu_negativo": float(d.loc[profondi, "r"].mean()), "esito": esito}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None or v != v else f"{100 * v:+.2f}%"  # noqa: E731
    bb = e["boot"]
    testo = "\n".join([
        "# Programma 7 — risultati della settantanovesima prova (FS: il funding che diventa negativo dopo una settimana positiva)", "",
        "Regole in `SETTANTANOVESIMA.md` (scritte prima). Long la moneta e short il Bitcoin dall'apertura del giorno, 7 giorni, uscita a "
        "−30%; universo di G1, dal 4 gennaio 2021 al 20 settembre 2026.", "",
        f"* **{bb['eventi']} eventi: {pc(bb['media'])} a operazione** (intervallo {pc(bb['basso'])}; {pc(bb['alto'])}, p {bb['p']:.4f}); "
        f"mediana {pc(e['mediana'])}, vinte {100 * e['vinti']:.0f}%; metà {pc(e['prima_meta'])} e {pc(e['seconda_meta'])}; senza le 5 "
        f"migliori {pc(e['senza_5_migliori'])}; uscita a −30% nel {100 * out['fermate']:.0f}%.",
        "* Per anno: " + ", ".join(f"{a} {pc(v['media'])} ({v['eventi']})" for a, v in e["per_anno"].items()) + ".",
        f"* **Controllo** (le stesse monete in {out['controllo']['operazioni']} giorni a funding negativo senza la settimana positiva prima): "
        f"{pc(out['controllo']['media'])}; differenza {pc(dd['media'])} (intervallo {pc(dd['basso'])}; {pc(dd['alto'])}, p {dd['p']:.3f}).",
        f"* Per capire: tenute di 3 giorni {pc(out['tre_giorni'])}, di 14 giorni {pc(out['quattordici_giorni'])}; senza la copertura del "
        f"Bitcoin {pc(out['senza_copertura'])}; il quarto con il funding più negativo {pc(out['quarto_piu_negativo'])}.", "",
        f"**Esito: {esito}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {soglia:.5f})."]) + "\n"
    (QUI / "RISULTATI_SETTANTANOVESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SETTANTANOVESIMA FINITA", flush=True)
