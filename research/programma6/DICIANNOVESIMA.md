# Programma 6 — diciannovesima prova: il premio del perpetuo sullo spot fra monete (P1, P2)

Scritto il 20 ottobre 2026, mattina, **prima di qualunque calcolo sui rendimenti**. Idea 4 della coda di
`research/REGISTRO.md` (la I-008 del programma 5, mai fatta). Vale `OTTAVA.md` (F3) dove qui non si dice altro.

## 1. Perché

* F3 (prova 8) ordina le monete con il funding dei 7 giorni prima. Ma il funding di Binance è il premio medio più un
  aggiustamento che lo **blocca a 0,01% ogni 8 ore** finché il premio resta fra −0,05% e +0,05%: nei periodi calmi molte
  monete hanno lo stesso funding e la scelta fra loro è casuale. Misura (senza rendimenti): in **47 settimane su 302** dal
  2021 il confine del quinto alto o basso di F3 cade dentro un gruppo di monete con lo stesso funding dei 7 giorni; la quota
  della moneta-valore più frequente arriva al 74% in una settimana.
* L'indice del premio (quanto il perpetuo sta sopra o sotto lo spot, ogni ora) non ha il blocco: dice la stessa cosa del
  funding (chi paga per stare long) in modo continuo.

## 2. La regola

* **Dati**: l'indice del premio orario dell'archivio pubblico (`scarico_premio.py`, file mensili con il CHECKSUM), per le
  monete passate almeno una volta dall'universo delle 100.
* **Segnale** di ogni moneta al lunedì: la media delle chiusure orarie dell'indice del premio delle **168 ore** prima del
  lunedì alle 00:00 UTC; serve almeno **120** ore con il dato, se no la moneta quella settimana non entra.
* **P1**: long il quinto con il premio più basso, short il quinto con il più alto.
* **P2**: la media dei ranghi (fra le monete dell'universo) di −funding dei 7 giorni e −premio dei 7 giorni; long il quinto
  più alto, short il più basso.
* Universo, pesi (inverso della volatilità dei 30 giorni), costi e funding come F3, con le correzioni del controllo dei dati
  del 20 ottobre (`controllo_zombi.py`).
* Due prove: nel conto del programma 6 diventano **44**.

## 3. L'esame

Come F3: dal **4 gennaio 2021**, `terza.esame` e `terza.esito` con lo Sharpe corretto sulle **44** prove. Si riportano anche
(senza decidere niente): quante monete-settimana non hanno il premio, la correlazione con F3 e M1, e il risultato di P1 e
di F3 nelle 47 settimane dei pari.
