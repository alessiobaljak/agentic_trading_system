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
    # i token GitHub hanno prefissi diversi per tipo: ghp_ (classici), github_pat_
    # (fine-grained), piu' quelli di installazione e di refresh. Coprirne solo uno
    # lascia passare gli altri, ed e' il tipo di svista che si scopre quando il
    # token e' gia' uscito.
    r"|gh[pousr]_[A-Za-z0-9]{20,}"
    r"|github_pat_[A-Za-z0-9_]{20,}"
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


def rebase_in_progress(git_dir: str) -> bool:
    """True se c'e' un rebase interrotto a meta'.

    E' successo davvero: `pull --rebase --autostash` ha trovato un conflitto
    riapplicando lo stash, si e' fermato lasciando l'HEAD staccato e la cartella
    `rebase-merge` sul disco. Da quel momento OGNI giro successivo falliva con "there
    is already a rebase-merge directory" — un blocco permanente che l'agente si era
    procurato da solo e da cui non poteva uscire senza una mano umana.

    Un processo automatico non deve poter arrivare in uno stato da cui non sa
    uscire: se lo trova, lo abbandona e riparte.
    """
    return any(os.path.isdir(os.path.join(git_dir, d))
               for d in ("rebase-merge", "rebase-apply"))


def branch_problem(code: int, head: str) -> str:
    """Perche' NON si puo' lavorare con questo HEAD, o stringa vuota se si puo'.

    L'HEAD staccato e' il caso pericoloso, e non perche' il pull fallisce: perche'
    i commit fatti li' non appartengono a nessun ramo. L'agente eseguirebbe, si
    scriverebbe le risposte, le committerebbe — e sparirebbero al primo checkout,
    senza che nessuno veda un errore. Meglio non fare niente e dirlo.
    """
    b = (head or "").strip()
    if code != 0:
        return "impossibile leggere il ramo corrente"
    if not b or b == "HEAD":
        return ("HEAD STACCATO: i commit fatti qui non appartengono a nessun ramo e "
                "andrebbero persi. Nessuna richiesta e' stata eseguita. Correggi con: "
                "git checkout claude/brave-albattani-1b12fv")
    return ""


HEARTBEAT = os.path.join(APP_DIR, "ops", "heartbeat.md")
HEARTBEAT_EVERY_S = float(os.getenv("OPS_HEARTBEAT_MINUTES", "60")) * 60


def heartbeat_due(last_ts: float, now: float,
                  every_s: float = HEARTBEAT_EVERY_S) -> bool:
    """Se e' ora di lasciare un segno di vita.

    Senza battito il silenzio e' AMBIGUO: "l'agente e' morto" e "non c'era niente da
    fare" si leggono allo stesso modo da fuori, e per distinguerli servirebbe
    proprio la macchina a cui non si ha accesso. Un file aggiornato a intervalli
    regolari trasforma l'assenza di notizie in un'informazione: se il battito si
    ferma, il canale e' caduto — e si sa QUANDO.

    Non a ogni giro: sarebbero millequattrocento commit al giorno. Un'ora basta a
    distinguere "morto" da "in attesa" senza sommergere la storia del repo.
    """
    return (now - max(0.0, last_ts)) >= every_s


def write_heartbeat(branch: str, pendenti: int, now: float) -> None:
    """Un file piccolo con l'ora e lo stato. Non serve a chi guarda la macchina —
    serve a chi puo' vedere SOLO git."""
    from datetime import datetime, timezone
    quando = datetime.fromtimestamp(now, timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    with open(HEARTBEAT, "w", encoding="utf-8") as f:
        f.write(f"# agente ops: vivo\n\n_ultimo giro: {quando}_\n\n"
                f"- ramo: `{branch}`\n"
                f"- richieste in attesa: {pendenti}\n\n"
                f"Se questa data smette di avanzare, il canale e' caduto: da fuori\n"
                f"il silenzio non si distinguerebbe da 'niente da fare'.\n")


def ahead_count(out: str) -> int:
    """Quanti commit locali non sono ancora su GitHub. Serve a decidere se ritentare
    una spedizione fallita: senza questo conteggio, l'unico modo di accorgersi che
    una risposta e' rimasta ferma sarebbe non vederla arrivare."""
    try:
        return int((out or "0").strip().split()[0])
    except (ValueError, IndexError):
        return 0


def push_pending(branch: str) -> bool:
    """Spedisce TUTTO cio' che e' rimasto indietro. Chiamata SEMPRE, anche nei giri
    senza lavoro: un push fallito ieri non ha nessun altro momento per riuscire.

    Copre entrambi i modi in cui una risposta puo' restare ferma sulla macchina:
    scritta ma non committata (il processo e' stato ucciso a meta' — succede se
    systemd chiude il servizio prima della fine) e committata ma non spedita (il
    push e' fallito). Prima ne copriva zero: `pending()` vedeva la richiesta come
    evasa e si usciva subito, e quella risposta non sarebbe mai piu' partita.
    """
    # risposte scritte ma mai committate (e il battito, se aggiornato)
    code, out = _git("status", "--porcelain", "--", "ops/results", "ops/heartbeat.md")
    if code == 0 and out.strip():
        _git("add", "ops/results", "ops/heartbeat.md")
        _git("-c", "user.email=ops@localhost", "-c", "user.name=ops-agent",
             "commit", "-m", "ops: risposte e battito [skip ci]")

    code, out = _git("rev-list", "--count", f"origin/{branch}..HEAD")
    n = ahead_count(out) if code == 0 else 0
    if n <= 0:
        return True
    code, out = _git("push")
    if code != 0:
        print(f"[ops] {n} risposte ancora da spedire, push fallito: "
              f"{out.strip()[:160]}{_git_hint()}")
        return False
    print(f"[ops] spedite {n} risposte rimaste indietro")
    return True


def _git_hint() -> str:
    """Perche' git puo' fallire QUI e non a mano. Senza questa riga il sintomo e'
    'l'agente non risponde', che manda a cercare nel posto sbagliato."""
    home = os.environ.get("HOME")
    if not home or home == "/":
        return (" — HOME non e' impostato in questo servizio, quindi git non trova "
                "ne' ~/.gitconfig ne' le credenziali. Aggiungi 'Environment=HOME=/root' "
                "alla unit (o rilancia scripts/install_ops_agent.sh)")
    if not os.path.exists(os.path.join(home, ".git-credentials")):
        return (f" — non ci sono credenziali salvate in {home}/.git-credentials, e un "
                f"servizio non puo' rispondere a una richiesta di password. Salvale "
                f"una volta con: git config credential.helper store && git push")
    return f" (HOME={home})"


def main() -> int:
    # 1) prendi le richieste nuove. Senza questo l'agente lavorerebbe su una copia
    # vecchia del repo e non vedrebbe mai nulla.
    # PRIMA di tutto: si e' su un ramo? Un HEAD staccato fa fallire il pull, ma il
    # danno vero verrebbe dopo — le risposte committate su nessun ramo spariscono
    # al primo checkout, e nel log si sarebbe visto solo un errore di pull.
    # Un rebase lasciato a meta' blocca ogni operazione successiva, per sempre.
    # Si abbandona: `--quit` scarta lo stato del rebase e LASCIA l'HEAD dov'e',
    # che e' esattamente cio' che serve qui (le risposte gia' committate restano).
    if rebase_in_progress(os.path.join(APP_DIR, ".git")):
        print("[ops] trovato un rebase interrotto: lo abbandono per non restare "
              "bloccato a ogni giro")
        _git("rebase", "--quit")

    code, head = _git("rev-parse", "--abbrev-ref", "HEAD")
    problema = branch_problem(code, head)
    if problema:
        print(f"[ops] {problema}")
        return 1
    branch = head.strip()

    # NIENTE rebase automatico. Era la fonte del blocco: un conflitto durante il
    # riapplico dello stash lascia il repo a meta' e nessuno la' fuori puo'
    # risolverlo. Un avanzamento veloce o niente — se non e' possibile si prosegue
    # comunque, perche' i commit locali (le risposte) vanno spinti lo stesso.
    _git("fetch", "origin", branch)
    code, out = _git("merge", "--ff-only", f"origin/{branch}")
    if code != 0:
        print(f"[ops] niente avanzamento veloce ({out.strip()[:120]}): "
              f"proseguo con lo stato locale{_git_hint()}")

    todo = pending()
    # il battito PRIMA di qualunque uscita anticipata: e' proprio nei giri senza
    # lavoro che serve dire "sono vivo".
    try:
        ultimo = os.path.getmtime(HEARTBEAT) if os.path.exists(HEARTBEAT) else 0.0
        if heartbeat_due(ultimo, time.time()):
            write_heartbeat(branch, len(todo), time.time())
    except Exception as exc:  # noqa: BLE001
        print(f"[ops] battito non scritto ({exc}): non e' un motivo per fermarsi")

    if not todo:
        # NIENTE DA FARE non vuol dire niente da SPEDIRE. Se un push era fallito, la
        # risposta e' gia' scritta e committata: al giro dopo `pending()` la vede
        # come evasa e prima si usciva subito, senza mai ritentare. La risposta
        # restava per sempre sulla macchina — e chi l'aspettava non vedeva ne' un
        # risultato ne' un errore. Il tentativo di spedizione va fatto SEMPRE.
        push_pending(branch)
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
    # UN SOLO PUNTO che committa e spedisce, usato sia qui sia nei giri senza
    # lavoro: due percorsi diversi vorrebbero dire due modi di dimenticarsi qualcosa.
    push_pending(branch)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
