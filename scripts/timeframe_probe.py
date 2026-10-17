"""LE MONETE CHE A 15 MINUTI NON COPRIAMO: A UN'ALTRA SCALA SI COPRONO?

Domanda del proprietario, 15 settembre: «se vediamo che ci sono monete non copribili
a 15 min, magari dobbiamo passare a 1 ora o 5 min».

L'idea e' giusta — ogni mercato ha una sua scala caratteristica, e una regolarita'
invisibile a 15 minuti puo' esistere a un'ora. Ma prima di cambiare il motore c'e'
da rispondere a una domanda che costa un giro e non rischia niente: **a quelle
scale, su quelle monete, c'e' davvero qualcosa?**

PERCHE' SERVE UN GRUPPO DI CONTROLLO, ed e' la parte che rende questa misura
diversa da un'impressione. Se a 1 ora passano piu' candidate, ci sono due
spiegazioni opposte:

  * «quelle monete hanno una regolarita' a 1 ora» — la tesi da verificare;
  * «a 1 ora il gate e' piu' facile da passare per tutti» — per esempio perche' i
    costi pesano meno su trade piu' lunghi, o perche' con meno barre la statistica
    e' piu' rumorosa e il rumore passa piu' spesso.

La seconda spiegazione non c'entra niente con le monete, e prenderla per la prima
vorrebbe dire riscrivere il sistema per inseguire un artefatto. Per separarle si
misurano NELLO STESSO RUN due gruppi: le monete scoperte e quelle gia' coperte. Se
il guadagno e' solo sulle scoperte, e' un fatto sulle monete. Se e' su entrambe, e'
un fatto sul timeframe — e va trattato come un allentamento del gate, non come una
scoperta.

IL PREZZO STATISTICO, da mettere in conto prima e non dopo. Provare tre timeframi
TRIPLICA i biglietti della lotteria: a parita' di tutto, le coppie che passano per
puro caso triplicano. Il budget di falsi positivi attuale ha circa 10x di margine
(vedi docs/andremo_live.md), quindi tre scale ci stanno — ma il margine scende a 3x,
e va detto invece che scoperto dopo.

QUESTO SCRIPT NON SCRIVE NIENTE. Non tocca il registro, non tocca le spec, non
cambia `ORCHESTRATOR_TIMEFRAME`. Legge, misura, stampa. Una coppia validata a 1 ora
che finisse nel registro verrebbe operata dal bot a 15 minuti — cioe' la divergenza
fra gate e vissuto che e' gia' costata BIRBUSDT, ma per costruzione invece che per
sfortuna.

Gira senza argomenti: il canale ops puo' solo NOMINARE una voce della lista bianca,
mai comporre un comando.
"""
from __future__ import annotations

import argparse
import os
import time
from datetime import date

from backtesting.data_loader import load_candles
from backtesting.optimizer import WalkForwardOptimizer
from backtesting.parallel import n_workers, parallel_map
from bot.core.firebase_client import decode_pairs, get_firebase
from bot.core.indicators import compute_indicator_frame
from bot.strategies.generator import generate_specs
from scripts.discover_strategies import evaluate_spec
from scripts.optimize import MIN_PASSES, _min_history, top_symbols_by_volume

#: Le scale da confrontare, DALLA PIU' ECONOMICA ALLA PIU' CARA. Non e' pignoleria:
#: il canale ops taglia a 900 secondi, e a 5 minuti la serie ha dodici volte le
#: candele di un'ora — per giunta non e' in cache, perche' il sistema gira a 15m.
#: Con l'ordine sbagliato il primo tentativo ha consumato tutto il tempo sui dati a
#: 5 minuti e non ha risposto a NIENTE. Cosi' invece, se il tempo finisce, si perde
#: solo l'ultima scala e le altre sono gia' state stampate.
#: 15m e' quella attuale e fa da riferimento: senza, un conteggio a 1 ora non si sa
#: se sia alto o basso.
TIMEFRAMES = ("1h", "15m", "5m")

#: Quanto tempo la sonda si concede prima di fermarsi DA SOLA e stampare cio' che ha.
#: Il canale ops uccide a 900s e restituisce l'output parziale: ma l'output parziale
#: di un processo Python ucciso e' VUOTO, perche' stdout su pipe e' bufferizzato a
#: blocchi. Il primo tentativo e' finito cosi': codice 124, zero righe, e nessuna
#: informazione su quanto fosse arrivata lontano. Un comando che gira dietro una
#: ghigliottina deve avere una deadline propria, piu' corta di quella.
BUDGET_S = float(os.getenv("PROBE_BUDGET_S", "780"))

#: Quante monete per gruppo. Piccolo di proposito: questa e' una SONDA, deve stare
#: nei 15 minuti di timeout del canale ops. Se dice che c'e' qualcosa, la misura
#: seria si fa dopo e in grande.
N_SCOPERTE = 6
N_CONTROLLO = 3

#: Candidate generate per timeframe. Le STESSE su tutti e tre (stesso seme), perche'
#: confrontare insiemi di strategie diversi non direbbe niente sul timeframe.
N_SPEC = 20
SEED = 4242

#: Finestra dati comune a tutte le scale. Non si parte dal 2022: a 5 minuti sarebbero
#: ~420.000 candele per moneta, cioe' un download e una cache che da soli sforano il
#: tempo a disposizione.
START = "2024-01-01"

_W: dict = {}


def di(msg: str = "") -> None:
    """Stampa SUBITO. Senza flush, stdout su pipe accumula a blocchi e un processo
    ucciso dal timeout non lascia una riga: e' esattamente com'e' andata la prima
    volta."""
    print(msg, flush=True)


def _statistiche(pf: list[float], passate: int, quasi: int) -> dict:
    """Riassume una casella (scala x gruppo) con numeri che ESISTONO sempre.

    `pf_mediano` e `quota_pf1` (quante candidate battono il pareggio) si muovono
    anche quando i passaggi sono zero — ed e' il caso normale, non l'eccezione.
    """
    ordinati = sorted(pf)
    n = len(ordinati)
    mediana = ordinati[n // 2] if n else 0.0
    return {"n": n, "pf_mediano": mediana,
            "quota_pf1": (sum(1 for v in ordinati if v >= 1.0) / n) if n else 0.0,
            "passate": passate, "quasi": quasi}


def _init(interval: str, specs: list, end: str) -> None:
    _W.update(opt=WalkForwardOptimizer(n_windows=3, interval=interval),
              interval=interval, specs=specs, end=end,
              min_history=_min_history(interval))


def _una(sym: str) -> tuple[str, list, int, int]:
    """(simbolo, profit factor di ogni candidata, passate, quasi-passaggi).

    SI RIPORTA LA DISTRIBUZIONE, non solo il conteggio dei passaggi, ed e' la
    correzione che rende questa sonda capace di rispondere.

    Il primo giro utile ha dato 0 passaggi su TUTTE e tre le scale e su TUTTI e due i
    gruppi. Non era una risposta: era un esperimento senza potenza. Il gate ha un
    tasso di passaggio misurato dello 0,19%, cioe' circa una candidata su 500; con
    180 valutazioni per casella ci si aspettano 0,3 passaggi. Zero ovunque e'
    l'esito piu' probabile anche se una scala fosse nettamente migliore — e leggerlo
    come «cambiare timeframe non serve» sarebbe una conclusione tratta dal nulla.

    Il profit factor invece c'e' per OGNI candidata, sempre. Se a un'ora le
    strategie su quelle monete vanno davvero meglio, la distribuzione si sposta, e
    con 120 misure lo si vede. E' la differenza fra contare i terni al lotto e
    guardare la media delle estrazioni.
    """
    try:
        candles = load_candles(sym, _W["interval"], START, _W["end"], prefer="binance")
    except Exception as exc:  # noqa: BLE001 - una moneta che non scarica non ferma la sonda
        print(f"  [{_W['interval']}] {sym}: dati non disponibili ({exc})")
        return (sym, [], 0, 0)
    if len(candles) < _W["min_history"]:
        # NON e' un fallimento della scala: e' storia insufficiente. Contarlo come
        # "zero passaggi" direbbe che a quella scala la moneta non funziona, che e'
        # un'altra affermazione.
        di(f"  [{_W['interval']}] {sym}: storia insufficiente "
           f"({len(candles)} candele su {_W['min_history']}), esclusa")
        return (sym, [], 0, 0)
    frame = compute_indicator_frame(candles)
    pf: list[float] = []
    passate = quasi = 0
    for spec in _W["specs"]:
        r = evaluate_spec(_W["opt"], sym, candles, frame, spec)
        pf.append(float(r.get("pf") or 0.0))
        if r["passed"]:
            passate += 1
        elif r.get("near_miss"):
            quasi += 1
    return (sym, pf, passate, quasi)


def scegli_monete(fb, n_scoperte: int, n_controllo: int) -> tuple[list[str], list[str]]:
    """Le monete scoperte da sondare, e quelle coperte che fanno da controllo.

    «Coperta» = ha almeno una coppia VALIDATA. E' la definizione che conta per
    «quante monete il bot potrebbe operare»: una a due conferme non e' operabile.
    """
    doc = fb.get_doc("strategy_registry", "validated") or {}
    pairs = decode_pairs(doc.get("pairs"))
    coperte = {r.get("symbol") for r in pairs.values()
               if int(r.get("pass_count", 0) or 0) >= MIN_PASSES and r.get("symbol")}
    universo = top_symbols_by_volume(120)
    controllo = [s for s in universo if s in coperte][:n_controllo]
    if not controllo:
        # Senza monete coperte nell'universo il controllo non esiste. Si ripiega
        # sulle piu' avanti (almeno MIN_PASSES-1 conferme): non e' lo stesso gruppo,
        # e il rapporto lo dice.
        quasi = {r.get("symbol") for r in pairs.values()
                 if int(r.get("pass_count", 0) or 0) >= MIN_PASSES - 1 and r.get("symbol")}
        controllo = [s for s in universo if s in quasi][:n_controllo]
    # I DUE GRUPPI NON SI DEVONO SOVRAPPORRE. Al primo giro XRPUSDT e' finita in
    # ENTRAMBI: «scoperte» escludeva solo le coin VALIDATE, e il controllo di
    # ripiego prende quelle a MIN_PASSES-1, che validate non sono. Un controllo che
    # contiene le stesse monete del gruppo misurato non controlla niente — e' il
    # difetto che rende un esperimento inutile senza che nessun numero lo dica.
    esclusi = coperte | set(controllo)
    scoperte = [s for s in universo if s not in esclusi][:n_scoperte]
    return scoperte, controllo


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scoperte", type=int, default=N_SCOPERTE)
    ap.add_argument("--controllo", type=int, default=N_CONTROLLO)
    ap.add_argument("--spec", type=int, default=N_SPEC)
    ap.add_argument("--timeframes", default=",".join(TIMEFRAMES))
    ap.add_argument("--budget", type=float, default=BUDGET_S,
                    help="secondi che la sonda si concede prima di fermarsi da sola")
    args = ap.parse_args()

    fb = get_firebase()
    scoperte, controllo = scegli_monete(fb, args.scoperte, args.controllo)
    if not scoperte:
        di("[probe] nessuna moneta scoperta nell'universo: niente da sondare.")
        return 1
    # LE STESSE candidate su tutte le scale: e' il timeframe la variabile, non le
    # strategie. Con insiemi diversi il confronto non direbbe niente.
    specs = generate_specs(args.spec, seed=SEED)
    end = date.today().isoformat()
    tfs = [t.strip() for t in args.timeframes.split(",") if t.strip()]

    di(f"[probe] {len(specs)} candidate (seme {SEED}) x "
       f"{len(scoperte)} monete scoperte + {len(controllo)} di controllo "
       f"x {len(tfs)} scale · dati da {START} · budget {args.budget:.0f}s")
    di(f"[probe] scoperte:  {', '.join(scoperte)}")
    di(f"[probe] controllo: {', '.join(controllo) or '— (nessuna coperta)'}")
    di()

    t_inizio = time.time()
    risultati: dict[str, dict[str, tuple[int, int, int]]] = {}
    saltate: list[str] = []
    for tf in tfs:
        # DEADLINE PROPRIA. Il canale ops uccide a 900s e l'output di un processo
        # ucciso e' vuoto: meglio fermarsi prima e stampare cio' che si e' misurato.
        restante = args.budget - (time.time() - t_inizio)
        if restante < 90:
            saltate.append(tf)
            di(f"[probe] {tf} SALTATA: restano {restante:.0f}s, non bastano. "
               f"Meglio un risultato parziale che nessuno.")
            continue
        t0 = time.time()
        gruppi: dict[str, tuple[int, int, int]] = {}
        for nome, monete in (("scoperte", scoperte), ("controllo", controllo)):
            if not monete:
                continue
            pf: list[float] = []
            p = q = 0
            for _sym, npf, np_, nq in parallel_map(
                _una, monete, workers=n_workers(),
                initializer=_init, initargs=(tf, specs, end),
            ):
                pf.extend(npf)
                p, q = p + np_, q + nq
            gruppi[nome] = _statistiche(pf, p, q)
            st = gruppi[nome]
            # SUBITO, non alla fine: se il tempo scade, questa riga c'e' gia'.
            di(f"[probe] {tf:>4} {nome:<10} {st['n']:>4} valutate · PF mediano "
               f"{st['pf_mediano']:.3f} · sopra il pareggio {st['quota_pf1'] * 100:.0f}% "
               f"· {p} passate, {q} quasi")
        risultati[tf] = gruppi
        di(f"[probe] {tf} finito in {time.time() - t0:.0f}s")

    di("\n--- COM'E' ANDATA, PER SCALA E PER GRUPPO ---")
    di(f"{'scala':<7} {'gruppo':<11} {'valutate':>9} {'PF mediano':>11} "
       f"{'sopra 1':>8} {'passate':>8} {'quasi':>6}")
    for tf in tfs:
        for nome, st in risultati.get(tf, {}).items():
            di(f"{tf:<7} {nome:<11} {st['n']:>9} {st['pf_mediano']:>11.3f} "
               f"{st['quota_pf1'] * 100:>7.0f}% {st['passate']:>8} {st['quasi']:>6}")
    if saltate:
        di(f"\nNON MISURATE per mancanza di tempo: {', '.join(saltate)}. "
           f"Rilanciare la voce\nripartendo da queste (le altre sono gia' risposte).")

    # --- LA LETTURA, che e' la parte che serve ------------------------------- #
    rif = risultati.get("15m")
    if not rif:
        di("\nSenza la misura a 15m non c'e' un riferimento: un tasso da solo non\n"
           "dice se sia alto o basso. Niente conclusioni da questo giro.")
        return 0
    di("\n--- COME SI LEGGE ---")
    di("Si guarda il PF MEDIANO, non i passaggi: col tasso di passaggio misurato\n"
       "(0,19%) una casella da ~120 valutazioni produce zero passaggi anche se una\n"
       "scala fosse nettamente migliore. Zero non sarebbe una risposta.")
    for tf in tfs:
        if tf == "15m" or tf not in risultati:
            continue
        sco = risultati[tf].get("scoperte", {})
        ctl = risultati[tf].get("controllo", {})
        sco0 = rif.get("scoperte", {})
        ctl0 = rif.get("controllo", {})
        if not (sco and sco0):
            continue
        d_sco = sco["pf_mediano"] - sco0["pf_mediano"]
        d_ctl = (ctl.get("pf_mediano", 0) - ctl0.get("pf_mediano", 0)) if (ctl and ctl0) else 0.0
        di(f"\n{tf} contro 15m (PF mediano):")
        di(f"  monete scoperte : {d_sco:+.3f}")
        di(f"  controllo       : {d_ctl:+.3f}")
        if d_sco <= 0.01:
            di("  -> a questa scala le strategie NON vanno meglio dove non copriamo:\n"
               "     cambiare timeframe non e' la risposta per queste monete.")
        elif d_ctl >= d_sco * 0.7:
            di("  -> vanno meglio OVUNQUE, non solo dove non copriamo. E' un fatto\n"
               "     sulla scala (costi, rumore), non sulle monete: trattarlo come una\n"
               "     scoperta vorrebbe dire allentare il gate senza dirlo.")
        else:
            di("  -> vanno meglio SOLO dove non copriamo, e non nel controllo. E' il\n"
               "     segnale che queste monete hanno una scala loro, e vale la pena\n"
               "     pagare il costo di portare il timeframe dentro la coppia.")

    di("\nNOTA SUL PREZZO. Tre scale triplicano le estrazioni: a parita' di tutto,\n"
       "anche le coppie che passano per CASO triplicano. Il margine sul budget di\n"
       "falsi positivi scende da ~10x a ~3x. Resta accettabile, ma va contato.")
    di("\nQuesta sonda non ha scritto niente: ne' registro, ne' spec, ne' "
       "configurazione.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
