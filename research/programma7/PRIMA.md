# Programma 7 — prima prova: F5 ogni giorno (G1)

Scritto il 23 ottobre 2026, **prima del calcolo**. Idea 1 di `METODO.md`.

## 1. Perché

F5 decide una volta a settimana. Il funding si regola tre volte al giorno e la revisione indipendente ha trovato che il segnale
fresco conta (il regolamento delle 00:00 del lunedì porta circa 0,2 di Sharpe; il lunedì è il giorno migliore di F5, +0,31%,
`RISULTATI_CALENDARIO.md`). Decidendo ogni giorno il segnale è sempre fresco e il sistema opera ogni giorno: entra nelle monete
che arrivano nella banda ed esce da quelle che la lasciano. Il rischio è il costo: decidere ogni giorno fa girare di più il
capitale (la prova 16, il modello ogni giorno, è stata bocciata per le spese).

## 2. La regola (valori fissati qui, tutti uguali a F5 tranne il giorno)

* **Ogni giorno alle 00:00 UTC**: le monete dell'universo della settimana (le 100 più scambiate, come F5), segnale −funding dei 7
  giorni prima (fino al regolamento delle 00:00 compreso, `sesta.funding_7` con le parità corrette), volatilità dei 30 giorni prima;
  banda 20%/40%, pesi secondo l'inverso della volatilità, ogni lato al 100%.
* **Esecuzione**: ogni variazione di peso del giorno (con i pesi che derivano col prezzo) come ordine limite all'apertura delle
  00:00 valido un'ora, poi a mercato all'apertura delle 01:00 con il movimento contro (come la prova 56); senza candele a 1 ora, a
  mercato. Si riporta anche la versione tutta a mercato.
* Funding vero di ogni giorno. Dal 4 gennaio 2021 al 4 ottobre 2026. Una prova: nel conto diventano **120**.

## 3. L'esame

I rendimenti giornalieri si sommano per settimana (dal lunedì alla domenica) e si esaminano con `terza.esame` e `terza.esito`,
Sharpe corretto con l'aggiunta del 23 ottobre, soglia 0,95. Si riportano: le monete che entrano e escono ogni giorno, la durata
media di una posizione, il giro e le spese l'anno, e F5 (settimanale, parità corrette) sulle stesse settimane.
