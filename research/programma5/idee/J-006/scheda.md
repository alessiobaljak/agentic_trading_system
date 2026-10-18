# J-006 — Il rimbalzo quando il prezzo è molto sotto il prezzo medio del giorno (monete fuori dalla fase 1)

Scheda scritta il 18 ottobre 2026 **prima del calcolo di questa idea nel motore a minuti e prima di aprire V2**
(REGOLE.md, sezioni 6bis, 7 e 7bis).

## Da dove viene

Dall'esplorazione **E-103**, famiglia W4 (prezzo medio), lato sotto, verso contro (`research/programma5/esplorazione/E-103/risultati.md`): celle promosse dai
criteri scritti prima, sul periodo C2 (2024-01-01 → 2025-06-30) e 24 monete. Trovata cercando: a dire se è vera è V2.

## Perché

Un prezzo molto sotto il prezzo medio delle ultime 24 ore pesato sul volume vuol dire una discesa rapida e recente,
fatta dopo che il grosso degli scambi del giorno era più in alto: chi ha comprato al prezzo medio è in perdita e chi vende
lo fa in fretta. È parente del rimbalzo dopo i crolli (i giorni sono gli stessi: 5 mar, 13 apr, 5 ago, 20 dic 2024; 3 feb e
7 apr 2025): su V2 si prova **solo sulle monete fuori dalla fase 1**.

## La regola

Ogni variante è **esattamente** la cella dell'esplorazione (`strumenti/esplora_fase2.py` o `esplora_calendario.py`: stessa
condizione alla chiusura dell'ora, stessa durata, stessa pausa), presa nel verso indicato, simulata nel motore a minuti
(`strumenti/idee_fase2.py`, `per_moneta_cella`): ingresso a mercato all'apertura dell'ora dopo, uscita alla chiusura
dell'ultima ora, commissione 0,05% per lato, scarto di prezzo **doppio** su tutti i trade (prudente), funding; per G1 le due
gambe (la moneta e BTC per β). Il caso: `motore5.caso` (stessa moneta, stesso mese, stessa direzione, 20 ripetizioni).

## Le varianti (giudicate insieme)

| Variante | Cella | Verso | Lordo in E-103 | Trade | t |
|---|---|---|---|---|---|
| J-006a | `W4 k1.5 sotto h24` | contro | +4.960% | 345 | 3.97 |
| J-006b | `W4 k1.5 sotto h4` | contro | +1.693% | 527 | 3.55 |

## Le monete e l'esame

* **C2**: le 24 monete della fase 2 (le stesse dell'esplorazione); netto con l'intervallo sopra zero e meglio del caso.
* **V2** (2025-07-01 → 2026-09-30, una volta): le 100 di `universo_top100.json` **tranne le 12 della fase 1** (88 monete); l'esame della sezione 7 (p ≤ 0,005 / 2, costi doppi,
  senza il giorno migliore, tutte e due le metà, 60% delle monete con almeno 20 trade, almeno 200 trade).
