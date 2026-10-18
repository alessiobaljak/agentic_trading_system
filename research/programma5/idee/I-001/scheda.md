# I-001 — Rimbalzo dopo i crolli fatti di liquidazioni

Scheda scritta il 18 ottobre 2026 **prima di qualunque calcolo su questa idea** (REGOLE.md, sezione 6).

## Perché

In un crollo violento chi è long a leva viene liquidato: le vendite forzate spingono il prezzo sotto il livello che i
compratori sono disposti a pagare, e appena le liquidazioni finiscono il prezzo risale. Se è così, i crolli che rimbalzano
di più sono quelli in cui **l'interesse aperto cala** mentre il prezzo crolla (posizioni chiuse a forza), non quelli in cui
cresce (posizioni nuove che vendono). La prima analisi dello scalping (`research/scalping/risultati.md`) ha visto un
rimbalzo medio dello 0,48% in 60 minuti dopo i crolli estremi del 2020-2022, forte nel 2021 e debole nel 2022: è da lì che
nasce l'idea, ed è dichiarato (quei dati sono già visti).

## La regola

* **Monete**: le 12 del programma. **Dati**: candele da 1 minuto e file `metrics` (interesse aperto ogni 5 minuti). Le
  decisioni si prendono solo nei minuti in cui c'è il dato dell'interesse aperto: per il periodo C, BTC da settembre 2020,
  le altre da dicembre 2021.
* **Crollo** alla chiusura del minuto t: rendimento degli ultimi 5 minuti ln(chiusura_t / chiusura_{t−5}) **minore di −L
  volte** la mediana del valore assoluto dello stesso rendimento nelle 1.440 finestre delle 24 ore prima (come in
  `research/scalping/regole.md`); tutti i 6 minuti presenti.
* **Liquidazioni**: variazione dell'interesse aperto (in quantità, `sum_open_interest`) fra le ultime due rilevazioni di 5
  minuti note al minuto t (orario ≤ t), nel **5% più negativo** delle stesse variazioni dei 30 giorni prima.
* **Ingresso**: long all'apertura del minuto t+1, a mercato. **Uscita**: alla chiusura del 60° minuto, senza stop e senza
  target. Dopo un ingresso, nessun altro sulla stessa moneta per 60 minuti.
* **Costi**: quelli del programma (REGOLE.md, sezione 5), con lo scarto di prezzo doppio (è sempre un'esplosione) e il
  funding se il trade attraversa un regolamento.

## Le varianti (3, giudicate insieme)

| Variante | L (crollo) | Condizione sull'interesse aperto |
|---|---|---|
| I-001a | 16 | sì (5% più negativo) |
| I-001b | 8 | sì (5% più negativo) |
| I-001c | 16 | nessuna (il crollo da solo, per confronto) |

## Il confronto con il caso

Gli stessi trade (stessa moneta, stesso mese, long, 60 minuti) a minuti presi a caso, 20 ripetizioni (`motore5.caso`).

## Cosa si scrive dopo il calcolo su C

`C.md`: per variante, trade, netto medio, intervallo, p, contro il caso, per moneta e per anno; poi, se una variante supera
il punto 1 dell'esame, `congelata.md` con la regola e l'impronta del codice, prima di aprire V.
