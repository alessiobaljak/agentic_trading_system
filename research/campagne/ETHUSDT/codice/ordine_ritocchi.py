"""L'ordine dei ritocchi della regola 6, letto dal log.

Entrano le varianti testate (idee e ritocchi) che:
* sono valutabili contro la (a) e contro la (b);
* NON hanno gia' battuto nettamente sia la (a) sia la (b);
* hanno una famiglia con meno di 5 ritocchi (gli scarti contano fra i ritocchi).
Ordine: t contro la (b) dal piu' alto; a parita' vale la variante registrata prima.
Stampa anche il conto del budget (varianti testate, ritocchi, famiglie).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import registro  # noqa: E402

RITOCCHI_MASSIMI = 5


def main() -> None:
    voci = registro.voci()
    reg = {v["id"]: v for v in voci if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante"}
    ris = {v["id"]: v for v in voci if v["tipo"] == "risultato" and v["id"] in reg}
    ritocchi_per_famiglia = {}
    for v in voci:
        if v["tipo"] in ("registrazione", "scarto") and v.get("ritocco_di"):
            ritocchi_per_famiglia[v["famiglia"]] = ritocchi_per_famiglia.get(v["famiglia"], 0) + 1
    lista = []
    for ident, r in ris.items():
        a, b = r.get("baseline_a") or {}, r.get("baseline_b") or {}
        if not (a.get("valutabile") and b.get("valutabile")):
            continue
        if a.get("netta") and b.get("netta"):
            continue
        fam = reg[ident]["famiglia"]
        if ritocchi_per_famiglia.get(fam, 0) >= RITOCCHI_MASSIMI:
            continue
        lista.append((-float(b["t"]), reg[ident]["variante_n"], ident, reg[ident].get("variante_ipotesi"), float(b["t"]), fam))
    lista.sort()
    print(f"varianti testate: {len(ris)}; ritocchi: {sum(1 for i in reg if reg[i].get('ritocco_di'))}; "
          f"famiglie: {len({reg[i]['famiglia'] for i in reg})}")
    for _, n, ident, nome, t, fam in lista:
        print(f"  {ident} ({nome}, variante_n {n}, famiglia {fam}): t contro la (b) {t:.3f}")


if __name__ == "__main__":
    main()
