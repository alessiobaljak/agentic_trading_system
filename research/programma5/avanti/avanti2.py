"""Programma 5: la seconda tornata della prova in avanti (REGOLE.md, sezione 9bis): N-001, N-002, N-003 sui dati dal
2026-10-19 00:00 UTC, sulle 100 monete. Scrive ``avanti/A2.json`` e ``avanti/A2.md``.

Uso: PYTHONPATH=. python3 research/programma5/avanti/avanti2.py [--rifai-barre]
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma5.strumenti.idee_fase2 import per_moneta_cella

QUI = Path(__file__).parent
IDEE = QUI.parent / "idee"
CENTO = tuple(json.loads((QUI.parent / "universo_top100.json").read_text())["scelte"])
INIZIO_A2 = int(datetime(2026, 10, 19, tzinfo=timezone.utc).timestamp() // 60)
FINE = datetime(2027, 3, 31, tzinfo=timezone.utc)
PROCEDURE = ("N-001", "N-002", "N-003")


def esame(t: pd.DataFrame, c: pd.DataFrame, finale: bool) -> dict:
    if t.empty:
        return {"trade": 0, "esito": "nessun trade chiuso"}
    m = t["minuto"].to_numpy()
    e = {"trade": int(len(t)), "netto": m5.bootstrap_giorni(t["netto"].to_numpy(), m, 10000),
         "netto_doppio": float(t["netto_doppio"].mean()), "caso_netto": float(c["netto"].mean()) if len(c) else None}
    giorno = m // 1440
    somme = t.groupby(giorno)["netto"].sum()
    e["senza_migliore"] = float(t["netto"][giorno != somme.idxmax()].mean()) if len(somme) > 1 else float("nan")
    e["per_moneta"] = {s: {"trade": int(len(g)), "netto": float(g["netto"].mean())} for s, g in t.groupby("simbolo")}
    if not finale:
        e["esito"] = f"in corso ({len(t)} trade chiusi su 400)"
        return e
    soglia = 0.05 / len(PROCEDURE)
    monete = [x for x in e["per_moneta"].values() if x["trade"] >= 10]
    if not (e["netto"]["media"] > 0 and e["netto"]["p"] <= soglia):
        e["esito"] = f"non passa: p {e['netto']['p']:.4f} oltre {soglia:.4f} o netto non positivo"
    elif not e["netto_doppio"] > 0:
        e["esito"] = "non passa: non positivo a costi doppi"
    elif not e["senza_migliore"] > 0:
        e["esito"] = "non passa: non positivo togliendo il giorno migliore"
    elif sum(1 for x in monete if x["netto"] > 0) < 0.6 * len(monete):
        e["esito"] = "non passa: positivo su meno del 60% delle monete"
    else:
        e["esito"] = "PASSA: strategia valida"
    return e


def main(argv) -> int:
    if "--rifai-barre" in argv:
        for f in (m5.DATI / "ore").glob("*_WA.pkl"):
            f.unlink()
    finale_data = datetime.now(timezone.utc) >= FINE
    risultati = {}
    for idea in PROCEDURE:
        varianti = json.loads((IDEE / idea / "varianti.json").read_text())
        tt, cc = [], []
        for s in CENTO:
            ris = per_moneta_cella(idea, varianti, s, "WA")
            if idea in ris:
                t, c = ris[idea]
                if len(t):
                    tt.append(t[t["minuto"] >= INIZIO_A2])
                if len(c):
                    cc.append(c[c["minuto"] >= INIZIO_A2])
        t = pd.concat(tt, ignore_index=True) if tt else pd.DataFrame()
        c = pd.concat(cc, ignore_index=True) if cc else pd.DataFrame()
        e = esame(t, c, finale_data or len(t) >= 400)
        risultati[idea] = e
        if len(t):
            t.to_csv(QUI / f"trade_A2_{idea}.csv.gz", index=False)
        print(idea, e.get("trade"), e.get("esito"), flush=True)
    dati_fino = max((x.name for x in (m5.DATI / "BTCUSDT" / "klines").glob("*.zip")), default="?")
    (QUI / "A2.json").write_text(json.dumps({"dati_fino_a": dati_fino, "procedure": risultati}, ensure_ascii=False,
                                            indent=1, default=float), encoding="utf-8")
    righe = ["# Seconda tornata della prova in avanti (periodo A2, dal 2026-10-19)", "",
             f"Calcolo di `avanti2.py` (REGOLE.md, sezione 9bis) con i dati fino a `{dati_fino}`. Solo trade chiusi.", "",
             "| Idea | Trade chiusi | Netto a trade | Intervallo al 95% | p | A costi doppi | Caso | Esito |",
             "|---|---|---|---|---|---|---|---|"]
    for n, e in risultati.items():
        if not e.get("trade"):
            righe.append(f"| {n} | 0 | | | | | | {e['esito']} |")
            continue
        nt = e["netto"]
        caso = e.get("caso_netto")
        righe.append(f"| {n} | {e['trade']} | {100 * nt['media']:+.3f}% | {100 * nt['basso']:+.3f}; {100 * nt['alto']:+.3f} | "
                     f"{nt['p']:.4f} | {100 * e['netto_doppio']:+.3f}% | "
                     f"{'' if caso is None else f'{100 * caso:+.3f}%'} | {e['esito']} |")
    (QUI / "A2.md").write_text("\n".join(righe) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
