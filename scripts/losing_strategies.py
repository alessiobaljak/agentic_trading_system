"""
Diagnostica: quali strategie in PRODUZIONE (paper) stanno accumulando perdite.

Legge tutti i trade chiusi da Firestore (`trades`) e per ogni strategia riporta:
  * trade totali, vittorie, perdite, win-rate
  * PnL netto realizzato
  * streak di perdite CONSECUTIVE corrente (le ultime N chiuse di fila in perdita)

Serve a capire cosa zavorra il paper. NON modifica nulla: sola lettura.

Uso sulla VPS (dove ci sono le credenziali Firebase):
    .venv/bin/python -m scripts.losing_strategies
    .venv/bin/python -m scripts.losing_strategies --min-losses 5   # solo >= 5 perdite
    .venv/bin/python -m scripts.losing_strategies --by-coin        # dettaglio strategia x coin
"""
from __future__ import annotations

import argparse
from collections import defaultdict

from bot.core.firebase_client import get_firebase


def _is_loss(t: dict) -> bool:
    # preferisci il flag esplicito; fallback sul segno del PnL
    if "is_win" in t:
        return not bool(t["is_win"])
    return float(t.get("pnl", 0.0)) < 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Strategie in perdita (paper).")
    ap.add_argument("--min-losses", type=int, default=0,
                    help="mostra solo le strategie con almeno N perdite totali")
    ap.add_argument("--by-coin", action="store_true",
                    help="raggruppa per (strategia, coin) invece che per sola strategia")
    args = ap.parse_args()

    fb = get_firebase()
    trades = fb.query_collection("trades", order_by="exit_ts")
    if not trades:
        print("Nessun trade chiuso trovato nella collection 'trades'.")
        return 0
    # ordina CRONOLOGICO ascendente noi stessi: il client live ritorna newest-first,
    # ma la streak consecutiva va calcolata dal piu' vecchio al piu' recente.
    trades.sort(key=lambda t: t.get("exit_ts", 0))

    def key(t: dict) -> str:
        s = t.get("strategy", "?")
        return f"{s} | {t.get('symbol', '?')}" if args.by_coin else s

    groups: dict[str, list[dict]] = defaultdict(list)
    for t in trades:  # gia' ordinati per exit_ts asc
        groups[key(t)].append(t)

    rows = []
    for k, ts in groups.items():
        losses = sum(1 for t in ts if _is_loss(t))
        wins = len(ts) - losses
        net = sum(float(t.get("pnl", 0.0)) for t in ts)
        # streak di perdite consecutive corrente: dalla piu' recente all'indietro
        streak = 0
        for t in reversed(ts):
            if _is_loss(t):
                streak += 1
            else:
                break
        rows.append({
            "key": k, "n": len(ts), "wins": wins, "losses": losses,
            "win_rate": wins / len(ts) if ts else 0.0, "net": net, "streak": streak,
        })

    rows = [r for r in rows if r["losses"] >= args.min_losses]
    rows.sort(key=lambda r: (r["losses"], -r["net"]), reverse=True)

    title = "strategia x coin" if args.by_coin else "strategia"
    print(f"\n{'':<38}  {'trade':>5} {'W':>4} {'L':>4} {'win%':>5} {'PnL netto':>11} {'streak':>7}")
    print(f"{title:<38}  " + "-" * 45)
    for r in rows:
        flag = "  <== 5+ perdite" if r["losses"] >= 5 else ""
        print(f"{r['key']:<38}  {r['n']:>5} {r['wins']:>4} {r['losses']:>4} "
              f"{r['win_rate']*100:>4.0f}% {r['net']:>11.2f} {r['streak']:>7}{flag}")

    n_flag = sum(1 for r in rows if r["losses"] >= 5)
    print(f"\n{len(rows)} {title} mostrate · {n_flag} con >= 5 perdite totali.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
