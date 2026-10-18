"""Fase 3, punto 1: analisi dei trade delle varianti gia' provate (solo LINKUSDT, solo costruzione).

Uso: python3 research/campagne/LINK6/codice/fase3_analisi.py <id> [<id> ...]

Legge campagne/LINK6/risultati/<id>.json (trade gia' calcolati in Fase 2): nessun nuovo calcolo sui prezzi.
Per ogni variante: costo medio in R stimato dalla larghezza dello stop (commissioni 0,05% + slippage 0,02% per
lato = 0,14% andata e ritorno, diviso la larghezza), R medio per motivo di uscita, per larghezza dello stop
(quinti), per ora d'ingresso (blocchi di 6 ore), per giorno feriale o fine settimana, per semestre.
"""
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

CAMPAGNA = Path(__file__).resolve().parents[1]
COSTO_ANDATA_RITORNO = 2 * (0.0005 + 0.0002)


def media(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def riga(nome, gruppi):
    parti = [f"{k}: {len(v)} t, {media(v):+.3f}" for k, v in gruppi.items()]
    print(f"  {nome}: " + "; ".join(parti))


for vid in sys.argv[1:]:
    tr = json.loads((CAMPAGNA / "risultati" / f"{vid}.json").read_text(encoding="utf-8"))["trade"]
    r = [t["r"] for t in tr]
    w = [t["larghezza_stop"] for t in tr]
    costo = [COSTO_ANDATA_RITORNO / x for x in w]
    print(f"{vid}: {len(tr)} trade, R medio {media(r):+.3f}, larghezza media dello stop {media(w):.2%}, "
          f"costo medio stimato {media(costo):.3f} R, R medio prima dei costi circa {media(r) + media(costo):+.3f}")
    per_motivo = defaultdict(list)
    for t in tr:
        per_motivo[t["motivo"]].append(t["r"])
    riga("per uscita", dict(per_motivo))
    ordine = sorted(range(len(tr)), key=lambda i: w[i])
    quinti = defaultdict(list)
    for pos, i in enumerate(ordine):
        quinti[f"Q{pos * 5 // len(tr) + 1}"].append(r[i])
    riga("per larghezza (Q1 stretta)", dict(sorted(quinti.items())))
    ore = defaultdict(list)
    giorni = defaultdict(list)
    semestri = defaultdict(list)
    for t in tr:
        d = datetime.strptime(t["ingresso"], "%Y-%m-%dT%H:%M:%SZ")
        ore[f"{d.hour // 6 * 6:02d}-{d.hour // 6 * 6 + 6:02d}"].append(t["r"])
        giorni["feriale" if d.weekday() < 5 else "fine sett."].append(t["r"])
        semestri[f"{d.year}-{1 if d.month <= 6 else 2}"].append(t["r"])
    riga("per ora d'ingresso (UTC)", dict(sorted(ore.items())))
    riga("per giorno", dict(giorni))
    riga("per semestre", dict(sorted(semestri.items())))
