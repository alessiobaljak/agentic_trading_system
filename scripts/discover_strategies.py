"""
Scoperta autonoma di NUOVE strategie (il "cervello" che ne aggiunge altre).

Genera N strategie candidate (combinazioni di feature su indicatori, vedi
bot/strategies/generator.py) e le valida con lo STESSO gate delle 6 base:
walk-forward OUT-OF-SAMPLE, al netto di fee+funding. Le candidate che passano su
una crypto vengono:
  * aggiunte al registro validato (strategy_registry/validated) -> operabili dal bot
  * salvate come spec su discovered_strategies/specs -> il bot le ricostruisce
NON tocca le strategie esistenti né la copertura del GATE 1.

Le strategie sono DATA (spec), non codice eseguito: sicuro e scalabile a centinaia.

Uso:
    python -m scripts.discover_strategies --top 25 --generate 40 --windows 3
"""
from __future__ import annotations

import argparse
import os
import time
from datetime import date

from backtesting.data_loader import load_candles
from bot.strategies.generated import MARKET_FEATURES, MARKET_SYMBOL, spec_id
from backtesting.engine import (StrategyStats, gate_verdict, max_drawdown, pf_by_regime,
                                pf_without_top, t_stat)
from backtesting.optimizer import WalkForwardOptimizer
from backtesting.parallel import n_workers, parallel_map
from bot.config import settings
from bot.core.firebase_client import decode_pairs, encode_pairs, get_firebase
from bot.core.indicators import compute_indicator_frame
from bot.strategies.generated import GeneratedStrategy
from bot.ai.hypotheses import propose as ai_propose
from bot.execution.exit_logic import SCALE_LADDER_CANDIDATES, ladder_from_mfe
from bot.ai.universe_filter import filter_universe as ai_filter_universe
from bot.strategies.generator import generate_specs, mutate, varianti_da_referto
from scripts.optimize import (FRESH_DAYS, MIN_PASSES, NEW_DATA_MIN_S, _min_history,
                              coin_in_maturazione, drifted_from_paper, judge_window,
                              publish_timeline, conferme_da_proteggere, scrivi_registro,
                              slim_registry, top_symbols_by_volume)

# stato pesante per-worker (optimizer + specs + parametri), costruito una volta per
# processo dall'initializer. Vedi _disc_init / _disc_one (parallelizzazione discovery).
_W: dict = {}


def _tondo(v: float) -> float:
    """Due soglie a cinque punti di distanza sono la stessa soglia (RSI 70 e 72
    sparano negli stessi momenti nove volte su dieci); i numeri piccoli si
    confrontano al millesimo."""
    return round(v / 5.0) * 5.0 if abs(v) >= 5.0 else round(v, 3)


def firma_spec(spec: dict) -> str:
    """LA LOGICA CHE OPERA, non l'id.

    `spec_id` e' un hash di tutto: due spec che differiscono per una soglia di
    due punti, o SOLO per `rr` — che sotto scale-out non ha alcun effetto sulle
    uscite (backlog B2bis) — hanno id diversi e per il sistema sono «strategie
    diverse». Il 21 settembre 2026 USELESSUSDT aveva tre coppie validate con PF
    1,541 / 1,541 / 1,54: la stessa scommessa contata tre volte, che il bot ha
    messo in fila — stop, riapre, stop, riapre. Qui `rr` e' escluso e le soglie
    sono arrotondate, cosi' le gemelle hanno la stessa firma."""
    feats = []
    for f in spec.get("features") or []:
        parti = [str(f.get("kind"))]
        for k, v in sorted(f.items()):
            if k == "kind":
                continue
            parti.append(f"{k}={_tondo(v) if isinstance(v, (int, float)) else v}")
        feats.append("|".join(parti))
    feats.sort()
    adx = _tondo(float(spec.get("min_adx", 0) or 0))
    vol = round(float(spec.get("volume_mult", 0) or 0) * 2) / 2
    atr = float(spec.get("atr_mult_stop", 0) or 0)
    firma = ";".join(feats) + f";adx={adx:g};vol={vol:g};atr={atr:g}"
    # il LATO operato e' logica (23 set 2026, varianti dai referti): «solo long»
    # e' una scommessa diversa dal genitore che opera entrambi i lati, altrimenti
    # `scarta_gemelle` butterebbe via la variante prima ancora di provarla.
    solo = str(spec.get("solo") or "").lower()
    if solo in ("long", "short"):
        firma += f";solo={solo}"
    return firma


def scarta_gemelle(specs: list[dict], existing: dict) -> tuple[list[dict], int]:
    """Toglie dalle CANDIDATE NUOVE quelle con la stessa firma di una gia' nota o
    di un'altra candidata. Le spec gia' nel registro passano intatte: non si
    butta via niente di gia' validato, si impedisce che entrino altre copie."""
    note = {firma_spec(sp) for sp in existing.values() if isinstance(sp, dict)}
    viste: set[str] = set()
    tenute: list[dict] = []
    scartate = 0
    for sp in specs:
        if sp.get("id") in existing:
            tenute.append(sp)
            continue
        fm = firma_spec(sp)
        if fm in note or fm in viste:
            scartate += 1
            continue
        viste.add(fm)
        tenute.append(sp)
    return tenute, scartate


def gemelle_validate(pairs: dict, existing: dict) -> list[tuple[str, list[str]]]:
    """Le gemelle GIA' validate sulla stessa coin: diagnostica, non rimozione.
    Sapere che ORCAUSDT ha otto coppie di cui cinque con la stessa firma e' il
    dato che serve per decidere; toglierle di nascosto no."""
    per_coin: dict[tuple[str, str], list[str]] = {}
    for key, rec in pairs.items():
        if not isinstance(rec, dict) or int(rec.get("pass_count", 0) or 0) < MIN_PASSES:
            continue
        if "|" not in key:
            continue
        sym, sid = key.split("|", 1)
        sp = existing.get(sid)
        if not isinstance(sp, dict):
            continue
        per_coin.setdefault((sym, firma_spec(sp)), []).append(sid)
    return sorted(((sym, ids) for (sym, _), ids in per_coin.items() if len(ids) > 1),
                  key=lambda t: -len(t[1]))


# LA RIVALUTAZIONE COMPLETA UNA VOLTA AL GIORNO (23 set 2026). Un giro rivaluta
# ~430 spec note su 200 coin: il 77% del lavoro. Ma una conferma o un fallimento
# contano SOLO quando si chiude la finestra dei 7 giorni, e la finestra si
# misura sui giorni di dati: rivalutare la stessa coppia otto volte al giorno da'
# otto volte lo stesso verdetto su 96 candele in piu' su 165.000. Quindi: la
# rivalutazione completa gira nel primo giro dopo mezzanotte UTC (quando le
# finestre si chiudono davvero); negli altri giri si rivalutano SOLO le coppie
# che possono cambiare stato adesso — quelle con almeno una conferma e la
# finestra in chiusura o gia' scaduta — cosi' una terza conferma non aspetta
# mai piu' di tre ore. Le candidate nuove restano ogni giro: la scoperta non
# rallenta. Misurato prima: 2h29 a giro; atteso dopo: ~1h nei giri normali.
REEVAL_DAILY = os.getenv("DISCOVERY_REEVAL_DAILY", "true").lower() == "true"
REEVAL_HOUR_MAX = int(os.getenv("DISCOVERY_REEVAL_HOUR_MAX", "3"))   # UTC: 00:xx-02:59


def giro_giornaliero(now: float) -> bool:
    """True nel primo giro dopo mezzanotte UTC (il timer parte alle 00:00 con un
    ritardo casuale fino a 10 minuti e il giro dura ~2h)."""
    from datetime import datetime, timezone
    return datetime.fromtimestamp(now, timezone.utc).hour < REEVAL_HOUR_MAX


def spec_urgenti(pairs: dict, now: float, margine_s: float = 3 * 3600) -> set:
    """Le spec con almeno una coppia che PUO' cambiare stato in questo giro: ha
    gia' una conferma e la sua finestra si chiude entro `margine_s` o e' gia'
    scaduta. Rivalutarle ogni giro costa poco (sono decine, non centinaia) e
    tiene la terza conferma a tre ore di distanza, non a un giorno."""
    from scripts.optimize import NEW_DATA_MIN_S
    out: set = set()
    for k, r in pairs.items():
        if not r.get("generated") or "|" not in k:
            continue
        if int(r.get("pass_count", 0) or 0) < 1:
            continue
        start = float(r.get("window_start", 0) or 0)
        if start <= 0:
            continue
        if now - start >= NEW_DATA_MIN_S - margine_s:
            out.add(k.split("|", 1)[1])
    return out


def specs_da_rivalutare(existing: dict, reg: dict, cap: int,
                        completa: bool = True, now: float | None = None) -> tuple[list[dict], dict]:
    """Quali spec gia' note si ri-valutano in questo run, e con che priorita'.

    IL DIFETTO CHE CORREGGE, in una riga: il taglio buttava fuori proprio le coppie
    piu' vicine alla validazione.

    Una coppia generata prende una conferma SOLO ripassando il gate (`judge_window`
    e' chiamato, nella discovery, unicamente sulle coppie che passano). Quindi una
    spec che non viene ri-valutata non e' "in attesa": e' ferma per sempre, e il
    calendario delle conferme continua a stampare per lei una data che nessuno
    onorera'.

    La versione precedente proteggeva dal taglio le sole spec GIA' VALIDATE, e le
    validate sono zero da quando il registro esiste. Tutto il resto entrava
    nell'ordine in cui era stato scoperto e veniva tagliato a `cap`: le spec piu'
    vecchie dentro, le piu' recenti fuori — un criterio che con le conferme non
    c'entra niente. Una coppia a 2 passaggi su 3 poteva restare fuori dal taglio e
    non arrivare mai al terzo, senza che nessun contatore lo dicesse.

    E' la terza volta che un tetto pensato per limitare i TEMPI finisce per
    sacrificare l'unica cosa che il sistema sta producendo (le altre due: il tetto
    sulle coppie del registro il 31 agosto, e la quota morta per le generate senza
    conferme). Il criterio ora e' esplicito: **prima le conferme, poi l'anzianita'**.

    Le spec con almeno una conferma passano SEMPRE, anche a costo di sforare il cap:
    sono poche (una manciata di centinaia contro migliaia di candidate nuove) e sono
    l'unica cosa che il gate ha prodotto in tre settimane. Sacrificarle per stare nei
    tempi vuol dire non arrivare mai in fondo, che non e' un risparmio.

    Ritorna la lista di spec e un dizionario di diagnostica, che finisce su Firestore
    e da li' nel rapporto: senza, la differenza fra "il taglio morde" e "il taglio
    non morde" resta invisibile esattamente come lo era prima.
    """
    pairs = decode_pairs(reg.get("pairs"))
    # quante conferme ha gia' ogni spec. Una spec puo' vivere su piu' coin: conta la
    # coppia piu' avanti, perche' e' quella che il taglio rischia di buttare via.
    conferme: dict[str, int] = {}
    for k, r in pairs.items():
        if not r.get("generated") or "|" not in k:
            continue
        gid = k.split("|", 1)[1]
        conferme[gid] = max(conferme.get(gid, 0), int(r.get("pass_count", 0) or 0))

    # `sorted` e' stabile: a parita' di conferme resta l'ordine di scoperta, cioe'
    # esattamente il comportamento precedente per tutta la coda senza conferme.
    ordinate = sorted(existing.items(), key=lambda kv: -conferme.get(kv[0], 0))
    con_conferme = [s for gid, s in ordinate if conferme.get(gid, 0) > 0]
    senza = [s for gid, s in ordinate if conferme.get(gid, 0) == 0]
    if completa:
        scelte = con_conferme + senza[: max(0, cap - len(con_conferme))]
        modalita = "completa"
    else:
        urgenti = spec_urgenti(pairs, now if now is not None else time.time())
        scelte = [sp for gid, sp in ordinate if gid in urgenti]
        modalita = "solo urgenti"
    diag = {
        "reeval_cap": cap,
        "reeval_modalita": modalita,
        "n_specs_note": len(existing),
        "n_specs_rivalutate": len(scelte),
        "n_specs_con_conferme": len(con_conferme),
        "n_specs_tagliate": max(0, len(existing) - len(scelte)),
    }
    return scelte, diag


# quanti semi per giro. Erano 10 su ~100 candidate: la ricerca guidata (mutare i
# quasi-passaggi, con precedenza alle coin NON coperte) pesava un decimo, e la
# copertura restava ferma a 26 coin su 165 mentre le validate si impilavano sulle
# stesse. Il calcolo per i semi in piu' viene dalle strategie base saltate
# (OPTIMIZER_SKIP_BASE). 21 set 2026.
SEEDS = int(os.getenv("DISCOVERY_SEEDS", "30"))


def mutation_seeds(fb, existing: dict, limit: int = SEEDS,
                   pairs: dict | None = None) -> list[dict]:
    """Le spec da cui vale la pena evolvere: i QUASI-PASSAGGI del run precedente,
    con precedenza a quelli sulle coin che NON copriamo ancora.

    Una candidata fermata da UN SOLO criterio e per poco e' l'informazione piu'
    preziosa che un run produce: dice che in quella zona dello spazio delle
    strategie c'e' qualcosa, e che manca poco. Mutare li' e' una ricerca guidata;
    generare candidate a caso e' ricominciare da zero a ogni giro.

    LA PRECEDENZA ALLA COPERTURA, e perche' esiste. L'obiettivo dichiarato dal
    proprietario e' «un sistema che non si ferma mai»: se una moneta non e' coperta,
    la ricerca deve andare a cercare una strategia per QUELLA. Senza questa regola i
    semi si prendevano nell'ordine in cui capitavano, quindi l'evoluzione tendeva a
    rinforzare le coin dove qualcosa gia' funziona — e la copertura, che e' il numero
    che decide quante monete il bot potra' operare, non si muoveva.

    Non e' teoria: al 14 settembre le coppie validate erano 7, tutte sulla STESSA
    moneta. Un'ottava strategia su quella moneta non aggiunge una moneta operabile;
    la prima su una moneta nuova si'.

    Le due meta' restano entrambe: prima i semi che estenderebbero la copertura, poi
    gli altri a riempire. Abbandonare del tutto le coin gia' coperte sarebbe l'errore
    opposto — una coin con una sola coppia validata e' fragile, e la seconda serve.

    Fail-open in ogni punto: nessuna autopsia, autopsia illeggibile, registro non
    passato o quasi-passaggi su strategie BASE (che non sono spec mutabili) -> si
    torna esattamente al comportamento precedente.
    """
    near: list = []
    try:
        # PRIMA l'autopsia della discovery: e' l'unica che contiene spec generate,
        # cioe' le uniche mutabili. Quella dell'optimizer parla di strategie BASE,
        # che non sono spec — leggerla da sola darebbe sempre lista vuota.
        for doc_id in ("discover", "current"):
            near.extend(((fb.get_doc("gate_autopsy", doc_id) or {})
                         .get("near_misses") or []))
    except Exception:  # noqa: BLE001
        return []

    # coin gia' coperte = hanno almeno una coppia VALIDATA. E' la definizione che
    # conta per «quante monete potremmo operare»: una coin con due conferme non e'
    # ancora operabile, quindi cercare li' estende comunque la copertura.
    coperte: set = set()
    for r in (pairs or {}).values():
        if int(r.get("pass_count", 0) or 0) >= MIN_PASSES and r.get("symbol"):
            coperte.add(r["symbol"])

    estendono: list[dict] = []
    resto: list[dict] = []
    visti: set = set()
    for n in near:
        key = str(n.get("key", ""))
        if "|" not in key:
            continue
        sym, gid = key.split("|", 1)
        spec = existing.get(gid)
        if spec is None or gid in visti:
            continue
        visti.add(gid)
        (resto if sym in coperte else estendono).append(spec)

    out = estendono[:limit] + resto[: max(0, limit - len(estendono))]
    if coperte and estendono:
        print(f"[discover] semi: {min(len(estendono), limit)} da coin NON coperte "
              f"(su {len(coperte)} gia' coperte)")
    return out[:limit]


def _publish_discover_autopsy(fb, evaluated: int, passed: int, binding: dict,
                              involved: dict, near: list, top_near: int = 40) -> dict:
    """Scrive l'autopsia della discovery, che e' dove sta il grosso del volume:
    l'optimizer valuta ~1500 coppie per run, la discovery oltre ventimila.

    Documento SEPARATO da quello dell'optimizer: sono due imbuti diversi (strategie
    classiche con grid search contro spec generate senza train) e mediarli
    nasconderebbe proprio la differenza che interessa. Best-effort: una diagnosi
    non salvata non deve far fallire un run di validazione.
    """
    near = sorted(near, key=lambda n: -(n.get("shortfall") or -9))[:top_near]
    rep = {"updated_at": time.time(), "evaluated": evaluated, "passed": passed,
           "diagnosed": int(sum(binding.values())),
           "binding": dict(sorted(binding.items(), key=lambda kv: -kv[1])),
           "involved": dict(sorted(involved.items(), key=lambda kv: -kv[1])),
           "near_misses": near, "near_miss_count": len(near)}
    try:
        fb.set_doc("gate_autopsy", "discover", rep)
    except Exception as exc:  # noqa: BLE001
        print(f"[autopsy] non salvata ({exc})")
    if rep["diagnosed"]:
        top = " · ".join(f"{k} {v}" for k, v in list(rep["binding"].items())[:5])
        print(f"[autopsy] {passed}/{evaluated} passate · muoiono su: {top}")
        print(f"[autopsy] quasi-passaggi (semi per le mutazioni del prossimo run): "
              f"{len(near)}")
    return rep


def prove_dal_paper(fb) -> str:
    """Cosa il PAPER ha misurato, in forma leggibile da chi propone strategie.

    Fino al 19 settembre l'AI riceveva questo, e solo questo:

        «Timeframe operativo: 15m. Universo: crypto futures USDT-M su Binance.»

    Proponeva alla cieca. Non sapeva che il prezzo si ferma a meta' strada dal primo
    obiettivo, che le short perdevano e le long no, ne' su quale criterio muoiono le
    candidate. Avevamo costruito un sistema che misura tutto e poi non lo dice a chi
    deve inventare le soluzioni.

    Qui si mettono insieme SOLO FATTI MISURATI, con il loro campione accanto. Niente
    interpretazioni e niente istruzioni: un'ipotesi la deve formulare chi legge, e
    il gate resta l'unico che decide se vale. Un numero senza il suo campione
    sarebbe peggio di nessun numero — chi legge non saprebbe quanto pesarlo.

    Fail-open in ogni punto: qualunque pezzo manchi, si salta quella riga.
    """
    righe: list[str] = []

    try:
        drift = fb.get_doc("drift", "current") or {}
    except Exception:  # noqa: BLE001
        drift = {}
    glob = drift.get("global") or {}
    if glob.get("trades"):
        righe.append(
            f"PAPER (vissuto, {glob['trades']} trade chiusi): profit factor "
            f"{glob.get('live_pf')} contro {glob.get('expected_pf')} promesso dal gate.")
        if glob.get("mfe_median") is not None and glob.get("first_rung_r"):
            righe.append(
                f"Escursione favorevole mediana {glob['mfe_median']}R contro un primo "
                f"take-profit a {glob['first_rung_r']}R: il prezzo si ferma prima di "
                f"arrivare al primo incasso.")

    try:
        trades = fb.query_collection("trades", order_by="exit_ts") or []
    except Exception:  # noqa: BLE001
        trades = []
    if trades:
        for direzione in ("long", "short"):
            sel = [t for t in trades
                   if str(t.get("direction", "")).lower() == direzione]
            if sel:
                vinti = sum(1 for t in sel if float(t.get("pnl", 0) or 0) > 0)
                pnl = sum(float(t.get("pnl", 0) or 0) for t in sel)
                righe.append(f"Direzione {direzione}: {len(sel)} trade, {vinti} vinti, "
                             f"PnL {pnl:+.2f}.")

    try:
        aut = fb.get_doc("gate_autopsy", "current") or {}
    except Exception:  # noqa: BLE001
        aut = {}
    binding = aut.get("binding") or {}
    if binding and aut.get("evaluated"):
        top = " · ".join(f"{k} {v}" for k, v in list(binding.items())[:4])
        righe.append(f"GATE: su {aut['evaluated']} valutazioni ne passano "
                     f"{aut.get('passed', 0)}; muoiono soprattutto su {top}.")

    if not righe:
        return ""
    return ("Prove misurate finora (campioni piccoli: sono indizi, non leggi).\n"
            + "\n".join(f"- {r}" for r in righe))


def scala_dal_paper(fb, min_trades: int = 10):
    """La scala di TP suggerita da dove il prezzo e' DAVVERO arrivato nel paper.

    E' l'anello che mancava. Il paper misurava `mfe_r` su ogni trade chiuso, il
    rilevatore di deriva lo confrontava col primo gradino e scriveva «mfe mediana
    0,74R < primo TP 1,50R» su una coppia dopo l'altra — e il gate continuava a
    scegliere fra quattro scale scritte a mano, senza mai vedere quel numero.

    Si calcola sui trade di TUTTE le coppie insieme, di proposito: per coppia ce ne
    sono uno o due e un quantile su due numeri non significa niente, mentre «quanto
    lontano arriva il prezzo in unita' di rischio» e' soprattutto una proprieta'
    della scala temporale e del mercato, non della singola moneta.

    Fail-open: senza Firebase, senza trade o senza abbastanza campione ritorna None
    e il gate resta esattamente com'era.
    """
    try:
        trades = fb.query_collection("trades", order_by="exit_ts") or []
    except Exception as exc:  # noqa: BLE001
        print(f"[paper] misura mfe non disponibile ({str(exc)[:80]}) -> scale fisse")
        return None
    mfes = [t.get("mfe_r") for t in trades if t.get("mfe_r") is not None]
    scala = ladder_from_mfe(mfes, min_trades=min_trades)
    if scala:
        print(f"[paper] {len(mfes)} trade chiusi -> scala candidata dal vissuto: "
              f"{list(scala)} (si aggiunge alle {len(SCALE_LADDER_CANDIDATES)} fisse, "
              f"non le sostituisce: sceglie il gate)")
    elif mfes:
        print(f"[paper] solo {len(mfes)} trade con mfe (ne servono {min_trades}): "
              f"scale fisse")
    return scala


def candidate_ladders(scala_paper=None) -> tuple:
    """Le scale che il gate mettera' a confronto per una coppia.

    Le quattro fisse sempre; quella misurata dal paper in piu', se c'e' ed e'
    diversa. Mai al posto delle altre — una misura su pochi trade puo' PROPORRE,
    non decidere."""
    if not scala_paper:
        return SCALE_LADDER_CANDIDATES
    if tuple(scala_paper) in {tuple(c) for c in SCALE_LADDER_CANDIDATES}:
        return SCALE_LADDER_CANDIDATES
    return SCALE_LADDER_CANDIDATES + (tuple(scala_paper),)


#: quante varianti dai referti entrano in un giro. Sostituiscono altrettante
#: casuali (come le ipotesi AI): il giro non si allunga, e dieci e' gia' piu'
#: delle ipotesi che il referto puo' formulare con i ~40 trade di oggi.
REFERTI_VARIANTI_MAX = int(os.getenv("DISCOVERY_REFERTI_MAX", "10"))


def varianti_dai_referti(fb, existing: dict, interval: str,
                         limit: int = REFERTI_VARIANTI_MAX) -> list[dict]:
    """Le VARIANTI che il paper propone, pronte per il gate (backlog B8).

    Il bot scrive in `learning/referti` le ipotesi ricavate dai post-mortem dei
    trade chiusi, con regole dichiarate prima (short 4/4 persi -> «solo long»;
    stop largo in due referti -> «stop piu' stretto»; ...). Qui ogni ipotesi su
    una spec NOTA e dello stesso timeframe diventa una spec figlia, con un solo
    cambiamento e un id suo, e si mette in coda alle candidate del giro: il gate
    la giudica sulla storia, tre conferme piu' holdout, come tutte le altre. Il
    paper propone, non decide — e' la stessa regola della scala dei TP.

    Si scartano prima le figlie gia' note per id o per firma (`scarta_gemelle`
    le toglierebbe comunque, ma qui sprecherebbero il tetto), e si tiene una
    figlia per id.

    Fail-open: senza documento, senza Firebase o con un documento malformato si
    torna a lista vuota e il giro e' identico a prima, con una riga di log.
    """
    try:
        doc = fb.get_doc("learning", "referti") or {}
        ipotesi = doc.get("ipotesi") or []
    except Exception as exc:  # noqa: BLE001
        print(f"[discover] referti del paper non disponibili ({str(exc)[:80]}) "
              f"-> nessuna variante")
        return []
    if not ipotesi:
        return []
    tf_bot = settings.ORCHESTRATOR_TIMEFRAME
    firme_note = {firma_spec(sp) for sp in existing.values() if isinstance(sp, dict)}
    out: list[dict] = []
    visti: set[str] = set()
    tagliate = 0
    for ip in ipotesi:
        if not isinstance(ip, dict):
            continue
        # L'id del genitore dev'essere una stringa: con una lista o un dict al
        # suo posto `existing.get` esplodeva (TypeError, non hashabile) e UN
        # documento storto fermava l'intero giro della discovery — il contrario
        # del fail-open promesso sopra (rilievo dei revisori, 23 set 2026).
        gid = ip.get("strategia")
        if not isinstance(gid, str):
            continue
        genitore = existing.get(gid)
        if not isinstance(genitore, dict):
            continue
        if (genitore.get("timeframe") or tf_bot) != interval:
            continue
        try:
            figlia = varianti_da_referto(genitore, str(ip.get("tipo") or ""))
        except Exception as exc:  # noqa: BLE001
            print(f"[discover] variante {ip.get('strategia')} ({ip.get('tipo')}) "
                  f"non costruibile: {str(exc)[:80]}")
            continue
        if figlia is None:
            continue
        fid = figlia["id"]
        if fid in existing or fid in visti:
            continue
        fm = firma_spec(figlia)
        if fm in firme_note:
            continue
        if len(out) >= limit:
            tagliate += 1
            continue
        visti.add(fid)
        firme_note.add(fm)
        out.append(figlia)
    if out:
        riga = " · ".join(f"{v['genitore']} -> {v['id']} ({v['ipotesi']})" for v in out[:6])
        print(f"[discover] {len(out)} varianti dai referti del paper (B8): {riga}"
              f"{' ...' if len(out) > 6 else ''}")
    if tagliate:
        print(f"[discover] {tagliate} varianti dai referti oltre il tetto di {limit} "
              f"(DISCOVERY_REFERTI_MAX): restano per il prossimo giro")
    return out


# LE TRE CONFERME NELLO STESSO GIRO, per le varianti dai referti (24 set 2026).
#
# Domanda del proprietario: «se impari e vuoi rivalidare, perche' non rivalidi
# dall'inizio fino a oggi e, se passa, la riprovi subito? Sei sicuro che i sistemi
# intelligenti aspettino davvero tre settimane?». No, non aspettano: la regola
# delle tre conferme distanziate di una settimana e' nata contro la lotteria delle
# migliaia di candidate casuali, e il tempo di calendario non e' l'ingrediente —
# lo sono i dati che finiscono in momenti diversi (e' la stessa idea di
# scripts/backfill_passes.sh, gia' usata a settembre). Una variante e' UNA
# modifica mirata a una spec gia' nota, non un'estrazione: qui si valuta con i
# dati fino a oggi, fino a 8 giorni fa e fino a 16 giorni fa nello stesso giro.
# Passa tutte e tre piu' l'holdout -> validata oggi; passa solo con i dati di oggi
# -> muore subito invece che fra tre settimane. Le due date arretrate stanno
# PRIMA del periodo in cui il paper ha formulato l'ipotesi: sono la parte della
# prova che il paper non ha mai visto. Costo: due valutazioni in piu' per
# variante passata, su al massimo REFERTI_VARIANTI_MAX spec.
RETRO_CONFERME = os.getenv("DISCOVERY_RETRO_CONFERME", "true").lower() == "true"
RETRO_STEP_DAYS = float(os.getenv("DISCOVERY_RETRO_STEP_DAYS", "8"))


def conferme_retroattive(opt, sym: str, candles, frame, spec: dict,
                         scale_candidates=None, context_by_ts=None,
                         n: int = MIN_PASSES - 1, step_days: float = RETRO_STEP_DAYS,
                         min_history: int = 0) -> int:
    """Quante delle `n` valutazioni con fine dati arretrata (step_days, 2*step_days,
    ...) la spec passa. Si ferma alla prima bocciatura: contano solo conferme
    consecutive, come nel registro. Il passo deve superare la finestra del pass
    onesto (168 ore), altrimenti due valutazioni contano come una."""
    if not candles or n <= 0:
        return 0
    if step_days * 86400 < NEW_DATA_MIN_S:
        return 0
    fine = candles[-1].open_time.timestamp()
    ok = 0
    for k in range(1, n + 1):
        taglio_ts = fine - k * step_days * 86400
        cut = 0
        for i, c in enumerate(candles):
            if c.open_time.timestamp() > taglio_ts:
                break
            cut = i + 1
        if cut < max(min_history, 1):
            break
        r = evaluate_spec(opt, sym, candles[:cut], frame.iloc[:cut].reset_index(drop=True),
                          spec, scale_candidates=scale_candidates,
                          context_by_ts=context_by_ts)
        if not r.get("passed"):
            break
        ok += 1
    return ok


def _disc_init(args, end: str, specs: list, scala_paper=None) -> None:
    opt = WalkForwardOptimizer(n_windows=args.windows, interval=args.interval)
    # IL MERCATO NEL GATE. `scripts/optimize.py` carica BTC come contesto
    # cross-asset da sempre; la discovery — che valida TUTTE le spec che il bot
    # opera davvero — non lo faceva, quindi per le strategie generate il mercato
    # non era «poco pesato»: non era proprio nella stanza. Senza questa riga una
    # spec che usa una feature di mercato non produce segnali e viene bocciata
    # per assenza di dati invece che per demerito.
    btc_ctx = None
    try:
        btc = load_candles(MARKET_SYMBOL, args.interval, args.start, end,
                           prefer=args.source)
        if len(btc) >= 200:
            btc_ctx = opt.bt.build_context(MARKET_SYMBOL, btc)
    except Exception as exc:  # noqa: BLE001
        print(f"[discover] contesto di mercato non disponibile nel worker: {exc}")
    _W.update(opt=opt, args=args, end=end, specs=specs,
              min_history=_min_history(args.interval), scala_paper=scala_paper,
              btc_ctx=btc_ctx)


def _disc_one(sym: str) -> tuple[str, dict, list, dict, int, list, dict]:
    """Valuta TUTTE le spec su un simbolo (nei worker).
    Ritorna (sym, passed_entries, passed_keys, specs_passed, n_eval, summary, diag).

    `diag` e' l'autopsia LOCALE: conteggi dei criteri che hanno fermato le spec e
    i pochi quasi-passaggi. Si aggregano numeri, non le migliaia di valutazioni
    bocciate — la diagnosi deve costare quanto un contatore, altrimenti non
    verrebbe fatta."""
    args, end, specs = _W["args"], _W["end"], _W["specs"]
    candles = load_candles(sym, args.interval, args.start, end, prefer=args.source)
    if len(candles) < _W["min_history"]:
        return (sym, {}, [], {}, 0, [], {})
    # coin DELISTATA: storia a sufficienza ma serie ferma a mesi fa. Vedi la nota
    # gemella in scripts/optimize.py: validare su un mercato che non esiste piu'.
    from backtesting.quality import looks_delisted
    from bot.config import timeframe_hours as _tfh
    if looks_delisted(candles, end, _tfh(args.interval)):
        print(f"[discover] {sym}: serie ferma al "
              f"{candles[-1].open_time:%Y-%m-%d} -> coin delistata, saltata")
        return (sym, {}, [], {}, 0, [], {})
    frame = compute_indicator_frame(candles)
    entries: dict = {}
    passed_keys: list = []
    specs_passed: dict = {}
    summary: list = []
    binding: dict = {}
    involved: dict = {}
    near: list = []
    n_eval = 0
    for spec in specs:
        # il contesto di mercato SOLO alle spec che lo usano: per le altre il
        # motore salterebbe una ricerca per candela che non serve a nessuno (e'
        # cio' che il 22 set ha fatto sforare la finestra di 3h)
        usa_mercato = any((f.get("kind") in MARKET_FEATURES)
                          for f in (spec.get("features") or []) if isinstance(f, dict))
        r = evaluate_spec(_W["opt"], sym, candles, frame, spec,
                          scale_candidates=candidate_ladders(_W.get("scala_paper")),
                          context_by_ts=_W.get("btc_ctx") if usa_mercato else None)
        n_eval += 1
        if not r["passed"] and r.get("fail_criteria"):
            b = r.get("fail_binding") or "?"
            binding[b] = binding.get(b, 0) + 1
            for c in r["fail_criteria"]:
                involved[c] = involved.get(c, 0) + 1
            if r.get("near_miss"):
                near.append({"key": f"{sym}|{spec['id']}", "binding": b,
                             "shortfall": r.get("fail_shortfall"),
                             "pf": r["pf"], "trades": r["trades"],
                             "t_stat": r.get("t_stat")})
        if r["passed"]:
            key = f"{sym}|{spec['id']}"
            retro = 0
            if RETRO_CONFERME and spec.get("origine") == "referto":
                retro = conferme_retroattive(
                    _W["opt"], sym, candles, frame, spec,
                    scale_candidates=candidate_ladders(_W.get("scala_paper")),
                    context_by_ts=_W.get("btc_ctx") if usa_mercato else None,
                    min_history=_W["min_history"])
                print(f"[discover] {sym}|{spec['id']} (variante di "
                      f"{spec.get('genitore')}, {spec.get('ipotesi')}): conferme "
                      f"retroattive {retro}/{MIN_PASSES - 1}"
                      f"{' -> VALIDATA oggi' if retro >= MIN_PASSES - 1 else ''}")
            entries[key] = {
                "symbol": sym, "strategy": spec["id"], "params": {}, "spec": spec,
                "oos_pf": r["pf"], "oos_pnl_pct": r["pnl"],
                "oos_trades": r["trades"], "oos_win_rate": r["win"], "passed": True,
                # SENZA questi campi il registro perde: il pass onesto (data_end
                # assente faceva incrementare a OGNI run - il bug delle coppie a
                # 3 pass in un giorno), il veto di regime e la scala per-coppia.
                "holdout": r.get("holdout"), "regime_pf": r.get("regime_pf"),
                "oos_max_dd": r.get("max_dd"), "scale_r_mults": r.get("scale_r_mults"),
                "sl_to_breakeven": r.get("sl_to_breakeven"),
                "data_end": r.get("data_end", 0),
                # conferme raccolte NELLO STESSO GIRO con fine dati arretrata
                # (solo varianti dai referti): 2 = validata subito
                "conferme_retro": retro,
            }
            passed_keys.append(key)
            specs_passed[spec["id"]] = spec
            summary.append({"symbol": sym, "id": spec["id"], "pf": r["pf"],
                            "pnl": r["pnl"], "desc": GeneratedStrategy(spec).description})
    near.sort(key=lambda n: -(n.get("shortfall") or -9))
    return (sym, entries, passed_keys, specs_passed, n_eval, summary,
            {"binding": binding, "involved": involved, "near": near[:10]})


def evaluate_spec(opt: WalkForwardOptimizer, symbol: str, candles, frame, spec: dict,
                  scale_candidates=None, context_by_ts=None):
    """Aggrega le performance del spec sulle SOLE finestre out-of-sample e applica
    il GATE 1 (PF, win-rate, ritorno minimo, consistenza per finestra).

    Le finestre sono calcolate sul CORPO (holdout escluso): le spec generate non
    hanno train, quindi qui l'OOS era l'unica difesa — e veniva riusato identico a
    ogni run da migliaia di candidate (la lotteria). L'holdout finale, mai visto
    dalla selezione, e' la verifica che mancava."""
    body, cut = opt.split_holdout(candles)

    def _run_oos(ladder=None, be=None) -> tuple:
        """(stats OOS, ritorni per finestra) con una scala di TP data e, se
        indicato, la scelta sul break-even dopo il primo gradino."""
        st_all = StrategyStats(strategy=spec["id"])
        per_window: list[float] = []
        for (_ta, _tb, sa, sb) in opt._windows(len(body)):
            g = GeneratedStrategy(spec)
            if ladder:
                g.params = {**(getattr(g, "params", {}) or {}), "scale_r_mults": list(ladder)}
            if be is not None:
                g.params = {**(getattr(g, "params", {}) or {}), "sl_to_breakeven": bool(be)}
            st = opt.bt.run_strategy(g, symbol, body[sa:sb],
                                     frame=frame.iloc[sa:sb].reset_index(drop=True),
                                     context_by_ts=context_by_ts)
            st_all.trades.extend(st.trades)
            # consistenza: solo le finestre con trade (una finestra senza segnali non
            # e' una perdita -> non deve far fallire il gate).
            if st.trades:
                per_window.append(sum(t.pnl_pct for t in st.trades))
        return st_all, per_window

    # 1) PRESELEZIONE con la scala globale: serve solo a scartare in fretta le spec
    #    senza speranza, prima di spendere 4 backtest per la scelta della scala.
    oos, window_pnls = _run_oos()
    verdict = gate_verdict(window_pnls, len(oos.trades), oos.profit_factor(),
                           oos.win_rate(), oos.total_pnl_pct(),
                           max_dd=max_drawdown(oos.trades),
                           regime_pf=pf_by_regime(oos.trades),
                           pf_ex_top=pf_without_top(oos.trades))
    passed = verdict.ok

    # 2) SCALA DI TP PER-COPPIA anche per le GENERATE. Le classiche la scelgono nella
    #    grid search; le generate non hanno grid -> senza questo passo restavano per
    #    sempre sulla scala globale (e sono la maggioranza del registro).
    best_ladder = None
    best_be = None
    if passed and settings.SCALE_OUT_ENABLED:
        best_metric = None
        # le candidate arrivano dal CHIAMANTE, non da uno stato globale: cosi'
        # `evaluate_spec` resta una funzione di cio' che riceve, e un test puo'
        # verificarla senza ricostruire lo stato dei worker
        for cand in (scale_candidates or SCALE_LADDER_CANDIDATES):
            st_c, _ = _run_oos(cand)
            metric = st_c.total_pnl_pct() - max_drawdown(st_c.trades)
            if best_metric is None or metric > best_metric:
                best_metric, best_ladder = metric, list(cand)
        # 2b) BREAK-EVEN DOPO IL PRIMO GRADINO: lo decide il gate, per coppia
        #     (backlog A2). Le generate giravano TUTTE sul default globale senza
        #     che nessuno l'avesse mai provato; e con il lock ancorato al primo
        #     gradino (A1) il BE cambia significato. Una sola passata in piu' —
        #     l'alternativa al default sulla scala scelta — invece di raddoppiare
        #     la ricerca: costa 1/4 e decide la stessa cosa.
        if best_ladder:
            be_default = bool(settings.SCALE_OUT_SL_TO_BREAKEVEN)
            st_alt, _ = _run_oos(best_ladder, not be_default)
            alt_metric = st_alt.total_pnl_pct() - max_drawdown(st_alt.trades)
            best_be = (not be_default) if alt_metric > best_metric else be_default

    # 3) METRICHE FINALI CON LA SCALA CHE VERRA' ESEGUITA. Prima i numeri spediti nel
    #    registro (last_pf, win, regime_pf) uscivano dal passo 1, cioe' dalla scala
    #    GLOBALE, mentre il bot operava la scala scelta al passo 2: per 95 coppie su
    #    184 erano due configurazioni diverse. Il registro pubblicizzava un PF che
    #    nessuno eseguiva, e il rilevatore di deriva confrontava il vissuto contro
    #    quel numero sbagliato.
    if best_ladder and (list(best_ladder) != list(settings.SCALE_OUT_R_MULTIPLES)
                        or best_be != bool(settings.SCALE_OUT_SL_TO_BREAKEVEN)):
        oos, window_pnls = _run_oos(best_ladder, best_be)
    pf = oos.profit_factor()
    pnl = oos.total_pnl_pct()
    reg_pf = pf_by_regime(oos.trades)
    # il verdetto si rifa' sulla configurazione vera: una scala scelta per il
    # (ritorno - drawdown) puo' comunque non superare gli altri criteri.
    if passed:
        verdict = gate_verdict(window_pnls, len(oos.trades), pf, oos.win_rate(), pnl,
                               max_dd=max_drawdown(oos.trades), regime_pf=reg_pf,
                               pf_ex_top=pf_without_top(oos.trades))
        passed = verdict.ok
    failed, binding = list(verdict.failed), verdict.binding
    shortfall, near = verdict.shortfall, verdict.near_miss()

    hold: dict = {}
    if passed and opt.holdout_bars > 0:
        g = GeneratedStrategy(spec)
        if best_ladder:
            g.params = {**(getattr(g, "params", {}) or {}), "scale_r_mults": best_ladder,
                        "sl_to_breakeven": best_be}
        # STESSO contesto dell'OOS: un holdout senza mercato boccerebbe le spec
        # di mercato per dati mancanti, cioe' proprio quelle da misurare.
        hold = opt._holdout_check(g, symbol, candles, frame, cut,
                                  context_by_ts=context_by_ts)
        passed = bool(hold.get("ok"))
        if not passed:
            # supera tutto e cade sui dati mai visti: l'esito piu' informativo
            failed, binding, shortfall, near = ["holdout"], "holdout", 0.0, True
    return {
        "pf": round(pf, 3), "pnl": round(pnl, 4),
        "trades": len(oos.trades), "win": round(oos.win_rate(), 3), "passed": passed,
        "holdout": hold, "regime_pf": reg_pf,
        "max_dd": round(max_drawdown(oos.trades), 4),
        "scale_r_mults": best_ladder,
        "sl_to_breakeven": best_be,
        "data_end": (candles[-1].open_time.timestamp() if candles else 0.0),
        "fail_criteria": failed, "fail_binding": binding,
        "fail_shortfall": shortfall, "near_miss": bool(near and not passed),
        # MISURATO, non usato per decidere: vedi t_stat in backtesting/engine.py
        "t_stat": round(t_stat(oos.trades), 3),
    }


def merge_into_registry(fb, out: dict, passed_now: list[str],
                        evaluated_symbols: set | None = None) -> list[str]:
    """Aggiunge SOLO le coppie generate che PASSANO (accumula pass_count) e pota
    quelle generate inutili/stantie, evitando crescita illimitata del documento.
    Ricalcola la lista validated PRESERVANDO i campi di copertura del GATE 1
    (universe/coverage/ready) che spettano a optimize.py.

    `evaluated_symbols`: le coin che QUESTA passata ha davvero guardato. Serve a dare
    a `last_seen_at` un significato solo. Qui dentro si scrivono solo le coppie che
    passano, quindi finora il campo per le generate voleva dire "ultima volta che ha
    PASSATO", mentre per le coppie base (scritte da optimize.py su tutto cio' che
    valuta) vuol dire "ultima volta che e' stata GUARDATA". Un campo, due significati:
    e chi ci costruisce sopra un filtro — per esempio per escludere le coppie di coin
    uscite dall'universo — finisce per scambiare "non passa piu'" con "non esiste
    piu'". Sono due diagnosi opposte: la prima e' una strategia che ha smesso di
    funzionare, la seconda e' un pezzo di mercato che non guardiamo piu'.
    """
    doc = fb.get_doc("strategy_registry", "validated") or {}
    pairs = decode_pairs(doc.get("pairs"))
    now = time.time()
    # le coppie GENERATE sulle coin appena guardate sono state valutate, anche se non
    # hanno passato: il campo lo deve dire.
    if evaluated_symbols:
        for r in pairs.values():
            if r.get("generated") and r.get("symbol") in evaluated_symbols:
                r["last_seen_at"] = now
    drifted = drifted_from_paper(fb)   # evidenza dal paper: vale come fallimento
    # 1) upsert SOLO delle coppie passate (non sporco il registro con i fallimenti)
    for key in passed_now:
        e = out[key]
        rec = pairs.get(key, {"pass_count": 0})
        # UNA SOLA CONTABILITA' PER TUTTO IL REGISTRO. Qui c'era una copia a mano
        # della vecchia regola del "pass onesto" (differenza fra due data_end), che
        # optimize.py ha smesso di usare quando e' passato al verdetto per finestra.
        # Due regole diverse sullo stesso documento: le coppie generate — che sono la
        # maggioranza del registro — accumulavano conferme con un criterio, le base
        # con un altro, e nessuno dei due sapeva dell'altro. E' lo stesso schema che
        # ha gia' prodotto due difetti (due orologi, un campo letto al posto di un
        # altro): finche' esistono due copie della stessa regola, prima o poi
        # divergono. Ora c'e' `judge_window` e basta, per tutti.
        data_end = float(e.get("data_end", 0) or 0)
        if key in drifted:
            # smentita dal vivo: la finestra non puo' chiudersi con una conferma.
            # Un fallimento per FINESTRA, non per run (vedi la nota gemella in
            # scripts/optimize.py: contando a ogni run si purgava in sei ore).
            rec["passed_in_window"] = False
            rec["drift_seen_at"] = now
            judge_window(rec, data_end, False)
            rec["symbol"], rec["strategy"] = e["symbol"], e["strategy"]
            rec["generated"] = True
            rec["last_seen_at"] = now
            pairs[key] = rec
            continue
        # FAIL-CLOSED sul data_end: `judge_window` non giudica senza. Era il buco da
        # cui i run sharded (entries senza data_end) gonfiavano il conteggio.
        judge_window(rec, data_end, True)
        # VARIANTE CON LE CONFERME RETROATTIVE (vedi conferme_retroattive): le
        # altre MIN_PASSES-1 conferme sono gia' state raccolte in questo giro, su
        # dati che finiscono in momenti diversi. Si scrive il conteggio pieno, la
        # data di nascita e si chiude la finestra: da qui in poi e' una validata
        # come le altre, con le stesse regole di deriva e di purga.
        retro = int(e.get("conferme_retro") or 0)
        if retro >= MIN_PASSES - 1 and int(rec.get("pass_count", 0) or 0) < MIN_PASSES:
            rec["pass_count"] = MIN_PASSES
            rec["last_pass_data_end"] = data_end
            rec["window_start"] = data_end
            rec["passed_in_window"] = False
            rec["fail_count"] = 0
            rec["validated_at"] = now
            rec["conferme_retro"] = retro
        if e.get("holdout"):
            rec["holdout"] = e["holdout"]
        if e.get("regime_pf"):
            rec["regime_pf"] = e["regime_pf"]
        # NB: last_params si assegna PRIMA, poi si innesta la scala. Invertendo,
        # l'assegnazione cancellerebbe la scala appena salvata.
        rec["last_params"] = dict(e["params"] or {})
        # scala validata per questa coppia generata: viaggia in last_params, cosi'
        # params_for -> open_position la consegna al live come per le classiche
        if e.get("scale_r_mults"):
            rec["last_params"]["scale_r_mults"] = e["scale_r_mults"]
        if e.get("sl_to_breakeven") is not None:
            rec["last_params"]["sl_to_breakeven"] = bool(e["sl_to_breakeven"])
        rec["last_pf"] = e["oos_pf"]
        rec["last_pnl_pct"] = e["oos_pnl_pct"]
        rec["last_trades"] = e["oos_trades"]
        rec["last_win_rate"] = e.get("oos_win_rate")
        rec["symbol"] = e["symbol"]
        rec["strategy"] = e["strategy"]
        rec["generated"] = True
        rec["last_seen_at"] = now
        rec["last_passed_at"] = now
        pairs[key] = rec
    # 2) potatura: scarta le coppie GENERATE che non hanno niente da perdere.
    #
    # QUI SI CANCELLAVANO LE COPPIE A META' STRADA. La condizione era
    # `pass_count < MIN_PASSES and last_seen_at < 6 giorni fa`: cioe' una coppia a
    # 2 conferme su 3 veniva CANCELLATA sei giorni dopo che la sua coin era uscita
    # dall'universo — non per un verdetto, ma perche' nessuno la guardava piu'.
    # Le otto coppie ORCAUSDT a 2/3 sarebbero sparite il 19 settembre.
    #
    # E lo faceva dieci righe sopra al commento del tetto, che promette «le coppie
    # con almeno una conferma non si toccano MAI». Due regole sullo stesso
    # documento, in disaccordo, nello stesso file: e' la terza volta.
    #
    # Ora il criterio e' uno solo, `conferme_da_proteggere`, condiviso con la potatura delle
    # base e con la riaggiunta delle coin all'universo: chi ha una conferma presa da
    # meno di MIN_PASSES finestre non si cancella. Chi non ne prende una da tre
    # settimane esce, altrimenti il registro cresce senza limite — che e' il difetto
    # del 31 agosto visto dall'altro lato.
    #
    # Le VALIDATE non si potano mai da qui: sono quelle che il bot opera, e toglierle
    # in silenzio cambierebbe cosa fa il sistema senza che nessuno l'abbia deciso.
    def _da_tenere(r: dict) -> bool:
        if not r.get("generated"):
            return True                                   # le base le pota optimize
        if int(r.get("pass_count", 0) or 0) >= MIN_PASSES:
            return True                                   # validate: mai da qui
        return conferme_da_proteggere(r, now)

    pairs = {k: r for k, r in pairs.items() if _da_tenere(r)}
    # cap: limita il numero di coppie per non superare 1 MiB di documento.
    #
    # QUI IL 31 AGOSTO IL REGISTRO SI E' FERMATO DEL TUTTO, in silenzio. Le coppie
    # base non venivano mai potate e crescevano a ogni rotazione dell'universo (ogni
    # coin mai scansionata lascia 8 coppie per sempre). Quando hanno superato il
    # tetto da sole — 3041 su 3000 — `gen_budget` e' diventato ZERO, e la riga qui
    # sotto cancellava TUTTE le generate a ogni passata. La discovery trovava ottanta
    # candidate a giro, le scriveva, e la stessa funzione le buttava via subito dopo.
    # Nessun errore, nessun log: solo un registro che non poteva piu' accumulare
    # niente. Le 137 coppie a un passaggio del 27 agosto erano diventate 2.
    #
    # Due difese, perche' una sola non basta:
    #   1. le coppie con almeno una CONFERMA non si toccano mai. Ognuna costa una
    #      settimana di attesa: buttarle per far spazio significa buttare l'unica
    #      cosa che il sistema sta producendo. Se per tenerle si sfora il tetto, si
    #      sfora — a quel punto e' `slim_registry` a togliere i campi descrittivi, che
    #      e' un prezzo che si puo' pagare. Cancellare passaggi veri no.
    #
    # UNA SOLA REGOLA, non due. La prima versione di questa correzione riservava
    # anche una quota alle generate SENZA conferme, ed era codice morto: la potatura
    # qui sopra le toglie tutte (`pass_count == 0`), quindi quell'insieme e' sempre
    # vuoto. Un test lo ha mostrato subito. Meglio una difesa sola che si capisce
    # che due di cui una non fa niente.
    max_pairs = int(os.getenv("OPTIMIZER_MAX_PAIRS", "3000"))
    if len(pairs) > max_pairs:
        base = {k: r for k, r in pairs.items() if not r.get("generated")}
        gen = {k: r for k, r in pairs.items() if r.get("generated")}
        # INTOCCABILI: hanno gia' pagato il prezzo del tempo. Ognuna e' una
        # settimana di attesa, e sono l'unica cosa che il sistema sta producendo.
        con_pass = {k: r for k, r in gen.items()
                    if int(r.get("pass_count", 0) or 0) > 0}
        resto = {k: r for k, r in gen.items() if k not in con_pass}
        budget = max(0, max_pairs - len(base) - len(con_pass))
        if len(resto) > budget:
            ranked = sorted(resto.items(),
                            key=lambda kv: kv[1].get("last_seen_at", 0), reverse=True)
            resto = dict(ranked[:budget])
        if len(base) + len(con_pass) > max_pairs:
            print(f"[registry] tetto {max_pairs} sforato per tenere "
                  f"{len(con_pass)} coppie con conferme: e' voluto. Le "
                  f"{len(base)} base vanno potate da optimize.py, non da qui.")
        pairs = {**base, **con_pass, **resto}
    validated = sorted(
        k for k, r in pairs.items()
        if r.get("pass_count", 0) >= MIN_PASSES
        and (now - r.get("last_seen_at", 0)) < FRESH_DAYS * 86400
    )
    # tiene COPERTURA/coins coerenti col nuovo set validato (incluse le generate),
    # cosi' Telegram e dashboard mostrano gli stessi numeri. Il denominatore
    # (universe_size) resta quello di optimize.
    validated_coins = sorted({pairs[k].get("symbol") or k.split("|", 1)[0] for k in validated})
    universe = max(doc.get("universe_size", 0) or 0, len(validated_coins)) or 1
    # ALLEGGERITO ANCHE QUI, e non e' un dettaglio: la discovery scrive il registro
    # DOPO optimize. Finche' questa riga usava `encode_pairs` grezzo, rigonfiava di
    # colpo tutto cio' che optimize aveva appena alleggerito — cioe' la rete c'era
    # ma l'ultimo a scrivere la toglieva.
    doc["pairs"] = slim_registry(pairs, validated)
    doc["validated"] = validated
    doc["coins_covered"] = len(validated_coins)
    doc["coins"] = validated_coins
    doc["universe_size"] = universe
    doc["coverage"] = round(len(validated_coins) / universe, 3)
    doc["updated_at"] = now
    scrivi_registro(fb, doc, pairs)
    publish_timeline(fb, pairs, "discover", len(out), len(passed_now))
    return validated


def persist_specs(fb, specs_by_id: dict) -> None:
    doc = fb.get_doc("discovered_strategies", "specs") or {}
    specs = decode_pairs(doc.get("specs"))     # dict annidato -> stringa JSON (limite 40k indici)
    specs.update(specs_by_id)
    fb.set_doc("discovered_strategies", "specs",
               {"specs": encode_pairs(specs), "updated_at": time.time()})


def _notify(passed: list[dict], n_eval: int, n_specs: int, n_coins: int) -> None:
    token, chat = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    lines = [f"🧠 <b>Scoperta strategie</b>: {n_specs} candidate × {n_coins} crypto "
             f"= {n_eval} valutazioni"]
    if passed:
        lines.append(f"✅ {len(passed)} coppie nuove passate (OOS, netto costi):")
        for p in sorted(passed, key=lambda x: x["pnl"], reverse=True)[:10]:
            lines.append(f"• {p['symbol']} <code>{p['id']}</code> "
                         f"pf={p['pf']} pnl={p['pnl']*100:+.0f}% — {p['desc']}")
    else:
        lines.append("Nessuna candidata ha passato in questo run (normale: il gate è severo).")
    text = "\n".join(lines)
    if not (token and chat):
        print("[discover] (telegram non configurato)\n" + text)
        return
    try:
        import requests
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                      json={"chat_id": chat, "text": text, "parse_mode": "HTML"}, timeout=8)
    except Exception as exc:  # noqa: BLE001
        print(f"[discover] telegram fallito: {exc}")


def _merge_discover_shards(fb, args) -> int:
    """Riunisce gli shard di discovery e aggiorna il registro UNA volta sola."""
    run_id = os.getenv("GITHUB_RUN_ID", "")
    combined_out: dict = {}
    passed_keys: list[str] = []
    combined_specs: dict = {}
    n_eval = 0
    used = 0
    for i in range(args.num_shards):
        d = fb.get_doc("discover_shards", str(i)) or {}
        if not d:
            print(f"[merge] shard {i}: assente, salto")
            continue
        if run_id and d.get("run_id") and d.get("run_id") != run_id:
            print(f"[merge] shard {i}: run_id diverso (stantio), salto")
            continue
        combined_out.update(decode_pairs(d.get("passed_entries")))
        passed_keys.extend(decode_pairs(d.get("passed_keys")) or [])
        combined_specs.update(decode_pairs(d.get("specs")))
        n_eval += int(d.get("n_eval", 0) or 0)
        used += 1
    print(f"[merge] {used}/{args.num_shards} shard uniti: {len(passed_keys)} coppie passate")
    if combined_specs:
        persist_specs(fb, combined_specs)
    validated = merge_into_registry(fb, combined_out, passed_keys)
    summary = [{"symbol": e["symbol"], "id": e["strategy"], "pf": e["oos_pf"],
                "pnl": e["oos_pnl_pct"], "desc": GeneratedStrategy(e["spec"]).description}
               for e in combined_out.values()]
    fb.set_doc("strategy_params", "discovered_last_run", {
        "updated_at": time.time(), "n_eval": n_eval, "n_passed": len(passed_keys),
        "passed": [{"symbol": s["symbol"], "id": s["id"], "pf": s["pf"], "pnl": s["pnl"]}
                   for s in summary],
    })
    print(f"[merge] coppie validate totali nel registro (base+generate): {len(validated)}")
    _notify(summary, n_eval, len(combined_specs), args.num_shards)
    return 0


def main() -> int:
    # IL TEMPO DEL GIRO SI MISURA QUI, e si salva su Firebase. Il 22 set 2026 per
    # sapere quanto durava un giro servivano `servizi` + `processi` + il journal,
    # e il journal tiene 80 righe di cache che spingono via la fine del giro. Da
    # ora `gate_progress` (allowlist `gate`) lo stampa: inizio, fine, durata.
    t0 = time.time()
    ap = argparse.ArgumentParser(description="Scoperta autonoma di nuove strategie.")
    ap.add_argument("--top", type=int, default=25, help="numero di crypto su cui validare")
    ap.add_argument("--symbols", default="",
                    help="lista esplicita di coin (CSV). Ha precedenza su --top: "
                         "serve alle conferme mirate su coppie gia' candidate")
    ap.add_argument("--generate", type=int, default=40, help="strategie candidate da generare")
    ap.add_argument("--windows", type=int, default=3)
    ap.add_argument("--seed", type=int, default=int(time.time()) % 100000,
                    help="seed generazione (varia per esplorare strategie diverse a ogni run)")
    ap.add_argument("--interval", default=settings.ORCHESTRATOR_TIMEFRAME)
    ap.add_argument("--start", default="2022-01-01")
    ap.add_argument("--end", default=None,
                    help="fine finestra dati (default: oggi). Far avanzare la finestra "
                         "rende la ri-validazione VERA su dati nuovi a ogni run.")
    ap.add_argument("--source", default="auto")
    ap.add_argument("--reeval-cap", type=int, default=80,
                    help="max strategie già scoperte da ri-validare per run (bound sui tempi)")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--num-shards", type=int, default=1)
    ap.add_argument("--merge", action="store_true",
                    help="modalita' MERGE: riunisce gli shard di discovery nel registro")
    args = ap.parse_args()
    end = args.end or date.today().isoformat()

    fb = get_firebase()
    if args.merge:
        return _merge_discover_shards(fb, args)

    # 1) candidate NUOVE  2) RI-VALUTA le scoperte precedenti (così accumulano i
    # pass e diventano operabili)  3) mutazioni per evolvere attorno alle vincenti.
    # 1a) IPOTESI AI: poche spec con un meccanismo dichiarato, al posto di altrettante
    #     estrazioni casuali. Non e' un'aggiunta all'imbuto: SOSTITUISCE una quota di
    #     candidate casuali, perche' ogni candidata in piu' e' un'estrazione in piu'
    #     della lotteria del confronto multiplo. Senza AI la quota resta casuale e il
    #     comportamento e' identico a prima.
    prove = prove_dal_paper(fb)
    if prove:
        print(f"[discover] prove del paper passate all'AI:\n{prove}")
    # B3: i quasi-passaggi del giro precedente al modello, che risponde con uno
    # schema e con consigli; i consigli entrano nel contesto delle proposte di
    # QUESTO giro. Fail-open: senza AI o senza autopsia si propone come prima.
    from bot.ai.autopsia import analizza as ai_autopsia, contesto_per_le_proposte
    try:
        autopsia = ai_autopsia(fb)
    except Exception as exc:  # noqa: BLE001
        autopsia = None
        print(f"[ai-autopsia] saltata ({str(exc)[:80]})")
    if autopsia:
        print(f"[ai-autopsia] schema: {autopsia.get('schema', '')[:300]}")
        print(f"[ai-autopsia] consigli: {autopsia.get('consigli', '')[:300]}")
    ai_specs = ai_propose(min(settings.AI_HYPOTHESES_PER_RUN, args.generate),
                          market_context=f"Timeframe operativo: {args.interval}. "
                                         f"Universo: crypto futures USDT-M su Binance."
                                         + (f"\n\n{prove}" if prove else "")
                                         + (f"\n\n{contesto_per_le_proposte(autopsia)}"
                                            if autopsia else ""))
    if ai_specs:
        print(f"[discover] {len(ai_specs)} ipotesi AI (motivate) + "
              f"{args.generate - len(ai_specs)} casuali")
    # L'ESITO SU FIREBASE, non solo nel log: il journal tiene le ultime righe e la
    # discovery gira ogni tre ore, quindi il motivo degli scarti e' illeggibile gia'
    # poche ore dopo. Best-effort: una diagnosi non salvata non deve far fallire un
    # giro di validazione.
    from bot.ai.hypotheses import ULTIMO_ESITO
    if ULTIMO_ESITO:
        try:
            fb.set_doc("ai_hypotheses", "last", dict(ULTIMO_ESITO))
        except Exception as exc:  # noqa: BLE001
            print(f"[ai-hypotheses] esito non salvato ({str(exc)[:80]})")
    # 1b) VARIANTI DAI REFERTI (B8): le spec note servono PRIMA, perche' una
    #     variante nasce da una spec che il bot ha gia' operato. Come le ipotesi
    #     AI, sostituiscono una quota di casuali: il giro non si allunga.
    existing = decode_pairs((fb.get_doc("discovered_strategies", "specs") or {}).get("specs"))
    varianti = varianti_dai_referti(fb, existing, args.interval)
    specs = (ai_specs + varianti
             + generate_specs(max(0, args.generate - len(ai_specs) - len(varianti)),
                              seed=args.seed))
    reg = fb.get_doc("strategy_registry", "validated") or {}
    _ora = time.time()
    _completa = (not REEVAL_DAILY) or giro_giornaliero(_ora) or bool(args.symbols)
    existing_list, diag_reeval = specs_da_rivalutare(existing, reg, args.reeval_cap,
                                                     completa=_completa, now=_ora)
    print(f"[discover] rivalutazione {diag_reeval['reeval_modalita']}: "
          f"{diag_reeval['n_specs_rivalutate']} spec note su {diag_reeval['n_specs_note']}")
    specs.extend(existing_list)
    # MUTAZIONE INFORMATA: si evolve attorno ai QUASI-PASSAGGI del run precedente
    # (una sola condizione mancata, e per poco), non attorno alle prime dieci spec
    # che capitano. E' la differenza fra cercare dove l'ultimo tentativo si e'
    # avvicinato e ricominciare da capo ogni volta. Fail-open: senza autopsia si
    # mutano le prime, come prima.
    # il registro serve a sapere quali coin sono GIA' coperte: i semi vanno
    # preferibilmente sulle altre, altrimenti l'evoluzione rinforza dove qualcosa
    # gia' funziona e il numero di monete operabili non si muove.
    seeds = mutation_seeds(fb, existing, pairs=decode_pairs(reg.get("pairs")))
    if seeds:
        print(f"[discover] {len(seeds)} semi dai quasi-passaggi del run precedente")
    bases = seeds or existing_list[:SEEDS]
    for i, base in enumerate(bases[:SEEDS]):
        specs.append(mutate(base, seed=args.seed + i + 1))
    # IL TIMEFRAME DELLA PASSATA sulle candidate nuove: una spec nata in una
    # passata a 1 ora e' una strategia a 1 ora, con il suo id (che include il
    # timeframe). Le spec gia' note NON si ristampano: si rivalutano solo quelle
    # dello stesso intervallo, altrimenti una spec a 15m giudicata a 1h finirebbe
    # nel registro con lo stesso nome e un'altra natura.
    tf_bot = settings.ORCHESTRATOR_TIMEFRAME
    nuove = []
    for sp in specs:
        if sp.get("id") in existing:
            if (existing[sp["id"]].get("timeframe") or tf_bot) == args.interval:
                nuove.append(sp)
            continue
        if args.interval != tf_bot:
            sp = {**sp, "timeframe": args.interval}
            sp["id"] = spec_id(sp)
        nuove.append(sp)
    specs = nuove
    # de-dup per id
    specs = list({s["id"]: s for s in specs}.values())
    # e per LOGICA: due spec con la stessa firma sono la stessa scommessa
    specs, n_gemelle = scarta_gemelle(specs, existing)
    if n_gemelle:
        print(f"[discover] {n_gemelle} candidate scartate perche' gemelle di una "
              f"spec gia' nota (stessa logica, id diverso)")
    for sym, ids in gemelle_validate(decode_pairs(reg.get("pairs")), existing)[:8]:
        print(f"[discover] GEMELLE gia' validate su {sym}: {len(ids)} coppie con la "
              f"stessa logica ({', '.join(ids[:4])}{'…' if len(ids) > 4 else ''})")
    print(f"[discover] {len(specs)} candidate "
          f"({diag_reeval['n_specs_con_conferme']} con conferme ri-validate + "
          f"{len(existing_list) - diag_reeval['n_specs_con_conferme']} altre, "
          f"{diag_reeval['n_specs_tagliate']} tagliate su "
          f"{diag_reeval['n_specs_note']} note) seed={args.seed} {args.start}->{end}")

    # UNIVERSO RISTRETTO (--symbols): serve alle conferme mirate. Quando si sa gia'
    # quali coppie possono ancora arrivare a MIN_PASSES, ri-testare l'intero mercato
    # e' tempo speso su coppie che non potrebbero comunque validarsi.
    if getattr(args, "symbols", ""):
        full_symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
        print(f"[discover] universo RISTRETTO a {len(full_symbols)} coin (--symbols)")
    else:
        full_symbols = top_symbols_by_volume(args.top)
    # FILTRO DI CONTESTO: toglie dall'imbuto le coin su cui una validazione non
    # sarebbe informativa (storia dentro la sola fase di listing, illiquide,
    # prezzo guidato da eventi discreti). Fail-open: senza AI non toglie nulla.
    full_symbols, _excluded = ai_filter_universe(
        [{"symbol": s} for s in full_symbols])
    for _sym, _why in list(_excluded.items())[:10]:
        print(f"[discover]   escluso {_sym}: {_why}")
    # L'UNIVERSO RUOTA, LA VALIDAZIONE NO. Il top-N per volume cambia ogni giorno —
    # fra l'8 e il 14 settembre ne e' uscito il 26% — ma una coppia ha bisogno di due
    # settimane con la SUA coin dentro. Quando la coin esce, la coppia non fallisce:
    # si ferma a meta' strada, perche' nella discovery una coppia prende la conferma
    # successiva solo ripassando, e chi non viene valutato non passa.
    #
    # E' successo a ORCAUSDT il 13 settembre, con OTTO coppie a 2 conferme su 3, il
    # giorno stesso in cui la loro finestra scadeva: un tentativo, uno solo, e poi il
    # sistema ha smesso di guardarle.
    #
    # La riaggiunta sta DOPO il filtro di proposito: una coin che ha gia' prodotto
    # conferme ha gia' dimostrato di essere informativa, e lasciarla escludere
    # rimetterebbe in piedi lo stesso buco da un'altra porta.
    if not getattr(args, "symbols", ""):
        maturazione, diag_mat = coin_in_maturazione(
            decode_pairs(reg.get("pairs")), time.time())
        riaggiunte = [s for s in maturazione if s not in set(full_symbols)]
        if riaggiunte:
            print(f"[discover] {len(riaggiunte)} coin riaggiunte: hanno una coppia in "
                  f"maturazione ma sono uscite dal top-{args.top} per volume "
                  f"({', '.join(riaggiunte[:12])}"
                  f"{' ...' if len(riaggiunte) > 12 else ''})")
            full_symbols = list(full_symbols) + riaggiunte
        # QUANTE NE RESTANO FUORI. La versione precedente lo prometteva in docstring
        # e non lo stampava: un tetto che morde in silenzio e' il difetto che la
        # riaggiunta esiste per chiudere, rientrato dalla porta del commento.
        print(f"[discover] maturazione: {diag_mat['intoccabili']} coin a un passo "
              f"dalla validazione (mai tagliate) + {diag_mat['coda_tenuta']} con una "
              f"conferma · {diag_mat['tagliate']} tagliate dalla coda")
    # SHARDING: ogni shard valida le candidate su una fetta dell'universo; il merge
    # riunisce. Così copriamo l'INTERO universo restando nel timeout.
    symbols = full_symbols[args.shard::args.num_shards] if args.num_shards > 1 else full_symbols
    print(f"[discover] shard {args.shard}/{args.num_shards}: {len(symbols)}/{len(full_symbols)} coin")
    out: dict[str, dict] = {}
    passed_summary: list[dict] = []
    passed_keys: list[str] = []
    specs_to_save: dict = {}
    n_eval = 0

    # PARALLELO: ogni simbolo valuta tutte le spec, indipendente dagli altri ->
    # distribuito su tutti i core del runner. Fallback sequenziale se BACKTEST_WORKERS=1.
    workers = n_workers()
    print(f"[discover] {len(symbols)} coin x {len(specs)} spec su {workers} worker (core)")
    diag_binding: dict = {}
    diag_involved: dict = {}
    diag_near: list = []
    for sym, entries, p_keys, p_specs, n_ev, summary, diag in parallel_map(
        _disc_one, symbols, workers=workers, initializer=_disc_init,
        initargs=(args, end, specs, scala_dal_paper(fb))
    ):
        n_eval += n_ev
        out.update(entries)
        passed_keys.extend(p_keys)
        specs_to_save.update(p_specs)
        passed_summary.extend(summary)
        for k, v in (diag.get("binding") or {}).items():
            diag_binding[k] = diag_binding.get(k, 0) + v
        for k, v in (diag.get("involved") or {}).items():
            diag_involved[k] = diag_involved.get(k, 0) + v
        diag_near.extend(diag.get("near") or [])
        if p_keys:
            print(f"[discover] {sym}: {len(p_keys)} coppie passate ✅")

    # Con gli shard ognuno vede una fetta dell'universo e sovrascriverebbe la
    # diagnosi degli altri: meglio nessuna autopsia che una parziale spacciata per
    # intera. Sulla VPS (non shardata) si pubblica sempre.
    if args.num_shards <= 1:
        _publish_discover_autopsy(fb, n_eval, len(passed_keys),
                                  diag_binding, diag_involved, diag_near)

    # SHARD: scrive il proprio risultato; il merge riunisce e aggiorna il registro.
    if args.num_shards > 1:
        fb.set_doc("discover_shards", str(args.shard), {
            "run_id": os.getenv("GITHUB_RUN_ID", ""),
            "passed_entries": encode_pairs({k: out[k] for k in passed_keys}),
            "passed_keys": encode_pairs(passed_keys),
            "specs": encode_pairs(specs_to_save),
            "n_eval": n_eval, "updated_at": time.time(),
        })
        print(f"[discover] shard {args.shard} scritto: {len(passed_keys)} coppie passate. "
              f"Il merge aggiornera' il registro.")
        return 0

    # persisti: spec scoperte + merge nel registro validato
    if specs_to_save:
        persist_specs(fb, specs_to_save)
    validated = merge_into_registry(fb, out, passed_keys,
                                    evaluated_symbols=set(symbols))
    # riepilogo COMPATTO (niente spec/entry per ogni coppia: sforerebbe il limite
    # di 1 MiB di Firestore). Le spec complete stanno in discovered_strategies/specs.
    durata = time.time() - t0
    print(f"[discover] GIRO FINITO in {durata / 3600:.0f}h {(durata % 3600) / 60:.0f}m "
          f"({n_eval} valutazioni, {len(passed_keys)} passate)")
    _doc_run = ("discovered_last_run" if args.interval == settings.ORCHESTRATOR_TIMEFRAME
                else f"discovered_last_run_{args.interval}")
    fb.set_doc("strategy_params", _doc_run, {
        "interval": args.interval,
        "symbols": len(symbols),
        "updated_at": time.time(),
        "started_at": t0,
        "duration_s": round(durata),
        "n_eval": n_eval,
        "n_passed": len(passed_keys),
        # QUANTO MORDE IL TAGLIO. Senza questi numeri, "il registro non accumula" e
        # "meta' del registro non viene piu' guardata" sono indistinguibili da fuori.
        **diag_reeval,
        "passed": [{"symbol": out[k]["symbol"], "id": out[k]["strategy"],
                    "pf": out[k]["oos_pf"], "pnl": out[k]["oos_pnl_pct"]}
                   for k in passed_keys],
    })

    print("\n" + "=" * 60)
    print(f"[discover] {n_eval} valutazioni, {len(passed_keys)} coppie nuove passate in QUESTO run.")
    print(f"[discover] coppie validate totali nel registro (base+generate): {len(validated)}")
    print("=" * 60)
    _notify(passed_summary, n_eval, len(specs), len(symbols))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
