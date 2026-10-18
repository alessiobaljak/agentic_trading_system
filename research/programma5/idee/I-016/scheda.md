# I-016 — Reti d'acquisto sotto il prezzo (ordini limite che prendono le code dei crolli)

Scheda scritta il 18 ottobre 2026 **prima del calcolo di questa idea nel motore a minuti** (REGOLE.md, sezioni 6 e 6bis).

## Da dove viene

Dall'esplorazione **E-002** (reti di ordini limite, `research/programma5/esplorazione/E-002/risultati.md`): 11 celle
promosse su 96, tutte dal lato dell'acquisto. **Trovata cercando** sul periodo C: a dire se è vera sarà la validazione sul
2023, poi il periodo recente. È lo stesso fenomeno di I-010 (il rimbalzo dopo i crolli), preso con un ordine fermo
invece che a mercato a fine ora.

## Perché

Nei crolli rapidi le vendite forzate attraversano il libro degli ordini e stampano prezzi molto sotto il valore per pochi
secondi o minuti (le code delle candele). Un ordine d'acquisto fermo molto sotto il prezzo si esegue solo lì, al prezzo
peggiore per chi vende di forza, e paga la commissione bassa da ordine limite. Il rischio è il crollo vero che continua:
lo misura il calcolo.

## La regola

* **Monete**: le 12 del programma; barre di un'ora (`strumenti/ore.py`) per il livello, candele da 1 minuto per
  l'esecuzione.
* All'inizio di ogni ora t (del periodo) un ordine limite d'acquisto a `P · exp(−k·σ)`, con P = chiusura dell'ora t−1 e
  σ = deviazione standard dei rendimenti orari delle 720 ore fino all'ora t−1 (almeno 500). Vale 60 minuti.
* **Esecuzione prudente** (`motore5.simula_limite`): solo se il minimo di un minuto è strettamente sotto il livello;
  prezzo = il livello; commissione 0,02%, niente scarto all'ingresso.
* **Uscita** a mercato alla chiusura del minuto H dopo il minuto dell'esecuzione: commissione 0,05% e scarto doppio.
  Funding se il trade attraversa un regolamento. Mentre il trade è aperto non si mettono ordini nuovi su quella moneta.
* **Il caso** (`motore5.caso_limite`): ingresso all'apertura di un minuto qualunque della stessa moneta e dello stesso
  mese, stessa durata e stessi costi (20 ripetizioni).

## Le varianti (giudicate insieme)

| Variante | k | H (minuti) | In E-002 (lordo, trade, t) |
|---|---|---|---|
| I-016a | 6 | 240 | +1,79%, 916, 4,65 |
| I-016b | 4 | 240 | +0,92%, 2.509, 4,55 |
| I-016c | 3 | 15 | +0,28%, 6.713, 4,53 |
