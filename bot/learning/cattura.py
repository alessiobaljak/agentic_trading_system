"""LA CATTURA DEI DATI MANCANTI (1 ott 2026, richiesta del proprietario).

«Controlla se ci sono dati che non registriamo e che servirebbero»: per capire
PERCHE' si perde, perche' si entra tardi, perche' il trailing esce presto e
quali idee reggono dopo il gate. Questo modulo raccoglie le funzioni PURE (o
quasi: `commit_corto` chiede a git, `scrivi_riga_giorno` scrive) con cui il bot
annota sul trade e sul giorno cio' che finora andava perso.

REGOLA DI FERRO: SOLO MISURA. Niente qui decide un trade, una size, uno stop,
un'uscita, un verdetto del gate o un keep. Ogni funzione e' fail-open: con un
dato mancante ritorna None (o un dict di None), mai un'eccezione verso il
chiamante. Nessuna lettura Firestore: tutto viene da dati gia' in memoria o da
candele gia' scaricate.

Cosa c'e', per numero della richiesta:
  1. `interruttori`, `config_hash`, `commit_corto`, `versione_avvio`: con che
     codice e con quali impostazioni (NON segrete) gira il bot;
  2. `promessa_gate`: cosa prometteva il registro per la coppia all'ingresso;
  3. `verdetto_trailing_gate`: il verdetto trailing calcolato come lo calcola
     il gate (ultimo gradino e stop ORIGINALE);
  4. `misure_post_uscita`: cosa ha fatto il prezzo dopo l'uscita, per OGNI uscita;
  5. `motore_sul_trade`: il motore del gate rigiocato sullo stesso segnale;
  6. `stop_in_r`, `passo_stop`: il percorso dello stop e l'armamento del lock;
  7. `qualita_ingresso`: l'ingresso rispetto alla chiusura del segnale;
  9. `riga_giorno`, `scrivi_riga_giorno`: una riga al giorno, per sempre.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from typing import Optional

# --------------------------------------------------------------------------- #
# 1. versione e impostazioni in vigore                                         #
# --------------------------------------------------------------------------- #
#: LE IMPOSTAZIONI CHE SI FOTOGRAFANO, per NOME (1 ott 2026). Una lista scritta
#: a mano e non `dir(settings)`: le impostazioni contengono chiavi e token (Binance,
#: Telegram, Firebase, API esterne), e una foto di tutto le scriverebbe su RTDB.
#: Qui solo interruttori e soglie che cambiano il comportamento. Chi aggiunge un
#: nome deve chiedersi: «e' un segreto?». Il test `test_dati_versione` rifiuta
#: nomi con KEY/SECRET/TOKEN/ACCOUNT/URL/CHAT/WORKSPACE/MODEL.
INTERRUTTORI = (
    "DRY_RUN", "BACKTEST_PARITY", "BACKTEST_ENTRY_NEXT_OPEN", "ORCHESTRATOR_TIMEFRAME",
    "DECISIONE_SU_CHIUSURA",
    # AI
    "AI_ENABLED", "AI_SHADOW_ENABLED", "AI_VETO_ENABLED", "AI_UNIVERSE_FILTER",
    "AI_HYPOTHESES_PER_RUN",
    # il gate
    "GATE_PF_THRESHOLD", "GATE_MIN_TRADES", "GATE_MIN_OOS_WINDOWS", "GATE_CONSISTENCY_FRACTION",
    "GATE_DROP_TOP_FRAC", "GATE_MIN_PF_EX_TOP", "GATE_MIN_RECOVERY", "GATE_MIN_TOTAL_RETURN",
    "GATE_HOLDOUT_DAYS", "GATE_HOLDOUT_MIN_TRADES", "GATE_HOLDOUT_PF",
    "GATE_RECENCY_HALFLIFE_DAYS", "GATE_REGIME_MIN_PF", "GATE_REGIME_MIN_TRADES",
    "GATE_WIN_RATE_FLOOR",
    # esplorative e declassate
    "ESPLORATIVE_ENABLED", "ESPLORATIVE_MAX", "ESPLORATIVE_MAX_APERTE", "ESPLORATIVA_SIZE_MULT",
    "DECLASSATE_ENABLED", "DECLASSATA_NOTTI", "DECLASSATA_SIZE_MULT",
    # i freni
    "DRIFT_ENABLED", "DRIFT_PF_RATIO", "DRIFT_WEIGHT_FACTOR", "DRIFT_WEIGHT_FLOOR",
    "POOL_BRAKE_ENABLED", "POOL_BRAKE_FACTOR", "STREAK_BRAKE_ENABLED", "STREAK_BRAKE_FACTOR",
    "STREAK_BRAKE_LOSSES", "CALIBRATION_ENABLED", "PANCHINA_PAVIMENTO", "REGIME_FILTER_ENABLED",
    "TREND_TILT_ENABLED", "SENTIMENT_TILT_ENABLED", "CORRELATION_GUARD_ENABLED",
    # rischio
    "MAX_OPEN_POSITIONS", "MAX_CORRELATED_POSITIONS", "MAX_DIRECTIONAL_RISK_PCT",
    "MAX_POSITION_EQUITY_FRACTION", "MAX_STOP_PCT", "COOLDOWN_HOURS", "STRATEGY_LOSS_STREAK",
    "STRATEGY_COOLDOWN_HOURS", "RISK_PER_COIN_DAY", "DEFAULT_LEVERAGE", "DEFAULT_RISK_PER_TRADE",
    # uscite
    "SCALE_OUT_ENABLED", "SCALE_OUT_R_MULTIPLES", "SCALE_OUT_FRACTIONS",
    "SCALE_OUT_SL_TO_BREAKEVEN", "PROFIT_LOCK_ENABLED", "PROFIT_LOCK_KEEP",
    "PROFIT_LOCK_TRIGGER",
    # esecuzione e registro
    "EXEC_PRICE_STREAM_ENABLED", "EXEC_PATH_REPLAY_ENABLED", "EXEC_WICK_FILLS_ENABLED",
    "REQUIRE_GATE1_READY", "REQUIRE_VALIDATED_PAIRS", "BOOTSTRAP_TRADE_UNVALIDATED",
)

#: le tre impostazioni dell'executor lette dall'ambiente (non stanno in `settings`)
INTERRUTTORI_ENV = ("EXEC_MAX_HOLD_HOURS", "BACKTEST_COST_PER_TRADE", "BACKTEST_FUNDING_PER_8H")

_RADICE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _jsonabile(v):
    """Un valore delle impostazioni scrivibile in JSON (tuple -> liste, il resto
    che non e' un numero/testo/bool -> testo)."""
    if v is None or isinstance(v, (bool, int, float, str)):
        return v
    if isinstance(v, (list, tuple)):
        return [_jsonabile(x) for x in v]
    return str(v)


def interruttori(settings_obj=None, env=None) -> dict:
    """{nome: valore} delle impostazioni in INTERRUTTORI (e delle tre lette
    dall'ambiente). Un nome che manca vale None. Puro a parte la lettura."""
    if settings_obj is None:
        from bot.config import settings as settings_obj
    env = os.environ if env is None else env
    out: dict = {}
    for nome in INTERRUTTORI:
        try:
            out[nome] = _jsonabile(getattr(settings_obj, nome, None))
        except Exception:  # noqa: BLE001
            out[nome] = None
    for nome in INTERRUTTORI_ENV:
        try:
            out[nome] = env.get(nome)
        except Exception:  # noqa: BLE001
            out[nome] = None
    return out


def config_hash(valori: dict) -> str:
    """Impronta corta (12 caratteri) degli interruttori: due avvii con lo
    stesso numero giravano con le stesse impostazioni. Pura."""
    testo = json.dumps(valori or {}, sort_keys=True, default=str, ensure_ascii=True)
    return hashlib.sha256(testo.encode("utf-8")).hexdigest()[:12]


def commit_corto(radice: str | None = None) -> Optional[str]:
    """`git rev-parse --short HEAD` della cartella del bot. FAIL-OPEN: None se
    git manca o non risponde entro 5 secondi (mai un'eccezione)."""
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=radice or _RADICE,
                             capture_output=True, text=True, timeout=5)
        testo = (out.stdout or "").strip()
        if out.returncode == 0 and 4 <= len(testo) <= 40:
            return testo
    except Exception:  # noqa: BLE001
        pass
    return None


def versione_avvio(avviato_at: float, settings_obj=None, commit: Optional[str] = "?") -> dict:
    """{commit, config_hash, interruttori, avviato_at}: la foto di un avvio.
    `commit="?"` = chiedilo a git (default); None = sconosciuto."""
    valori = interruttori(settings_obj)
    if commit == "?":
        commit = commit_corto()
    return {"commit": commit, "config_hash": config_hash(valori),
            "interruttori": valori, "avviato_at": float(avviato_at)}


# --------------------------------------------------------------------------- #
# 2. la promessa del gate, congelata all'ingresso                              #
# --------------------------------------------------------------------------- #
def _num(v) -> Optional[float]:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f else None          # NaN cade qui


#: i campi del record del registro copiati sul trade (nome sul trade: nome nel record)
_CAMPI_PROMESSA = ("pass_count", "fail_count", "last_pf", "last_win_rate", "last_t",
                   "last_trades", "val_t", "val_trades", "validated_at", "last_passed_at")
#: i campi del record che l'adattamento tiene in RAM per la promessa
CAMPI_RECORD_PROMESSA = _CAMPI_PROMESSA + ("declassata", "generated")


def promessa_gate(rec: Optional[dict], spec=None, generata: bool = True,
                  esplorativa_rec: Optional[dict] = None) -> Optional[dict]:
    """La promessa del gate per UNA coppia, compatta (pochi numeri): cosa diceva
    il registro quando il trade e' stato aperto. Il registro si riscrive a ogni
    giro, quindi senza questa copia «il gate prometteva PF 1,6 con 4 conferme»
    non si poteva piu' dire a trade chiuso. Pura; None se non c'e' niente.

    `rec`: il record della coppia in `strategy_registry/validated.pairs`;
    `spec`: la spec della strategia generata (per l'origine, vedi
    `bot.core.registry.origine_spec`); `esplorativa_rec`: il record della coppia
    nel registro esplorativo (pf, trade, quanto mancava, criterio)."""
    try:
        out: dict = {}
        if isinstance(rec, dict):
            for k in _CAMPI_PROMESSA:
                v = rec.get(k)
                if v is None:
                    continue
                f = _num(v)
                if f is not None:
                    out[k] = int(f) if k.endswith("_count") else round(f, 4)
            out["declassata"] = bool(rec.get("declassata"))
        if isinstance(esplorativa_rec, dict):
            out["esplorativa_pf"] = _num(esplorativa_rec.get("pf"))
            out["esplorativa_trades"] = _num(esplorativa_rec.get("trades"))
            out["esplorativa_shortfall"] = _num(esplorativa_rec.get("shortfall"))
            b = esplorativa_rec.get("binding")
            out["esplorativa_binding"] = str(b)[:40] if b is not None else None
            out["esplorativa_since"] = _num(esplorativa_rec.get("since"))
        if not out:
            return None
        try:
            from bot.core.registry import origine_spec
            out["origine"] = origine_spec(spec, generata=generata)
        except Exception:  # noqa: BLE001
            out["origine"] = None
        return out
    except Exception:  # noqa: BLE001
        return None


# --------------------------------------------------------------------------- #
# 3. il verdetto trailing alla maniera del gate                                #
# --------------------------------------------------------------------------- #
def verdetto_trailing_gate(during, after, entry, exit_price, orig_stop, tp_prices,
                           long: bool) -> Optional[dict]:
    """Il verdetto trailing calcolato COME IL GATE (`Backtester._trailing_verdict`
    nello scale-out): bersaglio = ULTIMO gradino della scala (`tp_prices[-1]`) e
    stop = stop ORIGINALE. Il verdetto del bot (`trailing_verdict`, che NON si
    tocca) usa `take_profit_price` e lo stop FINALE (alzato da pareggio e lock):
    sono due domande diverse, e senza questo secondo numero i «prematuri» del
    paper non si confrontavano con quelli del gate. Ritorna {verdict,
    miss_to_tp} o None se mancano scala o stop originale."""
    try:
        o = _num(orig_stop)
        tps = [x for x in (_num(p) for p in (tp_prices or [])) if x is not None]
        e, x = _num(entry), _num(exit_price)
        if o is None or not tps or e is None or x is None:
            return None
        from bot.execution.exit_logic import trailing_reason
        res = trailing_reason(during, after, e, x, o, tps[-1], long)
        return {"verdict": res.get("verdict"), "miss_to_tp": res.get("miss_to_tp")}
    except Exception:  # noqa: BLE001
        return None


# --------------------------------------------------------------------------- #
# 4. cosa ha fatto il prezzo dopo l'uscita                                     #
# --------------------------------------------------------------------------- #
#: le barre DOPO l'uscita su cui si misura (le 96 dell'orizzonte del gate)
BARRE_POST = 96
#: le barre a cui si legge la chiusura (4 = un'ora a 15m, 16 = 4 ore, 96 = 24 ore)
PUNTI_POST = (4, 16, 96)


def _ts(c) -> float:
    from bot.core.models import epoch_utc
    return epoch_utc(c.open_time)


def candele_chiuse_dopo(candles, da_ts: float, tf_s: float, now: float) -> list:
    """Le candele CHIUSE che aprono a/dopo `da_ts`, in ordine. Pura."""
    out = []
    for c in candles or []:
        try:
            t = _ts(c)
        except Exception:  # noqa: BLE001
            continue
        if t >= da_ts and t + tf_s <= now:
            out.append(c)
    out.sort(key=_ts)
    return out


def misure_post_uscita(after, exit_price, entry, orig_stop, long: bool,
                       exit_ts: float, barre: int = BARRE_POST) -> Optional[dict]:
    """Cosa ha fatto il prezzo DOPO l'uscita, in R dello stop ORIGINALE, con il
    segno della direzione del trade (positivo = sarebbe andato ancora a favore).
    Per OGNI uscita (TP, orizzonte, manuale...), non solo trailing e stop.

    `after`: candele CHIUSE che aprono a/dopo l'uscita (la candela in cui
    l'uscita e' avvenuta resta fuori: il suo massimo puo' essere di prima).
    Servono almeno `barre` candele: altrimenti None (il chiamante aspetta).
      * post_exit_mfe_r / post_exit_mae_r: la migliore escursione a favore /
        contro rispetto al prezzo d'uscita, nelle `barre` candele (>= 0);
      * post_exit_r_4b / _16b / _96b: chiusura della 4a/16a/96a candela contro
        il prezzo d'uscita;
      * t_post_mfe_s: secondi dall'uscita all'apertura della candela del
        miglior prezzo a favore.
    Se R non e' calcolabile (stop originale assente) i numeri sono None ma il
    dict c'e': il trade non resta in attesa per sempre."""
    try:
        finestra = list(after or [])[:int(barre)]
        if len(finestra) < int(barre):
            return None
        e, x, o = _num(entry), _num(exit_price), _num(orig_stop)
        R = abs(e - o) if (e is not None and o is not None) else 0.0
        vuoto = {"post_exit_mfe_r": None, "post_exit_mae_r": None,
                 **{f"post_exit_r_{n}b": None for n in PUNTI_POST}, "t_post_mfe_s": None}
        if x is None or not R or R <= 0:
            return vuoto

        def a_favore(p: float) -> float:
            return ((p - x) if long else (x - p)) / R

        best, best_c = None, None
        worst = None
        for c in finestra:
            fav = a_favore(c.high if long else c.low)
            con = a_favore(c.low if long else c.high)
            if best is None or fav > best:
                best, best_c = fav, c
            worst = con if worst is None else min(worst, con)
        out = dict(vuoto)
        out["post_exit_mfe_r"] = round(max(0.0, best), 3)
        out["post_exit_mae_r"] = round(max(0.0, -worst), 3)
        for n in PUNTI_POST:
            if len(finestra) >= n:
                out[f"post_exit_r_{n}b"] = round(a_favore(finestra[n - 1].close), 3)
        if best_c is not None and best > 0:
            out["t_post_mfe_s"] = round(max(0.0, _ts(best_c) - float(exit_ts)), 1)
        return out
    except Exception:  # noqa: BLE001
        return None


# --------------------------------------------------------------------------- #
# 5. il motore rigiocato sullo stesso segnale                                  #
# --------------------------------------------------------------------------- #
def motore_sul_trade(candles, t: dict, tf: Optional[str], now: float) -> Optional[dict]:
    """Il motore del gate (stesse regole d'uscita di `rifiutati.simula_segnale`)
    rigiocato sul segnale di QUESTO trade, dalla candela d'ingresso, con la
    scala, il keep e il break-even con cui il trade e' stato aperto, e con lo
    STESSO ingresso e lo STESSO stop originale del bot: cosi' la differenza fra
    `motore_pnl_r` e `bot_pnl_r_lordo` misura solo come sono state gestite le
    uscite (percorso dei prezzi dentro la candela, lock, orizzonte), non
    l'ingresso. Prezzo puro, niente costi: per questo accanto c'e' il R LORDO
    del bot (`gross_pnl_usdt` / rischio).

    Ritorna:
      * None: candele non ancora sufficienti (o la prima non e' quella
        d'ingresso) -> il chiamante aspetta;
      * {"motore_esito": "non_calcolabile", ...}: stop originale o ingresso
        mancanti, o candele troppo vecchie: non si riprova;
      * altrimenti motore_esito / motore_pnl_r / motore_mfe_r / motore_mae_r /
        motore_barre e bot_pnl_r_lordo."""
    try:
        from bot.learning.rifiutati import candela_di, simula_segnale, tf_secondi
        e, o = _num(t.get("entry_price")), _num(t.get("orig_stop"))
        non = {"motore_esito": "non_calcolabile", "motore_pnl_r": None, "motore_mfe_r": None,
               "motore_mae_r": None, "motore_barre": None, "bot_pnl_r_lordo": None}
        if e is None or o is None or e <= 0 or abs(e - o) <= 0:
            return non
        secs = tf_secondi(tf)
        ex = _num(t.get("exit_ts"))
        ingresso = _num(t.get("signal_candle_ts"))
        if ingresso is None and ex is not None:
            ingresso = ex - float(_num(t.get("duration_seconds")) or 0.0)
        if ingresso is None:
            return non
        ts0 = candela_di(ingresso, tf)
        dopo = candele_chiuse_dopo(candles, ts0, secs, now)
        if not dopo or abs(_ts(dopo[0]) - ts0) > 1.0:
            return None
        res = simula_segnale(dopo, t.get("direction"), e, o, t.get("take_profit_price"),
                             r_mults=t.get("scale_r_mults"),
                             keep=_num(t.get("profit_lock_keep")),
                             breakeven=(bool(t["sl_to_breakeven"])
                                        if t.get("sl_to_breakeven") is not None else None))
        if res is None:
            return non
        if not res.get("esito"):
            return None
        R = abs(e - o)
        lordo, size = _num(t.get("gross_pnl_usdt")), _num(t.get("size"))
        bot_r = round(lordo / (R * size), 3) if (lordo is not None and size) else None
        return {"motore_esito": res["esito"], "motore_pnl_r": res["pnl_r"],
                "motore_mfe_r": res["mfe_r"], "motore_mae_r": res["mae_r"],
                "motore_barre": res["barre"], "bot_pnl_r_lordo": bot_r}
    except Exception:  # noqa: BLE001
        return None


# --------------------------------------------------------------------------- #
# 6. il percorso dello stop                                                    #
# --------------------------------------------------------------------------- #
#: di quanto (in R) deve muoversi lo stop effettivo perche' si registri un passo
PASSO_STOP_R = 0.05
#: quanti passi al massimo per trade (il documento della posizione si riscrive
#: a ogni tick: 20 coppie di numeri sono ~400 byte)
MAX_PASSI_STOP = 20


def stop_in_r(stop, entry, orig_stop, long: bool) -> Optional[float]:
    """Lo stop in R dall'ingresso, col segno del trade: -1 = stop originale,
    0 = pareggio, +0,5 = mezzo R di guadagno bloccato. None se R non c'e'."""
    s, e, o = _num(stop), _num(entry), _num(orig_stop)
    if s is None or e is None or o is None:
        return None
    R = abs(e - o)
    if R <= 0:
        return None
    return round(((s - e) if long else (e - s)) / R, 3)


def passo_stop(passi: list, stop_r: Optional[float], t_s: float,
               soglia: float = PASSO_STOP_R, tetto: int = MAX_PASSI_STOP) -> bool:
    """Aggiunge {"t_s": secondi dall'ingresso, "r": stop in R} a `passi` se lo
    stop si e' mosso di almeno `soglia` R dall'ultimo passo registrato (dal -1
    dello stop originale se non ce ne sono) e c'e' ancora posto. Ritorna True
    se l'ha aggiunto. DIZIONARI e non coppie [t, r]: Firestore rifiuta le liste
    dentro le liste, e un documento rifiutato sarebbe un trade non registrato."""
    if stop_r is None or passi is None or len(passi) >= tetto:
        return False
    ultimo = -1.0
    try:
        if passi:
            ultimo = float(passi[-1]["r"])
    except (TypeError, ValueError, IndexError, KeyError):
        ultimo = -1.0
    if abs(float(stop_r) - ultimo) < soglia - 1e-12:
        return False
    passi.append({"t_s": round(float(t_s), 1), "r": round(float(stop_r), 3)})
    return True


# --------------------------------------------------------------------------- #
# 7. la qualita' dell'ingresso                                                 #
# --------------------------------------------------------------------------- #
def qualita_ingresso(asset, entry, stop, long: bool) -> dict:
    """Dallo snapshot su cui si apre (nessuna chiamata in piu'): l'ora dello
    snapshot, la chiusura su cui la regola ha deciso (`close_chiusa`), di
    quanti R l'ingresso e' peggiore di quella chiusura (positivo = entrati
    PEGGIO del segnale: piu' in alto per un long), e open interest, volume 24h
    e mark price se lo snapshot li ha. Ogni voce None se manca."""
    out = {"snapshot_ts": None, "close_segnale": None, "ingresso_vs_segnale_r": None,
           "open_interest_at_entry": None, "volume_24h_at_entry": None,
           "mark_price_at_entry": None}
    try:
        ts = getattr(asset, "timestamp", None)
        if ts is not None:
            from bot.core.models import epoch_utc
            out["snapshot_ts"] = round(epoch_utc(ts), 3)
    except Exception:  # noqa: BLE001
        pass
    try:
        cs = _num(getattr(asset, "close_chiusa", None))
        out["close_segnale"] = cs
        e, s = _num(entry), _num(stop)
        if cs is not None and e is not None and s is not None and abs(e - s) > 0:
            out["ingresso_vs_segnale_r"] = round(((e - cs) if long else (cs - e)) / abs(e - s), 4)
    except Exception:  # noqa: BLE001
        pass
    for chiave, attr in (("open_interest_at_entry", "open_interest"),
                         ("volume_24h_at_entry", "volume_24h"),
                         ("mark_price_at_entry", "mark_price")):
        try:
            out[chiave] = _num(getattr(asset, attr, None))
        except Exception:  # noqa: BLE001
            pass
    return out


# --------------------------------------------------------------------------- #
# 9. una riga al giorno, per sempre                                            #
# --------------------------------------------------------------------------- #
#: la collection Firestore delle righe giornaliere (una scrittura al giorno)
COLLECTION_GIORNI = "giorni"
#: la foglia RTDB che dice «riga di quel giorno gia' scritta» (si legge al
#: massimo una volta per processo e giorno: RTDB, non la quota di Firestore)
GIORNI_FATTI = "/giorni_fatti"


def conti_vuoti() -> dict:
    """I contatori del giorno tenuti in RAM dal bot."""
    return {"cicli": 0, "decisioni": 0, "aperti": 0, "rifiutati": 0,
            "scarti_silenziosi": 0, "stream_giu_s": 0.0, "dal": None}


def riga_giorno(giorno: str, dati: dict, conti: Optional[dict], now: float,
                intervallo_s: float, versione: Optional[dict] = None,
                trades=None) -> dict:
    """La riga del giorno `giorno` (YYYY-MM-DD, ora italiana), dai `dati` del
    controllo orario (gia' letti: nessuna lettura in piu') e dai contatori del
    bot in RAM. Pura. Chiavi:
      * foto alla scrittura (`foto_at`, di solito i primi minuti del giorno
        dopo): equity, uPnL, equity a mercato, rischio aperto, posizioni
        aperte, chiusura di BTC, regime globale;
      * riavvii del giorno (dall'anello /avvii), trade chiusi del giorno;
      * dai contatori in RAM: cicli di decisione fatti contro attesi (24 h /
        intervallo), decisioni, aperti, rifiutati, scarti silenziosi, minuti
        di stream giu'. `contatori_dal`: da quando contano (un riavvio nel
        giorno li azzera: lo si dice, non si inventa). None se il bot non era
        su quel giorno;
      * versione: commit e config_hash dell'avvio."""
    d = dati if isinstance(dati, dict) else {}
    out: dict = {"giorno": giorno, "foto_at": float(now)}
    try:
        from bot.core.tempo import giorno_locale
    except Exception:  # noqa: BLE001
        giorno_locale = None  # type: ignore[assignment]
    # foto delle posizioni
    try:
        pos = d.get("positions") if isinstance(d.get("positions"), dict) else {}
        upnl = sum(float(p.get("unrealized_pnl") or 0.0) for p in pos.values() if isinstance(p, dict))
        rischio = sum(float(p.get("risk_effective_pct") or 0.0) for p in pos.values()
                      if isinstance(p, dict))
        eq = _num(d.get("equity"))
        out.update({"equity": eq, "upnl": round(upnl, 4),
                    "equity_a_mercato": round(eq + upnl, 4) if eq is not None else None,
                    "rischio_aperto_pct": round(rischio, 6), "posizioni_aperte": len(pos)})
    except Exception:  # noqa: BLE001
        pass
    try:
        hist = d.get("btc_history") if isinstance(d.get("btc_history"), list) else []
        ultimo = [h for h in hist if isinstance(h, dict) and _num(h.get("close")) is not None]
        out["btc_close"] = _num(ultimo[-1].get("close")) if ultimo else None
    except Exception:  # noqa: BLE001
        out["btc_close"] = None
    try:
        out["regime_globale"] = (d.get("bot_status") or {}).get("regime")
    except Exception:  # noqa: BLE001
        out["regime_globale"] = None
    # riavvii e trade chiusi del giorno
    try:
        avvii = d.get("avvii") if isinstance(d.get("avvii"), list) else []
        out["riavvii"] = (sum(1 for a in avvii if _num(a) is not None
                              and giorno_locale(float(a)) == giorno) if giorno_locale else None)
    except Exception:  # noqa: BLE001
        out["riavvii"] = None
    try:
        lista = trades if trades is not None else d.get("trades")
        chiusi = [t for t in (lista or []) if isinstance(t, dict) and _num(t.get("exit_ts")) is not None
                  and giorno_locale(float(t["exit_ts"])) == giorno] if giorno_locale else []
        out["trade_chiusi"] = len(chiusi)
        out["pnl_chiusi"] = round(sum(float(_num(t.get("pnl")) or 0.0) for t in chiusi), 4)
    except Exception:  # noqa: BLE001
        pass
    # i contatori del bot
    c = conti if isinstance(conti, dict) else None
    out["cicli_attesi"] = int(round(86400.0 / intervallo_s)) if intervallo_s else None
    for k in ("cicli", "decisioni", "aperti", "rifiutati", "scarti_silenziosi"):
        out[k] = int(c.get(k) or 0) if c else None
    out["stream_giu_min"] = round(float(c.get("stream_giu_s") or 0.0) / 60.0, 1) if c else None
    out["contatori_dal"] = _num(c.get("dal")) if c else None
    v = versione if isinstance(versione, dict) else {}
    out["commit"] = v.get("commit")
    out["config_hash"] = v.get("config_hash")
    return out


def scrivi_riga_giorno(fb, giorno: str, riga: dict, verificato: bool) -> tuple[bool, bool]:
    """Scrive `giorni/{giorno}` (Firestore, UNA scrittura) e la foglia RTDB
    `/giorni_fatti/{giorno}`. Al primo tentativo del processo (`verificato`
    falso) guarda la foglia (RTDB): se c'e' gia', non riscrive (un riavvio
    dopo la scrittura non deve sovrascrivere i contatori con quelli vuoti).
    Ritorna (scritta_o_gia_presente, verificato). Non solleva."""
    try:
        if not verificato:
            gia = fb.get_rtdb(f"{GIORNI_FATTI}/{giorno}")
            verificato = True
            if gia:
                return True, verificato
        fb.set_doc(COLLECTION_GIORNI, giorno, riga)
        fb.set_rtdb(f"{GIORNI_FATTI}/{giorno}", float(riga.get("foto_at") or 0.0) or True)
        return True, verificato
    except Exception as exc:  # noqa: BLE001
        print(f"[giorni] riga del {giorno} non scritta ({str(exc)[:80]}): si riprova fra un'ora")
        return False, False


# --------------------------------------------------------------------------- #
# 3-4-5 insieme: cosa aggiungere a un trade chiuso dalle candele gia' scaricate #
# --------------------------------------------------------------------------- #
#: i campi «fatto» delle tre misure dopo l'uscita: assenti = ancora da fare
AT_GATE, AT_POST, AT_MOTORE = "trailing_verdict_gate_at", "post_exit_at", "motore_at"
#: le uscite per cui esiste un verdetto trailing (le stesse del verdetto del bot)
USCITE_TRAILING = ("trailing_stop", "scale_out")


def pendenti(t: dict) -> set:
    """Quali misure dopo l'uscita mancano ancora a un trade: «gate» (verdetto
    trailing alla maniera del gate, solo uscite trailing/scale_out), «post»
    (il prezzo dopo l'uscita), «motore» (il motore rigiocato). Pura."""
    if not isinstance(t, dict):
        return set()
    out = set()
    if t.get("exit_reason") in USCITE_TRAILING and AT_GATE not in t:
        out.add("gate")
    if AT_POST not in t:
        out.add("post")
    if AT_MOTORE not in t:
        out.add("motore")
    return out


def pronto_per_post(t: dict, now: float, tf_s: float, barre: int = BARRE_POST) -> bool:
    """Le `barre` candele dopo l'uscita sono gia' tutte chiuse? (Serve a non
    scaricare candele per un trade che le misure nuove non possono ancora
    completare.) Pura."""
    ex = _num(t.get("exit_ts"))
    return ex is not None and now >= ex + (int(barre) + 1) * float(tf_s)


def cattura_dopo_uscita(t: dict, candles, during, after, now: float, tf: Optional[str],
                        tf_s: float, window_s: float, long: bool) -> bool:
    """Aggiunge a `t` (il documento del trade, modificato sul posto) le misure
    nuove che le candele gia' scaricate permettono: il verdetto trailing alla
    maniera del gate (3), il prezzo dopo l'uscita (4), il motore rigiocato (5).
    Ognuna ha il suo campo «fatto» (`*_at`): finche' manca, il trade resta in
    attesa, come i verdetti di sempre. Chi non si potra' mai calcolare (dati
    mancanti, o candele che non arrivano entro due finestre) viene chiuso coi
    numeri a None, cosi' non si riscaricano candele per sempre. Ritorna True
    se ha aggiunto qualcosa. Non tocca MAI i campi esistenti
    (`trailing_verdict`, `post_stop_verdict`, ...). Mai un'eccezione."""
    try:
        quali = pendenti(t)
        if not quali:
            return False
        ex = _num(t.get("exit_ts"))
        if ex is None:
            return False
        scaduto = now - ex > 2.0 * float(window_s) + 8.0 * float(tf_s)
        cambiato = False
        if "gate" in quali and len(after or []) >= 2:
            res = verdetto_trailing_gate(during, after, t.get("entry_price"), t.get("exit_price"),
                                         t.get("orig_stop"), t.get("tp_prices"), long)
            if res is None:
                t["trailing_verdict_gate"], t["trailing_miss_to_tp_gate"] = None, None
                t[AT_GATE] = float(now)
                cambiato = True
            elif not (res["verdict"] == "neutral" and now - ex < window_s):
                # stessa regola del verdetto del bot: premature/protected sono
                # definitivi subito, «neutral» solo a finestra piena
                t["trailing_verdict_gate"] = res["verdict"]
                t["trailing_miss_to_tp_gate"] = res["miss_to_tp"]
                t[AT_GATE] = float(now)
                cambiato = True
        if "post" in quali:
            dopo = candele_chiuse_dopo(candles, ex, tf_s, now)
            res = misure_post_uscita(dopo, t.get("exit_price"), t.get("entry_price"),
                                     t.get("orig_stop"), long, ex)
            if res is None and scaduto:
                res = misure_post_uscita([], None, None, None, long, ex, barre=0)  # tutto None
            if res is not None:
                t.update(res)
                t[AT_POST] = float(now)
                cambiato = True
        if "motore" in quali:
            res = motore_sul_trade(candles, t, tf, now)
            if res is None and scaduto:
                res = {"motore_esito": "non_calcolabile", "motore_pnl_r": None,
                       "motore_mfe_r": None, "motore_mae_r": None, "motore_barre": None,
                       "bot_pnl_r_lordo": None}
            if res is not None:
                t.update(res)
                t[AT_MOTORE] = float(now)
                cambiato = True
        return cambiato
    except Exception:  # noqa: BLE001
        return False
