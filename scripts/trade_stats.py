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
  * CONTI IN R (1 ott 2026, K8): gli stessi gruppi in R, tutto e dal 27 set
  * PAPER CONTRO IL CASO (1 ott 2026, K4): accanto ai numeri d'uscita, quelli
    di un prezzo casuale con le nostre uscite (costanti del 30 set)

Il blocco DIREZIONE nasce da una domanda del proprietario (18 settembre) a cui nessun
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

from bot.config import settings
from bot.core.firebase_client import get_firebase
from bot.core.models import Regime
from bot.core.tempo import fuso, giorno_locale
from bot.learning.metrics import (KEEP_STRATEGIA_MIN_VERDETTI, conta_verdetti_strategia,
                                  proposta_keep_strategia, soldi_sul_tavolo)
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
# I CONTI IN R (1 ott 2026, backlog K8)                                        #
# --------------------------------------------------------------------------- #
# Le righe in USDT qui sopra (long/short, regime, trend) e i conti per
# strategia mescolano size diverse: piena, mezza col freno, ridotta per le
# declassate. E mescolano il periodo del difetto della sessione (J13): fino al
# 26 set -77,93 USDT, dal 27 set +10,19 (ops/results/0371). «Regime neutro
# -58,30» diceva soprattutto questo. Qui gli stessi gruppi in R, che mette ogni
# trade sulla stessa scala (quanto ha reso per ogni unita' di rischio preso
# all'apertura), con due colonne: tutto, e solo i trade entrati dopo il
# difetto. Le righe in USDT restano: questo blocco sta accanto, non al posto.
#: quante strategie si mostrano per nome nel blocco in R (le altre in una riga)
R_STRATEGIE_MAX = 8
#: le righe del blocco: (gruppo, chiave, etichetta) nell'ordine di stampa
_REGIMI_R = ("bull_trending", "bear_trending", "sideways", "high_uncertainty", "ignoto")
_TREND_R = (("in_trend", "in trend"), ("contro", "CONTROTREND"),
            ("neutro", "regime neutro"), ("ignoto", "regime ignoto"))
_CONTESTO_R = ("long_con", "long_contro", "short_con", "short_contro", "ignoto")


def _rischio_iniziale(t: dict) -> float | None:
    """|entry - stop originale| x size, cioe' il denominatore di
    `drift.r_multiplo` (stesso stop, stessa size). None se non si sa."""
    from bot.learning.drift import stop_originale
    stop = stop_originale(t)
    if stop is None:
        return None
    try:
        rischio = abs(float(t.get("entry_price") or 0) - stop) * float(t.get("size") or 0)
    except (TypeError, ValueError):
        return None
    return rischio if rischio > 0 else None


def _r_stat(valori: list[float], senza_r: int) -> dict:
    return {"n": len(valori), "senza_r": senza_r,
            "r_medio": round(sum(valori) / len(valori), 3) if valori else None,
            "r_tot": round(sum(valori), 2) if valori else None}


def conti_in_r_report(trades: list[dict], dal_ts: float | None = None) -> dict:
    """Gli stessi gruppi delle righe in USDT, in R (`drift.r_multiplo`: pnl /
    (|entry - stop originale| x size)), per «tutto» e per i soli trade ENTRATI
    da `dal_ts` (default: 27 set 19:40 UTC, la fine del difetto della sessione,
    lo stesso taglio della regola del 3 ott). Per ogni riga: n (trade con R), R
    medio, R totale, senza_r (trade del gruppo senza stop originale o size:
    fuori dall'R, ma contati). Righe in piu': i costi stimati in R
    (`total_cost_usdt` / rischio) e il lordo in R (`gross_pnl_usdt` / rischio),
    solo sui trade che portano quel campo. Pura."""
    from bot.learning.drift import r_multiplo
    from bot.learning.referti import casella_contesto, contesto_btc_del_trade

    dal_ts = DAL_REGOLA_3_OTT if dal_ts is None else dal_ts
    # (gruppo, chiave) -> {"tutto": ([r], senza), "dal": ([r], senza)}
    acc: dict[tuple, dict[str, list]] = defaultdict(lambda: {"tutto": [[], 0], "dal": [[], 0]})
    per_strategia_n: dict[str, int] = defaultdict(int)

    def _metti(chiave, colonna, r):
        cella = acc[chiave][colonna]
        if r is None:
            cella[1] += 1
        else:
            cella[0].append(r)

    for t in trades or []:
        d = _dir(t)
        r = r_multiplo(t)
        rischio = _rischio_iniziale(t)
        ts = _entry_ts(t)
        colonne = ["tutto"] + (["dal"] if ts is not None and ts >= dal_ts else [])
        reg = _regime(t)
        if reg is None:
            trend = "ignoto"
        elif d in ("long", "short"):
            a = Orchestrator._trend_align(reg, d)
            trend = "in_trend" if a > 0 else "contro" if a < 0 else "neutro"
        else:
            trend = None
        gid = str(t.get("strategy") or "?")
        per_strategia_n[gid] += 1
        chiavi = [("tutte", "tutte"), ("strategia", gid)]
        if d in ("long", "short"):
            chiavi += [("direzione", d), ("regime", reg.value if reg else "ignoto"),
                       ("contesto", casella_contesto(d, contesto_btc_del_trade(t)))]
            if trend is not None:
                chiavi.append(("trend", trend))
        for col in colonne:
            for k in chiavi:
                _metti(k, col, r)
            # i costi e il lordo, sullo stesso rischio: solo dove il campo c'e'
            for nome, campo in (("costi", "total_cost_usdt"), ("lordo", "gross_pnl_usdt")):
                v = t.get(campo)
                try:
                    v = float(v) if v is not None else None
                except (TypeError, ValueError):
                    v = None
                _metti(("soldi", nome), col, None if (v is None or rischio is None) else v / rischio)

    def _riga(k):
        b = acc.get(k) or {"tutto": [[], 0], "dal": [[], 0]}
        return {c: _r_stat(b[c][0], b[c][1]) for c in ("tutto", "dal")}

    strategie = sorted(per_strategia_n, key=lambda g: (-per_strategia_n[g], g))
    mostrate = strategie[:R_STRATEGIE_MAX]
    altre: dict[str, dict] = {}
    for col in ("tutto", "dal"):
        vals, senza = [], 0
        for g in strategie[R_STRATEGIE_MAX:]:
            vals += acc[("strategia", g)][col][0]
            senza += acc[("strategia", g)][col][1]
        altre[col] = _r_stat(vals, senza)
    return {
        "dal_ts": dal_ts,
        "tutte": _riga(("tutte", "tutte")),
        "costi": _riga(("soldi", "costi")),
        "lordo": _riga(("soldi", "lordo")),
        "direzione": {d: _riga(("direzione", d)) for d in ("long", "short")},
        "regime": {g: _riga(("regime", g)) for g in _REGIMI_R if ("regime", g) in acc},
        "trend": {k: _riga(("trend", k)) for k, _ in _TREND_R if ("trend", k) in acc},
        "contesto": {c: _riga(("contesto", c)) for c in _CONTESTO_R if ("contesto", c) in acc},
        "strategia": {g: _riga(("strategia", g)) for g in mostrate},
        "altre_strategie": {"n": len(strategie) - len(mostrate), **altre},
    }


def _cella_r(s: dict) -> str:
    if not s["n"]:
        return f"{0:>4} {'—':>7} {'—':>7} {s['senza_r']:>3}"
    return f"{s['n']:>4} {s['r_medio']:>+7.3f} {s['r_tot']:>+7.2f} {s['senza_r']:>3}"


def print_conti_in_r(rep: dict) -> None:
    print("\nCONTI IN R (K8): R = pnl / (|entry - stop originale| x size), come DECLASSATE: "
          "size diverse pesano uguale. Stessi trade delle righe in USDT. «dal 27/9» = "
          "entrati dal 27 set 19:40 UTC (fine del difetto della sessione)")
    print(f"  {'':<16} {'-------- tutto ---------':>24} ‖ {'------- dal 27/9 -------':>24}")
    print(f"  {'':<16} {'n':>4} {'R medio':>7} {'R tot':>7} {'s/R':>3} ‖ "
          f"{'n':>4} {'R medio':>7} {'R tot':>7} {'s/R':>3}")

    def _p(etichetta, riga):
        print(f"  {etichetta:<16} {_cella_r(riga['tutto'])} ‖ {_cella_r(riga['dal'])}")

    _p("TUTTE (netto)", rep["tutte"])
    _p("  lordo", rep["lordo"])
    _p("  costi stimati", rep["costi"])
    print(" direzione")
    for d, riga in rep["direzione"].items():
        _p(d, riga)
    print(" regime all'apertura")
    for g, riga in rep["regime"].items():
        _p(g, riga)
    print(" rispetto al trend")
    for k, etichetta in _TREND_R:
        if k in rep["trend"]:
            _p(etichetta, rep["trend"][k])
    print(" direzione x BTC (con = nel verso di BTC)")
    for c, riga in rep["contesto"].items():
        _p(c, riga)
    print(f" per strategia (le prime {R_STRATEGIE_MAX} per trade)")
    for g, riga in rep["strategia"].items():
        _p(g, riga)
    alt = rep["altre_strategie"]
    if alt["n"]:
        _p(f"altre {alt['n']}", alt)
    print("  n = trade con R; s/R = senza stop originale o size (fuori dall'R; per lordo e "
          "costi anche senza il campo); netto = lordo - costi (costi stimati dal modello)")


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


# --------------------------------------------------------------------------- #
# LA FIRMA DEL CASO (1 ott 2026, backlog K4)                                   #
# --------------------------------------------------------------------------- #
#: cosa darebbe un prezzo CASUALE con le nostre regole d'uscita. COSTANTI DI
#: RIFERIMENTO, NON ricalcolate qui: vengono dalla simulazione del 30 set
#: (docs/revisione_sospese_30set.md, sezione 4 punto 1; docs/backlog.md K4).
#: Stanno accanto ai numeri del paper perche' le classi «ingresso/uscita» e
#: «senza primo target» hanno la stessa forma anche senza alcun vantaggio:
#: senza questo metro sembrano una diagnosi.
CASO_30SET = {"stop": 0.46, "stop_ingresso": 0.485, "stop_uscita": 0.515,
              "mfe_mediana_r": 0.81, "primo_target": 0.17, "vinti": 0.54,
              "r_medio": -0.067}
FONTE_CASO = ("simulazione del 30 set su prezzo casuale, docs/revisione_sospese_30set.md "
              "e backlog K4: costanti, non ricalcolate")


def _primo_gradino_del_trade(t: dict):
    """Il primo gradino della scala di QUESTO trade (`scale_r_mults`), None se
    manca: `metrics.classi_stop` allora usa quello globale (come `tocca_tp1`)."""
    m = t.get("scale_r_mults")
    return min(float(x) for x in m) if m else None


def firma_del_caso_report(trades: list[dict]) -> dict:
    """I numeri del paper che la revisione del 30 set ha messo accanto al caso:
    quota di stop sulle uscite, stop d'ingresso (mfe < 0,25R) e d'uscita (fra
    0,25R e il primo gradino) sul totale degli stop (`metrics.classi_stop`,
    gradino del trade), massimo toccato mediano (`mfe_r`), quota arrivata al
    primo target (`drift.tocca_tp1`), vinti, R medio (`drift.r_multiplo`). Pura."""
    from bot.learning.drift import r_multiplo, tocca_tp1
    from bot.learning.metrics import _ESITI_STOP, classi_stop

    rows = list(trades or [])
    n = len(rows)
    cs = classi_stop(rows, _primo_gradino_del_trade)
    mfe = [float(t["mfe_r"]) for t in rows if t.get("mfe_r") is not None]
    tp1 = [x for x in (tocca_tp1(t) for t in rows) if x is not None]
    rs = [r for r in (r_multiplo(t) for t in rows) if r is not None]

    def _q(a, b):
        return round(a / b, 3) if b else None
    return {"n": n,
            "stop": _q(sum(1 for t in rows if str(t.get("exit_reason", "")) in _ESITI_STOP), n),
            "stop_n": cs["totale"],
            "stop_ingresso": _q(cs["sbagliati"], cs["totale"]),
            "stop_uscita": _q(cs["quasi"], cs["totale"]),
            "mfe_mediana_r": round(median(mfe), 2) if mfe else None,
            "primo_target": _q(sum(1 for x in tp1 if x), len(tp1)),
            "vinti": _q(sum(1 for t in rows if float(t.get("pnl", 0) or 0) > 0), n),
            "r_medio": round(mean(rs), 3) if rs else None, "r_n": len(rs)}


def _pct(v) -> str:
    return "n/d" if v is None else f"{v * 100:.0f}%"


def print_firma_del_caso(rep: dict) -> None:
    c = CASO_30SET
    print(f"\nPAPER CONTRO IL CASO (K4): il paper ({rep['n']} trade) accanto a un prezzo "
          f"CASUALE con le nostre uscite ({FONTE_CASO})")
    print(f"  {'':<30} {'paper':>9} {'caso':>11}")
    si, su = rep["stop_ingresso"], rep["stop_uscita"]
    paper_iu = "n/d" if si is None else f"{si * 100:.0f}/{su * 100:.0f}%"
    righe = (
        ("stop (sulle uscite)", _pct(rep["stop"]), _pct(c["stop"])),
        (f"stop ingresso/uscita (su {rep['stop_n']})", paper_iu,
         f"{c['stop_ingresso'] * 100:.1f}/{c['stop_uscita'] * 100:.1f}%"),
        ("massimo toccato mediano",
         "n/d" if rep["mfe_mediana_r"] is None else f"{rep['mfe_mediana_r']:.2f}R",
         f"{c['mfe_mediana_r']:.2f}R"),
        ("arrivati al primo target", _pct(rep["primo_target"]), _pct(c["primo_target"])),
        ("vinti", _pct(rep["vinti"]), _pct(c["vinti"])),
        (f"R medio (su {rep['r_n']})",
         "n/d" if rep["r_medio"] is None else f"{rep['r_medio']:+.3f}", f"{c['r_medio']:+.3f}"),
    )
    for nome, p, k in righe:
        print(f"  {nome:<30} {p:>9} {k:>11}")
    print("  vicino al caso = «stop d'ingresso/uscita» e «senza primo target» sono la forma "
          "delle uscite, non una diagnosi")


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
        # + le scartate uscite dalla storia per il taglio (1 ott 2026, K11)
        scartate = (int(esp_doc.get("scartate_tolte") or 0)
                    + sum(1 for v in storia.values() if (v or {}).get("esito") == "scartata"))
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
    return {"declassate": _blocco(decl), "attive": _blocco(attive),
            "regola_3_ott": confronto_3_ott(rows)}


# LA LETTURA DEL 3 OTT (30 set 2026, pacchetto A approvato dal proprietario,
# regola scritta PRIMA della lettura). La voce A4 del backlog dice: se le
# declassate fanno uguale alle attive, il gate sui dati recenti non discrimina e
# la soglia delle 2 notti va ripensata. Ma con ~60 trade contro ~80 il margine e'
# di circa ±0,29R (stima della revisione del 30 set): senza una regola, «uguale»
# vorrebbe dire solo «non si vede la differenza». Qui la regola sta accanto al
# confronto, dove vive gia' (blocco DECLASSATE), e non nel `portafoglio`, che e'
# vicino al limite di 20.000 caratteri del canale ops.
#: si confronta solo dai trade ENTRATI da qui: la fine del difetto della
#: sessione (J13), 27 set 19:40 UTC. Prima, le attive si portavano dentro i
#: giorni del difetto e le declassate (coppie vecchie) no.
DAL_REGOLA_3_OTT = datetime(2026, 9, 27, 19, 40, tzinfo=timezone.utc).timestamp()
#: «uguale» solo se il margine esclude una differenza di questa grandezza
UGUALE_ENTRO_R = 0.15


def esito_3_ott(diff: float | None, margine: float | None) -> str:
    """«diverso» se la differenza sta fuori dal margine (lo zero e' escluso);
    «uguale» solo se tutto l'intervallo differenza ± margine sta dentro
    ±UGUALE_ENTRO_R; altrimenti «non si decide». «diverso» si guarda per primo:
    una differenza vera ma piccola e' comunque una differenza (il gate
    discrimina un po'), e il testo lo dice."""
    if diff is None or margine is None:
        return "non si decide"
    if abs(diff) > margine:
        return "diverso"
    if abs(diff) + margine < UGUALE_ENTRO_R:
        return "uguale"
    return "non si decide"


def confronto_3_ott(rows: list[dict]) -> dict:
    """Declassate contro attive dai trade entrati dal 27 set 19:40 UTC: R medio,
    differenza (declassate - attive) e margine (2 errori standard PER GIORNATA,
    lo stesso conto del FUORI CAMPIONE del `portafoglio`; se esce piu' stretto di
    quello trade per trade si usa il piu' largo). Pura.

    30 set 2026, revisione: il calcolo e' quello della regola, invariato (anche
    senza un minimo di trade per lato: metterlo ora, coi numeri gia' visti,
    vorrebbe dire cambiare la regola). Si contano pero' i trade entrati dal 27
    set 19:40 UTC e lasciati fuori perche' senza R (`declassate_senza_r`,
    `attive_senza_r`): prima sparivano in silenzio."""
    from bot.learning.drift import r_multiplo
    from scripts.portafoglio_backtest import (errore_regola, errore_standard_differenza,
                                              errore_standard_per_giorno, statistiche_lato)

    lati: dict[str, list[tuple[float, str]]] = {"declassate": [], "attive": []}
    senza_r = {"declassate": 0, "attive": 0}
    for t in rows:
        ts = _entry_ts(t)
        if ts is None or ts < DAL_REGOLA_3_OTT:
            continue
        lato = "declassate" if t.get("declassata") else "attive"
        r = r_multiplo(t)
        if r is None:
            senza_r[lato] += 1
            continue
        lati[lato].append((r, giorno_locale(ts)))
    d = statistiche_lato([(r, None, None) for r, _ in lati["declassate"]])
    a = statistiche_lato([(r, None, None) for r, _ in lati["attive"]])
    diff = (d["r_medio"] - a["r_medio"]
            if d["r_medio"] is not None and a["r_medio"] is not None else None)
    es = errore_regola(errore_standard_differenza(d, a),
                       errore_standard_per_giorno(lati["declassate"], lati["attive"]))
    margine = 2.0 * es if es is not None else None
    return {"declassate_n": d["n"], "declassate_r": d["r_medio"],
            "attive_n": a["n"], "attive_r": a["r_medio"],
            "declassate_senza_r": senza_r["declassate"], "attive_senza_r": senza_r["attive"],
            "differenza": diff, "margine": margine, "esito": esito_3_ott(diff, margine)}


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
    c = rep.get("regola_3_ott")
    if c is not None:
        def _f(v, fmt="{:+.3f}"):
            return "n.d." if v is None else fmt.format(v)
        print("  REGOLA DEL 3 OTT (regola scritta il 30 set, prima delle letture): solo i trade "
              "entrati dal 27 set 19:40 UTC (fine del difetto della sessione); «uguale» solo se "
              "il margine esclude ±0,15R, «diverso» se la differenza e' fuori dal margine, "
              "altrimenti «non si decide». Margine = 2 errori standard, il piu' largo fra "
              "quello per giornata e quello trade per trade; almeno 2 giornate.")
        # 30 set 2026, revisione: il testo del margine ora e' quello del diario, e
        # si dicono i trade lasciati fuori perche' senza R
        testo = (f"  dal 27 set 19:40 UTC: declassate {c['declassate_n']} trade R "
                 f"{_f(c['declassate_r'])} · attive {c['attive_n']} trade R {_f(c['attive_r'])} "
                 f"· differenza {_f(c['differenza'])}R, margine {_f(c['margine'], '±{:.3f}')}R "
                 f"(esclusi perche' senza R: declassate {c.get('declassate_senza_r', 0)}, "
                 f"attive {c.get('attive_senza_r', 0)}) -> {c['esito'].upper()}")
        if c["esito"] == "diverso":
            testo += (" (le declassate fanno " + ("meglio" if c["differenza"] > 0 else "peggio")
                      + " delle attive" + (", ma meno di 0,15R" if abs(c["differenza"]) < UGUALE_ENTRO_R
                                           else "") + ")")
        print(testo)


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


def keep_per_strategia_report(trades: list[dict]) -> list[dict]:
    """Per ogni strategia con almeno un verdetto trailing (uscita `trailing_stop`,
    timeframe del bot): i conteggi di `metrics.conta_verdetti_strategia`, la
    proposta di `metrics.proposta_keep_strategia` (None sotto i 5 verdetti o
    fuori dalle soglie) e il tragitto medio lasciato sul tavolo
    (`metrics.soldi_sul_tavolo`). Puro; ordinato per verdetti decrescenti, poi id."""
    per: dict[str, list] = defaultdict(list)
    for t in trades or []:
        if isinstance(t, dict) and isinstance(t.get("strategy"), str) and t.get("strategy"):
            per[t["strategy"]].append(t)
    righe = []
    for gid, ts in per.items():
        c = conta_verdetti_strategia(ts)
        if c["n"] == 0:
            continue
        m = soldi_sul_tavolo(ts)
        righe.append({"strategia": gid, **c, "proposta": proposta_keep_strategia(ts),
                      "miss_n": m["n"], "miss_medio": m["miss_medio"]})
    righe.sort(key=lambda r: (-r["n"], r["strategia"]))
    return righe


#: (1 ott 2026) le righe per nome della tabella del keep: almeno 2 verdetti,
#: al massimo 20 strategie; le altre sommate in una riga
KEEP_RIGHE_MIN_VERDETTI = 2
KEEP_RIGHE_MAX = 20


def print_keep_per_strategia(trades: list[dict]) -> None:
    print(f"\nKEEP PER STRATEGIA (proposta dal vissuto: >= {KEEP_STRATEGIA_MIN_VERDETTI} "
          f"verdetti trailing sul timeframe del bot; 0.25 se prematuri >= 60% e almeno "
          f"meta' da rumore, 0.75 se protetti >= 60%; la giudica il gate, non decide)")
    righe = keep_per_strategia_report(trades)
    if not righe:
        print("  nessuna strategia con verdetti trailing (uscita trailing_stop, "
              f"timeframe {settings.ORCHESTRATOR_TIMEFRAME})")
        return
    print(f"  {'strategia':<14} {'verdetti':>8} {'prematuri':>16} {'protetti':>8} "
          f"{'proposta':>8} {'miss medio':>11}")
    # 1 ott 2026 (K8, spazio): con 76 strategie la tabella era ~3,5 KB e cresce
    # ogni giorno, mentre l'agente ops taglia oltre 20.000 caratteri. Per nome
    # solo le strategie con almeno KEEP_RIGHE_MIN_VERDETTI verdetti (al massimo
    # KEEP_RIGHE_MAX): con un verdetto solo nessuna proposta e' vicina (ne
    # servono KEEP_STRATEGIA_MIN_VERDETTI). Le altre in una riga, coi totali.
    mostrate = [r for r in righe if r["n"] >= KEEP_RIGHE_MIN_VERDETTI][:KEEP_RIGHE_MAX]
    nascoste = [r for r in righe if r not in mostrate]
    for r in mostrate:
        prem = f"{r['prematuri']} (rumore {r['prematuri_rumore']})"
        prop = f"{r['proposta']:g}" if r["proposta"] is not None else "-"
        miss = f"{r['miss_medio']:.2f}" if r["miss_medio"] is not None else "n/d"
        print(f"  {r['strategia']:<14} {r['n']:>8} {prem:>16} {r['protetti']:>8} "
              f"{prop:>8} {miss:>11}")
    if nascoste:
        print(f"  + altre {len(nascoste)} strategie con meno verdetti: "
              f"{sum(r['n'] for r in nascoste)} verdetti, prematuri "
              f"{sum(r['prematuri'] for r in nascoste)}, protetti "
              f"{sum(r['protetti'] for r in nascoste)}"
              + (f", {sum(1 for r in nascoste if r['proposta'] is not None)} con proposta"
                 if any(r["proposta"] is not None for r in nascoste) else ""))
    print("  miss medio = frazione del tragitto entry->TP lasciata sul tavolo all'uscita "
          "(0 = al TP, 1 = all'entrata): misura, non regola")


# --------------------------------------------------------------------------- #
# LA SOGLIA DEL WIN RATE ALLENTATA (1 ott 2026, backlog K10)                   #
# --------------------------------------------------------------------------- #
# Fra il 19 ago e l'8 set il supervisore automatico ha abbassato
# GATE_WIN_RATE_FLOOR da 0,45 a 0,3966 (`tuning.env`) e non l'ha piu' rimessa.
# Qui si CONTA soltanto (sola lettura, nessuna soglia cambia): quante validate
# hanno l'ultimo win rate del gate fra la soglia di oggi e 0,45, cioe' quelle
# che con la soglia di prima sarebbero cadute, e come rendono nel paper in R.
# Approssimazione dichiarata: `last_win_rate` e' l'ultimo passaggio, non tutti.
#: la soglia prima dell'allentamento del supervisore
SOGLIA_WR_ORIGINALE = 0.45


def gruppo_win_rate(rec, soglia_oggi: float,
                    originale: float = SOGLIA_WR_ORIGINALE) -> str:
    """«piena» (ultimo win rate >= originale), «allentata» (fra la soglia di
    oggi e l'originale: esiste solo grazie all'allentamento), «sotto» (sotto
    anche la soglia di oggi: e' passata prima o con altri numeri) o «ignoto»
    (campo assente, alleggerito). Pura."""
    try:
        wr = float((rec or {}).get("last_win_rate"))
    except (TypeError, ValueError):
        return "ignoto"
    if wr >= originale:
        return "piena"
    return "allentata" if wr >= soglia_oggi else "sotto"


def soglia_wr_report(trades: list[dict], pairs: dict | None, validate,
                     soglia_oggi: float, dal_ts: float | None = None) -> dict:
    """K10: le validate per gruppo di win rate (`gruppo_win_rate`) e i trade
    del paper delle stesse coppie in R (netto, `drift.r_multiplo`), tutto e dal
    27 set 19:40 UTC. I trade di coppie oggi non validate vanno in «non piu'
    validate». Pura."""
    from bot.learning.drift import r_multiplo
    dal_ts = DAL_REGOLA_3_OTT if dal_ts is None else dal_ts
    pairs = pairs if isinstance(pairs, dict) else {}
    validate = set(validate or ())
    gruppo = {k: gruppo_win_rate(pairs.get(k), soglia_oggi) for k in validate}
    nomi = ("piena", "allentata", "sotto", "ignoto", "non_validate")
    out = {g: {"coppie": 0, "tutto": [[], 0], "dal": [[], 0]} for g in nomi}
    for g in gruppo.values():
        out[g]["coppie"] += 1
    for t in trades or []:
        k = f"{t.get('symbol', '?')}|{t.get('strategy', '?')}"
        g = gruppo.get(k, "non_validate")
        r = r_multiplo(t)
        ts = _entry_ts(t)
        for col in ["tutto"] + (["dal"] if ts is not None and ts >= dal_ts else []):
            if r is None:
                out[g][col][1] += 1
            else:
                out[g][col][0].append(r)
    return {"soglia_oggi": soglia_oggi, "originale": SOGLIA_WR_ORIGINALE,
            "gruppi": {g: {"coppie": v["coppie"], "tutto": _r_stat(*v["tutto"]),
                           "dal": _r_stat(*v["dal"])} for g, v in out.items()}}


def _fr(v) -> str:
    return "—" if v is None else f"{v:+.3f}"


def print_soglia_wr(rep: dict | None) -> None:
    print("\nSOGLIA DEL WIN RATE (K10): il supervisore l'ha abbassata e non l'ha rimessa. "
          "Si conta e basta, nessuna soglia cambia qui")
    if not rep:
        print("  registro non letto: conteggio saltato")
        return
    print(f"  soglia di oggi {rep['soglia_oggi']:.4f} · prima {rep['originale']:.2f} · "
          f"«allentata» = ultimo win rate del gate fra le due: con la soglia di prima "
          f"sarebbe caduta (l'ultimo passaggio, non tutti: approssimazione)")
    etichette = {"piena": "win rate >= 0,45", "allentata": "ALLENTATA",
                 "sotto": "sotto la soglia di oggi", "ignoto": "win rate non salvato",
                 "non_validate": "trade di coppie non piu' validate"}
    print("                                   coppie ‖  paper tutto: n  R medio ‖ dal 27/9: n  R medio")
    for g, et in etichette.items():
        v = rep["gruppi"][g]
        cop = "" if g == "non_validate" else str(v["coppie"])
        print(f"  {et:<33}{cop:>5}  ‖ {v['tutto']['n']:>14}  {_fr(v['tutto']['r_medio']):>7} ‖ "
              f"{v['dal']['n']:>11}  {_fr(v['dal']['r_medio']):>7}")
    print("  lettura: solo un conteggio (pochi trade a coppia, nessun margine). Rimettere la "
          "soglia a 0,45 e' una modifica del gate: dopo le letture del 7-14 ott, col numero")


# --------------------------------------------------------------------------- #
# COSA SAREBBE SUCCESSO SUL PAPER con stop giornaliero e freno di serie        #
# (1 ott 2026, domanda del proprietario su H3 e H4, parcheggiate il 25 set)    #
# --------------------------------------------------------------------------- #
# Sola misura: rigioca i trade VERI del paper con una regola in piu' e dice
# quanto sarebbe cambiato il risultato. Approssimazioni dichiarate: un trade
# saltato non libera posto per altri (i trade del paper sono quelli che il bot
# ha aperto davvero); la size dimezzata dimezza il PnL di quel trade. Nessuna
# regola cambia qui: le due voci restano parcheggiate finche' il proprietario
# non le riprende, e una modifica passerebbe dal gate (portafoglio simulato).
#: l'equity con cui e' partito il paper (929,18 + 70,82 di perdite, ops 0387)
EQUITY_INIZIO_PAPER = 1000.0


def _uscita_ts(t: dict) -> float | None:
    v = t.get("exit_ts")
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def rigioca_paper(trades: list[dict], stop_giorno: float = 0.0, serie_k: int = 0,
                  serie_globale: bool = False, serie_mult: float = 0.5,
                  equity0: float = EQUITY_INIZIO_PAPER) -> dict:
    """I trade del paper con UNA regola in piu'. Pura.

    * `stop_giorno` (es. 0,03): un trade NON si apre se le chiusure dello
      stesso giorno (ora italiana) avvenute PRIMA del suo ingresso hanno gia'
      perso almeno `stop_giorno` x l'equity di inizio giornata.
    * `serie_k` (es. 4): un trade si apre a `serie_mult` della size se prima
      del suo ingresso la sua strategia (o tutto il bot, con `serie_globale`)
      ha chiuso `serie_k` perdite di fila; la serie si azzera alla prima
      vincita. Si contano solo i trade aperti davvero nel rigioco (un trade
      saltato non entra nella serie).
    Ritorna PnL, trade saltati e ridotti, giorni fermati, drawdown massimo
    sulla curva delle chiusure, e il PnL per giorno."""
    righe = []
    for t in trades or []:
        en, ex = _entry_ts(t), _uscita_ts(t)
        if en is None or ex is None:
            continue
        try:
            pnl = float(t.get("pnl", 0) or 0)
        except (TypeError, ValueError):
            continue
        righe.append((float(en), ex, pnl, str(t.get("strategy") or "?")))
    righe.sort(key=lambda r: (r[0], r[1]))
    aperti: list[tuple] = []           # (ex, pnl_effettivo, strategia, giorno_uscita)
    chiusi: list[tuple] = []           # (ex, pnl_effettivo, strategia)
    saltati = ridotti = 0
    giorni_fermati: set[str] = set()
    serie_strat: dict[str, int] = defaultdict(int)
    serie_glob = 0
    for en, ex, pnl, gid in righe:
        # le chiusure avvenute prima di questo ingresso, in ordine di uscita
        aperti.sort(key=lambda a: a[0])
        while aperti and aperti[0][0] <= en:
            c = aperti.pop(0)
            chiusi.append(c[:3])
            if c[1] < 0:
                serie_strat[c[2]] += 1
                serie_glob += 1
            elif c[1] > 0:
                serie_strat[c[2]] = 0
                serie_glob = 0
        giorno = giorno_locale(en)
        if stop_giorno > 0:
            inizio = equity0 + sum(p for e, p, _ in chiusi if giorno_locale(e) < giorno)
            oggi = sum(p for e, p, _ in chiusi if giorno_locale(e) == giorno)
            if -oggi >= stop_giorno * inizio - 1e-9:
                saltati += 1
                giorni_fermati.add(giorno)
                continue
        mult = 1.0
        if serie_k > 0 and (serie_glob if serie_globale else serie_strat[gid]) >= serie_k:
            mult = serie_mult
            ridotti += 1
        aperti.append((ex, pnl * mult, gid))
    chiusi.extend(a[:3] for a in aperti)
    chiusi.sort(key=lambda c: c[0])
    eq = picco = equity0
    dd = 0.0
    per_giorno: dict[str, float] = defaultdict(float)
    for ex, p, _ in chiusi:
        eq += p
        picco = max(picco, eq)
        dd = max(dd, (picco - eq) / picco if picco > 0 else 0.0)
        per_giorno[giorno_locale(ex)] += p
    return {"pnl": round(eq - equity0, 2), "n": len(chiusi), "saltati": saltati,
            "ridotti": ridotti, "giorni_fermati": len(giorni_fermati),
            "max_dd_pct": round(dd * 100, 2),
            "per_giorno": {g: round(v, 2) for g, v in sorted(per_giorno.items())}}


#: gli scenari del rigioco: (etichetta, argomenti)
SCENARI_PAPER = (
    ("com'e' andato davvero", {}),
    ("stop giornaliero 2%", {"stop_giorno": 0.02}),
    ("stop giornaliero 3%", {"stop_giorno": 0.03}),
    ("freno di serie: 4 perdite della strategia -> meta'", {"serie_k": 4}),
    ("freno di serie: 3 perdite della strategia -> meta'", {"serie_k": 3}),
    ("freno di serie: 4 perdite del bot -> meta'", {"serie_k": 4, "serie_globale": True}),
    ("freno di serie: 3 perdite del bot -> meta'", {"serie_k": 3, "serie_globale": True}),
)


def print_rigioco_paper(trades: list[dict]) -> None:
    print("\nCOSA SAREBBE SUCCESSO SUL PAPER (H3 stop giornaliero, H4 freno di serie): i trade "
          "veri rigiocati con una regola in piu'. Solo misura, nessuna regola cambia")
    base = rigioca_paper(trades)
    if not base["n"]:
        print("  nessun trade con apertura e chiusura note")
        return
    peggiori = sorted(base["per_giorno"].items(), key=lambda kv: kv[1])[:3]
    print(f"  {'scenario':<52}{'PnL':>9}{'diff':>8}{'max dd':>8}{'saltati':>8}"
          f"{'ridotti':>8}{'gg fermi':>9}  " + " ".join(g[5:] for g, _ in peggiori))
    for nome, kw in SCENARI_PAPER:
        r = rigioca_paper(trades, **kw)
        gp = " ".join(f"{r['per_giorno'].get(g, 0.0):>+6.2f}" for g, _ in peggiori)
        print(f"  {nome:<52}{r['pnl']:>+9.2f}{r['pnl'] - base['pnl']:>+8.2f}"
              f"{r['max_dd_pct']:>7.2f}%{r['saltati']:>8}{r['ridotti']:>8}"
              f"{r['giorni_fermati']:>9}  {gp}")
    print(f"  equity di partenza {EQUITY_INIZIO_PAPER:.0f}; le ultime colonne sono i 3 giorni "
          f"peggiori del paper vero (ora italiana). Approssimazione: un trade saltato non "
          f"libera posto per altri; meta' size = meta' PnL. Giudica il gate (portafoglio), "
          f"non il paper")


# --------------------------------------------------------------------------- #
# LE FUNZIONI SERVONO? (1 ott 2026, punto 3 della richiesta del proprietario) #
# --------------------------------------------------------------------------- #
def print_funzioni_servono(trades_tutti: list[dict], decisioni_ombra: list[dict] | None,
                           specs: dict | None) -> None:
    """Per ogni funzione che agisce sui trade: il gruppo toccato contro gli
    altri in R, col verdetto della regola scritta in `bot/learning/contributi.py`
    prima dei numeri, e i USDT risparmiati (o persi) dove la funzione riduce
    solo la size."""
    from bot.learning.contributi import contributi, ombra_ai, per_origine, riga_verdetto
    print("\nLE FUNZIONI SERVONO? (gruppo toccato dalla funzione contro gli altri, in R netto; "
          "regola in bot/learning/contributi.py, scritta prima dei numeri)")
    voci = contributi(trades_tutti)
    if decisioni_ombra is not None:
        voci.append(ombra_ai(trades_tutti, decisioni_ombra))
    for v in voci:
        print(f"  {v['nome']}: {v['cosa']}")
        print(f"    {riga_verdetto(v['confronto'])}")
        if "usdt_risparmiati" in v:
            print(f"    a size piena sugli stessi {v['n_usdt']} trade: "
                  f"{v['usdt_risparmiati']:+.2f} USDT risparmiati (negativo = guadagni tolti)")
        if v.get("rischio_medio_pct"):
            rm = v["rischio_medio_pct"]
            def _pc(v):
                return "—" if v is None else f"{v * 100:.2f}%"
            print(f"    rischio effettivo medio: declassate {_pc(rm.get('declassate'))} · "
                  f"attive {_pc(rm.get('attive'))} del capitale (K5: il quarto agisce davvero?)")
        if v.get("nota"):
            print(f"    nota: {v['nota']}")
    if specs is not None:
        po = per_origine(trades_tutti, specs)
        def _rr(v):
            return "—" if v is None else f"{v:+.3f}R"
        parti = " · ".join(f"{o} {st['n']} trade {_rr(st['r_medio'])}" for o, st in po.items())
        print(f"  ORIGINE DELLE STRATEGIE nel paper (le idee AI rendono?): {parti or 'nessun trade'}")
    print("  verdetti: «contribuisce» / «va contro» oltre il margine (2 errori standard), "
          "altrimenti «non si vede ancora»; sotto 10 trade per gruppo «campione piccolo»")


# --------------------------------------------------------------------------- #
# L'AFFOLLAMENTO: quante posizioni nello stesso verso, insieme (2 ott 2026)   #
# --------------------------------------------------------------------------- #
# Il 2 ott alle 20:47 il bot ha aperto 10 long in 20 secondi (ops 0442-0443):
# in parita' apre tutti i segnali validi del ciclo, il tetto di 5 posizioni e'
# spento e il tetto per direzione (3% in rischio) con le puntate ridotte ammette
# ~20 posizioni (backlog I6). Qui si MISURA, per decidere dopo le letture del
# 7-14 ott: per ogni trade, quante posizioni nello stesso verso erano aperte al
# suo ingresso (lui compreso), e come sono finiti i trade per fascia; piu' gli
# «episodi» (>= 6 aperture nello stesso verso entro 5 minuti).
#: le fasce di affollamento (posizioni nello stesso verso, trade compreso)
FASCE_AFFOLLAMENTO = ((1, 2, "1-2"), (3, 5, "3-5"), (6, 10 ** 6, "6+"))
#: una «ondata»: tante aperture nello stesso verso entro questi secondi
ONDATA_S = 300
ONDATA_MIN = 6


def affollamento_report(trades: list[dict]) -> dict:
    """Per fascia di affollamento: n, vinti, PnL, R netto medio (drift.r_multiplo);
    e gli episodi (ondate) con data, verso, quante e PnL totale. Pura."""
    from bot.learning.drift import r_multiplo
    righe = []
    for t in trades or []:
        en, ex, d = _entry_ts(t), _uscita_ts(t), _dir(t)
        if en is None or ex is None or d not in ("long", "short"):
            continue
        righe.append((en, ex, d, t))
    fasce = {et: {"n": 0, "vinti": 0, "pnl": 0.0, "r": []} for _a, _b, et in FASCE_AFFOLLAMENTO}
    for en, ex, d, t in righe:
        insieme = sum(1 for en2, ex2, d2, _ in righe if d2 == d and en2 <= en < ex2)
        for a, b, et in FASCE_AFFOLLAMENTO:
            if a <= insieme <= b:
                f = fasce[et]
                f["n"] += 1
                pnl = float(t.get("pnl", 0) or 0)
                f["pnl"] += pnl
                f["vinti"] += 1 if pnl > 0 else 0
                r = r_multiplo(t)
                if r is not None:
                    f["r"].append(r)
                break
    out = {et: {"n": f["n"], "vinti": f["vinti"], "pnl": round(f["pnl"], 2),
                "n_r": len(f["r"]),
                "r_medio": round(sum(f["r"]) / len(f["r"]), 3) if f["r"] else None}
           for et, f in fasce.items()}
    # le ondate: aperture nello stesso verso raggruppate entro ONDATA_S
    ondate = []
    for d in ("long", "short"):
        ap = sorted(((en, t) for en, _ex, d2, t in righe if d2 == d), key=lambda x: x[0])
        i = 0
        while i < len(ap):
            j = i
            while j + 1 < len(ap) and ap[j + 1][0] - ap[i][0] <= ONDATA_S:
                j += 1
            gruppo = ap[i:j + 1]
            if len(gruppo) >= ONDATA_MIN:
                # ora italiana davvero (3 ott 2026: astimezone() senza fuso dava l'ora della VPS, UTC)
                ondate.append({"quando": giorno_locale(ap[i][0]) + " " + datetime.fromtimestamp(
                    ap[i][0], fuso()).strftime("%H:%M"), "verso": d,
                    "n": len(gruppo),
                    "pnl": round(sum(float(t.get("pnl", 0) or 0) for _, t in gruppo), 2)})
            i = j + 1
    ondate.sort(key=lambda o: o["quando"])
    return {"fasce": out, "ondate": ondate}


def print_affollamento(rep: dict) -> None:
    print("\nAFFOLLAMENTO (2 ott 2026): posizioni nello stesso verso aperte all'ingresso del trade, "
          "trade compreso. Solo misura: il tetto per direzione (3% in rischio) non cambia qui")
    print(f"  {'insieme':<9}{'trade':>7}{'vinti':>7}{'PnL':>9}{'R medio':>9}")
    for _a, _b, et in FASCE_AFFOLLAMENTO:
        f = rep["fasce"][et]
        r = "—" if f["r_medio"] is None else f"{f['r_medio']:+.3f}"
        print(f"  {et:<9}{f['n']:>7}{f['vinti']:>7}{f['pnl']:>+9.2f}{r:>9}")
    if rep["ondate"]:
        print(f"  ondate (>= {ONDATA_MIN} aperture nello stesso verso entro {ONDATA_S // 60} minuti, ora "
              f"italiana):")
        for o in rep["ondate"][-10:]:
            print(f"    {o['quando']}  {o['verso']:<5} {o['n']:>3} aperture  PnL {o['pnl']:+.2f}")
    else:
        print(f"  nessuna ondata di {ONDATA_MIN}+ aperture nello stesso verso entro {ONDATA_S // 60} minuti")


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
        day = giorno_locale(float(ex))      # giornate in ora italiana (28 set 2026)
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
    print("  per giorno (ora italiana): " + " · ".join(
        f"{g} {per_day[g]}" for g in sorted(per_day)))
    if durations_h:
        print(f"Durata media holding:    {mean(durations_h):.1f}h  (min {min(durations_h):.1f}h · max {max(durations_h):.1f}h)")
    print(f"Posizioni contemporanee: MAX {max_conc} · media nel tempo {avg_conc:.1f}")
    print(f"Coin distinte:           {len(coins)}")
    print(f"Strategie distinte:      {len(strategies)}")
    print("\nLettura: se MAX contemporanee << 10 (il tetto da margine), il numero di")
    print("trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.")

    print_direction_report(direction_report(trades))
    # I CONTI IN R (1 ott 2026, K8): gli stessi gruppi, in R e col taglio al 27 set
    print_conti_in_r(conti_in_r_report(trades))

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
    # LA FIRMA DEL CASO (1 ott 2026, K4): accanto alle classi degli stop, cosa
    # darebbe un prezzo casuale con le nostre uscite (costanti del 30 set)
    print_firma_del_caso(firma_del_caso_report(trades))
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

    # IL KEEP PER STRATEGIA (27 set 2026, backlog I3): per ogni strategia con
    # almeno un verdetto trailing sul timeframe del bot, i conteggi da cui la
    # discovery ricava la proposta (`metrics.proposta_keep_strategia`: 0.25 se
    # i prematuri sono al 60% e almeno meta' da rumore, 0.75 se i protetti sono
    # al 60%, con >= 5 verdetti) e quanto tragitto verso il TP e' rimasto sul
    # tavolo (frazione entry->TP, solo misurata). Su TUTTI i trade letti,
    # esplorativi compresi: e' cio' che vede `keep_per_strategia`.
    print_keep_per_strategia(trades_letti)

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

    # LA SOGLIA DEL WIN RATE ALLENTATA (1 ott 2026, K10): una lettura del
    # registro in piu', fail-open
    try:
        from bot.core.firebase_client import decode_pairs
        from bot.core.registry import coppie_validate
        reg = fb.get_doc("strategy_registry", "validated") or {}
        reg_pairs = decode_pairs(reg.get("pairs"))
        rep_wr = soglia_wr_report(trades, reg_pairs, coppie_validate(reg_pairs),
                                  float(settings.GATE_WIN_RATE_FLOOR))
    except Exception as exc:  # noqa: BLE001
        print(f"[soglia-wr] registro non letto ({str(exc)[:80]})")
        rep_wr = None
    print_soglia_wr(rep_wr)

    # STOP GIORNALIERO E FRENO DI SERIE SUL PAPER (1 ott 2026, H3/H4): solo misura
    print_rigioco_paper(trades)

    # L'AFFOLLAMENTO (2 ott 2026): quante posizioni nello stesso verso insieme
    print_affollamento(affollamento_report(trades))

    # LE FUNZIONI SERVONO? (1 ott 2026): due letture in piu' (le decisioni
    # dell'ombra, ~240 documenti, e le spec), fail-open
    try:
        ombra = fb.query_collection("ai_shadow")
    except Exception as exc:  # noqa: BLE001
        print(f"[funzioni] ombra non letta ({str(exc)[:80]})")
        ombra = None
    try:
        from bot.core.firebase_client import decode_pairs as _dp
        specs_doc = _dp((fb.get_doc("discovered_strategies", "specs") or {}).get("specs"))
    except Exception as exc:  # noqa: BLE001
        print(f"[funzioni] spec non lette ({str(exc)[:80]})")
        specs_doc = None
    print_funzioni_servono(trades_letti, ombra, specs_doc)

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
