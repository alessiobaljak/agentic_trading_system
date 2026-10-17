"""
IL SELETTORE, PASSO 1 — «apri tutto» contro «selettore», offline, per famiglia.

A cosa serve: dare il verdetto del passo 1 del disegno (docs/disegno_cervello.md,
Punto 2): un modello addestrato sulle condizioni d'ingresso dei trade OOS del gate
batte o no il comportamento di oggi, che apre tutti i segnali validi? Il confronto
e' walk-forward (train prima del taglio, test dopo) e il metro e' (pnl - drawdown),
cosi' un selettore che si limita a togliere trade non vince per sottrazione.

Legge i file che il gate scrive in `data/selettore/` (o SELETTORE_DIR) dal 24 set
2026: se non ce ne sono ancora, lo dice e esce con 0 — non e' un errore, e' un
giro che deve ancora passare. Sola lettura sul disco; con Firebase raggiungibile
pubblica un riepilogo in `selector/report` (verdetti per famiglia), che e' quello
che il controllo del mattino leggera'.

IL BOT NON USA ANCORA IL SELETTORE PER DECIDERE. Questo script misura; il
verdetto e' «batte» solo su almeno 2 finestre su 3 — dove «batte» su una
finestra vuol dire sopra la baseline E sopra il 95° percentile di 200 selezioni
con le p rimescolate (`p_perm` stampato accanto: la frazione di rimescolamenti
che fanno almeno altrettanto; audit 24 set 2026).

DAL 25 SET 2026 PUBBLICA ANCHE IL MODELLO: `selector/current` su Firestore
(coefficienti, medie e scale come liste, soglia, verdetto, stato «ombra»),
addestrato su TUTTE le righe. Il bot lo rilegge ogni ora e, a ogni apertura,
annota la p del selettore sulla posizione e sul trade chiuso SENZA agire (passo 2
del disegno, l'ombra). Il verdetto oggi e' NON BATTE: l'ombra serve a misurare
sul paper, fra qualche settimana, se p predice l'esito — non a decidere.

Dal 24 set 2026 il dataset ha anche i trade delle spec BOCCIATE dal gate (campo
`passed`): si addestra su tutte, e per ogni finestra si stampano anche le due
righe «solo passate» e «solo bocciate», perche' quello che il bot aprirebbe sono
le prime.

Uso (sul VPS):
    .venv/bin/python -m scripts.selettore_report
    .venv/bin/python -m scripts.selettore_report --giorni 365
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone

from bot.learning import selettore as sel

#: quanti coefficienti stampare del modello «tutte» (sono 18 in tutto dal 24 set
#: 2026: si stampano tutti, ma il tetto resta scritto per quando cresceranno).
MAX_COEF = 20


def _num(x, dec=4) -> str:
    return "—" if x is None else f"{x:+.{dec}f}"


def _riga_finestra(f: dict) -> str:
    if f.get("insufficiente"):
        return (f"  finestra {f['finestra']}: train {f['train_n']} trade < minimo -> "
                f"campione insufficiente")
    b, z, s = f["baseline"], f.get("selezione") or f["selettore"], f["selettore"]
    p_perm, soglia_perm = f.get("p_perm"), f.get("soglia_perm")
    perm = ("" if p_perm is None else
            f", p_perm {p_perm:.3f}, 95° perc. {_num(soglia_perm)}")
    righe = [
        f"  finestra {f['finestra']} [{f['test_da']} -> {f['test_a']}] "
        f"train {f['train_n']:5d} | soglia {f['soglia']:.2f}",
        f"     apri tutto: n {b['n']:4d}  pnl {_num(b['pnl'])}  dd {b['dd']:.4f}  "
        f"wr {b['win_rate']:.1%}  metro {_num(b['metro'])}",
        f"     selezione : n {z['n']:4d}  pnl {_num(z['pnl'])}  dd {z['dd']:.4f}  "
        f"wr {z['win_rate']:.1%}  metro {_num(z['metro'])}  "
        f"-> {'BATTE' if f['batte'] else 'non batte'} (margine {_num(f['margine'])}{perm})",
        f"     con size  : n {s['n']:4d}  pnl {_num(s['pnl'])}  dd {s['dd']:.4f}  "
        f"metro {_num(s['metro'])}  (informativo: il verdetto e' sulla selezione)",
    ]
    # le due righe per `passed`: informative, il verdetto e' sull'insieme intero
    for etichetta, chiave in (("solo passate", "solo_passate"), ("solo bocciate", "solo_bocciate")):
        sub = f.get(chiave)
        if not sub:
            continue
        sb, sz = sub["baseline"], sub["selezione"]
        righe.append(f"     {etichetta:13s}: n {sub['n']:4d} | apri tutto pnl {_num(sb['pnl'])} "
                     f"metro {_num(sb['metro'])} | selezione n {sz['n']:4d} "
                     f"pnl {_num(sz['pnl'])} metro {_num(sz['metro'])}")
    return "\n".join(righe)


def stampa_famiglia(nome: str, wf: dict) -> None:
    print(f"\n[{nome}] {wf['n_righe']} trade usabili"
          + (f" ({wf['n_scartate']} scartati: variabili mancanti)" if wf["n_scartate"] else "")
          + (f", {wf['n_passate']} di spec passate e {wf['n_bocciate']} di bocciate"
             if wf.get("n_bocciate") else "")
          + (f", dal {wf['da']} al {wf['a']}" if wf["da"] else ""))
    for f in wf["finestre"]:
        print(_riga_finestra(f))
    print(f"  VERDETTO: {wf['verdetto'].upper()} ({wf['vittorie']}/{wf['n_finestre']} finestre; "
          f"«batte» = sopra la baseline e sopra il 95° percentile di "
          f"{wf.get('n_permutazioni', sel.N_PERMUTAZIONI)} permutazioni)")


def stampa_coefficienti(modello: dict | None) -> None:
    if not modello:
        print("\n[modello «tutte»] non addestrato: troppe poche righe.")
        return
    print(f"\n[modello «tutte»] n {modello['n']}, lam {modello['lam']}, "
          f"intercetta {modello['intercetta']:+.3f} — coefficienti su variabili "
          f"standardizzate, in ordine di modulo:")
    coppie = sorted(zip(modello["variabili"], modello["coef"]),
                    key=lambda kv: -abs(kv[1]))
    for nome, c in coppie[:MAX_COEF]:
        print(f"    {nome:10s} {c:+.3f}")
    print("  (segno +: quando la variabile sale, sale la probabilita' di chiudere in utile)")


def pubblica(report: dict, n_righe: int) -> None:
    """`selector/report` su Firestore, solo se Firebase e' davvero connesso. Senza
    (in locale, nei test) si stampa e basta: il report e' gia' tutto a schermo."""
    try:
        from bot.core.firebase_client import get_firebase
        fb = get_firebase()
        if not fb.is_live:
            print("\n[firebase] non connesso: report solo a schermo.")
            return
        doc = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "n_righe": int(n_righe),
            "verdetti": {fam: {"verdetto": wf["verdetto"], "vittorie": wf["vittorie"],
                               "n_finestre": wf["n_finestre"], "n_righe": wf["n_righe"],
                               "soglia_consigliata": wf["soglia_consigliata"]}
                         for fam, wf in report.items()},
            "nota": "il bot NON usa il selettore per decidere: in ombra dal 25 set 2026 (selector/current)",
        }
        fb.set_doc("selector", "report", doc)
        print("\n[firebase] pubblicato selector/report.")
    except Exception as exc:  # noqa: BLE001 — la pubblicazione non deve mai rompere il report
        print(f"\n[firebase] pubblicazione saltata ({exc}).")


def _mediana(valori: list[float]) -> float | None:
    v = sorted(float(x) for x in valori)
    if not v:
        return None
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0


def documento_modello(righe: list[dict], report: dict) -> dict | None:
    """Il documento `selector/current` (25 set 2026, passo 2: l'ombra nel bot).

    Il modello e' addestrato su TUTTE le righe (`addestra`, famiglia «tutte»),
    non su una finestra: e' il modello piu' informato che abbiamo, ed e' quello
    che il bot deve leggere. La soglia e' la MEDIANA delle soglie scelte sul
    train nelle finestre del walk-forward «tutte» (0.5 se non ce ne sono): non
    decide nulla, serve solo al log «avrebbe aperto / NON avrebbe aperto».
    Tutto JSON-safe (liste e float di Python, niente numpy), cosi' Firestore lo
    accetta e `prob(modello, riga)` lo rilegge tale e quale (round trip).
    None se le righe sono troppo poche per avere coefficienti sensati (stesso
    minimo di `walk_forward`)."""
    if len(righe) < max(len(sel.VARIABILI) + 1, 20):
        return None
    modello = sel.addestra(righe, famiglia="tutte")
    wf = report.get("tutte") or {}
    soglie = [f["soglia"] for f in wf.get("finestre", []) if f.get("soglia") is not None]
    soglia = _mediana(soglie) if soglie else None
    if soglia is None:
        soglia = float(wf.get("soglia_consigliata") or sel.SOGLIA_DEFAULT)
    doc = {
        "modello": modello,
        "soglia": float(soglia),
        "famiglia": "tutte",
        "righe": int(len(righe)),
        "verdetto": str(wf.get("verdetto") or sel.INSUFFICIENTE).upper(),
        "vittorie": int(wf.get("vittorie") or 0),
        "n_finestre": int(wf.get("n_finestre") or 0),
        "stato": "ombra",
        "generato_at": datetime.now(timezone.utc).isoformat(),
        "nota": ("il bot annota p su ogni apertura e NON agisce (passo 2, ombra); "
                 "entra solo se batte su 2/3 finestre e la calibrazione sul paper "
                 "non e' piatta (>= 40 trade con p)"),
    }
    # il round trip via json e' la garanzia: se qui passa, Firestore lo accetta e
    # il bot lo rilegge identico (un NaN o un tipo numpy fallirebbero QUI, non
    # sulla macchina alle tre di notte)
    return json.loads(json.dumps(doc, allow_nan=False))


def pubblica_modello(doc: dict | None, fb=None) -> bool:
    """`selector/current` su Firestore. Fail-open come `pubblica`: senza Firebase
    (in locale, nei test, o dal canale ops senza credenziali) si stampa e si va
    avanti — il report a schermo e' gia' completo. Ritorna True solo se ha
    scritto davvero."""
    if not doc:
        print("\n[firebase] selector/current NON pubblicato: troppe poche righe per un modello.")
        return False
    try:
        if fb is None:
            from bot.core.firebase_client import get_firebase
            fb = get_firebase()
        if not fb.is_live:
            print("\n[firebase] non connesso: selector/current solo a schermo "
                  f"(righe {doc['righe']}, soglia {doc['soglia']:.2f}, verdetto {doc['verdetto']}).")
            return False
        fb.set_doc("selector", "current", doc)
        print(f"\n[firebase] pubblicato selector/current: modello su {doc['righe']} righe, "
              f"soglia {doc['soglia']:.2f}, verdetto {doc['verdetto']}, stato {doc['stato']}.")
        return True
    except Exception as exc:  # noqa: BLE001 — mai rompere il report per la pubblicazione
        print(f"\n[firebase] pubblicazione di selector/current saltata ({exc}).")
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="apri tutto contro selettore, offline")
    ap.add_argument("--giorni", type=int, default=None,
                    help="usa solo i trade entrati negli ultimi N giorni (rispetto al piu' recente)")
    ap.add_argument("--cartella", default=None,
                    help=f"cartella del dataset (default: SELETTORE_DIR = {sel.SELETTORE_DIR})")
    ap.add_argument("--min-train", type=int, default=500,
                    help="trade minimi nel train di ogni finestra (default 500, dal disegno)")
    args = ap.parse_args(argv)

    t0 = time.time()
    cartella = args.cartella or sel.SELETTORE_DIR
    righe = sel.carica_righe(cartella, giorni=args.giorni)
    letto = sel.ULTIMA_LETTURA
    if not righe:
        print("nessun dataset: il gate lo scrive dal 24 set a ogni giro"
              f" (cartella: {cartella}, file trovati: {letto['file']})")
        print("Il bot NON usa ancora il selettore per decidere: senza dataset non c'e' nemmeno l'ombra.")
        return 0

    coppie = {(r.get("symbol"), r.get("strategy")) for r in righe}
    famiglie: dict[str, int] = {}
    for r in righe:
        famiglie[str(r.get("famiglia") or "altro")] = famiglie.get(str(r.get("famiglia") or "altro"), 0) + 1
    print(f"[selettore] {len(righe)} trade da {letto['file']} file "
          f"({letto['duplicate']} duplicati fusi, {letto.get('gemelle_fuse', 0)} gemelle fuse, "
          f"{letto['scartate']} righe rotte saltate)"
          + (f", ultimi {args.giorni} giorni" if args.giorni else ""))
    print(f"[selettore] {len(coppie)} coppie coin+strategia; famiglie: "
          + ", ".join(f"{k} {v}" for k, v in sorted(famiglie.items(), key=lambda kv: -kv[1])))
    print(f"[selettore] minimo train per finestra: {args.min_train}; "
          f"soglie candidate: {', '.join(f'{s:.2f}' for s in sel.SOGLIE)}")

    report = sel.report_per_famiglia(righe, min_train=args.min_train)
    for nome in ["tutte"] + [f for f in sel.FAMIGLIE if f in report]:
        stampa_famiglia(nome, report[nome])
    stampa_coefficienti(report["tutte"].get("modello"))

    print("\nIl bot NON usa ancora il selettore per decidere: dal 25 set 2026 e' in OMBRA "
          "(passo 2): annota la sua p su ogni apertura e non agisce. Entra solo se batte "
          "su 2/3 finestre e la calibrazione sul paper non e' piatta (>= 40 trade con p).")
    pubblica(report, len(righe))
    pubblica_modello(documento_modello(righe, report))
    print(f"[selettore] fatto in {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
