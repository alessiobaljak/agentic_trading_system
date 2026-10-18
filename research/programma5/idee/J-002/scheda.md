# J-002 — La continuazione dopo una salita forte di qualche ora

Scheda scritta il 18 ottobre 2026 **prima del calcolo di questa idea nel motore a minuti e prima di aprire V2**
(REGOLE.md, sezioni 6bis, 7 e 7bis).

## Da dove viene

Dall'esplorazione **E-101**, famiglia F1 (scossa), lato su, verso segue (`research/programma5/esplorazione/E-101/risultati.md`): celle promosse dai
criteri scritti prima, sul periodo C2 (2024-01-01 → 2025-06-30) e 24 monete. Trovata cercando: a dire se è vera è V2.

## Perché

Dopo una salita di 1-4 ore molto più grande del solito il prezzo nel 2024-2025 ha continuato a salire per uno-tre
giorni: chi era short chiude (liquidazioni e coperture), chi era fuori entra in ritardo (notizie, flussi dei fondi), e il
movimento si allunga. È il momento a breve, il contrario di quello che faceva il mercato nel 2022.

## La regola

Ogni variante è **esattamente** la cella dell'esplorazione (`strumenti/esplora_fase2.py` o `esplora_calendario.py`: stessa
condizione alla chiusura dell'ora, stessa durata, stessa pausa), presa nel verso indicato, simulata nel motore a minuti
(`strumenti/idee_fase2.py`, `per_moneta_cella`): ingresso a mercato all'apertura dell'ora dopo, uscita alla chiusura
dell'ultima ora, commissione 0,05% per lato, scarto di prezzo **doppio** su tutti i trade (prudente), funding; per G1 le due
gambe (la moneta e BTC per β). Il caso: `motore5.caso` (stessa moneta, stesso mese, stessa direzione, 20 ripetizioni).

## Le varianti (giudicate insieme)

| Variante | Cella | Verso | Lordo in E-101 | Trade | t |
|---|---|---|---|---|---|
| J-002a | `F1 w4 k4 su h72` | segue | +4.046% | 372 | 4.11 |
| J-002b | `F1 w4 k3 su h72` | segue | +3.043% | 772 | 3.97 |
| J-002c | `F1 w1 k3 su h24` | segue | +1.443% | 1628 | 3.87 |

## Le monete e l'esame

* **C2**: le 24 monete della fase 2 (le stesse dell'esplorazione); netto con l'intervallo sopra zero e meglio del caso.
* **V2** (2025-07-01 → 2026-09-30, una volta): le 100 di `universo_top100.json`; l'esame della sezione 7 (p ≤ 0,005 / 3, costi doppi,
  senza il giorno migliore, tutte e due le metà, 60% delle monete con almeno 20 trade, almeno 200 trade).
