# I-012 — Il rimbalzo dopo un'ora di volume enorme in discesa

Scheda scritta il 18 ottobre 2026 **prima del calcolo di questa idea nel motore a minuti** (REGOLE.md, sezioni 6 e 6bis).

## Da dove viene

Dall'esplorazione **E-001, famiglia F9 (volume) dal lato «giù», verso «contro»** (`research/programma5/esplorazione/E-001/risultati.md`): una cella promossa dai criteri
scritti prima. È stata **trovata cercando** fra 706 celle del periodo C: su C è quindi ottimista per costruzione, e a
dire se è vera sarà la validazione sul 2023 (soglia di p divisa per il numero di varianti), poi il periodo recente.

## Perché

Un'ora in discesa con un volume 5-10 volte il solito è un'ora di vendite affrettate (liquidazioni, stop, panico):
quando finiscono, il prezzo torna su. Il volume dice che la discesa è fatta di fretta, non di informazione lenta.

## Definizioni comuni

Barre di un'ora dalle candele da 1 minuto (`strumenti/ore.py`); σ = deviazione standard dei rendimenti orari
(logaritmici) delle 720 ore prima (almeno 500); z_w(t) = ln(C_t / C_{t−w}) / (σ_{t−w} · √w). Si decide alla chiusura
dell'ora t; nel motore a minuti (`motore5.simula`) la decisione è l'ultimo minuto dell'ora t, l'ingresso è a mercato
all'apertura dell'ora t+1, l'uscita alla chiusura dell'ora t+h (60·h minuti dopo l'ingresso). Dopo un ingresso, nessun
altro sulla stessa moneta per la pausa indicata (in ore). Costi del programma (REGOLE.md, sezione 5) con lo **scarto
doppio su tutti i trade** (si entra dopo una scossa: prudente) e il funding. Il caso: `motore5.caso` (stessa moneta, stesso
mese, stessa direzione, 20 ripetizioni).

## La regola

* **Evento** alla chiusura dell'ora t: volume dell'ora ≥ k volte la mediana dei volumi delle 720 ore prima (almeno
  500), e rendimento dell'ora negativo.
* **Trade**: long; uscita dopo 4 ore; pausa 4.

## Le varianti (giudicate insieme)

| Variante | k | h (ore) | In E-001 (lordo, trade, t) |
|---|---|---|---|
| I-012a | 5 | 4 | +0,48%, 3.187, 3,72 |
| I-012b | 10 | 4 | +1,16%, 771, 3,60 |
