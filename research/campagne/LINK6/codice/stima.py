"""Stima dei trade (sezione 8.4): solo il numero di trade sul periodo di costruzione, nessun risultato.

Uso: python3 research/campagne/LINK6/codice/stima.py <lotto.json> [--registra-scarti]

Stampa, per ogni variante del lotto, i trade stimati (e, per i limit, gli ordini inseriti ed eseguiti).
Con --registra-scarti scrive nel log uno `scarto` per ogni variante sotto i 150 trade (non consuma tentativi).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
from research.src.catalogo3 import compila, normalizza  # noqa: E402
from research.src.motore3 import stima_trade  # noqa: E402
from research.src.statistica4 import REGOLE_LINK  # noqa: E402


def stima(specifica):
    v = normalizza(specifica)
    s, a, b = comune.serie_costruzione(v["timeframe"])
    return stima_trade(compila(v, s), REGOLE_LINK, a, b)


def main():
    lotto = comune.leggi_lotto(sys.argv[1])
    registra = "--registra-scarti" in sys.argv[2:]
    for vid, voce in lotto.items():
        st = stima(voce["specifica"])
        nota = ""
        if st["ordini_inseriti"]:
            nota = f" (ordini inseriti {st['ordini_inseriti']}, eseguiti {st['ordini_eseguiti']})"
        esito = "sotto i minimi" if st["trade"] < comune.TRADE_MINIMI else "ok"
        print(f"{vid}: trade stimati {st['trade']}{nota} -> {esito}")
        if registra and st["trade"] < comune.TRADE_MINIMI:
            comune.aggiungi({"id": vid, "tipo": "scarto", "ipotesi": voce["ipotesi"], "specifica": voce["specifica"],
                             "trade_stimati": st["trade"],
                             "motivo": f"stima dei trade sotto il minimo di {comune.TRADE_MINIMI} (8.4)"})


if __name__ == "__main__":
    main()
