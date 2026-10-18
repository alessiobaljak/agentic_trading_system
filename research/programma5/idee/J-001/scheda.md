# J-001 — La moneta dopo una salita sua di un giorno, coperta con BTC

Scheda scritta il 18 ottobre 2026 **prima del calcolo di questa idea nel motore a minuti e prima di aprire V2**
(REGOLE.md, sezioni 6bis, 7 e 7bis).

## Da dove viene

Dall'esplorazione **E-101**, famiglia G1 (scossa propria coperta con BTC), lato su, verso segue (`research/programma5/esplorazione/E-101/risultati.md`): celle promosse dai
criteri scritti prima, sul periodo C2 (2024-01-01 → 2025-06-30) e 24 monete. Trovata cercando: a dire se è vera è V2.

## Perché

Una moneta che sale molto più di quanto dice BTC in un giorno (residuo estremo) ha un flusso suo — una notizia, una
rotazione dei fondi verso quel settore, una quotazione — che nel 2024-2025 si è diffuso per giorni: la moneta continua a
fare meglio del mercato. Coprendo con BTC si guadagna solo la parte propria.

## La regola

Ogni variante è **esattamente** la cella dell'esplorazione (`strumenti/esplora_fase2.py` o `esplora_calendario.py`: stessa
condizione alla chiusura dell'ora, stessa durata, stessa pausa), presa nel verso indicato, simulata nel motore a minuti
(`strumenti/idee_fase2.py`, `per_moneta_cella`): ingresso a mercato all'apertura dell'ora dopo, uscita alla chiusura
dell'ultima ora, commissione 0,05% per lato, scarto di prezzo **doppio** su tutti i trade (prudente), funding; per G1 le due
gambe (la moneta e BTC per β). Il caso: `motore5.caso` (stessa moneta, stesso mese, stessa direzione, 20 ripetizioni).

## Le varianti (giudicate insieme)

| Variante | Cella | Verso | Lordo in E-101 | Trade | t |
|---|---|---|---|---|---|
| J-001a | `G1 w24 k3 su h24` | segue | +2.083% | 360 | 4.25 |
| J-001b | `G1 w24 k3 su h12` | segue | +1.146% | 360 | 3.62 |
| J-001c | `G1 w24 k3 su h72` | segue | +3.013% | 286 | 3.60 |

## Le monete e l'esame

* **C2**: le 24 monete della fase 2 (le stesse dell'esplorazione); netto con l'intervallo sopra zero e meglio del caso.
* **V2** (2025-07-01 → 2026-09-30, una volta): le 100 di `universo_top100.json`; l'esame della sezione 7 (p ≤ 0,005 / 3, costi doppi,
  senza il giorno migliore, tutte e due le metà, 60% delle monete con almeno 20 trade, almeno 200 trade).
