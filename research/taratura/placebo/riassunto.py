"""Le misure della prova a placebo (regole.md, punto 5), da esiti_k<k>.jsonl. Si lancia solo a prova finita.

Ordine voluto: prima la copertura (tutte le coppie moneta-timeframe ci sono?) e il campione (almeno 1.000
placebo valutabili in costruzione?). Se uno dei due manca si stampano solo i conteggi e ci si ferma, senza
calcolare nessuna quota (regole.md, punto 5).
Uso: python -m research.taratura.placebo.riassunto [k ...]   (default: 0)
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Dict, List

import numpy as np

QUI = Path(__file__).resolve().parent
SOGLIA_M1 = 0.03
SOGLIA_M2 = 0.13
CAMPIONE_MINIMO = 1000
COPPIE_PER_K = 160  # 80 monete x 2 timeframe
FASCE_M1 = ((70, 149), (150, 299), (300, 10**9))
FASCE_M2 = ((30, 69), (70, 149), (150, 10**9))


def wilson(successi: int, n: int, z: float = 1.959964):
    if n == 0:
        return (float("nan"), float("nan"))
    p = successi / n
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    mezzo = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (centro - mezzo, centro + mezzo)


def intervallo_per_moneta(righe: List[dict], cond: Callable, B: int = 2000, seme: int = 0):
    """Intervallo al 95% ricampionando le MONETE, ciascuna con tutte le sue placebo (sono correlate)."""
    per: Dict[str, List[int]] = defaultdict(lambda: [0, 0])
    for r in righe:
        per[r["simbolo"]][0] += bool(cond(r))
        per[r["simbolo"]][1] += 1
    if not per:
        return (float("nan"), float("nan"))
    s = np.array([v[0] for v in per.values()])
    n = np.array([v[1] for v in per.values()])
    idx = np.random.default_rng(seme).integers(0, s.size, (B, s.size))
    q = s[idx].sum(1) / n[idx].sum(1)
    return float(np.percentile(q, 2.5)), float(np.percentile(q, 97.5))


def misura(righe: List[dict], cond: Callable) -> Dict[str, float]:
    n = len(righe)
    s = sum(1 for r in righe if cond(r))
    lo, hi = wilson(s, n)
    blo, bhi = intervallo_per_moneta(righe, cond)
    per_moneta = Counter(r["simbolo"] for r in righe if cond(r))
    return {"s": s, "n": n, "p": (s / n if n else float("nan")), "wilson": (lo, hi), "monete": (blo, bhi),
            "monete_con_almeno_una": len(per_moneta),
            "quota_max_una_moneta": (max(per_moneta.values()) / s if s else 0.0)}


def fmt(m: Dict[str, float]) -> str:
    if not m["n"]:
        return "nessuna"
    return (f"{m['s']} su {m['n']} = {100*m['p']:.2f}% (per moneta 95%: {100*m['monete'][0]:.2f}-"
            f"{100*m['monete'][1]:.2f}%; Wilson {100*m['wilson'][0]:.2f}-{100*m['wilson'][1]:.2f}%; "
            f"monete con almeno una: {m['monete_con_almeno_una']}; quota della moneta piu' presente: "
            f"{100*m['quota_max_una_moneta']:.0f}%)")


def in_fascia(r: dict, fascia) -> bool:
    return fascia[0] <= r["n_trade"] <= fascia[1]


def netta(r):
    return r.get("netta_b", False)


def p10(r):
    return r.get("p_b", 1.0) < 0.10


def main(argv: List[str]) -> int:
    ks = [int(a) for a in argv] or [0]
    righe = []
    for k in ks:
        percorso = QUI / f"esiti_k{k}.jsonl"
        righe += [json.loads(r) for r in open(percorso)] if percorso.exists() else []
    versioni = {r.get("versione_codice") for r in righe}
    print(f"sfasamenti {ks}; versioni del codice: {sorted(v[:8] for v in versioni if v)}")
    # 1. copertura
    coppie = {(r["simbolo"], r["timeframe"], r.get("sfasamento_k", 0)) for r in righe if not r.get("errore_moneta")}
    attese = COPPIE_PER_K * len(ks)
    err_monete = [r for r in righe if r.get("errore_moneta")]
    err_placebo = [r for r in righe if r.get("errore")]
    print(f"coppie moneta-timeframe: {len(coppie)} su {attese}; monete con errore: {len(err_monete)}; "
          f"placebo con errore: {len(err_placebo)}")
    for r in err_monete[:10] + err_placebo[:10]:
        print("  errore:", r.get("simbolo"), r.get("timeframe"), r.get("regola"), r.get("errore_moneta") or r.get("errore"))
    if len(coppie) < attese:
        print("COPERTURA INCOMPLETA: nessuna misura finche' mancano coppie (o la mancanza non e' dichiarata)")
        return 1
    # 2. campione
    costr_g = [r for r in righe if r["periodo"] == "costruzione" and r.get("giudicata")]
    costr = [r for r in costr_g if r.get("valutabile_b") and "netta_b" in r]
    valid_g = [r for r in righe if r["periodo"] == "validazione" and r.get("giudicata")]
    valid = [r for r in valid_g if r.get("valutabile_b") and "p_b" in r]
    tutte_c = [r for r in righe if r["periodo"] == "costruzione" and r.get("regola")]
    print(f"placebo in costruzione {len(tutte_c)}: con >= 70 trade {len(costr_g)}, valutabili contro la (b) "
          f"{len(costr)}; in validazione con >= 30 trade {len(valid_g)}, valutabili {len(valid)}")
    motivi = Counter(r.get("motivo_non_valutabile", "?") for r in costr_g + valid_g if not (r.get("valutabile_b") and ("netta_b" in r or "p_b" in r)))
    if motivi:
        print("non valutabili (a parte, fuori dal denominatore):", dict(motivi))
    if len(costr) < CAMPIONE_MINIMO:
        print(f"CAMPIONE INSUFFICIENTE ({len(costr)} < {CAMPIONE_MINIMO}): serve il secondo sfasamento prima di "
              f"leggere qualunque quota (regole.md, punto 5)")
        return 1
    # 3. misure
    m1 = misura(costr, netta)
    m2 = misura(valid, p10)
    print("M1 netta contro la (b), costruzione:", fmt(m1), "| soglia 3%")
    print("M2 p < 0,10 in validazione:", fmt(m2), "| soglia 13%")
    print("per fascia di trade (il confronto con il dichiarato 0-2% e 6-11% si fa sulla fascia piu' bassa):")
    for f in FASCE_M1:
        g = [r for r in costr if in_fascia(r, f)]
        print(f"  M1 {f[0]}-{f[1] if f[1] < 10**9 else '...'} trade: {fmt(misura(g, netta))}")
        for tf in ("1h", "4h"):
            print(f"      {tf}: {fmt(misura([r for r in g if r['timeframe'] == tf], netta))}")
    for f in FASCE_M2:
        g = [r for r in valid if in_fascia(r, f)]
        print(f"  M2 {f[0]}-{f[1] if f[1] < 10**9 else '...'} trade: {fmt(misura(g, p10))}")
        for tf in ("1h", "4h"):
            print(f"      {tf}: {fmt(misura([r for r in g if r['timeframe'] == tf], p10))}")
    print("informativo: candidati (netta (a) e (b), R medio > 0, nessuna violazione):",
          fmt(misura(costr, lambda r: r.get("candidato", False))))
    print("informativo: p < 0,10 in costruzione:", fmt(misura(costr, p10)))
    print("informativo: netta in validazione (p < 0,02275):", fmt(misura(valid, lambda r: r.get("p_b", 1.0) < 0.02275)))
    print("informativo: M1 contando le non valutabili come non nette:",
          fmt(misura(costr_g, netta)))
    for chiave in ("timeframe", "direzione", "regola", "uscita"):
        print(f"per {chiave}:")
        for g in sorted({r[chiave] for r in costr}):
            print(f"  {g}: M1 {fmt(misura([r for r in costr if r[chiave] == g], netta))}")
            print(f"  {' ' * len(g)}  M2 {fmt(misura([r for r in valid if r[chiave] == g], p10))}")
    bl = sorted(r.get("n_blocchi", 0) for r in costr)
    tr = sorted(r["n_trade"] for r in costr)
    print(f"blocchi interi in costruzione: mediana {bl[len(bl)//2]}, minimo {bl[0]}; trade: mediana {tr[len(tr)//2]}")
    # 4. esito (stima puntuale sul totale; al limite se la soglia cade nell'intervallo per moneta)
    ok1, ok2 = m1["p"] <= SOGLIA_M1, m2["p"] <= SOGLIA_M2
    limite = [nome for nome, m, s in (("M1", m1, SOGLIA_M1), ("M2", m2, SOGLIA_M2)) if m["monete"][0] <= s <= m["monete"][1]]
    if ok1 and ok2:
        print("ESITO: l'esame regge sui prezzi veri (M1 <= 3% e M2 <= 13%)")
    else:
        print("ESITO: l'esame e' troppo generoso sui prezzi veri: STOP (regole.md, punto 6)")
    if limite:
        print(f"ESITO AL LIMITE per {', '.join(limite)}: la soglia cade dentro l'intervallo per moneta")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
