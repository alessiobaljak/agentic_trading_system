"""Programma 7, quarantatreesima prova (QUARANTATREESIMA.md): CB, l'effetto Coinbase: short il perpetuo di Binance contro il Bitcoin dal
giorno dopo il primo giorno di scambi su Coinbase, uscita a +30% o dopo 7 giorni; controllo sulle stesse monete in giorni qualunque.

Uso: python3 -m research.programma7.quarantatreesima
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
from research.programma6 import ventunesima as vu
from research.programma7 import quarantunesima as lv

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantatreesima"
PRIMI = QUI.parent / "data" / "coinbase" / "primi_giorni.json"
DA, A = sc.giorno(2021, 1, 1), sc.giorno(2026, 10, 1)
STORIA_MIN, GIORNI, STOP, SCARTO = 30, 7, 0.30, 0.01
CONTROLLI, SEME = 20, 2026
PROVE_A_EVENTI = 31


PAUSA_RIUSO = 7


def nascita_vera(v: np.ndarray, t0: int, nascita: int, L: int, pausa: int = PAUSA_RIUSO) -> int:
    """Il giorno di nascita del perpetuo per la regola dei 30 giorni (correzione dei dati del 25 ottobre, revisione della prova 105):
    se prima di L il volume resta a zero per almeno ``pausa`` giorni di fila, il simbolo e' stato riusato o il contratto e' ripartito
    (PUMP, RAY, HNT, LUNA...), e la nascita vera e' il primo giorno con volume dopo l'ultima pausa. ``v`` = volume giornaliero."""
    k = L - t0
    corsa, fine = 0, None
    for kk in range(max(0, nascita - t0), min(k, len(v))):
        if not v[kk] > 0:
            corsa += 1
            if corsa >= pausa:
                fine = kk
        else:
            corsa = 0
    if fine is None:
        return nascita
    n = fine + 1
    while n < min(k, len(v)) and not v[n] > 0:
        n += 1
    return max(nascita, n + t0)


def operazione(c: pd.DataFrame, cb: pd.DataFrame, f: pd.Series, fb: pd.Series, g0: int, giorni: int = GIORNI) -> dict:
    """Short la moneta e long il Bitcoin dall'apertura del giorno g0; uscita a +30% (massimo orario) o dopo ``giorni``."""
    h0, h1 = g0 * 24, (g0 + giorni) * 24
    if h0 not in c.index or h0 not in cb.index or not np.isfinite(c.loc[h0, "open"]):
        return {}
    p0, b0 = c.loc[h0, "open"], cb.loc[h0, "open"]
    tratto = c[(c.index >= h0) & (c.index < h1)]
    su = tratto.index[tratto["high"].to_numpy() >= p0 * (1 + STOP)]
    if len(su):
        uh, pc, fermata = int(su[0]), p0 * (1 + STOP) * (1 + SCARTO), True
    elif h1 in c.index and np.isfinite(c.loc[h1, "open"]):
        uh, pc, fermata = h1, c.loc[h1, "open"], False
    elif len(tratto.dropna()):
        t2 = tratto.dropna()
        uh, pc, fermata = int(t2.index[-1]) + 1, t2["close"].iloc[-1], False
    else:
        return {}
    pb = cb.loc[uh, "open"] if (not fermata and uh in cb.index) else cb[cb.index <= uh]["close"].iloc[-1]
    gu = (uh - 1) // 24
    fc = f[(f.index >= g0) & (f.index <= gu)].sum()
    fbb = fb[(fb.index >= g0) & (fb.index <= gu)].sum()
    return {"r": float((pb / b0 - 1) - (pc / p0 - 1) - vu.COSTO_MONETA - vu.COSTO_BTC + fc - fbb), "fermata": fermata, "ore": int(uh - h0)}


def esegui(log=print) -> dict:
    pan = sc.pannello()
    t0 = pan["t0"]
    giorni = np.arange(pan["close"].shape[0]) + t0
    jb = pan["simboli"].index("BTCUSDT")
    fb = pd.Series(pan["funding"][:, jb], index=giorni)
    V = pan["quote_volume"]
    primi = json.loads(PRIMI.read_text())
    eventi = []
    for b, v in sorted(primi.items()):
        L, s = v["primo_giorno_coinbase"], v["perpetuo"]
        if not isinstance(L, int) or L <= 0 or not (DA <= L <= A) or s == "BTCUSDT":
            continue
        j = pan["simboli"].index(s)
        if nascita_vera(np.nan_to_num(V[:, j]), t0, v["primo_giorno_perpetuo"], L) > L - STORIA_MIN:
            continue
        k = L - t0
        if not (0 <= k < V.shape[0]) or not np.nan_to_num(V[k, j]) > 0:
            continue
        eventi.append((s, L))
    log(f"[quarantatreesima] {len(eventi)} eventi; scarico le candele orarie")
    rng = np.random.default_rng(SEME)
    controlli = []
    ultimo = int(giorni[-1]) - GIORNI - 1
    for s, L in eventi:
        cand = np.arange(L + 60, min(L + 366, ultimo))
        if len(cand):
            for g in rng.choice(cand, size=min(CONTROLLI, len(cand)), replace=False):
                controlli.append((s, int(g)))
    serve = sorted({(s, g) for s, g in eventi + controlli} | {(s, L - 14) for s, L in eventi})
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: lv.scarica_ore(x[0], (x[1] - 1) * 24, (x[1] + 15) * 24), serve))
    lv.scarica_ore("BTCUSDT", DA * 24, (A + 20) * 24)
    cb = es.ore_di("BTCUSDT")
    ore = {}

    def candele(s):
        if s not in ore:
            ore[s] = es.ore_di(s)
        return ore[s]
    righe = []
    for s, L in eventi:
        j = pan["simboli"].index(s)
        f = pd.Series(pan["funding"][:, j], index=giorni)
        c = candele(s)
        op = operazione(c, cb, f, fb, L + 1)
        o3, o14 = operazione(c, cb, f, fb, L + 1, 3), operazione(c, cb, f, fb, L + 1, 14)
        # descrittivo: la moneta contro il Bitcoin dai 14 giorni prima a L (chiusure giornaliere del pannello)
        k0, k1 = L - 14 - t0, L - t0
        prima = float((pan["close"][k1, j] / pan["close"][k0, j]) / (pan["close"][k1, jb] / pan["close"][k0, jb]) - 1) if k0 >= 0 else np.nan
        if op:
            righe.append({"data": sc.data(L + 1), "annuncio": int((L + 1 + 3) // 7), "simbolo": s, "coinbase": sc.data(L), **op,
                          "r3": o3.get("r", np.nan), "r14": o14.get("r", np.nan), "salita_14_prima": prima})
    ev = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    ev.to_csv(RIS / "eventi_CB.csv", index=False)
    cr = []
    for s, g in controlli:
        j = pan["simboli"].index(s)
        op = operazione(candele(s), cb, pd.Series(pan["funding"][:, j], index=giorni), fb, g)
        if op:
            cr.append({"data": sc.data(g), "annuncio": int((g + 3) // 7), "simbolo": s, "r": op["r"]})
    co = pd.DataFrame(cr)
    co.to_csv(RIS / "controllo_CB.csv", index=False)
    e = tr.esame(ev, "r")
    soglia = 0.01 / PROVE_A_EVENTI
    media_controllo = float(co["r"].mean()) if len(co) else float("nan")
    # differenza con il controllo, bootstrap per moneta
    per_moneta = co.groupby("simbolo")["r"].mean()
    diff = ev.set_index("simbolo")["r"] - per_moneta.reindex(ev["simbolo"]).to_numpy()
    diff = diff[np.isfinite(diff)].to_numpy()
    b = np.random.default_rng(SEME).choice(diff, size=(10000, len(diff)), replace=True).mean(axis=1) if len(diff) else np.array([np.nan])
    out = {"eventi": int(len(ev)), "esame": e, "controllo": {"operazioni": int(len(co)), "media": media_controllo},
           "differenza_con_controllo": {"media": float(diff.mean()) if len(diff) else None, "basso": float(np.quantile(b, 0.025)),
                                        "alto": float(np.quantile(b, 0.975)), "p": float((b <= 0).mean())},
           "tre_giorni": float(ev["r3"].mean()), "quattordici_giorni": float(ev["r14"].mean()),
           "salita_14_prima_mediana": float(ev["salita_14_prima"].median()), "fermate": float(ev["fermata"].mean()), "soglia_tutte": soglia}
    valida = e["esito"] == "VALIDA" and out["differenza_con_controllo"]["p"] <= 0.05
    out["esito"] = ("VALIDA" if valida and e["boot"]["p"] <= soglia else
                    "passa l'esame scritto ma non la soglia di tutte le prove a eventi" if valida else
                    e["esito"] if e["esito"] != "VALIDA" else "non sopra il controllo sulle stesse monete")
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None or v != v else f"{100 * v:+.2f}%"  # noqa: E731
    bb, d = e["boot"], out["differenza_con_controllo"]
    righe_t = ["# Programma 7 — risultati della quarantatreesima prova (CB: l'effetto Coinbase, vendere sulla notizia)", "",
               "Regole in `QUARANTATREESIMA.md` (scritte prima). Short il perpetuo di Binance contro il Bitcoin dal giorno dopo il primo giorno di scambi su Coinbase.", "",
               f"* **{bb['eventi']} eventi: {pc(bb['media'])} a operazione** (intervallo {pc(bb['basso'])}; {pc(bb['alto'])}, p {bb['p']:.4f}); mediana "
               f"{pc(e['mediana'])}, vinte {100 * e['vinti']:.0f}%; metà {pc(e['prima_meta'])} e {pc(e['seconda_meta'])}; senza le 5 migliori "
               f"{pc(e['senza_5_migliori'])}; uscita a +30% nel {100 * out['fermate']:.0f}%.",
               "* Per anno: " + ", ".join(f"{a} {pc(v['media'])} ({v['eventi']})" for a, v in e["per_anno"].items()) + ".",
               f"* **Controllo** (le stesse monete in {out['controllo']['operazioni']} giorni qualunque fra 60 e 365 giorni dopo): {pc(media_controllo)}; "
               f"differenza evento − controllo {pc(d['media'])} (intervallo {pc(d['basso'])}; {pc(d['alto'])}, p {d['p']:.3f}).",
               f"* Tenute di 3 giorni {pc(out['tre_giorni'])}, di 14 giorni {pc(out['quattordici_giorni'])}; la salita contro il Bitcoin nei 14 giorni prima "
               f"della quotazione, in mediana, {pc(out['salita_14_prima_mediana'])}.", "",
               f"**Esito: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {soglia:.5f})."]
    testo = "\n".join(righe_t) + "\n"
    (QUI / "RISULTATI_QUARANTATREESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTATREESIMA FINITA", flush=True)
