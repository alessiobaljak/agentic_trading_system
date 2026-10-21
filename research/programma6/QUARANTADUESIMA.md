# Programma 6 — quarantaduesima prova: F5 con l'esposizione secondo l'agitazione (F6)

Scritto il 21 ottobre 2026, primo pomeriggio, **prima del calcolo**. Si calcola dopo la prova 41 (il conto delle prove
deve contenerla).

## 1. Perché

F5 (il funding fra monete con la banda, prova 24) è la strategia più solida: Sharpe 1,93, ma lo Sharpe corretto per le
prove è 0,81, sotto 0,95. Un metodo pubblicato, provato su molti fattori di borsa, migliora lo Sharpe senza cambiare la
strategia: **tenere meno quando le settimane sono agitate e di più quando sono calme** (Moreira e Muir, «Volatility-Managed
Portfolios», Journal of Finance 2017; per il momentum Barroso e Santa-Clara 2015). Il motivo: l'agitazione si ripete da una
settimana all'altra, il guadagno no; le perdite grandi arrivano nelle settimane agitate. Non si sceglie niente sul passato
di F5: la finestra e il tetto sono fissati qui.

## 2. La regola (valori fissati qui)

* La serie settimanale di F5 (`risultati_ventiquattresima/settimane_F5.csv.gz`, già con i costi).
* Ogni settimana: **σ** = deviazione dei rendimenti netti di F5 delle **13 settimane prima** (almeno 8), all'anno (×√52).
  Esposizione **w = 0,30 / σ**, al massimo **2** (il margine), senza minimo; con meno di 8 settimane w = 1.
* Rendimento della settimana: w × netto di F5, meno il costo del cambio d'esposizione: |w − w della settimana prima| × 2
  (le due parti, long e short, ciascuna al 100%) × 0,07% (commissione 0,05% più 0,02% di scarto). A costi doppi: w × il
  netto a costi doppi di F5 meno il doppio di quel costo.
* Dal 4 gennaio 2021 al 5 ottobre 2026 (come F5). Una prova: nel conto del programma 6 diventano **65**.

## 3. L'esame

`terza.esame` e `terza.esito` come F5 (intervallo sopra zero, Sharpe corretto sulle **65** prove almeno 0,95, 4 anni su 6,
ultimo anno, costi doppi, trimestri, più del Bitcoin). Si riportano anche: F5 sulle stesse settimane, l'esposizione media,
minima e massima, quante settimane al tetto, la discesa peggiore.
