# La miscela sul conto demo (misura in avanti)

Decisione del proprietario, 11 novembre 2026: «ok, metti la miscela sul demo [...] fai in modo che questi ritardi non si ripetano mai più».
La prova 25 (`stock/prove/P025_miscela.md`) batte il tenere lo SPY sullo Sharpe (1,08 contro 0,89) ma non si distingue dal caso
(Sharpe corretto 0,05) e il periodo chiuso delle sue parti è già usato: la conferma può venire solo da qui, in avanti. Regole scritte
prima della prima operazione; una modifica vuol dire una misura nuova.

## Le regole (quelle delle prove 7, 15 e 16, senza numeri nuovi)

**Lo stesso conto demo della prima candela** (decisione del proprietario, 12 novembre 2026: «usa quello attuale»; dal 24 novembre c'è
anche la prova 45, su VOO, `GAMMA.md`: le strategie nel conto sono tre). Le strategie non si toccano: si dividono per **titolo** (la miscela compra solo SPY e QQQ, mai fra le azioni della prima candela) e ognuna ha il
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

## Cosa il demo può dire e cosa no (audit del 27 novembre 2026)

Sul passato (2'054 giorni in comune con lo SPY di Yahoo) la miscela ha Sharpe 1,08 contro 0,87 dello SPY, con una correlazione
giornaliera di 0,89. L'errore della differenza fra i due Sharpe (Jobson e Korkie con la correzione di Memmel) è 0,47 dopo un anno di
giorni, 0,27 dopo tre; già sugli 8,2 anni del passato la differenza vale z 1,29, e arriva a 2 solo dopo circa 20 anni. Quindi **il
demo non può dire, in mesi o in pochi anni, se la miscela batte lo SPY**: qualche mese buono o cattivo è caso. Può dire se il programma
fa quello che il passato prevede (ordini eseguiti, costi, quote decise, perdite nei giorni agitati). Va detto anche che la miscela
**guadagna meno dello SPY** (+139% contro +217% sugli stessi giorni; 11,3% l'anno contro 15,8%): vince sul rischio (volatilità 10,4%
contro 18,2%, beta 0,51, alfa 3,2% l'anno), non sul guadagno. Calcolo rifatto dalla sessione il 27 novembre con la serie
`prove/serie/P025_miscela.csv`.

## Le deviazioni (scritte quando succedono)

* **12 novembre 2026 — i primi ordini non sono stati eseguiti.** La miscela è partita la mattina del 12 (l'avvio delle 9:10 di New
  York ha fatto la «sera» dell'11, come previsto dalle regole sui ritardi): SPY +37 e QQQ +34, ordini a mercato «all'apertura»
  (`opg`) mandati alle 9:11. Sul conto demo sono **scaduti alle 9:31 senza esecuzione** (letto da Alpaca con il comando di sola
  lettura `ordini`). La miscela quindi il 12 novembre non era investita: valore 100'000, nessuna perdita e nessun guadagno.
  Da qui gli ordini della sera sono **ordini a mercato «day» mandati a borsa chiusa**, che Alpaca tiene in coda fino all'apertura
  (nome nuovo `miscela-sera-{giorno}-g-{titolo}`); gli ordini vecchi della miscela si cancellano, e un ordine con lo stesso nome già
  scaduto o cancellato non conta più come mandato. La sera del 12 si rifà a mano (`rifai_sera`). Le regole della strategia non
  cambiano: si compra all'apertura come nelle prove.
