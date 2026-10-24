# Le piattaforme per il conto demo (azioni, dalla Svizzera)

Scritto il 24 ottobre 2026 dalla sessione «trading stock». Le fonti sono state cercate sul web lo stesso giorno. Dove un sito
ufficiale non si è lasciato leggere (Interactive Brokers risponde «accesso negato» ai programmi automatici), il fatto viene da una
fonte secondaria, ed è scritto. Quello che non sono riuscito a verificare è segnato **(da verificare)**.

## La risposta in breve

1. **Interactive Brokers** è la scelta giusta: il conto demo («paper») è collegabile a un programma con le stesse interfacce del
   conto vero, dà 1 milione di dollari finti e copre la borsa svizzera e quasi tutte le altre. **Il prezzo da pagare:** prima bisogna
   aprire un conto vero, approvato e **con dei soldi depositati**. Il deposito non viene usato per fare trading (il programma lavora solo
   sul conto demo), ma è denaro vero presso il broker: lo decide il proprietario.
2. **Se il proprietario non vuole depositare nulla: Saxo**, con il conto di simulazione per sviluppatori. È gratuito, si collega a un
   programma, dà 100'000 dollari finti, ma i prezzi arrivano **con 15 minuti di ritardo** e alcuni dati mancano.
3. **Swissquote no**: per i clienti privati non ha un'interfaccia per eseguire ordini di azioni da un programma, e il suo demo è per
   cambi e CFD.

**Una cosa da sapere prima di scegliere:** nessun conto demo esegue davvero gli ordini sul mercato. Il broker *simula* le esecuzioni
con regole sue (Interactive Brokers lo dice: il simulatore «non ha capacità di esecuzione né di compensazione»). Quindi il demo
misura bene il collegamento, i costi dichiarati e il comportamento del programma, ma **non** dice se un ordine limite si sarebbe
eseguito davvero in coda sul mercato vero. La lezione delle crypto sugli ordini limite (`LEZIONI_DALLE_CRYPTO.md`) sul demo resta
aperta: va trattata con sospetto anche lì.

## Il confronto

| | Interactive Brokers | Saxo (Svizzera) | Swissquote | Alpaca |
|---|---|---|---|---|
| Per chi vive in Svizzera | Sì, tramite Interactive Brokers U.K. [1] | Sì, Saxo Bank (Switzerland) Ltd., diritto svizzero [5] | Sì, banca svizzera [8] | Solo il conto demo; il conto vero «caso per caso» [10] |
| Borsa svizzera | Sì [2] | Sì per il conto vero (da verificare quali titoli ci sono nel demo) | Sì (conto vero) | **No**: solo azioni americane (da verificare, non l'ho trovato scritto) |
| Altre borse | Quasi tutte | Molte (America, Europa, Asia) [6] | Molte | Solo America |
| Conto demo | Gratuito, 1 milione di dollari finti [3]; serve un conto vero **approvato e con soldi depositati** [3][4] | Due tipi: demo normale di **20 giorni** [5]; simulazione per sviluppatori gratuita con 100'000 dollari finti [7] | Demo con fino a 50'000 dollari finti, **30 giorni**, per cambi e CFD [9] (fonte secondaria) | Gratuito, aperto a chiunque nel mondo [10] |
| Collegamento a un programma (ordini automatici) | **Sì** sul demo, con le stesse interfacce del conto vero [3] | **Sì** sulla simulazione per sviluppatori [7]; la chiave del portale dura un giorno [7] | **No** per le azioni dei privati: l'interfaccia FIX è per i cambi e chiede 50'000 dollari depositati [8] | Sì [10] |
| Prezzi nel demo | In ritardo, oppure in tempo reale se si condividono gli abbonamenti del conto vero [4] | **15 minuti di ritardo** sulle azioni [11]; alcuni dati di mercato e i rapporti mancano [7] | (da verificare) | (non rilevante: niente borsa svizzera) |
| Costi delle operazioni (conto vero) | Fonte ufficiale non leggibile; una fonte secondaria cita lo 0,05% con minimo CHF 1,50 o 5 per ordine sulla borsa svizzera **(da verificare)** [12] | Tabella ufficiale non caricata (da verificare); commissione per gli ordini da programma: 3 punti base in Europa, 0,5 centesimi per azione in America [6] | (da verificare) | — |
| Regolamentazione | Interactive Brokers U.K. sorvegliata dall'autorità inglese FCA [1] | Banca con licenza della FINMA [13] | Banca con licenza della FINMA [8] | Autorità americane (da verificare) |

## Perché Interactive Brokers e non Saxo

* **Il demo vale quanto il conto vero.** Stesse interfacce per il programma [3], stesse autorizzazioni e stessi abbonamenti ai dati del
  conto vero [3]: quello che si costruisce sul demo funziona poi senza cambiare niente. Su Saxo la simulazione è dichiarata «a priorità
  più bassa» per i problemi tecnici e spesso ha versioni diverse dal conto vero [7].
* **I prezzi.** Con 15 minuti di ritardo (Saxo) si possono provare bene solo strategie lente (giorni o settimane): ogni strategia che
  reagisce al prezzo entro la giornata verrebbe misurata con prezzi vecchi. Non sappiamo ancora che strategie serviranno (le richieste
  sulle azioni sono diverse da quelle delle crypto: il proprietario, 24 ottobre), quindi conviene non chiudersi questa porta. Su
  Interactive Brokers il demo prende i prezzi in tempo reale dal conto vero se si attiva la condivisione [4].
* **L'universo.** Borsa svizzera e tutte le grandi borse in un posto solo [2].

**I rischi della scelta:**

* Il deposito sul conto vero è denaro vero. Le regole del progetto dicono «niente soldi veri»: io lo leggo come «niente operazioni con
  soldi veri», ma è una decisione del proprietario, non mia.
* I dati in tempo reale della borsa svizzera si pagano a parte; il prezzo mensile per un privato non l'ho trovato **(da verificare sul
  sito di Interactive Brokers, sezione dati di mercato)**. L'unico prezzo trovato è 0,03 dollari per singola richiesta di quotazione [14].
* La condivisione dei dati ha un limite: non si possono usare gli stessi dati sul conto vero e sul demo nello stesso momento [4] (non è
  un problema se il conto vero non si usa).

## Cosa serve dal proprietario

1. Sì o no al deposito su un conto vero di Interactive Brokers (che non verrà usato per operare).
2. Quali mercati: solo la borsa svizzera, o anche America ed Europa? Cambia quali dati vanno pagati.
3. L'apertura del conto la fa il proprietario (servono documenti e identità). **Le chiavi e le password non vanno mai nel repository**:
   si mettono solo sulla macchina che farà girare il programma.

## Fonti

1. The Poor Swiss, «Is Interactive Brokers safe for Swiss investors?» — https://thepoorswiss.com/is-interactive-brokers-safe-for-swiss-investors/ (fonte secondaria; le pagine di Interactive Brokers citate nei risultati di ricerca dicono la stessa cosa: Interactive Brokers U.K. serve i residenti dei paesi europei fuori dall'Unione, Svizzera compresa)
2. BrokerChooser, «Swiss stocks at Interactive Brokers» — https://brokerchooser.com/de/invest-long-term/diversification/swiss-stocks-at-interactive-brokers
3. Interactive Brokers, glossario «Paper trading account» — https://www.interactivebrokers.com/campus/wp-json/wp/v2/glossary-terms/179994 e documentazione Web API «Trading access for individuals» — https://www.interactivebrokers.com/docs/web-api/trading/getting-started/trading-access-for-individuals (letti tramite i risultati di ricerca: le pagine bloccano la lettura diretta)
4. Interactive Brokers, «Market Data Considerations for the Paper Trading Account» — https://ibkb.interactivebrokers.com/article/1719 e guida «Paper Trading Account» — https://www.interactivebrokers.co.uk/en/software/amcsh/PaperTrading.htm
5. Saxo Svizzera, pagina delle piattaforme — https://www.home.saxo/en-ch/platforms (letta direttamente)
6. Saxo Svizzera, commissioni sulle azioni — https://www.home.saxo/en-ch/rates-and-conditions/stocks/commissions (letta direttamente; le tabelle per livello non si sono caricate)
7. Saxo, portale sviluppatori, «Environments» — https://developer.saxo/openapi/learn/environments (letta direttamente)
8. Swissquote, «FIX API» — https://www.swissquote.com/en-ch/private/trade/platforms/forex-cfds/fix-api e «Securities and cryptos via an API» (per istituzioni) — https://www.swissquote.com/en/institutional/solutions/technology/apis/securities-cryptos
9. Daytrading.com, recensione Swissquote 2026 — https://www.daytrading.com/swissquote-vs-avatrade (fonte secondaria)
10. Alpaca, «Introducing the Alpaca Paper Trading API» — https://alpaca.markets/blog/paper-trading-api/
11. Saxo, portale sviluppatori, «Pricing» — https://www.developer.saxo/openapi/learn/pricing (l'esempio sulla simulazione ha il ritardo di 15 minuti)
12. Mustachian Post, «IBKR pricing: fixed or tiered» (aggiornato l'11 ottobre 2026) — https://mustachianpost.com/ibkr-pricing-fixed-or-tiered (le cifre esatte sono solo nelle immagini; i numeri 0,05% e CHF 1,50/5 vengono dal riassunto della ricerca e non li ho potuti confermare)
13. Saxo, «Swiss banking licence and ownership» — https://www.home.saxo/en-ch/legal/saxo-bank-switzerland-license/saxo-bank-switzerland-license
14. Interactive Brokers, base di conoscenza sui dati di mercato — https://ibkb.interactivebrokers.com/tag/market-data?page=1 (per la borsa svizzera: 0,03 dollari per quotazione singola)
