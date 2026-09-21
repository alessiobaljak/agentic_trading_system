"""GLI STOP LOSS DIVISI PER COME SONO MORTI — ingresso sbagliato o uscita tarata male.

Domanda del proprietario, 21 settembre 2026: «posizioni in positivo per ore, mai
al primo take profit, poi stop loss: siamo entrati sbagliati o il TP andava piu'
basso?». Sono due morti diverse: la prima si cura sull'ingresso, la seconda
sull'uscita. `mfe_r` le distingue da solo, e il rapporto ora lo stampa.
"""
import inspect

from scripts import mfe_report as m


def test_il_rapporto_divide_gli_stop_in_tre_classi():
    src = inspect.getsource(m.main)
    assert "sbagliati dall'inizio" in src and "problema di INGRESSO" in src
    assert "sotto il 1° gradino" in src and "problema di USCITA" in src
    assert "oltre il 1° gradino" in src


def test_la_soglia_di_ingresso_sbagliato_e_un_quarto_di_R():
    """Sotto 0,25R il prezzo non e' mai andato davvero a favore: e' la direzione
    ad essere sbagliata, non il gradino."""
    src = inspect.getsource(m.main)
    assert 'float(t["mfe_r"]) < 0.25' in src


def test_e_in_lista_bianca_di_esempio():
    txt = open("ops/allowlist.example").read()
    assert "mfe:          .venv/bin/python -m scripts.mfe_report" in txt
