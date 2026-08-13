"""DOVE MUOIONO LE CANDIDATE — la diagnosi che prima non esisteva.

Ogni run del GATE 1 valuta oltre ventimila combinazioni e ne promuove una manciata.
Fino a ieri di quelle ventimila bocciature non restava traccia: si sapeva "non
passa niente" e non si sapeva perche'. E' la condizione in cui l'unica reazione
possibile e' abbassare le soglie a caso — cioe' validare rumore.

Ora ogni valutazione registra il criterio che l'ha fermata. Questo script legge il
risultato e risponde a tre domande che prima non avevano risposta:

  1. DOVE si muore. Se il collo di bottiglia e' `trades`, il problema e' che le
     strategie sparano troppo poco su questo timeframe: si lavora sulla frequenza
     dei segnali, non sul profitto. Se e' `pf`, i costi non vengono battuti: si
     lavora su coin piu' liquide o su take-profit piu' lontani. Se e' `holdout`,
     le strategie funzionano dove le abbiamo scelte e non fuori: e' sovradattamento,
     e va ridotta la ricerca, non allargata.
  2. QUANTO manca. Un criterio mancato del 3% e uno mancato del 70% chiedono
     lavori diversi.
  3. SU COSA insistere. I quasi-passaggi sono i semi da cui il run successivo fa
     mutare le candidate: cercare dove ci si e' avvicinati invece di ripartire da
     zero a ogni giro.

Uso (sul VPS):
    .venv/bin/python -m scripts.gate_autopsy
    .venv/bin/python -m scripts.gate_autopsy --near 20
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone

from bot.core.firebase_client import get_firebase

# Cosa significa, in pratica, morire su ciascun criterio. Serve a trasformare
# un'etichetta in una direzione di lavoro: senza, la diagnosi resta un istogramma.
MEANING = {
    "trades": "pochi segnali: la strategia spara troppo poco su questo timeframe",
    "pf": "il profitto lordo non batte i costi (fee + spread + funding)",
    "win_rate": "vince troppo di rado perche' i guadagni ripaghino le perdite",
    "total_return": "profittevole, ma di troppo poco per valere il rischio",
    "consistency": "guadagna in un periodo e perde negli altri: non e' un edge stabile",
    "recovery": "la curva scava buche troppo profonde rispetto a quanto rende",
    "pf_ex_top": "regge solo grazie ai suoi pochi colpi migliori: fortuna, non edge",
    "regime": "in almeno un regime di mercato perde in modo conclamato",
    "holdout": "funziona dove l'abbiamo scelta e NON sui dati mai visti: sovradattamento",
}


def _show(rep: dict, title: str, near_n: int) -> None:
    if not rep:
        print(f"\n=== {title}: nessuna autopsia registrata ===")
        return
    ts = rep.get("updated_at", 0)
    when = (datetime.fromtimestamp(ts, timezone.utc).strftime("%d %b %H:%M UTC")
            if ts else "?")
    ev, ps, dg = rep.get("evaluated", 0), rep.get("passed", 0), rep.get("diagnosed", 0)
    print(f"\n=== {title} · {when} ===")
    print(f"  {ev} valutazioni · {ps} passate "
          f"({(ps / ev * 100) if ev else 0:.2f}%) · {dg} diagnosticate")

    binding = rep.get("binding") or {}
    if binding:
        tot = sum(binding.values()) or 1
        print("\n  DOVE MUOIONO (criterio messo peggio):")
        for k, v in list(binding.items())[:9]:
            print(f"    {k:<14} {v:>7}  {v / tot * 100:>5.1f}%  — {MEANING.get(k, '')}")

    involved = rep.get("involved") or {}
    if involved:
        print("\n  QUANTE VOLTE OGNI CRITERIO E' COINVOLTO (anche non da solo):")
        for k, v in list(involved.items())[:9]:
            print(f"    {k:<14} {v:>7}  {v / (dg or 1) * 100:>5.1f}% delle bocciate")
        # Un criterio presente quasi ovunque non sta SELEZIONANDO: sta descrivendo
        # una condizione del mercato in cui stiamo cercando. E' un'informazione
        # diversa da "e' il criterio piu' severo".
        univ = [k for k, v in involved.items() if v >= 0.9 * (dg or 1)]
        if univ:
            print(f"    -> {', '.join(univ)}: presente in quasi TUTTE le bocciature. "
                  f"Non sta\n       filtrando fra candidate, sta descrivendo il "
                  f"terreno in cui cerchiamo.")

    near = rep.get("near_misses") or []
    print(f"\n  QUASI-PASSAGGI (un solo criterio, mancato di poco): "
          f"{rep.get('near_miss_count', len(near))}")
    for n in near[:near_n]:
        sf = n.get("shortfall")
        print(f"    {str(n.get('key')):<34} manca {abs(sf) * 100 if sf else 0:>5.1f}% "
              f"su {n.get('binding')} · PF {n.get('pf')} · {n.get('trades')} trade")
    if near:
        print("    (sono i semi da cui il prossimo run fa mutare le candidate)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--near", type=int, default=10,
                    help="quanti quasi-passaggi elencare")
    args = ap.parse_args()
    fb = get_firebase()
    a = fb.get_doc("gate_autopsy", "current") or {}
    b = fb.get_doc("gate_autopsy", "discover") or {}
    if not a and not b:
        print("[autopsy] nessuna diagnosi registrata: serve un run dell'optimizer "
              "col codice aggiornato.")
        return 1
    _show(a, "STRATEGIE BASE (optimize)", args.near)
    _show(b, "STRATEGIE GENERATE (discover)", args.near)
    print("\nCOSA FARSENE. Il criterio dominante dice su cosa lavorare, e NON e' mai"
          "\n'abbassare quella soglia': una soglia abbassata finche' qualcosa passa"
          "\nseleziona esattamente il rumore che la soglia esisteva per escludere.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
