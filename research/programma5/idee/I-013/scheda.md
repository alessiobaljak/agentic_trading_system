# I-013 — La moneta dopo una scossa sua (non di BTC)

Scheda scritta il 18 ottobre 2026 **prima del calcolo di questa idea nel motore a minuti** (REGOLE.md, sezioni 6 e 6bis).

## Da dove viene

Dall'esplorazione **E-001, famiglia F3 (scossa propria)** (`research/programma5/esplorazione/E-001/risultati.md`): una cella promossa dai criteri
scritti prima. È stata **trovata cercando** fra 706 celle del periodo C: su C è quindi ottimista per costruzione, e a
dire se è vera sarà la validazione sul 2023 (soglia di p divisa per il numero di varianti), poi il periodo recente.

## Perché

Una moneta che si muove molto più di quanto dice BTC (residuo e = r_w − β·r_w(BTC) estremo) attira attenzione e
denaro: dopo una discesa propria il prezzo torna su (chi ha venduto da solo e in fretta), dopo una salita propria continua
(la notizia si diffonde). In tutti e due i casi E-001 dice: **long**.

## Definizioni comuni

Barre di un'ora dalle candele da 1 minuto (`strumenti/ore.py`); σ = deviazione standard dei rendimenti orari
(logaritmici) delle 720 ore prima (almeno 500); z_w(t) = ln(C_t / C_{t−w}) / (σ_{t−w} · √w). Si decide alla chiusura
dell'ora t; nel motore a minuti (`motore5.simula`) la decisione è l'ultimo minuto dell'ora t, l'ingresso è a mercato
all'apertura dell'ora t+1, l'uscita alla chiusura dell'ora t+h (60·h minuti dopo l'ingresso). Dopo un ingresso, nessun
altro sulla stessa moneta per la pausa indicata (in ore). Costi del programma (REGOLE.md, sezione 5) con lo **scarto
doppio su tutti i trade** (si entra dopo una scossa: prudente) e il funding. Il caso: `motore5.caso` (stessa moneta, stesso
mese, stessa direzione, 20 ripetizioni).

## La regola

* **Monete**: le 11 diverse da BTC. β = covarianza / varianza dei rendimenti orari con BTC nelle 720 ore prima (almeno
  500); σ_e = deviazione standard dei residui orari e_1 = r_1 − β·r_1(BTC) nelle stesse ore.
* **Evento** alla chiusura dell'ora t: e_w(t) / (σ_e(t−w) · √w) ≤ −k (lato giù) o ≥ +k (lato su), con β(t−w).
* **Trade**: long in tutte e tre le varianti; uscita dopo h ore; pausa max(w, h).

## Le varianti (giudicate insieme)

| Variante | w | k | lato | h | In E-001 (lordo del long, trade, t) |
|---|---|---|---|---|---|
| I-013a | 4 | 3 | giù | 1 | +0,52%, 854, 3,45 |
| I-013b | 4 | 3 | giù | 4 | +0,98%, 854, 3,11 |
| I-013c | 4 | 3 | su | 24 | +1,75%, 982, 3,10 |
