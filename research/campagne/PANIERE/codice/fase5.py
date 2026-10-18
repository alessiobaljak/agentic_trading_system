"""Fase 5, la prova dello scettico (lezioni/metodo.md: «togliere dall'ipotesi la parte che porta il meccanismo»).

La regola dei due candidati dell'idea C (k 1,25, uscita dopo 3 barre) SENZA la condizione di ritardo: dopo un giorno
forte al rialzo di Bitcoin entrano tutte le monete liquide con il rendimento del giorno, in ritardo o no
(``senza_condizione_di_ritardo``). Registrata prima, come verifica di PANIERE-043 (per PANIERE-040 la regola senza
la condizione è la stessa). Usa lo stesso percorso di fase4.py.
"""

import copy
import sys
from pathlib import Path

CODICE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODICE))

import fase4  # noqa: E402


def main():
    reg = fase4.registrazione_di("PANIERE-043")
    p = copy.deepcopy(reg["parametri"])
    p["senza_condizione_di_ritardo"] = True
    fase4.esegui("PANIERE-043", reg, "PANIERE-043 Fase 5 senza la condizione di ritardo", p, {},
                 "Dalla Fase 3 (il ritardo non ordina l'esito; conta che cosa fa Bitcoin dopo): R medio e t contro la (b) "
                 "simili a quelli del candidato (R fra +0,08 e +0,15, t fra 2 e 3,5). Se è così, il vantaggio è «comprare "
                 "il paniere dopo un giorno forte di Bitcoin» e non il ritardo delle monete: l'ipotesi C come scritta "
                 "non è sostenuta. Se invece il t scende sotto 1, il ritardo conta.",
                 "si riporta; smonta il meccanismo se il t contro la (b) senza la condizione è almeno quello del candidato",
                 True)
    print("fatto")


if __name__ == "__main__":
    main()
