"""Programma 9, quarta prova (QUARTA.md): P9D, le 613 operazioni della regola delle monete nuove al 7° giorno (prova 32) divise per
il funding dell'ultimo regolamento prima dell'entrata.

Uso: python3 -m research.programma9.quarta
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import trentesima as tr
from research.programma9 import seconda as p9c

QUI = Path(__file__).parent
RIS = QUI / "risultati_quarta"
EVENTI = QUI.parent / "programma6" / "risultati_trentaduesima" / "eventi_N3B.csv"
PROVE_A_EVENTI = 23


def differenza(a: pd.DataFrame, b: pd.DataFrame, n: int = 10000, seme: int = 2026) -> dict:
    """La differenza fra le medie di a e b, con il bootstrap sulle settimane (le settimane si ricampionano dentro ciascuna parte)."""
    ga = [g["r"].to_numpy() for _, g in a.groupby("annuncio")]
    gb = [g["r"].to_numpy() for _, g in b.groupby("annuncio")]
    rng = np.random.default_rng(seme)
    d = np.empty(n)
    for k in range(n):
        xa = np.concatenate([ga[i] for i in rng.integers(0, len(ga), len(ga))])
        xb = np.concatenate([gb[i] for i in rng.integers(0, len(gb), len(gb))])
        d[k] = xa.mean() - xb.mean()
    return {"differenza": float(a["r"].mean() - b["r"].mean()), "basso": float(np.percentile(d, 2.5)),
            "alto": float(np.percentile(d, 97.5)), "p": float((np.sum(d <= 0) + 1) / (n + 1))}


def esegui(log=print) -> dict:
    ev = pd.read_csv(EVENTI)
    cache: dict = {}
    f8 = []
    for _, x in ev.iterrows():
        s = x["simbolo"]
        if s not in cache:
            cache[s] = p9c.regolamenti(s)
        e = sc.giorno(*map(int, x["data"].split("-")))
        f8.append(p9c.funding_prima(cache[s], e * 1440 - 1))
    ev["funding_8h"] = f8
    RIS.mkdir(exist_ok=True)
    ev.to_csv(RIS / "eventi_N3B_funding.csv", index=False)
    noto = ev["funding_8h"].notna()
    aff = ev[noto & (ev["funding_8h"] >= p9c.SOGLIA_8H)].reset_index(drop=True)
    alt = ev[noto & (ev["funding_8h"] < p9c.SOGLIA_8H)].reset_index(drop=True)
    ex_a, ex_b = tr.esame(aff, "r"), tr.esame(alt, "r")
    dif = differenza(aff, alt)
    per_anno = {}
    for anno in sorted(ev["data"].str[:4].unique()):
        a_, b_ = aff[aff["data"].str[:4] == anno], alt[alt["data"].str[:4] == anno]
        per_anno[anno] = {"affollati": (len(a_), float(a_["r"].mean()) if len(a_) else None),
                          "funding_basso": (len(b_), float(b_["r"].mean()) if len(b_) else None)}
    soglia = 0.01 / PROVE_A_EVENTI
    migliore = dif["p"] <= 0.05 and dif["differenza"] > 0
    esito = ("VALIDA e migliore di N3" if ex_a["esito"] == "VALIDA" and ex_a["boot"]["p"] <= soglia and migliore else
             f"non migliore di N3 (P9D: {ex_a['esito']}; differenza {100 * dif['differenza']:+.2f} punti, p {dif['p']:.3f})")
    out = {"eventi": len(ev), "senza_funding": int((~noto).sum()), "affollati": ex_a, "funding_basso": ex_b, "differenza": dif,
           "per_anno": per_anno, "esito": esito, "soglia_tutte": soglia,
           "uscite_affollati": float(aff["fermata"].mean()), "uscite_funding_basso": float(alt["fermata"].mean()),
           "funding_mediano": float(ev["funding_8h"].median())}
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda x: "—" if x is None else f"{100 * x:+.2f}%"  # noqa: E731
    a, b = ex_a["boot"], ex_b["boot"]
    righe = ["# Programma 9 — risultati della quarta prova (P9D: le monete nuove al 7° giorno divise per funding)", "",
             "Regole in `QUARTA.md` (scritte prima). Le 613 operazioni della prova 32 (Binance, dal 2021).", "",
             f"* Funding mediano all'entrata: {pc(out['funding_mediano'])} per 8 ore; senza il funding: {out['senza_funding']}.",
             f"* **Con i long affollati** (almeno +0,01% per 8 ore): {a['eventi']} operazioni, **{pc(a['media'])} a operazione** (p {a['p']:.4f}), "
             f"mediana {pc(ex_a['mediana'])}, vinte {100 * ex_a['vinti']:.0f}%, uscita a +30% nel {100 * out['uscite_affollati']:.0f}%; metà "
             f"{pc(ex_a['prima_meta'])} e {pc(ex_a['seconda_meta'])}; senza le 5 migliori {pc(ex_a['senza_5_migliori'])}.",
             f"* Con il funding sotto la soglia: {b['eventi']} operazioni, {pc(b['media'])} a operazione (p {b['p']:.4f}), uscita a +30% nel "
             f"{100 * out['uscite_funding_basso']:.0f}%.",
             f"* Differenza: {100 * dif['differenza']:+.2f} punti (intervallo {100 * dif['basso']:+.2f}; {100 * dif['alto']:+.2f}, p {dif['p']:.3f}).",
             "* Per anno (affollati / funding basso): " + "; ".join(
                 f"{y} {pc(v['affollati'][1])} ({v['affollati'][0]}) / {pc(v['funding_basso'][1])} ({v['funding_basso'][0]})"
                 for y, v in per_anno.items()) + ".", "",
             f"**Esito: {esito}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {soglia:.5f})."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_QUARTA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("P9D FINITA", flush=True)
