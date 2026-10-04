"""G7: IL GATE SUL PREZZO CASUALE (4 ott 2026, si' del proprietario, «sì G7, procedi»).

La domanda: quante strategie passa il gate quando non c'e' niente da trovare?
A 1 ora il giro vero passa il 2,2% delle prove (218 su 9.840, ops 0468), a 15
minuti lo 0,12% (25 su 20.667, ops 0470). Prima che le prime validate a 1 ora
entrino nel paper (dall'8 ott) bisogna sapere quanta parte di quei passaggi il
gate darebbe anche a prezzi senza alcun vantaggio possibile.

ATTENZIONE, scritta prima dei numeri: le due quote del giro vero NON si
confrontano fra loro. La passata a 1 ora rivaluta soprattutto spec gia' note a
1 ora (259 su 328, riga ORIGINI di ops 0468), cioe' coppie che erano gia'
passate; il giro «solo urgenti» a 15 minuti e' quasi tutto candidate nuove.
Per questo il confronto di G7 e' fatto a parita' di tutto: LE STESSE candidate
NUOVE (il generatore del gate, seme fisso), sulle STESSE monete, giudicate dal
gate di produzione due volte:
  * «vero»: sulle candele vere;
  * «caso»: sulle stesse candele con l'ordine RIMESCOLATO candela per candela
    (`rimescola`): ogni candela tiene la sua forma rispetto alla chiusura prima
    e il suo volume, cambia solo l'ordine. Stessa distribuzione dei movimenti,
    stesso prezzo di partenza e di arrivo, nessuna dipendenza nel tempo: nessuna
    strategia puo' avere un vantaggio vero. Il rimescolamento a blocchi di un
    giorno della proposta e' stato scartato prima dei numeri: dentro il giorno
    terrebbe gli schemi veri, e un vantaggio infragiornaliero sopravviverebbe.
    Il contesto di mercato (BTC) resta quello vero: sulla moneta rimescolata non
    ha piu' nessun legame, quindi nessun vantaggio.

REGOLA (backlog G7, scritta prima dei numeri; qui si applica, non si cambia):
  quota sul caso >= meta' di quella vera  -> a quel timeframe il gate passa
      soprattutto rumore (la prossima modifica va nelle soglie del gate, con R1);
  quota sul caso <= un quinto di quella vera -> il gate filtra il rumore (il
      problema del paper e' altrove);
  altrimenti -> non si sa.
  Con meno di MIN_PASSATE_VERE passate sulle candele vere -> non si sa (troppo
  poche per un rapporto), e si dice.

DOVE E QUANDO: dentro il lancio di R1 (`scripts/replay_gate.py`, comando ops
`replay-gate`), dopo R2 e prima delle unita' di R1, con gli stessi worker, lo
stesso budget e le stesse regole sul giro del gate (mai insieme). Prima solo 1
ora (`INTERVALLO`); 15 minuti si aggiunge se serve. SOLO file locali in
data/replay_gate/g7/<intervallo>/ (ignorata da git): niente Firebase, niente
registro. L'esito si legge con `replay-gate-esito`.

COSTO (STIMA): 72 monete x 2 varianti x 100 candidate = 14.400 giudizi; la
passata vera a 1 ora fa 9.840 giudizi in 9 minuti con 6 worker (ops 0468), cioe'
~0,33 s a giudizio per worker: ~20 minuti con 4 worker, piu' lo scarico delle
candele a 1 ora delle monete che il gate a 1 ora non usa.
"""
from __future__ import annotations

import os
import random
import time
import zlib
from collections import Counter

from bot.config import settings
from bot.core.models import Candle
from bot.strategies.generated import spec_id
from bot.strategies.generator import generate_specs

#: G7 gira nei lanci di R1 finche' non e' completo (poi non costa niente)
G7_ATTIVO = True
INTERVALLO = "1h"
N_CANDIDATE = 100
#: il seme delle candidate e, combinato con la moneta, del rimescolamento
SEME = 20261004
VARIANTI = ("vero", "caso")
#: sotto tante passate sulle candele vere il rapporto non si legge
MIN_PASSATE_VERE = 10
SOGLIA_RUMORE = 0.5          # caso >= meta' del vero
SOGLIA_FILTRA = 0.2          # caso <= un quinto del vero
REGOLA_G7 = (
    "le stesse candidate nuove sulle stesse monete, giudicate dal gate di oggi sulle candele "
    "vere e sulle stesse candele rimescolate: quota sul caso >= meta' di quella vera -> il "
    "gate passa soprattutto rumore (la prossima modifica va nelle soglie del gate); <= un "
    "quinto -> il gate filtra il rumore (il problema del paper e' altrove); altrimenti non "
    f"si sa; con meno di {MIN_PASSATE_VERE} passate sul vero non si sa")


def _rv():
    """Il modulo di R1 (import tardivo: replay_gate importa questo modulo dentro
    il lancio, non in cima)."""
    from scripts import replay_gate
    return replay_gate


def dir_g7(intervallo: str = INTERVALLO) -> str:
    """Calcolata a ogni chiamata dalla cartella di R1 (i test la spostano)."""
    return os.path.join(_rv().DIR_R1, "g7", intervallo)


# --------------------------------------------------------------------------- #
# Le candidate e il prezzo rimescolato (pure)                                  #
# --------------------------------------------------------------------------- #
def candidate_g7(n: int = N_CANDIDATE, intervallo: str = INTERVALLO, seme: int = SEME) -> list[dict]:
    """Le candidate NUOVE: il generatore del gate col seme fisso, gemelle tolte
    come nel giro vero, e il timeframe della passata nel nome (come fa la
    discovery per le candidate nate in una passata a 1 ora)."""
    from scripts import discover_strategies as d
    specs, _ = d.scarta_gemelle(generate_specs(int(n), seed=int(seme)), {})
    if intervallo == settings.ORCHESTRATOR_TIMEFRAME:
        return specs
    out = []
    for sp in specs:
        sp = {**sp, "timeframe": intervallo}
        sp["id"] = spec_id(sp)
        out.append(sp)
    return list({s["id"]: s for s in out}.values())


def seme_moneta(coin: str, seme: int = SEME) -> int:
    return (zlib.crc32(coin.encode("utf-8")) ^ int(seme)) & 0x7FFFFFFF


def rimescola(candles: list, seme: int) -> list:
    """Le stesse candele in ordine casuale, candela per candela. Ogni candela
    tiene apertura, massimo, minimo e chiusura RISPETTO ALLA CHIUSURA PRIMA, e il
    suo volume; gli orari restano al loro posto. La prima candela resta com'e',
    quindi prezzo di partenza e di arrivo sono gli stessi (il prodotto dei
    movimenti non cambia). Pura e ripetibile col seme."""
    if len(candles) < 3:
        return list(candles)
    pezzi = []
    for prev, c in zip(candles, candles[1:]):
        base = float(prev.close)
        if base <= 0:
            return list(candles)
        pezzi.append((c.open / base, c.high / base, c.low / base, c.close / base, c.volume))
    ordine = list(range(len(pezzi)))
    random.Random(int(seme)).shuffle(ordine)
    out = [candles[0]]
    chiusura = float(candles[0].close)
    for pos, j in enumerate(ordine, start=1):
        o, h, lo, c, v = pezzi[j]
        orig = candles[pos]
        out.append(Candle(open_time=orig.open_time, close_time=orig.close_time,
                          open=chiusura * o, high=chiusura * h, low=chiusura * lo,
                          close=chiusura * c, volume=v))
        chiusura = chiusura * c
    return out


# --------------------------------------------------------------------------- #
# L'unita' di lavoro (nei worker di R1)                                        #
# --------------------------------------------------------------------------- #
def _una_unita_g7(item) -> dict:
    """UNA moneta in UNA variante: le candidate giudicate dal gate di oggi con
    tutte le candele (come R2), vere o rimescolate. Conta solo chi passa."""
    rv = _rv()
    variante, sym = item
    base = {"data": variante, "coin": sym}
    if rv._scaduto():
        return {**base, "stato": "tempo"}
    ferma = rv.gate_in_arrivo(rv.MARGINE_FERMATA_S)
    if ferma:
        return {**base, "stato": "giro", "errore": ferma}
    t0 = time.time()
    try:
        candles = rv._carica(sym)
        if not candles:
            return {**base, "stato": "errore", "errore": "nessuna candela"}
        if variante == "caso":
            candles = rimescola(candles, seme_moneta(sym))
        specs = rv._S.get("g7_specs")
        if specs is None:
            specs = rv._S["g7_specs"] = candidate_g7(intervallo=rv._S["cfg"]["interval"])
        oggi = rv._ts(rv._S["end"]) + 86400.0          # tutte le candele caricate
        esiti = rv.giudica(rv._S["opt"], sym, candles, oggi, specs, rv.contesto_gate)
        if esiti is None:
            return {**base, "stato": "storia", "secondi": round(time.time() - t0, 1)}
        voci = [rv.voce_candidata(sp, r) for sp, r in zip(specs, esiti)]
        rec = {**base, "stato": "ok", "n_candidate": len(voci),
               "passate": [v["id"] for v in voci if v["passata"]],
               "per_criterio": dict(Counter(str(v.get("binding")) for v in voci
                                           if not v["passata"]))}
    except Exception as exc:  # noqa: BLE001
        return {**base, "stato": "errore", "errore": str(exc)[:120],
                "secondi": round(time.time() - t0, 1)}
    rec["secondi"] = round(time.time() - t0, 1)
    rv.di(f"[g7] {sym} ({variante}): {rec['n_candidate']} candidate, {len(rec['passate'])} "
          f"passate, {rec['secondi']:.0f}s")
    return rec


def salva_unita_g7(rec: dict) -> bool:
    """Come R2: solo esiti finali o errori (coi tentativi, per non riprovare
    all'infinito). Un file per variante e moneta."""
    rv = _rv()
    if rec.get("stato") not in rv.FINALI and rec.get("stato") != "errore":
        return False
    cartella = os.path.join(dir_g7(), "unita", str(rec["data"]))
    os.makedirs(cartella, exist_ok=True)
    path = os.path.join(cartella, f"{rec['coin']}.json")
    if rec.get("stato") == "errore":
        prima = rv._leggi_json(path) or {}
        rec = {**rec, "tentativi": int(prima.get("tentativi") or 0) + 1}
    rv.scrivi_atomico(path, rec)
    return True


def leggi_unita_g7(base: str | None = None) -> dict:
    """{(variante, moneta): record} dai file."""
    rv = _rv()
    base = base or os.path.join(dir_g7(), "unita")
    out: dict = {}
    for variante in VARIANTI:
        cartella = os.path.join(base, variante)
        try:
            nomi = os.listdir(cartella)
        except OSError:
            continue
        for n in nomi:
            if n.endswith(".json"):
                rec = rv._leggi_json(os.path.join(cartella, n))
                if isinstance(rec, dict):
                    out[(variante, rec.get("coin") or n[:-5])] = rec
    return out


def lavoro_g7(monete: list[str], fatte: dict) -> list:
    """Le unita' ancora da fare: prima tutto il vero, poi tutto il caso (se il
    budget finisce a meta', il vero e' gia' completo)."""
    rv = _rv()
    return [(v, c) for v in VARIANTI for c in monete if not rv.unita_chiusa(fatte.get((v, c)))]


# --------------------------------------------------------------------------- #
# La lettura                                                                   #
# --------------------------------------------------------------------------- #
def lettura_g7(monete: list[str], fatte: dict) -> dict:
    """Le due quote e l'esito con la regola. Le monete che hanno un esito ok in
    tutte e due le varianti sono le sole confrontate (a parita' di monete)."""
    rv = _rv()
    monete = list(monete or [])
    completa = bool(monete) and all(rv.unita_chiusa(fatte.get((v, c)))
                                    for v in VARIANTI for c in monete)
    pari = [c for c in monete if all((fatte.get((v, c)) or {}).get("stato") == "ok"
                                     for v in VARIANTI)]
    q = {}
    for v in VARIANTI:
        recs = [fatte[(v, c)] for c in pari]
        prove = sum(int(r.get("n_candidate") or 0) for r in recs)
        passate = sum(len(r.get("passate") or []) for r in recs)
        crit: Counter = Counter()
        for r in recs:
            crit.update(r.get("per_criterio") or {})
        q[v] = {"prove": prove, "passate": passate,
                "quota": (passate / prove) if prove else None,
                "per_criterio": dict(crit.most_common(5))}
    qv, qc = q["vero"]["quota"], q["caso"]["quota"]
    rapporto = (qc / qv) if (qv and qc is not None) else None
    if not completa:
        esito = "in corso"
    elif q["vero"]["passate"] < MIN_PASSATE_VERE:
        esito = (f"NON SI SA: sulle candele vere passano solo {q['vero']['passate']} candidate "
                 f"nuove (ne servono {MIN_PASSATE_VERE} per leggere il rapporto)")
    elif rapporto >= SOGLIA_RUMORE:
        esito = ("IL GATE PASSA SOPRATTUTTO RUMORE a questo timeframe: la prossima modifica va "
                 "nelle soglie del gate (con R1)")
    elif rapporto <= SOGLIA_FILTRA:
        esito = "IL GATE FILTRA IL RUMORE a questo timeframe: il problema del paper e' altrove"
    else:
        esito = "NON SI SA: il rapporto sta fra un quinto e la meta'"
    return {"intervallo": INTERVALLO, "monete": len(monete), "a_pari": len(pari),
            "vero": q["vero"], "caso": q["caso"], "rapporto": rapporto,
            "completa": completa, "esito": esito}


def _pct(x) -> str:
    return "n.d." if x is None else f"{100 * x:.2f}%"


def righe_lettura_g7(monete: list[str] | None, fatte: dict) -> list[str]:
    if not G7_ATTIVO or not monete:
        return []
    r = lettura_g7(monete, fatte)
    if not fatte:
        return [f"[g7] il gate sul prezzo casuale ({INTERVALLO}): non ancora fatto, parte nel "
                f"prossimo lancio dopo R2"]
    v, c = r["vero"], r["caso"]
    return [
        f"[g7] IL GATE SUL PREZZO CASUALE ({INTERVALLO}) · {N_CANDIDATE} candidate nuove (seme "
        f"{SEME}) · monete a confronto {r['a_pari']}/{r['monete']}",
        f"  REGOLA G7 (4 ott, scritta prima dei numeri): {REGOLA_G7}",
        f"  candele vere: {v['passate']} passate su {v['prove']} prove = {_pct(v['quota'])}"
        + (f" · bocciate per criterio: " + ", ".join(f"{k} {n}" for k, n in v["per_criterio"].items())
           if v["per_criterio"] else ""),
        f"  candele rimescolate: {c['passate']} passate su {c['prove']} prove = {_pct(c['quota'])}"
        + (f" · bocciate per criterio: " + ", ".join(f"{k} {n}" for k, n in c["per_criterio"].items())
           if c["per_criterio"] else ""),
        f"  rapporto caso/vero: " + ("n.d." if r["rapporto"] is None else f"{r['rapporto']:.2f}"),
        f"  ESITO G7: {r['esito']}" + ("" if r["completa"] else " (PARZIALE)"),
    ]
