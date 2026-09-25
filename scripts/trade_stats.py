"""
Diagnostica: cosa determina il NUMERO di trade al giorno, e in che DIREZIONE.

Ricostruisce dai trade chiusi (Firestore `trades`) le metriche che spiegano il
throughput, così si vede se il collo di bottiglia e' la liquidita' (posizioni
contemporanee al tetto) o i SEGNALI (poche aperture al giorno):

  * trade al giorno (min/media/max)
  * durata media di holding
  * posizioni CONTEMPORANEE: massimo e media pesata nel tempo (sweep entry/exit)
  * coin e strategie distinte coinvolte
  * DIREZIONE: long vs short, incrociata col regime all'apertura

L'ultimo blocco nasce da una domanda del proprietario (18 settembre) a cui nessun
report sapeva rispondere: «come e' possibile che in una giornata di rialzo abbiamo
aperto 4 posizioni su 5 short?». Il conteggio esisteva solo nella dashboard, a
occhio, e nessuno lo incrociava col regime ne' col PnL — cioe' mancava proprio il
pezzo che distingue «e' il disegno» da «ci sta costando».

Sola lettura. Uso sulla VPS:
    .venv/bin/python -m scripts.trade_stats
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from statistics import mean, median

from bot.core.firebase_client import get_firebase
from bot.core.models import Regime
from bot.orchestrator.orchestrator import Orchestrator


def _entry_ts(t: dict) -> float | None:
    """epoch dell'apertura da entry_time (ISO) o entry_ts se presente."""
    if t.get("entry_ts") is not None:
        try:
            return float(t["entry_ts"])
        except (TypeError, ValueError):
            pass
    iso = t.get("entry_time")
    if not iso:
        return None
    try:
        return datetime.fromisoformat(str(iso).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _dir(t: dict) -> str:
    """'long' / 'short' / '?' — `direction` e' salvato come stringa dall'enum."""
    return str(t.get("direction", "?")).lower()


def _regime(t: dict):
    """Regime AL MOMENTO DELL'APERTURA. None se assente o non riconosciuto.

    Non si inventa un default: un trade senza regime registrato non e' un trade in
    mercato laterale, e contarlo come tale falserebbe proprio la riga che questo
    report esiste per produrre."""
    v = t.get("regime_at_entry")
    if not v:
        return None
    try:
        return Regime(str(v))
    except ValueError:
        return None


def direction_report(trades: list[dict]) -> dict:
    """long vs short: quanti, come vanno, e quanti sono CONTRO il trend.

    Il conteggio da solo non basta. Aprire controtrend NON e' un errore: e' una
    scelta esplicita del disegno — il trend modula la SIZE e non mette il veto
    (`Orchestrator.decide_all`), e meta' delle feature generate sono di ritorno
    alla media, che per costruzione vendono la forza. La domanda utile quindi non
    e' «quante short?» ma «quelle short stanno pagando?». Per questo accanto a
    ogni conteggio c'e' il PnL e la mediana di mfe_r.

    Il criterio di controtrend e' preso da `Orchestrator._trend_align` invece di
    essere riscritto qui: due definizioni di controtrend che divergono sarebbero
    peggio di nessuna — e' la classe di errore piu' cara di questo progetto.
    """
    per_dir: dict[str, dict] = {}
    for d in ("long", "short"):
        sel = [t for t in trades if _dir(t) == d]
        pnl = [float(t.get("pnl", 0.0) or 0.0) for t in sel]
        mfe = [float(t.get("mfe_r", 0.0) or 0.0) for t in sel]
        per_dir[d] = {
            "trade": len(sel),
            "vinti": sum(1 for p in pnl if p > 0),
            "pnl": round(sum(pnl), 2),
            "mfe_mediana": round(median(mfe), 2) if mfe else None,
        }

    # allineamento col trend: +1 in trend, -1 controtrend, 0 regime neutro
    align: dict[str, dict] = {k: {"trade": 0, "pnl": 0.0}
                              for k in ("in_trend", "contro", "neutro", "ignoto")}
    matrice: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for t in trades:
        d = _dir(t)
        if d not in ("long", "short"):
            continue
        reg = _regime(t)
        matrice[reg.value if reg else "ignoto"][d] += 1
        if reg is None:
            key = "ignoto"
        else:
            a = Orchestrator._trend_align(reg, d)
            key = "in_trend" if a > 0 else "contro" if a < 0 else "neutro"
        align[key]["trade"] += 1
        align[key]["pnl"] += float(t.get("pnl", 0.0) or 0.0)
    for v in align.values():
        v["pnl"] = round(v["pnl"], 2)

    return {"per_direzione": per_dir, "allineamento": align,
            "matrice": {k: dict(v) for k, v in matrice.items()}}


def print_direction_report(rep: dict) -> None:
    print("\nDIREZIONE — long vs short")
    print(f"{'':6} {'trade':>6} {'vinti':>7} {'PnL':>9} {'mfe mediana':>13}")
    for d, r in rep["per_direzione"].items():
        if not r["trade"]:
            continue
        quota = f"{r['vinti']}/{r['trade']}"
        mfe = f"{r['mfe_mediana']:.2f}R" if r["mfe_mediana"] is not None else "—"
        print(f"{d:6} {r['trade']:>6} {quota:>7} {r['pnl']:>9.2f} {mfe:>13}")

    if rep["matrice"]:
        print("\nRegime ALL'APERTURA x direzione:")
        for reg, riga in sorted(rep["matrice"].items()):
            voci = " · ".join(f"{d} {n}" for d, n in sorted(riga.items()))
            print(f"  {reg:18} {voci}")

    a = rep["allineamento"]
    print("\nRispetto al trend (stesso criterio dell'orchestratore):")
    for k, etichetta in (("in_trend", "in trend"), ("contro", "CONTROTREND"),
                         ("neutro", "regime neutro"), ("ignoto", "regime ignoto")):
        if a[k]["trade"]:
            print(f"  {etichetta:15} {a[k]['trade']:>3} trade · PnL {a[k]['pnl']:>8.2f}")
    print("\nLettura: il controtrend NON e' un errore — il trend modula la size, non")
    print("mette il veto, e le strategie di ritorno alla media vendono la forza per")
    print("costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.")


# --------------------------------------------------------------------------- #
# Il selettore in OMBRA (25 set 2026, docs/disegno_cervello.md punto 2 passo 2) #
# --------------------------------------------------------------------------- #
#: quanti trade con p servono prima di leggere la calibrazione sul paper (dal
#: disegno: «non flat dopo 40 segnali») e prima di calcolare una correlazione
#: che non sia rumore.
MIN_TRADE_CON_P = 40
MIN_CORRELAZIONE = 10

#: la regola d'ingresso, scritta una volta sola e stampata sempre: il selettore
#: entra solo se batte «apri tutto» su 2/3 finestre (scripts/selettore_report.py)
#: E la calibrazione sul paper non e' piatta (p media dei vinti sopra quella dei
#: persi, correlazione p/esito > 0) su almeno MIN_TRADE_CON_P trade con p.
REGOLA_SELETTORE = ("il selettore entra solo se batte «apri tutto» su 2/3 finestre "
                    "(report `selettore`) E la calibrazione sul paper non e' piatta "
                    f"(>= {MIN_TRADE_CON_P} trade con p, p media dei vinti > dei persi, "
                    "correlazione p/esito > 0)")


def _pearson(x: list[float], y: list[float]) -> float | None:
    """Correlazione di Pearson; None se una delle due serie e' costante."""
    n = len(x)
    if n < 2:
        return None
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    # «costante» con la tolleranza dei float: dodici 0.6 sommati non danno uno
    # scarto quadratico esattamente zero, ma quasi (1e-32), e non e' un segnale
    if sxx <= 1e-12 or syy <= 1e-12:
        return None
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return sxy / (sxx * syy) ** 0.5


def selettore_ombra_report(trades: list[dict]) -> dict:
    """Cosa dice il paper della p annotata dall'ombra del selettore.

    Legge SOLO i trade chiusi che portano `selector_p` (il bot la scrive dal
    25 set 2026; prima non c'era). Per ognuno la soglia e' `selector_soglia`
    del trade stesso (era quella del modello in vigore quando si e' aperto;
    0.5 se manca). Numeri: quanti trade con p; p media dei vinti e dei persi
    (se p predice, la prima e' piu' alta); quanti stavano sopra la soglia e il
    loro PnL contro il PnL di tutti i trade con p (cioe' cosa avrebbe fatto il
    selettore se avesse deciso, a size uguale); correlazione p/esito (esito
    1 = vinto, 0 = perso) solo da MIN_CORRELAZIONE trade in su. Non decide
    nulla: e' la misura che, con >= MIN_TRADE_CON_P trade, dira' se la
    calibrazione e' piatta o no."""
    con_p = []
    for t in trades or []:
        try:
            p = float(t.get("selector_p"))
            pnl = float(t.get("pnl", 0) or 0)
        except (TypeError, ValueError):
            continue
        if p != p:   # NaN
            continue
        try:
            soglia = float(t.get("selector_soglia"))
        except (TypeError, ValueError):
            soglia = 0.5
        con_p.append((p, soglia, pnl))
    n = len(con_p)
    out = {"n": n, "n_vinti": 0, "n_persi": 0, "p_media_vinti": None,
           "p_media_persi": None, "n_sopra": 0, "pnl_sopra": 0.0, "pnl_tutti": 0.0,
           "correlazione": None, "minimo_calibrazione": MIN_TRADE_CON_P,
           "regola": REGOLA_SELETTORE}
    if not n:
        return out
    vinti = [p for p, _, pnl in con_p if pnl > 0]
    persi = [p for p, _, pnl in con_p if pnl < 0]
    sopra = [(p, pnl) for p, s, pnl in con_p if p >= s]
    out.update({
        "n_vinti": len(vinti), "n_persi": len(persi),
        "p_media_vinti": round(mean(vinti), 4) if vinti else None,
        "p_media_persi": round(mean(persi), 4) if persi else None,
        "n_sopra": len(sopra),
        "pnl_sopra": round(sum(pnl for _, pnl in sopra), 4),
        "pnl_tutti": round(sum(pnl for _, _, pnl in con_p), 4),
    })
    if n >= MIN_CORRELAZIONE:
        c = _pearson([p for p, _, _ in con_p], [1.0 if pnl > 0 else 0.0 for _, _, pnl in con_p])
        out["correlazione"] = round(c, 4) if c is not None else None
    return out


def print_selettore_ombra(rep: dict) -> None:
    print("\nSELETTORE IN OMBRA (p annotata dal bot a ogni apertura, mai usata per decidere)")
    if not rep["n"]:
        print("  nessun trade con p ancora (il bot la scrive dal 25 set 2026, se "
              "`selector/current` e' pubblicato)")
        print(f"  regola: {rep['regola']}")
        return
    print(f"  trade con p: {rep['n']}  (vinti {rep['n_vinti']}, persi {rep['n_persi']}; "
          f"ne servono {rep['minimo_calibrazione']} per leggere la calibrazione)")
    pv, pp = rep["p_media_vinti"], rep["p_media_persi"]
    print(f"  p media dei vinti: {'—' if pv is None else f'{pv:.3f}'}   "
          f"p media dei persi: {'—' if pp is None else f'{pp:.3f}'}"
          + ("   (se p predice, la prima e' piu' alta)" if pv is not None and pp is not None else ""))
    print(f"  sopra la soglia: {rep['n_sopra']}/{rep['n']} trade, PnL {rep['pnl_sopra']:+.2f} "
          f"contro {rep['pnl_tutti']:+.2f} di tutti (a size uguale: e' cio' che il "
          f"selettore avrebbe tenuto)")
    c = rep["correlazione"]
    if rep["n"] < MIN_CORRELAZIONE:
        print(f"  correlazione p/esito: — (servono {MIN_CORRELAZIONE} trade, ce ne sono {rep['n']})")
    else:
        print(f"  correlazione p/esito: {'— (serie costante)' if c is None else f'{c:+.3f}'}")
    print(f"  regola: {rep['regola']}")


def main() -> int:
    fb = get_firebase()
    trades = fb.query_collection("trades", order_by="exit_ts")
    if not trades:
        print("Nessun trade chiuso trovato.")
        return 0

    spans = []  # (entry_ts, exit_ts) validi
    per_day: dict[str, int] = defaultdict(int)
    coins, strategies = set(), set()
    for t in trades:
        ex = t.get("exit_ts")
        en = _entry_ts(t)
        coins.add(t.get("symbol", "?"))
        strategies.add(t.get("strategy", "?"))
        if ex is None:
            continue
        day = datetime.fromtimestamp(float(ex), timezone.utc).strftime("%Y-%m-%d")
        per_day[day] += 1
        if en is not None and ex > en:
            spans.append((en, float(ex)))

    # --- posizioni contemporanee: sweep degli eventi apertura/chiusura ---
    events = []
    for en, ex in spans:
        events.append((en, 1))
        events.append((ex, -1))
    events.sort()
    cur = max_conc = 0
    prev_t = None
    area = 0.0  # integrale (posizioni * secondi) per la media pesata nel tempo
    for ts, delta in events:
        if prev_t is not None:
            area += cur * (ts - prev_t)
        cur += delta
        max_conc = max(max_conc, cur)
        prev_t = ts
    total_span = (events[-1][0] - events[0][0]) if len(events) >= 2 else 0
    avg_conc = area / total_span if total_span > 0 else 0.0

    durations_h = [(ex - en) / 3600.0 for en, ex in spans]
    counts = list(per_day.values())

    print(f"\nTrade totali analizzati: {len(trades)}  ({len(spans)} con apertura nota)")
    print(f"Giorni coperti:          {len(per_day)}")
    print(f"Trade/giorno:            min {min(counts)} · media {mean(counts):.1f} · max {max(counts)}")
    # LA RIPARTIZIONE, non solo min/media/max. La media sulla settimana non si puo'
    # confrontare con gli "attesi" di `signal_frequency`: quella sonda fa girare le
    # coppie validate di OGGI su giorni in cui il registro ne aveva meno, e su giorni
    # in cui il paper non girava ancora. Il confronto onesto e' giorno contro giorno,
    # sugli ultimi — e senza questa riga non c'era modo di farlo.
    print("  per giorno (UTC): " + " · ".join(
        f"{g} {per_day[g]}" for g in sorted(per_day)))
    if durations_h:
        print(f"Durata media holding:    {mean(durations_h):.1f}h  (min {min(durations_h):.1f}h · max {max(durations_h):.1f}h)")
    print(f"Posizioni contemporanee: MAX {max_conc} · media nel tempo {avg_conc:.1f}")
    print(f"Coin distinte:           {len(coins)}")
    print(f"Strategie distinte:      {len(strategies)}")
    print("\nLettura: se MAX contemporanee << 10 (il tetto da margine), il numero di")
    print("trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.")

    print_direction_report(direction_report(trades))

    # ---- I REFERTI (post_mortem) aggregati -------------------------------------
    # Scritti dal bot alla chiusura (bot/risk/setup_check.py), aggregati da
    # bot/learning/referti.py (stesso documento che il bot pubblica su Firestore
    # `learning/referti` e che la discovery legge). E' il conteggio che dice cosa
    # correggere, non il singolo caso — «stop largo» x N vale una regola, x 1
    # vale un'occhiata. Le IPOTESI qui sotto sono proposte del paper: le prova il
    # gate sulla storia. Nessun parametro cambia da questo script.
    from bot.learning.referti import (ESITI_ESTERNI, MIN_CAMPIONE, MIN_STOP_LARGO,
                                      aggrega_referti, riassunto_ipotesi)
    doc = aggrega_referti(trades)
    con_referto = [t for t in trades if isinstance(t.get("post_mortem"), dict)
                   and str(t.get("exit_reason", "")) not in ESITI_ESTERNI]
    persi = [t for t in con_referto if float(t.get("pnl", 0) or 0) < 0]
    if con_referto:
        print(f"\nREFERTI (post_mortem) sui trade chiusi: {doc['n_con_referto']} "
              f"({doc['n_persi_con_referto']} in perdita; esclusi gli esiti "
              f"manual/kill_switch/circuit_breaker)")
        conta = defaultdict(int)
        for t in persi:
            pm = t["post_mortem"]
            if pm.get("classe"):
                conta[f"classe {pm['classe']}"] += 1
            if pm.get("stop_largo"):
                conta["stop troppo largo"] += 1
            if pm.get("lock_mai_armato"):
                conta["lock mai armato"] += 1
            if pm.get("controtrend"):
                conta["controtrend"] += 1
        for k, v in sorted(conta.items(), key=lambda kv: -kv[1]):
            print(f"  {k:<24} x{v}")
        # le prime 8 strategie per numero di perdite: i rilievi sono contati SOLO
        # sui trade in perdita con referto, n/vinti/persi/PnL su tutti i trade
        righe = sorted(doc["per_strategia"].items(),
                       key=lambda kv: (-kv[1]["persi"], kv[0]))[:8]
        if righe:
            print("\n  PER STRATEGIA (trade in perdita con referto):")
            print(f"  {'strategia':<14} {'n':>3} {'vinti':>5} {'persi':>5} {'PnL':>8}  "
                  f"{'ingr/usc/prot':>13} {'stop largo':>10} {'lock mai':>8} {'controtrend':>11}")
            for gid, b in righe:
                print(f"  {gid:<14} {b['n']:>3} {b['vinti']:>5} {b['persi']:>5} {b['pnl']:>8.2f}  "
                      f"{b['ingresso']:>4}/{b['uscita']:>3}/{b['protezione']:>4} "
                      f"{b['stop_largo']:>10} {b['lock_mai']:>8} {b['controtrend']:>11}")
        print("  ultimi referti in perdita:")
        for t in sorted(persi, key=lambda t: float(t.get("exit_ts") or 0))[-6:]:
            print(f"   - {t.get('symbol')} {t.get('strategy')} {t.get('direction')} "
                  f"{float(t.get('pnl', 0) or 0):+.2f}: {t['post_mortem'].get('verdetto')}")
    else:
        esterni = sum(1 for t in trades if isinstance(t.get("post_mortem"), dict)
                      and str(t.get("exit_reason", "")) in ESITI_ESTERNI)
        if esterni:
            print(f"\nREFERTI: {esterni} referti presenti ma tutti su esiti esterni "
                  f"(manual/kill_switch/circuit_breaker): esclusi dai conteggi")
        else:
            print("\nREFERTI: nessun trade porta ancora `post_mortem` (si scrive sui "
                  "trade chiusi DOPO il rilascio del 23 set)")

    # ---- LE SERIE DI PERDITE per strategia (freno di serie) --------------------
    # Stessa funzione del bot (bot/learning/drift.py): a STREAK_BRAKE_LOSSES
    # perdite di fila size e leva si dimezzano fino al primo guadagno. Qui si
    # vede CHI e' frenato adesso, senza entrare sulla macchina. Il bot la calcola
    # sui trade degli ultimi 30 giorni: se qui compare una serie piu' lunga e'
    # perche' questo script legge tutti i trade.
    from bot.learning.drift import serie_perdite
    from bot.config import settings as _cfg
    serie = {k: v for k, v in serie_perdite(trades).items() if v >= 2}
    if serie:
        # L'ETICHETTA DICE IL VERO (25 set 2026): il freno di serie e' SPENTO per
        # default dal 24 set (settings.STREAK_BRAKE_ENABLED, backlog H4), ma questa
        # riga continuava a scrivere «FRENO attivo» come se dimezzasse la size.
        # Ora si legge lo stato dell'interruttore, non la soglia.
        if _cfg.STREAK_BRAKE_ENABLED:
            print(f"\nSERIE DI PERDITE in corso per strategia (freno x"
                  f"{_cfg.STREAK_BRAKE_FACTOR:g} da {_cfg.STREAK_BRAKE_LOSSES} di fila):")
        else:
            print(f"\nSERIE DI PERDITE in corso per strategia (freno spento: "
                  f"STREAK_BRAKE_ENABLED=false, solo misura; soglia "
                  f"{_cfg.STREAK_BRAKE_LOSSES} di fila):")
        for k, v in sorted(serie.items(), key=lambda kv: (-kv[1], kv[0]))[:10]:
            if v >= _cfg.STREAK_BRAKE_LOSSES:
                freno = ("  <- FRENO attivo" if _cfg.STREAK_BRAKE_ENABLED
                         else "  (freno spento)")
            else:
                freno = ""
            print(f"  {k:<14} {v} perdite di fila{freno}")

    # ---- I RIFIUTI D'INGRESSO ------------------------------------------------
    # (25 set 2026, backlog H5) Il bot scarta segnali PRIMA di aprire: cooldown
    # per coin, tetto per coin al giorno, margine, risk gate (stop troppo largo),
    # rischio direzionale, peso sotto soglia, veto di regime. Non esiste un
    # contatore persistente: RTDB /decision_status tiene solo l'ULTIMO esito
    # (sovrascritto a ogni ciclo) e qui si mostra per quello che e'. Il conteggio
    # vero sta nel log del bot, dove ogni scarto lascia una riga «[rifiuto]».
    print("\nRIFIUTI D'INGRESSO")
    stato = None
    try:
        stato = fb.get_rtdb("/decision_status")
    except Exception as exc:  # noqa: BLE001
        print(f"  /decision_status non leggibile: {exc}")
    if isinstance(stato, dict) and stato:
        quando = stato.get("ts")
        try:
            quando = datetime.fromtimestamp(float(quando), timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        except (TypeError, ValueError):
            quando = "?"
        print(f"  ultimo esito (RTDB /decision_status, solo l'ultimo, {quando}): "
              f"{stato.get('outcome', '?')} — {stato.get('reason', '?')}")
    else:
        print("  nessun /decision_status leggibile da qui")
    print("  nessun contatore persistente: i motivi dei rifiuti sono nel log del bot, "
          "righe [rifiuto] (ops: `log-bot`)")

    # Le ipotesi per direzione (solo_long/solo_short) non hanno bisogno del
    # referto: bastano pnl e direzione, quindi si stampano comunque.
    print("\nIPOTESI DAI REFERTI (regole dichiarate; le prova il gate sulla storia, "
          "non il paper):")
    righe_ipotesi = riassunto_ipotesi(doc)
    if righe_ipotesi:
        for r in righe_ipotesi:
            print(f"  - {r}")
    else:
        print(f"  nessuna: servono almeno {MIN_CAMPIONE} perdite per direzione o "
              f"controtrend, {MIN_STOP_LARGO} stop larghi")

    # L'OMBRA DEL SELETTORE (25 set 2026): la p che il bot annota su ogni
    # apertura, letta contro l'esito. Il paper qui e' il giudice del modello
    # addestrato sul gate, non un dato di training.
    print_selettore_ombra(selettore_ombra_report(trades))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
