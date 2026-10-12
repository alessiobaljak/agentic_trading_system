"""Controllo positivo degli strumenti (lezioni/metodo.md): lookahead DICHIARATO.

La strategia legge di proposito la barra SUCCESSIVA a quella del segnale (dalla serie
completa passata in chiusura): entra long se la barra d'ingresso chiudera' sopra la sua
apertura, stop 1% sotto, esce alla chiusura della barra d'ingresso ("chiudi" dopo 1 barra).
Deve battere nettamente (a) e (b) e crollare con il ritardo di una barra. Non e' una
variante e non consuma budget: si registra come nota, prima e dopo.
Uso: python controllo_positivo.py <file di uscita json>
"""
import json
import sys

import quadro
from comune import parametri, motore
from research.src import statistica

TF = "1h"
MS = quadro.MS[TF]


def variante():
    def prepara(candele):
        # LOOKAHEAD VOLUTO: per ogni ts, la barra dopo (quella in cui si entrerebbe)
        succ = {}
        for a, b in zip(candele, candele[1:]):
            succ[a.ts] = b.close > b.open
        return succ

    def condizione(stato, storia):
        return stato.get(storia[-1].ts, False)

    def segnale(stato, storia):
        c = storia[-1].close
        return motore.Segnale("long", stop=c * 0.99)

    def uscita(stato, storia, pos):
        return "chiudi" if quadro.barre_tenute(storia, pos, MS) >= 1 else None

    return quadro.Variante("CONTROLLO", TF, "long", prepara, condizione, segnale, uscita)


v = variante()
out = {"senza_ritardo": quadro.valuta_costruzione(v)}
# ritardo di una barra: (b) ricalcolata col ritardo
out["ritardo_1"] = quadro.valuta_costruzione(v, par=parametri(ritardo_barre=1))
with open(sys.argv[1], "w") as f:
    json.dump(out, f, indent=1, default=str)
print("fatto")
