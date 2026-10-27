"""Programma 7, cinquantunesima prova (CINQUANTUNESIMA.md): N3G, le 613 operazioni di N3 (prova 32) divise fra le monete distribuite
gratis da Binance (HODLer Airdrops, Launchpool, Megadrop) e le altre; differenza nello stesso trimestre, etichetta mescolata a caso
dentro il trimestre.

Uso: python3 -m research.programma7.cinquantunesima
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import annunci as an
from research.programma6 import seconda as sc
from research.programma6 import trentesima as tr

QUI = Path(__file__).parent
RADICE = QUI.parents[1]
EVENTI = RADICE / "research" / "programma6" / "risultati_trentaduesima" / "eventi_N3B.csv"
QUOTAZIONI = RADICE / "research" / "data" / "annunci" / "quotazioni.json"
GRATIS = re.compile(r"Binance (HODLer Airdrops|Launchpool|Megadrop)", re.I)
FINESTRA, ETA, MESCOLATE, SEME = 60, 7, 10_000, 2026
PROVE_A_EVENTI = 34


def gratis(simboli) -> dict:
    """Perpetuo → [(giorno dell'annuncio, tipo)] degli annunci di distribuzione gratis."""
    out: dict = {}
    for x in json.loads(QUOTAZIONI.read_text(encoding="utf-8")):
        m = GRATIS.search(x["titolo"])
        if not m or "Launchpad" in x["titolo"]:
            continue
        for s in re.findall(r"\(([A-Z0-9]{1,15})\)", x["titolo"]):
            p = an.perpetuo(s, simboli)
            if p:
                out.setdefault(p, []).append((x["ms"] / 86_400_000, m.group(1).lower()))
    return out


def etichetta(ev: pd.DataFrame, g: dict) -> pd.DataFrame:
    d = ev.copy()
    d["g_ent"] = d["data"].map(lambda x: sc.giorno(*map(int, x.split("-"))))
    tipi = []
    for s, ge in zip(d["simbolo"], d["g_ent"]):
        vicini = [t for m, t in g.get(s, []) if 0 <= ge - m <= FINESTRA]
        tipi.append(vicini[0] if vicini else "")
    d["tipo"] = tipi
    d["gratis"] = d["tipo"] != ""
    d["trimestre"] = d["data"].str[:4] + "T" + ((d["data"].str[5:7].astype(int) - 1) // 3 + 1).astype(str)
    return d


def differenza(d: pd.DataFrame, col: str = "r") -> float:
    """Media pesata (numero delle gratis) delle differenze gratis − altre nei trimestri con tutti e due i gruppi."""
    num = den = 0.0
    for _, q in d.groupby("trimestre"):
        a, b = q.loc[q["gratis"], col], q.loc[~q["gratis"], col]
        if len(a) and len(b):
            num += len(a) * (a.mean() - b.mean())
            den += len(a)
    return num / den if den else np.nan


def mescola(d: pd.DataFrame, col: str = "r", n: int = MESCOLATE, seme: int = SEME) -> np.ndarray:
    rng = np.random.default_rng(seme)
    gruppi = [(q[col].to_numpy(), int(q["gratis"].sum())) for _, q in d.groupby("trimestre")
              if 0 < q["gratis"].sum() < len(q)]
    out = np.empty(n)
    for k in range(n):
        num = den = 0.0
        for v, ng in gruppi:
            idx = rng.permutation(len(v))
            a, b = v[idx[:ng]], v[idx[ng:]]
            num += ng * (a.mean() - b.mean())
            den += ng
        out[k] = num / den
    return out


def esegui(log=print) -> dict:
    ev = pd.read_csv(EVENTI)
    pan = sc.pannello()
    d = etichetta(ev, gratis(pan["simboli"]))
    obs = differenza(d)
    perm = mescola(d)
    p = float((np.sum(perm >= obs) + 1) / (len(perm) + 1))
    g, o = d[d["gratis"]], d[~d["gratis"]]
    ex_g = tr.esame(g, "r")
    out = {"eventi": len(d), "gratis": int(len(g)), "altre": int(len(o)),
           "trimestri_con_tutti_e_due": int(sum(1 for _, q in d.groupby("trimestre") if 0 < q["gratis"].sum() < len(q))),
           "gratis_in_trimestri_confrontabili": int(sum(q["gratis"].sum() for _, q in d.groupby("trimestre") if 0 < q["gratis"].sum() < len(q))),
           "differenza": obs, "p_differenza": p, "differenza_senza_uscita": differenza(d, "r_senza"),
           "media_gratis": float(g["r"].mean()), "media_altre": float(o["r"].mean()),
           "esame_gratis": ex_g,
           "per_tipo": {t: {"eventi": int(len(x)), "media": float(x["r"].mean())} for t, x in g.groupby("tipo")},
           "per_anno": {a: {"gratis": int(x["gratis"].sum()), "media_gratis": float(x.loc[x["gratis"], "r"].mean()) if x["gratis"].any() else None,
                            "altre": int((~x["gratis"]).sum()), "media_altre": float(x.loc[~x["gratis"], "r"].mean())}
                        for a, x in d.groupby(d["data"].str[:4])},
           "uscite_a_30_gratis": float(g["fermata"].astype(bool).mean()), "uscite_a_30_altre": float(o["fermata"].astype(bool).mean()),
           "senza_uscita_gratis": float(g["r_senza"].mean()), "senza_uscita_altre": float(o["r_senza"].mean()),
           "soglia_tutte": 0.01 / PROVE_A_EVENTI}
    passa = p <= 0.01 and ex_g["esito"] == "VALIDA"
    out["esito"] = ("VALIDA" if passa and p <= out["soglia_tutte"] else
                    "passa l'esame scritto (p ≤ 0,01) ma non la soglia di tutte le prove a eventi" if passa else
                    f"la differenza non è sopra zero con p ≤ 0,01 (p {p:.4f})" if p > 0.01 else f"le gratis da sole: {ex_g['esito']}")
    ris = QUI / "risultati_cinquantunesima"
    ris.mkdir(exist_ok=True)
    d[["data", "simbolo", "tipo", "gratis", "trimestre", "r", "r_senza", "fermata"]].to_csv(ris / "eventi_N3G.csv", index=False)
    (ris / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    b = ex_g["boot"]
    testo = "\n".join([
        "# Programma 7 — risultati della cinquantunesima prova (N3G: le monete nuove distribuite gratis)", "",
        "Regole in `CINQUANTUNESIMA.md` (scritte prima). Le 613 operazioni della regola delle monete nuove (prova 32) così come sono.", "",
        f"* **Monete gratis**: {out['gratis']} eventi, **{100 * out['media_gratis']:+.2f}% a evento**; le altre: {out['altre']}, "
        f"{100 * out['media_altre']:+.2f}%.",
        f"* **La differenza nello stesso trimestre** ({out['trimestri_con_tutti_e_due']} trimestri con tutti e due i gruppi, "
        f"{out['gratis_in_trimestri_confrontabili']} gratis): **{100 * obs:+.2f} punti a evento**, p {p:.4f} (l'etichetta mescolata a caso "
        f"{MESCOLATE} volte dentro il trimestre). Senza l'uscita a +30%: {100 * out['differenza_senza_uscita']:+.2f} punti.",
        f"* **Le gratis da sole**: {100 * b['media']:+.2f}% (intervallo {100 * b['basso']:+.2f}%; {100 * b['alto']:+.2f}%, p {b['p']:.4f}); "
        f"mediana {100 * ex_g['mediana']:+.2f}%, vinte {100 * ex_g['vinti']:.0f}%; metà {100 * ex_g['prima_meta']:+.2f}% e "
        f"{100 * ex_g['seconda_meta']:+.2f}%; senza le 5 migliori {100 * ex_g['senza_5_migliori']:+.2f}%.",
        "* Per tipo: " + ", ".join(f"{t} {100 * v['media']:+.2f}% ({v['eventi']})" for t, v in out["per_tipo"].items()) + ".",
        "* Per anno (gratis / altre): " + ", ".join(
            f"{a} " + (f"{100 * v['media_gratis']:+.2f}% ({v['gratis']})" if v["media_gratis"] is not None else "— (0)") +
            f" / {100 * v['media_altre']:+.2f}% ({v['altre']})" for a, v in out["per_anno"].items()) + ".",
        f"* Uscite a +30%: gratis {100 * out['uscite_a_30_gratis']:.0f}%, altre {100 * out['uscite_a_30_altre']:.0f}%. Senza l'uscita: "
        f"gratis {100 * out['senza_uscita_gratis']:+.2f}%, altre {100 * out['senza_uscita_altre']:+.2f}%.", "",
        f"**Esito: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {out['soglia_tutte']:.5f})."]) + "\n"
    (QUI / "RISULTATI_CINQUANTUNESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CINQUANTUNESIMA FINITA", flush=True)
