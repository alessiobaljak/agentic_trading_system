"""Programma 7, trentaquattresima prova (TRENTAQUATTRESIMA.md): G22, la deriva del Bitcoin dopo il comunicato della Fed: il segno
dell'ora del comunicato (14:00 di New York) seguito dall'apertura dell'ora dopo per 6 ore; controllo sui giorni feriali senza riunione.

Uso: python3 -m research.programma7.trentaquattresima
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentaquattresima"
RIUNIONI = ["2021-01-27", "2021-03-17", "2021-04-28", "2021-06-16", "2021-07-28", "2021-09-22", "2021-11-03", "2021-12-15",
            "2022-01-26", "2022-03-16", "2022-05-04", "2022-06-15", "2022-07-27", "2022-09-21", "2022-11-02", "2022-12-14",
            "2023-02-01", "2023-03-22", "2023-05-03", "2023-06-14", "2023-07-26", "2023-09-20", "2023-11-01", "2023-12-13",
            "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12", "2024-07-31", "2024-09-18", "2024-11-07", "2024-12-18",
            "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18", "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10",
            "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17", "2026-07-29", "2026-09-16"]
ORA_NY = 14
TENUTA = 6
PROVE_A_EVENTI = 26
ESTRAZIONI, SEME = 2000, 2026
NY = ZoneInfo("America/New_York")


def ora_utc(data: str, ora_ny: int = ORA_NY) -> int:
    """L'ora (dal 1970) in UTC delle ``ora_ny`` di New York del giorno ``data``."""
    a, m, g = map(int, data.split("-"))
    t = dt.datetime(a, m, g, ora_ny, tzinfo=NY).astimezone(dt.timezone.utc)
    return int(t.timestamp()) // 3600


def operazione(c: pd.DataFrame, h: int, costo: float, tenuta: int = TENUTA) -> dict | None:
    """Segno della candela h, entrata all'apertura di h+1, uscita all'apertura di h+1+tenuta; None se mancano le candele."""
    serve = [h, h + 1, h + 1 + tenuta]
    if any(k not in c.index for k in serve):
        return None
    segno = np.sign(c.loc[h, "close"] - c.loc[h, "open"])
    if segno == 0:
        return None
    r = segno * (c.loc[h + 1 + tenuta, "open"] / c.loc[h + 1, "open"] - 1) - 2 * costo
    return {"segno": int(segno), "prima_ora": float(c.loc[h, "close"] / c.loc[h, "open"] - 1), "r": float(r)}


def bootstrap(x: np.ndarray, n: int = 10000, seme: int = SEME) -> dict:
    rng = np.random.default_rng(seme)
    medie = rng.choice(x, size=(n, len(x)), replace=True).mean(axis=1)
    return {"eventi": int(len(x)), "media": float(x.mean()), "basso": float(np.quantile(medie, 0.025)), "alto": float(np.quantile(medie, 0.975)),
            "p": float((medie <= 0).mean())}


def esegui(log=print) -> dict:
    c = es.ore_di("BTCUSDT")
    costo = float(sc.costi_moneta(["BTCUSDT"])[0])
    fine = sc.giorno(2026, 10, 5)
    righe = []
    for d in RIUNIONI:
        h = ora_utc(d)
        op = operazione(c, h, costo)
        if op:
            righe.append({"data": d, "ora_utc": h % 24, **op})
    ev = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    ev.to_csv(RIS / "eventi_G22.csv", index=False)
    b = bootstrap(ev["r"].to_numpy())
    meta1, meta2 = ev[ev["data"] < "2024"], ev[ev["data"] >= "2024"]
    # il controllo: tutti i giorni feriali senza riunione, stessa ora di New York
    riunioni = set(RIUNIONI)
    g0, g1 = sc.giorno(2021, 1, 4), fine
    contr = []
    for g in range(g0, g1 + 1):
        data = sc.data(g)
        if data in riunioni or dt.date.fromisoformat(data).weekday() >= 5:
            continue
        op = operazione(c, ora_utc(data), costo)
        if op:
            contr.append(op["r"])
    contr = np.asarray(contr)
    rng = np.random.default_rng(SEME)
    medie_caso = (np.array([rng.choice(contr, size=len(ev), replace=len(contr) < len(ev)).mean() for _ in range(ESTRAZIONI)])
                  if len(contr) else np.array([]))
    # descrittivo: la forma della reazione, ora per ora, firmata con il segno della prima ora
    forma = {}
    for k in range(-3, 13):
        vals = []
        for d in RIUNIONI:
            h = ora_utc(d)
            if h + k in c.index and h in c.index:
                segno = np.sign(c.loc[h, "close"] - c.loc[h, "open"])
                r = c.loc[h + k, "close"] / c.loc[h + k, "open"] - 1
                vals.append(float(segno * r) if k > 0 else float(r))
        forma[str(k)] = float(np.mean(vals)) if vals else None
    out = {"operazioni": b, "vinte": float((ev["r"] > 0).mean()), "prima_meta": float(meta1["r"].mean()) if len(meta1) else None,
           "seconda_meta": float(meta2["r"].mean()) if len(meta2) else None,
           "per_anno": {a: float(x["r"].mean()) for a, x in ev.groupby(ev["data"].str[:4])},
           "controllo": {"giorni": int(len(contr)), "media": float(contr.mean()) if len(contr) else None,
                         "quota_caso_almeno_come_riunioni": float((medie_caso >= b["media"]).mean()) if len(medie_caso) else None},
           "forma_oraria_firmata": forma, "contraria_media": float(-ev["r"].mean() - 4 * costo), "costo_per_lato": costo,
           "soglia_tutte": 0.01 / PROVE_A_EVENTI}
    valida = b["p"] <= 0.01 and b["media"] > 0 and (out["prima_meta"] or 0) > 0 and (out["seconda_meta"] or 0) > 0
    out["esito"] = ("VALIDA" if valida and b["p"] <= out["soglia_tutte"] else
                    "passa l'esame scritto ma non la soglia di tutte le prove a eventi" if valida else "non passa")
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None else f"{100 * v:+.2f}%"  # noqa: E731
    co = out["controllo"]
    righe_t = ["# Programma 7 — risultati della trentaquattresima prova (G22: la deriva del Bitcoin dopo la Fed)", "",
               "Regole in `TRENTAQUATTRESIMA.md` (scritte prima). Candele orarie del perpetuo BTCUSDT.", "",
               f"* **{b['eventi']} riunioni: {pc(b['media'])} a operazione** (intervallo {pc(b['basso'])}; {pc(b['alto'])}, p {b['p']:.3f}), vinte "
               f"{100 * out['vinte']:.0f}%; 2021-2023 {pc(out['prima_meta'])}, 2024-2026 {pc(out['seconda_meta'])}; costo per lato {100 * costo:.3f}%.",
               "* Per anno: " + ", ".join(f"{a} {pc(v)}" for a, v in out["per_anno"].items()) + ".",
               f"* Controllo: {co['giorni']} giorni feriali senza riunione alla stessa ora, media {pc(co['media'])}; in {100 * (co['quota_caso_almeno_come_riunioni'] or 0):.0f}% "
               f"delle {ESTRAZIONI} estrazioni di {b['eventi']} giorni a caso la media è almeno quella delle riunioni.",
               "* Forma della reazione (media oraria, dopo il comunicato firmata con il segno della prima ora): "
               + ", ".join(f"{k}h {pc(v)}" for k, v in forma.items()) + ".",
               f"* La versione contraria (per leggere): {pc(out['contraria_media'])}.", "",
               f"**Esito: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {out['soglia_tutte']:.5f})."]
    testo = "\n".join(righe_t) + "\n"
    (QUI / "RISULTATI_TRENTAQUATTRESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTAQUATTRESIMA FINITA", flush=True)
