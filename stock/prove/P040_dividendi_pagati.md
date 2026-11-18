# Prova 40 — i giorni con molti dividendi pagati: tenere lo SPY solo quando il pagamento è sopra la mediana dell'anno prima

Regole scritte il 18 novembre 2026 **prima di qualsiasi calcolo** e prima di scaricare le date di pagamento (idea I46 di `REGISTRO.md`,
che precisa la I41, dalla ricerca su GitHub). Si conoscevano le prove 1-39: in particolare la 6 (il cambio del mese, bocciata), la 9 e la
14 (i giorni speciali, bocciate nel periodo chiuso) e la 39 (da cui vengono le azioni in circolazione). Contano come **2 prove** (la
strategia da sola, e la miscela con lei): 97 nel conto.

## Perché dovrebbe funzionare

Hartzmark e Solomon, «Predictable Price Pressure», NBER w30688 (2022), American Economic Review 115 (2025); letto il testo (sezione
III.A, tabelle I e II, figure 1, 2 e 4). I dividendi pagati vengono in buona parte reinvestiti (fondi, piani di reinvestimento) nei giorni
del pagamento e in quello dopo: è un flusso di acquisti **annunciato settimane prima**, che non porta notizie. Dal 1926 al 2018 il
mercato rende circa 1,7 punti base nei giorni con pagamenti sotto la mediana e 6,4 sopra (quasi quattro volte); nel quarto più alto
+7,1 punti base al giorno (t 4,27). L'effetto è **cresciuto dopo il 1990** con i fondi e i fondi quotati (figura 4), e il loro campione
finisce nel 2018: il nostro 2017-2024 è in gran parte dopo e prima della pubblicazione su rivista (2025).

**Sospetti scritti prima:**

* **ha la forma dei giorni speciali** (prove 6, 9 e 14, bocciate): i pagamenti si affollano a metà e a fine mese, e una parte può essere
  il cambio del mese; si legge accanto quanti giorni scelti cadono nel cambio del mese;
* **solo le aziende dell'S&P 500** (lo studio usa tutto il mercato americano); i dividendi delle grandi sono la gran parte del totale;
* **il numero di azioni** viene dalla copertina dei bilanci (prova 39), con la data di deposito: per le aziende senza quel numero il
  dividendo resta fuori e si conta;
* **stare fuori metà del tempo** costa poco come rischio ma rinuncia a metà del guadagno: per battere lo SPY servono giorni scelti
  davvero migliori.

## I dati

* **I dividendi:** le azioni societarie di Alpaca dei membri dell'S&P 500 (simbolo di allora), dividendi in contanti con data di
  stacco, **data di pagamento** e importo per azione, dal 2016 al 2024.
* **Le azioni in circolazione:** `dati/P039_azioni.csv.gz` e il codice SEC di allora `dati/P039_codici.csv.gz` (prova 39): per ogni
  dividendo, l'ultimo numero di copertina depositato **prima della data di stacco**; se fra la data del numero e lo stacco c'è un
  frazionamento, il numero si moltiplica per il suo rapporto.
* **Lo SPY:** le chiusure dell'archivio delle prove (come il tenere lo SPY delle altre prove).

## La regola (dallo studio, figura 2)

* **Il pagamento del giorno:** la somma, sui membri dell'S&P 500 del giorno di pagamento, di importo per azione × azioni in circolazione,
  per i dividendi con quella data di pagamento (un pagamento in un giorno senza borsa va al giorno di borsa dopo).
* **La misura:** D(t) = pagamento del giorno t + pagamento del giorno di borsa prima (lo studio somma t e t−1).
* **La regola:** si tiene lo SPY nel giorno t (comprato alla chiusura del giorno prima, venduto alla chiusura di t) se D(t) è **sopra
  la mediana** dei D dei 252 giorni di borsa prima; altrimenti niente (liquidità senza interesse). Le date e gli importi sono annunciati
  settimane prima: alla chiusura del giorno prima si sa già.
* **Periodo:** dal 3 gennaio 2017 al 31 dicembre 2024 (il 2016 serve solo per la prima mediana). Il periodo chiuso non si usa.

## I costi (fissati prima)

Ogni entrata e uscita all'asta di chiusura dello SPY: metà dello scarto 0,185 punti base (`stock/dati/ESITO_CONTROLLI.md`),
slittamento 0,5 punti base, commissioni Interactive Brokers «fisso» su un conto di 100'000 dollari. Versione con i costi raddoppiati.

## L'esame (uguale alle prove 28 e 30-39)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30 rafforzata): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione con la
miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe più alto della
miscela e del tenere lo SPY; il t dello Sharpe della parte almeno 1,3; la miscela nuova più alta in almeno l'80% di 2000 campionamenti
a blocchi di 20 giorni.

Da leggere accanto (non cambiano l'esito): il rendimento medio dello SPY nei giorni sopra e sotto la mediana e la differenza con il t;
lo stesso per il quarto più alto dell'anno prima (la tabella II dello studio) e per i 10 giorni più alti; la quota dei giorni scelti nel
cambio del mese (ultimo giorno e primi tre); la quota dei dividendi senza numero di azioni; l'anno per anno.

**Famiglia e periodo chiuso (deciso prima):** è la famiglia dei «giorni speciali» (tenere l'indice solo in certi giorni), che ha già
aperto il periodo chiuso (prove 9 e 14): **se passa, revisore separato e poi solo la misura in avanti**.
