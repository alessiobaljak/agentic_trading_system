"""QUELLO CHE LA DASHBOARD MOSTRA DEV'ESSERE QUELLO CHE IL BOT FA.

Due difetti trovati il 20 settembre guardando una posizione VIVA (PROMUSDT short,
validata con la scala 2/4/6). Nessuno dei due toccava il trading; entrambi facevano
leggere al proprietario numeri che non descrivevano la sua posizione.

  1. L'ETICHETTA DEI GRADINI veniva dal default globale (1.5/3/5) mentre i PREZZI
     erano calcolati sulla scala validata per la coppia. Sullo schermo si leggeva
     «✓ 3R» accanto a un prezzo che era 4R. Il proprietario ha letto 3R e ha
     ragionato su 3R: un'etichetta sbagliata accanto a un prezzo giusto sembra
     un'informazione e invece e' una bugia.

  2. LO STOP MOSTRATO era `stop_price`, cioe' la base — spostata a pareggio dopo il
     primo TP. La protezione del profitto pero' alza lo stop a ogni tick senza
     persisterlo, quindi la dashboard diceva «pareggio» mentre il bot proteggeva
     molto piu' in alto. Sottostimare la protezione spinge a chiudere a mano una
     posizione gia' al sicuro — il modo piu' silenzioso di perdere una vincita.
"""
import inspect

from bot.execution.executor import ExecutionEngine


def test_le_etichette_dei_gradini_vengono_dalla_scala_della_coppia():
    """Il caso PROMUSDT: scala validata 2/4/6, etichette mostrate 1.5/3/5."""
    src = inspect.getsource(ExecutionEngine._write_position_state)
    assert "_mults = pos.scale_r_mults or settings.SCALE_OUT_R_MULTIPLES" in src
    assert "_mults = settings.SCALE_OUT_R_MULTIPLES\n" not in src


def test_prezzi_ed_etichette_escono_dalla_stessa_scala():
    """La garanzia vera: qualunque sia la scala, i due usano la STESSA fonte. Erano
    gia' due righe vicine e divergevano lo stesso — la vicinanza non basta."""
    src = inspect.getsource(ExecutionEngine._write_position_state)
    i_mults = src.index("_mults = ")
    blocco = src[i_mults:i_mults + 600]
    assert "r_mults=pos.scale_r_mults" in blocco, (
        "i PREZZI non usano piu' la scala della coppia")
    assert "_mults[i]" in blocco, "le ETICHETTE non usano piu' la stessa fonte"


def test_lo_stop_effettivo_viene_pubblicato():
    """Include la protezione del profitto. `stop_price` resta la base perche' serve
    a ricostruire la posizione dopo un riavvio: cambiarne il significato di nascosto
    romperebbe quel percorso."""
    src = inspect.getsource(ExecutionEngine._write_position_state)
    assert '"effective_stop"' in src
    assert '"stop_price": pos.stop_price' in src, "la base non va toccata"


def test_lo_stop_effettivo_arriva_da_chi_lo_ha_calcolato():
    """Se `_write_position_state` lo ricalcolasse per conto suo, sarebbe una SECONDA
    copia della regola del profit-lock: due copie che divergono nel tempo sono il
    difetto piu' caro di questo progetto."""
    src = inspect.getsource(ExecutionEngine.update_position)
    assert src.count("eff_stop=") == 2, (
        "entrambi i rami (scale-out e TP unico) devono passare lo stop effettivo")
    scrittura = inspect.getsource(ExecutionEngine._write_position_state)
    assert "locked_stop(" not in scrittura, "non ricalcolare: ricevilo"


def test_la_dashboard_mostra_quello_effettivo_con_ripiego():
    """Le posizioni aperte prima di oggi non hanno `effective_stop`: devono
    continuare a mostrare la base invece di una cella vuota."""
    with open("dashboard/app/components/Positions.tsx", encoding="utf-8") as f:
        tsx = f.read()
    assert "p.effective_stop ?? p.stop_price" in tsx
    assert "effective_stop != null" in tsx, (
        "serve un segno visibile quando la protezione e' piu' alta della base")
