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


def _init(interval: str, specs: list, end: str) -> None:
    _W.update(opt=WalkForwardOptimizer(n_windows=3, interval=interval),
              interval=interval, specs=specs, end=end,
              min_history=_min_history(interval))


def _una(sym: str) -> tuple[str, int, int, int]:
    """(simbolo, valutate, passate, quasi-passaggi) per una moneta a un timeframe."""
    try:
        candles = load_candles(sym, _W["interval"], START, _W["end"], prefer="binance")
    except Exception as exc:  # noqa: BLE001 - una moneta che non scarica non ferma la sonda
        print(f"  [{_W['interval']}] {sym}: dati non disponibili ({exc})")
        return (sym, 0, 0, 0)
    if len(candles) < _W["min_history"]:
        # NON e' un fallimento della scala: e' storia insufficiente. Contarlo come
        # "zero passaggi" direbbe che a quella scala la moneta non funziona, che e'
        # un'altra affermazione.
        di(f"  [{_W['interval']}] {sym}: storia insufficiente "
           f"({len(candles)} candele su {_W['min_history']}), esclusa")
        return (sym, 0, 0, 0)
    frame = compute_indicator_frame(candles)
    valutate = passate = quasi = 0
    for spec in _W["specs"]:
        r = evaluate_spec(_W["opt"], sym, candles, frame, spec)
        valutate += 1
        if r["passed"]:
            passate += 1
        elif r.get("near_miss"):
            quasi += 1
    return (sym, valutate, passate, quasi)


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
    scoperte = [s for s in universo if s not in coperte][:n_scoperte]
    controllo = [s for s in universo if s in coperte][:n_controllo]
    if not controllo:
        # Senza monete coperte il controllo non esiste. Si prendono le piu' avanti
        # (almeno una conferma): non e' lo stesso gruppo, e il rapporto lo dice.
        quasi = {r.get("symbol") for r in pairs.values()
                 if int(r.get("pass_count", 0) or 0) >= MIN_PASSES - 1 and r.get("symbol")}
        controllo = [s for s in universo if s in quasi][:n_controllo]
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
            v = p = q = 0
            for _sym, nv, np_, nq in parallel_map(
                _una, monete, workers=n_workers(),
                initializer=_init, initargs=(tf, specs, end),
            ):
                v, p, q = v + nv, p + np_, q + nq
            gruppi[nome] = (v, p, q)
            tasso = f"{100 * p / v:.2f}%" if v else "—"
            # SUBITO, non alla fine: se il tempo scade, questa riga c'e' gia'.
            di(f"[probe] {tf:>4} {nome:<10} {v:>5} valutate · {p:>3} passate "
               f"({tasso}) · {q} quasi")
        risultati[tf] = gruppi
        di(f"[probe] {tf} finito in {time.time() - t0:.0f}s")

    di("\n--- QUANTO PASSA, PER SCALA E PER GRUPPO ---")
    di(f"{'scala':<7} {'gruppo':<11} {'valutate':>9} {'passate':>8} "
       f"{'tasso':>8} {'quasi':>7}")
    for tf in tfs:
        for nome, (v, p, q) in risultati.get(tf, {}).items():
            tasso = f"{100 * p / v:.2f}%" if v else "—"
            di(f"{tf:<7} {nome:<11} {v:>9} {p:>8} {tasso:>8} {q:>7}")
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
    for tf in tfs:
        if tf == "15m" or tf not in risultati:
            continue
        sco = risultati[tf].get("scoperte", (0, 0, 0))
        ctl = risultati[tf].get("controllo", (0, 0, 0))
        sco0 = rif.get("scoperte", (0, 0, 0))
        ctl0 = rif.get("controllo", (0, 0, 0))
        d_sco = (sco[1] / sco[0] if sco[0] else 0) - (sco0[1] / sco0[0] if sco0[0] else 0)
        d_ctl = (ctl[1] / ctl[0] if ctl[0] else 0) - (ctl0[1] / ctl0[0] if ctl0[0] else 0)
        di(f"\n{tf} contro 15m:")
        di(f"  monete scoperte : {d_sco * 100:+.2f} punti di tasso")
        di(f"  controllo       : {d_ctl * 100:+.2f} punti di tasso")
        if d_sco <= 0:
            di("  -> a questa scala NON passa di piu' dove non copriamo: cambiare\n"
               "     timeframe non e' la risposta per queste monete.")
        elif d_ctl >= d_sco * 0.7:
            di("  -> passa di piu' OVUNQUE, non solo dove non copriamo. E' un fatto\n"
               "     sul timeframe (costi, rumore), non sulle monete: trattarlo come\n"
               "     una scoperta vorrebbe dire allentare il gate senza dirlo.")
        else:
            di("  -> passa di piu' SOLO dove non copriamo, e non nel controllo.\n"
               "     E' il segnale che queste monete hanno una scala loro. Vale la\n"
               "     pena pagare il costo di portare il timeframe dentro la coppia.")

    di("\nNOTA SUL PREZZO. Tre scale triplicano le estrazioni: a parita' di tutto,\n"
       "anche le coppie che passano per CASO triplicano. Il margine sul budget di\n"
       "falsi positivi scende da ~10x a ~3x. Resta accettabile, ma va contato.")
    di("\nQuesta sonda non ha scritto niente: ne' registro, ne' spec, ne' "
       "configurazione.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
