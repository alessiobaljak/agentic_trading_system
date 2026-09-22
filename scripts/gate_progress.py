"""QUANDO RIPARTE IL BOT — la data, non la speranza.

Dopo un reset del registro il paper resta fermo finche' il GATE 1 non dichiara
`ready`, e "aspetta qualche settimana" e' una risposta che non si puo' verificare.
Questo script la trasforma in un calendario, usando le stesse regole del gate:

  * una coppia e' VALIDATA con `pass_count >= OPTIMIZER_MIN_PASSES` (default 3);
  * un pass conta solo se dall'ultimo sono entrate OPTIMIZER_NEW_DATA_MIN_HOURS
    (default 168 = una settimana) di dati NUOVI. Quindi la prossima conferma di una
    coppia ha una DATA, e si puo' leggere adesso;
  * `ready` scatta per COPERTURA (frazione dell'universo con almeno una strategia
    validata) OPPURE per NUMERO ASSOLUTO di coppie validate
    (OPTIMIZER_READY_MIN_PAIRS), con i minimi di sicurezza sempre necessari.

La stima assume che ogni coppia passi ALMENO UNA VOLTA per finestra settimanale.
E' un'ipotesi realistica da quando il registro giudica per finestra e non per run:
prima la stessa stima era una finzione, perche' il purge contava i fallimenti a
ogni run e nessuna coppia sopravviveva abbastanza da arrivare alla conferma
successiva (vedi judge_window in scripts/optimize.py). Resta un limite inferiore:
chi non passa per due settimane intere esce comunque dal registro.

Uso (sul VPS):
    .venv/bin/python -m scripts.gate_progress
    .venv/bin/python -m scripts.gate_progress --top 20
"""
from __future__ import annotations

import argparse
import os
import time
from collections import Counter
from datetime import datetime, timezone

from bot.core.firebase_client import decode_pairs, get_firebase

MIN_PASSES = int(os.getenv("OPTIMIZER_MIN_PASSES", "3"))
NEW_DATA_MIN_S = float(os.getenv("OPTIMIZER_NEW_DATA_MIN_HOURS", "168")) * 3600
READY_FRACTION = float(os.getenv("OPTIMIZER_READY_FRACTION", "0.60"))
READY_MIN_PAIRS = int(os.getenv("OPTIMIZER_READY_MIN_PAIRS", "0"))
MIN_COVERED = int(os.getenv("OPTIMIZER_MIN_COVERED", "5"))
PURGE_FAILS = int(os.getenv("OPTIMIZER_PURGE_FAILS", "2"))
# Da quanti giorni senza essere valutata una coppia e' da considerare CONGELATA.
# Stessa variabile che usa il registro per decidere chi conta come validata:
# duplicarla come costante locale vorrebbe dire poterle far divergere.
FRESH_DAYS = float(os.getenv("OPTIMIZER_FRESH_DAYS", "3"))
#: il limite vero e' 1 MiB di Firestore; qui si guarda contro il tetto che il codice
#: si e' dato (`PARAM_DOC_MAX_BYTES`), che e' quello che scatta per primo.
LIMITE_DOC = float(os.getenv("PARAM_DOC_MAX_BYTES", "900000"))


def _when(ts: float) -> str:
    if ts <= 0:
        return "—"
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%d %b %H:%M")


def eta_ready(rec: dict, now: float) -> float:
    """Quando QUESTA coppia diventerebbe validata, se continuasse a passare.

    Il conto e' meccanico: mancano `MIN_PASSES - pass_count` conferme, e ognuna
    arriva alla chiusura di una finestra. Una coppia che non ha mai passato non ha
    una data — non ha ancora nemmeno la prima conferma.

    SI PARTE DA `window_start`, NON dall'ultimo pass. Sono due cose diverse e per
    alcune coppie divergono: quelle che esistevano gia' quando la regola della
    finestra e' entrata in vigore hanno la finestra aperta al momento del cambio,
    non al loro ultimo passaggio. Leggere `last_pass_data_end` dava date piu'
    ottimistiche di quelle vere — e' l'errore che mi ha fatto annunciare le seconde
    conferme per il 19 agosto quando sarebbero arrivate il 22.

    E SENZA FINESTRA NON C'E' NESSUNA DATA. E' la terza volta che questa funzione
    produce un calendario su coppie che non ci arriveranno, e ogni volta da una porta
    diversa: prima leggendo il campo sbagliato, poi contando coppie di coin uscite
    dall'universo, ora queste — valutate a ogni giro, ma che il gate non passa piu'.
    La finestra si apre solo quando una coppia RIPASSA, quindi per loro la prossima
    conferma non e' fra N giorni: dipende da un evento che potrebbe non succedere
    mai. Ripiegare su `last_pass_data_end` significa scambiare "l'ultima volta che ha
    funzionato" per "quando tornera' a funzionare", che e' esattamente la promessa
    che non si puo' fare.

    Il costo di quella finzione non era solo una data sbagliata: quelle coppie hanno
    la data piu' VECCHIA, quindi finivano in cima all'elenco e nascondevano le uniche
    che stavano davvero maturando.
    """
    passes = int(rec.get("pass_count", 0) or 0)
    if passes >= MIN_PASSES:
        return 0.0
    if passes <= 0:
        return float("inf")
    da = float(rec.get("window_start", 0) or 0)
    if da <= 0:
        return float("inf")
    return da + (MIN_PASSES - passes) * NEW_DATA_MIN_S


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=15,
                    help="quante coppie mostrare nel dettaglio")
    ap.add_argument("--coins-min-pass", type=int, default=None, metavar="K",
                    help="stampa SOLO la lista CSV delle coin con almeno K pass, "
                         "e nient'altro: e' l'input delle conferme mirate")
    args = ap.parse_args()

    fb = get_firebase()
    doc = fb.get_doc("strategy_registry", "validated") or {}
    pairs = decode_pairs(doc.get("pairs"))

    if args.coins_min_pass is not None:
        # solo le coppie ancora valutate: una lista di conferme mirate su coin
        # uscite dall'universo manderebbe l'optimizer a lavorare a vuoto
        _ora = time.time()
        coins = sorted({r.get("symbol") for r in pairs.values()
                        if int(r.get("pass_count", 0) or 0) >= args.coins_min_pass
                        and r.get("symbol")
                        and _ora - float(r.get("last_seen_at", 0) or 0)
                        < FRESH_DAYS * 86400})
        print(",".join(coins))
        return 0 if coins else 1

    if not pairs:
        print("[gate] registro VUOTO: nessuna coppia tracciata. Il bot non puo' "
              "operare finche' l'optimizer non ne accumula.")
        return 1
    now = time.time()

    # --- CHI E' ANCORA IN GIOCO --------------------------------------------- #
    # Una coppia che l'optimizer non valuta piu' e' CONGELATA: non prende conferme,
    # non prende fallimenti, non viene purgata. Resta nel registro esattamente com'era
    # l'ultimo giorno in cui e' stata vista.
    #
    # Non e' un caso di scuola: alzando la storia minima a 365 giorni, 57 coin sono
    # uscite dall'universo in un colpo solo, e con loro tutte le coppie che avevano
    # gia' accumulato un passaggio. Contarle qui dentro faceva due danni. Gonfiava la
    # distribuzione — "249 a un passaggio" quando molte non possono piu' avanzare — e
    # soprattutto la DATA: il calendario qui sotto si costruisce sulle coppie piu'
    # vicine al traguardo, che erano proprio quelle ferme dal 13 agosto. Il risultato
    # era un "il bot riparte il 27 agosto" calcolato su coppie che nessuno stava piu'
    # valutando. Una data che non sarebbe mai arrivata.
    fresche = {k: r for k, r in pairs.items()
               if now - float(r.get("last_seen_at", 0) or 0) < FRESH_DAYS * 86400}
    congelate = {k: r for k, r in pairs.items() if k not in fresche}

    dist = Counter(int(r.get("pass_count", 0) or 0) for r in fresche.values())
    validated = [k for k, r in fresche.items()
                 if int(r.get("pass_count", 0) or 0) >= MIN_PASSES]
    coins = {r.get("symbol") for k, r in fresche.items() if k in validated}

    print(f"[gate] {len(pairs)} coppie nel registro · {len(fresche)} ancora valutate "
          f"· soglia {MIN_PASSES} pass · un pass ogni {NEW_DATA_MIN_S / 3600:.0f}h "
          f"di dati nuovi")
    # SU QUANTE COIN DISTINTE. E' la domanda che il proprietario ha fatto l'11
    # settembre — «quante crypto potremmo operare?» — e il conteggio delle coppie non
    # la risponde: otto strategie diverse sulla STESSA moneta sono otto coppie e una
    # sola crypto. Peggio, sembrano una diversificazione e non lo sono: se il bot le
    # operasse tutte, avrebbe otto posizioni che salgono e scendono insieme.
    #
    # E' anche la soglia che decide se il paper puo' partire: OPTIMIZER_MIN_COVERED
    # coin distinte, non coppie.
    coin_per_livello: dict[int, set] = {}
    for r in fresche.values():
        p = int(r.get("pass_count", 0) or 0)
        coin_per_livello.setdefault(p, set()).add(r.get("symbol"))
    print("  distribuzione pass (solo coppie vive): " +
          " · ".join(f"{p} pass: {n} su {len(coin_per_livello.get(p, ())) } coin"
                     for p, n in sorted(dist.items())))
    if congelate:
        con_pass = sum(1 for r in congelate.values()
                       if int(r.get("pass_count", 0) or 0) > 0)
        print(f"  CONGELATE: {len(congelate)} coppie non piu' valutate da oltre "
              f"{FRESH_DAYS:g} giorni ({con_pass} avevano gia' un passaggio).\n"
              f"  La coin e' uscita dall'universo — di solito per storia insufficiente "
              f"o delisting.\n  Non avanzano e non falliscono: sono escluse da tutti i "
              f"conti qui sotto.")
    # --- DI CHE COSA E' FATTO IL REGISTRO ------------------------------------ #
    # Il 31 agosto le coppie a un passaggio sono passate da 137 a 2 in quattro
    # giorni. Con la contabilita' per finestra non e' possibile: per purgarne una
    # servono DUE finestre fallite, cioe' due settimane. Quindi qualcos'altro le ha
    # tolte — la potatura per anzianita' della discovery, o il tetto sul numero di
    # coppie — e senza questi conteggi la differenza non si vede.
    #
    # Le due popolazioni vanno separate perche' hanno regole diverse: le BASE non
    # vengono mai potate dalla discovery, le GENERATE si. Se il registro si riempie
    # di base morte, il tetto le tiene e butta fuori le generate — cioe' le uniche
    # che passano il gate. Un numero solo, "3041 coppie", nasconde esattamente questo.
    base = {k: r for k, r in fresche.items() if not r.get("generated")}
    gen = {k: r for k, r in fresche.items() if r.get("generated")}
    base_tot = sum(1 for r in pairs.values() if not r.get("generated"))
    tetto = int(os.getenv("OPTIMIZER_MAX_PAIRS", "3000"))
    print(f"  COMPOSIZIONE (vive): {len(base)} base · {len(gen)} generate.  "
          f"Nel registro intero: {base_tot} base su {len(pairs)}, tetto {tetto}.")
    if base_tot >= tetto * 0.8:
        print(f"  ATTENZIONE: le coppie base occupano quasi tutto il tetto. Non "
              f"vengono mai potate,\n  quindi lo spazio che resta alle generate — le "
              f"uniche che passano il gate — si\n  riduce a {max(0, tetto - base_tot)}.")
    falliti = Counter(int(r.get("fail_count", 0) or 0) for r in fresche.values()
                      if int(r.get("fail_count", 0) or 0) > 0)
    if falliti:
        print("  fallimenti accumulati: " +
              " · ".join(f"{n} fallimenti: {q}" for n, q in sorted(falliti.items())))
    print(f"  VALIDATE ora: {len(validated)} su {len(coins)} coin distinte")
    print(f"  ready dichiarato dal registro: {doc.get('ready')} "
          f"(via {doc.get('ready_by') or '—'})")
    # LA REGOLA COM'E' STATA APPLICATA, non com'e' scritta nei default. Il 16
    # settembre `ready` e' rimasto False con 31 coppie validate su 16 coin, e senza
    # questi due numeri non c'era modo di sapere se il problema fosse la soglia o il
    # fatto che l'optimizer non avesse letto la configurazione. Sono valori che
    # l'ultimo run ha SCRITTO nel registro: dicono cosa ha usato davvero.
    _cop = doc.get("coverage")
    print(f"     copertura {(_cop * 100 if isinstance(_cop, (int, float)) else 0):.1f}% "
          f"su obiettivo {float(doc.get('ready_fraction') or 0) * 100:.0f}% · "
          f"via a conteggio: {doc.get('ready_min_pairs') or 'spenta'} coppie "
          f"(0 = spenta) · minimi {doc.get('min_universe')} coin nell'universo, "
          f"{doc.get('min_covered')} coperte")
    # E I NUMERI SU CUI IL CALCOLO E' STATO FATTO. Non sono gli stessi che si leggono
    # qui sopra: `ready` lo decide la fase OPTIMIZE, e la discovery riscrive
    # `validated` e `coins_covered` DOPO senza ricalcolarlo. Senza questa riga, un
    # registro che mostra 31 validate e `ready: False` sembra una contraddizione.
    _in = doc.get("ready_inputs") or {}
    if _in:
        print(f"     deciso il {_when(float(_in.get('at', 0) or 0))} su "
              f"{_in.get('validated')} validate / {_in.get('covered')} coin coperte "
              f"/ universo {_in.get('universe')} · minimi ok: {_in.get('base_ok')} · "
              f"copertura ok: {_in.get('by_coverage')} · conteggio ok: "
              f"{_in.get('by_count')}")

    # --- LA FINESTRA E' APERTA? ---------------------------------------------- #
    # Il conto che mancava. Una coppia con un passaggio ma SENZA finestra non e' in
    # attesa: e' ferma. La finestra si apre solo quando `judge_window` viene chiamato
    # per quella coppia, e nella discovery questo succede soltanto se la coppia
    # ripassa il gate. Se la maggioranza delle coppie a un passaggio non ha una
    # finestra, il fronte che sembra "in maturazione" non sta maturando affatto — e
    # la distribuzione da sola non lo dice.
    con_pass = [r for r in fresche.values() if int(r.get("pass_count", 0) or 0) > 0]
    aperte = [r for r in con_pass if float(r.get("window_start", 0) or 0) > 0]
    if con_pass:
        print(f"  FINESTRE APERTE: {len(aperte)}/{len(con_pass)} coppie con almeno "
              f"un passaggio.\n"
              f"  E' QUESTO il numero da guardare: solo queste stanno contando i "
              f"giorni verso la\n  conferma successiva, e solo queste compaiono nel "
              f"calendario qui sotto.\n"
              f"  Le altre {len(con_pass) - len(aperte)} sono ferme: la finestra si "
              f"apre solo quando la coppia RIPASSA\n  il gate, quindi per loro la "
              f"prossima conferma non ha una data — dipende da un\n  evento che "
              f"potrebbe non succedere.")

    # --- CHI PUO' VALIDARSI OGGI --------------------------------------------- #
    # LA DOMANDA DEL PROPRIETARIO, il 14 settembre: «perche' devo aspettare il 21?
    # Non ci sono crypto che arrivano a 3 oggi, domani, dopodomani?».
    #
    # Se la risposta si legge contando a mano le righe del calendario qui sotto, si
    # legge male: quell'elenco e' troncato a `--top`, e dedurre una proporzione da un
    # elenco troncato e' gia' costato un falso allarme (11 settembre, ORCAUSDT).
    #
    # E soprattutto: una finestra SCADUTA non e' una scadenza mancata. `judge_window`
    # nella discovery si attiva solo sui passaggi, quindi chi non ripassa non prende
    # un fallimento: resta idoneo, e ha un tentativo nuovo ogni giorno, su un giorno
    # di dati in piu'. Il gruppo degli idonei si ACCUMULA, non si consuma.
    a_un_passo = [r for r in aperte
                  if int(r.get("pass_count", 0) or 0) == MIN_PASSES - 1]
    if a_un_passo:
        scaduta = [r for r in a_un_passo
                   if float(r.get("window_start", 0)) + NEW_DATA_MIN_S <= now]
        coin_pronte = {r.get("symbol") for r in scaduta}
        print(f"\n  A UN PASSO DALLA VALIDAZIONE: {len(a_un_passo)} coppie a "
              f"{MIN_PASSES - 1}/{MIN_PASSES}.")
        print(f"  Di queste, {len(scaduta)} su {len(coin_pronte)} coin hanno GIA' la "
              f"finestra scaduta: si\n  validano al primo run in cui ripassano il "
              f"gate, cioe' potenzialmente oggi.")
        prossime: Counter = Counter()
        for r in a_un_passo:
            fine = float(r.get("window_start", 0)) + NEW_DATA_MIN_S
            if fine > now:
                prossime[_when(fine)] += 1
        if prossime:
            print("  Le altre diventano idonee: " +
                  " · ".join(f"{q} il {g}" for g, q in sorted(prossime.items())))

    # --- QUANTO SPAZIO RESTA NEI DOCUMENTI ----------------------------------- #
    # Firestore rifiuta un documento oltre 1 MiB. Due documenti ci arrivano vicino, e
    # il modo in cui cedono e' diverso ma il risultato e' lo stesso: si smette di
    # accumulare senza che nessuno lo dica.
    #
    #  * `strategy_registry/validated` tiene i PASSAGGI, cioe' settimane di attesa.
    #    `slim_registry` toglie i campi descrittivi quando cresce, ma se non basta
    #    lascia che sia Firestore a rifiutare: quel run perde le conferme appena
    #    guadagnate.
    #  * `discovered_strategies/specs` tiene le spec. Se la scrittura fallisce, una
    #    coppia puo' entrare nel registro senza che la sua spec venga salvata: non
    #    sara' mai piu' ri-valutata, quindi restera' a una conferma per sempre.
    #
    # Un limite che nessuno guarda e' esattamente la forma di difetto che questo
    # sistema ha gia' pagato tre volte. Qui si guarda.
    for coll, campo, cosa in (("strategy_registry", "pairs", "registro"),
                              ("discovered_strategies", "specs", "spec scoperte")):
        try:
            d = fb.get_doc(coll, "validated" if campo == "pairs" else "specs") or {}
            n = len((d.get(campo) or "").encode("utf-8"))
        except Exception:                     # noqa: BLE001 - diagnostica, mai fatale
            continue
        if n:
            quota = 100 * n / LIMITE_DOC
            segno = "  ATTENZIONE:" if quota >= 80 else ""
            print(f"  spazio {cosa}: {n / 1024:.0f} KiB su {LIMITE_DOC / 1024:.0f} "
                  f"({quota:.0f}%){segno}")
            # QUANTO MANCA, in coppie e non in percentuale. Una percentuale dice
            # dove siamo, non quanto tempo resta: l'86% del 19 settembre erano tre
            # giorni, e nessuno lo aveva calcolato. Il costo per coppia e' anche
            # l'unica misura che dice se un alleggerimento ha davvero funzionato.
            if campo == "pairs" and len(pairs):
                per_coppia = n / len(pairs)
                capienza = int((LIMITE_DOC - n) / per_coppia) if per_coppia else 0
                print(f"    {per_coppia:.0f} byte a coppia · ci stanno ancora "
                      f"~{capienza} coppie oltre le {len(pairs)} di adesso")
            if quota >= 80:
                print(f"  oltre il limite Firestore rifiuta la scrittura e il run "
                      f"perde\n  le conferme appena guadagnate. Va alzato il tetto "
                      f"o alleggerito il documento.")

    # --- CHI VIENE ANCORA RI-VALUTATO ---------------------------------------- #
    # Il calendario qui sotto vale SOLO per le spec che la discovery ri-guarda: una
    # coppia generata prende la conferma successiva unicamente ripassando il gate, e
    # se la sua spec resta fuori dal taglio per i tempi non ripassera' mai. Sarebbe
    # una data stampata su una coppia ferma — la quarta volta, dopo il campo
    # sbagliato, le coin congelate e le coppie senza finestra.
    diag = fb.get_doc("strategy_params", "discovered_last_run") or {}
    # QUANTO DURA IL GIRO (discovery): scritto dalla discovery stessa alla fine.
    # E' il vincolo numero uno del sistema (finestra del timer: 3h) e prima si
    # ricavava a mano da tre comandi. Se `started_at` manca, il giro in corso o
    # l'ultimo finito girava col codice vecchio.
    if diag.get("started_at") and diag.get("duration_s") is not None:
        ini = datetime.fromtimestamp(float(diag["started_at"]), timezone.utc)
        d = int(diag["duration_s"])
        fine = datetime.fromtimestamp(float(diag["started_at"]) + d, timezone.utc)
        avviso = "  ← SFORA la finestra di 3h" if d > 3 * 3600 else ""
        print(f"\n  TEMPO DELL'ULTIMO GIRO (discovery): {d // 3600}h {(d % 3600) // 60:02d}m · "
              f"iniziato {ini:%d %b %H:%M} UTC · finito {fine:%H:%M} UTC{avviso}")
    else:
        print("\n  TEMPO DELL'ULTIMO GIRO: non ancora registrato (codice del 22 set: "
              "arriva col primo giro finito)")
    # la passata extra (strategie native a 1 ora, per ora solo BTC)
    d1h = fb.get_doc("strategy_params", "discovered_last_run_1h") or {}
    if d1h.get("started_at") and d1h.get("duration_s") is not None:
        d = int(d1h["duration_s"])
        print(f"  PASSATA A 1 ORA ({d1h.get('symbols', '?')} coin): {d // 60}m · "
              f"{d1h.get('n_eval', '?')} valutazioni · {d1h.get('n_passed', '?')} passate")
    if diag.get("n_specs_note"):
        tagliate = int(diag.get("n_specs_tagliate", 0) or 0)
        print(f"\n  RI-VALUTAZIONE (ultimo run discovery): "
              f"{diag.get('n_specs_rivalutate')} spec su {diag.get('n_specs_note')} "
              f"note · cap {diag.get('reeval_cap')} · "
              f"{diag.get('n_specs_con_conferme')} con almeno una conferma")
        if tagliate:
            print(f"  {tagliate} spec restano fuori dal taglio: sono ferme, non in "
                  f"attesa.\n  Quelle con conferme passano comunque, quindi il taglio "
                  f"tocca solo candidate a zero passaggi.")

    # --- il calendario ------------------------------------------------------ #
    etas = sorted((eta_ready(r, now), k) for k, r in fresche.items())
    finite = [(t, k) for t, k in etas if t != float("inf")]

    print(f"\n--- QUANDO ARRIVANO LE PROSSIME CONFERME (limite inferiore) ---")
    if not finite:
        print("  Nessuna coppia ha ancora una prima conferma: non c'e' una data da "
              "calcolare.\n  Serve che l'optimizer trovi coppie che passano il gate.")
    for t, k in finite[:args.top]:
        r = pairs[k]
        stato = "GIA' VALIDATA" if t <= 0 else f"validata il {_when(t)}"
        # SE LA FINESTRA NON C'E', NON SI STAMPA UNA DATA. Sommando la settimana a un
        # `window_start` assente usciva l'8 gennaio 1970, che in mezzo a date vere
        # sembra un dato e non lo e'. Le coppie senza finestra sono quelle generate
        # dalla discovery, che fino a poco fa non passava da judge_window: la finestra
        # si apre alla prima passata dopo l'unificazione della contabilita'.
        ws = float(r.get("window_start", 0) or 0)
        fin = (f"finestra chiusa il {_when(ws + NEW_DATA_MIN_S)}" if ws > 0
               else "finestra non ancora aperta")
        # `visto` = l'ultima volta che l'optimizer l'ha VALUTATA, che e' diverso da
        # `ultimo pass`. Le due date insieme distinguono i tre casi che finora
        # sembravano uguali: valutata e continua a passare, valutata e non passa
        # piu', non piu' valutata affatto.
        print(f"  {k:<34} {int(r.get('pass_count', 0) or 0)}/{MIN_PASSES} pass · "
              f"{stato} · ultimo pass "
              f"{_when(float(r.get('last_pass_data_end', 0) or 0))} · {fin}"
              f" · vista {_when(float(r.get('last_seen_at', 0) or 0))}"
              + (f" · {r.get('fail_count')} fallimenti di fila" if r.get("fail_count") else ""))

    # --- la data che interessa: quando riparte il bot ----------------------- #
    print(f"\n--- QUANDO RIPARTE IL BOT ---")
    if READY_MIN_PAIRS <= 0:
        print(f"  La via 'numero di coppie' e' DISATTIVATA (OPTIMIZER_READY_MIN_PAIRS=0):"
              f"\n  vale solo la copertura ({READY_FRACTION * 100:.0f}% dell'universo), che"
              f" con un gate severo\n  puo' non arrivare mai. Vedi docs/fase5_report.md.")
        return 0
    need = max(READY_MIN_PAIRS, MIN_COVERED)
    if len(finite) < READY_MIN_PAIRS:
        print(f"  Coppie con almeno una conferma: {len(finite)}. Ne servono "
              f"{READY_MIN_PAIRS}.\n  Finche' non ce ne sono abbastanza NON esiste una "
              f"data: prima devono passare\n  il gate, poi si conta il tempo.")
        return 0
    target = finite[READY_MIN_PAIRS - 1][0]
    giorni = (target - now) / 86400
    print(f"  Al piu' presto il {_when(target)} (fra {giorni:.1f} giorni), quando la "
          f"{READY_MIN_PAIRS}a coppia\n  raggiungerebbe {MIN_PASSES} pass.")
    print(f"  E' un LIMITE INFERIORE: assume che ognuna passi almeno una volta per"
          f"\n  finestra settimanale. Chi non passa per {PURGE_FAILS} finestre intere "
          f"esce dal registro,\n  quindi la data vera puo' essere piu' in la'. Serve anche coprire "
          f">= {MIN_COVERED} coin distinte ({need} coppie\n  su coin diverse bastano).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
