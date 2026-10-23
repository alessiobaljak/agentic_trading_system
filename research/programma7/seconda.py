"""Programma 7, seconda prova (SECONDA.md): G2, lo short in giornata delle monete con il funding dei 7 giorni piu' alto.

Uso: python3 -m research.programma7.seconda
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import esecuzione as es
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6.motore import MAKER
from research.programma7 import prima as pr

QUI = Path(__file__).parent
RIS = QUI / "risultati_seconda"
QUOTA, STOP_MIN, MULTIPLO, RISCHIO, TETTO = 0.20, 0.002, 2.0, 0.005, 0.20
ULTIMA_CHIUSURA = 20          # l'ultima candela d'entrata chiude alle 20:00 (parte alle 19:00)
REGOLAMENTI = (8, 16)


def operazione(o: np.ndarray, h: np.ndarray, l: np.ndarray, c: np.ndarray, a_mercato: float, funding_giorno: float,
               verso: int = -1):
    """Lo short (``verso`` -1, G2) o il long (+1, G3, lo specchio) di una moneta in un giorno, dalle 25 candele da 1 ora dalle
    00:00 alle 00:00 del giorno dopo (l'ultima serve solo per l'apertura). None se non c'e' entrata. Restituisce un dict con R
    lordo, costi e funding in R e il motivo."""
    apertura = o[0]
    for k in range(ULTIMA_CHIUSURA):
        if (c[k] < apertura) if verso < 0 else (c[k] > apertura):
            break
    else:
        return None
    e_ora = k + 1
    entrata = o[e_ora]
    if verso < 0:
        stop = max(float(h[:e_ora].max()), entrata * (1 + STOP_MIN))
    else:
        stop = min(float(l[:e_ora].min()), entrata * (1 - STOP_MIN))
    rischio = abs(stop - entrata)
    obiettivo = entrata + verso * MULTIPLO * rischio
    uscita, motivo, x_ora, costo_uscita = o[24], "tempo", 24, a_mercato
    for j in range(e_ora, 24):
        if (h[j] >= stop) if verso < 0 else (l[j] <= stop):
            uscita, motivo, x_ora, costo_uscita = (max(stop, o[j]) if verso < 0 else min(stop, o[j])), "stop", j, a_mercato
            break
        if (l[j] <= obiettivo) if verso < 0 else (h[j] >= obiettivo):
            uscita, motivo, x_ora, costo_uscita = obiettivo, "obiettivo", j, MAKER
            break
    regolamenti = sum(1 for s in REGOLAMENTI if e_ora <= s < x_ora)
    return {"entrata_ora": e_ora, "uscita_ora": x_ora, "motivo": motivo, "entrata": float(entrata), "stop": float(stop),
            "R_lordo": float(verso * (uscita - entrata) / rischio),
            "costo_R": float((a_mercato * entrata + costo_uscita * uscita) / rischio),
            # chi e' short incassa il funding positivo, chi e' long lo paga
            "funding_R": float(-verso * regolamenti * funding_giorno / 3 * entrata / rischio),
            "rischio_quota": float(min(RISCHIO, TETTO * rischio / entrata))}


def candidate_del_giorno(f7: np.ndarray, U: np.ndarray, sig: np.ndarray, verso: int = -1) -> np.ndarray:
    """(giorni × monete) le monete nel 20% con il funding dei 7 giorni piu' alto (``verso`` -1, gli short di F5) o piu' basso
    (+1, i long di F5) fra quelle dell'universo con la volatilita'."""
    out = np.zeros_like(U, dtype=bool)
    for d in range(U.shape[0]):
        idx = np.flatnonzero(U[d] & np.isfinite(f7[d]) & np.isfinite(sig[d]) & (sig[d] > 0))
        if len(idx) < te.MIN_MONETE:
            continue
        p = pd.Series(-f7[d, idx]).rank(pct=True).to_numpy()      # come F5: rango di −funding, short se ≤ 20%, long se > 80%
        out[d, idx[(p <= QUOTA) if verso < 0 else (p > 1 - QUOTA)]] = True
    return out


def bootstrap_p(per_giorno_R: np.ndarray, per_giorno_n: np.ndarray, volte: int = 5000, seme: int = 58) -> float:
    rng = np.random.default_rng(seme)
    medie = np.empty(volte)
    for b in range(volte):
        i = rng.integers(0, len(per_giorno_R), len(per_giorno_R))
        medie[b] = per_giorno_R[i].sum() / per_giorno_n[i].sum()
    return float((medie <= 0).mean())


def esegui(log=print, verso: int = -1, nome: str = "G2", numero: str = "58", ris: Path = RIS,
           file_risultati: str = "RISULTATI_SECONDA.md", titolo: str = "seconda prova (G2: short in giornata sulla leva più cara)",
           regole: str = "SECONDA.md") -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    cand = candidate_del_giorno(se.funding_7(pan, idx), Ud, sig, verso)
    costo = sc.costi_moneta(pan["simboli"])
    fund = np.nan_to_num(pan["funding"][idx])
    righe = []
    for j in np.flatnonzero(cand.any(axis=0)):
        b = es.ore_di(pan["simboli"][j])
        if b.empty:
            continue
        for d in np.flatnonzero(cand[:, j]):
            ore = np.arange(int(giorni[d]) * 24, int(giorni[d]) * 24 + 25)
            if not np.isin(ore, b.index).all():
                continue
            x = b.loc[ore, ["open", "high", "low", "close"]].to_numpy(float)
            if not np.isfinite(x).all():
                continue
            r = operazione(x[:, 0], x[:, 1], x[:, 2], x[:, 3], float(costo[j]), float(fund[d, j]), verso)
            if r is not None:
                righe.append({"giorno": int(giorni[d]), "simbolo": pan["simboli"][j]} | r)
    op = pd.DataFrame(righe)
    op["R"] = op["R_lordo"] - op["costo_R"] + op["funding_R"]
    ris.mkdir(exist_ok=True)
    op.to_csv(ris / f"operazioni_{nome}.csv.gz", index=False)
    # per operazione
    pg = op.groupby("giorno").agg(R=("R", "sum"), n=("R", "size"))
    meta = int(np.median(op["giorno"]))
    migliori = pg["R"].nlargest(5).index
    e = {"operazioni": int(len(op)), "giorni_con_operazioni": int(len(pg)), "giorni": int(len(giorni)),
         "al_giorno": float(len(op) / len(giorni)), "media_R": float(op["R"].mean()), "media_R_lorda": float(op["R_lordo"].mean()),
         "costo_R": float(op["costo_R"].mean()), "funding_R": float(op["funding_R"].mean()),
         "vinte": float((op["R"] > 0).mean()), "vincita_media": float(op.loc[op["R"] > 0, "R"].mean()),
         "perdita_media": float(op.loc[op["R"] <= 0, "R"].mean()),
         "p": bootstrap_p(pg["R"].to_numpy(), pg["n"].to_numpy()),
         "prima_meta": float(op.loc[op["giorno"] < meta, "R"].mean()), "seconda_meta": float(op.loc[op["giorno"] >= meta, "R"].mean()),
         "senza_5_migliori": float(op.loc[~op["giorno"].isin(migliori), "R"].mean()),
         "motivi": op["motivo"].value_counts(normalize=True).round(3).to_dict(),
         "per_anno_R": {int(a): float(v) for a, v in op.groupby(pd.to_datetime(op["giorno"] * 86400, unit="s").dt.year)["R"].mean().items()}}
    # come portafoglio: il risultato di ogni operazione con il suo rischio, sommato per giorno e poi per settimana
    op["netto"] = op["R"] * op["rischio_quota"]
    op["lordo"] = op["R_lordo"] * op["rischio_quota"]
    op["spese"] = op["costo_R"] * op["rischio_quota"]
    op["funding"] = -op["funding_R"] * op["rischio_quota"]
    op["giro"] = 2 * op["rischio_quota"] * op["entrata"] / (op["stop"] - op["entrata"]).abs()
    gd = op.groupby("giorno")[["netto", "lordo", "spese", "funding", "giro"]].sum().reindex(giorni, fill_value=0.0)
    gd["netto_doppio"] = gd["lordo"] - 2 * gd["spese"] - gd["funding"]
    gd["long"], gd["short"] = (0.0, gd["netto"]) if verso < 0 else (gd["netto"], 0.0)
    gd["monete"] = op.groupby("giorno").size().reindex(giorni, fill_value=0)
    sett = pr.per_settimana(gd.reset_index(drop=True), giorni)
    sett.to_csv(ris / f"settimane_{nome}.csv.gz")
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    ex = te.esame(sett, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    chiave = f"{numero} {nome}"
    nuove = {**ast.serie_nuove(), chiave: sett["netto"]}
    if verso > 0 and (RIS / "settimane_G2.csv.gz").exists():
        nuove["58 G2"] = pd.read_csv(RIS / "settimane_G2.csv.gz", index_col=0)["netto"]
    rivisto = ast.corretto_rivisto(nuove, {chiave: ex["intero"]})
    r = rivisto["candidate"][chiave]
    ex["sharpe_corretto"], ex["t"], ex["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    ex["esito"] = te.esito(ex, ex["sharpe_corretto"])
    passa_op = e["media_R"] > 0 and e["p"] <= 0.01 and e["prima_meta"] > 0 and e["seconda_meta"] > 0 and e["senza_5_migliori"] > 0
    out = {"operazioni": e, "portafoglio": ex, "passa_per_operazione": bool(passa_op)}
    (ris / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i = ex["intero"]
    testo = "\n".join([
        f"# Programma 7 — risultati della {titolo}", "",
        f"Regole in `{regole}` (scritte prima).", "",
        f"* Operazioni: {e['operazioni']} in {e['giorni_con_operazioni']} giorni su {e['giorni']} ({e['al_giorno']:.1f} al giorno).",
        f"* A operazione: **{e['media_R']:+.3f} R** (prima dei costi {e['media_R_lorda']:+.3f}, costi {e['costo_R']:.3f}, funding "
        f"{e['funding_R']:+.3f}); vinte {100 * e['vinte']:.0f}%, vincita media {e['vincita_media']:+.2f} R, perdita media "
        f"{e['perdita_media']:+.2f} R; p {e['p']:.4f}.",
        f"* Metà del periodo: {e['prima_meta']:+.3f} e {e['seconda_meta']:+.3f} R; senza i 5 giorni migliori {e['senza_5_migliori']:+.3f} R.",
        "* Uscite: " + ", ".join(f"{k} {100 * v:.0f}%" for k, v in e["motivi"].items()) + ".",
        "* Per anno (R a operazione): " + ", ".join(f"{a} {v:+.3f}" for a, v in e["per_anno_R"].items()) + ".",
        f"* Come portafoglio (0,5% di rischio a operazione): Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, volatilità "
        f"{100 * i['volatilita']:.1f}%, discesa {100 * i['discesa_max']:.1f}%; Sharpe corretto {ex['sharpe_corretto']:.2f} "
        f"({ex['gruppi']} gruppi), t {ex['t']:.2f}.", "",
        f"**Esito per operazione: {'passa' if passa_op else 'non passa'}** (media sopra zero con p ≤ 0,01, due metà positive, senza i 5 "
        f"giorni migliori positiva). **Come portafoglio: {ex['esito']}**"]) + "\n"
    (QUI / file_risultati).write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SECONDA FINITA", flush=True)
