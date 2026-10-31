"""Misura descrittiva (non una prova, non entra nel conto): il conto unico per i soldi veri, G1 più gli eventi (N3 ed E4), sul passato.
G1 con tutto il capitale (i giorni della prova 57); in più ogni evento della prova 32 (N3 su Binance) e della prova 26 (E4) con il 5% del
capitale, al massimo 20 aperti insieme, come il paper degli eventi. Il rendimento di ogni evento è spalmato in parti uguali sui suoi
giorni (un'approssimazione: la discesa vera degli eventi è un po' più grande).

Uso: python3 -m research.programma7.conto_unico
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc

QUI = Path(__file__).parent
P6 = QUI.parent / "programma6"
QUOTA, MASSIMO = 0.05, 20


def numeri(x: pd.Series) -> dict:
    eq = (1 + x).cumprod()
    return {"annuo": float((1 + x).prod() ** (365 / len(x)) - 1), "sharpe": float(x.mean() / x.std() * np.sqrt(365)),
            "discesa": float((eq / eq.cummax() - 1).min()), "giorno_peggiore": float(x.min())}


def main() -> None:
    g = pd.read_csv(QUI / "risultati_prima" / "giorni_G1.csv.gz")
    g1 = pd.Series(g["netto"].to_numpy(), index=g["giorno"].to_numpy())
    n3 = pd.read_csv(P6 / "risultati_trentaduesima" / "eventi_N3B.csv")
    e4 = pd.read_csv(P6 / "risultati_ventiseiesima" / "eventi_E4.csv")
    ev = [(int(pd.Timestamp(d).timestamp() // 86400), max(1, int(round(gg))), float(r), "N3")
          for d, gg, r in zip(n3["data"], n3["giorni"], n3["r"]) if np.isfinite(r)]
    ev += [(int(pd.Timestamp(d).timestamp() // 86400), 7, float(r), "E4") for d, r in zip(e4["data"], e4["r7"]) if np.isfinite(r)]
    ev.sort()
    extra = pd.Series(0.0, index=g1.index)
    aperti, saltati, usati = [], 0, 0
    for g0, durata, r, tipo in ev:
        aperti = [a for a in aperti if a > g0]
        if len(aperti) >= MASSIMO:
            saltati += 1
            continue
        aperti.append(g0 + durata)
        usati += 1
        giorni = [d for d in range(g0, g0 + durata) if d in extra.index]
        for d in giorni:
            extra[d] += QUOTA * r / durata
    insieme = g1 + extra
    a, b, c = numeri(g1), numeri(insieme), numeri(extra)
    anni = pd.to_datetime(g1.index.to_numpy() * 86400, unit="s").year
    per_anno = {int(y): (float((1 + g1[anni == y]).prod() - 1), float((1 + insieme[anni == y]).prod() - 1)) for y in sorted(set(anni))}
    corr = float(np.corrcoef(g1, extra)[0, 1])
    pc = lambda v: f"{100 * v:+.1f}%"  # noqa: E731
    righe = ["# Il conto unico per i soldi veri: G1 più gli eventi, sul passato (misura descrittiva)", "",
             "Script `conto_unico.py`. G1 con tutto il capitale (i giorni della prova 57, dal 4 gennaio 2021 al 4 ottobre 2026); in più ogni "
             "evento della prova 32 (le monete appena quotate su Binance) e della prova 26 (il funding al tetto) con il 5% del capitale, al "
             "massimo 20 aperti insieme, come il paper degli eventi. Il rendimento di ogni evento è spalmato sui suoi giorni: è "
             "un'approssimazione, la discesa vera è un po' più grande. Non è una prova e non entra nel conto.", "",
             f"* Eventi usati {usati}, saltati perché ce n'erano già 20 aperti {saltati}.", "",
             "| | Rendimento all'anno | Sharpe | Discesa massima | Giorno peggiore |", "|---|---|---|---|---|",
             f"| G1 da sola | {pc(a['annuo'])} | {a['sharpe']:.2f} | {pc(a['discesa'])} | {pc(a['giorno_peggiore'])} |",
             f"| G1 più gli eventi | {pc(b['annuo'])} | {b['sharpe']:.2f} | {pc(b['discesa'])} | {pc(b['giorno_peggiore'])} |",
             f"| Gli eventi da soli (al 5%) | {pc(c['annuo'])} | {c['sharpe']:.2f} | {pc(c['discesa'])} | {pc(c['giorno_peggiore'])} |", "",
             "Per anno (G1 da sola → G1 più gli eventi): " + ", ".join(f"{y} {pc(x)} → {pc(z)}" for y, (x, z) in per_anno.items()) + ".", "",
             f"Correlazione fra G1 e gli eventi, giorno per giorno: {corr:.2f}."]
    testo = "\n".join(righe) + "\n"
    (QUI / "CONTO_UNICO.md").write_text(testo, encoding="utf-8")
    print(testo)


if __name__ == "__main__":
    main()
