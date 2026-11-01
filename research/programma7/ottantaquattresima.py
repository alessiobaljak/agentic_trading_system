"""Programma 7, ottantaquattresima prova (OTTANTAQUATTRESIMA.md): AT, vendere dopo un attacco informatico al protocollo. Short il
perpetuo del gettone e long il Bitcoin dall'apertura del secondo giorno dopo l'attacco (elenco di DefiLlama), +30% o 7 giorni; controllo
sulle stesse monete in giorni qualunque.

Uso: python3 -m research.programma7.ottantaquattresima
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import annunci as an
from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import trentesima as tr
from research.programma7 import diciassettesima as dc
from research.programma7 import quarantatreesima as cb_
from research.programma7 import quarantunesima as lv

QUI = Path(__file__).parent
RIS = QUI / "risultati_ottantaquattresima"
DATI = QUI.parent / "data" / "attacchi"
DAL, AL = se.INIZIO, sc.giorno(2026, 9, 20)
ETA_MIN, PAUSA, TOLLERANZA, CONTROLLI, SEME, GRANDI = 30, 14, 0.20, 20, 2026, 1e7
PROVE_A_EVENTI = 45


def eventi(pan: dict, log=print) -> tuple:
    h = json.loads((DATI / "hacks.json").read_text())
    pr = {str(p["id"]): p for p in json.loads((DATI / "protocols.json").read_text())}
    S, t0 = list(pan["simboli"]), pan["t0"]
    ok = np.isfinite(pan["close"])
    primo = {s: int(np.argmax(ok[:, j])) + t0 for j, s in enumerate(S) if ok[:, j].any()}
    cache_f = DATI / "prezzi_controllo.json"
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}
    conti = {"attacchi": len(h), "fuori_periodo": 0, "senza_moneta": 0, "senza_perpetuo": 0, "perpetuo_giovane": 0, "senza_coingecko": 0,
             "prezzo_diverso": 0, "ripetuti": 0, "eventi": 0}
    cand = []
    for x in sorted(h, key=lambda z: z["date"]):
        g = int(x["date"] // 86400)
        if not DAL <= g <= AL:
            conti["fuori_periodo"] += 1
            continue
        p = pr.get(str(x.get("defillamaId")))
        sym = (p or {}).get("symbol")
        if not sym or sym == "-":
            conti["senza_moneta"] += 1
            continue
        s = an.perpetuo(sym.upper(), S)
        if not s or s == "BTCUSDT":
            conti["senza_perpetuo"] += 1
            continue
        if primo.get(s, 10 ** 9) > g - ETA_MIN:
            conti["perpetuo_giovane"] += 1
            continue
        gid = p.get("gecko_id")
        if not gid:
            conti["senza_coingecko"] += 1
            continue
        chiave = f"{g}:{gid}"
        if chiave not in cache:
            try:
                r = dc._get(dc.PREZZI.format(f"historical/{g * 86_400 + 82_800}/coingecko:{gid}"))
                cache[chiave] = float(next(iter((r.get("coins") or {}).values()))["price"])
            except Exception:  # noqa: BLE001
                cache[chiave] = float("nan")
        pz = cache[chiave]
        j = S.index(s)
        rap = pan["close"][g - t0, j] / dc.prefisso(s, sym.upper()) / pz if pz and pz > 0 else float("nan")
        if not abs(rap - 1) <= TOLLERANZA:
            conti["prezzo_diverso"] += 1
            continue
        cand.append((x["name"], s, g, float(x.get("amount") or 0), x.get("targetType")))
    cache_f.write_text(json.dumps(cache))
    ev, ultimo = [], {}
    for n, s, g, a, tt in cand:
        if g - ultimo.get(s, -10 ** 9) < PAUSA:
            conti["ripetuti"] += 1
            continue
        ultimo[s] = g
        ev.append((n, s, g, a, tt))
    conti["eventi"] = len(ev)
    return ev, conti, cand


def esegui(log=print) -> dict:
    pan = sc.pannello()
    t0, S = pan["t0"], list(pan["simboli"])
    giorni = np.arange(pan["close"].shape[0]) + t0
    ev, conti, cand = eventi(pan, log)
    log(f"[ottantaquattresima] {conti}")
    giorni_attacco: dict = {}
    for _, s, g, _a, _t in cand:
        giorni_attacco.setdefault(s, []).append(g)
    rng = np.random.default_rng(SEME)
    fine = int(giorni[-1]) - 8
    controlli = []
    for _, s, g, _a, _t in ev:
        c = np.arange(g + 60, min(g + 366, fine))
        altri = np.array(giorni_attacco[s])
        c = np.array([x for x in c if np.all(np.abs(altri - x) > PAUSA)])
        if len(c):
            controlli += [(s, int(x)) for x in rng.choice(c, size=min(CONTROLLI, len(c)), replace=False)]
    serve = sorted({(s, g + 1) for _, s, g, _a, _t in ev} | set(controlli))
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: lv.scarica_ore(x[0], (x[1] - 1) * 24, (x[1] + 16) * 24), serve))
    lv.scarica_ore("BTCUSDT", DAL * 24, (AL + 400) * 24)
    cb = es.ore_di("BTCUSDT")
    jb = S.index("BTCUSDT")
    fb = pd.Series(np.nan_to_num(pan["funding"][:, jb]), index=giorni)
    ore: dict = {}

    def candele(s):
        if s not in ore:
            ore[s] = es.ore_di(s)
        return ore[s]
    righe = []
    for n, s, g, a, tt in ev:
        j = S.index(s)
        f = pd.Series(np.nan_to_num(pan["funding"][:, j]), index=giorni)
        c = candele(s)
        op = cb_.operazione(c, cb, f, fb, g + 1)
        if not op:
            continue
        k0, k1 = g - t0, g + 1 - t0
        gia = float((pan["open"][k1, j] / pan["open"][k0, j]) / (pan["open"][k1, jb] / pan["open"][k0, jb]) - 1)
        righe.append({"data": sc.data(g + 1), "annuncio": int((g + 1 + 3) // 7), "simbolo": s, "protocollo": n, "importo": a, "tipo": tt,
                      **op, "r3": cb_.operazione(c, cb, f, fb, g + 1, 3).get("r", np.nan),
                      "r14": cb_.operazione(c, cb, f, fb, g + 1, 14).get("r", np.nan), "gia_fatto": gia})
    d = pd.DataFrame(righe)
    cr = []
    for s, g in controlli:
        j = S.index(s)
        op = cb_.operazione(candele(s), cb, pd.Series(np.nan_to_num(pan["funding"][:, j]), index=giorni), fb, g)
        if op:
            cr.append({"simbolo": s, "r": op["r"]})
    co = pd.DataFrame(cr)
    RIS.mkdir(exist_ok=True)
    d.to_csv(RIS / "eventi_AT.csv", index=False)
    co.to_csv(RIS / "controllo_AT.csv", index=False)
    e = tr.esame(d, "r")
    pm = co.groupby("simbolo")["r"].mean()
    diff = (d.set_index("simbolo")["r"] - pm.reindex(d["simbolo"]).to_numpy()).to_numpy()
    diff = diff[np.isfinite(diff)]
    b = np.random.default_rng(SEME).choice(diff, size=(10000, len(diff)), replace=True).mean(axis=1)
    dd = {"media": float(diff.mean()), "basso": float(np.quantile(b, 0.025)), "alto": float(np.quantile(b, 0.975)), "p": float((b <= 0).mean()),
          "eventi": int(len(diff))}
    soglia = 0.01 / PROVE_A_EVENTI
    valida = e["esito"] == "VALIDA" and dd["p"] <= 0.05
    esito = ("VALIDA" if valida and e["boot"]["p"] <= soglia else
             "passa l'esame scritto ma non la soglia di tutte le prove a eventi" if valida else
             e["esito"] if e["esito"] != "VALIDA" else "non sopra il controllo sulle stesse monete")
    grandi = d[d["importo"] >= GRANDI]
    out = {"conti": conti, "eventi": int(len(d)), "esame": e, "controllo": {"operazioni": int(len(co)), "media": float(co["r"].mean())},
           "differenza": dd, "tre_giorni": float(d["r3"].mean()), "quattordici_giorni": float(d["r14"].mean()),
           "gia_fatto_mediana": float(d["gia_fatto"].median()), "fermate": float(d["fermata"].mean()),
           "grandi": {"eventi": int(len(grandi)), "media": float(grandi["r"].mean()) if len(grandi) else None}, "esito": esito}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None or v != v else f"{100 * v:+.2f}%"  # noqa: E731
    bb = e["boot"]
    testo = "\n".join([
        "# Programma 7 — risultati dell'ottantaquattresima prova (AT: vendere dopo un attacco informatico al protocollo)", "",
        "Regole in `OTTANTAQUATTRESIMA.md` (scritte prima). Short il perpetuo del gettone contro il Bitcoin dall'apertura del secondo giorno "
        "dopo l'attacco, uscita a +30% o dopo 7 giorni; elenco di DefiLlama, dal 4 gennaio 2021 al 20 settembre 2026.", "",
        "* **Gli attacchi**: " + ", ".join(f"{k} {v}" for k, v in conti.items()) + ".",
        f"* **{bb['eventi']} eventi: {pc(bb['media'])} a operazione** (intervallo {pc(bb['basso'])}; {pc(bb['alto'])}, p {bb['p']:.4f}); "
        f"mediana {pc(e['mediana'])}, vinte {100 * e['vinti']:.0f}%; metà {pc(e['prima_meta'])} e {pc(e['seconda_meta'])}; senza le 5 "
        f"migliori {pc(e['senza_5_migliori'])}; uscita a +30% nel {100 * out['fermate']:.0f}%.",
        "* Per anno: " + ", ".join(f"{a} {pc(v['media'])} ({v['eventi']})" for a, v in e["per_anno"].items()) + ".",
        f"* **Controllo** (le stesse monete in {out['controllo']['operazioni']} giorni qualunque fra 60 e 365 giorni dopo): "
        f"{pc(out['controllo']['media'])}; differenza {pc(dd['media'])} (intervallo {pc(dd['basso'])}; {pc(dd['alto'])}, p {dd['p']:.3f}).",
        f"* Per capire: il crollo già fatto dal giorno dell'attacco all'entrata, contro il Bitcoin, in mediana {pc(out['gia_fatto_mediana'])}; "
        f"gli attacchi sopra i 10 milioni di dollari {out['grandi']['eventi']}, {pc(out['grandi']['media'])} a operazione; tenute di 3 giorni "
        f"{pc(out['tre_giorni'])}, di 14 giorni {pc(out['quattordici_giorni'])}.", "",
        f"**Esito: {esito}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {soglia:.5f})."]) + "\n"
    (QUI / "RISULTATI_OTTANTAQUATTRESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("OTTANTAQUATTRESIMA FINITA", flush=True)
