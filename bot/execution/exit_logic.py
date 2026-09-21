"""
Logica di uscita CONDIVISA tra backtest (GATE 1) e live executor.

Tenerla in un solo posto garantisce che il paper trading si comporti ESATTAMENTE
come la validazione: stesso stop, stesso profit-lock, stessi parametri.

profit-lock (protezione del profitto):
  Quando una posizione va in profitto ma non tocca il take-profit, invece di
  restituire tutto il guadagno blocchiamo una parte del MIGLIOR profitto visto.
  - si "arma" quando il prezzo ha coperto PROFIT_LOCK_TRIGGER della distanza
    entry->TP (es. metà strada);
  - una volta armato, lo stop sale (long) / scende (short) a
    entry +/- PROFIT_LOCK_KEEP * (miglior_escursione_favorevole),
    e può solo MIGLIORARE (ratchet), mai peggiorare.
"""
from __future__ import annotations

from bot.config import settings


def locked_stop(entry: float, target: float, long: bool,
                best_favorable_price: float, base_stop: float,
                keep: float | None = None) -> float:
    """
    Ritorna lo stop EFFETTIVO data la migliore escursione favorevole vista finora.
    Se il profit-lock non è armato (o disattivato) ritorna lo stop base invariato.

    `best_favorable_price` è il prezzo più favorevole raggiunto FINORA (il massimo
    per un long, il minimo per uno short), escludendo la barra corrente per evitare
    look-ahead nel backtest.

    `keep`: frazione del miglior guadagno da bloccare. None -> default globale
    (PROFIT_LOCK_KEEP, il valore VALIDATO dal gate). Il bot live puo' passare il
    valore IMPARATO per-strategia dai verdetti trailing (metrics.compute_trailing_keep).
    """
    if not settings.PROFIT_LOCK_ENABLED:
        return base_stop
    tp_dist = abs(target - entry)
    if tp_dist <= 0:
        return base_stop
    fav_move = (best_favorable_price - entry) if long else (entry - best_favorable_price)
    if fav_move <= 0 or fav_move < settings.PROFIT_LOCK_TRIGGER * tp_dist:
        return base_stop  # non ancora armato
    lock = (settings.PROFIT_LOCK_KEEP if keep is None else keep) * fav_move
    locked = entry + lock if long else entry - lock
    # lo stop può solo migliorare: sale per i long, scende per gli short
    return max(base_stop, locked) if long else min(base_stop, locked)


# ---- SCALE DI TP CANDIDATE (per la taratura per-coppia dal GATE) ------------ #
# La scala giusta NON e' la stessa per tutte le coppie: R e' gia' normalizzato sulla
# volatilita' (R = atr_mult x ATR), quindi la domanda non e' "quanto e' volatile la
# coin" ma "quanto TENDE, in unita' della sua volatilita'". Una coin che ritraccia
# subito non vedra' mai 5R; una che tende lo supera. Per questo la scala e' un
# PARAMETRO da validare per coppia, non una costante globale.
# Le quote (30/30/40) restano fisse: sono il risultato VALIDATO dall'A/B, e farle
# variare qui allargherebbe lo spazio di ricerca senza una domanda aperta a cui
# rispondere. Questo elenco e' un punto di partenza da rivedere sui dati misurati
# (mfe_r: dove arriva davvero il prezzo, in unita' di R).
SCALE_LADDER_CANDIDATES: tuple[tuple[float, ...], ...] = (
    (1.0, 1.5, 2.5),    # molto corta: incassa presto, per coppie che ritracciano
    (1.0, 2.0, 3.0),    # corta
    (1.5, 3.0, 5.0),    # attuale (default globale dall'A/B)
    (2.0, 4.0, 6.0),    # lunga: per coppie che tendono davvero
)


def ladder_from_mfe(mfes, min_trades: int = 10) -> tuple[float, ...] | None:
    """Una scala di TP ricavata da DOVE IL PREZZO E' DAVVERO ARRIVATO nel paper.

    IL PROBLEMA CHE CHIUDE. Le quattro scale candidate sopra sono un elenco scritto
    a mano, e il gate sceglie fra quelle guardando solo la storia simulata. Il paper
    intanto misurava un fatto che nessuno usava: `mfe_r`, quanto lontano arriva il
    prezzo prima di tornare. Al 19 settembre la mediana era **0,74 R** contro un
    primo gradino a 1,5-2,0 R — cioe' puntavamo sistematicamente oltre la portata
    del mercato, e il rilevatore di deriva lo scriveva su ogni coppia senza che
    nessuno potesse farci niente.

    PERCHE' `mfe` FUNZIONA CON POCHI TRADE, e vincere/perdere no. Un esito e' testa
    o croce: dodici lanci non distinguono la sfortuna dal difetto (su 12 trade con 2
    vinti, un sistema sano produce quel risultato il 3,6% delle volte). `mfe_r` e'
    un NUMERO per ogni trade, non una monetina: dodici numeri dicono dove va il
    mercato molto prima che dodici monetine dicano se si vince.

    E RESTA UN CANDIDATO, non una decisione. Questa scala viene semplicemente
    aggiunta alle quattro fisse e il gate sceglie la migliore sui PROPRI dati, con
    le proprie tre conferme. Il paper propone, il gate dispone: cosi' una misura su
    dodici trade non puo' scavalcare la validazione, e la parita' gate<->paper
    regge. Se la scala derivata non e' buona, il gate non la sceglie e basta.

    Quantili 50/75/90: il primo gradino alla mediana significa che circa meta' dei
    trade incassa la prima fetta, invece di quasi nessuno.

    None se i trade non bastano o se non ne esce una scala sensata — e in quel caso
    i candidati restano i quattro di sempre.
    """
    validi = sorted(float(m) for m in (mfes or [])
                    if m is not None and float(m) > 0)
    if len(validi) < min_trades:
        return None

    def quantile(p: float) -> float:
        i = int(round(p * (len(validi) - 1)))
        return validi[min(len(validi) - 1, max(0, i))]

    fuori: list[float] = []
    prec = 0.0
    for p in (0.5, 0.75, 0.9):
        # arrotondato a 0.25 R: una scala non ha bisogno di tre decimali, e numeri
        # tondi rendono leggibile il confronto con le quattro candidate fisse
        x = round(quantile(p) * 4) / 4
        x = max(x, prec + 0.25, 0.5)     # gradini strettamente crescenti
        if x > 8.0:
            return None                 # oltre, non e' piu' una scala: e' un sogno
        fuori.append(x)
        prec = x
    return tuple(fuori)


def scale_ladder(entry: float, base_stop: float, long: bool,
                 r_mults=None, fracs=None) -> list[tuple[float, float]]:
    """Scala di take-profit a MULTIPLI di R (R = |entry - base_stop|).

    Ritorna [(price, fraction), ...] in ordine di R crescente. L'ultimo livello è
    il TP FINALE. Vuota se R<=0 o scale-out disattivo. CONDIVISA tra backtest e
    live per garantire la parità GATE 1 <-> paper.
    """
    r_mults = settings.SCALE_OUT_R_MULTIPLES if r_mults is None else r_mults
    fracs = settings.SCALE_OUT_FRACTIONS if fracs is None else fracs
    R = abs(entry - base_stop)
    if R <= 0 or not r_mults:
        return []
    out: list[tuple[float, float]] = []
    for m, f in zip(r_mults, fracs):
        price = entry + m * R if long else entry - m * R
        out.append((price, f))
    return out


def breakeven_after_tp1(params: dict | None) -> bool:
    """Se spostare lo stop a BREAK-EVEN dopo il primo TP, per QUESTA coppia.

    Non e' una scelta ovvia e non era mai stata isolata: l'A/B confronto' TP-unico
    vs scale-out-CON-BE, quindi il BE non e' mai stato testato da solo. I dati lo
    rendono ambiguo: protegge (un ritorno a entry dopo il TP1 diventa +0.3R invece
    di -0.55R) ma taglia i runner (con mfe mediana ~1.1R il prezzo ritocca l'entry
    di continuo). Quale prevalga dipende dalla coppia -> lo decide il gate.
    Assente nei params -> default globale (comportamento storico)."""
    if params is not None and "sl_to_breakeven" in params:
        return bool(params["sl_to_breakeven"])
    return settings.SCALE_OUT_SL_TO_BREAKEVEN


def effective_param_grid(grid: dict) -> dict:
    """Griglia di ricerca EFFETTIVA per una strategia, in base al modello di uscita.

    Sotto scale-out il take-profit non e' piu' `rr` x R: e' la SCALA di gradini. `rr`
    resta nella griglia ma non ha NESSUN effetto sulle uscite (il ramo scale-out non
    usa `target`), quindi con `--max-combos` che campiona a caso finirebbe per diluire
    la ricerca su un parametro morto — misurato: 67-75% delle combinazioni campionate
    sarebbero cloni. Qui `rr` viene SOSTITUITO dalla scala: stesso numero di
    combinazioni, ma tarate su cio' che decide davvero le uscite.
    Senza scale-out la griglia resta identica a prima."""
    if not settings.SCALE_OUT_ENABLED or "rr" not in grid:
        return grid
    out = {k: v for k, v in grid.items() if k != "rr"}
    out["scale_r_mults"] = list(SCALE_LADDER_CANDIDATES)
    # il BE dopo TP1 e' un'ipotesi, non una certezza: si valida per coppia
    out["sl_to_breakeven"] = [True, False]
    return out


def lock_anchor(ladder) -> float:
    """A quale prezzo e' ancorata la protezione del profitto sotto scale-out.

    IL PRIMO GRADINO, dal 21 settembre 2026. Prima era l'ultimo: con la scala 2/4/6
    il lock si armava a meta' strada da 6R, cioe' a 3R, e un trade a +1,9R per
    tre ore non era protetto da niente — usciva allo stop pieno. Misurato su 27
    trade chiusi: 21 stop, e 13 di quei 21 erano andati a favore (mfe mediana
    0,69R) senza toccare il primo gradino. Ancorando al primo gradino il lock si
    arma a meta' strada da esso (1R su 2/4/6, 0,75R su 1,5/3/5) e quei trade
    escono vicino al pareggio invece che a -1R.

    Una sola definizione per motore e executor: e' il punto in cui gate e paper
    devono coincidere, e due copie divergerebbero al primo ritocco."""
    return ladder[0][0]


def ladder_multiples(params: dict | None) -> tuple | None:
    """Multipli di R da usare per QUESTA coppia, letti dai params validati dal gate.

    None -> `scale_ladder` usa il default globale (SCALE_OUT_R_MULTIPLES). E' il caso
    delle coppie non ancora ri-validate col nuovo spazio di ricerca: continuano a
    operare con la scala CON CUI SONO STATE VALIDATE, quindi la parita' gate<->paper
    regge anche a registro misto durante la migrazione."""
    if not params:
        return None
    v = params.get("scale_r_mults")
    if not v:
        return None
    try:
        out = tuple(float(x) for x in v)
    except (TypeError, ValueError):
        return None
    return out or None


def mfe_in_r(entry: float, best_favorable: float, base_stop: float) -> float:
    """Massima escursione FAVOREVOLE in unita' di R (R = |entry - stop base|).

    E' la misura che rende decidibile la scala: da questo unico numero si sa quali
    gradini AVREBBE colpito QUALUNQUE scala, senza doverle provare una per una ne'
    sacrificare trade per esplorare. 0 se R non e' calcolabile."""
    R = abs(entry - base_stop)
    if R <= 0:
        return 0.0
    return abs(best_favorable - entry) / R


def scale_fills(ladder, stage: int, long: bool, hi: float, lo: float):
    """Quante fette della scala si riempiono nel range [lo, hi] a partire da `stage`.

    Ritorna (new_stage, fills) con fills = [(price, fraction), ...] nell'ordine.
    Per il live basta passare hi=lo=mark. I livelli si riempiono in sequenza: un
    livello superiore non può riempirsi prima di quello inferiore.
    """
    fills: list[tuple[float, float]] = []
    while stage < len(ladder):
        price, frac = ladder[stage]
        reached = (hi >= price) if long else (lo <= price)
        if not reached:
            break
        fills.append((price, frac))
        stage += 1
    return stage, fills


def trailing_verdict(candles, stop: float, target: float, long: bool) -> str:
    """Controfattuale su un'uscita TRAILING: se avessimo TENUTO (stop base + TP),
    cosa sarebbe arrivato PRIMA scorrendo le candele DALL'uscita in avanti?
      - TP per primo   -> 'premature' (tagliato un vincitore)
      - stop base primo-> 'protected' (evitata una perdita)
      - nessuno / stessa candela -> 'neutral'
    Condivisa tra backtest (GATE 1) e bot (learning dal paper). `candles`: sequenza
    con attributi .high e .low."""
    for c in candles:
        tp_hit = (c.high >= target) if long else (c.low <= target)
        sl_hit = (c.low <= stop) if long else (c.high >= stop)
        if tp_hit and sl_hit:
            return "neutral"          # stessa candela: ordine intra-candela ignoto
        if tp_hit:
            return "premature"
        if sl_hit:
            return "protected"
    return "neutral"


def _atr(candles, period: int = 14) -> float:
    """ATR semplice (media dei true range) sulle candele date. 0 se dati insufficienti."""
    if len(candles) < 2:
        return 0.0
    trs, prev = [], candles[0].close
    for c in candles[1:]:
        trs.append(max(c.high - c.low, abs(c.high - prev), abs(c.low - prev)))
        prev = c.close
    window = trs[-period:] if len(trs) >= period else trs
    return sum(window) / len(window) if window else 0.0


def trailing_reason(during, after, entry: float, exit_price: float,
                    stop: float, target: float, long: bool) -> dict:
    """Verdetto trailing + il PERCHE', per capire come ridurre i 'premature'.

    - verdict: 'premature' | 'protected' | 'neutral' (dal prezzo DOPO l'uscita).
    - miss_to_tp: frazione del tragitto entry->TP lasciata sul tavolo all'uscita
      (0 = uscito al TP, 1 = uscito all'entrata). Premature con miss piccola = per un
      soffio, un trail piu' largo lo prende.
    - knockout_atr: profondita' del ritracciamento che ha fatto scattare il trail
      (dal massimo/minimo raggiunto fino all'uscita) in MULTIPLI di ATR. < ~1 = rumore
      (un trail consapevole dell'ATR lo eviterebbe); grande = inversione reale.

    `during` = candele TRA entrata e uscita (per max/min e ATR); `after` = candele
    DALL'uscita in avanti (per il controfattuale)."""
    verdict = trailing_verdict(after, stop, target, long)
    tp_dist = abs(target - entry) or 1e-9
    miss = min(1.0, abs(target - exit_price) / tp_dist)
    hw = (max((c.high for c in during), default=exit_price) if long
          else min((c.low for c in during), default=exit_price))
    dip = (hw - exit_price) if long else (exit_price - hw)
    atr = _atr(during)
    return {
        "verdict": verdict,
        "miss_to_tp": round(miss, 3),
        "knockout_atr": round(dip / atr, 2) if atr > 0 else None,
    }
