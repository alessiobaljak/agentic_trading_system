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
    ad essere sbagliata, non il gradino. Dal 25 set 2026 la soglia vive in
    `bot/learning/metrics.py` (la usa anche il controllo orario) e il rapporto
    la stampa da li': una copia sola, cosi' non puo' divergere."""
    from bot.learning.metrics import SOGLIA_INGRESSO_SBAGLIATO, classi_stop
    assert SOGLIA_INGRESSO_SBAGLIATO == 0.25
    src = inspect.getsource(m.main)
    assert "classi_stop(" in src and "SOGLIA_INGRESSO_SBAGLIATO" in src
    cs = classi_stop([{"exit_reason": "stop_loss", "mfe_r": 0.24},
                      {"exit_reason": "stop_loss", "mfe_r": 0.25}])
    assert (cs["sbagliati"], cs["quasi"]) == (1, 1)


def test_e_in_lista_bianca_di_esempio():
    txt = open("ops/allowlist.example").read()
    assert "mfe:          .venv/bin/python -m scripts.mfe_report" in txt
