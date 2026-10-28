# La letteratura sui segnali delle crypto non ancora provati (28 ottobre 2026)

Rapporto di un aiutante separato, chiesto il 28 ottobre 2026 alle 00:25 UTC con l'elenco di tutto quello che abbiamo già provato
(`research/REGISTRO.md`). **I numeri vengono dai lavori citati**. Le probabilità sono stime dell'aiutante, non misure. Prima di ogni prova
la fonte va riletta.

Fonti di dati verificate dall'aiutante con chiamate vere:
* **CoinMetrics community**, gratis:
  * indirizzi attivi per 138 attivi, indirizzi con saldo, offerta e capitalizzazione (circa 50 hanno un perpetuo su Binance);
  * non c'è SOL, mancano quasi tutte le monete nuove e non ci sono gli indirizzi nuovi;
  * i flussi verso le borse solo per BTC ed ETH, e i valori vengono ricalcolati dopo, quindi usano informazioni che allora non c'erano.
* **Deribit** (`history.deribit.com`): le operazioni sulle opzioni, gratis.
* **DefiLlama**: 1.320 attacchi informatici ai protocolli, con la sola data senza l'ora.

## I segnali, dal più promettente

1. **Il valore misurato con gli utenti** (prezzo o capitalizzazione rispetto agli utenti).
   * **Cosa fa e perché**: long le monete con molti utenti rispetto al valore, short le «care», a settimana. Il prezzo che corre oltre
     l'uso reale rientra.
   * **Fonti**:
     * Liu, Tsyvinski e Wu 2021, «Accounting for Cryptocurrency Value», SSRN 3951514: 127 monete dal 2018 al giugno 2021, prezzo diviso
       per gli indirizzi nuovi (Glassnode), +1,9% a settimana, Sharpe 2,0.
     * Borri, Liu, Tsyvinski e Wu 2026, *Annual Review of Financial Economics* 18 (arXiv 2510.14435): −3,5% a settimana con il segno del
       «caro», t −3,50 sul 2014-2025 e −2,3% (t −2,32) dal 2020. Va verificato quanto del «dal 2020» è dopo il giugno 2021.
     * Liebi 2022, *Economic Modelling* 109, 105777: indirizzi attivi divisi per la capitalizzazione, 652 monete dal 2017 al 2020, +3,7
       punti a settimana, quasi tutto nelle piccole.
     * Cong, Karolyi, Tang e Zhao, «Crypto Value, Factor Pricing, and Market Segmentation», *Management Science*.
   * **Dati**: gli indirizzi nuovi sono a pagamento; la versione di Liebi è **gratis con CoinMetrics** su circa 50 monete con il
     perpetuo.
   * **Stima**: circa 15%.
2. **Il capitale lento: corsa più crollo nel trimestre (EWIL).**
   * **Cosa fa e perché**: le monete con una grande salita e un grande crollo nei 3 mesi prima rendono male nelle 1-8 settimane dopo.
   * **Fonte**: Li, Liao, Yang e Zhang, «Predictive Crypto Crashes and Asset Pricing Implications: An Inelastic Market Perspective»,
     bozza del maggio 2026 (ABFER 2026). 4.284 monete fino al maggio 2024, +2,5% a settimana fuori campione, +3,4% insieme al momento.
     Non è pubblicato, e non c'è un'analisi dei costi.
   * **Dati**: gratis.
   * **Si sovrappone in parte** a MAX, volatilità e momento.
   * **Stima**: circa 10%.
3. **La crescita degli utenti** (indirizzi con saldo).
   * **Cosa fa**: long le monete in cui gli indirizzi con saldo crescono di più nella settimana.
   * **Fonte**: Cong e coautori, +4,0% a settimana (t 2,8), 616 monete dal 2014 al gennaio 2021. Per Liu, Tsyvinski e Wu, invece, il
     prezzo prende la notizia subito.
   * **Dati**: gratis con CoinMetrics.
   * **Stima**: circa 8%.
4. **L'inclinazione delle opzioni sul Bitcoin** (la differenza fra call e put a 25 delta).
   * **Fonti**:
     * Neo 2026, tesi di dottorato alla Singapore Management University, dati Deribit dal 2021 al 2025: t 1,91 da sola, più debole dal
       2024;
     * Alexander, Deng, Feng e Wan 2023, *Journal of Financial Markets* 63.
   * **Dati**: gratis, ma il sorriso va ricostruito dalle operazioni.
   * **Stima**: circa 7%.
5. **I flussi verso le borse** (ETH, USDT).
   * **Fonte**: Chi, Chu e Hao, arXiv 2411.06327, 2017-2023.
   * **Dati**: per BTC ed ETH gratis su CoinMetrics, ma ricalcolati dopo i fatti; i flussi di USDT sono a pagamento.
   * **Stima**: circa 5%.
6. **L'attenzione su Google fra le monete.**
   * **Fonte**: Hoang e Vo 2024, *Journal of Behavioral and Experimental Finance* 44.
   * **Dati**: Google Trends, senza un servizio ufficiale e con nomi ambigui. È la stessa famiglia dell'idea su Wikipedia.
   * **Stima**: circa 5%.
7. **Il momento dei «vicini»** (le monete simili salite ieri).
   * **Fonti**:
     * Guo, Härdle e Tao 2024, *Journal of Business & Economic Statistics* 42(2): +1,08% al giorno sul 2016-2018, senza costi;
     * la versione al minuto è già bruciata nel programma 5.
   * **Stima**: circa 5%.
8. **I grandi portafogli che accumulano Ether.**
   * **Fonte**: Chernoff e Jagtiani 2024, working paper della Federal Reserve di Philadelphia.
   * **Dati**: a pagamento.
   * **Stima**: circa 4%.
9. **Gli annunci di acquisto di Strategy (MicroStrategy).**
   * **Fonte**: K33 Research 2023, il Bitcoin a −2,2% nel giorno dell'annuncio. È un rapporto di settore.
   * **Dati**: gratis, i comunicati alla SEC su EDGAR.
   * **Stima**: circa 5%.
10. **Gli attacchi informatici ai protocolli.**
    * **Fonte**: Kitzler, Paquet-Clouston e Haslhofer 2025, −14% intorno all'attacco, ma solo 22 casi e nessuna discesa dopo la notizia.
    * **Stima**: circa 4%.
11. **La potenza di calcolo del Bitcoin.**
    * **Fonte**: VanEck 2025 (rapporto di settore), Bhambhwani e coautori 2023.
    * **Dati**: circa un evento l'anno.
    * **Stima**: circa 3%.

## Le famiglie che la letteratura considera consumate nelle crypto

* **Dimensione, illiquidità e volume**: l'effetto sta nelle monete piccolissime (Fieberg, Liedtke e Zaremba 2024).
* **Il momento**: dopo il 2020 regge solo quello a 2 settimane, e i costi lo mangiano.
* **Carry e funding**: negativo nel 2025 (Borri e coautori 2026; Schmeling, Schrimpf e Todorov, «Crypto carry»).
* **Le differenze di prezzo fra borse**: esistono solo dove non si può investire.
* **I fattori presi dalle azioni**: non significativi dopo il 2020. Su 20.736 modi di fare le prove reggono solo dimensione e momento
  (Fieberg, Günther, Poddig e Zaremba 2024).
* **I modelli complessi**: aggiungono poco.
* **Il ritardo fra monete**: dura al massimo 10 minuti.
* **Il sentimento dai titoli delle notizie**: non dà guadagni fuori campione.

Per noi il funding fra monete regge ancora sul 2025-2026 (G1, G1N), ma la letteratura avverte che il carry nel suo insieme si è
indebolito: è un motivo in più per guardare il paper e il demo.
