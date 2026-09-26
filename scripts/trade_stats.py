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


def print_contesto_btc(per_contesto: dict | None) -> None:
    """DIREZIONE x CONTESTO BTC (26 set 2026, backlog J7): la tabella
    `per_contesto` di `aggrega_referti`. Risponde a «le short perdono» o «le
    short perdono con BTC su»? Globale, poi le strategie con almeno un trade a
    contesto noto (le prime 8 per trade). Il contesto c'e' solo dal 25 set
    (`feats_at_entry.market_up`): i trade prima sono «ignoto», e si contano."""
    from bot.learning.referti import CASELLE_CONTESTO, MIN_CAMPIONE
    print("\nDIREZIONE x CONTESTO BTC (market_up all'apertura, feats_at_entry dal 25 set; "
          "«con» = nel verso di BTC, «contro» = opposto)")
    if not isinstance(per_contesto, dict) or not isinstance(per_contesto.get("globale"), dict):
        print("  non disponibile (documento dei referti senza `per_contesto`)")
        return
    glob = per_contesto["globale"]
    noti = sum(int((glob.get(c) or {}).get("trade", 0) or 0)
               for c in CASELLE_CONTESTO if c != "ignoto")
    ignoti = int((glob.get("ignoto") or {}).get("trade", 0) or 0)
    if not noti:
        print(f"  nessun trade con il contesto BTC noto ({ignoti} ignoti: aperti prima del "
              f"25 set o senza feats_at_entry)")
        return

    def _cella(b, c):
        x = (b.get(c) or {})
        n = int(x.get("trade", 0) or 0)
        if not n:
            return f"{'—':>14}"
        return f"{int(x.get('vinti', 0) or 0)}/{n} {float(x.get('pnl', 0) or 0):+.2f}".rjust(14)

    colonne = [c for c in CASELLE_CONTESTO if c != "ignoto"]
    print(f"  {'':<14} " + " ".join(f"{c:>14}" for c in colonne) + f" {'ignoti':>7}")
    print(f"  {'tutte':<14} " + " ".join(_cella(glob, c) for c in colonne) + f" {ignoti:>7}")
    righe = []
    for gid, b in (per_contesto.get("per_strategia") or {}).items():
        if not isinstance(b, dict):
            continue
        n = sum(int((b.get(c) or {}).get("trade", 0) or 0) for c in colonne)
        if n:
            righe.append((-n, gid, b))
    for _, gid, b in sorted(righe)[:8]:
        print(f"  {gid:<14} " + " ".join(_cella(b, c) for c in colonne)
              + f" {int((b.get('ignoto') or {}).get('trade', 0) or 0):>7}")
    print(f"  (cella: vinti/trade PnL; ipotesi controtrend_btc a >= {MIN_CAMPIONE} perdite "
          f"contro il contesto e 0 vinti contro, per strategia)")


def print_calibrazione_contesto(cal_doc: dict | None) -> None:
    """CALIBRAZIONE (regime, F&G) da `calibration/current` (26 set 2026, J8):
    le fasce della confidenza del regime col verdetto, e le tre fasce del Fear &
    Greed. Solo misura: il documento dice se `trust` le guarda (no)."""
    from bot.learning.calibration import MIN_PER_FASCIA
    print("\nCALIBRAZIONE (regime, F&G) — misure, non toccano la size")
    if not isinstance(cal_doc, dict) or not cal_doc:
        print("  calibration/current non disponibile (bot fermo o Firestore non leggibile)")
        return
    if cal_doc.get("_errore"):
        print(f"  calibration/current non leggibile: {cal_doc['_errore']}")
        return
    reg, fg = cal_doc.get("regime_confidence"), cal_doc.get("fear_greed")
    if not isinstance(reg, dict) or not isinstance(fg, dict):
        print("  documento precedente al 26 set: le fasce del regime e del F&G arrivano "
              "col prossimo ricalcolo orario del bot")
        return

    def _tab(titolo, fasce):
        print(f"  {titolo}")
        print(f"    {'fascia':<12} {'n':>4} {'win rate':>9} {'pnl medio':>10}")
        for f in fasce or []:
            wr = f.get("win_rate")
            pm = f.get("pnl_medio")
            print(f"    {str(f.get('fascia')):<12} {int(f.get('n', 0) or 0):>4} "
                  f"{'—' if wr is None else f'{wr * 100:.0f}%':>9} "
                  f"{'—' if pm is None else f'{pm * 100:+.2f}%':>10}")

    _tab(f"confidenza del REGIME (terzili, {int(reg.get('trades', 0) or 0)} trade): "
         f"verdetto {reg.get('verdetto_regime', '?')} (< {MIN_PER_FASCIA} per fascia = "
         f"campione insufficiente)", reg.get("fasce"))
    _tab(f"FEAR & GREED all'apertura ({int(fg.get('trades', 0) or 0)} trade)", fg.get("fasce"))


def esplorativo_report(trades: list[dict], esp_doc: dict | None) -> dict:
    """I numeri del PAPER ESPLORATIVO (25 set 2026, backlog F1bis), a parte da
    quelli delle validate: trade, vinti, PnL, le 5 coppie con piu' trade, e il
    metro dell'esperimento letto dalla storia di `strategy_registry/esplorative`
    (quante coppie esplorative sono POI passate il gate, quante scartate). Pura."""
    from bot.learning.referti import ESITI_ESTERNI
    rows = [t for t in trades if t.get("esplorativa")
            and str(t.get("exit_reason", "")) not in ESITI_ESTERNI]
    per_coppia: dict[str, dict] = {}
    for t in rows:
        k = f"{t.get('symbol', '?')}|{t.get('strategy', '?')}"
        b = per_coppia.setdefault(k, {"coppia": k, "trades": 0, "vinti": 0, "pnl": 0.0})
        pnl = float(t.get("pnl", 0) or 0)
        b["trades"] += 1
        b["vinti"] += 1 if pnl > 0 else 0
        b["pnl"] = round(b["pnl"] + pnl, 2)
    top = sorted(per_coppia.values(), key=lambda b: (-b["trades"], b["coppia"]))[:5]
    attive = validate_poi = scartate = None
    if isinstance(esp_doc, dict):
        from bot.core.firebase_client import decode_pairs
        attive = len(decode_pairs(esp_doc.get("pairs")))
        storia = decode_pairs(esp_doc.get("storia"))
        validate_poi = sum(1 for v in storia.values() if (v or {}).get("esito") == "validata")
        scartate = sum(1 for v in storia.values() if (v or {}).get("esito") == "scartata")
    return {"trades": len(rows), "vinti": sum(1 for t in rows if float(t.get("pnl", 0) or 0) > 0),
            "pnl": round(sum(float(t.get("pnl", 0) or 0) for t in rows), 2),
            "per_coppia": top, "coppie_attive": attive,
            "validate_poi": validate_poi, "scartate": scartate}


def declassate_report(trades: list[dict]) -> dict:
    """LE DECLASSATE (26 set 2026, passo 2) contro le ATTIVE: fra i trade delle
    validate (esplorative ed esiti esterni fuori), quelli con `declassata: true`
    e gli altri: trade, vinti, PnL e R medio (`drift.r_multiplo`: pnl /
    (|entry − orig_stop| × size), ripiego `post_mortem.stop_pct`; `r_n` dice su
    quanti trade l'R e' calcolabile). Pura: nessun verdetto, solo il confronto
    che il metro del passo 2 chiede (PF vissuto delle declassate contro le
    attive nei 7 giorni dopo il declassamento si legge da qui, giorno per
    giorno)."""
    from bot.learning.drift import r_multiplo
    from bot.learning.referti import ESITI_ESTERNI

    def _blocco(rows):
        rs = [r for r in (r_multiplo(t) for t in rows) if r is not None]
        pnls = [float(t.get("pnl", 0) or 0) for t in rows]
        return {"trades": len(rows), "vinti": sum(1 for p in pnls if p > 0),
                "pnl": round(sum(pnls), 2),
                "r_medio": round(sum(rs) / len(rs), 3) if rs else None, "r_n": len(rs)}

    rows = [t for t in trades if not t.get("esplorativa")
            and str(t.get("exit_reason", "")) not in ESITI_ESTERNI]
    decl = [t for t in rows if t.get("declassata")]
    attive = [t for t in rows if not t.get("declassata")]
    return {"declassate": _blocco(decl), "attive": _blocco(attive)}


def print_declassate(rep: dict) -> None:
    def _riga(nome, b):
        r = "n/d" if b["r_medio"] is None else f"{b['r_medio']:+.3f}R su {b['r_n']}"
        print(f"  {nome:<12} {b['trades']:>4} trade · {b['vinti']} vinti · PnL {b['pnl']:+.2f} · R medio {r}")

    print("\nDECLASSATE (validate bocciate dal gate per DECLASSATA_NOTTI giri completi, operate a "
          "DECLASSATA_SIZE_MULT della size; passo 2 del 26 set) contro le ATTIVE")
    if rep["declassate"]["trades"] == 0:
        print("  nessun trade chiuso da una declassata (il gate non ne ha ancora scritte, "
              "o il bot non le ha ancora operate)")
    _riga("declassate", rep["declassate"])
    _riga("attive", rep["attive"])
    print("  R = pnl / (|entry - stop originale| x size); i trade senza stop originale non entrano nell'R medio")


def print_esplorativo(rep: dict) -> None:
    print("\nPAPER ESPLORATIVO (quasi-passaggi a un quarto della size, F1bis; fuori dai "
          "numeri qui sopra e dai pesi)")
    if rep["coppie_attive"] is None:
        print("  registro esplorativo non ancora scritto dal gate")
    else:
        print(f"  coppie attive adesso: {rep['coppie_attive']}")
    print(f"  trade chiusi: {rep['trades']} · vinti {rep['vinti']} · PnL {rep['pnl']:+.2f}")
    for b in rep["per_coppia"]:
        print(f"    {b['coppia']:<34} {b['trades']:>3} trade · {b['vinti']} vinti · {b['pnl']:+.2f}")
    if rep["validate_poi"] is None:
        print("  coppie esplorative poi validate / scartate: n/d (senza registro)")
    else:
        print(f"  coppie esplorative poi validate {rep['validate_poi']} / scartate "
              f"{rep['scartate']}  (il metro: si legge a 100 trade esplorativi)")


def main() -> int:
    fb = get_firebase()
    trades_letti = fb.query_collection("trades", order_by="exit_ts")
    if not trades_letti:
        print("Nessun trade chiuso trovato.")
        return 0
    # IL PAPER ESPLORATIVO A PARTE (25 set 2026, F1bis): le statistiche qui sotto
    # sono delle VALIDATE; gli esplorativi hanno la loro sezione in fondo.
    trades = [t for t in trades_letti if not t.get("esplorativa")]
    if not trades:
        print("Nessun trade chiuso delle validate (solo esplorativi).")
        try:
            esp_doc = fb.get_doc("strategy_registry", "esplorative")
        except Exception:  # noqa: BLE001
            esp_doc = None
        print_esplorativo(esplorativo_report(trades_letti, esp_doc))
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
    from bot.learning.referti import (ESITI_ESTERNI, MIN_CAMPIONE, MIN_INGRESSO,
                                      MIN_STOP_LARGO, VARIABILI_INGRESSO,
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
    print_contesto_btc(doc.get("per_contesto"))

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

    # LE CONDIZIONI D'INGRESSO (26 set 2026, backlog I4ter): per ogni strategia
    # con almeno MIN_INGRESSO perdite «mai andate a favore» (classe ingresso) con
    # la variabile nota, la mediana di ADX / volume / ATR% / RSI all'apertura
    # delle perdite contro quella dei vinti. Sono i numeri da cui nascono le
    # ipotesi `ingresso_<variabile>` qui sopra; dove non scattano, si vede
    # perche' (stesso lato, o troppo pochi vinti). Dal doc `ingresso` di
    # aggrega_referti: solo conteggi e mediane, mai le liste.
    print(f"\nCONDIZIONI D'INGRESSO (perdite d'ingresso vs vinti, per strategia con "
          f">= {MIN_INGRESSO} perdite d'ingresso):")
    righe_ing = [(gid, r) for gid, r in sorted((doc.get("ingresso") or {}).items())
                 if any(int((r.get(v) or {}).get("persi", 0) or 0) >= MIN_INGRESSO
                        for v in VARIABILI_INGRESSO)]
    if righe_ing:
        def _mv(r, var, chiave):
            x = (r.get(var) or {}).get(chiave)
            if x is None:
                return "n/d"
            return f"{x * 100:.2f}%" if var == "atr_pct" else f"{x:.2f}"
        print(f"  {'strategia':<14} {'persi/vinti':>11}  "
              + "  ".join(f"{v + ' persi|vinti':>22}" for v in VARIABILI_INGRESSO))
        for gid, r in righe_ing:
            n_p = max(int((r.get(v) or {}).get("persi", 0) or 0) for v in VARIABILI_INGRESSO)
            n_v = max(int((r.get(v) or {}).get("vinti", 0) or 0) for v in VARIABILI_INGRESSO)
            celle = "  ".join(f"{_mv(r, v, 'mediana_persi') + '|' + _mv(r, v, 'mediana_vinti'):>22}"
                              for v in VARIABILI_INGRESSO)
            print(f"  {gid:<14} {f'{n_p}/{n_v}':>11}  {celle}")
    else:
        print(f"  nessuna strategia con >= {MIN_INGRESSO} perdite d'ingresso con le "
              f"variabili note (feats_at_entry dal 25 set, o indicators_at_entry)")

    # L'OMBRA DEL SELETTORE (25 set 2026): la p che il bot annota su ogni
    # apertura, letta contro l'esito. Il paper qui e' il giudice del modello
    # addestrato sul gate, non un dato di training.
    print_selettore_ombra(selettore_ombra_report(trades))

    # LA CALIBRAZIONE DEL REGIME E DEL F&G (26 set 2026, backlog J8): il bot la
    # scrive in `calibration/current` insieme al verdetto sulla confidenza;
    # `state_snapshot` stampa quello, qui si stampano le due misure nuove. Sola
    # lettura, fail-open: senza documento (o senza Firestore) lo si dice.
    try:
        cal_doc = fb.get_doc("calibration", "current")
    except Exception as exc:  # noqa: BLE001
        cal_doc = {"_errore": str(exc)[:80]}
    print_calibrazione_contesto(cal_doc)

    # LE DECLASSATE (26 set 2026, passo 2): il vissuto delle validate declassate
    # dal gate contro quello delle attive, sugli stessi trade di qui sopra.
    print_declassate(declassate_report(trades))

    # IL PAPER ESPLORATIVO (25 set 2026, F1bis): in fondo, coi suoi numeri e il
    # metro dell'esperimento dalla storia del registro esplorativo.
    try:
        esp_doc = fb.get_doc("strategy_registry", "esplorative")
    except Exception:  # noqa: BLE001
        esp_doc = None
    print_esplorativo(esplorativo_report(trades_letti, esp_doc))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
