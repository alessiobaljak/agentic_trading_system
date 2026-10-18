# I-010 — Il rimbalzo dopo i crolli di qualche ora

Scheda scritta il 18 ottobre 2026 **prima del calcolo di questa idea nel motore a minuti** (REGOLE.md, sezioni 6 e 6bis).

## Da dove viene

Dall'esplorazione **E-001, famiglia F1 (scossa) dal lato «giù» e verso «contro»** (`research/programma5/esplorazione/E-001/risultati.md`): una cella promossa dai criteri
scritti prima. È stata **trovata cercando** fra 706 celle del periodo C: su C è quindi ottimista per costruzione, e a
dire se è vera sarà la validazione sul 2023 (soglia di p divisa per il numero di varianti), poi il periodo recente.

## Perché

Un crollo di 4-24 ore molto più grande del solito (z ≤ −k) è fatto in buona parte di vendite forzate (liquidazioni,
chiusure per margine) e di panico: il prezzo scende sotto quello che i compratori pagherebbero con calma, e nelle ore dopo
torna su. È lo stesso meccanismo del rimbalzo a 60 minuti dell'analisi dello scalping, su una scala più lunga, dove il
movimento è molto più grande dei costi.

## Definizioni comuni

Barre di un'ora dalle candele da 1 minuto (`strumenti/ore.py`); σ = deviazione standard dei rendimenti orari
(logaritmici) delle 720 ore prima (almeno 500); z_w(t) = ln(C_t / C_{t−w}) / (σ_{t−w} · √w). Si decide alla chiusura
dell'ora t; nel motore a minuti (`motore5.simula`) la decisione è l'ultimo minuto dell'ora t, l'ingresso è a mercato
all'apertura dell'ora t+1, l'uscita alla chiusura dell'ora t+h (60·h minuti dopo l'ingresso). Dopo un ingresso, nessun
altro sulla stessa moneta per la pausa indicata (in ore). Costi del programma (REGOLE.md, sezione 5) con lo **scarto
doppio su tutti i trade** (si entra dopo una scossa: prudente) e il funding. Il caso: `motore5.caso` (stessa moneta, stesso
mese, stessa direzione, 20 ripetizioni).

## La regola

* **Evento** alla chiusura dell'ora t: z_w(t) ≤ −k.
* **Trade**: long; uscita dopo h ore; pausa max(w, h).

## Le varianti (giudicate insieme)

| Variante | w (ore) | k | h (ore) | In E-001 (lordo, trade, t) |
|---|---|---|---|---|
| I-010a | 4 | 5 | 12 | +2,68%, 283, 4,23 |
| I-010b | 4 | 4 | 12 | +1,73%, 522, 3,37 |
| I-010c | 24 | 3 | 4 | +2,49%, 327, 3,26 |
