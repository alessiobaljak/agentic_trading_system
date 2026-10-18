# I-019 — La moneta dopo una salita sua, coperta con BTC

Scheda scritta il 18 ottobre 2026 **prima di qualunque calcolo di questa idea nel motore a minuti** (REGOLE.md, sezioni
6, 6bis e 6ter).

## Da dove viene

Dall'esplorazione **E-003, famiglia G1** (scossa propria coperta con BTC), lato «su», verso «segue»: le tre celle più forti
per t del lato «su» (`research/programma5/esplorazione/E-003/risultati.md`), tutte promosse; nel 2022 (ribasso) restano
positive (+0,69% / +0,41% / +1,19%). È trovata cercando su C. **V vale come prova** (regola 6ter, punto 4): l'idea parente
senza copertura (I-013c, la stessa salita propria, long 24 ore) su V ha dato un netto di −0,000%, cioè un'informazione
contro, non a favore.

## Perché

Una moneta che sale molto più di quanto dice BTC ha una notizia o un flusso suo (una quotazione, un aggiornamento, un
fondo che compra): l'informazione si diffonde piano, e la moneta continua a fare meglio del mercato nei giorni dopo.
Coprendo con BTC si guadagna solo la parte propria, qualunque cosa faccia il mercato (I-013c senza copertura nel 2023
faceva quanto il mercato).

## La regola

* **Monete**: le 11 diverse da BTC; barre di un'ora. β, σ_e e e_w come I-015 (`../I-015/scheda.md`).
* **Evento** alla chiusura dell'ora t: e_w(t) / (σ_e(t−w)·√w) ≥ k.
* **Trade coperto**: long la moneta per 1, short BTC per β(t−w), a mercato all'apertura dell'ora t+1; uscita dei due alla
  chiusura dell'ora t+h; costi delle due gambe con lo scarto doppio, funding delle due gambe; pausa max(w, h).
* **Il caso**: le stesse due gambe con lo stesso β e la stessa durata a un minuto qualunque della stessa moneta e dello
  stesso mese (20 ripetizioni).

## Le varianti (giudicate insieme) e l'esame

| Variante | w | k | h | In E-003 (lordo coperto, trade, t) |
|---|---|---|---|---|
| I-019a | 4 | 3 | 72 | +2,80%, 734, 4,32 |
| I-019b | 4 | 2 | 24 | +1,16%, 2.103, 4,25 |
| I-019c | 4 | 2 | 72 | +1,87%, 1.371, 4,03 |

Esame (`esame.json`, regola 6ter): V con p a una coda ≤ 0,05 / 3 e positivo a costi doppi; R come la sezione 5 più
«positivo togliendo il giorno migliore».
