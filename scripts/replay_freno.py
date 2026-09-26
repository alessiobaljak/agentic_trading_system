"""IL REPLAY DEL FRENO PER GRUPPO — voce ops `replay` (26 set 2026, passo 4).

Il freno per gruppo (`bot/learning/drift.py`, chiave `pool` di `drift/current`)
ha soglie COSTANTI dichiarate prima di ogni misura: CUSUM a un lato sui multipli
di R con allarme a `POOL_CUSUM_H` (4R) e ripresa a `POOL_CUSUM_RIPRESA` (2,5R),
SPRT su «ha toccato TP1» con p0 = 0,45 e p1 = 0,25. Non sono tarate sui trade
del paper e non lo saranno: il paper e' il giudice, non il maestro.

Questo replay ripercorre i trade chiusi del paper in ordine cronologico e dice,
per ogni pool (famiglia x regime all'ingresso, direzione x contesto BTC):
  * il giorno in cui il CUSUM e lo SPRT AVREBBERO suonato, contro il giorno in
    cui il freno globale si e' acceso (`drift/current.global.dal`, oppure il
    primo giorno del replay in cui la regola globale — 40 trade a 30 giorni e
    PF < 0,6 x atteso — era soddisfatta);
  * il PnL del pool nei 7 giorni DOPO l'allarme: se e' positivo l'allarme era
    falso, se e' negativo il freno avrebbe risparmiato qualcosa;
  * se sulla macchina esiste il dataset del selettore (`data/selettore/*.jsonl`,
    i trade OOS del gate), il tasso di falsi allarmi per 100 trade delle coppie
    VALIDATE su storia «sana» (ARL0): un allarme li' e' rumore per costruzione,
    perche' quelle coppie il gate le ha promosse.

LA REGOLA, scritta prima dei numeri: il replay puo' solo BOCCIARE le soglie,
mai sceglierle. Se un pool suona DOPO il freno globale, per quel pool il freno
e' inutile; se sulla storia sana suona piu' di 5 volte ogni 100 trade, h e'
troppo basso. In nessun caso si sposta una soglia «finche' torna»: sarebbe
BIRBUSDT con un altro nome.

Sola lettura. Senza Firebase (in locale, nei test) gira sullo store in memoria:
tutto vuoto, ed esce con 0.

Uso (sul VPS):
    .venv/bin/python -m scripts.replay_freno
    .venv/bin/python -m scripts.replay_freno --giorni-dopo 7
"""
from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from typing import Optional

from bot.config import settings
from bot.core.firebase_client import decode_pairs, get_firebase
from bot.learning import drift as dr

#: sopra questo tasso di allarmi per 100 trade SANI del gate, h e' troppo basso
MAX_FALSI_PER_100 = 5.0
#: la finestra in cui si legge il PnL del pool dopo l'allarme
GIORNI_DOPO = 7


def _f(v) -> Optional[float]:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f else None


def _giorno(ts: Optional[float]) -> str:
    if ts is None:
        return "mai"
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).strftime("%Y-%m-%d")
    except (OverflowError, OSError, ValueError):
        return "?"


def _pf(pnls: list[float]) -> float:
    gains = sum(x for x in pnls if x > 0)
    losses = -sum(x for x in pnls if x < 0)
    if losses > 0:
        return gains / losses
    return 99.0 if gains > 0 else 0.0


# --------------------------------------------------------------------------- #
# i trade del paper, in ordine                                                 #
# --------------------------------------------------------------------------- #
def trade_ordinati(trades: list[dict]) -> list[dict]:
    """Le validate (esplorative fuori), esiti esterni fuori, in ordine di
    chiusura; senza exit_ts un trade non ha un posto nel tempo e si salta."""
    rows = [t for t in (trades or []) if isinstance(t, dict)
            and str(t.get("exit_reason", "")) not in dr._EXTERNAL
            and not t.get("esplorativa") and _f(t.get("exit_ts")) is not None]
    return sorted(rows, key=lambda t: float(t["exit_ts"]))


def giorno_freno_globale(trades: list[dict], pairs: dict, drift_doc: dict | None,
                         giorni: float = 30.0) -> tuple[Optional[float], str]:
    """(epoch, fonte) dell'accensione del freno globale: `drift/current.global.dal`
    se il documento lo porta (il bot lo scrive dal 25 set), altrimenti il
    replay della regola globale sui trade in ordine: primo trade alla cui
    chiusura la finestra dei 30 giorni ha >= DRIFT_MIN_TRADES_GLOBAL trade e
    PF < DRIFT_PF_RATIO x atteso (atteso = media dei last_pf del registro, come
    `compute_drift`). Solo la regola del PF: quella sulla mfe mediana non si
    rigioca qui. None se non e' mai scattato."""
    glob = (drift_doc or {}).get("global") if isinstance(drift_doc, dict) else None
    if isinstance(glob, dict) and glob.get("verdict") == dr.DRIFT and _f(glob.get("dal")):
        return float(glob["dal"]), "drift/current.global.dal"
    attese = [float(r.get("last_pf") or 0) for r in (pairs or {}).values()
              if isinstance(r, dict) and _f(r.get("last_pf")) and float(r["last_pf"]) > 0]
    if not attese:
        return None, "nessun atteso nel registro: regola globale non rigiocabile"
    atteso = sum(attese) / len(attese)
    soglia = atteso * float(settings.DRIFT_PF_RATIO)
    fonte = (f"replay della regola globale ({settings.DRIFT_MIN_TRADES_GLOBAL} trade a "
             f"{int(giorni)} giorni, PF < {settings.DRIFT_PF_RATIO:g} x {atteso:.2f} = {soglia:.2f}, "
             f"atteso da {len(attese)} coppie)")
    finestra: list[dict] = []
    for t in trades:
        ts = float(t["exit_ts"])
        finestra.append(t)
        finestra = [x for x in finestra if float(x["exit_ts"]) >= ts - giorni * 86400.0]
        if len(finestra) >= int(settings.DRIFT_MIN_TRADES_GLOBAL):
            if _pf([float(x.get("pnl", 0) or 0) for x in finestra]) < soglia:
                return ts, fonte
    return None, fonte + ": mai soddisfatta"


# --------------------------------------------------------------------------- #
# il replay di un pool                                                          #
# --------------------------------------------------------------------------- #
def replay_pool(xs: list[dict], riferimento: float, giorni_dopo: float = GIORNI_DOPO) -> dict:
    """`xs` = [{r, ts, tp1, pnl}] in ordine. Ritorna i giorni in cui CUSUM e SPRT
    avrebbero suonato (primo allarme), quante volte il CUSUM ha suonato in tutto
    con la ripresa, e il PnL del pool nei `giorni_dopo` giorni dopo il primo
    allarme (None se non ha suonato)."""
    rs = [x["r"] for x in xs]
    allarme, _s, i_primo = dr.cusum_r(rs, riferimento, settings.POOL_CUSUM_H, dr.CUSUM_K)
    st = dr.stato_pool(rs, riferimento, settings.POOL_CUSUM_H, settings.POOL_CUSUM_RIPRESA, dr.CUSUM_K)
    con_tp1 = [x for x in xs if x.get("tp1") is not None]
    esito, llr, i_sprt = dr.sprt_tp1([bool(x["tp1"]) for x in con_tp1],
                                     settings.POOL_SPRT_P0, settings.POOL_SPRT_P1)
    ts_all = xs[i_primo]["ts"] if i_primo is not None else None
    pnl_dopo = n_dopo = None
    if ts_all is not None:
        dopo = [x for x in xs if ts_all < x["ts"] <= ts_all + giorni_dopo * 86400.0]
        pnl_dopo, n_dopo = round(sum(float(x.get("pnl", 0) or 0) for x in dopo), 2), len(dopo)
    return {"n": len(rs), "riferimento": riferimento,
            "r_medio": round(sum(rs) / len(rs), 3) if rs else None,
            "cusum_allarme_ts": ts_all, "cusum_allarmi": st["allarmi"],
            "ripresa": st["ripresa"],
            "ripresa_ts": xs[st["indice_ripresa"]]["ts"] if st["indice_ripresa"] is not None else None,
            "sprt": esito, "sprt_llr": llr,
            "sprt_ts": con_tp1[i_sprt]["ts"] if i_sprt is not None else None,
            "tp1_n": len(con_tp1),
            "pnl_dopo": pnl_dopo, "n_dopo": n_dopo}


def replay_pools(trades: list[dict], pairs: dict, specs: dict | None, validated,
                 giorni_dopo: float = GIORNI_DOPO) -> dict[str, dict]:
    """Tutti i pool sui trade del paper (TUTTA la storia, non solo 30 giorni: il
    replay vuole vedere QUANDO avrebbe suonato la prima volta)."""
    famiglie = {str(t.get("strategy")): dr.famiglia_di(str(t.get("strategy")), specs) for t in trades}
    for k in (pairs or {}):
        if "|" in str(k):
            strat = str(k).split("|", 1)[1]
            famiglie.setdefault(strat, dr.famiglia_di(strat, specs))
    per_pool: dict[str, list[dict]] = {}
    for t in trades:
        r = dr.r_multiplo(t)
        if r is None:
            continue
        for ch in dr.chiavi_pool(t, famiglie):
            per_pool.setdefault(ch, []).append({"r": r, "ts": float(t["exit_ts"]),
                                                "tp1": dr.tocca_tp1(t),
                                                "pnl": float(t.get("pnl", 0) or 0)})
    out = {}
    for ch, xs in sorted(per_pool.items()):
        rif, nota, n_rif = dr.riferimento_pool(ch, pairs or {}, famiglie, validated)
        rec = replay_pool(xs, rif, giorni_dopo)
        rec["riferimento_nota"], rec["coppie_riferimento"] = nota, n_rif
        out[ch] = rec
    return out


# --------------------------------------------------------------------------- #
# ARL0: falsi allarmi su storia sana (dataset del selettore, solo sulla VPS)    #
# --------------------------------------------------------------------------- #
def _r_riga_selettore(row: dict) -> Optional[float]:
    """R di una riga OOS del gate: pnl_pct (variazione di prezzo, netta) diviso
    la larghezza dello stop `feats.stop_pct`, entrambe frazioni del prezzo."""
    feats = row.get("feats") if isinstance(row.get("feats"), dict) else {}
    p, sp = _f(row.get("pnl_pct")), _f(feats.get("stop_pct"))
    if p is None or not sp or sp <= 0:
        return None
    return p / sp


def arl0_storia_sana(righe: list[dict], pairs: dict, specs: dict | None, validated) -> dict[str, dict]:
    """Per pool: quante volte il CUSUM (con ripresa) suona su una sequenza di
    trade OOS delle coppie VALIDATE (storia «sana»: il gate le ha promosse),
    per 100 trade. Sopra MAX_FALSI_PER_100, h e' troppo basso: BOCCIATA."""
    val = set(validated or [])
    righe = [r for r in righe if isinstance(r, dict) and f"{r.get('symbol')}|{r.get('strategy')}" in val]
    righe.sort(key=lambda r: _f(r.get("entry_ts")) or 0.0)
    famiglie = {str(r.get("strategy")): (r.get("famiglia") or dr.famiglia_di(str(r.get("strategy")), specs))
                for r in righe}
    per_pool: dict[str, list[float]] = {}
    for r in righe:
        x = _r_riga_selettore(r)
        if x is None:
            continue
        feats = r.get("feats") if isinstance(r.get("feats"), dict) else {}
        t = {"strategy": r.get("strategy"), "regime_at_entry": r.get("regime"),
             "direction": r.get("direction"), "feats_at_entry": {"market_up": feats.get("market_up")}}
        for ch in dr.chiavi_pool(t, famiglie):
            per_pool.setdefault(ch, []).append(x)
    out = {}
    for ch, rs in sorted(per_pool.items()):
        rif, _nota, _n = dr.riferimento_pool(ch, pairs or {}, famiglie, validated)
        st = dr.stato_pool(rs, rif, settings.POOL_CUSUM_H, settings.POOL_CUSUM_RIPRESA, dr.CUSUM_K)
        per_100 = round(st["allarmi"] / len(rs) * 100.0, 2) if rs else None
        out[ch] = {"n": len(rs), "allarmi": st["allarmi"], "per_100": per_100,
                   "riferimento": rif,
                   "bocciata": bool(per_100 is not None and per_100 > MAX_FALSI_PER_100)}
    return out


# --------------------------------------------------------------------------- #
# stampa                                                                        #
# --------------------------------------------------------------------------- #
def stampa(trades: list[dict], pools: dict[str, dict], globale: tuple[Optional[float], str],
           arl0: dict[str, dict] | None, cartella_selettore: str, giorni_dopo: float) -> None:
    ts_glob, fonte_glob = globale
    print("REPLAY DEL FRENO PER GRUPPO (26 set 2026, passo 4) — sola lettura")
    print(f"  soglie COSTANTI (bot/learning/drift.py, bot/config.py): CUSUM h={settings.POOL_CUSUM_H:g}R "
          f"k={dr.CUSUM_K:g}, ripresa {settings.POOL_CUSUM_RIPRESA:g}R, SPRT p0={settings.POOL_SPRT_P0:g} "
          f"p1={settings.POOL_SPRT_P1:g} alpha=beta={dr.SPRT_ALPHA:g}")
    print("  LA REGOLA: il replay puo' solo BOCCIARE le soglie, mai sceglierle. Un pool che suona DOPO il "
          "freno globale e' inutile;")
    print(f"  piu' di {MAX_FALSI_PER_100:g} allarmi ogni 100 trade sani del gate = h troppo basso. "
          "Nessuna soglia si sposta «finche' torna».")
    if not trades:
        print("  nessun trade chiuso delle validate: niente da rigiocare")
        return
    con_r = sum(1 for t in trades if dr.r_multiplo(t) is not None)
    print(f"  trade del paper: {len(trades)} (validate, esiti esterni fuori) dal {_giorno(trades[0]['exit_ts'])} "
          f"al {_giorno(trades[-1]['exit_ts'])}; con R calcolabile {con_r} "
          f"(R = pnl / (|entry - stop originale| x size); senza stop originale il trade si salta)")
    print(f"  freno globale: {'acceso il ' + _giorno(ts_glob) if ts_glob else 'mai acceso'} "
          f"(fonte: {fonte_glob})")
    print(f"\nPER POOL (famiglia x regime all'ingresso; direzione x contesto BTC, «ignoto» escluso):")
    if not pools:
        print("  nessun pool: nessun trade con R calcolabile")
    testata = (f"  {'pool':<30} {'n':>4} {'rif R':>7} {'R medio':>8} {'CUSUM suona':>12} "
               f"{'vs globale':>14} {'allarmi':>7} {'SPRT':>8} {'quando':>10} {'PnL ' + str(int(giorni_dopo)) + 'g dopo':>14}  verdetto")
    print(testata)
    for ch, p in pools.items():
        ts_a = p["cusum_allarme_ts"]
        if ts_a is None:
            vs = "—"
        elif ts_glob is None:
            vs = "globale mai"
        else:
            delta = (ts_a - ts_glob) / 86400.0
            vs = f"{abs(delta):.1f} g {'PRIMA' if delta < 0 else 'DOPO'}"
        if ts_a is None:
            verdetto = "non suona"
        elif ts_glob is not None and ts_a >= ts_glob:
            verdetto = "BOCCIATO qui: suona dopo il globale (inutile)"
        elif p["pnl_dopo"] is None or p["n_dopo"] == 0:
            verdetto = "suona prima; nessun trade nei giorni dopo"
        elif p["pnl_dopo"] > 0:
            verdetto = "suona prima; FALSO ALLARME? (il pool ha poi guadagnato)"
        else:
            verdetto = "suona prima; allarme utile (il pool ha poi perso)"
        pnl_dopo = "—" if p["pnl_dopo"] is None else f"{p['pnl_dopo']:+.2f} ({p['n_dopo']} tr)"
        rm = "—" if p["r_medio"] is None else f"{p['r_medio']:+.2f}"
        print(f"  {ch:<30} {p['n']:>4} {p['riferimento']:>+7.2f} {rm:>8} {_giorno(ts_a):>12} "
              f"{vs:>14} {p['cusum_allarmi']:>7} {p['sprt']:>8} {_giorno(p['sprt_ts']):>10} {pnl_dopo:>14}  {verdetto}")
    note = {p["riferimento_nota"] for p in pools.values()}
    for n in sorted(note):
        print(f"  riferimento: {n}")
    print("  lo SPRT e' solo registrato: il freno ascolta il CUSUM; qui si vede chi dei due avrebbe suonato prima.")

    print(f"\nARL0 — falsi allarmi su storia SANA (trade OOS delle validate dal dataset del selettore, "
          f"{cartella_selettore}/*.jsonl):")
    if arl0 is None:
        print("  dataset del selettore assente da qui (vive sulla VPS): ARL0 non misurabile in questo replay")
        return
    if not arl0:
        print("  nessuna riga delle coppie validate con R calcolabile nel dataset")
        return
    print(f"  {'pool':<30} {'n':>5} {'allarmi':>7} {'per 100':>8}  verdetto (> {MAX_FALSI_PER_100:g} = h troppo basso)")
    for ch, a in arl0.items():
        v = "BOCCIATA: h troppo basso per questo pool" if a["bocciata"] else "regge"
        per = "—" if a["per_100"] is None else f"{a['per_100']:.1f}"
        print(f"  {ch:<30} {a['n']:>5} {a['allarmi']:>7} {per:>8}  {v}")
    tot_n = sum(a["n"] for a in arl0.values())
    tot_a = sum(a["allarmi"] for a in arl0.values())
    if tot_n:
        # un trade sta in piu' pool (famiglia e direzione): la somma conta trade-pool, non trade
        print(f"  tutti i pool: {tot_a} allarmi su {tot_n} trade-pool = {tot_a / tot_n * 100:.1f} per 100 "
              f"(un trade conta in ogni pool a cui appartiene)")


# --------------------------------------------------------------------------- #
def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Replay del freno per gruppo (sola lettura)")
    ap.add_argument("--giorni-dopo", type=float, default=GIORNI_DOPO,
                    help=f"giorni dopo l'allarme in cui leggere il PnL del pool (default {GIORNI_DOPO})")
    ap.add_argument("--dir-selettore", default=None,
                    help="cartella del dataset del selettore (default: SELETTORE_DIR o data/selettore)")
    args = ap.parse_args(argv)

    fb = get_firebase()
    try:
        trades = fb.query_collection("trades", order_by="exit_ts") or []
    except Exception as exc:  # noqa: BLE001
        print(f"trade non leggibili ({str(exc)[:80]}): niente da rigiocare")
        return 0
    try:
        reg = fb.get_doc("strategy_registry", "validated") or {}
    except Exception:  # noqa: BLE001
        reg = {}
    try:
        specs = decode_pairs((fb.get_doc("discovered_strategies", "specs") or {}).get("specs"))
    except Exception:  # noqa: BLE001
        specs = {}
    try:
        drift_doc = fb.get_doc("drift", "current") or {}
    except Exception:  # noqa: BLE001
        drift_doc = {}
    pairs = decode_pairs(reg.get("pairs"))
    validated = reg.get("validated") or None

    rows = trade_ordinati(trades)
    pools = replay_pools(rows, pairs, specs, validated, args.giorni_dopo)
    globale = giorno_freno_globale(rows, pairs, drift_doc)

    from bot.learning.selettore import SELETTORE_DIR, carica_righe
    cartella = args.dir_selettore or SELETTORE_DIR
    arl0 = None
    if os.path.isdir(cartella) and any(n.endswith(".jsonl") for n in os.listdir(cartella)):
        try:
            arl0 = arl0_storia_sana(carica_righe(cartella), pairs, specs, validated)
        except Exception as exc:  # noqa: BLE001
            print(f"dataset del selettore non leggibile ({str(exc)[:80]}): ARL0 saltato")
            arl0 = None
    stampa(rows, pools, globale, arl0, cartella, args.giorni_dopo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
