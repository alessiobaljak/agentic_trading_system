"""L'AGENTE OPS — un canale di comando su una macchina che tiene le chiavi.

Questi test non chiedono "funziona?", chiedono "cosa succede se la richiesta e'
ostile?". Un canale che esegue comandi su una macchina con le chiavi dell'exchange
e' peggio del problema che risolve se sbagliato, e sbagliato non si vede: funziona
benissimo fino al giorno in cui esegue la cosa sbagliata.

Le tre proprieta' da difendere: la lista bianca comanda (e non sta nel repo), non
c'e' shell da iniettare, e niente segreti nelle risposte committate.
"""
import base64
import hashlib
import json
import time

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
    sempre, anche se il commit viene poi rimosso. Non basta che compaia «[OSCURATO]»:
    il segreto non deve esserci piu' (audit del 26 novembre 2026, salute-5)."""
    for veleno, segreto in (("BINANCE_API_SECRET=abc123xyz", "abc123xyz"),
                            ("ANTHROPIC_API_KEY: sk-ant-0123456789abcdef0123", "0123456789abcdef"),
                            ("password = hunter2", "hunter2"),
                            ("-----BEGIN RSA PRIVATE KEY-----", "RSA PRIVATE KEY")):
        uscita = redact(veleno)
        assert "[OSCURATO]" in uscita and segreto not in uscita


# ---- le chiavi private: via tutto il blocco, non solo la prima riga ------- #
# Audit del 26 novembre 2026 (salute-5): redact toglieva solo la riga BEGIN, e il corpo
# della chiave, cioe' il segreto, sarebbe finito nel repository pubblico. Le chiavi di
# questi test sono FINTE: il corpo e' calcolato da una parola con sha256, e le righe
# BEGIN ed END si compongono qui, cosi' nel file non c'e' niente che somigli a una chiave.
GIORNALE = "Nov 27 12:00:00 Trading-Agent python3[1234]: "
TIPI_DI_CHIAVE = ["PRIVATE KEY", "RSA PRIVATE KEY", "EC PRIVATE KEY", "DSA PRIVATE KEY",
                  "ED25519 PRIVATE KEY", "OPENSSH PRIVATE KEY", "ENCRYPTED PRIVATE KEY",
                  "PGP PRIVATE KEY BLOCK"]


def _riga(quale: str, tipo: str) -> str:
    return "-----" + quale + " " + tipo + "-----"


def _corpo_finto(seme: str) -> list:
    """Tre righe da 64 caratteri di base64 e un'ultima corta, come il corpo di un PEM."""
    righe = [base64.b64encode(hashlib.sha256(f"{seme}-{i}".encode()).digest()
                              + hashlib.sha256(f"{seme}-{i}-bis".encode()).digest()[:16]).decode()
             for i in range(3)]
    return righe + [base64.b64encode(hashlib.sha256(seme.encode()).digest()[:15]).decode()]


def _pem(tipo: str, corpo: list, a_capo: str = "\n", fine: bool = True) -> str:
    righe = [_riga("BEGIN", tipo)] + corpo + ([_riga("END", tipo)] if fine else [])
    return a_capo.join(righe)


def _pezzi_rimasti(corpo: list, uscita: str) -> list:
    """I pezzi di 12 caratteri del corpo ancora leggibili nell'uscita: devono essere zero."""
    tutto = "".join(corpo)
    pezzi = (tutto[i:i + 12] for i in range(0, len(tutto) - 11, 4))
    return [p for p in pezzi if p in uscita]


def _forme(pem: str) -> dict:
    """Le forme in cui una chiave puo' comparire nell'uscita di un comando."""
    return {
        "a capo veri": "prima\n" + pem + "\ndopo",
        "a capo di Windows": "prima\r\n" + pem.replace("\n", "\r\n") + "\r\ndopo",
        "JSON": json.dumps({"type": "service_account", "private_key": pem + "\n", "nota": "dopo"}),
        "JSON dentro JSON": json.dumps({"risposta": json.dumps({"private_key": pem})}) + " dopo",
        "NOME=valore con \\n": "BINANCE_DEMO_API_SECRET=" + pem.replace("\n", "\\n") + "\ndopo",
        "repr di Python": f"errore leggendo {pem!r}: dopo",
        "journalctl": "\n".join(GIORNALE + r for r in pem.split("\n")) + "\n" + GIORNALE + "dopo",
    }


@pytest.mark.parametrize("tipo", TIPI_DI_CHIAVE)
@pytest.mark.parametrize("forma", list(_forme("x")))
def test_the_whole_private_key_is_removed_not_only_its_first_line(tipo, forma):
    """Prima si toglieva solo la riga BEGIN e il corpo restava, anche con gli a capo
    scritti come \\n (il file di servizio di Firebase, BINANCE_DEMO_API_SECRET); con le
    cifre nel nome (ED25519) non si toglieva nemmeno quella."""
    corpo = _corpo_finto(tipo + forma)
    uscita = redact(_forme(_pem(tipo, corpo))[forma])
    assert "[OSCURATO]" in uscita
    assert _pezzi_rimasti(corpo, uscita) == []
    assert "dopo" in uscita   # cio' che segue la chiave resta leggibile


@pytest.mark.parametrize("a_capo", ["\n", "\\n", "\r\n", "\\\\n"])
def test_a_key_cut_before_its_end_loses_its_body_too(a_capo):
    """Un'uscita tagliata (un timeout, un errore accorciato) puo' avere la riga BEGIN
    senza la END: si toglie tutto cio' che puo' essere corpo, e quello che segue resta."""
    corpo = _corpo_finto("tagliata" + a_capo)
    uscita = redact("errore: " + _pem("ED25519 PRIVATE KEY", corpo, a_capo, fine=False)
                    + "\n--- stderr ---\nTraceback (most recent call last):")
    assert _pezzi_rimasti(corpo, uscita) == []
    assert uscita.startswith("errore: [OSCURATO]")
    assert "--- stderr ---\nTraceback (most recent call last):" in uscita


def test_a_key_cut_at_the_top_by_journalctl_loses_its_long_lines():
    """journalctl mostra le ultime righe, ognuna con data e processo davanti: la riga
    BEGIN puo' restare fuori. Le righe lunghe del corpo vanno via lo stesso, perche'
    sembrano una chiave; puo' restare solo l'ultima riga, quella corta."""
    corpo = _corpo_finto("giornale")
    uscita = redact("\n".join(GIORNALE + r for r in corpo[1:] + [_riga("END", "PRIVATE KEY")]))
    for r in corpo[1:-1]:
        assert r not in uscita
    assert uscita.count("[OSCURATO]") == 2 and GIORNALE in uscita


def test_the_firebase_service_account_loses_its_key_and_its_key_id():
    """Il file di servizio di Firebase: `private_key_id` e il corpo di `private_key`
    uscivano intatti (il nome «private_key» non era fra quelli cercati). Ora vanno via i
    due valori, il resto resta, e il JSON resta valido."""
    corpo = _corpo_finto("servizio")
    servizio = {"type": "service_account", "project_id": "progetto-finto",
                "private_key_id": hashlib.sha1(b"finto").hexdigest(),
                "private_key": _pem("PRIVATE KEY", corpo) + "\n", "client_id": "1234567890"}
    for testo in (json.dumps(servizio, indent=2), json.dumps(servizio), repr(servizio)):
        uscita = redact(testo)
        assert servizio["private_key_id"] not in uscita
        assert _pezzi_rimasti(corpo, uscita) == []
        assert "service_account" in uscita and "progetto-finto" in uscita
        assert redact(uscita) == uscita   # ripassare non cambia niente (esporta_storia lo fa)
    pulito = json.loads(redact(json.dumps(servizio, indent=2)))
    assert pulito == {**servizio, "private_key_id": "[OSCURATO]", "private_key": "[OSCURATO]"}


def test_quoted_secrets_lose_their_value_and_numbers_stay():
    """«"NOME": "valore"» (un JSON, un dizionario di Python) non si vedeva per la
    virgoletta dopo il nome. Si toglie il valore e il JSON resta valido (redact pulisce
    anche i file di scripts/esporta_storia.py); i numeri restano, perche' un conteggio di
    token e' una misura."""
    dati = {"api_secret": "segretissimo", "bot_token": "777:XYZ", "secret_word": "due parole",
            "tokens_in": 1200, "pnl": -1.5}
    assert json.loads(redact(json.dumps(dati))) == {
        "api_secret": "[OSCURATO]", "bot_token": "[OSCURATO]", "secret_word": "[OSCURATO]",
        "tokens_in": 1200, "pnl": -1.5}
    stampa = redact(repr(dati))
    assert "segretissimo" not in stampa and "XYZ" not in stampa and "due parole" not in stampa
    assert "1200" in stampa


def test_a_long_random_sequence_goes_but_hashes_paths_and_numbers_stay():
    """Una chiave senza il suo nome (64 caratteri come quelle di Binance, una riga di una
    chiave privata) va via. Restano gli hash dei commit e dei file, i percorsi dei dati di
    Binance, i numeri e i nomi lunghi: oscurarli renderebbe le risposte illeggibili."""
    riga = base64.b64encode(hashlib.sha256(b"riga-finta").digest()
                            + hashlib.sha256(b"riga-finta-2").digest()[:16]).decode()
    alfanumerica = "".join(c for c in base64.b64encode(hashlib.sha512(b"chiave-finta").digest()).decode()
                           if c.isalnum())[:64]
    assert redact(f"firma con {alfanumerica} riga {riga} fine") == "firma con [OSCURATO] riga [OSCURATO] fine"
    for testo in ("commit b665eac8a7afaf92dde8d3beaf9083048c02fc59",
                  "sha256 " + hashlib.sha256(b"x").hexdigest(),
                  "SHA1 " + hashlib.sha1(b"x").hexdigest().upper(),
                  "scaricato data/futures/um/monthly/klines/BTCUSDT/1d/BTCUSDT-1d-2024-01.zip",
                  "letto data/vault/BNBUSDT/markPriceKlines/1h/BNBUSDT",
                  "research/programma6/CINQUANTAQUATTRESIMA",
                  "ordine 12345678901234567890123456789012345678901234567890",
                  GIORNALE + "G1 pesi BTCUSDT 0.05 ETHUSDT -0.05 1000SHIBUSDT 0.01"):
        assert redact(testo) == testo


def test_the_answer_file_never_contains_a_key_body():
    """Dall'uscita del comando al file di risposta (oscuramento e taglio insieme)."""
    corpo = _corpo_finto("risposta")
    uscita = "avvio\n" + _pem("PRIVATE KEY", corpo) + "\nfine"
    body = render("x.req", "log-bot", ["journalctl"], "",
                  {"code": 0, "output": uscita, "seconds": 0.1}, "ora")
    assert _pezzi_rimasti(corpo, body) == [] and "avvio" in body and "fine" in body


def test_redaction_stays_fast_on_huge_or_hostile_output():
    """redact gira su tutta l'uscita, prima del taglio: un'uscita grande non deve fermare
    l'agente. Una riga di 40.000 lettere costava 52 secondi (la regola dei nomi ripartiva
    da ogni lettera; misurato il 27 novembre 2026); migliaia di intestazioni senza fine
    non devono far rileggere il testo a ogni intestazione."""
    for testo in ("a" * 30_000, "token" * 20_000, _riga("BEGIN", "PRIVATE KEY") * 50_000,
                  base64.b64encode(bytes(range(256)) * 3000).decode(),
                  ('"' + "secret" * 100 + " ") * 2000):
        inizio = time.time()
        redact(testo)
        assert time.time() - inizio < 3, testo[:40]


def _cryptography():
    """La libreria delle chiavi, se c'e' e funziona. In qualche ambiente si rompe gia'
    all'import con un errore che non e' un Exception (PanicException): allora si salta."""
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa
    except BaseException as exc:  # noqa: BLE001
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        pytest.skip(f"cryptography non disponibile: {type(exc).__name__}")
    return serialization, ec, ed25519, rsa


@pytest.mark.parametrize("quale", ["ed25519", "ed25519 openssh", "rsa", "rsa tradizionale",
                                   "ec", "rsa cifrata"])
def test_real_keys_generated_here_leave_nothing_behind(quale):
    """Chiavi vere generate qui in memoria e buttate via (come in tests/test_demo_binance.py),
    in tutte le forme di `_forme`: del corpo non resta niente."""
    serialization, ec, ed25519, rsa = _cryptography()
    f, libera = serialization.PrivateFormat, serialization.NoEncryption()
    nuova = {
        "ed25519": lambda: (ed25519.Ed25519PrivateKey.generate(), f.PKCS8, libera),
        "ed25519 openssh": lambda: (ed25519.Ed25519PrivateKey.generate(), f.OpenSSH, libera),
        "rsa": lambda: (rsa.generate_private_key(public_exponent=65537, key_size=2048), f.PKCS8, libera),
        "rsa tradizionale": lambda: (rsa.generate_private_key(public_exponent=65537, key_size=2048),
                                     f.TraditionalOpenSSL, libera),
        "ec": lambda: (ec.generate_private_key(ec.SECP256R1()), f.TraditionalOpenSSL, libera),
        "rsa cifrata": lambda: (rsa.generate_private_key(public_exponent=65537, key_size=2048),
                                f.TraditionalOpenSSL, serialization.BestAvailableEncryption(b"finta")),
    }[quale]
    chiave, formato, cifratura = nuova()
    pem = chiave.private_bytes(serialization.Encoding.PEM, formato, cifratura).decode().strip()
    corpo = [r for r in pem.split("\n")[1:-1] if r and ":" not in r]
    for forma, testo in _forme(pem).items():
        uscita = redact(testo)
        assert _pezzi_rimasti(corpo, uscita) == [], forma
        assert "dopo" in uscita, forma


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
