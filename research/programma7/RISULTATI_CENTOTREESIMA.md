# Risultati della prova 165: vendere le monete che somigliano a quelle chiuse (idea 156)

Eseguita il 22 novembre 2026 da strategy-researcher. Nessun giudizio sulla credibilità (lo dà backtest-auditor).

## Riepilogo
* **Esito secondo il criterio scritto: NON PASSA, per tutte e due le varianti** (A: +5,67% l'anno; B: +20,66% l'anno, sul capitale fisso di 1.000 USDT).
* Condizioni non soddisfatte, in entrambe: ogni anno positivo (il 2026 è a −42,8% in A e −47,0% in B, dopo un 2024 e un 2025 positivi), t almeno 3
  (A 0,30; B 0,75), Sharpe corretto per famiglie almeno 0,80 (A 0,005; B 0,015), meglio della selezione a caso sopra il 95° percentile
  (A: media settimanale +0,11% contro 95° percentile +1,07%; B: +0,40% contro +0,76%). Soddisfatta solo: netto positivo.
* **Il guadagno non viene dalle chiusure**: nella variante A nessuna delle 145 posizioni è stata annunciata in chiusura durante la tenuta (100% del netto
  è «mai annunciata»); in B solo 3 uscite per annuncio, la classe «dopo l'annuncio» vale il 22% del netto, la classe «prima dell'annuncio» −0,2%. La prova
  si comporta come «vendere monete poco scambiate e comprare Bitcoin», senza la chiusura vera. Precisione descrittiva: B prime 10 monete chiuse entro 45
  giorni 1,9% contro 0,8% di base; A 0 su 135 contro 0,8%.
* Il coefficiente della variazione del volume ha il segno **opposto** all'atteso (positivo nella maggior parte delle decisioni): scritto, non cambiato.
* Controllo notevole, descrittivo: senza i 10 contratti il cui volume continua oltre 7 giorni dopo la chiusura (tolti dal modello e dalla scelta) A fa +49,2%
  l'anno e B +35,7%, ma il 2026 resta negativo (−8,7% e −9,4%) e il t è 1,84 e 1,32; non è una variante e non cambia l'esito.

## La prova come è scritta (citata, non riformulata) e scala di tempo
Regole: `research/programma7/CENTOTREESIMA.md` (commit e2680f2), con «Chiusura della verifica» e, dove diverse, le correzioni di
`VERIFICA_CENTOTREESIMA.md` (punti 3-5, 8-15, 17-19). Citazioni:
* «Quattro numeri [...] diventano **due**, misurati sulle candele giornaliere: (a) il volume medio in USDT dei 30 giorni interi prima del giorno, (c) il rapporto fra
  il volume medio dei 30 giorni e quello dei 60 giorni prima (giorni D−90…D−31), ciascuno in classifica fra i contratti vivi quel giorno».
* «regressione logistica con penalità fissa (L2, forza 1,0), [...] rifatta a ogni decisione» = `LogisticRegression(penalty='l2', C=1.0, solver='lbfgs', max_iter=1000)`.
* «Alla decisione si prendono le **N monete con il punteggio più alto** [...] **Short** di ogni moneta e **long Bitcoin** per lo stesso valore totale».
* «**A (lenta)**: N = 5 monete, decisione il primo giorno del mese [...]. **B (veloce)**: N = 10 monete, decisione ogni lunedì, tenuta 7 giorni.»
* «se in un giorno il massimo supera del 30% il prezzo di entrata, uscita a quel prezzo +1% di scarto»; se annunciata durante la tenuta «si tiene [...] e si
  esce all'apertura dell'ultimo giorno prima della chiusura o alla fine del periodo, il primo dei due».
* Spese: 0,05% a mercato + scarto 0,01% su BTC, ETH e SOL e 0,02% sulle altre.
* Prime decisioni (punto 5 della chiusura): A il 1° giugno 2024, B lunedì 13 maggio 2024. Capitale fisso 1.000 USDT, senza comporre.
* Esame: netto positivo; ogni anno positivo (anno parziale solo con almeno 8 settimane: il 2024 le ha, 32 in A e 34 in B); t almeno 3; Sharpe corretto almeno 0,80 con
  `corretto_famiglie` (le due varianti in `nuove`); ciascuna variante sopra il suo 95° percentile della selezione a caso (1.000 estrazioni, seme 2026).
* Scala di tempo: giornaliera (decisione e prezzi all'apertura delle 00:00 UTC; massimo giornaliero per la protezione); esame sulle settimane lunedì-domenica.
  Periodo: dalla prima decisione al 31 ottobre 2026; tutto si chiude all'apertura del 1° novembre 2026 con le spese.

### Scritto prima dei risultati (nessun rendimento guardato: fase «modello», file `risultati_centotreesima/modello.json`, `modello_A.csv`, `modello_B.csv`)
* Date di partenza: A 1° giugno 2024, B 13 maggio 2024. Con il file degli eventi gli annunci prima del 7 maggio 2024 sono 20 (il quindicesimo è del 6 maggio 2024).
  Alla prima decisione il modello ha 23 contratti chiusi con almeno una riga positiva valida (in A e in B); alla fine 82 (A) e 85 (B). Tutte le decisioni hanno il modello
  (A 29 su 29, B 129 su 129), nessuna mancata convergenza.
* Eventi: il file ha 87 righe e 87 contratti, per anno 2022: 12, 2024: 19, 2025: 27, 2026: 29 (i numeri 85 e 3/21/29/32 delle regole non tornano: vale il file). Tutti e 87
  hanno le candele nell'archivio.
* **Contratti con volume positivo oltre 7 giorni dopo la chiusura del file (10):** BLZ (844 giorni, fino al 23 dicembre 2024); CTK (550, fino al 31 ottobre 2026); CVC (534, fino al
  31 ottobre 2026); CVX (466, 31 ottobre 2026); ICP (1.496, 31 ottobre 2026); MAVIA (585, 31 ottobre 2026); MDT (11, 31 ottobre 2026); OMG (39, fino al 31 gennaio 2025);
  SLP (466, 31 ottobre 2026); TLM (1.312, 31 ottobre 2026). Restano nel modello come chiusi (dati tagliati alla chiusura del file); i risultati senza di loro sono nei controlli.
* **Controllo di coerenza dei coefficienti** (media, minimo e massimo sulle decisioni; classifiche in [0,1]): volume del livello **negativo in tutte le decisioni** (A: media −4,14, da −4,92 a −3,32;
  B: media −4,13, da −4,93 a −3,18), cioè volume basso → più probabilità, come atteso. Variazione del volume (rapporto 30 giorni su 60): **positiva** (segno opposto all'atteso) in 26 decisioni su 29 (A,
  media +0,50, da −0,36 a +1,55) e in 116 su 129 (B, media +0,51, da −0,39 a +1,64). Il segno del coefficiente cambia fra una decisione e l'altra 2 volte in A e 2 in B. Ultimo modello: A volume −4,01, variazione +0,61; B −3,96 e +0,56.
* **Precisione descrittiva** (non decide; decisioni con 45/90 giorni dopo entro il 1° ottobre 2026, ultimo annuncio del file): prime N monete chiuse (annunciate) entro 45 giorni: A 0 su 135 (0,0%)
  contro frequenza di base 0,78%; B 23 su 1.190 (1,93%) contro 0,80%. Entro 90 giorni: A 2 su 130 (1,54%) contro 1,65%; B 36 su 1.120 (3,21%) contro 1,69%. Primo 5% dei punteggi, 45 giorni dopo: A 2,1% di
  precisione (11 casi su 524 monete in classifica alta), B 2,4%; quota delle chiusure vere nel primo 5%: A 13,9%, B 15,4%.

## Implementazione (file, commit)
* Dati: `research/programma7/centotreesima_dati.py` (fasi `elenca`, `scarica`, `rapporto`): candele giornaliere mensili di `data.binance.vision` per 915 simboli USDT-M (compresi i chiusi, escluse le stabili),
  dal dicembre 2021 al 31 ottobre 2026, con il CHECKSUM di ogni file; 21.226 file scaricati, nessuno mancante (0 file con errore 404), 913 simboli con file. Dati in `research/data/centotreesima/d1/` (fuori da git).
  Impronte e buchi: `risultati_centotreesima/impronte_dati.json` (impronta unica dell'elenco `8d1f13ed…`) e `buchi_dati.json`.
* Calcolo: `research/programma7/centotreesima.py` (fasi `modello` e `prova`). Funding dal pannello (`seconda.pannello`) solo fino al 31 ottobre 2026. Deterministico salvo la selezione a caso (seme 2026).
  Commit di riferimento nel registro: a6ded67 (HEAD al momento del calcolo). Dopo il calcolo ho aggiunto un dato nella chiave della memoria interna (il valore per posizione, V); ho verificato rieseguendo A e B che le serie
  giornaliere salvate sono identiche, quindi nessun risultato cambia.
* Un mio errore nello scarico: la prima esecuzione ha messo i file nella cartella `klines` invece che per simbolo (indice sbagliato nello script). Ho corretto lo script e spostato i 21.226 file nelle cartelle dei simboli, senza
  riscaricare né toccarne il contenuto (i controlli e le impronte sono fatti dopo lo spostamento).

## Varianti provate
**2** (A e B), solo quelle scritte. Registro: `research/trials/centotreesima.csv` (2 righe, esito «non passa» tutte e due, seme 2026). Nessuna variante fallita o interrotta. I controlli (selezione a caso, scarto 0,04%, ordine limite,
senza i contratti con volume dopo la chiusura, classi A/B/C) non sono varianti e non sono registrati come tali: stanno in `risultati_centotreesima/esame.json`.

## Risultati
Serie: `risultati_centotreesima/giorni_A.csv.gz`, `giorni_B.csv.gz`, `settimane_A.csv.gz`, `settimane_B.csv.gz` (colonna `netto`, indice = lunedì della settimana come nelle prove 157-163). Rendimenti sul capitale fisso di 1.000 USDT.
`ast.periodo()` ferma le settimane dell'esame al 5 ottobre 2026 (come nelle prove 157-163); le cifre per anno e il netto annuo sono sui giorni fino al 31 ottobre 2026.

| | A (5 monete, mensile) | B (10 monete, lunedì) |
|---|---|---|
| giorni (settimane dell'esame) | 883 (124) | 902 (126) |
| netto annuo sul capitale | +5,67% | +20,66% |
| 2024 / 2025 / 2026 (a ottobre) | +26,37% / +33,87% / −42,75% | +10,41% / +83,54% / −46,98% |
| prezzo (lordo senza funding) annuo | +9,06% (2024 +33,9, 2025 +35,6, 2026 −40,2) | +24,77% (+15,2, +87,1, −42,8) |
| funding annuo | −1,73% | −1,29% |
| costo medio (spese) annuo | 1,66% | 2,83% |
| discesa più grande (giornaliera, capitale fisso) / (settimanale) | −43,4% / −58,3% | −34,4% / −52,3% |
| Sharpe su 52 settimane / su 365 giorni | 0,19 / 0,12 | 0,48 / 0,43 |
| t | 0,30 | 0,75 |
| Sharpe corretto per famiglie (287 serie nel mazzo, 200 famiglie; A e B sono una famiglia a sé) | 0,005 | 0,015 |
| selezione a caso: media settimanale reale / media a caso / 95° percentile / quota di estrazioni sotto il reale | +0,11% / +0,41% / +1,07% / 22,6% | +0,40% / +0,25% / +0,76% / 69,9% |
| durata media di una posizione | 26,6 giorni | 6,8 giorni |
| posizioni (rimaste dalla decisione prima) | 145 (44) | 1.290 (927) |
| uscite per protezione al +30% / per annuncio / prezzo mancante | 34 / 0 / 0 | 76 / 3 / 0 |
| correlazione settimanale con G1 | 0,26 | 0,22 |
| esito secondo il criterio scritto | non passa | non passa |

Controlli descrittivi (esame.json):
* **Scarto allo 0,04%** (monete diverse da BTC, ETH, SOL): A +5,3% l'anno (2024 +26,0, 2025 +33,5, 2026 −43,1), B +20,0% (+9,8, +82,9, −47,7). Cambia poco, non cambia l'esito.
* **Ordine limite (0,02%)**: A +6,4%, B +21,9%; stesso esito.
* **Senza i 10 contratti con volume dopo la chiusura** (tolti dal modello e dalla scelta): A +49,2% (2024 +56,4, 2025 +93,2, 2026 −8,7), Sharpe 0,19→1,19, t 1,84, discesa −16,8%; B +35,7% (+11,5, +88,6, −9,4), Sharpe 0,85, t 1,32, discesa −33,0%.
  Il 2026 resta negativo; sono controlli, non l'esame.
* **Da dove viene il guadagno (A = giorni prima dell'annuncio, B = dal giorno dell'annuncio in poi, C = mai annunciata nella tenuta), netto in USDT:** variante A: C 137,8 (100%), A e B zero.
  Variante B: C 397,9 (77,9%), B 114,4 (22,4%), A −1,2 (−0,2%); funding C −33,9, B +1,2, A +0,9. Per anno (B): 2024 C 66,3; 2025 C 771,5 e B 63,5; 2026 C −440,0, B 50,9, A −1,2.
  La classe B non è la maggioranza: «non promosso per natura del guadagno» non scatta; scatterebbe solo se l'esame fosse passato.
* **Senza le 5 monete migliori** (togliendo il loro netto): A −429,4 USDT in totale (DF, NTRN, FORTH, LOKA, HFT); B −7,1 (C −120,1, B +114,4, A −1,2; NKN, NULS, DF, OXT, LOKA). Il netto positivo dipende da poche monete.
  Contributo delle migliori: A DF +138, NTRN +126, FORTH +116, LOKA +107, HFT +81; peggiori SCRT −134, KOMA −89, VELODROME −88. B migliori NKN +146, NULS +104, DF +98, OXT +92, LOKA +78; peggiori BR −99, FIO −80, BMT −78.
* Monete scelte più spesso: A DEFI 14 volte, BNT 11, OXT 7; B BNT 79, DEFI 66, OXT 42, RIF 35, SYS 31 (BTCDOM 3 volte in A).

## Variante migliore e sua sensibilità alle varianti vicine
La migliore per netto e per Sharpe è B (+20,7% l'anno, Sharpe 0,48), ma non passa nessuna condizione tranne il netto positivo. Le varianti vicine (scarto doppio, ordine limite) cambiano il netto di 1-2 punti: l'esito è robusto alle spese.
Non è robusta alle monete: senza le 5 migliori il netto diventa negativo in tutte e due; e al 2026, negativo in tutte le letture. Nessuna altra variante è stata provata (N, finestre e penalità non si cambiano).

## Anomalie e possibili errori di motore o dati
1. **Segno della variazione del volume opposto all'atteso** (vedi sopra): il modello associa la chiusura a volume basso ma in crescita rispetto ai 60 giorni prima. Scritto, non cambiato.
2. **Contratti indice o strani nelle scelte:** DEFIUSDT (indice DeFi) è scelto 14 volte in A e 66 in B, BTCDOMUSDT (indice di dominanza di Bitcoin) 3 volte in A. Non sono monete che Binance «chiude per poco volume»; le regole non li escludono e non li ho esclusi.
   Non ho potuto escludere i contratti su azioni per tipo ufficiale (backlog P32): non so se alcuni sono nella scelta.
3. **Contratti dell'elenco degli eventi ancora vivi:** 10 hanno volume anche molti mesi dopo la chiusura scritta (elenco sopra). Sono chiusure rinviate o annullate o errori del file; nel modello sono esempi positivi, e togliendoli i risultati cambiano molto (A +49%).
4. **Il file degli eventi arriva al 1° ottobre 2026** (ultimo annuncio): gli annunci successivi (per esempio quello del 21 ottobre 2026 su PTB e MITO, citato in `REVISIONE_107.md`) non ci sono. Quei contratti restano «vivi» e possono entrare nella scelta o contare come negativi nelle etichette.
5. **Funding mancante:** 171 dei 913 simboli non hanno il funding nel pannello (zero al posto del dato); 25 posizioni su 145 in A e 165 su 1.290 in B sono su simboli senza funding. Il funding annuo totale è piccolo e negativo (−1,7% e −1,3%): l'effetto non cambia l'esito, ma non è misurato.
6. **Buchi dell'archivio:** 53 simboli hanno 331 giorni mancanti in tutto, tutti il 26-28 febbraio 2022 e il 1-2 aprile 2022 (e un giorno il 17 aprile 2022); non ci sono duplicati né mesi mancanti. Toccano solo le prime finestre del modello (un contratto con un giorno mancante nei 90 non è ammissibile quel giorno).
7. Il file `eventi_finale.csv` ha 87 contratti, non 85, con distribuzione diversa da quella scritta nelle regole.
8. **Il prezzo del 1° novembre 2026** è la chiusura del 31 ottobre (manca il file di novembre): le posizioni aperte alla fine si chiudono a quel prezzo con le spese.
9. Nessuna posizione non aperta per prezzo mancante e nessuna uscita per prezzo mancante o «annunciata e chiusa nello stesso giorno».
10. Nessun errore del motore o dei caricatori ufficiali trovato (la prova ha un suo motore, perché le prove 157-163 non hanno un motore con questa regola; verifica interna: il netto giornaliero somma esattamente profitti + funding − spese, e il profitto di una posizione ricalcolata a mano coincide).

## Varianti non previste che proporrei (non eseguite)
* Una prova nuova, con regole scritte prima, che elimini dal modello gli esempi «chiusi» con volume dopo la chiusura e i contratti indice (DEFI, BTCDOM): il controllo senza i 10 contratti dà numeri molto più alti, ma è un risultato guardato dopo, quindi non va usato per cambiare questa prova.
* Il modello con l'interesse aperto (tolto per la dimensione dello scarico) se un giorno ci sarà un archivio più leggero.

## Domande aperte
1. Il segno positivo della variazione del volume (opposto all'atteso) va accettato come è, o va indagato (può dipendere dai 10 contratti con volume dopo la chiusura)?
2. I contratti indice (DEFI, BTCDOM) e quelli su azioni vanno esclusi dall'universo nelle prove nuove?
3. Per i 10 contratti dell'elenco degli eventi ancora vivi, la chiusura scritta nel file va considerata un evento vero (come qui) o va corretta nel file degli eventi?
4. Il file degli eventi va esteso a dopo il 1° ottobre 2026 (annunci di ottobre mancanti)?
5. La correlazione con la prova 107 non è stata calcolata: la 107 non ha una serie settimanale leggibile da `asticella.py` fra quelle che ho usato. Serve?
6. Il funding per i 171 simboli fuori dal pannello va aggiunto con uno scarico dedicato?

## Letture delle regole che ho dovuto scegliere
1. Contratto «ammissibile» a t: candele valide in tutti i 90 giorni t−90…t−1, non annunciato prima di t (ora di annuncio prima delle 00:00 di t), volume medio dei 30 giorni e dei 60 giorni prima entrambi maggiori di zero (per il logaritmo e il rapporto), Bitcoin ed Ether esclusi dalla classifica e dalla scelta (restano come gamba long).
2. Classifica con rango medio per i pari e posizione (rango−1)/(n−1); righe di allenamento = tutte le coppie (contratto, giorno) ammissibili con t+45 ≤ D−1; etichetta = annuncio fra le 00:00 di t e le 00:00 di t+45.
3. Alla decisione la moneta che resta fra le prime N viene **riportata a capitale/N** pagando le spese sulla differenza (lettura prudente di «si paga solo il cambio»); il prezzo di entrata della protezione resta quello originale finché la posizione è continua.
4. Il Bitcoin long è ripreso alla decisione al valore di capitale/N per ogni short aperto, con spese sulla differenza netta; dopo un'uscita per protezione la sua parte esce all'apertura del giorno dopo (senza prezzi orari), pagando le spese.
5. Funding del giorno di uscita per protezione contato per il giorno intero; funding del Bitcoin pagato dalla gamba long.
6. Se alla decisione una moneta scelta non ha il prezzo di apertura, il posto resta vuoto (mai capitato).
7. Protezione: massimo giornaliero > 1,30 × prezzo di entrata (anche nel giorno di entrata); uscita a 1,30 × 1,01 del prezzo di entrata; la moneta non rientra fino alla decisione dopo.
8. Discesa su capitale fisso: somma cumulata dei rendimenti giornalieri (senza capitalizzare); Sharpe su 52 settimane e t come in `asticella.py` (settimane fino al 5 ottobre 2026), Sharpe su 365 giorni dai giorni fino al 31 ottobre.
9. Anni dell'esame: 2024 (con almeno 8 settimane), 2025, 2026 fino a ottobre; «ogni anno positivo» sul netto annualizzato dell'anno.
10. Selezione a caso: nuova estrazione a ogni decisione fra i contratti ammissibili e con il modello valido (stesse date, stessa tenuta, stessa protezione e spese), generatore con seme 2026 ripartito per variante; confronto sulla media settimanale netta del periodo intero.
11. Controllo senza i contratti con volume dopo la chiusura: tolti sia dall'allenamento sia dalla scelta; senza le 5 monete migliori: tolti i loro profitti, funding e spese dalla ripartizione A/B/C (non rifatta la simulazione).
12. Classi A/B/C: per posizione, A = giorni prima di quello dell'annuncio; B = giorno dell'annuncio e successivi; C = non annunciata nella tenuta. Le spese sono messe nella classe del primo giorno della posizione.
13. Scarto 0,04%: sulle monete diverse da BTC, ETH, SOL (che restano a 0,01%); ordine limite: 0,02% al posto dello 0,05% (lo scarto resta).
14. Prima settimana della variante A: è parziale (1-2 giugno 2024, settimana del 27 maggio).
15. Orizzonte della precisione descrittiva: solo decisioni con 45 (o 90) giorni dopo entro il 1° ottobre 2026.
