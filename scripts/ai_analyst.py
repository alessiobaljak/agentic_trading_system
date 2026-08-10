"""ANALISTA NOTTURNO — il post-mortem che finora facevamo a mano.

Mette accanto la promessa del GATE 1 e il vissuto del paper, e scrive cosa non
torna. I difetti trovati in questi giorni (la coda >=3R che non si ripete, il
freno di deriva che non scattava, il PF misurato con una scala diversa da quella
eseguita) non erano leggibili in nessuna singola metrica: emergevano solo
incrociandone piu' di una. E' quel lavoro qui.

NON TOCCA NULLA: legge da Firestore, scrive un solo documento (`ai_reports`),
non modifica registro ne' posizioni. Le sue ipotesi sono sospetti da verificare
col gate o con gli script, mai azioni.

Uso (sul VPS, o da cron notturno):
    .venv/bin/python -m scripts.ai_analyst
    .venv/bin/python -m scripts.ai_analyst --days 7 --dry-run
"""
from __future__ import annotations

import argparse
import json
import time

from bot.ai.analyst import analyze, build_digest
from bot.ai.client import available
from bot.core.firebase_client import decode_pairs, get_firebase
from bot.learning.trade_logger import TradeLogger


def _print_report(rep: dict) -> None:
    print(f"\n=== VERDETTO ({rep.get('fiducia', '?')} fiducia) ===")
    print(rep.get("verdetto", "—"))
    for key, title in (("osservazioni", "OSSERVAZIONI"), ("ipotesi", "IPOTESI DA VERIFICARE")):
        items = rep.get(key) or []
        if not items:
            continue
        print(f"\n=== {title} ===")
        for i, o in enumerate(items, 1):
            if key == "osservazioni":
                print(f"{i}. {o.get('titolo', '')}")
                print(f"   evidenza: {o.get('evidenza', '')}")
                print(f"   solidita': {o.get('quanto_e_solido', '')}")
            else:
                print(f"{i}. {o.get('ipotesi', '')}")
                print(f"   come verificarla: {o.get('come_verificarla', '')}")
                print(f"   cosa la smentirebbe: {o.get('cosa_la_smentirebbe', '')}")
    limits = rep.get("cosa_non_si_puo_dire") or []
    if limits:
        print("\n=== COSA I DATI NON DICONO ===")
        for x in limits:
            print(f"- {x}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=float, default=0,
                    help="finestra di trade da analizzare (0 = tutti)")
    ap.add_argument("--dry-run", action="store_true",
                    help="stampa solo il digest, senza chiamare il modello")
    args = ap.parse_args()

    fb = get_firebase()
    since = (time.time() - args.days * 86400) if args.days > 0 else 0.0
    trades = TradeLogger(fb).all_since(since)
    if not trades:
        print("[analyst] nessun trade chiuso da analizzare.")
        return 1

    pairs = decode_pairs((fb.get_doc("strategy_registry", "validated") or {}).get("pairs"))
    drift = fb.get_doc("drift", "current") or {}
    calib = fb.get_doc("calibration", "current") or {}
    equity = (fb.get_rtdb("/bot_status") or {}).get("equity")

    if args.dry_run:
        print(build_digest(trades, pairs, drift, calib, equity))
        return 0
    if not available():
        print("[analyst] AI non disponibile (ANTHROPIC_API_KEY assente o AI_ENABLED=false).")
        print("          Ecco comunque il digest fattuale:\n")
        print(build_digest(trades, pairs, drift, calib, equity))
        return 1

    rep = analyze(trades, pairs, drift, calib, equity)
    if not rep:
        print("[analyst] nessun report prodotto.")
        return 1
    _print_report(rep)

    # lo storico serve: due report a distanza di giorni dicono se un'ipotesi ha
    # retto o e' evaporata, che e' l'unico modo di valutare l'analista stesso.
    fb.set_doc("ai_reports", "latest", rep)
    fb.set_doc("ai_reports", time.strftime("%Y-%m-%d", time.gmtime()), rep)
    print(f"\n[analyst] report salvato su ai_reports/latest ({len(trades)} trade)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
