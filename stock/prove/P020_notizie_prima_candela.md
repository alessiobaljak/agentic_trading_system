# Prova 20 — la prima candela sulle azioni con una notizia (bilanci, S&P 500)

Regole scritte il 25 ottobre 2026 **prima di qualsiasi calcolo** su questa idea (idea I21 di `REGISTRO.md`, chiesta dal proprietario:
«procedi con le azioni con notizie»), committate prima di lanciare il programma. Famiglia: in giornata, seguendo l'apertura (come le
prove 2 e 17): il periodo chiuso di questa famiglia è consumato; se passa la ricerca, la conferma è il demo. Conta come **1 prova** (50).

## Perché dovrebbe funzionare, e perché qui più che nella prova 17

La prova 17 (la prima candela su SPY e QQQ) aveva un vantaggio prima dei costi (QQQ, 5 minuti: Sharpe 0,88) ma troppo piccolo per i
costi di ogni giorno. Il vantaggio di questa regola dovrebbe essere più grande dove c'è una ragione per muoversi: il giorno di un bilancio,
quando all'apertura il prezzo salta, gli ordini accumulati nella notte continuano ad arrivare per ore. Zarattini, Barbon, Aziz, «A
profitable day trading strategy for the U.S. equity market» (SSRN 2024) lo trovano sulle «azioni in gioco». **Sospetto scritto prima:**
è dello stesso gruppo delle prove 2 e 17, che sul periodo successivo non hanno retto; le azioni che saltano hanno scarti più larghi di
quelli misurati nei giorni normali.

## La regola

* **Gli eventi:** i comunicati sui risultati (moduli 8-K con la voce 2.02, data di deposito d, `stock/dati/bilanci.py`) delle aziende
  dell'S&P 500 di quel giorno (codice SEC dai moduli dei dirigenti, che riportano codice e simbolo di allora).
* **In gioco:** il primo fra il giorno di borsa d (o il primo dopo, se d non è di borsa) e il giorno di borsa dopo in cui l'apertura (prima
  barra delle 9:30) dista almeno il **2%** dalla chiusura della seduta prima. Un solo giorno per evento. Il salto si vede alle 9:30: niente
  dati del futuro.
* **Operazione:** la regola della prova 17 con la candela di 5 minuti: direzione della candela 9:30-9:34, ingresso a mercato alle 9:35,
  stop all'altro estremo della candela (valido già nella barra dell'ingresso), obiettivo 10 volte il rischio, uscita alle 15:59.
* **Quanto:** ogni operazione usa il **10%** del valore del conto all'inizio del giorno, al massimo 10 operazioni nello stesso giorno (se
  sono di più, prima i salti più grandi). Le operazioni si simulano una per una (non ci sono posizioni di notte); il rendimento del giorno
  è la somma dei loro risultati per il loro peso.
* **Periodo:** 2016-2024. Barre al minuto di Alpaca, solo i giorni degli eventi.

## Costi ed esame

Costi come la prova 11 (scarto misurato per i 34 titoli, metà scarto 5 punti base e 2 di slittamento per gli altri; Interactive
Brokers «fisso»; costi doppi). Passa la ricerca se sono vere **tutte**: (1) Sharpe annuo con i costi più alto del tenere lo SPY e del
tenere l'indice a pesi uguali; (2) Sharpe corretto ≥ 0,95; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei 32 trimestri in
guadagno. Da leggere: il risultato per operazione e il suo t, e lo stesso con l'obiettivo a 5R, 20R e nessuno.
