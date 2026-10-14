# Passo 0 della seconda edizione — rapporto del coordinamento (13 ottobre 2026, sera)

> Stato: **finito, STOP sciolto dal proprietario il 14 ottobre 2026 alle 05:00 UTC circa («procedi»)**; prima: finito, in STOP
> (13 ottobre 2026, 22:10 UTC). Il Passo 0 finisce con uno STOP: il proprietario approva `research/config/parametri_2.yaml`
> e solo dopo si apre la sessione di campagna `PANIERE` (`research/PROTOCOLLO_2.md`, sezione 10). Questo file dice
> cosa è fatto, con i numeri e le fonti, e cosa manca; le risposte sono nell'ultima sezione.

## La tabella del Passo 0 (sezione 10 di PROTOCOLLO_2)

| Punto | Cosa | Stato | Numeri e fonte |
|---|---|---|---|
| 1 | Dati 1d delle 80 monete e di BTCUSDT (klines, mark, funding) 2020-2023, più BTCUSDT 8h | **fatto** | 245 serie, 0 errori, 0 checksum mancanti, 48 minuti (`scratchpad`, log dello scarico); 9.406 file con SHA-256 in `research/campagne/PANIERE/impronte_1d.json`; mesi presenti 3.061 klines/1d, 3.061 mark 1d, 3.044 funding su 3.061 attesi dalle schede (il funding ha 17 mesi in meno: le monete che partono nel mese del listing, come nel gruppo a 1 ora) |
| 2 | Motore a barre giornaliere: funding 1d contro 8h, distanza dello stop, costo per trade | **fatto** | `research/passo0_2/misure_motore_1d.md`: stessa strategia (A1-20) su BTCUSDT, 24 trade long e 16 short identici a 1d e a 8h; differenza di funding per trade −0,0003 R (long) e +0,0007 R (short), massima 0,016 R → **si usano le barre di 1 giorno** (sotto i 0,005 R della sezione 3.4). Stop 2,5 ATR(20): mediana 22,2% del prezzo sulle 80 monete (da 13,3% a 27,8%; BTC 11,8%). Costo atteso per trade: mediana 0,0068 R (0,0043-0,0113) |
| 3 | Serie di paniere con controllo di causalità | **fatto** | `research/src/paniere.py` (allineamento sul calendario UTC, rendimento a n giorni, classifica con parità alfabetica, giorni forti di Bitcoin con la deviazione dei 60 giorni precedenti); `test_paniere.py`, 6 test, fra cui quello che cambia il futuro e controlla che il passato non cambi |
| 4 | Strumenti di gruppo a 1d, prova a placebo a 1d, controllo positivo | **fatto** (placebo regge; controllo positivo: due lezioni, sezione sotto) | il modulo delle regole da manuale ammette «1d» (uscita a tempo 10 barre); lanciatore `research/taratura/placebo_paniere/esegui.py` (riusa quello a 1 ora: sfasamento comune, ingressi placebo, esame, identità); copertura dei dati: 80 monete, tutte con barre 1d, funding e giorni 1d nei due periodi; **la prova (96 esami) sta girando**; esito e controllo positivo: sezione sotto |
| 5 | Caricatore e vault; guardiano della sessione PANIERE | **fatto** | il vault si riapre solo con `research/vault/APERTURA_2.md` (`APERTURA.md` dell'11 ottobre non apre più); la campagna PANIERE è una campagna di gruppo per guardiano, caricatore e strumenti (`SIMBOLI_GRUPPO`), con elenco e schede propri in sola lettura; test: 1.348 passati (`test_guardiano_paniere.py`, `test_guardiano_gruppo.py`, `test_guardiano.py`, `test_dati.py`, `test_gruppo_dati.py`) |
| 6 | `research/config/parametri_2.yaml` | **bozza scritta** | tutti i numeri del testo più quelli misurati al punto 2; stato `bozza_passo_0`; lo approva il proprietario allo STOP |
| 7 | Il bot: cosa gli manca per il Passo 9 | **deciso, non costruito** | sezione sotto |

## Il bot (punto 7): cosa serve, cosa no

Il bot esegue oggi strategie generate dal gate (combinazioni di indicatori a 15 minuti e 1 ora, registro
`strategy_registry/validated`), con l'ingresso a ordine limite dal 13 ottobre. Per il paper della seconda edizione
(sezione 9) servirebbero, SOLO se una candidata passa il vault: (1) un tipo di strategia «di paniere a barre
giornaliere» che legga le 80 monete insieme (classifica, giorno forte di Bitcoin) e decida alla chiusura del giorno
UTC; (2) lo stop a 2,5 ATR(20) giornalieri e l'uscita a tempo in giorni al posto delle 96 barre del gate; (3) il tetto
di esposizione per verso che già esiste (`MAX_DIRECTIONAL_RISK_PCT`). Non si costruisce ora: si costruisce dopo il
vault, e si prova sui dati del vault che il paper riproduca il motore (parità), come per le campagne.

## Cosa si è capito al Passo 0 (per il diario)

* **A giorni il costo d'esecuzione sparisce, il funding no.** Con lo stop a 2,5 ATR(20) il rischio di un trade vale
  un quinto del nozionale: 0,09% di commissioni e scarto fanno 0,007 R. Ma un long su Bitcoin tenuto 25 giorni nel
  2020-2023 ha pagato in media 0,23 R di funding (24 trade della misura): a questo orizzonte il funding è il costo
  che conta, e il motore lo addebita (gli short lo incassano: −0,018 R sui 16 short).
* **Lo stop giornaliero è largo**: 22% mediano sulle monete del paniere, 12% su Bitcoin. È quello che dice l'ATR a
  giorni; le posizioni escono soprattutto a segnale e a tempo, non allo stop (BTC: 8 stop su 24).
* **Il motore a barre giornaliere non ha bisogno di barre più fini**: la stessa strategia dà gli stessi trade a 1d e
  a 8h, con il funding a meno di un millesimo di R.

## La prova a placebo a 1d e il controllo positivo

**La prova a placebo regge** (`research/taratura/placebo_paniere/risultati.md`, 96 esami, 45 minuti, commit
e98d0fec): 47 placebo valutabili per periodo su 48 (minimo 40); «nette» in costruzione 0 su 47 (soglia 3%); p sotto
0,10 in validazione 0 su 47 (soglia 13%); code M3 0,35% e 0,58%. Prima di arrivarci due correzioni, scritte prima di
qualunque esito (regole della prova, sezione 7): con i parametri a 1 ora le regole da manuale davano 227-420 trade
sommati (sotto 700: scarti), quindi parametri più corti per il giorno; e senza un tetto di durata le posizioni in ATR
giornalieri duravano centinaia di giorni, un solo blocco, esame non valutabile: tetto di 60 barre come le idee.

**Il controllo positivo a 1d non passa nella forma delle regole del gruppo**, e dice due cose vere sull'esame a
barre giornaliere (`research/passo0_2/controllo_positivo_1d*.json`):

1. **La baseline (b) può non entrare.** La strategia che guarda avanti (segnale ogni giorno in cui la chiusura del
   giorno dopo è a favore) è in posizione quasi sempre; la (b) vuole lo stesso numero di ingressi casuali distanziati
   della durata media, e su 13 monete (long) e 16 (short) con la storia giornaliera più corta le barre non bastano:
   «gli ingressi casuali non entrano» e l'intera variante è non valutabile (regole del gruppo, sezione 5, punto 4).
   Per il controllo è un artefatto (nessuna variante vera è in posizione sempre); per la campagna è un rischio reale
   su una variante con molti trade e posizioni lunghe su una moneta dalla storia corta.
2. **Con pochi blocchi l'esame ha poca potenza.** Sulle monete dove la (b) entra, lo short senza ritardo ha R medio
   +0,29 a trade e t 2,42 contro la (b), ma con 7 blocchi (il blocco è la posizione più lunga: 60 barre su 1.112 di
   costruzione) la soglia è 2,6: non «netto». Con il ritardo di una barra t −0,67: il vantaggio sparisce come deve.
   Il long non è valutabile nemmeno sul sottoinsieme (la (b) non entra su ROSEUSDT). Un vantaggio di +0,3 R a trade
   che non è «netto» dice che, a un giorno, l'esame vede solo vantaggi grandi o varianti con posizioni brevi (più
   blocchi): le placebo con uscita a tempo di 5 barre avevano 16-18 blocchi.

## Lo STOP: cosa decide il proprietario

1. **Approvare `research/config/parametri_2.yaml`** così com'è (i numeri del testo più quelli misurati: stop
   mediano 22,2%, costo 0,0068 R, barre di 1 giorno).
2. **La potenza dell'esame a un giorno.** Tre strade, scritte prima: (a) lasciare l'esame com'è, sapendo che a un
   giorno passano solo vantaggi grandi o idee con posizioni brevi, e che è questo il prezzo di non farsi
   ingannare (la placebo dà 0 falsi positivi); (b) tenere l'uscita a tempo delle idee più corta (per esempio 20
   barre invece di 60) per avere più blocchi: cambia il testo approvato (sezione 3.1) e va riscritto prima della
   campagna; (c) cambiare la regola del blocco per il giorno: è un cambiamento all'esame, va rifatto il placebo e
   non si fa senza il tuo sì. Il coordinamento propone la (a) con una nota in più: una variante «non netta» per
   pochi blocchi si riporta con il suo t e il numero di blocchi, così si vede.
3. **Le monete su cui la (b) non entra.** Oggi rendono non valutabile l'intera variante. Proposta: nella seconda
   edizione quelle monete escono dall'esame di QUELLA variante, si dichiarano (quante e quali) e la variante resta
   valutabile sulle altre se le monete tolte portano meno del 10% dei trade (la stessa regola della (a) di
   gruppo); oltre, non valutabile. È una modifica a `gruppo.py` (sezione 5, punto 4) da scrivere e testare prima
   della campagna, e vale solo con il tuo sì.
4. **Il funding a giorni** pesa (long su Bitcoin: +0,23 R a trade nel 2020-2023): è dentro il motore e dentro
   l'esame; nessuna decisione, solo da sapere quando si leggeranno i risultati.

Finché non arrivano le risposte, nessuna sessione di campagna si apre.

## Le risposte del proprietario (14 ottobre 2026, 05:00 UTC circa, le 07:00 in Italia): «procedi»

Sì a tutte e quattro, come proposte (`research/PROTOCOLLO_2.md`, correzione 3, scritta alle 05:05 UTC prima di
toccare gli strumenti):

1. `research/config/parametri_2.yaml` approvato così com'era: stato `congelato`, `approvazione_parametri`
   2026-10-14T05:00Z.
2. L'esame resta com'è (strada a); ogni variante «non netta» per pochi blocchi si riporta con il suo t e il numero
   di blocchi.
3. La regola per le monete su cui gli ingressi casuali della (b) non entrano: restano fuori dalla combinazione
   della (b) come per la (a); non valutabile contro la (b) se portano più del 10% dei trade del candidato.
   Strumenti: `statistica.baseline_casuale_di_gruppo` (la regola), `statistica.b_ripesata` (le monete lasciate fuori
   restano fuori anche dalla B ripesata di stabilità ed estremi), `gruppo.py` (docstring e stabilità); test nuovi in
   `test_gruppo_statistica.py` e `test_gruppo_esecutore.py` (la moneta sotto il 10% resta fuori e la variante è
   valutabile con la (b) delle altre, bit per bit; sopra il 10% non valutabile; senza monete fuori i numeri di
   prima). Senza monete lasciate fuori i numeri sono identici a prima: la prova a placebo a 1 ora e i risultati della
   campagna di gruppo non cambiano.
4. Il funding a giorni: nessuna decisione, resta dentro motore ed esame.

**Ricontrolli con gli strumenti nuovi** (richiesti dalla correzione 3, prima dell'apertura): la prova a placebo a 1d e
il controllo positivo a 1d si rifanno; gli esiti vanno in `research/taratura/placebo_paniere/risultati.md`, in
`research/campagne/PANIERE/regole.md` (sezione 6) e nelle voci `ricontrollo_con_la_regola_nuova` di
`parametri_2.yaml`.

* **Controllo positivo a 1d con la regola nuova** (`controllo_positivo_1d_regola3.json`, 14 ottobre, 05:36 UTC, 80
  monete, stesso modulo del 13 ottobre): senza ritardo ancora **non valutabile**, perché le monete su cui la (b) non
  entra portano il 12,0% dei trade (long: 13 monete, 424 su 3.535) e il 13,3% (short: 16 monete, 457 su 3.427), oltre
  il 10%: la regola fa quello che dice, e la strategia che guarda avanti resta un caso estremo (in posizione quasi
  sempre). Con il ritardo di una barra la (b) si costruisce (3 e 6 monete fuori, 1,1% e 3,7% dei trade) e il t è
  −0,28 (long) e −0,55 (short): il vantaggio sparisce come deve. Contro la (a) senza ritardo t 1,47 e 1,46 con 7
  blocchi (R medio +0,37 e +0,27 a trade contro +0,04 e −0,08 della (a), effetto grappolo 39 e 30): non «netto».
  Conferma della lezione 2: con posizioni fino a 60 barre i blocchi sono 7 e anche +0,3 R a trade non risulta netto.
* **Prova a placebo a 1d con la regola nuova**: in corso (lancio delle 05:37 UTC, commit c9bb86ad); atteso identico al
  13 ottobre (nessuna delle 96 placebo aveva monete senza ingressi). Esito in
  `research/taratura/placebo_paniere/risultati.md`.
