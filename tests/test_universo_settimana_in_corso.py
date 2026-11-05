"""L'universo del lunedi' calcolato da solo (terza.universo_lunedi) e la settimana non ancora chiusa per i conti giornalieri del
paper (paper/aggiorna.universi_con_settimana_in_corso): HLI e DXI devono vedere anche i giorni della settimana in corso."""
import numpy as np

from research.programma6 import terza as te
from research.programma6.paper import aggiorna as ag


def _pannello(giorni: int = 400, monete: int = 5, t0: int = 4) -> dict:
    rng = np.random.default_rng(0)
    C = 100 * np.exp(np.cumsum(rng.normal(0, 0.02, (giorni, monete)), axis=0))
    V = np.tile(np.array([5e6, 4e6, 3e6, 1e6, 6e6]), (giorni, 1))
    V[:, 4] = 0.0                                       # una moneta senza scambi: mai nell'universo
    return {"close": C, "open": C.copy(), "high": C, "low": C, "quote_volume": V, "t0": t0,
            "funding": np.zeros((giorni, monete)), "simboli": [f"M{j}USDT" for j in range(monete)]}


def test_universo_lunedi_uguale_al_pannello_delle_settimane():
    pan = _pannello()
    psw = te.pannello_settimane(pan, log=lambda x: None, a=2, indicatori_si=False)
    for k, m in enumerate(psw["lunedi"] - pan["t0"]):
        U, peso = te.universo_lunedi(pan, int(m), 0, 2)
        assert (U == psw["U"][k]).all()
        assert np.array_equal(peso, psw["peso"][k])
    # dopo 200 giorni di storia: le due monete con piu' volume
    assert psw["U"][-1].tolist() == [True, True, False, False, False]


def test_settimana_in_corso_aggiunta():
    pan = _pannello()
    psw = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lunedi, U = ag.universi_con_settimana_in_corso(pan, psw)
    ultimo = pan["t0"] + pan["close"].shape[0] - 1
    assert lunedi[-1] <= ultimo < lunedi[-1] + 7       # l'ultimo giorno dei dati sta nell'ultima settimana dell'elenco
    assert len(lunedi) == len(U) and len(lunedi) >= len(psw["lunedi"])
    assert np.array_equal(lunedi[:len(psw["lunedi"])], psw["lunedi"])
    assert (U[-1] == te.universo_lunedi(pan, int(lunedi[-1] - pan["t0"]))[0]).all()
