"""L'OMBRA DEI SEGNALI RIFIUTATI (26 set 2026, backlog H5 -> J6).

IL BUCO CHE CHIUDE. Un segnale che il bot non apre (cooldown, tetto per coin,
peso sotto soglia, posizione gia' aperta, esplorative al tetto, veto di regime,
margine, rischio direzionale, stop troppo largo) lasciava una riga «[rifiuto]»
nel log e un contatore in RAM: nessuno sapeva se AVREBBE VINTO. L'unica misura
che c'era (ops 0211, 24 set: 9 segnali non aperti con PF 1,23 contro 15 aperti
con PF 0,50) era troppo piccola per decidere e non si aggiornava da sola. Senza
questo numero i freni si tarano a intuito, e il proprietario ha chiesto il
contrario: «un numero va con la sua fonte».

COME FUNZIONA, in tre pezzi:
  * `registra`: al momento del rifiuto scrive un documento in Firestore
    `segnali_rifiutati/{YYYYMMDDHHMM}_{coin}_{strategia}` con entry, stop,
    target, scala, motivo (e la sua classe), stato «in_attesa». La chiave e'
    l'apertura della candela del timeframe del segnale: lo stesso segnale
    rifiutato due volte nello stesso giro (o dallo stesso giro rilanciato) non
    fa due documenti.
  * `valuta_pendenti`: ogni giro del bot (chi chiama passa la funzione che
    scarica le candele: nel bot e' `price.get_candles`, la stessa fonte di
    `evaluate_pending_trailing`) prende i segnali in attesa, scarica le candele
    SUCCESSIVE e li simula con le stesse regole d'uscita del motore di backtest
    (`simula_segnale`): esito, R netto di niente, mfe/mae in R, barre. Chi non
    ha ancora abbastanza candele aspetta; chi e' troppo vecchio per averle
    (finestra passata) diventa «scaduto» e si conta a parte.
  * `riassunto`: per classe di motivo, quanti, quanti valutati, R medio, quota
    di vincenti, mfe mediana. Il confronto con gli APERTI dello stesso periodo
    lo fa `scripts/rifiutati_report.py`, che legge i trade.

FAIL-OPEN OVUNQUE: niente qui puo' fermare un ciclo del bot. Ogni funzione
prende i suoi errori, stampa al massimo una riga, e torna None/0. E' una MISURA,
non una decisione: nessun freno legge questi documenti.

DIFFERENZE COL MOTORE (backtesting/engine.py::run_strategy), scritte perche' i
numeri non siano confrontati alla cieca con quelli del gate:
  * niente fee, slippage ne' funding: `pnl_r` e' prezzo puro. Gli aperti, nel
    report, sono NETTI di costi: la differenza va tenuta a mente (costo di
    andata e ritorno ~0,1-0,2 R su stop del 2%);
  * l'ingresso e' il prezzo del segnale (chiusura della candela che l'ha
    generato), come fa il bot che esegue al mark subito dopo il confine; il
    motore, con BACKTEST_ENTRY_NEXT_OPEN, entra all'apertura della barra dopo e
    trasla stop e target. La prima barra simulata e' la stessa in tutti e due;
  * il keep del profit-lock e' quello globale (settings.PROFIT_LOCK_KEEP) se chi
    registra non ne passa uno; il motore e il bot usano quello scelto dal gate
    per coppia. Il break-even dopo il TP1 segue il default globale;
  * un segnale senza stop suggerito prende lo stesso ripiego del motore
    (2% dal prezzo), e senza target il 4%.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from statistics import mean, median, stdev
from typing import Callable, Optional

from bot.config import settings
from bot.core.firebase_client import kw_chi
from bot.execution.exit_logic import (breakeven_after_tp1, ladder_multiples, lock_anchor,
                                      locked_stop, scale_fills, scale_ladder)

#: la collection Firestore. Un documento per segnale rifiutato.
COLLECTION = "segnali_rifiutati"

#: stati del documento: registrato e in attesa di candele -> valutato (esito
#: scritto) oppure scaduto (troppo vecchio per scaricare le candele giuste).
IN_ATTESA, VALUTATO, SCADUTO = "in_attesa", "valutato", "scaduto"

#: esiti possibili di `simula_segnale`
ESITI = ("tp", "stop", "trailing", "orizzonte")

#: barre dell'orizzonte: le stesse 96 del motore (backtesting.engine.HORIZON_BARS,
#: non importato per non tirarsi dietro tutto il motore dentro il bot)
ORIZZONTE_BARRE = 96

_TF_SECS = {"1m": 60, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600,
            "4h": 14400, "1d": 86400}

#: etichetta nel contatore delle letture Firestore
CHI = "rifiutati"
#: quanti documenti al massimo legge un giro di `valuta_pendenti` (tetto alle
#: letture: la finestra a 15m tiene ~30 documenti al giorno)
MAX_LETTURE_GIRO = 200
#: un pendente piu' vecchio di cosi' diventa «scaduto» nella passata giornaliera
#: (`chiudi_scaduti`): nessun documento resta «in_attesa» per sempre
SCADENZA_S = 5 * 86400
#: i timeframe VISTI fra i pendenti negli ultimi giri: la finestra di lettura
#: si dimensiona sul piu' lungo fra questi e quello del bot
_TF_VISTI: set[str] = set()


def tf_secondi(timeframe: Optional[str]) -> int:
    """Secondi di una candela del timeframe; sconosciuto o vuoto -> quello del bot."""
    return _TF_SECS.get(str(timeframe or ""), 0) or _TF_SECS.get(settings.ORCHESTRATOR_TIMEFRAME, 900)


def candela_di(ts: float, timeframe: Optional[str]) -> float:
    """L'apertura (epoch) della candela del timeframe in cui cade `ts`.

    Il bot decide subito DOPO la chiusura di una candela, quindi `ts` cade
    nella candela successiva: e' quella in cui il trade sarebbe entrato, e la
    prima che `simula_segnale` percorre (come la barra i+1 del motore)."""
    secs = tf_secondi(timeframe)
    return float(int(ts) // secs * secs)


def chiave(ts: float, symbol: str, strategy: str, timeframe: Optional[str] = None) -> str:
    """L'id del documento: `{YYYYMMDDHHMM}_{coin}_{strategia}` sull'apertura
    della candela. Idempotente per (coin, strategia, candela)."""
    quando = datetime.fromtimestamp(candela_di(ts, timeframe), tz=timezone.utc)
    pulito = str(strategy or "").replace("/", "_").replace(" ", "_")
    return f"{quando.strftime('%Y%m%d%H%M')}_{symbol}_{pulito}"


def _num(v) -> Optional[float]:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f else None      # NaN cade qui


# --------------------------------------------------------------------------- #
# 1. registrare                                                                #
# --------------------------------------------------------------------------- #
def registra(fb, *, symbol: str, strategy: str, direction, motivo: str,
             timeframe: Optional[str], entry, stop, target, scale_r_mults,
             feats: Optional[dict], selector_p, now: float,
             esplorativa: bool = False) -> Optional[str]:
    """Scrive il documento del rifiuto. Ritorna l'id, o None se non ha potuto.

    Non solleva MAI: e' chiamata dentro il ciclo di decisione. Se il documento
    esiste gia' (stesso segnale nello stesso giro) non lo riscrive, cosi' un
    esito gia' valutato non torna «in_attesa». Un ingresso non numerico o <= 0
    non si registra: senza entry non c'e' R e non c'e' niente da misurare."""
    try:
        from bot.orchestrator.orchestrator import motivo_rifiuto   # evita l'import circolare
        entry_f = _num(entry)
        if not entry_f or entry_f <= 0 or fb is None:
            return None
        lato = str(getattr(direction, "value", direction) or "").lower()
        long = lato.endswith("long")
        stop_f = _num(stop)
        if stop_f is None or stop_f <= 0:
            stop_f = entry_f * (0.98 if long else 1.02)      # ripiego del motore
        target_f = _num(target)
        if target_f is None or target_f <= 0:
            target_f = entry_f * (1.04 if long else 0.96)
        tf = str(timeframe or settings.ORCHESTRATOR_TIMEFRAME)
        doc_id = chiave(now, symbol, strategy, tf)
        if fb.get_doc(COLLECTION, doc_id, **kw_chi(fb, CHI)):
            return doc_id
        try:
            scala = [float(x) for x in (scale_r_mults or [])] or None
        except (TypeError, ValueError):
            scala = None
        doc = {
            "id": doc_id, "symbol": symbol, "strategy": strategy,
            "direction": "long" if long else "short",
            "motivo": str(motivo or "")[:160], "motivo_classe": motivo_rifiuto(motivo),
            "timeframe": tf, "entry": entry_f, "stop": stop_f, "target": target_f,
            "scale_r_mults": scala,
            "feats": feats if isinstance(feats, dict) else None,
            "selector_p": _num(selector_p),
            "esplorativa": bool(esplorativa),
            "ts": float(now), "ts_candela": candela_di(now, tf),
            "stato": IN_ATTESA,
        }
        fb.set_doc(COLLECTION, doc_id, doc)
        return doc_id
    except Exception as exc:  # noqa: BLE001
        print(f"[rifiutati] registrazione saltata ({exc})")
        return None


def registra_decisione(fb, decision, motivo: str, *, entry, now: float, adaptation=None,
                       feats: Optional[dict] = None, selector_p=None) -> Optional[str]:
    """`registra` a partire da una OrchestratorDecision: e' la forma comoda per
    `TradingBot._try_open`, dove il rifiuto arriva dopo l'orchestratore.
    Timeframe e scala vengono dall'adattamento (come all'apertura), stop e
    target dalla decisione. Fail-open come `registra`."""
    try:
        symbol, strategy = decision.asset, decision.strategy
        tf = None
        params: dict = {}
        if adaptation is not None:
            try:
                tf = adaptation.timeframe_for(strategy)
                params = (adaptation.params_for(symbol) or {}).get(strategy, {}) or {}
            except Exception:  # noqa: BLE001
                tf, params = None, {}
        return registra(fb, symbol=symbol, strategy=strategy, direction=decision.direction,
                        motivo=motivo, timeframe=tf or settings.ORCHESTRATOR_TIMEFRAME,
                        entry=entry, stop=getattr(decision, "suggested_stop", None),
                        target=getattr(decision, "suggested_target", None),
                        scale_r_mults=ladder_multiples(params), feats=feats,
                        selector_p=selector_p, now=now,
                        esplorativa=bool(getattr(decision, "esplorativa", False)))
    except Exception as exc:  # noqa: BLE001
        print(f"[rifiutati] registrazione saltata ({exc})")
        return None


# --------------------------------------------------------------------------- #
# 2. simulare                                                                  #
# --------------------------------------------------------------------------- #
def simula_segnale(candles, direction, entry: float, stop: float, target=None,
                   r_mults=None, keep: Optional[float] = None,
                   breakeven: Optional[bool] = None,
                   orizzonte: int = ORIZZONTE_BARRE) -> Optional[dict]:
    """Cosa sarebbe successo a un segnale, sulle candele SUCCESSIVE. Pura.

    Stesse regole d'uscita di `Backtester.run_strategy` (vedi le differenze in
    testa al modulo): con scale-out attivo la scala di TP a multipli di R
    (`r_mults` o il default globale, quote SCALE_OUT_FRACTIONS), protezione del
    profitto ancorata al primo gradino e break-even dopo il TP1; senza, TP unico
    a `target` e protezione ancorata al TP. In una candela lo stop si controlla
    PRIMA del TP (prudente, come il motore).

    Ritorna None se R non e' calcolabile. Altrimenti un dict con:
      esito   «tp» / «stop» / «trailing» (stop alzato dal lock) / «orizzonte»
              (ancora aperto dopo `orizzonte` barre: chiuso al close) — oppure
              None se le candele finiscono prima: ancora in attesa;
      pnl_r   R realizzato (prezzo puro, fette pesate con le quote);
      mfe_r / mae_r  massima escursione a favore / contro, in R, sulle barre
              percorse fino all'uscita;
      barre   quante candele ha percorso."""
    entry_f, stop_f = _num(entry), _num(stop)
    if not entry_f or stop_f is None or entry_f <= 0:
        return None
    R = abs(entry_f - stop_f)
    if R <= 0:
        return None
    lato = str(getattr(direction, "value", direction) or "").lower()
    long = lato.endswith("long")
    target_f = _num(target)
    if target_f is None or target_f <= 0:
        target_f = entry_f * (1.04 if long else 0.96)
    if breakeven is None:
        breakeven = breakeven_after_tp1(None)
    ladder = (scale_ladder(entry_f, stop_f, long, r_mults=r_mults)
              if settings.SCALE_OUT_ENABLED else [])

    def guadagno(prezzo: float) -> float:
        return (prezzo - entry_f) if long else (entry_f - prezzo)

    best_fav = entry_f
    mfe = entry_f
    mae = entry_f
    stop_base = stop_f
    anchor = lock_anchor(ladder) if ladder else target_f
    stage, taken, realizzato = 0, 0.0, 0.0
    esito: Optional[str] = None
    barre = 0
    ultimo_close = entry_f
    for c in list(candles or [])[:max(1, int(orizzonte))]:
        barre += 1
        eff_stop = locked_stop(entry_f, anchor, long, best_fav, stop_base, keep=keep)
        trailing = eff_stop != stop_base
        mfe = max(mfe, c.high) if long else min(mfe, c.low)
        mae = min(mae, c.low) if long else max(mae, c.high)
        stop_hit = (c.low <= eff_stop) if long else (c.high >= eff_stop)
        if stop_hit:
            realizzato += (1.0 - taken) * guadagno(eff_stop)
            esito = "trailing" if trailing else "stop"
            break
        if ladder:
            stage, fills = scale_fills(ladder, stage, long, c.high, c.low)
            for price, frac in fills:
                realizzato += frac * guadagno(price)
                taken += frac
            if fills and breakeven:
                stop_base = entry_f          # break-even sul residuo dopo il TP1
            if stage >= len(ladder):
                esito = "tp"
                break
        else:
            tp_hit = (c.high >= target_f) if long else (c.low <= target_f)
            if tp_hit:
                realizzato += guadagno(target_f)
                esito = "tp"
                break
        best_fav = max(best_fav, c.high) if long else min(best_fav, c.low)
        ultimo_close = c.close
    if esito is None and barre >= int(orizzonte):
        realizzato += (1.0 - taken) * guadagno(ultimo_close)
        esito = "orizzonte"
    return {
        "esito": esito,
        "pnl_r": round(realizzato / R, 3) if esito else None,
        "mfe_r": round(max(0.0, guadagno(mfe)) / R, 3),
        "mae_r": round(max(0.0, -guadagno(mae)) / R, 3),
        "barre": barre,
    }


# --------------------------------------------------------------------------- #
# 3. valutare i pendenti                                                       #
# --------------------------------------------------------------------------- #
def _finestra_pendenti_s(orizzonte_barre: int, margine_barre: int,
                         timeframes=None) -> float:
    """Quanto indietro leggere i documenti: (orizzonte + margine + 2) barre del
    timeframe PIU' LUNGO fra quelli dei segnali (`timeframes`, piu' quello del
    bot e quelli visti nei giri precedenti). A 15m sono 106 barre, ~26 ore; a
    1h ~106 ore. Oltre, un pendente e' per forza gia' valutato o scaduto (o lo
    chiude la passata giornaliera `chiudi_scaduti`).

    Fino al 28 set 2026 la finestra era dimensionata sul 4h piu' un giorno
    (~18 giorni) per QUALUNQUE segnale: a ogni candela il bot rileggeva tutti i
    documenti di 17 giorni (~30 al giorno, ~5.300 letture al giorno il 28 set,
    ~24.000 una settimana dopo), per valutarne una manciata. Le 2 barre in piu'
    sono quelle in cui `valuta_pendenti` scarica ancora le candele di un
    segnale al limite."""
    tfs = {settings.ORCHESTRATOR_TIMEFRAME} | set(timeframes or ()) | set(_TF_VISTI)
    secs = max(tf_secondi(tf) for tf in tfs)
    return (orizzonte_barre + margine_barre + 2) * secs


def valuta_pendenti(fb, candele_fn: Callable, now: float,
                    orizzonte_barre: int = ORIZZONTE_BARRE, margine_barre: int = 8,
                    max_per_giro: int = 20, timeframes=None,
                    max_letture: int = MAX_LETTURE_GIRO) -> int:
    """Valuta i segnali «in_attesa»: scarica le candele, simula, scrive l'esito.

    `candele_fn(symbol, timeframe, limit)` ritorna le ULTIME `limit` candele
    (oggetti con open_time/high/low/close), come `PriceAgent.get_candles`.
    Un segnale si guarda solo se la sua candela d'ingresso e' chiusa da almeno
    2 barre; si usano solo le candele CHIUSE da `ts_candela` in poi. Se le
    candele scaricate non partono dalla candela d'ingresso (segnale piu' vecchio
    del limite, o buco) il segnale aspetta, e oltre orizzonte + margine barre
    diventa «scaduto». `max_per_giro` limita le chiamate a Binance per giro;
    `max_letture` i documenti letti da Firestore (i piu' recenti della
    finestra); `timeframes` sono i timeframe in uso oltre a quello del bot (la
    finestra si dimensiona sul piu' lungo). Ritorna quanti documenti ha
    aggiornato (valutati + scaduti). Fail-open."""
    try:
        finestra = _finestra_pendenti_s(orizzonte_barre, margine_barre, timeframes)
        docs = fb.query_collection(COLLECTION, order_by="ts", min_value=now - finestra,
                                  limit=max(1, int(max_letture)), **kw_chi(fb, CHI))
    except Exception as exc:  # noqa: BLE001
        print(f"[rifiutati] lettura pendenti saltata ({exc})")
        return 0
    pendenti = sorted((d for d in (docs or []) if isinstance(d, dict) and d.get("stato") == IN_ATTESA),
                      key=lambda d: float(d.get("ts") or 0))
    for d in pendenti:
        if d.get("timeframe"):
            _TF_VISTI.add(str(d["timeframe"]))
    chiamate, aggiornati = 0, 0
    for d in pendenti:
        if chiamate >= max_per_giro:
            break
        try:
            tf = str(d.get("timeframe") or settings.ORCHESTRATOR_TIMEFRAME)
            secs = tf_secondi(tf)
            ts_c = _num(d.get("ts_candela"))
            if ts_c is None:
                ts_c = candela_di(float(d.get("ts") or 0), tf)
            eta_barre = (now - ts_c) / secs
            if eta_barre < 2:
                continue
            scaduto = eta_barre > orizzonte_barre + margine_barre
            doc_id = d.get("id") or chiave(float(d.get("ts") or ts_c), d.get("symbol", ""),
                                            d.get("strategy", ""), tf)
            candles = []
            if not scaduto or eta_barre <= orizzonte_barre + margine_barre + 2:
                chiamate += 1
                try:
                    candles = candele_fn(d.get("symbol", ""), tf, orizzonte_barre + margine_barre + 2) or []
                except Exception as exc:  # noqa: BLE001
                    print(f"[rifiutati] candele {d.get('symbol')} {tf} non lette ({exc})")
                    candles = []
            dopo = [c for c in candles
                    if c.open_time.timestamp() >= ts_c and c.open_time.timestamp() + secs <= now]
            # la prima candela dev'essere quella d'ingresso: se manca, il tragitto
            # simulato partirebbe da un altro punto e il numero sarebbe inventato
            if dopo and dopo[0].open_time.timestamp() >= ts_c + secs:
                dopo = []
            res = simula_segnale(dopo, d.get("direction"), d.get("entry"), d.get("stop"),
                                 d.get("target"), r_mults=d.get("scale_r_mults"),
                                 orizzonte=orizzonte_barre) if dopo else None
            if res is None and not scaduto:
                if not dopo:
                    continue          # candele non ancora disponibili: si riprova
                # R non calcolabile (entry/stop rotti): non si valutera' mai
                scaduto = True
            if res is not None and res.get("esito"):
                d.update({"stato": VALUTATO, "esito": res["esito"], "pnl_r": res["pnl_r"],
                          "mfe_r": res["mfe_r"], "mae_r": res["mae_r"], "barre": res["barre"],
                          "valutato_at": float(now)})
            elif scaduto:
                d.update({"stato": SCADUTO, "valutato_at": float(now),
                          "barre": (res or {}).get("barre", 0)})
            else:
                continue              # candele ancora insufficienti: aspetta
            d["id"] = doc_id
            fb.set_doc(COLLECTION, doc_id, d)
            aggiornati += 1
        except Exception as exc:  # noqa: BLE001
            print(f"[rifiutati] valutazione saltata per {d.get('id')} ({exc})")
            continue
    if aggiornati:
        print(f"[rifiutati] {aggiornati} segnali rifiutati valutati")
    return aggiornati


def chiudi_scaduti(fb, now: float, scadenza_s: float = SCADENZA_S,
                   fetta_s: float = 3 * 86400, max_docs: int = 200) -> int:
    """La passata GIORNALIERA (28 set 2026): segna «scaduto» ogni documento ancora
    «in_attesa» piu' vecchio di `scadenza_s` (5 giorni). E' la rete sotto la
    finestra di `valuta_pendenti`: un segnale a un timeframe che la finestra
    non copriva (o registrato mentre il bot era giu') non resta in attesa per
    sempre, e `riassunto` lo conta fra gli scaduti invece che fra i pendenti.

    Legge SOLO la fetta fra `scadenza_s` e `scadenza_s + fetta_s` (dal 5° all'8°
    giorno, i piu' recenti prima, al massimo `max_docs`): girando ogni giorno,
    ogni documento passa di qui una volta sola, con tre giorni di margine per
    i giorni saltati. Costo: ~30 documenti al giorno di rifiuti = ~90 letture
    al giorno. Fail-open, ritorna quanti ha chiuso."""
    try:
        docs = fb.query_collection(COLLECTION, order_by="ts",
                                  min_value=now - scadenza_s - fetta_s,
                                  max_value=now - scadenza_s, limit=max(1, int(max_docs)),
                                  **kw_chi(fb, CHI)) or []
    except Exception as exc:  # noqa: BLE001
        print(f"[rifiutati] passata degli scaduti saltata ({exc})")
        return 0
    chiusi = 0
    for d in docs:
        if not isinstance(d, dict) or d.get("stato") != IN_ATTESA:
            continue
        try:
            tf = str(d.get("timeframe") or settings.ORCHESTRATOR_TIMEFRAME)
            doc_id = d.get("id") or chiave(float(d.get("ts") or 0), d.get("symbol", ""),
                                            d.get("strategy", ""), tf)
            d.update({"stato": SCADUTO, "valutato_at": float(now), "barre": 0,
                      "scaduto_da": "passata_giornaliera"})
            d["id"] = doc_id
            fb.set_doc(COLLECTION, doc_id, d)
            chiusi += 1
        except Exception as exc:  # noqa: BLE001
            print(f"[rifiutati] scadenza saltata per {d.get('id')} ({exc})")
    if chiusi:
        print(f"[rifiutati] {chiusi} segnali in attesa da piu' di "
              f"{int(scadenza_s / 86400)} giorni segnati scaduti")
    return chiusi


# --------------------------------------------------------------------------- #
# 4. riassumere                                                                #
# --------------------------------------------------------------------------- #
def riassunto(fb, giorni: int = 30, now: Optional[float] = None) -> dict:
    """Per classe di motivo: n, valutati, scaduti, in attesa, pnl_r medio,
    quota di vincenti (pnl_r > 0 fra i valutati), mfe_r mediana, esiti.
    Un dict vuoto di motivi se non c'e' niente (mai un'eccezione).

    1 ott 2026 (J6), due campi in piu', letti solo da scripts/rifiutati_report.py:
      * `primo_ts`: l'istante del primo rifiutato registrato nella finestra
        (None se non ce n'e'). Il report prende gli aperti da qui, cosi' i due
        gruppi coprono lo stesso periodo;
      * per motivo, `pnl_r_dev`: la deviazione standard dei pnl_r valutati
        (None sotto i 2), per il margine che il report stampa come informazione.
    Cosa registra il bot non cambia, e non si legge niente in piu'."""
    now = time.time() if now is None else now
    dal = now - giorni * 86400
    try:
        docs = fb.query_collection(COLLECTION, order_by="ts", min_value=dal,
                                  **kw_chi(fb, CHI)) or []
    except Exception as exc:  # noqa: BLE001
        print(f"[rifiutati] riassunto saltato ({exc})")
        docs = []
    per_motivo: dict[str, dict] = {}
    primo_ts: Optional[float] = None
    for d in docs:
        if not isinstance(d, dict):
            continue
        ts = _num(d.get("ts"))
        if ts is not None and (primo_ts is None or ts < primo_ts):
            primo_ts = ts
        m = str(d.get("motivo_classe") or "altro")
        r = per_motivo.setdefault(m, {"n": 0, "valutati": 0, "scaduti": 0, "in_attesa": 0,
                                      "_pnl": [], "_mfe": [], "esiti": {}})
        r["n"] += 1
        stato = d.get("stato")
        if stato == VALUTATO:
            r["valutati"] += 1
            p, mf = _num(d.get("pnl_r")), _num(d.get("mfe_r"))
            if p is not None:
                r["_pnl"].append(p)
            if mf is not None:
                r["_mfe"].append(mf)
            e = str(d.get("esito") or "?")
            r["esiti"][e] = r["esiti"].get(e, 0) + 1
        elif stato == SCADUTO:
            r["scaduti"] += 1
        else:
            r["in_attesa"] += 1
    out: dict[str, dict] = {}
    for m, r in per_motivo.items():
        pnl, mfe = r.pop("_pnl"), r.pop("_mfe")
        r["pnl_r_medio"] = round(mean(pnl), 3) if pnl else None
        r["pnl_r_dev"] = round(stdev(pnl), 4) if len(pnl) >= 2 else None
        r["quota_vincenti"] = round(sum(1 for p in pnl if p > 0) / len(pnl), 3) if pnl else None
        r["mfe_r_mediana"] = round(median(mfe), 3) if mfe else None
        out[m] = r
    return {"dal": dal, "giorni": giorni, "totale": len(docs), "per_motivo": out,
            "primo_ts": primo_ts}
