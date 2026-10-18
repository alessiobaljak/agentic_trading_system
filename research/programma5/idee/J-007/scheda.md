# J-007 — La giornata in salita che continua fino a mezzanotte

Scheda scritta il 18 ottobre 2026 **prima del calcolo di questa idea nel motore a minuti e prima di aprire V2**
(REGOLE.md, sezioni 6bis, 7 e 7bis).

## Da dove viene

Dall'esplorazione **E-103**, famiglia W3 (giornata), lato su, verso segue (`research/programma5/esplorazione/E-103/risultati.md`): celle promosse dai
criteri scritti prima, sul periodo C2 (2024-01-01 → 2025-06-30) e 24 monete. Trovata cercando: a dire se è vera è V2.

## Perché

Una giornata (00-20 UTC) in salita più del solito continua nelle ultime quattro ore: chi compra durante la giornata
americana (i fondi quotati in borsa negli Stati Uniti comprano in quelle ore) non ha finito, e chi vende è meno presente
la sera.

## La regola

Ogni variante è **esattamente** la cella dell'esplorazione (`strumenti/esplora_fase2.py` o `esplora_calendario.py`: stessa
condizione alla chiusura dell'ora, stessa durata, stessa pausa), presa nel verso indicato, simulata nel motore a minuti
(`strumenti/idee_fase2.py`, `per_moneta_cella`): ingresso a mercato all'apertura dell'ora dopo, uscita alla chiusura
dell'ultima ora, commissione 0,05% per lato, scarto di prezzo **doppio** su tutti i trade (prudente), funding; per G1 le due
gambe (la moneta e BTC per β). Il caso: `motore5.caso` (stessa moneta, stesso mese, stessa direzione, 20 ripetizioni).

## Le varianti (giudicate insieme)

| Variante | Cella | Verso | Lordo in E-103 | Trade | t |
|---|---|---|---|---|---|
| J-007a | `W3 giornata k1 su` | segue | +0.510% | 1556 | 3.63 |
| J-007b | `W3 giornata k2 su` | segue | +0.866% | 364 | 3.05 |

## Le monete e l'esame

* **C2**: le 24 monete della fase 2 (le stesse dell'esplorazione); netto con l'intervallo sopra zero e meglio del caso.
* **V2** (2025-07-01 → 2026-09-30, una volta): le 100 di `universo_top100.json`; l'esame della sezione 7 (p ≤ 0,005 / 2, costi doppi,
  senza il giorno migliore, tutte e due le metà, 60% delle monete con almeno 20 trade, almeno 200 trade).
