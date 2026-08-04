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

from bot.core.firebase_client import decode_pairs, get_firebase

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
    equity = fb.get_rtdb("/account/equity")
    eq_str = f"${float(equity):,.2f}" if equity is not None else "—"
    lines += [
        "## Bot",
        f"- stato: **{status.get('state', '—')}** ({'🟢 online' if online else '🔴 offline'})",
        f"- regime: {status.get('regime', '—')}",
        f"- DRY_RUN: {status.get('dry_run', '—')}",
        f"- equity: **{eq_str}**",
        f"- ultimo heartbeat: {_ts(hb)}",
        # sorgente prezzi: True = stream vivo (ogni variazione, in ordine);
        # False = ripiego sulle candele 1m (tocchi si', ordine no)
        f"- stream prezzi: {'🟢 attivo' if status.get('price_stream') else '🟡 candele REST'}",
        "",
    ]

    # --- ultima decisione orchestratore (RTDB) ---
    dec = fb.get_rtdb("/decision_status") or {}
    if isinstance(dec, dict) and dec:
        outcome = dec.get("outcome", "—")
        icon = "🟢 APERTA" if outcome == "opened" else "⚪ FLAT"
        best = ""
        if dec.get("best_symbol"):
            best = (f" · miglior segnale {dec.get('best_symbol')} {dec.get('best_strategy','')} "
                    f"(conf. {dec.get('best_adjusted')}/soglia {dec.get('threshold')})")
        lines += [
            "## Ultima decisione",
            f"- esito: **{icon}** ({_ts(dec.get('ts'))})",
            f"- motivo: {dec.get('reason', '—')}",
            f"- asset valutati: {dec.get('assets_evaluated', 0)} · "
            f"segnali: {dec.get('signals_found', 0)}{best}",
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
    pairs = decode_pairs(reg.get("pairs"))
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
    # entries/passed sono CODIFICATI come stringa JSON (limite indici Firestore):
    # decode_pairs legge sia il nuovo formato-stringa sia il vecchio dict/list.
    entries = decode_pairs(sp.get("entries"))
    passed = decode_pairs(sp.get("passed")) or []
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
    lines += _closed_trades_section(fb)
    lines += _drift_section(fb)
    return "\n".join(lines)


def _drift_section(fb) -> list[str]:
    """Deriva: dove il VISSUTO contraddice la PROMESSA del gate. E' l'anello di
    ritorno paper -> gate, quindi va visto senza SSH."""
    try:
        doc = fb.get_doc("drift", "current") or {}
    except Exception as exc:  # noqa: BLE001
        return ["## Deriva paper vs gate", f"_non leggibile: {exc}_", ""]
    if not doc or not (doc.get("pairs") or doc.get("strategies")):
        return ["## Deriva paper vs gate",
                "_nessun verdetto ancora: servono trade chiusi su coppie validate._", ""]
    out = ["## Deriva paper vs gate",
           "_il gate promette sulla storia, il paper misura il presente. `drift` = "
           "promessa contraddetta -> size/leva frenate subito e fallimento al gate "
           "alla prossima passata._", ""]
    g = doc.get("global") or {}
    if g:
        out += [f"- **globale**: {g.get('verdict', '—')} · {g.get('trades', 0)} trade · "
                f"PF vissuto {g.get('live_pf')} vs {g.get('expected_pf')} atteso"
                + (f" · mfe mediana {g['mfe_median']}R" if g.get("mfe_median") else ""), ""]
    rows = [(k, v) for k, v in (doc.get("pairs") or {}).items()
            if v.get("verdict") in ("drift", "watch")]
    rows.sort(key=lambda kv: (kv[1]["verdict"] != "drift", -kv[1].get("trades", 0)))
    if rows:
        out += ["| Coppia | Verdetto | Trade | PF vissuto/atteso | Motivo |",
                "|---|---|---|---|---|"]
        for k, v in rows[:20]:
            out.append(f"| {k} | {v['verdict']} | {v['trades']} | "
                       f"{v['live_pf']} / {v['expected_pf']} | {v['reason']} |")
        out.append("")
    strat = [(k, v) for k, v in (doc.get("strategies") or {}).items()
             if v.get("verdict") == "drift"]
    if strat:
        out += ["- strategie in deriva: "
                + ", ".join(f"**{k}** ({v['trades']} trade, PF {v['live_pf']})"
                            for k, v in strat), ""]
    return out


_EXIT_LABEL = {
    "take_profit": "Take profit (fino all'ultimo gradino)",
    "scale_out": "Scale-out (>=1 TP incassato, residuo a BE)",
    "trailing_stop": "Trailing stop",
    "stop_loss": "Stop loss (prima di qualsiasi TP)",
    "time_exit": "Time exit (orizzonte scaduto)",
    "manual": "Manuale", "kill_switch": "Kill switch", "circuit_breaker": "Circuit breaker",
}


def _closed_trades_section(fb) -> list[str]:
    """PERCHE' usciamo dai trade: e' la diagnosi piu' diretta di come sta andando.

    - la distribuzione di `exit_reason` dice se veniamo stoppati PRIMA di incassare
      qualcosa (stop_loss) o se usciamo dopo aver bancato dei TP (scale_out);
    - `scale_stage_reached` dice quanti gradini della scala vengono davvero raggiunti;
    - `mfe_r` dice DOVE arriva il prezzo in unita' di R: e' il dato su cui si decide
      se una scala di TP e' raggiungibile per quelle coppie.
    """
    from collections import Counter
    try:
        from bot.learning.trade_logger import TradeLogger
        trades = TradeLogger(fb).all_since(0.0)
    except Exception as exc:  # noqa: BLE001
        return ["## Trade chiusi", f"_non leggibili: {exc}_", ""]
    if not trades:
        return ["## Trade chiusi", "_nessun trade chiuso._", ""]

    n = len(trades)
    pnl = sum(float(t.get("pnl", 0) or 0) for t in trades)
    wins = sum(1 for t in trades if float(t.get("pnl", 0) or 0) > 0)
    out = ["## Trade chiusi — perché usciamo",
           f"- totale: **{n}** · vinti: {wins} ({wins / n * 100:.0f}%) · "
           f"PnL realizzato: **{pnl:+.2f}**", ""]

    reasons = Counter(str(t.get("exit_reason", "?")) for t in trades)
    out += ["| Uscita | Trade | % | PnL |", "|---|---|---|---|"]
    for r, c in reasons.most_common():
        rp = sum(float(t.get("pnl", 0) or 0) for t in trades
                 if str(t.get("exit_reason", "?")) == r)
        out.append(f"| {_EXIT_LABEL.get(r, r)} | {c} | {c / n * 100:.0f}% | {rp:+.2f} |")
    out.append("")

    stages = [int(t.get("scale_stage_reached", 0) or 0) for t in trades
              if t.get("scale_stage_reached") is not None]
    if stages:
        sc = Counter(stages)
        tot = len(stages)
        desc = " · ".join(f"{k} TP: {sc.get(k, 0)} ({sc.get(k, 0) / tot * 100:.0f}%)"
                          for k in sorted(sc))
        out += [f"- gradini raggiunti (su {tot} trade): {desc}", ""]

    mfes = sorted(float(t["mfe_r"]) for t in trades if t.get("mfe_r") is not None)
    if mfes:
        med = mfes[len(mfes) // 2]
        reach = " · ".join(f"≥{r:g}R: {sum(1 for v in mfes if v >= r) / len(mfes) * 100:.0f}%"
                           for r in (1.0, 1.5, 3.0, 5.0))
        out += [f"- escursione favorevole (mfe_r, {len(mfes)} trade): mediana "
                f"**{med:.2f}R** · {reach}",
                "  _quanto lontano arriva il prezzo, in unità di R: dice se la scala"
                " di TP è raggiungibile. Dettaglio: `python -m scripts.mfe_report`_", ""]
    else:
        out += ["- escursione favorevole (mfe_r): _non ancora disponibile — si popola"
                " sui trade chiusi dopo l'aggiornamento del bot._", ""]
    return out


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
