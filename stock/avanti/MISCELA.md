# La miscela sul conto demo (misura in avanti)

Decisione del proprietario, 11 novembre 2026: «ok, metti la miscela sul demo [...] fai in modo che questi ritardi non si ripetano mai più».
La prova 25 (`stock/prove/P025_miscela.md`) batte il tenere lo SPY sullo Sharpe (1,08 contro 0,89) ma non si distingue dal caso
(Sharpe corretto 0,05) e il periodo chiuso delle sue parti è già usato: la conferma può venire solo da qui, in avanti. Regole scritte
prima della prima operazione; una modifica vuol dire una misura nuova.

## Le regole (quelle delle prove 7, 15 e 16, senza numeri nuovi)

**Lo stesso conto demo della prima candela** (decisione del proprietario, 12 novembre 2026: «usa quello attuale»). Le due strategie
non si toccano: si dividono per **titolo** (la miscela compra solo SPY e QQQ, mai fra le azioni della prima candela) e ognuna ha il
suo **capitale virtuale di 100'000 dollari**, su cui calcola quantità e rendimento (`stock/avanti/conto.py`). Il conto vero ha quindi
fino a circa il doppio dell'esposizione del suo valore: è solo il contenitore, e usa il margine del conto demo. Sei parti da un sesto
del capitale: tre regole × SPY e QQQ.

* **Prima della banca centrale (prova 7):** il giorno di borsa prima del comunicato si compra alle 14:00 di New York, il giorno del
  comunicato si vende alle 13:59. Date: `stock/dati/fomc.py` (`COMUNICATI_AVANTI`, dal sito della Federal Reserve).
* **Più investiti con il mercato calmo (prova 15):** l'ultimo giorno di borsa di ogni settimana, quota = 16% / volatilità annua delle
  ultime 21 sedute, fra 0 e 1,5; la parte si muove solo se cambia di almeno il 10%.
* **Metà fuori quando la salita la fanno in poche (prova 16):** l'ultimo giorno di borsa di ogni mese, la quota dei membri attuali
  dell'S&P 500 sopra la propria media di 200 sedute; dal 50% in su la parte è investita al 98%, sotto al 49%.
* **Gli ordini:** le parti comprano e vendono solo SPY e QQQ: gli ordini si sommano. Le decisioni di fine settimana e di fine mese si
  eseguono **all'apertura** del giorno dopo, come nelle prove. Niente ordini sotto il 10% di una parte.
* **La partenza:** alla prima sera le regole della calma e dell'ampiezza decidono subito con i dati di quel giorno (senza aspettare
  la fine della settimana o del mese); la regola della banca centrale parte dal primo comunicato dopo.

## I ritardi: chi avvia non deve essere puntuale

Come per la prima candela, ogni avvio lancia il comando `auto` (`stock/avanti/miscela.py`, funzione `cosa_fare`), che guarda l'orologio
di New York. **La sera** si può decidere a qualunque ora fra le 19:00 (da quando Alpaca accetta gli ordini «all'apertura») e un quarto
d'ora prima dell'apertura dopo: un ritardo di ore non cambia niente. **La banca centrale** (16 giorni l'anno) è l'unica con un'ora
precisa: il giro resta acceso e aspetta le 14:00 o le 13:59, fino a 5 ore e 20 minuti prima; l'ingresso in ritardo di più di 20 minuti
si salta, **l'uscita non si salta mai** (in ritardo si vende subito, o all'apertura dopo). Avvii: GitHub ogni mezz'ora, le routine
della sessione «trading stock», e la VPS quando sarà installata (`stock/avanti/vps/`). Niente doppioni: ordini con nome unico e stato
in `miscela_stato.json`.

## I numeri

Ogni decisione in `miscela_diario.csv`, i valori di fine giornata delle due strategie in `valori.csv`, e sulla Plancia (`/azioni/strategie/miscela`); ogni lunedì nel riepilogo al
proprietario, accanto al tenere lo SPY e alla prova 25 sugli stessi giorni.
