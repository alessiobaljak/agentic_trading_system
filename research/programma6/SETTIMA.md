# Programma 6 — settima prova: conferma del funding fra monete sulle monete dalla 101ª alla 200ª

Scritto il 19 ottobre 2026, subito dopo la sesta prova e **prima di qualunque calcolo** di questa. Vale `SESTA.md` dove
qui non si dice altro.

## 1. Perché

La sesta prova (`RISULTATI_SESTA.md`) ha la prima strategia che passa quasi tutto l'esame: **F2**, il funding fra monete a
pesi uguali, fra le 100 monete più scambiate di ogni settimana: +47,5% l'anno dal 2021, Sharpe 1,03, intervallo della media
settimanale +0,15%; +1,71% (sopra zero), positiva in 6 anni su 6 e nell'ultimo anno, a costi doppi, quasi senza legame col
Bitcoin (beta −0,03). Le manca solo lo **Sharpe corretto** per le 26 prove del programma (0,66 contro 0,95).

Lo Sharpe corretto serve a non credere alla migliore di tante prove fatte sugli stessi dati. La risposta pulita è provare
la **stessa regola, senza cambiare niente**, su dati che questa regola non ha mai visto: le monete **dalla 101ª alla 200ª**
per volume di ogni settimana (stessa costruzione dell'universo, posizioni 101-200 invece di 1-100). Nessuna prova del
programma 6 ha usato il funding come segnale su queste monete.

## 2. Le regole

* Ogni lunedì, con i dati fino alla domenica: le monete ammesse come nella terza prova (almeno 200 giorni di candele, la
  candela della domenica, mediana del volume dei 30 giorni prima di almeno 2 milioni), ordinate per quella mediana;
  si prendono le posizioni **dalla 101ª alla 200ª**. Si opera solo con almeno 20 monete.
* Segnale: la somma del funding dei 7 giorni prima (come la sesta prova).
* Long il quinto con il funding più basso, short il quinto più alto, **pesi uguali**, lato long +1 e short −1.
* **Costi più alti**, perché sono monete meno scambiate: commissione 0,05% e **scarto 0,10%** a ogni lato su ogni variazione
  di peso; funding con il segno della posizione.

## 3. L'esame (una regola sola, una prova sola)

Sulle settimane dal 4 gennaio 2021 all'ultima completa in cui ci sono almeno 20 monete. **Confermata** se tutte e cinque:

1. rendimento netto settimanale medio positivo con l'intervallo al 95% sopra zero e **p ≤ 0,01** a una coda (bootstrap
   a blocchi di 4 settimane, 10.000 volte);
2. positiva in almeno i **tre quarti degli anni** con almeno 26 settimane operate, e nell'ultimo anno (dal 2025-10-01);
3. positiva a **costi doppi**;
4. positiva **senza le 5 settimane migliori**;
5. positiva sia nella parte che viene dal prezzo **o** almeno con il prezzo non sotto −50% del funding incassato (cioè il
   guadagno non è solo funding pagato da monete che poi salgono il doppio): si riportano le due parti e la condizione è
   prezzo ≥ −0,5 × funding incassato, sull'intero periodo.

Si riporta anche la correlazione settimanale con F2 sulle stesse settimane.
