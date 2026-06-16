"""
Azzera SOLO lo stato del PAPER TRADING per ripartire da una situazione pulita
dopo una fix. Da usare col bot FERMO.

Cancella:
  * /positions            (RTDB)  posizioni aperte
  * collection 'trades'   (FS)    trade chiusi
  * /risk_state           (RTDB)  contatori circuit breaker (PnL giorno/settimana)
  * /account/equity       (RTDB)  reimpostata all'equity iniziale di paper
  * /bot_status           (RTDB)  verrà riscritto dal bot al riavvio
  * /commands/kill_switch (RTDB)  riportato a False

NON tocca (resta tutto): strategy_registry/validated (GATE 1), strategy_params,
strategy_weights, memory, insights, user_risk_settings.

Uso sulla VPS:
    systemctl stop trading-bot
    .venv/bin/python -m scripts.reset_paper            # dry-run: mostra e basta
    .venv/bin/python -m scripts.reset_paper --yes      # esegue davvero
    systemctl start trading-bot
"""
from __future__ import annotations

import argparse

from bot.core.firebase_client import get_firebase

START_EQUITY = 10_000.0

KEEP = [
    "strategy_registry", "strategy_params", "strategy_weights",
    "memory", "insights", "user_risk_settings",
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Reset dello stato paper trading.")
    ap.add_argument("--yes", action="store_true", help="conferma ed esegue la cancellazione")
    ap.add_argument("--equity", type=float, default=START_EQUITY,
                    help=f"equity paper iniziale (default {START_EQUITY:g})")
    args = ap.parse_args()

    fb = get_firebase()
    n_trades = len(fb.list_doc_ids("trades"))
    positions = fb.get_rtdb("/positions") or {}
    n_pos = len(positions) if isinstance(positions, dict) else 0

    print("[reset] AZZERO:  /positions, collection 'trades', /risk_state, "
          "/account/equity, /bot_status, /commands/kill_switch")
    print(f"[reset] CONSERVO: {', '.join(KEEP)}")
    print(f"[reset] stato attuale: {n_pos} posizioni aperte, {n_trades} trade chiusi")

    if not args.yes:
        print("\n[reset] DRY-RUN: niente cancellato. Aggiungi --yes per eseguire.")
        return 0

    fb.set_rtdb("/positions", None)
    for tid in fb.list_doc_ids("trades"):
        fb.delete_doc("trades", tid)
    fb.set_rtdb("/risk_state", None)
    fb.set_rtdb("/account/equity", args.equity)
    fb.set_rtdb("/account/starting_equity", args.equity)
    fb.set_rtdb("/bot_status", None)
    fb.set_rtdb("/commands/kill_switch", False)

    print(f"[reset] FATTO. Rimosse {n_pos} posizioni e {n_trades} trade chiusi. "
          f"Equity paper = {args.equity:g}. Le strategie validate (GATE 1) restano.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
