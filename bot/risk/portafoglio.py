"""BACKTEST DI PORTAFOGLIO: le coppie validate messe INSIEME, con i limiti veri.

24 settembre 2026. Il gate valida una coppia (coin + strategia) alla volta, con
10.000$ fissi e nessun'altra posizione aperta. Il paper e' la PRIMA volta in
cui le ~59 coppie validate girano insieme sullo stesso conto, con il tetto di
posizioni aperte, una posizione per coin, il cooldown dopo uno stop e il tetto
di perdita per coin al giorno. Tutto cio' che succede FRA le coppie — quante
sono aperte nello stesso momento, quante spingono nella stessa direzione, che
giornata fanno sommate — il gate non lo puo' vedere per costruzione, e finora
lo si scopriva solo vivendolo nel paper (i tre short in fila del 21 set, backlog
E4, sono nati esattamente cosi').

Questo modulo e' la simulazione, PURA: prende una lista di trade gia' calcolati
dal motore di backtest (uno per coppia, come farebbe il gate) e li fa passare in
ordine di tempo da un conto solo che applica i limiti del bot. Non carica
candele, non legge Firebase, non conosce le strategie: cosi' si testa con
quattro trade sintetici e tre numeri. Chi carica i dati e stampa e'
`scripts/portafoglio_backtest.py`.

COSA MISURA e cosa no. Misura quanti trade al giorno, quante posizioni
contemporanee, quante nella stessa direzione, il PnL per giornata, il drawdown
e l'effetto di tre limiti di portafoglio, ognuno con un what-if:

  * il TETTO DI RISCHIO PER DIREZIONE (la somma del rischio aperto sui long, o
    sugli short, piu' il nuovo trade, non oltre una frazione dell'equity: e' la
    regola che il bot ha dall'8 set, `MAX_DIRECTIONAL_RISK_PCT`);
  * lo STOP GIORNALIERO di portafoglio (`tetto_giorno`, dal 24 set: persa una
    frazione dell'equity di inizio giornata, nessuna apertura fino a
    mezzanotte UTC); il bot non ce l'ha, e' un what-if;
  * il NETTO DIREZIONALE (`netto_r_max`, dal 24 set: |rischio long aperto -
    rischio short aperto| dopo l'apertura non oltre N volte il rischio
    unitario); anche questo e' solo un what-if.

Dal 24 set misura anche due cose che servono a decidere, non a limitare: il
WIN RATE CONDIZIONATO dopo k perdite di fila per strategia (se il freno di
serie ha senso) e il DIVERSIFICATION RATIO delle giornate (se il portafoglio
e' tante scommesse o una sola).

NON e' un gate: i trade in ingresso sono quelli del backtest, quindi ereditano
le sue semplificazioni (uscita a barra chiusa, costi modellati). E il rischio
per trade e' quello del bot in forma semplice — l'1% dell'equity corrente
(DEFAULT_RISK_PER_TRADE), senza le riduzioni per confidenza o volatilita' — per
una ragione precisa: qui si vuole vedere l'effetto dei LIMITI, non della size.

CONVENZIONI. Un trade e' un dict con `entry_ts` (epoch), `bars_held`,
`direction` ("long"/"short"), `symbol`, `strategy`, `pnl_pct` (sul margine,
netto costi, come `SimTrade.pnl_pct`) e `stop_pct` (distanza dello stop
dall'ingresso, frazione: `feats["stop_pct"]` del motore, dal 24 set). Il PnL in
valuta e' R * rischio, con R = pnl_pct / stop_pct: un trade fermato allo stop
vale -1R, cioe' -1% dell'equity. Senza `stop_pct` non si sa quanto valga R e
il trade si SCARTA e si conta, invece di inventare uno stop.
"""
from __future__ import annotations

import datetime as dt
import math
from collections import defaultdict

from bot.config import settings

#: rischio per trade come frazione dell'equity corrente: la stessa costante del
#: bot (bot/config.py), letta da li' per non avere due copie.
RISCHIO_PER_TRADE: float = float(getattr(settings, "DEFAULT_RISK_PER_TRADE", 0.01))

#: i motivi con cui un trade puo' essere saltato, nell'ORDINE in cui si
#: controllano. L'ordine conta per i contatori: un trade che violerebbe due
#: limiti viene attribuito al primo della lista. Si controllano prima le regole
#: "di stato" (coin gia' aperta, posizioni piene), poi quelle "di storia"
#: (cooldown, tetto per coin), e per ultimi i tre limiti di portafoglio
#: nell'ordine in cui lo script li accende (direzione, giorno, netto), cosi'
#: ogni colonna del what-if sposta solo i trade che SOLO quel limite fermerebbe.
MOTIVI = ("senza_stop", "coin_gia_aperta", "max_posizioni", "cooldown",
          "tetto_coin_giorno", "tetto_direzione", "tetto_giorno", "netto_r",
          "equity_esaurita")

#: fino a quante perdite di fila si misura il win rate condizionato
K_MAX_SERIE = 5


def limiti_default() -> dict:
    """I limiti del bot cosi' come sono configurati ADESSO, letti da settings.

    Il tetto per direzione e' `MAX_DIRECTIONAL_RISK_PCT` (bot/main.py
    `_directional_risk_blocks`, dall'8 set: 3% = tre stop pieni da 1%). Fino al
    24 set qui si leggeva `MAX_RISK_PER_DIRECTION`, una chiave doppia che il
    bot non usava e che viene tolta. 0 spegne il tetto.

    `tetto_giorno` e `netto_r_max` sono what-if che il bot NON ha: qui partono
    spenti (0) e li accende lo script, colonna per colonna."""
    return {
        "max_posizioni": int(getattr(settings, "MAX_OPEN_POSITIONS", 5)),
        "una_per_coin": True,
        "tetto_coin_giorno": float(getattr(settings, "RISK_PER_COIN_DAY", 0.015)),
        "tetto_direzione": float(getattr(settings, "MAX_DIRECTIONAL_RISK_PCT", 0.03)),
        "cooldown_ore": float(getattr(settings, "COOLDOWN_HOURS", 0.0) or 0.0),
        "rischio_per_trade": RISCHIO_PER_TRADE,
        "tetto_giorno": 0.0,
        "netto_r_max": 0.0,
    }


def _ts(v) -> float:
    """Epoch da numero o ISO. Lo stesso helper di daily_cap: una data ISO che
    diventa 0 farebbe sparire i trade in silenzio (difetto del 21 set)."""
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return dt.datetime.fromisoformat(str(v)).timestamp()
    except (TypeError, ValueError):
        return 0.0


def _giorno(ts: float) -> str:
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).date().isoformat()


def _mezzanotte(ts: float) -> float:
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0).timestamp()


def _prepara(trades: list[dict], secondi_barra: float) -> tuple[list[dict], int]:
    """Normalizza i trade e scarta quelli senza stop.

    `exit_ts` = `entry_ts` + barre tenute * secondi per barra: il motore chiude a
    barra chiusa, quindi un trade con `bars_held` 0 e' comunque vissuto almeno
    una barra (e' stato aperto e chiuso dentro la stessa). Se il trade porta gia'
    un `exit_ts`, si rispetta."""
    pronti: list[dict] = []
    scartati = 0
    for t in trades:
        entry = _ts(t.get("entry_ts"))
        try:
            stop = float(t.get("stop_pct") or 0.0)
        except (TypeError, ValueError):
            stop = 0.0
        if entry <= 0 or stop <= 0:
            scartati += 1
            continue
        exit_ts = _ts(t.get("exit_ts"))
        if exit_ts <= entry:
            barre = max(int(t.get("bars_held", 0) or 0), 1)
            exit_ts = entry + barre * float(secondi_barra)
        pronti.append({
            "entry_ts": entry, "exit_ts": exit_ts,
            "direction": str(t.get("direction") or "long").lower(),
            "symbol": str(t.get("symbol") or "?"),
            "strategy": str(t.get("strategy") or "?"),
            "pnl_pct": float(t.get("pnl_pct", 0.0) or 0.0),
            "stop_pct": stop,
        })
    # ordine di tempo, e a parita' d'istante un ordine stabile (coin, strategia):
    # due trade nello stesso istante non devono cambiare esito fra due run.
    pronti.sort(key=lambda t: (t["entry_ts"], t["symbol"], t["strategy"]))
    return pronti, scartati


def _drawdown_pct(curva: list[float]) -> float:
    """Massima caduta dal picco precedente, in percento, sulla curva dell'equity."""
    picco, peggiore = float("-inf"), 0.0
    for e in curva:
        picco = max(picco, e)
        if picco > 0:
            peggiore = max(peggiore, (picco - e) / picco * 100.0)
    return peggiore


def _std(valori: list[float]) -> float:
    """Deviazione standard di popolazione; 0 con meno di due valori."""
    n = len(valori)
    if n < 2:
        return 0.0
    media = sum(valori) / n
    return math.sqrt(sum((v - media) ** 2 for v in valori) / n)


def wr_condizionato(pronti: list[dict], k_max: int = K_MAX_SERIE) -> dict:
    """Win rate dei trade che seguono ESATTAMENTE k perdite di fila della stessa
    strategia, contro il win rate incondizionato. Dal 24 set.

    Serve a una domanda sola: il freno di serie (dopo 4 perdite la size si
    dimezza) ha un fondamento? Se dopo 4 perdite il win rate NON e' piu' basso
    di quello incondizionato, il freno costa e non protegge. Si misura sui
    trade CANDIDATI (tutti quelli che il motore ha prodotto), non solo su quelli
    aperti dal portafoglio: la serie di una strategia e' la sua, non dipende da
    quante posizioni erano libere sul conto.

    La sequenza e' per STRATEGIA (come `_strat_streak` del bot), in ordine di
    ingresso, e "perdita" e' `pnl_pct <= 0`: una vincita azzera la serie. Un
    trade che segue k perdite conta solo nel gruppo k (non anche in k-1). Il t
    approssimato e' differenza / sqrt(p(1-p)/n) con p il win rate
    incondizionato: dice se n e' abbastanza perche' la differenza sia piu' del
    rumore, non e' un test rigoroso (i trade non sono indipendenti)."""
    esiti: dict[str, list[bool]] = defaultdict(list)
    for t in pronti:                       # `pronti` e' gia' in ordine di tempo
        esiti[t["strategy"]].append(t["pnl_pct"] > 0)
    n_tot = sum(len(v) for v in esiti.values())
    vinti_tot = sum(sum(v) for v in esiti.values())
    p = vinti_tot / n_tot if n_tot else 0.0
    conteggi = {k: [0, 0] for k in range(1, k_max + 1)}   # k -> [n, vinti]
    for seq in esiti.values():
        serie = 0
        for vinto in seq:
            if 1 <= serie <= k_max:
                conteggi[serie][0] += 1
                conteggi[serie][1] += int(vinto)
            serie = 0 if vinto else serie + 1
    dopo_k: dict[str, dict] = {}
    for k, (n, vinti) in conteggi.items():
        wr = vinti / n if n else 0.0
        diff = (wr - p) * 100.0 if n else 0.0
        errore = math.sqrt(p * (1.0 - p) / n) * 100.0 if n and 0.0 < p < 1.0 else 0.0
        dopo_k[str(k)] = {
            "n": n, "wr": round(wr, 4),
            "diff_punti": round(diff, 2),
            "t": round(diff / errore, 2) if errore > 0 else 0.0,
        }
    return {"incondizionato": {"n": n_tot, "wr": round(p, 4)}, "dopo_k": dopo_k}


def diversification_ratio(pnl_giorno_portafoglio: dict[str, float],
                          pnl_giorno_per_coppia: dict[str, dict[str, float]]) -> float | None:
    """std(PnL giornaliero del portafoglio) / somma delle std per coppia, sugli
    stessi giorni. Dal 24 set.

    Vale 1 quando le coppie si muovono insieme (le giornate sommano come una
    scommessa sola: nessun beneficio dal metterle insieme) e tende a 0 quando
    si compensano. Ogni coppia vale 0 nei giorni in cui non ha chiuso nulla:
    e' il suo contributo vero a quella giornata. None se non e' definito (meno
    di due giorni, o coppie tutte piatte)."""
    giorni = sorted(pnl_giorno_portafoglio)
    if len(giorni) < 2 or not pnl_giorno_per_coppia:
        return None
    somma_std = sum(_std([serie.get(g, 0.0) for g in giorni])
                    for serie in pnl_giorno_per_coppia.values())
    if somma_std <= 0:
        return None
    return _std([pnl_giorno_portafoglio[g] for g in giorni]) / somma_std


def simula(trades: list[dict], equity0: float, limiti: dict | None = None,
           secondi_barra: float = 900.0,
           periodo: tuple[float, float] | None = None) -> dict:
    """Fa passare i trade, in ordine di ingresso, da un conto solo con i limiti.

    `limiti` sovrascrive i valori di `limiti_default()` (chiavi: max_posizioni,
    una_per_coin, tetto_coin_giorno, tetto_direzione, cooldown_ore,
    rischio_per_trade, tetto_giorno, netto_r_max). `secondi_barra` e' la durata
    di una candela (900 = 15m). `periodo` (inizio, fine) in epoch delimita i
    giorni su cui si fa la media dei trade al giorno; se manca, dal primo
    ingresso all'ultima uscita.

    Un trade si APRE se all'istante d'ingresso rispetta tutti i limiti (le
    posizioni aperte sono i trade gia' aperti con uscita dopo quell'istante);
    altrimenti e' SALTATO col primo motivo che lo ferma. L'equity si aggiorna
    alla chiusura, e i limiti in frazione (tetto per coin, per direzione,
    rischio) si leggono sull'equity di quel momento.

    I tre limiti di portafoglio, con la semantica esatta:
      * `tetto_direzione`: rischio in valuta delle aperte nello stesso verso +
        rischio del NUOVO trade > tetto * equity -> saltato. E' la regola del
        bot (`_directional_risk_blocks`): il nuovo trade si conta, e il confronto
        e' stretto, quindi con 3% entrano tre stop da 1% e non il quarto. Fino
        al 24 set qui si contavano solo le aperte, con `>=`: bloccava un trade
        prima del bot.
      * `tetto_giorno`: perdita del PORTAFOGLIO dal giorno UTC in corso (PnL
        netto delle chiusure del giorno, se negativo) >= tetto * equity di
        inizio giornata -> nessuna apertura fino a mezzanotte. `giorni_fermati`
        conta i giorni in cui ha fermato almeno un trade.
      * `netto_r_max`: |rischio long aperto - rischio short aperto| DOPO
        l'apertura > netto_r_max * rischio unitario (rischio_per_trade *
        equity) -> saltato. Con 2R si possono avere al massimo due stop pieni
        di sbilancio fra i due versi.

    Tutto e' deterministico e senza stato esterno: chiamarla quattro volte con
    quattro `limiti` diversi e' il what-if dello script."""
    lim = {**limiti_default(), **(limiti or {})}
    max_pos = int(lim.get("max_posizioni") or 0)
    una_per_coin = bool(lim.get("una_per_coin", True))
    tetto_coin = float(lim.get("tetto_coin_giorno") or 0.0)
    tetto_dir = float(lim.get("tetto_direzione") or 0.0)
    tetto_giorno = float(lim.get("tetto_giorno") or 0.0)
    netto_r_max = float(lim.get("netto_r_max") or 0.0)
    cooldown_s = float(lim.get("cooldown_ore") or 0.0) * 3600.0
    rischio_frac = float(lim.get("rischio_per_trade") or RISCHIO_PER_TRADE)

    pronti, senza_stop = _prepara(trades, secondi_barra)
    saltati: dict[str, int] = {m: 0 for m in MOTIVI}
    saltati["senza_stop"] = senza_stop
    saltati_direzione: dict[str, int] = {"long": 0, "short": 0}

    equity = float(equity0)
    aperti: list[dict] = []                 # posizioni aperte, con exit_ts e pnl
    pnl_per_giorno: dict[str, float] = defaultdict(float)
    pnl_giorno_coppia: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    perdite_coin_giorno: dict[tuple[str, str], float] = defaultdict(float)
    cooldown_fino: dict[str, float] = {}    # coin -> epoch in cui puo' riaprire
    equity_a_fine_giorno: dict[str, float] = {}
    equity_inizio_giorno: dict[str, float] = {}   # per il tetto giornaliero
    giorni_fermati: set[str] = set()
    curva_chiusure: list[float] = [equity]
    per_direzione = {"long": {"n": 0, "pnl": 0.0}, "short": {"n": 0, "pnl": 0.0}}
    aperti_per_giorno: dict[str, int] = defaultdict(int)
    contemporanee: list[int] = []           # posizioni aperte a ogni apertura (compresa)
    stessa_dir: list[int] = []              # di cui nella stessa direzione (compresa)
    quote_stessa_dir: list[float] = []      # fra le ALTRE aperte, quota nella stessa direzione
    n_aperti = 0
    ultima_uscita = 0.0

    def _chiudi_fino_a(t: float) -> None:
        """Chiude, in ordine di uscita, le posizioni uscite entro `t`."""
        nonlocal equity
        aperti.sort(key=lambda p: p["exit_ts"])
        while aperti and aperti[0]["exit_ts"] <= t:
            p = aperti.pop(0)
            giorno = _giorno(p["exit_ts"])
            # l'equity di inizio giornata e' quella PRIMA della prima chiusura
            # del giorno: e' la base su cui si legge il tetto giornaliero.
            equity_inizio_giorno.setdefault(giorno, equity)
            equity += p["pnl"]
            pnl_per_giorno[giorno] += p["pnl"]
            pnl_giorno_coppia[f"{p['symbol']}|{p['strategy']}"][giorno] += p["pnl"]
            equity_a_fine_giorno[giorno] = equity
            curva_chiusure.append(equity)
            per_direzione[p["direction"]]["pnl"] += p["pnl"]
            if p["pnl"] < 0:
                perdite_coin_giorno[(p["symbol"], giorno)] += -p["pnl"]
                if cooldown_s > 0:
                    cooldown_fino[p["symbol"]] = max(
                        cooldown_fino.get(p["symbol"], 0.0), p["exit_ts"] + cooldown_s)

    for t in pronti:
        ora = t["entry_ts"]
        _chiudi_fino_a(ora)
        direzione = t["direction"] if t["direction"] in per_direzione else "long"
        giorno = _giorno(ora)
        # nessuna chiusura ancora oggi: l'equity di inizio giornata e' questa
        equity_inizio_giorno.setdefault(giorno, equity)
        rischio = equity * rischio_frac      # il rischio del NUOVO trade, in valuta
        rischio_long = sum(p["rischio"] for p in aperti if p["direction"] == "long")
        rischio_short = sum(p["rischio"] for p in aperti if p["direction"] == "short")

        motivo = None
        if equity <= 0:
            motivo = "equity_esaurita"
        elif una_per_coin and any(p["symbol"] == t["symbol"] for p in aperti):
            motivo = "coin_gia_aperta"
        elif max_pos > 0 and len(aperti) >= max_pos:
            motivo = "max_posizioni"
        elif cooldown_s > 0 and cooldown_fino.get(t["symbol"], 0.0) > ora:
            motivo = "cooldown"
        elif tetto_coin > 0 and (
                perdite_coin_giorno.get((t["symbol"], giorno), 0.0)
                >= tetto_coin * equity):
            motivo = "tetto_coin_giorno"
        elif tetto_dir > 0 and (
                (rischio_long if direzione == "long" else rischio_short) + rischio
                > tetto_dir * equity + 1e-9):
            # la regola del bot: aperte nello stesso verso + il nuovo, confronto
            # stretto. Il margine di 1e-9 e' solo contro l'aritmetica binaria:
            # tre volte l'1% deve valere esattamente il 3%, non un soffio di piu'.
            motivo = "tetto_direzione"
            saltati_direzione[direzione] += 1
        elif tetto_giorno > 0 and (
                -pnl_per_giorno.get(giorno, 0.0)
                >= tetto_giorno * equity_inizio_giorno[giorno] - 1e-9):
            motivo = "tetto_giorno"
            giorni_fermati.add(giorno)
        elif netto_r_max > 0:
            netto = (rischio_long - rischio_short
                     + (rischio if direzione == "long" else -rischio))
            if abs(netto) > netto_r_max * rischio + 1e-9:
                motivo = "netto_r"

        if motivo:
            saltati[motivo] += 1
            continue

        r = t["pnl_pct"] / t["stop_pct"]
        pos = {**t, "direction": direzione, "rischio": rischio, "r": r, "pnl": r * rischio}
        aperti.append(pos)
        n_aperti += 1
        per_direzione[direzione]["n"] += 1
        aperti_per_giorno[giorno] += 1
        contemporanee.append(len(aperti))
        stessi = sum(1 for p in aperti if p["direction"] == direzione)
        stessa_dir.append(stessi)
        altre = len(aperti) - 1
        if altre:
            quote_stessa_dir.append((stessi - 1) / altre)
        ultima_uscita = max(ultima_uscita, pos["exit_ts"])

    # chiude quello che resta aperto alla fine: il PnL di un trade che il motore
    # ha gia' chiuso non si butta via solo perche' e' l'ultimo.
    _chiudi_fino_a(float("inf"))

    # ---- i giorni: trade al giorno e curva campionata a fine giornata --------
    if periodo:
        inizio_g, fine_g = _mezzanotte(float(periodo[0])), _mezzanotte(float(periodo[1]))
    elif pronti:
        inizio_g = _mezzanotte(pronti[0]["entry_ts"])
        fine_g = _mezzanotte(max(ultima_uscita, pronti[-1]["entry_ts"]))
    else:
        inizio_g = fine_g = 0.0
    giorni: list[str] = []
    g = inizio_g
    while inizio_g and g <= fine_g:
        giorni.append(_giorno(g))
        g += 86400.0
    conteggi = [aperti_per_giorno.get(d, 0) for d in giorni]
    # la curva porta l'equity a FINE di ogni giornata del periodo, anche nei
    # giorni senza chiusure (si trascina l'ultima), cosi' si disegna senza buchi.
    curva: list[tuple[float, float]] = []
    eq = float(equity0)
    for d in giorni:
        eq = equity_a_fine_giorno.get(d, eq)
        fine_giorno = dt.datetime.fromisoformat(d).replace(
            tzinfo=dt.timezone.utc).timestamp() + 86400.0 - 1.0
        curva.append((fine_giorno, round(eq, 2)))

    dr = diversification_ratio(dict(pnl_per_giorno), pnl_giorno_coppia)

    return {
        "equity_finale": round(equity, 2),
        "pnl_totale": round(equity - float(equity0), 2),
        "n_candidati": len(trades),
        "n_aperti": n_aperti,
        "saltati": saltati,
        "saltati_direzione": saltati_direzione,
        "giorni_fermati": len(giorni_fermati),
        "trade_al_giorno": {
            "min": min(conteggi) if conteggi else 0,
            "media": (sum(conteggi) / len(conteggi)) if conteggi else 0.0,
            "max": max(conteggi) if conteggi else 0,
        },
        "posizioni_contemporanee": {
            "max": max(contemporanee) if contemporanee else 0,
            "media": (sum(contemporanee) / len(contemporanee)) if contemporanee else 0.0,
        },
        "stessa_direzione_max": max(stessa_dir) if stessa_dir else 0,
        "quota_contemporanee_stessa_direzione": (
            sum(quote_stessa_dir) / len(quote_stessa_dir)) if quote_stessa_dir else 0.0,
        "pnl_per_giorno": {d: round(v, 2) for d, v in sorted(pnl_per_giorno.items())},
        "giorni_utile": sum(1 for v in pnl_per_giorno.values() if v > 0),
        "giorni_perdita": sum(1 for v in pnl_per_giorno.values() if v < 0),
        "max_drawdown_pct": round(_drawdown_pct(curva_chiusure), 2),
        "per_direzione": {k: {"n": v["n"], "pnl": round(v["pnl"], 2)}
                          for k, v in per_direzione.items()},
        "wr_condizionato": wr_condizionato(pronti),
        "diversification_ratio": round(dr, 3) if dr is not None else None,
        "n_coppie_aperte": len(pnl_giorno_coppia),
        "curva": curva,
        "limiti": lim,
    }
