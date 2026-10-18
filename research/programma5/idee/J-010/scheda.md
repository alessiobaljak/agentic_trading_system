# J-010 — Reti d'acquisto sotto il prezzo con uscita a mercato (monete fuori dalla fase 1)

Scheda scritta il 18 ottobre 2026 **prima del calcolo di questa idea nel motore a minuti e prima di aprire V2**
(REGOLE.md, sezioni 6bis, 7 e 7bis).

## Da dove viene

Dall'esplorazione **E-102** (`research/programma5/esplorazione/E-102/risultati.md`), celle promosse sul periodo C2 e 24
monete. Trovata cercando: a dire se è vera è V2.

## Perché

Come J-009 ma con l'uscita a mercato dopo un'ora o un giorno: si compra nelle code dei crolli e si tiene il
rimbalzo. Parente del rimbalzo dopo i crolli: su V2 **solo sulle monete fuori dalla fase 1**.

## La regola

Ogni variante è esattamente la cella di E-102 (`strumenti/esplora_limiti.py`), simulata nel motore a minuti
(`strumenti/idee_fase2.py`, `per_moneta_rete`): all'inizio di ogni ora un ordine limite d'acquisto a `P·exp(−k·σ)` (P
chiusura dell'ora prima, σ dei rendimenti orari delle 720 ore fino all'ora prima), valido 60 minuti, eseguito solo ad
attraversamento al livello (0,02%, niente scarto). Tipo **S**: uscita a limite a `L·exp(m·σ)` dal minuto dopo, ad
attraversamento (0,02%), altrimenti a mercato dopo H minuti (0,05% e scarto doppio). Tipo **R**: uscita a mercato dopo H
minuti (0,05% e scarto doppio). Funding. Mentre il trade è aperto, nessun ordine nuovo sulla moneta. Il caso:
`motore5.caso_limite` (R) o `scalping.caso_doppio` (S).

## Le varianti (giudicate insieme)

| Variante | Cella | In E-102 (lordo R / netto S) | Trade | t |
|---|---|---|---|---|
| J-010a | `R acquisto k6 H1440` | +2.692% | 715 | 3.74 |
| J-010b | `R acquisto k3 H60` | +0.309% | 5891 | 3.42 |
| J-010c | `R acquisto k3 H1440` | +1.140% | 3192 | 3.10 |

## Le monete e l'esame

* **C2**: le 24 monete della fase 2; netto con l'intervallo sopra zero e meglio del caso.
* **V2** (una volta): le 100 di `universo_top100.json` **tranne le 12 della fase 1** (88 monete); l'esame della sezione 7
  (p ≤ 0,005 / 3, costi doppi, senza il giorno migliore, tutte e due le metà, 60% delle monete con almeno 20 trade,
  almeno 200 trade).
