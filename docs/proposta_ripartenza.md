# Proposta: come ripartire per trovare strategie valide

**Seconda bozza, 18 ottobre 2026, da approvare.** Il proprietario ha deciso: «dobbiamo continuare fino a quando non trovi
delle strategie valide... se serve riscriviamo totalmente il gate». Questa proposta dice come, costruita su quello che
la storia del progetto ha misurato (`docs/storia/README.md`). La prima bozza (commit `fb4c074e`) è stata letta da due
revisori indipendenti, uno di metodo statistico e uno di trading e di codice: 32 rilievi, quasi tutti accolti; cosa è
cambiato e perché è in fondo (sezione 9). Ogni numero ha la sua fonte; dove è una stima, è scritto.

## 0. In una pagina

**La diagnosi.** In quattro mesi il sistema ha cercato quasi sempre la stessa cosa: indovinare la direzione del prezzo
dal grafico, con regole tecniche, a orizzonti brevi. Il vecchio gate ne provava circa 27.000 a giro (`ops/gate_fermo`),
la ricerca a protocollo circa 730 varianti in 24 campagne (`docs/storia/README.md`, sezione 1). Risultato: prima dei
costi gli ingressi fanno circa zero (−0,026 R a trade su 629, `ops/results/0622`), i costi stimati portano via 0,087 R a
trade (stessa fonte), e nessuna strategia ha superato il periodo chiuso. Il metodo d'esame invece regge: trova i
vantaggi inseriti apposta da 0,35 R in su, 88 su 88 (`research/collaudo_4/esiti.md`).

**La proposta, in quattro cambiamenti.**
1. **Cambiare il tipo di idee.** Prima di tutto il **carry**: tenere la moneta e vendere la stessa quantità sul
   perpetuo, e incassare il funding che i long a leva pagano agli short, senza scommettere sulla direzione. Poi i
   portafogli fra monete giudicati come portafogli. Il posizionamento (interesse aperto, rapporti long/short) solo se lo
   togli dal parcheggio e se i dati bastano.
2. **Il primo passo non è una ricerca, è una misura.** Il carry semplice (sempre aperto, regole fissate dalla
   letteratura, nessuna scelta) si misura su tutto lo storico, al netto di costi, margine, liquidazioni e rendimento dei
   dollari fermi. Senza scelte non c'è adattamento ai dati, quindi non consuma tentativi. Dice se vale la pena
   costruire il resto.
3. **Un esame nuovo, e la conferma sui dati che arrivano dopo.** Il periodo 2024-2026 è già stato aperto per altre idee
   e il modello conosce il mercato di quegli anni: diventa un filtro, aperto una sola volta per tutte le famiglie
   insieme. La conferma vera è sui dati in avanti, nel paper, con una durata calcolata prima e un tetto ai falsi
   positivi per tutto il programma.
4. **Un motore solo, in un servizio separato.** Ricerca e paper eseguono la stessa specifica con la stessa funzione; il
   paper dei portafogli gira in un processo suo, senza chiavi e senza codice per ordini veri, con un capitale suo, e non
   tocca il paper di oggi.

**Cosa ci si può aspettare, onestamente.**
* Il carry è un premio piccolo, non un moltiplicatore. Con il funding al suo valore di base su Binance (0,01% ogni 8
  ore: è la componente d'interesse della formula pubblica) fa circa l'11% l'anno sul **valore della posizione**
  (0,01% × 3 × 365), cioè **circa il 5,5-7% sul capitale** con la gamba corta a leva 1-2, **prima** dei costi (circa
  0,30% del valore per aprire e chiudere le due gambe: stima, da misurare) e **prima** del rendimento che gli stessi
  dollari avrebbero dati in prestito. Il premio vero è solo la parte di funding sopra la base, e nei mercati che scendono
  il funding va sotto zero.
* Il tempo vero non è la ricerca: sono gli strumenti (stima: **alcune settimane**, non giorni) e la conferma in avanti
  (per uno Sharpe di 2, circa un anno e mezzo di dati nuovi; sezione 3.6). Per questo la proposta distingue una
  strategia **in prova** (passa storia, filtro ed esame d'esecuzione, e gira nel paper) da una **confermata** (passa la
  conferma in avanti).

---

## 1. Perché (i numeri della storia)

| Cosa ha detto la storia | Il numero | Cosa ne segue |
|---|---|---|
| Gli ingressi tecnici non sanno la direzione | lordo −0,026 R su 629 trade (`ops` 0622); nessun vantaggio misurabile a 1, 4, 12, 24 ore (`docs/storia/03_ottobre.md`, sezione 3.4); ~730 varianti di ricerca, 0 oltre il periodo chiuso | non insistere su quel terreno |
| I costi decidono sotto l'ora | 0,05-0,14 R a giro a 30 minuti, 0,034 a 4 ore, 0,012 a 1 giorno (`docs/storia/05_ricerca_per_moneta_e_gruppo.md`, sezione 7.1); paper 0,087 R a trade (stimati dal modello, non misurati sui riempimenti: `ops` 0623) | orizzonti lunghi, pochi cambi |
| Lo stesso catalogo ridà le stesse idee | la ricerca su LINK ha riscritto quasi le stesse varianti di quella su BTC senza vederle (`docs/storia/06_ricerca_protocolli_2_4.md`, sezione 3.11) | cambiare famiglia, non moneta |
| Il vecchio gate sceglieva fortuna | dopo la scelta −0,05 R su 230 segnali e −0,03 R su 566 (`ops` 0532, 0619); profit factor promesso 2,02, vissuto 0,709 (`ops` 0623); sui prezzi rimescolati il doppio di promosse, indizio che la sua regola lasciava a «non si sa» (`ops` 0506) | niente più migliaia di candidate; confronto con il caso; correzione per i tentativi |
| L'esame dei protocolli funziona, nel suo campo | 88 vantaggi da 0,35 R su 88, 0 falsi su 90 (`research/collaudo_4/esiti.md`); non dice niente sotto 0,2 R né per i portafogli | collaudo nuovo, con una curva di potenza |
| Il bot non sa eseguire ciò che la ricerca prova | nessuna variante del catalogo dei protocolli 3 e 4 eseguibile così com'è (`research/config/bot_4.md`, sezione 3) | un motore solo |
| Il funding usato per indovinare la direzione è bruciato | il funding sotto zero comprato: tre edizioni, tre cadute; il funding estremo come segno d'affollamento: 19 campagne, 33 varianti, nessuna netta (`docs/storia/06_ricerca_protocolli_2_4.md`, sezione 3.11; `docs/storia/05_ricerca_per_moneta_e_gruppo.md`, sezione 3.F) | il funding si usa come premio da incassare, non come segnale |

## 2. Le famiglie, in ordine

Ogni famiglia ha un perché economico (chi paga, e perché dovrebbe continuare a pagare), una fonte pubblicata prima del
2024, un costo per giro calcolato prima e un **calcolo di potenza** prima di qualunque prova (sezione 3.6). Le varianti
precise le scrive la sessione di ricerca, come nei protocolli; qui c'è la direzione.

### A0. Il carry semplice, misurato (primo, non consuma tentativi)

* **Cosa.** Una regola fissata **prima** e senza parametri da scegliere: su ogni moneta che ha spot e perpetuo profondi
  (scelte data per data, con le monete poi tolte dal listino e con la conversione delle unità «1000»), tenere la moneta
  spot e vendere la stessa quantità sul perpetuo, leva della gamba corta 1, ribilanciamento a regola fissa, rabbocco del
  margine simulato (vendere spot e trasferire). Fonti: Christin, Routledge, Soska, Zetlin-Jones (2022), «The Crypto
  Carry Trade»; He, Manela, Ross, von Wachter (2022), «Fundamentals of Perpetual Futures»; Schmeling, Schrimpf, Todorov
  (2023), «Crypto Carry», documento di lavoro BIS 1087, che lega il carry all'alta domanda di leva e al rischio di crollo.
* **Su quale periodo.** Tutto lo storico disponibile, 2020-2026. Siccome non si sceglie niente, guardare anche il
  2024-2026 non adatta la regola ai dati; lo si dichiara comunque.
* **Cosa si riporta**: guadagno netto sul capitale rispetto al rendimento dei dollari fermi (fissato prima con una
  fonte); per semestre; negli episodi di crisi (marzo 2020, maggio 2021, maggio 2022, novembre 2022); perdita massima in
  una prova di stress scritta prima (salita violenta con la chiusura forzata della gamba corta al prezzo peggiore del
  giorno, la base che salta).
* **Cosa decide**: se il carry semplice non paga più dei dollari fermi al netto di tutto, la famiglia A si chiude qui e
  non si costruisce la gamba spot nel paper.

### A. Le varianti del carry (seconde: queste consumano tentativi)

* **Varianti possibili**: aprire solo quando il funding previsto supera i costi; ruotare fra monete; il carry sui
  **contratti trimestrali** USDT-M (rendimento noto all'ingresso, niente rischio di funding che cambia segno; l'archivio
  pubblico li ha, per esempio da BTCUSDT_210326 a BTCUSDT_270326).
* **Contro cosa**: il carry semplice di A0 e un carry con tempi d'ingresso casuali, con lo stesso tempo in posizione e lo
  stesso giro. Una variante vale solo se fa meglio del premio che c'è già.
* **Regole di sicurezza scritte prima**: leva massima 1-1,5; liquidazione calcolata sui massimi del mark price (che ha
  buchi: `docs/storia/05_ricerca_per_moneta_e_gruppo.md`, sezione 6); niente monete senza spot; un tetto alla
  dimensione per il rischio di tenere tutto su un exchange (FTX, novembre 2022).
* **Attenzione nota**: la rotazione verso il funding più alto sceglie proprio le monete più tirate, dove il funding può
  andare al pavimento negativo con regolazioni ogni ora (`docs/backlog.md`, voce C5).

### C. Portafogli fra monete, giudicati come portafogli (terza)

* **Cosa**: comprare le monete forti e vendere le deboli (o il contrario) togliendo l'esposizione a BTC, con
  ribilanciamento giornaliero o settimanale; oppure regolare l'esposizione di un paniere sulla sua volatilità. Fonti:
  Liu, Tsyvinski, Wu (2022), «Common Risk Factors in Cryptocurrency»; Moreira, Muir (2017), «Volatility-Managed
  Portfolios» (già proposta in `docs/backlog.md`, voce P6).
* **Già provato in parte**: il momentum fra monete trade per trade nel paniere (`docs/storia/06_ricerca_protocolli_2_4.md`,
  sezione 3.2) e i rendimenti al netto di BTC, in continuazione e in inversione (`docs/storia/05_ricerca_per_moneta_e_gruppo.md`,
  sezione 3.G): la ricerca riceve queste idee come già bruciate.
* **Trappole**: sui perpetui la gamba long paga il funding (circa l'11% l'anno sul valore al funding di base): un
  portafoglio che pende verso il long ha questo freno; le monete appena quotate tendono a perdere, ed è un effetto
  dell'età, non del segnale.

### B. Il posizionamento (ultima, e solo con un tuo sì)

* **È una voce che hai parcheggiato** il 23 settembre: lo storico di interesse aperto e long/short (`docs/backlog.md`,
  voce B6). Si prova solo se la togli dal parcheggio.
* **Cosa resta di nuovo**: solo l'interesse aperto e i rapporti long/short. Il funding estremo, il premio del perpetuo e
  lo squilibrio degli acquisti aggressivi sono già stati provati (`docs/storia/05_ricerca_per_moneta_e_gruppo.md`, sezioni
  3.E e 3.F) e vanno alla ricerca come idee bruciate.
* **I dati non bastano così com'è**: il file `metrics` c'è dal 1 settembre 2020 per BTCUSDT e dal 1 dicembre 2021 per
  le altre monete (archivio pubblico, controllato il 18 ottobre). Con la costruzione fino al 2022 sono **13 mesi**, tutti
  nel ribasso del 2022: si vedrebbero solo Sharpe sopra 2. La famiglia resta solo in una di queste forme: una regola unica
  su 30 o più monete quotate prima di dicembre 2021 (un fattore fra monete); solo BTC dal 2020; solo in avanti,
  registrando i dati da adesso.
* **Trappole dei file** (viste dai revisori): righe doppie nel 2020; righe non in ordine di orario e formato dei numeri
  cambiato nei file recenti; un file dal nome sbagliato; pubblicazione con circa un giorno di ritardo; l'interfaccia in
  tempo reale tiene solo 30 giorni, quindi il paper userebbe un'altra fonte; non è detto se l'orario indica l'inizio o la
  fine dei 5 minuti. Il caricatore esiste già (`backtesting/metrics_loader.py`, dal 20 settembre) e va riusato.
* **Manca ancora una fonte pubblicata** prima del 2024 sul meccanismo: senza, la famiglia non si apre.

### Fuori da questa proposta

Notizie e dati di altri exchange (`docs/backlog.md`, voci B5 e B7, parcheggiate): si riprendono solo se A, C e B non
danno niente.

## 3. L'esame nuovo

Il vecchio gate (generazione a caso, giro ogni 3 ore, supervisore che ritocca le soglie) non si riaccende: il codice resta
nel repository, il registro è archiviato (`ops/results/archivio_20261018/`).

### 3.1 Le unità e il confronto giusto per ogni famiglia

| Famiglia | Si misura | Contro cosa |
|---|---|---|
| A0 | guadagno netto giornaliero sul capitale | rendimento dei dollari fermi |
| A (varianti) | guadagno netto in più rispetto al carry semplice | carry semplice e carry con ingressi casuali allo stesso tempo in posizione e allo stesso giro |
| C | guadagno netto giornaliero del portafoglio | portafogli casuali con lo stesso numero di monete e lo stesso giro, pareggiati su esposizione a BTC (il beta), volatilità ed età delle monete; oppure una regressione su BTC, sul paniere e su un fattore di dimensione |
| B | guadagno netto dei trade o del fattore | segnali casuali ottenuti spostando in blocco il calendario dei segnali (conserva il fatto che l'affollamento arriva su molte monete insieme), con errori a blocchi |

Per tutte: il **guadagno in più sulle alternative semplici**, misurato come intercetta della regressione dei guadagni
giornalieri (oltre i dollari fermi) su quattro confronti costruiti con gli stessi strumenti e con i loro costi: BTC spot;
BTC long sul perpetuo, che paga il funding; un paniere a pesi uguali con le monete valide data per data, comprese quelle
poi tolte dal listino, ribilanciato ogni settimana; i dollari fermi. Per le famiglie dichiarate senza direzione, il beta
verso BTC deve stare sotto 0,1 in valore assoluto. Il confronto degli indici di Sharpe si riporta solo come
informazione: una strategia senza direzione con Sharpe 0,8 migliora un portafoglio di BTC anche se non batte BTC.

### 3.2 I periodi

* **Costruzione**: dall'inizio dei dati al 2022. **Validazione**: 2023. Qui si sceglie; qui non si spende il budget dei
  falsi positivi.
* **Filtro dichiarato contaminato**: dal 1 gennaio 2024 al 30 settembre 2026. È già stato aperto per altre idee su BTC,
  BNB, ADA, ETH, SOL, XRP, DOGE, APT, LTC, MATIC e BCH (`research/vault/`, `research/altre_monete_3/`), e il modello
  conosce il mercato di quegli anni. **Si apre una volta sola per tutte le famiglie insieme**: prima si consegnano tutte,
  con candidati e regole congelati con l'impronta, poi si apre con la tua frase. Serve a scartare, non a confermare.
* **Conferma**: i dati che arrivano **dopo** il congelamento delle regole, nel paper. È l'unico periodo pulito.
* **La sessione di ricerca non legge** questa proposta, la storia del progetto né i file del periodo chiuso: riceve solo
  l'elenco delle idee bruciate e le regole di metodo, su un branch con una storia propria, come nel protocollo 4.

### 3.3 Il tetto ai falsi positivi

* **Il budget**: al massimo il 5% di probabilità che una strategia senza vantaggio arrivi a «confermata», su tutto il
  programma. La prima famiglia che arriva alla conferma ne ha metà, la seconda un quarto, e così via: ogni famiglia nuova
  ha un esame più severo. Una famiglia bocciata non si ritocca; una «seconda versione» è una famiglia nuova e consuma
  budget. Il programma non riparte con un budget nuovo.
* **Dove si spende**: solo nella conferma in avanti.
* **Dentro una famiglia**: il numero di candidati si fissa prima; si giudicano con il metodo di Holm o, meglio, con un
  test sul massimo che tiene conto della somiglianza fra candidati (Romano-Wolf o il test di Hansen, con bootstrap a
  blocchi).
* **Cosa si respinge**: «nessun guadagno in più sul confronto della famiglia» (tabella 3.1), non «nessun guadagno». Il
  carry semplice guadagna per costruzione: passarlo non è una scoperta.
* **Perché cambia rispetto al protocollo 4** (che usava il 10% con il metodo di Benjamini-Hochberg sul periodo chiuso):
  qui si continua «finché non si trova», quindi serve un limite che valga per tutte le famiglie insieme, e la probabilità
  di sbagliare almeno una volta (Bonferroni nel tempo) è quella giusta.

### 3.4 Le statistiche

* **Errori corretti per la dipendenza fra i giorni**: Newey-West o bootstrap a blocchi di almeno un mese. Lo Sharpe di
  una strategia con guadagni giornalieri correlati (il carry, le posizioni tenute più giorni) può risultare gonfiato
  fino a circa il 65% (Lo, 2002, «The Statistics of Sharpe Ratios»); i regimi del funding durano mesi.
* **Un pavimento all'errore** per le serie di molti piccoli guadagni senza perdite, come nel primo protocollo
  (`research/PROTOCOLLO.md`, riga 256).
* **Effetti attesi dimezzati** rispetto a quelli pubblicati, perché dopo la pubblicazione un effetto si riduce in media
  di circa la metà (McLean, Pontiff, 2016, «Does Academic Research Destroy Stock Return Predictability?»).

### 3.5 Le soglie

Si fissano allo STOP degli strumenti, con il collaudo davanti, e le approvi tu. Principi già decisi:
* **una regola di dimensione fissata prima** (una volatilità obiettivo per i portafogli, un rischio per trade per le
  regole di trade), così le soglie non si passano cambiando la size;
* per le regole di trade resta la difesa che ha funzionato ogni volta: **vantaggio netto almeno pari a un multiplo del
  costo di un giro**, e positivo anche **a costi doppi**;
* per il carry: guadagno netto sopra i dollari fermi, **perdita massima nelle prove di stress** sotto un tetto scritto
  prima (per un libro senza direzione, 5-10% del capitale), contributo a un portafoglio con BTC;
* la caduta massima si misura rispetto alla volatilità obiettivo, non in assoluto;
* costi del 2020-2022 stimati dal modello del 2023 per un moltiplicatore prudente scritto prima (lo scarto di prezzo del
  2023 è ottimista per il 2020-2021: `docs/storia/README.md`, sezione 5, punto 2); risultati sempre anche a costi doppi.

### 3.6 La potenza, prima di provare

Per ogni famiglia si calcola, prima, il guadagno più piccolo che i dati possono vedere; **se la potenza sull'effetto atteso
(dimezzato) è sotto il 50%, la famiglia non si apre**. Un'idea dell'ordine di grandezza, con un solo candidato, il 5%
d'errore e l'80% di potenza (calcolo del revisore di metodo, con l'errore dello Sharpe circa 1 diviso la radice degli
anni, senza la correzione per la dipendenza, che lo allunga):

| Sharpe vero | Anni di dati nuovi per confermarlo |
|---|---|
| 3 | circa 0,7 |
| 2 | circa 1,6 |
| 1,5 | circa 2,75 |

Con le quote del budget per famiglia (metà, un quarto...) e con più candidati, i tempi crescono. È il motivo della
distinzione fra «in prova» e «confermata»: una strategia può girare nel paper mentre si accumula la conferma.

### 3.7 Il collaudo, anche per l'esame nuovo

Prima di qualunque ricerca, come nei protocolli 3 e 4, ma con una **curva di potenza**: quante volte l'esame trova
vantaggi inseriti di Sharpe 1, 1,5 e 2, e quante volte passa senza vantaggio. Per C: dati in cui si gira il segno di
tutte le monete nello stesso giorno (conserva il fatto che si muovono insieme). Per B: il segnale spostato dai prezzi di
un ritardo casuale. Per A: funding riportato a media zero.

### 3.8 Il paper: due esami diversi

* **Esame d'esecuzione, 60-90 giorni.** Il paper deve fare quello che fa il motore della ricerca rigiocato sugli stessi
  giorni: con gli stessi dati in ingresso, risultati identici al 100%; fra i dati dell'archivio e quelli in tempo reale,
  differenza del guadagno giornaliero al massimo dello 0,02% del capitale nel 95% dei giorni e decisioni uguali nel 98%;
  funding incassato entro ±5% del modello; costi misurati contro costi stimati. Si legge a una data fissata, con lo
  strumento scritto prima.
* **Conferma.** Durata fissata prima dal calcolo di potenza; letture ogni 3 mesi con confini decisi prima che spendono il
  budget poco alla volta (metodo di O'Brien-Fleming o di Lan-DeMets: si può dichiarare «confermata» prima solo se il
  risultato è molto forte); una regola d'uscita scritta prima (per esempio, caduta oltre 1,5 volte quella prevista).
* `DRY_RUN` resta vero. I soldi veri, solo per una strategia confermata e solo su tua richiesta esplicita e ripetuta.

## 4. Un motore solo, in un servizio separato

* **Le strategie come specifiche**: un file dice cosa tenere di ogni moneta; una sola funzione «pura» (senza file e senza
  rete, come `research/src/motore3.py`) la esegue nella ricerca e nel paper. Fra giugno e agosto quasi ogni differenza
  fra gate e paper veniva da due motori diversi (`docs/storia/01_origini_e_sistema.md`, sezione 7.1).
* **Il funding per regolazione, con l'intervallo vero**: dall'archivio per la ricerca, dalle interfacce pubbliche di
  Binance per il paper. Oggi il bot lo calcola in modo continuo, come se l'intervallo fosse sempre di 8 ore e con il
  tasso letto all'ingresso (`bot/core/costs.py`, righe 27-39; `bot/execution/executor.py`, righe 1121-1125): sulle monete a
  4 ore conta metà del funding vero, su quelle a 1 ora un ottavo. Per il paper di oggi pesa poco, per il carry è la voce di
  guadagno. Va sistemato nel motore nuovo, prima del carry.
* **Un servizio separato sulla macchina**: un processo suo per il paper dei portafogli, **senza `.env` e senza codice per
  ordini veri** (non un interruttore spento: il codice non c'è), con un capitale suo, uno spazio suo in Firebase (per
  esempio `/portafoglio`), i prezzi letti in sola lettura e una pagina in dashboard. Il bot di oggi non si tocca: ha una
  posizione per moneta, un capitale solo, stop e target obbligatori e un'uscita forzata dopo 96 candele
  (`bot/execution/executor.py`, `bot/risk/risk_manager.py`), cose incompatibili con un portafoglio a due gambe.
* **Servono interventi tuoi sulla macchina**: il nuovo servizio e le sue voci nella lista bianca, che vive solo lì.
* **I costi misurati**: commissioni vere di spot e futures (da confermare sulle pagine ufficiali), scarto fra denaro e
  lettera stimato dagli scambi (`aggTrades`, per tutti gli anni e tutti e due i mercati), e registrato dal vivo da adesso
  (serve il tuo sì: «registrare noi lo storico», voce B7, è parcheggiata). La profondità del libro (`bookDepth`, solo
  futures, dal 2023) serve solo per la capacità, se il capitale crescesse.

## 5. Il piano, a passi con uno STOP ciascuno

| Passo | Cosa | Chi | Fine del passo |
|---|---|---|---|
| 0 | Le decisioni di questa proposta | tu | sì, no o modifiche |
| 1 | Motore puro con funding per regolazione, margine, liquidazione e prove di stress; caricatori di spot, perpetuo, funding e trimestrali; **misura del carry semplice (A0)** | il coordinamento | STOP: il carry semplice paga più dei dollari fermi, al netto di tutto? |
| 2 | Se sì: esame nuovo per A, collaudo con la curva di potenza, servizio del paper dei portafogli con l'esame d'esecuzione pronto | il coordinamento | STOP: esiti del collaudo, soglie da approvare |
| 3 | Famiglia A (varianti del carry): costruzione e validazione | una sessione di ricerca | STOP |
| 4 | Famiglia C, con i suoi strumenti costruiti solo adesso | coordinamento e una sessione di ricerca | STOP |
| 5 | Famiglia B, solo se l'hai tolta dal parcheggio e la potenza basta | coordinamento e una sessione di ricerca | STOP |
| 6 | Filtro 2024-2026, una volta per tutte le famiglie consegnate, con la tua frase | il coordinamento | STOP |
| 7 | Paper: esame d'esecuzione, poi conferma con letture trimestrali | il servizio dei portafogli | regole scritte prima |

Ogni passo si chiude con le sue lezioni nel diario e nella storia. Se A0 dice di no, si salta ad A-C senza gamba spot (i
portafogli fra monete non la richiedono). Durante tutto il piano il paper di oggi resta acceso come banco di misura
dell'esecuzione, e la misura degli ordini limite si legge a una data fissata (`docs/backlog.md`, voce P12).

## 6. Cosa non si rifà (dalla storia)

* Migliaia di candidate generate a caso e scelte sul massimo (`docs/storia/README.md`, sezione 5, punto 4).
* Imparare dal paper: varianti dai referti, figlie, selettore, pesi (punto 3).
* Lavorare su uscite, trailing, freni e size per creare un vantaggio che all'ingresso non c'è (sezione 3.1).
* Cambiare regole o soglie mentre si misura; una macchina che ritocca le soglie da sola (punto 14).
* Tante cose nuove insieme: per questo il Passo 1 costruisce solo ciò che serve al carry (punto 18).
* Un periodo usato due volte; più tentativi per «riempire» un limite (punti 3 e 17).

## 7. Le decisioni che servono

| N. | Decisione | Proposta |
|---|---|---|
| 1 | L'ordine | misura del carry semplice; varianti del carry; portafogli fra monete; posizionamento per ultimo |
| 2 | Il posizionamento (lo storico di interesse aperto e long/short, parcheggiato il 23 settembre) | resta parcheggiato per ora; se ne riparla dopo A e C |
| 3 | La gamba spot | sì, nel paper, in un servizio separato senza chiavi e senza codice per ordini veri |
| 4 | Registrare da adesso lo scarto fra denaro e lettera di spot e futures (oggi parcheggiato) | sì, serve a misurare i costi veri |
| 5 | Il vecchio gate | spento per sempre (codice e registro restano archiviati) |
| 6 | Il paper di oggi | acceso come banco di misura, senza toccarlo |
| 7 | I periodi | costruzione fino al 2022; validazione 2023; filtro 2024-2026 una volta sola per tutte le famiglie, con la tua frase; conferma sui dati in avanti |
| 8 | Il tetto ai falsi positivi | 5% su tutto il programma, speso solo nella conferma: metà alla prima famiglia, un quarto alla seconda... |
| 9 | Cosa chiamiamo «strategia valida» | «in prova»: passa storia, filtro ed esame d'esecuzione, gira nel paper; «confermata»: passa la conferma in avanti. Soldi veri solo per una confermata, solo su tua richiesta |
| 10 | La delega e i branch | come nel protocollo 4: il coordinamento va avanti da solo con i passi e ti informa; il filtro 2024-2026 si apre solo con la tua frase; i branch di ricerca delle famiglie (per esempio `research/campagna/CARRY`) rientrano nell'eccezione dei branch di ricerca |

## 8. Cosa serve sulla macchina (per quando arriva il Passo 2)

Un servizio nuovo per il paper dei portafogli e due o tre voci nuove nella lista bianca (lettura dello stato del
servizio, esame d'esecuzione). Le istruzioni esatte arrivano con lo STOP del Passo 2.

## 9. Cosa è cambiato dalla prima bozza, e perché

| Rilievo dei revisori | Cosa è cambiato |
|---|---|
| Il periodo 2024-2026 è già aperto, conosciuto dal modello, e «una volta per famiglia» lo riaprirebbe tre volte | diventa un filtro aperto una volta sola per tutte le famiglie; la conferma è sui dati in avanti |
| Sessanta giorni di paper non hanno potenza (errore dello Sharpe circa 2,5) | due esami: d'esecuzione (60-90 giorni) e conferma con durata dalla potenza e letture a confini fissati |
| L'11% era sul valore della posizione, non sul capitale, e prima del rendimento dei dollari fermi | scritto 5,5-7% sul capitale prima dei costi; confronto con i dollari fermi |
| Il carry semplice è un premio noto: confrontarlo con zero non è una scoperta | misurato senza tentativi (A0); consumano budget solo le varianti, contro il carry semplice |
| I rischi di coda (liquidazione, chiusure forzate dell'exchange, monete tolte dal listino, fallimento dell'exchange) non li vedeva nessuno strumento | prove di stress scritte prima, leva massima 1-1,5, liquidazione sui massimi del mark, tetto per l'exchange |
| Il bot calcola il funding in modo continuo a 8 ore con il tasso d'ingresso | funding per regolazione con l'intervallo vero nel motore nuovo |
| Molte monete con funding estremo non hanno lo spot su Binance | solo monete con spot e perpetuo, scelte data per data |
| Il posizionamento è una voce parcheggiata, tre dati su cinque sono idee bruciate, 13 mesi di costruzione | ultimo, solo con il tuo sì, solo interesse aperto e long/short, solo con potenza sufficiente |
| Anche i portafogli fra monete sono stati provati in parte | dichiarato; idee bruciate passate alla ricerca; confronto pareggiato su beta, volatilità, età |
| Il budget non diceva dove si spende, cosa succede con più candidati, contro cosa si respinge | sezione 3.3 |
| La potenza era solo un principio | tabella della durata (3.6), errori corretti per la dipendenza, effetti attesi dimezzati |
| Il confronto «a parità di rischio con BTC» non era definito e boccerebbe le strategie senza direzione | regressione su quattro confronti costruiti con gli stessi strumenti; Sharpe solo informativo |
| Il motore «accanto al bot, senza toccarlo» non sta nel bot di oggi | servizio separato, senza chiavi, con capitale e spazio suoi |
| La prova di parità al 98% su 12 mesi era o banale o mirata male | due prove: identità sul rigioco degli stessi dati, e archivio contro tempo reale sugli stessi giorni |
| Il Passo 1 metteva troppe cose nuove insieme | diviso: prima solo ciò che serve a misurare il carry, poi il resto dopo ogni STOP |
| Il dato dei prezzi rimescolati (16 contro 8) per la sua regola era «non si sa» | citato come indizio, anche nella storia |
