"""IL TEMPO DEL GIRO SI MISURA DA SOLO.

22 set 2026: un giro ha sforato la finestra di 3 ore e per saperlo sono serviti
tre comandi (`servizi`, `processi`, il journal) letti a mano — e il journal tiene
80 righe di cache che spingono via la fine del giro. Il proprietario ha chiesto
di essere sicuri di poterlo misurare, perche' e' il vincolo su cui si decidono
le prossime modifiche. Ora la discovery scrive inizio e durata su Firebase e
`gate_progress` (allowlist `gate`) li stampa.
"""
import inspect

from scripts import discover_strategies as d
from scripts import gate_progress as g


def test_la_discovery_registra_inizio_e_durata():
    src = inspect.getsource(d.main)
    assert "t0 = time.time()" in src
    assert '"started_at": t0' in src and '"duration_s": round(durata)' in src
    assert "GIRO FINITO in" in src


def test_gate_progress_stampa_la_durata_e_avvisa_se_sfora():
    src = inspect.getsource(g)
    assert "TEMPO DELL'ULTIMO GIRO" in src
    assert "SFORA la finestra di 3h" in src
    assert 'diag.get("started_at")' in src


def test_senza_il_dato_lo_dice_invece_di_tacere():
    """Un giro col codice vecchio non ha il campo: deve dirlo, non stampare zero."""
    assert "non ancora registrato" in inspect.getsource(g)
