"""OGNI VOCE DELLA LISTA BIANCA DEVE PARTIRE COSI' COM'E'.

Il difetto, in una riga: una richiesta ops **nomina** una voce, non compone un
comando. Quindi il comando scritto nella lista bianca e' esattamente e per sempre
quello che verra' eseguito — e se pretende argomenti, non potra' mai riceverli.

Non e' un'ipotesi. `gate-vs-paper` e' stata messa in lista dopo un controllo che
cercava `required=True` nel sorgente; quello script pero' valida a mano e usciva
con l'usage di argparse, codice 2. Il controllo statico era piu' debole di cio' che
pretendeva di verificare, e la voce e' rimasta morta finche' non e' stata lanciata.

Questo test la lancia. Per ogni voce di `ops/allowlist.example` che invoca un
modulo Python, esegue il comando davvero e pretende che NON esca con 2, il codice
con cui argparse dice "ti mancano degli argomenti". Tutto il resto va bene: se
fallisce per rete, per Firebase o per dati mancanti ha comunque superato il punto
che qui interessa — ha iniziato a lavorare. E un comando che ci mette piu' di
qualche secondo, a maggior ragione, gli argomenti li aveva.

Perche' si testa `allowlist.example` e non la lista vera: quella vive sulla
macchina e non e' nel repo, ed e' giusto cosi' (se fosse versionata, chiunque possa
committare potrebbe ampliarla). L'esempio e' il documento da cui si copia: se e'
sano li', chi copia ottiene voci che funzionano.
"""
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESEMPIO = os.path.join(ROOT, "ops", "allowlist.example")

#: quanto aspettare prima di considerare "e' partito" un comando lento. Non serve
#: che finisca: serve che abbia superato la lettura degli argomenti.
AVVIATO_DOPO_S = 12

#: il codice con cui argparse dice "argomenti mancanti o sbagliati". E' l'UNICO
#: esito che questo test considera un fallimento.
ARGPARSE_USAGE = 2


def _voci_python() -> list[tuple[str, list[str]]]:
    """(chiave, argomenti) per ogni voce che invoca un modulo Python del progetto.

    Le voci di sistema (journalctl, systemctl, free, df, uptime, ps, tmux, du, git)
    non si testano: non sono nostre, e lanciarle qui non direbbe niente sul repo.
    """
    from scripts.ops_agent import parse_allowlist

    with open(ESEMPIO, encoding="utf-8") as f:
        voci = parse_allowlist(f.read())
    out = []
    for chiave, v in sorted(voci.items()):
        pezzi = v["cmd"].split()
        if len(pezzi) >= 3 and pezzi[0].endswith("python") and pezzi[1] == "-m":
            out.append((chiave, pezzi[2:]))
    return out


VOCI = _voci_python()


def test_the_example_actually_contains_entries():
    """Se il parsing cambiasse e la lista uscisse vuota, tutti i test sotto
    passerebbero senza provare niente: il modo classico in cui una suite diventa
    verde e inutile."""
    assert len(VOCI) >= 8, f"solo {len(VOCI)} voci Python trovate: parsing rotto?"


@pytest.mark.parametrize("chiave,argomenti", VOCI, ids=[c for c, _ in VOCI])
def test_an_allowlisted_command_starts_without_extra_arguments(chiave, argomenti):
    """Lanciata cosi' com'e', la voce non deve morire sugli argomenti."""
    env = {
        **os.environ,
        # niente credenziali e niente dati finti: se anche riesce a partire, non
        # tocca il Firebase vero e non valida su serie inventate.
        "FIREBASE_SERVICE_ACCOUNT": "",
        "TRADING_BOT_TEST_MODE": "1",
        "BACKTEST_ALLOW_SYNTHETIC": "false",
        "DRY_RUN": "true",
        "PYTHONPATH": ROOT,
    }
    try:
        p = subprocess.run([sys.executable, "-m", *argomenti], cwd=ROOT, env=env,
                           capture_output=True, text=True, timeout=AVVIATO_DOPO_S)
    except subprocess.TimeoutExpired:
        return          # ancora al lavoro dopo N secondi: gli argomenti li aveva

    if p.returncode == ARGPARSE_USAGE:
        pytest.fail(
            f"la voce '{chiave}' pretende argomenti che il canale ops non puo' "
            f"darle:\n{(p.stderr or p.stdout)[-400:]}\n"
            f"Uno script in lista bianca deve avere un comportamento di default "
            f"sensato, oppure non ci va."
        )
