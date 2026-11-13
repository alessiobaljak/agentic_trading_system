# Registro di strategy-scout (voci aperte e ultime 10; il resto in ARCHIVE.md)

Le idee nuove proposte dal cercatore di idee (dall'11 novembre 2026), con il perché forte e la fonte. Le regole delle prove stanno nei
file delle prove; la riga nel registro la scrive la sessione principale.

## Voci aperte
- Prova 149, la 1:1:1 (idea del proprietario): regole scritte dalla sessione principale l'11 novembre, in corso con strategy-researcher.

## Ultime voci
- 11 novembre 2026: agente creato (il proprietario: «non fermarti a cercarne di nuove [...] dovremmo continuare a provare cose nuove»).
- 11 novembre 2026 (primo giro): proposte 2 idee. (1) l'asimmetria realizzata dai minuti (Amaya e altri, JFE 2015; Kumar 2009), come G1 ma
  con un altro segnale: regole scritte in `programma7/OTTANTOTTESIMA.md` (prova 150, 2 varianti). (2) la semivarianza al rialzo e al
  ribasso (Bollerslev, Li e Zhao, JFQA 2020): solo idea, non scritta (parente della prima, si decide dopo il suo esito). Controllati:
  registro già copre funding, premio, volume, interesse aperto, beta, volatilità, notizie, Hyperliquid, Coinbase, Kraken.

- 11 novembre 2026 (secondo giro): proposte 2 idee. (1) il weekend dei perpetui su azioni (circa 150 contratti mai usati come segnale,
  esclusi dall'universo da `esclusi.py`): rimbalzo del lunedì, long/short a quinti sul rendimento venerdì 22:00 - lunedì 00:00 (mercato
  sottile mentre Wall Street è chiusa; fonti generali Kyle 1985 e Jegadeesh 1990, nessuno studio diretto): regole in
  `programma7/OTTANTANOVESIMA.md` (prova 151, 1 variante; servono le candele da 1 ora da scaricare; storia corta, giudizio in avanti
  dal 16 novembre). (2) il ritardo delle monete piccole sul Bitcoin (Hou, RFS 2007, diffusione lenta dell'informazione): solo idea,
  indicatore sul prezzo, probabilità bassa, non scritta. Scartate dopo il controllo: sblocchi, opzioni, stablecoin, posizioni dei grandi
  conti, liquidazioni, notizie, trader di Hyperliquid, rimozioni, funding a intervalli: già in registro.

- 12 novembre 2026 (terzo giro): proposte 2 idee. (1) il libro degli ordini fra le monete, ogni giorno come G1 (long il quinto con più
  ordini fermi dal lato dei compratori entro il 5% o l'1%; Cao, Hansch e Wang, JFM 2009; Cont, Kukanov e Stoikov, JFEC 2014): dati
  `bookDepth` di Binance dal 2 gennaio 2023, gratis, mai provato su 100 monete (solo 24 monete a ore nel programma 5): regole in
  `programma7/NOVANTUNESIMA.md` (prova 153, 2 varianti). (2) la base dei future trimestrali di Binance su Bitcoin ed Ether (file
  `futures/um/daily/klines/BTCUSDT_<scadenza>` esistono, verificato): solo idea, non scritta (due soli contratti, serie nel tempo, pochi
  casi, parente del premio e del funding già provati). Scartate dopo il controllo: (a) il funding di Hyperliquid è già in registro
  (prove 135 e 137); Bybit non è raggiungibile da qui e OKX dà il funding solo per gli ultimi mesi (non verificato a fondo); (c) la quota
  del Bitcoin sul mercato è un indicatore sul prezzo (nessuna prova dirette in registro, ma vicina a «rotazione» prova 127).

- 13 novembre 2026 (quarto giro, 00:17): proposta 1 idea. La dimensione media dello scambio (dollari diviso numero di scambi, colonna
  `count` delle candele, mai usata) fra le monete, come G1: regole in `programma7/NOVANTADUESIMA.md` (prova 154, 2 varianti; Barber, Odean
  e Zhu RFS 2009; Boehmer e altri JF 2021). Solo idea, non scritta: l'illiquidità di Amihud (JFM 2002; Brauneis e altri, JBF 2021), mai
  in registro ma universo di 100 monete tutte liquide, probabilità bassa. Scartate: rapporto volume derivati/pronti (prova 101), acquisti
  aggressivi (prova 9), base dei future trimestrali (resta idea: due soli contratti).

- 13 novembre 2026 (quinto giro, 08:17): **nessuna idea con un perché forte, nessuna regola scritta** (esito valido). Controllate nel registro
  (`--cerca`): le tre idee passate il 12 novembre (funding fra borse: Hyperliquid già provato, prove 135 e 137, Bybit non raggiungibile, OKX solo
  pochi mesi; base dei trimestrali: solo due contratti su Bitcoin ed Ether, resta idea; dominanza del Bitcoin: indicatore sul prezzo, vicino a
  «rotazione», prova 127). Valutate e scartate: (1) gli hack dei protocolli (DefiLlama `api.llama.fi/hacks`, 1.351 voci, 560 dal 2021 sopra 1 milione
  di dollari; nota della sessione principale: già provati, idea 128 → prova 146, AT): quasi tutti protocolli senza perpetuo su Binance, stima di pochi decine di eventi abbinabili, t da 3 fuori portata e
  la data è solo il giorno; (2) le visite a Wikipedia per moneta (mai in registro): stesso concetto dell'attenzione delle notizie, già no (prova 138,
  Sharpe -0,07 e -1,22), copertura parziale delle monete, il limite di richieste dell'API blocca lo scarico; (3) l'effetto del quarto d'ora (Kim e
  Hansen, arXiv 2607.09426, luglio 2026, sei perpetui di Binance: lo squilibrio degli ordini all'apertura dei quarti d'ora prevede i rendimenti a 4-12
  ore): fatto nuovo, ma serve il flusso dei singoli scambi (nelle candele da 1 minuto c'è solo il volume dei compratori aggressivi), l'orizzonte
  sono ore (costi di circa 0,12% a giro), e il segnale a livello di moneta è parente della prova 9; resta idea, non scritta; (4) la stagionalità per
  ora del giorno sul Bitcoin: nessuna prova in registro, ma è un indicatore sul prezzo e il perché economico è debole. Lezione delle ultime 5 prove
  (150-154) tenuta presente: nessun altro segnale giornaliero fra monete dalle sole candele o dal libro.
