# Ricerca nei repository pubblici di GitHub: strategie sulle azioni americane (16 novembre 2026)

> Rapporto di un agente di ricerca (16 novembre 2026, solo pagine pubbliche, nessun codice eseguito), chiesto dal proprietario: «hai provato a cercare tra tutti i repository di github se qualcuno ha mai condiviso strategie su stock?». Controllato dalla sessione solo per la prima idea (la pagina NBER w33554 conferma titolo, autori e i −17 punti base del giorno dopo; non riporta la strategia né lo Sharpe). Le idee scelte sono in coda in `REGISTRO.md` (I39-I43).

Ricerca di idee, non di codice. Strumenti usati: solo ricerca sul web e lettura di pagine pubbliche (README di GitHub,
riassunti di articoli, due PDF di articoli aperti in lettura). Nessun repository clonato, nessun file scaricato per
eseguirlo, nessun codice eseguito. Il registro delle azioni (`stock/REGISTRO.md`) è stato letto solo sulle righe delle
prove (1-36) e delle idee (I1-I38).

**Avvertenza sui numeri.** Ogni numero ha accanto l'indirizzo da cui viene. Quando viene da un riassunto di terzi o da
un estratto di ricerca e non dall'articolo, è scritto. Le pagine che non ho potuto aprire o leggere per intero sono
elencate alla sezione 6.

---

## 1. Il quadro: cosa dicono le raccolte serie di repliche (la fonte più solida)

| Raccolta | Cosa contiene | Il numero che conta | Fonte |
|---|---|---|---|
| **Open Source Asset Pricing** (Chen e Zimmermann) | Codice (Python e R) che ricostruisce 319 segnali pubblicati sulle azioni americane; servono dati a pagamento (WRDS) per rifarlo; i rendimenti dei portafogli sono scaricabili da openassetpricing.com | Dei 161 segnali chiaramente significativi negli articoli originali, il 98% ha t sopra 1,96 nella replica: **gli effetti si replicano sul periodo degli articoli** | https://github.com/OpenSourceAP/CrossSection ; https://www.federalreserve.gov/econres/feds/open-source-cross-sectional-asset-pricing.htm |
| **JKP, «Is there a replication crisis in finance?»** (Jensen, Kelly, Pedersen, Journal of Finance 78, 2023) | 153 fattori in 93 paesi; repository non più mantenuto, passato a `bkelly-lab/jkp-data`; fattori scaricabili da jkpfactors.com | Circa l'85% dei fattori si replica (84,9%: numero da un riassunto di CXO Advisory, non verificato sull'articolo) | https://github.com/bkelly-lab/ReplicationCrisis ; https://www.cxoadvisory.com/big-ideas/re-examining-equity-factor-research-replicability/ |
| **Chen e Velikov, «Zeroing in on the expected returns of anomalies»** (JFQA 58, 2023) | Le stesse anomalie, ma **con i costi veri e dopo la pubblicazione** | Versione di lavoro (2020, 120 anomalie, PDF letto pagine 1-6): **66 punti base al mese prima dei costi → 38 dopo i costi → 13 dopo la pubblicazione → 8 dopo il 2005**; il 90° percentile, con pesi per capitalizzazione, rende 6 punti base al mese; il prestito per lo scoperto costa da solo 10-20 punti base al mese. Versione pubblicata (204 anomalie, da riassunto di ricerca): **4 punti base al mese** per l'anomalia media, le più forti al massimo 10 | https://www.federalreserve.gov/econres/feds/files/2020039pap.pdf ; https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/zeroing-in-on-the-expected-returns-of-anomalies/945133D5A3ECEEAF466AEE91551FD225 |
| **Greenwood e Sammon, «The disappearing index effect»** (Journal of Finance 80, 2025) | Entrate e uscite dall'S&P 500 | Entrata: da +7,4% negli anni '90 a meno dell'1% nell'ultimo decennio; uscita: −0,6% nel 2010-2020, non diverso da zero | https://papers.ssrn.com/abstract=4294297 ; https://www.nber.org/system/files/working_papers/w30748/w30748.pdf |

**Cosa ne segue per noi.** Le raccolte serie dicono due cose insieme: gli effetti pubblicati sono veri sul passato degli
articoli, ma **dopo i costi e dopo la pubblicazione l'anomalia media vale quasi zero** (Chen e Velikov). È esattamente
quello che hanno trovato le nostre prove 12, 13, 24, 31, 32, 33 e 34. Le idee che restano interessanti sono quindi di
due tipi: (a) **flussi obbligati e prevedibili** (qualcuno deve comprare o vendere in un giorno noto), meglio se
sull'indice, dove i costi sono minimi; (b) segnali **pubblicati da poco** o fatti con dati che pochi elaborano (testi
della SEC). Le classifiche delle liste «awesome» riportano invece Sharpe **prima dei costi** (vedi sezione 5).

---

## 2. Le idee nuove che giudico serie (le migliori prima)

Nessuna di queste è nel registro, salvo dove è detto «parente di». Dati nostri: prezzi al giorno e al minuto di Alpaca
(dal 2016), dati pubblici della SEC e di FINRA, Yahoo.

### N1. Anticipare il ribilanciamento dei fondi 60/40 (SPY contro le obbligazioni del Tesoro) — **la più promettente**

- **Cosa fa.** Quando nel mese le azioni sono salite più delle obbligazioni, i fondi pensione e i fondi «a data» devono
  vendere azioni e comprare obbligazioni (a fine mese o quando superano una soglia): la strategia va corta sulle azioni e
  lunga sulle obbligazioni il giorno prima, e al contrario quando le azioni sono rimaste indietro. Due segnali: «soglia»
  (scarto del peso azionario di un 60/40 simulato, soglie da 0 a 2-2,5%) e «calendario» (ultima settimana del mese).
- **Dove.** Harvey, Mazzoleni, Melone, «The Unintended Consequences of Rebalancing», NBER w33554 (2025, versione del 14
  gennaio 2026, presentata all'AFA 2026): https://www.nber.org/papers/w33554 ; PDF letto (pagine 1-6):
  https://www.edhec.edu/sites/default/files/2026-03/Scientific%20paper.%20ssrn-5122748.pdf . Nessun repository GitHub
  degli autori trovato; una replica indipendente su blog: https://quantreturns.substack.com/p/front-running-the-rebalancers ;
  una pagina di backtest su QuantConnect che cita la scheda Quantpedia (codice non aperto):
  https://www.quantconnect.com/terminal/cache/embedded_backtest_b09aa0102d4041f655deeefe24d5622c.html
- **Prova dichiarata.** Un segnale più alto di una deviazione standard abbassa il rendimento delle azioni di circa 16-17
  punti base il giorno dopo; l'effetto rientra quasi tutto in due settimane; la prevedibilità del «calendario» c'è solo a
  fine mese; il segnale diventa significativo dai primi anni 2000 (PDF, pagine 2-4). Strategia sui futures S&P 500 contro
  Treasury a 10 anni, 1997-2023: **Sharpe sopra 1** (PDF, pagina 4); secondo CXO Advisory **Sharpe 1,08 prima dei costi,
  contro 0,38 delle azioni e 0,50 delle obbligazioni, settembre 1997 - marzo 2023, calibrata sullo stesso periodo**
  (https://www.cxoadvisory.com/calendar-effects/exploiting-predictable-institutional-portfolio-rebalancing). Replica del
  blog Quant Returns: versione con SPY e TLT **Sharpe 1,17**, crescita annua 15,62%, asimmetria 7,07; versione futures
  Sharpe «sopra 1,4»; periodo non scritto; **costi non contati**.
- **Sospetto più forte.** Costi non contati (si gira ogni giorno) e **calibrazione sullo stesso periodo** (le soglie e la
  scala dei due segnali sono scelte sui dati). Seconda cosa: l'asimmetria 7 della replica dice che pochi giorni enormi
  (2008? 2020?) possono fare tutto il risultato. Terza: è parente del «cambio del mese» (prova 6), ma qui la direzione
  dipende da come è andato il mese, quindi è un'altra regola.
- **Punto a favore.** Il campione dell'articolo finisce a marzo 2023: **da aprile 2023 a oggi è un vero periodo fuori
  campione** per noi. Si fa su due fondi quotati liquidi (SPY e IEF o TLT): costi bassi, scoperto sullo SPY economico.
- **Dati.** Prezzi giornalieri rettificati per i dividendi di SPY, IEF (Treasury 7-10 anni) e TLT: Yahoo o Alpaca. Basta.

### N2. Le giornate in cui le aziende pagano tanti dividendi (pressione dei dividendi reinvestiti sull'indice)

- **Cosa fa.** I dividendi pagati (date note settimane prima) vengono in parte reinvestiti in borsa: nei giorni con molti
  pagamenti l'indice sale di più. Si tiene l'indice (o se ne tiene di più) solo nei giorni con i pagamenti più alti.
- **Dove.** Hartzmark e Solomon, «Predictable Price Pressure», NBER w30688; pubblicato come «Market-Wide Predictable
  Price Pressure», American Economic Review 115 (2025): https://www.nber.org/papers/w30688 ;
  https://econpapers.repec.org/RePEc:aea:aecrev:v:115:y:2025:i:9:p:3171-3213 . Nessun repository GitHub trovato.
- **Prova dichiarata.** Il rendimento dell'indice nel quinto dei giorni con più pagamenti è **quattro volte** quello del
  quinto con meno (abstract NBER); vale anche fuori dagli Stati Uniti; più forte con molto reinvestimento e poca
  liquidità. Secondo Alpha Architect (non verificato sull'articolo) +13 punti base nei 5 giorni con più pagamenti e +5
  nei 50 giorni con più pagamenti (https://alphaarchitect.com/can-investment-flows-affect-prices-yep/); nel primo
  trimestre l'effetto è più forte, nel quarto non c'è (dal riassunto di ricerca del PDF NBER). Costi: non dichiarati.
- **Sospetto più forte.** Ha la **stessa forma** delle prove 9 e 14 (stare dentro o aumentare la leva solo nei «giorni
  speciali»), bocciate nel periodo chiuso: pochi giorni, pochi punti base, poca forza statistica. Il «quarto trimestre
  senza effetto» puzza di scelta a posteriori se usato come filtro. Il moltiplicatore di prezzo (1,5-2,3) è la tesi
  degli autori, non un risultato di trading.
- **Dati.** Date di **pagamento** e importi dei dividendi di tutte le azioni dell'S&P 500: l'API delle operazioni
  societarie di Alpaca riporta `payable_date` e l'importo (https://docs.alpaca.markets/reference/corporateactions ; da
  verificare quanto indietro va lo storico); Yahoo dà solo la data di stacco. Prezzi SPY: Yahoo/Alpaca.

### N3. «Lazy prices»: le aziende che non cambiano il testo dei loro bilanci annuali e trimestrali

- **Cosa fa.** Si confronta il testo del 10-K (o 10-Q) con quello dell'anno prima: chi lo cambia molto (soprattutto i
  rischi e la discussione della direzione) va peggio nei mesi dopo, chi non lo cambia va meglio. Ogni mese si comprano le
  aziende che non hanno cambiato e si vendono (o si copre con lo SPY) quelle che hanno cambiato.
- **Dove.** Cohen, Malloy, Nguyen, «Lazy Prices», Journal of Finance 75 (2020), NBER w25084:
  https://www.nber.org/papers/w25084 ; riassunto NBER:
  https://www.nber.org/digest/nov18/are-investors-inattentive-sec-mandated-corporate-reports . Su GitHub:
  https://github.com/AlexBdx/secScraper (10-K e 10-Q 1997-2018, quintili di somiglianza; **il README non riporta numeri**);
  una replica su QuantConnect con le 100 azioni più liquide (solo lato comprato, risultati non letti):
  https://www.quantconnect.com/research/20966/filing-language-stability-as-a-selection-signal/
- **Prova dichiarata.** Fino a **188 punti base al mese** di rendimento in eccesso per comprati meno venduti sulla sezione
  dei rischi (abstract, tramite https://www.nber.org/papers/w25084); per la misura generale, con pesi per capitalizzazione,
  **34-58 punti base al mese** (4-7% l'anno) nell'anno dopo; i guadagni arrivano fino a 18 mesi dopo il deposito, non si
  annullano dopo, e secondo gli autori non dipendono dalla dimensione dell'azienda (riassunto NBER). Periodo dell'articolo
  1995-2014 circa (da un riassunto di ricerca). Costi: non contati, per quanto ho potuto vedere.
- **Sospetto più forte.** Troppe varianti possibili (quattro misure di somiglianza, sezioni diverse, 10-K o 10-Q): il
  188 è il migliore della scelta. Estrarre la sezione dei rischi dal testo è fragile. Punto a favore: la prima bozza
  pubblica è del novembre 2015 (https://dash.harvard.edu/server/api/core/bitstreams/837f965d-78fd-4f8e-8f8e-78622de15a26/content ,
  da riassunto di ricerca), quindi **il nostro periodo 2016-2024 è già dopo la pubblicazione**. Ritmo lento (mesi):
  costi bassi.
- **Dati.** Testi completi dei 10-K e 10-Q da EDGAR (SEC, con l'indirizzo di contatto già usato per la prova 18), data
  di deposito vera per il momento d'ingresso; prezzi Alpaca. Si fa sull'S&P 500 o su tutte le azioni liquide.

### N4. Il mese del dividendo (le azioni salgono nel mese in cui si aspetta il dividendo)

- **Cosa fa.** Ogni mese si comprano le azioni che, guardando il calendario dei dividendi dell'anno prima, dovrebbero
  pagare il dividendo questo mese; si copre con lo SPY o con le azioni che non pagano.
- **Dove.** Hartzmark e Solomon, «The dividend month premium», Journal of Financial Economics 109 (2013):
  https://econpapers.repec.org/RePEc:eee:jfinec:v:109:y:2013:i:3:p:640-660 . Replicato nella raccolta di Chen e
  Zimmermann come segnale `DivSeason` (https://raw.githubusercontent.com/OpenSourceAP/CrossSection/master/SignalDoc.csv ,
  file di documentazione letto, non scaricato).
- **Prova dichiarata.** Nella tabella di Chen e Zimmermann: rendimento 0,36% al mese, **t 16,19**, campione fino al 2011
  (SignalDoc.csv). Circa 41 punti base al mese in eccesso secondo un riassunto di Alpha Architect
  (https://alphaarchitect.com/?p=94467). Gli autori la dicono grande come il premio del valore ma meno ballerina.
- **Sospetto più forte.** È lo stesso meccanismo del «premio del comunicato» (prova 30: evento prevedibile, data presa
  dall'anno prima), che da noi ha dato **−0,130% a settimana**: rischio alto che nelle grandi aziende non ci sia più.
  CXO Advisory scrive che costi e prestito per lo scoperto «ridurrebbero di molto, forse annullerebbero» il premio
  (https://www.cxoadvisory.com/fundamental-valuation/dividend-month-premium). Nessuna replica dopo il 2013 trovata. La
  pressione rientra dopo lo stacco (lo dicono gli autori): l'uscita va scritta prima.
- **Dati.** Storico dei dividendi (date di stacco e importi) da Yahoo o Alpaca; prezzi Alpaca. Fattibile sull'S&P 500.

### N5. L'emissione netta di azioni (chi riacquista azioni proprie va meglio di chi ne emette)

- **Cosa fa.** Una volta l'anno (o al trimestre) si calcola di quanto è cambiato il numero di azioni in circolazione
  nell'ultimo anno (rettificato per gli split); si comprano le aziende che lo hanno ridotto e si vendono (o si copre con
  lo SPY) quelle che lo hanno aumentato.
- **Dove.** Pontiff e Woodgate, Journal of Finance 63 (2008); Daniel e Titman, Journal of Finance 61 (2006). Replicati
  in Chen e Zimmermann come `ShareIss1Y`, `ShareIss5Y`, `CompEquIss`
  (https://raw.githubusercontent.com/OpenSourceAP/CrossSection/master/SignalDoc.csv).
- **Prova dichiarata.** `ShareIss1Y` **t 7,08** (campione fino al 2003); `ShareIss5Y` e `CompEquIss` t 4,39 (fino al
  2003). Rendimenti mensili non riportati nella tabella per questi segnali. Costi: no. Post-pubblicazione: non ho trovato
  una prova specifica dopo il 2016; uno studio su 231 anomalie trova negli Stati Uniti un calo dopo la pubblicazione di
  circa il 62% con pesi uguali (dagli estratti della ricerca; fonte primaria non aperta e non individuata con
  certezza, probabilmente Jacobs e Müller:
  https://www.wiwi.hu-berlin.de/en/Professorships/bwl/finance/seminars/papers-fin-acc-res-seminars/17s/jacobs.pdf).
- **Sospetto più forte.** Il guaio della prova 31: **le «cornici» della SEC danno i numeri rifatti dopo** (revisione
  FAIL). Qui il numero di azioni va preso dal primo deposito (campo «filed» di ciascun valore), e gli split vanno
  corretti a mano: un errore sugli split crea falsi «grandi riacquisti». Effetto più forte nelle piccole, e il lato
  venduto (chi emette) costa il prestito.
- **Dati.** SEC: numero di azioni in circolazione dai depositi XBRL (copertina dei 10-K/10-Q), con la data di deposito;
  split da Alpaca o Yahoo; prezzi Alpaca. Ritmo annuale: costi minimi.

### N6. Gli attivisti: comprare subito dopo il deposito del modulo 13D alla SEC

- **Cosa fa.** Quando un investitore supera il 5% di un'azienda con l'intenzione di influire sulla gestione deposita un
  13D; si compra a pochi minuti dall'accettazione del modulo da parte della SEC (come nella prova 36) e si tiene settimane
  o mesi.
- **Dove.** Brav, Jiang, Partnoy, Thomas, «Hedge fund activism», Journal of Finance (2008):
  https://law.duke.edu/sites/default/files/centers/gfmc/session_3/2_brav_et_al-hedge_fund_activism-2008.pdf (numeri presi
  dagli estratti della ricerca, PDF non aperto). Nessun repository GitHub con risultati trovato.
- **Prova dichiarata.** Circa **+7-8%** di rendimento in eccesso nella finestra da 20 giorni prima a 20 dopo l'annuncio,
  2001-2006; **nessun calo nell'anno dopo**; prezzo e volume iniziano a salire circa 10 giorni prima del deposito. Costi:
  no.
- **Sospetto più forte.** Gran parte del salto avviene **prima** del deposito e nei primi minuti dopo: quello che resta a
  chi arriva «due minuti dopo» può essere poco. La prova 36 insegna che fuori seduta lo scarto mediano è 103,6 punti
  base. Le aziende colpite sono spesso piccole. Dal febbraio 2024 il termine per depositare è sceso da 10 giorni a 5
  giorni lavorativi (da una fonte secondaria, **da verificare sulla SEC**): il periodo cambia regola a metà. Scegliere
  «gli attivisti famosi» a mano sarebbe guardare nel futuro: si usano tutti i 13D.
- **Dati.** EDGAR: elenco dei moduli SC 13D con l'ora vera di accettazione (la stessa via della prova 36); prezzi al
  minuto di Alpaca.

### N7. La stagionalità dello stesso mese (chi è andato bene a marzo degli anni passati va bene a marzo)

- **Cosa fa.** Ogni mese si comprano le azioni con il rendimento più alto nello stesso mese di calendario degli anni
  precedenti e si vendono quelle con il più basso.
- **Dove.** Heston e Sadka, Journal of Financial Economics 87 (2008); Keloharju, Linnainmaa, Nyberg, «Return
  seasonalities», Journal of Finance 71 (2016), NBER w20815: https://www.nber.org/papers/w20815.pdf . Replicata in Chen e
  Zimmermann come `MomSeason`, `MomSeasonShort`, `MomSeason06YrPlus`.
- **Prova dichiarata.** `MomSeasonShort` (solo l'anno prima) 1,15% al mese, **t 7,6**; `MomSeason` (anni 2-5) 0,67%, t
  5,35; campione fino al 2002 (SignalDoc.csv). Keloharju e altri: in media **13% l'anno** nel 1963-2011 (dagli estratti
  della ricerca). Costi: no. Un commento sulla pagina del premio AQR la dice «difficile da negoziare e forse in via di
  sparizione» (https://www.aqr.com/Our-Firm/AQR-Insight-Award/2015/Common-Factors-in-Return-Seasonalities).
- **Sospetto più forte.** **Il portafoglio cambia quasi tutto ogni mese**: costi alti, proprio il tipo di anomalia che
  Chen e Velikov azzerano. Per gli anni 2-10 servono molti anni di storia: Alpaca parte dal 2016 e Yahoo ha solo le
  aziende ancora quotate (titoli sopravvissuti).
- **Dati.** Rendimenti mensili delle azioni (Alpaca dal 2016: si può fare solo la versione «anno prima»).

### N8. Il rimbalzo solo quando non ci sono notizie (variante di due famiglie già bocciate)

- **Cosa fa.** Dopo un grande movimento di un mese, si scommette sul ritorno **solo** se l'azione non ha avuto notizie;
  se le notizie c'erano (soprattutto cattive) si segue la direzione.
- **Dove.** Chan, «Stock price reaction to news and no-news: drift and reversal after headlines», Journal of Financial
  Economics 70 (2003): https://econpapers.repec.org/RePEc:eee:jfinec:v:70:y:2003:i:2:p:223-260 . Nessun repository
  trovato.
- **Prova dichiarata.** Deriva forte dopo le cattive notizie, meno dopo le buone; ritorno dopo i grandi movimenti senza
  notizie; **soprattutto nelle azioni piccole e poco scambiate** (abstract). Numeri mensili non letti (articolo non
  aperto).
- **Sospetto più forte.** È una variante delle prove 3 e 11 (rimbalzo, bocciate) e 28-29 (tono delle notizie, bocciate);
  l'effetto vive nelle piccole, dove le prove 32 e 34 hanno perso con i costi. Va contata come prova nuova di una
  famiglia già provata.
- **Dati.** Archivio delle notizie di Alpaca (già usato nella prova 28) e prezzi Alpaca.

### N9. Le «idee migliori» dei gestori (dai moduli 13F della SEC) — priorità bassa

- **Cosa fa.** Ogni trimestre si comprano le azioni su cui i gestori puntano di più rispetto al loro solito, lette dai
  moduli 13F con 45 giorni di ritardo.
- **Dove.** Cohen, Polk, Silli, «Best Ideas»: https://personal.lse.ac.uk/polk/research/BestIdeas.pdf (non aperto).
- **Prova dichiarata.** Circa 2,8-4,5% l'anno meglio del mercato secondo un blog che cita una versione del 2009; per i
  fondi speculativi piccoli +15% l'anno sui grandi (estratti della ricerca, non verificati). Campione 1991-2005. Costi:
  no (https://quantpedia.com/Screener/Details/42).
- **Sospetto più forte.** L'articolo usa le partecipazioni dei fondi alla data di fine trimestre, non alla data di
  pubblicazione: con il ritardo vero di 45 giorni il vantaggio può sparire (un progetto su GitHub, Super Investor Compass,
  dice che la maggior parte dei gestori copiati con il ritardo fa peggio: affermazione non verificata,
  https://super-investor-compass.vercel.app/about/). Le «idee migliori» sono azioni piccole e poco liquide.
- **Dati.** SEC: moduli 13F (formato strutturato dal 2013), prezzi Alpaca.

### N10. Le coppie di azioni (pairs trading) — priorità bassa

- **Cosa fa.** Si cercano coppie di azioni che si muovono insieme; quando si allontanano si compra quella rimasta indietro
  e si vende l'altra, finché si riavvicinano.
- **Dove.** Gatev, Goetzmann, Rouwenhorst, Review of Financial Studies 19 (2006):
  https://econpapers.repec.org/RePEc:oup:rfinst:v:19:y:2006:i:3:p:797-827 ; su GitHub solo versioni didattiche senza costi
  (per esempio nella raccolta https://github.com/je-suis-tm/quant-trading , «all trades are frictionless»).
- **Prova dichiarata.** Fino all'11% l'anno nel 1962-2002; Do e Faff: il calo continua fino al 2008; una tesi CBS sul
  1963-2019: **nessun guadagno significativo dopo i costi**; Zhu (2024) dice il contrario, 6,2% l'anno per la variante
  migliore (riassunti, non verificati): https://harbourfrontquant.substack.com/p/further-on-the-profitability-of-pairs ;
  https://research-api.cbs.dk/ws/portalfiles/portal/62182077/905597_Liquidity_Premium_in_Pairs_Trading.pdf
- **Sospetto più forte.** È un rimbalzo (famiglia delle prove 3 e 11) con molte varianti possibili; «la variante
  migliore» di Zhu è proprio il problema delle troppe varianti.
- **Dati.** Prezzi giornalieri Alpaca.

---

## 3. Strategie trovate che sono già nel registro

| Trovata dove | Nel registro |
|---|---|
| Inizio del mese (scheda Quantpedia, Sharpe 1,04 nel 1926-2005: https://quantpedia.com/strategies/turn-of-the-month-in-equity-indexes) | prova 6, bocciata |
| Tenere solo di notte | prova 4, bocciata; idea I9 |
| Rottura della prima candela, azioni «in gioco» (Zarattini) | prove 17, 20, 21, 35, bocciate |
| Zona di rumore (Zarattini) | prova 2, bocciata |
| **Tendenza in giornata sopra/sotto il VWAP su QQQ** (Zarattini e Aziz, 2018-2023, 25'000 → 192'656 dollari dichiarati: https://concretumgroup.com/volume-weighted-average-price-vwap-the-holy-grail-for-day-trading-systems/) | **non nel registro come regola**, ma è della famiglia della tendenza in giornata (prove 2 e 17, bocciate). Le repliche su GitHub non concordano: una per smentirla (https://github.com/algo-dude/QuantConnect_public , perdita massima 49% nel suo rapporto) e una su QuantConnect che dice che si replica nel 2018-2023 (risultati dagli estratti della ricerca, codice non aperto). Non la metto fra le nuove |
| Ultima mezz'ora (fondi a leva che ribilanciano in chiusura) | prova 1, bocciata; idea I8 |
| Titoli tolti dall'S&P 500 | prova 8, bocciata (Greenwood e Sammon lo confermano: −0,6% nel 2010-2020) |
| Deriva dopo i bilanci | prove 10 e 34, bocciate; idea I13 |
| Premio del comunicato | prova 30, bocciata |
| Acquisti dei dirigenti | prove 18, 19, 27, 36, bocciate |
| Vendite allo scoperto | prove 24 e 32, bocciate |
| Tono delle notizie | prove 28 e 29, bocciate |
| Redditività lorda | prova 31, bocciata |
| Momento dei settori; momento a 12 mesi | prove 33 e 13, bocciate |
| Bassa volatilità, «betting against beta» | prova 12, bocciata (stessa famiglia) |
| Tendenza dell'indice e di altre classi | prove 5 e 26 |
| Più investiti quando il mercato è calmo | prova 15 |
| Prima della banca centrale | prove 7, 9, 14 |
| Agenti a modelli linguistici (TradingAgents) | idea I24 |

---

## 4. Il criterio con cui ho ordinato le dieci

1. **Flussi obbligati e prevedibili sull'indice** (N1, N2): costi minimi, meccanismo chiaro (qualcuno deve comprare o
   vendere), poche varianti. N1 sopra N2 perché ha un vero periodo fuori campione dopo marzo 2023 e una replica
   indipendente, mentre N2 ha la forma dei «giorni speciali» già bocciati due volte nel periodo chiuso.
2. **Dati della SEC lavorati da pochi, ritmo lento** (N3, N5): costi bassi; N3 è stato reso pubblico nel 2015, quindi il
   nostro 2016-2024 è già una prova dopo la pubblicazione.
3. **Eventi prevedibili sulle azioni** (N4, N6): effetti forti negli articoli, ma parenti stretti di prove bocciate (30 e
   36).
4. **Segnali ad alto ricambio o di famiglie bocciate** (N7-N10): li tengo per completezza.

---

## 5. Categorie scartate e perché

- **Robot di indicatori tecnici** (MACD, Bollinger, RSI, Heikin-Ashi, Parabolic SAR, «London breakout»...): per esempio
  https://github.com/je-suis-tm/quant-trading dichiara «all trades are frictionless» e non riporta risultati né periodi
  fuori campione. Nessuna prova, nessun articolo dietro.
- **Liste «awesome»**: https://github.com/wilsonfreitas/awesome-quant elenca librerie e strumenti, non strategie con
  risultati sulle azioni americane. https://github.com/paperswithbacktest/awesome-systematic-trading (lo stesso di
  `edarchimbaud/awesome-systematic-trading`) ha una tabella di strategie azionarie con Sharpe da 1,28 a 1,89, ma la pagina
  stessa dice che sono **prima dei costi** e su finestre diverse, e molte sono europee o di mercati di frontiera; la
  mediana dichiarata sulle 4'843 repliche è Sharpe 0,37. Utile solo come elenco di titoli di articoli.
- **Modelli di previsione con apprendimento automatico o per rinforzo** (FinRL, qlib, raccolte didattiche): pagine non
  aperte una per una; li scarto come categoria perché di solito non contano i costi, hanno periodi di prova brevi e
  moltissime varianti. TradingAgents è già nel registro (I24).
- **Copiare gli acquisti dei parlamentari americani**: Belmont, Sacerdote, Sehgal, Van Hoek, Journal of Public Economics
  207 (2022), dati 2012-2020: gli acquisti dei deputati fanno **26 punti base peggio** del mercato in sei mesi, e anche le
  code sono come una scelta a caso (https://ideas.repec.org/a/eee/pubeco/v207y2022ics0047272722000044.html). I backtest
  dei venditori di dati partono dal 2020 e sono ipotetici (https://www.quiverquant.com/strategies/s/Congress%20Buys).
- **Entrate nell'S&P 500**: l'effetto è sceso sotto l'1% (Greenwood e Sammon, sopra); coerente con la prova 8.
- **Strategie su opzioni, consigli degli analisti, flussi dei fondi**: servono dati a pagamento (OptionMetrics, IBES,
  ANcerno) che non abbiamo. **Superato in parte (audit del 27 novembre 2026):** gli indici delle strategie in opzioni della CBOE
  sono gratuiti (PUT dal 1991, WPUT, CNDR, BXM) e Alpaca dà le opzioni dal febbraio 2024 (idee I62 e I64 del registro); i consigli
  degli analisti sono stati provati con i titoli delle notizie (prova 53). Le N4, N8, N9 e N10 qui sopra sono entrate nel registro
  come I69, I68, I70 e I71.
- **Il flusso degli ordini dei piccoli risparmiatori** (Boehmer, Jones, Zhang, Zhang, Journal of Finance 76, 2021: chi è
  comprato dai piccoli fa circa 10 punti base meglio la settimana dopo): servirebbero tutti gli scambi con il prezzo al
  decimo di centesimo; l'algoritmo riconosce solo il 35% degli ordini dei piccoli secondo Barber e altri; 10 punti base a
  settimana non pagano i costi su azioni piccole. Fonti dagli estratti della ricerca:
  https://econpapers.repec.org/RePEc:bla:jfinan:v:76:y:2021:i:5:p:2249-2305 . Scartata per ora.
- **Raccolte di repliche come strategia in sé** (comprare «tutte le anomalie»): Chen e Velikov danno circa 20 punti base
  al mese per i modi di combinare le anomalie, prima del prestito per lo scoperto (riassunto di ricerca della versione
  pubblicata): con i dati gratuiti che abbiamo non si rifà, e il margine è sotto i costi del lato venduto.

---

## 6. Cosa non ho potuto aprire o verificare

- Versione pubblicata di Chen e Velikov (JFQA 2023): numeri (4 punti base, 10, 20, 44) dagli estratti della ricerca; ho
  letto solo la versione di lavoro del 2020 (pagine 1-6).
- JKP: l'84,9% viene da un riassunto di CXO Advisory.
- Harvey, Mazzoleni, Melone: letto il PDF pagine 1-6; la sezione 5 con la strategia (tabelle, costi, sottoperiodi) **non
  letta**; lo Sharpe 1,08 viene da CXO Advisory (pagina in parte a pagamento); i numeri della replica Quant Returns sono
  nel testo del blog, le tabelle sono immagini non lette; il codice su QuantConnect non è stato aperto.
- Hartzmark e Solomon (dividendi sull'indice): letto solo l'abstract NBER; i 13 e 5 punti base vengono da Alpha Architect.
- Lazy prices: articolo non aperto; numeri dall'abstract (tramite estratti) e dal riassunto NBER; data della prima bozza
  (novembre 2015) dagli estratti della ricerca.
- Brav e altri (attivisti), Chan (notizie), Cohen-Polk-Silli (idee migliori), Gatev e altri (coppie): articoli non aperti,
  numeri dagli estratti della ricerca o da riassunti.
- La tabella delle strategie di paperswithbacktest è stata letta solo in parte (la pagina è lunga 249'000 caratteri).
- Repository di GitHub con codice (algo-dude, QuantConnect 552, secScraper): letti solo i README o gli estratti, mai il
  codice.
