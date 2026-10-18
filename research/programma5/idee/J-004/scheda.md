# J-004 — Il rimbalzo dopo i crolli di un giorno (monete fuori dalla fase 1)

Scheda scritta il 18 ottobre 2026 **prima del calcolo di questa idea nel motore a minuti e prima di aprire V2**
(REGOLE.md, sezioni 6bis, 7 e 7bis).

## Da dove viene

Dall'esplorazione **E-101**, famiglia F1 (scossa), lato giù, verso contro (`research/programma5/esplorazione/E-101/risultati.md`): celle promosse dai
criteri scritti prima, sul periodo C2 (2024-01-01 → 2025-06-30) e 24 monete. Trovata cercando: a dire se è vera è V2.

## Perché

È il rimbalzo dopo i crolli della fase 1 (vendite forzate della leva, poi il prezzo torna), su un crollo di 4-24 ore e
una tenuta di uno-tre giorni. Già provato su R sulle 12 monete della fase 1 (I-017): qui su V2 si prova **solo sulle altre
monete** (REGOLE.md, 7 e 7bis).

## La regola

Ogni variante è **esattamente** la cella dell'esplorazione (`strumenti/esplora_fase2.py` o `esplora_calendario.py`: stessa
condizione alla chiusura dell'ora, stessa durata, stessa pausa), presa nel verso indicato, simulata nel motore a minuti
(`strumenti/idee_fase2.py`, `per_moneta_cella`): ingresso a mercato all'apertura dell'ora dopo, uscita alla chiusura
dell'ultima ora, commissione 0,05% per lato, scarto di prezzo **doppio** su tutti i trade (prudente), funding; per G1 le due
gambe (la moneta e BTC per β). Il caso: `motore5.caso` (stessa moneta, stesso mese, stessa direzione, 20 ripetizioni).

## Le varianti (giudicate insieme)

| Variante | Cella | Verso | Lordo in E-101 | Trade | t |
|---|---|---|---|---|---|
| J-004a | `F1 w24 k3 giu h24` | contro | +4.843% | 268 | 3.74 |
| J-004b | `F1 w4 k5 giu h24` | contro | +4.731% | 252 | 3.28 |
| J-004c | `F1 w24 k3 giu h72` | contro | +4.538% | 250 | 3.13 |

## Le monete e l'esame

* **C2**: le 24 monete della fase 2 (le stesse dell'esplorazione); netto con l'intervallo sopra zero e meglio del caso.
* **V2** (2025-07-01 → 2026-09-30, una volta): le 100 di `universo_top100.json` **tranne le 12 della fase 1** (88 monete); l'esame della sezione 7 (p ≤ 0,005 / 3, costi doppi,
  senza il giorno migliore, tutte e due le metà, 60% delle monete con almeno 20 trade, almeno 200 trade).
