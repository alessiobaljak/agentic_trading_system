"""
IL CONTROLLO AUTOMATICO — il documento orario `dashboard/controllo` (25 set 2026).

Richiesta del proprietario: «check di status, learning, paper, gate, strategie,
tutto in automatico, e le evidenze in dashboard ogni ora». Prima ogni controllo
era un comando ops letto a mano e incrociato con altri tre: una diagnosi cosi'
cara non viene rifatta, e infatti restava non fatta per giorni.

Il contratto dei campi e' `docs/controllo_schema.md` (§1): i nomi qui sono
quelli. Questo modulo e' PURO — niente print, niente rete, niente candele —
cosi' si testa con un Firebase in memoria e lo puo' chiamare chiunque:
  * il bot (`TradingBot._publish_controllo`, gancio orario accanto ai pesi);
  * lo snapshot su GitHub (`scripts/state_snapshot.py --publish-controllo`),
    ripiego quando il bot tace da piu' di 90 minuti;
  * il comando ops `controllo` (`scripts/controllo.py`).

Tre funzioni fanno tutto:
  * `carica_dati(fb, now, trades, registro)` — SOLO letture (RTDB e Firestore),
    nessun calcolo: e' l'unica che tocca Firebase;
  * `costruisci_controllo(dati, now, generato_da, settings_da_bot, durata_ms)`
    — pura: da quei dati al documento. Ogni sezione in un try suo: se una
    fallisce porta `errore` e la lettura «sezione non calcolata», il resto esce;
  * `pubblica_controllo(fb, doc)` — Firestore `dashboard/controllo`, poi lo
    specchio RTDB `/controllo`.

Regole del documento (dal contratto): timestamp in secondi epoch, frazioni 0-1
salvo i campi `_pct`, `null` = «non misurato» (mai zero al posto di un dato che
manca), niente NaN/inf, niente liste di liste, niente `. # $ [ ] /` nelle chiavi
(`pulisci` lo garantisce), PF senza perdite = `null` col gemello `perdite: 0`.
Le letture sono frasi da regole (≤ 140 caratteri), mai da un modello.
"""
from __future__ import annotations

import math
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from statistics import median

from bot.config import settings
from bot.learning.referti import ESITI_ESTERNI, riassunto_ipotesi
from bot.learning.metrics import (KEEP_PAPER_MIN_VERDETTI, classi_stop, cost_alerts,
                                  cost_report, proposta_keep)

VERSIONE_SCHEMA = 1
#: la dashboard calcola «online» da sola con questa soglia (900 s: il market scan
#: puo' durare minuti senza battito). Il bot non scrive `online`: sarebbe sempre true.
SOGLIA_ONLINE_S = 900
#: peso sotto il quale una strategia×regime e' «in panchina» (a confidenza 60 non
#: passa piu' la soglia 30 dell'orchestratore); a 0 e' spenta.
SOGLIA_PANCHINA = 0.5
LETTURA_MAX = 140
#: caratteri che il RTDB rifiuta nelle chiavi
CHIAVI_VIETATE = frozenset(".#$[]/")
ROSSO, GIALLO, INFO, VERDE = "rosso", "giallo", "info", "verde"
SISTEMA, PAPER = "sistema", "paper"

#: nomi corti delle anomalie per la lettura di salute («1 avviso: freno globale»)
_ETICHETTA = {
    "BOT_FERMO": "bot fermo", "KILL_SWITCH_ATTIVO": "kill switch",
    "MANUTENZIONE": "manutenzione", "WAL_NON_VUOTO": "WAL non vuoto",
    "CICLO_IN_ERRORE": "cicli in errore", "RIAVVII": "riavvii",
    "GATE_IN_RITARDO": "gate in ritardo", "GATE_SFORA": "gate lento",
    "GATE_FALLITO": "gate fallito", "GATE_NON_PRONTO": "gate non pronto",
    "CONTROLLO_VECCHIO": "controllo vecchio", "REGISTRO_CALATO": "registro calato",
    "REGISTRO_PIENO": "registro pieno", "PESI_SOSPESI": "pesi sospesi",
    "STREAM_PREZZI_OFF": "stream prezzi off", "RTDB_DEGRADATO": "RTDB degradato",
    "EQUITY_NON_TORNA": "equity non torna", "PF_VISSUTO_BASSO": "PF basso",
    "FRENO_GLOBALE": "freno globale", "RISCHIO_ALTO": "rischio alto",
    "DIREZIONE_AL_TETTO": "direzione al tetto",
    "OLTRE_TETTO_POSIZIONI": "oltre il tetto posizioni",
    "CIRCUIT_BREAKER": "circuit breaker", "NESSUN_TRADE_48H": "nessun trade da 48 h",
    "SENZA_PROMESSA": "validate senza promessa", "CONTROLLO_LENTO": "controllo lento",
}


# --------------------------------------------------------------------------- #
# attrezzi                                                                     #
# --------------------------------------------------------------------------- #
def _f(v):
    """float o None: mai zero al posto di un dato che manca."""
    if v is None or isinstance(v, bool):
        return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return None if (math.isnan(x) or math.isinf(x)) else x


def _i(v):
    x = _f(v)
    return int(x) if x is not None else None


def _ts(v):
    """Epoch (float) da un numero, una stringa ISO o un datetime; None se manca."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, datetime):
        return v.timestamp()
    if isinstance(v, (int, float)):
        return _f(v)
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00")).timestamp()
    except (TypeError, ValueError):
        return None


def _giorno(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def _pnl(t: dict) -> float:
    return _f(t.get("pnl")) or 0.0


def _exit_ts(t: dict):
    return _ts(t.get("exit_ts")) or _ts(t.get("exit_time"))


def _entry_ts(t: dict):
    return _ts(t.get("entry_ts")) or _ts(t.get("entry_time"))


def _rows(trades) -> list[dict]:
    """I trade decisi dalla strategia: fuori gli esiti esterni (manual,
    kill_switch, circuit_breaker), come in `bot/learning/referti.py`."""
    return [t for t in (trades or []) if isinstance(t, dict)
            and str(t.get("exit_reason", "")) not in ESITI_ESTERNI]


def _r(v, n=2):
    x = _f(v)
    return round(x, n) if x is not None else None


def _num(v, dec=0) -> str:
    """Numero in italiano («1,5»), col segno se chiesto dal chiamante."""
    return f"{v:.{dec}f}".replace(".", ",")


def _eta(s) -> str:
    """«22 s», «5 min», «1 h 30», «2 g 3 h»."""
    s = int(max(0, s or 0))
    if s < 60:
        return f"{s} s"
    if s < 3600:
        return f"{s // 60} min"
    if s < 86400:
        h, m = divmod(s, 3600)
        return f"{h} h {m // 60:02d}" if m >= 60 else f"{h} h"
    g, r = divmod(s, 86400)
    return f"{g} g {r // 3600} h"


def taglia(testo: str, n: int = LETTURA_MAX) -> str:
    testo = " ".join(str(testo or "").split())
    return testo if len(testo) <= n else testo[: n - 1].rstrip() + "…"


def pulisci(obj):
    """Il documento PRONTO per Firestore e RTDB: NaN/inf -> None, tuple/set ->
    liste, datetime -> epoch, chiavi sempre stringhe e MAI con `. # $ [ ] /`
    (il RTDB rifiuterebbe l'intero documento). Solleva ValueError su una chiave
    vietata: meglio una sezione non pubblicata che un documento rifiutato."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            k = str(k)
            if any(c in CHIAVI_VIETATE for c in k):
                raise ValueError(f"chiave non ammessa nel documento: {k!r}")
            out[k] = pulisci(v)
        return out
    if isinstance(obj, (list, tuple, set, frozenset)):
        seq = sorted(obj) if isinstance(obj, (set, frozenset)) else obj
        return [pulisci(v) for v in seq]
    if isinstance(obj, bool) or obj is None or isinstance(obj, (str, int)):
        return obj
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if isinstance(obj, datetime):
        return obj.timestamp()
    if hasattr(obj, "value"):          # enum
        return pulisci(obj.value)
    return str(obj)


# --------------------------------------------------------------------------- #
# letture da Firebase (l'unica funzione che tocca il database)                  #
# --------------------------------------------------------------------------- #
def _figlio(fb, base: str, *chiavi):
    """Un figlio del RTDB letto con una chiamata a parte (pochi byte). Se il
    client non sa risolvere il percorso figlio (lo store in memoria dei test
    tiene i nodi come li ha scritti), ripiega sul nodo base e naviga."""
    path = base.rstrip("/") + "/" + "/".join(chiavi)
    try:
        v = fb.get_rtdb(path)
    except Exception:  # noqa: BLE001
        v = None
    if v is not None and not isinstance(v, dict):
        return v
    try:
        nodo = fb.get_rtdb(base)
    except Exception:  # noqa: BLE001
        return None
    for k in chiavi:
        if not isinstance(nodo, dict):
            return None
        nodo = nodo.get(k)
    return nodo


def carica_dati(fb, now: float, trades=None, registro=None) -> dict:
    """SOLO letture: i nodi RTDB e i documenti Firestore elencati nel contratto.

    `trades` e `registro` si passano quando chi chiama li ha gia' in mano (il
    bot): senza, si leggono qui. Un errore di lettura non ferma nulla: il dato
    resta None e finisce in `errori_lettura`, cosi' la sezione lo dice."""
    d: dict = {"now": now, "errori_lettura": []}

    def rt(path):
        try:
            return fb.get_rtdb(path)
        except Exception as exc:  # noqa: BLE001
            d["errori_lettura"].append(f"rtdb:{path}: {str(exc)[:80]}")
            return None

    def fs(coll, doc_id):
        try:
            return fb.get_doc(coll, doc_id)
        except Exception as exc:  # noqa: BLE001
            d["errori_lettura"].append(f"fs:{coll}/{doc_id}: {str(exc)[:80]}")
            return None

    d["bot_status"] = rt("/bot_status") or {}
    # il battito come FIGLIO, chiamata a parte: e' scritto nel `finally` del loop
    # e non sta nel dict che `refresh_regime` riscrive ogni ora
    d["heartbeat"] = _figlio(fb, "/bot_status", "heartbeat")
    d["avviato_at"] = _figlio(fb, "/bot_status", "avviato_at")
    d["errori_ciclo_1h"] = _figlio(fb, "/bot_status", "errori_ciclo_1h")
    d["kill_switch"] = rt("/commands/kill_switch")
    d["maintenance"] = rt("/commands/maintenance")
    d["decision_status"] = rt("/decision_status") or {}
    d["risk_state"] = rt("/risk_state") or {}
    d["adapt_state"] = rt("/adapt_state") or {}
    d["positions"] = rt("/positions") or {}
    d["unlogged"] = rt("/unlogged_trades") or {}
    d["equity"] = rt("/account/equity")
    d["starting_equity"] = rt("/account/starting_equity")
    d["paper_started_at"] = rt("/account/paper_started_at")
    d["avvii"] = rt("/avvii")
    d["btc_history"] = rt("/btc_history")
    d["precedente_at"] = _figlio(fb, "/controllo", "meta", "generato_at")
    d["impronta_precedente"] = _figlio(fb, "/controllo", "learning", "attivo", "impronta")

    d["gate"] = fs("dashboard", "gate") or {}
    d["registro"] = registro if registro is not None else (fs("strategy_registry", "validated") or {})
    d["weights"] = fs("strategy_weights", "current") or {}
    d["drift"] = fs("drift", "current") or {}
    d["calibration"] = fs("calibration", "current") or {}
    d["referti"] = fs("learning", "referti") or {}
    d["supervisor"] = fs("supervisor", "state") or {}
    d["selector"] = fs("selector", "report")
    d["ai_hypotheses"] = fs("ai_hypotheses", "last")
    d["memory"] = fs("memory", "30") or {}
    d["portfolio_backtest"] = fs("portfolio", "backtest")
    d["discovered_last_run"] = fs("strategy_params", "discovered_last_run") or {}
    try:
        d["ai_shadow"] = fb.query_collection("ai_shadow", order_by="at", limit=200) or []
    except Exception as exc:  # noqa: BLE001
        d["errori_lettura"].append(f"fs:ai_shadow: {str(exc)[:80]}")
        d["ai_shadow"] = None
    if trades is None:
        try:
            trades = fb.query_collection("trades", order_by="exit_ts", min_value=0.0) or []
        except Exception as exc:  # noqa: BLE001
            d["errori_lettura"].append(f"fs:trades: {str(exc)[:80]}")
            trades = None
    d["trades"] = trades
    try:
        d["rtdb_degradato_s"] = float(fb.degraded_for(now)) if hasattr(fb, "degraded_for") else None
    except Exception:  # noqa: BLE001
        d["rtdb_degradato_s"] = None
    return d


# --------------------------------------------------------------------------- #
# funzioni pure sui trade                                                       #
# --------------------------------------------------------------------------- #
def pf(trades) -> float | None:
    """Profit factor; None senza perdite (non 99, non inf): il gemello e' `perdite`."""
    pnls = [_pnl(t) for t in (trades or [])]
    gains = sum(p for p in pnls if p > 0)
    losses = -sum(p for p in pnls if p < 0)
    return round(gains / losses, 3) if losses > 0 else None


def giornate(trades, now: float) -> dict:
    """Le giornate (UTC, per data di uscita): quante con trade, positive,
    negative, la migliore e la peggiore, e le ultime 7 una per una (anche vuote,
    cosi' la serie ha sempre 7 punti)."""
    per: dict[str, dict] = defaultdict(lambda: {"trades": 0, "pnl": 0.0})
    for t in trades or []:
        ts = _exit_ts(t)
        if ts is None:
            continue
        g = per[_giorno(ts)]
        g["trades"] += 1
        g["pnl"] += _pnl(t)
    righe = sorted(per.items())
    positive = sum(1 for _, g in righe if g["pnl"] > 0)
    negative = sum(1 for _, g in righe if g["pnl"] < 0)
    migliore = peggiore = None
    if righe:
        d, g = max(righe, key=lambda kv: kv[1]["pnl"])
        migliore = {"data": d, "pnl": round(g["pnl"], 2)}
        d, g = min(righe, key=lambda kv: kv[1]["pnl"])
        peggiore = {"data": d, "pnl": round(g["pnl"], 2)}
    ultime = []
    for i in range(6, -1, -1):
        d = _giorno(now - i * 86400)
        g = per.get(d, {"trades": 0, "pnl": 0.0})
        ultime.append({"data": d, "trades": g["trades"], "pnl": round(g["pnl"], 2)})
    return {"con_trade": len(righe), "positive": positive, "negative": negative,
            "migliore": migliore, "peggiore": peggiore, "ultime_7": ultime}


def oggi(trades, now: float) -> dict:
    """Il giorno UTC corrente: trade, vinti, pnl, migliore e peggiore per coin."""
    d = _giorno(now)
    sel = [t for t in (trades or []) if (ts := _exit_ts(t)) is not None and _giorno(ts) == d]
    mig = peg = None
    if sel:
        t = max(sel, key=_pnl)
        mig = {"coin": str(t.get("symbol", "?")), "pnl": round(_pnl(t), 2)}
        t = min(sel, key=_pnl)
        peg = {"coin": str(t.get("symbol", "?")), "pnl": round(_pnl(t), 2)}
    return {"trades": len(sel), "vinti": sum(1 for t in sel if _pnl(t) > 0),
            "pnl": round(sum(_pnl(t) for t in sel), 2), "migliore": mig, "peggiore": peg}


def _etichette_uscita() -> dict:
    """Le etichette di `scripts/state_snapshot._EXIT_LABEL`, importate pigre
    (quel modulo tira dentro il motore di backtest). Senza, il motivo grezzo."""
    try:
        from scripts.state_snapshot import _EXIT_LABEL
        return dict(_EXIT_LABEL)
    except Exception:  # noqa: BLE001
        return {}


def uscite_per_motivo(trades) -> list[dict]:
    """[{motivo, etichetta, trades, quota, pnl}] dal piu' frequente."""
    rows = [t for t in (trades or []) if isinstance(t, dict)]
    n = len(rows)
    if not n:
        return []
    eti = _etichette_uscita()
    conta = Counter(str(t.get("exit_reason", "?")) for t in rows)
    out = []
    for motivo, c in conta.most_common():
        out.append({"motivo": motivo, "etichetta": eti.get(motivo, motivo), "trades": c,
                    "quota": round(c / n, 3),
                    "pnl": round(sum(_pnl(t) for t in rows
                                     if str(t.get("exit_reason", "?")) == motivo), 2)})
    return out


def gradini(trades) -> list[dict]:
    """[{gradino, n}] da `scale_stage_reached` (solo trade che lo portano)."""
    conta = Counter(int(_f(t.get("scale_stage_reached")) or 0) for t in (trades or [])
                    if t.get("scale_stage_reached") is not None)
    return [{"gradino": k, "n": v} for k, v in sorted(conta.items())]


def mfe_riassunto(trades) -> dict:
    """{n, mediana_r, quota_1r, quota_1_5r, quota_3r} da `mfe_r`; null senza dati."""
    vals = sorted(x for t in (trades or []) if (x := _f(t.get("mfe_r"))) is not None)
    if not vals:
        return {"n": 0, "mediana_r": None, "quota_1r": None, "quota_1_5r": None, "quota_3r": None}
    n = len(vals)
    return {"n": n, "mediana_r": round(float(median(vals)), 3),
            "quota_1r": round(sum(1 for v in vals if v >= 1.0) / n, 3),
            "quota_1_5r": round(sum(1 for v in vals if v >= 1.5) / n, 3),
            "quota_3r": round(sum(1 for v in vals if v >= 3.0) / n, 3)}


def cooldown_attivi(adapt_state, now: float) -> dict:
    """{coin: [{nome, fino_a}], strategie: [...]} dai cooldown ancora futuri."""
    adapt_state = adapt_state if isinstance(adapt_state, dict) else {}

    def _vivi(mappa):
        out = []
        for k, v in (mappa or {}).items():
            fino = _f(v)
            if fino is not None and fino > now:
                out.append({"nome": str(k), "fino_a": fino})
        return sorted(out, key=lambda r: r["nome"])

    return {"coin": _vivi(adapt_state.get("coin_cooldown")),
            "strategie": _vivi(adapt_state.get("strat_cooldown"))}


def panchina(weights_doc, soglia: float = SOGLIA_PANCHINA) -> dict:
    """I pesi strategia×regime letti come DECISIONE: sotto `soglia` la strategia
    e' in panchina (a confidenza 60 non passa la soglia 30), a 0 e' spenta."""
    doc = weights_doc if isinstance(weights_doc, dict) else {}
    ws = [w for w in (doc.get("weights") or []) if isinstance(w, dict)]
    sotto = [w for w in ws if (_f(w.get("weight")) or 0.0) < soglia]
    spente = [w for w in sotto if (_f(w.get("weight")) or 0.0) <= 0.0]
    sotto.sort(key=lambda w: (_f(w.get("weight")) or 0.0, str(w.get("strategy")), str(w.get("regime"))))
    righe = [{"strategia": str(w.get("strategy")), "regime": str(w.get("regime")),
              "peso": _r(w.get("weight"), 4), "campione": _i(w.get("sample_size")),
              "win_rate": _r(w.get("win_rate"), 3)} for w in sotto[:10]]
    return {"at": _ts(doc.get("updated_at")),
            "aggiornato_da_nota": "bot orario o notturno GitHub",
            "versione": _i(doc.get("version")),
            "campioni_sommati": _i(doc.get("trade_count_used")),
            "combinazioni": len(ws), "soglia_panchina": soglia,
            "in_panchina_n": len(sotto), "spente_n": len(spente), "in_panchina": righe}


def keep_distribuzione(pairs_validated) -> dict:
    """{distribuzione: [{valore, n}], non_rivalutate} dal keep del profit-lock
    scelto dal gate per coppia (`last_params.profit_lock_keep`). Una validata
    senza la chiave non e' un errore: e' stata validata prima del parametro."""
    recs = pairs_validated.values() if isinstance(pairs_validated, dict) else (pairs_validated or [])
    conta: dict[float, int] = {}
    senza = 0
    for rec in recs:
        lp = rec.get("last_params") if isinstance(rec, dict) else None
        v = lp.get("profit_lock_keep") if isinstance(lp, dict) else None
        v = _f(v)
        if v is None:
            senza += 1
        else:
            conta[v] = conta.get(v, 0) + 1
    return {"distribuzione": [{"valore": v, "n": n} for v, n in sorted(conta.items())],
            "non_rivalutate": senza}


def impronta(freno: bool, panchina_righe, cooldown, keep, validate: int, gate_pronto) -> dict:
    """La foto di cio' che DECIDE adesso: e' quella che si confronta col
    documento precedente per dire cosa e' cambiato."""
    return {
        "freno": bool(freno),
        "panchina": sorted(f"{r.get('strategia')}|{r.get('regime')}" for r in (panchina_righe or [])),
        "cooldown": sorted(str(c.get("nome")) for c in (cooldown or [])),
        "keep": [{"valore": k.get("valore"), "n": k.get("n")} for k in (keep or [])],
        "validate": int(validate or 0),
        "gate_pronto": bool(gate_pronto),
    }


def _keep_testo(keep) -> str:
    return ", ".join(f"{_f(k.get('valore')):g} ×{k.get('n')}" for k in (keep or [])
                     if _f(k.get("valore")) is not None) or "nessuno"


def cambiamenti_24h(imp: dict | None, prec: dict | None) -> list[str]:
    """Le differenze fra l'impronta di adesso e quella del documento precedente,
    in frasi. Vuota = «nessun pezzo del learning ha cambiato decisione»."""
    if not isinstance(imp, dict) or not isinstance(prec, dict) or not prec:
        return []
    out: list[str] = []
    if bool(imp.get("freno")) != bool(prec.get("freno")):
        out.append("freno globale ACCESO" if imp.get("freno") else "freno globale SPENTO")
    p_now, p_prev = set(imp.get("panchina") or []), set(prec.get("panchina") or [])
    out += [f"{k} in panchina" for k in sorted(p_now - p_prev)]
    out += [f"{k} fuori dalla panchina" for k in sorted(p_prev - p_now)]
    c_now, c_prev = set(imp.get("cooldown") or []), set(prec.get("cooldown") or [])
    out += [f"cooldown {k} attivo" for k in sorted(c_now - c_prev)]
    out += [f"cooldown {k} finito" for k in sorted(c_prev - c_now)]
    k_now, k_prev = _keep_testo(imp.get("keep")), _keep_testo(prec.get("keep"))
    if k_now != k_prev:
        out.append(f"keep per coppia: {k_prev} → {k_now}")
    if int(imp.get("validate") or 0) != int(prec.get("validate") or 0):
        out.append(f"validate {int(prec.get('validate') or 0)} → {int(imp.get('validate') or 0)}")
    if bool(imp.get("gate_pronto")) != bool(prec.get("gate_pronto")):
        out.append("gate pronto" if imp.get("gate_pronto") else "gate NON pronto: il bot resta flat")
    return out


def _btc_pct(ring, now: float, orizzonte_s: float):
    """Variazione % di BTC dall'anello `/btc_history` ({ts, close} orari, 200
    punti): ultimo punto contro il piu' recente di almeno `orizzonte_s` fa.
    None se l'anello non copre l'orizzonte."""
    punti = [(t, c) for p in (ring or []) if isinstance(p, dict)
             and (t := _f(p.get("ts"))) is not None and (c := _f(p.get("close"))) is not None]
    if len(punti) < 2:
        return None
    punti.sort()
    ultimo_ts, ultimo = punti[-1]
    if now - ultimo_ts > 3 * 3600:
        return None                     # anello fermo: un numero vecchio sarebbe una bugia
    prima = [(t, c) for t, c in punti if t <= now - orizzonte_s]
    if not prima or prima[-1][1] <= 0:
        return None
    return round((ultimo / prima[-1][1] - 1.0) * 100.0, 2)


def _pairs_registro(registro) -> tuple[dict, list]:
    """(pairs decodificate, chiavi validate) dal documento del registro."""
    from bot.core.firebase_client import decode_pairs
    registro = registro if isinstance(registro, dict) else {}
    pairs = decode_pairs(registro.get("pairs")) or {}
    validate = [k for k in (registro.get("validated") or []) if isinstance(k, str)]
    return pairs, validate


# --------------------------------------------------------------------------- #
# le sezioni                                                                   #
# --------------------------------------------------------------------------- #
def _salute(d: dict, now: float, generato_da: str) -> dict:
    st = d.get("bot_status") or {}
    st = st if isinstance(st, dict) else {}
    hb = _f(d.get("heartbeat")) or _f(st.get("heartbeat"))
    avviato = _f(d.get("avviato_at")) or _f(st.get("avviato_at"))
    err1h = _i(d.get("errori_ciclo_1h"))
    if err1h is None:
        err1h = _i(st.get("errori_ciclo_1h"))
    avvii = d.get("avvii")
    riavvii = None
    if isinstance(avvii, list):
        riavvii = sum(1 for a in avvii if (x := _f(a if not isinstance(a, dict) else a.get("at"))) is not None
                      and now - x <= 86400)
    dec = d.get("decision_status") or {}
    dec = dec if isinstance(dec, dict) else {}
    esito = dec.get("outcome")
    esito = "aperta" if esito in ("decided", "opened") else ("flat" if esito == "flat" else None)

    gate = d.get("gate") or {}
    gmeta = gate.get("meta") if isinstance(gate.get("meta"), dict) else {}
    gate_at = _f(gmeta.get("generato_at"))
    if gate_at is None:
        dlr = d.get("discovered_last_run") or {}
        s0, dur = _f(dlr.get("started_at")), _f(dlr.get("duration_s"))
        if s0 is not None:
            gate_at = s0 + (dur or 0.0)
    registro = d.get("registro") or {}
    registro = registro if isinstance(registro, dict) else {}
    pronto = registro.get("ready")
    pronto = bool(pronto) if pronto is not None else None

    drift = d.get("drift") or {}
    glob = drift.get("global") if isinstance(drift.get("global"), dict) else {}
    rs = d.get("risk_state") or {}
    rs = rs if isinstance(rs, dict) else {}
    cd = cooldown_attivi(d.get("adapt_state"), now)

    positions = d.get("positions") or {}
    positions = positions if isinstance(positions, dict) else {}
    pos_list = [p for p in positions.values() if isinstance(p, dict)]
    from bot.risk.daily_cap import rischio_direzione
    posizioni = []
    for sym, p in sorted(positions.items()):
        if not isinstance(p, dict):
            continue
        posizioni.append({"coin": str(p.get("symbol") or sym),
                          "direzione": str(p.get("direction") or "?").lower(),
                          "rischio_pct": _r((_f(p.get("risk_effective_pct")) or 0.0) * 100, 3),
                          "upnl": _r(p.get("unrealized_pnl"), 2)})
    wal = d.get("unlogged") or {}
    precedente_at = _f(d.get("precedente_at"))

    out = {
        "computed_at": now,
        "fonti": ["rtdb:/bot_status", "rtdb:/bot_status/heartbeat", "rtdb:/commands",
                  "rtdb:/decision_status", "rtdb:/risk_state", "rtdb:/adapt_state",
                  "rtdb:/positions", "rtdb:/unlogged_trades", "rtdb:/avvii",
                  "rtdb:/btc_history", "rtdb:/controllo/meta", "fs:dashboard/gate",
                  "fs:strategy_registry/validated", "fs:drift/current",
                  "fs:strategy_weights/current", "fs:calibration/current",
                  "fs:learning/referti", "fs:supervisor/state"],
        "lettura": "", "dettaglio": (
            "rischio per direzione = somma di risk_effective_pct delle posizioni "
            "aperte (stima: il tetto del bot usa lo stop ORIGINALE e la quantita' "
            "residua)"),
        "errore": None,
        "bot_stato": st.get("state") if isinstance(st.get("state"), str) else None,
        "heartbeat_at": hb,
        "heartbeat_eta_s": int(now - hb) if hb is not None else None,
        "soglia_online_s": SOGLIA_ONLINE_S,
        "avviato_at": avviato,
        "riavvii_24h": riavvii,
        "errori_ciclo_1h": err1h,
        "price_stream": st.get("price_stream") if isinstance(st.get("price_stream"), bool) else None,
        "dry_run": st.get("dry_run") if isinstance(st.get("dry_run"), bool) else None,
        "kill_switch": bool(d.get("kill_switch")),
        "manutenzione": bool(d.get("maintenance")),
        "regime": st.get("regime") if isinstance(st.get("regime"), str) else None,
        "fear_greed": _i(st.get("fear_greed")),
        "btc_24h_pct": _btc_pct(d.get("btc_history"), now, 24 * 3600),
        "btc_7g_pct": _btc_pct(d.get("btc_history"), now, 7 * 86400),
        "ultima_decisione_at": _f(dec.get("ts")),
        "ultima_decisione_esito": esito,
        "ultima_decisione_motivo": str(dec["reason"])[:200] if dec.get("reason") else None,
        "asset_valutati": _i(dec.get("assets_evaluated")),
        "segnali_trovati": _i(dec.get("signals_found")),
        "rifiuti_ciclo": dec.get("rifiuti_ciclo") if isinstance(dec.get("rifiuti_ciclo"), list) else None,
        "rifiuti_24h": dec.get("rifiuti_24h") if isinstance(dec.get("rifiuti_24h"), list) else None,
        "rifiuti_24h_dal": _f(dec.get("rifiuti_24h_dal")),
        "gate_ultimo_giro_at": gate_at,
        "gate_ultimo_giro_eta_s": int(now - gate_at) if gate_at is not None else None,
        "gate_stato": gmeta.get("stato") if isinstance(gmeta.get("stato"), str) else None,
        "gate_modalita": gmeta.get("modalita") if isinstance(gmeta.get("modalita"), str) else None,
        "gate_pronto": pronto,
        "registro_at": _f(registro.get("updated_at")),
        "pesi_at": _ts((d.get("weights") or {}).get("updated_at")),
        "deriva_at": _ts(drift.get("updated_at")),
        "calibrazione_at": _ts((d.get("calibration") or {}).get("updated_at")),
        "referti_at": _ts((d.get("referti") or {}).get("updated_at")),
        "supervisore_at": _ts((d.get("supervisor") or {}).get("updated_at")),
        "freno_globale": glob.get("verdict") == "drift",
        "freno_globale_dal": _f(glob.get("dal")),
        "circuit_breaker": {
            "halted_for_day": bool(rs.get("halted_for_day")),
            "paused_until_ts": _f(rs.get("paused_until_ts")),
            "macro_flat_until_ts": _f(rs.get("macro_flat_until_ts")),
            "consecutive_sl": _i(rs.get("consecutive_sl")),
            "daily_pnl_pct": _f(rs.get("daily_pnl_pct")),
        },
        "cooldown_coin": cd["coin"],
        "cooldown_strategie": cd["strategie"],
        "posizioni_aperte": len(pos_list),
        "posizioni": posizioni[:12],
        "upnl_totale": round(sum(_f(p.get("unrealized_pnl")) or 0.0 for p in pos_list), 2),
        "tetto_posizioni": int(settings.MAX_OPEN_POSITIONS),
        "tetto_posizioni_attivo": not settings.BACKTEST_PARITY,
        "rischio_aperto_pct": round(sum(_f(p.get("risk_effective_pct")) or 0.0 for p in pos_list) * 100, 3),
        "rischio_long_pct": round(rischio_direzione(pos_list, "long") * 100, 3),
        "rischio_short_pct": round(rischio_direzione(pos_list, "short") * 100, 3),
        "tetto_direzione_pct": round(float(settings.MAX_DIRECTIONAL_RISK_PCT) * 100, 3),
        "wal_non_vuoto": len(wal) if isinstance(wal, dict) else 0,
        "rtdb_degradato_s": _f(d.get("rtdb_degradato_s")) if generato_da == "bot" else None,
        "controllo_precedente_eta_s": int(now - precedente_at) if precedente_at is not None else None,
        "anomalie": [],
    }
    return out


def _trailing(trades_tutti) -> dict:
    """I verdetti trailing: tutti (anche scale_out) nei primi quattro campi; SOLO
    `exit_reason == trailing_stop` e timeframe del bot in quelli `_tf`, che sono
    i numeri con cui `metrics.proposta_keep` propone il keep al gate (stessa
    regola di `keep_dal_paper` nella discovery)."""
    tf = settings.ORCHESTRATOR_TIMEFRAME
    con = [t for t in (trades_tutti or []) if isinstance(t, dict) and t.get("trailing_verdict") is not None]
    prem = sum(1 for t in con if t.get("trailing_verdict") == "premature")
    prot = sum(1 for t in con if t.get("trailing_verdict") == "protected")
    neutri = sum(1 for t in con if t.get("trailing_verdict") == "neutral")
    tf_rows = [t for t in con if t.get("exit_reason") == "trailing_stop" and t.get("timeframe") == tf]
    prem_tf = sum(1 for t in tf_rows if t.get("trailing_verdict") == "premature")
    prot_tf = sum(1 for t in tf_rows if t.get("trailing_verdict") == "protected")
    n_prop = prem_tf + prot_tf
    return {"verdetti_totali": len(con), "prematuri": prem, "protetti": prot, "neutri": neutri,
            "verdetti_per_proposta": n_prop, "prematuri_tf": prem_tf, "protetti_tf": prot_tf,
            "proposta_paper": proposta_keep(n_prop, prem_tf, prot_tf),
            "soglia": KEEP_PAPER_MIN_VERDETTI}


def _paper(d: dict, now: float) -> dict:
    trades_tutti = [t for t in (d.get("trades") or []) if isinstance(t, dict)]
    if d.get("trades") is None:
        raise RuntimeError("trade non leggibili da Firestore")
    rows = _rows(trades_tutti)
    equity = _f(d.get("equity"))
    iniziale = _f(d.get("starting_equity"))
    iniziale_fonte = "rtdb" if iniziale is not None else "default 1000"
    iniziale = iniziale if iniziale is not None else 1000.0
    dal = _f(d.get("paper_started_at"))
    dal_fonte = "rtdb" if dal is not None else "primo trade"
    if dal is None:
        entrate = [x for t in trades_tutti if (x := _entry_ts(t)) is not None]
        dal = min(entrate) if entrate else None
    pnls = [_pnl(t) for t in rows]
    vinti = sum(1 for p in pnls if p > 0)
    perdite = sum(1 for p in pnls if p < 0)
    n = len(rows)
    pnl_rows = sum(pnls)

    # ultimi 30 giorni: i numeri del documento di deriva (quelli su cui scatta il
    # freno globale); win rate inline sugli stessi trade. PF 99 (senza perdite) -> null.
    drift = d.get("drift") or {}
    glob = drift.get("global") if isinstance(drift.get("global"), dict) else {}
    rows_30 = [t for t in rows if (x := _exit_ts(t)) is not None and x >= now - 30 * 86400]
    if glob:
        pf30 = _f(glob.get("live_pf"))
        pf30 = None if (pf30 is None or pf30 >= 99) else pf30
        ultimi = {"trades": _i(glob.get("trades")), "pnl": _f(glob.get("pnl")), "pf": pf30,
                  "win_rate": round(sum(1 for t in rows_30 if _pnl(t) > 0) / len(rows_30), 3) if rows_30 else None}
    else:
        ultimi = {"trades": len(rows_30), "pnl": round(sum(_pnl(t) for t in rows_30), 2),
                  "pf": pf(rows_30),
                  "win_rate": round(sum(1 for t in rows_30 if _pnl(t) > 0) / len(rows_30), 3) if rows_30 else None}

    pairs, validate = _pairs_registro(d.get("registro"))
    first_rung = None
    if pairs:
        first_rung = {}
        for k in validate:
            lp = (pairs.get(k) or {}).get("last_params") if isinstance(pairs.get(k), dict) else None
            mults = lp.get("scale_r_mults") if isinstance(lp, dict) else None
            try:
                if mults:
                    first_rung[k] = float(min(float(m) for m in mults))
            except (TypeError, ValueError):
                continue

    from scripts.trade_stats import direction_report   # pigro: importa l'orchestratore
    dr = direction_report(rows)

    rep = cost_report(trades_tutti, equity)
    costi = {"totale": _f(rep.get("total_cost_usdt")), "per_trade": _f(rep.get("cost_per_trade_usdt")),
             "commissioni": _f(rep.get("commission_usdt")), "spread": _f(rep.get("spread_usdt")),
             "funding": _f(rep.get("funding_usdt")), "lordo": _f(rep.get("gross_pnl_usdt")),
             "netto": _f(rep.get("net_pnl_usdt")), "break_even_pct": _f(rep.get("break_even_pct")),
             "stimati": bool(rep.get("estimated", True)), "avvisi": cost_alerts(rep) if rep else []}

    dd = conc = None
    eventi = [(x, _pnl(t)) for t in trades_tutti if (x := _exit_ts(t)) is not None]
    if eventi:
        from backtesting.engine import max_concurrent, portfolio_drawdown   # pigro: pesante
        dd, _tot = portfolio_drawdown(eventi)
        dd = round(dd, 2)
        conc = int(max_concurrent((_entry_ts(t), _exit_ts(t)) for t in trades_tutti))

    trailing = _trailing(trades_tutti)
    pb = d.get("portfolio_backtest")
    benchmark = {"btc_24h_pct": _btc_pct(d.get("btc_history"), now, 24 * 3600),
                 "btc_7g_pct": _btc_pct(d.get("btc_history"), now, 7 * 86400),
                 "nota": ("BTC dall'anello orario /btc_history (200 ore): non e' il "
                          "buy&hold dal primo giorno del paper (serve Binance: ops `stato`)"),
                 "portafoglio": ({"lettura": str(pb.get("lettura"))[:300] if pb.get("lettura") else None,
                                  "updated_at": _ts(pb.get("updated_at"))}
                                 if isinstance(pb, dict) and pb else None)}

    return {
        "computed_at": now,
        "fonti": ["fs:trades", "rtdb:/account", "fs:drift/current", "rtdb:/btc_history",
                  "fs:strategy_registry/validated", "fs:portfolio/backtest"],
        "lettura": "",
        "dettaglio": ("trades/vinti/perdite/win_rate/pf/expectancy sui trade decisi dalla "
                      "strategia (fuori manual/kill_switch/circuit_breaker); pnl_realizzato "
                      "su TUTTI i trade chiusi, com'e' nell'equity"),
        "errore": None,
        "equity": equity,
        "equity_iniziale": iniziale, "equity_iniziale_fonte": iniziale_fonte,
        "paper_dal": dal, "paper_dal_fonte": dal_fonte,
        "giorni_paper": int((now - dal) / 86400) if dal is not None else None,
        "rendimento_pct": round((equity / iniziale - 1.0) * 100, 2) if (equity is not None and iniziale > 0) else None,
        "trades": n, "vinti": vinti, "perdite": perdite,
        "win_rate": round(vinti / n, 3) if n else None,
        "pnl_realizzato": round(sum(_pnl(t) for t in trades_tutti), 2),
        "pf_vissuto": pf(rows),
        "expectancy": round(pnl_rows / n, 3) if n else None,
        "ultimi_30g": ultimi,
        "oggi": oggi(rows, now),
        "giornate": giornate(rows, now),
        "uscite": uscite_per_motivo(trades_tutti),
        "gradini": gradini(trades_tutti),
        "mfe": mfe_riassunto(trades_tutti),
        "stop": classi_stop(trades_tutti, first_rung),
        "direzione": dr["per_direzione"],
        "allineamento": dr["allineamento"],
        "costi": costi,
        "drawdown_portafoglio": dd,
        "max_posizioni_insieme": conc,
        "trailing": trailing,
        "benchmark": benchmark,
    }


def _attivo(d: dict, now: float, paper: dict) -> dict:
    drift = d.get("drift") or {}
    glob = drift.get("global") if isinstance(drift.get("global"), dict) else {}
    verdetto = glob.get("verdict") if isinstance(glob.get("verdict"), str) else None
    atteso = _f(glob.get("expected_pf"))
    pf_vissuto = _f(glob.get("live_pf"))
    pf_vissuto = None if (pf_vissuto is None or pf_vissuto >= 99) else pf_vissuto
    freno = {
        "attivo": bool(settings.DRIFT_ENABLED and verdetto == "drift"),
        "verdetto": verdetto, "trades": _i(glob.get("trades")),
        "pf_vissuto": pf_vissuto, "pf_atteso": atteso,
        "pf_atteso_nota": "media semplice dei last_pf del registro",
        "soglia_uscita_pf": round(atteso * float(settings.DRIFT_PF_RATIO), 3) if atteso else None,
        "size_x": float(settings.DRIFT_WEIGHT_FACTOR),
        "leva_x_min": 0.5,
        "motivo": str(glob.get("reason"))[:200] if glob.get("reason") else None,
        "dal": _f(glob.get("dal")),
    }
    registro = d.get("registro") or {}
    registro = registro if isinstance(registro, dict) else {}
    pronto = registro.get("ready")
    pronto = bool(pronto) if pronto is not None else None
    pesi = panchina(d.get("weights"), SOGLIA_PANCHINA)
    pairs, validate = _pairs_registro(registro)
    keep = keep_distribuzione({k: pairs[k] for k in validate if isinstance(pairs.get(k), dict)})
    serie = drift.get("serie") if isinstance(drift.get("serie"), dict) else {}
    righe_serie = sorted(((str(k), int(v)) for k, v in serie.items()
                          if _f(v) is not None and int(_f(v)) >= 2),
                         key=lambda kv: (-kv[1], kv[0]))[:5]
    cd = cooldown_attivi(d.get("adapt_state"), now)
    from bot.learning.calibration import confidence_trust
    imp = impronta(freno["attivo"], pesi["in_panchina"], cd["coin"] + cd["strategie"],
                   keep["distribuzione"], len(validate), pronto)
    prec = d.get("impronta_precedente")
    return {
        "computed_at": now,
        "fonti": ["fs:drift/current", "fs:strategy_weights/current",
                  "fs:strategy_registry/validated", "rtdb:/adapt_state",
                  "fs:calibration/current", "rtdb:/controllo/learning/attivo/impronta",
                  "settings"],
        "lettura": "", "errore": None,
        "freno_globale": freno,
        "gate_pronto": pronto,
        "pesi": pesi,
        "tilt": {"trend_enabled": bool(settings.TREND_TILT_ENABLED),
                 "trend_strength": float(settings.TREND_TILT_STRENGTH),
                 "trend_floor": float(settings.TREND_TILT_FLOOR),
                 "sentiment_enabled": bool(settings.SENTIMENT_TILT_ENABLED),
                 "sentiment_strength": float(settings.SENTIMENT_TILT_STRENGTH)},
        "keep_per_coppia": keep,
        "freno_serie": {"enabled": bool(settings.STREAK_BRAKE_ENABLED),
                        "perdite_soglia": int(settings.STREAK_BRAKE_LOSSES),
                        "fattore": float(settings.STREAK_BRAKE_FACTOR),
                        "serie": [{"strategia": k, "perdite": v} for k, v in righe_serie]},
        "tetti": {"coin_giorno_pct": round(float(settings.RISK_PER_COIN_DAY) * 100, 3),
                  "direzione_pct": round(float(settings.MAX_DIRECTIONAL_RISK_PCT) * 100, 3),
                  "max_posizioni": int(settings.MAX_OPEN_POSITIONS),
                  "max_posizioni_attivo": not settings.BACKTEST_PARITY,
                  "correlate_max": int(settings.MAX_CORRELATED_POSITIONS)},
        "cooldown_attivi": len(cd["coin"]) + len(cd["strategie"]),
        "calibrazione_trust": _f(confidence_trust(d.get("calibration") or {})),
        "impronta": imp,
        "cambiamenti_24h": cambiamenti_24h(imp, prec if isinstance(prec, dict) else None),
    }


def _misurato(d: dict, now: float, paper: dict) -> dict:
    drift = d.get("drift") or {}
    pairs = drift.get("pairs") if isinstance(drift.get("pairs"), dict) else {}
    righe = [(k, v) for k, v in pairs.items() if isinstance(v, dict)]
    ordine = {"drift": 0, "watch": 1, "ok": 2}
    righe.sort(key=lambda kv: (ordine.get(kv[1].get("verdict"), 3), -(_i(kv[1].get("trades")) or 0), kv[0]))
    top = []
    for k, v in righe[:10]:
        pfv = _f(v.get("live_pf"))
        top.append({"coppia": k, "verdetto": v.get("verdict"), "trades": _i(v.get("trades")),
                    "pf_vissuto": None if (pfv is None or pfv >= 99) else pfv,
                    "pf_atteso": _f(v.get("expected_pf")),
                    "motivo": str(v.get("reason"))[:120] if v.get("reason") else None})
    deriva = {"at": _ts(drift.get("updated_at")),
              "coppie_ok": sum(1 for _, v in righe if v.get("verdict") == "ok"),
              "coppie_watch": sum(1 for _, v in righe if v.get("verdict") == "watch"),
              "coppie_drift": sum(1 for _, v in righe if v.get("verdict") == "drift"),
              "soglia_coppia": int(settings.DRIFT_MIN_TRADES_PAIR),
              "soglia_strategia": int(settings.DRIFT_MIN_TRADES_STRATEGY),
              "max_trades_coppia": max((_i(v.get("trades")) or 0 for _, v in righe), default=None),
              "top": top}
    cal = d.get("calibration") or {}
    cal = cal if isinstance(cal, dict) else {}
    calibrazione = {"at": _ts(cal.get("updated_at")), "verdetto": cal.get("verdict"),
                    "trades": _i(cal.get("trades")), "correlazione": _f(cal.get("correlation")),
                    "trust": _f(cal.get("trust")), "nota": str(cal.get("note"))[:200] if cal.get("note") else None}
    ref = d.get("referti") or {}
    ref = ref if isinstance(ref, dict) else {}
    pdir = ref.get("per_direzione") if isinstance(ref.get("per_direzione"), dict) else {}

    def _somma(campo):
        return sum(_i((pdir.get(k) or {}).get(campo)) or 0 for k in ("long", "short"))

    referti = {"n_con_referto": _i(ref.get("n_con_referto")),
               "persi_con_referto": _i(ref.get("n_persi_con_referto")),
               "ingresso": _somma("ingresso"), "uscita": _somma("uscita"),
               "protezione": _somma("protezione"), "stop_largo": _somma("stop_largo"),
               "lock_mai": _somma("lock_mai"), "controtrend": _somma("controtrend"),
               "ipotesi": [taglia(r, 120) for r in riassunto_ipotesi(ref)[:5]]}
    sel = d.get("selector")
    selettore = None
    if isinstance(sel, dict) and sel:
        verd = sel.get("verdetti") if isinstance(sel.get("verdetti"), dict) else {}
        selettore = {"at": _ts(sel.get("updated_at")),
                     "verdetti": {str(f).replace(".", "_"): str((v or {}).get("verdetto"))
                                  for f, v in verd.items() if isinstance(v, dict)},
                     "nota": str(sel.get("nota"))[:200] if sel.get("nota") else None}
    ombra = None
    shadow = d.get("ai_shadow")
    if isinstance(shadow, list) and shadow:
        ats = [x for s in shadow if isinstance(s, dict) and (x := _f(s.get("at"))) is not None]
        ombra = {"n": len(shadow),
                 "agree": sum(1 for s in shadow if isinstance(s, dict) and s.get("verdict") == "agree"),
                 "ultimo_at": max(ats) if ats else None}
    ipo = d.get("ai_hypotheses")
    ipotesi_ai = ({"proposte": _i(ipo.get("proposte")), "accettate": _i(ipo.get("accettate")),
                   "at": _f(ipo.get("at"))} if isinstance(ipo, dict) and ipo else None)
    mem = d.get("memory") or {}
    return {
        "computed_at": now,
        "fonti": ["fs:drift/current", "fs:calibration/current", "fs:learning/referti",
                  "fs:selector/report", "fs:ai_shadow", "fs:ai_hypotheses/last", "fs:memory/30"],
        "lettura": "", "errore": None,
        "deriva": deriva,
        "calibrazione": calibrazione,
        "trailing": paper.get("trailing") if isinstance(paper, dict) and not paper.get("errore") else None,
        "referti": referti,
        "selettore": selettore,
        "ombra_ai": ombra,
        "ipotesi_ai": ipotesi_ai,
        "notturno_at": _ts(mem.get("generated_at")) if isinstance(mem, dict) else None,
    }


# --------------------------------------------------------------------------- #
# anomalie e semafori                                                           #
# --------------------------------------------------------------------------- #
def anomalie(salute: dict, paper: dict, attivo: dict, dati: dict, now: float,
             durata_ms=None) -> list[dict]:
    """Le anomalie del contratto (§1.6), da regole. Una sezione fallita non
    produce anomalie (i suoi campi mancano): il semaforo non inventa."""
    s = salute if isinstance(salute, dict) and not salute.get("errore") else {}
    p = paper if isinstance(paper, dict) and not paper.get("errore") else {}
    a = attivo if isinstance(attivo, dict) and not attivo.get("errore") else {}
    out: list[dict] = []

    def add(codice, famiglia, gravita, testo, valore=None, soglia=None):
        out.append({"codice": codice, "famiglia": famiglia, "gravita": gravita,
                    "testo": taglia(testo, 200), "valore": valore, "soglia": soglia})

    if s:
        eta = s.get("heartbeat_eta_s")
        if not s.get("manutenzione"):
            if eta is None:
                add("BOT_FERMO", SISTEMA, ROSSO, "battito del bot mai visto su /bot_status/heartbeat",
                    None, SOGLIA_ONLINE_S)
            elif eta > SOGLIA_ONLINE_S:
                add("BOT_FERMO", SISTEMA, ROSSO, f"nessun battito da {_eta(eta)}", eta, SOGLIA_ONLINE_S)
        if s.get("kill_switch"):
            add("KILL_SWITCH_ATTIVO", SISTEMA, GIALLO, "kill switch attivo: nessuna nuova posizione", True, False)
        if s.get("manutenzione"):
            add("MANUTENZIONE", SISTEMA, INFO, "bot in manutenzione (commands/maintenance)", True, False)
        if (s.get("wal_non_vuoto") or 0) > 0:
            add("WAL_NON_VUOTO", SISTEMA, ROSSO,
                f"{s['wal_non_vuoto']} trade chiusi nel WAL non ancora su Firestore", s["wal_non_vuoto"], 0)
        if (s.get("errori_ciclo_1h") or 0) > 3:
            add("CICLO_IN_ERRORE", SISTEMA, GIALLO, f"{s['errori_ciclo_1h']} cicli in errore nell'ultima ora",
                s["errori_ciclo_1h"], 3)
        if (s.get("riavvii_24h") or 0) > 3:
            add("RIAVVII", SISTEMA, GIALLO, f"{s['riavvii_24h']} riavvii del bot in 24 h", s["riavvii_24h"], 3)
        gate = dati.get("gate") or {}
        gmeta = gate.get("meta") if isinstance(gate.get("meta"), dict) else {}
        durata = _f(gmeta.get("durata_s")) or 0.0
        geta = s.get("gate_ultimo_giro_eta_s")
        if geta is not None:
            if geta > 6 * 3600:
                add("GATE_IN_RITARDO", SISTEMA, ROSSO, f"ultimo giro del gate {_eta(geta)} fa", geta, 6 * 3600)
            elif geta > 3 * 3600 + durata:
                add("GATE_IN_RITARDO", SISTEMA, GIALLO, f"ultimo giro del gate {_eta(geta)} fa",
                    geta, int(3 * 3600 + durata))
        if durata > 3 * 3600:
            add("GATE_SFORA", SISTEMA, GIALLO, f"il giro del gate e' durato {_eta(durata)} (piu' di 3 h)",
                int(durata), 3 * 3600)
        if s.get("gate_stato") == "errore":
            add("GATE_FALLITO", SISTEMA, ROSSO, "l'ultimo giro del gate e' finito in errore", "errore", None)
        if s.get("gate_pronto") is False:
            add("GATE_NON_PRONTO", SISTEMA, ROSSO, "registro non pronto (ready=false): il bot resta flat", False, True)
        ceta = s.get("controllo_precedente_eta_s")
        if ceta is not None and ceta > 7200:
            add("CONTROLLO_VECCHIO", SISTEMA, GIALLO, f"controllo precedente di {_eta(ceta)} fa", ceta, 7200)
        greg = gate.get("registro") if isinstance(gate.get("registro"), dict) else {}
        occ, lim = _f(greg.get("occupazione")), _f(greg.get("limite"))
        if occ is not None and lim and occ >= 0.8 * lim:
            add("REGISTRO_PIENO", SISTEMA, GIALLO, f"registro a {int(occ)}/{int(lim)} coppie", occ, 0.8 * lim)
        pesi_at, deriva_at = s.get("pesi_at"), s.get("deriva_at")
        if pesi_at is not None and deriva_at is not None and now - pesi_at > 7200 and now - deriva_at < 7200:
            add("PESI_SOSPESI", SISTEMA, GIALLO,
                f"pesi fermi da {_eta(now - pesi_at)} mentre la deriva e' fresca: ricalcolo sospeso?",
                int(now - pesi_at), 7200)
        if s.get("price_stream") is False:
            add("STREAM_PREZZI_OFF", SISTEMA, GIALLO, "stream prezzi spento: il bot usa le candele REST", False, True)
        if (s.get("rtdb_degradato_s") or 0) > 60:
            add("RTDB_DEGRADATO", SISTEMA, GIALLO, f"RTDB muto da {_eta(s['rtdb_degradato_s'])}",
                s["rtdb_degradato_s"], 60)
        if s.get("rischio_aperto_pct", 0) > 6:
            add("RISCHIO_ALTO", PAPER, ROSSO, f"rischio aperto {_num(s['rischio_aperto_pct'], 2)}% dell'equity",
                s["rischio_aperto_pct"], 6)
        tetto = s.get("tetto_direzione_pct") or 0
        if tetto > 0:
            for lato in ("long", "short"):
                v = s.get(f"rischio_{lato}_pct") or 0
                if v >= tetto:
                    add("DIREZIONE_AL_TETTO", PAPER, GIALLO,
                        f"rischio {lato} {_num(v, 2)}% al tetto {_num(tetto, 2)}%", v, tetto)
        if s.get("tetto_posizioni_attivo") and (s.get("posizioni_aperte") or 0) > (s.get("tetto_posizioni") or 0):
            add("OLTRE_TETTO_POSIZIONI", PAPER, GIALLO,
                f"{s['posizioni_aperte']} posizioni aperte oltre il tetto {s['tetto_posizioni']}",
                s["posizioni_aperte"], s["tetto_posizioni"])
        cb = s.get("circuit_breaker") or {}
        if cb.get("halted_for_day") or (cb.get("paused_until_ts") or 0) > now or (cb.get("macro_flat_until_ts") or 0) > now:
            add("CIRCUIT_BREAKER", PAPER, GIALLO, "circuit breaker attivo (fermo per oggi / pausa / macro flat)", True, False)

    # REGISTRO_CALATO: validate di adesso contro quelle del controllo precedente
    prec = dati.get("impronta_precedente")
    if a and isinstance(prec, dict) and _i(prec.get("validate")):
        ora, prima = int((a.get("impronta") or {}).get("validate") or 0), int(_i(prec.get("validate")))
        if ora < 0.7 * prima:
            add("REGISTRO_CALATO", SISTEMA, ROSSO, f"validate {prima} → {ora}", ora, round(0.7 * prima, 1))
        elif ora < 0.8 * prima:
            add("REGISTRO_CALATO", SISTEMA, GIALLO, f"validate {prima} → {ora}", ora, round(0.8 * prima, 1))

    if p:
        eq = p.get("equity")
        if eq is not None:
            positions = dati.get("positions") or {}
            parziali = sum(_f(x.get("realized_partial")) or 0.0 for x in positions.values()
                           if isinstance(x, dict)) if isinstance(positions, dict) else 0.0
            atteso = (p.get("equity_iniziale") or 0.0) + (p.get("pnl_realizzato") or 0.0) + parziali
            if abs(eq - atteso) > 1.0:
                add("EQUITY_NON_TORNA", SISTEMA, GIALLO,
                    f"equity {_num(eq, 2)} contro {_num(atteso, 2)} = iniziale + pnl + fette aperte",
                    round(eq - atteso, 2), 1.0)
        u = p.get("ultimi_30g") or {}
        if (u.get("trades") or 0) >= 20 and u.get("pf") is not None and u["pf"] < 0.5:
            add("PF_VISSUTO_BASSO", PAPER, ROSSO, f"PF a 30 giorni {_num(u['pf'], 2)} su {u['trades']} trade",
                u["pf"], 0.5)
        if s and (s.get("segnali_trovati") or 0) > 0:
            trades = dati.get("trades") or []
            ultima_chiusura = max((x for t in trades if isinstance(t, dict) and (x := _exit_ts(t)) is not None),
                                  default=None)
            positions = dati.get("positions") or {}
            ultima_apertura = max((x for x0 in (positions.values() if isinstance(positions, dict) else [])
                                   if isinstance(x0, dict) and (x := _ts(x0.get("entry_time"))) is not None),
                                  default=None)
            if ((ultima_chiusura is None or now - ultima_chiusura > 48 * 3600)
                    and (ultima_apertura is None or now - ultima_apertura > 48 * 3600)):
                add("NESSUN_TRADE_48H", PAPER, GIALLO,
                    "nessuna apertura ne' chiusura da 48 h con segnali trovati (approssimata)",
                    int(now - max(x for x in (ultima_chiusura, ultima_apertura) if x is not None))
                    if (ultima_chiusura or ultima_apertura) else None, 48 * 3600)
    if a and (a.get("freno_globale") or {}).get("verdetto") == "drift":
        fg = a["freno_globale"]
        add("FRENO_GLOBALE", PAPER, GIALLO,
            f"freno globale da deriva: PF {_num(fg['pf_vissuto'] or 0, 2)} vs {_num(fg['pf_atteso'] or 0, 2)} atteso"
            + ("" if fg.get("attivo") else " (DRIFT_ENABLED=false: solo misura)"),
            fg.get("pf_vissuto"), fg.get("soglia_uscita_pf"))
    gate = dati.get("gate") or {}
    gstr = gate.get("strategie") if isinstance(gate.get("strategie"), dict) else {}
    n_op, n_sp = _i(gstr.get("n_operate")), _i(gstr.get("n_senza_promessa"))
    if n_op and n_sp is not None and n_sp / n_op > 0.3:
        add("SENZA_PROMESSA", PAPER, GIALLO, f"{n_sp} validate su {n_op} senza promessa (last_pf)",
            round(n_sp / n_op, 3), 0.3)
    # 5 s, non 2: la prima prova dalla VPS fuori dal bot (ops 0245, 25 set) ha
    # impiegato 2002 ms per le sole letture Firestore a freddo; dentro il bot
    # 1441 ms. L'anomalia deve segnalare un controllo che si e' impantanato, non
    # la latenza normale di una ventina di letture.
    if durata_ms is not None and durata_ms > 5000:
        add("CONTROLLO_LENTO", SISTEMA, GIALLO, f"il controllo ha impiegato {int(durata_ms)} ms", int(durata_ms), 5000)

    peso = {ROSSO: 0, GIALLO: 1, INFO: 2}
    out.sort(key=lambda x: (peso.get(x["gravita"], 3), x["codice"]))
    return out


def semaforo(anomalie_lista, famiglia: str) -> str:
    """rosso se una rossa, giallo se una gialla, verde altrimenti; le info non colorano."""
    grav = {a.get("gravita") for a in (anomalie_lista or []) if a.get("famiglia") == famiglia}
    if ROSSO in grav:
        return ROSSO
    if GIALLO in grav:
        return GIALLO
    return VERDE


# --------------------------------------------------------------------------- #
# letture                                                                      #
# --------------------------------------------------------------------------- #
def lettura_salute(s: dict, anomalie_lista) -> str:
    parti = []
    eta = s.get("heartbeat_eta_s")
    if eta is None:
        parti.append("Bot: battito mai visto")
    elif eta <= SOGLIA_ONLINE_S:
        parti.append(f"Bot vivo (battito {_eta(eta)} fa)")
    else:
        parti.append(f"Bot FERMO (battito {_eta(eta)} fa)")
    g = s.get("gate_ultimo_giro_eta_s")
    if g is None:
        parti.append("gate mai visto")
    else:
        mod = f" ({s['gate_modalita']})" if s.get("gate_modalita") else ""
        parti.append(f"gate {_eta(g)} fa{mod}")
    parti.append(f"{s.get('posizioni_aperte', 0)} posizioni, "
                 f"{_num(s.get('rischio_aperto_pct') or 0.0, 1)}% a rischio")
    frase = ", ".join(parti) + "."
    avvisi = [x for x in (anomalie_lista or []) if x.get("gravita") in (ROSSO, GIALLO)]
    if avvisi:
        nomi = ", ".join(_ETICHETTA.get(x["codice"], x["codice"].lower()) for x in avvisi[:3])
        frase += f" {len(avvisi)} avvis{'o' if len(avvisi) == 1 else 'i'}: {nomi}."
    else:
        frase += " Nessun avviso."
    return taglia(frase)


def lettura_paper(p: dict) -> str:
    n = int(p.get("trades") or 0)
    testo = f"{n} trade"
    if p.get("giorni_paper") is not None:
        testo += f" in {p['giorni_paper']} giorni"
    if p.get("win_rate") is not None:
        testo += f", {_num(p['win_rate'] * 100)}% vinti"
    if p.get("pnl_realizzato") is not None:
        testo += f", {_num(p['pnl_realizzato'], 2) if p['pnl_realizzato'] < 0 else '+' + _num(p['pnl_realizzato'], 2)} USDT"
    if p.get("rendimento_pct") is not None:
        r = p["rendimento_pct"]
        testo += f" ({'+' if r >= 0 else ''}{_num(r, 1)}%)"
    testo += "."
    stop = next((u for u in (p.get("uscite") or []) if u.get("motivo") == "stop_loss"), None)
    if stop and stop.get("quota") is not None:
        testo += f" Stop nel {_num(stop['quota'] * 100)}% delle uscite."
    og = p.get("oggi") or {}
    if og.get("trades"):
        v = og.get("pnl") or 0.0
        testo += f" Oggi {'+' if v >= 0 else ''}{_num(v, 2)}."
    else:
        testo += " Oggi nessun trade."
    if n < 20:
        testo += " Numeri piccoli."
    return taglia(testo)


def lettura_learning(att: dict, mis: dict) -> str:
    attivo = []
    if (att.get("freno_globale") or {}).get("attivo"):
        attivo.append("freno globale")
    n_p = (att.get("pesi") or {}).get("in_panchina_n") or 0
    if n_p:
        attivo.append(f"{n_p} strategie in panchina")
    keep = (att.get("keep_per_coppia") or {}).get("distribuzione") or []
    if keep:
        attivo.append("keep per coppia " + _keep_testo(keep))
    if att.get("cooldown_attivi"):
        attivo.append(f"{att['cooldown_attivi']} cooldown")
    if att.get("gate_pronto") is False:
        attivo.append("gate NON pronto (bot flat)")
    misurato = []
    dv = mis.get("deriva") or {}
    if (dv.get("coppie_ok") or 0) + (dv.get("coppie_watch") or 0) + (dv.get("coppie_drift") or 0):
        misurato.append("deriva")
    if (mis.get("calibrazione") or {}).get("verdetto"):
        misurato.append("calibrazione")
    tr = mis.get("trailing") or {}
    if tr.get("verdetti_totali"):
        misurato.append(f"{tr['verdetti_totali']} verdetti trailing")
    if (mis.get("referti") or {}).get("n_con_referto"):
        misurato.append("referti")
    if mis.get("selettore"):
        misurato.append("selettore")
    if (mis.get("ombra_ai") or {}).get("n"):
        misurato.append("ombra AI")

    def _frase():
        return (f"Attivo: {', '.join(attivo) or 'niente'}. "
                f"Solo misurato: {', '.join(misurato) or 'niente'}.")
    # oltre i 140 caratteri si lasciano cadere le voci «solo misurato» dalla
    # coda (le meno importanti) invece di troncare una parola a meta'
    while len(_frase()) > LETTURA_MAX and len(misurato) > 1:
        misurato.pop()
    return taglia(_frase())


def manca() -> list[dict]:
    """Cio' che il controllo NON puo' dare oggi, scritto dal codice (nessun numero
    inventato) e con la strada per averlo."""
    return [
        {"evidenza": "battito dell'agente ops",
         "perche": "vive in git (ops/heartbeat.md), non su Firebase",
         "come_avere": "leggere ops/heartbeat.md nel repo"},
        {"evidenza": "benchmark BTC buy&hold dal primo giorno del paper",
         "perche": "servono le candele di Binance (GitHub non le raggiunge): qui solo "
                   "l'anello orario /btc_history di 200 punti",
         "come_avere": "comando ops `stato` sulla VPS (state_snapshot col confronto col mercato)"},
        {"evidenza": "cosa aspetta il si' del proprietario",
         "perche": "vive in docs/backlog.md, non e' un dato del sistema",
         "come_avere": "leggere docs/backlog.md (voce F1 per il learning)"},
    ]


# --------------------------------------------------------------------------- #
# il documento                                                                 #
# --------------------------------------------------------------------------- #
def _sezione_fallita(nome: str, exc: Exception, now: float) -> dict:
    return {"computed_at": now, "fonti": [], "errore": f"{type(exc).__name__}: {str(exc)[:200]}",
            "lettura": taglia(f"sezione non calcolata: {type(exc).__name__}: {exc}")}


def costruisci_controllo(dati: dict, now: float, generato_da: str, settings_da_bot: bool,
                         durata_ms=None) -> dict:
    """Dal dict di `carica_dati` al documento del contratto (§1). Pura.

    Ogni sezione in un try suo (fail-open per sezione): una sezione fallita porta
    `errore` e la lettura «sezione non calcolata: ...», e il suo nome finisce in
    `meta.errori`; il resto del documento esce lo stesso. `settings_da_bot` dice
    se i `settings.*` letti valgono per la VPS (solo quando scrive il bot)."""
    errori: list[str] = []

    def sezione(nome, fn):
        try:
            return pulisci(fn())
        except Exception as exc:  # noqa: BLE001
            errori.append(nome)
            return _sezione_fallita(nome, exc, now)

    salute = sezione("salute", lambda: _salute(dati, now, generato_da))
    paper = sezione("paper", lambda: _paper(dati, now))
    attivo = sezione("learning.attivo", lambda: _attivo(dati, now, paper))
    misurato = sezione("learning.misurato", lambda: _misurato(dati, now, paper))
    try:
        lista = pulisci(anomalie(salute, paper, attivo, dati, now, durata_ms))
    except Exception as exc:  # noqa: BLE001
        errori.append("anomalie")
        lista = [{"codice": "ANOMALIE_NON_CALCOLATE", "famiglia": SISTEMA, "gravita": GIALLO,
                  "testo": taglia(f"anomalie non calcolate: {exc}", 200), "valore": None, "soglia": None}]
    salute["anomalie"] = lista
    if not salute.get("errore"):
        salute["lettura"] = lettura_salute(salute, lista)
    if not paper.get("errore"):
        paper["lettura"] = lettura_paper(paper)
    if not attivo.get("errore") and not misurato.get("errore"):
        lettura_l = lettura_learning(attivo, misurato)
    else:
        lettura_l = taglia("sezione non calcolata: " + "; ".join(
            x.get("errore") or "" for x in (attivo, misurato) if x.get("errore")))
    if not attivo.get("errore"):
        attivo["lettura"] = lettura_learning(attivo, misurato if not misurato.get("errore") else {})
    if not misurato.get("errore"):
        misurato["lettura"] = lettura_l

    precedente_at = _f(dati.get("precedente_at"))
    letture_fallite = list(dati.get("errori_lettura") or [])
    meta = {
        "versione_schema": VERSIONE_SCHEMA,
        "generato_at": now,
        "generato_da": generato_da,
        "durata_ms": int(durata_ms) if durata_ms is not None else None,
        "precedente_at": precedente_at,
        "semaforo_sistema": semaforo(lista, SISTEMA),
        "semaforo_paper": semaforo(lista, PAPER),
        "errori": errori + [f"lettura: {e}" for e in letture_fallite],
        "fonte_impostazioni": "processo bot" if settings_da_bot else "default repo",
    }
    learning = {
        "computed_at": now,
        "fonti": sorted(set((attivo.get("fonti") or []) + (misurato.get("fonti") or []))),
        "lettura": lettura_l,
        "errore": "; ".join(x["errore"] for x in (attivo, misurato) if x.get("errore")) or None,
        "attivo": attivo,
        "misurato": misurato,
    }
    return pulisci({"meta": meta, "salute": salute, "paper": paper,
                    "learning": learning, "manca": manca()})


def pubblica_controllo(fb, doc: dict) -> None:
    """Firestore `dashboard/controllo`, poi lo specchio RTDB `/controllo` (da cui
    il controllo successivo rilegge `meta.generato_at` e l'impronta)."""
    doc = pulisci(doc)
    fb.set_doc("dashboard", "controllo", doc)
    fb.set_rtdb("/controllo", doc)


def esegui(fb, generato_da: str, settings_da_bot: bool, trades=None, registro=None,
           now: float | None = None, pubblica: bool = False) -> dict:
    """Carica, costruisce (misurando `durata_ms`) e, se chiesto, pubblica.
    E' la sequenza che bot, snapshot e comando ops ripetono uguale."""
    now = time.time() if now is None else now
    t0 = time.time()
    dati = carica_dati(fb, now, trades=trades, registro=registro)
    doc = costruisci_controllo(dati, now, generato_da, settings_da_bot,
                               durata_ms=int((time.time() - t0) * 1000))
    if pubblica:
        pubblica_controllo(fb, doc)
    return doc
