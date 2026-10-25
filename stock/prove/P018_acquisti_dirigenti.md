# Prova 18 — gli acquisti dei dirigenti nelle loro aziende (S&P 500)

Regole scritte il 25 ottobre 2026 **prima di qualsiasi calcolo** su questa idea (idea I18 di `REGISTRO.md`, chiesta dal proprietario),
committate prima di lanciare il programma. Famiglia nuova (informazione da chi guida l'azienda): il periodo chiuso si può riusare (i
dati della SEC arrivano al primo trimestre 2026). Conta come **1 prova**.

## Perché dovrebbe funzionare

Chi guida un'azienda sa di lei più del mercato. Quando un dirigente compra azioni della sua azienda con i suoi soldi, sul mercato, è un
segnale costoso: le vendite hanno mille ragioni (tasse, case, diversificare), gli acquisti una sola. Lakonishok, Lee, «Are insider trades
informative?», *Review of Financial Studies* 14 (2001); Cohen, Malloy, Pomorski, «Decoding inside information», *Journal of Finance* 67
(2012). **Sospetto scritto prima:** nelle grandi aziende gli acquisti dei dirigenti sono rari e piccoli rispetto all'azienda; l'effetto è
noto e ci sono servizi che li pubblicano in pochi minuti.

## I dati

I dati trimestrali della SEC sulle operazioni dei dirigenti (`stock/dati/dirigenti.py`): moduli 4, operazioni sulle azioni (non sulle
opzioni), codice **P** (acquisto sul mercato) e «acquisito». Chi compra deve essere un **dirigente o un consigliere** dell'azienda (non
solo un socio con più del 10%). Il simbolo è quello scritto nel modulo, con i cambi di simbolo del 2016-2024. Vale la **data di deposito**
alla SEC (il giorno in cui l'acquisto diventa pubblico), non quella dell'acquisto.

**Pulizia dei dati** *(aggiunta il 25 ottobre, prima del calcolo della strategia, dopo aver visto che nei moduli ci sono errori di
compilazione: acquisti singoli fino a 1,6 × 10^14 dollari in aziende piccolissime)*: si scarta ogni operazione il cui prezzo per azione
dista più del 50% dalla chiusura non rettificata del titolo nel giorno dell'operazione (o, se quel giorno non c'è la barra, nel giorno di
borsa precedente). Le operazioni senza prezzo si scartano.

## La regola

* **Evento:** per ogni azienda dell'S&P 500 del giorno di deposito (composizione storica) e per ogni giorno di deposito, la somma degli
  acquisti che soddisfano i criteri sopra; conta solo se è almeno **100'000 dollari** (per escludere gli acquisti simbolici; numero
  fissato qui).
* **Ingresso:** a mercato all'apertura del primo giorno di borsa **dopo** il giorno di deposito (il modulo può arrivare dopo la chiusura),
  con il **5%** del conto, azioni intere; al massimo 20 titoli insieme; se i posti non bastano, prima gli acquisti di valore più alto.
  Se il titolo è già in mano, niente.
* **Uscita:** a mercato all'apertura del 21° giorno di borsa dopo l'ingresso (20 sedute, come le prove 8 e 10).
* **Periodo:** depositi dal 1 gennaio 2016 al 30 novembre 2024. Prezzi al giorno, dividendi, frazionamenti, scissioni, come la prova 11.

## Costi ed esame

Costi come la prova 11 (scarto misurato per i 34, metà scarto 5 punti base e 2 di slittamento per gli altri; Interactive Brokers; costi
doppi). Passa la ricerca se sono vere **tutte**: (1) Sharpe annuo con i costi più alto del tenere lo SPY e del tenere tutto l'indice a pesi
uguali (prova 11), sugli stessi giorni; (2) Sharpe corretto ≥ 0,95; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei 32
trimestri in guadagno. Da leggere: il guadagno medio per evento rispetto allo SPY e il suo t, e il risultato anno per anno.
