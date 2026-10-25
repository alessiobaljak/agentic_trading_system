# Programma 7 — quarantatreesima prova: l'effetto Coinbase, vendere sulla notizia (CB)

Scritto il 25 ottobre 2026, alle 12:45 UTC, **prima di qualunque calcolo sui prezzi**. Idea 75 della coda di `research/REGISTRO.md`. Il
controllo di fattibilità ha preso solo le date: dall'elenco pubblico dei prodotti di Coinbase (`api.exchange.coinbase.com/products`), per
le 311 monete quotate contro il dollaro che hanno anche il perpetuo su Binance, il primo giorno con una candela giornaliera su Coinbase
(`research/data/coinbase/primi_giorni.json`, fuori da git). Le monete quotate su Coinbase dal 2021 al 1° ottobre 2026 che avevano già il
perpetuo su Binance da almeno 30 giorni sono 108: 26 nel 2021, 20 nel 2022, 4 nel 2023, 9 nel 2024, 36 nel 2025, 13 nel 2026.

## 1. Perché, e il dubbio

L'«effetto Coinbase» è noto: quando Coinbase annuncia una moneta, il prezzo sale prima dell'apertura degli scambi, perché arriva il pubblico
americano al dettaglio. Il giorno in cui gli scambi aprono, chi ha comprato sulla voce vende sulla notizia: il prezzo dovrebbe scendere nei
giorni dopo. È un'informazione diversa da tutte quelle provate: un evento di un'altra borsa, messo insieme con il perpetuo di Binance.
**Il dubbio scritto prima**: dal 2021 Coinbase quota quasi tutto, quindi la notizia vale meno; il primo giorno di candele può non essere il
giorno dell'apertura agli utenti dell'app; 108 eventi sono pochi; e lo short delle monete piccole contro il Bitcoin è stato positivo in
generale nel 2024-2025 (prova 103: anche gli eventi di controllo rendevano), quindi serve un confronto con giorni qualunque.

## 2. La regola (valori fissati qui)

* **Evento**: il primo giorno L con una candela giornaliera di Coinbase contro il dollaro, con il perpetuo di Binance nato almeno 30 giorni
  prima di L e volume sopra zero il giorno L; L dal 1° gennaio 2021 al 1° ottobre 2026.
* **Operazione**: **short il perpetuo di Binance e long il Bitcoin** per lo stesso valore, entrata all'apertura del giorno L+1 (00:00 UTC
  dopo il primo giorno di scambi: la quotazione è nota), uscita a **+30%** dall'entrata (candele a 1 ora, 1% di scarto) o dopo **7 giorni**;
  costi della regola delle monete nuove (`vu.COSTO_MONETA + vu.COSTO_BTC`), funding giornaliero vero dei due lati.
* **Controllo**: la stessa operazione sulle stesse monete in 20 giorni presi a caso fra i 60 e i 365 giorni dopo L (stessa moneta, giorni
  senza la notizia), seme 2026: quanto rende la stessa moneta senza l'evento.
* **Descrittivo, non nel conto**: la salita prima della notizia (dai 14 giorni prima di L al giorno L, la moneta contro il Bitcoin), le
  tenute di 3 e 14 giorni, per anno.
* Una prova a eventi: nel conto **175**, le prove a eventi **31**.

## 3. L'esame

Come la regola delle monete nuove (`trentesima.esame`, bootstrap per settimana): media sopra zero con **p ≤ 0,01**, positiva nelle due
metà e senza le 5 migliori, **e sopra il controllo** sulle stesse monete; contando le 31 prove a eventi la soglia è 0,00032.

## Correzioni dopo la revisione separata (25 ottobre 2026, 13:30 UTC)

Le regole qui sopra restano quelle. Il revisore separato della prova 105 ha trovato due errori di dati, corretti prima di rifare il
calcolo (i numeri di prima restano nel registro accanto a quelli nuovi):

1. **La lettura delle candele orarie** (`programma6/esecuzione.ore_di`) ignorava i file mensili scaricati quando esistevano le barre del
   programma 6, che per 14 monete cominciano il 1° settembre 2023: gli eventi di quelle monete prima di quella data sparivano senza dirlo
   (91 operazioni invece di 105). Corretta nel codice comune, con i test (`tests/test_ore_di.py`).
2. **I simboli riusati**: la regola «perpetuo nato almeno 30 giorni prima» va letta sul contratto vero. Se prima del giorno della
   quotazione il volume del perpetuo resta a zero per almeno 7 giorni di fila, il simbolo è stato riusato o il contratto è ripartito, e la
   nascita è il primo giorno con volume dopo la pausa (`quarantatreesima.nascita_vera`). Toglie PUMP, RAY e HNT da Coinbase; AI, LIT, LUNA
   e PUMP da OKX.

Le altre osservazioni del revisore (prodotti già quotati in USDC prima del dollaro, il nuovo nome di un token, i giorni di nascita dei
token con un perpetuo di pre-mercato) non violano le regole scritte e restano dentro; il loro peso si riporta a parte.

