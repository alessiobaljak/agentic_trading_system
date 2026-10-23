# Programma 7 — tredicesima prova: G1 con il funding fresco (G11)

Scritto il 23 ottobre 2026, **prima del calcolo**. Idea 32 della coda di `research/REGISTRO.md` (in giornata, ogni giorno).

## 1. Perché

Il revisore indipendente (`programma6/CONTROLLO_PARITA.md`) ha trovato che l'ultimo regolamento del funding porta circa 0,2 di
Sharpe a F5: il segnale fresco conta. G1 (prova 57) decide ogni giorno con il funding dei 7 giorni; qui al funding dei 7 giorni si
affianca quello **dell'ultimo giorno** (i tre regolamenti più recenti), con lo stesso peso. **Riserva:** è una variante di G1 nata da
un numero visto (quello del revisore, sugli stessi dati): si giudica come una prova nuova nel conto, ma se passasse la soglia non la
si chiamerebbe una scoperta indipendente da F5.

## 2. La regola (tutto come G1 tranne il segnale)

* Ogni giorno alle 00:00 UTC, fra le 100 della settimana: segnale = **media dei ranghi** di −funding dei 7 giorni e di −funding
  dell'ultimo giorno (`terza.ranghi`); banda 20%/40%, pesi secondo l'inverso della volatilità dei 30 giorni, ogni lato al 100%;
  ordini limite come G1. Dal 4 gennaio 2021 al 4 ottobre 2026. Nel conto diventano **134**.

## 3. L'esame

Come G1: `terza.esame` e `terza.esito`, Sharpe corretto con l'aggiunta del 23 ottobre, soglia 0,95; accanto G1 sulle stesse
settimane, le entrate e uscite al giorno e le spese.
