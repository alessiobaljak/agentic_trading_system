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
    args = ap.parse_args()

    content = build()
    print(content)
    if args.no_write:
        return 0
    d = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(d, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n[snapshot] scritto {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
