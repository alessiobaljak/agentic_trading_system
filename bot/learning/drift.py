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

IL FRENO PER GRUPPO CON USCITA (26 set 2026, passo 4 del piano del 26 set 15:xx)
Fra la coppia (8 trade, mai raggiunti: massimo 5 per coppia) e il globale (40
trade, acceso dal 23 set senza data di uscita) mancava un livello che maturi in
giorni E sappia spegnersi da solo. E' il POOL: famiglia x regime all'ingresso e
direzione x contesto BTC. Su ogni pool, sugli ultimi POOL_GIORNI giorni di trade
delle validate, un CUSUM a un lato sui multipli di R sotto il riferimento
promesso dal registro (`cusum_r`: allarme a POOL_CUSUM_H R di deficit cumulato)
e, dopo l'allarme, un CUSUM di ripresa (`cusum_ripresa`: POOL_CUSUM_RIPRESA R
sopra il riferimento -> il freno si toglie). Accanto, solo REGISTRATO, un test
sequenziale di Wald su «ha toccato TP1» (`sprt_tp1`). Le soglie sono costanti
di modulo dichiarate prima di ogni misura: il replay (`scripts/replay_freno.py`)
puo' solo bocciarle, mai sceglierle — il paper e' il giudice, non il maestro.
"""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Iterable

from bot.config import settings

# esiti NON decisi dalla strategia: non dicono nulla sul suo edge
_EXTERNAL = {"manual", "kill_switch", "circuit_breaker"}

OK, WATCH, DRIFT = "ok", "watch", "drift"

# --------------------------------------------------------------------------- #
# Il freno per gruppo: soglie DICHIARATE (26 set 2026), mai tarate sul paper     #
# --------------------------------------------------------------------------- #
#: CUSUM a un lato sui multipli di R: allarme quando il deficit cumulato sotto
#: il riferimento raggiunge h (in R). k=0: nessuna tolleranza, ogni trade sotto
#: il riferimento conta per intero. 4R = quattro stop pieni piu' del promesso.
CUSUM_H = 4.0
CUSUM_K = 0.0
#: ripresa: dopo l'allarme, il pool si libera quando cumula 2,5R SOPRA il
#: riferimento (un CUSUM speculare). E' la data di uscita che al globale manca.
CUSUM_RIPRESA = 2.5
#: SPRT su «ha toccato TP1» (mfe_r >= primo gradino): p0 sano, p1 degradato,
#: alpha = beta = 0,05. Il 45% e' la promessa tipica del gate («il prezzo tocca
#: il primo gradino nel 60% dei casi» in backtest, meno dal vivo: ops 0237,
#: 20 stop su 32 sotto il primo gradino); il 25% e' meta' abbondante.
SPRT_P0 = 0.45
SPRT_P1 = 0.25
SPRT_ALPHA = 0.05
SPRT_BETA = 0.05
#: finestra dei pool: gli ultimi 30 giorni di trade chiusi (come i pesi)
POOL_GIORNI = 30
#: prefissi delle chiavi dei pool nel documento `drift/current.pool`
POOL_FAM, POOL_DIR = "fam:", "dir:"
#: bucket del contesto BTC; «ignoto» (market_up assente) NON forma un pool
CTX_SU, CTX_GIU = "btc_su", "btc_giu"


def cusum_r(rs: Iterable[float], riferimento: float, h: float = CUSUM_H,
            k: float = CUSUM_K) -> tuple[bool, float, int | None]:
    """CUSUM a UN lato (verso il basso) sui multipli di R.

    S_t = max(0, S_{t-1} + (riferimento - r_t) - k): cresce quando il trade
    rende MENO del riferimento, torna a zero quando rende di piu'. Allarme
    quando S_t >= h. Ritorna (allarme, statistica finale, indice del PRIMO
    allarme o None). Pura: nessuna soglia letta dal paper."""
    s, idx = 0.0, None
    for i, r in enumerate(rs):
        s = max(0.0, s + (float(riferimento) - float(r)) - float(k))
        if idx is None and s >= float(h):
            idx = i
    return idx is not None, round(s, 4), idx


def cusum_ripresa(rs: Iterable[float], riferimento: float, h: float = CUSUM_RIPRESA,
                  k: float = CUSUM_K) -> tuple[bool, float, int | None]:
    """Lo specchio di `cusum_r`, da usare sui trade DOPO un allarme: S_t =
    max(0, S_{t-1} + (r_t - riferimento) - k), ripresa quando S_t >= h (2,5R
    cumulati sopra la promessa). Ritorna (ripresa, statistica, indice)."""
    s, idx = 0.0, None
    for i, r in enumerate(rs):
        s = max(0.0, s + (float(r) - float(riferimento)) - float(k))
        if idx is None and s >= float(h):
            idx = i
    return idx is not None, round(s, 4), idx


def sprt_tp1(hit_flags: Iterable[bool], p0: float = SPRT_P0, p1: float = SPRT_P1,
             alpha: float = SPRT_ALPHA, beta: float = SPRT_BETA) -> tuple[str, float, int | None]:
    """Test sequenziale di Wald su «ha toccato TP1» (H0: p = p0 sano contro
    H1: p = p1 degradato). Ritorna ("accept" | "reject" | "continue", log-
    verosimiglianza cumulata, indice della decisione o None): "reject" = si
    rifiuta H0, il pool tocca TP1 meno del promesso; "accept" = sano.
    Una volta decisa, la decisione resta (il test si ferma: e' un SPRT, non
    un contatore scorrevole). Pura."""
    p0, p1 = float(p0), float(p1)
    if not (0.0 < p1 < p0 < 1.0):
        return "continue", 0.0, None
    a = math.log((1.0 - float(beta)) / float(alpha))
    b = math.log(float(beta) / (1.0 - float(alpha)))
    l_hit = math.log(p1 / p0)
    l_miss = math.log((1.0 - p1) / (1.0 - p0))
    llr, esito, idx = 0.0, "continue", None
    for i, hit in enumerate(hit_flags):
        llr += l_hit if hit else l_miss
        if llr >= a:
            esito, idx = "reject", i
            break
        if llr <= b:
            esito, idx = "accept", i
            break
    return esito, round(llr, 4), idx


def stato_pool(rs: Iterable[float], riferimento: float, h: float = CUSUM_H,
               h_ripresa: float = CUSUM_RIPRESA, k: float = CUSUM_K) -> dict:
    """Ripercorre la sequenza di R di un pool con le due fasi: NORMALE (CUSUM
    verso il basso, `cusum_r`) e ALLARME (CUSUM di ripresa, `cusum_ripresa`).
    All'allarme si entra in fase allarme e la statistica di ripresa riparte da
    zero; alla ripresa si torna in fase normale con la statistica azzerata (un
    pool puo' suonare piu' volte in una finestra: `allarmi` li conta tutti).

    Ritorna {allarme, ripresa, cusum, cusum_ripresa, indice_allarme,
    indice_ripresa, allarmi}: `allarme` = almeno un allarme nella sequenza,
    `ripresa` = l'ULTIMO allarme si e' chiuso con una ripresa (quindi niente
    freno), gli indici sono dell'ultimo allarme / ultima ripresa."""
    s_giu = s_su = 0.0
    fase = "normale"
    allarmi, i_all, i_rip = 0, None, None
    for i, r in enumerate(rs):
        r = float(r)
        if fase == "normale":
            s_giu = max(0.0, s_giu + (float(riferimento) - r) - float(k))
            if s_giu >= float(h):
                fase, allarmi, i_all, s_su = "allarme", allarmi + 1, i, 0.0
        else:
            s_su = max(0.0, s_su + (r - float(riferimento)) - float(k))
            if s_su >= float(h_ripresa):
                fase, i_rip, s_giu = "normale", i, 0.0
    return {"allarme": allarmi > 0, "ripresa": allarmi > 0 and fase == "normale",
            "cusum": round(s_giu, 4), "cusum_ripresa": round(s_su, 4),
            "indice_allarme": i_all, "indice_ripresa": i_rip, "allarmi": allarmi}


def stop_originale(t: dict) -> float | None:
    """Lo stop che DEFINISCE R: `orig_stop` (dal 25 set 2026 sul trade chiuso),
    altrimenti ricostruito da `post_mortem.stop_pct`; None se non c'e' ne'
    l'uno ne' l'altro (il trade si salta: `stop_price` alla chiusura e' spesso
    gia' a pareggio e darebbe un R falsato). Stessa scala di priorita' di
    scripts/mfe_report.stop_originale, senza l'ultimo ripiego."""
    try:
        entry = float(t.get("entry_price") or 0)
    except (TypeError, ValueError):
        return None
    if entry <= 0:
        return None
    try:
        if t.get("orig_stop"):
            return float(t["orig_stop"])
    except (TypeError, ValueError):
        pass
    pm = t.get("post_mortem") or {}
    frac = pm.get("stop_pct") if isinstance(pm, dict) else None
    try:
        frac = float(frac) if frac is not None else None
    except (TypeError, ValueError):
        return None
    if not frac or frac <= 0:
        return None
    long = str(t.get("direction", "long")).lower() != "short"
    return entry * (1.0 - frac) if long else entry * (1.0 + frac)


def r_multiplo(t: dict) -> float | None:
    """Il PnL del trade in unita' di R: pnl / (|entry - orig_stop| x size).
    None se lo stop originale o la size non ci sono (il trade non entra nei
    pool: meglio un campione piu' piccolo che un R inventato)."""
    stop = stop_originale(t)
    if stop is None:
        return None
    try:
        entry = float(t.get("entry_price") or 0)
        size = float(t.get("size") or 0)
        pnl = float(t.get("pnl", 0) or 0)
    except (TypeError, ValueError):
        return None
    rischio = abs(entry - stop) * size
    if rischio <= 0:
        return None
    return pnl / rischio


def tocca_tp1(t: dict) -> bool | None:
    """True se il prezzo ha toccato il primo gradino della scala di QUESTO trade
    (`mfe_r` >= min(`scale_r_mults`), ripiego sulla scala globale); None senza
    mfe: non si inventa un esito."""
    mfe = t.get("mfe_r")
    if mfe is None:
        return None
    try:
        mfe = float(mfe)
    except (TypeError, ValueError):
        return None
    mults = t.get("scale_r_mults") or settings.SCALE_OUT_R_MULTIPLES
    try:
        rung = float(min(float(m) for m in mults))
    except (TypeError, ValueError):
        return None
    return rung > 0 and mfe >= rung


def contesto_btc(market_up) -> str | None:
    """Il bucket del contesto BTC da `feats_at_entry.market_up` (1/0/None):
    «ignoto» (None) non forma un pool, per costruzione."""
    if market_up is None:
        return None
    try:
        return CTX_SU if float(market_up) >= 0.5 else CTX_GIU
    except (TypeError, ValueError):
        return None


def famiglia_di(strategy: str, specs: dict | None) -> str:
    """La famiglia della strategia dalla sua spec generata (`famiglia_spec`);
    «altro» se la spec non e' nota (strategie base, spec assente)."""
    spec = (specs or {}).get(strategy)
    if not isinstance(spec, dict):
        return "altro"
    try:
        from bot.strategies.generated import famiglia_spec
        return famiglia_spec(spec)
    except Exception:  # noqa: BLE001
        return "altro"


def chiavi_pool(t: dict, famiglie: dict[str, str]) -> list[str]:
    """I pool a cui appartiene un trade chiuso: «fam:<famiglia>|<regime>» e, se
    il contesto BTC all'ingresso e' noto, «dir:<direzione>|<btc_su|btc_giu>»."""
    out = []
    # il regime e' il valore dell'enum («sideways»); se arrivasse «Regime.SIDEWAYS»
    # (il gate scrive `str(t.regime)` nel dataset del selettore) si normalizza
    regime = str(t.get("regime_at_entry") or "").strip().split(".")[-1].lower()
    if regime:
        out.append(f"{POOL_FAM}{famiglie.get(str(t.get('strategy')), 'altro')}|{regime}")
    feats = t.get("feats_at_entry") if isinstance(t.get("feats_at_entry"), dict) else {}
    ctx = contesto_btc(feats.get("market_up"))
    direzione = str(t.get("direction") or "").lower()
    if ctx and direzione in ("long", "short"):
        out.append(f"{POOL_DIR}{direzione}|{ctx}")
    return out


def chiave_pool_famiglia(famiglia: str, regime) -> str | None:
    """La chiave del pool famiglia x regime per una DECISIONE (regime corrente)."""
    rk = str(getattr(regime, "value", regime) or "").strip().split(".")[-1].lower()
    if not rk:
        return None
    return f"{POOL_FAM}{famiglia}|{rk}"


def chiave_pool_direzione(direzione, contesto) -> str | None:
    """La chiave del pool direzione x contesto per una DECISIONE: `contesto` e'
    market_up (1/0/True/False/None) o gia' il bucket («btc_su»/«btc_giu»)."""
    d = str(getattr(direzione, "value", direzione) or "").lower()
    if d not in ("long", "short"):
        return None
    ctx = contesto if contesto in (CTX_SU, CTX_GIU) else contesto_btc(contesto)
    if ctx is None:
        return None
    return f"{POOL_DIR}{d}|{ctx}"


def expectancy_r(rec: dict) -> float | None:
    """L'attesa per trade in R che il registro promette per una coppia, da
    `last_pf` e `last_win_rate` con la perdita media posta a 1R: PF = wr*W /
    ((1-wr)*1) -> W = PF*(1-wr)/wr, e attesa = wr*W - (1-wr) = (1-wr)*(PF-1).
    E' una derivazione dichiarata, non una misura: dal vivo le perdite medie
    sono spesso sotto 1R (pareggio, trailing), quindi e' un riferimento
    generoso — il CUSUM misura il deficit rispetto a QUESTA promessa. None se
    manca uno dei due numeri."""
    try:
        pf = float(rec.get("last_pf", 0) or 0)
        wr = rec.get("last_win_rate")
        wr = float(wr) if wr is not None else None
    except (TypeError, ValueError, AttributeError):
        return None
    if pf <= 0 or wr is None or not (0.0 < wr < 1.0):
        return None
    return (1.0 - wr) * (min(pf, 99.0) - 1.0)


def riferimento_pool(chiave: str, pairs: dict, famiglie: dict[str, str],
                     validated=None) -> tuple[float, str, int]:
    """(riferimento in R, nota, coppie usate) per un pool: media delle attese
    (`expectancy_r`) delle coppie validate del pool — per «fam:» le coppie la
    cui strategia e' di quella famiglia, per «dir:» tutte (il registro non
    promette per direzione). Se nessuna coppia e' derivabile: 0.0, e la nota
    lo dice (non si inventa una promessa)."""
    chiavi = list(validated) if validated else list((pairs or {}).keys())
    fam = None
    if chiave.startswith(POOL_FAM):
        fam = chiave[len(POOL_FAM):].split("|", 1)[0]
    attese = []
    for k in chiavi:
        rec = (pairs or {}).get(k)
        if not isinstance(rec, dict) or "|" not in str(k):
            continue
        strat = str(k).split("|", 1)[1]
        if fam is not None and famiglie.get(strat, "altro") != fam:
            continue
        e = expectancy_r(rec)
        if e is not None:
            attese.append(e)
    if not attese:
        return 0.0, "non derivabile dal registro (last_pf/last_win_rate assenti): 0.0", 0
    return round(sum(attese) / len(attese), 4), "media di (1-wr)*(PF-1) delle validate del pool", len(attese)


def compute_pools(rows: list[dict], pairs: dict | None, specs: dict | None = None,
                  validated=None, now: float | None = None,
                  giorni: float = POOL_GIORNI) -> tuple[dict, dict]:
    """I pool su cui scatta il freno per gruppo (26 set 2026). Ritorna
    (pool, famiglie): `pool` = {chiave: {n, r_medio, cusum, allarme, ripresa,
    dal, riferimento, riferimento_nota, coppie_riferimento, cusum_ripresa,
    allarmi, sprt, sprt_llr, tp1_n, tp1_hit}}, `famiglie` = {strategia:
    famiglia} (serve a `weight_factor` per ritrovare il pool di una decisione).

    `rows` sono i trade gia' filtrati (esiti esterni ed esplorative fuori);
    qui si tengono gli ultimi `giorni` giorni (rispetto a `now`, o all'orologio)
    in ordine di chiusura, e SOLO i trade con un R calcolabile (`r_multiplo`).
    `dal` e' l'exit_ts del trade che ha fatto suonare l'ultimo allarme."""
    import time as _time
    now = float(now) if now is not None else _time.time()
    limite = now - float(giorni) * 86400.0
    famiglie = {str(t.get("strategy")): famiglia_di(str(t.get("strategy")), specs) for t in rows}
    for k in (pairs or {}):
        if "|" in str(k):
            strat = str(k).split("|", 1)[1]
            famiglie.setdefault(strat, famiglia_di(strat, specs))
    ordinati = sorted((t for t in rows if _ts_sicuro(t.get("exit_ts")) >= limite),
                      key=lambda t: _ts_sicuro(t.get("exit_ts")))
    per_pool: dict[str, list[dict]] = defaultdict(list)
    for t in ordinati:
        r = r_multiplo(t)
        if r is None:
            continue
        for ch in chiavi_pool(t, famiglie):
            per_pool[ch].append({"r": r, "ts": _ts_sicuro(t.get("exit_ts")), "tp1": tocca_tp1(t)})
    out: dict[str, dict] = {}
    for ch, xs in per_pool.items():
        rif, nota, n_rif = riferimento_pool(ch, pairs or {}, famiglie, validated)
        rs = [x["r"] for x in xs]
        st = stato_pool(rs, rif, settings.POOL_CUSUM_H, settings.POOL_CUSUM_RIPRESA, CUSUM_K)
        flags = [x["tp1"] for x in xs if x["tp1"] is not None]
        esito, llr, _i = sprt_tp1(flags, settings.POOL_SPRT_P0, settings.POOL_SPRT_P1)
        out[ch] = {
            "n": len(rs), "r_medio": round(sum(rs) / len(rs), 4),
            "cusum": st["cusum"], "allarme": st["allarme"], "ripresa": st["ripresa"],
            "dal": xs[st["indice_allarme"]]["ts"] if st["indice_allarme"] is not None else None,
            "riferimento": rif, "riferimento_nota": nota, "coppie_riferimento": n_rif,
            "cusum_ripresa": st["cusum_ripresa"], "allarmi": st["allarmi"],
            "sprt": esito, "sprt_llr": llr, "tp1_n": len(flags), "tp1_hit": sum(1 for f in flags if f),
        }
    return out, famiglie


def pool_in_allarme(drift_doc: dict | None, strategy: str, regime=None,
                    contesto=None, direzione=None) -> list[str]:
    """Le chiavi dei pool di QUESTA decisione che sono in allarme senza
    ripresa: il pool famiglia x regime della strategia (se il regime e' noto)
    e il pool direzione x contesto BTC (se direzione e contesto sono noti).
    Vuoto = nessun freno di gruppo (o funzione spenta, o documento senza pool)."""
    if not settings.POOL_BRAKE_ENABLED or not drift_doc:
        return []
    pool = drift_doc.get("pool") if isinstance(drift_doc.get("pool"), dict) else {}
    if not pool:
        return []
    famiglie = drift_doc.get("pool_famiglie") if isinstance(drift_doc.get("pool_famiglie"), dict) else {}
    chiavi = [chiave_pool_famiglia(famiglie.get(str(strategy), "altro"), regime),
              chiave_pool_direzione(direzione, contesto)]
    out = []
    for ch in chiavi:
        rec = pool.get(ch) if ch else None
        if isinstance(rec, dict) and rec.get("allarme") and not rec.get("ripresa"):
            out.append(ch)
    return out


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


def compute_drift(trades: Iterable[dict], pairs: dict | None = None,
                  specs: dict | None = None, validated=None,
                  now: float | None = None) -> dict:
    """Confronta il vissuto (trade paper) con la promessa del gate (registro).

    `pairs`: mappa "SYMBOL|strategy" -> record del registro (last_pf, last_params).
    Ritorna {"pairs": {...}, "strategies": {...}, "global": {...}, "serie": {...},
    "pool": {...}, "pool_famiglie": {...}} con un verdetto per ciascuna
    granularita'. Coppie senza promessa nel registro vengono saltate: senza un
    atteso non c'e' niente da falsificare. "serie" invece copre TUTTE le
    strategie con trade, anche senza promessa: il freno di serie non confronta
    con un atteso, guarda solo se sta perdendo di fila.

    "pool" (26 set 2026, passo 4): i gruppi famiglia x regime e direzione x
    contesto BTC sugli ultimi POOL_GIORNI giorni, con CUSUM, ripresa e SPRT
    (`compute_pools`); `specs` sono le spec generate (per la famiglia: «altro»
    se ignota), `validated` le chiavi validate per il riferimento (None = tutte
    le coppie con promessa), `now` l'orologio (None = adesso). Un errore nel
    calcolo dei pool non tocca le altre granularita': pool vuoto."""
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
    try:
        pool, famiglie = compute_pools(rows, pairs, specs, validated, now)
    except Exception as exc:  # noqa: BLE001 — il freno per gruppo non ferma la deriva
        print(f"[drift] pool saltati: {exc}")
        pool, famiglie = {}, {}
    return {"pairs": out_pairs, "strategies": out_strats, "global": glob,
            "serie": serie_perdite(rows), "pool": pool, "pool_famiglie": famiglie}


def weight_factor(drift_doc: dict | None, symbol: str, strategy: str,
                  regime=None, contesto=None, direzione=None) -> float:
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
    settimane, e DRIFT_WEIGHT_FLOOR resta il pavimento di tutto.

    Il FRENO PER GRUPPO (26 set 2026, `regime`, `contesto` = market_up del BTC
    adesso, `direzione`): se un pool della decisione e' in allarme senza
    ripresa, POOL_BRAKE_FACTOR — combinato con gli altri col MINIMO, mai col
    prodotto: il globale e il pool dicono la stessa cosa («questo mercato non
    rende come promesso») a due grane, e un trade non si frena due volte per
    lo stesso motivo. Con DRIFT_ENABLED spento e' spento anche questo."""
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
    if pool_in_allarme(drift_doc, strategy, regime, contesto, direzione):
        f = min(f, float(settings.POOL_BRAKE_FACTOR))
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


def motivi_freno(drift_doc: dict | None, symbol: str, strategy: str,
                 regime=None, contesto=None, direzione=None) -> list[str]:
    """I motivi per cui weight_factor sta frenando questa coppia, in parole: vanno
    nella nota del trade, cosi' dal registro si legge PERCHE' la size era ridotta
    invece di dover ricostruire il documento di deriva di quel momento. Lista
    vuota = nessun freno (o funzione disattivata), coerente con weight_factor.
    I pool in allarme (26 set 2026) compaiono come «pool fam:...|...»."""
    if not settings.DRIFT_ENABLED or not drift_doc:
        return []
    motivi: list[str] = []
    for ch in pool_in_allarme(drift_doc, strategy, regime, contesto, direzione):
        motivi.append(f"pool {ch}")
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
