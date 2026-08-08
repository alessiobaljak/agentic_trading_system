"""
DOVE ARRIVA DAVVERO IL PREZZO — distribuzione dell'escursione favorevole in unita' di R.

A cosa serve: decidere se una scala di TP e' raggiungibile per una coppia. R e' gia'
normalizzato sulla volatilita' (R = atr_mult x ATR), quindi la domanda non e' "quanto
e' volatile la coin" ma "quanto TENDE, in unita' della sua volatilita'". Questo report
risponde con i dati, invece di tarare la scala a intuito.

Il dato chiave e' `mfe_r`, registrato su ogni trade chiuso: il massimo raggiunto a
favore, in R. Da quell'unico numero si sa quali gradini AVREBBE colpito QUALUNQUE
scala — senza doverle provare una per una ne' sacrificare trade per esplorare.

Uso (sul VPS):
    .venv/bin/python -m scripts.mfe_report
    .venv/bin/python -m scripts.mfe_report --by pair --min-trades 5
"""
from __future__ import annotations

import argparse
from collections import defaultdict

from bot.core.firebase_client import get_firebase
from bot.execution.exit_logic import SCALE_LADDER_CANDIDATES
from bot.config import settings
from bot.learning.trade_logger import TradeLogger

# soglie su cui riportare la frazione di trade che le raggiunge
REACH = (0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0)


def _pct(a: int, b: int) -> str:
    return f"{a / b * 100:4.0f}%" if b else "   —"


def banked_r(mfe: float, mults, fracs) -> float:
    """R incassati da una scala, dato il massimo raggiunto (MODELLO SEMPLIFICATO).

    Ipotesi dichiarate: i gradini con multiplo <= mfe si riempiono; la frazione residua
    esce a BREAK-EVEN (0R) se almeno un gradino si e' riempito, altrimenti il trade e'
    una perdita piena (-1R). E' CONSERVATIVO sul residuo (non gli attribuisce mai un
    guadagno) e serve solo a SCEGLIERE LE CANDIDATE: la validazione vera la fa il gate,
    che simula il percorso completo con lo stop che si sposta."""
    filled = [(m, f) for m, f in zip(mults, fracs) if m <= mfe + 1e-12]
    if not filled:
        return -1.0
    banked = sum(m * f for m, f in filled)
    return banked            # il residuo esce a break-even -> non aggiunge nulla


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--by", choices=("strategy", "pair", "symbol"), default="strategy",
                    help="granularita' del raggruppamento")
    ap.add_argument("--min-trades", type=int, default=3,
                    help="gruppi con meno trade di cosi' non vengono mostrati")
    ap.add_argument("--limit", type=int, default=40, help="quanti gruppi mostrare")
    args = ap.parse_args()

    fb = get_firebase()
    trades = TradeLogger(fb).all_since(0.0)
    if not trades:
        print("[mfe] nessun trade chiuso trovato.")
        return 1

    usable = [t for t in trades if t.get("mfe_r") is not None]
    print(f"[mfe] trade chiusi: {len(trades)} · con mfe_r registrato: {len(usable)}")
    if not usable:
        print("[mfe] Nessun trade porta ancora `mfe_r`: il campo si popola sui trade")
        print("      chiusi DOPO l'aggiornamento del bot. Riprova tra qualche chiusura.")
        return 1
    print(f"[mfe] scala globale attuale: {tuple(settings.SCALE_OUT_R_MULTIPLES)} "
          f"quote {tuple(settings.SCALE_OUT_FRACTIONS)}\n")

    def key(t: dict) -> str:
        if args.by == "strategy":
            return t.get("strategy", "?")
        if args.by == "symbol":
            return t.get("symbol", "?")
        return f"{t.get('symbol', '?')}|{t.get('strategy', '?')}"

    groups: dict[str, list[float]] = defaultdict(list)
    for t in usable:
        try:
            groups[key(t)].append(float(t["mfe_r"]))
        except (TypeError, ValueError):
            continue

    rows = [(k, v) for k, v in groups.items() if len(v) >= args.min_trades]
    rows.sort(key=lambda kv: -len(kv[1]))
    shown = sum(len(v) for _, v in rows)
    if shown < len(usable):
        print(f"[mfe] {len(usable) - shown} trade su {len(usable)} sono in gruppi sotto "
              f"--min-trades {args.min_trades} e NON compaiono nelle righe per gruppo "
              f"(compaiono solo nel TOTALE).")
    # TOTALE sempre in testa: con i trade sparsi su molti gruppi le righe per gruppo
    # sono tutte sotto soglia e l'aggregato e' l'unico numero con una statistica.
    # Va letto per primo: dice se l'edge c'e', prima di chiedersi DOVE sia.
    all_vals = [v for vals in groups.values() for v in vals]
    rows = [("TOTALE (tutti i trade)", all_vals)] + rows

    # --- 1) quanto lontano arriva il prezzo -------------------------------- #
    head = "gruppo".ljust(34) + "n".rjust(4) + "  mediana" + \
        "".join(f"  ≥{r:g}R".rjust(7) for r in REACH)
    print(head)
    print("-" * len(head))
    for k, vals in rows[: args.limit]:
        vals_sorted = sorted(vals)
        med = vals_sorted[len(vals_sorted) // 2]
        line = k[:33].ljust(34) + str(len(vals)).rjust(4) + f"{med:9.2f}"
        for r in REACH:
            line += _pct(sum(1 for v in vals if v >= r), len(vals)).rjust(7)
        print(line)

    # --- 2) quale scala avrebbe incassato di piu' -------------------------- #
    fracs = tuple(settings.SCALE_OUT_FRACTIONS)
    print(f"\nR medi incassati per scala (modello semplificato, quote {fracs}):")
    head2 = "gruppo".ljust(34) + "n".rjust(4) + \
        "".join(f"  {'/'.join(f'{m:g}' for m in c)}".rjust(14) for c in SCALE_LADDER_CANDIDATES)
    print(head2)
    print("-" * len(head2))
    for k, vals in rows[: args.limit]:
        line = k[:33].ljust(34) + str(len(vals)).rjust(4)
        scores = [sum(banked_r(v, c, fracs) for v in vals) / len(vals)
                  for c in SCALE_LADDER_CANDIDATES]
        best = max(range(len(scores)), key=lambda i: scores[i])
        for i, sc in enumerate(scores):
            cell = f"{sc:+.3f}" + (" *" if i == best else "  ")
            line += cell.rjust(14)
        print(line)

    print("\n(*) scala col miglior R medio in questo gruppo, secondo il modello")
    print("    semplificato: gradini raggiunti = incassati, residuo a break-even.")
    print("    Serve a SCEGLIERE le candidate — la validazione vera la fa il GATE,")
    print("    che simula il percorso completo con lo stop che si sposta.")
    print("    Campioni piccoli non decidono nulla: guardare la colonna n.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
