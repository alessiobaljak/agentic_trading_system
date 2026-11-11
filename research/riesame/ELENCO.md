# Il riesame delle prove bocciate di poco: l'elenco (idea 137)

Fatto l'11 novembre 2026 dal registro (`python3 -m research.src.registro --riepilogo`, `--cerca`, `--prova N`), senza rifare calcoli.
Idea 137 di `research/REGISTRO.md`, sezione 5, approvata dal proprietario l'8 novembre: backtest-auditor rilegge le prove bocciate per
un margine stretto e cerca un errore che abbia cambiato il verdetto (codice, costi, esame); solo dove lo trova, la prova si rifà.

Candidate: verdetto «quasi» o «no» con lo Sharpe corretto fra 0,60 e 0,80, o il t fra 2 e 3, o un solo criterio mancato. Escluse la
famiglia del funding fra monete (F3, F5, G1, G11, G1N e le loro varianti), le strategie già nel paper o nel demo e le prove con una
revisione separata (`programma7/REVISIONE_*.md`) che non ha lasciato dubbi sul calcolo. Soglie: Sharpe corretto 0,95 (da 0,90 in su,
ogni anno positivo e t sopra 3 non si boccia, decisione del 24 ottobre; l'8 novembre «qualche punto sotto» non è un muro); per le
prove a eventi p ≤ 0,01.

**Attenzione per le righe 1 e 2**: sono miscele che hanno dentro il funding di F5 e nell'esame stanno nello stesso gruppo di F5
(correlazione ≥ 0,5, `programma6/RISULTATI_CINQUANTACINQUESIMA.md`). Se l'esclusione della famiglia del funding vale anche per le
miscele, si tolgono e l'elenco comincia dalla riga 3.

## Le candidate, dalla più vicina al passaggio

| # | Prova | Cosa fa | Numeri chiave e verdetto | Criterio che l'ha fatta cadere | File dei risultati | Perché vale un riesame (dove guardare) |
|---|---|---|---|---|---|---|
| 1 | 28 | K2 (il segnale di K1: funding, acquisti a mercato, interesse aperto, con la banda) e F5 + M7 + K2 a rischio uguale, a settimana dal 2022 | K2 Sharpe 1,72 (1,745 dopo le parità), t 3,77, 5 anni su 5; F5 + M7 + K2 Sharpe 2,11 (2,101), t 4,62, 5 anni su 5. Verdetto «quasi»: corretti 0,47 e 0,76 con 52 prove contate una per una. Ricalcolati: 0,70 e 0,90 (gruppi, 22 ott), **0,79 e 0,94** (aggiunta del 23 ott) | Sharpe corretto sotto 0,95 col calcolo di allora; «costruzione» (i due versi di K1 visti prima, prova 12) | `research/programma6/RISULTATI_VENTOTTESIMA.md`; numeri rivisti in `research/programma6/RISULTATI_ASTICELLA.md` e `RISULTATI_ASTICELLA_23.md` | **Esame**: il verdetto è stato dato con un calcolo poi corretto due volte, e i numeri sono saliti di 0,32 e 0,18. F5 + M7 + K2 (0,94, t 4,62, ogni anno positivo) rientra nei numeri della regola del 24 ottobre, con cui F5 è stata ammessa a 0,90, ma non è mai stata rigiudicata con quella regola. Da controllare: la riserva «viste prima della regola non diventano validate» (`programma6/ASTICELLA.md`, sezione 5), il peso della «costruzione», e che le serie siano quelle dopo la correzione delle parità. L'asticella di allora contava le prove fino alla 55: oggi i gruppi sono almeno 81 e il numero scenderebbe |
| 2 | 55 | C3: un solo punteggio dalla media dei ranghi di F5 (funding), K2 e M7, con la banda di F5, a settimana dal 2022 | Sharpe 1,88, +55,9% l'anno, discesa −41,9%, ogni anno positivo, t 4,12; corretto 0,00 come scritto, **0,86** con l'aggiunta del 23 ottobre. Verdetto «no» | Il corretto a 0,00 (azzerato dalle serie dello scalping) e «non migliora F5» (1,88 contro 1,93) | `research/programma6/RISULTATI_CINQUANTACINQUESIMA.md` | **Esame e codice**, tutti e due i motivi hanno un errore noto. Lo 0,00 è l'errore dell'esame corretto il 23 ottobre, regola in vigore «dalla prova 56»: C3 la manca di una prova. L'1,93 di F5 usato nel confronto è quello prima della correzione delle parità del funding (in vigore dalla prova 57; F5 dopo la correzione 1,868, sezione 1 del registro e `programma6/CONTROLLO_PARITA.md`). Ma anche il rango del funding dentro C3 aveva lo stesso residuo: va controllato se, rifatte tutte e due con la correzione, C3 resta sotto F5 |
| 3 | 96 | G22: la deriva del Bitcoin dopo le riunioni della Fed, la direzione dell'ora del comunicato (14:00 di New York) seguita per 6 ore, 46 riunioni dal 2021 | +0,61% a operazione, **p 0,021**, vinte 65%; metà 2021-2023 +0,85% e 2024-2026 +0,34% (tutte e due positive); 2025 −0,59%, 2026 −0,21%; nessuna delle 2.000 estrazioni di giorni a caso arriva alla media. Verdetto «no» | Solo la p sopra 0,01 (bootstrap sulle 46 operazioni, `TRENTAQUATTRESIMA.md`, sezione 3) | `research/programma7/RISULTATI_TRENTAQUATTRESIMA.md` | **Esame**: un solo criterio, a 2 volte la soglia. Da controllare che il bootstrap sia quello scritto e che l'elenco delle 46 riunioni sia completo. Nessun sospetto concreto sul codice: l'ora di New York è già convertita con l'ora legale (`trentaquattresima.py`, `ZoneInfo`). Probabilità bassa che un errore la salvi; il verdetto stesso dice «da riguardare quando le riunioni saranno di più» |
| 4 | 113 | N3G: la regola delle monete nuove (prova 32, 613 eventi così come sono) divisa fra le monete distribuite gratis da Binance (HODLer Airdrops, Launchpool, Megadrop: 87) e le altre (526) | Gratis +12,11% a evento, altre +2,99%; differenza nello stesso trimestre +7,87 punti, **p 0,027** (15 trimestri); le gratis da sole p 0,0006, senza le 5 migliori +8,9%; 75 eventi gratis su 87 nel 2024-2025. Verdetto «no per le regole»; misura in avanti a tavolino in corso | Solo la p della differenza sopra 0,01 | `research/programma7/RISULTATI_CINQUANTUNESIMA.md` | **Dati ed esame**: gli eventi sono letti dal file della prova 32 (`programma6/risultati_trentaduesima/eventi_N3B.csv`), e `trentaduesima.py` usa `programma6/esecuzione.ore_di`, la lettura corretta il 25 ottobre dal revisore della prova 105 (14 monete perse). Da controllare se il file è stato rifatto dopo la correzione, se contiene simboli riusati (come PUMP nella prova 105) e se le etichette «gratis» sono giuste. Il mescolamento dentro 15 trimestri limita da solo quanto può scendere la p |
| 5 | 84 | G20: il modello ad alberi deciso ogni giorno (M3) con cinque semi e ordini limite sulle variazioni, banda 20/40, dal 2022 | Sharpe 1,35, +42,1% l'anno, discesa −46%, spese 16,5% l'anno; 2022-2025 positivi, **2026 −10,4%**; **t 2,94**, corretto 0,35 (76 gruppi). Verdetto «no» | Corretto 0,35 sotto 0,95, t sotto 3, il 2026 negativo (regola del 24 ottobre: no) | `research/programma7/RISULTATI_VENTIDUESIMA.md` | **Esame**: il t manca 3 di 0,06, ma i criteri mancati sono tre. Il t è basso anche perché la serie parte dal 2022 (il modello si allena sul 2021): non è un errore. Il testo del verdetto è confuso sul confronto con M7 («1,25 con molte meno spese? no: pari»): da chiarire. L'ipotesi del 98% delle variazioni eseguite a limite è ottimista, e un errore lì abbasserebbe il risultato invece di salvarlo. Probabilità bassa |

Nel brief a backtest-auditor vanno solo il numero della prova, i file delle regole e dei risultati e il punto da controllare (codice,
costi, esame), non la colonna «perché» né giudizi sul risultato (regole dei token in `CLAUDE.md`).

## Le scartate, con il motivo

**Famiglia del funding fra monete (esclusa per il brief)**
* 6, funding fra monete: «quasi», corretto 0,66; superata da F3 e F5.
* 8, F3: «quasi», corretto 0,76; superata da F5, che è nel paper.
* 15, F3 + M1: «quasi», corretto 0,76; e l'errore delle monete tolte dal listino, già trovato, abbassa M1 (1,35 → 0,79).
* 19, il premio del perpetuo (P1, P2): corretto 0,33; è il vantaggio di F3 misurato in un altro modo (correlazione 0,83-0,92).
* 42, F6 (F5 con l'esposizione secondo l'agitazione): corretto 0,31, poi 0,81 rivisto, t 4,13; variante di F5.
* 50, F5 sulle monete 101-150: Sharpe 0,30, p 0,24; lontana.
* 56, F9 (F5 a ordini limite): corretto 0,94, t 4,79; variante di F5, e il bot l'ha già presa (voce P17).
* 61, F5T e G1T (tetto per moneta): corretti 0,85 e 0,90; varianti di F5 e G1.
* 63, G6 (K2 decisa ogni giorno): corretto 0,38 da sola; lo 0,73 è solo con G1 dentro, e G1 + G6 rende meno di G1 da sola.
* 86, F5N (F5 neutra al mercato): corretto 0,83, t 4,58; è F5 al 93%.
* 89, F5C (esposizione secondo il carry atteso): variante di F5, aggiunge solo volatilità.
* 92, il clima del mercato su G1 e F5: corretti 0,86 e 0,83; regolatore di G1 e F5.
* 93, G1-S (interruttore sulle perdite): corretto 0,87, t 4,76; variante di G1, verdetto già favorevole («aggiunge protezione»).
* 94, G1N-S: corretto 0,82, t 4,53; variante di G1N.
* 97, CC (il lato venduto di F5 coperto a pronti): corretto 0,71, t 3,99; variante di F5.
* 124, G1M (minimo di monete per lato): corretto 0,85; variante di G1.
* 142, G1S (G1 dentro i settori): Sharpe 1,49, sotto G1 in ogni anno; variante di G1.

**Nel paper o nel demo, o non bocciate**
* 24 F5, 57 G1, 69 G11, 88 G1N: nel paper o nel demo.
* 26 e 27 (E4), 30 e 32 (N3): nel paper (eventi).
* 59, G4: passa l'esame (p 0,0093); fuori dal paper per scelta (doppione di N3), non per un numero.
* 147, GA2C: conferma debole, va nel paper; non bocciata.
* 148, G1P: «sì».

**Già riesaminate da una revisione separata, senza dubbi aperti sul calcolo**
* 70, G12 ed E4 (`REVISIONE_G12.md`): E4 corretto a p 0,0067, resta nel paper come informazione.
* 105, l'effetto Coinbase (`REVISIONE_105.md`): p 0,016 dopo la revisione, giudizio «non regge»; la misura in avanti continua, ma non è un dubbio sul calcolo.
* 107, i perpetui in chiusura (`REVISIONE_107.md`): con i dati completi p 0,116; resta solo l'osservazione su Binance che blocca i nuovi ordini.
* 110, vendere le opzioni (`REVISIONE_110.md`): il t 2,81 veniva tutto dall'approssimazione dei prezzi; con i prezzi veri Sharpe 0,01.

**Lontane dal passaggio o già spiegate**
* 12, K1: sostituita da K2 (riga 1).
* 14, M1: «quasi», corretto 0,59; l'errore già trovato la abbassa (1,35 → 0,79), e M6 la rifà con cinque semi: corretto 0,16.
* 25, M7 e F5 + M7: M7 t 2,73 ma corretto 0,32; F5 + M7 0,83 sta sotto F5 da sola. M7 è dentro la riga 1 ed è lo stesso vantaggio della riga 5 (correlazione 0,70).
* 31, M7 + M8: corretto rivisto 0,44, t 3,05; lontana.
* 48, R1 (il regista): corretto rivisto 0,54, t 3,24; sotto 0,60 e peggio delle tre strategie sempre accese.
* 45, I1 e I2: I1 corretto 0,05; I2 p 0,0064 contro la soglia 0,001 (sei volte).
* 65, G8: p 0,030, ma peggio di N3 sugli stessi eventi con l'intervallo tutto sotto zero (−2,41; −0,54 punti).
* 74, G15 (gli sblocchi dei gettoni): p 0,063, 2026 negativo e senza l'uscita a +30% −0,02%; più di un criterio.
* 41, U1 (Upbit): p 0,070 contro la soglia 0,0014.
* 81 e 83 (programma 9, il funding come filtro): p 0,31 e differenza p 0,35.
* 90, N3V: il risultato va al contrario dell'ipotesi.
* 95, CF (l'uso delle catene): t 1,26, corretto 0,02; 13 catene non scaricate (errore del server), ma il margine è troppo largo perché cambino il verdetto.
* 101, VS: t 1,63, quattro anni su cinque negativi.
* 112, LQ: p 0,33 su tutto, Sharpe del portafoglio 0,00.
* 137, HLI: t 1,32, corretto 0,05.
* 146, AT (gli attacchi informatici): p 0,071 e negativa senza le 5 migliori, cioè due criteri; 28 eventi.
* 149, 1:1:1: il t più alto (2,42) è il migliore di 60 combinazioni, corretto 0,10 con 306 prove; è quello che ci si aspetta dal caso.
* Tutte le altre: corretto sotto 0,40, t sotto 2, p sopra 0,05 o verso opposto all'ipotesi.
