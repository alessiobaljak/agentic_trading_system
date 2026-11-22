# Prova 165 — Arrivare prima dell'annuncio: vendere le monete che somigliano a quelle chiuse (idea 156)

Regole scritte il 22 novembre 2026 da strategy-scout, **prima di ogni calcolo** (nessun rendimento guardato, nemmeno medie), per la
decisione del proprietario del 22 novembre (le idee nuove si provano senza aspettare il suo via libera). La esegue strategy-researcher
(prima in modalità verifica), il giudizio lo dà backtest-auditor. Non spegne e non sostituisce niente. Le regole le committa la sessione
principale.

## Il perché
* Idea 156 del registro. Le prove 105 e 107 vendono **dopo** l'annuncio (107: +7,89% a evento con l'uscita a +30%, p 0,028; con tutti i
  contratti +4,85%, p 0,116; no). La 71 aveva 7 eventi. Dal 21 ottobre 2026 Binance blocca i nuovi ordini dal momento dell'annuncio:
  vendere dopo l'annuncio non si può più, **arrivare prima si può**.
* Binance chiude i contratti con poco scambio e poco interesse aperto, per settimane di calo: la 107 trova un calo medio già prima
  dell'annuncio (controllo «prima dell'annuncio» −0,45% a evento, quindi poco) ma su 77 eventi; qui si chiede se il calo si può
  anticipare con un punteggio fatto **solo con il passato**. Fonte economica: i criteri di Binance per togliere un contratto (poco
  volume, poco interesse aperto, liquidità in calo) e la fuga dei market maker; studio serio sulla chiusura dei contratti non ce n'è,
  quindi la prova vale come dato nuovo (annunci datati + interesse aperto mai messi insieme: `--cerca` sul registro dà solo 105, 107, 71).
* **Non è la 107 di nuovo**: nessuna entrata dopo l'annuncio, nessun evento come segnale; l'evento serve solo per «insegnare» il
  punteggio. Non è G1 né K1/K2 (volume e interesse aperto come fattori su tutte le monete): qui la risposta è «somiglia a una moneta
  chiusa?», non «ha poco volume?».
* **Rischi scritti prima**: pochi eventi (85 contratti, 3 nel 2022, 21 nel 2024, 29 nel 2025, 32 nel 2026; la 107 ne ha usati 77),
  quindi il punteggio si può imparare bene solo dal 2024; le monete poco scambiate si vendono male (scarto più alto, ordine rifiutato);
  il rischio opposto, gli short affollati schiacciati (ALPACA nel 2025), per questo l'uscita a +30%; le monete che Binance non chiude mai
  e salgono; un solo regime (2024-2026), pochi anni per l'esame.

## Dati
* **Annunci**: `research/programma7/revisione_107/eventi_finale.csv` (87 righe: data, id annuncio, simbolo, ore) e il testo degli annunci
  «Binance Futures Will Delist …» (`research/programma6/scarico_annunci.py`, letti da `quarantacinquesima.py`; correzioni di
  `REVISIONE_107.md`: 18 chiusure sbagliate corrette, OMG rinviata, 10 contratti mancanti aggiunti). La **data di annuncio** (ora UTC) e la
  **chiusura** vengono da lì. Un contratto annunciato due volte vale il primo annuncio.
* **Numeri giornalieri dei contratti**: candele giornaliere (`scarico_giorni.py`: volume in USDT, prezzi) e, per l'interesse aperto,
  `research/data/p6m/<SIMBOLO>.pkl` (`scarico_metrics.py`: valore dell'interesse aperto a fine giorno, dall'archivio `metrics` di Binance).
  Candele orarie `scarico_ore.py` solo se serve per l'uscita. Funding vero come nelle altre prove.
* Tutto gratuito. **Da verificare prima di calcolare** (punto dubbio 1): che i contratti già chiusi (i 85 delle prove 107) abbiano
  candele e `metrics` nell'archivio fino alla chiusura; se per più di 10 mancano, la prova non parte e si scrive.
* **Periodo**: le decisioni partono dal primo lunedì (B) o primo giorno del mese (A) in cui le chiusure annunciate prima di quel giorno
  sono **almeno 15** (la data si scrive nel rapporto prima dei risultati: usa solo date di annuncio, nessun rendimento); finiscono
  all'ultima apertura con tutti i dati (al più 31 ottobre 2026). Gli anni dell'esame: quelli con decisioni.

## Come si fissa il punteggio ogni giorno (solo dal passato)
Alla decisione del giorno D (apertura 00:00 UTC), per ogni contratto USDT del pannello vivo in quel giorno (Bitcoin ed Ether esclusi;
**contratti già annunciati in chiusura prima di D esclusi**; almeno 90 giorni di storia):
1. **Quattro numeri** misurati sui 30 giorni interi prima di D (mai D): (a) volume medio in USDT, (b) valore medio dell'interesse aperto,
   (c) variazione del volume: media degli ultimi 30 giorni divisa per la media dei 60 giorni prima, (d) variazione dell'interesse aperto
   allo stesso modo. Ogni numero diventa **posizione in classifica fra tutti i contratti vivi quel giorno** (0 = più basso, 1 = più alto;
   (a) e (b) in logaritmo prima della classifica), così i livelli di mercato diversi nel tempo non contano.
2. **Il modello delle chiusure**: per ogni contratto chiuso con annuncio prima di D e ogni giorno t in cui era vivo con almeno 90 giorni
   di storia, i quattro numeri di t. **Solo le righe con t + 45 giorni ≤ D − 1** (così il risultato «annunciato entro 45 giorni dopo t» è
   già noto a D; nessun contratto annunciato dopo D − 1 entra, e una riga di un contratto non ancora annunciato vale «no» solo se
   t + 45 ≤ D − 1). Etichetta = 1 se il contratto è annunciato entro 45 giorni da t. Il modello è una **regressione logistica con
   penalità fissa (L2, forza 1,0)**, quattro numeri più un'intercetta, rifatta a ogni decisione.
   Il **punteggio** di un contratto a D = la probabilità data dal modello ai suoi quattro numeri.
3. Niente altro: nessun numero in più, nessuna penalità o finestra scelta dopo i risultati. Se alla decisione il modello ha meno di 10
   contratti chiusi con righe valide, nessuna posizione quel giorno.
4. **Controllo di coerenza scritto nel rapporto prima dei risultati**: il verso dei quattro coefficienti (ci si aspetta volume e interesse
   aperto bassi e in calo → più probabilità; se un segno è opposto, si scrive, non si cambia) e quante chiusure vere cadono nel primo
   5% dei punteggi nei 45 giorni dopo (precisione descrittiva, non decide).

## La regola (fissata qui)
1. Alla decisione si prendono le **N monete con il punteggio più alto** (nessuna soglia: sempre N, salvo quando sotto N monete sono
   ammissibili o vale il punto 3 sopra).
2. **Short** di ogni moneta e **long Bitcoin** per lo stesso valore totale (neutra contro il mercato, come la 107): valore di ogni short =
   capitale / N; il long Bitcoin = il valore totale degli short aperti.
3. Esecuzione all'**apertura del giorno D** dopo il segnale calcolato con i dati fino a D − 1 (00:00 UTC). Tenuta per il periodo della
   variante; alla decisione dopo si rifà la classifica: le monete che restano fra le prime N **restano** (si paga solo il cambio).
4. **Uscita anticipata**: se in un giorno il massimo supera del 30% il prezzo di entrata, uscita a quel prezzo +1% di scarto (come la
   protezione delle prove 107 e 71); se la moneta viene annunciata in chiusura durante la tenuta, **si tiene** (è il guadagno cercato)
   e si esce all'apertura dell'ultimo giorno prima della chiusura o alla fine del periodo, il primo dei due; se la moneta smette di
   avere prezzi, chiusura all'ultimo prezzo con le spese e il caso si scrive.
5. Rendimento giornaliero = (long Bitcoin − short monete, ciascuno sul suo valore) + funding vero (chi è venduto riceve quando il
   funding è positivo) − spese.
6. **Spese** (confermate dal proprietario, 7 novembre): 0,05% a mercato sul valore scambiato + scarto 0,01% su BTC, ETH e SOL e 0,02%
   sulle altre; si pagano all'entrata, all'uscita, al cambio di moneta e al riequilibrio del Bitcoin. Sempre a mercato (conservativo);
   il caso con ordine limite (0,02%) solo come controllo.

## Varianti (fissate, solo 2)
* **A (lenta)**: N = 5 monete, decisione il primo giorno del mese, tenuta fino alla decisione dopo (circa 30 giorni).
* **B (veloce)**: N = 10 monete, decisione ogni lunedì, tenuta 7 giorni.
Il 45 giorni dell'etichetta, i quattro numeri, la penalità e il 30% di protezione sono uguali nelle due. Nessun N, finestra, penalità
o etichetta diversi dopo i risultati. Conta **2 prove** (una famiglia con la 107 per la correlazione si decide dal conto per famiglie).

## L'esame (regole approvate dal proprietario il 9 e l'11 novembre; `METODO.md`)
Passa se: netto dopo i costi positivo; **ogni anno positivo** (gli anni con decisioni: con tutta probabilità 2024 parziale, 2025, 2026
fino a ottobre; l'anno parziale conta se ha almeno 8 settimane di decisioni); **t almeno 3**; **Sharpe corretto almeno 0,80** con il
conto per famiglie (`research/programma6/asticella.py`, `corretto_famiglie`, le due varianti in `nuove`); serie settimanali nette come
nelle prove 157-163. Per scritto: con 2-3 anni e poche chiusure il t da 3 è difficile; l'esame non si abbassa. **Anche** (condizione
in più, perché le chiusure sono pochi eventi): meglio di una selezione a caso con la stessa regola (1.000 estrazioni a caso delle N
monete fra le ammissibili, stesso periodo e spese, seme 2026): la media di A e di B sopra il 95° percentile.

## Il controllo: da dove viene il guadagno
Ogni giorno di ogni posizione si etichetta: **A** = giorno prima dell'annuncio di chiusura di quella moneta (il calo che si voleva
anticipare), **B** = dal giorno dell'annuncio fino all'uscita (l'effetto della 107), **C** = moneta mai annunciata nella tenuta. Il
rapporto dà la quota di netto (e di funding) di A, B, C per variante, per anno, e **senza le 5 monete migliori**. Se la parte B è la
maggior parte, la prova non sta battendo la 107 ma ripete l'annuncio (non fattibile dal 21 ottobre) e si scrive: «non promosso per
natura del guadagno». Descrittivi (non varianti): precisione del punteggio (quante delle prime N vengono chiuse entro 45 e 90 giorni
contro la frequenza di base), durata media, quante volte scatta la protezione, quante volte il segno di un coefficiente cambia fra una
decisione e l'altra, la correlazione con G1 e con la prova 107.

## Cosa si consegna
`research/programma7/RISULTATI_CENTOTREESIMA.md`, serie in `research/programma7/risultati_centotreesima/` (giornaliere e settimanali
nette, leggibili da `asticella.py`), script `research/programma7/centotreesima.py`, varianti in `research/trials/centotreesima.csv`;
a schermo al massimo 20 righe. Nessuna chiamata a servizi a pagamento. Prima del calcolo, strategy-researcher in modalità verifica
(le ambiguità si chiudono e si ricommittano) e fra i punti: l'esistenza dei dati dei contratti già chiusi, la data di partenza delle
decisioni, il tempo di rifare il modello a ogni decisione (sono poche righe: nessun problema atteso).

## Chiusura della verifica (22 novembre 2026, sessione principale, prima di ogni calcolo)
Dalla verifica di strategy-researcher (`VERIFICA_CENTOTREESIMA.md`, 19 punti, 2 bloccanti). **Dove il testo sopra dice diversamente, vale
questa sezione.** Dove c'era una scelta, si è presa la più prudente.
1. **Niente interesse aperto** (punto 1 bloccante): lo scarico giornaliero dei `metrics` di tutti i perpetui dal dicembre 2021 sarebbe di
   circa un milione di file e non si fa. I numeri del modello diventano **due**, misurati sulle candele giornaliere: (a) il volume medio
   in USDT dei 30 giorni interi prima del giorno, (c) il rapporto fra il volume medio dei 30 giorni e quello dei 60 giorni prima (giorni
   D−90…D−31), ciascuno in classifica fra i contratti vivi quel giorno. Il controllo di coerenza vale per i due versi (ci si aspetta
   volume basso e in calo per i contratti chiusi). È autorizzato un solo script nuovo per i dati, `programma7/centotreesima_dati.py`
   (sul modello di `novantanovesima_dati.py`): candele giornaliere mensili di `data.binance.vision` per tutti i perpetui in USDT
   dell'archivio, compresi i chiusi, dal dicembre 2021 al 31 ottobre 2026, con impronte e buchi nella cartella dei risultati.
2. **Chiuso e vivo** (punto 2 bloccante): un contratto è «annunciato» dall'ora dell'annuncio `h_e` e chiuso dall'ora di chiusura `h_u`
   di `revisione_107/eventi_finale.csv` (87 contratti, la fonte vale più dei numeri 85 e 3/21/29/32 scritti sopra); dopo `h_e` non dà più
   righe al modello e non si sceglie, dopo `h_u` non ha dati anche se l'archivio continua. Prima del calcolo si scrive l'elenco dei
   contratti con volume positivo oltre 7 giorni dopo `h_u` (ICP, TLM, SC, CVC, BLZ e gli altri) e i risultati si danno anche senza di loro.
3. Punti 3-5 e 8-15, 17-19: valgono le correzioni scritte nel rapporto di verifica, punto per punto, così come sono (il momento di ogni
   passo; le etichette su tutte le coppie contratto-giorno con t+45 ≤ D−1; la classifica del giorno; `LogisticRegression(penalty='l2',
   C=1.0, solver='lbfgs')`; i contratti chiusi validi; meno di N monete; protezione al massimo giornaliero, uscita a 1,30 × 1,01; uscita
   per annuncio con i rinvii; prezzo e funding; il controllo A/B/C; spese e chiusura al 1° novembre 2026; settimane da lunedì).
4. **Capitale fisso** di 1.000 USDT, senza comporre, come nelle prove 157-163 (punto 11).
5. **Prime decisioni** (punto 7): A il 1° giugno 2024, B lunedì 13 maggio 2024; i mesi prima a zero.
6. **La selezione a caso** (punto 16): **ciascuna variante** sopra il **suo** 95° percentile di 1.000 scelte a caso con la stessa regola
   di tenuta e di uscita.

## Punti ancora dubbi (da chiudere nella verifica, non dopo i risultati)
1. I contratti chiusi hanno candele e `metrics` fino alla chiusura? (sopravvivenza: senza, il modello non ha esempi.)
2. L'universo vivo ogni giorno va ricostruito dal pannello giornaliero e dalle date di quotazione, includendo i contratti poi chiusi.
3. Gli annunci del 2022 (3) e prima: i contratti chiusi molto prima dei dati `metrics` (archivio dal 2021) non entrano nel modello.
4. Il modello vede solo ciò che era annunciato a D − 1: gli annunci con più contratti (stessa data) valgono tutti dalla stessa data.
5. Esecuzione: le monete poco scambiate possono avere uno scarto più alto dello 0,02% (la 107 lo ammetteva solo dopo l'annuncio); si
   guarda come controllo con scarto doppio (0,04%).
