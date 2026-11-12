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

import os
import time
from datetime import datetime, timezone

from backtesting.engine import max_concurrent, portfolio_drawdown
from bot.config import settings
from bot.core.firebase_client import decode_pairs, get_firebase

OUT = "docs/state.md"


def _ts(v) -> str:
    try:
        return datetime.fromtimestamp(float(v), tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:  # noqa: BLE001
        return "—"


def _salute_registro(pairs: dict) -> list[str]:
    """IL REGISTRO STA ACCUMULANDO, O STA BUTTANDO VIA CIO' CHE TROVA?

    Nasce dal difetto del 31 agosto, e serve a non farlo ripetere. Le coppie base
    erano cresciute oltre il tetto da sole, e il tetto cancellava tutte le GENERATE
    a ogni passata — cioe' le uniche che passano il gate. La ricerca trovava ottanta
    candidate a giro e il registro le buttava un istante dopo.

    E' rimasto invisibile per giorni per un motivo preciso: ogni numero che
    guardavamo era VERO. "80 candidate passate" vero. "3041 coppie nel registro"
    vero. Nessuno confrontava le due cose, e nessuno guardava di che cosa fosse
    fatto quel 3041. Un totale non dice mai se dentro c'e' quello che serve.

    Queste tre righe fanno esattamente quel confronto, e finiscono in docs/state.md
    — che e' committato, quindi si legge da qualunque posto senza entrare sulla
    macchina. Se il registro torna a soffocare, la prossima volta si vede subito.
    """
    if not pairs:
        return []
    tetto = int(os.getenv("OPTIMIZER_MAX_PAIRS", "3000"))
    base = sum(1 for r in pairs.values() if not r.get("generated"))
    gen = len(pairs) - base
    gen_con_pass = sum(1 for r in pairs.values()
                       if r.get("generated") and int(r.get("pass_count", 0) or 0) > 0)
    out = [
        "### Salute del registro",
        "",
        f"- composizione: **{base} base** · **{gen} generate** "
        f"(di cui {gen_con_pass} con almeno una conferma)",
        f"- occupazione: {len(pairs)}/{tetto} — "
        f"{'⚠️ SOPRA IL TETTO' if len(pairs) > tetto else 'ok'}",
    ]
    # L'ALLARME. Le generate sono le uniche che passano il gate: se sono zero, o se
    # le base da sole riempiono il tetto, il sistema non puo' accumulare NIENTE per
    # quante candidate trovi.
    if gen == 0:
        out.append("- 🔴 **ZERO coppie generate**: sono le uniche che passano il "
                   "gate. Il registro non puo' accumulare niente, per quante "
                   "candidate la ricerca trovi.")
    elif base >= tetto * 0.9:
        out.append(f"- 🟠 **le base occupano il {base / tetto * 100:.0f}% del "
                   f"tetto**: alle generate restano {max(0, tetto - base)} posti. "
                   f"Sotto zero il registro smette di accumulare.")
    out.append("")
    return out


def build() -> str:
    fb = get_firebase()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# Stato sistema (snapshot)", f"_Generato: {now}_", ""]

    # --- stato bot (RTDB) ---
    status = fb.get_rtdb("/bot_status") or {}
    hb = status.get("heartbeat")
    # 900s (era 180): il market scan tocca 200 coin con pacing e puo' durare
    # minuti, durante i quali l'heartbeat non si aggiorna. A 180s il bot risultava
    # "offline" mentre stava lavorando — falso allarme ricorrente. Il tick e' 30s,
    # quindi 15 minuti di silenzio restano un segnale vero di blocco.
    online = hb and (time.time() - float(hb) < 900)
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

    # --- il paper di F5 eseguito dal bot (bot/portafoglio/f5.py, backlog P16) ---
    lines += sezione_paper_f5(fb)
    lines += sezione_paper_f5(fb, ramo="/paper_g1", titolo="## Paper G1 (F5 decisa ogni giorno, eseguito dal bot)",
                              interruttore="ops/paper_g1_acceso")
    lines += sezione_paper_f5(fb, ramo="/paper_g11", titolo="## Paper G11 (G1 con il funding fresco, a confronto con G1)",
                              interruttore="ops/paper_g11_acceso")
    lines += sezione_paper_f5(fb, ramo="/paper_g1n", titolo="## Paper G1N (G1 neutra al mercato, a confronto con G1; per i soldi veri resta G1, revisione del 29 ottobre)",
                              interruttore="ops/paper_g1n_acceso")
    lines += sezione_paper_eventi(fb)
    lines += sezione_demo_binance(fb)
    lines += sezione_demo_contro_paper(fb)
    lines += sezione_conto_vero(fb)
    lines += sezione_demo_esecuzioni(fb)

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
            # rischio EFFETTIVO: quanto costa davvero lo stop, in % dell'equity.
            # E' il numero che dice se la manopola del rischio sta funzionando: sotto
            # il cap per-posizione diverge dall'impostazione e varia con lo stop.
            r = p.get("risk_effective_pct")
            risk = f" · rischio {float(r) * 100:.2f}%" if r else ""
            lines.append(f"- {sym}: {p.get('direction')} qty={p.get('quantity')} "
                         f"@ {p.get('entry_price')} uPnL={p.get('unrealized_pnl')}"
                         f"{risk} · leva {p.get('leverage')}x")
        risks = [float(p.get("risk_effective_pct") or 0) for p in positions.values()
                 if isinstance(p, dict) and p.get("risk_effective_pct")]
        if risks:
            lines.append(f"- **rischio aperto totale: {sum(risks) * 100:.2f}%** "
                         f"dell'equity su {len(risks)} posizioni")
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
    lines += _salute_registro(pairs)
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
    lines += _autopsy_section(fb)
    lines += _supervisor_section(fb)
    lines += _closed_trades_section(fb, pairs)
    lines += _drift_section(fb)
    lines += _calibration_section(fb)
    return "\n".join(lines)


def _autopsy_section(fb) -> list[str]:
    """DOVE MUOIONO LE CANDIDATE, dentro lo snapshot committato.

    Sta qui e non solo in uno script a parte per una ragione precisa: questo file
    finisce su git a ogni aggiornamento, quindi la diagnosi diventa leggibile senza
    entrare sulla VPS. Un numero che richiede un comando manuale per essere visto,
    in pratica non viene visto — e questa e' l'informazione che dice su cosa
    lavorare quando il gate non promuove nulla.
    """
    out = ["## Dove muoiono le candidate (autopsia del GATE 1)", ""]
    docs = [("strategie base", fb.get_doc("gate_autopsy", "current") or {}),
            ("strategie generate", fb.get_doc("gate_autopsy", "discover") or {})]
    if not any(d for _, d in docs):
        out += ["_nessuna diagnosi ancora registrata: serve un run dell'optimizer._", ""]
        return out
    for label, rep in docs:
        if not rep:
            continue
        ev, ps = rep.get("evaluated", 0), rep.get("passed", 0)
        out.append(f"**{label}** — {ev} valutazioni, {ps} passate "
                   f"({(ps / ev * 100) if ev else 0:.2f}%) · {_ts(rep.get('updated_at'))}")
        binding = rep.get("binding") or {}
        if binding:
            tot = sum(binding.values()) or 1
            out += ["", "| Criterio che ferma | Casi | Quota |", "|---|---|---|"]
            for k, v in list(binding.items())[:8]:
                out.append(f"| {k} | {v} | {v / tot * 100:.1f}% |")
        out += ["", f"- quasi-passaggi (un solo criterio, di poco): "
                    f"**{rep.get('near_miss_count', 0)}** "
                    f"— sono i semi delle mutazioni del run successivo", ""]
    return out


def _supervisor_section(fb) -> list[str]:
    """COSA HA DECISO IL SUPERVISORE, e con quali numeri.

    Un sistema che si tara da solo deve lasciare per iscritto perche' ogni soglia
    sta dove sta: senza, fra due mesi nessuno sapra' piu' se un valore e' frutto di
    una misura o di una svista, e l'unica reazione possibile sara' rimettere tutto
    ai default buttando via cio' che si e' imparato.
    """
    st = fb.get_doc("supervisor", "state") or {}
    out = ["## Supervisore (taratura automatica)", ""]
    if not st:
        out += ["_non ha ancora deciso nulla._", ""]
        return out
    tuning = st.get("tuning") or {}
    out.append(f"- ultimo giro: {_ts(st.get('updated_at'))} · coppie validate: "
               f"**{st.get('validated', 0)}** · GATE 1 pronto: {st.get('ready')}")
    out.append(f"- tasso di passaggio misurato: **{float(st.get('pass_rate', 0)) * 100:.3f}%**")
    if tuning:
        out += ["", "**Parametri modificati rispetto ai default:**", "",
                "| Parametro | Valore |", "|---|---|"]
        out += [f"| {k} | {v} |" for k, v in sorted(tuning.items())]
    else:
        out.append("- nessun parametro modificato: il gate gira coi valori di partenza")
    hist = (st.get("history") or [])[-5:]
    if hist:
        out += ["", "**Ultime decisioni:**", ""]
        for h in reversed(hist):
            what = h.get("kind", "?")
            if h.get("param"):
                what += f" {h['param']} {h.get('old')} → {h.get('new')}"
            out.append(f"- `{what}` — {h.get('reason', '')}")
    out.append("")
    return out


def _benchmark_return(start_ts: float) -> float | None:
    """Rendimento di BTC dall'inizio del periodo: il metro di paragone.

    Senza, "equity positiva" non dice se il sistema crea valore: guadagnare il 5%
    mentre il mercato fa +20% significa che comprare e tenere sarebbe stato
    meglio, con meno rischio operativo e zero costi di esecuzione."""
    try:
        import requests
        r = requests.get("https://fapi.binance.com/fapi/v1/klines",
                         params={"symbol": "BTCUSDT", "interval": "1h",
                                 "startTime": int(start_ts * 1000), "limit": 1000},
                         timeout=15)
        kl = r.json()
        if not isinstance(kl, list) or len(kl) < 2:
            return None
        first, last = float(kl[0][1]), float(kl[-1][4])
        return (last - first) / first if first > 0 else None
    except Exception:  # noqa: BLE001
        return None


def _calibration_section(fb) -> list[str]:
    """Calibrazione della confidenza: quel numero predice davvero l'esito?"""
    try:
        doc = fb.get_doc("calibration", "current") or {}
    except Exception as exc:  # noqa: BLE001
        return ["## Calibrazione della confidenza", f"_non leggibile: {exc}_", ""]
    if not doc:
        return ["## Calibrazione della confidenza",
                "_nessun verdetto ancora: servono trade chiusi._", ""]
    out = ["## Calibrazione della confidenza",
           "_la confidenza del segnale modula size e leva: qui si verifica che "
           "predica davvero l'esito, invece di darlo per scontato._", "",
           f"- verdetto: **{doc.get('verdict', '—')}** · {doc.get('trades', 0)} trade · "
           f"correlazione {doc.get('correlation')} · influenza applicata "
           f"**x{doc.get('trust', 1.0)}**",
           f"- {doc.get('note', '')}", ""]
    b = doc.get("buckets") or []
    if b:
        out += ["| Fascia di confidenza | Trade | Win rate | Esito medio |",
                "|---|---|---|---|"]
        for x in b:
            out.append(f"| {x['conf_min']}–{x['conf_max']} | {x['trades']} | "
                       f"{x['win_rate']*100:.0f}% | {x['expectancy']*100:+.2f}% |")
        out += ["", "_se l'esito medio CRESCE dalla fascia bassa all'alta, la "
                "confidenza ordina correttamente i trade._", ""]
    return out


def _drift_section(fb) -> list[str]:
    """Deriva: dove il VISSUTO contraddice la PROMESSA del gate. E' l'anello di
    ritorno paper -> gate, quindi va visto senza SSH."""
    try:
        doc = fb.get_doc("drift", "current") or {}
    except Exception as exc:  # noqa: BLE001
        return ["## Deriva paper vs gate", f"_non leggibile: {exc}_", ""]
    # il FRENO DI SERIE (23 set 2026): chi sta perdendo di fila adesso. Va
    # mostrato anche quando non c'e' ancora nessun verdetto di deriva, perche'
    # matura in giorni e non ha bisogno di una promessa del gate.
    from bot.config import settings as _cfg
    serie = [(k, int(v)) for k, v in (doc.get("serie") or {}).items()
             if isinstance(v, (int, float)) and v >= _cfg.STREAK_BRAKE_LOSSES]
    serie.sort(key=lambda kv: (-kv[1], kv[0]))
    _eti = ("- **freno di serie** (size x%g): " % _cfg.STREAK_BRAKE_FACTOR
            if _cfg.STREAK_BRAKE_ENABLED else
            "- serie di perdite (freno SPENTO dal 24 set, solo misura): ")
    riga_serie = ([_eti
                   + ", ".join(f"**{k}** ({v} perdite di fila)" for k, v in serie), ""]
                  if serie else [])
    if not doc or not (doc.get("pairs") or doc.get("strategies")):
        return ["## Deriva paper vs gate",
                "_nessun verdetto ancora: servono trade chiusi su coppie validate._", ""
                ] + riga_serie
    out = ["## Deriva paper vs gate",
           "_il gate promette sulla storia, il paper misura il presente. `drift` = "
           "promessa contraddetta -> size/leva frenate subito e fallimento al gate "
           "alla prossima passata._", ""]
    g = doc.get("global") or {}
    if g:
        out += [f"- **globale**: {g.get('verdict', '—')} · {g.get('trades', 0)} trade · "
                f"PF vissuto {g.get('live_pf')} vs {g.get('expected_pf')} atteso"
                + (f" · mfe mediana {g['mfe_median']}R" if g.get("mfe_median") else ""), ""]
    if g.get("verdict") == "drift":
        # IL FRENO GLOBALE (25 set 2026): col verdetto globale in `drift`,
        # weight_factor (bot/learning/drift.py) moltiplica size e leva di OGNI
        # trade, non solo delle coppie in deriva. Non compariva in nessun log ne'
        # comando: lo si scopriva solo dalla nota del singolo trade. I numeri
        # sono quelli di settings, cosi' la riga non mente se cambiano.
        if _cfg.DRIFT_ENABLED:
            out += [f"- **freno globale attivo**: size x{_cfg.DRIFT_WEIGHT_FACTOR:g} e "
                    f"leva x{_cfg.DRIFT_WEIGHT_FACTOR ** 0.5:.2f} (radice) su OGNI "
                    f"trade finche' il PF a 30 giorni resta sotto "
                    f"{_cfg.DRIFT_PF_RATIO:g} x atteso"
                    + (f" (motivo: {g['reason']})" if g.get("reason") else ""), ""]
        else:
            out += ["- freno globale SPENTO (`DRIFT_ENABLED=false`): il verdetto e' "
                    "solo misura, size e leva restano piene", ""]
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
    out += riga_serie
    return out


_EXIT_LABEL = {
    "take_profit": "Take profit (fino all'ultimo gradino)",
    "scale_out": "Scale-out (>=1 TP incassato, residuo a BE)",
    "trailing_stop": "Trailing stop",
    "stop_loss": "Stop loss (prima di qualsiasi TP)",
    "time_exit": "Time exit (orizzonte scaduto)",
    "manual": "Manuale", "kill_switch": "Kill switch", "circuit_breaker": "Circuit breaker",
}


def _closed_trades_section(fb, pairs=None) -> list[str]:
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
           f"PnL realizzato: **{pnl:+.2f}**"]
    # BENCHMARK: "equity positiva" non basta a dire che il sistema crea valore
    ts = [float(t.get("exit_ts", 0) or 0) for t in trades if t.get("exit_ts")]
    if ts:
        bench = _benchmark_return(min(ts))
        eq0 = 1000.0
        if bench is not None:
            ours = pnl / eq0
            verdetto = "**batte** il mercato" if ours > bench else "**sotto** il mercato"
            out.append(f"- confronto col mercato: noi {ours*100:+.2f}% vs "
                       f"BTC buy&hold {bench*100:+.2f}% nello stesso periodo → {verdetto}")
    out.append("")

    # COSTI SCOMPOSTI: il PnL netto da solo non dice se un risultato e' mancato
    # edge o troppa spesa. Il break-even e' la domanda operativa: quanto deve
    # rendere il sistema SOLO per coprire cio' che spende.
    from bot.learning.metrics import cost_alerts, cost_report
    _eq = fb.get_rtdb("/account/equity")
    rep = cost_report(trades, float(_eq) if _eq else None)
    if rep:
        stima = " _(stimati dal modello del gate, non misurati dai fill)_" if rep.get("estimated") else ""
        out += [f"- costi: **{rep['total_cost_usdt']:.2f} USDT** su {rep['trades']} trade "
                f"({rep['cost_per_trade_usdt']:.2f}/trade){stima}",
                f"  - commissioni {rep['commission_usdt']:.2f} · spread "
                f"{rep['spread_usdt']:.2f} · funding {rep['funding_usdt']:+.2f}",
                f"  - lordo {rep['gross_pnl_usdt']:+.2f} → netto {rep['net_pnl_usdt']:+.2f}"
                + (f" · **break-even {rep['break_even_pct']:.2f}%** dell'equity"
                   if rep.get("break_even_pct") is not None else "")]
        if rep.get("cost_by_symbol"):
            top = " · ".join(f"{k} {v:.2f}" for k, v in
                             list(rep["cost_by_symbol"].items())[:5])
            out.append(f"  - piu' costose: {top}")
        for a in cost_alerts(rep):
            out.append(f"  - ⚠️ {a}")
        out.append("")

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
    # DRAWDOWN DI PORTAFOGLIO: le uscite ordinate nel TEMPO, non per coppia. Il
    # gate misura la buca che una coppia scava DA SOLA e promuove solo curve
    # regolari (recovery >= 2); ma dieci curve regolari che scendono negli stessi
    # giorni — e su crypto si muovono quasi tutte con BTC — scavano insieme una
    # buca che nessuno dei numeri per coppia mostrava.
    def _t(v):
        if isinstance(v, (int, float)):
            return float(v)
        try:
            return datetime.fromisoformat(str(v)).timestamp()
        except (TypeError, ValueError):
            return None
    events = [(_t(t.get("exit_ts") or t.get("exit_time")), float(t.get("pnl", 0) or 0))
              for t in trades]
    events = [e for e in events if e[0] is not None]
    if events:
        dd, tot = portfolio_drawdown(events)
        conc = max_concurrent((_t(t.get("entry_time")), _t(t.get("exit_time")))
                              for t in trades)
        rec = (tot / dd) if dd > 0 else None
        out += [f"- **drawdown di portafoglio: {dd:.2f} USDT** "
                f"(ritorno {tot:+.2f} · recovery "
                f"{f'{rec:.2f}' if rec is not None else '—'}) "
                f"· max {conc} posizioni aperte insieme"]
        # confronto con la PROMESSA: il gate accetta una coppia solo se il suo
        # recovery e' >= GATE_MIN_RECOVERY. Se il portafoglio sta sotto mentre ogni
        # coppia stava sopra, la soglia per coppia non protegge il portafoglio.
        recs = [float(r.get("last_pnl_pct") or 0) / float(r.get("last_max_dd") or 0)
                for r in (pairs or {}).values()
                if float((r or {}).get("last_max_dd") or 0) > 0]
        if recs and rec is not None:
            worst = min(recs)
            out.append(f"  - il gate prometteva recovery ≥ "
                       f"{settings.GATE_MIN_RECOVERY:.1f} per ogni coppia "
                       f"(peggiore in registro: {worst:.2f}); il PORTAFOGLIO "
                       f"realizza {rec:.2f}")
        out += ["  _uscite in ordine di TEMPO: e' la buca vera, quella che il gate"
                " non vede perche' valida una coppia alla volta._", ""]

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


def sezione_paper_f5(fb, ramo: str = "/paper_f5", titolo: str = "## Paper F5 (strategie nuove, eseguito dal bot)",
                     interruttore: str = "ops/paper_f5_acceso") -> list:
    """Le righe di un paper di portafoglio del bot (RTDB /paper_f5, o /paper_g1 per G1): acceso, equity, posizioni, ultimo
    ribilancio."""
    st = fb.get_rtdb(f"{ramo}/stato") or {}
    if not isinstance(st, dict) or not st:
        return [titolo, f"- spento (manca `{interruttore}`)", ""]
    righe = [titolo, f"- stato: **{st.get('stato', '—')}** ({_ts(st.get('aggiornato'))})"]
    pr = fb.get_rtdb(f"{ramo}/prova") or {}
    if isinstance(pr, dict) and pr:
        righe.append(f"- prova a secco ({_ts(pr.get('eseguita'))}, pesi del {pr.get('lunedi')}): universo {pr.get('universo')}, "
                     f"{pr.get('long')} long, {pr.get('short')} short; pesi maggiori "
                     + ", ".join(f"{s} {100 * float(w):+.1f}%" for s, w in (pr.get('pesi_maggiori') or {}).items()))
    if st.get("equity") is not None:
        righe += [f"- equity: **${float(st['equity']):,.2f}** su ${float(st.get('capitale', 0)):,.0f} "
                  f"({100 * float(st.get('rendimento', 0)):+.2f}%) · costi ${float(st.get('costi_totali', 0)):,.2f} · "
                  f"funding pagato ${float(st.get('funding_totale', 0)):,.2f}",
                  f"- posizioni: {st.get('long', 0)} long, {st.get('short', 0)} short · ultimo ribilancio {st.get('ultimo_lunedi', '—')}"]
        if int(st.get("limite_variazioni") or 0) or int(st.get("ordini_in_attesa") or 0):
            righe.append(f"- ordini limite: {st.get('limite_eseguite', 0)} eseguiti su {st.get('limite_variazioni', 0)} · "
                         f"tutto a mercato sarebbe costato ${float(st.get('costi_a_mercato_totali', 0)):,.2f} · "
                         f"in attesa del controllo dell'ora: {st.get('ordini_in_attesa', 0)}")
        pos = fb.get_rtdb(f"{ramo}/posizioni") or {}
        if isinstance(pos, dict) and pos:
            ordine = sorted(pos.items(), key=lambda kv: -abs(float(kv[1])))
            righe.append("- pesi maggiori: " + ", ".join(f"{s} {100 * float(w):+.1f}%" for s, w in ordine[:10]))
    return righe + [""]


def sezione_paper_eventi(fb) -> list:
    """Le righe del paper di N3 ed E4 (RTDB /paper_eventi): acceso, equity, operazioni aperte e chiuse."""
    titolo = "## Paper N3 ed E4 (eventi, eseguito dal bot)"
    st = fb.get_rtdb("/paper_eventi/stato") or {}
    if not isinstance(st, dict) or not st:
        return [titolo, "- spento (manca `ops/paper_eventi_acceso`)", ""]
    med = st.get("rendimento_medio")
    righe = [titolo, f"- stato: **{st.get('stato', '—')}** ({_ts(st.get('aggiornato'))})",
             f"- equity: **${float(st.get('equity', 0)):,.2f}** su ${float(st.get('capitale', 0)):,.0f} "
             f"({100 * float(st.get('rendimento', 0)):+.2f}%) · aperte N3 {st.get('aperte_n3', 0)}, E4 {st.get('aperte_e4', 0)} · "
             f"chiuse {st.get('chiuse', 0)}" + (f", media {100 * float(med):+.2f}% a operazione" if med is not None else "")
             + f" · E4 in attesa {st.get('e4_in_attesa', 0)}"]
    aperte = fb.get_rtdb("/paper_eventi/aperte") or {}
    if isinstance(aperte, dict) and aperte:
        righe.append("- aperte: " + ", ".join(f"{p.get('tipo')} {p.get('simbolo')} {100 * float(p.get('rendimento_ora') or 0):+.1f}% "
                                              f"(fino al {p.get('uscita_giorno')})" for p in aperte.values() if isinstance(p, dict)))
    return righe + [""]


def sezione_demo_binance(fb) -> list:
    """Le righe di G1 sul conto demo di Binance (RTDB /demo_binance): stato, equity, ordini limite, ultimo errore."""
    titolo = "## G1 sul conto demo di Binance (ordini veri, soldi finti)"
    st = fb.get_rtdb("/demo_binance/stato") or {}
    err = fb.get_rtdb("/demo_binance/errore") or {}
    st = st if isinstance(st, dict) else {}
    err = err if isinstance(err, dict) else {}
    if not st and not err:
        return [titolo, "- spento o mai partito (manca `ops/demo_binance_acceso`, o il bot non è stato riavviato)", ""]
    righe = [titolo, f"- stato: **{st.get('stato', 'nessuna valutazione del conto ancora')}** ({_ts(st.get('aggiornato'))})"]
    if st.get("equity") is not None:
        righe.append(f"- equity: **${float(st['equity']):,.2f}** su ${float(st.get('capitale_iniziale') or 0):,.2f} "
                     f"({100 * float(st.get('rendimento') or 0):+.2f}%) · posizioni {st.get('long', 0)} long, {st.get('short', 0)} short · "
                     f"ordini limite eseguiti {st.get('limite_eseguiti', 0)} su {st.get('limite_totali', 0)} · in attesa "
                     f"{st.get('ordini_in_attesa', 0)}")
    if st.get("capitale_in_attesa"):
        righe.append(f"- capitale nuovo in attesa: **${float(st['capitale_in_attesa']):,.0f}**, parte alla prossima decisione di G1 "
                     f"(mezzanotte), chiudendo tutto e riaprendo da zero")
    if st.get("conto_ridotto"):
        righe.append(f"- conto ridotto: il demo lavora come un conto di ${float(st['conto_ridotto']):,.0f} (prova 148, il capitale del "
                     f"proprietario); valore vero del conto demo ${float(st.get('valore_vero_del_conto_demo') or 0):,.2f}")
    rib = fb.get_rtdb("/demo_binance/ribilanciamenti") or {}
    if isinstance(rib, dict) and rib:
        g = max(rib)
        x = rib[g] if isinstance(rib[g], dict) else {}
        lim = x.get("limite") or {}
        righe.append(f"- ultima decisione {g}: {x.get('ordini', 0)} ordini"
                     + (f", eseguiti a limite {lim.get('eseguiti_a_limite', 0)}, a mercato {lim.get('a_mercato', 0)}" if lim else "")
                     + (f"; sotto il minimo {x['sotto_il_minimo'].get('variazioni', 0)} variazioni "
                        f"({100 * float(x['sotto_il_minimo'].get('valore_in_frazione_del_conto') or 0):.1f}% del conto)"
                        if isinstance(x.get("sotto_il_minimo"), dict) else "")
                     + (f"; monete che sul demo non ci sono: {', '.join(x['monete_mancanti_sul_demo'])}"
                        if x.get("monete_mancanti_sul_demo") else "")
                     + (f"; rifiutati {len(x['rifiutati'])}: " + "; ".join(f"{r.get('simbolo')} {str(r.get('errore'))[:80]}"
                                                                         for r in x["rifiutati"][:3]) if x.get("rifiutati") else ""))
        rif = [r.get("simbolo") for r in (x.get("rifiutati") or []) if isinstance(r, dict) and r.get("simbolo")]
        rif += [m for m in (x.get("monete_mancanti_sul_demo") or []) if m not in rif]
        pos = fb.get_rtdb("/paper_g1/posizioni") or {}
        if rif and isinstance(pos, dict):
            righe.append("- peso nel paper G1 delle monete rifiutate o mancanti sul demo (MIGLIORARE_G1.md, voce 4): "
                         + ", ".join(f"{s_} {100 * float(pos.get(s_) or 0):+.2f}%" for s_ in rif))
    if st.get("stop_a") is not None:
        # il livello vero dello stop (revisione dell'8 novembre 2026, decisione 2 e problema 49): il più alto fra −35% dal massimo e
        # il 65% del capitale di partenza della fase
        righe.append(f"- stop sul conto: si chiude tutto sotto ${float(st['stop_a']):,.2f} (il più alto fra −35% dal massimo, "
                     f"${float(st.get('massimo') or 0):,.2f}, e il 65% del capitale di partenza); ora "
                     f"{100 * float(st.get('dal_massimo') or 0):+.2f}% dal massimo")
    allarme = fb.get_rtdb("/demo_binance/allarme")
    if isinstance(allarme, dict) and allarme:
        righe.append(f"- **ALLARME** ({_ts(allarme.get('ora'))}): {allarme.get('testo')}"
                     + (f" ({', '.join(allarme.get('posizioni') or [])})" if allarme.get("posizioni") else ""))
    # gli altri allarmi del demo, uno per tipo (revisione del 7 novembre 2026: ordini bloccati, decisione di G1 vecchia, pesi fuori
    # dai limiti, limiti di Binance, capitale del file, filtri del conto vero vecchi, «riparti» sotto il pavimento)
    allarmi = fb.get_rtdb("/demo_binance/allarmi")
    for tipo, a in sorted(allarmi.items()) if isinstance(allarmi, dict) else []:
        if isinstance(a, dict) and a.get("testo"):
            righe.append(f"- **ALLARME** {tipo.replace('_', ' ')} ({_ts(a.get('ora'))}): {a.get('testo')}")
    fermo = fb.get_rtdb("/demo_binance/fermo")
    if isinstance(fermo, dict) and fermo:
        righe.append(f"- **FERMO** dal {_ts(fermo.get('ora'))}: {fermo.get('motivo')} · posizioni chiuse {fermo.get('chiuse', 0)}, "
                     f"errori {len(fermo.get('errori') or [])} (riparte solo con il pulsante «riparti» della dashboard)")
    mg = fb.get_rtdb("/demo_binance/margine")
    if isinstance(mg, dict) and mg:
        sep = mg.get("separati_trovati") or []
        righe.append(f"- margine ({_ts(mg.get('controllato'))}): " + ("unico su tutte le monete" if not sep else
                     f"separato su {', '.join(sep)}; sistemate {', '.join(mg.get('sistemate') or []) or 'nessuna'}"))
    cf = fb.get_rtdb("/demo_binance/confronto")
    if isinstance(cf, dict) and cf:
        dif = cf.get("differenze") or []
        righe.append(f"- posizioni vere contro volute ({_ts(cf.get('ora'))}): {cf.get('monete', 0)} monete, scarto totale "
                     f"{100 * float(cf.get('scarto_totale') or 0):.1f}% del conto; " + ("nessuna moneta oltre il 2%" if not dif else
                     "oltre il 2%: " + ", ".join(f"{x.get('simbolo')} {100 * float(x.get('scarto') or 0):+.1f}%" for x in dif[:6])))
    if err:
        righe.append(f"- ultimo errore ({_ts(err.get('ora'))}): `{str(err.get('testo', ''))[:200]}`")
    return righe + [""]


def sezione_conto_vero(fb) -> list:
    """Le righe di G1 sul conto vero di Binance (RTDB /conto_vero, `bot/portafoglio/conto_vero.py`, nasce spento): spento e perché,
    oppure acceso con equity, stop sul conto, fermo e allarmi."""
    titolo = "## G1 sul conto vero di Binance (soldi veri; nasce spento, si accende solo con il gesto del proprietario)"
    def allarmi_per_tipo() -> list:
        allarmi = fb.get_rtdb("/conto_vero/allarmi")
        return [f"- **ALLARME** {tipo.replace('_', ' ')} ({_ts(a.get('ora'))}): {a.get('testo')}"
                for tipo, a in (sorted(allarmi.items()) if isinstance(allarmi, dict) else []) if isinstance(a, dict) and a.get("testo")]

    st = fb.get_rtdb("/conto_vero/stato") or {}
    st = st if isinstance(st, dict) else {}
    if not st:
        # problema 73 (revisione dell'8 novembre 2026): gli allarmi si vedono anche senza stato (la creazione non riuscita)
        return [titolo, "- spento: nessuno stato scritto (il bot non lo ha ancora fatto girare)"] + allarmi_per_tipo() + [""]
    righe = [titolo, f"- stato: **{st.get('stato', '—')}** ({_ts(st.get('aggiornato'))})"]
    if st.get("equity") is not None:
        righe.append(f"- equity: **${float(st['equity']):,.2f}** su ${float(st.get('capitale_iniziale') or 0):,.2f} "
                     f"({100 * float(st.get('rendimento') or 0):+.2f}%) · posizioni {st.get('long', 0)} long, {st.get('short', 0)} short")
    if st.get("stop_a") is not None:
        righe.append(f"- stop sul conto: si chiude tutto sotto ${float(st['stop_a']):,.2f}; ora "
                     f"{100 * float(st.get('dal_massimo') or 0):+.2f}% dal massimo")
    fermo = fb.get_rtdb("/conto_vero/fermo")
    if isinstance(fermo, dict) and fermo:
        righe.append(f"- **FERMO** dal {_ts(fermo.get('ora'))}: {fermo.get('motivo')} · posizioni chiuse {fermo.get('chiuse', 0)}")
    allarme = fb.get_rtdb("/conto_vero/allarme")
    if isinstance(allarme, dict) and allarme.get("testo"):
        righe.append(f"- **ALLARME** ({_ts(allarme.get('ora'))}): {allarme.get('testo')}")
    righe += allarmi_per_tipo()
    err = fb.get_rtdb("/conto_vero/errore")
    if isinstance(err, dict) and err:
        righe.append(f"- ultimo errore ({_ts(err.get('ora'))}): `{str(err.get('testo', ''))[:200]}`")
    return righe + [""]


def confronto_giorni(demo: dict, paper: dict, eventi: dict | None = None) -> list:
    """Giorno per giorno, il rendimento di G1 sul demo (equity a fine giorno) e nel paper, e la differenza; i giorni con i due valori
    e il giorno prima. Il demo dal 31 ottobre porta anche gli eventi al 5%: la colonna degli eventi del paper serve a leggerlo."""
    eventi = eventi or {}
    def _num(d):
        out = {}
        for k, v in (d or {}).items():
            try:
                out[str(k)] = float(v)
            except (TypeError, ValueError):
                continue
        return out
    demo, paper, eventi = _num(demo), _num(paper), _num(eventi)
    giorni = sorted(set(demo) & set(paper))
    righe = []
    for a, b in zip(giorni, giorni[1:]):
        rd, rp = demo[b] / demo[a] - 1, paper[b] / paper[a] - 1
        re = eventi[b] / eventi[a] - 1 if a in eventi and b in eventi and eventi[a] else None
        righe.append({"giorno": b, "demo": rd, "paper": rp, "differenza": rd - rp, "eventi": re})
    return righe


def confronto_entrate(demo_diario: dict, paper_diario: dict, demo_giorni: dict | None = None) -> list:
    """Giorno per giorno, funding e spese in % dell'equity: sul demo quelli veri (``diario/{giorno}/entrate``: funding incassato,
    commissioni pagate), nel paper la differenza dei totali fra un giorno e il prima (``funding_totale`` positivo = pagato,
    ``costi_totali``). MIGLIORARE_G1.md, voci 2-3."""
    def _f(x, k):
        try:
            return float(x[k])
        except (KeyError, TypeError, ValueError):
            return None
    demo_diario, paper_diario = demo_diario or {}, paper_diario or {}
    righe = []
    giorni_p = sorted(k for k, v in paper_diario.items() if isinstance(v, dict) and _f(v, "funding_totale") is not None)
    paper = {}
    for a, b in zip(giorni_p, giorni_p[1:]):
        e = _f(paper_diario[b], "equity")
        if e:
            paper[b] = (-(_f(paper_diario[b], "funding_totale") - _f(paper_diario[a], "funding_totale")) / e,
                        (_f(paper_diario[b], "costi_totali") - _f(paper_diario[a], "costi_totali")) / e)
    for g in sorted(set(demo_diario) | set(paper)):
        v = demo_diario.get(g) if isinstance(demo_diario.get(g), dict) else {}
        en, e = v.get("entrate") if isinstance(v.get("entrate"), dict) else None, _f(v, "equity")
        if e is None:                                   # i giorni prima del diario (3 novembre): l'equity dai valori del giorno
            e = _f(demo_giorni or {}, g)
        righe.append({"giorno": g, "demo_funding_usdt": _f(en, "funding_incassato") if en else None,
                      "demo_spese_usdt": _f(en, "commissioni_pagate") if en else None,
                      "demo_funding": _f(en, "funding_incassato") / e if en and e else None,
                      "demo_spese": _f(en, "commissioni_pagate") / e if en and e else None,
                      "paper_funding": paper[g][0] if g in paper else None, "paper_spese": paper[g][1] if g in paper else None})
    return [r for r in righe if any(r[k] is not None for k in ("demo_funding", "paper_funding"))]


def sezione_demo_contro_paper(fb) -> list:
    """G1 sul demo contro G1 nel paper, giorno per giorno (MIGLIORARE_G1.md, voce 1): quanto costa l'esecuzione vera."""
    titolo = "## G1: il demo contro il paper, giorno per giorno"
    righe = confronto_giorni(fb.get_rtdb("/demo_binance/giorni") or {}, fb.get_rtdb("/paper_g1/giorni") or {},
                             fb.get_rtdb("/paper_eventi/giorni") or {})
    if not righe:
        return [titolo, "- non ancora: servono almeno due giorni con il demo e il paper", ""]
    out = [titolo, "Equity a fine giorno (l'ultimo valore scritto). Dal 6 novembre il demo lavora come un conto ridotto (280 USDT, dall'8 novembre "
           "1.000), senza gli eventi; le fasi di prima sono in /demo_binance/fasi; con i minimi di Binance la differenza con il paper "
           "oscilla di più (prova 148).", "",
           "| giorno | demo | paper G1 | demo meno paper | eventi nel paper |", "|---|---|---|---|---|"]
    for r in righe:
        ev = f"{100 * r['eventi']:+.2f}%" if r["eventi"] is not None else "—"
        out.append(f"| {r['giorno']} | {100 * r['demo']:+.2f}% | {100 * r['paper']:+.2f}% | {100 * r['differenza']:+.2f}% | {ev} |")
    tot_d = 1.0
    tot_p = 1.0
    for r in righe:
        tot_d *= 1 + r["demo"]
        tot_p *= 1 + r["paper"]
    dif = [r["differenza"] for r in righe]
    media = sum(dif) / len(dif)
    osc = (sum((x - media) ** 2 for x in dif) / (len(dif) - 1)) ** 0.5 if len(dif) > 1 else None
    out += ["", f"- dal {righe[0]['giorno']} ({len(righe)} giorni): demo {100 * (tot_d - 1):+.2f}%, paper {100 * (tot_p - 1):+.2f}%; "
            f"differenza media al giorno {100 * media:+.3f}%" + (f", oscillazione {100 * osc:.3f}%" if osc is not None else ""), ""]
    en = confronto_entrate(fb.get_rtdb("/demo_binance/diario") or {}, fb.get_rtdb("/paper_g1/diario") or {},
                           fb.get_rtdb("/demo_binance/giorni") or {})
    if en:
        pc = lambda x: f"{100 * x:+.3f}%" if x is not None else "—"  # noqa: E731
        out += ["Funding e spese veri, in % dell'equity del giorno (funding: + incassato; spese: + pagate; nel paper dal 6 novembre).",
                "", "| giorno | funding demo | funding paper | spese demo | spese paper |", "|---|---|---|---|---|"]
        out += [f"| {r['giorno']} | {pc(r['demo_funding'])} | {pc(r['paper_funding'])} | {pc(r['demo_spese'])} | {pc(r['paper_spese'])} |"
                for r in en]
        fu = [r["demo_funding_usdt"] for r in en if r["demo_funding_usdt"] is not None]
        sp = [r["demo_spese_usdt"] for r in en if r["demo_spese_usdt"] is not None]
        if fu:
            out += ["", f"- sul demo, dal {min(r['giorno'] for r in en if r['demo_funding_usdt'] is not None)} ({len(fu)} giorni): "
                    f"funding incassato {sum(fu):+,.2f} USDT, commissioni pagate {sum(sp):,.2f} USDT"]
        out.append("")
    return out


# ---- G1 sul demo: esecuzioni, commissioni e funding letti da Binance (backlog P33; gate2/reports/2026-11-12-G1-funding-commissioni.md) --
# SOLA LETTURA: tre indirizzi GET firmati del conto demo, nessun ordine, nessuna scrittura su Binance né su Firebase. Il peso di ogni
# richiesta è quello della documentazione di Binance (future USDⓈ-M); l'indirizzo della macchina ne ha 2.400 al minuto, condivisi con il bot.
PESO_LETTURE = {"/fapi/v1/userTrades": 5, "/fapi/v1/commissionRate": 20, "/fapi/v1/income": 30}
GIORNI_CHIUSI = 5                      # i 5 giorni UTC chiusi più quello in corso
PAUSA_TRA_RICHIESTE_S = 0.2
PESO_MASSIMO_SEZIONE = 1000            # meno della metà del minuto dell'indirizzo: il bot deve poter continuare a lavorare
PESO_USATO_MASSIMO = 600               # se Binance dice che nel minuto l'indirizzo ha già usato di più, la sezione smette di chiedere
                                       # (600 finché il limite del demo non è misurato: revisione del 12 novembre 2026, problema 80)
TEMPO_MASSIMO_S = 180.0                # la richiesta «stato» della macchina deve restare breve
PAGINE_MASSIME = 10
ERRORI_DI_FILA_MASSIMI = 3
ORA_DOPO_LA_DECISIONE_S = 2 * 3600     # G1 decide alle 00:05 UTC e il demo esegue entro l'ora dopo: dalle 02:00 le posizioni sono quelle nuove
# la finestra del ribilancio del demo (revisione del 12 novembre 2026, problema 79): la decisione delle 00:05, l'ora degli ordini limite e
# il tentativo dopo un errore (30 minuti); dentro, nessuna richiesta, perché un blocco dell'indirizzo fermerebbe anche il bot del demo
FINESTRA_VIETATA = ((23 * 60 + 50) * 60, (1 * 60 + 45) * 60)   # dalle 23:50 alle 01:45 UTC, in secondi dalla mezzanotte
MONETE_ASSENTI_MASSIME = 10


class LimiteInLettura(Exception):
    """Binance risponde 429 o 418 a una lettura della sezione: ci si ferma al primo segnale, senza che il cliente del demo riprovi
    (revisione del 12 novembre 2026, problema 80). Non è un ``RuntimeError``: ferma tutte le richieste dopo."""


def nella_finestra_vietata(now: float) -> bool:
    s = int(now) % 86400
    return s >= FINESTRA_VIETATA[0] or s < FINESTRA_VIETATA[1]


class SoloLettura:
    """La funzione HTTP del cliente del demo per questa sezione: solo GET e solo gli indirizzi della lettura (più l'ora di Binance, che il
    cliente rilegge da solo dopo un errore d'orario); qualunque altra richiesta si rifiuta prima di partire. Tiene il peso usato
    nel minuto dall'indirizzo (intestazione ``X-MBX-USED-WEIGHT-1M`` di Binance)."""

    AMMESSI = frozenset(PESO_LETTURE) | {"/fapi/v1/time"}

    def __init__(self, http=None) -> None:
        if http is None:
            import requests
            http = requests.request
        self.http, self.peso_usato = http, None

    def __call__(self, metodo, url, **kw):
        from urllib.parse import urlparse
        percorso = urlparse(url).path
        if metodo != "GET" or percorso not in self.AMMESSI:
            raise ValueError(f"sola lettura: {metodo} {percorso} non ammesso")
        r = self.http(metodo, url, **kw)
        if getattr(r, "status_code", None) in (418, 429):
            attesa = (getattr(r, "headers", None) or {}).get("Retry-After")
            raise LimiteInLettura(f"Binance {r.status_code} su GET {percorso}: la sezione si ferma"
                                  + (f" (Retry-After {attesa} s)" if attesa is not None else ""))
        try:
            self.peso_usato = int((getattr(r, "headers", None) or {}).get("X-MBX-USED-WEIGHT-1M"))
        except (TypeError, ValueError):
            pass
        return r


class _Basta(Exception):
    """La sezione smette di chiedere (tetto di peso o di tempo, limite di Binance, rete): il motivo va nella riga «non letto»."""


def _motivo(exc) -> str:
    from bot.portafoglio.demo_binance import senza_firma
    testo = senza_firma(str(exc))[:160]
    return testo if isinstance(exc, _Basta) else f"{type(exc).__name__}: {testo[:120]}"


class _Lettore:
    """Le richieste della sezione, una per volta con una pausa, dentro il tetto di peso e di tempo. Un errore di Binance su una
    richiesta (``RuntimeError`` del cliente) si passa a chi chiede; un limite di Binance, un errore di rete o un rifiuto della
    sola lettura fermano tutte le richieste dopo."""

    def __init__(self, cliente, dormi=time.sleep, peso_massimo: int = PESO_MASSIMO_SEZIONE, tempo_massimo_s: float = TEMPO_MASSIMO_S,
                 orologio=time.monotonic) -> None:
        self.c, self.dormi, self.peso_massimo, self.tempo_massimo_s = cliente, dormi, peso_massimo, tempo_massimo_s
        self.orologio, self.inizio = orologio, orologio()
        self.richieste, self.peso, self.fermo = 0, 0, None

    def peso_usato(self):
        return getattr(getattr(self.c, "http", None), "peso_usato", None)

    def chiedi(self, percorso: str, parametri: dict):
        if self.fermo:
            raise _Basta(self.fermo)
        peso, usato = PESO_LETTURE[percorso], self.peso_usato()
        if self.peso + peso > self.peso_massimo:
            self.fermo = f"tetto di peso della sezione ({self.peso_massimo})"
        elif usato is not None and usato > PESO_USATO_MASSIMO:
            self.fermo = f"l'indirizzo ha già usato {usato} di peso nel minuto (oltre {PESO_USATO_MASSIMO})"
        elif self.orologio() - self.inizio > self.tempo_massimo_s:
            self.fermo = f"tempo della sezione oltre {self.tempo_massimo_s:g} s"
        if self.fermo:
            raise _Basta(self.fermo)
        if self.richieste:
            self.dormi(PAUSA_TRA_RICHIESTE_S)
        self.richieste += 1
        self.peso += peso
        try:
            return self.c.chiedi("GET", percorso, parametri, firmata=True)
        except RuntimeError:
            raise
        except Exception as exc:  # noqa: BLE001
            self.fermo = _motivo(exc)
            raise _Basta(self.fermo) from None


def _pagine(lettore: _Lettore, percorso: str, parametri: dict, chiave, limite: int = 1000) -> tuple:
    """Tutte le righe fra ``startTime`` e ``endTime``, a pagine di ``limite``: la pagina dopo riparte dall'ora più alta letta (non
    +1: le righe con la stessa ora, come i regolamenti di molte monete, non si perdono) e le righe già viste si scartano. Se una pagina
    intera ha la stessa ora si va avanti di 1 ms e la lettura si dice forse incompleta. Restituisce le righe e se è completa."""
    righe, viste, inizio, completo, fine = [], set(), int(parametri["startTime"]), True, int(parametri["endTime"])
    for _ in range(PAGINE_MASSIME):
        pagina = lettore.chiedi(percorso, {**parametri, "startTime": inizio, "limit": limite}) or []
        nuove = [r for r in pagina if chiave(r) not in viste]
        viste.update(chiave(r) for r in nuove)
        righe += nuove
        if len(pagina) < limite:
            return righe, completo
        alta = max(int(r.get("time") or 0) for r in pagina)
        if alta <= inizio:
            alta, completo = inizio + 1, False
        if alta > fine:
            return righe, completo
        inizio = alta
    return righe, False


def _giorno(t_s: float) -> str:
    return time.strftime("%Y-%m-%d", time.gmtime(t_s))


def _regolamento(t_ms) -> str:
    """Il regolamento del funding: «00», «08», «16», o «altre» (le monete con il funding ogni 1 o 4 ore)."""
    h = time.gmtime(int(t_ms) / 1000).tm_hour
    return f"{h:02d}" if h in (0, 8, 16) else "altre"


def esecuzioni_per_giorno(righe: list) -> dict:
    """Le esecuzioni del demo (``/fapi/v1/userTrades``) giorno per giorno: valore scambiato, commissione pagata (in USDT; quelle in
    un'altra valuta si contano a parte), valore eseguito «maker» (ordine nel libro) e numero di esecuzioni."""
    out: dict = {}
    for r in righe:
        if not r.get("time"):
            continue
        x = out.setdefault(_giorno(int(r["time"]) / 1000), {"valore": 0.0, "commissione": 0.0, "maker": 0.0, "n": 0, "altre_valute": 0})
        v = abs(float(r.get("quoteQty") or 0))
        x["valore"] += v
        x["n"] += 1
        if r.get("maker") in (True, "true"):
            x["maker"] += v
        if (r.get("commissionAsset") or "USDT") == "USDT":
            x["commissione"] += abs(float(r.get("commission") or 0))
        else:
            x["altre_valute"] += 1
    return out


def funding_per_giorno(righe: list, giorni_chiusi: set) -> tuple:
    """Gli incassi di funding (``FUNDING_FEE``, + incassato) per giorno e regolamento, con le monete pagate alle 08 e alle 16; e per
    moneta nei giorni chiusi."""
    giorni: dict = {}
    monete: dict = {}
    for r in righe:
        if (r.get("asset") or "USDT") != "USDT" or not r.get("time"):
            continue
        g, reg, v, s = _giorno(int(r["time"]) / 1000), _regolamento(r["time"]), float(r.get("income") or 0), r.get("symbol") or "?"
        x = giorni.setdefault(g, {"totale": 0.0, "00": 0.0, "08": 0.0, "16": 0.0, "altre": 0.0, "monete_08": set(), "monete_16": set()})
        x["totale"] += v
        x[reg] += v
        if reg in ("08", "16"):
            x[f"monete_{reg}"].add(s)
        if g in giorni_chiusi:
            m = monete.setdefault(s, {"totale": 0.0, "00": 0.0, "08": 0.0, "16": 0.0, "altre": 0.0})
            m["totale"] += v
            m[reg] += v
    return giorni, monete


def cliente_di_sola_lettura():
    """Il cliente del conto demo (``ClienteDemo``: solo ``demo-fapi.binance.com``) con la funzione HTTP di sola lettura; None senza
    le chiavi del conto demo (su GitHub non ci sono)."""
    from bot.portafoglio.demo_binance import ClienteDemo, segreto_dall_ambiente
    k, s = os.environ.get("BINANCE_DEMO_API_KEY", ""), segreto_dall_ambiente()
    return ClienteDemo(k, s, http=SoloLettura()) if k and s else None


def sezione_demo_esecuzioni(fb, cliente=None, now: float | None = None, dormi=time.sleep,
                            peso_massimo: int = PESO_MASSIMO_SEZIONE) -> list:
    """Quanto costano davvero gli ordini di G1 sul demo e quanto funding incassa, moneta per moneta (backlog P33), per i 5 giorni UTC
    chiusi più quello in corso: esecuzioni (valore, commissione, quota maker e taker), commissione del conto, funding per giorno e
    regolamento, le 10 monete con il funding più grande, le monete del paper di G1 che il demo non ha. Sola lettura; un endpoint che
    non risponde diventa una riga «non letto», e lo stato non fallisce mai per questa sezione."""
    titolo = "## G1 sul demo: esecuzioni, commissioni e funding letti da Binance (sola lettura)"
    try:
        return _demo_esecuzioni(fb, cliente, time.time() if now is None else float(now), dormi, peso_massimo, titolo)
    except Exception as exc:  # noqa: BLE001
        return [titolo, f"- non letto: {_motivo(exc)}", ""]


def _demo_esecuzioni(fb, cliente, now: float, dormi, peso_massimo: int, titolo: str) -> list:
    if nella_finestra_vietata(now):
        return [titolo, "- non letto: finestra del ribilancio del demo (23:50-01:45 UTC), richiedere dopo", ""]
    oggi = int(now // 86400)
    giorni = [_giorno(d * 86400) for d in range(oggi - GIORNI_CHIUSI, oggi + 1)]
    chiusi = set(giorni[:-1])
    da_ms, a_ms = (oggi - GIORNI_CHIUSI) * 86400_000, int(now * 1000)
    if cliente is None:
        try:
            cliente = cliente_di_sola_lettura()
        except Exception as exc:  # noqa: BLE001  (il testo dell'errore di una chiave non si stampa)
            return [titolo, f"- non letto: chiave del conto demo non leggibile ({type(exc).__name__})", ""]
        if cliente is None:
            return [titolo, "- non letto: manca la chiave del conto demo (BINANCE_DEMO_API_KEY nel .env; c'è solo sulla macchina)", ""]
    lt = _Lettore(cliente, dormi=dormi, peso_massimo=peso_massimo)
    out = [titolo, f"Dal {giorni[0]} 00:00 a {_ts(now)}; USDT; funding: + incassato; maker = ordine rimasto nel libro (commissione bassa)."]

    def rtdb(ramo):
        try:
            v = fb.get_rtdb(ramo) if fb is not None else None
        except Exception:  # noqa: BLE001
            return {}
        return v if isinstance(v, dict) else {}

    # 1. la commissione del conto
    try:
        cr = lt.chiedi("/fapi/v1/commissionRate", {"symbol": "BTCUSDT"}) or {}
        out.append(f"- commissione del conto (BTCUSDT): maker {100 * float(cr['makerCommissionRate']):.4f}%, "
                   f"taker {100 * float(cr['takerCommissionRate']):.4f}%")
    except Exception as exc:  # noqa: BLE001
        out.append(f"- commissione del conto: non letta: {_motivo(exc)}")

    # 2. gli incassi: funding e commissioni (le commissioni dicono anche quali monete hanno avuto esecuzioni)
    def incassi(tipo):
        try:
            righe, completo = _pagine(lt, "/fapi/v1/income", {"incomeType": tipo, "startTime": da_ms, "endTime": a_ms},
                                      lambda r: (r.get("tranId"), r.get("symbol"), r.get("time"), r.get("income")))
            return righe, ("" if completo else f"oltre {PAGINE_MASSIME} pagine: forse incompleto")
        except Exception as exc:  # noqa: BLE001
            return None, _motivo(exc)
    funding, nota_funding = incassi("FUNDING_FEE")
    commissioni, nota_commissioni = incassi("COMMISSION")

    # 3. le esecuzioni, moneta per moneta: prima quelle con più commissioni (senza le commissioni, le monete con funding)
    peso_moneta: dict = {}
    for r in commissioni if commissioni is not None else (funding or []):
        if r.get("symbol"):
            peso_moneta[r["symbol"]] = peso_moneta.get(r["symbol"], 0.0) + abs(float(r.get("income") or 0))
    simboli = sorted(peso_moneta, key=lambda s: (-peso_moneta[s], s))
    esecuzioni, lette, errori, di_fila, nota_esec = [], 0, 0, 0, ""
    for s in simboli:
        try:
            righe, completo = _pagine(lt, "/fapi/v1/userTrades", {"symbol": s, "startTime": da_ms, "endTime": a_ms}, lambda r: r.get("id"))
            esecuzioni += righe
            lette, di_fila = lette + 1, 0
            if not completo:
                nota_esec = f"{s}: oltre {PAGINE_MASSIME} pagine, forse incompleto"
        except RuntimeError as exc:
            errori, di_fila = errori + 1, di_fila + 1
            nota_esec = _motivo(exc)
            if di_fila >= ERRORI_DI_FILA_MASSIMI:
                nota_esec = f"{ERRORI_DI_FILA_MASSIMI} errori di fila, l'ultimo {nota_esec}"
                break
        except Exception as exc:  # noqa: BLE001
            nota_esec = _motivo(exc)
            break
    if not simboli:
        out.append("- esecuzioni: non lette: " + (f"servono gli incassi per sapere le monete ({nota_commissioni or nota_funding})"
                                                  if commissioni is None and funding is None else "nessuna esecuzione nei giorni (nessuna commissione negli incassi)"))
    else:
        per_g = esecuzioni_per_giorno(esecuzioni)
        out += [f"Esecuzioni (`userTrades`) lette per {lette} monete su {len(simboli)}"
                + (f"; non lette {len(simboli) - lette}: {nota_esec}" if lette < len(simboli) else (f"; {nota_esec}" if nota_esec else "")),
                "", "| giorno | valore scambiato | commissione | in % del valore | maker | taker | esecuzioni |", "|---|---|---|---|---|---|---|"]
        tot = {"valore": 0.0, "commissione": 0.0, "maker": 0.0, "n": 0, "altre_valute": 0}
        for g in giorni:
            x = per_g.get(g)
            if not x:
                out.append(f"| {g} | 0 | 0 | — | — | — | 0 |")
                continue
            for k in tot:
                tot[k] += x[k]
            out.append(_riga_esecuzioni(g, x))
        out.append(_riga_esecuzioni(f"{len(giorni)} giorni", tot))
        if tot["altre_valute"]:
            out.append(f"- commissioni in un'altra valuta (non sommate): {tot['altre_valute']} esecuzioni")
        if commissioni is not None:
            da_incassi = sum(-float(r.get("income") or 0) for r in commissioni if (r.get("asset") or "USDT") == "USDT")
            out.append(f"- controllo: commissioni dagli incassi {da_incassi:,.4f} USDT, dalle esecuzioni {tot['commissione']:,.4f} USDT")
    if commissioni is None:
        out.append(f"- incassi delle commissioni: non letti: {nota_commissioni}")

    # 4. il funding per giorno e regolamento, e le 10 monete più grandi nei giorni chiusi
    pesi_paper = {s: float(w) for s, w in rtdb("/paper_g1/posizioni").items() if _numero(w)}
    diario_paper = rtdb("/paper_g1/diario")
    per_monete = {}
    if funding is None:
        out.append(f"- funding: non letto: {nota_funding}")
    else:
        per_g, per_monete = funding_per_giorno(funding, chiusi)
        out += ["", "Funding (`income`, FUNDING_FEE) per regolamento UTC; monete: pagate alle 16 (o alle 08) sul demo / nel paper G1."
                + (f" {nota_funding}" if nota_funding else ""),
                "", "| giorno | totale | 00 | 08 | 16 | altre ore | monete demo/paper |", "|---|---|---|---|---|---|---|"]
        for g in giorni:
            x = per_g.get(g) or {"totale": 0.0, "00": 0.0, "08": 0.0, "16": 0.0, "altre": 0.0, "monete_08": set(), "monete_16": set()}
            d = x["monete_16"] or x["monete_08"]
            p = diario_paper.get(g) if isinstance(diario_paper.get(g), dict) else {}
            np_ = int(p.get("long") or 0) + int(p.get("short") or 0) if p else None
            out.append(f"| {g}{' (in corso)' if g not in chiusi else ''} | {x['totale']:+.4f} | {x['00']:+.4f} | {x['08']:+.4f} | "
                       f"{x['16']:+.4f} | {x['altre']:+.4f} | {len(d) if d else '—'}/{np_ if np_ is not None else '—'} |")
        grandi = sorted(per_monete, key=lambda s: (-abs(per_monete[s]["totale"]), s))[:10]
        if grandi:
            out += ["", f"Le 10 monete con il funding più grande nei {GIORNI_CHIUSI} giorni chiusi (peso nel paper G1 di oggi).", "",
                    "| moneta | 5 giorni | 00 | 08 | 16 | altre ore | peso paper |", "|---|---|---|---|---|---|---|"]
            for s in grandi:
                m = per_monete[s]
                out.append(f"| {s} | {m['totale']:+.4f} | {m['00']:+.4f} | {m['08']:+.4f} | {m['16']:+.4f} | {m['altre']:+.4f} | "
                           + (f"{100 * pesi_paper[s]:+.2f}% |" if s in pesi_paper else "— |"))

    # 5. le monete del paper di G1 che il demo non ha avuto
    out.append("")
    assenti: dict = {}
    for k, x in sorted(rtdb("/demo_binance/ribilanciamenti").items()):
        if str(k)[:10] not in giorni or not isinstance(x, dict) or x.get("solo_eventi"):
            continue
        for s in x.get("monete_mancanti_sul_demo") or []:
            assenti.setdefault((s, "mancante sul demo"), set()).add(str(k)[:10])
        for r in x.get("rifiutati") or []:
            if isinstance(r, dict) and r.get("simbolo"):
                assenti.setdefault((r["simbolo"], "rifiutata"), set()).add(str(k)[:10])
    elenco = sorted(assenti.items(), key=lambda t: (-len(t[1]), t[0]))
    out.append("- monete del paper G1 che il demo non ha avuto (ribilanciamenti del demo): " + (", ".join(
        f"{s} {come} {len(gg)} giorni dal {min(gg)}" for (s, come), gg in elenco[:MONETE_ASSENTI_MASSIME]) or "nessuna")
        + (f" e altre {len(elenco) - MONETE_ASSENTI_MASSIME}" if len(elenco) > MONETE_ASSENTI_MASSIME else ""))
    if funding is not None and pesi_paper:
        dalle_ms = oggi * 86400_000 + ORA_DOPO_LA_DECISIONE_S * 1000
        dopo = [r for r in funding if int(r.get("time") or 0) >= dalle_ms]
        if not any(time.gmtime(int(r["time"]) / 1000).tm_hour >= 8 for r in dopo):
            out.append("- il paper G1 di oggi contro il funding del demo, per nome: dopo il regolamento delle 08 UTC "
                       "(i pesi dei giorni passati del paper non sono su Firebase)")
        else:
            pagate = {r.get("symbol") for r in dopo}
            senza = {s: w for s, w in pesi_paper.items() if w and s not in pagate}
            out.append(f"- nel paper G1 di oggi ma senza funding sul demo dalle 02 UTC: {len(senza)} monete su "
                       f"{sum(1 for w in pesi_paper.values() if w)}, peso lordo {100 * sum(abs(w) for w in senza.values()):.2f}%"
                       + (": " + ", ".join(f"{s} {100 * w:+.2f}%" for s, w in sorted(senza.items(), key=lambda t: -abs(t[1]))[:8])
                          if senza else ""))
    # la riga delle richieste subito sotto il titolo: con il taglio dei 20.000 caratteri dell'agente resta visibile (problema 81)
    usato = lt.peso_usato()
    out.insert(1, f"- richieste a Binance di questa sezione: {lt.richieste}, peso {lt.peso} (userTrades 5, income 30, commissionRate 20)"
               + (f"; peso usato dall'indirizzo nel minuto {usato}" if usato is not None else "")
               + (f"; fermata: {lt.fermo}" if lt.fermo else ""))
    return out + [""]


def _numero(x) -> bool:
    try:
        float(x)
        return True
    except (TypeError, ValueError):
        return False


def _riga_esecuzioni(g: str, x: dict) -> str:
    v = x["valore"]
    if v <= 0:
        return f"| {g} | 0 | {x['commissione']:.4f} | — | — | — | {x['n']} |"
    return (f"| {g} | {v:,.2f} | {x['commissione']:.4f} | {100 * x['commissione'] / v:.4f}% | {100 * x['maker'] / v:.0f}% | "
            f"{100 * (v - x['maker']) / v:.0f}% | {x['n']} |")


def main() -> int:
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT,
                    help="dove scrivere. Sulla VPS conviene un percorso FUORI dal "
                         "repo: docs/state.md e' tracciato e lo scrive anche la "
                         "GitHub Action, quindi riscriverlo qui sporca il working "
                         "tree e fa abortire il git pull successivo — col risultato "
                         "che i comandi dopo girano sulla versione vecchia del codice")
    ap.add_argument("--no-write", action="store_true",
                    help="stampa e basta, non tocca nessun file")
    ap.add_argument("--publish-controllo", action="store_true",
                    help="dopo lo snapshot, pubblica dashboard/controllo con "
                         "generato_da=github se quello del bot e' piu' vecchio di "
                         "--se-vecchio secondi (ripiego: il bot e' la fonte)")
    ap.add_argument("--se-vecchio", type=float, default=5400.0, metavar="SECONDI",
                    help="eta' del controllo del bot oltre la quale il ripiego scrive "
                         "(default 5400 = 90 minuti: il bot pubblica ogni ora)")
    args = ap.parse_args()

    content = build()
    print(content)
    if not args.no_write:
        d = os.path.dirname(os.path.abspath(args.out))
        os.makedirs(d, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n[snapshot] scritto {args.out}")
    if args.publish_controllo:
        pubblica_controllo_se_vecchio(args.se_vecchio)
    return 0


def pubblica_controllo_se_vecchio(soglia_s: float = 5400.0) -> bool:
    """RIPIEGO GitHub del controllo orario (25 set 2026, docs/controllo_schema.md §3.8).

    Il bot e' la fonte di `dashboard/controllo` (ogni ora). GitHub Actions non
    regge l'ora (buchi misurati di 3-7 h), quindi qui si pubblica SOLO se il
    documento del bot manca o e' piu' vecchio di `soglia_s`: un bot vivo non va
    coperto da un documento che non conosce i suoi settings ne' il suo RTDB
    degradato. Ritorna True se ha pubblicato. Un errore non ferma lo snapshot:
    docs/state.md va comunque committato."""
    try:
        from bot.learning.controllo import _figlio, esegui
        fb = get_firebase()
        now = time.time()
        prec = _figlio(fb, "/controllo", "meta", "generato_at")
        try:
            prec = float(prec) if prec else None
        except (TypeError, ValueError):
            prec = None
        if prec is not None and now - prec < soglia_s:
            print(f"[controllo] il bot ha pubblicato {int(now - prec)} s fa "
                  f"(< {soglia_s:g} s): niente ripiego")
            return False
        doc = esegui(fb, "github", settings_da_bot=False, now=now, pubblica=True)
        m = doc["meta"]
        print(f"[controllo] ripiego GitHub pubblicato: sistema {m['semaforo_sistema']}, "
              f"paper {m['semaforo_paper']}, {len(doc['salute'].get('anomalie') or [])} "
              f"anomalie (bot: {'mai visto' if prec is None else f'{int(now - prec)} s fa'})")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[controllo] ripiego saltato: {exc}")
        return False


if __name__ == "__main__":
    raise SystemExit(main())
