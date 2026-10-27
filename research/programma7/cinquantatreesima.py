"""Programma 7, cinquantatreesima prova (CINQUANTATREESIMA.md): BL, il BNB dopo gli annunci di Launchpool e Megadrop. Long il perpetuo
del BNB e short quello del Bitcoin 5 minuti dopo l'annuncio, per 24 ore; controllo in minuti a caso 30-60 giorni prima.

Uso: python3 -m research.programma7.cinquantatreesima
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import trentesima as tr
from research.trader_copiati.analisi_trader2 import minuti

QUI = Path(__file__).parent
RADICE = QUI.parents[1]
QUOTAZIONI = RADICE / "research" / "data" / "annunci" / "quotazioni.json"
RIS = QUI / "risultati_cinquantatreesima"
EVENTO = re.compile(r"Binance (Launchpool|Megadrop)", re.I)
DA, A = sc.giorno(2020, 10, 22), sc.giorno(2026, 10, 24)
RITARDO, DURATA, LUNGA = 5, 1440, 3 * 1440
CASI, LONTANO, PRIMA_DA, PRIMA_A = 5, 3 * 1440, 30 * 1440, 60 * 1440
PROVE_A_EVENTI = 35


def annunci() -> list:
    """[(minuto della pubblicazione, tipo, titolo)] in ordine di tempo."""
    out = []
    for x in json.loads(QUOTAZIONI.read_text(encoding="utf-8")):
        m = EVENTO.search(x["titolo"])
        if m and "Launchpad" not in x["titolo"] and DA <= x["ms"] // 86_400_000 <= A:
            out.append((int(x["ms"] // 60_000), m.group(1).lower(), x["titolo"]))
    return sorted(out)


def serie(simbolo: str, da_min: int, a_min: int) -> pd.DataFrame:
    parti = [minuti(simbolo, sc.data(g)) for g in range(da_min // 1440, a_min // 1440 + 1)]
    parti = [p for p in parti if not p.empty]
    return pd.concat(parti).sort_index() if parti else pd.DataFrame()


def gambe(e: int, durata: int) -> dict | None:
    """Il rendimento del BNB e del Bitcoin dall'apertura del minuto e all'apertura di e + durata."""
    b, c = serie("BNBUSDT", e, e + durata), serie("BTCUSDT", e, e + durata)
    if b.empty or c.empty or e not in b.index or e not in c.index or (e + durata) not in b.index or (e + durata) not in c.index:
        return None
    return {"bnb": b.loc[e + durata, "open"] / b.loc[e, "open"] - 1, "btc": c.loc[e + durata, "open"] / c.loc[e, "open"] - 1}


def netto(g: dict, giorno: int, pan: dict, costo: dict, durata: int) -> float:
    k = giorno - pan["t0"]
    jb, jc = pan["simboli"].index("BNBUSDT"), pan["simboli"].index("BTCUSDT")
    f = (np.nan_to_num(pan["funding"][k, jb]) - np.nan_to_num(pan["funding"][k, jc])) * durata / 1440
    return g["bnb"] - g["btc"] - 2 * (costo["BNBUSDT"] + costo["BTCUSDT"]) - f


def esegui(log=print) -> dict:
    pan = sc.pannello()
    costo = dict(zip(pan["simboli"], sc.costi_moneta(pan["simboli"])))
    ann = annunci()
    momenti = [m for m, _, _ in ann]
    log(f"[cinquantatreesima] {len(ann)} annunci")
    righe, libero = [], -1
    for m, tipo, titolo in ann:
        e = m + RITARDO
        if e < libero:
            continue
        g = gambe(e, DURATA)
        if g is None:
            continue
        libero = e + DURATA
        g72, g1, g5 = gambe(e, LUNGA), gambe(m, 1), gambe(m, RITARDO)
        righe.append({"data": sc.data(e // 1440), "annuncio": int((e // 1440 + 3) // 7), "tipo": tipo, "titolo": titolo[:80],
                      "entrata_min": e, "bnb": g["bnb"], "btc": g["btc"], "r": netto(g, e // 1440, pan, costo, DURATA),
                      "r_72h": netto(g72, e // 1440, pan, costo, LUNGA) if g72 else np.nan,
                      "bnb_primo_minuto": g1["bnb"] - g1["btc"] if g1 else np.nan,
                      "bnb_primi_5_minuti": g5["bnb"] - g5["btc"] if g5 else np.nan})
    df = pd.DataFrame(righe)
    rng = np.random.default_rng(2026)
    caso = []
    for m in df["entrata_min"] - RITARDO:
        n = 0
        for _ in range(200):
            t = int(m - rng.integers(PRIMA_DA, PRIMA_A))
            if min(abs(t - x) for x in momenti) < LONTANO:
                continue
            g = gambe(t, DURATA)
            if g:
                caso.append({"data": sc.data(t // 1440), "annuncio": int((t // 1440 + 3) // 7), "r": netto(g, t // 1440, pan, costo, DURATA)})
                n += 1
            if n >= CASI:
                break
    dc = pd.DataFrame(caso)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_BL.csv", index=False)
    dc.to_csv(RIS / "caso.csv", index=False)
    ex_ = tr.esame(df, "r")
    out = {"annunci": len(ann), "eventi": len(df), "esame": ex_, "caso": {"operazioni": len(dc), "media": float(dc["r"].mean())},
           "r_72h": float(df["r_72h"].mean()), "bnb_da_solo": float(df["bnb"].mean()), "btc": float(df["btc"].mean()),
           "primo_minuto": float(df["bnb_primo_minuto"].mean()), "primi_5_minuti": float(df["bnb_primi_5_minuti"].mean()),
           "per_tipo": {t: {"eventi": int(len(x)), "media": float(x["r"].mean())} for t, x in df.groupby("tipo")},
           "soglia_tutte": 0.01 / PROVE_A_EVENTI}
    sopra_caso = ex_["boot"]["media"] > out["caso"]["media"]
    out["esito"] = ("VALIDA" if ex_["esito"] == "VALIDA" and sopra_caso and ex_["boot"]["p"] <= out["soglia_tutte"] else
                    "passa l'esame scritto (p ≤ 0,01) ma non la soglia di tutte le prove a eventi" if ex_["esito"] == "VALIDA" and sopra_caso else
                    "non sopra il controllo" if ex_["esito"] == "VALIDA" else ex_["esito"])
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    b = ex_["boot"]
    testo = "\n".join([
        "# Programma 7 — risultati della cinquantatreesima prova (BL: il BNB dopo gli annunci di Launchpool e Megadrop)", "",
        "Regole in `CINQUANTATREESIMA.md` (scritte prima). Candele a 1 minuto di Binance, dal 22 ottobre 2020 al 24 ottobre 2026.", "",
        f"* {out['annunci']} annunci, **{out['eventi']} operazioni** (long il BNB e short il Bitcoin per 24 ore, 5 minuti dopo l'annuncio).",
        f"* **{100 * b['media']:+.2f}% a evento** dopo i costi (intervallo {100 * b['basso']:+.2f}%; {100 * b['alto']:+.2f}%, p {b['p']:.4f}); mediana "
        f"{100 * ex_['mediana']:+.2f}%, vinte {100 * ex_['vinti']:.0f}%; metà {100 * ex_['prima_meta']:+.2f}% e {100 * ex_['seconda_meta']:+.2f}%; "
        f"senza le 5 migliori {100 * ex_['senza_5_migliori']:+.2f}%.",
        f"* **Il controllo** (minuti a caso 30-60 giorni prima, lontani dagli annunci): {out['caso']['operazioni']} operazioni, "
        f"{100 * out['caso']['media']:+.2f}% a operazione.",
        "* Per anno: " + ", ".join(f"{a} {100 * v['media']:+.2f}% ({v['eventi']})" for a, v in ex_["per_anno"].items()) + ".",
        "* Per tipo: " + ", ".join(f"{t} {100 * v['media']:+.2f}% ({v['eventi']})" for t, v in out["per_tipo"].items()) + ".",
        f"* Tenuta di 72 ore: {100 * out['r_72h']:+.2f}%. Il BNB da solo nelle 24 ore: {100 * out['bnb_da_solo']:+.2f}% (il Bitcoin "
        f"{100 * out['btc']:+.2f}%). Il BNB contro il Bitcoin nel primo minuto dopo l'annuncio: {100 * out['primo_minuto']:+.3f}%; nei primi 5 "
        f"minuti: {100 * out['primi_5_minuti']:+.3f}%.", "",
        f"**Esito: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {out['soglia_tutte']:.5f})."]) + "\n"
    (QUI / "RISULTATI_CINQUANTATREESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CINQUANTATREESIMA FINITA", flush=True)
