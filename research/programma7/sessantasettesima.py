"""Programma 7, sessantasettesima prova (SESSANTASETTESIMA.md): IM, l'inizio del mese sul Bitcoin: long dall'apertura dell'ultimo giorno
del mese a quella del quarto giorno del mese dopo; controllo con la stessa tenuta negli altri giorni.

Uso: python3 -m research.programma7.sessantasettesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import trentesima as tr
from research.programma6 import ventunesima as vu
from research.programma7 import prima as g1

QUI = Path(__file__).parent
RIS = QUI / "risultati_sessantasettesima"
DAL, AL = sc.giorno(2020, 1, 1), sc.giorno(2026, 10, 1)
TENUTA, SEME = 4, 2026
PROVE_A_EVENTI = 38


def ultimi_giorni() -> list:
    """L'ultimo giorno di ogni mese (giorno dall'epoca) con la tenuta di 4 giorni dentro il periodo."""
    fine = pd.date_range(sc.data(DAL), sc.data(AL - 1), freq="ME")
    return [int(x.timestamp() // 86400) for x in fine if int(x.timestamp() // 86400) + TENUTA <= AL]


def esegui(log=print) -> dict:
    pan = sc.pannello()
    t0, S = pan["t0"], list(pan["simboli"])
    jb = S.index("BTCUSDT")
    O, F = pan["open"], np.nan_to_num(pan["funding"])

    def lungo(g: int) -> float:
        a, b = g - t0, g + TENUTA - t0
        return float(O[b, jb] / O[a, jb] - 1 - vu.COSTO_BTC - F[a:b, jb].sum())
    eventi = ultimi_giorni()
    ev = pd.DataFrame([{"data": sc.data(L), "annuncio": int((L + 3) // 7), "r": lungo(L),
                        "ultimo_giorno": float(O[L + 1 - t0, jb] / O[L - t0, jb] - 1),
                        "primi_tre": float(O[L + TENUTA - t0, jb] / O[L + 1 - t0, jb] - 1)} for L in eventi])
    vietati = set()
    for L in eventi:
        vietati.update(range(L - TENUTA + 1, L + TENUTA))
    controllo = np.array([lungo(g) for g in range(DAL, AL - TENUTA) if g not in vietati])
    RIS.mkdir(exist_ok=True)
    ev.to_csv(RIS / "eventi_IM.csv", index=False)
    e = tr.esame(ev, "r")
    rng = np.random.default_rng(SEME)
    b = rng.choice(ev["r"].to_numpy(), size=(10000, len(ev)), replace=True).mean(axis=1) - controllo.mean()
    diff = {"media": float(ev["r"].mean() - controllo.mean()), "basso": float(np.quantile(b, 0.025)), "alto": float(np.quantile(b, 0.975)),
            "p": float((b <= 0).mean())}
    # per capire: le altcoin (indice a pesi uguali dell'universo di G1) contro il Bitcoin nelle stesse finestre
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    alt = []
    for L in eventi:
        if L < int(ps["lunedi"][0]):
            continue
        u = g1.universo_del_giorno(np.array([L]), ps["lunedi"], ps["U"])[0].copy()
        u[jb] = False
        r = O[L + TENUTA - t0, u] / O[L - t0, u] - 1
        r = r[np.isfinite(r)]
        if len(r):
            alt.append(float(r.mean() - (O[L + TENUTA - t0, jb] / O[L - t0, jb] - 1)))
    vecchi = ev["data"] < "2024-01-01"
    out = {"eventi": int(len(ev)), "esame": e, "controllo": {"giorni": int(len(controllo)), "media": float(controllo.mean())},
           "differenza_con_controllo": diff, "ultimo_giorno": float(ev["ultimo_giorno"].mean()), "primi_tre": float(ev["primi_tre"].mean()),
           "2020_2023": float(ev.loc[vecchi, "r"].mean()), "2024_2026": float(ev.loc[~vecchi, "r"].mean()),
           "altcoin_contro_btc": {"eventi": len(alt), "media": float(np.mean(alt)) if alt else None}, "soglia_tutte": 0.01 / PROVE_A_EVENTI}
    valida = e["esito"] == "VALIDA" and diff["p"] <= 0.05
    out["esito"] = ("VALIDA" if valida and e["boot"]["p"] <= out["soglia_tutte"] else
                    "passa l'esame scritto ma non la soglia di tutte le prove a eventi" if valida else
                    e["esito"] if e["esito"] != "VALIDA" else "non sopra il controllo")
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: "—" if v is None or v != v else f"{100 * v:+.2f}%"  # noqa: E731
    bb = e["boot"]
    testo = "\n".join([
        "# Programma 7 — risultati della sessantasettesima prova (IM: l'inizio del mese sul Bitcoin)", "",
        "Regole in `SESSANTASETTESIMA.md` (scritte prima). Long il perpetuo del Bitcoin dall'apertura dell'ultimo giorno del mese a quella "
        "del quarto giorno del mese dopo, dal gennaio 2020 al settembre 2026, costi a mercato e funding.", "",
        f"* **{bb['eventi']} mesi: {pc(bb['media'])} a operazione** (intervallo {pc(bb['basso'])}; {pc(bb['alto'])}, p {bb['p']:.4f}); "
        f"mediana {pc(e['mediana'])}, vinte {100 * e['vinti']:.0f}%; metà {pc(e['prima_meta'])} e {pc(e['seconda_meta'])}; senza le 5 "
        f"migliori {pc(e['senza_5_migliori'])}.",
        "* Per anno: " + ", ".join(f"{a} {pc(v['media'])} ({v['eventi']})" for a, v in e["per_anno"].items()) + ".",
        f"* **Controllo** (la stessa tenuta di 4 giorni in {out['controllo']['giorni']} altri giorni): {pc(out['controllo']['media'])}; "
        f"differenza {pc(diff['media'])} (intervallo {pc(diff['basso'])}; {pc(diff['alto'])}, p {diff['p']:.3f}).",
        f"* Per capire: l'ultimo giorno da solo {pc(out['ultimo_giorno'])}, i primi tre da soli {pc(out['primi_tre'])} (prima dei costi); "
        f"2020-2023 {pc(out['2020_2023'])}, 2024-2026 {pc(out['2024_2026'])}; le altcoin contro il Bitcoin nelle stesse finestre "
        f"{pc(out['altcoin_contro_btc']['media'])} ({out['altcoin_contro_btc']['eventi']} mesi).", "",
        f"**Esito: {out['esito']}** (soglia contando le {PROVE_A_EVENTI} prove a eventi: {out['soglia_tutte']:.5f})."]) + "\n"
    (QUI / "RISULTATI_SESSANTASETTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SESSANTASETTESIMA FINITA", flush=True)
