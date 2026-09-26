"""
REFERTI AGGREGATI — dai singoli post_mortem alle IPOTESI per il gate.

IL PROBLEMA CHE RISOLVE
Dal 23 set 2026 ogni trade chiuso porta un referto (`post_mortem` in
bot/risk/setup_check.py): classe della morte (ingresso / uscita / protezione),
stop largo, lock mai armato, controtrend. Presi uno alla volta sono aneddoti:
«stop largo» x1 vale un'occhiata, x4 sulla stessa strategia vale una regola.
Finora li contava a mano `scripts/trade_stats.py`; nessuno li leggeva a macchina.
Il proprietario, dopo 8 giorni di paper con 6 chiusi in perdita, ha chiesto che
il sistema «impari e si adatti tutti i giorni»: questo modulo e' il primo pezzo.

IL RUOLO CORRETTO: IL PAPER PROPONE, IL GATE DECIDE (backlog F1 / B8)
Il paper e' l'unico dato mai visto dalla selezione. Se qui si ritarassero le
soglie d'ingresso sui referti, il paper diventerebbe training set — lo stesso
difetto rimosso dal gate con l'holdout (BIRBUSDT). Percio' questo modulo produce
solo IPOTESI leggibili («gen_x: solo_long — short 4/4 persi»), con regole
DICHIARATE PRIMA nelle costanti qui sotto e mai tarate sui risultati visti. Le
ipotesi finiscono su Firestore `learning/referti`; la discovery le legge e le
prova come VARIANTI sulla storia, nel gate. Se la storia le conferma entrano,
altrimenti muoiono li'. Il paper non cambia un parametro da solo.

LE CINQUE IPOTESI (una per tipo, per strategia)
  * solo_long  / solo_short: una direzione ha PERSO almeno MIN_CAMPIONE trade
    e non ne ha mai vinto uno (i pareggi non contano) -> variante che la spegne.
  * conferma_trend: le perdite sono controtrend o «mai andate a favore»
    (classe ingresso) e la strategia non ha vinto niente -> variante con
    conferma del trend all'ingresso.
  * stop_stretto: MIN_STOP_LARGO perdite con stop oltre MAX_STOP_PCT -> variante
    con stop piu' stretto (il caso 0,07022/0,0595 del 23 set, -15,3%).
  * scala_stretta (25 set 2026, backlog I4): MIN_SCALA_STRETTA perdite di classe
    «uscita» — il prezzo e' andato a favore ma e' morto SOTTO il primo gradino
    della scala dei TP. Il numero che l'ha fatta nascere: 20 stop su 32 erano
    trade andati a favore (mfe mediana ~0,7 R) con il primo gradino a 1,5-2 R.
    Non produce una variante della spec: dice alla discovery di RIGIUDICARE la
    strategia nel gate con in piu' la scala ricavata dai SUOI mfe
    (`scale_per_strategia` in scripts/discover_strategies.py). Sceglie sempre il
    gate sulla storia; il paper indica solo dove guardare.

LA SESTA IPOTESI: LE CONDIZIONI D'INGRESSO (26 set 2026, backlog I4ter)
  * ingresso_<variabile> (adx, vol_ratio, atr_pct, rsi): le perdite «mai andate a
    favore» (classe ingresso) di una strategia sono nate in una condizione
    riconoscibile — ADX basso, volume sotto la media, volatilita' alta, RSI nel
    mezzo — e i suoi trade VINTI no. Il dato viene da `feats_at_entry` (dal 25
    set su ogni trade) o, per i trade piu' vecchi, da `indicators_at_entry`
    con le stesse formule del gate (`variabili_ingresso_del_trade`). Regola:
    almeno MIN_INGRESSO perdite d'ingresso con la variabile nota, almeno il
    QUOTA_INGRESSO di esse dallo stesso lato della soglia DICHIARATA qui sotto,
    e la mediana dei vinti (almeno MIN_VINTI_INGRESSO) dall'altro lato. La
    variante figlia stringe il filtro corrispondente (min_adx, volume_mult,
    volatility_regime, banda RSI) di un gradino del generatore, e come sempre
    la giudica il gate sulla storia. Il paper propone, non tara.

LA SETTIMA IPOTESI: LA DIREZIONE CONTRO IL CONTESTO BTC (26 set 2026, backlog J7)
  * controtrend_btc: l'audit del flusso di learning ha chiesto se «le short
    perdono» (E1: short 54 trade, -44,95) voglia dire «short» o «short con BTC
    su». Il dato c'e' dal 25 set: `feats_at_entry.market_up` (BTC sopra o sotto
    la sua media lenta a 1h nell'istante dell'apertura, la STESSA variabile del
    gate e del selettore). Qui ogni trade finisce in una casella direzione x
    contesto (`per_contesto`: long_con / long_contro / short_con / short_contro,
    ignoto se il trade e' precedente al 25 set: il contesto NON si ricava dagli
    indicatori della coin). La regola, dichiarata prima: almeno MIN_CAMPIONE
    perdite CONTRO il contesto (long con BTC giu', short con BTC su) e nessun
    vinto contro -> ipotesi `controtrend_btc`, che la discovery prova come
    figlia `conferma_trend` (la conferma a 1 ora e' il mattoncino che c'e').
    Misura, non decisione: il bot non cambia nulla.

LA STORIA DELLE IPOTESI (26 set 2026, backlog J9)
  Le ipotesi vanno e vengono con i trade; senza una memoria non si puo' dire
  se una REGOLA di questo modulo (un tipo) produce varianti che poi passano il
  gate, o solo rumore. `aggiorna_storia` / `registra_esiti_storia` tengono il
  documento Firestore `learning/ipotesi_storia`: una voce per «strategia|tipo»
  con la data di nascita e l'ultimo esito (aperta -> variante_creata ->
  passata -> validata, oppure bocciata / scartata), e `per_tipo` i conteggi.
  Funzioni pure: le scrive il bot dopo i referti e la discovery a ogni giro.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable

# esiti NON decisi dalla strategia: non dicono nulla sul suo edge
# (stessa lista di bot/learning/drift.py _EXTERNAL; qui pubblica perche' la usa
# anche scripts/trade_stats.py per contare gli stessi trade del documento)
ESITI_ESTERNI = frozenset({"manual", "kill_switch", "circuit_breaker"})

# Soglie DICHIARATE PRIMA di vedere i risultati (23 set 2026), non tarate sul
# paper. 3 trade e' il minimo perche' «0 vinti» smetta di essere un caso: con
# 2 succede spesso anche a una strategia sana. 2 stop larghi bastano perche'
# lo stop largo e' una proprieta' della geometria, non della fortuna.
MIN_CAMPIONE = 3
MIN_STOP_LARGO = 2
# 3 perdite «sotto il primo gradino» sulla stessa strategia (25 set 2026): come
# MIN_CAMPIONE, e' il minimo perche' smetta di essere un caso. Dichiarata prima
# di vedere per quali strategie scatta.
MIN_SCALA_STRETTA = 3
# Condizioni d'ingresso (26 set 2026, backlog I4ter). Le soglie sono quelle del
# manuale, non dei risultati: ADX < 20 e' «senza trend» per definizione dell'
# indicatore; volume sotto la media e' vol_ratio < 1; RSI 40-60 e' la fascia in
# cui l'oscillatore non dice niente; per la volatilita' il confine e' il 75°
# percentile dei VINTI della stessa strategia (o 3% del prezzo se e' piu' basso:
# oltre il 3% per candela lo stop in ATR e' quasi sempre fuori dal setup_check).
# 4 perdite: una in piu' di MIN_CAMPIONE perche' qui si contano solo quelle con
# la variabile nota, e 3 su 4 dallo stesso lato con 3 sole perdite sarebbe
# sempre vero. La quota 3/4 e' dichiarata prima di vedere per chi scatta.
MIN_INGRESSO = 4
MIN_VINTI_INGRESSO = 2
QUOTA_INGRESSO = 0.75
VARIABILI_INGRESSO = ("adx", "vol_ratio", "atr_pct", "rsi")
SOGLIA_ADX_BASSO = 20.0
SOGLIA_VOLUME_SOTTO = 1.0
SOGLIA_ATR_ALTA = 0.03
BANDA_RSI_NEUTRO = (40.0, 60.0)
TIPI_INGRESSO = tuple(f"ingresso_{v}" for v in VARIABILI_INGRESSO)

TIPI = ("solo_long", "solo_short", "conferma_trend", "stop_stretto", "scala_stretta",
        *TIPI_INGRESSO, "controtrend_btc")

# le caselle direzione x contesto BTC (26 set 2026): «con» = nel verso di BTC
# (long con BTC su, short con BTC giu'), «contro» il verso opposto, «ignoto»
# quando il trade non porta `market_up` (precedente al 25 set)
CASELLE_CONTESTO = ("long_con", "long_contro", "short_con", "short_contro", "ignoto")

_RILIEVI = ("ingresso", "uscita", "protezione", "stop_largo", "lock_mai", "controtrend")


def _bucket_vuoto() -> dict:
    return {"n": 0, "vinti": 0, "persi": 0, "pnl": 0.0,
            "ingresso": 0, "uscita": 0, "protezione": 0,
            "stop_largo": 0, "lock_mai": 0, "controtrend": 0,
            "long_n": 0, "long_vinti": 0, "long_persi": 0,
            "short_n": 0, "short_vinti": 0, "short_persi": 0,
            # gli mfe (in R) delle perdite di classe «uscita»: servono solo alla
            # mediana nell'ipotesi scala_stretta; `_arrotonda` li toglie dal
            # documento (una lista per strategia non serve a nessun lettore)
            "_uscita_mfe": []}


def _aggiungi(b: dict, pnl: float, direzione: str, pm: dict | None) -> None:
    """Un trade nel bucket. n/vinti/persi/pnl/long_*/short_* contano tutti i trade;
    i rilievi SOLO i trade in perdita con referto: un rilievo su un trade vinto
    non dice cosa correggere."""
    b["n"] += 1
    b["pnl"] += pnl
    vinto = pnl > 0
    if vinto:
        b["vinti"] += 1
    elif pnl < 0:
        b["persi"] += 1
    if direzione in ("long", "short"):
        b[f"{direzione}_n"] += 1
        if vinto:
            b[f"{direzione}_vinti"] += 1
        elif pnl < 0:
            b[f"{direzione}_persi"] += 1
    if pnl < 0 and pm is not None:
        classe = pm.get("classe")
        if classe in ("ingresso", "uscita", "protezione"):
            b[classe] += 1
        if classe == "uscita" and isinstance(pm.get("mfe_r"), (int, float)):
            b["_uscita_mfe"].append(float(pm["mfe_r"]))
        if pm.get("stop_largo"):
            b["stop_largo"] += 1
        if pm.get("lock_mai_armato"):
            b["lock_mai"] += 1
        if pm.get("controtrend"):
            b["controtrend"] += 1


def _ts_trade(t: dict):
    """Epoch dell'apertura (entry_ts, o entry_time ISO; in mancanza exit_ts)."""
    import datetime as _dt
    for k in ("entry_ts", "exit_ts"):
        v = t.get(k)
        if isinstance(v, (int, float)):
            return float(v)
    v = t.get("entry_time")
    if v:
        try:
            return _dt.datetime.fromisoformat(str(v)).timestamp()
        except (TypeError, ValueError):
            pass
    return None


def _mediana(xs: list[float], nd: int = 2) -> float | None:
    xs = sorted(xs)
    if not xs:
        return None
    n = len(xs)
    return round(xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2, nd)


def _percentile(xs: list[float], q: float) -> float | None:
    """Percentile per interpolazione lineare (come numpy di default), senza
    numpy: qui girano poche decine di numeri."""
    xs = sorted(xs)
    if not xs:
        return None
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


# --------------------------------------------------------------------------- #
# LE VARIABILI D'INGRESSO DI UN TRADE (26 set 2026)                             #
# --------------------------------------------------------------------------- #
def _r4(v):
    """Come `_r4` di backtesting/engine.py: float a 4 decimali o None. Copiata
    (non importata) perche' questo modulo gira nel bot e deve restare leggero."""
    if v is None:
        return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    if x != x or x in (float("inf"), float("-inf")):
        return None
    return round(x, 4)


def _campo(snap, nome):
    return snap.get(nome) if isinstance(snap, dict) else getattr(snap, nome, None)


def variabili_ingresso_del_trade(t: dict) -> dict:
    """Le quattro variabili d'ingresso (adx, vol_ratio, atr_pct, rsi) di un trade
    chiuso; None dove il dato manca. Funzione pura.

    Dal 25 set 2026 ogni trade porta `feats_at_entry`, scritto da
    `feats_ingresso` (backtesting/engine.py): si legge quello. I trade piu'
    vecchi portano solo `indicators_at_entry` (timeframe -> snapshot degli
    indicatori): le stesse variabili si ricavano qui con LE STESSE FORMULE del
    gate (atr_pct = atr/close, vol_ratio = volume/volume_sma, 4 decimali), sul
    timeframe del trade, altrimenti su quello del bot, altrimenti sul primo che
    c'e'. `feats_ingresso` divide l'ATR per il prezzo dell'asset nell'istante
    del segnale; qui c'e' la chiusura della candela, che e' lo stesso numero
    salvo lo scarto fra chiusura e prezzo corrente."""
    out = {v: None for v in VARIABILI_INGRESSO}
    if not isinstance(t, dict):
        return out
    feats = t.get("feats_at_entry")
    if isinstance(feats, dict) and any(feats.get(v) is not None for v in VARIABILI_INGRESSO):
        for v in VARIABILI_INGRESSO:
            out[v] = _r4(feats.get(v))
        return out
    ind = t.get("indicators_at_entry")
    if not isinstance(ind, dict) or not ind:
        return out
    snap = None
    tf = t.get("timeframe")
    if tf and ind.get(tf) is not None:
        snap = ind[tf]
    else:
        try:
            from bot.config import settings
            tf_bot = settings.ORCHESTRATOR_TIMEFRAME
        except Exception:  # noqa: BLE001
            tf_bot = None
        if tf_bot and ind.get(tf_bot) is not None:
            snap = ind[tf_bot]
        else:
            snap = next((v for v in ind.values() if v is not None), None)
    if snap is None:
        return out
    out["rsi"] = _r4(_campo(snap, "rsi"))
    out["adx"] = _r4(_campo(snap, "adx"))
    atr, close = _campo(snap, "atr"), _campo(snap, "close")
    if not close:
        close = t.get("entry_price")
    try:
        if atr is not None and close:
            out["atr_pct"] = _r4(float(atr) / float(close))
    except (TypeError, ValueError, ZeroDivisionError):
        pass
    vol, sma = _campo(snap, "volume"), _campo(snap, "volume_sma")
    try:
        if vol is not None and sma:
            out["vol_ratio"] = _r4(float(vol) / float(sma))
    except (TypeError, ValueError, ZeroDivisionError):
        pass
    return out


def contesto_btc_del_trade(t: dict) -> bool | None:
    """BTC era sopra (True) o sotto (False) la sua media lenta a 1h all'apertura
    del trade; None se non si sa. Legge SOLO `feats_at_entry.market_up` (scritto
    dal bot dal 25 set 2026 con la stessa funzione del gate). Per i trade piu'
    vecchi NON si ricava da `indicators_at_entry`: quelli sono gli indicatori
    della coin, non di BTC, e un contesto inventato sarebbe peggio di uno
    mancante. Funzione pura."""
    if not isinstance(t, dict):
        return None
    feats = t.get("feats_at_entry")
    if not isinstance(feats, dict):
        return None
    v = feats.get("market_up")
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)) and v == v:
        return bool(v >= 0.5)
    return None


def casella_contesto(direzione: str, market_up: bool | None) -> str:
    """La casella direzione x contesto di un trade (vedi CASELLE_CONTESTO)."""
    if market_up is None or direzione not in ("long", "short"):
        return "ignoto"
    con = (direzione == "long") == bool(market_up)
    return f"{direzione}_{'con' if con else 'contro'}"


def _contesto_vuoto() -> dict:
    return {c: {"trade": 0, "vinti": 0, "pnl": 0.0} for c in CASELLE_CONTESTO}


def _aggiungi_contesto(b: dict, casella: str, pnl: float) -> None:
    c = b[casella]
    c["trade"] += 1
    c["pnl"] += pnl
    if pnl > 0:
        c["vinti"] += 1


def _arrotonda_contesto(b: dict) -> dict:
    for c in b.values():
        c["pnl"] = round(c["pnl"], 2)
    return b


def _arrotonda(b: dict) -> dict:
    b["pnl"] = round(b["pnl"], 2)
    b.pop("_uscita_mfe", None)
    return b


def _lato_ingresso(var: str, persi: list[float], vinti: list[float]) -> dict | None:
    """La regola della sesta ipotesi per UNA variabile: quante perdite d'ingresso
    stanno dal lato «cattivo» della soglia dichiarata, e se i vinti stanno
    dall'altro. Ritorna None se non scatta, altrimenti i numeri per il testo.
    `soglia` e' quella che la figlia deve superare (per atr_pct e' misurata sui
    vinti, e per questo viaggia nell'ipotesi)."""
    if len(persi) < MIN_INGRESSO or len(vinti) < MIN_VINTI_INGRESSO:
        return None
    med_v = _mediana(vinti, 4)
    if var == "adx":
        soglia, etich, nd = SOGLIA_ADX_BASSO, "ADX < 20", 0
        lato = [x for x in persi if x < soglia]
        vinti_ok = med_v >= soglia
    elif var == "vol_ratio":
        soglia, etich, nd = SOGLIA_VOLUME_SOTTO, "volume sotto la media (vol_ratio < 1)", 2
        lato = [x for x in persi if x < soglia]
        vinti_ok = med_v >= soglia
    elif var == "atr_pct":
        p75 = _percentile(vinti, 0.75)
        soglia = min(SOGLIA_ATR_ALTA, p75) if p75 is not None else SOGLIA_ATR_ALTA
        soglia = round(soglia, 4)
        etich, nd = f"volatilita' alta (ATR > {soglia * 100:.2f}% del prezzo)", 4
        lato = [x for x in persi if x > soglia]
        vinti_ok = med_v <= soglia
    elif var == "rsi":
        lo, hi = BANDA_RSI_NEUTRO
        soglia, etich, nd = None, f"RSI neutro ({lo:g}-{hi:g})", 0
        lato = [x for x in persi if lo <= x <= hi]
        vinti_ok = not (lo <= med_v <= hi)
    else:
        return None
    if len(lato) < QUOTA_INGRESSO * len(persi) or not vinti_ok:
        return None
    return {"soglia": soglia, "etichetta": etich, "sul_lato": len(lato), "nd": nd,
            "mediana_persi": _mediana(lato, 4), "mediana_vinti": med_v}


def _fmt_var(var: str, x: float | None, nd: int) -> str:
    if x is None:
        return "n/d"
    if var == "atr_pct":
        return f"{x * 100:.2f}%"
    return f"{x:.{nd}f}"


def _ipotesi_per(gid: str, b: dict, ingresso: dict | None = None,
                 contesto: dict | None = None) -> list[dict]:
    """Le regole, una per tipo, sul bucket di una strategia. Ogni regola e' una
    riga: se la cambi, cambia il commento in testa al modulo e la data.
    `ingresso`: {variabile: {"persi": [...], "vinti": [...]}} — le variabili
    d'ingresso delle perdite di classe ingresso e dei vinti (26 set 2026).
    `contesto`: il bucket direzione x contesto BTC della strategia (26 set 2026,
    settima ipotesi `controtrend_btc`)."""
    out = []
    # si contano le PERDITE vere, non «tutti tranne i vinti»: con un pareggio
    # (pnl 0, raro con le fee ma possibile) il motivo direbbe «3/3 persi» su 2
    # perdite. Un numero va con la sua fonte (rilievo dei revisori, 23 set).
    if b["short_persi"] >= MIN_CAMPIONE and b["short_vinti"] == 0:
        out.append({"strategia": gid, "tipo": "solo_long",
                    "motivo": f"short {b['short_persi']}/{b['short_n']} persi",
                    "campione": b["short_n"]})
    if b["long_persi"] >= MIN_CAMPIONE and b["long_vinti"] == 0:
        out.append({"strategia": gid, "tipo": "solo_short",
                    "motivo": f"long {b['long_persi']}/{b['long_n']} persi",
                    "campione": b["long_n"]})
    if b["controtrend"] >= MIN_CAMPIONE:
        out.append({"strategia": gid, "tipo": "conferma_trend",
                    "motivo": f"{b['controtrend']} perdite controtrend",
                    "campione": b["controtrend"]})
    elif b["ingresso"] >= MIN_CAMPIONE and b["vinti"] == 0:
        out.append({"strategia": gid, "tipo": "conferma_trend",
                    "motivo": (f"{b['ingresso']} perdite mai andate a favore "
                               f"(classe ingresso) e 0 vinti su {b['n']}"),
                    "campione": b["ingresso"]})
    if b["stop_largo"] >= MIN_STOP_LARGO:
        out.append({"strategia": gid, "tipo": "stop_stretto",
                    "motivo": f"{b['stop_largo']} perdite con stop troppo largo",
                    "campione": b["stop_largo"]})
    # scala_stretta (25 set 2026): perdite andate a favore ma morte sotto il primo
    # gradino. La mediana degli mfe e' il numero che dice QUANTO era fuori
    # portata la scala; se un referto vecchio non porta `mfe_r`, si scrive n/d.
    if b["uscita"] >= MIN_SCALA_STRETTA:
        med = _mediana(b.get("_uscita_mfe") or [])
        out.append({"strategia": gid, "tipo": "scala_stretta",
                    "motivo": (f"{b['uscita']} perdite sotto il primo gradino "
                               f"(mfe mediana {f'{med:.2f}' if med is not None else 'n/d'} R)"),
                    "campione": b["uscita"], "mfe_mediana": med})
    # le condizioni d'ingresso (26 set 2026, backlog I4ter): una voce per
    # variabile, perche' ognuna diventa una variante diversa nel generatore
    for var in VARIABILI_INGRESSO:
        dati = (ingresso or {}).get(var) or {}
        persi, vinti = list(dati.get("persi") or []), list(dati.get("vinti") or [])
        r = _lato_ingresso(var, persi, vinti)
        if r is None:
            continue
        nd = r["nd"]
        h = {"strategia": gid, "tipo": f"ingresso_{var}",
             "motivo": (f"{r['sul_lato']} perdite d'ingresso su {len(persi)} con "
                        f"{r['etichetta']} (mediana {_fmt_var(var, r['mediana_persi'], nd)}), "
                        f"vinti mediana {_fmt_var(var, r['mediana_vinti'], nd)}"),
             "campione": len(persi), "variabile": var,
             "mediana_persi": r["mediana_persi"], "mediana_vinti": r["mediana_vinti"]}
        if r["soglia"] is not None:
            h["soglia"] = r["soglia"]
        out.append(h)
    # controtrend_btc (26 set 2026, backlog J7): le perdite CONTRO il contesto
    # BTC (long con BTC giu', short con BTC su), sommate sulle due direzioni,
    # e nessun vinto contro. Stesso MIN_CAMPIONE delle ipotesi per direzione:
    # con 3 perdite e 0 vinti smette di essere un caso, come per «short 3/3».
    if contesto:
        contro = [contesto.get("long_contro") or {}, contesto.get("short_contro") or {}]
        n_contro = sum(int(c.get("trade", 0) or 0) for c in contro)
        vinti_contro = sum(int(c.get("vinti", 0) or 0) for c in contro)
        persi_contro = sum(int(c.get("_persi", 0) or 0) for c in contro)
        if persi_contro >= MIN_CAMPIONE and vinti_contro == 0:
            out.append({"strategia": gid, "tipo": "controtrend_btc",
                        "motivo": f"{persi_contro}/{n_contro} persi contro il contesto BTC",
                        "campione": n_contro})
    return out


def aggrega_referti(trades: Iterable[dict]) -> dict:
    """Aggrega i trade chiusi per strategia, coin e direzione e produce le ipotesi.

    E' il documento Firestore `learning/referti` (contratto condiviso con la
    discovery e con `scripts/trade_stats.py`). Gli esiti esterni (manual,
    kill_switch, circuit_breaker) sono esclusi: non li ha decisi la strategia.
    Le ipotesi per direzione NON richiedono il referto: bastano pnl e direction,
    quindi scattano anche sui trade chiusi prima del 23 set.

    I trade del PAPER ESPLORATIVO (25 set 2026, F1bis) sono INCLUSI, di proposito:
    le ipotesi per il gate sono il punto stesso dell'esplorazione, e un referto
    vale come referto a qualunque size. Il documento li conta in `esplorative`,
    cosi' chi legge sa quanta parte dell'evidenza viene da li'."""
    rows = [t for t in trades if str(t.get("exit_reason", "")) not in ESITI_ESTERNI]
    n_esplorative = sum(1 for t in rows if t.get("esplorativa"))
    per_strat: dict[str, dict] = defaultdict(_bucket_vuoto)
    per_coin: dict[str, dict] = defaultdict(_bucket_vuoto)
    per_dir: dict[str, dict] = {"long": _bucket_vuoto(), "short": _bucket_vuoto()}
    n_con_referto = n_persi_con_referto = 0
    # il PRIMO trade del paper per strategia: la variante che nasce da un'ipotesi
    # si valida su dati che finiscono prima di quella data (pre-registrazione,
    # audit del 24 set)
    primo_ts: dict[str, float] = {}
    # le variabili d'ingresso, per strategia: delle PERDITE di classe ingresso
    # (mai andate a favore) e dei VINTI. Solo i valori noti: un None non e' un
    # numero (26 set 2026)
    ingresso: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(
        lambda: {v: {"persi": [], "vinti": []} for v in VARIABILI_INGRESSO})
    # direzione x contesto BTC (26 set 2026): per strategia e globale. `_persi`
    # serve solo alla settima ipotesi (i pareggi non sono perdite); il documento
    # porta trade/vinti/pnl
    contesto_strat: dict[str, dict] = defaultdict(_contesto_vuoto)
    contesto_glob = _contesto_vuoto()

    for t in rows:
        pnl = float(t.get("pnl", 0) or 0)
        ts = _ts_trade(t)
        direzione = str(t.get("direction", "") or "").lower()
        pm = t.get("post_mortem")
        pm = pm if isinstance(pm, dict) else None
        if pm is not None:
            n_con_referto += 1
            if pnl < 0:
                n_persi_con_referto += 1
        gid = str(t.get("strategy", "?") or "?")
        sym = str(t.get("symbol", "?") or "?")
        if ts is not None and (gid not in primo_ts or ts < primo_ts[gid]):
            primo_ts[gid] = ts
        _aggiungi(per_strat[gid], pnl, direzione, pm)
        _aggiungi(per_coin[sym], pnl, direzione, pm)
        if direzione in per_dir:
            _aggiungi(per_dir[direzione], pnl, direzione, pm)
        casella = casella_contesto(direzione, contesto_btc_del_trade(t))
        for cb in (contesto_strat[gid], contesto_glob):
            _aggiungi_contesto(cb, casella, pnl)
            if pnl < 0:
                cb[casella]["_persi"] = int(cb[casella].get("_persi", 0)) + 1
        perso_ingresso = pnl < 0 and pm is not None and pm.get("classe") == "ingresso"
        if (perso_ingresso or pnl > 0) and gid != "?":
            vals = variabili_ingresso_del_trade(t)
            for var in VARIABILI_INGRESSO:
                if vals.get(var) is not None:
                    ingresso[gid][var]["persi" if perso_ingresso else "vinti"].append(vals[var])

    ipotesi: list[dict] = []
    for gid in sorted(per_strat):
        if gid == "?":
            continue    # trade senza strategia: contano nei bucket, non propongono
        for h in _ipotesi_per(gid, per_strat[gid], ingresso.get(gid),
                              contesto_strat.get(gid)):
            if gid in primo_ts:
                h["da_ts"] = round(primo_ts[gid], 0)
            ipotesi.append(h)
    ipotesi.sort(key=lambda h: (h["strategia"], h["tipo"]))
    # il riassunto delle condizioni d'ingresso per strategia: solo conteggi e
    # mediane (mai le liste), solo le 4 variabili, solo chi ha almeno un dato
    ingresso_doc: dict[str, dict] = {}
    for gid in sorted(ingresso):
        riga = {}
        for var in VARIABILI_INGRESSO:
            d = ingresso[gid][var]
            if not d["persi"] and not d["vinti"]:
                continue
            riga[var] = {"persi": len(d["persi"]), "vinti": len(d["vinti"]),
                         "mediana_persi": _mediana(d["persi"], 4),
                         "mediana_vinti": _mediana(d["vinti"], 4)}
        if riga:
            ingresso_doc[gid] = riga
    # direzione x contesto BTC nel documento: solo trade/vinti/pnl (il contatore
    # `_persi` e' di servizio, come `_uscita_mfe`)
    for cb in list(contesto_strat.values()) + [contesto_glob]:
        for c in cb.values():
            c.pop("_persi", None)
        _arrotonda_contesto(cb)

    return {
        "n_trades": len(rows),
        "esplorative": n_esplorative,
        "n_con_referto": n_con_referto,
        "n_persi_con_referto": n_persi_con_referto,
        "per_strategia": {k: _arrotonda(v) for k, v in sorted(per_strat.items())},
        "per_coin": {k: _arrotonda(v) for k, v in sorted(per_coin.items())},
        "per_direzione": {k: _arrotonda(v) for k, v in per_dir.items()},
        "ipotesi": ipotesi,
        "ingresso": ingresso_doc,
        "per_contesto": {"globale": contesto_glob,
                         "per_strategia": {k: contesto_strat[k] for k in sorted(contesto_strat)}},
    }


def riassunto_ipotesi(doc: dict | None) -> list[str]:
    """Una riga leggibile per ipotesi, per il print del bot e per `trades`:
    «gen_ba3a671f: solo_long — short 4/4 persi (campione 4)»."""
    if not doc:
        return []
    return [f"{h.get('strategia')}: {h.get('tipo')} — {h.get('motivo')} "
            f"(campione {h.get('campione')})"
            for h in (doc.get("ipotesi") or [])]


# --------------------------------------------------------------------------- #
# LA STORIA DELLE IPOTESI (26 set 2026, backlog J9)                             #
# --------------------------------------------------------------------------- #
# gli esiti di una voce, nell'ordine in cui una vita puo' attraversarli
ESITI_STORIA = ("aperta", "variante_creata", "passata", "validata", "bocciata", "scartata")
# il primo istante in cui la voce ha toccato quel traguardo: da qui `per_tipo`
# conta «quante varianti / passate / validate / bocciate» anche se l'ultimo
# esito e' poi cambiato (una variante bocciata e rinata al giro dopo resta
# contata come bocciata una volta)
_TRAGUARDI = {"variante_creata": "variante_at", "passata": "passata_at",
              "validata": "validata_at", "bocciata": "bocciata_at",
              "scartata": "scartata_at"}


def chiave_storia(strategia, tipo) -> str:
    return f"{strategia}|{tipo}"


def per_tipo_storia(voci: dict) -> dict:
    """I conteggi per tipo di regola: nate (voci), varianti (con una figlia),
    passate (la figlia ha passato il gate almeno una volta), validate (e' entrata
    nel registro), bocciate. Pura, deterministica (tipi in ordine)."""
    out: dict[str, dict] = {}
    for v in (voci or {}).values():
        if not isinstance(v, dict):
            continue
        tipo = str(v.get("tipo") or "?")
        r = out.setdefault(tipo, {"nate": 0, "varianti": 0, "passate": 0,
                                  "validate": 0, "bocciate": 0})
        r["nate"] += 1
        r["varianti"] += int(bool(v.get("variante_id")) or bool(v.get("variante_at")))
        r["passate"] += int(bool(v.get("passata_at")) or bool(v.get("validata_at")))
        r["validate"] += int(bool(v.get("validata_at")))
        r["bocciate"] += int(bool(v.get("bocciata_at")))
    return {k: out[k] for k in sorted(out)}


def aggiorna_storia(doc_prec: dict | None, referti_doc: dict | None, now: float) -> dict:
    """Aggiunge alla storia le ipotesi che compaiono per la PRIMA volta nei
    referti (`nata_at = now`, esito «aperta»); le voci gia' note non si toccano
    (la data di nascita e' il punto). Ritorna il documento nuovo, mai muta gli
    argomenti. Pura: la scrive chi la chiama (il bot dopo `learning/referti`, la
    discovery all'inizio del giro)."""
    voci = {k: dict(v) for k, v in ((doc_prec or {}).get("voci") or {}).items()
            if isinstance(v, dict)}
    for h in (referti_doc or {}).get("ipotesi") or []:
        if not isinstance(h, dict):
            continue
        gid, tipo = h.get("strategia"), h.get("tipo")
        if not isinstance(gid, str) or not gid or not isinstance(tipo, str) or not tipo:
            continue
        k = chiave_storia(gid, tipo)
        if k in voci:
            continue
        voci[k] = {"nata_at": round(float(now), 0), "tipo": tipo, "strategia": gid,
                   "variante_id": None, "esito": "aperta", "at": round(float(now), 0)}
    return {"voci": voci, "per_tipo": per_tipo_storia(voci), "updated_at": round(float(now), 0)}


def registra_esiti_storia(doc_prec: dict | None, eventi: dict, now: float) -> dict:
    """Applica gli esiti della discovery: `eventi` = {"strategia|tipo": (esito,
    variante_id)} con esito in ESITI_STORIA. Una voce che non esiste ancora
    (ipotesi nata prima della storia) viene creata con `nata_at = now`, cosi'
    l'esito non si perde. Aggiorna l'ultimo esito e segna il traguardo la prima
    volta che lo tocca. Pura."""
    voci = {k: dict(v) for k, v in ((doc_prec or {}).get("voci") or {}).items()
            if isinstance(v, dict)}
    ts = round(float(now), 0)
    for k, ev in (eventi or {}).items():
        if not isinstance(k, str) or "|" not in k:
            continue
        esito, vid = (ev if isinstance(ev, (tuple, list)) and len(ev) == 2 else (ev, None))
        if esito not in ESITI_STORIA:
            continue
        gid, tipo = k.split("|", 1)
        v = voci.setdefault(k, {"nata_at": ts, "tipo": tipo, "strategia": gid,
                                "variante_id": None, "esito": "aperta", "at": ts})
        v["esito"] = esito
        v["at"] = ts
        if vid:
            v["variante_id"] = str(vid)
        tr = _TRAGUARDI.get(esito)
        if tr and not v.get(tr):
            v[tr] = ts
    return {"voci": voci, "per_tipo": per_tipo_storia(voci), "updated_at": ts}
