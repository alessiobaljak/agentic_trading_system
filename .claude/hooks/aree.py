#!/usr/bin/env python3
"""Il blocco delle aree: ogni sessione scrive solo nella sua area e nei file in comune (richiesta del proprietario dell'11 novembre
2026: «una cartella con crypto dove ci scrivi solo tu, una cartella con stock dove ci scrive l'altra sessione e altre cartelle che
magari creo dopo tipo Forex»; la mappa e' in `AREE.json`, spiegata in `AREE.md`).

Gira come hook PreToolUse su Edit, Write, NotebookEdit e Bash. La sessione si riconosce dall'identificativo remoto
(`CLAUDE_CODE_REMOTE_SESSION_ID`, senza il prefisso prima del primo «_»), che vale anche per i suoi subagent. Leggere e' sempre
permesso: si blocca solo lo scrivere fuori dall'area.

* Edit, Write, NotebookEdit: il file deve stare nell'area della sessione o fra i file in comune; i file fuori dal repository
  (scratchpad, /tmp, ~/.claude) sono sempre permessi.
* Bash: un controllo di buon senso sui comandi che scrivono (redirezioni `>`/`>>`, `tee`, `rm`, `mv`, `cp` verso, `touch`, `mkdir`,
  `sed -i`, `git add/rm/mv/checkout/restore/clean`) con un percorso di un'altra area. Non vede tutto (per esempio uno script Python
  che scrive): e' una protezione contro gli errori, non contro chi vuole aggirarla.
* Una sessione non registrata scrive solo nei file in comune finche' non si registra:
  `python3 .claude/hooks/aree.py registra <area>`.
* Fuori da una sessione remota (nessun identificativo, per esempio in locale o nei test) non blocca niente.

Qualunque errore nel leggere l'ingresso o la mappa: esce zitto senza bloccare, come gli altri hook del repo; i test
(`tests/test_hook_aree.py`) controllano i casi veri.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
MAPPA = RADICE / "AREE.json"


def carica(percorso: Path = MAPPA) -> dict:
    return json.loads(percorso.read_text(encoding="utf-8"))


def id_sessione() -> str:
    v = os.environ.get("CLAUDE_CODE_REMOTE_SESSION_ID", "").strip()
    return v.split("_", 1)[1] if "_" in v else v


def relativo(percorso: str, cwd: str = "") -> str | None:
    """Il percorso relativo alla radice del repository, o None se e' fuori dal repository."""
    p = Path(percorso)
    if not p.is_absolute():
        p = Path(cwd or os.getcwd()) / p
    try:
        return Path(os.path.normpath(p)).relative_to(RADICE).as_posix()
    except ValueError:
        return None


def _dentro(rel: str, prefisso: str) -> bool:
    prefisso = prefisso.rstrip("/")
    return rel == prefisso or rel.startswith(prefisso + "/")


def proprietario(rel: str, mappa: dict) -> str:
    """L'area di un percorso relativo: prima le aree con cartelle esplicite (la piu' lunga vince), poi i file in comune, poi l'area
    con la cartella «*»."""
    migliore, lung = None, -1
    for nome, a in mappa["aree"].items():
        for c in a.get("cartelle", []):
            if c != "*" and _dentro(rel, c) and len(c) > lung:
                migliore, lung = nome, len(c)
    if migliore:
        return migliore
    if any(_dentro(rel, c) for c in mappa.get("comuni", [])):
        return "comune"
    for nome, a in mappa["aree"].items():
        if "*" in a.get("cartelle", []):
            return nome
    return "comune"


def permesso(rel: str | None, area: str | None, mappa: dict) -> bool:
    if rel is None or rel == "" or rel.startswith(".git/"):
        return True
    chi = proprietario(rel, mappa)
    return chi == "comune" or (area is not None and chi == area)


# --- Bash: i percorsi che un comando scrive ---------------------------------------------------------------------------------------

_SEPARATORI = re.compile(r"\|\||&&|;|\||\n")
_SCRIVE_TUTTI = {"rm", "rmdir", "touch", "mkdir", "truncate", "mv", "tee", "unlink", "shred"}
_SCRIVE_ULTIMO = {"cp", "install", "rsync", "ln"}
_GIT_SCRIVE = {"add", "rm", "mv", "checkout", "restore", "clean"}


def _argomenti(tok: list[str]) -> list[str]:
    return [t for t in tok if not t.startswith("-")]


_HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\1[ \t]*(?=\n|$)", re.S)
_TESTO = re.compile(r"'[^']*'|\"(?:[^\"\\]|\\.)*\"")


def scritti_da_bash(cmd: str) -> list[str]:
    """I percorsi che il comando scrive (stima): redirezioni e argomenti dei comandi che scrivono. Il testo dei «heredoc» e quello
    fra virgolette (per esempio il messaggio di un commit) non contano come comandi."""
    fuori: list[str] = []
    cmd = _HEREDOC.sub(lambda m: m.group(0).split("\n", 1)[0], cmd)        # resta solo la riga col comando
    senza_testo = _TESTO.sub("''", cmd)
    for m in re.finditer(r"(?<![<>&\d])>>?\s*([^\s;&|<>]+)", senza_testo):     # > file e >> file (non 2>, non &>)
        fuori.append(m.group(1))
    for seg in _SEPARATORI.split(cmd):
        try:
            tok = shlex.split(seg, comments=False, posix=True)
        except ValueError:
            tok = seg.split()
        while tok and (re.fullmatch(r"\w+=.*", tok[0]) or tok[0] in ("sudo", "timeout", "nice", "command")):
            tok = tok[1:] if not (tok[0] == "timeout" and len(tok) > 1) else tok[2:]
        tok = [t for t in tok if not t.startswith(">") and not re.fullmatch(r"\d*>>?", t)]
        if not tok:
            continue
        verbo, resto = Path(tok[0]).name, tok[1:]
        if verbo in _SCRIVE_TUTTI:
            fuori += _argomenti(resto)
        elif verbo in _SCRIVE_ULTIMO:
            a = _argomenti(resto)
            fuori += a[-1:]
        elif verbo == "sed" and any(t == "-i" or t.startswith("-i") or t == "--in-place" for t in resto):
            a = _argomenti(resto)
            fuori += a[1:]
        elif verbo == "git" and resto:
            sotto = next((t for t in resto if not t.startswith("-")), "")
            if sotto in _GIT_SCRIVE:
                i = resto.index(sotto)
                fuori += [t for t in _argomenti(resto[i + 1:]) if t not in (".", "HEAD")]
    return fuori


def motivo(strumento: str, ingresso: dict, area: str | None, mappa: dict, cwd: str = "") -> str:
    if strumento in ("Edit", "Write", "NotebookEdit"):
        candidati = [str(ingresso.get("file_path") or ingresso.get("notebook_path") or "")]
    elif strumento == "Bash":
        candidati = scritti_da_bash(str(ingresso.get("command") or ""))
    else:
        return ""
    for c in candidati:
        if not c:
            continue
        rel = relativo(c, cwd)
        if not permesso(rel, area, mappa):
            chi = proprietario(rel, mappa)
            if area is None:
                return (f"questa sessione non ha un'area registrata: puo' scrivere solo nei file in comune. «{rel}» e' dell'area «{chi}». "
                        f"Registrala con: python3 .claude/hooks/aree.py registra <area> (le aree sono in AREE.json, spiegate in AREE.md)")
            return (f"«{rel}» e' dell'area «{chi}»: questa sessione e' dell'area «{area}» e scrive solo nella sua area e nei file in comune "
                    f"(AREE.md; regola del proprietario dell'11 novembre 2026)")
    return ""


def main() -> int:
    try:
        dati = json.load(sys.stdin)
        sid = id_sessione()
        if not sid:
            return 0
        mappa = carica()
        area = mappa.get("sessioni", {}).get(sid)
        m = motivo(str(dati.get("tool_name") or ""), dict(dati.get("tool_input") or {}), area, mappa, str(dati.get("cwd") or ""))
    except Exception:  # noqa: BLE001
        return 0
    if m:
        print(f"[aree] bloccato: {m}", file=sys.stderr)
        return 2
    return 0


def registra(area: str) -> int:
    mappa = carica()
    if area not in mappa["aree"]:
        print(f"area sconosciuta: {area}; le aree sono {sorted(mappa['aree'])} (AREE.json)")
        return 1
    sid = id_sessione()
    if not sid:
        print("nessun identificativo di sessione remota: niente da registrare")
        return 1
    mappa.setdefault("sessioni", {})[sid] = area
    MAPPA.write_text(json.dumps(mappa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"sessione {sid} registrata nell'area «{area}»: ricorda di committare AREE.json")
    return 0


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "registra":
        sys.exit(registra(sys.argv[2]))
    sys.exit(main())
