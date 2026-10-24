# Programma 8 — lo spot

Scritto il 24 ottobre 2026, **prima di qualunque calcolo**. Il proprietario: «abbiamo sempre operato in future ma mai in spot per
una mia precisa richiesta, possiamo per favore rieseguire le strategie anche in spot e vedere cosa cambia?».

## 1. Cosa cambia nello spot (fatti, non risultati)

* **Si può solo comprare.** Vendere allo scoperto richiede il margine (si prende in prestito la moneta, si pagano interessi, e
  spesso le monete nuove non si possono prendere in prestito). Quindi il lato short di F5, N3 (le monete nuove vendute al 7° giorno)
  ed E4 (il funding al tetto) nello spot non si fanno.
* **Commissioni più alte**: 0,10% a ordine (0,075% pagando con BNB), contro 0,02% (limite) e 0,05% (mercato) dei future; nello spot
  gli ordini limite non abbassano la commissione, solo lo scarto.
* **Niente funding**: nello spot non si paga né si incassa.
* **Meno monete**: solo quelle che hanno anche la coppia contro USDT a pronti su Binance (433 delle 721 del pannello).

## 2. Cosa si prova

* Il **lato long di F5** (prova 24; con le parità corrette), cioè comprare a pronti le monete dove la leva nei future costa meno
  (funding dei 7 giorni più basso): il segnale viene dai future, l'acquisto si fa a pronti. Una volta a settimana (**S1**) e ogni
  giorno come G1 (**S2**).
* Gli indicatori tecnici e lo scalping non si rifanno: nelle prove sui future perdevano già **prima** dei costi (prove 34-39, 46,
  54, 58, 60), e nello spot i costi sono più alti. Scritto qui per non perderlo.

## 3. Cosa è venuto fuori (prova 73, `RISULTATI_PRIMA.md`)

Comprare a pronti il lato long di F5 rende come il mercato delle altcoin, con le sue cadute: Sharpe 0,43 (a settimana) e 0,44 (ogni
giorno), discesa del 90-91% (2022 e 2025), contro 0,36 del paniere delle stesse monete e 0,58 del Bitcoin tenuto. La scelta delle
monete dal funding aggiunge 4-6 punti l'anno sul paniere, ma non in modo sicuro (p 0,21-0,25). **Il vantaggio di F5 sta nel tenere
insieme long e short** (il mercato si annulla e resta la differenza fra monete affollate e trascurate): nello spot, senza vendite
allo scoperto, resta solo il rischio del mercato. Per questo le strategie restano sui future; nello spot servirebbero idee diverse
(che non abbiano bisogno di vendere), da scrivere nella coda unica.
