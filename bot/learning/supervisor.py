"""IL SUPERVISORE — cambia i parametri da solo, dentro un vincolo che non puo' violare.

IL PROBLEMA CHE RISOLVE. Quando il gate non promuove niente per settimane, l'unica
reazione umana disponibile e' "abbassiamo le soglie finche' qualcosa passa". E'
anche la peggiore: una soglia abbassata fino a far passare qualcosa seleziona
esattamente il rumore che quella soglia esisteva per escludere, e il conto arriva
dopo, in paper o coi soldi veri.

Il modo per automatizzare la taratura SENZA cadere in quella trappola non e' la
prudenza — e' un vincolo misurabile. Eccolo.

    IL BUDGET DI FALSI POSITIVI

Il gate valuta migliaia di coppie per run. A quella scala, una parte di cio' che
passa passa PER CASO: se si estrae abbastanza, qualcosa vince alla lotteria. Il
numero atteso di coppie fortunate e' calcolabile, e l'autopsia ne fornisce
l'ingrediente che prima mancava — il TASSO DI PASSAGGIO OSSERVATO.

    attese_per_caso ~= valutazioni x tasso_passaggio ^ conferme_efficaci

Il supervisore puo' muovere qualunque parametro PURCHE' questo numero resti sotto
il budget (default: 1 coppia fortunata attesa per giro). E' una licenza
quantitativa: se il gate e' molto piu' severo di quanto il budget richieda, si puo'
allentare — e si sa esattamente di quanto. Se il budget e' esaurito, non si allenta
piu' nulla, nemmeno se non passa niente per mesi. In quel caso il problema non e'
la soglia ed e' onesto dirlo.

Le conferme NON contano come test indipendenti: finestre distanti pochi giorni
vedono quasi gli stessi dati. `SUPERVISOR_CONFIRM_INDEPENDENCE` (default 0.5) dice
quanto vale una conferma in piu' — mezzo test indipendente. E' una stima prudente e
dichiarata, non una verita': con 3 conferme l'esponente vale 2, non 3.

    COSA NON PUO' FARE, MAI

  * scendere sotto i PAVIMENTI: sono valori sotto i quali un criterio smette di
    significare qualcosa (un profit factor sotto i costi, trenta trade che
    diventano cinque, un holdout che sparisce);
  * toccare l'holdout, la parita' col backtest, i dati sintetici, i limiti di
    rischio hard, DRY_RUN;
  * ABBASSARE il numero di conferme richieste: puo' solo alzarlo;
  * allentare quando le candidate muoiono sull'HOLDOUT. Li' il messaggio dei dati
    e' "funzionano dove le abbiamo scelte e non fuori", cioe' sovradattamento:
    allentare promuoverebbe proprio le sovradattate. La reazione corretta e'
    l'opposta — ridurre le estrazioni.

    COME SI ACCORGE DI AVER SBAGLIATO

Ogni modifica e' registrata con il tasso di passaggio che l'ha motivata. Il run
successivo misura il nuovo tasso: se il budget viene superato, il supervisore
TORNA INDIETRO da solo. E' un anello chiuso con un segnale misurato, non una
sequenza di aggiustamenti al buio.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# --------------------------------------------------------------------------- #
# Cosa si puo' muovere, e fin dove                                            #
# --------------------------------------------------------------------------- #
# (parametro, pavimento, passo relativo, tipo). Il pavimento non e' prudenza: e'
# il punto sotto il quale il criterio smette di misurare qualcosa.
@dataclass(frozen=True)
class Tunable:
    name: str
    floor: float
    step: float          # frazione di allentamento per mossa
    kind: str = "float"  # "int" per i conteggi
    why_floor: str = ""


TUNABLES = {
    "trades": Tunable("GATE_MIN_TRADES", 20.0, 0.15, "int",
                      "sotto i venti trade nessuna statistica dice piu' niente"),
    "pf": Tunable("GATE_PF_THRESHOLD", 1.15, 0.05, "float",
                  "sotto 1.15 il margine sui costi sparisce col primo slippage"),
    "win_rate": Tunable("GATE_WIN_RATE_FLOOR", 0.30, 0.05, "float",
                        "sotto il 30% servono code enormi per pareggiare"),
    "total_return": Tunable("GATE_MIN_TOTAL_RETURN", 0.05, 0.15, "float",
                            "sotto il 5% OOS il risultato e' indistinguibile da zero"),
    "consistency": Tunable("GATE_CONSISTENCY_FRACTION", 0.60, 0.10, "float",
                           "sotto il 60% delle finestre positive non e' piu' un edge, "
                           "e' un periodo fortunato"),
    "recovery": Tunable("GATE_MIN_RECOVERY", 1.0, 0.10, "float",
                        "sotto 1 la curva rende meno della buca che scava"),
    "regime": Tunable("GATE_REGIME_MIN_PF", 0.50, 0.10, "float",
                      "sotto 0.5 si accetta un regime in emorragia aperta"),
    # pf_ex_top e' GIA' al suo pavimento (1.0 = pareggio senza i colpi migliori):
    # compare qui perche' la diagnosi lo nomini, non perche' si possa muovere.
    "pf_ex_top": Tunable("GATE_MIN_PF_EX_TOP", 1.0, 0.0, "float",
                         "sotto il pareggio senza i colpi migliori si valida la fortuna"),
}

# Non si toccano. Non "di default": mai.
NEVER = {
    "GATE_HOLDOUT_DAYS": "l'holdout e' l'unico campione mai visto dalla selezione",
    "GATE_DROP_TOP_FRAC": "spegnerebbe il test di robustezza invece di superarlo",
    "OPTIMIZER_MIN_PASSES": "si puo' solo ALZARE, e lo fa un'altra regola",
    "OPTIMIZER_NEW_DATA_MIN_HOURS": "conferme su dati sovrapposti non sono conferme",
    "BACKTEST_ALLOW_SYNTHETIC": "validare su dati finti produce coppie fasulle",
    "DRY_RUN": "non e' un parametro di ricerca",
    "BACKTEST_PARITY": "cambierebbe il significato del confronto gate-paper",
}

# Il criterio che ferma -> il parametro che lo governa.
CRITERION_PARAM = {k: t.name for k, t in TUNABLES.items()}


@dataclass
class Decision:
    kind: str                      # set_param | tighten | fast_gate | revert | none
    reason: str
    param: str = ""
    old: Optional[float] = None
    new: Optional[float] = None
    detail: dict = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Il vincolo                                                                   #
# --------------------------------------------------------------------------- #
def effective_confirmations(min_passes: int, independence: float) -> float:
    """Quante conferme INDIPENDENTI valgono `min_passes` conferme reali.

    La prima e' piena; ogni successiva vale `independence` (default 0.5), perche'
    finestre a pochi giorni di distanza vedono quasi gli stessi dati. Trattarle come
    indipendenti gonfierebbe la fiducia proprio dove serve prudenza.
    """
    return 1.0 + max(0, min_passes - 1) * max(0.0, min(1.0, independence))


def expected_lucky(evaluated: int, pass_rate: float, min_passes: int,
                   independence: float = 0.5, runs_per_day: float = 1.0) -> float:
    """Coppie attese che raggiungono la validazione PER CASO, al giorno.

    E' il numero che il supervisore non puo' far crescere oltre il budget. Con
    ventiduemila valutazioni e un tasso dello 0.036% vale circa 0.003: il gate e'
    oggi molto piu' severo di quanto il budget richieda, ed e' esattamente questa
    misura a dire quanto margine c'e' — invece di allentare a sentimento.
    """
    if evaluated <= 0 or pass_rate <= 0:
        return 0.0
    exp = effective_confirmations(min_passes, independence)
    return evaluated * (pass_rate ** exp) * max(0.0, runs_per_day)


def max_pass_rate(evaluated: int, min_passes: int, budget: float = 1.0,
                  independence: float = 0.5, runs_per_day: float = 1.0) -> float:
    """Il tasso di passaggio piu' alto che il budget consente. Oltre questo, ogni
    allentamento comprerebbe candidate fortunate invece che strategie."""
    if evaluated <= 0 or budget <= 0:
        return 0.0
    exp = effective_confirmations(min_passes, independence)
    return min(1.0, (budget / (evaluated * max(1e-9, runs_per_day))) ** (1.0 / exp))


def headroom(evaluated: int, pass_rate: float, min_passes: int, budget: float = 1.0,
             independence: float = 0.5, runs_per_day: float = 1.0) -> float:
    """Quante volte il tasso attuale puo' ancora crescere restando nel budget.
    < 1 = budget gia' sforato; 1 = al limite; 10 = c'e' spazio per dieci volte tanto."""
    top = max_pass_rate(evaluated, min_passes, budget, independence, runs_per_day)
    if pass_rate <= 0:
        return float("inf") if top > 0 else 0.0
    return top / pass_rate


# --------------------------------------------------------------------------- #
# La decisione                                                                 #
# --------------------------------------------------------------------------- #
@dataclass
class Context:
    ready: bool = False
    validated: int = 0
    days_stagnant: float = 0.0
    evaluated: int = 0
    passed: int = 0
    binding: dict = field(default_factory=dict)     # criterio -> casi
    # QUASI-PASSAGGI: criterio -> scarti (negativi) delle candidate fermate da QUEL
    # SOLO criterio. E' il segnale che guida la taratura; `binding` serve a capire
    # il terreno, non a scegliere la mossa. Vedi `_lever`.
    near: dict = field(default_factory=dict)
    current: dict = field(default_factory=dict)     # nome parametro -> valore attuale
    min_passes: int = 3
    runs_per_day: float = 3.0
    budget: float = 1.0
    independence: float = 0.5
    stagnant_after_days: float = 2.0
    fast_gate_after_days: float = 0.0     # 0 = disarmato (vedi decide())
    days_since_fast_gate: float = 999.0
    fast_gate_cooldown_days: float = 7.0

    @property
    def pass_rate(self) -> float:
        return (self.passed / self.evaluated) if self.evaluated else 0.0


def _relaxed(t: Tunable, value: float, need: float = 0.0) -> Optional[float]:
    """Il valore dopo UNA mossa di allentamento, o None se e' gia' al pavimento.

    `need` = scarto relativo da coprire per sbloccare le candidate che quel criterio
    sta fermando da solo. Si allenta di quanto SERVE (piu' un margine minimo), mai
    piu' del passo massimo: un allentamento piu' grande del necessario regala
    passaggi a candidate che non erano vicine.

    Un parametro alla volta: cambiarne due insieme renderebbe impossibile sapere
    quale dei due ha prodotto l'effetto misurato al run successivo.
    """
    if t.step <= 0 or value <= t.floor:
        return None
    frac = min(t.step, max(0.01, abs(need) * 1.1))   # +10% di margine sullo scarto
    nxt = value * (1.0 - frac)
    if t.kind == "int":
        nxt = float(int(nxt))
        if nxt >= value:
            nxt = value - 1
    return max(t.floor, nxt)


def _lever(ctx: "Context") -> tuple[str, list]:
    """QUALE criterio conviene allentare, e per quali candidate.

    Qui sta la lezione dei primi dati veri. La scelta ovvia sarebbe il criterio che
    ferma piu' candidate (`binding`), e sarebbe SBAGLIATA: nella prima autopsia
    reale il 78% moriva su `total_return`, ma quelle stesse candidate fallivano
    anche pf, win_rate, recovery, consistency e pf_ex_top — sei criteri insieme,
    ognuno presente in oltre il 90% delle bocciature. Allentare `total_return` non
    ne avrebbe convertita NESSUNA: avrebbe speso una mossa di budget per spostare
    una soglia davanti a candidate che restavano bocciate da altre cinque.

    Quando quasi tutto fallisce quasi tutto, il conteggio delle bocciature descrive
    la qualita' media delle candidate, non un collo di bottiglia da rimuovere.

    Le uniche candidate che un allentamento converte davvero sono quelle fermate da
    UN SOLO criterio. Quindi la leva si sceglie li': il criterio con piu'
    quasi-passaggi, e il passo si dimensiona sui loro scarti. Cosi' la decisione
    diventa anche falsificabile — si puo' dire in anticipo quante candidate
    dovrebbe sbloccare, e verificarlo al giro dopo.
    """
    if not ctx.near:
        return "", []
    best = max(ctx.near.items(), key=lambda kv: (len(kv[1]), -min(kv[1], default=0)))
    return best[0], list(best[1])


def decide(ctx: Context) -> list[Decision]:
    """Cosa fare adesso. Lista vuota = niente da fare, ed e' un esito normale."""
    out: list[Decision] = []

    if ctx.ready:
        # Il paper e' partito: si SMETTE di tarare. Continuare ad allentare mentre
        # il sistema opera significherebbe cambiare le regole a partita in corso, e
        # rendere non interpretabile il confronto fra cio' che il gate ha promesso e
        # cio' che il paper sta vivendo.
        return [Decision("none", "GATE 1 superato: il paper opera, la taratura si ferma")]

    if ctx.days_stagnant < ctx.stagnant_after_days:
        return [Decision("none",
                         f"solo {ctx.days_stagnant:.1f} giorni senza validate: "
                         f"si aspetta ({ctx.stagnant_after_days:g} giorni) prima di "
                         f"toccare qualcosa")]

    # 1) IL BUDGET. E' il vincolo, quindi si guarda per primo.
    room = headroom(ctx.evaluated, ctx.pass_rate, ctx.min_passes, ctx.budget,
                    ctx.independence, ctx.runs_per_day)
    lucky = expected_lucky(ctx.evaluated, ctx.pass_rate, ctx.min_passes,
                           ctx.independence, ctx.runs_per_day)
    budget_detail = {"pass_rate": round(ctx.pass_rate, 6),
                     "expected_lucky_per_day": round(lucky, 4),
                     "headroom": (None if room == float("inf") else round(room, 2)),
                     "evaluated": ctx.evaluated, "runs_per_day": ctx.runs_per_day}

    if room < 1.0:
        # Budget sforato: allentare comprerebbe fortuna. Si riduce il numero di
        # ESTRAZIONI, che e' l'altro modo di rientrare — e l'unico onesto qui.
        out.append(Decision(
            "tighten",
            f"budget di falsi positivi SFORATO ({lucky:.2f} coppie fortunate attese "
            f"al giorno, tetto {ctx.budget:g}): non si allenta nulla, si riducono le "
            f"estrazioni", detail=budget_detail))
        return out

    # 2) DOVE MUOIONO. Senza diagnosi non si tocca niente: sarebbe tarare al buio,
    # cioe' la cosa che questo modulo esiste per evitare.
    if not ctx.binding:
        return [Decision("none", "nessuna autopsia disponibile: non si tara al buio",
                         detail=budget_detail)]

    # 3) LA LEVA si sceglie sui QUASI-PASSAGGI, non sul conteggio delle bocciature.
    # (Il perche' sta in `_lever`: quando quasi tutte le candidate falliscono quasi
    # tutti i criteri, allentare il criterio piu' frequente non converte nessuno.)
    worst, shortfalls = _lever(ctx)
    if not worst:
        return [Decision(
            "none",
            "nessun quasi-passaggio: nessuna candidata e' fermata da UN SOLO "
            "criterio, quindi non esiste una soglia che ne sbloccherebbe qualcuna. "
            "Allentare qui sarebbe una mossa al buio: il problema non e' il gate, "
            "sono le candidate", detail=budget_detail)]

    # 4) IL CASO HOLDOUT. La candidata supera tutto e cade sui dati mai visti: e'
    # sovradattamento conclamato. Allentare promuoverebbe proprio le sovradattate.
    if worst == "holdout":
        out.append(Decision(
            "tighten",
            f"i {len(shortfalls)} quasi-passaggi muoiono sull'HOLDOUT: superano ogni "
            f"criterio sulle finestre di selezione e falliscono sui dati mai visti. "
            f"E' sovradattamento — si riducono le candidate, non si allentano i "
            f"criteri", detail=budget_detail))
        return out

    t = TUNABLES.get(worst)
    if t is None:
        return [Decision("none", f"criterio '{worst}' non e' tarabile automaticamente",
                         detail=budget_detail)]
    cur = ctx.current.get(t.name)
    if cur is None:
        return [Decision("none", f"valore attuale di {t.name} sconosciuto",
                         detail=budget_detail)]

    # scarto da coprire: la MEDIANA dei quasi-passaggi. Coprirli tutti significherebbe
    # dimensionare la mossa sul caso peggiore, cioe' allentare piu' del necessario per
    # la maggioranza.
    ordered = sorted(abs(s) for s in shortfalls if s is not None)
    need = ordered[len(ordered) // 2] if ordered else 0.0
    nxt = _relaxed(t, float(cur), need)
    if nxt is None:
        return [Decision(
            "none",
            f"le candidate piu' vicine al passaggio ({len(shortfalls)}) sono fermate "
            f"da {t.name}, che e' gia' al pavimento ({t.floor:g}): {t.why_floor}. "
            f"Non si scende oltre: quello che manca non e' una soglia piu' bassa",
            param=t.name, old=float(cur), detail={**budget_detail,
                                                  "near_misses": len(shortfalls)})]

    moved = abs(nxt - float(cur)) / float(cur) if cur else 0.0
    converts = sum(1 for s in ordered if s <= moved + 1e-9)
    out.append(Decision(
        "set_param",
        f"{len(shortfalls)} candidate sono fermate SOLO da '{worst}' (mediana: manca "
        f"{need * 100:.1f}%). La mossa ne dovrebbe sbloccare ~{converts}, e il budget "
        f"la consente (spazio {room:.0f}x, attese {lucky:.3f}/giorno contro un tetto "
        f"di {ctx.budget:g})",
        param=t.name, old=float(cur), new=nxt,
        detail={**budget_detail, "near_misses": len(shortfalls),
                "expected_conversions": converts}))

    # 5) MISURARE SUBITO. Un parametro cambiato che aspetta tre settimane per essere
    # giudicato non e' un anello chiuso: e' una scommessa. fast_gate rigioca la
    # storia su tre finestre e restituisce il verdetto in ore.
    #
    # MA E' DISARMATO PER DEFAULT (soglia <= 0), ed e' l'unica azione irreversibile
    # che questo modulo puo' decidere da solo. Tre ragioni, tutte emerse guardando
    # cosa succederebbe davvero:
    #   * AZZERA il registro validato — cioe' proprio le conferme che si stanno
    #     accumulando, che costano una settimana l'una. Farlo scattare mentre
    #     maturano distruggerebbe l'unica cosa che stiamo aspettando;
    #   * il backup che scrive resta SUL DISCO della macchina, fuori da git, e non
    #     esiste nessuno script che lo ripristini: da remoto non si torna indietro;
    #   * non si vede. Gira in tmux, ferma il timer dell'optimizer mentre lavora, e
    #     se si interrompe lascia il registro a meta' senza che nessuno lo sappia.
    # Un'azione che non si puo' osservare ne' annullare da lontano non deve partire
    # da sola. Si arma esplicitamente (SUPERVISOR_FAST_GATE_DAYS > 0) quando c'e'
    # qualcuno che guarda.
    if (ctx.fast_gate_after_days > 0
            and ctx.days_stagnant >= ctx.fast_gate_after_days and ctx.validated == 0
            and ctx.days_since_fast_gate >= ctx.fast_gate_cooldown_days):
        out.append(Decision(
            "fast_gate",
            f"{ctx.days_stagnant:.0f} giorni senza una sola coppia validata: si "
            f"rigioca la storia su 3 finestre per misurare il cambiamento in ore "
            f"invece che in settimane", detail=budget_detail))
    return out
