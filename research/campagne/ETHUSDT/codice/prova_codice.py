"""Prova che il codice delle varianti giri senza errori. NON conta trade e NON da' risultati.

Per ogni variante esegue le quattro fabbriche (variante, (a), casuale, segnale) sulle
prime 3000 barre di costruzione e stampa solo "ok" o l'errore. Prova poi su dati
inventati le funzioni di supporto (livelli tondi, indicatori, stop col tetto).
"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
import idee  # noqa: E402
from indicatori import ATR, Estremo, Media, RSI, Ritardo  # noqa: E402
from research.src import motore  # noqa: E402


def prove_sintetiche() -> None:
    assert idee.livello_tondo_in(995.0, 1000.0)
    assert not idee.livello_tondo_in(1000.0, 1099.0)
    assert idee.livello_tondo_in(1000.0, 1100.0)
    assert idee.livello_tondo_in(129.5, 130.0)
    assert not idee.livello_tondo_in(130.0, 139.9)
    assert not idee.livello_tondo_in(140.0, 130.0)
    e = Estremo(3, massimo=True)
    for x, atteso in [(1, None), (5, None), (2, 5), (1, 5), (0, 2), (7, 7)]:
        e.aggiorna(x)
        assert e.valore == atteso, (x, e.valore, atteso)
    m = Media(2)
    for x in (1.0, 3.0, 5.0):
        m.aggiorna(x)
    assert m.valore == 4.0
    r = Ritardo(2)
    for x in (1, 2, 3, 4):
        r.aggiorna(x)
    assert r.valore == 2
    rsi = RSI(2)
    for x in (10.0, 11.0, 12.0):
        rsi.aggiorna(x)
    assert rsi.valore == 100.0
    s = idee.segnale_da_distanza("long", 100.0, 10.0)
    assert abs(s.stop - 94.0) < 1e-9
    s = idee.segnale_da_livello("short", 100.0, 101.0)
    assert abs(s.stop - 101.0) < 1e-9
    a = ATR(2)
    a.aggiorna(11, 9, 10)
    a.aggiorna(12, 10, 11)
    assert a.valore == 2.0
    print("prove sintetiche: ok")


def main() -> None:
    prove_sintetiche()
    p = comune.parametri()
    for nome, (V, kw, tf) in idee.VARIANTI.items():
        s = comune.carica(tf, "costruzione")
        pezzo = s.last[:3000]
        mark = s.mark[:3000]
        try:
            motore.esegui(pezzo, None, mark, s.funding, comune.fabbrica(V, kw, s)(), p)
            motore.esegui(pezzo, None, mark, s.funding, comune.fabbrica_a(V, kw, s)(), p)
            motore.esegui(pezzo, None, mark, s.funding, comune.fabbrica_casuale(V, kw, s)(frozenset(range(0, 3000, 50))), p)
            motore.barre_vietate_segnale_non_valido(pezzo, comune.fabbrica_segnale(V, kw, s), p)
            print(nome, "ok")
        except Exception:
            print(nome, "ERRORE")
            traceback.print_exc()


if __name__ == "__main__":
    main()
