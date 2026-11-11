# La miscela sul conto demo (misura in avanti)

Decisione del proprietario, 11 novembre 2026: «ok, metti la miscela sul demo [...] fai in modo che questi ritardi non si ripetano mai più».
La prova 25 (`stock/prove/P025_miscela.md`) batte il tenere lo SPY sullo Sharpe (1,08 contro 0,89) ma non si distingue dal caso
(Sharpe corretto 0,05) e il periodo chiuso delle sue parti è già usato: la conferma può venire solo da qui, in avanti. Regole scritte
prima della prima operazione; una modifica vuol dire una misura nuova.

## Le regole (quelle delle prove 7, 15 e 16, senza numeri nuovi)

Un conto demo di Alpaca suo (non quello della prima candela). Sei parti da un sesto del capitale: tre regole × SPY e QQQ.

* **Prima della banca centrale (prova 7):** il giorno di borsa prima del comunicato si compra alle 14:00 di New York, il giorno del
  comunicato si vende alle 13:59. Date: `stock/dati/fomc.py` (`COMUNICATI_AVANTI`, dal sito della Federal Reserve).
* **Più investiti con il mercato calmo (prova 15):** l'ultimo giorno di borsa di ogni settimana, quota = 16% / volatilità annua delle
  ultime 21 sedute, fra 0 e 1,5; la parte si muove solo se cambia di almeno il 10%.
* **Metà fuori quando la salita la fanno in poche (prova 16):** l'ultimo giorno di borsa di ogni mese, la quota dei membri attuali
  dell'S&P 500 sopra la propria media di 200 sedute; dal 50% in su la parte è investita al 98%, sotto al 49%.
* **Gli ordini:** le parti comprano e vendono solo SPY e QQQ: gli ordini si sommano in un conto solo. Le decisioni di fine settimana e di
  fine mese si prendono la sera (dopo le 19:00 di New York, quando Alpaca accetta gli ordini) e si eseguono **all'apertura** del giorno
  dopo, come nelle prove. Niente ordini sotto il 10% di una parte.

## I ritardi

Solo la regola della banca centrale ha un'ora precisa (14:00 e 13:59), 16 giorni l'anno. Le altre decidono la sera per l'apertura del
giorno dopo: un ritardo di ore non cambia niente. Partenze indipendenti: due orari di GitHub per la sera e due per la banca centrale,
più una routine della sessione «trading stock»; la coda dei lavori di GitHub e lo stato in `miscela_stato.json` impediscono doppioni.
Un'ora precisa al minuto, garantita, si avrebbe solo con un computer sempre acceso (decisione del proprietario).

## I numeri

Ogni giorno in `miscela_diario.csv` (decisioni e ordini) e sulla Plancia (`/azioni/strategie/miscela`); ogni lunedì nel riepilogo al
proprietario, accanto al tenere lo SPY e alla prova 25 sugli stessi giorni.
