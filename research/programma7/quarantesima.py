"""Programma 7, quarantesima prova (QUARANTESIMA.md): G25, il momento in giornata: il rendimento delle prime 23 ore (00:00-23:00 UTC)
decide la direzione dell'ultima ora (23:00-24:00), su 14 monete grandi; controllo con il segno a caso.

Uso: python3 -m research.programma7.quarantesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma7 import prima as pr

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarantesima"
MONETE = ["BTCUSDT", "ETHUSDT", "BCHUSDT", "LTCUSDT", "XRPUSDT", "LINKUSDT", "TRXUSDT", "ADAUSDT", "BNBUSDT", "DOGEUSDT", "DOTUSDT",
          "AVAXUSDT", "UNIUSDT", "SOLUSDT"]
INIZIO = sc.giorno(2021, 1, 4)
FINE = sc.giorno(2026, 10, 4)
ESTRAZIONI, SEME = 2000, 2026


def operazioni_moneta(c: pd.DataFrame, costo: float, giorni: np.ndarray) -> pd.DataFrame:
    """Per ogni giorno: segnale (00:00 → chiusura delle 22:00), lordo dell'ultima ora firmato, netto; NaN dove mancano le candele."""
    o, cl = c["open"], c["close"]
    righe = []
    for d in giorni:
        h0, h22, h23, h24 = 24 * d, 24 * d + 22, 24 * d + 23, 24 * (d + 1)
        if h0 not in o.index or h22 not in cl.index or h23 not in o.index:
            continue
        uscita = o.get(h24, np.nan)
        if not np.isfinite(uscita):
            uscita = cl.get(h23, np.nan)
        if not np.isfinite(uscita):
            continue
        seg = cl[h22] / o[h0] - 1
        ultima = uscita / o[h23] - 1
        if not np.isfinite(seg) or not np.isfinite(ultima) or seg == 0:
            continue
        s = float(np.sign(seg))
        righe.append({"giorno": int(d), "segnale": float(seg), "ultima": float(ultima), "lordo": s * float(ultima), "netto": s * float(ultima) - 2 * costo})
    return pd.DataFrame(righe)


def bootstrap_giorni(x: pd.Series, n: int = 10000, seme: int = SEME) -> dict:
    """Bootstrap per giorni (le operazioni dello stesso giorno restano insieme): la media per operazione."""
    gruppi = x.groupby(level=0)
    somme, conte = gruppi.sum().to_numpy(), gruppi.count().to_numpy()
    rng = np.random.default_rng(seme)
    idx = rng.integers(0, len(somme), size=(n, len(somme)))
    medie = somme[idx].sum(axis=1) / conte[idx].sum(axis=1)
    return {"operazioni": int(conte.sum()), "giorni": int(len(somme)), "media": float(somme.sum() / conte.sum()),
            "basso": float(np.quantile(medie, 0.025)), "alto": float(np.quantile(medie, 0.975)), "p": float((medie <= 0).mean())}


def esegui(log=print) -> dict:
    giorni = np.arange(INIZIO, FINE + 1, dtype=np.int64)
    costi = dict(zip(MONETE, sc.costi_moneta(MONETE)))
    tutte = []
    for s in MONETE:
        df = operazioni_moneta(es.ore_di(s), float(costi[s]), giorni)
        df["simbolo"] = s
        tutte.append(df)
        log(f"[quarantesima] {s}: {len(df)} giorni")
    op = pd.concat(tutte, ignore_index=True)
    RIS.mkdir(exist_ok=True)
    op.to_csv(RIS / "operazioni_G25.csv.gz", index=False)
    netto = op.set_index("giorno")["netto"]
    lordo = op.set_index("giorno")["lordo"]
    b, bl = bootstrap_giorni(netto), bootstrap_giorni(lordo)
    anno = op["giorno"].map(lambda g: sc.data(int(g))[:4])
    m1, m2 = op[anno <= "2023"], op[anno >= "2024"]
    # portafoglio: ogni giorno le operazioni con peso 1/14
    gior = (op.groupby("giorno")["netto"].sum() / len(MONETE)).reindex(giorni, fill_value=0.0)
    d = pd.DataFrame({"lordo": (op.groupby("giorno")["lordo"].sum() / len(MONETE)).reindex(giorni, fill_value=0.0),
                      "spese": (op.groupby("giorno").apply(lambda x: (x["lordo"] - x["netto"]).sum()) / len(MONETE)).reindex(giorni, fill_value=0.0),
                      "funding": 0.0, "netto": gior})
    d["netto_doppio"] = d["lordo"] - 2 * d["spese"]
    d["giro"] = (op.groupby("giorno").size() * 2 / len(MONETE)).reindex(giorni, fill_value=0.0)
    d["long"] = 0.0
    d["short"] = 0.0
    d["monete"] = op.groupby("giorno").size().reindex(giorni, fill_value=0).astype(int)
    sett = pr.per_settimana(d, giorni)
    sett.to_csv(RIS / "settimane_G25.csv.gz")
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    ex = te.esame(sett, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    # il controllo: il segno a caso
    rng = np.random.default_rng(SEME)
    ult = op["ultima"].to_numpy()
    cst = (op["lordo"] - op["netto"]).to_numpy()
    medie_caso = np.array([(rng.choice([-1.0, 1.0], size=len(ult)) * ult - cst).mean() for _ in range(ESTRAZIONI)])
    out = {"netto": b, "lordo": bl, "prima_meta": float(m1["netto"].mean()), "seconda_meta": float(m2["netto"].mean()),
           "per_anno": {a: {"netto": float(x["netto"].mean()), "lordo": float(x["lordo"].mean())} for a, x in op.groupby(anno)},
           "per_moneta": {s: {"n": int(len(x)), "lordo": float(x["lordo"].mean()), "netto": float(x["netto"].mean())} for s, x in op.groupby("simbolo")},
           "vinte": float((op["netto"] > 0).mean()), "costo_medio_giro": float(cst.mean()),
           "caso": {"media": float(medie_caso.mean()), "quota_almeno_come_vero": float((medie_caso >= b["media"]).mean())},
           "portafoglio": ex}
    serie = {**ast.serie_nuove(), "102 G25": sett["netto"]}
    rivisto = ast.corretto_rivisto(serie, {"102 G25": ex["intero"]})
    r = rivisto["candidate"]["102 G25"]
    ex["sharpe_corretto"], ex["t"], ex["gruppi"] = r["corretto_con_aggiunta"], r["t"], rivisto["gruppi"]
    ex["esito"] = te.esito(ex, ex["sharpe_corretto"])
    valida = b["p"] <= 0.01 and b["media"] > 0 and out["prima_meta"] > 0 and out["seconda_meta"] > 0
    out["esito"] = "VALIDA per operazione" if valida else "non passa"
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: f"{100 * v:+.3f}%"  # noqa: E731
    i = ex["intero"]
    righe = ["# Programma 7 — risultati della quarantesima prova (G25: il momento in giornata, le prime 23 ore decidono l'ultima)", "",
             "Regole in `QUARANTESIMA.md` (scritte prima). 14 monete, dal 4 gennaio 2021 al 4 ottobre 2026, un'operazione al giorno per moneta.", "",
             f"* **{b['operazioni']} operazioni in {b['giorni']} giorni: {pc(b['media'])} a operazione al netto** (intervallo {pc(b['basso'])}; "
             f"{pc(b['alto'])}, p {b['p']:.3f}); **al lordo {pc(bl['media'])}** (p {bl['p']:.3f}); costo medio di un giro {pc(out['costo_medio_giro'])}; "
             f"vinte {100 * out['vinte']:.0f}%; 2021-2023 {pc(out['prima_meta'])}, 2024-2026 {pc(out['seconda_meta'])}.",
             "* Per anno (netto / lordo): " + ", ".join(f"{a} {pc(v['netto'])} / {pc(v['lordo'])}" for a, v in out["per_anno"].items()) + ".",
             "* Per moneta (lordo): " + ", ".join(f"{s[:-4]} {pc(v['lordo'])}" for s, v in out["per_moneta"].items()) + ".",
             f"* Il segno a caso ({ESTRAZIONI} estrazioni): media {pc(out['caso']['media'])}; nel {100 * out['caso']['quota_almeno_come_vero']:.0f}% arriva almeno al segno vero.",
             f"* Portafoglio (1/14 a moneta): Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, discesa {100 * i['discesa_max']:.1f}%; Sharpe corretto "
             f"{ex['sharpe_corretto']:.2f} ({ex['gruppi']} gruppi), t {ex['t']:.2f}; esito {ex['esito']}.", "",
             f"**Esito: {out['esito']}.**"]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_QUARANTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTESIMA FINITA", flush=True)
