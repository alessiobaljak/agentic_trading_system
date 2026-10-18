# I-004 — Il posizionamento della folla agli estremi (rapporti long/short), orizzonte un giorno

Scheda scritta il 18 ottobre 2026 **prima di qualunque calcolo su questa idea** (REGOLE.md, sezione 6).

## Perché

Quando quasi tutti i conti sono dalla stessa parte (rapporto long/short dei conti agli estremi), il mercato è affollato:
chi doveva comprare ha già comprato, e il prezzo tende ad andare contro la folla. I conti più grandi (i «top trader» di
Binance) sono invece spesso dalla parte giusta: seguirli è l'idea opposta. Non conosco una fonte accademica precisa
precedente al 2024 su questi dati di Binance: è un'idea diffusa fra i trader, ed è dichiarato.

## La regola

* **Dati**: file `metrics`, colonne `count_long_short_ratio` (tutti i conti) e `sum_toptrader_long_short_ratio`
  (posizioni dei conti più grandi). Si decide **una volta al giorno, alla chiusura delle 00:00 UTC**, con l'ultima
  rilevazione nota (orario ≤ 00:00).
* **Estremo**: il valore nel 10% più alto (o più basso) dei 90 giorni prima (stessa ora, una rilevazione al giorno).
* **Ingresso** all'apertura del minuto 00:01, a mercato; **uscita** dopo 24 ore (1.440 minuti), senza stop. Costi del
  programma (senza scarto doppio: non è un'esplosione) e funding.

## Le varianti (3)

| Variante | Rapporto | Regola |
|---|---|---|
| I-004a | tutti i conti | contro la folla: short se nel 10% più alto, long se nel 10% più basso |
| I-004b | conti grandi | con i conti grandi: long se nel 10% più alto, short se nel 10% più basso |
| I-004c | tutti e due | long se i conti grandi sono nel 10% più alto **e** tutti i conti non lo sono; short al contrario |
