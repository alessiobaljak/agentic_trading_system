"""Programma 7, quarantaquattresima prova (QUARANTAQUATTRESIMA.md): CBO, conferma della prova 105 sulle quotazioni a pronti di OKX:
stessa regola (short il perpetuo di Binance contro il Bitcoin dal giorno dopo, +30% o 7 giorni), stesso controllo.

Uso: python3 -m research.programma7.quarantaquattresima
"""
from __future__ import annotations

import collections
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma6 import trentesima as tr
from research.programma7 import quarantatreesima as cbm
from research.programma7 import quarantunesima as lv

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantaquattresima"
PRIMI = QUI.parent / "data" / "okx_primi_giorni.json"
TECNICO = 10


def esegui(log=print) -> dict:
    pan = sc.pannello()
    t0 = pan["t0"]
    giorni = np.arange(pan["close"].shape[0]) + t0
    jb = pan["simboli"].index("BTCUSDT")
    fb = pd.Series(pan["funding"][:, jb], index=giorni)
    V = pan["quote_volume"]
    primi = json.loads(PRIMI.read_text())
    conta = collections.Counter(v["primo_giorno_okx"] for v in primi.values())
    tecnici = {g for g, n in conta.items() if n >= TECNICO}
    eventi = []
    for b, v in sorted(primi.items()):
        L, s = v["primo_giorno_okx"], v["perpetuo"]
        if L in tecnici or not (cbm.DA <= L <= cbm.A) or s == "BTCUSDT":
            continue
        j = pan["simboli"].index(s)
        if cbm.nascita_vera(np.nan_to_num(V[:, j]), t0, v["primo_giorno_perpetuo"], L) > L - cbm.STORIA_MIN:
            continue
        k = L - t0
        if 0 <= k < V.shape[0] and np.nan_to_num(V[k, j]) > 0:
            eventi.append((s, L))
    log(f"[quarantaquattresima] {len(eventi)} eventi (tolti {len(tecnici)} giorni tecnici: {[sc.data(g) for g in sorted(tecnici)]})")
    rng = np.random.default_rng(cbm.SEME)
    ultimo = int(giorni[-1]) - cbm.GIORNI - 1
    controlli = []
    for s, L in eventi:
        cand = np.arange(L + 60, min(L + 366, ultimo))
        if len(cand):
            controlli += [(s, int(g)) for g in rng.choice(cand, size=min(cbm.CONTROLLI, len(cand)), replace=False)]
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: lv.scarica_ore(x[0], (x[1] - 1) * 24, (x[1] + 9) * 24), sorted(set(eventi + controlli))))
    cb = es.ore_di("BTCUSDT")
    ore = {}

    def candele(s):
        if s not in ore:
            ore[s] = es.ore_di(s)
        return ore[s]
    righe = []
    for s, L in eventi:
        j = pan["simboli"].index(s)
        op = cbm.operazione(candele(s), cb, pd.Series(pan["funding"][:, j], index=giorni), fb, L + 1)
        if op:
            righe.append({"data": sc.data(L + 1), "annuncio": int((L + 1 + 3) // 7), "simbolo": s, "okx": sc.data(L), **op})
    ev = pd.DataFrame(righe)
    cr = []
    for s, g in controlli:
        j = pan["simboli"].index(s)
        op = cbm.operazione(candele(s), cb, pd.Series(pan["funding"][:, j], index=giorni), fb, g)
        if op:
            cr.append({"simbolo": s, "r": op["r"]})
    co = pd.DataFrame(cr)
    RIS.mkdir(exist_ok=True)
    ev.to_csv(RIS / "eventi_CBO.csv", index=False)
    co.to_csv(RIS / "controllo_CBO.csv", index=False)
    e = tr.esame(ev, "r")
    per_moneta = co.groupby("simbolo")["r"].mean()
    diff = (ev.set_index("simbolo")["r"] - per_moneta.reindex(ev["simbolo"]).to_numpy()).dropna().to_numpy()
    bd = np.random.default_rng(cbm.SEME).choice(diff, size=(10000, len(diff)), replace=True).mean(axis=1)
    out = {"eventi": int(len(ev)), "esame": e, "controllo_media": float(co["r"].mean()),
           "differenza": {"media": float(diff.mean()), "basso": float(np.quantile(bd, 0.025)), "alto": float(np.quantile(bd, 0.975)), "p": float((bd <= 0).mean())},
           "giorni_tecnici": [sc.data(g) for g in sorted(tecnici)]}
    out["esito"] = "conferma riuscita" if e["boot"]["p"] <= 0.05 and e["boot"]["media"] > 0 and out["differenza"]["p"] <= 0.05 else "conferma non riuscita"
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: f"{100 * v:+.2f}%"  # noqa: E731
    b, d = e["boot"], out["differenza"]
    testo = "\n".join([
        "# Programma 7 — risultati della quarantaquattresima prova (CBO: la quotazione su OKX, conferma della prova 105)", "",
        "Regole in `QUARANTAQUATTRESIMA.md` (scritte prima). Stessa regola della prova 105 sulle quotazioni a pronti di OKX.", "",
        f"* Giorni tecnici tolti: {', '.join(out['giorni_tecnici'])}.",
        f"* **{b['eventi']} eventi: {pc(b['media'])} a operazione** (intervallo {pc(b['basso'])}; {pc(b['alto'])}, p {b['p']:.4f}); mediana {pc(e['mediana'])}, "
        f"vinte {100 * e['vinti']:.0f}%; metà {pc(e['prima_meta'])} e {pc(e['seconda_meta'])}; senza le 5 migliori {pc(e['senza_5_migliori'])}.",
        "* Per anno: " + ", ".join(f"{a} {pc(v['media'])} ({v['eventi']})" for a, v in e["per_anno"].items()) + ".",
        f"* Controllo sulle stesse monete in giorni qualunque: {pc(out['controllo_media'])}; differenza {pc(d['media'])} (intervallo {pc(d['basso'])}; "
        f"{pc(d['alto'])}, p {d['p']:.3f}).", "",
        f"**Esito: {out['esito']}** (serve p ≤ 0,05 e la differenza con il controllo sopra zero con p ≤ 0,05)."]) + "\n"
    (QUI / "RISULTATI_QUARANTAQUATTRESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTAQUATTRESIMA FINITA", flush=True)
