#!/usr/bin/env python3
"""Blocco dei segreti per TUTTE le sessioni e per tutti i subagent (7 novembre 2026, richiesta del proprietario di far rispettare le
regole critiche nel codice e nei permessi, non solo nei prompt; regola di `CLAUDE.md`: «Mai un segreto in un commit [...] Questo repo
e' pubblico»).

Gira come hook PreToolUse su Bash, Read, Grep e Glob. Le regole `deny` di `.claude/settings.json` coprono i comandi piu' semplici
(`cat .env`); questo hook copre quello che una regola sul prefisso del comando non vede: un file di segreti citato in mezzo a un
comando (`python3 -c "open('.env')"`, `xxd .env`, `cp .env x`), le chiavi private, l'ambiente intero del processo, il remoto di git.

Blocca (uscita 2, il messaggio va all'agente):
* i file di segreti: `.env` e `*.env` (non `.env.example`), `*service-account*.json`, `*.pem`, `.git-credentials`, `id_rsa`/`id_ed25519`;
* l'ambiente intero: `env` e `printenv` come comandi, `/proc/<pid>/environ`, `os.environ` stampato tutto;
* `git remote -v` e `git config --list`, che possono contenere il token.

Qualunque errore nel leggere l'ingresso: esce zitto senza bloccare (come gli altri hook del repo), perche' un hook rotto non deve
fermare il lavoro; i test (`tests/test_hook_segreti.py`) controllano che i casi veri vengano bloccati.
"""
from __future__ import annotations

import json
import re
import sys

_FILE = [
    r"(?<![\w.\-])\.env(?![\w.\-])",                  # .env da solo (non .venv, non .env.example)
    r"(?<![\w.\-/])[\w\-]+\.env(?![\w.\-])",          # tuning.env e simili
    r"(?<![\w.\-])\.env\.(?!example\b)[\w\-]+",       # .env.local, .env.prod (non .env.example)
    r"service[-_]?account[\w\-]*\.json",
    r"\.pem\b",
    r"\.git-credentials",
    r"\bid_(rsa|ed25519|ecdsa)\b",
]
_AMBIENTE = [
    r"(^|[;&|(]\s*|\bsudo\s+)(printenv|env)(\s*$|\s*[;&|)>])",
    r"(^|[;&|(]\s*)env\s+-0\b",
    r"/proc/[^\s/]+/environ",
    r"print\(\s*(dict\()?\s*os\.environ\s*\)?\s*\)",
    r"json\.dumps\(\s*(dict\()?\s*os\.environ",
]
_GIT = [r"git\s+remote\s+(-v|--verbose)", r"git\s+config\s+(--list|-l)\b", r"git\s+config\s+--get-regexp\s+remote"]


def motivo(strumento: str, ingresso: dict) -> str:
    """Il motivo del blocco, o stringa vuota se la chiamata e' permessa."""
    if strumento == "Bash":
        cmd = str(ingresso.get("command") or "")
        for p in _GIT:
            if re.search(p, cmd):
                return "il remoto e la configurazione di git possono contenere il token: non si leggono (CLAUDE.md)"
        for p in _AMBIENTE:
            if re.search(p, cmd):
                return "l'ambiente del processo contiene le chiavi: non si stampa intero (leggi solo la variabile che serve, se non e' un segreto)"
        testi = [cmd]
    elif strumento in ("Read", "Grep", "Glob"):
        testi = [str(ingresso.get(k) or "") for k in ("file_path", "path", "pattern", "glob")]
    else:
        return ""
    for t in testi:
        for p in _FILE:
            if re.search(p, t):
                return ("file di segreti: non si legge e non si copia (CLAUDE.md, «Mai un segreto in un commit»; il repo e' pubblico). "
                        "Se stai solo scrivendo un testo che ne cita il nome, usa Write o Edit invece di un comando")
    return ""


def main() -> int:
    try:
        dati = json.load(sys.stdin)
        m = motivo(str(dati.get("tool_name") or ""), dict(dati.get("tool_input") or {}))
    except Exception:  # noqa: BLE001
        return 0
    if m:
        print(f"[segreti] bloccato: {m}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
