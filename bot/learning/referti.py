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

LE QUATTRO IPOTESI (una per tipo, per strategia)
  * solo_long  / solo_short: una direzione ha PERSO almeno MIN_CAMPIONE trade
    e non ne ha mai vinto uno (i pareggi non contano) -> variante che la spegne.
  * conferma_trend: le perdite sono controtrend o «mai andate a favore»
    (classe ingresso) e la strategia non ha vinto niente -> variante con
    conferma del trend all'ingresso.
  * stop_stretto: MIN_STOP_LARGO perdite con stop oltre MAX_STOP_PCT -> variante
    con stop piu' stretto (il caso 0,07022/0,0595 del 23 set, -15,3%).
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

TIPI = ("solo_long", "solo_short", "conferma_trend", "stop_stretto")

_RILIEVI = ("ingresso", "uscita", "protezione", "stop_largo", "lock_mai", "controtrend")


def _bucket_vuoto() -> dict:
    return {"n": 0, "vinti": 0, "persi": 0, "pnl": 0.0,
            "ingresso": 0, "uscita": 0, "protezione": 0,
            "stop_largo": 0, "lock_mai": 0, "controtrend": 0,
            "long_n": 0, "long_vinti": 0, "long_persi": 0,
            "short_n": 0, "short_vinti": 0, "short_persi": 0}


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


def _arrotonda(b: dict) -> dict:
    b["pnl"] = round(b["pnl"], 2)
    return b


def _ipotesi_per(gid: str, b: dict) -> list[dict]:
    """Le regole, una per tipo, sul bucket di una strategia. Ogni regola e' una
    riga: se la cambi, cambia il commento in testa al modulo e la data."""
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
    return out


def aggrega_referti(trades: Iterable[dict]) -> dict:
    """Aggrega i trade chiusi per strategia, coin e direzione e produce le ipotesi.

    E' il documento Firestore `learning/referti` (contratto condiviso con la
    discovery e con `scripts/trade_stats.py`). Gli esiti esterni (manual,
    kill_switch, circuit_breaker) sono esclusi: non li ha decisi la strategia.
    Le ipotesi per direzione NON richiedono il referto: bastano pnl e direction,
    quindi scattano anche sui trade chiusi prima del 23 set."""
    rows = [t for t in trades if str(t.get("exit_reason", "")) not in ESITI_ESTERNI]
    per_strat: dict[str, dict] = defaultdict(_bucket_vuoto)
    per_coin: dict[str, dict] = defaultdict(_bucket_vuoto)
    per_dir: dict[str, dict] = {"long": _bucket_vuoto(), "short": _bucket_vuoto()}
    n_con_referto = n_persi_con_referto = 0
    # il PRIMO trade del paper per strategia: la variante che nasce da un'ipotesi
    # si valida su dati che finiscono prima di quella data (pre-registrazione,
    # audit del 24 set)
    primo_ts: dict[str, float] = {}

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

    ipotesi: list[dict] = []
    for gid in sorted(per_strat):
        if gid == "?":
            continue    # trade senza strategia: contano nei bucket, non propongono
        for h in _ipotesi_per(gid, per_strat[gid]):
            if gid in primo_ts:
                h["da_ts"] = round(primo_ts[gid], 0)
            ipotesi.append(h)
    ipotesi.sort(key=lambda h: (h["strategia"], h["tipo"]))

    return {
        "n_trades": len(rows),
        "n_con_referto": n_con_referto,
        "n_persi_con_referto": n_persi_con_referto,
        "per_strategia": {k: _arrotonda(v) for k, v in sorted(per_strat.items())},
        "per_coin": {k: _arrotonda(v) for k, v in sorted(per_coin.items())},
        "per_direzione": {k: _arrotonda(v) for k, v in per_dir.items()},
        "ipotesi": ipotesi,
    }


def riassunto_ipotesi(doc: dict | None) -> list[str]:
    """Una riga leggibile per ipotesi, per il print del bot e per `trades`:
    «gen_ba3a671f: solo_long — short 4/4 persi (campione 4)»."""
    if not doc:
        return []
    return [f"{h.get('strategia')}: {h.get('tipo')} — {h.get('motivo')} "
            f"(campione {h.get('campione')})"
            for h in (doc.get("ipotesi") or [])]
