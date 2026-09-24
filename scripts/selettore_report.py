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

IL BOT NON USA ANCORA IL SELETTORE. Questo script misura e basta: il passo 2 (ombra
nel bot, con calibrazione sul paper) viene dopo, e solo se qui il verdetto e'
«batte» su almeno 2 finestre su 3 — dove «batte» su una finestra vuol dire
sopra la baseline E sopra il 95° percentile di 200 selezioni con le p
rimescolate (`p_perm` stampato accanto: la frazione di rimescolamenti che fanno
almeno altrettanto; audit 24 set 2026).

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
            "nota": "il bot NON usa il selettore: passo 1 (misura offline)",
        }
        fb.set_doc("selector", "report", doc)
        print("\n[firebase] pubblicato selector/report.")
    except Exception as exc:  # noqa: BLE001 — la pubblicazione non deve mai rompere il report
        print(f"\n[firebase] pubblicazione saltata ({exc}).")


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
        print("Il bot NON usa ancora il selettore: questo e' il passo 1, solo misura.")
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

    print("\nIl bot NON usa ancora il selettore: questo e' il passo 1 (misura offline); "
          "il passo 2 (ombra nel bot) viene dopo, e solo con verdetto «batte».")
    pubblica(report, len(righe))
    print(f"[selettore] fatto in {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
