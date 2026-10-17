"""QUANTO SPENDE L'AI, E PER COSA (29 set 2026).

PERCHE'. Il proprietario ha chiesto di vedere nel report del mattino «la spesa
giornaliera di AI e per quali ragioni». Fino a oggi l'unica cifra era la stima D6
del backlog (~2,75 $ al giorno), ricostruita a mano dai log: e i log scorrono via
in poche ore, le risposte senza JSON non lasciavano i token (pagate e invisibili),
e la spesa nasce in almeno quattro processi diversi (bot, optimize, discovery, il
runner GitHub della domenica). Un contatore in memoria, come quello delle letture
Firestore, avrebbe visto un processo solo.

COME. Dopo OGNI chiamata al modello, `registra` somma i token che l'API dice di
aver usato nel documento Firestore `ai_spesa/{giorno italiano}`, divisi per
RAGIONE (l'etichetta del chiamante, es. `ai-shadow`). La somma e' atomica fra
processi e costa una scrittura, zero letture (`FirebaseClient.incrementa`). Il
report del mattino (`scripts/ai_status.py`) legge quei documenti e li traduce in
dollari con `righe_spesa`.

Forma del documento:
    ragioni: {etichetta: {n, in, out, cache_w, cache_r, stop: {motivo: n},
                          modelli: {modello che ha risposto: n}}}
    modelli: {modello che ha risposto: n}   (il totale del giorno)
    ore:     {"HH" ora italiana: n}    (dice da che ora il conto e' partito)
    aggiornato_at: epoch dell'ultima registrazione

COSA NON E'. Non e' la fattura: i dollari sono token × prezzo configurato
(`AI_PREZZO_*` in bot/config.py). La fattura vera e' nella console Anthropic.
Restano fuori, e il report lo dice: il controllo della chiave del mattino (lo fa
uno script di sola lettura) e le sessioni @claude su GitHub (non passano da
questo codice).

FAIL-OPEN. `registra` non solleva mai: una misura persa costa una riga di log,
una chiamata AI buttata per colpa della misura costerebbe la chiamata.
"""
from __future__ import annotations

import re
import time
from datetime import date, datetime, timedelta
from typing import Any, Optional

from bot.config import settings
from bot.core.firebase_client import get_firebase
from bot.core.tempo import fuso, giorno_locale

#: un documento per giorno italiano (`YYYY-MM-DD`)
COLLEZIONE = "ai_spesa"

#: perche' si paga ogni etichetta, detto semplice. Un'etichetta che non e' qui
#: esce col suo nome: meglio un nome tecnico che una riga sparita.
RAGIONI: dict[str, str] = {
    "ai-hypotheses": "idee di strategie nuove da far provare al gate",
    "ai-shadow": "ombra: cosa farebbe l'AI al posto del bot, solo misura",
    "ai-autopsia": "lettura delle strategie quasi promosse per dare consigli "
                   "alla ricerca",
    "ai-universe": "filtro delle monete su cui cercare",
    "ai-analyst": "analisi del vissuto lanciata a mano",
    "ai-orchestratore": "scelta del trade fatta dal modello (spenta finche' "
                        "decide la parita')",
    "ai-learning": "riassunto settimanale della domenica",
    "ai-connettivita": "prova di collegamento della chiave",
    "ai-verifica": "verifica delle chiavi lanciata a mano",
}

#: la stima di riferimento finche' non ci sono giorni misurati (backlog D6)
STIMA_D6 = "~2,75 $ al giorno, stimata dai log il 29 set"

#: le prove della chiave chiedono 5 token APPOSTA (connectivity_check,
#: verify_keys): finire lo spazio di risposta e' l'esito atteso, non un guasto
TRONCATE_VOLUTE = frozenset({"ai-connettivita", "ai-verifica"})
#: chi usa il testo cosi' com'e' e non aspetta dati strutturati (JSON): una
#: risposta tagliata a meta' resta, monca (learning_loop la salva se non e' vuota)
TESTO_LIBERO = frozenset({"ai-learning"})
#: le ragioni che girano (anche) sul runner GitHub, col modello preso dal segreto
#: ANTHROPIC_MODEL e non dal .env della VPS: learning.yml la domenica,
#: connectivity.yml ai push dei suoi file (la prova si lancia anche dalla VPS)
DAL_RUNNER = frozenset({"ai-learning", "ai-connettivita"})
#: sotto questa cifra (fra ieri e oggi) un modello diverso non vale un ⚠️: basta
#: una riga ➖ che lo dice (29 set 2026: il ping del runner costa ~0,0002 $)
SOGLIA_AVVISO_MODELLO_USD = 0.01

_MESI = ("gen", "feb", "mar", "apr", "mag", "giu",
         "lug", "ago", "set", "ott", "nov", "dic")


def perche(etichetta: str) -> str:
    """La frase del perche' di un'etichetta; sconosciuta -> l'etichetta stessa."""
    return RAGIONI.get(etichetta, etichetta)


def _intero(x: Any) -> int:
    try:
        return max(0, int(x or 0))
    except (TypeError, ValueError):
        return 0


def _chiave(x: Any, riserva: str = "?") -> str:
    """Un nome di campo Firestore non puo' essere vuoto."""
    s = str(x).strip() if x is not None else ""
    return s[:100] or riserva


# --------------------------------------------------------------------------- #
# REGISTRAZIONE — dopo ogni messages.create                                    #
# --------------------------------------------------------------------------- #
def registra(resp: Any, label: str, now: Optional[float] = None, fb: Any = None) -> None:
    """Somma i token di UNA risposta nel documento del giorno. Non solleva mai.

    Va chiamata SUBITO dopo `messages.create`, prima di guardare il testo: una
    risposta senza JSON, o troncata, e' pagata come una buona.
    """
    try:
        ts = time.time() if now is None else float(now)
        usage = getattr(resp, "usage", None)
        voce = {
            "n": 1,
            "in": _intero(getattr(usage, "input_tokens", 0)),
            "out": _intero(getattr(usage, "output_tokens", 0)),
            "cache_w": _intero(getattr(usage, "cache_creation_input_tokens", 0)),
            "cache_r": _intero(getattr(usage, "cache_read_input_tokens", 0)),
            "stop": {_chiave(getattr(resp, "stop_reason", None)): 1},
        }
        modello = _chiave(getattr(resp, "model", None))
        # il modello anche PER RAGIONE (29 set 2026): senza, l'avviso «ha
        # risposto un modello diverso» non sa dire chi e' stato (runner GitHub o
        # VPS), e il rimedio e' diverso
        voce["modelli"] = {modello: 1}
        ora = datetime.fromtimestamp(ts, fuso()).strftime("%H")
        client = fb if fb is not None else get_firebase()
        client.incrementa(
            COLLEZIONE, giorno_locale(ts),
            {"ragioni": {_chiave(label, "ai"): voce},
             "modelli": {modello: 1},
             "ore": {ora: 1}},
            imposta={"aggiornato_at": ts})
    except Exception as exc:  # noqa: BLE001 — la misura non ferma mai la chiamata
        print(f"[ai-spesa] non registrata ({type(exc).__name__}: {str(exc)[:120]})")


# --------------------------------------------------------------------------- #
# CONTI — funzioni pure, per il report                                         #
# --------------------------------------------------------------------------- #
def costo_usd(n_in: int, n_out: int, cache_w: int = 0, cache_r: int = 0) -> float:
    """Dollari di una quantita' di token, ai prezzi configurati (per milione).
    I token della cache si pagano come multipli del prezzo di lettura."""
    p_in = float(settings.AI_PREZZO_INGRESSO_MTOK) / 1_000_000
    p_out = float(settings.AI_PREZZO_USCITA_MTOK) / 1_000_000
    return (n_in * p_in + n_out * p_out
            + cache_w * p_in * float(settings.AI_CACHE_SCRITTURA_MULT)
            + cache_r * p_in * float(settings.AI_CACHE_LETTURA_MULT))


def riepilogo(doc: Any) -> list[dict]:
    """Le ragioni di un giorno, dalla piu' cara: [{etichetta, perche, n, in, out,
    cache_w, cache_r, letti, usd, troncate, modelli}]. `letti` = tutti i token
    in ingresso, cache compresa; `troncate` = risposte finite per max_tokens;
    `modelli` = {modello: chiamate} della ragione (vuoto nei documenti scritti
    prima del 29 set sera, che li tenevano solo per giorno)."""
    ragioni = (doc or {}).get("ragioni") if isinstance(doc, dict) else None
    righe = []
    for etichetta, v in (ragioni or {}).items():
        if not isinstance(v, dict):
            continue
        r = {k: _intero(v.get(k)) for k in ("n", "in", "out", "cache_w", "cache_r")}
        if not r["n"]:
            continue
        stop = v.get("stop") if isinstance(v.get("stop"), dict) else {}
        modelli = v.get("modelli") if isinstance(v.get("modelli"), dict) else {}
        r.update(etichetta=etichetta, perche=perche(etichetta),
                 letti=r["in"] + r["cache_w"] + r["cache_r"],
                 usd=costo_usd(r["in"], r["out"], r["cache_w"], r["cache_r"]),
                 troncate=_intero(stop.get("max_tokens")),
                 modelli={str(m): _intero(n) for m, n in modelli.items() if _intero(n)})
        righe.append(r)
    righe.sort(key=lambda r: (-r["usd"], r["etichetta"]))
    return righe


def _usd(x: float) -> str:
    cifre = 2 if (x == 0 or x >= 0.1) else (3 if x >= 0.01 else 4)
    return f"{x:.{cifre}f}".replace(".", ",") + " $"


def _chiamate(n: int) -> str:
    return "1 chiamata" if n == 1 else f"{n} chiamate"


def _num(x: float) -> str:
    return f"{x:g}".replace(".", ",")


def _tok(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1e6:.1f} milioni".replace(".", ",")
    if n >= 10_000:
        return f"{n / 1000:.0f} mila"
    if n >= 1000:
        return f"{n / 1000:.1f} mila".replace(".", ",")
    return str(n)


def _giorno_breve(giorno: str) -> str:
    try:
        d = date.fromisoformat(giorno)
        return f"{d.day} {_MESI[d.month - 1]}"
    except (TypeError, ValueError):
        return str(giorno)


def _prima_ora(doc: Any) -> Optional[int]:
    ore = (doc or {}).get("ore") if isinstance(doc, dict) else None
    valide = [int(h) for h, n in (ore or {}).items()
              if str(h).isdigit() and _intero(n) > 0]
    return min(valide) if valide else None


#: come si chiama una ragione attesa quando manca, nella riga di «ieri»
_NOME_BREVE = {"ai-shadow": "l'ombra"}


def ragioni_attese() -> frozenset:
    """Le ragioni che in una giornata normale ci sono di sicuro. Oggi solo
    l'ombra (`ai-shadow`, ~42 chiamate al giorno per la D6), se accesa: gira nel
    BOT, che comincia a contare solo dopo il riavvio col codice nuovo, mentre la
    ricerca (discovery, optimize) conta dal primo pull dell'agente ops."""
    if settings.AI_SHADOW_ENABLED and settings.AI_ENABLED:
        return frozenset({"ai-shadow"})
    return frozenset()


def _perche_non_intero(giorno: str, docs: dict, attese=frozenset()) -> Optional[str]:
    """Perche' `giorno` e' probabilmente misurato solo in parte, o None se
    sembra intero. Due casi (29 set 2026):

      * il contatore e' partito a giornata iniziata: il giorno prima non ha dati
        e la prima chiamata e' arrivata tardi (il primo giorno, o dopo un buco
        della macchina). Il giorno prima si guarda solo se e' fra quelli letti:
        per questo `stato_spesa` legge un giorno in piu' della finestra;
      * manca una ragione attesa (`ragioni_attese`): nei giorni fra il pull della
        ricerca e il riavvio del bot conta la ricerca ma non l'ombra, e il conto
        esce piu' basso di ~0,80 $ (D6) pur sembrando una giornata piena.

    Senza, la media della prima settimana conterebbe un conto parziale come una
    giornata intera."""
    doc = docs.get(giorno)
    presenti = {r["etichetta"] for r in riepilogo(doc)}
    mancano = sorted(set(attese) - presenti)
    if presenti and mancano:
        chi = ", ".join(f"{_NOME_BREVE.get(m, m)} ({m})" for m in mancano)
        return f"manca {chi}, cioe' il bot non ha contato: non ancora riavviato col contatore, o fermo"
    try:
        prima = (date.fromisoformat(giorno) - timedelta(days=1)).isoformat()
    except (TypeError, ValueError):
        return None
    if prima not in docs or riepilogo(docs.get(prima)):
        return None
    ora = _prima_ora(doc)
    # «tardi» = dalle 3 in poi: in un giorno normale la ricerca gira ogni 3 ore e
    # l'ombra decine di volte, quindi la prima chiamata arriva nelle prime ore.
    # E' una soglia a buon senso, non misurata; conta solo dopo un giorno vuoto.
    if ora is not None and ora >= 3:
        return f"prima chiamata contata alle {ora:02d}"
    return None


def _senza_data(modello: str) -> str:
    """Il nome del modello senza la data finale (`-AAAAMMGG`) ne' `-latest`: un
    alias e la sua versione con data sono lo stesso listino."""
    m = str(modello).strip()
    m = re.sub(r"-latest$", "", m)
    return re.sub(r"-\d{8}$", "", m)


def _stesso_modello(visto: str, atteso: str) -> bool:
    """Stesso listino = stesso nome, a meno della data finale. NON per prefisso:
    «x-4» e «x-4-8» sono modelli diversi con prezzi che possono differire."""
    return _senza_data(visto) == _senza_data(atteso)


def _modelli_diversi(docs: dict, giorni, atteso: str) -> list[dict]:
    """Le chiamate di `giorni` fatte da un modello diverso da `atteso`, per
    ragione: [{etichetta, modello, n, usd}]. `usd` e' la quota della ragione
    (costo × chiamate di quel modello / chiamate): i token non sono divisi per
    modello, e' una stima. I documenti senza modelli per ragione (scritti prima
    del 29 set sera) finiscono in una voce senza etichetta e senza costo."""
    per: dict = {}
    for g in giorni:
        doc = docs.get(g) or {}
        spiegati: dict[str, int] = {}
        for r in riepilogo(doc):
            for m, n in r["modelli"].items():
                spiegati[m] = spiegati.get(m, 0) + n
                if m == "?" or _stesso_modello(m, atteso):
                    continue
                v = per.setdefault((r["etichetta"], m), {"etichetta": r["etichetta"], "modello": m,
                                                         "n": 0, "usd": 0.0})
                v["n"] += n
                v["usd"] += r["usd"] * n / r["n"] if r["n"] else 0.0
        for m, n in ((doc.get("modelli") or {}) if isinstance(doc, dict) else {}).items():
            resto = _intero(n) - spiegati.get(str(m), 0)
            if resto > 0 and str(m) != "?" and not _stesso_modello(str(m), atteso):
                v = per.setdefault((None, str(m)), {"etichetta": None, "modello": str(m),
                                                    "n": 0, "usd": None})
                v["n"] += resto
    return sorted(per.values(), key=lambda v: (-(v["usd"] or 0.0), str(v["etichetta"]), v["modello"]))


def _riga_modello(v: dict, atteso: str) -> str:
    """Una riga sull'avviso del modello: chi, quanto, e il rimedio GIUSTO. Il
    runner GitHub prende il modello dal segreto ANTHROPIC_MODEL (vuoto = quello
    di default del codice): li' si corregge il segreto, non i prezzi della VPS."""
    et = v["etichetta"]
    chi = (f"{_chiamate(v['n'])} fra ieri e oggi" if et is None else
           f"{_chiamate(v['n'])} fra ieri e oggi per «{perche(et)}» ({et}, circa {_usd(v['usd'])})")
    testa = f"{chi} ha usato il modello «{v['modello']}» invece di quello della VPS «{atteso}»"
    if v["usd"] is not None and v["usd"] < SOGLIA_AVVISO_MODELLO_USD:
        dove = " (probabile runner GitHub: segreto ANTHROPIC_MODEL)" if et in DAL_RUNNER else ""
        return f"➖ {testa}{dove}: cifra trascurabile, contata col prezzo della VPS"
    if et in DAL_RUNNER:
        return (f"⚠️ {testa}: probabile runner GitHub, che prende il modello dal segreto "
                f"ANTHROPIC_MODEL (se e' vuoto, quello di default del codice). Il costo e' "
                f"calcolato col prezzo della VPS, quindi e' approssimato; per allinearlo si "
                f"imposta quel segreto, NON si cambiano i prezzi AI_PREZZO_*")
    return (f"⚠️ {testa}: se il modello della VPS e' cambiato davvero, i dollari qui sopra "
            f"usano il prezzo vecchio e vanno aggiornati i prezzi AI_PREZZO_* nel .env della VPS")


def righe_spesa(docs_per_giorno: dict, oggi: str, ieri: str, ora_locale: str,
                modello_atteso: Optional[str] = None, attese=None) -> list[str]:
    """Il testo della sezione SPESA AI del report. Funzione pura: riceve i
    documenti `ai_spesa` per giorno (quelli che mancano valgono «nessun dato»).
    `attese`: le ragioni che una giornata intera deve avere (default
    `ragioni_attese()`)."""
    docs = {g: (d if isinstance(d, dict) else {}) for g, d in (docs_per_giorno or {}).items()}
    atteso = settings.ANTHROPIC_MODEL if modello_atteso is None else modello_atteso
    attese = ragioni_attese() if attese is None else frozenset(attese)
    out = [f"SPESA AI (misurata: token restituiti dall'API × prezzo configurato "
           f"{_num(settings.AI_PREZZO_INGRESSO_MTOK)}/{_num(settings.AI_PREZZO_USCITA_MTOK)}"
           f" $ per milione letti/scritti; la fattura vera e' nella console Anthropic)"]

    # IERI, giornata intera: e' il numero da leggere. Il controllo del mattino
    # gira verso le 8 italiane, quindi «oggi» copre poche ore.
    r_ieri = riepilogo(docs.get(ieri))
    tot_ieri = sum(r["usd"] for r in r_ieri)
    if r_ieri:
        motivo = _perche_non_intero(ieri, docs, attese)
        intera = ("giornata intera ora italiana" if motivo is None
                  else f"giornata NON intera: {motivo}")
        out.append(f"💶 ieri ({_giorno_breve(ieri)}, {intera}): {_usd(tot_ieri)} in "
                   f"{_chiamate(sum(r['n'] for r in r_ieri))}")
        for r in r_ieri:
            quota = r["usd"] / tot_ieri * 100 if tot_ieri > 0 else 0.0
            out.append(f"   {r['perche']} ({r['etichetta']}): {_chiamate(r['n'])} · "
                       f"{_tok(r['letti'])} token letti + {_tok(r['out'])} scritti · "
                       f"{_usd(r['usd'])} · {quota:.0f}% della spesa di ieri")
    else:
        out.append(f"➖ ieri ({_giorno_breve(ieri)}): nessuna chiamata registrata "
                   f"(contatore appena nato, AI ferma o Firebase non raggiungibile)")

    r_oggi = riepilogo(docs.get(oggi))
    if r_oggi:
        out.append(f"💶 oggi fino alle {ora_locale} ora italiana: {_usd(sum(r['usd'] for r in r_oggi))} "
                   f"in {_chiamate(sum(r['n'] for r in r_oggi))}")
    else:
        out.append(f"➖ oggi fino alle {ora_locale} ora italiana: nessuna chiamata registrata")

    # ULTIMI 7 GIORNI COMPLETI con dati: media e proiezione, dichiarando su quanti.
    # Un giorno in piu' letto (il piu' vecchio) serve solo a giudicare il primo
    # dei 7: non entra nella media.
    completi = sorted(g for g in docs if g < oggi)[-7:]
    con_dati = [g for g in completi if riepilogo(docs[g])]
    parziali = [g for g in con_dati if _perche_non_intero(g, docs, attese) is not None]
    validi = [g for g in con_dati if g not in parziali]
    fuori = (f" (escluso {', '.join(_giorno_breve(g) for g in parziali)}: "
             f"misurato solo in parte)" if parziali else "")
    if validi:
        media = sum(sum(r["usd"] for r in riepilogo(docs[g])) for g in validi) / len(validi)
        su = "1 giorno" if len(validi) == 1 else f"{len(validi)} giorni"
        mese = media * 30
        mese_txt = f"{mese:.0f} $" if mese >= 10 else _usd(mese)
        out.append(f"   ultimi 7 giorni completi: media {_usd(media)} al giorno su {su} "
                   f"con dati → circa {mese_txt} al mese (media × 30){fuori}")
    else:
        out.append(f"   media: nessun giorno completo misurato ancora{fuori}; fino ad allora "
                   f"vale la stima D6 del backlog ({STIMA_D6})")

    # AVVISI — risposte tagliate a meta': pagate, e se aspettavano dati
    # strutturati buttate. Le prove della chiave (5 token apposta) non contano.
    per_ieri = {r["etichetta"]: r for r in r_ieri}
    per_oggi = {r["etichetta"]: r for r in r_oggi}
    troncate = []
    for etichetta in sorted((set(per_ieri) | set(per_oggi)) - TRONCATE_VOLUTE):
        parti = [f"{quando} {r['troncate']} su {r['n']}"
                 for quando, r in (("ieri", per_ieri.get(etichetta)),
                                   ("oggi", per_oggi.get(etichetta)))
                 if r and r["troncate"]]
        if parti:
            esito = ("testo salvato ma monco" if etichetta in TESTO_LIBERO
                     else "pagate e buttate: aspettavano dati strutturati")
            troncate.append(f"   {perche(etichetta)} ({etichetta}): {' · '.join(parti)} → {esito}")
    if troncate:
        out.append("⚠️ risposte tagliate a meta' (il modello ha finito lo spazio di risposta "
                   "concesso, max_tokens):")
        out.extend(troncate)

    # AVVISO — ha risposto un modello diverso da quello per cui vale il prezzo
    if atteso:
        out.extend(_riga_modello(v, atteso) for v in _modelli_diversi(docs, (ieri, oggi), atteso))

    out.append("➖ non contati: le sessioni @claude su GitHub (workflow claude.yml: "
               "stessa chiave, ma non passano da questo codice) e il controllo della "
               "chiave del mattino (~0,0002 $: questo report non scrive nulla)")
    return out
