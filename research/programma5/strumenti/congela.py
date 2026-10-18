"""Programma 5: congela la regola di un'idea prima di aprire V (REGOLE.md, sezione 4): scrive ``congelata.md`` con
le varianti, l'esito su C e l'impronta SHA-256 di ogni file che fa il calcolo. Dopo, quei file non si toccano per
quell'idea: un'idea modificata e' un'idea nuova.

Uso: python3 -m research.programma5.strumenti.congela I-010
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[3]
IDEE = RADICE / "research" / "programma5" / "idee"
STRUMENTI = RADICE / "research" / "programma5" / "strumenti"
COMUNI = ["motore5.py", "ore.py", "eventi.py", "idee_minuti.py", "idee_ore.py", "idee_ore2.py", "idee_giorno.py", "esplosioni_oi.py",
          "rapporto.py", "esplorazione.py"]


def impronta(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _soglie(cartella: Path, n: int) -> str:
    from research.programma5.strumenti.rapporto import esame_idea
    cfg = esame_idea(cartella)
    if cfg.get("solo_r"):
        return (f"Prova solo su R (REGOLE.md, 6ter, punto 3): V è costruzione; su R p ≤ {cfg['soglia_r']} / numero "
                "delle varianti portate su R, con tutte le condizioni di R e il giorno migliore tolto.")
    testo = f"Soglia di V: p ≤ {cfg['soglia_v']} / {n} = {cfg['soglia_v'] / n:.5f}"
    if cfg.get("senza_giorno_migliore"):
        testo += "; su R anche positivo togliendo il giorno migliore (REGOLE.md, 6ter)"
    return testo + "."


def congela(idea: str) -> str:
    cartella = IDEE / idea
    spec = importlib.util.spec_from_file_location("calcolo", cartella / "calcolo.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    c = json.loads((cartella / "C.json").read_text(encoding="utf-8"))
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RADICE, capture_output=True, text=True).stdout.strip()
    righe = [f"# {idea} — regola congelata", "",
             f"Congelata prima di aprire V (REGOLE.md, sezione 4), sul commit `{commit}`. Le varianti, i valori e il codice "
             "qui sotto non si cambiano più per questa idea: V e R si calcolano con questi file, e un file con "
             "un'impronta diversa vuol dire un'idea nuova.", "",
             _soglie(cartella, len(mod.VARIANTI)), "",
             "## Le varianti", "", "```json", json.dumps(mod.VARIANTI, ensure_ascii=False, indent=1), "```", "",
             "## Su C (da `C.json`)", "", "| Variante | Trade | Netto | Intervallo al 95% | Caso (netto) |",
             "|---|---|---|---|---|"]
    for n, e in c.items():
        if e.get("trade"):
            righe.append(f"| {n} | {e['trade']} | {100 * e['netto']['media']:+.3f}% | "
                         f"{100 * e['netto']['basso']:+.3f}; {100 * e['netto']['alto']:+.3f} | "
                         f"{100 * e.get('caso_netto', float('nan')):+.3f}% |")
    righe += ["", "## Impronte SHA-256 dei file del calcolo", "", "| File | SHA-256 |", "|---|---|"]
    for p in [cartella / "scheda.md", cartella / "calcolo.py", cartella / "esame.json"] + [STRUMENTI / f for f in COMUNI]:
        if p.exists():
            righe.append(f"| `{p.relative_to(RADICE)}` | `{impronta(p)}` |")
    testo = "\n".join(righe) + "\n"
    (cartella / "congelata.md").write_text(testo, encoding="utf-8")
    return testo


def verifica(idea: str) -> list:
    """I file del calcolo la cui impronta non e' piu' quella congelata (vuoto se tutto torna)."""
    testo = (IDEE / idea / "congelata.md").read_text(encoding="utf-8")
    diversi = []
    for riga in testo.splitlines():
        if riga.startswith("| `") and "` | `" in riga:
            nome, h = riga.split("` | `")
            nome, h = nome[3:], h.rstrip("` |")
            p = RADICE / nome
            if not p.exists() or impronta(p) != h:
                diversi.append(nome)
    return diversi


if __name__ == "__main__":
    print(congela(sys.argv[1]))
