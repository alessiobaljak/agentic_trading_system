"""QUANDO RIPARTE IL BOT — la data, non la speranza.

Dopo un reset del registro il paper resta fermo finche' il GATE 1 non dichiara
`ready`, e "aspetta qualche settimana" e' una risposta che non si puo' verificare.
Questo script la trasforma in un calendario, usando le stesse regole del gate:

  * una coppia e' VALIDATA con `pass_count >= OPTIMIZER_MIN_PASSES` (default 3);
  * un pass conta solo se dall'ultimo sono entrate OPTIMIZER_NEW_DATA_MIN_HOURS
    (default 168 = una settimana) di dati NUOVI. Quindi la prossima conferma di una
    coppia ha una DATA, e si puo' leggere adesso;
  * `ready` scatta per COPERTURA (frazione dell'universo con almeno una strategia
    validata) OPPURE per NUMERO ASSOLUTO di coppie validate
    (OPTIMIZER_READY_MIN_PAIRS), con i minimi di sicurezza sempre necessari.

La stima assume che ogni coppia passi ALMENO UNA VOLTA per finestra settimanale.
E' un'ipotesi realistica da quando il registro giudica per finestra e non per run:
prima la stessa stima era una finzione, perche' il purge contava i fallimenti a
ogni run e nessuna coppia sopravviveva abbastanza da arrivare alla conferma
successiva (vedi judge_window in scripts/optimize.py). Resta un limite inferiore:
chi non passa per due settimane intere esce comunque dal registro.

Uso (sul VPS):
    .venv/bin/python -m scripts.gate_progress
    .venv/bin/python -m scripts.gate_progress --top 20
"""
from __future__ import annotations

import argparse
import os
import time
from collections import Counter
from datetime import datetime, timezone

from bot.core.firebase_client import decode_pairs, get_firebase

MIN_PASSES = int(os.getenv("OPTIMIZER_MIN_PASSES", "3"))
NEW_DATA_MIN_S = float(os.getenv("OPTIMIZER_NEW_DATA_MIN_HOURS", "168")) * 3600
READY_FRACTION = float(os.getenv("OPTIMIZER_READY_FRACTION", "0.60"))
READY_MIN_PAIRS = int(os.getenv("OPTIMIZER_READY_MIN_PAIRS", "0"))
MIN_COVERED = int(os.getenv("OPTIMIZER_MIN_COVERED", "5"))
PURGE_FAILS = int(os.getenv("OPTIMIZER_PURGE_FAILS", "2"))


def _when(ts: float) -> str:
    if ts <= 0:
        return "—"
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%d %b %H:%M")


def eta_ready(rec: dict, now: float) -> float:
    """Quando QUESTA coppia diventerebbe validata, se continuasse a passare.

    Il conto e' meccanico: mancano `MIN_PASSES - pass_count` conferme, e ognuna
    arriva alla chiusura di una finestra. Una coppia che non ha mai passato non ha
    una data — non ha ancora nemmeno la prima conferma.

    SI PARTE DA `window_start`, NON dall'ultimo pass. Sono due cose diverse e per
    alcune coppie divergono: quelle che esistevano gia' quando la regola della
    finestra e' entrata in vigore hanno la finestra aperta al momento del cambio,
    non al loro ultimo passaggio. Leggere `last_pass_data_end` dava date piu'
    ottimistiche di quelle vere — e' l'errore che mi ha fatto annunciare le seconde
    conferme per il 19 agosto quando sarebbero arrivate il 22.
    """
    passes = int(rec.get("pass_count", 0) or 0)
    if passes >= MIN_PASSES:
        return 0.0
    if passes <= 0:
        return float("inf")
    da = float(rec.get("window_start", 0) or 0) or float(
        rec.get("last_pass_data_end", 0) or 0)
    if da <= 0:
        return float("inf")
    return da + (MIN_PASSES - passes) * NEW_DATA_MIN_S


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=15,
                    help="quante coppie mostrare nel dettaglio")
    ap.add_argument("--coins-min-pass", type=int, default=None, metavar="K",
                    help="stampa SOLO la lista CSV delle coin con almeno K pass, "
                         "e nient'altro: e' l'input delle conferme mirate")
    args = ap.parse_args()

    doc = get_firebase().get_doc("strategy_registry", "validated") or {}
    pairs = decode_pairs(doc.get("pairs"))

    if args.coins_min_pass is not None:
        coins = sorted({r.get("symbol") for r in pairs.values()
                        if int(r.get("pass_count", 0) or 0) >= args.coins_min_pass
                        and r.get("symbol")})
        print(",".join(coins))
        return 0 if coins else 1

    if not pairs:
        print("[gate] registro VUOTO: nessuna coppia tracciata. Il bot non puo' "
              "operare finche' l'optimizer non ne accumula.")
        return 1
    now = time.time()

    dist = Counter(int(r.get("pass_count", 0) or 0) for r in pairs.values())
    validated = [k for k, r in pairs.items()
                 if int(r.get("pass_count", 0) or 0) >= MIN_PASSES]
    coins = {r.get("symbol") for k, r in pairs.items() if k in validated}

    print(f"[gate] {len(pairs)} coppie tracciate · soglia {MIN_PASSES} pass · "
          f"un pass ogni {NEW_DATA_MIN_S / 3600:.0f}h di dati nuovi")
    print("  distribuzione pass: " +
          " · ".join(f"{p} pass: {n}" for p, n in sorted(dist.items())))
    print(f"  VALIDATE ora: {len(validated)} su {len(coins)} coin distinte")
    print(f"  ready dichiarato dal registro: {doc.get('ready')} "
          f"(via {doc.get('ready_by') or '—'})")

    # --- il calendario ------------------------------------------------------ #
    etas = sorted((eta_ready(r, now), k) for k, r in pairs.items())
    finite = [(t, k) for t, k in etas if t != float("inf")]

    print(f"\n--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---")
    if not finite:
        print("  Nessuna coppia ha ancora una prima conferma: non c'e' una data da "
              "calcolare.\n  Serve che l'optimizer trovi coppie che passano il gate.")
    for t, k in finite[:args.top]:
        r = pairs[k]
        stato = "GIA' VALIDATA" if t <= 0 else f"validata il {_when(t)}"
        # SE LA FINESTRA NON C'E', NON SI STAMPA UNA DATA. Sommando la settimana a un
        # `window_start` assente usciva l'8 gennaio 1970, che in mezzo a date vere
        # sembra un dato e non lo e'. Le coppie senza finestra sono quelle generate
        # dalla discovery, che fino a poco fa non passava da judge_window: la finestra
        # si apre alla prima passata dopo l'unificazione della contabilita'.
        ws = float(r.get("window_start", 0) or 0)
        fin = (f"finestra chiusa il {_when(ws + NEW_DATA_MIN_S)}" if ws > 0
               else "finestra non ancora aperta")
        print(f"  {k:<34} {int(r.get('pass_count', 0) or 0)}/{MIN_PASSES} pass · "
              f"{stato} · ultimo pass "
              f"{_when(float(r.get('last_pass_data_end', 0) or 0))} · {fin}"
              + (f" · {r.get('fail_count')} fallimenti di fila" if r.get("fail_count") else ""))

    # --- la data che interessa: quando riparte il bot ----------------------- #
    print(f"\n--- QUANDO RIPARTE IL BOT ---")
    if READY_MIN_PAIRS <= 0:
        print(f"  La via 'numero di coppie' e' DISATTIVATA (OPTIMIZER_READY_MIN_PAIRS=0):"
              f"\n  vale solo la copertura ({READY_FRACTION * 100:.0f}% dell'universo), che"
              f" con un gate severo\n  puo' non arrivare mai. Vedi docs/fase5_report.md.")
        return 0
    need = max(READY_MIN_PAIRS, MIN_COVERED)
    if len(finite) < READY_MIN_PAIRS:
        print(f"  Coppie con almeno una conferma: {len(finite)}. Ne servono "
              f"{READY_MIN_PAIRS}.\n  Finche' non ce ne sono abbastanza NON esiste una "
              f"data: prima devono passare\n  il gate, poi si conta il tempo.")
        return 0
    target = finite[READY_MIN_PAIRS - 1][0]
    giorni = (target - now) / 86400
    print(f"  Al piu' presto il {_when(target)} (fra {giorni:.1f} giorni), quando la "
          f"{READY_MIN_PAIRS}a coppia\n  raggiungerebbe {MIN_PASSES} pass.")
    print(f"  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per"
          f"\n  finestra settimanale. Chi non passa per {PURGE_FAILS} finestre intere "
          f"esce dal registro,\n  quindi la data vera puo' essere piu' in la'. Serve anche coprire "
          f">= {MIN_COVERED} coin distinte ({need} coppie\n  su coin diverse bastano).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
