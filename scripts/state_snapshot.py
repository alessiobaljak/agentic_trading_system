"""
Snapshot dello stato del sistema da Firebase -> file nel repo (docs/state.md).

Pensato per girare in GitHub Actions (che ha il secret Firebase): legge ciò che
la VPS ha scritto su Firebase (risultati ottimizzazione, stato bot, posizioni) e
produce un riepilogo leggibile. Il workflow poi committa il file nel repo, così:
  * tu lo vedi dal repo/telefono ovunque tu sia (anche senza SSH);
  * io lo leggo da qui con un semplice `git pull`.

Uso: python -m scripts.state_snapshot
"""
from __future__ import annotations

import time
from datetime import datetime, timezone

from bot.core.firebase_client import get_firebase

OUT = "docs/state.md"


def _ts(v) -> str:
    try:
        return datetime.fromtimestamp(float(v), tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:  # noqa: BLE001
        return "—"


def build() -> str:
    fb = get_firebase()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# Stato sistema (snapshot)", f"_Generato: {now}_", ""]

    # --- stato bot (RTDB) ---
    status = fb.get_rtdb("/bot_status") or {}
    hb = status.get("heartbeat")
    online = hb and (time.time() - float(hb) < 180)
    lines += [
        "## Bot",
        f"- stato: **{status.get('state', '—')}** ({'🟢 online' if online else '🔴 offline'})",
        f"- regime: {status.get('regime', '—')}",
        f"- DRY_RUN: {status.get('dry_run', '—')}",
        f"- ultimo heartbeat: {_ts(hb)}",
        "",
    ]

    # --- posizioni aperte (RTDB) ---
    positions = fb.get_rtdb("/positions") or {}
    if isinstance(positions, dict) and positions:
        lines.append("## Posizioni aperte")
        for sym, p in positions.items():
            if not isinstance(p, dict):
                continue
            lines.append(f"- {sym}: {p.get('direction')} qty={p.get('quantity')} "
                         f"@ {p.get('entry_price')} uPnL={p.get('unrealized_pnl')}")
        lines.append("")

    # --- GATE 1: registro di validazione cumulativo ---
    reg = fb.get_doc("strategy_registry", "validated") or {}
    pairs = reg.get("pairs", {}) or {}
    validated = reg.get("validated", []) or []
    ready = reg.get("ready", False)
    cov = reg.get("coverage", 0) * 100
    target = reg.get("ready_fraction", 0.6) * 100
    lines += [
        "## GATE 1 — Validazione strategie",
        f"- stato: **{'✅ SUPERATO — pronti per il paper trading' if ready else '🔄 in corso'}**",
        f"- copertura universo: **{reg.get('coins_covered', 0)}/{reg.get('universe_size', 0)} "
        f"crypto ({cov:.0f}%)** · obiettivo ≥ {target:.0f}%",
        f"- coppie validate (>= {reg.get('min_passes', 3)} pass OOS): **{len(validated)}**",
        f"- universo scansionato: {', '.join(reg.get('universe_coins', [])) or '—'}",
        f"- aggiornato: {_ts(reg.get('updated_at'))}",
        "",
    ]
    if validated:
        lines.append("### Strategie VALIDATE (operate dal bot)")
        lines.append("| Coin | Strategia | Passes | PF | PnL OOS | Parametri |")
        lines.append("|---|---|---|---|---|---|")
        rows = sorted((pairs[k] for k in validated),
                      key=lambda e: e.get("last_pnl_pct", 0), reverse=True)
        for e in rows:
            params = ", ".join(f"{k}={v}" for k, v in (e.get("last_params") or {}).items())
            lines.append(f"| {e.get('symbol')} | {e.get('strategy')} | {e.get('pass_count')} | "
                         f"{e.get('last_pf')} | {e.get('last_pnl_pct', 0)*100:.0f}% | {params} |")
        lines.append("")

    # --- ultimo run (snapshot corrente) ---
    sp = fb.get_doc("strategy_params", "current") or {}
    entries = sp.get("entries", {}) or {}
    passed = sp.get("passed", []) or []
    lines += [
        "## Ultimo run di ottimizzazione",
        f"_aggiornato: {_ts(sp.get('updated_at'))} · {len(entries)} coppie valutate, "
        f"{len(passed)} passate in questo run_",
        "",
    ]
    if entries:
        rows = sorted((entries[k] for k in passed if k in entries),
                      key=lambda e: e.get("oos_pnl_pct", 0), reverse=True)
        if rows:
            lines.append("| Coin | Strategia | PF | PnL OOS | Trade | Win |")
            lines.append("|---|---|---|---|---|---|")
            for e in rows:
                lines.append(f"| {e.get('symbol')} | {e.get('strategy')} | "
                             f"{e.get('oos_pf')} | {e.get('oos_pnl_pct', 0)*100:.0f}% | "
                             f"{e.get('oos_trades')} | {e.get('oos_win_rate', 0)*100:.0f}% |")
        else:
            lines.append("_Nessuna coppia ha passato in questo run._")
    else:
        lines.append("_Nessun risultato di ottimizzazione ancora presente su Firebase._")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    content = build()
    print(content)
    import os
    os.makedirs("docs", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n[snapshot] scritto {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
