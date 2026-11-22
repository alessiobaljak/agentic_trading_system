# Verifica della prova 166 (regole in `CENTOQUATTRESIMA.md`), 22 novembre 2026

Modalità verifica: nessun calcolo di risultati e nessun rendimento guardato. Solo piccole richieste di prova alle fonti (formato, numero di righe,
prime date; nessun prezzo letto), file temporanei fuori dal repo e poi cancellati. Regole committate: `b905724` (22 novembre 2026, 08:13 UTC).

## Esito: NON eseguibile così com'è. Sei punti bloccano, gli altri vanno chiusi prima del calcolo.

## Cosa risponde davvero ciascuna fonte (provato il 22 novembre)
* **Yahoo, prezzi delle azioni**: con `range=max&interval=1d` per le società quotate da molti anni (BTCS, FWDI, SUIG, BNC, FRMM, BTBT) la risposta è
  **mensile** (scarto massimo fra due date 31 giorni), non giornaliera. Con `period1=1748736000&period2=1793491200&interval=1d` (2 giugno 2025 - 31 ottobre
  2026) invece torna giornaliera, 357 righe, scarto massimo 4 giorni (provato su FWDI, BTCS, SUIG, BNC). Le regole indicano `range=max`: va cambiato.
  BMNR con `range=max` oggi risponde (369 giorni dal 5 giugno 2025). **ETHM: nessuna serie** (risposta di 782 byte senza dati), **FGNX: 1 solo giorno**
  (ora è «FG Communities Holdings», lo storico non sta sotto il simbolo), **ETHZ** (vecchio simbolo di ETHZilla, oggi FRMM): senza dati; FRMM ha 114 giorni.
  SBET con `range=max` parte dal 1997 (simbolo riusato da un'altra società): serve cercare per date.
* **Commissione per i titoli degli Stati Uniti (EDGAR)**: `company_tickers.json` ha risposto 403 («Request Rate Threshold Exceeded») con un nome
  di programma generico e 200 con un nome più un indirizzo di contatto. L'ente chiede un contatto nell'intestazione: «solo un nome di programma»
  (regole) non basta. `submissions/CIK…json` 200: per BitMine 140 comunicati «8-K», con data e ora di accettazione (`acceptanceDateTime`).
  Codici: BMNR 1829311, SBET 1981535, BTBT 1710350, BTCS 1436229, FWDI 38264, PURR 2078856, SUIG 1425355, BNC 1482541, FRMM 1690080, DFDV 1805526,
  UPXI 1775194, HSDT 1610853, TRON 1956744, SLNH 64463. Senza codice nel file: ETHM, FGNX, ETHZ, ENA/USDE, TONX non cercati.
* **Azioni in circolazione** (`dei/EntityCommonStockSharesOutstanding`): per BitMine solo **26 valori in tutta la storia**, dalla copertina di 10-Q e 10-K. Dal
  2025: 14 aprile, 2 e 3 luglio, 21 novembre 2025, 13 gennaio, 14 aprile, 14 luglio, 10 novembre 2026. Buchi fra un deposito e il successivo di 90-130 giorni,
  mentre le azioni passano da 384 a 454, 537, 603, 626 milioni. **Con il limite di 45 giorni la cifra è vecchia in oltre metà dei giorni.**
* **Monete in cassa nei comunicati**: il documento allegato si chiama in modo diverso a ogni comunicato (`ex99-1.htm` per BitMine); si trova solo con
  `…/<numero>/index.json`. Per BitMine il comunicato del 16 novembre 2026 contiene la frase «hold… 6,077,745 ETH at $1,823 per ETH» (riconoscibile con
  un'espressione regolare, e uguale alla cifra di CoinGecko). Il titolo però scrive «6.08 Million» (arrotondato): serve dire quale cifra vale. Letto **solo
  BitMine**: per le altre 16 società il formato non è stato visto. Il comunicato conta anche altre cose (216 Bitcoin, 448 milioni in contanti e titoli,
  una quota in ORBS): la regola le esclude (scritto come limite).
* **CoinGecko** `companies/public_treasury/<moneta>`: 200 per ethereum (35 società), solana, binancecoin, hyperliquid, sui, ethena, tron, the-open-network
  (con pause di 10 secondi nessun 429). `world-liberty-financial-usd`: 404 «Coin not supported» (WLFI non c'è). `entities/list` 200 ma 100 voci per pagina
  (elenco paginato, 10 KB). **Storico (`holding_chart`, `transaction_history`): 404 con tutti i nomi provati** (entità non trovata; il nome giusto sta nell'elenco
  paginato, non cercato oltre). Resta non verificato: lo storico viene solo dai comunicati.
* La lista di CoinGecko è **solo oggi (22 novembre)**: la regola dice «al 31 ottobre secondo la lista», ma la lista del 31 ottobre non esiste.

## Punti bloccanti (da decidere prima del calcolo)
1. **L'universo include società che non sono tesorerie.** La regola dice «quelle ... con un gettone diverso dal Bitcoin in cassa che valgono almeno 50
   milioni». La lista dell'Ether ha COIN (Coinbase, 152.649 ETH) e GLXY (Galaxy); lista di Solana e Hyperliquid ha ancora GLXY; c'è BLSH, CRCL, GEMI.
   Il loro «premio» è circa −99% (cassa minuscola rispetto al valore della società) e trascina la mediana verso il basso. Nessuna regola dice di
   toglierle. *Correzione proposta:* elenco **scritto a mano nel rapporto prima dei calcoli** (solo società la cui attività principale è tenere il gettone), approvato
   dalla sessione principale; fuori COIN, GLXY, BLSH, CRCL, GEMI, EXOD, CAN, SOS e simili.
2. **Soglie «50 milioni» e «60 giorni» a quale data.** Fissate «al 31 ottobre» con una lista di oggi: ma ETH vale 1.823 dollari e molte società sono
   vicine alla soglia (FGNX 66,8 milioni, SUIG 70, NA 69, GLXY su Solana 53, YDKG 52). Inoltre la frase della mediana («con la cassa del punto sopra almeno 50
   milioni di dollari») si può leggere come condizione **giorno per giorno** (la composizione della mediana cambia ogni giorno) oppure fissa. *Correzione:*
   scrivere «universo fissato una volta con la lista del 22 novembre e il valore in dollari di quella lista; la soglia non si ricontrolla giorno per giorno»
   (oppure il contrario, ma scriverlo). Si dice anche che il periodo ammesso per una società comincia dal suo primo deposito con la cassa.
3. **Cassa vecchia senza limite.** Il limite dei 45 giorni vale solo per le azioni. Per le società con comunicati trimestrali l'ultima cifra delle monete
   può avere 90 giorni e più; «comunicati regolari» non è definito. *Correzione:* «una società è nell'universo a D solo se l'ultima cifra delle
   monete ha al massimo N giorni (proposta: 45, come le azioni); altrimenti quel giorno non entra nella mediana». L'elenco finale dice per ogni società
   da quando e fino a quando.
4. **Azioni in circolazione: la cifra è quasi sempre vecchia e sbaglia sempre nello stesso verso.** Una società che emette azioni ha più azioni di quelle
   dell'ultimo deposito: il valore di mercato risulta troppo basso, il premio troppo negativo e il segnale scatta troppo spesso. La regola dice solo «si scrive
   quante volte accade». *Correzione da decidere:* (a) leggere le azioni anche dai comunicati settimanali (dove ci sono; non verificato), (b) escludere la società
   nei giorni con la cifra oltre i 45 giorni, oppure (c) tenere la regola com'è e scrivere che il segnale è sistematicamente spostato verso il basso. Inoltre
   le chiusure di Yahoo sono corrette per i frazionamenti inversi mentre le azioni depositate no: va scritto quale chiusura (`close` o `adjclose` e cosa fare con un
   frazionamento, per esempio escludere i giorni fra frazionamento e nuovo deposito).
5. **«Eventi indipendenti» non è definito**, ma decide il verdetto (sotto 20: «non conclusivo»; misura in avanti: si ferma a 20). La regola 3 dice «un evento
   per gettone per episodio» e il testo dice che gli eventi «sono raggruppati nelle stesse settimane». *Correzione:* una definizione eseguibile, per esempio
   «due eventi sono indipendenti se le loro finestre di 14 giorni non si sovrappongono in calendario, qualunque gettone»; in caso diverso scrivere la regola.
   Serve anche la formula del «t sul rendimento medio per evento» (media diviso errore standard sugli eventi? con quali eventi sovrapposti?).
6. **La misura in avanti non è eseguibile**: non dice dove gira lo script (macchina, giro, intervallo), dove scrive l'uscita (percorso), come legge i comunicati ogni giorno
   (lettura automatica di 15-17 società, formato visto solo per BitMine; CoinGecko dà 4-5 chiamate poi 429), se l'elenco delle società è quello del 31 ottobre o
   si aggiorna (società nuove dopo il 23 novembre), e cosa succede fra il 1° e il 22 novembre (periodo nè nella prova sul passato nè in avanti). Lo script
   «stile `bot/portafoglio/`» sta in un'area dove ogni modifica ha regole proprie; la consegna dice «script e uscita della misura in avanti» senza percorso.
   *Correzione:* percorso (per esempio `research/programma7/centoquattresima_avanti.py`, uscita in `research/programma7/risultati_centoquattresima/avanti/`),
   chi lo lancia e dove, elenco fisso, e che i giorni 1-22 novembre sono scartati o recuperati.

## Ambiguità minori (si chiudono con una riga)
7. Intestazione per l'archivio della Commissione: serve un contatto (es. indirizzo generico). Al massimo 10 richieste al secondo.
8. Yahoo: usare le date (`period1`/`period2`) e non `range=max` (vedi sopra); l'interfaccia di Yahoo non è ufficiale: se risponde 429 si ripete dopo una pausa.
9. Giorno dell'azione: «chiusura del giorno D−1» per sabato, domenica e festivi (lunedì D usa il venerdì?); la chiusura dell'azione è alle 21:00 UTC circa e il perpetuo alle
   00:00 UTC (tre ore di scarto). *Correzione:* «ultima chiusura disponibile prima di D; nessuna correzione dell'orario».
10. Mediana con numero pari di società: media delle due centrali (si scrive).
11. Regola 3: «segnale spento almeno 7 giorni» — consecutivi dopo la chiusura, oppure contando anche i giorni di segnale spento durante i 14? Scrivere.
12. Capitale e peso: 20% del conto per gamba è sul capitale iniziale (1.000 USDT fissi) o sul patrimonio corrente? Le gambe si riequilibrano ogni giorno o restano a
    quote fisse? Con 5 eventi insieme ogni lato vale il 100% del conto (valore lordo 200%): scritto la leva e il margine e se si controlla la liquidazione
    (le regole non la citano, mentre i costi del motore sì).
13. Posizioni aperte al 31 ottobre 2026: si chiudono all'apertura del 1° novembre pagando le spese? (come nel verbale della prova 163, domanda 3).
14. Perpetui su Binance: i gettoni con simbolo atteso ETH, SOL, BNB, HYPE, SUI, ENA, TRX, TON. Non verificato che tutti abbiano 30 giorni di storia nel caricatore
    ufficiale (non apro `research/data/`); la regola dell'universo lo chiede, e va scritto quale caricatore serve per l'archivio giornaliero con apertura e funding (le
    regole dicono «come nelle prove recenti» senza nome).
15. Settimane e anni: lunedì-domenica, somma dei rendimenti netti giornalieri, 2025 dal primo giorno con una posizione (come nelle altre regole recenti).
16. `corretto_famiglie(nuove, candidate, taglio=TAGLIO)` esiste in `research/programma6/asticella.py` (riga 387): ok.

## Società e gettoni possibili (da CoinGecko del 22 novembre + Yahoo del 22 novembre, nessun premio calcolato)
Società di tesoreria con almeno 50 milioni di dollari e Yahoo giornaliero di almeno 60 giorni (per data di inizio il conto è approssimato):
* Ether: BMNR, SBET, BTBT, BTCS, FRMM (114 giorni) = **5**; scartate per mancanza di prezzo: ETHM (nessuna serie) e FGNX (1 giorno).
* Solana: FWDI, DFDV, UPXI, HSDT = **4**.
* Hyperliquid: PURR (244 giorni dal 3 dicembre 2025), HYPD = **2**.
* BNB: BNC (153 giorni), NA (Nano Labs, 69 milioni) = **2**.
* Sui: SUIG (70 milioni) = **1**. Ethena: USDE (104 giorni dal 26 giugno 2026) = **1**. Tron: TRON = **1**. Ton: TONX = **1**.
* **Totale: 17 società su 8 gettoni.** Con le non tesorerie lette alla lettera (COIN, GLXY per Ether, Solana e Hyperliquid, YDKG per Solana) sarebbero 20 (punto 1).

## Quanti eventi sono realmente possibili (solo da società e mesi coperti)
Un evento dura 14 giorni e il successivo sullo stesso gettone parte dopo almeno 7 giorni di pausa: **al massimo un evento ogni 21 giorni per gettone**.
Mesi coperti per gettone (cassa e prezzo disponibili, fino al 31 ottobre 2026): Ether circa 16 (da giugno-luglio 2025), Tron circa 16, Solana, Sui, BNB, Ton e Hyperliquid
(HYPD) circa 13-14, Ethena circa 2 (dal 26 giugno 2026 più 60 giorni di prezzo, cioè dal 25 agosto). Limite alto per gettone: Ether 22, Tron 22, Solana, Sui, BNB, Ton
e Hyperliquid 20 ciascuno, Ethena 3: **al massimo circa 147 eventi** in teoria, ma solo se il segnale resta acceso quasi sempre. Il limite di 5 eventi insieme non
lo abbassa in modo importante. **Eventi indipendenti** (finestre che non si sovrappongono nel calendario, qualunque gettone, definizione proposta al punto 5):
la prova copre circa 69 settimane ≈ 483 giorni, a una finestra ogni 14 giorni **al massimo 34 e in pratica meno di 23** se si tiene conto della pausa di 7 giorni.
Per arrivare a 20 eventi indipendenti il segnale dovrebbe essere acceso quasi senza interruzione per tutto il periodo: è molto improbabile. **Il verdetto sarà
quasi certamente «non conclusivo»** (lo scrive già la regola). Il numero vero si conosce solo calcolando il premio, che qui non è stato fatto.
Per la misura in avanti: con questa cadenza 20 eventi indipendenti nuovi richiedono almeno 20 × 14 = 280 giorni (e probabilmente oltre un anno).

## Punti verificati e a posto
* Formula del premio, segno (short del gettone, long del Bitcoin, stesso valore), durata 14 giorni, due sole varianti A (0%) e B (20%), conto di 2 prove: chiari.
* Le spese: 0,05% a mercato + scarto 0,01% su BTC, ETH, SOL e 0,02% sulle altre, su ogni gamba, apertura e chiusura: chiaro.
* Data del deposito: usare `acceptanceDateTime` dell'archivio dei depositi prima di 00:00 UTC di D è eseguibile (BitMine: 140 comunicati con data e ora).
* Lo storico delle monete per BitMine si ricostruisce dai comunicati settimanali (formato letto una volta); per le altre società non verificato.
* Esame (soglie, ogni anno positivo, Sharpe con famiglie, minimo 20 eventi) scritto.

## Domande aperte (testuali)
1. Quale elenco **scritto a mano** di società di tesoreria vale (punto 1): le 17 sopra o un altro? Le non tesorerie (Coinbase, Galaxy, Bullish, Circle e simili) si escludono?
2. L'universo si fissa con la lista del 22 novembre senza ricontrollare giorno per giorno la soglia dei 50 milioni (punto 2)?
3. Per la cassa e per le azioni, limite di vecchiaia (45 giorni?) e cosa si fa oltre: società fuori quel giorno, oppure cifra vecchia con segnalazione (punti 3 e 4)? Le azioni si leggono anche dai comunicati settimanali?
4. Definizione di «evento indipendente» e formula del t per evento (punto 5).
5. Misura in avanti: dove gira lo script, dove scrive, chi lo lancia, elenco fisso, trattamento dei giorni 1-22 novembre (punto 6).
6. Quale capitale (1.000 USDT fissi o composti), riequilibrio giornaliero, leva e liquidazione (punto 12)? Posizioni aperte al 31 ottobre: si chiudono il 1° novembre?
7. Si accetta Yahoo con date esplicite al posto di `range=max`, e un contatto generico nell'intestazione per la Commissione (punti 7 e 8)?
