"""IL REGISTRO DELLE COPPIE, LETTO IN UN POSTO SOLO (25 set 2026).

Le regole che dicono quali coppie il bot opera e in che stato e' il registro
vivevano sparse in tre script (`scripts/optimize.py`, `scripts/discover_strategies.py`,
`scripts/gate_progress.py`) e in `bot/learning/adaptation.py`: ognuno ricalcolava
la propria versione, e quando una divergeva nessuno se ne accorgeva (e' successo
tre volte sul solo criterio «validata»). Da qui si leggono TUTTI: il gate quando
scrive il documento `dashboard/gate`, `gate_progress` quando stampa, il controllo
orario quando riassume.

Regole di questo modulo:
  * funzioni PURE su dizionari gia' decodificati (`decode_pairs`): niente rete,
    niente motore di backtest, niente `requests`. Il bot le importa nel processo
    che gira ogni 30 secondi, quindi l'import deve costare zero;
  * i numeri escono come dizionari e liste `[{valore, n}]`, mai liste di liste:
    Firestore e RTDB le rifiutano (`docs/controllo_schema.md`, regole comuni);
  * le soglie si leggono dalle stesse variabili d'ambiente di `optimize.py`, con
    gli stessi default: un default diverso qui sarebbe una seconda regola.

Le uniche due funzioni che toccano Firebase sono in fondo (`scrivi_doc_gate`,
`aggiorna_meta_gate`): scrivono il documento del gate e non sollevano mai.
"""
from __future__ import annotations

import math
import os
import time
from collections import Counter

# le stesse variabili, con gli stessi default, di scripts/optimize.py
MIN_PASSES = int(os.getenv("OPTIMIZER_MIN_PASSES", "3"))
FRESH_DAYS = float(os.getenv("OPTIMIZER_FRESH_DAYS", "3"))
NEW_DATA_MIN_S = float(os.getenv("OPTIMIZER_NEW_DATA_MIN_HOURS", "168")) * 3600


def tetto_coppie() -> int:
    """OPTIMIZER_MAX_PAIRS letto AL MOMENTO, non all'import: e' cosi' che lo legge
    la potatura nella discovery, e i test lo cambiano nell'ambiente a run in corso."""
    return int(os.getenv("OPTIMIZER_MAX_PAIRS", "3000"))


def _n(rec: dict, campo: str) -> int:
    try:
        return int((rec or {}).get(campo, 0) or 0)
    except (TypeError, ValueError):
        return 0


def _f(rec: dict, campo: str) -> float:
    try:
        return float((rec or {}).get(campo, 0) or 0)
    except (TypeError, ValueError):
        return 0.0


# --------------------------------------------------------------------------- #
# Chi si opera                                                                 #
# --------------------------------------------------------------------------- #
def coppie_fresche(pairs: dict, now: float | None = None) -> dict:
    """Le coppie ancora VALUTATE (viste da meno di FRESH_DAYS). Le altre sono
    congelate: la coin e' uscita dall'universo e non avanzano ne' falliscono."""
    ora = time.time() if now is None else now
    return {k: r for k, r in (pairs or {}).items()
            if isinstance(r, dict) and ora - _f(r, "last_seen_at") < FRESH_DAYS * 86400}


def coppie_validate(pairs: dict, now: float | None = None) -> list[str]:
    """LE COPPIE CHE IL BOT OPERA, in un posto solo.

    Fino al 24 set 2026 la regola (pass_count >= MIN_PASSES e vista da meno di
    FRESH_DAYS) era copiata in due file, optimize e discover: due copie della
    stessa regola prima o poi divergono (e' gia' successo tre volte su questo
    documento). Ora e' qui, e aggiunge la terza condizione: una madre SOSTITUITA
    da una figlia dell'intorno (`sostituita_da`) non si opera piu' — resta nel
    registro con la sua storia, ma la scommessa la porta avanti la figlia.
    Dal 25 set 2026 vive in `bot/core/registry.py`: optimize e discovery la
    importano da qui."""
    ora = time.time() if now is None else now
    return sorted(
        k for k, r in (pairs or {}).items()
        if isinstance(r, dict)
        and _n(r, "pass_count") >= MIN_PASSES
        and (ora - _f(r, "last_seen_at")) < FRESH_DAYS * 86400
        and not r.get("sostituita_da")
    )


def coppie_robuste(keys, min_coins: int | None = None) -> set:
    """La regola di robustezza del bot, COPIATA da
    `bot/learning/adaptation.py::TradingBotAdaptation._robust_only` (non si tocca
    quel file: qui serve la stessa regola senza importare il bot intero).

    Le strategie BASE devono essere passate su >= MIN_COINS_PER_STRATEGY coin
    distinte (anti-fluke a coin singola). Le GENERATE (`gen_*`) sono coin-specifiche
    per costruzione e sono esentate. Soglia <= 1 -> nessun filtro. Se le due copie
    divergessero, `tests/test_doc_gate.py` lo dice."""
    keys = [k for k in (keys or []) if isinstance(k, str) and "|" in k]
    if min_coins is None:
        from bot.config import settings          # import pigro: il modulo resta leggero
        min_coins = int(settings.MIN_COINS_PER_STRATEGY)
    if min_coins <= 1:
        return set(keys)
    generated = {k for k in keys if k.split("|", 1)[1].startswith("gen_")}
    coins_per_strat: dict[str, set] = {}
    for k in keys:
        sym, strat = k.split("|", 1)
        if not strat.startswith("gen_"):
            coins_per_strat.setdefault(strat, set()).add(sym)
    robust = {s for s, c in coins_per_strat.items() if len(c) >= min_coins}
    return generated | {k for k in keys if k.split("|", 1)[1] in robust}


def coppie_operate(pairs: dict, now: float | None = None,
                   min_coins: int | None = None) -> list[str]:
    """Validate E robuste: e' l'insieme che `adaptation.load_params` mette davvero
    in mano al bot."""
    return sorted(coppie_robuste(coppie_validate(pairs, now), min_coins))


# --------------------------------------------------------------------------- #
# Di che cosa e' fatto il registro                                             #
# --------------------------------------------------------------------------- #
def salute_registro(pairs: dict) -> dict:
    """Il gemello in numeri di `scripts/state_snapshot._salute_registro` (che
    resta com'e' e produce righe di testo).

    `occupazione` e' la parte del tetto che NESSUNO pota: le base (le pota solo
    optimize, per anzianita') piu' le generate con almeno una conferma (intoccabili
    per scelta). E' il numero del difetto del 31 agosto: quando arriva al tetto, le
    candidate nuove non hanno posto e il registro smette di accumulare — per quante
    ne trovi la ricerca. `alleggerito` = almeno una VALIDATA senza i campi
    descrittivi (`last_pnl_pct`): o l'alleggerimento d'emergenza di `slim_registry`
    o una promozione avvenuta dalla chiusura della finestra senza ripassare dal
    merge; in entrambi i casi la scheda in dashboard e' senza PnL."""
    pairs = {k: r for k, r in (pairs or {}).items() if isinstance(r, dict)}
    base = sum(1 for r in pairs.values() if not r.get("generated"))
    gen = len(pairs) - base
    gen_con_pass = sum(1 for r in pairs.values()
                       if r.get("generated") and _n(r, "pass_count") > 0)
    alleggerito = any(_n(r, "pass_count") >= MIN_PASSES and r.get("last_pnl_pct") is None
                      for r in pairs.values())
    return {"coppie": len(pairs), "base": base, "generate": gen,
            "generate_con_conferme": gen_con_pass,
            "occupazione": base + gen_con_pass, "limite": tetto_coppie(),
            "alleggerito": bool(alleggerito)}


def distribuzione_pass(pairs: dict, now: float | None = None) -> dict:
    """Quante coppie VIVE a ogni numero di conferme, su quante coin distinte, e i
    tre numeri che dicono se il fronte sta maturando davvero:
      * `congelate`: non piu' valutate da FRESH_DAYS (escluse da tutto il resto);
      * `a_un_passo`: vive, a MIN_PASSES-1 conferme e con la finestra aperta;
      * `finestre_scadute`: di queste, quante hanno gia' la settimana di dati:
        si validano al primo giro in cui ripassano.
    Una coppia a un passo SENZA finestra non conta: la finestra si apre solo
    quando ripassa, quindi per lei la prossima conferma non ha una data."""
    ora = time.time() if now is None else now
    fresche = coppie_fresche(pairs, ora)
    congelate = [r for k, r in (pairs or {}).items()
                 if isinstance(r, dict) and k not in fresche]
    per_livello: dict[int, list] = {}
    for r in fresche.values():
        per_livello.setdefault(_n(r, "pass_count"), []).append(r.get("symbol"))
    dist = [{"pass": p, "coppie": len(v), "coin": len({s for s in v if s})}
            for p, v in sorted(per_livello.items())]
    con_pass = [r for r in fresche.values() if _n(r, "pass_count") > 0]
    aperte = [r for r in con_pass if _f(r, "window_start") > 0]
    a_un_passo = [r for r in aperte if _n(r, "pass_count") == MIN_PASSES - 1]
    scadute = [r for r in a_un_passo if _f(r, "window_start") + NEW_DATA_MIN_S <= ora]
    return {"distribuzione": dist,
            "vive": len(fresche),
            "congelate": len(congelate),
            "congelate_con_conferme": sum(1 for r in congelate if _n(r, "pass_count") > 0),
            "con_conferme": len(con_pass),
            "finestre_aperte": len(aperte),
            "a_un_passo": len(a_un_passo),
            "finestre_scadute": len(scadute),
            "coin_finestre_scadute": len({r.get("symbol") for r in scadute if r.get("symbol")})}


def statistica_t(pairs: dict) -> dict:
    """La statistica t delle VALIDATE (24 set 2026): misurata dal gate per ogni
    coppia, NON ancora un criterio. Si contano tutte le coppie a >= MIN_PASSES con
    `last_t`, anche le congelate: e' una misura sulla storia, non sull'operativita'.
    `mediana` e' l'elemento centrale superiore, come la stampa di gate_progress."""
    con_t = sorted((float(r["last_t"]), k) for k, r in (pairs or {}).items()
                   if isinstance(r, dict) and _n(r, "pass_count") >= MIN_PASSES
                   and r.get("last_t") is not None)
    if not con_t:
        return {"misurate": 0, "sopra_2": 0, "sopra_3": 0, "mediana": None, "piu_basse": []}
    return {"misurate": len(con_t),
            "sopra_2": sum(1 for t, _ in con_t if t >= 2.0),
            "sopra_3": sum(1 for t, _ in con_t if t >= 3.0),
            "mediana": con_t[len(con_t) // 2][0],
            "piu_basse": [{"coppia": k, "t": t} for t, k in con_t[:3]]}


def _keep_di(rec) -> float | None:
    lp = rec.get("last_params") if isinstance(rec, dict) else None
    v = lp.get("profit_lock_keep") if isinstance(lp, dict) else None
    try:
        return None if (v is None or isinstance(v, bool)) else float(v)
    except (TypeError, ValueError):
        return None


def conta_keep(pairs: dict, validated) -> dict:
    """Quale keep del profit-lock il gate ha scelto per le coppie validate, da
    `last_params["profit_lock_keep"]`. Una validata SENZA la chiave non e' un
    errore: e' stata validata prima del parametro e opera col keep di allora
    (`lock_keep` -> default); si conta in `non_rivalutate`."""
    conta: Counter = Counter()
    senza = 0
    for k in validated or []:
        v = _keep_di((pairs or {}).get(k))
        if v is None:
            senza += 1
        else:
            conta[v] += 1
    return {"distribuzione": [{"valore": v, "n": n} for v, n in sorted(conta.items())],
            "non_rivalutate": senza}


def scala_str(mults) -> str | None:
    """`(1.5, 3.0, 5.0)` -> `"1.5/3/5"`: la scala come stringa, perche' una lista
    dentro una lista Firestore la rifiuta."""
    if not mults:
        return None
    try:
        return "/".join(f"{float(m):g}" for m in mults)
    except (TypeError, ValueError):
        return None


def scala_distribuzione(pairs: dict, validated) -> list[dict]:
    """[{scala, n}] delle validate, da `last_params.scale_r_mults`; le coppie
    senza scala nei parametri (validate prima dello scale-out) vanno sotto
    `"nessuna"`."""
    conta: Counter = Counter()
    for k in validated or []:
        rec = (pairs or {}).get(k)
        lp = rec.get("last_params") if isinstance(rec, dict) else None
        s = scala_str(lp.get("scale_r_mults") if isinstance(lp, dict) else None)
        conta[s or "nessuna"] += 1
    return [{"scala": s, "n": n} for s, n in sorted(conta.items(), key=lambda kv: (-kv[1], kv[0]))]


def breakeven_n(pairs: dict, validated) -> int:
    """Quante validate hanno scelto lo stop a break-even (`last_params.sl_to_breakeven`)."""
    n = 0
    for k in validated or []:
        rec = (pairs or {}).get(k)
        lp = rec.get("last_params") if isinstance(rec, dict) else None
        if isinstance(lp, dict) and lp.get("sl_to_breakeven"):
            n += 1
    return n


def senza_promessa(pairs: dict, validated) -> int:
    """Validate senza `last_pf`: per loro la deriva va in fail-open (misurato il
    25 set 2026: 72 su 131 prima che `last_pf` entrasse nel nucleo)."""
    return sum(1 for k in validated or []
               if isinstance((pairs or {}).get(k), dict)
               and (pairs[k].get("last_pf") is None or _f(pairs[k], "last_pf") <= 0))


# --------------------------------------------------------------------------- #
# Il documento del gate: pulizia e scrittura                                   #
# --------------------------------------------------------------------------- #
_VIETATI_CHIAVE = str.maketrans({c: "_" for c in ".#$[]/"})


def pulisci_per_firestore(obj):
    """Rende un documento accettabile a Firestore E al RTDB, senza sollevare:
    NaN/inf -> None; tuple -> liste; una lista dentro una lista -> `{"valori": [...]}`
    (Firestore rifiuta le liste annidate); nelle chiavi `. # $ [ ] /` -> `_`
    (il RTDB le rifiuta); le chiavi non-stringa diventano stringhe."""
    if isinstance(obj, bool) or obj is None or isinstance(obj, (str, int)):
        return obj
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if isinstance(obj, dict):
        return {str(k).translate(_VIETATI_CHIAVE): pulisci_per_firestore(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set, frozenset)):
        out = []
        for v in obj:
            v = pulisci_per_firestore(v)
            out.append({"valori": v} if isinstance(v, list) else v)
        return out
    return str(obj)


def leggi_doc_gate(fb) -> dict:
    """Il documento del giro precedente, o {} — mai un'eccezione."""
    try:
        doc = fb.get_doc("dashboard", "gate")
        return dict(doc) if isinstance(doc, dict) else {}
    except Exception as exc:  # noqa: BLE001
        print(f"[gate-doc] documento precedente non leggibile ({str(exc)[:120]})")
        return {}


def scrivi_doc_gate(fb, doc: dict) -> bool:
    """Firestore `dashboard/gate`, poi lo specchio RTDB `/gate`. Non solleva mai:
    il documento e' un racconto del giro, e un racconto non salvato non deve
    costare le conferme appena guadagnate. True se almeno Firestore l'ha preso."""
    doc = pulisci_per_firestore(doc)
    ok = False
    try:
        fb.set_doc("dashboard", "gate", doc)
        ok = True
    except Exception as exc:  # noqa: BLE001
        print(f"[gate-doc] Firestore dashboard/gate non scritto ({str(exc)[:160]})")
    try:
        fb.set_rtdb("/gate", doc)
    except Exception as exc:  # noqa: BLE001
        print(f"[gate-doc] specchio RTDB /gate non scritto ({str(exc)[:160]})")
    return ok


def aggiorna_meta_gate(fb, meta: dict) -> bool:
    """Scrive `in_corso` (o `errore`) SENZA cancellare le sezioni del giro
    precedente: si legge il documento, si fonde il solo `meta`, si riscrive.
    Cosi' il controllo orario e la dashboard continuano a mostrare l'ultimo giro
    finito mentre questo lavora. Non solleva mai."""
    doc = leggi_doc_gate(fb)
    prima = dict(doc.get("meta") or {}) if isinstance(doc.get("meta"), dict) else {}
    prima.update(meta)
    prima.setdefault("versione_schema", 1)
    prima.setdefault("generato_da", "discovery")
    doc["meta"] = prima
    return scrivi_doc_gate(fb, doc)
