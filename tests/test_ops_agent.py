"""L'AGENTE OPS — un canale di comando su una macchina che tiene le chiavi.

Questi test non chiedono "funziona?", chiedono "cosa succede se la richiesta e'
ostile?". Un canale che esegue comandi su una macchina con le chiavi dell'exchange
e' peggio del problema che risolve se sbagliato, e sbagliato non si vede: funziona
benissimo fino al giorno in cui esegue la cosa sbagliata.

Le tre proprieta' da difendere: la lista bianca comanda (e non sta nel repo), non
c'e' shell da iniettare, e niente segreti nelle risposte committate.
"""
import pytest

from scripts.ops_agent import (parse_allowlist, parse_request, redact, render,
                               resolve, truncate)

ALLOW = parse_allowlist("""
# commento
autopsy: .venv/bin/python -m scripts.gate_autopsy
log-bot: journalctl -u trading-bot.service -n 80 --no-pager +args
riavvia-bot: systemctl restart trading-bot.service
# fast-gate: bash scripts/fast_gate.sh --yes
""")


# ---- la lista bianca comanda --------------------------------------------- #
def test_a_known_key_resolves_to_its_command():
    cmd, refusal = resolve("autopsy", ALLOW)
    assert refusal == ""
    assert cmd[-1] == "scripts.gate_autopsy"


def test_an_unknown_key_is_refused_and_says_what_exists():
    """Un rifiuto muto sarebbe indistinguibile da un agente fermo: si aspetterebbe
    per ore una risposta che non arriva."""
    cmd, refusal = resolve("cancella-tutto", ALLOW)
    assert cmd is None and "non e' nella lista bianca" in refusal
    assert "autopsy" in refusal


def test_a_commented_entry_is_not_active():
    """Le voci distruttive sono commentate di proposito: devono restare inerti."""
    cmd, refusal = resolve("fast-gate", ALLOW)
    assert cmd is None and refusal


def test_an_empty_allowlist_refuses_everything():
    """Senza approvazione esplicita non si esegue nulla — e' il default voluto,
    non un caso degenere."""
    cmd, refusal = resolve("autopsy", {})
    assert cmd is None and refusal


# ---- non c'e' shell da iniettare ----------------------------------------- #
def test_shell_metacharacters_have_no_power():
    """Il comando viene da shlex.split ed e' eseguito senza shell: `;` e backtick
    restano caratteri, non operatori. Qui si verifica che non entrino nemmeno."""
    for ostile in ("autopsy; rm -rf /", "autopsy && cat .env", "autopsy | nc x 1",
                   "autopsy `cat .env`", "autopsy$(id)"):
        cmd, refusal = resolve(ostile, ALLOW)
        assert cmd is None, f"{ostile!r} non deve risolversi"
        assert refusal


def test_arguments_are_refused_where_not_declared():
    cmd, refusal = resolve("autopsy\n--evil", ALLOW)
    assert cmd is None and "non accetta argomenti" in refusal


def test_arguments_are_allowed_where_declared():
    cmd, refusal = resolve("log-bot\n-n\n200", ALLOW)
    assert refusal == "" and cmd[-2:] == ["-n", "200"]


def test_a_dangerous_argument_stops_the_whole_request():
    """Ripulire l'argomento e proseguire eseguirebbe qualcosa di diverso da cio'
    che e' stato chiesto: peggio che rifiutare."""
    for arg in ("; rm -rf /", "$(id)", "a b", "`x`", "--out=/tmp/x;id"):
        cmd, refusal = resolve(f"log-bot\n{arg}", ALLOW)
        assert cmd is None and "argomento rifiutato" in refusal


def test_path_traversal_is_refused():
    """`..` passa il filtro dei caratteri (punto e barra sono innocui presi
    singolarmente) ma insieme risalgono l'albero: con una voce che accetta un
    percorso, `../../.env` sarebbe esattamente il file che non deve uscire.
    Questo caso e' stato trovato da un test, non dalla lettura del codice."""
    for arg in ("../../etc/shadow", "../.env", "ops/../../.env"):
        cmd, refusal = resolve(f"log-bot\n{arg}", ALLOW)
        assert cmd is None and "risale l'albero" in refusal


def test_an_empty_request_is_refused():
    assert resolve("", ALLOW)[0] is None
    assert resolve("# solo commenti\n", ALLOW)[0] is None


def test_comments_and_blank_lines_are_ignored_in_a_request():
    cmd, refusal = resolve("\n# nota\nautopsy\n", ALLOW)
    assert refusal == "" and cmd


# ---- niente segreti nelle risposte --------------------------------------- #
def test_keys_are_redacted():
    """Il risultato finisce in un repo: un segreto committato e' compromesso per
    sempre, anche se il commit viene poi rimosso."""
    for veleno in ("BINANCE_API_SECRET=abc123xyz",
                   "ANTHROPIC_API_KEY: sk-ant-0123456789abcdef0123",
                   "password = hunter2",
                   "-----BEGIN RSA PRIVATE KEY-----"):
        assert "[OSCURATO]" in redact(veleno)


def test_every_flavour_of_github_token_is_redacted():
    """I token GitHub hanno prefissi diversi per tipo: classici, fine-grained, di
    installazione. Coprirne solo uno lascia passare gli altri — ed e' il tipo di
    svista che si scopre quando il token e' gia' uscito."""
    for t in ("ghp_AbCdEf0123456789AbCdEf0123456789",
              "gho_AbCdEf0123456789AbCdEf0123456789",
              "ghs_AbCdEf0123456789AbCdEf0123456789",
              "github_pat_11ABCDEFG0123456789_abcdefghijklmnopqrstuvwxyz0123456789"):
        assert "[OSCURATO]" in redact(f"remote: usando {t} per il push")


def test_ordinary_output_survives_redaction():
    """Un oscuramento troppo largo renderebbe le risposte illeggibili, e nessuno
    userebbe piu' il canale."""
    testo = "FERMATE SOLO DA pf_ex_top: 14 · miglior t = 2.65"
    assert redact(testo) == testo


def test_truncation_keeps_head_and_tail():
    """L'inizio dice cosa e' partito, la fine perche' e' finito: tagliare solo in
    fondo perderebbe proprio l'errore."""
    testo = "INIZIO" + ("x" * 5000) + "ERRORE FINALE"
    corto = truncate(testo, limit=200)
    assert corto.startswith("INIZIO") and corto.endswith("ERRORE FINALE")
    assert len(corto) < 400


def test_short_output_is_untouched():
    assert truncate("breve", limit=200) == "breve"


# ---- la risposta racconta cio' che e' successo davvero ------------------- #
def test_the_answer_shows_the_command_actually_run():
    """Mostrare la richiesta invece del comando eseguito darebbe una falsa
    sicurezza su cosa e' girato sulla macchina."""
    body = render("x.req", "autopsy", [".venv/bin/python", "-m", "scripts.gate_autopsy"],
                  "", {"code": 0, "output": "tutto bene", "seconds": 1.2}, "ora")
    assert "scripts.gate_autopsy" in body and "codice 0" in body


def test_a_refusal_is_written_down_with_its_reason():
    body = render("x.req", "cancella", None, "non e' nella lista bianca", None, "ora")
    assert "RIFIUTATA" in body and "lista bianca" in body


def test_the_answer_is_redacted_too():
    body = render("x.req", "autopsy", ["echo"],
                  "", {"code": 0, "output": "API_KEY=segretissimo", "seconds": 0.1},
                  "ora")
    assert "segretissimo" not in body


# ---- il formato della lista bianca --------------------------------------- #
def test_the_plus_args_marker_is_not_part_of_the_command():
    assert ALLOW["log-bot"]["args"] is True
    assert "+args" not in ALLOW["log-bot"]["cmd"]
    assert ALLOW["autopsy"]["args"] is False


def test_the_shipped_example_contains_no_destructive_entry_active():
    """fast_gate azzera il registro: settimane di passaggi accumulati. Nel modello
    consegnato deve essere commentata."""
    import os
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(here, "ops", "allowlist.example")) as f:
        entries = parse_allowlist(f.read())
    for pericolosa in ("fast-gate", "reset-paper"):
        assert pericolosa not in entries
    assert "autopsy" in entries and "gate" in entries


# ---- l'HEAD staccato: il guasto che perde le risposte in silenzio -------- #
def test_a_detached_head_stops_everything():
    """Non perche' il pull fallisce — quello e' solo il sintomo. Il danno vero
    verrebbe dopo: le risposte committate su nessun ramo spariscono al primo
    checkout, e nel log si sarebbe visto solo un errore di pull."""
    from scripts.ops_agent import branch_problem
    problema = branch_problem(0, "HEAD")
    assert "STACCATO" in problema and "git checkout" in problema


def test_an_unreadable_head_is_treated_as_a_problem():
    from scripts.ops_agent import branch_problem
    assert branch_problem(128, "") != ""


def test_a_normal_branch_is_no_problem():
    from scripts.ops_agent import branch_problem
    assert branch_problem(0, "claude/brave-albattani-1b12fv\n") == ""
    assert branch_problem(0, "main") == ""


def test_an_interrupted_rebase_is_detected(tmp_path):
    """E' successo davvero: `pull --rebase --autostash` ha trovato un conflitto, si
    e' fermato, e da quel momento OGNI giro falliva con 'there is already a
    rebase-merge directory'. Un blocco permanente che l'agente si era procurato da
    solo e da cui non poteva uscire. Un processo automatico non deve poter arrivare
    in uno stato da cui non sa uscire."""
    from scripts.ops_agent import rebase_in_progress
    git = tmp_path / ".git"
    git.mkdir()
    assert rebase_in_progress(str(git)) is False
    (git / "rebase-merge").mkdir()
    assert rebase_in_progress(str(git)) is True


def test_the_other_rebase_flavour_is_detected_too(tmp_path):
    """`git rebase --apply` usa un'altra cartella: cercarne una sola lascerebbe
    scoperta meta' dei casi."""
    from scripts.ops_agent import rebase_in_progress
    git = tmp_path / ".git"
    (git / "rebase-apply").mkdir(parents=True)
    assert rebase_in_progress(str(git)) is True


def test_a_missing_git_dir_is_not_a_rebase(tmp_path):
    from scripts.ops_agent import rebase_in_progress
    assert rebase_in_progress(str(tmp_path / "inesistente")) is False


# ---- una risposta scritta ma non spedita non deve restare ferma ---------- #
def test_the_ahead_count_is_read_from_git():
    from scripts.ops_agent import ahead_count
    assert ahead_count("3\n") == 3
    assert ahead_count("0") == 0


def test_an_unreadable_count_means_nothing_to_send():
    """Meglio non spedire per prudenza che spedire su un conteggio inventato."""
    from scripts.ops_agent import ahead_count
    assert ahead_count("") == 0
    assert ahead_count("boh") == 0
    assert ahead_count(None) == 0


# ---- il battito: distinguere "morto" da "niente da fare" ----------------- #
def test_the_heartbeat_is_due_after_the_interval():
    from scripts.ops_agent import heartbeat_due
    assert heartbeat_due(1000.0, 1000.0 + 3601, every_s=3600) is True
    assert heartbeat_due(1000.0, 1000.0 + 60, every_s=3600) is False


def test_a_missing_heartbeat_is_written_immediately():
    """Al primo giro non c'e' nessun file: il battito deve partire subito,
    altrimenti la prima ora sarebbe indistinguibile da un agente morto."""
    from scripts.ops_agent import heartbeat_due
    assert heartbeat_due(0.0, 1_700_000_000.0, every_s=3600) is True


def test_the_heartbeat_says_when_and_what(tmp_path, monkeypatch):
    import scripts.ops_agent as ops
    monkeypatch.setattr(ops, "HEARTBEAT", str(tmp_path / "heartbeat.md"))
    ops.write_heartbeat("mio-ramo", 3, 1_700_000_000.0)
    testo = (tmp_path / "heartbeat.md").read_text()
    assert "mio-ramo" in testo and "3" in testo and "2023" in testo
    # deve spiegare a cosa serve: un file di stato che non si spiega viene ignorato
    assert "silenzio" in testo
