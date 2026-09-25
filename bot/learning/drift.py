"""
RILEVATORE DI DERIVA — chiude l'anello tra paper e gate.

IL PROBLEMA CHE RISOLVE
Il gate valida sui dati storici e produce una PROMESSA per ogni coppia: "PF ~1.4,
il prezzo tocca il primo gradino nel 60% dei casi". Il paper esegue e misura cosa
succede DAVVERO. Finora le due cose non si parlavano: il paper aggiustava solo
QUANTO tradare (peso/leva/rischio), mai segnalava che una coppia stava tradendo la
promessa. Il gate se ne accorgeva solo indirettamente, alla passata successiva.

IL RUOLO CORRETTO DEL PAPER: FALSIFICARE, NON OTTIMIZZARE
Il paper e' l'unico dato davvero mai visto dalla selezione. Usarlo per TARARE i
parametri lo consumerebbe come training set — lo stesso difetto appena rimosso dal
gate. Qui il paper fa il giudice: confronta il vissuto con la promessa e, quando la
contraddice, (a) frena subito in produzione e (b) manda l'evidenza al gate, che
rivalidera' su dati storici ORA comprensivi del periodo appena vissuto. Se la
coppia si redime torna piena; se no, il fail_count la porta all'auto-purge.

TRE GRANULARITA', perche' i campioni arrivano a velocita' diverse
  * COPPIA (coin+strategia): il segnale piu' preciso ma il piu' lento (~0.03
    trade/giorno per coppia). Serve pazienza.
  * STRATEGIA: aggrega su tutte le coin -> si popola in giorni, non mesi.
  * GLOBALE: il piu' rapido. Se l'intero registro delude, e' un problema di
    sistema (regime, costi, gate), non della singola coppia.

DUE SEGNALI INDIPENDENTI
  1. PROFIT FACTOR: il vissuto contro il PF validato dal gate.
  2. RAGGIUNGIBILITA' DEI TP (mfe_r): se il prezzo non arriva mai nemmeno al primo
     gradino, la scala e' un desiderio — e lo si sa da UN numero per trade, senza
     aspettare esiti completi. E' il segnale piu' efficiente che abbiamo.

IL FRENO DI SERIE (size, non veto)
Le soglie sopra chiedono campione: 20 trade per strategia, 40 per il globale. Il
23 set 2026 il paper aveva 40 trade in 8 giorni, 6 giornate su 8 in perdita e una
strategia con 4 trade e 4 perdite — e nessun freno l'aveva ancora toccata. Per
"adattarsi ogni giorno" serve un segnale che maturi in giorni: la SERIE di
perdite consecutive alla fine della sequenza di ogni strategia (su tutte le
coin). A STREAK_BRAKE_LOSSES perdite di fila la size si moltiplica per
STREAK_BRAKE_FACTOR finche' non arriva un trade in guadagno, che azzera la serie.
Non e' un verdetto e non tara nulla: la soglia e' dichiarata prima (4, ragionato:
con win rate 45% capita ~9% delle volte per sequenza), il freno e' solo sulla
size, e rimuovere resta compito del gate sulla storia.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from bot.config import settings

# esiti NON decisi dalla strategia: non dicono nulla sul suo edge
_EXTERNAL = {"manual", "kill_switch", "circuit_breaker"}

OK, WATCH, DRIFT = "ok", "watch", "drift"


def _pf(pnls: list[float]) -> float:
    gains = sum(x for x in pnls if x > 0)
    losses = -sum(x for x in pnls if x < 0)
    if losses > 0:
        return gains / losses
    return 99.0 if gains > 0 else 0.0


def _median(xs: list[float]) -> float:
    if not xs:
        return 0.0
    s = sorted(xs)
    return s[len(s) // 2]


def _first_rung(params: dict | None) -> float:
    """Primo gradino della scala di questa coppia, in unita' di R. E' la soglia che
    il prezzo DEVE superare perche' il trade incassi qualcosa."""
    mults = (params or {}).get("scale_r_mults") or settings.SCALE_OUT_R_MULTIPLES
    try:
        return float(min(float(m) for m in mults))
    except (TypeError, ValueError):
        return 0.0


def _verdict(n: int, min_n: int, live_pf: float, expected_pf: float,
             mfe_med: float, rung: float) -> tuple[str, str]:
    """(verdetto, motivo). WATCH = sospetto senza campione: si vede, non si agisce."""
    reasons = []
    if expected_pf > 0 and live_pf < expected_pf * settings.DRIFT_PF_RATIO:
        reasons.append(f"PF {live_pf:.2f} vs {expected_pf:.2f} atteso")
    if rung > 0 and mfe_med > 0 and mfe_med < rung * settings.DRIFT_MFE_RATIO:
        reasons.append(f"mfe mediana {mfe_med:.2f}R < primo TP {rung:.2f}R")
    if not reasons:
        return OK, ""
    # il campione decide se e' un ALLARME o solo un SOSPETTO
    return (DRIFT if n >= min_n else WATCH), " · ".join(reasons)


def _bucket(trades: list[dict], expected_pf: float, params: dict | None,
            min_n: int) -> dict:
    pnls = [float(t.get("pnl", 0) or 0) for t in trades]
    mfes = [float(t["mfe_r"]) for t in trades if t.get("mfe_r") is not None]
    live_pf = _pf(pnls)
    mfe_med = _median(mfes)
    rung = _first_rung(params)
    verdict, reason = _verdict(len(trades), min_n, live_pf, expected_pf, mfe_med, rung)
    return {
        "verdict": verdict, "reason": reason, "trades": len(trades),
        "live_pf": round(live_pf, 3), "expected_pf": round(expected_pf, 3),
        "pnl": round(sum(pnls), 2),
        "mfe_median": round(mfe_med, 2) if mfes else None,
        "first_rung_r": round(rung, 2),
    }


def _ts_sicuro(v) -> float:
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def serie_perdite(trades: Iterable[dict]) -> dict[str, int]:
    """Per strategia: quante perdite CONSECUTIVE chiudono la sua sequenza di trade.

    La sequenza e' ordinata per exit_ts (assente o illeggibile -> 0: l'ordine
    e' stabile, quindi i trade senza data restano nell'ordine in cui arrivano, e
    una data storta non fa saltare l'intero documento di deriva). Un pnl >= 0
    interrompe la serie: un trade in pari basta a rimetterla a zero, perche' la
    domanda e' "sta perdendo ADESSO", non "quanto ha perso". Gli esiti esterni
    (manual, kill switch, circuit breaker) non contano: non li ha decisi la
    strategia. Strategie senza trade utili non compaiono.

    La serie si calcola sui trade che riceve: nel bot sono quelli degli ultimi
    30 giorni (refresh_weights), quindi una strategia ferma da un mese esce dal
    freno anche senza un guadagno — senza trade non c'e' size da frenare."""
    by_strat: dict[str, list[dict]] = defaultdict(list)
    for t in trades:
        if str(t.get("exit_reason", "")) in _EXTERNAL:
            continue
        by_strat[str(t.get("strategy", "?"))].append(t)
    out: dict[str, int] = {}
    for strat, ts in by_strat.items():
        ordered = sorted(ts, key=lambda t: _ts_sicuro(t.get("exit_ts")))
        n = 0
        for t in ordered:
            n = n + 1 if float(t.get("pnl", 0) or 0) < 0 else 0
        out[strat] = n
    return out


def compute_drift(trades: Iterable[dict], pairs: dict | None = None) -> dict:
    """Confronta il vissuto (trade paper) con la promessa del gate (registro).

    `pairs`: mappa "SYMBOL|strategy" -> record del registro (last_pf, last_params).
    Ritorna {"pairs": {...}, "strategies": {...}, "global": {...}, "serie": {...}}
    con un verdetto per ciascuna granularita'. Coppie senza promessa nel registro
    vengono saltate: senza un atteso non c'e' niente da falsificare. "serie"
    invece copre TUTTE le strategie con trade, anche senza promessa: il freno di
    serie non confronta con un atteso, guarda solo se sta perdendo di fila."""
    pairs = pairs or {}
    # PAPER ESPLORATIVO (25 set 2026, F1bis): fuori da TUTTE le granularita',
    # globale compresa. La deriva confronta il vissuto con la PROMESSA del gate,
    # e un quasi-passaggio non ha una promessa: i suoi trade (a un quarto della
    # size) non devono ne' frenare le validate ne' bocciarle per coppia.
    rows = [t for t in trades if str(t.get("exit_reason", "")) not in _EXTERNAL
            and not t.get("esplorativa")]

    by_pair: dict[str, list[dict]] = defaultdict(list)
    by_strat: dict[str, list[dict]] = defaultdict(list)
    for t in rows:
        sym, strat = t.get("symbol", "?"), t.get("strategy", "?")
        by_pair[f"{sym}|{strat}"].append(t)
        by_strat[strat].append(t)

    out_pairs: dict[str, dict] = {}
    for key, ts in by_pair.items():
        rec = pairs.get(key) or {}
        expected = float(rec.get("last_pf", 0) or 0)
        if expected <= 0:
            continue        # nessuna promessa dal gate -> niente da falsificare
        out_pairs[key] = _bucket(ts, expected, rec.get("last_params"),
                                 settings.DRIFT_MIN_TRADES_PAIR)

    # atteso di strategia = media dei PF validati delle sue coppie
    exp_by_strat: dict[str, list[float]] = defaultdict(list)
    for key, rec in pairs.items():
        pf = float((rec or {}).get("last_pf", 0) or 0)
        if pf > 0:
            exp_by_strat[key.split("|", 1)[-1]].append(pf)
    out_strats = {
        name: _bucket(ts, sum(exp_by_strat[name]) / len(exp_by_strat[name]),
                      None, settings.DRIFT_MIN_TRADES_STRATEGY)
        for name, ts in by_strat.items() if exp_by_strat.get(name)
    }

    all_exp = [pf for v in exp_by_strat.values() for pf in v]
    glob = _bucket(rows, (sum(all_exp) / len(all_exp)) if all_exp else 0.0,
                   None, settings.DRIFT_MIN_TRADES_GLOBAL) if rows else {}
    return {"pairs": out_pairs, "strategies": out_strats, "global": glob,
            "serie": serie_perdite(rows)}


def weight_factor(drift_doc: dict | None, symbol: str, strategy: str) -> float:
    """Moltiplicatore di size/leva da applicare ORA, prima che il gate rivaluti.

    Frena la coppia (o l'intera strategia) che sta contraddicendo la promessa,
    senza spegnerla: la decisione di rimuoverla spetta al gate, che rivalidera' su
    dati storici. 1.0 = nessuna deriva o funzione disattivata.

    Le tre granularita' si moltiplicano perche' dicono cose diverse e cumulabili:
    la coppia sbaglia, la strategia sbaglia ovunque, il registro INTERO sbaglia.
    Il livello GLOBALE e' quello che matura per primo (le soglie per coppia
    richiedono 8 trade e i trade si spargono su decine di coppie), ed e' anche il
    piu' solido perche' e' l'unico con abbastanza campione: ignorarlo lasciava il
    bot a size piena mentre il suo stesso rilevatore aveva gia' emesso 'drift'.

    Il FRENO DI SERIE si somma agli altri: matura in giorni invece che in
    settimane, e DRIFT_WEIGHT_FLOOR resta il pavimento di tutto."""
    if not settings.DRIFT_ENABLED or not drift_doc:
        return 1.0
    f = 1.0
    if (drift_doc.get("pairs") or {}).get(f"{symbol}|{strategy}", {}).get("verdict") == DRIFT:
        f *= settings.DRIFT_WEIGHT_FACTOR
    if (drift_doc.get("strategies") or {}).get(strategy, {}).get("verdict") == DRIFT:
        f *= settings.DRIFT_WEIGHT_FACTOR
    if (drift_doc.get("global") or {}).get("verdict") == DRIFT:
        f *= settings.DRIFT_WEIGHT_FACTOR
    if _serie_attiva(drift_doc, strategy):
        f *= settings.STREAK_BRAKE_FACTOR
    return max(settings.DRIFT_WEIGHT_FLOOR, f)


def _serie_attiva(drift_doc: dict, strategy: str) -> bool:
    """True se la strategia ha chiuso almeno STREAK_BRAKE_LOSSES perdite di fila."""
    if not settings.STREAK_BRAKE_ENABLED:
        return False
    try:
        n = int((drift_doc.get("serie") or {}).get(strategy, 0) or 0)
    except (TypeError, ValueError):
        return False
    return n >= settings.STREAK_BRAKE_LOSSES


def motivi_freno(drift_doc: dict | None, symbol: str, strategy: str) -> list[str]:
    """I motivi per cui weight_factor sta frenando questa coppia, in parole: vanno
    nella nota del trade, cosi' dal registro si legge PERCHE' la size era ridotta
    invece di dover ricostruire il documento di deriva di quel momento. Lista
    vuota = nessun freno (o funzione disattivata), coerente con weight_factor."""
    if not settings.DRIFT_ENABLED or not drift_doc:
        return []
    motivi: list[str] = []
    if (drift_doc.get("pairs") or {}).get(f"{symbol}|{strategy}", {}).get("verdict") == DRIFT:
        motivi.append("deriva coppia")
    if (drift_doc.get("strategies") or {}).get(strategy, {}).get("verdict") == DRIFT:
        motivi.append("deriva strategia")
    if (drift_doc.get("global") or {}).get("verdict") == DRIFT:
        motivi.append("deriva globale")
    if _serie_attiva(drift_doc, strategy):
        n = int((drift_doc.get("serie") or {}).get(strategy, 0) or 0)
        motivi.append(f"serie {n} perdite")
    return motivi


def drifted_keys(drift_doc: dict | None) -> list[str]:
    """Coppie in deriva CONFERMATA: e' l'evidenza che il gate consuma alla passata
    successiva (fail_count -> auto-purge se anche la storia la boccia)."""
    if not drift_doc:
        return []
    return sorted(k for k, v in (drift_doc.get("pairs") or {}).items()
                  if v.get("verdict") == DRIFT)
