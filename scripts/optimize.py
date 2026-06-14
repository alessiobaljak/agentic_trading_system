"""
Job autonomo di ottimizzazione strategie (test -> learn -> iterate).

Per ogni asset del paniere:
  * carica i dati storici (OKX/Binance/Bybit, gratis),
  * esegue il walk-forward optimizer (parametri migliori, validati out-of-sample),
  * scrive su Firebase `strategy_params/current` i parametri + l'esito OOS per
    ogni (asset, strategia), e quali coppie hanno "passato".

NESSUNA validazione manuale: il bot legge questi parametri e li applica; la
prossima esecuzione schedulata ri-ottimizza su dati freschi (i parametri migliori
cambiano nel tempo, per questo gira periodicamente).

Uso:
  python -m scripts.optimize --symbols BTCUSDT,ETHUSDT,SOLUSDT
"""
from __future__ import annotations

import argparse
import time

import requests

from backtesting.data_loader import load_candles
from backtesting.optimizer import WalkForwardOptimizer
from bot.core.firebase_client import get_firebase

FAPI = "https://fapi.binance.com"
OKX = "https://www.okx.com"


def top_symbols_by_volume(n: int) -> list[str]:
    """
    Universo = i top-N perpetual USDT per volume 24h (Layer 2: scansiona TUTTO
    l'universo, non un set fisso). Prova Binance; se bloccata (es. geo-block sui
    runner GitHub) ricade su OKX. Nessuna chiave.
    """
    # --- Binance ---
    try:
        info = requests.get(f"{FAPI}/fapi/v1/exchangeInfo", timeout=20).json()
        perp = {
            s["symbol"] for s in info.get("symbols", [])
            if s.get("contractType") == "PERPETUAL" and s.get("quoteAsset") == "USDT"
            and s.get("status") == "TRADING"
        }
        tickers = requests.get(f"{FAPI}/fapi/v1/ticker/24hr", timeout=20).json()
        if isinstance(tickers, list) and perp:
            ranked = sorted((t for t in tickers if t.get("symbol") in perp),
                            key=lambda t: float(t.get("quoteVolume", 0)), reverse=True)
            if ranked:
                return [t["symbol"] for t in ranked[:n]]
    except Exception as exc:  # noqa: BLE001
        print(f"[optimize] universo Binance non disponibile ({str(exc)[:60]}); provo OKX")

    # --- OKX fallback (USDT perpetual swap) ---
    try:
        data = requests.get(f"{OKX}/api/v5/market/tickers",
                            params={"instType": "SWAP"}, timeout=20).json().get("data", [])
        usdt = [t for t in data if t.get("instId", "").endswith("-USDT-SWAP")]
        ranked = sorted(usdt, key=lambda t: float(t.get("volCcy24h", 0) or 0), reverse=True)
        return [t["instId"].replace("-USDT-SWAP", "") + "USDT" for t in ranked[:n]]
    except Exception as exc:  # noqa: BLE001
        print(f"[optimize] universo OKX non disponibile ({str(exc)[:60]}); uso il default")
        return []


def main() -> int:
    p = argparse.ArgumentParser(description="Ottimizzazione walk-forward autonoma")
    p.add_argument("--symbols", default="BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,XRPUSDT")
    p.add_argument("--top", type=int, default=0,
                   help="se >0, ottimizza i top-N future per volume (ignora --symbols)")
    p.add_argument("--interval", default="1h")
    p.add_argument("--start", default="2023-01-01")
    p.add_argument("--end", default="2026-01-01")
    p.add_argument("--source", default="binance")
    p.add_argument("--windows", type=int, default=3)
    p.add_argument("--max-combos", type=int, default=12,
                   help="max combinazioni di parametri provate per strategia (0=tutte)")
    args = p.parse_args()

    if args.top > 0:
        symbols = top_symbols_by_volume(args.top)
        print(f"[optimize] universo: top {args.top} per volume -> {len(symbols)} coin")
    if not args.top or not symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    opt = WalkForwardOptimizer(n_windows=args.windows, max_combos=args.max_combos)
    fb = get_firebase()

    out: dict[str, dict] = {}
    summary_passed: list[str] = []

    for sym in symbols:
        print(f"\n[optimize] === {sym} ===")
        candles = load_candles(sym, args.interval, args.start, args.end, prefer=args.source)
        # storia minima: escludi token troppo recenti (validazione non affidabile su
        # poche settimane di dati). ~10000 candele 1h ≈ 14 mesi. Regolabile via env.
        min_history = int(os.getenv("OPTIMIZER_MIN_HISTORY", "10000"))
        if len(candles) < min_history:
            print(f"[optimize] {sym}: storia insufficiente ({len(candles)} < {min_history}), "
                  f"salto (token troppo recente)")
            continue
        results = opt.optimize_symbol(sym, candles)
        for r in results:
            key = f"{sym}|{r.strategy}"
            out[key] = {
                "symbol": sym, "strategy": r.strategy, "params": r.best_params,
                "oos_pf": r.oos_pf, "oos_pnl_pct": r.oos_pnl_pct,
                "oos_trades": r.oos_trades, "oos_win_rate": r.oos_win_rate,
                "passed": r.passed,
            }
            flag = "✅" if r.passed else "  "
            print(f"  {flag} {r.strategy:22s} pf={r.oos_pf:4.2f} pnl={r.oos_pnl_pct*100:+7.1f}% "
                  f"trades={r.oos_trades:4d} params={r.best_params}")
            if r.passed:
                summary_passed.append(key)

    fb.set_doc("strategy_params", "current", {
        "updated_at": time.time(),
        "entries": out,
        "passed": summary_passed,
    })

    # --- registro di validazione cumulativo (robustezza nel tempo) ---
    reg = update_registry(fb, out, summary_passed)

    cov_pct = reg["coverage"] * 100
    gate_str = ("SUPERATO ✅" if reg["ready"]
                else f"in corso ({cov_pct:.0f}% < {READY_FRACTION*100:.0f}%)")
    print("\n" + "=" * 60)
    print(f"[optimize] {len(out)} coppie valutate, {len(summary_passed)} passate in QUESTO run.")
    print(f"[optimize] REGISTRO: {reg['coins_covered']}/{reg['universe_size']} crypto "
          f"({cov_pct:.0f}%) con strategia validata (>= {MIN_PASSES} pass). GATE 1 {gate_str}")
    for k in reg["validated"]:
        print(f"   ✅ {k}  passes={reg['pairs'][k]['pass_count']}  -> {reg['pairs'][k]['last_params']}")
    print("=" * 60)

    # --- report automatico su Telegram ---
    _notify_telegram(out, summary_passed, reg)
    return 0


import os

# numero di run in cui una coppia deve passare l'OOS per essere "validata"
MIN_PASSES = int(os.getenv("OPTIMIZER_MIN_PASSES", "3"))
# GATE 1 in PERCENTUALE: pronto quando la frazione dei coin scansionati ORA che
# hanno almeno una strategia validata supera questa soglia. Si adatta se cambiano
# le crypto nell'universo (non un numero fisso). Regolabile via env.
READY_FRACTION = float(os.getenv("OPTIMIZER_READY_FRACTION", "0.60"))
# minimi di sicurezza: non dichiarare "ready" se l'universo è troppo piccolo o se
# le crypto validate in assoluto sono troppo poche.
MIN_UNIVERSE = int(os.getenv("OPTIMIZER_MIN_UNIVERSE", "10"))
MIN_COVERED = int(os.getenv("OPTIMIZER_MIN_COVERED", "5"))
# una coppia resta "validata" solo se rivista entro questi giorni (auto-pulizia:
# i coin usciti dall'universo decadono e il bot smette di operarli).
FRESH_DAYS = float(os.getenv("OPTIMIZER_FRESH_DAYS", "3"))


def update_registry(fb, out: dict, passed_now: list[str]) -> dict:
    """
    Accumula nel tempo: ogni run incrementa il pass_count delle coppie che passano.
    Una coppia è VALIDATA con pass_count >= MIN_PASSES. Il modello è "ready" quando
    ci sono strategie validate su >= READY_COINS crypto distinte.
    """
    doc = fb.get_doc("strategy_registry", "validated") or {}
    pairs: dict = doc.get("pairs", {}) or {}
    passed_set = set(passed_now)

    for key, e in out.items():
        rec = pairs.get(key, {"pass_count": 0})
        if key in passed_set:
            rec["pass_count"] = rec.get("pass_count", 0) + 1
            rec["last_params"] = e["params"]
            rec["last_pf"] = e["oos_pf"]
            rec["last_pnl_pct"] = e["oos_pnl_pct"]
            rec["last_trades"] = e["oos_trades"]
            rec["last_passed_at"] = time.time()
        rec["symbol"] = e["symbol"]
        rec["strategy"] = e["strategy"]
        rec["last_seen_at"] = time.time()
        pairs[key] = rec

    validated = sorted(
        k for k, r in pairs.items()
        if r.get("pass_count", 0) >= MIN_PASSES
        and (time.time() - r.get("last_seen_at", 0)) < FRESH_DAYS * 86400
    )
    validated_coins = {pairs[k]["symbol"] for k in validated}

    # universo SCANSIONATO in questo run (denominatore della percentuale)
    current_coins = sorted({e["symbol"] for e in out.values()})
    covered = [c for c in current_coins if c in validated_coins]
    coverage = (len(covered) / len(current_coins)) if current_coins else 0.0
    ready = (coverage >= READY_FRACTION
             and len(current_coins) >= MIN_UNIVERSE
             and len(covered) >= MIN_COVERED)

    registry = {
        "updated_at": time.time(),
        "pairs": pairs,
        "validated": validated,
        "coins_covered": len(covered),
        "coins": covered,
        "universe_size": len(current_coins),
        "coverage": round(coverage, 3),
        "ready": ready,
        "min_passes": MIN_PASSES,
        "ready_fraction": READY_FRACTION,
        "min_universe": MIN_UNIVERSE,
        "min_covered": MIN_COVERED,
    }
    fb.set_doc("strategy_registry", "validated", registry)
    return registry


def _notify_telegram(out: dict, passed: list[str], reg: dict) -> None:
    try:
        from bot.execution.notifier import TelegramNotifier
        notifier = TelegramNotifier()
        top = sorted((out[k] for k in passed), key=lambda e: e["oos_pnl_pct"], reverse=True)[:8]
        cov_pct = reg["coverage"] * 100
        lines = ["🧠 <b>Ottimizzazione completata</b>",
                 f"{len(passed)}/{len(out)} coppie passate in questo run (netto fee).",
                 f"📚 GATE 1: <b>{reg['coins_covered']}/{reg['universe_size']} crypto "
                 f"({cov_pct:.0f}%)</b> con strategia validata "
                 f"(obiettivo {reg['ready_fraction']*100:.0f}%).", ""]
        if top:
            lines.append("<b>Migliori in questo run:</b>")
            for e in top:
                lines.append(f"• {e['symbol']} · {e['strategy']} · pf {e['oos_pf']:.2f} · "
                             f"{e['oos_pnl_pct']*100:+.0f}%")
        if reg["ready"]:
            lines += ["", "🎯 <b>GATE 1 SUPERATO</b>: modello validato su abbastanza crypto. "
                      "Si può passare al PAPER TRADING."]
        notifier.send("\n".join(lines))
    except Exception as exc:  # noqa: BLE001
        print(f"[optimize] notifica Telegram saltata: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
