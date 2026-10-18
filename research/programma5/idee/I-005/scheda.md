# I-005 — Gli acquisti (o le vendite) aggressivi durante un'esplosione

Scheda scritta il 18 ottobre 2026 **prima di qualunque calcolo su questa idea** (REGOLE.md, sezione 6).

## Perché

In un'esplosione, se quasi tutto il volume viene da chi compra a mercato (o vende a mercato), c'è qualcuno con fretta o
con un'informazione, e il movimento continua; se il volume è equilibrato, è più probabile un movimento senza seguito. Fonte
sul principio (lo squilibrio del flusso degli ordini anticipa il prezzo nel breve): Cont, Kukanov, Stoikov (2014), «The
Price Impact of Order Book Events», Journal of Financial Econometrics. La ricerca per moneta aveva già provato lo
squilibrio degli acquisti aggressivi a candele di 15 minuti-4 ore (`docs/storia/05_ricerca_per_moneta_e_gruppo.md`, sezione
3.E): qui è a 1 minuto e solo dentro le esplosioni.

## La regola

* **Esplosione**: |ln(chiusura_t / chiusura_{t−5})| > 8 volte la mediana di |r5| delle 24 ore prima.
* **Squilibrio**: quota del volume comprato a mercato sui 5 minuti dell'esplosione = somma `taker_buy_volume` / somma
  `volume` delle candele da 1 minuto t−4…t.
* **Ingresso** nella direzione dell'esplosione, all'apertura del minuto t+1, solo se lo squilibrio è dalla stessa parte
  (vedi varianti); **uscita** a tempo; pausa per moneta pari alla durata (almeno 60 minuti); costi con scarto doppio;
  funding.

## Le varianti (3)

| Variante | Squilibrio richiesto | Uscita |
|---|---|---|
| I-005a | quota ≥ 0,70 nelle salite, ≤ 0,30 nelle discese | 15 minuti |
| I-005b | quota ≥ 0,70 / ≤ 0,30 | 60 minuti |
| I-005c | quota ≥ 0,80 / ≤ 0,20 | 15 minuti |
