# Proposta: come ripartire per trovare strategie valide

**Bozza del 18 ottobre 2026, da approvare.** Il proprietario ha deciso: «dobbiamo continuare fino a quando non trovi
delle strategie valide... se serve riscriviamo totalmente il gate». Questa proposta dice come, costruita su quello che
la storia del progetto ha misurato (`docs/storia/README.md`). Ogni numero ha la sua fonte; dove è una stima, è scritto.

## 0. In una pagina

**La diagnosi.** In quattro mesi il sistema ha cercato quasi sempre la stessa cosa: indovinare la direzione del prezzo
dal grafico, con regole tecniche, a orizzonti brevi. Il vecchio gate ne provava 27.000 a giro (`ops/gate_fermo`), la
ricerca a protocollo circa 730 varianti in 24 campagne (`docs/storia/README.md`, sezione 1). Risultato: gli ingressi non
sanno la direzione (lordo −0,026 R a trade, `ops/results/0622`), i costi si mangiano tutto (0,087 R a trade, stessa
fonte), nessuna strategia ha superato il periodo chiuso. Il metodo d'esame invece funziona: trova i vantaggi inseriti
apposta, 88 su 88 (`research/collaudo_4/esiti.md`).

**La proposta, in tre cambiamenti.**
1. **Cambiare il tipo di idee.** Smettere di cercare la direzione nel grafico e cercare due cose che il sistema non ha
   mai usato: un **premio pagato per un servizio** (il carry del funding: tenere la moneta e vendere il perpetuo, e
   incassare il pagamento che i long a leva fanno agli short, senza scommettere sulla direzione) e il
   **posizionamento del mercato** (interesse aperto, rapporti long/short, acquisti aggressivi, premio del perpetuo
   sullo spot: dati che Binance pubblica e che non abbiamo mai letto). In terza fila, i portafogli fra monete a mercato
   neutro, giudicati come portafogli.
2. **Un gate nuovo, fatto come il protocollo.** Poche ipotesi scritte prima, un esame tarato con il collaudo, un tetto
   ai falsi positivi per **tutto il programma** (più famiglie si provano, più severo diventa l'esame per la successiva),
   un periodo di prova usato una volta per famiglia, il paper come esame finale con la regola scritta prima. Il vecchio
   gate si spegne per sempre.
3. **Un solo motore.** La ricerca, il paper e i soldi veri eseguono la stessa specifica con lo stesso codice, e il bot
   impara a tenere un portafoglio (più posizioni bilanciate, anche una gamba spot), oltre ai trade singoli.

**In più, una regola che finora mancava:** una strategia vale solo se batte, dopo i costi e a parità di rischio, le
alternative semplici che chiunque potrebbe scegliere: tenere BTC, tenere un paniere di monete a pesi uguali, stare
fermi. Nello stesso periodo del paper BTC ha fatto +7,94% e il paper −17,44% (`ops/results/0623`).

**Cosa ci si può aspettare, onestamente.** Il carry è un premio piccolo e stabile, non un moltiplicatore: con il funding
al suo valore di base su Binance (0,01% ogni 8 ore, la componente d'interesse della formula pubblica) vale circa l'11%
lordo l'anno sul capitale della gamba (calcolo: 0,01% × 3 × 365), meno nei mercati che scendono, quando il funding va
sotto zero. Il posizionamento può dare di più, ma non sappiamo se c'è: è proprio quello che l'esame deve dire. Il
tempo vero non è la ricerca (la campagna su LINK ha richiesto circa 17 minuti di lavoro della sessione,
`research/campagne/LINK6/lezioni.md`), sono gli strumenti nuovi (alcuni giorni) e il paper (mesi).

---

## 1. Perché proprio questo (i numeri della storia)

| Cosa ha detto la storia | Il numero | Cosa ne segue |
|---|---|---|
| Gli ingressi tecnici non sanno la direzione | lordo −0,026 R su 629 trade (`ops` 0622); nessun vantaggio a 1, 4, 12, 24 ore (`docs/storia/03_ottobre.md`, sezione 3.4); ~730 varianti di ricerca, 0 oltre il periodo chiuso | non insistere su quel terreno; serve informazione nuova |
| I costi decidono sotto l'ora | 0,05-0,14 R a giro a 30 minuti, 0,034 a 4 ore, 0,012 a 1 giorno (`docs/storia/05_ricerca_per_moneta_e_gruppo.md`, sezione 7.1); paper 0,087 R a trade | orizzonti di giorni, pochi cambi di posizione |
| Lo stesso catalogo ridà le stesse idee | la ricerca su LINK ha riscritto quasi le stesse varianti di quella su BTC senza vederle (`docs/storia/06_ricerca_protocolli_2_4.md`, sezione 3.11) | cambiare la famiglia, non la moneta |
| Il vecchio gate selezionava fortuna | promosse 16 strategie su 7.200 sui prezzi rimescolati contro 8 su quelli veri (`ops` 0506); promessa 2,02 di profit factor, vissuto 0,709 (`ops` 0623) | niente più migliaia di candidate a caso; confronto con il caso e correzione per i tentativi |
| Il metodo d'esame funziona | 88 vantaggi inseriti su 88 trovati, 0 falsi su 90 (`research/collaudo_4/esiti.md`) | tenerlo, e collaudarlo anche per i portafogli |
| Il bot non sa eseguire ciò che la ricerca prova | nessuna variante del catalogo dei protocolli 3 e 4 eseguibile così com'è (`research/config/bot_4.md`, sezione 3) | un solo motore per ricerca e bot |
| Il funding sotto zero, comprato, è tornato tre volte e tre volte è caduto | la famiglia migliore in costruzione su BTC e LINK, caduta nel periodo chiuso e sulle altre monete (`docs/storia/06_ricerca_protocolli_2_4.md`, sezione 3.11) | il funding usato per indovinare la direzione è bruciato; usarlo come premio da incassare è un'altra idea |

## 2. Le famiglie di idee, in ordine

Ogni famiglia ha un **perché economico** (chi paga, e perché dovrebbe continuare a pagare), una fonte pubblicata prima
del 2024 e un costo per giro calcolato prima dei test. Le ipotesi precise, con i loro valori, le scrive la ricerca al
Passo 1 della famiglia, come nei protocolli; qui c'è solo la direzione.

### A. Il carry del funding, a mercato neutro (prima)

* **Meccanismo.** Quando il perpetuo vale più dello spot, chi è long sul perpetuo paga il funding a chi è short, ogni 8
  ore. Chi tiene la moneta spot e vende la stessa quantità sul perpetuo non guadagna né perde con la direzione, e incassa
  il funding. È il prezzo che i long a leva pagano per la leva.
* **Fonti.** Christin, Routledge, Soska, Zetlin-Jones (2022), «The Crypto Carry Trade»; He, Manela, Ross, von Wachter
  (2022), «Fundamentals of Perpetual Futures»: tutti e due documentano che la differenza fra perpetuo e spot è stata
  grande e persistente.
* **Varianti possibili** (le sceglie la ricerca): sempre aperto sulle monete più liquide; aperto solo quando il funding
  previsto supera i costi; rotazione verso le monete col funding più alto; chiusura quando va sotto zero.
* **Rischi da misurare.** Il funding che cambia segno nei ribassi; la differenza fra il prezzo spot e quello del
  perpetuo all'apertura e alla chiusura; la liquidazione della gamba short se la moneta sale molto e il margine non
  basta; il rischio di tenere tutto su un solo exchange. **Costo**: commissioni su due gambe e due mercati, da
  misurare per moneta.
* **Cosa richiede al bot**: una gamba spot (oggi il bot opera solo futures).

### B. Il posizionamento del mercato (seconda)

* **Meccanismo.** Quando il mercato è affollato da una parte (interesse aperto che cresce, rapporti long/short estremi,
  funding alto, premio del perpetuo alto), una mossa contraria costringe molti a chiudere insieme e la mossa si allunga
  (le cascate di liquidazioni). È informazione sul **chi** è nel mercato, non sul disegno del prezzo.
* **Dati.** Il file `metrics` di Binance: interesse aperto, rapporto long/short dei conti grandi e di tutti, rapporto fra
  acquisti e vendite aggressive, ogni 5 minuti; c'è dal 1 settembre 2020 per BTCUSDT e dal 1 dicembre 2021 per ETH, LINK
  e DOGE (controllato oggi sull'archivio pubblico). Il premio del perpetuo sullo spot (`premiumIndexKlines`) ogni ora dal
  gennaio 2020. **Limite**: per quasi tutte le monete la storia del posizionamento comincia a dicembre 2021, quindi la
  costruzione è più corta (due anni invece di quattro). Le liquidazioni non sono nell'archivio per questi contratti.
* **Orizzonte**: da 1 a 7 giorni, per tenere i costi bassi in R.

### C. Portafogli fra monete a mercato neutro (terza)

* **Meccanismo.** Comprare le monete forti e vendere le deboli (o il contrario), togliendo l'esposizione a BTC, con
  ribilanciamento giornaliero o settimanale. **Fonte**: Liu, Tsyvinski, Wu (2022), «Common Risk Factors in
  Cryptocurrency», Journal of Finance.
* **Prima di provarla**: il paniere a barre giornaliere ha già provato il momentum fra monete, giudicato trade per trade,
  e non ha passato (`docs/storia/06_ricerca_protocolli_2_4.md`, sezione 3.2). Qui il giudizio è sul portafoglio intero,
  che è un'altra cosa, ma la famiglia parte con un'indicazione contraria: per questo è terza.

### D. Fuori da questa proposta

Le idee che chiedono dati che non abbiamo (notizie, quotazioni nuove, sblocchi dei token, dati di altri exchange): le ha
parcheggiate il proprietario il 23 settembre (`docs/backlog.md`, voci B5, B6, B7). Si riprendono solo se le famiglie A, B
e C non danno niente.

## 3. Il gate nuovo

È il metodo del protocollo, reso permanente e allargato ai portafogli. Il vecchio gate (generazione a caso, giro ogni 3
ore, supervisore che ritocca le soglie) non si riaccende: il suo codice resta nel repository, il suo registro è già
archiviato (`ops/results/archivio_20261018/`).

1. **Unità d'esame**: una regola di trade o una regola di portafoglio. Per tutte e due si misura la curva dei guadagni
   giorno per giorno, dopo i costi.
2. **Il confronto con il caso**: per i trade, le entrate casuali con le stesse uscite e la stessa larghezza di stop
   (come nei protocolli 3 e 4); per i portafogli, portafogli casuali con lo stesso numero di monete, lo stesso giro di
   posizioni e la stessa esposizione al mercato. Più il confronto con tenere BTC, tenere il paniere e stare fermi.
3. **I periodi**: costruzione dal 2020 (o dall'inizio dei dati) al 2022; validazione 2023; prova finale dal 1 gennaio
   2024 al 30 settembre 2026, **una volta per famiglia**, aperta solo con una frase del proprietario; poi il paper, su
   dati che nessuno ha visto. Va detto chiaro: il periodo 2024-2026 è già stato aperto per altre idee su alcune monete, e
   il modello conosce il mercato di quegli anni. Per questo la prova finale vera resta il paper.
4. **Il tetto ai falsi positivi su tutto il programma.** Se si continua «finché non si trova», prima o poi una strategia
   passa per fortuna. Per evitarlo, il programma ha un budget fisso: al massimo il 5% di probabilità che una strategia
   senza vantaggio arrivi al paper, su tutte le famiglie insieme. La prima famiglia ne usa metà, la seconda un quarto, e
   così via: ogni famiglia nuova ha un esame più severo della precedente.
5. **Prima di provare, la potenza.** Per ogni famiglia si calcola, prima dei test, il vantaggio più piccolo che i dati
   possono vedere. Esempio del perché: per una strategia giudicata sui guadagni di ogni giorno, l'errore sulla stima
   dell'indice di Sharpe è circa 1 diviso la radice degli anni (Lo, 2002, «The Statistics of Sharpe Ratios»), cioè circa
   1 su un anno di validazione e circa 0,6 sui 2,75 anni della prova finale. Una strategia con Sharpe 1 in un anno non si
   distingue da zero. Se una famiglia non può essere vista con i dati che ci sono, non si prova (e non si consuma il
   periodo di prova).
6. **Il collaudo, anche per i portafogli**: le prove A (dati senza direzione: nessun portafoglio deve passare più del
   dovuto) e B (vantaggi inseriti apposta: devono essere trovati) rifatte per il nuovo esame, prima di qualunque ricerca.
7. **Le soglie dell'esame**: si fissano allo STOP degli strumenti, con il collaudo davanti, e le approva il proprietario.
   Proposta di partenza, da confermare con il collaudo: dopo i costi, guadagno positivo in costruzione, validazione e
   prova finale; nella prova finale indice di Sharpe almeno 1,2 (circa 2 errori standard su 2,75 anni) e meglio di tenere
   BTC e il paniere a parità di rischio; caduta massima sotto il 25% del capitale della strategia.
8. **Il paper come esame finale**: almeno 60 giorni, con la regola di promozione scritta prima (per esempio: guadagno
   dopo i costi dentro l'intervallo previsto dalla prova finale). I soldi veri restano esclusi: `DRY_RUN` resta vero
   finché il proprietario non lo chiede in modo esplicito e ripetuto.

## 4. Un solo motore

* **Le strategie come specifiche.** Una strategia è un file che dice cosa fare (entrare, uscire, quanto tenere di ogni
  moneta), e una sola funzione la esegue: la stessa nella ricerca, nel paper e, un giorno, con i soldi veri. Fra giugno e
  agosto quasi ogni differenza fra gate e paper veniva da due motori diversi (`docs/storia/01_origini_e_sistema.md`,
  sezione 7.1): così non può succedere per costruzione.
* **Il bot che tiene un portafoglio**: posizioni obiettivo per moneta, ribilanciamento all'ora o al giorno stabiliti,
  una gamba spot simulata nel paper per il carry. Si aggiunge accanto al motore dei trade di oggi, senza toccarlo.
* **La prova di parità** (la prova C dei protocolli, mai fatta): 12 mesi rigiocati dal motore della ricerca e dal
  simulatore del paper devono dare gli stessi ordini almeno nel 98% dei casi.
* **I costi misurati per moneta** (voce C5 del backlog, approvata il 2 ottobre e mai fatta): commissioni vere di spot e
  futures e lo scarto di prezzo misurato sul libro degli ordini (l'archivio pubblico ne ha la profondità dal 1 gennaio
  2023).

## 5. Il piano, a passi con uno STOP ciascuno

| Passo | Cosa | Chi | Fine del passo |
|---|---|---|---|
| 0 | Le decisioni di questa proposta | il proprietario | sì, no o modifiche |
| 1 | Dati nuovi (posizionamento, premio, spot) con impronte; motore unico per trade e portafogli; esame per i portafogli; collaudo A, B e C | il coordinamento | STOP con gli esiti del collaudo e le soglie da approvare |
| 2 | Famiglia A (carry): ipotesi scritte prima, costruzione, validazione; poi la prova finale con la frase del proprietario | una sessione di ricerca, come nei protocolli | STOP con l'esito |
| 3 | Famiglia B (posizionamento), con l'esame più severo | una sessione di ricerca | STOP con l'esito |
| 4 | Famiglia C (portafogli fra monete) | una sessione di ricerca | STOP con l'esito |
| 5 | Paper di ciò che passa, appena passa (le altre famiglie vanno avanti) | il bot | regola di promozione |
| dopo | Lezioni di ogni famiglia; se nessuna passa, si torna alle idee parcheggiate (sezione 2.D) con il budget rimasto | il coordinamento | — |

Durante i passi 1-4 il paper di oggi resta acceso sulle 249 coppie del vecchio gate, come banco di misura
dell'esecuzione e degli ordini limite (la misura degli ordini limite va finalmente letta: `docs/backlog.md`, voce P12),
e si spegne quando il motore nuovo è pronto.

## 6. Cosa non si rifà (dalla storia)

* Migliaia di candidate generate a caso e scelte sul massimo (`docs/storia/README.md`, sezione 5, punto 4).
* Imparare dal paper: varianti dai referti, figlie, selettore, pesi (stessa fonte, punto 3).
* Lavorare su uscite, trailing, freni e size per creare un vantaggio che all'ingresso non c'è (sezione 3.1).
* Cambiare regole o soglie mentre si misura; una macchina che ritocca le soglie da sola (punto 14; voce K10).
* Nuove funzioni senza una misura del loro contributo (punto 18).
* Un periodo di prova usato due volte, o più tentativi per «riempire» un limite (punti 3 e 17).

## 7. Le decisioni che servono

| N. | Decisione | Proposta |
|---|---|---|
| 1 | Il tipo di idee | sì alle famiglie A (carry), B (posizionamento), C (portafogli fra monete), in quest'ordine |
| 2 | La gamba spot | sì, prima nel paper; per i soldi veri si decide a parte |
| 3 | Il vecchio gate | spento per sempre (codice e registro restano archiviati) |
| 4 | Il paper di oggi | acceso fino al motore nuovo, come banco di misura |
| 5 | I periodi | costruzione fino al 2022, validazione 2023, prova finale 2024-01 → 2026-09 una volta per famiglia con la tua frase, poi il paper |
| 6 | Il tetto ai falsi positivi | 5% su tutto il programma, metà alla prima famiglia, un quarto alla seconda, e così via |
| 7 | La delega | come per il protocollo 4: il coordinamento va avanti da solo con i passi e ti informa; la prova finale di ogni famiglia si apre solo con la tua frase |

Le soglie precise dell'esame non si decidono adesso: arrivano allo STOP del Passo 1, con il collaudo davanti.
