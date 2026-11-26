# Prova 52 — vendere la volatilità quando la curva è normale: SVXY tenuto solo con il VIX sotto il VIX a tre mesi

Regole scritte il 26 novembre 2026 **prima di qualsiasi calcolo** (idea I60 di `REGISTRO.md`). Si conoscevano le prove 1-51, in
particolare la 44 (la stessa curva al contrario: VIXY comprato quando il VIX supera quello a tre mesi; bocciata, tutto il guadagno da
marzo 2020) e i dati del VIX e del VIX a tre mesi della CBOE usati lì. Contano come **2 prove** (la strategia da sola, e la miscela con
lei): 120 e 121 nel conto.

## Perché dovrebbe funzionare

Chi compra opzioni sull'indice paga in media più della volatilità che poi arriva: è il **premio per il rischio di volatilità**, un premio
per un'assicurazione, non un'anomalia (Carr e Wu, Review of Financial Studies 22, 2009; Eraker, 2009). Sui futures del VIX si vede come
una curva quasi sempre in salita: chi li vende allo scoperto e aspetta guadagna lo scivolamento verso il prezzo di oggi. Simon e
Campasano, Journal of Derivatives 21 (2014): vendere i futures del VIX quando la curva è in salita e stare fuori quando è rovesciata
rende, coperti o no. Qui la stessa idea con un fondo quotato che lo fa da solo: **SVXY** (−1 volta i futures del VIX a breve fino al 27
febbraio 2018, poi −0,5 volte).

**Sospetti scritti prima:**

* **i crolli**: il 5 febbraio 2018 i fondi come questo hanno perso fino al 90% in un giorno (uno è stato chiuso), e il marzo 2020 è
  stato pesante; il filtro della curva può arrivare tardi, perché si decide con la curva del giorno prima;
* **la parte è un'assicurazione venduta**: guadagna poco e spesso, perde tanto e di rado; un periodo di nove anni può non bastare a
  giudicarla, e lo Sharpe può sembrare buono finché non arriva il crollo;
* **il fondo è cambiato** a febbraio 2018 (da −1 a −0,5 volte): due strategie diverse nello stesso periodo;
* **la prova 44** ha già usato la stessa curva (al contrario) e la prova 15 la volatilità: stessa famiglia, il periodo chiuso
  della famiglia è già usato.

## I dati

* **La curva:** le chiusure del VIX e del VIX a tre mesi della CBOE (`VIX_History.csv` e `VIX3M_History.csv`, come la prova 44),
  scaricate dal programma, mai nel repository.
* **SVXY e SPY:** chiusure giornaliere rettificate per i dividendi (Yahoo, in locale, mai nel repository).

## La regola

* **Ogni giorno di borsa**, alla **chiusura** (asta di chiusura): se il giorno di borsa **prima** il VIX ha chiuso **sotto** il VIX a
  tre mesi, SVXY al **98%** del conto fino alla chiusura dopo; se uguale o sopra, **niente**. La curva del giorno prima perché il VIX
  chiude alle 16:15, dopo la chiusura di SVXY.
* **Il resto del conto** non rende niente. Nessuna leva.
* **Periodo:** dal 4 gennaio 2016 al 31 dicembre 2024. Il periodo chiuso non si usa.

## I costi

A ogni cambio (dentro o fuori): slittamento di **2 punti base** sulla parte comprata o venduta (all'asta di chiusura, fondo meno
scambiato dello SPY) e la commissione di Interactive Brokers «fisso». Versione con tutti i costi raddoppiati.

## L'esame (uguale alle prove 28 e 30-51)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le serie
del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela:** Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la miscela della prova 25 sotto
0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della miscela e del tenere lo SPY; il t
dello Sharpe della parte almeno 1,3, anche senza marzo 2020; la miscela nuova più alta in almeno l'80% di 2000 campionamenti a blocchi
di 20 giorni.

Da leggere accanto (non cambiano l'esito): SVXY tenuto sempre; la quota di giorni dentro; i cambi per anno; il giorno peggiore e il
mese peggiore; febbraio 2018 e marzo 2020 da soli; prima e dopo il 27 febbraio 2018; l'anno per anno; la perdita massima.

**Se passa uno dei due esami:** revisore separato; poi, poiché la famiglia «volatilità» ha già usato il periodo chiuso (prova 15,
come scritto nella prova 44), la conferma è solo in avanti, sul demo, e la decide il proprietario.
