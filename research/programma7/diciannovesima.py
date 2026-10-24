"""Programma 7, diciannovesima prova (DICIANNOVESIMA.md): G17, il segnale della prova 75 senza protezione (obiettivo −5%, al
massimo 7 giorni) con l'1% del conto a operazione, sul 2023-2024.

Uso: python3 -m research.programma7.diciannovesima
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import trentesima as tr
from research.programma7 import diciottesima as g16
from research.trader_copiati.analisi_trader2 import minuti

QUI = Path(__file__).parent
RIS = QUI / "risultati_diciannovesima"
DA, A = sc.giorno(2023, 1, 1), sc.giorno(2024, 12, 31)
MAX_MIN = 7 * 1440
QUOTA, MAX_APERTE, DISCESA_MAX = 0.01, 50, 0.30
PROVE_A_EVENTI = 19


def conto(df: pd.DataFrame, quota: float) -> tuple:
    """Il conto con ``quota`` del capitale a operazione (al massimo 50 aperte): la serie settimanale (per la settimana di uscita) e
    la discesa peggiore, sommando i risultati nell'ordine delle uscite."""
    d = df.sort_values("entrata_min").reset_index(drop=True)
    aperte, tenute = [], []
    for k, x in d.iterrows():
        aperte = [u for u in aperte if u > x["entrata_min"]]
        if len(aperte) >= MAX_APERTE:
            continue
        aperte.append(x["uscita_min"])
        tenute.append(k)
    t = d.loc[tenute].sort_values("uscita_min")
    giorno = t["uscita_min"].to_numpy() // 1440
    lun = ((giorno + 3) // 7) * 7 - 3
    sett = pd.Series(quota * t["r"].to_numpy(), index=lun).groupby(level=0).sum()
    tutte = np.arange(((DA + 3) // 7) * 7 - 3, A + 14, 7)
    out = pd.DataFrame({"netto": sett.reindex(tutte).fillna(0.0)})
    out["netto_doppio"] = out["netto"]
    for c in ("lordo", "spese", "funding", "giro", "long", "short"):
        out[c] = 0.0
    out["monete"] = 1
    cum = 1 + np.cumsum(quota * t["r"].to_numpy())
    discesa = float((cum - np.maximum.accumulate(np.concatenate([[1.0], cum]))[1:]).min()) if len(cum) else 0.0
    return out, discesa, len(tenute)


def esegui(log=print) -> dict:
    g16.DA, g16.A = DA, A
    pan = sc.pannello()
    t0, simboli = pan["t0"], pan["simboli"]
    cand = g16.candidati(pan)
    log(f"[diciannovesima] {len(cand)} giorni-moneta candidati su {len({j for j, _ in cand})} monete")
    file = sorted({(simboli[j], k + t0 + d) for j, k in cand for d in range(-1, 9)})
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda x: minuti(x[0], sc.data(x[1])), file))
    costo = dict(zip(simboli, sc.costi_moneta(simboli)))
    per_moneta: dict = {}
    for j, k in cand:
        per_moneta.setdefault(j, set()).add(k)
    righe = []
    for j, giorni_k in sorted(per_moneta.items()):
        s = simboli[j]
        w = g16.blocco(s, sorted({k + t0 + d for k in giorni_k for d in range(-1, 9)}))
        if w.empty:
            continue
        ammessi = np.concatenate([np.arange((k + t0) * 1440, (k + t0 + 1) * 1440) for k in sorted(giorni_k)])
        libero_da = -1
        for t in g16.segnali(w, ammessi):
            if t < libero_da:
                continue
            op = g16.operazione(w, t, costo[s], protezione=False, max_min=MAX_MIN)
            if op is None:
                continue
            k = t // 1440 - t0
            f = float(np.nan_to_num(pan["funding"][k, j])) * op["minuti"] / 1440.0
            righe.append({"data": sc.data(t // 1440), "annuncio": int((t // 1440 + 3) // 7), "simbolo": s, "segnale_min": t,
                          **op, "funding": f, "r": op["r_prezzo"] - op["costi"] + f})
            libero_da = op["uscita_min"] + g16.PAUSA
    df = pd.DataFrame(righe).sort_values(["data", "segnale_min"]).reset_index(drop=True)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "eventi_G17.csv", index=False)
    ex_ = tr.esame(df, "r")
    sett, discesa, tenute = conto(df, QUOTA)
    sett2, discesa2, _ = conto(df, 2 * QUOTA)
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    inizio = int(sett.index.min())
    p = te.esame(sett, btc, inizio=inizio, anni_pieni=(2023, 2024))
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "76 G17": sett["netto"]}, {"76 G17": p["intero"]})
    rr = rivisto["candidate"]["76 G17"]
    p["sharpe_corretto"], p["t"], p["gruppi"] = rr["corretto_con_aggiunta"], rr["t"], rivisto["gruppi"]
    p["esito"] = te.esito(p, p["sharpe_corretto"])
    peggiore = float(df["r"].min()) if len(df) else 0.0
    out = {"eventi": ex_, "candidati": len(cand), "operazioni": len(df), "tenute_nel_conto": tenute, "monete": int(df["simbolo"].nunique()),
           "motivi": df["motivo"].value_counts(normalize=True).round(4).to_dict(), "minuti_mediana": float(df["minuti"].median()),
           "oltre_meno_100": int((df["r"] < -1).sum()), "peggiore": peggiore, "peggiori": df.nsmallest(5, "r")[["data", "simbolo", "r"]].to_dict("records"),
           "discesa_1": discesa, "discesa_2": discesa2, "fine_1": float(1 + QUOTA * df["r"].sum()),
           "fine_2": float(1 + 2 * QUOTA * df["r"].sum()), "soglia_tutte": 0.01 / PROVE_A_EVENTI, "portafoglio": p,
           "per_mese": {m: {"operazioni": int(len(g)), "media": float(g["r"].mean())} for m, g in df.groupby(df["data"].str[:7])}}
    passa_ev = ex_["esito"] == "VALIDA" and ex_["boot"]["p"] <= out["soglia_tutte"]
    out["esito"] = ("VALIDA" if passa_ev and p["esito"] == "VALIDA" and -discesa < DISCESA_MAX else
                    f"non valida (operazioni: {ex_['esito']}, p {ex_['boot']['p']:.4f}; conto: {p['esito']}; discesa {100 * discesa:.1f}%)")
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    b, i = ex_["boot"], p["intero"]
    testo = "\n".join([
        "# Programma 7 — risultati della diciannovesima prova (G17: le fiammate senza protezione, con l'1% a operazione, 2023-2024)", "",
        "Regole in `DICIANNOVESIMA.md` (scritte prima).", "",
        f"* {len(cand)} giorni-moneta candidati; **{len(df)} operazioni** su {out['monete']} monete; durata mediana "
        f"{out['minuti_mediana']:.0f} minuti; uscite: " + ", ".join(f"{k} {100 * v:.0f}%" for k, v in out["motivi"].items()) + ".",
        f"* **{100 * b['media']:+.2f}% a operazione** dopo i costi (intervallo {100 * b['basso']:+.2f}%; {100 * b['alto']:+.2f}%, p {b['p']:.4f}); "
        f"mediana {100 * ex_['mediana']:+.2f}%, vinte {100 * ex_['vinti']:.0f}%; metà {100 * ex_['prima_meta']:+.2f}% e "
        f"{100 * ex_['seconda_meta']:+.2f}%; senza le 5 migliori {100 * ex_['senza_5_migliori']:+.2f}%.",
        f"* Operazioni oltre −100%: {out['oltre_meno_100']}; la peggiore {100 * peggiore:+.0f}% (" +
        ", ".join(f"{x['simbolo']} {x['data']} {100 * x['r']:+.0f}%" for x in out["peggiori"]) + ").",
        "* Per anno: " + ", ".join(f"{a} {100 * v['media']:+.2f}% ({v['eventi']})" for a, v in ex_["per_anno"].items()) + ".",
        f"* **Il conto con l'1% a operazione**: alla fine {out['fine_1']:.2f} volte il conto, discesa peggiore {100 * discesa:.1f}% "
        f"(soglia 30%); Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno; Sharpe corretto {p['sharpe_corretto']:.2f} "
        f"({p['gruppi']} gruppi), t {p['t']:.2f}. Con il 2%: alla fine {out['fine_2']:.2f} volte, discesa {100 * discesa2:.1f}%.", "",
        f"**Esito: {out['esito']}**"]) + "\n"
    (QUI / "RISULTATI_DICIANNOVESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("DICIANNOVESIMA FINITA", flush=True)
