"""Programma 7, quarantaduesima prova (QUARANTADUESIMA.md): G26, cavalcare la fiammata invece di venderla: long allo stesso segnale
della prova 75, stop che segue il prezzo al 10% sotto il massimo raggiunto, al massimo 24 ore, rientri a ogni segnale nuovo.
Decisione sul 2021-2022; il 2023-2024 e il 2025-2026 solo descrittivi.

Uso: python3 -m research.programma7.quarantaduesima
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import trentesima as tr
from research.programma7 import diciottesima as g16
from research.trader_copiati.analisi_trader2 import minuti

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantaduesima"
PERIODI = {"decisione 2021-2022": (sc.giorno(2021, 1, 1), sc.giorno(2022, 12, 31)),
           "descrittivo 2023-2024": (sc.giorno(2023, 1, 1), sc.giorno(2024, 12, 31)),
           "descrittivo 2025-2026": (sc.giorno(2025, 1, 1), sc.giorno(2026, 6, 26))}
TRAILING, SCARTO, MAX_MIN, PAUSA = 0.10, 0.01, 1440, 15
PROVE_A_EVENTI = 30
QUOTA = 0.01


def operazione_long(w: pd.DataFrame, t: int, costo: float, trailing: float = TRAILING, max_min: int = MAX_MIN) -> dict | None:
    """Long all'apertura del minuto t + 1; stop al (1 - trailing) del massimo raggiunto (prima l'apertura), uscita al livello meno lo
    scarto quando il minimo lo tocca; altrimenti all'apertura del minuto dopo max_min."""
    e = t + 1
    if e not in w.index:
        return None
    tratto = w.loc[e:e + max_min]
    p0 = float(w.loc[e, "open"])
    if not p0 > 0 or tratto.empty:
        return None
    hi, lo, mm = tratto["high"].to_numpy(), tratto["low"].to_numpy(), tratto.index.to_numpy()
    massimo = p0
    for i in range(len(mm)):
        stop = massimo * (1 - trailing)
        if lo[i] <= stop:                         # prudente: nel minuto in cui si tocca lo stop, il nuovo massimo non conta
            px = stop * (1 - SCARTO)
            return {"entrata_min": e, "uscita_min": int(mm[i]), "minuti": int(mm[i] - e), "p0": p0, "px": px, "motivo": "stop",
                    "massimo": massimo / p0 - 1, "r_prezzo": px / p0 - 1, "costi": 2 * costo}
        massimo = max(massimo, hi[i])
    ultimo = int(mm[-1])
    completo = ultimo >= e + max_min
    uscita = e + max_min if completo and (e + max_min) in w.index else ultimo
    px = float(w.loc[uscita, "open"]) if completo and uscita in w.index else float(w.loc[ultimo, "close"])
    return {"entrata_min": e, "uscita_min": int(uscita), "minuti": int(uscita - e), "p0": p0, "px": px,
            "motivo": "tempo" if completo else "dati finiti", "massimo": massimo / p0 - 1, "r_prezzo": px / p0 - 1, "costi": 2 * costo}


def periodo(pan: dict, da: int, a: int, log=print) -> tuple:
    g16.DA, g16.A = da, a
    t0, simboli = pan["t0"], pan["simboli"]
    cand = g16.candidati(pan)
    log(f"[quarantaduesima] {sc.data(da)} → {sc.data(a)}: {len(cand)} giorni-moneta candidati su {len({j for j, _ in cand})} monete; candele a 1 minuto")
    file = sorted({(simboli[j], k + t0 + d) for j, k in cand for d in (-1, 0, 1)})
    with ThreadPoolExecutor(max_workers=12) as ex:
        list(ex.map(lambda x: minuti(x[0], sc.data(x[1])), file))
    costo = dict(zip(simboli, sc.costi_moneta(simboli)))
    per_moneta: dict = {}
    for j, k in cand:
        per_moneta.setdefault(j, set()).add(k)
    rng = np.random.default_rng(2026)
    righe, caso = [], []
    for j, giorni_k in sorted(per_moneta.items()):
        s = simboli[j]
        w = g16.blocco(s, sorted({k + t0 + d for k in giorni_k for d in (-1, 0, 1)}))
        if w.empty:
            continue
        ammessi = np.concatenate([np.arange((k + t0) * 1440, (k + t0 + 1) * 1440) for k in sorted(giorni_k)])
        libero_da = -1
        segn = g16.segnali(w, ammessi)
        for t in segn:
            if t < libero_da:
                continue
            op = operazione_long(w, t, costo[s])
            if op is None:
                continue
            k = t // 1440 - t0
            f = -float(np.nan_to_num(pan["funding"][k, j])) * op["minuti"] / 1440.0
            righe.append({"data": sc.data(t // 1440), "annuncio": int((t // 1440 + 3) // 7), "simbolo": s, "segnale_min": t,
                          **op, "funding": f, "r": op["r_prezzo"] - op["costi"] + f})
            libero_da = op["uscita_min"] + PAUSA
        n_giorno = pd.Series([t // 1440 for t in segn]).value_counts().to_dict() if segn else {}
        for gg, n in n_giorno.items():
            for t in rng.integers(gg * 1440, gg * 1440 + 1440, size=int(n)):
                op = operazione_long(w, int(t), costo[s])
                if op:
                    caso.append({"data": sc.data(int(t) // 1440), "annuncio": int((int(t) // 1440 + 3) // 7), "simbolo": s,
                                 "r": op["r_prezzo"] - op["costi"], "motivo": op["motivo"]})
    df = pd.DataFrame(righe)
    if len(df):
        df = df.sort_values(["data", "segnale_min"]).reset_index(drop=True)
        df["giorno"] = df["entrata_min"] // 1440
        df["n_nel_giorno"] = df.sort_values("entrata_min").groupby(["simbolo", "giorno"]).cumcount() + 1
    return df, pd.DataFrame(caso), len(cand)


def conto(df: pd.DataFrame, quota: float = QUOTA) -> dict:
    """Il conto con ``quota`` del conto a operazione (somma alle uscite, interesse semplice): finale e discesa peggiore."""
    if df.empty:
        return {}
    x = df.sort_values("uscita_min")
    curva = 1 + quota * x["r"].cumsum().to_numpy()
    picco = np.maximum.accumulate(np.concatenate([[1.0], curva]))[1:]
    return {"finale": float(curva[-1]), "discesa_peggiore": float((curva / picco - 1).min())}


def descrivi(df: pd.DataFrame, caso: pd.DataFrame, n_cand: int) -> dict:
    if df.empty:
        return {"operazioni": 0}
    ex_ = tr.esame(df, "r")
    return {"esame": ex_, "candidati": n_cand, "operazioni": int(len(df)), "monete": int(df["simbolo"].nunique()),
            "motivi": df["motivo"].value_counts(normalize=True).round(4).to_dict(), "minuti_mediana": float(df["minuti"].median()),
            "r_prezzo_medio": float(df["r_prezzo"].mean()), "costi_medi": float(df["costi"].mean()), "funding_medio": float(df["funding"].mean()),
            "oltre_50": int((df["r"] > 0.5).sum()), "peso_oltre_50": float(df.loc[df["r"] > 0.5, "r"].sum() / max(1e-12, df["r"].sum())) if df["r"].sum() > 0 else None,
            "massimo_mediano": float(df["massimo"].median()),
            "per_ordine": {int(k): {"n": int(len(x)), "media": float(x["r"].mean()), "vinte": float((x["r"] > 0).mean())}
                           for k, x in df.groupby(df["n_nel_giorno"].clip(upper=4))},
            "caso": {"operazioni": int(len(caso)), "media": float(caso["r"].mean()) if len(caso) else None},
            "conto_1pc": conto(df), "migliori": df.nlargest(5, "r")[["data", "simbolo", "r"]].to_dict("records")}


def esegui(log=print) -> dict:
    pan = sc.pannello()
    RIS.mkdir(exist_ok=True)
    out = {}
    for nome, (da, a) in PERIODI.items():
        df, caso, n_cand = periodo(pan, da, a, log)
        df.to_csv(RIS / f"eventi_G26_{nome.split()[-1]}.csv", index=False)
        out[nome] = descrivi(df, caso, n_cand)
        log(f"[quarantaduesima] {nome}: {out[nome].get('operazioni', 0)} operazioni")
    d = out["decisione 2021-2022"]
    soglia = 0.01 / PROVE_A_EVENTI
    e = d.get("esame")
    out["esito"] = ("nessuna operazione" if e is None else "VALIDA" if e["esito"] == "VALIDA" and e["boot"]["p"] <= soglia else
                    "passa l'esame scritto ma non la soglia di tutte le prove a eventi" if e["esito"] == "VALIDA" else e["esito"])
    out["soglia_tutte"] = soglia
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None else f"{100 * v:+.2f}%"  # noqa: E731
    righe = ["# Programma 7 — risultati della quarantaduesima prova (G26: cavalcare la fiammata invece di venderla)", "",
             "Regole in `QUARANTADUESIMA.md` (scritte prima). Long allo stesso segnale della prova 75, stop che segue il prezzo al 10% sotto il "
             "massimo, al massimo 24 ore, rientri a ogni segnale nuovo. **Decide il 2021-2022**; gli altri periodi sono solo descrittivi.", ""]
    for nome, x in out.items():
        if not isinstance(x, dict) or "esame" not in x:
            continue
        b = x["esame"]["boot"]
        righe += [f"## {nome}", "",
                  f"* {x['candidati']} giorni-moneta candidati; **{x['operazioni']} operazioni** su {x['monete']} monete; durata mediana "
                  f"{x['minuti_mediana']:.0f} minuti; uscite " + ", ".join(f"{k} {100 * v:.0f}%" for k, v in x["motivi"].items()) + ".",
                  f"* **{pc(b['media'])} a operazione** (intervallo {pc(b['basso'])}; {pc(b['alto'])}, p {b['p']:.4f}); mediana {pc(x['esame']['mediana'])}, "
                  f"vinte {100 * x['esame']['vinti']:.0f}%; metà {pc(x['esame']['prima_meta'])} e {pc(x['esame']['seconda_meta'])}; **senza le 5 migliori "
                  f"{pc(x['esame']['senza_5_migliori'])}**. Prezzo {pc(x['r_prezzo_medio'])}, costi {pc(x['costi_medi'])}, funding {pc(x['funding_medio'])}.",
                  f"* Operazioni oltre +50%: {x['oltre_50']}; il massimo raggiunto dopo l'entrata, in mediana, {pc(x['massimo_mediano'])}. Le 5 migliori: "
                  + ", ".join(f"{m['simbolo'][:-4]} {m['data']} {pc(m['r'])}" for m in x["migliori"]) + ".",
                  "* Per ordine nel giorno: " + ", ".join(f"n. {k}{'+' if k == 4 else ''} {pc(v['media'])} ({v['n']}, vinte {100 * v['vinte']:.0f}%)"
                                                          for k, v in x["per_ordine"].items()) + ".",
                  f"* Il caso (entrate a minuti presi a caso negli stessi giorni-moneta): {x['caso']['operazioni']} operazioni, {pc(x['caso']['media'])}.",
                  f"* Il conto con l'1% a operazione: alla fine {x['conto_1pc'].get('finale', float('nan')):.2f} volte, discesa peggiore "
                  f"{pc(x['conto_1pc'].get('discesa_peggiore'))}.", ""]
    righe += [f"**Esito (2021-2022): {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {soglia:.5f})."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_QUARANTADUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTADUESIMA FINITA", flush=True)
