"""
Report del backtest: HTML interattivo + Excel dettagliato.
Output in backtesting/output/.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

from backtesting.engine import LEVERAGE_LEVELS, StrategyStats

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def _ensure_dir() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def write_html(all_stats: dict[str, StrategyStats], verdict: dict, weights: list) -> str:
    _ensure_dir()
    path = os.path.join(OUTPUT_DIR, "backtest_report.html")
    regimes = ["bull_trending", "bear_trending", "sideways", "high_uncertainty"]

    # heatmap strategia × regime (PnL%)
    heat_rows = ""
    for name, stats in all_stats.items():
        by_reg = stats.by_regime()
        cells = ""
        for reg in regimes:
            ts = by_reg.get(reg, [])
            pnl = sum(t.pnl_pct for t in ts) * 100
            color = "#1b5e20" if pnl > 2 else "#388e3c" if pnl > 0 else "#b71c1c" if pnl < -2 else "#e53935" if pnl < 0 else "#424242"
            cells += f'<td style="background:{color};color:#fff;text-align:center">{pnl:+.1f}%<br><small>{len(ts)}</small></td>'
        heat_rows += f"<tr><td><b>{name}</b></td>{cells}</tr>"

    # tabella riepilogo + liquidazioni
    summ_rows = ""
    for name, stats in all_stats.items():
        liq = stats.liquidations_at_leverage()
        liq_cells = "".join(f"<td>{liq[l]}</td>" for l in LEVERAGE_LEVELS)
        summ_rows += (
            f"<tr><td><b>{name}</b></td><td>{len(stats.trades)}</td>"
            f"<td>{stats.win_rate()*100:.1f}%</td>"
            f"<td>{stats.profit_factor():.2f}</td>"
            f"<td>{stats.total_pnl_pct()*100:+.1f}%</td>{liq_cells}</tr>"
        )

    weight_rows = "".join(
        f"<tr><td>{w.strategy}</td><td>{w.regime.value}</td><td>{w.weight:.2f}</td>"
        f"<td>{(w.win_rate or 0)*100:.0f}%</td><td>{w.sample_size}</td></tr>"
        for w in weights
    )

    verdict_color = "#1b5e20" if verdict["passed"] else "#b71c1c"
    lev_headers = "".join(f"<th>{l}x</th>" for l in LEVERAGE_LEVELS)

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Backtest Report — GATE 1</title>
<style>
body{{font-family:system-ui,Arial;background:#121212;color:#e0e0e0;margin:24px}}
h1,h2{{color:#fff}} table{{border-collapse:collapse;width:100%;margin:12px 0}}
td,th{{border:1px solid #333;padding:8px}} th{{background:#1e1e1e}}
.verdict{{padding:16px;border-radius:8px;background:{verdict_color};color:#fff;font-size:18px}}
</style></head><body>
<h1>Backtest Report — GATE 1</h1>
<p>Generato: {datetime.now(timezone.utc).isoformat()}</p>
<div class="verdict"><b>{'✅ PASSED' if verdict['passed'] else '❌ NON SUPERATO'}</b> — {verdict['message']}<br>
PnL totale: {verdict['total_pnl_pct']*100:+.1f}%</div>

<h2>Heatmap performance — Strategia × Regime (PnL%, n. trade)</h2>
<table><tr><th>Strategia</th>{''.join(f'<th>{r}</th>' for r in regimes)}</tr>{heat_rows}</table>

<h2>Riepilogo strategie + liquidazioni per leva</h2>
<table><tr><th>Strategia</th><th>Trade</th><th>Win rate</th><th>Profit factor</th><th>PnL%</th>{lev_headers}</tr>
{summ_rows}</table>
<p><small>Le colonne {', '.join(f'{l}x' for l in LEVERAGE_LEVELS)} mostrano quante volte saresti stato liquidato a quella leva.</small></p>

<h2>Pesi appresi (validazione learning loop su dati storici)</h2>
<table><tr><th>Strategia</th><th>Regime</th><th>Peso</th><th>Win rate</th><th>Campione</th></tr>{weight_rows}</table>
</body></html>"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def write_excel(all_stats: dict[str, StrategyStats]) -> str:
    _ensure_dir()
    path = os.path.join(OUTPUT_DIR, "backtest_detail.xlsx")
    try:
        from openpyxl import Workbook
    except ImportError:
        print("[report] openpyxl non installato, salto Excel")
        return ""
    wb = Workbook()
    ws = wb.active
    ws.title = "summary"
    ws.append(["strategy", "trades", "win_rate", "profit_factor", "total_pnl_pct"]
              + [f"liq_{l}x" for l in LEVERAGE_LEVELS])
    for name, stats in all_stats.items():
        liq = stats.liquidations_at_leverage()
        ws.append([name, len(stats.trades), round(stats.win_rate(), 3),
                   round(stats.profit_factor(), 2), round(stats.total_pnl_pct(), 4)]
                  + [liq[l] for l in LEVERAGE_LEVELS])

    ws2 = wb.create_sheet("trades")
    ws2.append(["strategy", "regime", "direction", "entry", "exit", "pnl_pct",
                "max_adverse_pct", "confidence", "is_win"])
    for stats in all_stats.values():
        for t in stats.trades:
            ws2.append([t.strategy, t.regime, t.direction, round(t.entry_price, 4),
                        round(t.exit_price, 4), round(t.pnl_pct, 4),
                        round(t.max_adverse_pct, 4), t.confidence, t.is_win])
    wb.save(path)
    return path
