"""KILL SWITCH A TRE LIVELLI — fermarsi non e' un'operazione sola.

Un interruttore binario costringe a scegliere fra "non fare niente" e "liquida
tutto adesso". Le tre situazioni reali chiedono risposte diverse: sospendere le
nuove aperture lasciando lavorare gli SL/TP gia' piazzati; uscire gradualmente
senza regalare lo spread; uscire subito a qualunque prezzo.

Due invarianti che questi test difendono, perche' sbagliarle e' silenzioso:

* NON SI DECLASSA MAI. Fra lo stato nuovo e il vecchio flag booleano vince il
  piu' GRAVE. Un valore rimasto indietro non deve poter abbassare una protezione
  richiesta, e un valore illeggibile non deve spegnerla.
* LO STOP DI PROTEZIONE SI MUOVE SOLO VERSO IL PREZZO. Allontanarlo allargherebbe
  la perdita possibile proprio mentre si sta cercando di uscire.
"""
import pytest

from bot.risk.kill_switch import BotState, blocks_new_positions, protect_stop, resolve


# ---- risoluzione dello stato ----------------------------------------------- #
def test_no_command_means_normal():
    assert resolve(None, None) is BotState.NORMAL
    assert resolve("", False) is BotState.NORMAL


@pytest.mark.parametrize("raw,expected", [
    ("paused", BotState.PAUSED),
    ("stopping", BotState.STOPPING),
    ("emergency", BotState.EMERGENCY),
])
def test_each_level_is_recognised(raw, expected):
    assert resolve(raw, False) is expected


def test_the_legacy_boolean_still_means_emergency():
    """La dashboard attuale e reset_paper scrivono ancora il flag booleano:
    cambiargli significato di nascosto trasformerebbe un "ferma tutto" in un
    "sospendi" senza che nessuno lo sappia."""
    assert resolve(None, True) is BotState.EMERGENCY


def test_the_more_severe_level_always_wins():
    # stato nuovo blando + flag storico acceso -> vince l'emergenza
    assert resolve("paused", True) is BotState.EMERGENCY
    # stato nuovo grave + flag storico spento -> resta grave
    assert resolve("emergency", False) is BotState.EMERGENCY


def test_an_unreadable_state_does_not_freeze_the_bot_nor_disarm_it():
    assert resolve("qualcosa-di-strano", False) is BotState.NORMAL
    # ...ma se il flag storico chiede l'emergenza, quella vale comunque
    assert resolve("qualcosa-di-strano", True) is BotState.EMERGENCY


# ---- cosa blocca cosa ------------------------------------------------------ #
def test_new_positions_are_blocked_from_pause_upwards():
    assert blocks_new_positions(BotState.NORMAL) is False
    assert blocks_new_positions(BotState.PAUSED) is True
    assert blocks_new_positions(BotState.STOPPING) is True
    assert blocks_new_positions(BotState.EMERGENCY) is True


# ---- stop di protezione ---------------------------------------------------- #
def test_protect_stop_tightens_a_long():
    # mark 100, ATR 2, 0.3 ATR -> stop a 99.4, piu' vicino del 95 attuale
    assert protect_stop(100.0, 95.0, 2.0, long=True, atr_mult=0.3) == pytest.approx(99.4)


def test_protect_stop_tightens_a_short():
    assert protect_stop(100.0, 105.0, 2.0, long=False, atr_mult=0.3) == pytest.approx(100.6)


def test_protect_stop_never_moves_away_from_price():
    """Se lo stop e' gia' piu' stretto, resta dov'e': allargarlo aumenterebbe la
    perdita possibile proprio mentre si sta uscendo."""
    assert protect_stop(100.0, 99.9, 2.0, long=True) == pytest.approx(99.9)
    assert protect_stop(100.0, 100.1, 2.0, long=False) == pytest.approx(100.1)


def test_protect_stop_leaves_the_stop_alone_on_bad_data():
    """Meglio l'uscita lenta di uno stop calcolato su un ATR sporco."""
    assert protect_stop(100.0, 95.0, 0.0, long=True) == 95.0
    assert protect_stop(100.0, 95.0, -1.0, long=True) == 95.0
    assert protect_stop(0.0, 95.0, 2.0, long=True) == 95.0


def test_a_wider_multiplier_gives_a_looser_stop():
    stretto = protect_stop(100.0, 90.0, 2.0, long=True, atr_mult=0.3)
    largo = protect_stop(100.0, 90.0, 2.0, long=True, atr_mult=1.0)
    assert stretto > largo      # 0.3 ATR e' piu' vicino al prezzo di 1.0 ATR
