"""Programma 7, trentaseiesima prova (TRENTASEIESIMA.md): G23, la deriva del Bitcoin dopo il dato dell'inflazione americana (8:30 di
New York): la stessa regola della prova 96 (segno della candela che contiene il dato, 6 ore dopo), 69 pubblicazioni dal 2021.

Uso: python3 -m research.programma7.trentaseiesima
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma7 import trentaquattresima as g22

QUI = Path(__file__).parent
RIS = QUI / "risultati_trentaseiesima"
PUBBLICAZIONI = ["2021-02-10", "2021-03-10", "2021-04-13", "2021-05-12", "2021-06-10", "2021-07-13", "2021-08-11", "2021-09-14", "2021-10-13",
                 "2021-11-10", "2021-12-10", "2022-01-12", "2022-02-10", "2022-03-10", "2022-04-12", "2022-05-11", "2022-06-10", "2022-07-13",
                 "2022-08-10", "2022-09-13", "2022-10-13", "2022-11-10", "2022-12-13", "2023-01-12", "2023-02-14", "2023-03-14", "2023-04-12",
                 "2023-05-10", "2023-06-13", "2023-07-12", "2023-08-10", "2023-09-13", "2023-10-12", "2023-11-14", "2023-12-12", "2024-01-11",
                 "2024-02-13", "2024-03-12", "2024-04-10", "2024-05-15", "2024-06-12", "2024-07-11", "2024-08-14", "2024-09-11", "2024-10-10",
                 "2024-11-13", "2024-12-11", "2025-01-15", "2025-02-12", "2025-03-12", "2025-04-10", "2025-05-13", "2025-06-11", "2025-07-15",
                 "2025-08-12", "2025-09-11", "2025-10-24", "2025-12-18", "2026-01-13", "2026-02-13", "2026-03-11", "2026-04-10", "2026-05-12",
                 "2026-06-10", "2026-07-14", "2026-08-12", "2026-09-11", "2026-10-14"]
ORA_NY = 8
PROVE_A_EVENTI = 27


def esegui(log=print) -> dict:
    c = es.ore_di("BTCUSDT")
    costo = float(sc.costi_moneta(["BTCUSDT"])[0])
    fine = sc.giorno(2026, 10, 5)
    eventi = [d for d in PUBBLICAZIONI if sc.giorno(*map(int, d.split("-"))) <= fine]
    righe = []
    for d in eventi:
        h = g22.ora_utc(d, ORA_NY)
        op = g22.operazione(c, h, costo)
        if op:
            righe.append({"data": d, "ora_utc": h % 24, **op})
    ev = pd.DataFrame(righe)
    RIS.mkdir(exist_ok=True)
    ev.to_csv(RIS / "eventi_G23.csv", index=False)
    b = g22.bootstrap(ev["r"].to_numpy())
    meta1, meta2 = ev[ev["data"] < "2024"], ev[ev["data"] >= "2024"]
    insieme = set(PUBBLICAZIONI)
    contr = []
    for g in range(sc.giorno(2021, 1, 4), fine + 1):
        data = sc.data(g)
        if data in insieme or dt.date.fromisoformat(data).weekday() >= 5:
            continue
        op = g22.operazione(c, g22.ora_utc(data, ORA_NY), costo)
        if op:
            contr.append(op["r"])
    contr = np.asarray(contr)
    rng = np.random.default_rng(g22.SEME)
    medie_caso = np.array([rng.choice(contr, size=len(ev), replace=False).mean() for _ in range(g22.ESTRAZIONI)])
    forma = {}
    for k in range(-3, 13):
        vals = []
        for d in eventi:
            h = g22.ora_utc(d, ORA_NY)
            if h + k in c.index and h in c.index:
                segno = np.sign(c.loc[h, "close"] - c.loc[h, "open"])
                r = c.loc[h + k, "close"] / c.loc[h + k, "open"] - 1
                vals.append(float(segno * r) if k > 0 else float(r))
        forma[str(k)] = float(np.mean(vals)) if vals else None
    out = {"operazioni": b, "vinte": float((ev["r"] > 0).mean()), "prima_meta": float(meta1["r"].mean()), "seconda_meta": float(meta2["r"].mean()),
           "per_anno": {a: float(x["r"].mean()) for a, x in ev.groupby(ev["data"].str[:4])},
           "controllo": {"giorni": int(len(contr)), "media": float(contr.mean()), "quota_caso_almeno_come_eventi": float((medie_caso >= b["media"]).mean())},
           "forma_oraria_firmata": forma, "contraria_media": float(-ev["r"].mean() - 4 * costo), "costo_per_lato": costo, "soglia_tutte": 0.01 / PROVE_A_EVENTI}
    valida = b["p"] <= 0.01 and b["media"] > 0 and out["prima_meta"] > 0 and out["seconda_meta"] > 0
    out["esito"] = ("VALIDA" if valida and b["p"] <= out["soglia_tutte"] else
                    "passa l'esame scritto ma non la soglia di tutte le prove a eventi" if valida else "non passa")
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None else f"{100 * v:+.2f}%"  # noqa: E731
    co = out["controllo"]
    righe_t = ["# Programma 7 — risultati della trentaseiesima prova (G23: la deriva del Bitcoin dopo il dato dell'inflazione)", "",
               "Regole in `TRENTASEIESIMA.md` (scritte prima). Candele orarie del perpetuo BTCUSDT.", "",
               f"* **{b['eventi']} pubblicazioni: {pc(b['media'])} a operazione** (intervallo {pc(b['basso'])}; {pc(b['alto'])}, p {b['p']:.3f}), vinte "
               f"{100 * out['vinte']:.0f}%; 2021-2023 {pc(out['prima_meta'])}, 2024-2026 {pc(out['seconda_meta'])}; costo per lato {100 * costo:.3f}%.",
               "* Per anno: " + ", ".join(f"{a} {pc(v)}" for a, v in out["per_anno"].items()) + ".",
               f"* Controllo: {co['giorni']} giorni feriali senza dato alla stessa ora, media {pc(co['media'])}; in {100 * co['quota_caso_almeno_come_eventi']:.0f}% "
               f"delle {g22.ESTRAZIONI} estrazioni di {b['eventi']} giorni a caso la media è almeno quella delle pubblicazioni.",
               "* Forma della reazione (media oraria, dopo il dato firmata con il segno della candela del dato): " + ", ".join(f"{k}h {pc(v)}" for k, v in forma.items()) + ".",
               f"* La versione contraria (per leggere): {pc(out['contraria_media'])}.", "",
               f"**Esito: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {out['soglia_tutte']:.5f})."]
    testo = "\n".join(righe_t) + "\n"
    (QUI / "RISULTATI_TRENTASEIESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("TRENTASEIESIMA FINITA", flush=True)
