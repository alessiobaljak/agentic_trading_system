# Programma 6 — seconda prova: la tendenza sulle candele giornaliere

Scritto il 19 ottobre 2026, dopo la prima prova (`RISULTATI.md`) e **prima di qualunque calcolo** di questa. Vale tutto
`METODO.md` dove qui non si dice altro.

## 1. Cosa abbiamo imparato dalla prima prova (fonte: `risultati/*.json` e `risultati/trade_*.csv.gz`)

1. **La scelta va sempre sulle candele più lunghe che le davamo.** Nei 24 trimestri la scelta prende le candele a 4 ore 23
   volte su 24 per la compressione, 23 per l'incrocio delle medie, 21 per la rottura del canale, 20 per il Supertrend (le
   altre volte non opera). Quando la scelta sta sempre sul bordo della griglia, la griglia è troppo corta: si prova il passo
   dopo, le candele di **1 giorno**.
2. **Funziona meglio chi segue la tendenza, non chi scommette sul ritorno.** Le due famiglie migliori seguono la rottura
   (compressione: +0,093 R a trade; Supertrend: +0,056); le due di ritorno sono a +0,021 e −0,028, e negative nell'ultimo
   anno.
3. **Il lato long regge meglio del lato short** nelle rotture: rottura del canale +0,045 R long e −0,073 short; incrocio
   +0,082 e −0,059; Keltner +0,093 e −0,085 (la compressione fa eccezione: +0,072 e +0,114).
4. **Nessuna passa perché l'intervallo è largo**: il risultato medio è positivo ma i trade dello stesso giorno su monete
   diverse si muovono insieme, e l'incertezza resta alta.
5. **Un difetto dell'universo**: le 100 monete erano le più scambiate a settembre 2026, cioè quelle che **oggi** sappiamo
   sopravvissute e cresciute. Chi nel 2021 avesse scelto le monete non poteva saperlo. Per una strategia che compra le
   monete che salgono è un vantaggio regalato. Da qui in avanti l'universo si sceglie **mese per mese con i soli dati di
   allora**, fra **tutte** le monete dell'archivio, anche quelle tolte dal listino.

## 2. Cosa si legge prima (19 ottobre 2026)

* **Zarattini, Pagani e Barbon, «Catching Crypto Trends; A Tactical Approach for Bitcoin and Altcoins»** (Swiss Finance
  Institute, Research Paper 25-80, SSRN 5209907, 8 aprile 2025): un insieme di rotture di canale di Donchian con nove
  periodi, la posizione dimensionata sulla volatilità, un portafoglio che ruota sulle 20 monete più liquide; dichiarano lo
  Sharpe netto sopra 1,5 e un extra sul Bitcoin del 10,8% l'anno. Il testo completo non è scaricabile da qui (SSRN e il sito
  dell'autore rispondono 403 e 502); le regole vengono dal riassunto di CXO Advisory («Crypto-asset Trend-following
  Strategies») e dalla pagina di Concretum Group, e dove mancano le scrivo qui sotto **prima** di calcolare.
* «AdaptiveTrend» (arXiv 2602.11708, 2026): tendenza a 6 ore con lo stop che segue a 2-3,5 ATR su oltre 150 perpetui di
  Binance; risultati dichiarati alti ma da un solo autore, con parametri mancanti: non si prova (non è replicabile così).
* Detzel, Liu, Strauss, Zhou e Zhu (Financial Management 2021) e Hudson e Urquhart (Annals of Operations Research 2021): le
  regole di tendenza su orizzonti di settimane hanno potere sul Bitcoin; i costi e la ricerca di molte regole riducono molto
  quello che resta.

La **prova più pulita** è la regola pubblicata: i valori li hanno scelti altri, prima, su dati che finiscono a marzo 2025.
Da aprile 2025 a oggi (18 mesi) è fuori dal loro campione **e** dal nostro.

## 3. I dati

* Candele giornaliere (`1d`) dei perpetui USDT-M dall'archivio pubblico di Binance (`data.binance.vision`), file mensili e,
  per ottobre 2026, giornalieri; il funding mensile; tutto con il CHECKSUM (`scarico_giorni.py`, impronte in
  `scarico_giorni.json`). **Tutti** i simboli `…USDT` dell'archivio, anche quelli tolti dal listino; escluse le monete
  stabili (come nel programma 5) e i contratti che non sono una moneta (indici come BTCDOM, DEFI; metalli e azioni):
  l'elenco degli esclusi si scrive in fondo a questo file **dopo aver visto i nomi e prima di ogni calcolo sui prezzi**.
* L'archivio parte da gennaio 2020; i calcoli si giudicano dal **1 gennaio 2021** all'ultimo giorno completo scaricato.
* Funding: dove manca (ottobre 2026, non ancora pubblicato; o un buco), si usa la media giornaliera della stessa moneta nei
  90 giorni prima.

## 4. L'universo, mese per mese, con i soli dati di allora

Il primo giorno di ogni mese, con i dati fino alla chiusura del giorno prima: sono ammesse le monete con almeno **365
giorni** di candele, una candela nel giorno prima e la **mediana del volume giornaliero in USDT degli ultimi 30 giorni** di
almeno 2 milioni; si ordinano per quella mediana e si prendono le prime **20** (parte A) o **50** (parte B). L'universo vale
per tutto il mese. Una moneta che esce dall'universo si chiude all'apertura dopo; una tolta dal listino si chiude
all'ultima chiusura disponibile.

## 5. Parte A — la regola pubblicata

Per ogni moneta e ogni periodo L in {5, 10, 20, 30, 60, 90, 150, 250, 360} giorni, sulle **chiusure** giornaliere:

* **ingresso long** del modello L quando la chiusura supera il massimo delle L chiusure prima;
* **stop che segue**: all'ingresso è il punto medio fra massimo e minimo delle ultime L chiusure (oggi compreso); ogni
  giorno sale al punto medio nuovo se è più alto, non scende mai;
* **uscita** quando la chiusura è sotto lo stop del giorno prima;
* il **segnale della moneta** è la media dei nove modelli (da 0 a 1);
* **volatilità**: deviazione standard dei rendimenti giornalieri degli ultimi 90 giorni, annualizzata con √365; il
  moltiplicatore è 25% diviso la volatilità, al massimo 2;
* **peso** della moneta = segnale × moltiplicatore / 20 del capitale (20 fisso anche se le ammesse sono meno);
* si decide alla chiusura del giorno, si opera all'**apertura del giorno dopo**, si tiene fino all'apertura dopo ancora;
  ogni giorno si riportano i pesi a quelli voluti;
* **costi**: su ogni variazione di peso, commissione a mercato 0,05% più lo scarto (0,01% BTC, ETH, SOL; 0,02% le altre);
  il funding su ogni regolamento, con il segno della posizione.

Le varianti, **tre e solo tre**, contano come tre prove:

* **A1** (quella pubblicata): solo long, 20 monete. È la principale.
* **A2**: anche short, in modo speculare (ingresso sotto il minimo delle L chiusure prima, stop che scende al punto
  medio, uscita sopra lo stop); segnale = (modelli long − modelli short) / 9.
* **A3**: solo Bitcoin, peso = segnale × moltiplicatore (la prima parte dell'articolo).

Confronti, che non sono prove: Bitcoin sempre comprato; le stesse 20 monete sempre comprate con lo stesso moltiplicatore
di volatilità («sempre dentro»).

## 6. Parte B — le famiglie della prima prova sulle candele di 1 giorno

Le nove famiglie, le griglie, le uscite e i due modi d'ingresso della prima prova (`famiglie.py`), con il **solo tempo di
1 giorno** al posto di 15 minuti, 1 ora e 4 ore (i periodi delle griglie diventano giorni); le stesse finestre che avanzano
(12 mesi di costruzione, 3 di prova, dal 2021-01), la stessa regola di scelta (sezione 4 di `METODO.md`), lo stesso
esame (sezione 6 di `METODO.md`). Le monete: l'universo della sezione 4 con le **prime 50**; un trade conta solo se
l'ingresso cade in un mese in cui la moneta è nell'universo. Contano come **nove** prove. Il capitale si riporta con il
tetto: un trade nuovo non si apre se il valore di tutte le posizioni aperte supererebbe 5 volte il capitale.

## 7. L'esame della parte A (per A1, A2, A3), dal 2021-01-01 all'ultimo giorno

Una variante è **valida** se tutte e sei:

1. rendimento netto giornaliero medio positivo con l'intervallo al 95% sopra zero (bootstrap a blocchi circolari di 20
   giorni, 10.000 volte);
2. **Sharpe corretto** (Deflated Sharpe Ratio) ≥ 0,95, con il numero di prove di tutto il programma 6: 9 della prima prova
   + 3 della parte A + 9 della parte B = **21**;
3. positiva in almeno **4 anni su 6** e nell'ultimo anno (dal 2025-10-01);
4. positiva **dopo l'uscita dell'articolo** (dal 2025-04-09);
5. positiva a costi doppi;
6. rendimento in più rispetto al Bitcoin (l'intercetta della regressione sui rendimenti giornalieri del Bitcoin) positivo.

Lo Sharpe corretto nella parte B usa lo stesso numero di prove, 21.

## 8. Cosa non si fa

* Non si cambia nessun valore dopo aver visto i risultati; un'idea nuova che nasce dai risultati va in una terza prova
  scritta prima, e le prove si sommano nel conto dello Sharpe corretto.
* La leva oltre quella della regola (al massimo 2 per moneta nella parte A, 5 in tutto nella parte B) non si discute qui:
  moltiplica guadagni e perdite, non crea vantaggio. `DRY_RUN` resta vero.

## 9. Esclusi (scritto dopo aver visto i nomi, prima dei calcoli)

Scritto il 19 ottobre 2026 alle 06:30 UTC, dall'elenco dei 892 simboli `…USDT` dell'archivio (stabili già tolte), senza
aver calcolato niente sui prezzi. L'elenco è anche in `seconda.py` (`ESCLUSI`).

* **Indici** (4): BTCDOMUSDT, DEFIUSDT, FOOTBALLUSDT, BLUEBIRDUSDT.
* **Metalli, materie prime, oro in gettoni, valute** (9): XAUUSDT, XAGUSDT, XPTUSDT, XPDUSDT, COPPERUSDT, NATGASUSDT, PAXGUSDT, XAUTUSDT, USDBRLUSDT.
* **Azioni e fondi** (142): AAOIUSDT, AAPLUSDT, ACNUSDT, ADBEUSDT, ALABUSDT, AMATUSDT, AMDUSDT, AMZNUSDT, ANETUSDT, ANTHROPICUSDT, APLDUSDT, APPUSDT, ASMLUSDT, ASTSUSDT, AVGOUSDT, AXTIUSDT, BABAUSDT, BITOUSDT, BMNRUSDT, BRKBUSDT, BYDUSDT, CIENUSDT, COHRUSDT, COINUSDT, COSTUSDT, CRCLUSDT, CRDOUSDT, CRMUSDT, CRWDUSDT, CRWVUSDT, CSCOUSDT, CSOPSAMSUNG2LUSDT, CSOPSKHYNIX2LUSDT, CVNAUSDT, CXMTUSDT, DDOGUSDT, DELLUSDT, DISUSDT, DJTUSDT, DKNGUSDT, EBAYUSDT, EWJUSDT, EWYUSDT, EWZUSDT, FLNCUSDT, GDXUSDT, GEVUSDT, GIGADEVUSDT, GLWUSDT, GMEUSDT, GOOGLUSDT, GTLBUSDT, HANMIUSDT, HIMSUSDT, HK0625USDT, HK0700USDT, HK0992USDT, HK1810USDT, HOODUSDT, HPEUSDT, HUTUSDT, HYUNDAIUSDT, IBMUSDT, INTCUSDT, IONQUSDT, IRENUSDT, IWMUSDT, JPMUSDT, KLACUSDT, KODEX200USDT, KUAISHOUUSDT, LGELECTRONICSUSDT, LLYUSDT, LRCXUSDT, MARAUSDT, MDBUSDT, MEITUANUSDT, METAUSDT, MINIMAXUSDT, MRKUSDT, MRNAUSDT, MRVLUSDT, MSFTUSDT, MSTRUSDT, NAVERUSDT, NBISUSDT, NFLXUSDT, NKEUSDT, NOWUSDT, NVDAUSDT, NVDLUSDT, NVOUSDT, OKLOUSDT, ONDSUSDT, OPENAIUSDT, ORCLUSDT, PANWUSDT, PDDUSDT, PLTRUSDT, POPMARTUSDT, PYPLUSDT, QCOMUSDT, QQQUSDT, RDDTUSDT, RIVNUSDT, RKLBUSDT, SAMSUNGEMUSDT, SAMSUNGUSDT, SHOPUSDT, SKHYNIXUSDT, SMCIUSDT, SMHUSDT, SNDKUSDT, SNOWUSDT, SOFIUSDT, SONYUSDT, SOXLUSDT, SOXSUSDT, SPCXUSDT, SPYUSDT, SQQQUSDT, TEMUSDT, TENCENTUSDT, TMFUSDT, TQQQUSDT, TSLAUSDT, TSLLUSDT, TSMUSDT, TTWOUSDT, TXNUSDT, TZAUSDT, UBERUSDT, UNHUSDT, UNITREEUSDT, URNMUSDT, UVXYUSDT, WDCUSDT, WMTUSDT, XBIUSDT, XLEUSDT, XOMUSDT, ZHIPUUSDT.

Quasi tutti i contratti su azioni sono nati nel 2025-2026: con la regola dei 365 giorni non entrerebbero comunque. Se fra
le monete scelte dall'universo comparisse un altro contratto che non è una moneta, si toglie e si scrive qui con la data,
prima di guardare i risultati.
