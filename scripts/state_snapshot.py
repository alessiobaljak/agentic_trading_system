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

import calendar
import math
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

    Dal 27 novembre 2026 lo stato non stampa piu' queste righe: il GATE 1 e' fermo dal 13 ottobre e sta in una riga (audit del 26
    novembre, salute-1). La funzione resta, gemella di bot.core.registry.salute_registro (tests/test_doc_gate.py,
    tests/test_registry_capacity.py).

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


# L'agente della macchina tiene al massimo 20.000 caratteri di ogni risposta e taglia il mezzo, tenendo testa e coda
# (scripts/ops_agent.py, MAX_OUTPUT e truncate). Fino al 27 novembre 2026 lo «stato» ne faceva circa 51.700 e perdeva ogni giorno un
# pezzo in più delle righe del demo, che si leggono solo sulla macchina (audit del 26 novembre, salute-1). Il resto dei 20.000 è il
# margine per la riga «[firebase] connesso» e per gli avvisi stampati insieme.
LIMITE_DELLA_RISPOSTA = 19_500
GIORNI_TABELLE = 14               # le tabelle giornaliere: gli ultimi 14 giorni (i giorni prima sono nelle risposte «stato» di prima)


def build() -> str:
    fb = get_firebase()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    # la salute della macchina in cima (audit del 26 novembre 2026, salute-8): disco, memoria, orologio
    lines = [f"# Stato sistema (snapshot)", f"_Generato: {now}_", riga_della_macchina(), ""]
    # il battito e il DRY_RUN dell'unico processo del bot, subito sotto la macchina (revisione del 27 novembre 2026, problema 203)
    lines += sezione_del_bot(fb)

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
    # un solo cliente di sola lettura del demo per le due sezioni che leggono Binance (revisione del 14 novembre 2026, problema 84): il
    # primo 429 o 418 e il peso usato dall'indirizzo valgono per tutte e due; senza chiave ognuna scrive da sola il suo «non letto»
    try:
        cliente_demo = cliente_di_sola_lettura()
    except Exception:  # noqa: BLE001  (il testo dell'errore di una chiave non si stampa)
        cliente_demo = None
    lines += sezione_demo_esecuzioni(fb, cliente=cliente_demo)
    lines += sezione_pesi_g1_oggi(fb, cliente=cliente_demo)
    lines += sezione_funding_demo_paper(fb, cliente=cliente_demo)

    # --- il vecchio sistema, fermo dal 13 ottobre 2026 (ops/gate_fermo): in fondo (audit del 26 novembre 2026, salute-1) ---
    testa, dettagli = sezioni_vecchio_sistema(fb)
    testo = "\n".join(lines + testa + dettagli)
    if len(testo) > LIMITE_DELLA_RISPOSTA and os.environ.get("GITHUB_ACTIONS") != "true":
        # oltre il limite l'agente taglierebbe il mezzo in silenzio, cioè le righe del demo: restano fuori prima le sezioni del
        # vecchio sistema, che non cambiano più e sono intere in docs/state.md (lo fa GitHub, dove lo stato è più corto). Su GitHub
        # nessuno taglia la risposta e docs/state.md resta intero (revisione del 27 novembre 2026, problema 205)
        fuori = len("\n".join(dettagli))
        testo = "\n".join(lines + testa + [
            f"- le altre sezioni del vecchio sistema ({fuori} caratteri) restano fuori: con loro lo stato "
            f"passerebbe i {LIMITE_DELLA_RISPOSTA} caratteri e l'agente della macchina ne taglierebbe il mezzo; sono intere in "
            f"docs/state.md (lo fa GitHub)", ""])
    return testo


BATTITO_MASSIMO_S = 900


def sezione_del_bot(fb) -> list:
    """Lo stato, l'ultimo battito e il DRY_RUN dell'unico processo del bot (``bot/main.py``: scrive ``/bot_status`` e il battito a ogni
    giro), che fa girare i paper, il demo e il conto vero. In cima allo stato: un bot bloccato o un DRY_RUN falso non si devono
    leggere come un dato del vecchio sistema fermo (revisione del 27 novembre 2026, problema 203)."""
    status = fb.get_rtdb("/bot_status") or {}
    status = status if isinstance(status, dict) else {}
    hb = status.get("heartbeat")
    # 900s (era 180): il market scan tocca 200 coin con pacing e puo' durare
    # minuti, durante i quali l'heartbeat non si aggiorna. A 180s il bot risultava
    # "offline" mentre stava lavorando — falso allarme ricorrente. Il tick e' 30s,
    # quindi 15 minuti di silenzio restano un segnale vero di blocco.
    try:
        eta = time.time() - float(hb)
    except (TypeError, ValueError):
        eta = None
    online = eta is not None and eta < BATTITO_MASSIMO_S
    dry = status.get("dry_run", "—")
    return [
        "## Il bot (un solo processo: paper, demo e conto vero)",
        f"- stato: **{status.get('state', '—')}** ("
        + ("🟢 online" if online else "🔴 **offline**" + (f": nessun battito da {eta / 60:.0f} minuti" if eta is not None else "")) + ")",
        f"- ultimo heartbeat: {_ts(hb)}",
        f"- DRY_RUN: {dry}" + ("" if dry is True or dry == "—" else " **⚠️ non vero: i soldi veri non sono più bloccati dal DRY_RUN**"),
        "",
    ]


def sezioni_vecchio_sistema(fb) -> tuple:
    """Il vecchio sistema (gate, strategie, orchestratore), fermo dal 13 ottobre 2026 (``ops/gate_fermo``): la testa (regime, equity,
    prezzi e GATE 1 in una riga) e le altre sezioni. In fondo allo stato; la tabella delle coppie validate del GATE 1 (249 righe, circa
    33.000 caratteri) non si stampa più (audit del 26 novembre 2026, salute-1). Lo stato del processo, il battito e il DRY_RUN sono in
    cima, in ``sezione_del_bot`` (revisione del 27 novembre 2026, problema 203)."""
    status = fb.get_rtdb("/bot_status") or {}
    status = status if isinstance(status, dict) else {}
    equity = fb.get_rtdb("/account/equity")
    eq_str = f"${float(equity):,.2f}" if equity is not None else "—"
    # --- GATE 1: registro di validazione cumulativo, in una riga (quante coppie, quando) ---
    reg = fb.get_doc("strategy_registry", "validated") or {}
    pairs = decode_pairs(reg.get("pairs"))
    validated = reg.get("validated", []) or []
    testa = [
        "## Vecchio sistema (fermo dal 13 ottobre)",
        f"- regime: {status.get('regime', '—')}",
        f"- equity: **{eq_str}**",
        # sorgente prezzi: True = stream vivo (ogni variazione, in ordine);
        # False = ripiego sulle candele 1m (tocchi si', ordine no)
        f"- stream prezzi: {'🟢 attivo' if status.get('price_stream') else '🟡 candele REST'}",
        f"- GATE 1: {len(validated)} coppie validate (>= {reg.get('min_passes', 3)} pass OOS) su {len(pairs)} nel registro, copertura "
        f"{reg.get('coins_covered', 0)}/{reg.get('universe_size', 0)} crypto; aggiornato {_ts(reg.get('updated_at'))}",
        "",
    ]
    lines = []

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
    return testa, lines


# ---- la salute della macchina in una riga (audit del 26 novembre 2026, salute-8): disco, memoria, orologio ----
TEMPO_COMANDO_S = 5.0
DISCO_QUASI_PIENO = 90            # % usata del disco oltre cui la riga lo dice in grassetto
MEMORIA_QUASI_FINITA = 0.10       # memoria disponibile sotto il 10% del totale: in grassetto


def _esegui_comando(comando: list) -> str:
    """Un comando di sola lettura della macchina, senza shell, con un tempo massimo e la lingua C (le parole dell'uscita non
    cambiano con la lingua della macchina). Un codice diverso da zero è un errore."""
    import subprocess
    p = subprocess.run(comando, capture_output=True, text=True, timeout=TEMPO_COMANDO_S, env={**os.environ, "LC_ALL": "C"})
    if p.returncode != 0:
        raise RuntimeError(f"codice {p.returncode}")
    return p.stdout


def _leggi_df(testo: str) -> str:
    campi = testo.strip().splitlines()[1].split()          # Filesystem Size Used Avail Use% Mounted (df -P: una riga sola)
    usato = int(campi[4].rstrip("%"))
    riga = f"disco / libero {campi[3]} su {campi[1]} (usato {usato}%)"
    return f"**{riga}: quasi pieno**" if usato >= DISCO_QUASI_PIENO else riga


def _leggi_free(testo: str) -> str:
    righe = [r.split() for r in testo.strip().splitlines()]
    nomi = righe[0]                                         # total used free shared buff/cache available
    mem = next(r for r in righe if r and r[0] == "Mem:")
    valori = dict(zip(nomi, (int(x) for x in mem[1:])))
    totale = valori["total"]
    disponibile = valori.get("available", valori["free"])
    swap = next((r for r in righe if r and r[0] == "Swap:"), None)
    riga = f"memoria disponibile {disponibile} MB su {totale}" + (f", swap usata {int(swap[2])} MB su {int(swap[1])}" if swap else "")
    return f"**{riga}: quasi finita**" if totale and disponibile < MEMORIA_QUASI_FINITA * totale else riga


def _leggi_timedatectl(testo: str) -> str:
    valori = {}
    for r in testo.splitlines():
        if ":" in r:
            k, v = r.split(":", 1)
            valori[k.strip().lower()] = v.strip()
    sinc = next(v for k, v in valori.items() if k.endswith("synchronized"))     # «System clock synchronized» (prima «NTP synchronized»)
    ntp = next((v for k, v in valori.items() if k in ("ntp service", "network time on")), None)
    if sinc not in ("yes", "no"):
        raise ValueError(sinc[:20])
    riga = "orologio sincronizzato" if sinc == "yes" else "**orologio NON sincronizzato**"
    return riga + (f" (NTP {ntp})" if ntp else "")


def riga_della_macchina(esegui=None) -> str:
    """Disco libero (``df -hP /``), memoria (``free -m``) e sincronizzazione dell'orologio (``timedatectl``) in una riga: il disco
    pieno ferma in silenzio i file dei paper e il git pull, un orologio che salta fa rifiutare le richieste firmate. Un comando che
    manca, va in errore o non risponde diventa «non letto»: lo stato non fallisce mai per questa riga. Su GitHub non si legge
    (sarebbe la macchina di GitHub, non quella del bot)."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return "- macchina: non letta qui (lo stato lo fa GitHub): disco, memoria e orologio sono nella risposta «stato» della macchina"
    esegui = esegui or _esegui_comando
    parti = []
    for nome, comando, leggi in (("disco", ["df", "-hP", "/"], _leggi_df), ("memoria", ["free", "-m"], _leggi_free),
                                 ("orologio", ["timedatectl"], _leggi_timedatectl)):
        try:
            parti.append(leggi(esegui(comando)))
        except Exception as exc:  # noqa: BLE001  (comando assente, errore, tempo scaduto, uscita diversa: la riga non si rompe)
            parti.append(f"{nome} non letto ({type(exc).__name__})")
    return "- macchina: " + " · ".join(parti)


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
                                                                         for r in x["rifiutati"][:3]) if x.get("rifiutati") else "")
                     + _resti_rifiutati(x))
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


def strategia_del_conto_vero() -> str:
    """La strategia che il conto vero esegue (``bot/portafoglio/conto_vero.py``, STRATEGIA: F5 dal 25 novembre 2026, decisione del
    proprietario); vuota se il modulo non si legge."""
    try:
        from bot.portafoglio.conto_vero import STRATEGIA
        return str(STRATEGIA)
    except Exception:  # noqa: BLE001
        return ""


def strategia_del_processo(fb, nel_codice: str) -> tuple:
    """La strategia che il processo del bot esegue sul conto vero: quella scritta dal conto vero al suo avvio
    (``/conto_vero/avvio/strategia``), se l'avvio è di questo processo; altrimenti quella del codice sul disco. Fra un commit che
    cambia la strategia e il riavvio i due sono diversi, e la nota lo dice (revisione del 27 novembre 2026, problema 207).
    L'avvio è di un processo di prima se il suo commit non è quello che il processo di adesso scrive in ``/conto_vero/versione``
    (HEAD all'avvio del processo): allora vale il codice. Restituisce la strategia e la nota (vuota se non serve)."""
    av = fb.get_rtdb("/conto_vero/avvio")
    nel_processo = str(av.get("strategia") or "") if isinstance(av, dict) else ""
    if not nel_processo:
        return nel_codice, ""
    ver = fb.get_rtdb("/conto_vero/versione")
    c_avvio, c_ora = av.get("commit_in_esecuzione"), (ver.get("commit") if isinstance(ver, dict) else None)
    if c_avvio and c_ora and c_avvio != c_ora:
        return nel_codice, ""
    if nel_codice and nel_processo != nel_codice:
        return nel_processo, (f"- **strategia: nel codice {nel_codice}, nel processo {nel_processo}** (avvio del conto vero del "
                              f"{_ts(av.get('ora'))}): manca il riavvio")
    return nel_processo, ""


def _e_un_giorno(k) -> bool:
    k = str(k)
    return len(k) == 10 and k[4] == k[7] == "-" and (k[:4] + k[5:7] + k[8:]).isdigit()


def _scaduti_senza_mercato(scaduti: dict) -> str:
    return (f"ordini limite scaduti senza il resto a mercato ({_ts(scaduti.get('ora'))}): "
            f"{len(scaduti.get('monete') or [])} monete, {str(scaduti.get('motivo'))[:80]}")


def _resti_rifiutati(x: dict) -> str:
    """I resti a mercato rifiutati di un ribilancio (``ribilanciamenti/{chiave}/resti_rifiutati``, scritti dal bot dal primo riavvio
    con le correzioni del 27 novembre 2026, audit del 26 novembre, ordini-4): quanti, e i primi tre con il peso e l'errore."""
    resti = x.get("resti_rifiutati") or []
    resti = [r for r in (resti.values() if isinstance(resti, dict) else resti) if isinstance(r, dict)]
    if not resti:
        return ""
    return f"; resti a mercato rifiutati {len(resti)}: " + "; ".join(
        f"{r.get('simbolo')}" + (f" ({100 * float(r['peso']):+.2f}% del conto)" if _numero(r.get("peso")) else "")
        + f" {str(r.get('errore'))[:80]}" for r in resti[:3])


def righe_ultimo_ribilancio_vero(fb, strategia: str) -> list:
    """L'ultimo ribilancio del conto vero (``/conto_vero/ribilanciamenti/{giorno}``, se c'è; audit del 26 novembre 2026, ordini-2 e
    ordini-4): ordini, eseguiti a limite e a mercato, rifiutati con il loro peso nel paper della strategia, variazioni sotto il minimo
    di Binance e il loro peso, ordini scaduti senza il resto a mercato, resti a mercato rifiutati; e le posizioni vere contro quelle
    volute. L'ultimo è il giorno più alto fra le chiavi che hanno la forma di un giorno: la chiave «in_corso» (scritta quando manca la
    chiave degli ordini, ``bot/portafoglio/conto_vero.py``) si mostra a parte (revisione del 27 novembre 2026, problema 206)."""
    righe = []
    rib = fb.get_rtdb("/conto_vero/ribilanciamenti")
    chiavi = ([k for k, v in rib.items() if _e_un_giorno(k) and isinstance(v, dict) and not v.get("solo_eventi")]
              if isinstance(rib, dict) else [])
    if chiavi:
        g = max(chiavi)
        x = rib[g]
        lim = x.get("limite") if isinstance(x.get("limite"), dict) else {}
        sm = x.get("sotto_il_minimo") if isinstance(x.get("sotto_il_minimo"), dict) else None
        rif = [r for r in x.get("rifiutati") or [] if isinstance(r, dict)]
        ramo = {"F5": "/paper_f5", "G1": "/paper_g1"}.get(strategia)
        pesi = (fb.get_rtdb(f"{ramo}/posizioni") if ramo and rif else None) or {}
        pesi = pesi if isinstance(pesi, dict) else {}

        def peso(s):
            return f" ({100 * float(pesi[s]):+.2f}% in {strategia})" if _numero(pesi.get(s)) else ""
        riga = (f"- ultimo ribilancio {g}: {x.get('ordini', 0)} ordini"
                + (f", eseguiti a limite {lim.get('eseguiti_a_limite', 0)}, a mercato {lim.get('a_mercato', 0)}" if lim else "")
                + (f"; sotto il minimo {sm.get('variazioni', 0)} variazioni "
                   f"({100 * float(sm.get('valore_in_frazione_del_conto') or 0):.1f}% del conto)" if sm else "")
                + f"; rifiutati {len(rif)}" + (": " + "; ".join(f"{r.get('simbolo')}{peso(r.get('simbolo'))} {str(r.get('errore'))[:80]}"
                                                                  for r in rif[:3]) if rif else "")
                + (f"; monete senza i filtri del conto vero: {', '.join(map(str, x['monete_mancanti_sul_demo']))}"
                   if x.get("monete_mancanti_sul_demo") else ""))
        scaduti = x.get("scaduti_senza_mercato")
        if isinstance(scaduti, dict):
            riga += "; " + _scaduti_senza_mercato(scaduti)
        righe.append(riga + _resti_rifiutati(x))
    in_corso = rib.get("in_corso") if isinstance(rib, dict) else None
    if isinstance(in_corso, dict) and isinstance(in_corso.get("scaduti_senza_mercato"), dict):
        righe.append("- ribilancio senza la chiave degli ordini («in_corso»): " + _scaduti_senza_mercato(in_corso["scaduti_senza_mercato"]))
    cf = fb.get_rtdb("/conto_vero/confronto")
    if isinstance(cf, dict) and cf:
        dif = cf.get("differenze") or []
        righe.append(f"- posizioni vere contro volute ({_ts(cf.get('ora'))}): {cf.get('monete', 0)} monete, scarto totale "
                     f"{100 * float(cf.get('scarto_totale') or 0):.1f}% del conto; " + ("nessuna moneta oltre il 2%" if not dif else
                     "oltre il 2%: " + ", ".join(f"{d.get('simbolo')} {100 * float(d.get('scarto') or 0):+.1f}%" for d in dif[:6])))
    return righe


def sezione_conto_vero(fb) -> list:
    """Le righe del conto vero di Binance (RTDB /conto_vero, `bot/portafoglio/conto_vero.py`, nasce spento): spento e perché,
    oppure acceso con equity, stop sul conto, fermo, allarmi, l'ultimo ribilancio. Dal 25 novembre 2026 esegue F5 (salute-9); il
    titolo dice la strategia del processo, se il conto vero l'ha scritta al suo avvio (problema 207)."""
    try:
        strategia, nota = strategia_del_processo(fb, strategia_del_conto_vero())
    except Exception:  # noqa: BLE001  (un dato rotto non ferma lo stato)
        strategia, nota = strategia_del_conto_vero(), ""
    titolo = (f"## {strategia + ' sul conto vero' if strategia else 'Il conto vero'} di Binance "
              "(soldi veri; nasce spento, si accende solo con il gesto del proprietario)")
    titolo = [titolo, nota] if nota else [titolo]

    def allarmi_per_tipo() -> list:
        allarmi = fb.get_rtdb("/conto_vero/allarmi")
        return [f"- **ALLARME** {tipo.replace('_', ' ')} ({_ts(a.get('ora'))}): {a.get('testo')}"
                for tipo, a in (sorted(allarmi.items()) if isinstance(allarmi, dict) else []) if isinstance(a, dict) and a.get("testo")]

    st = fb.get_rtdb("/conto_vero/stato") or {}
    st = st if isinstance(st, dict) else {}
    if not st:
        # problema 73 (revisione dell'8 novembre 2026): gli allarmi si vedono anche senza stato (la creazione non riuscita)
        return titolo + ["- spento: nessuno stato scritto (il bot non lo ha ancora fatto girare)"] + allarmi_per_tipo() + [""]
    righe = titolo + [f"- stato: **{st.get('stato', '—')}** ({_ts(st.get('aggiornato'))})"]
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
    try:
        righe += righe_ultimo_ribilancio_vero(fb, strategia)
    except Exception as exc:  # noqa: BLE001  (un dato rotto non ferma lo stato)
        righe.append(f"- ultimo ribilancio: non letto ({type(exc).__name__})")
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


def monete_mancanti_per_giorno(ribilanciamenti: dict, giorni: list) -> dict:
    """Per ogni giorno, le monete del paper G1 che il demo non ha avuto: rifiutate o mancanti al ribilancio del demo di quel giorno, o
    dell'ultimo prima se quel giorno il demo non ha ribilanciato (tiene le posizioni di prima). I ribilanci degli eventi non contano."""
    decisioni = sorted((str(k), x) for k, x in (ribilanciamenti or {}).items()
                       if isinstance(x, dict) and len(str(k)) == 10 and not x.get("solo_eventi"))
    out = {}
    for g in giorni:
        prima = [x for k, x in decisioni if k <= g]
        x = prima[-1] if prima else {}
        m = {s for s in x.get("monete_mancanti_sul_demo") or [] if isinstance(s, str) and s}
        m |= {r["simbolo"] for r in x.get("rifiutati") or [] if isinstance(r, dict) and isinstance(r.get("simbolo"), str)}
        out[g] = m
    return out


def senza_le_monete_mancanti(righe: list, mancanti: dict, pesi: dict, rendimenti: dict) -> tuple:
    """Il guadagno del paper sulle monete che il demo non ha, giorno per giorno: la somma di peso per rendimento del giorno; demo meno
    paper senza quelle monete è la differenza più quel guadagno (audit del 26 novembre 2026, ordini-5). Il giorno senza un prezzo per
    una delle sue monete resta None; una moneta senza un peso nel paper di oggi non si conta e va nell'elenco dei «senza peso»."""
    out, senza_peso = {}, set()
    for r in righe:
        g, c = r["giorno"], 0.0
        for s in sorted(mancanti.get(g) or ()):
            w = pesi.get(s)
            if not w:
                senza_peso.add(s)
                continue
            x = (rendimenti.get(s) or {}).get(g)
            if x is None:
                c = None
                break
            c += w * x
        out[g] = None if c is None else r["differenza"] + c
    return out, senza_peso


PREZZI_MARK_GIORNALIERI = "https://fapi.binance.com/fapi/v1/markPriceKlines"   # pubblico, peso 1 a richiesta (limit sotto 100)
MONETE_DA_PREZZARE_MASSIME = 12


def rendimenti_mark_giornalieri(simboli: list, da_giorno: str, now: float, http=None, dormi=time.sleep) -> tuple:
    """Il rendimento di ogni giorno UTC dal prezzo mark pubblico di Binance (candele di un giorno: chiusura su apertura; per oggi
    l'ultimo prezzo), una richiesta per moneta con una pausa. Al primo 429 o 418 nessuna richiesta parte più, come nelle altre letture
    dello stato (problemi 80 e 84; revisione del 27 novembre 2026, problema 204): le monete rimaste restano non lette. Restituisce i
    rendimenti, le monete non lette e il motivo dello stop (vuoto se non c'è stato)."""
    if http is None:
        import requests
        http = requests.get
    da_ms = calendar.timegm(time.strptime(da_giorno, "%Y-%m-%d")) * 1000
    out, non_lette, fermo = {}, [], ""
    for i, s in enumerate(simboli):
        if i:
            dormi(PAUSA_TRA_RICHIESTE_S)
        try:
            r = http(PREZZI_MARK_GIORNALIERI, params={"symbol": s, "interval": "1d", "startTime": da_ms, "endTime": int(now * 1000),
                                                      "limit": 99}, timeout=10)
            codice = getattr(r, "status_code", 200)
            if codice in (418, 429):
                attesa = (getattr(r, "headers", None) or {}).get("Retry-After")
                fermo = f"Binance {codice}: letture fermate" + (f" (Retry-After {attesa} s)" if attesa is not None else "")
                non_lette += list(simboli[i:])
                break
            if codice != 200:
                raise RuntimeError(f"HTTP {codice}")
            out[s] = {_giorno(int(k[0]) / 1000): float(k[4]) / float(k[1]) - 1 for k in r.json() if float(k[1]) > 0}
        except Exception:  # noqa: BLE001  (una moneta non letta lascia «—» nei suoi giorni)
            non_lette.append(s)
    return out, non_lette, fermo


def sezione_demo_contro_paper(fb, now: float | None = None, http=None, dormi=time.sleep) -> list:
    """G1 sul demo contro G1 nel paper, giorno per giorno (MIGLIORARE_G1.md, voce 1): quanto costa l'esecuzione vera. Le tabelle
    mostrano gli ultimi ``GIORNI_TABELLE`` giorni; il totale e la media restano su tutti i giorni."""
    now = time.time() if now is None else float(now)
    titolo = "## G1: il demo contro il paper, giorno per giorno"
    righe = confronto_giorni(fb.get_rtdb("/demo_binance/giorni") or {}, fb.get_rtdb("/paper_g1/giorni") or {},
                             fb.get_rtdb("/paper_eventi/giorni") or {})
    if not righe:
        return [titolo, "- non ancora: servono almeno due giorni con il demo e il paper", ""]
    mostrate = righe[-GIORNI_TABELLE:]
    # demo meno paper senza le monete che il demo non ha (audit del 26 novembre 2026, ordini-5): i pesi del paper di oggi (quelli
    # dei giorni passati non sono su Firebase) per i rendimenti del giorno dai prezzi pubblici; un errore lascia la colonna vuota
    try:
        pos = fb.get_rtdb("/paper_g1/posizioni")
        pesi = {s: float(w) for s, w in (pos.items() if isinstance(pos, dict) else ()) if _numero(w) and math.isfinite(float(w))}
        rib = fb.get_rtdb("/demo_binance/ribilanciamenti")
        mancanti = monete_mancanti_per_giorno(rib if isinstance(rib, dict) else {}, [r["giorno"] for r in mostrate])
        da_prezzare = sorted({s for m in mancanti.values() for s in m if pesi.get(s)})
        rendimenti, nota_senza = {}, ""
        if da_prezzare and nella_finestra_vietata(now):
            nota_senza = "prezzi non letti: finestra del ribilancio (23:50-01:45 UTC)"
        elif da_prezzare:
            rendimenti, non_lette, fermo = rendimenti_mark_giornalieri(da_prezzare[:MONETE_DA_PREZZARE_MASSIME],
                                                                       mostrate[0]["giorno"], now, http=http, dormi=dormi)
            non_lette += da_prezzare[MONETE_DA_PREZZARE_MASSIME:]
            nota_senza = "; ".join(x for x in (fermo, f"prezzi non letti: {', '.join(non_lette)}" if non_lette else "") if x)
        senza, senza_peso = senza_le_monete_mancanti(mostrate, mancanti, pesi, rendimenti)
    except Exception as exc:  # noqa: BLE001
        senza, senza_peso, mancanti, pesi = {}, set(), None, {}
        nota_senza = f"non letto ({type(exc).__name__})"
    prima = len(righe) - len(mostrate)
    out = [titolo, "Equity a fine giorno (l'ultimo valore scritto). Dal 6 novembre il demo lavora come un conto ridotto (280 USDT, dall'8 novembre "
           "1.000), senza gli eventi; le fasi di prima sono in /demo_binance/fasi; con i minimi di Binance la differenza con il paper "
           "oscilla di più (prova 148)." + (f" Gli ultimi {GIORNI_TABELLE} giorni: i {prima} prima sono nelle risposte «stato» di prima "
                                            "e su Firebase." if prima else ""), "",
           "| giorno | demo | paper G1 | demo meno paper | eventi nel paper | senza le monete che il demo non ha |",
           "|---|---|---|---|---|---|"]
    for r in mostrate:
        ev = f"{100 * r['eventi']:+.2f}%" if r["eventi"] is not None else "—"
        pulita = f"{100 * senza[r['giorno']]:+.2f}%" if senza.get(r["giorno"]) is not None else "—"
        out.append(f"| {r['giorno']} | {100 * r['demo']:+.2f}% | {100 * r['paper']:+.2f}% | {100 * r['differenza']:+.2f}% | {ev} "
                   f"| {pulita} |")
    tot_d = 1.0
    tot_p = 1.0
    for r in righe:
        tot_d *= 1 + r["demo"]
        tot_p *= 1 + r["paper"]
    dif = [r["differenza"] for r in righe]
    media = sum(dif) / len(dif)
    osc = (sum((x - media) ** 2 for x in dif) / (len(dif) - 1)) ** 0.5 if len(dif) > 1 else None
    out += ["", f"- dal {righe[0]['giorno']} ({len(righe)} giorni): demo {100 * (tot_d - 1):+.2f}%, paper {100 * (tot_p - 1):+.2f}%; "
            f"differenza media al giorno {100 * media:+.3f}%" + (f", oscillazione {100 * osc:.3f}%" if osc is not None else "")]
    out += [_riga_senza_le_monete_mancanti(mostrate, senza, senza_peso, mancanti, pesi, nota_senza), ""]
    en = confronto_entrate(fb.get_rtdb("/demo_binance/diario") or {}, fb.get_rtdb("/paper_g1/diario") or {},
                           fb.get_rtdb("/demo_binance/giorni") or {})
    if en:
        pc = lambda x: f"{100 * x:+.3f}%" if x is not None else "—"  # noqa: E731
        out += ["Funding e spese veri, in % dell'equity del giorno (funding: + incassato; spese: + pagate; nel paper dal 6 novembre)"
                + (f"; gli ultimi {GIORNI_TABELLE} giorni." if len(en) > GIORNI_TABELLE else "."),
                "", "| giorno | funding demo | funding paper | spese demo | spese paper |", "|---|---|---|---|---|"]
        out += [f"| {r['giorno']} | {pc(r['demo_funding'])} | {pc(r['paper_funding'])} | {pc(r['demo_spese'])} | {pc(r['paper_spese'])} |"
                for r in en[-GIORNI_TABELLE:]]
        fu = [r["demo_funding_usdt"] for r in en if r["demo_funding_usdt"] is not None]
        sp = [r["demo_spese_usdt"] for r in en if r["demo_spese_usdt"] is not None]
        if fu:
            out += ["", f"- sul demo, dal {min(r['giorno'] for r in en if r['demo_funding_usdt'] is not None)} ({len(fu)} giorni): "
                    f"funding incassato {sum(fu):+,.2f} USDT, commissioni pagate {sum(sp):,.2f} USDT"]
        out.append("")
    return out


def _riga_senza_le_monete_mancanti(mostrate: list, senza: dict, senza_peso: set, mancanti, pesi: dict, nota: str) -> str:
    """La riga «demo meno paper senza le monete che il demo non ha» (audit del 26 novembre 2026, ordini-5): media e oscillazione nei
    giorni della tabella, con e senza quelle monete, e a parte il loro peso nel paper di oggi."""
    def media_osc(xs):
        m = sum(xs) / len(xs)
        return m, ((sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5 if len(xs) > 1 else None)
    titolo = "- demo meno paper senza le monete che il demo non ha"
    if mancanti is None:                                    # un errore nel calcolo della colonna
        return f"{titolo}: {nota}"
    if not any(mancanti.values()):
        return f"{titolo}: uguale (nei giorni della tabella il demo le ha avute tutte)"
    oggi = mancanti.get(mostrate[-1]["giorno"]) or set()
    peso = (f"; quelle di oggi pesano nel paper G1 il {100 * sum(abs(pesi.get(s, 0.0)) for s in oggi):.2f}% lordo del conto "
            f"({len(oggi)} monete, elenco nella sezione del demo)" if oggi else "; oggi nessuna")
    coppie = [(r["differenza"], senza[r["giorno"]]) for r in mostrate if senza.get(r["giorno"]) is not None]
    if not coppie:
        return f"{titolo}: non letto ({nota or 'nessun giorno con tutti i prezzi'})" + peso
    (m0, o0), (m1, o1) = media_osc([a for a, _ in coppie]), media_osc([b for _, b in coppie])
    return (f"{titolo} (ultima colonna; stima: pesi del paper di oggi, prezzi mark giornalieri di Binance, senza funding): in "
            f"{len(coppie)} giorn{'o' if len(coppie) == 1 else 'i'} media al giorno {100 * m1:+.3f}% (con quelle monete {100 * m0:+.3f}%)"
            + (f", oscillazione {100 * o1:.3f}% (con {100 * o0:.3f}%)" if o1 is not None else "") + peso
            + (f"; senza un peso di oggi, non contate: {', '.join(sorted(senza_peso))}" if senza_peso else "")
            + (f"; {nota}" if nota else ""))


# ---- G1 sul demo: esecuzioni, commissioni e funding letti da Binance (backlog P33; gate2/reports/2026-11-12-G1-funding-commissioni.md) --
# SOLA LETTURA: tre indirizzi GET firmati del conto demo, nessun ordine, nessuna scrittura su Binance né su Firebase. Il peso di ogni
# richiesta è quello della documentazione di Binance (future USDⓈ-M); l'indirizzo della macchina ne ha 2.400 al minuto, condivisi con il bot.
PESO_LETTURE = {"/fapi/v1/userTrades": 5, "/fapi/v1/commissionRate": 20, "/fapi/v1/income": 30,
                "/fapi/v2/positionRisk": 5}      # le posizioni del demo per i pesi di oggi (sezione_pesi_g1_oggi)
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
        self.http, self.peso_usato, self.bloccato = http, None, None

    def __call__(self, metodo, url, **kw):
        from urllib.parse import urlparse
        percorso = urlparse(url).path
        if metodo != "GET" or percorso not in self.AMMESSI:
            raise ValueError(f"sola lettura: {metodo} {percorso} non ammesso")
        if self.bloccato:      # dopo un 429 o un 418 nessuna richiesta parte più, per nessuna sezione (revisione del 14 novembre, 84)
            raise LimiteInLettura(self.bloccato)
        r = self.http(metodo, url, **kw)
        if getattr(r, "status_code", None) in (418, 429):
            attesa = (getattr(r, "headers", None) or {}).get("Retry-After")
            self.bloccato = (f"Binance {r.status_code} su GET {percorso}: le letture si fermano"
                             + (f" (Retry-After {attesa} s)" if attesa is not None else ""))
            raise LimiteInLettura(self.bloccato)
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


def sezione_pesi_g1_oggi(fb, cliente=None, now: float | None = None, dormi=time.sleep) -> list:
    """I pesi di oggi moneta per moneta, in % del conto: G1 nel paper (`/paper_g1/posizioni`, l'ultimo ribilancio) e G1 sul demo
    (posizioni vere da Binance, `positionRisk`: valore della posizione sull'equity del conto ridotto). Il paper tiene solo i pesi di
    oggi: con una lettura al giorno dopo il ribilancio e i prezzi pubblici si spiega lo scarto fra demo e paper moneta per moneta
    (research/programma7/MIGLIORARE_G1.md, voci 8, 10 e 11; backlog P33). Sola lettura: una GET firmata con la funzione
    ``SoloLettura``; fuori dalla finestra del ribilancio; un errore diventa la riga «non letto» e lo stato non fallisce mai."""
    titolo = "## G1 oggi, moneta per moneta: paper e demo (sola lettura)"
    try:
        return _pesi_g1_oggi(fb, cliente, time.time() if now is None else float(now), dormi, titolo)
    except Exception as exc:  # noqa: BLE001
        return [titolo, f"- non letto: {_motivo(exc)}", ""]


MONETE_PER_RIGA = 6
EQUITY_DEMO_MASSIMA = 1e9         # oltre, l'equity letta da Firebase non è un numero sensato (problema 85)
EQUITY_VECCHIA_S = 2 * 3600       # il demo riscrive l'equity ogni ora (demo_binance.py): oltre 2 ore si avvisa
GIORNI_FUNDING_CONFRONTO = 3      # il confronto del funding per regolamento: oggi e i due giorni prima
MONETE_FUNDING_CONFRONTO = 6      # le monete più grandi del demo nell'ultimo regolamento, accanto alle più grandi del paper
MONETE_DEL_FUNDING_PAPER = 10     # quante monete il paper pubblica per regolamento (bot/portafoglio/f5.py, MONETE_DEL_FUNDING)


def sezione_funding_demo_paper(fb, cliente=None, now: float | None = None, dormi=time.sleep) -> list:
    """Il funding di G1 regolamento per regolamento, sul demo (incassi veri di Binance, ``/fapi/v1/income`` FUNDING_FEE) contro il
    paper (``/paper_g1/funding/{giorno}/{ora}``, pubblicato dalla fase 2 del 16 novembre 2026), in % del conto di ciascuno, e nell'ultimo
    regolamento le monete più grandi (research/programma7/MIGLIORARE_G1.md, voce 3: il demo incassa meno funding del paper). Sola
    lettura; in fondo allo stato perché il taglio dei 20.000 caratteri dell'agente tiene la coda; un errore diventa «non letto»."""
    titolo = "## G1: il funding per regolamento, demo contro paper (sola lettura)"
    try:
        return _funding_demo_paper(fb, cliente, time.time() if now is None else float(now), dormi, titolo)
    except Exception as exc:  # noqa: BLE001
        return [titolo, f"- non letto: {_motivo(exc)}", ""]


def _equity_valida(st: dict) -> float:
    e = float(st["equity"]) if isinstance(st, dict) and _numero(st.get("equity")) else 0.0
    return e if math.isfinite(e) and 0 < e < EQUITY_DEMO_MASSIMA else 0.0


def _funding_demo_paper(fb, cliente, now: float, dormi, titolo: str) -> list:
    if nella_finestra_vietata(now):
        return [titolo, "- non letto: finestra del ribilancio del demo (23:50-01:45 UTC), richiedere dopo", ""]

    rotti = []

    def rtdb(ramo):
        try:
            v = fb.get_rtdb(ramo) if fb is not None else None
        except Exception:  # noqa: BLE001
            rotti.append(ramo)
            return {}
        return v if isinstance(v, dict) else {}

    oggi = int(now // 86400)
    giorni = [_giorno(d * 86400) for d in range(oggi - GIORNI_FUNDING_CONFRONTO + 1, oggi + 1)]
    paper = {g: v for g, v in rtdb("/paper_g1/funding").items() if g in giorni and isinstance(v, dict)}
    eq_demo, eq_paper = _equity_valida(rtdb("/demo_binance/stato")), _equity_valida(rtdb("/paper_g1/stato"))
    if rotti:                      # revisione del 17 novembre 2026, problema 92: Firebase che non risponde non è «non ancora»
        return [titolo, f"- non letto: Firebase non risponde ({', '.join(rotti)})", ""]
    if not paper:
        return [titolo, "- non ancora: il paper di G1 non ha funding per regolamento in questi giorni (`/paper_g1/funding`)", ""]
    if eq_demo <= 0 or eq_paper <= 0:
        return [titolo, "- non letto: manca l'equity del demo o del paper", ""]
    if cliente is None:
        try:
            cliente = cliente_di_sola_lettura()
        except Exception as exc:  # noqa: BLE001  (il testo dell'errore di una chiave non si stampa)
            return [titolo, f"- non letto: chiave del conto demo non leggibile ({type(exc).__name__})", ""]
        if cliente is None:
            return [titolo, "- non letto: manca la chiave del conto demo (c'è solo sulla macchina)", ""]
    lt = _Lettore(cliente, dormi=dormi)
    da_ms = (oggi - GIORNI_FUNDING_CONFRONTO + 1) * 86400_000
    righe, completo = _pagine(lt, "/fapi/v1/income", {"incomeType": "FUNDING_FEE", "startTime": da_ms, "endTime": int(now * 1000)},
                              lambda r: (r.get("tranId"), r.get("symbol"), r.get("time"), r.get("income")))
    return [titolo] + confronto_funding_regolamenti(righe, paper, eq_demo, eq_paper, giorni) + (
        [] if completo else ["- incassi forse incompleti (oltre il numero massimo di pagine)"]) + [""]


def confronto_funding_regolamenti(funding: list, paper: dict, eq_demo: float, eq_paper: float, giorni: list) -> list:
    """Le righe del confronto: per ogni regolamento (00, 08, 16 UTC, e «altre» per le monete con il funding ogni 1 o 4 ore) il funding
    del demo e del paper in % del proprio conto (equity di oggi di ciascuno: un'approssimazione dichiarata), e nell'ultimo regolamento
    00/08/16 le monete più grandi, demo/paper; «—» per una moneta che il paper non mette fra le sue più grandi."""
    demo: dict = {}
    for r in funding:
        if (r.get("asset") or "USDT") != "USDT" or not r.get("time") or not _numero(r.get("income")):
            continue
        k = (_giorno(int(r["time"]) / 1000), _regolamento(r["time"]))
        x = demo.setdefault(k, {"totale": 0.0, "monete": {}, "pagamenti": 0})
        v, s = float(r["income"]), r.get("symbol") or "?"
        x["totale"] += v
        x["pagamenti"] += 1
        x["monete"][s] = x["monete"].get(s, 0.0) + v
    righe, ultimo = [], None
    for g in giorni:
        p_g = paper.get(g)
        if not isinstance(p_g, dict):
            continue
        for reg in ("00", "08", "16", "altre"):
            voci = [v for h, v in sorted(p_g.items()) if isinstance(v, dict)
                    and ((str(h)[:2] == reg) if reg != "altre" else (str(h)[:2] not in ("00", "08", "16")))]
            if not voci:
                continue
            p_tot = sum(float(v["incassato"]) for v in voci if _numero(v.get("incassato")))
            p_n = sum(int(v["monete"]) for v in voci if _numero(v.get("monete")))
            d = demo.get((g, reg), {"totale": 0.0, "monete": {}, "pagamenti": 0})
            dp, pp = 100 * d["totale"] / eq_demo, 100 * p_tot / eq_paper
            # pagamenti da tutte e due le parti (problema 90): nella riga «altre» una moneta pagata ogni 4 ore conta più volte
            righe.append(f"| {g} {reg} | {dp:+.4f}% | {pp:+.4f}% | {dp - pp:+.4f}% | {d['pagamenti']}/{p_n} |")
            if reg != "altre":
                ultimo = (g, reg, d, voci[0])
    if not righe:
        return ["- nessun regolamento del paper nei giorni letti"]
    out = [f"Equity di oggi: demo {eq_demo:,.2f} USDT, paper {eq_paper:,.2f}; + incassato. Paper da `/paper_g1/funding` (dalla fase 2 del "
           "16 novembre 2026), demo dagli incassi di Binance.", "",
           "| regolamento | demo | paper | demo meno paper | pagamenti demo/paper |", "|---|---|---|---|---|"] + righe
    if ultimo:
        g, reg, d, v = ultimo
        maggiori = {s: float(x) for s, x in (v.get("maggiori") or {}).items() if _numero(x)} if isinstance(v.get("maggiori"), dict) else {}
        dal_demo = sorted(d["monete"], key=lambda s: (-abs(d["monete"][s]), s))[:MONETE_FUNDING_CONFRONTO]
        simboli = sorted(set(maggiori) | set(dal_demo), key=lambda s: (-max(abs(maggiori.get(s, 0.0)) / eq_paper,
                                                                            abs(d["monete"].get(s, 0.0)) / eq_demo), s))
        celle = [f"{s} {100 * d['monete'].get(s, 0.0) / eq_demo:+.4f}/" + (f"{100 * maggiori[s] / eq_paper:+.4f}" if s in maggiori else "—")
                 for s in simboli]
        out += ["", f"- regolamento {g} {reg}, le monete più grandi in % del conto, demo/paper (— = non fra le "
                    f"{MONETE_DEL_FUNDING_PAPER} più grandi pubblicate dal paper): " + " · ".join(celle)]
    return out


def _pesi_g1_oggi(fb, cliente, now: float, dormi, titolo: str) -> list:
    if nella_finestra_vietata(now):
        return [titolo, "- non letto: finestra del ribilancio del demo (23:50-01:45 UTC), richiedere dopo", ""]

    def rtdb(ramo):
        try:
            v = fb.get_rtdb(ramo) if fb is not None else None
        except Exception:  # noqa: BLE001
            return {}
        return v if isinstance(v, dict) else {}

    paper = {s: float(w) for s, w in rtdb("/paper_g1/posizioni").items() if _numero(w) and math.isfinite(float(w)) and float(w)}
    st = rtdb("/demo_binance/stato")
    equity = float(st["equity"]) if _numero(st.get("equity")) else 0.0
    equity = equity if math.isfinite(equity) and 0 < equity < EQUITY_DEMO_MASSIMA else 0.0     # problema 85
    vecchia = (now - float(st["aggiornato"])) if _numero(st.get("aggiornato")) else None
    demo, nota = None, ""
    if equity <= 0:
        nota = "manca l'equity del demo (`/demo_binance/stato`) o non è un numero sensato"
    else:
        if cliente is None:
            try:
                cliente = cliente_di_sola_lettura()
            except Exception as exc:  # noqa: BLE001  (il testo dell'errore di una chiave non si stampa)
                cliente, nota = None, f"chiave del conto demo non leggibile ({type(exc).__name__})"
            else:
                if cliente is None:
                    nota = "manca la chiave del conto demo (c'è solo sulla macchina)"
        if cliente is not None:
            lt = _Lettore(cliente, dormi=dormi)
            try:
                pos = lt.chiedi("/fapi/v2/positionRisk", {}) or []
                demo = {}
                for x in pos if isinstance(pos, list) else []:
                    # il segno dalla quantità, come il bot (problema 86); il valore della posizione in valore assoluto
                    s, q, n = x.get("symbol"), x.get("positionAmt"), x.get("notional")
                    if s and _numero(q) and _numero(n) and float(q) and math.isfinite(float(n)):
                        demo[s] = demo.get(s, 0.0) + math.copysign(abs(float(n)), float(q)) / equity
            except Exception as exc:  # noqa: BLE001
                demo, nota = None, _motivo(exc)
    out = [titolo, f"Letto il {_ts(now)}. In % del conto, paper/demo; + comprato, − venduto. Paper G1: `/paper_g1/posizioni` "
           f"(l'ultimo ribilancio, ai prezzi di allora); demo: `positionRisk`, valore della posizione ai prezzi di adesso sull'equity "
           f"del conto ridotto" + (f" ({equity:,.2f} USDT)" if equity > 0 else "") + ". La differenza mescola esecuzione e movimento "
           "dei prezzi dal ribilancio (problema 87): lo scarto di esecuzione allo stesso prezzo è il confronto del bot, nella sezione del demo."]
    if vecchia is not None and vecchia > EQUITY_VECCHIA_S:
        out.append(f"- attenzione: l'equity del demo è di {vecchia / 3600:.1f} ore fa ({_ts(st.get('aggiornato'))})")
    if demo is None:
        out.append(f"- demo: non letto: {nota}")
    d = demo or {}
    simboli = sorted(set(paper) | set(d), key=lambda s: (-max(abs(paper.get(s, 0.0)), abs(d.get(s, 0.0))), s))
    if not simboli:
        return out + ["- nessuna posizione nel paper né sul demo", ""]
    celle = [f"{s} {100 * paper.get(s, 0.0):+.2f}/" + (f"{100 * d.get(s, 0.0):+.2f}" if demo is not None else "—") for s in simboli]
    out += ["- " + " · ".join(celle[i:i + MONETE_PER_RIGA]) for i in range(0, len(celle), MONETE_PER_RIGA)]
    lordo_p = sum(abs(w) for w in paper.values())
    riga = f"- monete: paper {len(paper)}, demo " + (f"{len(d)}" if demo is not None else "—") + f"; esposizione lorda paper {100 * lordo_p:.1f}%"
    if demo is not None:
        riga += (f", demo {100 * sum(abs(w) for w in d.values()):.1f}%; somma delle differenze "
                 f"{100 * sum(abs(d.get(s, 0.0) - paper.get(s, 0.0)) for s in simboli):.1f}% del conto")
    return out + [riga, ""]


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
