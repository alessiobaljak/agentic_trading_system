# I-014 — Le altre monete nei tre giorni dopo uno strappo in su di BTC

Scheda scritta il 18 ottobre 2026 **prima del calcolo di questa idea nel motore a minuti** (REGOLE.md, sezioni 6 e 6bis).

## Da dove viene

Dall'esplorazione **E-001, famiglia F4 (scossa di BTC) dal lato «su», verso «segue»** (`research/programma5/esplorazione/E-001/risultati.md`): una cella promossa dai criteri
scritti prima. È stata **trovata cercando** fra 706 celle del periodo C: su C è quindi ottimista per costruzione, e a
dire se è vera sarà la validazione sul 2023 (soglia di p divisa per il numero di varianti), poi il periodo recente.

## Perché

Uno strappo di BTC in un'ora (z ≥ 4) porta denaro in tutto il mercato; le altre monete lo ricevono dopo e più a lungo
(chi compra BTC poi passa alle altre).

## Definizioni comuni

Barre di un'ora dalle candele da 1 minuto (`strumenti/ore.py`); σ = deviazione standard dei rendimenti orari
(logaritmici) delle 720 ore prima (almeno 500); z_w(t) = ln(C_t / C_{t−w}) / (σ_{t−w} · √w). Si decide alla chiusura
dell'ora t; nel motore a minuti (`motore5.simula`) la decisione è l'ultimo minuto dell'ora t, l'ingresso è a mercato
all'apertura dell'ora t+1, l'uscita alla chiusura dell'ora t+h (60·h minuti dopo l'ingresso). Dopo un ingresso, nessun
altro sulla stessa moneta per la pausa indicata (in ore). Costi del programma (REGOLE.md, sezione 5) con lo **scarto
doppio su tutti i trade** (si entra dopo una scossa: prudente) e il funding. Il caso: `motore5.caso` (stessa moneta, stesso
mese, stessa direzione, 20 ripetizioni).

## La regola

* **Monete**: le 11 diverse da BTC. **Evento** alla chiusura dell'ora t: z_1 di BTC ≥ 4.
* **Trade**: long sulla moneta; uscita dopo 72 ore; pausa 72.

## Le varianti (giudicate insieme)

| Variante | w | k | h | In E-001 (lordo, trade, t) |
|---|---|---|---|---|
| I-014a | 1 | 4 | 72 | +3,45%, 658, 3,10 |
