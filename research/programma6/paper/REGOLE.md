# Programma 6 — il paper delle candidate (misura sui dati nuovi)

Scritto il 19 ottobre 2026, sera, **prima di qualunque dato dopo il 17 ottobre 2026**, su delega del proprietario («se
pensi serva misurare in paper procedi hai campo libero fino a che non trovi cosa funziona», 19 ottobre 2026). `DRY_RUN`
resta vero: niente soldi veri, niente chiavi, il bot sulla macchina non cambia.

## 1. Cosa si misura

Le candidate del programma 6, con le regole **già scritte e già calcolate sul passato**, senza cambiare niente:

| Nome | Regola | Da | Sul passato |
|---|---|---|---|
| **F2** | il funding fra monete, pesi uguali: ogni lunedì, fra le 100 monete più scambiate, long il quinto con il funding dei 7 giorni prima più basso, short il quinto più alto (`SESTA.md`) | `sesta.py` | +47,5% l'anno, Sharpe 1,03 dal 2021 |
| **C1** | CTREND: 28 indicatori combinati, long il quinto più forte, short il più debole delle 100 più scambiate, ogni lunedì (`TERZA.md`) | `terza.py` | Sharpe 0,39 dal 2022; 1,49 dopo l'aprile 2025 |
| **A1** | la regola pubblicata di tendenza: 9 canali di Donchian, volatilità al 25%, 20 monete più liquide, ogni giorno (`SECONDA.md`) | `seconda.py` | Sharpe 0,53 dal 2021 |

F2 è la candidata principale. C1 e A1 si misurano perché costano poco e la loro correlazione con F2 è bassa.

**Aggiunta del 19 ottobre 2026, sera, ancora prima di qualunque dato nuovo** (i dati nell'archivio arrivano al 18 ottobre, il
periodo P comincia il 20 per i giorni e il 26 per le settimane): **F3**, il funding fra monete con i pesi secondo la
volatilità (`OTTAVA.md`, `ottava.py`; sul passato +50,6% l'anno, Sharpe 1,28 dal 2021, positiva in ogni anno), diventa la
candidata principale insieme a F2. Il verdetto di F3 segue la sezione 3 come le altre.

**Seconda aggiunta, stessa sera, ancora prima di qualunque dato nuovo**: **K1** (`DODICESIMA.md`, `dodicesima.py`): denaro
che entra e leva che costa poco (la media dei ranghi di −funding, +acquisti a mercato e +crescita dell'interesse aperto
dei 7 giorni prima). Sul passato è **costruzione** (due versi visti dopo il calcolo: +37,6% l'anno dal 2022, Sharpe 1,27):
per K1 il paper è l'unica prova. Ogni mattina si scaricano anche i dati sulle posizioni dei giorni nuovi
(`scarico_metrics.py`). Verdetto come le altre (sezione 3).

**Terza aggiunta, 20 ottobre 2026, ancora prima di qualunque dato della prima settimana misurata** (quella dal 26
ottobre): **M1** (`QUATTORDICESIMA.md`, `quattordicesima.py`), il modello ad alberi che impara ogni 4 settimane, solo dal
passato, come unire tutti gli ingredienti (28 indicatori, rendimenti, volatilità, funding, acquisti a mercato, volume,
legame col Bitcoin, posizioni, stato del mercato). Sul passato, dal 2022 e sempre fuori dal campione del modello: +50,9%
l'anno, Sharpe 1,35, sopra il caso (`caso_M1.json`); non passa lo Sharpe corretto (0,59 con 36 prove). Correlazione con F3
0,17 e con K1 0,03: è quasi indipendente dalle altre. Nel paper il modello si riallena con la stessa cadenza (ogni 4
settimane dal 3 gennaio 2022). Verdetto come le altre (sezione 3).

**Quarta aggiunta, 20 ottobre 2026, ancora prima della prima settimana misurata**: **F3 + M1 a rischio uguale**
(`QUINDICESIMA.md`): il capitale diviso fra le due in parti inversamente proporzionali alla volatilità delle 26 settimane
prima. Sul passato dal 2022: +44,8% l'anno, Sharpe 1,69, positiva in ogni anno; non passa lo Sharpe corretto (0,76 con 37
prove). Verdetto come le altre (sezione 3).

## 2. Come

* Ogni mattina (con l'aggiornamento della prova in avanti del programma 5) si scaricano le candele giornaliere nuove di
  tutti i perpetui e l'indice del premio orario del mese in corso; si ricostruisce la tabella; si ricalcolano le tre regole
  **con lo stesso codice**; si tengono i giorni (A1) e le settimane (F2, C1) **dal 20 ottobre 2026** in poi: il **periodo P**.
* Il **funding** del mese in corso non è ancora nell'archivio (esce a fine mese): fino ad allora si stima dall'indice del
  premio orario con la formula di Binance (premio medio dell'intervallo più l'interesse dello 0,01% riportato entro
  ±0,05%), tre intervalli al giorno. Quando esce il file del mese si ricalcola tutto con il funding vero: il risultato che
  conta è quello col funding vero. Nel rapporto si dice quali giorni sono ancora stimati.
* **27 novembre 2026 (audit del 26 novembre).** Il funding dei giorni dopo l'ultimo file mensile non si stima più dall'indice del
  premio: ogni mattina, prima di ricostruire la tabella, si scarica il funding vero dall'interfaccia pubblica di Binance
  (`/fapi/v1/fundingRate`, `funding_api.py`); quando esce il file del mese vince l'archivio. La stima dal premio resta solo per i
  giorni ancora senza il dato vero (`funding_stimato`), che il rapporto conta nella riga «Funding senza il dato vero». Il 31 ottobre
  prende anche il regolamento delle 00:00 del 1° novembre. Dalla stessa data la tabella toglie i contratti che non sono monete dal
  loro onboardDate (il tipo ufficiale di Binance: la regola del bot più i perpetui di pre-mercato su una moneta, sezione 11) e tiene
  separati i simboli rilanciati: contratto nuovo dal onboardDate, la parte di prima come `<SIMBOLO>_prima_del_<giorno>`, con i dati
  sulle posizioni e le candele a 1 ora del simbolo di base fino al rilancio (SECONDA.md, sezione 9). Il rapporto dice quanti giorni
  in coda la tabella ha tolto perché l'archivio li ha pubblicati a metà (riga «Giorni in coda tolti», `controllo_dati.giorni_in_coda_tolti`
  in paper.json; con più di 2 la riga lo segnala). Numeri del periodo P rifatti il 27 novembre (dati fino al 25 novembre; prima →
  dopo, rendimento totale): F5 +5,56% → +7,70%, K2 +3,98% → +8,01%, F3 +2,61% → +5,60%, K1 −0,16% → +4,90%, F2 +0,67% → +3,44%,
  M7 −0,43% → −3,09%, M1 −11,86% → −5,96%, C1 −25,89% → −8,55%, F5 + M7 + K2 +3,69% → +5,66%. F, K ed EWIL cambiano per il solo
  funding vero; M e C1 anche per i rilanci, perché si allenano sulla storia (prima il contratto nuovo entrava nell'universo con la
  storia del vecchio). Gli eventi N3 restano quelli pubblicati; l'evento E4 cambia di poco (r28 da 0,2553 a 0,2565). Fonte: rapporto della correzione «motore» del 27 novembre (giri con il
  codice di prima, con i rilanci uniti e con i rilanci separati, sugli stessi dati).
* Il rapporto (`PAPER.md`, `paper.json`) dice per ogni candidata: il rendimento del periodo P, settimana per settimana o
  giorno per giorno, lo Sharpe da quando è partito, il confronto col Bitcoin, e **le posizioni di adesso** (cosa terrebbe la
  regola nella settimana o nel giorno in corso).

## 3. Quando e come si giudica

* Il verdetto si dà a **52 settimane** (il lunedì 25 ottobre 2027) e a **104 settimane** (23 ottobre 2028), mai prima.
* Una candidata **passa** se il rendimento netto medio del periodo P è positivo con **p ≤ 0,025** a una coda (bootstrap a
  blocchi di 4 settimane per F2 e C1, di 20 giorni per A1), è positiva a costi doppi e il suo Sharpe nel periodo P non è
  sotto la metà di quello sul passato. Due sguardi (52 e 104 settimane) con 0,025 l'uno: la soglia d'insieme resta il 5%.
* Prima del verdetto i numeri si leggono come informazione, non come prova: con uno Sharpe vero di 1, un anno di dati dà
  un intervallo che passa lo zero quasi sempre.

## 4. Controllo della stima del funding (19 ottobre 2026, prima di usarla)

Sui tre mesi luglio-settembre 2026, dove il funding vero è nell'archivio, la stima dall'indice del premio orario (programma
5, `research/data/p5/<SIMBOLO>/premium`) dà la **stessa media** e una correlazione giorno per giorno di 0,775 (BTC), 0,683
(ETH), 0,910 (SOL), 0,846 (DOGE), 0,908 (XRP), 0,719 (LINK), su 92 giorni ciascuna. Il segnale di F2 è la somma di 7 giorni:
la stima basta fino all'arrivo del file vero.

## 5. Correzione dei dati prima della prima settimana misurata (20 ottobre 2026)

Le monete tolte dal listino restano nei file dell'archivio con il prezzo fermo e il volume zero, e il loro funding era
riempito con la media dei 90 giorni prima (`research/programma6/controllo_zombi.py`). Da oggi, **prima della prima
settimana misurata (26 ottobre)**, per tutte le candidate: funding zero nei giorni a volume zero e fuori dall'universo le
monete con volume zero la domenica. Effetto sul passato (`controllo_zombi.json`): F3 Sharpe 1,296 → 1,295, K1 1,269 →
1,262, **M1 1,35 → 0,79**. Le regole del giudizio (sezione 3) non cambiano; per M1 e per F3 + M1 il confronto «Sharpe del
periodo P non sotto la metà di quello sul passato» usa il numero sul passato con i dati corretti.

## 6. M6 come informazione (20 ottobre 2026, prima della prima settimana misurata)

La ventitreesima prova (`research/programma6/VENTITREESIMA.md`, regole scritte prima) dà a M6 (il modello di M1 con la media
dei ranghi di cinque semi) Sharpe 1,02 dal 2022 sui dati corretti, positivo in tutti gli anni, ma Sharpe corretto 0,16. Come
scritto nella sezione 3 di quelle regole, entra nel paper **come informazione accanto a M1** (non come candidata con il suo
verdetto), dalla settimana del 26 ottobre.

## 7. F5 come informazione (20 ottobre 2026, prima della prima settimana misurata)

La ventiquattresima prova (`research/programma6/VENTIQUATTRESIMA.md`, regole scritte prima) dà a F5 (il segnale di F3 con la
banda: entrata nel 20%, uscita sotto il 40%) Sharpe 1,93 dal 2021, contro 1,28 di F3 sugli stessi dati, con spese del 4,9%
invece del 7,7%; contro il caso media −0,11 e massimo 0,79 su 200 (`F5_caso.json`); Sharpe corretto 0,81 con 48 prove. Come
scritto nella sezione 4 di quelle regole, entra nel paper **come informazione accanto a F3** dalla settimana del 26 ottobre.

## 8. M7 e F5 + M7 come informazione (20 ottobre 2026, prima della prima settimana misurata)

La venticinquesima prova (`research/programma6/VENTICINQUESIMA.md`, regole scritte prima) dà dal 2022: M7 (M6 con la banda)
Sharpe 1,25 contro 1,08 di M6 sugli stessi anni; F5 + M7 a rischio uguale Sharpe 1,83 contro 1,69 di F5 da sola, volatilità
24,2%, ogni anno positivo; Sharpe corretti 0,20 e 0,65 con 50 prove. Come scritto nella sezione 4 di quelle regole, entrano
nel paper **come informazione** dalla settimana del 26 ottobre.

## 9. E4 come candidata a eventi (20 ottobre 2026, regola fissata prima di ogni evento del periodo P)

La ventiseiesima prova (`research/programma6/VENTISEIESIMA.md`) passa l'esame scritto con E4: dopo il passaggio a un
intervallo del funding più corto con funding positivo, short la moneta e long il Bitcoin per 7 giorni dall'apertura del giorno
dopo: +11,67% a evento netto, 62 eventi dal 2023, p 0,0047. Contando tutte le prove a eventi del programma la soglia sarebbe
più bassa e non passerebbe: per questo la prova vera è qui.

* **Periodo P**: gli eventi con il primo regolamento all'intervallo più corto dal **21 ottobre 2026 00:00 UTC**.
* **Misura**: ogni evento come la prova (`ventiseiesima.tabella`, verso −1), con i file mensili del funding dell'archivio
  (l'evento si vede quando esce il file del mese: la regola non cambia, si conta dopo).
* **Verdetto** a 52 e 104 settimane (come le altre), mai prima: passa se la media degli eventi del periodo P è sopra zero con
  **p ≤ 0,025** a una coda (bootstrap sulle settimane), se è positiva senza il migliore evento e se non è sotto la metà della
  media sul passato (+5,8%). Con meno di 15 eventi a 52 settimane il verdetto si rimanda a 104.
* Per usarla dal vivo servirebbe vedere il cambio dell'intervallo subito (l'interfaccia pubblica dei futures, che da questa
  macchina non è raggiungibile; dalla VPS sì): è nel backlog, non serve per il paper.

**Nota del 20 ottobre, sera (prova 27, `VENTISETTESIMA.md`).** La conferma di E4 su Gate.io non c'è: come scritta −4,24% a
evento (p 0,67), ma la prova era guastata dai cambi d'intervallo fatti da Gate.io in blocco; senza quelli (calcolo fatto
dopo, descrittivo) +6,00% a evento, 75% vinti, p 0,096. E4 resta nel paper con le sue regole: è il paper che decide.

## 10. K2 e F5 + M7 + K2 come informazione (20 ottobre 2026, sera, prima della prima settimana misurata)

La ventottesima prova (`research/programma6/VENTOTTESIMA.md`) dà dal 2022: K2 (K1 con la banda, **costruzione** come K1)
Sharpe 1,72 contro 1,25 di K1; F5 + M7 + K2 a rischio uguale Sharpe 2,11, volatilità 20,5%, ogni anno positivo; Sharpe
corretti 0,47 e 0,76 con 52 prove. Come scritto nella sezione 4 di quelle regole, entrano nel paper **come informazione**.

## 11. N3 come candidata a eventi (21 ottobre 2026, regola fissata prima di ogni evento del periodo P)

La trentesima prova (`research/programma6/TRENTESIMA.md`) passa l'esame scritto su dati mai guardati (Gate.io): short a 7
giorni dalla quotazione, long il Bitcoin, uscita a +30% (candele a 1 ora, 1% di scarto) o dopo 30 giorni: +7,59% a evento su
449 monete dal 2023, p 0,0001 (con la correzione dei contratti che non sono monete, `TRENTESIMA.md` sezione 4). Solo
monete: su Gate.io il tipo del contratto vuoto (`tipi_gate.py`), su Binance i contratti lanciati con un annuncio di
moneta (titolo con il simbolo, senza «TradFi» né «Pre-IPO»). Due misure in avanti, con la stessa regola:

* **N3-Gate**: le monete nuove di Gate.io non ancora perpetuo su Binance, con la **prima candela dal 21 ottobre 2026**, dai
  file mensili dell'archivio di Gate.io (si vedono quando esce il file del mese).
* **N3-Binance**: le monete nuove dei perpetui di Binance (esclusi i contratti che non sono una moneta), prima candela dal 21
  ottobre 2026, dall'archivio di Binance (candele a 1 ora). Su Binance la regola sul passato sarebbe una costruzione (l'idea
  dell'uscita viene dalla prova 18 sugli stessi dati): per questo vale solo in avanti.
* **Verdetto** a 52 e 104 settimane, mai prima, per ognuna: media degli eventi del periodo P sopra zero con **p ≤ 0,025** a
  una coda (bootstrap sulle settimane), positiva senza il migliore evento, e non sotto la metà della media sul passato
  (+3,8%). Con meno di 30 eventi a 52 settimane il verdetto si rimanda a 104.
* Il calcolo in avanti si aggiunge al paper prima del primo esito possibile (un evento del 21 ottobre si chiude al più tardi
  il 27 novembre).
* **27 novembre 2026 (audit del 26 novembre).** La tabella della ricerca toglie i contratti che non sono monete con il tipo
  ufficiale di Binance (`tipi_contratto.json`). Un perpetuo di pre-mercato su una moneta (contractType PERPETUAL, underlyingType
  PREMARKET, senza TradFi né Pre-IPO: oggi solo PREDICTUSDT) resta una moneta, come vuole la regola di questa sezione (annuncio di
  moneta). Per questo l'evento N3-Binance «PREDICTUSDT dal 1° novembre» resta, e PREDICT_USDT di Gate.io non è un evento (perpetuo
  su Binance dal 25 ottobre). Il bot (sezione 14) toglie i contratti di pre-mercato (`f5.contratti_monete`) e non ha aperto
  PREDICTUSDT: è una differenza nota fra il calcolo e l'esecuzione del bot e non cambia il verdetto, che resta su questo calcolo.

## 12. M7 + M8 come informazione (21 ottobre 2026, mattina, prima della prima settimana misurata)

La trentunesima prova (`research/programma6/TRENTUNESIMA.md`, costruzione) dà a M7 + M8 a rischio uguale Sharpe 1,39 dal 2022
contro 1,25 di M7 da solo; Sharpe corretto 0,20 con 54 prove. Entra nel paper **come informazione**.

## 13. F5 eseguito dal bot (dal 26 ottobre 2026; aggiunto il 22 ottobre, prima dei dati)

Oltre al calcolo di ogni mattina, F5 gira anche **nel bot sulla macchina** (`bot/portafoglio/f5.py`, backlog P16): stesse
regole, con i dati di Binance del momento; ogni lunedì alle 00:05 UTC le operazioni simulate al prezzo mark con commissione e
scarto, poi il funding vero di ogni regolamento; capitale virtuale di 10.000 dollari, nessun ordine vero. Acceso dal file
`ops/paper_f5_acceso`, fuori dal kill switch del vecchio paper; lo stato in `docs/state.md` («Paper F5») e su RTDB in
`/paper_f5`. Serve a misurare quanto l'esecuzione vera si allontana dal calcolo (prezzi del momento, funding vero, parità
ordinate in modo diverso: in 26 settimane del passato 0,15 monete diverse a settimana in media, l'1,3% di peso); **non cambia
il verdetto di F5**, che resta sul calcolo di questo paper a 52 e 104 settimane.

## 14. N3 ed E4 eseguiti dal bot (aggiunto il 22 ottobre 2026, prima di ogni evento eseguito)

Come F5 (sezione 13), anche N3 ed E4 girano **nel bot sulla macchina** (`bot/portafoglio/eventi.py`), con le regole delle
sezioni 9 e 11 e i dati di Binance del momento: N3 short a 7 giorni di vita della moneta (alle 00:05 UTC al prezzo mark),
uscita a +30% sulle candele a 1 ora o dopo 30 giorni; E4 al primo regolamento a un intervallo del funding più corto con il
funding positivo (letto ogni ora da `fundingInfo`, che dalla macchina si raggiunge), short dal giorno UTC dopo per 7 giorni;
sempre long il Bitcoin per lo stesso valore, il 5% del capitale a operazione, al massimo 20 aperte, costi e funding come la
ricerca, 10.000 dollari virtuali, nessun ordine vero. Acceso dal file `ops/paper_eventi_acceso`, fuori dal kill switch del
vecchio paper; lo stato in `docs/state.md` («Paper N3 ed E4») e su RTDB in `/paper_eventi`. Serve a misurare l'esecuzione
vera e a vedere subito gli eventi (E4 qui si vede in giornata, nel calcolo solo quando esce il file del mese); **non cambia i
verdetti di N3 ed E4**, che restano sul calcolo di questo paper a 52 e 104 settimane.


## 6. Aggiunta del 28 ottobre 2026: EWIL, solo informazione

Il proprietario (28 ottobre), dopo la prova 117: «se è un articolo creato nel 2026 forse [...] è una strategia trovata per il mercato
attuale 2025 e 2026?». La prova 117 (`research/programma7/RISULTATI_CINQUANTACINQUESIMA.md`) dice che EWIL (le vincenti elastiche
contro le perdenti inelastiche, Li, Liao, Yang e Zhang) sulle 100 monete più scambiate perde molto nel 2021-2023 e va bene dopo i dati
dell'articolo: dal giugno 2024 Sharpe 1,19.

Quel periodo l'abbiamo già visto, quindi non conta come prova. Si misura in avanti, **senza cambiare niente della regola della prova
117**:
* **le settimane dal lunedì 2 novembre 2026**;
* **una prima occhiata a 26 settimane** (il 3 maggio 2027);
* **il verdetto a 52 settimane**, con le regole della sezione 3. Il confronto «Sharpe del periodo P non sotto la metà di quello sul
  passato» usa lo Sharpe del 2021-2026, −0,20.

Fino ad allora è solo informazione: non entra nel bot.

## 15. Aggiunta del 30 ottobre 2026: HLI, solo informazione

Scritta il 30 ottobre 2026 alle 20:22 UTC, prima di ogni giorno misurato. La prova 135 (`research/programma7/RISULTATI_SETTANTATREESIMA.md`)
ha trovato che vendere le monete dove su Hyperliquid i long pagano più che su Binance faceva Sharpe −2,38, in ogni anno dal giugno 2023;
il verso al contrario (HLI) sulle prime 100 fa 1,90 con i costi, ma è nato da quei dati, e sulle monete 101-200 non ha battuto G1 (prova
137). Quel periodo l'abbiamo già visto: si misura in avanti, **senza cambiare niente della regola della prova 137 sulle prime 100**:
* **la regola**: ogni giorno alle 00:00, fra le monete dell'universo di G1 con il funding di Hyperliquid in tutti e 7 i giorni prima, long il
  quinto con lo scarto (funding di Hyperliquid meno funding di Binance dei 7 giorni) più alto, short il più basso, banda 20/40, pesi secondo
  l'inverso della volatilità, almeno 20 monete, ordini limite come G1 (`cinquantaduesima.conto`); accanto, **G1 sulle stesse monete**;
* **il funding di Hyperliquid** dall'API pubblica, solo dal 20 ottobre 2026 in avanti (`aggiorna.funding_hyperliquid`), salvato in
  `research/data/hyperliquid_recente/` fuori da git;
* **i giorni dal 2 novembre 2026**; un'occhiata a 26 settimane (maggio 2027) e il **verdetto a 52 settimane** (novembre 2027): regge se lo
  Sharpe dell'anno è sopra quello di G1 sulle stesse monete negli stessi giorni.

Fino ad allora è solo informazione: non entra nel bot.

## 16. Aggiunta del 1° novembre 2026: DXI, la stessa regola di HLI con il funding di dYdX, solo informazione

Scritta il 1° novembre 2026 alle 04:23 UTC, prima di ogni giorno misurato e prima di aver letto il funding di dYdX (si è solo provato che
il servizio pubblico risponde). HLI (sezione 15) è nata dai dati di Hyperliquid della prova 135: se il meccanismo è vero (dove i trader
sulla catena pagano più che su Binance, la moneta poi sale), deve vedersi anche su un'altra borsa sulla catena. Sul passato non si
prova: i prezzi di Binance del 2023-2026 sono gli stessi su cui HLI è nata, quindi una prova sul passato non sarebbe indipendente (idea
129 del registro). Si misura solo in avanti:
* **la regola**: identica a HLI (sezione 15), con il funding di **dYdX** (servizio pubblico `indexer.dydx.trade/v4/historicalFunding`, un
  tasso ogni ora, sommato per giorno di tenuta) al posto di quello di Hyperliquid; le monete di dYdX (`XYZ-USD`) si abbinano ai perpetui di
  Binance `XYZUSDT` o `1000XYZUSDT`; accanto, **G1 sulle stesse monete**;
* **il funding di dYdX** solo dal 20 ottobre 2026 in avanti (`aggiorna.funding_dydx`), salvato in `research/data/dydx_recente/` fuori da
  git;
* **i giorni dal 2 novembre 2026**, verdetto a 52 settimane (novembre 2027), come HLI: regge se lo Sharpe dell'anno è sopra quello di G1
  sulle stesse monete negli stessi giorni. Conta come conferma di HLI, non come prova nuova nel conto.

Fino ad allora è solo informazione: non entra nel bot.

## 17. Aggiunta del 1° novembre 2026: niente attese fisse

Il proprietario, 1° novembre 2026: «perché il 30 novembre? devo per forza aspettare un mese? [...] verdetto dopo 52 settimane? questo
è inaccettabile, cosa usiamo a fare il backtesting e demo se devo aspettare 52 settimane». Ha ragione: lo aveva già detto il 21 ottobre
(«si giudica sul passato di Binance, il paper è una conferma, non una condizione») e il 24 ottobre («usiamo i dati passati e simuliamo con
paper / live demo per qualche giorno, settimana, ma poi se funziona andiamo live»). Quindi, **da oggi e per tutte le misure in avanti di
questo file** (comprese quelle scritte prima con le 52 e le 104 settimane):
* **niente attese fisse**: le 26, 52 e 104 settimane non sono più condizioni; restano solo come date in cui si rifà il conto per informazione;
* **i numeri vanno al proprietario ogni settimana**, con il confronto con il passato e con G1 negli stessi giorni, detti chiari anche
  quando sono pochi («4 settimane non bastano a dire che funziona» si scrive, ma non blocca niente);
* **cosa decide**: quello che passa la regola del proprietario sul passato (sezione 1 del registro: Sharpe corretto da 0,90 in su, ogni
  anno positivo, t sopra 3) va subito in paper e sul demo; dopo qualche giorno o settimana di demo che esegue come il paper, **i soldi
  veri li decide il proprietario quando li chiede in modo esplicito** (regola di `CLAUDE.md`: `DRY_RUN` resta vero fino ad allora);
* le idee nate dai dati, che sul passato non si possono giudicare in modo pulito, vanno in paper (soldi finti) appena si può, e il
  proprietario decide quando ha visto abbastanza.

## 18. Aggiunta del 27 novembre 2026 (audit del 26 novembre): F5 con l'esposizione dimezzata quando il funding medio è molto negativo (idea 45), misura in avanti a tavolino

Scritta il 27 novembre 2026 (venerdì), prima di ogni settimana misurata. L'idea 45 del registro (`research/REGISTRO.md`, sezione 5) è
nata dal controllo descrittivo `research/programma6/PERDITE_F5.md` (punto 4): sulle 302 settimane dal 2021, quando il funding medio
dell'universo nei 7 giorni prima era molto negativo (il quinto più basso, sotto −11% l'anno: gli short affollati su tutto il mercato),
F5 faceva +0,25% a settimana, contro +1,16%, +0,67%, +1,12% e +2,10% negli altri quinti (61 settimane per quinto, circa 2 errori
standard: suggestivo, non dimostrato). È stata vista su tutti gli anni usati, quindi l'idea stessa diceva: **si prova solo in avanti**,
con la regola scritta prima. La regola è quella dell'idea 45, **senza cambiarla**:
* **la regola**: ogni lunedì, se il funding medio dei 7 giorni dell'universo di F5 è **sotto −11% l'anno**, F5 tiene la settimana con
  l'**esposizione dimezzata** (tutti i pesi, long e short, per 0,5; l'altra metà del capitale resta ferma); altrimenti F5 com'è;
* **il funding medio dei 7 giorni**: fra le monete dell'universo del lunedì che F5 ordina (le 100 della settimana con la volatilità dei
  30 giorni), la media della somma del funding dei 7 giorni di tenuta prima del lunedì. È lo stesso calcolo che il bot fa dal 25
  ottobre nei ribilanci dei paper (`funding_medio_7`, `bot/portafoglio/f5.py`, idea 48). In ragione d'anno si moltiplica per 365/7:
  la soglia è una somma dei 7 giorni sotto −0,211%;
* **le settimane**: dal **lunedì 30 novembre 2026**, la prima dopo questa nota; sulle settimane di prima nessun numero;
* **il conto, ogni settimana, a tavolino**: `research/programma6/paper/funding_medio.py`, dal pannello della ricerca, con la stima dal
  premio nei giorni ancora senza il funding vero, come il resto del paper (sezione 2). Per ogni settimana: F5 com'è (lo stesso codice
  del paper, `ventiquattresima.pesi_banda`) e F5 con la regola, con lo stesso conto (`terza.conto`: dentro ci sono le spese per
  dimezzare e per tornare pieni). Quando esce il funding vero si rifà tutto: conta il numero col funding vero. Risultati in
  `research/programma6/paper/funding_medio.json`;
* **cosa si guarda**: ogni settimana il funding medio, se la regola dimezza, F5 com'è e con la regola, la differenza e il totale dal 30
  novembre. Il confronto con il passato è quello di `PERDITE_F5.md` (+0,25% a settimana sotto la soglia). Nelle settimane sopra la
  soglia le due righe hanno gli stessi pesi: cambiano solo le spese (per tornare pieni dopo una settimana dimezzata);
* **chi decide**: come la sezione 17: niente attese fisse, i numeri al proprietario ogni settimana, detti chiari anche quando sono
  pochi; il proprietario decide quando ha visto abbastanza. Fino ad allora è solo informazione: non cambia F5 nel bot, sul demo né nel
  conto vero.

Perché a tavolino e non con il dato del bot: il `funding_medio_7` del bot sta su Firebase, che la ricerca non legge, e non arriva nello
stato della macchina; il pannello della ricerca permette lo stesso calcolo sui dati dell'archivio. L'idea 48 rimandava la misura di 8-12
settimane; con la sezione 17 (i numeri ogni settimana) si comincia subito.

## 19. Aggiunta del 27 novembre 2026 (audit del 26 novembre): chiusa la misura in avanti delle monete distribuite gratis (prova 113)

La prova 113 (N3G, `research/programma7/RISULTATI_CINQUANTUNESIMA.md`, «Esito e misura in avanti») aveva promesso una misura in avanti a
tavolino: ogni moneta nuova dei perpetui di Binance dal 22 ottobre 2026 etichettata «gratis» (HODLer Airdrops, Launchpool, Megadrop) o
no, e lo stesso conto rifatto con 30 eventi gratis nuovi. Non era mai stata scritta in questo file né calcolata (backlog P32). **Si
chiude oggi, senza numeri**, perché eventi possibili non ce ne sono:
* secondo `exchangeInfo` di Binance (`research/programma6/tipi_contratto.json`, aggiornato il 27 novembre 2026), dal 22 ottobre Binance
  non ha aperto nessun perpetuo in USDT su una moneta: l'ultimo è CTUSDT, del 1° ottobre. Dei 38 contratti aperti dal 1° ottobre, 36
  sono su azioni o fondi, uno è di pre-mercato (PREDICTUSDT) e uno è CTUSDT;
* già prima i perpetui nuovi su monete erano scesi (stesso file, solo i simboli ancora in elenco): da 9 a 31 al mese nel 2025, 15 a
  gennaio 2026, da 2 a 8 al mese da febbraio a settembre, 1 a ottobre, nessuno a novembre. A quel ritmo, e con le monete gratis che
  sono solo una parte delle nuove, i 30 eventi non arriverebbero mai.

La regola e il verdetto della prova 113 non cambiano («no»). La proposta di spostare la misura sulle monete nuove di un'altra borsa, con
le regole scritte prima, è nel backlog (`docs/backlog.md`). Se Binance torna a quotare perpetui su monete, la misura si riapre solo con
una nota nuova in questo file, con la data d'inizio di quel giorno.
