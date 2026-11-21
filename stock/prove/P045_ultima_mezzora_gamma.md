# Prova 45 — l'ultima mezz'ora segue la giornata, solo nei giorni in cui chi vende opzioni deve inseguire il prezzo (SPY)

Regole scritte il 21 novembre 2026 **prima di qualsiasi calcolo sui prezzi** (idea I52 di `REGISTRO.md`). Visti prima solo i conteggi
del dato nuovo: la copertura delle opzioni sull'S&P 500 stimata da SqueezeMetrics (colonna `gex` di
`squeezemetrics.com/monitor/static/DIX.csv`, dal 2 maggio 2011) è **sotto zero in 256 giorni su 2'264** dal 2016 al 2024. Si conosceva
la prova 1 (la stessa regola in tutti i giorni: bocciata, il vantaggio prima dei costi era piccolo, circa 0,5 punti base al giorno, e i
costi circa 1,7 punti base a operazione) e l'idea I8 (uscire all'asta di chiusura per pagare meno). Contano come **2 prove** (la
strategia da sola, e la miscela con lei).

## Perché dovrebbe funzionare

Baltussen, Da, Lammers e Martens, «Hedging demand and market intraday momentum», Journal of Financial Economics 142 (2021): la
direzione della giornata continua nell'ultima mezz'ora **soprattutto quando chi vende opzioni ha una copertura negativa** (deve
comprare quando il prezzo sale e vendere quando scende, e lo fa verso la chiusura). In 60 mercati; sull'S&P 500 dal 1974. Barbon,
Beckmeyer, Buraschi e Moerke (working paper SFI 22-40, 2022, letto dall'agente di ricerca): la spinta della copertura delle opzioni a
fine giornata resta dopo i costi (Sharpe 1,76 nel 2012-2019), a differenza di quella dei fondi a leva. La prova 1 ha mescolato i giorni
buoni con tutti gli altri; qui si guardano **solo i giorni con la copertura sotto zero**, e si esce all'asta di chiusura (nessuno scarto).

**Sospetti scritti prima:**

* **il dato è una stima** di una società privata (presume che i venditori di opzioni siano sempre gli intermediari), non la copertura
  vera; può sbagliare proprio nei giorni che contano;
* **pochi giorni** (circa 256, l'11%), concentrati in tre periodi (fine 2018, 2020, 2022): il risultato può venire da un solo periodo;
* **giorni agitati**: l'ultima mezz'ora è più larga, e un errore di direzione costa di più;
* **l'idea è pubblicata dal 2018** (Gao e altri) e dal 2021 (Baltussen e altri): può essere stata consumata.

## I dati

* **La copertura:** la colonna `gex` di SqueezeMetrics, scaricata dal lavoro di GitHub, mai nel repository. Il valore con la data del
  **giorno di borsa prima** (pubblicato prima dell'apertura del giorno dopo) decide il giorno.
* **Lo SPY:** le barre al minuto non rettificate di Alpaca (tutte le borse), solo dentro la seduta, e il calendario di borsa di Alpaca
  (chiusure anticipate comprese), come la prova 1; la **chiusura ufficiale** dalla barra al giorno di Alpaca.

## La regola

* **Il giorno:** si opera solo se la copertura del giorno di borsa prima è **sotto zero**.
* **Il segnale** (come la prova 1): r = chiusura della barra che finisce mezz'ora prima della chiusura / chiusura dell'ultima barra della
  seduta di ieri − 1. Se r > 0 si compra, se r < 0 si vende allo scoperto, se r = 0 niente.
* **L'ingresso:** a mercato, all'apertura della barra dopo (di solito le 15:30).
* **L'uscita:** **all'asta di chiusura** (ordine «alla chiusura»): il prezzo è la chiusura ufficiale del giorno. Nessuna posizione resta
  aperta di notte.
* **Quanto:** il 98% del valore del conto diviso per il prezzo del segnale, azioni intere, niente leva (come la prova 1).
* **Giorni esclusi:** come la prova 1 (il primo giorno, i giorni segnalati dal controllo dei minuti, e quelli in cui manca la barra del
  segnale o dell'ingresso, o la chiusura ufficiale, o la copertura del giorno prima).
* **Periodo:** dal 4 gennaio 2016 al 31 dicembre 2024. Il periodo chiuso non si usa.

## I costi (come la prova 1)

All'ingresso metà dello scarto misurato (0,185 punti base) e lo slittamento di 0,5 punti base; all'asta di chiusura nessuno scarto e lo
stesso slittamento di 0,5 punti base (margine); commissioni Interactive Brokers «fisso» all'ingresso e all'uscita. Versione con tutti
i costi raddoppiati.

## L'esame (uguale alle prove 28 e 30-44)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30 rafforzata): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la
miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della
miscela e del tenere lo SPY; il t dello Sharpe della parte almeno 1,3; la miscela nuova più alta in almeno l'80% di 2000 campionamenti a
blocchi di 20 giorni.

Da leggere accanto (non cambiano l'esito): il guadagno medio per operazione prima e dopo i costi, con il t; **la stessa regola nei
giorni con la copertura sopra zero** (se lì il vantaggio è uguale, il dato della copertura non serve); la stessa regola in tutti i
giorni con l'uscita all'asta; quante operazioni per anno e il guadagno per anno.

**Se passa uno dei due esami:** revisore separato, poi il periodo chiuso (dal 2 gennaio 2025 al 30 settembre 2026) **una volta**: la
famiglia «ultima mezz'ora» non l'ha mai usato (la prova 1 è stata bocciata prima).
