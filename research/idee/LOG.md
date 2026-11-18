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

- 13 novembre 2026 (sesto giro, 12:17): proposta 1 idea. G1 con il freno dell'indice di paura delle opzioni (DVOL di Deribit, serie giornaliera
  verificata dal 23 marzo 2021): sopra l'80% del rango a 180 giorni l'esposizione scende a metà (A) o a zero (B); mai usato come freno di G1
  (prova 47 era direzione del Bitcoin, prova 42 volatilità passata su F5, no). Regole in `programma7/NOVANTATREESIMA.md` (prova 155, 2 varianti;
  Moreira e Muir JF 2017; Brunnermeier e Pedersen RFS 2009). Probabilità medio-bassa, detto nel file. Scartate dopo il controllo: diluizione
  (idea 131 già in registro), offerta delle stablecoin (prove 44 e 100), inclinazione delle opzioni (121-122), premio DVOL (47); attività degli
  sviluppatori su GitHub (mai in registro, ma limite di richieste senza chiave, abbinare repository a 100 monete è lavoro manuale, studio non
  solido: non scritta); flussi verso le borse (storico gratuito lungo non trovato).

- 13 novembre 2026 (settimo giro, 16:17): **nessuna idea con un perché forte, nessuna regola scritta** (esito valido). Angolo: gli annunci di Binance
  (`scarico_annunci.json`: 2.294 quotazioni, 4.500 notizie, 446 rimozioni; caricatore `research/programma6/annunci.py`). Controllo nel registro
  (`--cerca`) delle quattro categorie: (1) etichetta di sorveglianza: già provata (prove 21 E1, 88 eventi, e 43 Q2; 2026 senza vantaggio dopo i 5
  minuti); (2) cambio dell'intervallo del funding / funding al tetto: già provato (prova 26 E4, 62 eventi, passa l'esame scritto ed è nel paper;
  prova 27 conferma su Gate non confermata; prova 70 entrata all'ora, no); (3) tetto del funding e leva massima: la leva è la prova 103 (tagli,
  2026 −3,31%), il tetto del funding è dentro E4; (4) perpetui nuovi con leva alta: le monete appena quotate sono le prove 18 e 30 (N1-N3), la
  quotazione a pronti la 43; un'entrata prima del lancio del perpetuo è impossibile (non si scambia fino al debutto) e dopo il debutto è N1-N3.
  Nessuna categoria libera. Non scritta: l'annuncio del perpetuo nuovo come evento a sé (parente di N1-N3, e ora Binance ne quota 2-3 al mese:
  pochi casi nuovi, t da 3 fuori portata). Nessuna riga di registro da preparare.

- 14 novembre 2026 (ottavo giro, 08:17): **nessuna idea con un perché forte, nessuna regola scritta** (esito valido). Controllato: (1) idee del proprietario mai
  provate: `docs/decisioni_del_proprietario.md` e `docs/backlog.md` non ne contengono di aperte (le strategie 27-28 sulle opzioni sono la prova VO, voce 110);
  (2) calendario macro: il dato dell'inflazione è già la voce 98 (G23); la riunione della Banca centrale americana (deriva prima della decisione, Lucca e
  Moench, JF 2015) non è in registro (`--cerca FOMC` = 0), ma sono circa 8 eventi l'anno, un solo asset (Bitcoin): circa 40 casi dal 2022, t da 3 fuori
  portata, e lo studio vale per le azioni; resta idea, non scritta; (3) scadenza mensile delle opzioni (blocco dei prezzi): un asset, indicatore, perché debole;
  (4) studi di agosto-novembre 2026 su perpetui: nessuno nuovo trovato oltre al quarto d'ora (Kim e Hansen, già nel giro del 13 novembre). Nessuna riga di registro.

- 14 novembre 2026 (nono giro, 12:17): **nessuna idea con un perché forte, nessuna regola scritta** (esito valido). Angolo: i fatti visti in avanti nei dati
  raccolti da noi. Controllato: (1) notizie (`research/notizie/archivio`, 15 giorni dal 30 ottobre) e monete di tendenza (15 giorni): già coperte dalle prove
  138 e 145 e dall'idea 126 (verdetto in avanti non prima del 30 aprile 2027); un tipo di notizia seguito da un movimento è un indicatore su testo con pochi
  giorni e pochi casi, t da 3 fuori portata; (2) conti di Hyperliquid (`HYPERLIQUID_CONTO.md`, 12 giorni, 3 gruppi): copiare e il contrario sono le idee 132 e
  135 (in avanti); «le balene prima di una fiammata» sarebbe la stessa misura letta per moneta, con soli 12 giorni di posizioni (4 ore) e una decina di
  fiammate: nessuna regola seria si può scrivere né provare ora (`--cerca balene` e `--cerca liquidazion` = 0, ma il dato è troppo corto); si riguarda
  quando le posizioni raccolte superano i 3 mesi (circa febbraio 2027); (3) HLI, DXI e candidate a tavolino: già in registro (135, 137, 140), nessun
  fatto ripetuto nuovo oltre ai numeri in avanti già seguiti. Nessuna riga di registro.

- 15 novembre 2026 (richiesta del proprietario «pensa fuori dagli schemi», rendimento regolare con soli prodotti di Binance): **una regola scritta**,
  `programma7/NOVANTASETTESIMA.md` (prova 159, base dei future trimestrali di Bitcoin ed Ether come rendimento fisso, Schmeling, Schrimpf e Todorov, BIS 2023;
  dati gratuiti su data.binance.vision: coin-margined dal 2020, USDT dal 2022; netto atteso 3-8% l'anno su capitale con riserva, probabilmente meno nel 2025-2026;
  diversa dall'idea 139 che era un segnale). Non scritte: (1) Launchpool e HODLer Airdrop con il BNB coperto: negli annunci scaricati ci sono solo i titoli
  (nessuna quantità, né il totale di BNB bloccato nel pool, da cui dipende la quota per BNB), quindi il rendimento in gettoni non si ricostruisce dal passato;
  il prova BL (115) ha già misurato il BNB negli annunci; la parte del funding del BNB è la prova 157 su un'altra moneta; si segue in avanti raccogliendo i
  gettoni ricevuti, non si prova; (2) altre strade guardate: prestito del USDT (Earn/margine): tasso non scaricabile storico gratis, sotto la base; spread tra
  future trimestrale e perpetuo: stesso dato della 159 e in quella si legge come controllo. Riga del registro nel file.

- 15 novembre 2026 (decimo giro, 08:17): proposta 1 idea, una regola scritta: `programma7/NOVANTOTTESIMA.md` (prova 160): miscela G1 + funding coperto di Bitcoin
  ed Ether (80/20 e 60/40, riequilibrio mensile, serie già calcolate; esame scritto più «utile» sulla discesa e sui mesi negativi). Angolo 1 (mettere
  insieme): nel registro nessuna miscela con G1 e il coperto (`--cerca miscela` = 0; le miscele sono tutte fra strategie di direzione, prove 15-33); G1 + G1N
  scartata (G1N è una variante di G1, correlazione alta). Angolo 2 (dati Binance mai usati): `--cerca topLong`, `top trader`, `prestito`, `basis` = 0 nel
  registro, ma non scritta nessuna: statistiche dei top trader e opzioni europee di Binance hanno solo uno storico breve (circa 30 giorni sull'API, non
  verificato qui: da controllare prima di scrivere), prestito del margine non scaricabile storico; il premio pronti-perpetuo è la prova 128 (BP) e la base 159.
  Probabilità media-bassa per la miscela; il rischio vero del coperto resta non misurato.

- 16 novembre 2026 (giro delle 08:17): **nessuna idea con un perché forte, nessuna regola scritta** (esito valido). Angolo 1 (lato comprato di G1): le fasce di
  grandezza e i due lati sono già misurati (`MIGLIORARE_G1.md`, voci 151-181: il comprato lavora in tutte le fasce, il funding 2026 viene soprattutto da lì); la
  voce 12 ha diviso solo il lato venduto per età e fiammate. Un taglio simile sul comprato (per età o grandezza) sarebbe una variante di G1 scelta guardando i
  dati, stessa famiglia di prove, e non ho trovato uno studio serio che dica cosa fanno le monete con il funding più negativo nei giorni dopo (la prova 141 è il
  funding che gira da positivo a negativo). Angolo 2 (archivio pubblico di Binance): `--cerca` su interesse aperto, acquisti a mercato, top trader, rapporto long/short,
  liquidazioni: interesse aperto e acquisti a mercato sono già in K1/K2 (G6, P2), le liquidazioni sono LQ (112) e le prove 157-161; nessuna serie dell'archivio
  davvero mai usata. Nessuna riga di registro.

- 17 novembre 2026 (giro delle 12:17): **nessuna idea con un perché forte, nessuna regola scritta** (esito valido). Controllato con `--cerca`: (1) ora del giorno e
  regolamento del funding (Eross e altri 2019, Wen e altri 2022; Vojtko e Padysak 2022 su Bitcoin): `--cerca UTC` trova solo G25 (rendimento delle prime 23 ore); un
  vantaggio per ora vale circa 0,01-0,03% e i costi di un giro (0,04% a limite, 0,10% a mercato) lo mangiano: è un indicatore sul prezzo, la lezione dice no;
  (2) funding di un'altra borsa (Bybit, OKX): Bybit e Kraken non sono in registro, ma l'idea è la stessa delle prove 135 e 137 (Hyperliquid contro Binance), stessa
  famiglia di prove; (3) sblocchi dei token e diluizione: già prove 74 e 131; il calendario di DefiLlama ora risponde 402 (a pagamento), niente dati nuovi;
  (4) stagionalità di giorno della settimana, fine mese: nessuna fonte seria con ragione economica, un asset, pochi casi. Nessuna riga di registro.

- 18 novembre 2026 (giro delle 08:17): proposta 1 idea, una regola scritta: `programma7/CENTESIMA.md` (prova 162, idea 147): il funding fra il perpetuo in USDT e
  quello in USDC della stessa moneta (vendere il contratto che paga di più, comprare l'altro; senza rischio sul prezzo; mai provato: `--cerca USDC` = 0; dati
  gratuiti di data.binance.vision dal gennaio 2024, verificata solo l'esistenza dei file; meno di 3 anni di storia; meccanismo: He, Manela, Ross e von Wachter, arXiv
  2212.06888). Probabilità medio-bassa (lordo piccolo, spese di quattro gambe), detto nel file. Scartata: la chiusura dei perpetui di Binance dopo l'annuncio (134
  annunci «Will Delist» su perpetui dal 2021): già G13 e G13C (prove 71 e 107). Altri angoli controllati con `--cerca`: fine settimana (solo azioni e CME), ETF (G24),
  halving (0, ma 3 eventi: t da 3 fuori portata). Nessun'altra idea forte.
