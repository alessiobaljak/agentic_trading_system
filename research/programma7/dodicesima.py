"""Programma 7, dodicesima prova (DODICESIMA.md): G10, il «buco» del CME sul Bitcoin.

Uso: python3 -m research.programma7.dodicesima
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from research.programma6 import esecuzione as es
from research.programma6 import seconda as sc
from research.programma6.motore import MAKER, TAKER

QUI = Path(__file__).parent
RIS = QUI / "risultati_dodicesima"
CHICAGO = ZoneInfo("America/Chicago")
BUCO_MIN, A_MERCATO = 0.01, TAKER + 0.0001
DA, A = datetime(2021, 1, 1, tzinfo=timezone.utc), datetime(2026, 10, 4, tzinfo=timezone.utc)
REGOLAMENTI = (0, 8, 16)


def ore_cme(venerdi_locale: datetime) -> tuple:
    """(ora UTC della chiusura del venerdi', ora UTC della riapertura della domenica) in ore dall'epoca, con l'ora legale di
    Chicago; ``venerdi_locale`` e' una data (il venerdi')."""
    chiusura = datetime(venerdi_locale.year, venerdi_locale.month, venerdi_locale.day, 16, tzinfo=CHICAGO)
    domenica = venerdi_locale + timedelta(days=2)
    riapertura = datetime(domenica.year, domenica.month, domenica.day, 17, tzinfo=CHICAGO)
    return int(chiusura.timestamp()) // 3600, int(riapertura.timestamp()) // 3600


def operazione(b: pd.DataFrame, h_c: int, h_r: int, h_fine: int, funding: pd.Series) -> dict | None:
    """Il trade di un fine settimana: None se mancano le candele o se il buco e' sotto l'1%."""
    ore = np.arange(h_r, h_fine + 1)
    if h_c not in b.index or not np.isin(ore, b.index).all():
        return None
    p_c, entrata = float(b.loc[h_c, "open"]), float(b.loc[h_r, "open"])
    buco = entrata / p_c - 1
    if abs(buco) < BUCO_MIN:
        return None
    verso = -1 if buco > 0 else 1                       # buco in su: short verso la chiusura del venerdi'
    obiettivo, rischio = p_c, abs(entrata - p_c)
    stop = entrata - verso * rischio
    x = b.loc[ore]
    uscita, motivo, x_ora, costo_u = float(x["open"].iloc[-1]), "tempo", h_fine, A_MERCATO
    for h in ore[:-1]:
        hi, lo, op = x.loc[h, "high"], x.loc[h, "low"], x.loc[h, "open"]
        if (hi >= stop) if verso < 0 else (lo <= stop):
            uscita, motivo, x_ora, costo_u = (max(stop, op) if verso < 0 else min(stop, op)), "stop", h, A_MERCATO
            break
        if (lo <= obiettivo) if verso < 0 else (hi >= obiettivo):
            uscita, motivo, x_ora, costo_u = obiettivo, "obiettivo", h, MAKER
            break
    attraversati = [h for h in range(h_r + 1, x_ora + 1) if h % 24 in REGOLAMENTI]
    fund = sum(float(funding.get(h // 24, 0.0)) / 3 for h in attraversati)
    return {"buco": float(buco), "verso": verso, "motivo": motivo, "ore": int(x_ora - h_r),
            "R_lordo": float(verso * (uscita - entrata) / rischio),
            "costo_R": float((A_MERCATO * entrata + costo_u * uscita) / rischio),
            "funding_R": float(-verso * fund * entrata / rischio)}


def esegui(log=print) -> dict:
    b = es.ore_di("BTCUSDT")
    pan = sc.pannello()
    jb = pan["simboli"].index("BTCUSDT")
    funding = pd.Series(pan["funding"][:, jb], index=np.arange(pan["close"].shape[0]) + pan["t0"])
    righe = []
    g = DA + timedelta(days=(4 - DA.weekday()) % 7)      # il primo venerdi'
    while g < A:
        h_c, h_r = ore_cme(g)
        h_fine, _ = ore_cme(g + timedelta(days=7))
        r = operazione(b, h_c, h_r, h_fine, funding)
        if r is not None:
            righe.append({"venerdi": g.date().isoformat()} | r)
        g += timedelta(days=7)
    op = pd.DataFrame(righe)
    op["R"] = op["R_lordo"] - op["costo_R"] + op["funding_R"]
    RIS.mkdir(exist_ok=True)
    op.to_csv(RIS / "operazioni_G10.csv", index=False)
    rng = np.random.default_rng(10)
    medie = np.array([op["R"].sample(len(op), replace=True, random_state=int(rng.integers(1 << 31))).mean() for _ in range(10000)])
    meta = len(op) // 2
    e = {"operazioni": int(len(op)), "fine_settimana": int(len(pd.date_range(DA, A, freq="W-FRI"))),
         "media_R": float(op["R"].mean()), "media_R_lorda": float(op["R_lordo"].mean()), "p": float((medie <= 0).mean()),
         "prima_meta": float(op["R"].iloc[:meta].mean()), "seconda_meta": float(op["R"].iloc[meta:].mean()),
         "senza_5_migliori": float(op["R"].sort_values(ascending=False).iloc[5:].mean()),
         "vinte": float((op["R"] > 0).mean()), "buchi_chiusi": float((op["motivo"] == "obiettivo").mean()),
         "motivi": op["motivo"].value_counts(normalize=True).round(3).to_dict(),
         "per_anno": {a: float(v) for a, v in op.groupby(op["venerdi"].str[:4])["R"].mean().items()}}
    e["esito"] = ("VALIDA" if e["media_R"] > 0 and e["p"] <= 0.01 and e["prima_meta"] > 0 and e["seconda_meta"] > 0
                  and e["senza_5_migliori"] > 0 else "non valida")
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    testo = "\n".join([
        "# Programma 7 — risultati della dodicesima prova (G10: il «buco» del CME sul Bitcoin)", "",
        "Regole in `DODICESIMA.md` (scritte prima).", "",
        f"* Fine settimana con un buco di almeno l'1%: {e['operazioni']} su {e['fine_settimana']}.",
        f"* Buchi chiusi (obiettivo raggiunto) entro la settimana: {100 * e['buchi_chiusi']:.0f}%; uscite: "
        + ", ".join(f"{k} {100 * v:.0f}%" for k, v in e["motivi"].items()) + ".",
        f"* A operazione: **{e['media_R']:+.3f} R** (prima dei costi {e['media_R_lorda']:+.3f}); vinte {100 * e['vinte']:.0f}%; p {e['p']:.4f}; "
        f"metà {e['prima_meta']:+.3f} e {e['seconda_meta']:+.3f}; senza le 5 migliori {e['senza_5_migliori']:+.3f}.",
        "* Per anno: " + ", ".join(f"{a} {v:+.3f} R" for a, v in e["per_anno"].items()) + ".", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_DODICESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("DODICESIMA FINITA", flush=True)
