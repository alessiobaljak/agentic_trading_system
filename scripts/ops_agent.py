"""IL PONTE — comandi chiesti via git, eseguiti sulla VPS, risposte rimesse su git.

IL PROBLEMA. Chi scrive il codice non ha accesso alla macchina, e ogni diagnosi
passa da un copia-incolla manuale: un giro di domanda-risposta costa minuti di
attenzione umana e si perde a ogni sessione. Serve un canale, ma su una macchina
che tiene chiavi Binance e gestisce posizioni un canale sbagliato e' peggio del
problema.

COME FUNZIONA. Un file di richiesta viene committato nel repo; questo agente lo
trova al giro successivo, esegue, e ricommitta la risposta. Nessuna porta aperta,
nessuna chiave su GitHub, nessun runner esterno con accesso alla shell.

LE TRE PROPRIETA' CHE LO RENDONO ACCETTABILE

1. LA LISTA BIANCA NON STA NEL REPO. Vive in `ops/allowlist`, sulla macchina, ed e'
   ignorata da git. E' la differenza fra "esegue solo cio' che il proprietario ha
   approvato" e "esegue cio' che chiede chi ha scritto la richiesta": se la lista
   fosse versionata, chiunque possa committare potrebbe ampliarla, e il controllo
   sarebbe finto.
2. NIENTE SHELL. Il comando viene da `shlex.split` ed eseguito senza shell, quindi
   `;`, backtick e pipe non hanno alcun potere. La richiesta puo' solo NOMINARE una
   voce della lista, mai comporre un comando.
3. ARGOMENTI RISTRETTI. Solo dove la voce lo consente esplicitamente (`+args`), e
   solo caratteri innocui. Un argomento che non passa la verifica ferma l'intera
   richiesta invece di essere ripulito in silenzio.

In piu': timeout su ogni esecuzione, output troncato, e una passata di oscuramento
su tutto cio' che somiglia a una chiave — perche' il risultato finisce in un repo,
e un segreto committato per sbaglio va considerato compromesso per sempre.
"""
from __future__ import annotations

import os
import re
import shlex
import subprocess
import time
from typing import Optional

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQ_DIR = os.path.join(APP_DIR, "ops", "requests")
RES_DIR = os.path.join(APP_DIR, "ops", "results")
ALLOWLIST = os.path.join(APP_DIR, "ops", "allowlist")

# argomenti ammessi: niente spazi, niente metacaratteri, niente percorsi risalenti.
ARG_RE = re.compile(r"^[A-Za-z0-9._:=/@+-]+$")
MAX_OUTPUT = int(os.getenv("OPS_MAX_OUTPUT", "20000"))
TIMEOUT_S = float(os.getenv("OPS_TIMEOUT_S", "900"))

# Cio' che non deve MAI finire in un file committato. Meglio oscurare qualche riga
# innocua che pubblicare una chiave: un segreto finito in un repo e' compromesso
# anche se il commit viene poi rimosso.
SECRET_RE = re.compile(
    r"(?i)("
    r"[A-Za-z0-9_-]*(?:api[_-]?key|secret|token|password|passwd|credential)"
    r"[A-Za-z0-9_-]*\s*[:=]\s*\S+"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|sk-[A-Za-z0-9-]{16,}"
    r"|ghp_[A-Za-z0-9]{20,}"
    r"|AIza[A-Za-z0-9_-]{20,}"
    r")")


def redact(text: str) -> str:
    """Oscura cio' che somiglia a un segreto. Non e' una garanzia — e' l'ultima
    rete prima che qualcosa finisca in un repo."""
    return SECRET_RE.sub("[OSCURATO]", text or "")


def truncate(text: str, limit: int = MAX_OUTPUT) -> str:
    """Tiene la TESTA e la CODA: l'inizio dice cosa e' partito, la fine perche' e'
    finito. Tagliare solo in fondo perderebbe proprio l'errore."""
    if len(text) <= limit:
        return text
    head, tail = text[: limit // 2], text[-limit // 2:]
    return (f"{head}\n\n[... {len(text) - limit} caratteri omessi "
            f"(testa e coda conservate) ...]\n\n{tail}")


def parse_allowlist(text: str) -> dict:
    """`chiave: comando` per riga, `#` per i commenti. Un `+args` in fondo alla riga
    consente argomenti aggiuntivi dalla richiesta.

    Formato volutamente banale: e' il file che decide cosa puo' girare su una
    macchina con le chiavi dell'exchange, e deve poter essere letto e verificato in
    dieci secondi da chi lo scrive.
    """
    out: dict = {}
    for raw in (text or "").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, cmd = line.split(":", 1)
        key, cmd = key.strip(), cmd.strip()
        allows_args = cmd.endswith("+args")
        if allows_args:
            cmd = cmd[: -len("+args")].strip()
        if key and cmd:
            out[key] = {"cmd": cmd, "args": allows_args}
    return out


def parse_request(text: str) -> tuple[str, list]:
    """(chiave, argomenti) da un file di richiesta. Prima riga utile = chiave, le
    successive = un argomento ciascuna."""
    lines = [l.strip() for l in (text or "").splitlines()]
    lines = [l for l in lines if l and not l.startswith("#")]
    if not lines:
        return "", []
    return lines[0], lines[1:]


def resolve(req_text: str, allow: dict) -> tuple[Optional[list], str]:
    """(comando da eseguire, motivo del rifiuto). Uno dei due e' sempre vuoto.

    Ogni rifiuto e' esplicito e finisce nel risultato: una richiesta ignorata in
    silenzio sarebbe indistinguibile da un agente fermo, e si aspetterebbe per ore
    una risposta che non arriva.
    """
    key, args = parse_request(req_text)
    if not key:
        return None, "richiesta vuota"
    entry = allow.get(key)
    if entry is None:
        return None, (f"'{key}' non e' nella lista bianca di questa macchina. "
                      f"Disponibili: {', '.join(sorted(allow)) or '(nessuna)'}")
    if args and not entry["args"]:
        return None, f"'{key}' non accetta argomenti (manca '+args' nella lista)"
    for a in args:
        if not ARG_RE.match(a):
            return None, (f"argomento rifiutato: {a!r}. Ammessi solo lettere, cifre "
                          f"e . _ : = / @ + -")
        # `..` passava il filtro dei caratteri (punto e barra sono innocui presi
        # singolarmente) ma insieme risalgono l'albero: con una voce che accetta un
        # percorso, `../../.env` sarebbe esattamente il file che non deve uscire.
        if ".." in a:
            return None, f"argomento rifiutato: {a!r} risale l'albero dei percorsi"
    return shlex.split(entry["cmd"]) + args, ""


def run(cmd: list, timeout: float = TIMEOUT_S) -> dict:
    """Esegue SENZA shell: `;`, pipe e backtick non hanno potere. Un timeout scaduto
    e' un esito, non un'eccezione — la risposta deve tornare comunque."""
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=APP_DIR, capture_output=True, text=True,
                           timeout=timeout)
        out = (p.stdout or "") + (("\n--- stderr ---\n" + p.stderr) if p.stderr else "")
        return {"code": p.returncode, "output": out, "seconds": time.time() - t0}
    except subprocess.TimeoutExpired as exc:
        partial = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        return {"code": 124, "output": partial + f"\n[TIMEOUT dopo {timeout:g}s]",
                "seconds": time.time() - t0}
    except Exception as exc:  # noqa: BLE001
        return {"code": 127, "output": f"[non eseguito: {exc}]",
                "seconds": time.time() - t0}


def render(name: str, req_text: str, cmd: Optional[list], refusal: str,
           result: Optional[dict], when: str) -> str:
    """Il file di risposta. Contiene il comando ESEGUITO, non quello chiesto: se i
    due divergessero, leggere il secondo darebbe una falsa sicurezza."""
    L = [f"# {name}", "", f"_eseguito: {when}_", ""]
    key, args = parse_request(req_text)
    L.append(f"**richiesta:** `{key}`" + (f" `{' '.join(args)}`" if args else ""))
    if refusal:
        L += ["", f"**RIFIUTATA:** {refusal}", ""]
        return "\n".join(L)
    L += [f"**eseguito:** `{' '.join(cmd or [])}`",
          f"**esito:** codice {result['code']} in {result['seconds']:.1f}s", "",
          "```", truncate(redact(result["output"]).rstrip()) or "(nessun output)",
          "```", ""]
    return "\n".join(L)


def pending() -> list:
    """Richieste senza risposta. Il file di risposta E' lo stato: niente database,
    niente marcatori da tenere allineati, e un riavvio non perde nulla."""
    try:
        reqs = sorted(f for f in os.listdir(REQ_DIR) if not f.startswith("."))
    except FileNotFoundError:
        return []
    done = set(os.listdir(RES_DIR)) if os.path.isdir(RES_DIR) else set()
    return [f for f in reqs if f"{os.path.splitext(f)[0]}.md" not in done]


def _git(*args: str) -> tuple[int, str]:
    p = subprocess.run(["git", *args], cwd=APP_DIR, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main() -> int:
    # 1) prendi le richieste nuove. Senza questo l'agente lavorerebbe su una copia
    # vecchia del repo e non vedrebbe mai nulla.
    code, out = _git("pull", "--rebase", "--autostash")
    if code != 0:
        print(f"[ops] pull fallito: {out.strip()[:200]}")

    todo = pending()
    if not todo:
        return 0
    allow = {}
    if os.path.exists(ALLOWLIST):
        with open(ALLOWLIST, encoding="utf-8") as f:
            allow = parse_allowlist(f.read())
    else:
        print(f"[ops] nessuna lista bianca in {ALLOWLIST}: ogni richiesta verra' "
              f"rifiutata (e' il comportamento voluto: senza approvazione esplicita "
              f"non si esegue nulla)")

    os.makedirs(RES_DIR, exist_ok=True)
    from datetime import datetime, timezone
    for name in todo:
        with open(os.path.join(REQ_DIR, name), encoding="utf-8") as f:
            req_text = f.read()
        cmd, refusal = resolve(req_text, allow)
        print(f"[ops] {name}: " + (f"RIFIUTATA ({refusal})" if refusal
                                   else " ".join(cmd)))
        res = run(cmd) if cmd else None
        when = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        body = render(name, req_text, cmd, refusal, res, when)
        with open(os.path.join(RES_DIR, f"{os.path.splitext(name)[0]}.md"), "w",
                  encoding="utf-8") as f:
            f.write(body)

    # 2) rimanda indietro le risposte. `[skip ci]` per non innescare workflow.
    _git("add", "ops/results")
    _git("-c", "user.email=ops@localhost", "-c", "user.name=ops-agent",
         "commit", "-m", f"ops: {len(todo)} risposte [skip ci]")
    code, out = _git("push")
    if code != 0:
        # non si perde niente: il commit resta locale e il push si ritenta al giro
        # dopo. Va detto, pero': senza push la risposta non arriva a destinazione.
        print(f"[ops] push fallito, riprovo al prossimo giro: {out.strip()[:200]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
