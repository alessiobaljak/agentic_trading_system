"""Il registro delle prove (`research/REGISTRO.md`, 181 KB) interrogato senza leggerlo tutto: quante prove, il conto delle prove,
le ultime prove, le idee ancora in coda. Serve alla sessione principale e agli agenti (`.claude/agents/`), che non devono leggere il
registro per intero (regole dei token in `CLAUDE.md`).

Uso:
  python3 -m research.src.registro --riepilogo        al massimo 20 righe
  python3 -m research.src.registro --prova 148        la riga di una prova, intera
  python3 -m research.src.registro --cerca G1N        le righe che contengono il testo (accorciate)
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REGISTRO = Path(__file__).resolve().parents[1] / "REGISTRO.md"
_RIGA = re.compile(r"^\|\s*(\d+)\s*\|(.*)$")
_CONTO = re.compile(r"Totale nel conto:.*?=\s*\*\*(\d+)\*\*")
_IDEA_APERTA = re.compile(r"^(\d+)\.\s+\*\*(.+?)\*\*")
_IDEA_CHIUSA = re.compile(r"^\d+\.\s+~~")


def leggi(percorso: Path = REGISTRO) -> dict:
    prove, aperte, chiuse, conto = {}, [], 0, None
    for riga in percorso.read_text(encoding="utf-8").splitlines():
        m = _RIGA.match(riga)
        if m:
            celle = [c.strip() for c in m.group(2).split("|")]
            prove[int(m.group(1))] = celle
            continue
        c = _CONTO.search(riga)
        if c:
            conto = int(c.group(1))
        if _IDEA_CHIUSA.match(riga):
            chiuse += 1
            continue
        a = _IDEA_APERTA.match(riga)
        if a:
            aperte.append((int(a.group(1)), a.group(2)))
    return {"prove": prove, "conto": conto, "idee_aperte": aperte, "idee_chiuse": chiuse}


def _corto(t: str, n: int) -> str:
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[: n - 1] + "…"


def riepilogo(dati: dict, ultime: int = 5) -> list:
    prove = dati["prove"]
    righe = [f"prove nel registro: {len(prove)} (ultima: {max(prove) if prove else '-'}); conto delle prove: {dati['conto']}",
             f"idee in coda: {len(dati['idee_aperte'])} aperte, {dati['idee_chiuse']} chiuse"]
    righe.append("ultime prove (numero, descrizione, verdetto):")
    for n in sorted(prove)[-ultime:]:
        c = prove[n]
        righe.append(f"  {n}: {_corto(c[0] if c else '', 70)} → {_corto(c[3] if len(c) > 3 else '', 45)}")
    righe.append("idee aperte (le prime):")
    for n, t in dati["idee_aperte"][:5]:
        righe.append(f"  {n}. {_corto(t, 90)}")
    return righe[:20]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--riepilogo", action="store_true")
    p.add_argument("--prova", type=int)
    p.add_argument("--cerca")
    a = p.parse_args(argv)
    dati = leggi()
    if a.prova is not None:
        c = dati["prove"].get(a.prova)
        print(f"| {a.prova} | " + " | ".join(c) + " |" if c else f"prova {a.prova} non trovata")
        return
    if a.cerca:
        trovate = [(n, c) for n, c in sorted(dati["prove"].items()) if a.cerca.lower() in " ".join(c).lower()]
        for n, c in trovate[:20]:
            print(f"{n}: {_corto(c[0], 100)}")
        print(f"(trovate {len(trovate)})")
        return
    print("\n".join(riepilogo(dati)))


if __name__ == "__main__":
    main()
