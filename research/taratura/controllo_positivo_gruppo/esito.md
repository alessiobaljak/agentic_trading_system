# Controllo positivo degli strumenti di gruppo, fatto dal coordinamento (10 ottobre 2026, 20:05 UTC)

Perché: la sessione di gruppo si è fermata alle 19:12 UTC perché il suo controllo positivo (regole.md, sezione 5,
punto 10) non passava per poco (t 1,96 contro la soglia 2,07, dal riassunto della sessione). Il coordinamento ha
rifatto lo stesso controllo, con `gruppo.controllo_positivo` al commit 2a88046a, sulle 80 monete del gruppo,
periodo di costruzione, con il modulo della prova a placebo di gruppo (`placebo_gruppo/placebo_gruppo.py`) e le
sue uscite, direzione long, dati della radice della prova a placebo. Nessuna idea della campagna è stata letta.

| Timeframe e uscita | Passa | t contro la (b) senza ritardo | soglia | t contro la (a) | t con 1 barra di ritardo | trade | effetto grappolo | secondi |
|---|---|---|---|---|---|---|---|---|
| 4h, stop a 2 ATR e chiusura dopo 12 barre | sì | 6.15 | 2.03 | 3.43 | 0.74 | 24619 | 23.56 | 575 |
| 4h, stop a 1,5 ATR e target a 2,5 ATR, senza chiusura a tempo | no | non valutabile | non valutabile | non valutabile | non valutabile | 20199 | non valutabile | 462 |
| 1h, stop a 2 ATR e chiusura dopo 24 barre | sì | 6.10 | 2.03 | 4.19 | -0.25 | 61498 | 31.18 | 1934 |

Lettura: con uscite a tempo (al massimo 1-2 giorni) gli strumenti vedono il vantaggio dell'ingresso che guarda
avanti (t circa 6) e lo perdono con il ritardo di una barra: funzionano. Con un'uscita senza chiusura a tempo la
posizione più lunga allunga la finestra del blocco per tutte le monete e il confronto diventa non valutabile (meno
di 3 blocchi interi): è la regola del blocco della sezione 5, punto 2, non un errore. Consiglio al proprietario: la
strada 2 della sessione (rifare il controllo con uscita a 1 giorno).
