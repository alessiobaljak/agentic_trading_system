"""Programma 7, settantottesima prova (SETTANTOTTESIMA.md): QH, vendere quando una moneta gia' su Binance arriva su Hyperliquid: short il
perpetuo di Binance contro il Bitcoin dal giorno dopo il primo funding su Hyperliquid, +30% o 7 giorni, come la prova 105.

Uso: python3 -m research.programma7.settantottesima
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma6 import trentesima as tr
from research.programma7 import quarantatreesima as cb_
from research.programma7 import quarantunesima as lv
from research.programma7 import settantatreesima as hl

QUI = Path(__file__).parent
RIS = QUI / "risultati_settantottesima"
DAL, AL = sc.giorno(2023, 6, 12), sc.giorno(2026, 9, 20)
ETA_MIN, CONTROLLI, SEME = 30, 20, 2026
PROVE_A_EVENTI = 43


def eventi(pan: dict) -> list:
    S, t0 = list(pan["simboli"]), pan["t0"]
    ok = np.isfinite(pan["close"])
    primo = {s: t0 + int(ok[:, j].argmax()) for j, s in enumerate(S) if ok[:, j].any()}
    out = []
    for f in sorted(hl.DATI.glob("*.json")):
        n = f.stem
        d = json.loads(f.read_text())
        if not d:
            continue
        g = int(d[0][0] // 86_400_000)
        corta = n.startswith("k") and n[1:].isupper()
        cand = (f"1000{n[1:]}USDT",) if corta else (f"{n}USDT", f"1000{n}USDT")
        s = next((x for x in cand if x in S), None)
        if s and s != "BTCUSDT" and DAL <= g <= AL and g - primo[s] >= ETA_MIN:
            out.append((n, s, g))
    return out


def esegui(log=print) -> dict:
    pan = sc.pannello()
    t0, S = pan["t0"], list(pan["simboli"])
    giorni = np.arange(pan["close"].shape[0]) + t0
    ev = eventi(pan)
    log(f"[settantottesima] {len(ev)} eventi")
    rng = np.random.default_rng(SEME)
    ultimo = int(giorni[-1]) - 8
    controlli = []
    for _, s, g in ev:
        cand = np.arange(g + 60, min(g + 366, ultimo))
        if len(cand):
            controlli += [(s, int(x)) for x in rng.choice(cand, size=min(CONTROLLI, len(cand)), replace=False)]
    serve = sorted({(s, g + 1) for _, s, g in ev} | {(s, g - 7) for _, s, g in ev} | set(controlli))
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: lv.scarica_ore(x[0], (x[1] - 1) * 24, (x[1] + 16) * 24), serve))
    lv.scarica_ore("BTCUSDT", DAL * 24, (AL + 400) * 24)
    cb = es.ore_di("BTCUSDT")
    fb = pd.Series(np.nan_to_num(pan["funding"][:, S.index("BTCUSDT")]), index=giorni)
    jb = S.index("BTCUSDT")
    ore: dict = {}

    def candele(s):
        if s not in ore:
            ore[s] = es.ore_di(s)
        return ore[s]
    righe = []
    for n, s, g in ev:
        j = S.index(s)
        f = pd.Series(np.nan_to_num(pan["funding"][:, j]), index=giorni)
        c = candele(s)
        op = cb_.operazione(c, cb, f, fb, g + 1)
        if not op:
            continue
        k0, k1 = g - 7 - t0, g - t0
        prima = float((pan["close"][k1, j] / pan["close"][k0, j]) / (pan["close"][k1, jb] / pan["close"][k0, jb]) - 1)
        righe.append({"data": sc.data(g + 1), "annuncio": int((g + 1 + 3) // 7), "simbolo": s, "hyperliquid": n, **op,
                      "r3": cb_.operazione(c, cb, f, fb, g + 1, 3).get("r", np.nan),
                      "r14": cb_.operazione(c, cb, f, fb, g + 1, 14).get("r", np.nan), "salita_7_prima": prima})
    d = pd.DataFrame(righe)
    cr = []
    for s, g in controlli:
        j = S.index(s)
        op = cb_.operazione(candele(s), cb, pd.Series(np.nan_to_num(pan["funding"][:, j]), index=giorni), fb, g)
        if op:
            cr.append({"simbolo": s, "r": op["r"]})
    co = pd.DataFrame(cr)
    RIS.mkdir(exist_ok=True)
    d.to_csv(RIS / "eventi_QH.csv", index=False)
    co.to_csv(RIS / "controllo_QH.csv", index=False)
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
             e["esito"] if e["esito"] != "VALIDA" else "non sopra il controllo sulle stesse monete")
    out = {"eventi": int(len(d)), "esame": e, "controllo": {"operazioni": int(len(co)), "media": float(co["r"].mean())}, "differenza": dd,
           "tre_giorni": float(d["r3"].mean()), "quattordici_giorni": float(d["r14"].mean()),
           "salita_7_prima_mediana": float(d["salita_7_prima"].median()), "fermate": float(d["fermata"].mean()), "esito": esito}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None or v != v else f"{100 * v:+.2f}%"  # noqa: E731
    bb = e["boot"]
    testo = "\n".join([
        "# Programma 7 — risultati della settantottesima prova (QH: vendere quando una moneta arriva su Hyperliquid)", "",
        "Regole in `SETTANTOTTESIMA.md` (scritte prima). Short il perpetuo di Binance contro il Bitcoin dal giorno dopo il primo funding su "
        "Hyperliquid, uscita a +30% o dopo 7 giorni; dal giugno 2023 al settembre 2026.", "",
        f"* **{bb['eventi']} eventi: {pc(bb['media'])} a operazione** (intervallo {pc(bb['basso'])}; {pc(bb['alto'])}, p {bb['p']:.4f}); "
        f"mediana {pc(e['mediana'])}, vinte {100 * e['vinti']:.0f}%; metà {pc(e['prima_meta'])} e {pc(e['seconda_meta'])}; senza le 5 "
        f"migliori {pc(e['senza_5_migliori'])}; uscita a +30% nel {100 * out['fermate']:.0f}%.",
        "* Per anno: " + ", ".join(f"{a} {pc(v['media'])} ({v['eventi']})" for a, v in e["per_anno"].items()) + ".",
        f"* **Controllo** (le stesse monete in {out['controllo']['operazioni']} giorni qualunque fra 60 e 365 giorni dopo): "
        f"{pc(out['controllo']['media'])}; differenza {pc(dd['media'])} (intervallo {pc(dd['basso'])}; {pc(dd['alto'])}, p {dd['p']:.3f}).",
        f"* Per capire: tenute di 3 giorni {pc(out['tre_giorni'])}, di 14 giorni {pc(out['quattordici_giorni'])}; la moneta contro il Bitcoin "
        f"nei 7 giorni prima, in mediana, {pc(out['salita_7_prima_mediana'])}.", "",
        f"**Esito: {esito}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {soglia:.5f})."]) + "\n"
    (QUI / "RISULTATI_SETTANTOTTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SETTANTOTTESIMA FINITA", flush=True)
