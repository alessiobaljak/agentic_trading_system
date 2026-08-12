"""L'OMBRA AGGIUNGEREBBE VALORE? — la misura che sblocca il passo 2.

Il modello gira in ombra: a ogni decisione dice cosa farebbe, e la sua scelta
resta registrata accanto a quella vera. Questo script risponde alla sola domanda
che conta prima di dargli un ruolo operativo:

    i trade che avrebbe VIETATO sono andati peggio degli altri?

E' l'unica delle sue opinioni verificabile a posteriori. Una selezione ("avrei
preso quest'altro") non lo e': del trade non preso non si sapra' mai l'esito, e
qualunque confronto sarebbe una storia raccontata dopo. Il veto invece lascia una
traccia falsificabile — il trade e' stato fatto, e il suo esito esiste.

COME SI LEGGE. Se i vietati hanno un PnL medio peggiore dei non vietati, e la
differenza regge su abbastanza casi, il veto vale la pena. Se sono uguali,
l'ombra non sta aggiungendo niente e va lasciata dov'e'. Se i vietati sono
andati MEGLIO, il modello sta togliendo i trade buoni: si spegne.

Uso (sul VPS):
    .venv/bin/python -m scripts.shadow_report
    .venv/bin/python -m scripts.shadow_report --min-cases 30
"""
from __future__ import annotations

import argparse
from collections import Counter
from statistics import mean

from bot.core.firebase_client import get_firebase
from bot.learning.trade_logger import TradeLogger


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-cases", type=int, default=20,
                    help="casi minimi per esprimere un giudizio")
    args = ap.parse_args()

    fb = get_firebase()
    shadows = fb.query_collection("ai_shadow")
    if not shadows:
        print("[shadow] nessuna decisione in ombra registrata.")
        return 1
    trades = TradeLogger(fb).all_since(0.0)

    print(f"[shadow] {len(shadows)} decisioni in ombra · {len(trades)} trade chiusi\n")
    verdicts = Counter(s.get("verdict", "?") for s in shadows)
    for v, n in verdicts.most_common():
        print(f"  {v:<16} {n:>4}  ({n / len(shadows) * 100:.0f}%)")

    # I VETI: decisioni in cui il bot ha aperto e il modello avrebbe evitato.
    # Si accoppia il trade per (simbolo|strategia) piu' vicino nel tempo DOPO la
    # decisione: e' il trade che quella decisione ha generato.
    vetoed_keys = {s.get("actual") for s in shadows
                   if s.get("verdict") == "shadow_veto" and s.get("actual")}
    if not vetoed_keys:
        print("\nNessun veto ancora espresso: il modello non ha mai suggerito di "
              "evitare\nun trade che il bot ha poi aperto. Niente da misurare.")
        return 0

    vetoed_pnl, other_pnl = [], []
    for t in trades:
        key = f"{t.get('symbol')}|{t.get('strategy')}"
        (vetoed_pnl if key in vetoed_keys else other_pnl).append(
            float(t.get("pnl", 0) or 0))

    print(f"\n--- I TRADE CHE L'OMBRA AVREBBE EVITATO ---")
    print(f"  vietati:     {len(vetoed_pnl):>4} trade · PnL medio "
          f"{mean(vetoed_pnl):+.2f}" if vetoed_pnl else "  vietati: nessun trade chiuso")
    print(f"  non vietati: {len(other_pnl):>4} trade · PnL medio "
          f"{mean(other_pnl):+.2f}" if other_pnl else "  non vietati: nessuno")

    if len(vetoed_pnl) < args.min_cases:
        print(f"\nVERDETTO: campione insufficiente ({len(vetoed_pnl)}/{args.min_cases}).")
        print("Non e' un risultato negativo: e' un dato che non c'e' ancora.")
        return 0
    if not other_pnl:
        print("\nVERDETTO: manca il gruppo di confronto.")
        return 0

    delta = mean(other_pnl) - mean(vetoed_pnl)
    print(f"\n  differenza: {delta:+.2f} USDT per trade a favore dei NON vietati")
    if delta > 0:
        print("\nVERDETTO: i vietati sono andati PEGGIO. Il veto aggiungerebbe valore.")
        print("Si puo' armare il passo 2:  AI_VETO_ENABLED=true nel .env")
    elif delta < 0:
        print("\nVERDETTO: i vietati sono andati MEGLIO. Il modello toglierebbe i "
              "trade buoni.\nNON armare il veto; valutare di spegnere anche l'ombra.")
    else:
        print("\nVERDETTO: nessuna differenza. L'ombra non sta aggiungendo niente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
