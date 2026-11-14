# Prova 31 — le aziende dell'S&P 500 che guadagnano di più sui beni che hanno, contro quelle che guadagnano di meno, un anno

Regole scritte il 14 novembre 2026 **prima di qualsiasi calcolo** e prima di scaricare i bilanci (idea I33 di `REGISTRO.md`). Si
conoscevano le prove 1-30 e una sola risposta della SEC, scaricata per controllare che il servizio risponda (l'utile lordo del 2019 di
tutte le aziende: nessun rendimento e nessun confronto guardati). Contano come **2 prove** (la strategia da sola, e la miscela con lei):
79 nel conto.

## Perché dovrebbe funzionare

Le aziende con l'**utile lordo** (ricavi meno costo del venduto) più alto rispetto al totale dei beni rendono di più delle altre, anche
fra le più grandi e anche a parità di prezzo rispetto ai conti: Novy-Marx, «The other side of value: the gross profitability premium»,
*Journal of Financial Economics* 108 (2013); la redditività è uno dei cinque fattori di Fama e French, «A five-factor asset pricing
model», *Journal of Financial Economics* 116 (2015). Il mercato sottovaluta quanto la redditività di oggi dura negli anni.

Perché ora: **è un dato mai usato** nelle prove (i conti delle aziende; finora prezzi, notizie, dirigenti, vendite allo scoperto e date
dei comunicati); si cambia **una volta l'anno**, quindi i costi pesano poco (la lezione delle prove 29 e 30); ed è venduto e comprato
insieme, quindi dovrebbe muoversi poco con la miscela.

**Sospetti scritti prima:**

* **2016-2024 è stato il decennio delle aziende «di crescita»** (tecnologia, software, marchi forti), che hanno spesso utile lordo alto
  e pochi beni: un risultato buono può essere solo «la crescita ha battuto il valore» in quegli anni, non un vantaggio che dura. Si
  stampa la correlazione con QQQ meno SPY;
* è pubblicato dal 2013: dopo la pubblicazione gli effetti calano di circa un terzo (McLean e Pontiff, *Journal of Finance* 71, 2016);
* **9 decisioni in tutto** (una l'anno): poche scommesse indipendenti, anche se i rendimenti sono di tutti i giorni;
* i valori della SEC per periodo (le «cornici» di `data.sec.gov/api/xbrl/frames`) sono gli ultimi depositati: se un'azienda ha
  corretto un bilancio in seguito, si vede il valore corretto, non quello di allora (un piccolo sguardo nel futuro, da dire);
* nel controllo del servizio una cornice «2019» conteneva un esercizio chiuso il **31 maggio 2020**: per non usare bilanci non ancora
  pubblicati, vale la regola dei 120 giorni qui sotto;
* le voci dei bilanci hanno nomi diversi fra le aziende: chi non ha né l'utile lordo né ricavi e costo del venduto resta fuori; si
  stampa quante aziende restano fuori.

## I dati

* **I conti:** le cornici annuali della SEC (`us-gaap`, in dollari) per l'utile lordo, i ricavi e il costo del venduto, e le cornici
  trimestrali «istantanee» per il totale dei beni (`Assets`), dal 2013 al 2025. Sono dati pubblici: nel repository va il valore
  calcolato per azienda e anno, in `stock/prove/dati/P031_redditivita.csv.gz`.
* **Il settore:** il codice SIC dell'azienda dalla SEC (`data.sec.gov/submissions`); si escludono le **finanziarie** (SIC da 6000 a
  6999), come fa Novy-Marx: per banche e assicurazioni l'utile lordo non ha senso.
* **Il codice SEC di ogni simbolo:** `stock/universo/codici_sec.csv` (prova 20).
* **I prezzi e l'indice:** come la prova 30 (Alpaca con il simbolo di allora, `dati/P028_membri.csv.gz`); un titolo che resta 5 giorni
  di borsa senza prezzi si chiude all'ultima chiusura e si conta.

## La regola

* **L'utile lordo** dell'esercizio: la voce `GrossProfit`; se non c'è, ricavi meno costo del venduto, con le voci in quest'ordine:
  ricavi `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`, `SalesRevenueNet`,
  `RevenueFromContractWithCustomerIncludingAssessedTax`; costo `CostOfRevenue`, `CostOfGoodsAndServicesSold`, `CostOfGoodsSold`,
  `CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization`.
* **Il totale dei beni:** `Assets` alla data di chiusura dell'esercizio; se manca, l'ultimo valore nei 31 giorni prima. Beni mancanti o
  non positivi: l'azienda resta fuori.
* **La redditività lorda** = utile lordo / totale dei beni.
* **Quale esercizio si usa:** alla decisione del giorno D, l'esercizio più recente **chiuso almeno 120 giorni prima di D** (le grandi
  aziende depositano il bilancio annuale entro 60 giorni, le altre entro 90: con 120 giorni il bilancio era già pubblico).
* **Ogni anno**, all'ultima chiusura di giugno: fra i membri dell'S&P 500 di quel giorno (con la barra), escluse le finanziarie, con la
  redditività calcolabile: comprato il **20% con la redditività più alta**, al massimo 50 (i più alti); venduto allo scoperto il **20%
  più basso**, al massimo 50 (i più bassi); a pari valore, in ordine alfabetico. Se le aziende con la redditività sono meno di 100,
  quell'anno si resta fuori.
* **Posizioni:** 50% del conto nei comprati a pesi uguali, 50% nei venduti a pesi uguali; ordini a mercato all'apertura del giorno di
  borsa dopo; si tiene **un anno**, senza ribilanciare in mezzo, fino alla decisione di giugno dopo.
* **Il limite del conto:** il simulatore esegue le vendite prima degli acquisti, quindi al cambio dell'anno le vendite allo scoperto
  nuove passerebbero prima delle ricoperture vecchie; come nella prova 29, il calcolo usa il limite di un conto con margine (2 volte il
  valore); l'esposizione voluta non cambia (50% e 50%).
* **Periodo:** decisioni da giugno 2016 a giugno 2024; rendimenti dal luglio 2016 al 31 dicembre 2024. Il periodo chiuso (2025-01 →
  2026-09) non si guarda.

## I costi (fissati prima, come le prove 11, 24, 28 e 30 sulle azioni dell'S&P 500)

Metà dello scarto misurato dove c'è, altrimenti 5 punti base più 2 di slittamento; commissioni Interactive Brokers «fisso»; prestito dei
titoli venduti allo scoperto **0,5% l'anno** (grandi aziende, facili da prendere a prestito). Versione con tutti i costi raddoppiati.

## L'esame (uguale alle prove 28 e 30)

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione dei rendimenti
giornalieri con la miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe
più alto della miscela e del tenere lo SPY.

Da leggere accanto (non sono prove): quante aziende con la redditività ogni anno e quante fuori (finanziarie, voci mancanti); il
rendimento di ogni anno dei comprati meno i venduti, senza costi; la correlazione con QQQ meno SPY; il beta rispetto allo SPY; il
risultato anno per anno. **Se passa uno dei due esami:** revisore separato, poi il periodo chiuso (la famiglia «conti delle aziende» non
l'ha mai usato), poi la misura in avanti sul demo.
