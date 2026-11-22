# Prova 166 — Le società che tengono una moneta in cassa e valgono meno di lei (idea 155)

Regole scritte il 22 novembre 2026 da strategy-scout, **prima di ogni calcolo** (nessun prezzo, nessun premio e nessun conteggio di giorni
è stato guardato). Il proprietario il 22 novembre ha chiesto di provare le idee nuove senza aspettare il suo via libera. La esegue
strategy-researcher (prima in modalità verifica), il giudizio lo dà backtest-auditor. Non spegne e non sostituisce niente. Nota sul nome:
il file segue la numerazione dei file del programma 7 (centoquattresimo), il numero di prova nel registro è 166.

## Il perché
* Dal 2025 aziende quotate (BitMine, SharpLink, Forward Industries, Hyperliquid Strategies, Sui Group, BNB Standard, StablecoinX per
  Ethena e altre) raccolgono soldi dagli azionisti e comprano un gettone. Finché l'azione vale **più** della cassa possono emettere altre
  azioni e comprare altre monete (domanda nuova); quando vale **meno** non possono più, e alcune vendono monete o ricomprano azioni per
  chiudere lo sconto. Una vendita forzata che prima del 2025 non esisteva: nessuno studio serio la copre ancora sui gettoni diversi dal
  Bitcoin (non c'è fonte accademica: è un fatto nuovo, e si scrive come tale).
* Dato mai usato nella ricerca: `registro --cerca` per «tesoreria», «azioni», «società», «mNAV» non trova nulla (22 novembre). Dato
  nuovo per le crypto: i prezzi delle azioni e i comunicati delle società. Idea 155 della coda del registro, sezione 5.
* Il meccanismo economico è quello dei flussi forzati (chi è costretto a vendere), uno dei pochi vantaggi che hanno retto nelle prove.
* **Rischi scritti prima**: (1) gli eventi sono pochi e arrivano tutti insieme (stesso periodo di mercato, 2025-2026), quindi la prova
  può dire poco; (2) gli sconti possono restare per mesi senza vendite; (3) una società può invece comprare di più (riacquisto di
  azioni con soldi presi a prestito, o raccolta con sconto) e il gettone sale; (4) le monete sono correlate fra loro: tanti eventi non
  sono tanti esperimenti indipendenti; (5) il Bitcoin è una copertura imperfetta.

## Le fonti dei dati, provate il 22 novembre 2026 (senza registrazione e senza chiave)
Funzionano:
* **Prezzo giornaliero delle azioni**: `https://query1.finance.yahoo.com/v8/finance/chart/<SIMBOLO>?range=max&interval=1d` (risposta 200 con
  chiusure e date; provati BMNR, FWDI, SBET, PURR, SUIG, BNC). Storico lungo quanto la quotazione (PURR 244 giorni, SUIG 201, BNC 153,
  SBET 355). **Non funziona per ETHM** (nessun dato: quotata da poco) né per BMNR con `range=max`: la risposta all'ultima prova era
  senza serie, da rifare con `range=1y` (200 con 28 KB). Stooq: pagina di verifica con JavaScript, **inutilizzabile**.
* **Azioni in circolazione**: `https://query2.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/<SIMBOLO>?type=quarterlyOrdinarySharesNumber&period1=..&period2=..`
  (200; per BMNR 5 date trimestrali), solo a fine trimestre; in mezzo vale il numero dell'ultimo documento (vedi sotto, dilatazione).
  In alternativa l'archivio della Commissione per i titoli degli Stati Uniti: `https://data.sec.gov/api/xbrl/companyconcept/<CIK>/dei/EntityCommonStockSharesOutstanding.json`
  (200 per BitMine, con data di deposito). Serve solo un nome di programma nell'intestazione, nessuna chiave.
* **Monete in cassa oggi**: `https://api.coingecko.com/api/v3/companies/public_treasury/<moneta>` (200 per ethereum, solana, binancecoin,
  hyperliquid, sui, ethena; 35 società per l'Ether). **Solo la fotografia di oggi, nessuno storico**; limite basso di chiamate (risposte
  429 dopo 4-5 chiamate in fila: va dato un respiro di 10 secondi fra una e l'altra). Per tron, the-open-network, world-liberty-financial-usd
  non ho avuto risposta (limite superato, da rifare con pause).
* **Monete in cassa nel tempo e date dei riacquisti**: archivio dei depositi della Commissione, `https://data.sec.gov/submissions/CIK<10 cifre>.json`
  (200; per BitMine 140 comunicati «8-K» dal 2025, uno a settimana, l'ultimo il 16 novembre 2026) e i documenti allegati sotto
  `https://www.sec.gov/Archives/edgar/data/<CIK>/<numero>/...`; ricerca testuale `https://efts.sec.gov/LATEST/search-index?q=...&forms=8-K`
  (200: «repurchase» + «ETH» 139 risultati, «sold ETH» 0). Il numero di monete in cassa sta nel comunicato (allegato, non nel documento
  principale: nel principale della prova la frase non c'era), da leggere con espressioni regolari.
Non funzionano o non bastano:
* DefiLlama `api.llama.fi/treasuries`: **402, a pagamento**. CoinGecko storico delle monete in cassa (`holding_chart`, `transaction_history`):
  provato con un nome non valido (404) e poi 429: **non verificato**; va tentato con la lista `entities/list` (429 al primo tentativo).
  Se non risponde, lo storico delle monete in cassa viene solo dai comunicati.
* Il sito strategicethreserve.xyz risponde (200) ma è una pagina che si costruisce nel browser: nessun storico pulito.
Cosa **manca per certo**: uno storico unico e pulito delle monete in cassa giorno per giorno per tutte le società. Si ricostruisce dai
comunicati (settimanali per BitMine e poche altre; trimestrali per le altre). È lavoro lungo ma si fa gratis; in questo caso si usano
solo le società con comunicati regolari (vedi universo).

## Dati e universo (fissati qui)
* **Società**: quelle quotate negli Stati Uniti con un gettone diverso dal Bitcoin in cassa che, al 31 ottobre 2026 secondo la lista di
  CoinGecko, valgono almeno **50 milioni di dollari di monete** e hanno almeno **60 giorni di prezzo** dell'azione. Il gettone deve avere
  il perpetuo su Binance con almeno 30 giorni di storia. Gettoni attesi: Ether (BMNR, SBET, ETHM, BTBT, BTCS, FGNX...), Solana (FWDI e
  altre), Hyperliquid (PURR), BNB (BNC), Sui (SUIG), Ethena (USDE.US), e Tron, Ton, WLFI se la lista li dà. Elenco e primo giorno scritti
  nel rapporto prima dei risultati.
* **Monete in cassa**: l'ultima cifra dichiarata in un comunicato **depositato prima delle 00:00 UTC del giorno D** (data del deposito,
  non la data a cui si riferisce). Azioni: l'ultimo numero di azioni in circolazione depositato prima di D. Se la cifra delle azioni è più
  vecchia di 45 giorni vale quella (si scrive quante volte accade).
* **Prezzi del perpetuo**: archivio giornaliero di Binance (apertura 00:00 UTC), funding vero, come nelle prove recenti.
* **Periodo**: dalla prima data in cui una società dell'universo ha prezzo e cassa dichiarata (per BitMine giugno-luglio 2025) al
  **31 ottobre 2026**.

## La misura «vale meno della cassa» (solo dati pubblici prima di D)
Per ogni società s e giorno D (decisione all'apertura 00:00 UTC):
  premio(s, D) = (chiusura dell'azione del giorno D−1 × azioni in circolazione) / (monete in cassa × prezzo di chiusura del perpetuo del
  gettone del giorno D−1 in dollari) − 1.
Il premio è negativo quando l'azione vale meno della cassa. Per ogni gettone, **premio del gettone** = **mediana** dei premi delle
società di quel gettone con la cassa del punto sopra almeno 50 milioni di dollari e almeno 60 giorni di prezzo (con una sola società
vale il suo premio; con due la media). Un debito della società e i soldi in contanti non si contano (non sono dati affidabili e
leggibili in automatico: si scrive come limite).

## La regola (fissata qui)
1. Segnale al giorno D: premio del gettone < −θ.
2. **Apertura** (00:00 UTC del giorno D): **short del perpetuo del gettone e long del perpetuo del Bitcoin**, stesso valore (neutra
   rispetto al mercato). Il Bitcoin non si vende contro se stesso: il gettone Bitcoin non è nell'universo.
3. **Durata fissa 14 giorni**, poi si chiude all'apertura. Dopo la chiusura, nuovo ingresso sullo stesso gettone solo se il segnale è
   rimasto spento almeno **7 giorni** (niente eventi sovrapposti; si conta un evento per gettone per episodio).
4. Peso: **20% del conto** per gamba per evento (short + long); al massimo 5 eventi insieme (ordine per premio più basso); il resto in
   contanti. Capitale 1.000 USDT (come il demo). Rendimento giornaliero = −(gettone) + Bitcoin, più funding vero (short del gettone
   incassa se il funding è positivo) di tutte le scadenze delle due gambe, meno spese.
5. **Spese**: come confermate dal proprietario: 0,05% a mercato, scarto 0,01% su BTC, ETH e SOL e 0,02% sulle altre, su ogni gamba,
   all'apertura e alla chiusura. Ordine limite (0,02%) solo come controllo descrittivo.

## Varianti (fissate, solo 2)
* **A**: θ = 0% (l'azione vale meno della cassa).
* **B**: θ = 20% (sconto di almeno il 20%: le società sono davvero strette).
Durata, mediana, peso e universo uguali. Nessuna soglia, durata o universo diverso dopo i risultati. Conta **2 prove**, e dello
stesso gruppo per correlazione (probabilmente una sola famiglia). Controlli descrittivi (non varianti): la durata 7 e 30 giorni; solo
l'Ether; il guadagno senza l'evento migliore e senza il gettone migliore; il rendimento medio dei 14 giorni **prima** del segnale;
il Bitcoin da solo contro il gettone.

## Quanti eventi ci si aspetta (stima, nessun dato guardato)
La storia parte dal 2025 (BitMine da luglio 2025; Hyperliquid Strategies, Sui, BNB, Ethena da settembre-dicembre 2025; Solana da
settembre 2025): circa **15 mesi al massimo, 5-9 gettoni**. Con la durata di 14 giorni e 7 giorni di pausa, il numero di episodi
indipendenti per gettone è piccolo: stima **da 8 a 25 eventi in tutto per A** (i premi sotto zero sono arrivati dopo la caduta di
ottobre 2025 e di nuovo nel 2026) e **da 3 a 12 per B**. Gli eventi sono **raggruppati nelle stesse settimane** (le società di Ether
si muovono insieme, e quasi tutti i gettoni insieme al mercato). Un t di 3 su una serie settimanale di circa 60 settimane con
la maggior parte a zero richiede un rendimento medio di circa 3-4 punti a evento con poca variazione: possibile ma **molto improbabile con
meno di 20 eventi indipendenti**. Conclusione scritta prima: **gli eventi sono troppo pochi perché un t di 3 e uno Sharpe corretto di
0,80 siano un esame solido; la prova sul passato può solo bocciare o dare un indizio**. Per questo si affianca una misura in avanti.

## La misura in avanti (parte dal giorno in cui si approvano le regole, a soldi finti simulati)
Dal 23 novembre 2026 uno script (stile `bot/portafoglio/`, nessun ordine) scrive ogni giorno alle 00:00 UTC: premio di ogni società e di
ogni gettone con la stessa formula, il segnale A e B, e la serie simulata del lato breve contro il Bitcoin (stesse spese). Si
valuta dopo **20 eventi indipendenti nuovi** (non dopo un tempo fisso), con le stesse soglie dell'esame; i dati futuri non sono mai stati
usati per scegliere θ, durata o peso. Serve a decidere se la prova sul passato era un caso.

## L'esame (regole approvate dal proprietario il 9 e l'11 novembre)
Passa se: netto dopo i costi positivo; **ogni anno positivo** (2025 e 2026: con due soli anni parziali si scrive che l'esame è debole);
t almeno 3 sulla serie settimanale **e sul rendimento medio per evento**; Sharpe corretto almeno 0,80 con il conto per famiglie
(`research/programma6/asticella.py`, `corretto_famiglie`, tutte e due le varianti in `nuove`). Se gli eventi indipendenti sono meno di
20 il verdetto è «non conclusivo» e non «promosso», anche se i numeri passano. Netto almeno 3% l'anno sul capitale.

## Cosa si consegna
`research/programma7/RISULTATI_CENTOQUATTRESIMA.md` (con l'elenco delle società, i primi giorni, gli eventi uno per uno, il numero di
eventi indipendenti e le fonti usate), serie in `research/programma7/risultati_centoquattresima/`, script
`research/programma7/centoquattresima.py` e `centoquattresima_dati.py` (prezzi, azioni, comunicati), varianti in
`research/trials/centoquattresima.csv`, dati in `research/data/` (non committati), script e uscita della misura in avanti. A schermo al
massimo 20 righe. Nessuna chiamata a servizi a pagamento e nessuna scrittura in `stock/` (i prezzi delle azioni sono solo un dato per
le crypto). Con le chiamate a CoinGecko: una ogni 10 secondi.
