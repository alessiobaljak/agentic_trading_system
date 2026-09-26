"""AUTOPSIA DELLE VALIDATE: il gate le boccia su una configurazione che il bot NON opera?

26 set 2026. Il giro completo di oggi ha rivalutato le 182 coppie validate e 167
NON hanno passato il gate sui dati di adesso (`merge_into_registry` riscrive
`last_params` solo per chi passa: keep e scala di quelle 167 sono rimasti quelli
di prima). Un revisore ha trovato un possibile ARTEFATTO in `evaluate_spec`
(scripts/discover_strategies.py): il passo 1 (preselezione) gira SEMPRE con la
scala, il break-even e il keep GLOBALI (SCALE_OUT_R_MULTIPLES, ecc.), e la
ricerca per coppia del passo 2 — e il verdetto finale — avvengono solo
`if passed`. Una coppia che il bot opera a 2/4/6 con keep 0,75 viene quindi
rigiudicata a ogni giro su 1,5/3/5 con keep 0,5: il gate puo' bocciare una
configurazione che il bot non esegue.

Prima di toccare il gate si MISURA (regola del proprietario). Per ogni coppia
validata (`coppie_validate` sul registro, spec da `discovered_strategies/specs`)
questo script valuta la spec sulla sua coin in TRE modi:

  (A) come fa il gate oggi: `evaluate_spec` col passo 1 sulla configurazione
      globale -> passa?, criterio binding, holdout;
  (B) col passo 1 FORZATO sulla configurazione che la coppia opera davvero
      (`last_params` del registro, letti con le STESSE funzioni del bot:
      `ladder_multiples`, `breakeven_after_tp1`, `lock_keep`) -> passa?, binding.
      Il passo 2 e il verdetto finale restano quelli del gate;
  (C) la storia RECENTE: PF, trade e pnl degli ultimi 45/120/180 giorni con la
      configurazione operata, in UNA passata sulla serie intera. Non si puo'
      leggere dalle finestre OOS del gate: finiscono 45 giorni prima della fine
      dei dati (l'holdout), quindi «gli ultimi 45 giorni» li' sarebbero vuoti per
      costruzione. E' una promessa, non una prova: sono gli stessi dati su cui la
      coppia e' stata scelta.

Bocciata in (A) e passata in (B) = ARTEFATTO della configurazione globale.
Bocciata in entrambe = la bocciatura regge anche sulla configurazione operata:
il passo 1 non e' il problema.

SOLA LETTURA: non scrive registro, spec ne' documenti. Stesso motore, stessi
caricatori e stesso initializer dei worker della discovery (`_disc_init`), stesse
candidate di scala e keep dal paper: (A) riproduce IL gate di oggi, non una copia.

TEMPO. Il canale ops uccide a 900 s (OPS_TIMEOUT_S) e di un processo ucciso resta
solo cio' che e' stato svuotato su stdout: qui ogni riga e' `flush`, e c'e' una
deadline propria (`--budget`, default 720 s). Scaduta, i worker restituiscono le
coppie rimaste come «non valutate per tempo» e il riassunto esce comunque, su
cio' che e' stato misurato. Le coin con piu' coppie validate si valutano per
prime. Stima dai giri della discovery (~85 s di costo fisso per coin: candele,
indicatori, snapshot; meno di un secondo per passata): 62 coin su 6 worker fanno
15-17 minuti per tutte le 182 coppie, quindi nel canale ops ne entrano circa 45-50
coin; il resto con `--budget 0` da tmux, oppure alzando OPS_TIMEOUT_S.

Uso (sulla VPS):
    .venv/bin/python -m scripts.autopsia_validate
    .venv/bin/python -m scripts.autopsia_validate --limit 20      # prova rapida
    .venv/bin/python -m scripts.autopsia_validate --budget 0      # senza deadline (tmux)
Senza Firebase (test, locale) stampa «nessuna validata» ed esce con 0.
"""
from __future__ import annotations

import argparse
import multiprocessing
import os
import time
from collections import Counter
from datetime import date

from backtesting.data_loader import load_candles
from backtesting.parallel import n_workers, parallel_map
from backtesting.quality import looks_delisted
from bot.config import settings, timeframe_hours
from bot.core.firebase_client import decode_pairs, get_firebase
from bot.core.indicators import compute_indicator_frame
from bot.core.registry import coppie_validate, scala_str
from bot.execution.exit_logic import breakeven_after_tp1, ladder_multiples, lock_keep
from bot.strategies.generated import MARKET_FEATURES, GeneratedStrategy
from scripts import discover_strategies as d

#: le finestre della storia recente, in giorni. 45 = l'holdout del gate
#: (GATE_HOLDOUT_DAYS): i giorni che la selezione non ha mai visto.
FINESTRE_GIORNI = (45, 120, 180)
#: deadline propria, sotto i 900 s del canale ops, con margine per la coin in corso
BUDGET_S = float(os.getenv("AUTOPSIA_BUDGET_S", "720"))
#: gli stessi worker del giro della discovery sulla VPS (`n_workers` li riduce se
#: la RAM non basta: e' il tetto che ha salvato i giri del 24 set dall'OOM)
WORKERS = int(os.getenv("AUTOPSIA_WORKERS", "6"))
#: ogni quante coppie i worker stampano un avanzamento
PROGRESSO_OGNI = 20
#: le classi del confronto A/B, nell'ordine in cui si stampano (prima le interessanti)
CLASSI = ("artefatto", "solo_globale", "bocciata", "passa")

#: stato per-worker di QUESTO script (deadline, contatore), accanto a `d._W`
_S: dict = {}


def di(msg: str = "") -> None:
    """Stampa SUBITO: stdout su pipe accumula a blocchi e un processo ucciso dal
    timeout del canale ops non lascia una riga (e' successo a timeframe_probe)."""
    print(msg, flush=True)


# --------------------------------------------------------------------------- #
# Funzioni pure                                                                #
# --------------------------------------------------------------------------- #
def _campo(t, nome: str, default: float = 0.0) -> float:
    v = t.get(nome, default) if isinstance(t, dict) else getattr(t, nome, default)
    try:
        return float(v or 0.0)
    except (TypeError, ValueError):
        return float(default)


def pf_recente(trades, giorni: float, now: float) -> dict:
    """PF, numero di trade e pnl dei trade ENTRATI negli ultimi `giorni` prima di
    `now` (epoch). Un trade senza `entry_ts` (0 = sconosciuto) resta fuori: non si
    inventa una data. Stessa convenzione di `StrategyStats.profit_factor` (999
    senza perdite, 0 senza guadagni); `pf` None se nella finestra non c'e' nessun
    trade. Accetta oggetti (SimTrade) e dizionari."""
    da = float(now) - float(giorni) * 86400.0
    sel = [t for t in (trades or [])
           if _campo(t, "entry_ts") > 0 and _campo(t, "entry_ts") >= da]
    pnls = [_campo(t, "pnl_pct") for t in sel]
    g = sum(p for p in pnls if p > 0)
    perdite = -sum(p for p in pnls if p < 0)
    if not sel:
        pf = None
    elif perdite > 0:
        pf = round(g / perdite, 3)
    else:
        pf = 999.0 if g > 0 else 0.0
    return {"giorni": float(giorni), "trades": len(sel), "pf": pf,
            "pnl": round(sum(pnls), 4)}


def config_globale() -> dict:
    """La configurazione con cui il passo 1 del gate giudica TUTTE le spec."""
    return {"scale_r_mults": [float(x) for x in settings.SCALE_OUT_R_MULTIPLES],
            "sl_to_breakeven": bool(settings.SCALE_OUT_SL_TO_BREAKEVEN),
            "profit_lock_keep": float(settings.PROFIT_LOCK_KEEP)}


def config_operata(last_params) -> dict:
    """La configurazione che il bot opera per QUESTA coppia, letta da `last_params`
    con le STESSE funzioni del bot e del motore (bot/execution/exit_logic.py): un
    campo assente vale il default globale, esattamente come in `open_position` e
    in `run_strategy`. Cosi' (B) misura cio' che gira davvero, non una lettura
    parallela del registro."""
    lp = last_params if isinstance(last_params, dict) else {}
    scala = ladder_multiples(lp)
    keep = lock_keep(lp)
    return {"scale_r_mults": [float(x) for x in (scala or settings.SCALE_OUT_R_MULTIPLES)],
            "sl_to_breakeven": bool(breakeven_after_tp1(lp)),
            "profit_lock_keep": float(settings.PROFIT_LOCK_KEEP if keep is None else keep)}


def e_globale(cfg: dict) -> bool:
    """True se la coppia opera esattamente la configurazione globale: per lei (A)
    e (B) sono la stessa valutazione, e non si rifa'."""
    g = config_globale()
    try:
        return (list(float(x) for x in (cfg.get("scale_r_mults") or [])) == g["scale_r_mults"]
                and bool(cfg.get("sl_to_breakeven")) == g["sl_to_breakeven"]
                and abs(float(cfg.get("profit_lock_keep", g["profit_lock_keep"]))
                        - g["profit_lock_keep"]) < 1e-9)
    except (TypeError, ValueError):
        return False


def config_str(cfg: dict) -> str:
    return (f"{scala_str(cfg.get('scale_r_mults')) or '-'} "
            f"{'BE' if cfg.get('sl_to_breakeven') else 'noBE'} "
            f"keep{float(cfg.get('profit_lock_keep', 0) or 0):g}")


def classifica(passa_a, passa_b) -> str:
    """`artefatto` = bocciata col passo 1 globale (A) e passata col passo 1 sulla
    configurazione operata (B); `solo_globale` = il contrario (il gate conferma
    una configurazione che il bot non opera); `passa` / `bocciata` = d'accordo."""
    a, b = bool(passa_a), bool(passa_b)
    if a and b:
        return "passa"
    if b:
        return "artefatto"
    if a:
        return "solo_globale"
    return "bocciata"


def coppie_da_autopsiare(pairs: dict, specs: dict, interval: str, now=None,
                         limit: int = 0) -> tuple[list, dict]:
    """[(coin, [(chiave, spec, config_operata), ...])] per le coppie validate che
    qui si possono giudicare, e i conteggi di quelle che no: `base` (i parametri
    stanno nel registro, non in una spec), `senza_spec`, `altro_timeframe` (le
    candele sarebbero un'altra serie: si valutano con --interval). Le coin con
    piu' coppie prima: se il tempo finisce, si e' misurato il massimo di coppie
    per coin caricata. `limit` taglia le coppie (0 = tutte)."""
    tf_bot = settings.ORCHESTRATOR_TIMEFRAME
    saltate: Counter = Counter()
    per_coin: dict[str, list] = {}
    for key in coppie_validate(pairs, now):
        rec = pairs.get(key) or {}
        sym, sid = key.split("|", 1)
        spec = specs.get(sid) if isinstance(specs, dict) else None
        if not isinstance(spec, dict):
            saltate["base" if not rec.get("generated") else "senza_spec"] += 1
            continue
        if (spec.get("timeframe") or tf_bot) != interval:
            saltate["altro_timeframe"] += 1
            continue
        per_coin.setdefault(sym, []).append((key, spec, config_operata(rec.get("last_params"))))
    ordine = sorted(per_coin, key=lambda s: (-len(per_coin[s]), s))
    piatte = [(s, c) for s in ordine for c in per_coin[s]]
    if limit and limit > 0:
        piatte = piatte[:limit]
    out: list = []
    for s, c in piatte:
        if out and out[-1][0] == s:
            out[-1][1].append(c)
        else:
            out.append((s, [c]))
    return out, dict(saltate)


# --------------------------------------------------------------------------- #
# I worker                                                                     #
# --------------------------------------------------------------------------- #
def _init(args, end: str, scala_paper, keep_paper, scale_strategie, deadline: float,
          contatore, totale: int, t0: float) -> None:
    """Lo STESSO initializer dei worker della discovery (`_disc_init`: optimizer,
    contesto BTC, candidati dal paper), piu' lo stato di questo script."""
    d._disc_init(args, end, [], scala_paper, None, None, False, keep_paper, scale_strategie)
    _S.update(deadline=float(deadline or 0.0), contatore=contatore, totale=int(totale),
              t0=float(t0))


def _scaduto() -> bool:
    dl = float(_S.get("deadline") or 0.0)
    return bool(dl) and time.time() > dl


def _avanza() -> None:
    """Una coppia in piu': ogni PROGRESSO_OGNI stampa quante sono fatte. Il
    contatore e' condiviso fra i processi (`multiprocessing.Value`)."""
    c = _S.get("contatore")
    if c is None:
        return
    with c.get_lock():
        c.value += 1
        v = c.value
    if v % PROGRESSO_OGNI == 0 or v == _S.get("totale"):
        di(f"[autopsia] {v}/{_S.get('totale')} coppie valutate "
           f"· {time.time() - float(_S.get('t0') or time.time()):.0f}s")


def _riga(key: str, cfg: dict, stato: str, **extra) -> dict:
    r = {"key": key, "config": cfg, "stato": stato}
    r.update(extra)
    return r


def _contesto(W: dict, spec: dict):
    """Il contesto di mercato SOLO alle spec che lo usano, come in `_disc_one`."""
    usa_mercato = any((f.get("kind") in MARKET_FEATURES)
                      for f in (spec.get("features") or []) if isinstance(f, dict))
    return W.get("btc_ctx") if usa_mercato else None


def _holdout(r: dict):
    h = r.get("holdout") or {}
    return bool(h.get("ok")) if isinstance(h, dict) and "ok" in h else None


def _valuta(W: dict, sym: str, candles, frame, key: str, spec: dict, cfg: dict,
            end: str, args) -> dict:
    """(A) e (B) per una coppia. Le candidate di scala e keep sono quelle che
    `_disc_one` passa oggi al gate: (A) e' il gate, non una sua copia."""
    scala_strategia = (W.get("scale_strategie") or {}).get(spec.get("id"))
    kw = dict(scale_candidates=d.candidate_ladders(W.get("scala_paper"),
                                                   scala_strategia=scala_strategia),
              keep_candidates=d.candidate_keeps(W.get("keep_paper")),
              context_by_ts=_contesto(W, spec), run_end=end, interval=args.interval)
    ra = d.evaluate_spec(W["opt"], sym, candles, frame, spec, **kw)
    stessa = e_globale(cfg)
    rb = ra if stessa else d.evaluate_spec(W["opt"], sym, candles, frame, spec,
                                           config_iniziale=cfg, **kw)
    return _riga(key, cfg, "ok", spec=spec, stessa_config=stessa,
                 passa_a=bool(ra["passed"]), binding_a=str(ra.get("fail_binding") or ""),
                 holdout_a=_holdout(ra), pf_a=ra.get("pf"), trades_a=ra.get("trades"),
                 passa_b=bool(rb["passed"]), binding_b=str(rb.get("fail_binding") or ""),
                 holdout_b=_holdout(rb), pf_b=rb.get("pf"), trades_b=rb.get("trades"),
                 classe=classifica(ra["passed"], rb["passed"]))


def _storia_recente(W: dict, sym: str, candles, frame, spec: dict, cfg: dict,
                    data_end: float) -> dict:
    """(C): una passata sulla serie intera con la configurazione operata, poi le
    tre finestre. `now` e' la fine dei DATI, non l'orologio: la cache puo' essere
    indietro, e il gate giudica sugli stessi dati."""
    g = GeneratedStrategy(spec)
    g.params = {**(getattr(g, "params", {}) or {}), **cfg}
    st = W["opt"].bt.run_strategy(g, sym, candles, frame=frame,
                                  context_by_ts=_contesto(W, spec))
    return {int(gg): pf_recente(st.trades, gg, data_end) for gg in FINESTRE_GIORNI}


def _una_coin(item) -> list[dict]:
    """Tutte le coppie validate di UNA coin: candele e indicatori una volta sola
    (e' il costo fisso), poi (A)+(B) per coppia, poi (C). Fail-open per coppia:
    un errore e' una riga «errore», non la fine dell'autopsia."""
    sym, lista = item
    W = d._W
    args, end = W["args"], W["end"]
    if _scaduto():
        return [_riga(k, c, "tempo") for k, _s, c in lista]
    try:
        candles = load_candles(sym, args.interval, args.start, end, prefer=args.source)
    except Exception as exc:  # noqa: BLE001
        di(f"[autopsia] {sym}: candele non disponibili ({str(exc)[:80]})")
        return [_riga(k, c, "errore", errore=f"candele: {str(exc)[:80]}")
                for k, _s, c in lista]
    if len(candles) < W["min_history"]:
        return [_riga(k, c, "storia", errore=f"{len(candles)} candele su {W['min_history']}")
                for k, _s, c in lista]
    if looks_delisted(candles, end, timeframe_hours(args.interval)):
        return [_riga(k, c, "delistata",
                      errore=f"serie ferma al {candles[-1].open_time:%Y-%m-%d}")
                for k, _s, c in lista]
    frame = compute_indicator_frame(candles)
    data_end = float(candles[-1].open_time.timestamp())
    t_coin = time.time()
    righe: list[dict] = []
    for key, spec, cfg in lista:
        if _scaduto():
            righe.append(_riga(key, cfg, "tempo"))
            continue
        try:
            righe.append(_valuta(W, sym, candles, frame, key, spec, cfg, end, args))
        except Exception as exc:  # noqa: BLE001
            di(f"[autopsia] {key}: errore ({str(exc)[:100]})")
            righe.append(_riga(key, cfg, "errore", errore=str(exc)[:100]))
        _avanza()
    # (C) DOPO tutte le A/B della coin: e' una passata sulla serie intera, con
    # snapshot propri. Il motore tiene 4 slice in cache (le 3 finestre OOS e
    # l'holdout): alternarla alle valutazioni farebbe ricostruire tutto a ogni
    # coppia, e tenere le due serie insieme raddoppia la memoria (OOM del 24 set).
    d.svuota_cache_motore(W["opt"])
    for r in righe:
        if r["stato"] != "ok" or _scaduto():
            continue
        try:
            r["recente"] = _storia_recente(W, sym, candles, frame, r["spec"], r["config"],
                                           data_end)
        except Exception as exc:  # noqa: BLE001
            r["recente_errore"] = str(exc)[:80]
    d.svuota_cache_motore(W["opt"])
    for r in righe:
        r.pop("spec", None)          # al main non serve, e viaggia via pickle
    di(f"[autopsia] {sym}: {len(lista)} coppie in {time.time() - t_coin:.0f}s")
    return righe


# --------------------------------------------------------------------------- #
# Tabella e riassunto                                                          #
# --------------------------------------------------------------------------- #
def _esito(passa, binding: str) -> str:
    if passa:
        return "PASSA"
    return f"NO:{binding or '?'}"        # `NO:holdout` = OOS ok, cade sui dati mai visti


def _cella_recente(rec: dict | None, giorni: int) -> str:
    x = (rec or {}).get(giorni) or (rec or {}).get(str(giorni))
    if not x:
        return "-"
    pf = "-" if x.get("pf") is None else f"{x['pf']:g}"
    return f"{pf}({x.get('trades', 0)})"


def intestazione() -> str:
    return (f"{'COPPIA':<36} {'CONFIG OPERATA':<22} {'(A) gate oggi':<16} "
            f"{'(B) config op.':<16} {'CLASSE':<12} PF(trade) ultimi "
            + " / ".join(f"{g}g" for g in FINESTRE_GIORNI))


def riga_tabella(r: dict) -> str:
    key = r["key"][:36].ljust(36)
    cfg = config_str(r["config"])[:22].ljust(22)
    if r.get("stato") != "ok":
        return f"{key} {cfg} {str(r.get('stato', '?')).upper():<16} {r.get('errore', '')}"
    a = _esito(r["passa_a"], r["binding_a"])
    b = "= A" if r.get("stessa_config") else _esito(r["passa_b"], r["binding_b"])
    rec = " / ".join(_cella_recente(r.get("recente"), g) for g in FINESTRE_GIORNI)
    if r.get("recente_errore"):
        rec = f"errore: {r['recente_errore']}"
    return f"{key} {cfg} {a:<16} {b:<16} {r.get('classe', '?'):<12} {rec}"


def _dist(conta: Counter) -> str:
    return " · ".join(f"{k} {n}" for k, n in conta.most_common()) or "-"


def lettura(n: int, passa_a: int, artefatti: int, bocciate_a: int,
            perdono_120: int, con_trade_120: int) -> str:
    """La frase che dice cosa fare dei numeri. Il criterio: se la MAGGIORANZA delle
    bocciature sparisce col passo 1 sulla configurazione operata, e' il passo 1 a
    bocciare; se solo una minoranza, correggerlo recupera poco."""
    if n == 0:
        return "nessuna coppia valutata: niente da leggere."
    coda = ""
    if con_trade_120:
        coda = (f" Sugli ultimi 120 giorni {perdono_120} su {con_trade_120} con trade "
                f"hanno PF < 1 con la configurazione operata.")
    if bocciate_a == 0:
        return (f"tutte le {n} valutate passano il gate anche oggi: il passo 1 non sta "
                f"bocciando nessuno." + coda)
    if artefatti / bocciate_a >= 0.5:
        return (f"la maggior parte delle bocciature ({artefatti} su {bocciate_a}) e' un "
                f"artefatto del passo 1: il gate giudica una configurazione che il bot "
                f"non opera, e correggere il passo 1 (preselezione sulla configurazione "
                f"operata) e' giustificato dai numeri." + coda)
    if artefatti > 0:
        return (f"solo una parte delle bocciature ({artefatti} su {bocciate_a}) e' un "
                f"artefatto del passo 1: la maggior parte regge anche sulla configurazione "
                f"operata, quindi correggere il gate recupera poco e il problema "
                f"principale e' altrove (mercato recente o soglie)." + coda)
    return (f"nessun artefatto: le {bocciate_a} bocciature reggono anche sulla "
            f"configurazione operata; il passo 1 non e' il problema." + coda)


def riassunto(righe: list[dict], saltate: dict | None = None,
              n_validate: int | None = None) -> list[str]:
    """Le righe del riassunto, in fondo all'output: il canale ops tronca testa e
    coda dell'output lungo, e la coda e' quella che resta."""
    ok = [r for r in righe if r.get("stato") == "ok"]
    stati = Counter(str(r.get("stato")) for r in righe)
    saltate = dict(saltate or {})
    n_val = len(righe) + sum(saltate.values()) if n_validate is None else int(n_validate)
    testa = f"RIASSUNTO · {n_val} validate · {len(ok)} valutate"
    altri = " · ".join(f"{k} {v}" for k, v in sorted(stati.items()) if k != "ok")
    if altri:
        testa += " · " + altri
    if saltate:
        testa += " · saltate: " + ", ".join(f"{k} {v}" for k, v in sorted(saltate.items()))
    out = [testa]
    if not ok:
        out.append("  LETTURA: " + lettura(0, 0, 0, 0, 0, 0))
        return out
    a = sum(1 for r in ok if r.get("passa_a"))
    b = sum(1 for r in ok if r.get("passa_b"))
    classi = Counter(r.get("classe") for r in ok)
    stesse = sum(1 for r in ok if r.get("stessa_config"))
    bocc_a = len(ok) - a
    art = classi.get("artefatto", 0)
    out.append(f"  (A) passano col gate di oggi (passo 1 = configurazione globale "
               f"{config_str(config_globale())}): {a} su {len(ok)}")
    out.append(f"  (B) passano col passo 1 sulla configurazione operata: {b} su {len(ok)} "
               f"({stesse} operano gia' la configurazione globale: A = B)")
    out.append(f"  bocciate in (A) e passate in (B) = ARTEFATTO della configurazione "
               f"globale: {art} su {bocc_a} bocciate")
    out.append(f"  passate in (A) ma bocciate in (B): {classi.get('solo_globale', 0)} "
               f"(il gate conferma una configurazione che il bot non opera)")
    resto = [r for r in ok if r.get("classe") == "bocciata"]
    out.append(f"  bocciate in entrambe: {len(resto)} · criterio binding (B): "
               f"{_dist(Counter(r.get('binding_b') or '?' for r in resto))} · (A): "
               f"{_dist(Counter(r.get('binding_a') or '?' for r in resto))}")
    con_trade = [r for r in ok if ((r.get("recente") or {}).get(120) or {}).get("trades")]
    perdono = [r for r in con_trade if float(r["recente"][120].get("pf") or 0.0) < 1.0]
    out.append(f"  PF < 1 negli ultimi 120 giorni (configurazione operata, serie intera): "
               f"{len(perdono)} su {len(con_trade)} con trade")
    out.append("  LETTURA: " + lettura(len(ok), a, art, bocc_a, len(perdono), len(con_trade)))
    return out


# --------------------------------------------------------------------------- #
# main                                                                         #
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=0, help="quante coppie al massimo (0 = tutte)")
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--budget", type=float, default=BUDGET_S,
                    help="secondi prima di fermarsi da soli (0 = mai)")
    ap.add_argument("--interval", default=settings.ORCHESTRATOR_TIMEFRAME)
    ap.add_argument("--start", default="2022-01-01")
    ap.add_argument("--end", default=None, help="fine dati (default: oggi)")
    ap.add_argument("--source", default="auto")
    ap.add_argument("--windows", type=int, default=3)
    args = ap.parse_args()
    end = args.end or date.today().isoformat()
    t0 = time.time()

    fb = get_firebase()
    reg = fb.get_doc("strategy_registry", "validated") or {}
    pairs = decode_pairs(reg.get("pairs"))
    validate = coppie_validate(pairs)
    if not validate:
        di("[autopsia] nessuna validata nel registro: niente da autopsiare.")
        return 0
    specs = decode_pairs((fb.get_doc("discovered_strategies", "specs") or {}).get("specs"))
    lavoro, saltate = coppie_da_autopsiare(pairs, specs, args.interval, limit=args.limit)
    totale = sum(len(l) for _s, l in lavoro)
    di(f"[autopsia] {len(validate)} validate · {totale} coppie su {len(lavoro)} coin da "
       f"valutare a {args.interval} · dati {args.start}->{end}"
       + (" · saltate: " + ", ".join(f"{k} {v}" for k, v in sorted(saltate.items()))
          if saltate else ""))
    if not lavoro:
        di("[autopsia] niente da valutare a questo timeframe.")
        return 0
    # le stesse candidate del giro della discovery: (A) deve essere IL gate
    trades_paper = d.trades_del_paper(fb)
    keep_paper = d.keep_dal_paper(fb, trades=trades_paper)
    scala_paper = d.scala_dal_paper(fb, trades=trades_paper)
    scale_strategie = d.scale_per_strategia(trades_paper or [])
    workers = max(1, min(int(args.workers), n_workers()))
    deadline = (t0 + float(args.budget)) if args.budget > 0 else 0.0
    di(f"[autopsia] {workers} worker · configurazione globale "
       f"{config_str(config_globale())} · deadline "
       f"{'nessuna' if not deadline else f'{args.budget:.0f}s'}")
    contatore = multiprocessing.Value("i", 0)
    risultati = parallel_map(_una_coin, lavoro, workers=workers, initializer=_init,
                             initargs=(args, end, scala_paper, keep_paper, scale_strategie,
                                       deadline, contatore, totale, t0))
    righe = [r for gruppo in risultati for r in gruppo]
    ordine = {c: i for i, c in enumerate(CLASSI)}
    righe.sort(key=lambda r: (0 if r.get("stato") == "ok" else 1,
                              ordine.get(r.get("classe"), 9), r["key"]))
    di()
    di(intestazione())
    for r in righe:
        di(riga_tabella(r))
    di()
    for line in riassunto(righe, saltate, n_validate=len(validate)):
        di(line)
    per_tempo = sum(1 for r in righe if r.get("stato") == "tempo")
    if per_tempo:
        di(f"  {per_tempo} coppie NON valutate per tempo (budget {args.budget:.0f}s): "
           f"--budget 0 da tmux, oppure OPS_TIMEOUT_S piu' alto")
    di(f"[autopsia] finito in {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
