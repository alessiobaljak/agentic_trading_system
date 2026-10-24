"""Programma 9, seconda prova (SECONDA.md): P9C, le fiammate della prova 75 da vendere solo quando i long sono affollati (funding
dell'ultimo regolamento almeno +0,01% per 8 ore), dal 27 giugno al 30 settembre 2026.

Uso: python3 -m research.programma9.seconda
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
from research.src.dati import funding_da_zip
from research.trader_copiati.analisi_trader2 import minuti

QUI = Path(__file__).parent
RIS = QUI / "risultati_seconda"
DA, A = sc.giorno(2026, 6, 27), sc.giorno(2026, 9, 30)
SOGLIA_8H = 0.0001
PROVE_A_EVENTI = 21


def regolamenti(simbolo: str) -> pd.DataFrame:
    """I regolamenti del funding (minuto, ore dell'intervallo, tasso) dai file mensili dell'archivio."""
    righe = []
    for p in sorted((sc.DATI / simbolo / "funding").glob("*.zip")):
        righe += funding_da_zip(p)
    if not righe:
        return pd.DataFrame(columns=["minuto", "ore", "tasso"])
    d = pd.DataFrame(righe, columns=["ts", "ore", "tasso"]).drop_duplicates("ts").sort_values("ts")
    d["minuto"] = d["ts"] // 60_000
    return d[["minuto", "ore", "tasso"]].reset_index(drop=True)


def funding_prima(reg: pd.DataFrame, t: int) -> float | None:
    """Il tasso dell'ultimo regolamento prima del minuto t, riportato a 8 ore (None se non c'e' o se e' di piu' di 9 ore prima)."""
    prima = reg[reg["minuto"] <= t]
    if prima.empty or t - int(prima["minuto"].iloc[-1]) > 9 * 60:
        return None
    x = prima.iloc[-1]
    ore = float(x["ore"]) if x["ore"] > 0 else 8.0
    return float(x["tasso"]) * 8.0 / ore


def esegui(log=print) -> dict:
    g16.DA, g16.A = DA, A
    pan = sc.pannello()
    t0, simboli = pan["t0"], pan["simboli"]
    cand = g16.candidati(pan)
    log(f"[p9 seconda] {len(cand)} giorni-moneta candidati su {len({j for j, _ in cand})} monete")
    file = sorted({(simboli[j], k + t0 + d) for j, k in cand for d in (-1, 0, 1)})
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: minuti(x[0], sc.data(x[1])), file))
    costo = dict(zip(simboli, sc.costi_moneta(simboli)))
    per_moneta: dict = {}
    for j, k in cand:
        per_moneta.setdefault(j, set()).add(k)
    righe = []
    for j, giorni_k in sorted(per_moneta.items()):
        s = simboli[j]
        w = g16.blocco(s, sorted({k + t0 + d for k in giorni_k for d in (-1, 0, 1)}))
        if w.empty:
            continue
        reg = regolamenti(s)
        ammessi = np.concatenate([np.arange((k + t0) * 1440, (k + t0 + 1) * 1440) for k in sorted(giorni_k)])
        libero_da = -1
        for t in g16.segnali(w, ammessi):
            if t < libero_da:
                continue
            op = g16.operazione(w, t, costo[s])
            if op is None:
                continue
            k = t // 1440 - t0
            f = float(np.nan_to_num(pan["funding"][k, j])) * op["minuti"] / 1440.0
            righe.append({"data": sc.data(t // 1440), "annuncio": int((t // 1440 + 3) // 7), "simbolo": s, "segnale_min": t,
                          **op, "funding": f, "r": op["r_prezzo"] - op["costi"] + f, "funding_8h": funding_prima(reg, t)})
            libero_da = op["uscita_min"] + g16.PAUSA
    df = pd.DataFrame(righe).sort_values(["data", "segnale_min"]).reset_index(drop=True)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_P9C.csv", index=False)
    noto = df["funding_8h"].notna()
    affollati = df[noto & (df["funding_8h"] >= SOGLIA_8H)]
    altri = df[noto & (df["funding_8h"] < SOGLIA_8H)]
    ex_ = tr.esame(affollati, "r") if len(affollati) > 10 else None

    def breve(d: pd.DataFrame) -> dict:
        return {"n": len(d), "media": float(d["r"].mean()) if len(d) else None, "vinte": float((d["r"] > 0).mean()) if len(d) else None,
                "protezione": float((d["motivo"] == "protezione").mean()) if len(d) else None,
                "oltre_meno_30": int((d["r_prezzo"] < -0.3).sum()) if len(d) else 0}

    out = {"candidati": len(cand), "operazioni": len(df), "senza_funding": int((~noto).sum()), "affollati": breve(affollati),
           "altri": breve(altri), "tutte": breve(df), "esame": ex_, "soglia_tutte": 0.01 / PROVE_A_EVENTI}
    if ex_ is None:
        out["esito"] = "troppo poche operazioni"
    elif ex_["esito"] == "VALIDA" and ex_["boot"]["p"] <= out["soglia_tutte"]:
        out["esito"] = "VALIDA"
    else:
        out["esito"] = ex_["esito"]
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    a, b, c = out["affollati"], out["altri"], out["tutte"]
    pct = lambda x: "—" if x is None else f"{100 * x:+.2f}%"  # noqa: E731
    righe_t = ["# Programma 9 — risultati della seconda prova (P9C: le fiammate con i long affollati)", "",
               "Regole in `SECONDA.md` (scritte prima). Dal 27 giugno al 30 settembre 2026, candele a 1 minuto e funding dell'archivio.", "",
               f"* {len(cand)} giorni-moneta candidati; {len(df)} operazioni della regola delle fiammate (senza il funding noto: {out['senza_funding']}).",
               f"* **Con i long affollati** (funding almeno +0,01% per 8 ore): {a['n']} operazioni, **{pct(a['media'])} a operazione**, vinte "
               f"{pct(a['vinte'])}, alla protezione {pct(a['protezione'])}, prezzo oltre −30%: {a['oltre_meno_30']}.",
               f"* Con il funding sotto la soglia: {b['n']} operazioni, {pct(b['media'])} a operazione, alla protezione {pct(b['protezione'])}, "
               f"oltre −30%: {b['oltre_meno_30']}.",
               f"* Tutte (la prova 75 su questi mesi): {c['n']} operazioni, {pct(c['media'])} a operazione."]
    if ex_:
        bb = ex_["boot"]
        righe_t.append(f"* Esame (long affollati): intervallo {pct(bb['basso'])}; {pct(bb['alto'])}, p {bb['p']:.4f}; metà "
                       f"{pct(ex_['prima_meta'])} e {pct(ex_['seconda_meta'])}; senza le 5 migliori {pct(ex_['senza_5_migliori'])}.")
    righe_t += ["", f"**Esito: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {out['soglia_tutte']:.5f})"
                + (" — meno di 100 operazioni: la prova dice poco." if a["n"] < 100 else "")]
    testo = "\n".join(righe_t) + "\n"
    (QUI / "RISULTATI_SECONDA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("P9C FINITA", flush=True)
