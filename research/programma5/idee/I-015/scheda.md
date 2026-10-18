# I-015 — La moneta dopo una discesa sua, coperta con BTC

Scheda scritta il 18 ottobre 2026 **prima del calcolo di questa idea nel motore a minuti** (REGOLE.md, sezioni 6 e 6bis).

## Da dove viene

Dall'esplorazione **E-003, famiglia G1** (scossa propria coperta con BTC), lato «giù», verso «contro»
(`research/programma5/esplorazione/E-003/risultati.md`): 26 celle promosse su 185, tutte di G1. È stata **trovata
cercando** sul periodo C: a dire se è vera sarà la validazione sul 2023, poi il periodo recente. È parente di I-013 (la
stessa scossa senza copertura): qui il movimento di tutto il mercato è tolto con BTC, ed è il motivo per cui la cella
regge anche nel 2022.

## Perché

Una moneta che scende da sola, molto più di quanto dice BTC, è spesso venduta in fretta da pochi (una notizia, una
liquidazione su quella moneta, un fondo che esce): il prezzo va sotto il valore relativo agli altri e poi torna. Coprendo
con BTC si guadagna solo se la moneta recupera **rispetto al mercato**, qualunque cosa faccia il mercato.

## La regola

* **Monete**: le 11 diverse da BTC; barre di un'ora (`strumenti/ore.py`). β = covarianza / varianza dei rendimenti orari
  con BTC nelle 720 ore prima (almeno 500); σ_e = deviazione standard dei residui orari e_1 = r_1 − β·r_1(BTC) nelle stesse
  ore; e_w(t) = ln(C_t/C_{t−w}) − β(t−w)·ln(B_t/B_{t−w}) (B = BTC).
* **Evento** alla chiusura dell'ora t: e_w(t) / (σ_e(t−w) · √w) ≤ −k.
* **Trade coperto**: long la moneta per 1 di valore, short BTC per β(t−w) di valore, tutti e due a mercato all'apertura
  dell'ora t+1; uscita dei due alla chiusura dell'ora t+h. Rendimento per unità di valore della moneta: lordo della moneta
  + β · lordo dello short di BTC, meno i costi delle due gambe (commissione e scarto doppio su tutte e due: prudente), meno
  il funding delle due gambe. Pausa max(w, h) per moneta.
* **Il caso**: le stesse due gambe, con lo stesso β e la stessa durata, a un minuto qualunque della stessa moneta e dello
  stesso mese (20 ripetizioni).

## Le varianti (giudicate insieme)

| Variante | w (ore) | k | h (ore) | In E-003 (lordo coperto, trade, t) |
|---|---|---|---|---|
| I-015a | 1 | 3 | 4 | +0,63%, 1.686, 4,93 |
| I-015b | 4 | 2 | 24 | +0,98%, 1.860, 4,72 |
| I-015c | 1 | 2 | 24 | +0,95%, 2.919, 4,56 |
