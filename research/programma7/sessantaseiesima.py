"""Programma 7, sessantaseiesima prova (SESSANTASEIESIMA.md): BP, comprare il perpetuo quando e' sotto il pronti: l'ora chiude con
l'indice del premio di Binance a −1% o sotto (dopo un'ora sopra −0,5%), long il perpetuo e short il Bitcoin dall'ora dopo per 4 ore;
controllo sulle stesse monete in ore normali.

Uso: python3 -m research.programma7.sessantaseiesima
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import esecuzione as es
from research.programma6 import scarico_giorni as sg
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import trentesima as tr
from research.programma6 import ventunesima as vu
from research.programma6 import sesta as se
from research.programma7 import buco_perpetuo as bp
from research.programma7 import quarantunesima as lv

QUI = Path(__file__).parent
RIS = QUI / "risultati_sessantaseiesima"
DAL, AL = se.INIZIO, sc.giorno(2026, 10, 1)
SOGLIA, PRIMA, ORE, PAUSA = -0.01, -0.005, 4, 24
CONTROLLI, SEME = 20, 2026
PROVE_A_EVENTI = 37


def operazione(c: pd.DataFrame, cb: pd.DataFrame, f: pd.Series, fb: pd.Series, h0: int, ore: int, copertura: bool = True) -> float:
    """Long la moneta (e short il Bitcoin) dall'apertura dell'ora h0 all'apertura di h0 + ore; costi a mercato; funding a un terzo
    del giorno per ogni regolamento delle 00, 08, 16 UTC in (h0, h0 + ore]."""
    h1 = h0 + ore
    if not all(h in c.index and np.isfinite(c.loc[h, "open"]) for h in (h0, h1)):
        return np.nan
    r = c.loc[h1, "open"] / c.loc[h0, "open"] - 1 - vu.COSTO_MONETA
    regolamenti = [h for h in range(h0 + 1, h1 + 1) if h % 8 == 0]
    r -= sum(f.get(h // 24, 0.0) for h in regolamenti) / 3
    if copertura:
        if not all(h in cb.index and np.isfinite(cb.loc[h, "open"]) for h in (h0, h1)):
            return np.nan
        r -= cb.loc[h1, "open"] / cb.loc[h0, "open"] - 1 + vu.COSTO_BTC
        r += sum(fb.get(h // 24, 0.0) for h in regolamenti) / 3
    return float(r)


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun, U = ps["lunedi"], ps["U"]
    k = (lun >= DAL - 6) & (lun < AL)
    settimane, lavori = {}, []
    for j, s in enumerate(ps["simboli"]):
        w = lun[k][U[k, j]]
        if len(w):
            settimane[s] = set(int(x) for x in w)
            for m in bp.mesi(int(w.min()), int(w.max()) + 7):
                lavori.append((s, m))
    log(f"[sessantaseiesima] {len(settimane)} monete, {len(lavori)} file mensili del premio")

    def uno(x):
        s, m = x
        try:
            sg._scarica(f"data/futures/um/monthly/premiumIndexKlines/{s}/1h/{s}-1h-{m}.zip", bp.DATI / s)
        except Exception:  # noqa: BLE001
            pass
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(uno, lavori))
    premi, eventi = {}, []
    for s, sw in settimane.items():
        p = bp.premio_ore(s)
        if p.empty:
            continue
        premi[s] = p
        ultimo = -10 ** 9
        for h in p.index[(p.to_numpy() <= SOGLIA)]:
            g = int(h // 24)
            if not (DAL <= g < AL) or (g - ((g + 3) % 7)) not in sw or h - ultimo < PAUSA:
                continue
            if (h - 1) not in p.index or not p.loc[h - 1] > PRIMA:
                continue
            ultimo = h
            eventi.append((s, int(h)))
    log(f"[sessantaseiesima] {len(eventi)} eventi")
    rng = np.random.default_rng(SEME)
    per_moneta: dict = {}
    for s, h in eventi:
        per_moneta.setdefault(s, []).append(h)
    controlli = []
    for s, h in eventi:
        p, sw = premi[s], settimane[s]
        ev = np.array(per_moneta[s])
        cand = np.r_[np.arange(h - 365 * 24, h - 30 * 24 + 1), np.arange(h + 30 * 24, h + 365 * 24 + 1)]
        cand = cand[np.isin(cand, p.index.to_numpy())]
        cand = cand[p.reindex(cand).to_numpy() > PRIMA]
        lunc = (cand // 24) - (((cand // 24) + 3) % 7)
        cand = cand[np.isin(lunc, list(sw)) & ((cand // 24) >= DAL) & ((cand // 24) < AL)]
        ev = np.sort(ev)
        pos = np.searchsorted(ev, cand)
        vicino = np.minimum(np.abs(cand - ev[np.clip(pos - 1, 0, len(ev) - 1)]), np.abs(cand - ev[np.clip(pos, 0, len(ev) - 1)]))
        cand = cand[vicino >= PAUSA]
        if len(cand):
            for x in rng.choice(cand, size=min(CONTROLLI, len(cand)), replace=False):
                controlli.append((s, int(x)))
    serve = sorted({(s, h // 24) for s, h in eventi + controlli})
    log(f"[sessantaseiesima] {len(controlli)} controlli; scarico le candele orarie di {len(serve)} giorni")
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: lv.scarica_ore(x[0], (x[1] - 1) * 24, (x[1] + 3) * 24), serve))
    lv.scarica_ore("BTCUSDT", DAL * 24, AL * 24)
    cb = es.ore_di("BTCUSDT")
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    S = list(pan["simboli"])
    fb = pd.Series(np.nan_to_num(pan["funding"][:, S.index("BTCUSDT")]), index=giorni)
    ore_c: dict = {}

    def candele(s):
        if s not in ore_c:
            ore_c[s] = es.ore_di(s)
        return ore_c[s]
    righe = []
    for s, h in eventi:
        c, f = candele(s), pd.Series(np.nan_to_num(pan["funding"][:, S.index(s)]), index=giorni)
        r = operazione(c, cb, f, fb, h + 1, ORE)
        if not np.isfinite(r):
            continue
        p = premi[s]
        g = h // 24
        righe.append({"data": sc.data(g), "annuncio": int((g + 3) // 7), "simbolo": s, "ora": h, "premio": float(p.loc[h]), "r": r,
                      **{f"r{o}": operazione(c, cb, f, fb, h + 1, o) for o in (1, 2, 8, 24)},
                      "senza_copertura": operazione(c, cb, f, fb, h + 1, ORE, copertura=False),
                      "cambio_premio": float(p.loc[h + ORE] - p.loc[h]) if (h + ORE) in p.index else np.nan})
    ev = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    ev.to_csv(RIS / "eventi_BP.csv", index=False)
    cr = []
    for s, h in controlli:
        r = operazione(candele(s), cb, pd.Series(np.nan_to_num(pan["funding"][:, S.index(s)]), index=giorni), fb, h + 1, ORE)
        if np.isfinite(r):
            cr.append({"data": sc.data(h // 24), "simbolo": s, "r": r})
    co = pd.DataFrame(cr)
    co.to_csv(RIS / "controllo_BP.csv", index=False)
    e = tr.esame(ev, "r")
    soglia = 0.01 / PROVE_A_EVENTI
    pm = co.groupby("simbolo")["r"].mean()
    diff = (ev.set_index("simbolo")["r"] - pm.reindex(ev["simbolo"]).to_numpy()).to_numpy()
    diff = diff[np.isfinite(diff)]
    b = np.random.default_rng(SEME).choice(diff, size=(10000, len(diff)), replace=True).mean(axis=1)
    vecchi = ev["data"] < "2024-01-01"
    profondi = ev["premio"] <= -0.02
    out = {"eventi_trovati": len(eventi), "eventi": int(len(ev)), "esame": e,
           "controllo": {"operazioni": int(len(co)), "media": float(co["r"].mean())},
           "differenza_con_controllo": {"media": float(diff.mean()), "eventi": int(len(diff)), "basso": float(np.quantile(b, 0.025)),
                                        "alto": float(np.quantile(b, 0.975)), "p": float((b <= 0).mean())},
           "tenute": {o: float(ev[f"r{o}"].mean()) for o in (1, 2, 8, 24)}, "senza_copertura": float(ev["senza_copertura"].mean()),
           "profondi": {"eventi": int(profondi.sum()), "media": float(ev.loc[profondi, "r"].mean())},
           "2021_2023": {"eventi": int(vecchi.sum()), "media": float(ev.loc[vecchi, "r"].mean())},
           "2024_2026": {"eventi": int((~vecchi).sum()), "media": float(ev.loc[~vecchi, "r"].mean())},
           "cambio_premio_mediana": float(ev["cambio_premio"].median()), "soglia_tutte": soglia}
    valida = e["esito"] == "VALIDA" and out["differenza_con_controllo"]["p"] <= 0.05
    out["esito"] = ("VALIDA" if valida and e["boot"]["p"] <= soglia else
                    "passa l'esame scritto ma non la soglia di tutte le prove a eventi" if valida else
                    e["esito"] if e["esito"] != "VALIDA" else "non sopra il controllo sulle stesse monete")
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None or v != v else f"{100 * v:+.2f}%"  # noqa: E731
    bb, d = e["boot"], out["differenza_con_controllo"]
    testo = "\n".join([
        "# Programma 7 — risultati della sessantaseiesima prova (BP: comprare il perpetuo quando è sotto il pronti)", "",
        "Regole in `SESSANTASEIESIMA.md` (scritte prima). Long il perpetuo e short il Bitcoin per 4 ore dall'ora dopo quella che chiude "
        "con il premio a −1% o sotto; dal 4 gennaio 2021 al 30 settembre 2026, costi a mercato.", "",
        f"* **{bb['eventi']} eventi** (trovati {len(eventi)}): **{pc(bb['media'])} a operazione** (intervallo {pc(bb['basso'])}; "
        f"{pc(bb['alto'])}, p {bb['p']:.4f}); mediana {pc(e['mediana'])}, vinte {100 * e['vinti']:.0f}%; metà {pc(e['prima_meta'])} e "
        f"{pc(e['seconda_meta'])}; senza le 5 migliori {pc(e['senza_5_migliori'])}.",
        "* Per anno: " + ", ".join(f"{a} {pc(v['media'])} ({v['eventi']})" for a, v in e["per_anno"].items()) + ".",
        f"* **Controllo** (le stesse monete in {out['controllo']['operazioni']} ore normali): {pc(out['controllo']['media'])}; differenza "
        f"evento − controllo {pc(d['media'])} (intervallo {pc(d['basso'])}; {pc(d['alto'])}, p {d['p']:.3f}).",
        "* Per capire: tenute di " + ", ".join(f"{o} ore {pc(v)}" for o, v in out["tenute"].items()) + f"; senza la copertura del "
        f"Bitcoin {pc(out['senza_copertura'])}; eventi a −2% o sotto {pc(out['profondi']['media'])} ({out['profondi']['eventi']}); "
        f"2021-2023 {pc(out['2021_2023']['media'])} ({out['2021_2023']['eventi']}), 2024-2026 {pc(out['2024_2026']['media'])} "
        f"({out['2024_2026']['eventi']}); il premio nelle 4 ore cambia di {pc(out['cambio_premio_mediana'])} in mediana.", "",
        f"**Esito: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {soglia:.5f})."]) + "\n"
    (QUI / "RISULTATI_SESSANTASEIESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SESSANTASEIESIMA FINITA", flush=True)
