# I-011 — La rottura del massimo di 60 giorni

Scheda scritta il 18 ottobre 2026 **prima del calcolo di questa idea nel motore a minuti** (REGOLE.md, sezioni 6 e 6bis).

## Da dove viene

Dall'esplorazione **E-001, famiglia F5 (rottura) dal lato «su», verso «segue»** (`research/programma5/esplorazione/E-001/risultati.md`): una cella promossa dai criteri
scritti prima. È stata **trovata cercando** fra 706 celle del periodo C: su C è quindi ottimista per costruzione, e a
dire se è vera sarà la validazione sul 2023 (soglia di p divisa per il numero di varianti), poi il periodo recente.

## Perché

Quando il prezzo supera il massimo dei 60 giorni prima, chi aspettava fuori entra (tendenza, notizie, chi chiude gli
short): il movimento continua nei giorni dopo. È la regola più antica del trading di tendenza; nelle cripto è documentata
(per esempio Liu e Tsyvinski, «Risks and Returns of Cryptocurrency», 2021, sul momento a 1-4 settimane).

## Definizioni comuni

Barre di un'ora dalle candele da 1 minuto (`strumenti/ore.py`); σ = deviazione standard dei rendimenti orari
(logaritmici) delle 720 ore prima (almeno 500); z_w(t) = ln(C_t / C_{t−w}) / (σ_{t−w} · √w). Si decide alla chiusura
dell'ora t; nel motore a minuti (`motore5.simula`) la decisione è l'ultimo minuto dell'ora t, l'ingresso è a mercato
all'apertura dell'ora t+1, l'uscita alla chiusura dell'ora t+h (60·h minuti dopo l'ingresso). Dopo un ingresso, nessun
altro sulla stessa moneta per la pausa indicata (in ore). Costi del programma (REGOLE.md, sezione 5) con lo **scarto
doppio su tutti i trade** (si entra dopo una scossa: prudente) e il funding. Il caso: `motore5.caso` (stessa moneta, stesso
mese, stessa direzione, 20 ripetizioni).

## La regola

* **Evento** alla chiusura dell'ora t: C_t > massimo dei massimi orari delle 1.440 ore prima (almeno 1.428 presenti).
* **Trade**: long; uscita dopo 72 ore; pausa 72.

## Le varianti (giudicate insieme)

| Variante | N (giorni) | h (ore) | In E-001 (lordo, trade, t) |
|---|---|---|---|
| I-011a | 60 | 72 | +5,73%, 327, 4,10 |

Una sola variante: è l'unica cella della famiglia promossa.
