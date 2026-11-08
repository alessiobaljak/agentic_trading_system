# Diario «Andremo live?» (dal 31 ottobre 2026)

Il diario fino al 30 ottobre 2026, con il documento iniziale «Il sistema è buono? Andremo mai live?», è in
`docs/diario/andremo_live_fino_al_30_ottobre_2026.md` (spostato il 7 novembre 2026, parola per parola, per le regole dei token in
`CLAUDE.md`). Qui si scrive in coda; non si legge mai intero (`tail` o `grep`).

### 31 ottobre 2026 (00:30 UTC)

**Giro delle 00:17.** Notizie: 46 articoli nuovi, tutte e 21 le fonti. Controlli in avanti delle 00:21: niente di nuovo. Chiesto il log
dei ribilanci della notte (0679). **Prova 140, vendere quando una moneta arriva su Hyperliquid** (`programma7/SETTANTOTTESIMA.md`, 00:21
UTC; idea nuova 117): 63 monete già su Binance quotate poi su Hyperliquid, short contro il Bitcoin per 7 giorni. **No**: −0,88% a
operazione (p 0,63). Capito: Hyperliquid quota le monete che stanno già correndo (+27% sul Bitcoin nella settimana prima); dopo, di
solito scendono un po', ma una volta su cinque continuano a salire e l'uscita a +30% si mangia tutto. Nel conto: 238.
**I ribilanci della notte, puliti** (log 0679, nessun errore): G1 alle 00:09 (24 long e 25 short, conto 10.399,79: +4,00% dall'inizio);
G11 alle 00:13 (27 e 23, conto 10.463,71: +4,64%); G1N alle 00:17 (24 e 25, conto 10.632,08: +6,32%); il conto demo alle 00:17 (32 ordini
limite, 1 rifiutato, la solita moneta con il nome in caratteri cinesi). **Chiusa la prima operazione a eventi del bot**: la vendita su
IRYS (E4, aperta il 24 ottobre), uscita a tempo dopo 7 giorni con **+62,74% (+313,71 dollari)**. È un evento solo: E4 sul passato faceva
+11,7% a evento (prova 26), quindi questo è molto sopra la media e non dice niente da solo.
**Giro delle 04:18.** Notizie: 25 articoli nuovi da 20 fonti su 21 (CoinJournal non ha risposto). Controlli in avanti delle 04:21:
niente di nuovo. L'idea 119 (i furti alle borse come evento) non si fa: dal 2020 sono 4. **Prova 141, il funding che diventa negativo
dopo una settimana positiva** (`programma7/SETTANTANOVESIMA.md`, 04:22 UTC; idea nuova 118, trading di ogni giorno): comprare la moneta
il giorno in cui arrivano in fretta tanti short. **No, e al contrario**: −0,98% a operazione su 3.896 eventi, peggio dei giorni in cui il
funding era già negativo (+0,05%). Capito: gli short che arrivano in fretta su una moneta tranquilla di solito hanno ragione; quelli che
perdono, nella regola di G1, sono le folle affollate da tempo, non chi arriva per primo. Nel conto: 239.
**Gli eventi sul conto demo accanto a G1** (il proprietario, 31 ottobre: «ok aggiungi gli eventi sul demo accanto a G1»): le operazioni
aperte del paper degli eventi si sommano ai pesi di G1 sullo stesso conto demo, il 5% del conto ciascuna; quando il paper ne apre o
chiude una, il demo tocca solo quella moneta e il Bitcoin (`bot/portafoglio/demo_binance.py`, interruttore
`ops/demo_binance_eventi_acceso`, 4 test nuovi; tutti i 2.480 test passano). È la prova generale del conto unico per i soldi veri.
Chiesto il riavvio del bot alla VPS (0680).
Il bot è ripartito alle 07:26 UTC (log 0681) con `DRY_RUN=True` e il codice degli eventi sul demo (commit f6ce9a66), senza errori del
paper o del demo; restano solo due avvisi vecchi del sistema fermo (le posizioni aperte di MITOUSDT e PTBUSDT non lette da Binance).
**Mattino del 31 ottobre.** Prova in avanti del programma 5: M-001c 181 su 400, M-002 e M-003 non passano, la seconda tornata ferma.
Conto a tavolino: dati fino al 29 ottobre, le 22 monete nuove dell'universo sono tutte monete; il funding di Hyperliquid letto per 213
monete (HLI parte dal 2 novembre). **Prova 142, G1 dentro ogni settore** (`programma7/OTTANTESIMA.md`, 08:01 UTC; idea 120): il funding
confrontato solo fra monete dello stesso settore (CoinGecko). **No**: Sharpe 1,49 contro 1,98 di G1, con la stessa discesa. Capito: G1
resta in media comprata sulle reti principali e venduta su meme e finanza decentralizzata, e quel confronto fra settori è una parte del
guadagno, non solo un rischio; scritto nel backlog fra i rischi di G1 per i soldi veri (P26). Nel conto: 240.
**Giro delle 08:18.** Notizie: 18 articoli nuovi, tutte e 21 le fonti. Controlli in avanti delle 08:20: niente di nuovo. **Il conto
unico sul passato** (`programma7/conto_unico.py`, `CONTO_UNICO.md`; una misura per capire, non una prova, non entra nel conto): G1 con
tutto il capitale più gli eventi delle prove 32 (monete appena quotate) e 26 (funding al tetto) al 5% ciascuno, al massimo 20 aperti,
come fa ora il demo. Dal 2021 al 4 ottobre 2026: **G1 da sola +65,7% l'anno, Sharpe 1,98, discesa −30,1%; G1 più gli eventi +115,5%,
Sharpe 2,82, discesa −22,3%**; gli eventi da soli +30,2%, Sharpe 3,41, discesa −25,2%; correlazione fra i due 0,03 (664 eventi usati, 11
saltati perché ce n'erano già 20 aperti). Il 2021 è l'unico anno in cui gli eventi tolgono (da +177,6% a +166,5%). Capito: le due
famiglie guadagnano in giorni diversi, quindi insieme la discesa scende invece di salire; è il motivo del conto unico. Le riserve: il
rendimento di ogni evento è spalmato sui suoi giorni (la discesa vera è più grande), e gli eventi su Binance non sono dimostrati come
G1 (la prova 32 è valida sui dati di Gate.io e passa con riserva su Binance; la 26 è promettente, non dimostrata).
**Giro delle 12:18.** Notizie: 43 articoli nuovi, tutte e 21 le fonti. Controlli in avanti delle 12:22: niente di nuovo (su Coinbase
sempre solo STABLE, nessuna chiusura nuova di Binance). L'idea 122 (vendere quando una moneta arriva su Kraken) non si fa: la stessa
idea non ha retto su Coinbase, OKX e Hyperliquid. **Prova 143, il momento dei settori** (`programma7/OTTANTUNESIMA.md`, 12:27 UTC; idea
121, dalla tesi di Luo del 2025): ogni lunedì long le monete dei settori saliti di più nelle 4 settimane prima, short quelle dei settori
saliti di meno. **No**: Sharpe 0,40, discesa −55%, il 2024 a −45%; i settori finti fatti a caso fanno in media −0,11, quindi un po' di
segnale c'è, ma con sei settori ogni lato è una scommessa su uno o due racconti interi, troppo agitata. Capito: nei perpetui il
momento dei settori non regge dopo i costi; non è legato a G1 (correlazione 0,00), ma da solo non vale. Nel conto: 241.
**Giro delle 16:18.** Notizie: 63 articoli nuovi, tutte e 21 le fonti; da oggi la raccolta salva anche le 15 monete di tendenza di
CoinGecko a ogni giro (idea 126: la famiglia dell'attenzione; lo storico gratuito non esiste, si prova in avanti fra 6 mesi). Controlli
in avanti delle 16:19: niente di nuovo. Ricerca nelle pubblicazioni del 2026 con la coda vuota: tre idee nuove. Due non si fanno: le
monete poco agitate (è quasi la scommessa contro il beta, già bocciata) e il momento dell'apertura di Wall Street sul Bitcoin (i controlli
delle prove sulla Fed e sull'inflazione l'hanno già misurato: −0,15% e −0,11% a operazione). **Prova 144, il momento delle salite
continue** («la rana nella pentola», `programma7/OTTANTADUESIMA.md`, 16:21 UTC; idea 123; trading di ogni giorno): comprare le monete
salite a piccoli passi nei 14 giorni, vendere quelle scese a piccoli passi. **No**: Sharpe −0,20, discesa −89%, sotto il momento
semplice (0,15). Capito: nei perpetui il momento non regge in nessuna forma, e il filtro della continuità lo peggiora (lati più piccoli
e il doppio delle spese). Nel conto: 242.
**Giro delle 20:18.** Notizie: 42 articoli nuovi da 20 fonti su 21 (ZyCrypto non ha risposto); 15 monete di tendenza salvate.
Controlli in avanti delle 20:20: niente di nuovo. **Prova 145, le notizie nuove contro quelle ripetute** (`programma7/OTTANTATREESIMA.md`,
20:22 UTC; idea 127, da Tetlock 2011 e Chu e Tsiakas 2026): per ogni articolo su una moneta, quanto è diverso dai 20 articoli precedenti
sulla stessa moneta; comprare le monete con le notizie più nuove, vendere quelle con le notizie più ripetute. **No**: Sharpe −0,36,
discesa −80%, e il segnale mescolato a caso fa quasi lo stesso (13 volte su 20 almeno quanto quello vero). Capito: con i titoli e i
riassunti dei giornali crypto, né quanto si parla di una moneta (prova 138) né quanto è nuovo quello che se ne dice muovono il prezzo
della settimana dopo. Nel conto: 243.

### 1° novembre 2026 (00:50 UTC)

**Giro delle 00:18.** Notizie: 24 articoli nuovi, tutte e 21 le fonti; rifatto l'elenco dei nomi delle monete per novembre. Controlli
in avanti delle 00:20: niente di nuovo. **I ribilanci della notte, puliti** (log 0684): G1 alle 00:09 (25 long e 26 short, conto
10.320,45: +3,20% dall'inizio), G11 alle 00:13 (30 e 23, 10.457,50: +4,58%), G1N alle 00:17 (25 e 26, 10.538,03: +5,38%), il conto demo
alle 00:18 (34 ordini limite, 1 rifiutato, la solita moneta con il nome in caratteri cinesi). La sera del 31 tutti avevano perso circa un
punto e mezzo per la discesa di Tron (−7,8% in 24 ore su CoinGecko), la moneta più comprata (12-13% in G1, 31% in F5).
**Prova 146, vendere dopo un attacco informatico al protocollo** (`programma7/OTTANTAQUATTRESIMA.md`, 00:22 UTC; idea 128, che riapre
la 93 con l'elenco pubblico di DefiLlama). **No**: dei 1.333 attacchi restano 28 eventi con il gettone sul perpetuo di Binance, +3,94% a
operazione ma p 0,071, e senza le 5 migliori è negativo. Capito: dopo un attacco il gettone in media scende ancora un po' contro il
Bitcoin (i 3 attacchi sopra i 10 milioni fanno +26,8% sul nostro short), ma quasi tutti gli attacchi colpiscono protocolli senza gettone
o senza perpetuo, e 28 eventi in sei anni non bastano. Nel conto: 244 (45 a eventi).
**Giro delle 04:18.** Notizie: 14 articoli nuovi da 20 fonti su 21 (CoinJournal non ha risposto). Controlli in avanti delle 04:21:
niente di nuovo. Nessuna prova nuova sul passato: due idee scritte e non provate, con il perché nel registro (129, la regola di HLI con
il funding di dYdX: sul passato non sarebbe indipendente; 130, il Bitcoin tenuto solo fuori dagli orari di Wall Street: i costi di ogni
giorno la mangiano). **Una misura in avanti in più, DXI** (`programma6/paper/REGOLE.md`, sezione 16, scritta alle 04:23 UTC prima di
leggere i dati): la stessa regola di HLI con il funding di dYdX, dal 2 novembre accanto a HLI, verdetto a 52 settimane; se il meccanismo
di HLI è vero deve vedersi anche lì. Scarico provato: 226 monete di dYdX abbinate ai perpetui di Binance, funding ogni ora dal 20
ottobre (`aggiorna.funding_dydx`); tutti i 2.480 test passano. Capito oggi: niente di nuovo sui prezzi; una correzione mia, detta al
proprietario: il tetto del 10% per moneta **non** c'è nella versione per i soldi veri (la prova 61 l'ha bocciato: alzava la discesa).
**Mattino del 1° novembre.** Notizie: 8 articoli nuovi da 20 fonti su 21. Prova in avanti del programma 5: M-001c 215 su 400, M-002 e
M-003 non passano, la seconda tornata N-001 34, N-002 21, N-003 6. Conto a tavolino: dati fino al 30 ottobre, le 22 monete entrate
nell'universo sono le stesse di ieri (tutte monete); il funding letto per 213 monete di Hyperliquid e 226 di dYdX (HLI e DXI partono
dal 2 novembre). Fra le vendite a tavolino sulle monete nuove di Gate.io, PREDICT chiusa a −31,7% (uscita a +30% contro).
**Giro delle 08:17.** Notizie: 16 articoli nuovi, tutte e 21 le fonti. Controlli in avanti delle 08:18: niente di nuovo. Nessuna prova
nuova: la ricerca nelle pubblicazioni del 2025-2026 sugli eventi ha portato solo un'idea, vendere nelle 72 ore dopo uno sblocco (idea
131), che non si fa perché i nostri 513 sblocchi dicono già il contrario per il giorno dello sblocco (la moneta risale contro il
Bitcoin). Capito oggi: niente di nuovo sui prezzi; le idee con dati gratuiti e un perché forte che non abbiamo ancora provato sono
quasi finite, e le prossime verranno soprattutto dalle misure in avanti (notizie, monete di tendenza, HLI e DXI dal 2 novembre).
**Giro delle 12:18.** Notizie: 52 articoli nuovi, tutte e 21 le fonti. Controlli in avanti delle 12:19: niente di nuovo. **Una misura in
avanti nuova: copiare i trader migliori di Hyperliquid** (idea 132, `trader_copiati/HYPERLIQUID.md`, regola scritta alle 12:20 UTC
prima di raccogliere qualunque posizione): la versione automatica dell'idea del proprietario dei trader da copiare. Su Hyperliquid la
classifica (48.270 conti) e le posizioni di ognuno sono pubbliche; dal 2 novembre, ogni lunedì i 20 conti con il rendimento del mese più
alto (almeno 1 milione nel conto), le loro posizioni lette a ogni giro della raccolta e copiate sui perpetui di Binance; verdetto a 52
settimane. Sul passato non si può: la classifica di oggi tiene solo i sopravvissuti. Lettura provata in una cartella di prova: 20 conti
su 20 (`trader_copiati/hyperliquid.py`, chiamata dalla raccolta delle notizie). Idea 133 ferma: le liquidazioni vere per moneta
(Coinalyze) servono una chiave che può creare solo il proprietario.
**Il proprietario, 1° novembre: «perché il 30 novembre? [...] verdetto dopo 52 settimane? questo è inaccettabile».** Ha ragione: le
attese di 52 settimane andavano contro quello che aveva detto il 21 e il 24 ottobre (si giudica sul passato, il demo è una conferma di
qualche giorno o settimana, poi decide lui). Corretto in tutte le regole delle misure in avanti (`programma6/paper/REGOLE.md` sezione 17,
`notizie/REGOLE.md`, `trader_copiati/HYPERLIQUID.md`): niente attese fisse, i numeri al proprietario ogni settimana, i soldi veri quando
li chiede. **E invece di aspettare il 30 novembre, la regola delle notizie si è provata subito sui titoli del 2026** (prova 147, archivio
pubblico katelabs, 25.407 titoli di febbraio-aprile 2026, mai usati): **+0,14% a settimana dopo i costi, contro −0,48% di G1 nelle stesse
8 settimane**, 4 settimane positive su 8. Conferma il verso, ma debole e su poche settimane. Il primo calcolo con la nostra raccolta resta
il 30 novembre solo perché la regola conta gli articoli dei 28 giorni prima. Nel conto: 245.
**La revisione di G1 con le skill** (richiesta del proprietario: «lanciale subito»; `programma7/REVISIONE_SKILL_G1.md`). Revisione del
backtest: nessun errore nel codice (niente dati dal futuro, monete tolte dal listino dentro, costi e funding veri, entrata all'apertura
dopo), ma tre limiti: nessun periodo davvero nuovo, sulle monete 101-200 Sharpe 0,75, una moneta sola può pesare troppo. Il guadagno
separato dal mercato: il mercato spiega il 3,6%, resta +62% l'anno prima delle spese (t 5,1), i settori non lo spiegano; negli ultimi 6
mesi circa la metà. Il rischio: discesa −30,1%, la più lunga 354 giorni, code grasse (curtosi 8,7). I dati: pochi problemi (0,1%). La
critica avversaria di un revisore separato: **oggi no ai soldi veri, sì con condizioni e solo G1**. Ricontrollato da me: **lo Sharpe
corretto di G1 oggi è 0,86, non 0,94** (rifatto il 25 ottobre con più prove nel conto; il valore vecchio era rimasto nel registro e nei
miei messaggi: errore mio, detto al proprietario); **N3 dal 1° luglio 2025 fa −2,30% a evento su 213**, quindi il conto unico G1 più
eventi non è la proposta per i soldi veri; il demo imposta la leva 5 ma non il tipo di margine. Le condizioni sono nel backlog (P26).
Capito oggi: G1 ha un vantaggio vero sul passato che non viene dal mercato, ma è sotto la soglia del proprietario contando tutte le
prove, dipende da pochi periodi e dal funding estremo, e gli eventi nell'ultimo anno tolgono invece di aggiungere.
**Giro delle 16:18.** Notizie: 49 articoli nuovi, tutte e 21 le fonti. Controlli in avanti delle 16:21: niente di nuovo. Una misura per il
piano dei soldi veri (`programma7/REVISIONE_SKILL_G1.md`, sezione 6): con il margine separato per ogni moneta a leva 5 almeno una
posizione di G1 sarebbe stata chiusa a forza in 313 giorni su 2.100 dal lato comprato e in 843 dal lato venduto; con il margine unico per
tutto il conto mai. Quindi il margine unico va impostato e controllato dal codice prima dei soldi veri (oggi non è controllato). Capito
oggi: il tipo di margine non è un dettaglio, decide se il backtest vale o no.
**Le protezioni del conto demo** (il proprietario, 1° novembre: «sì prepara e soglia −35%»; `bot/portafoglio/demo_binance.py`, 6 test
nuovi, tutti i 2.486 test passano): (1) il margine unico per tutto il conto chiesto a Binance per ogni moneta prima della leva, e
controllato ogni ora: una moneta con il margine separato si chiude, passa al margine unico e si riapre subito ai pesi di oggi; (2) il
pulsante «Chiudi tutto sul demo» nella dashboard, con la conferma, e «Riparti»; lo stesso comando anche come file
(`ops/demo_binance_chiudi_tutto`, `ops/demo_binance_riparti`), che la sessione può scrivere su richiesta del proprietario; (3) lo stop
sul conto: a −35% dal massimo il demo chiude tutto da solo e si ferma finché non si preme «Riparti»; (4) ogni ora il confronto fra le
quantità vere e quelle volute all'ultimo ribilancio, con le monete oltre il 2% del conto su RTDB e nello stato della macchina. Il
pulsante della dashboard ha bisogno delle regole del database aggiornate (`firebase/database.rules.json`, da pubblicare con `firebase
deploy`); fino ad allora vale il comando come file. Gli eventi restano solo sul demo, con i soldi finti (conferma del proprietario).
**Giro delle 20:17.** Notizie: 36 articoli nuovi, tutte e 21 le fonti. Controlli in avanti delle 20:20: niente di nuovo. **Il primo
controllo delle protezioni del demo** (stato 0688, 20:07 UTC): il conto demo usava già il margine unico su tutte le monete (niente da
sistemare); lo stop sul conto è attivo, con il massimo contato dalla ripartenza (5.159,32 dollari, si chiude tutto sotto 3.353,55); il
confronto fra posizioni vere e volute parte dopo il ribilancio di stanotte. Conto demo +3,33% dall'inizio. Nessuna prova nuova: la coda
delle idee con dati gratuiti e un perché forte è vuota; le misure in avanti nuove (HLI, DXI, la copia dei trader di Hyperliquid)
partono domani.

### 2 novembre 2026 (00:25 UTC)

**Giro delle 00:18.** Notizie: 31 articoli nuovi, tutte e 21 le fonti. Controlli in avanti delle 00:21: niente di nuovo. **Partita la
copia dei trader di Hyperliquid**: scelti i 20 conti della settimana fra 48.241 in classifica (conto da almeno 1,06 milioni, rendimento
del mese fra +93% e +409%: usano molta leva), lette le posizioni di tutti e 20 (`trader_copiati/hyperliquid/`). Ribilanci della notte
(log 0689): F5 alle 00:09, il ribilancio del lunedì (26 long e 25 short, conto 9.852,92: −1,47% dall'inizio); G1 alle 00:13 (27 e 25,
10.274,39: +2,74%); G11 alle 00:17 (30 e 22, 10.404,61: +4,05%); G1N e il demo dopo le 00:20, nel prossimo stato. Da oggi contano i
giorni di HLI e DXI.
**Giro delle 04:17.** Notizie: 27 articoli nuovi da 20 fonti su 21; posizioni dei 20 trader di Hyperliquid lette. Controlli in avanti
delle 04:21: niente di nuovo. **Il primo confronto del demo fra le posizioni vere e quelle volute** (stato 0690, 03:22 UTC): 52 monete,
scarto totale 2,5% del conto, nessuna moneta oltre il 2% (dentro c'è la moneta con il nome in caratteri cinesi che Binance rifiuta);
margine unico su tutte le monete; ribilancio del demo del 2 novembre: 46 ordini, 45 eseguiti a limite e 1 a mercato. Conto demo +2,92%
dall'inizio, G1N nel paper +4,33%.
**Mattino del 2 novembre.** Prova in avanti del programma 5: M-001c 224 su 400, M-002 e M-003 non passano, la seconda tornata N-001 35,
N-002 23, N-003 6. Conto a tavolino: dati fino al 31 ottobre, le 22 monete entrate nell'universo sono le stesse (tutte monete);
funding letto per 213 monete di Hyperliquid e 226 di dYdX. Stato del mattino (0691): conto demo +2,23%, G1 +1,60%, G1N +4,01%, F5 −2,30%
dall'inizio; nelle 24 ore sono scese alcune monete piccole comprate (POL −3,4%, ALGO −2,6% su CoinGecko) mentre il Bitcoin venduto è salito
un poco (+0,2%).
**Giro delle 08:28.** Notizie: 25 articoli nuovi, tutte e 21 le fonti; posizioni dei trader di Hyperliquid lette (4 giri da stanotte).
Controlli in avanti delle 08:30: niente di nuovo. Scritto il conto della copia dei trader (`trader_copiati/conto_hyperliquid.py`): dei
20 conti scelti, 14 hanno posizioni sui perpetui (gli altri 6 hanno i soldi altrove); la loro leva media è circa 7,5 volte il conto, il
portafoglio copiato si scala a 2 come G1; 94 monete in tutto. Il primo conto si fa domani, quando l'archivio di Binance pubblica le
candele di oggi.
**Giro delle 12:36.** Notizie: 116 articoli nuovi, tutte e 21 le fonti (il lunedì i giornali scrivono di più); posizioni dei 20 trader di
Hyperliquid lette. Controlli in avanti delle 12:39: niente di nuovo. Nessuna prova nuova.
**Giro delle 16:53.** Notizie: 138 articoli nuovi da 20 fonti su 21; la pagina di Crypto Briefing era tutta nuova (qualche articolo
fra un giro e l'altro può essere sfuggito: il giro è partito con mezz'ora di ritardo). Posizioni dei 20 trader di Hyperliquid lette.
Controlli in avanti delle 16:56: niente di nuovo. Nessuna prova nuova.
**Giro delle 20:18.** Notizie: 90 articoli nuovi, tutte e 21 le fonti; posizioni dei 20 trader di Hyperliquid lette. Controlli in
avanti delle 20:19: niente di nuovo. Stato delle 20:03 (0692): conto demo +2,20%, G1 +1,75%, G1N +4,44%, F5 −2,20% dall'inizio; nel
demo nessuna moneta oltre il 2% di scarto, margine unico. Nessuna prova nuova.

### 3 novembre 2026 (00:30 UTC)

**Giro delle 00:18.** Notizie: 94 articoli nuovi, tutte e 21 le fonti; posizioni dei 20 trader di Hyperliquid lette (8 giri). Controlli
in avanti delle 00:22: niente di nuovo. Ribilanci della notte (log 0693), puliti: G1 alle 00:09 (27 long e 25 short, conto 10.160,09:
+1,60%), G11 alle 00:13 (30 e 23, 10.308,05: +3,08%), G1N alle 00:17 (27 e 25, 10.432,74: +4,33%), il demo alle 00:18 (33 ordini limite, 1
rifiutato, la solita moneta). Il conto della copia dei trader non ha ancora i prezzi: l'archivio di Binance non ha pubblicato le candele
del 2 novembre; si rifà nel prossimo giro.
**Giro delle 04:17.** Notizie: 37 articoli nuovi, tutte e 21 le fonti; posizioni dei 20 trader di Hyperliquid lette (9 giri). Controlli in
avanti delle 04:23: niente di nuovo. Il conto della copia dei trader aspetta ancora le candele del 2 novembre: l'archivio pubblico di
Binance alle 04:22 non le aveva (risposta 404); di solito escono con un giorno e mezzo di ritardo.
**La scheda «Giorno per giorno» della dashboard** (il proprietario, 3 novembre: «un grafico che ti fa vedere paper e demo come stanno
andando giornalmente, sia profitto che win rate che percentuali, posizioni aperte e chiuse»): `dashboard/app/components/DiarioPaper.tsx`,
nella scheda del paper sotto il grafico dell'andamento. Una tabella con tutte le strategie (valore, dall'inizio, profitto, giorni in
guadagno sul totale, giorno migliore e peggiore, posizioni aperte, entrate e uscite; per gli eventi le operazioni chiuse e quante in
guadagno); toccando una riga, le barre del profitto di ogni giorno e la tabella dei giorni. Nel bot (`f5.py`, `eventi.py`,
`demo_binance.py`): le entrate e le uscite di ogni ribilancio, il diario del giorno, e il valore di ogni giorno anche per gli eventi. Il
grafico dell'andamento ha anche gli eventi. Tutti i 2.486 test passano, la dashboard si costruisce; chiesto il riavvio del bot.
**Mattino del 3 novembre.** Prova in avanti del programma 5: M-001c 228 su 400, M-002 e M-003 non passano, la seconda tornata N-001 43,
N-002 30, N-003 6. Conto a tavolino: dati fino al 1° novembre; entrate nell'universo nuove (AGT, AVA, CHIP, ERA, JCT, MAGMA, OGN): tutte
monete (CHIP è il gettone di USD.AI su CoinGecko), niente da togliere. Corrette le istruzioni della routine del mattino: niente attese
fisse, il lunedì il riepilogo settimanale al proprietario (la regola del 1° novembre).
**Giro delle 08:17.** Notizie: 28 articoli nuovi, tutte e 21 le fonti; posizioni dei 20 trader di Hyperliquid lette (11 giri); il conto
della copia aspetta ancora le candele del 2 novembre. Controlli in avanti delle 08:20: CT compare fra le monete su Coinbase, ma scambia lì
dal 19 ottobre e il perpetuo di Binance ha solo un mese: non è un evento nuovo per la misura dell'effetto Coinbase. Nessuna prova nuova.
**Giro delle 12:19.** Notizie: 98 articoli nuovi, tutte e 21 le fonti; posizioni dei 20 trader di Hyperliquid lette (12 giri).
Controlli in avanti delle 12:23: niente di nuovo. **Il primo conto della copia dei trader di Hyperliquid** (le candele del 2 novembre sono
uscite; `trader_copiati/HYPERLIQUID_CONTO.md`): dal 2 novembre all'01:00 UTC, 20 ore, **+3,22%** (prezzo +3,38%, spese −0,16%; il funding
del 2 novembre non è ancora nel pannello), esposizione 2, la leva dei 20 conti prima di scalare 7,5 volte. Un giorno solo: non dice niente.
**Giro delle 16:18.** Notizie: 127 articoli nuovi da 19 fonti su 21 (la pagina di Crypto Briefing era tutta nuova); posizioni dei 20
trader di Hyperliquid lette. Controlli in avanti delle 16:22: niente di nuovo. Nessuna prova nuova.
**Giro delle 20:18.** Notizie: 102 articoli nuovi, tutte e 21 le fonti (la pagina di Crypto Briefing di nuovo tutta nuova); posizioni dei
20 trader di Hyperliquid lette. Controlli in avanti delle 20:22: niente di nuovo. Nessuna prova nuova.

### 4 novembre 2026 (00:30 UTC)

**Giro delle 00:18.** Notizie: 95 articoli nuovi da 22 fonti su 22; da oggi si legge anche la seconda pagina di Crypto Briefing (la
prima era tutta nuova tre volte: qualche articolo sfuggiva). Controlli in avanti delle 00:23: niente di nuovo. Ribilanci della notte (log
0696), puliti: G1 alle 00:09 (27 long e 26 short, conto 10.100,02: +1,00%), G11 alle 00:13 (27 e 22, 10.280,00: +2,80%), G1N alle 00:17
(27 e 26, 10.382,33: +3,82%), il demo alle 00:18 (32 ordini limite, 1 rifiutato, la solita moneta).
**Giro delle 04:18.** Notizie: 31 articoli nuovi da 22 fonti su 22 (nessuna pagina piena); posizioni dei 20 trader di Hyperliquid lette
(16 giri); il conto della copia aspetta le candele del 3 novembre. Controlli in avanti delle 04:23: niente di nuovo. Nessuna prova nuova.
**Mattino del 4 novembre.** Prova in avanti del programma 5: M-001c 230 su 400, M-002 e M-003 non passano, la seconda tornata N-001 48,
N-002 31, N-003 23. Conto a tavolino: dati fino al 2 novembre, le monete entrate nell'universo sono le stesse di ieri (tutte monete); HLI e
DXI compaiono da domani (serve l'apertura del giorno dopo per il primo giorno). Copia dei trader di Hyperliquid: +3,24% nelle prime 20 ore
(le candele del 3 novembre non sono ancora uscite).
**Giro delle 08:18.** Notizie: 40 articoli nuovi da 22 fonti su 22; posizioni dei 20 trader di Hyperliquid lette. Controlli in avanti
delle 08:19: niente di nuovo. Nessuna prova nuova.
**Giro delle 12:20.** Notizie: 100 articoli nuovi da 22 fonti su 22; posizioni dei 20 trader di Hyperliquid lette. Copia dei trader:
dopo 44 ore **−0,18%** (prezzo +0,09%, spese −0,20%, funding +0,02%): il +3% del primo giorno è tornato indietro il secondo. Controlli
in avanti delle 12:27: niente di nuovo. Nessuna prova nuova.
**Giro delle 16:18.** Notizie: 141 articoli nuovi da 22 fonti su 22 (la prima pagina di Crypto Briefing era tutta nuova, la seconda
ha coperto il resto); posizioni dei 20 trader di Hyperliquid lette. Controlli in avanti delle 16:23: niente di nuovo. Nessuna prova
nuova.
**Giro delle 20:18.** Notizie: 111 articoli nuovi da 21 fonti su 22; posizioni dei 20 trader di Hyperliquid lette. Controlli in avanti
delle 20:21: niente di nuovo. Nessuna prova nuova.

### 5 novembre 2026 (00:30 UTC)

**Giro delle 00:18.** Notizie: 85 articoli nuovi da 22 fonti su 22 (la prima pagina di Crypto Briefing di nuovo piena); posizioni dei
20 trader di Hyperliquid lette (22 giri raccolti). Copia dei trader ancora a −0,18% dopo 44 ore: le candele orarie del 4 novembre non
sono ancora pubblicate. Controlli in avanti delle 00:27: nessuna quotazione nuova su Coinbase oltre STABLE e CT, nessun annuncio di
chiusura dei perpetui dopo il 21 ottobre. Richiesta del log del bot per i ribilanci della notte (ops 0697). Nessuna prova nuova.
Ribilanci della notte (log del bot, ops 0697): paper G1 a 10.311,91 (ieri 10.100,02, +2,1% in un giorno), G11 a 10.526,26 (+2,4%), G1N
a 10.550,64 (+1,6%); sul demo G1 ha mandato 41 ordini limite, 1 rifiutato (come nei giorni scorsi). Nessun errore del bot oltre le
solite letture rifiutate di MITO e PTB (perpetui chiusi da Binance).
**Giro delle 04:18.** Notizie: 38 articoli nuovi da 21 fonti su 22; posizioni dei 20 trader di Hyperliquid lette (23 giri); copia dei
trader ancora a −0,18% (le candele del 4 novembre non sono uscite). Controlli in avanti delle 04:25: niente di nuovo. Guardata l'ultima
voce «da guardare solo in avanti» del registro (vendere il perpetuo quando Binance annuncia la moneta a pronti): contati solo gli
annunci, uno solo dall'11 ottobre (PREDICT), circa uno al mese, quindi una misura in avanti non deciderebbe in tempi utili: scritta come
idea 134 con il perché, non avviata. Nessuna prova nuova. **Capito oggi**: le quotazioni a pronti di monete già nate come perpetuo sono
diventate rare (5 dal 17 luglio), quindi quella famiglia di eventi non può più dare una strategia.
**Aggiornamento della mattina (06:14).** Notizie: 28 articoli nuovi da 21 fonti su 22. Prova in avanti del programma 5 (dati fino al 3
novembre): M-001c 233 trade chiusi su 400 (in corso), M-002 e M-003 non passano; seconda tornata N-001 49, N-002 31, N-003 27. Il primo
lancio si è fermato su un comando del repo troppo lento (il salvataggio delle notizie nello stesso momento), il secondo sul limite di
50 minuti che avevo messo io: l'ultima procedura rifatta da sola. Conto a tavolino del programma 6 con i dati fino al 4 novembre; le
monete entrate nell'universo sono tutte crypto (USUSDT è Talus, perpetuo nato il 12 dicembre 2025 insieme a CYSUSDT).
**Errore trovato e corretto**: HLI e DXI (dal 2 novembre) non comparivano nel conto a tavolino. Il calcolo giornaliero prendeva
l'universo delle 100 monete dal pannello delle settimane, che contiene solo le settimane chiuse, quindi i giorni della settimana in corso
restavano fuori fino al lunedì dopo (avevo scritto che sarebbero comparse col primo giorno dopo il 2 novembre: non era vero). Ora
l'universo della settimana in corso si calcola il lunedì con i dati di prima, come fa il bot (`terza.universo_lunedi`, la stessa regola
spostata in una funzione: universi e pesi identici a prima su tutte le settimane chiuse, prime 100 e 101-200; due test nuovi; 2.488 test
passano). Primi due giorni (2-3 novembre): **HLI −1,75%** contro G1 sulle stesse monete −0,22%; **DXI −0,79%** contro −0,37%. Due
giorni non dicono niente. Il proprietario ha chiesto se si possono copiare le balene sulla blockchain: risposto (la copia di Hyperliquid
lo fa già; sulle altre catene lo storico gratuito non è pulito) e proposto un secondo gruppo di Hyperliquid con i 20 conti più grandi.
**Copia dei trader di Hyperliquid, con i prezzi del 4 novembre: −7,90% dopo 68 ore** (prezzo −7,55%, spese −0,32%, funding +0,06%;
`trader_copiati/HYPERLIQUID_CONTO.md`). Quasi tutto in un tratto: dalle 13:00 alle 17:00 UTC del 4 novembre −7,37%, quando l'Ether è
salito del 5,22% in 4 ore (Bitcoin +2,85%, XRP +2,93%; prezzi orari di Binance controllati). **Capito**: il portafoglio copiato è in
pratica uno short sull'Ether: venduto per circa 1,75 su un'esposizione di 2 in tutti i giri (Ether −1,0/−1,2, Bitcoin −0,3). All'ultimo
giro 13 dei 14 conti con posizioni aperte erano corti sull'Ether, con leve da 7 a 16 volte il conto; 6 dei 20 conti scelti il 2
novembre hanno ora il conto da perpetui quasi vuoto. La media dei pesi la decidono i conti con più leva: copiare «i migliori del mese»
oggi vuol dire copiare una sola scommessa molto spinta. Da guardare: una variante con ogni conto portato a esposizione 1 prima della
media (regola da scrivere prima, solo in avanti) e il gruppo dei 20 conti più grandi.
**Giro delle 08:17.** Notizie: 30 articoli nuovi da 21 fonti su 22; posizioni dei 20 trader lette. Controlli in avanti delle 08:30:
niente di nuovo. Ricerca: **due gruppi nuovi nella copia di Hyperliquid**, regole scritte prima (`trader_copiati/HYPERLIQUID.md`,
aggiunta del 5 novembre, 08:40 UTC) e solo in avanti: (1) gli stessi 20 conti, ognuno portato a esposizione 2 prima della media (si copia
la direzione di ognuno, non la sua leva); (2) le «balene», i 20 conti più grandi della classifica con guadagno del mese sopra zero, scelti
la prima volta al prossimo giro (12:17) e poi ogni lunedì. Il gruppo di prima resta identico (−7,90% rifatto con il codice nuovo: stesso
numero). Tre test nuovi; 2.491 test passano.
**Giro delle 12:18.** Notizie: 89 articoli nuovi da 21 fonti su 22. Scelte le prime 20 «balene» di Hyperliquid (conti da 31 a 211
milioni di dollari, `trader_copiati/hyperliquid/scelti_balene_2026-11-05.json`); letti 39 conti (uno sta in tutti e due i gruppi). Al
primo giro, prima di qualunque prezzo: le balene sono anche loro più vendute che comprate (−1,91 su 2: Bitcoin −0,56, Hyperliquid −0,42,
Ether −0,33), con leva media 4,2 contro 8,6 dei migliori del mese; i migliori del mese a esposizione uguale −0,98 su 1,33 (Ether −0,74).
Controlli in avanti delle 12:24: niente di nuovo. Nessuna prova nuova.
**Giro delle 16:17.** Notizie: 153 articoli nuovi da 22 fonti su 22 (la prima pagina di Crypto Briefing piena, la seconda ha coperto il
resto); 39 conti di Hyperliquid letti. Controlli in avanti delle 16:22: niente di nuovo. Idea 135 scritta (il contrario dei trader con
più leva): non serve una misura nuova, si legge dal conto della copia con il segno opposto. Nessuna prova nuova.
**Decisione del proprietario (5 novembre, sera)**: alla domanda «serve continuare a trovare idee nuove ogni 4 ore?» ho risposto di no
(le idee con dati gratuiti e un perché forte sono quasi finite, e ogni prova in più alza l'asticella per tutte), proponendo di tenere la
raccolta e di migliorare quello che funziona. Lui: «si cambia, e sono d'accordo miglioriamo quello che già funziona». Fatto: la routine
delle 4 ore ora si chiama «Raccolta dati e miglioramento di G1» (raccolta e controlli sempre, poi una voce del piano, un'idea nuova solo
con un perché forte); il piano è `research/programma7/MIGLIORARE_G1.md` (6 voci: demo contro paper, prezzo vero degli ordini, funding
incassato, monete che il demo non ha, meno scambi solo se le spese vere sono più alte, l'ora della decisione). Voce 1 avviata: il rapporto
di stato ha una sezione nuova che confronta giorno per giorno il rendimento di G1 sul demo e nel paper (`scripts/state_snapshot.py`, due
test); richiesta «stato» al canale ops (0698) per la prima lettura.
**Migliorare G1, voce 1, prima lettura (21:15)**: dal 25 ottobre al 5 novembre (12 giorni) **G1 sul demo +6,80%, nel paper +6,92%**;
differenza media −0,011% al giorno con un'oscillazione di 0,62% al giorno, cioè nessun costo nascosto misurabile: gli ordini veri
eseguono come il paper ipotizza (`ops/results/0698-5nov-stato-demo-contro-paper.md`). Due giorni che si compensano (29 ottobre +1,21%,
30 ottobre −1,54%) vengono probabilmente dall'ora dell'ultimo valore del giorno. Demo a 5.277,11 USDT (+5,69% dal 24 ottobre), ordini
limite eseguiti 435 su 453. **Capito oggi**: l'ipotesi più fragile di G1 (gli ordini limite) regge sul demo; la voce «meno scambi» non
ha motivo per ora. Prossimo passo: scomporre il guadagno del demo in prezzo, spese e funding veri (voci 2-3).
**Migliorare G1, voci 2-3** (sì del proprietario, sera del 5 novembre: «ok procedi pure con le due letture e il riavvio»): il demo ora
legge dal conto il funding incassato e le commissioni pagate davvero, giorno per giorno dal 24 ottobre, e il paper scrive i suoi totali
di spese e funding nel diario del giorno; il rapporto di stato li mette a confronto. Solo letture, gli ordini non cambiano. Quattro test
nuovi, 2.496 test passano. Riavvio del bot chiesto alla macchina (ops 0699), poi il log e lo stato per controllare.
**Migliorare G1, voci 2-3, prima lettura (22:56)**: dal 24 ottobre al 5 novembre il demo ha incassato **72,54 USDT di funding** e pagato
**8,42 USDT di commissioni**, su un guadagno di 239,92 USDT: funding +1,45% del capitale, commissioni −0,17%, prezzo circa +3,5%
(`ops/results/0703-6nov-stato-entrate-dal-24-ottobre.md`). Il funding del giorno è salito da 0,02-0,07% a fine ottobre a 0,16-0,23% dal
30 ottobre. Corretto il rapporto (i giorni prima del diario prendono l'equity dai valori del giorno; totali in USDT; un test). **Capito
oggi**: sul conto vero G1 esegue come il paper (12 giorni, differenza −0,02% al giorno, dentro il rumore), il funding c'è davvero (un
terzo del guadagno) e le commissioni sono piccole (circa un trentesimo del funding negli ultimi giorni).

### 6 novembre 2026 (00:30 UTC)

**Giro delle 00:17.** Notizie: 83 articoli nuovi da 22 fonti su 22; 39 conti di Hyperliquid letti. Controlli in avanti delle 00:21: niente
di nuovo. Idee nuove: niente di nuovo. **Migliorare G1, voce 4**: la moneta che il demo rifiuta ogni giorno (龙虾USDT) non è mai stata
nella ricerca sul passato (l'archivio non ha simboli con caratteri cinesi), mentre il bot la mette in G1 dal listino vivo; il rapporto di
stato ora scrive il peso che il paper le dà (un test; 2.498 test passano). Richiesta «stato» (ops 0704) per la lettura.
**Migliorare G1, voce 4, lettura (00:27)**: 龙虾USDT pesa −1,41% nel paper G1 (venduta), il demo ne è privo: poco, si lascia così. Nella
decisione del 6 novembre il demo segnala anche ICPUSDT come moneta che sul demo non c'è; il rapporto ora scrive anche il suo peso.
**Giro delle 04:17.** Notizie: 36 articoli nuovi da 22 fonti su 22; 39 conti di Hyperliquid letti; controlli in avanti delle 04:21: niente
di nuovo; idee nuove: niente di nuovo. **Migliorare G1, voce 3**: il paper G1 dal 23 ottobre ha incassato 155,21 USDT di funding su
10.000 (1,55%) e pagato 16,34 di spese (0,16%); il demo dal 24 ottobre 72,54 su 4.992,87 (1,45%) e 8,42 di commissioni (0,17%):
**combaciano**. **Capito oggi**: con il rendimento (voce 1), il funding e le spese (voci 2-3) e le monete mancanti (voce 4), G1 sul conto
vero fa quello che il paper calcola; l'esecuzione non ha niente da correggere. Voce 6: nel paper dal 23 ottobre G1 +4,14%, G11 +6,81%,
G1N +7,08% (dal 25): troppo pochi giorni per dire quale decide meglio.
**G1 con 250 euro (06:10).** Il proprietario: «voglio partire con 250 euro». Prova 148 (`research/programma7/OTTANTASEIESIMA.md`, regole
spinte prima del calcolo; risultati in `RISULTATI_OTTANTASEIESIMA.md`): 250 euro sono 280 USDT (cambio 1,1209 di Binance); i minimi veri
del listino di oggi (5 USDT quasi per tutti, 20 per ETH, BCH, LTC, ETC, LINK, 50 per il Bitcoin con il passo di 0,001). Sul passato
2021-2026, G1 come lo esegue il bot oggi con 280 USDT: **Sharpe 1,90 contro 1,98 senza minimi**, +57,8% l'anno, discesa −26,8%, ogni anno
positivo, 6,6 ordini al giorno invece di 55,7. Passa l'esame scritto prima. Permettere le chiusure sotto il minimo peggiora (1,83); 10
monete per lato peggiora (1,72, discesa −39,5%). **Capito oggi**: con poco capitale il minimo di Binance fa da banda e costa poco; il bot
non va toccato; il bordo è intorno ai 220 USDT (200 USDT 1,66, 150 USDT 1,49). `DRY_RUN` resta vero: i soldi veri solo con la richiesta
esplicita, ripetuta e consapevole del proprietario.
**Il demo da 280 USDT (07:00).** Il proprietario: «le chiavi di binance future reali le hai già, si posso usare future binance da
svizzera, spegni eventi», e chiede se il bot si adatta al valore del conto (sì: a ogni ribilancio le posizioni si calcolano sul valore
letto in quel momento). Il demo ora lavora come un conto di 280 USDT (`ops/demo_binance_capitale`), con i filtri degli ordini del
conto vero; la fase a 5.000 passa in `/demo_binance/fasi/`; eventi spenti sul demo (il paper degli eventi resta acceso). Tre test nuovi;
riavvio del bot chiesto alla macchina. Le chiavi del conto vero restano sulla macchina, non lette e non usate: `DRY_RUN` vero.
**Giro delle 08:17.** Notizie: 27 articoli nuovi da 22 fonti su 22; 39 conti di Hyperliquid letti; controlli in avanti delle 08:25:
niente di nuovo (nessuna chiusura dopo il 21 ottobre; su Coinbase CT e STABLE come prima). Idee nuove: niente di nuovo. **Migliorare
G1, voce 7**: sul passato il guadagno di prezzo di G1 (+32,9% l'anno) viene per il 43% dalle comprate che fanno meglio della media e per
il 57% dalle vendute che fanno peggio; le tre fasce di grandezza contribuiscono tutte (1-10 +7,3%, 11-50 +14,5%, 51-100 +11,1% l'anno);
nel 2026 il lato venduto perde (−20,2%). **Trovato e corretto**: il 28 ottobre 2026 manca nell'archivio pubblico di Binance per tutte le
monete; riempito dall'interfaccia pubblica per la ricerca (programma 6, 878 monete; programma 5, 100 monete, minuti); il conto a
tavolino del programma 6 della settimana dal 26 ottobre è cambiato, la prova in avanti del programma 5 è stata rifatta. Il bot non ne
risentiva. **Capito oggi**: i due lati di G1 si danno il cambio negli anni; e un archivio pubblico può perdere un giorno intero senza
dirlo: da qui `buchi_archivio.py` lo controlla.
**Giro delle 12:17.** Notizie: 93 articoli nuovi da 22 fonti su 22; 39 conti di Hyperliquid letti; controlli in avanti delle 12:22: niente
di nuovo. Idee nuove: niente di nuovo. **Il demo da 280 dopo cinque ore**: posizioni come voluto a meno del 14,3% del conto (la prova 148
si aspettava circa il 14%); il Bitcoin non si compra (il passo vero vale 78 USDT, G1 ne vuole 20). Il valore è sceso da 278,17 a 267,08
nell'ora del passaggio da 5.000 a 280 (le posizioni vecchie ancora aperte); dopo, fino a mezzogiorno, +0,34% contro +0,19% del paper.
**Capito oggi**: la fase da 280 si misura dalle 08:00 (267,08); con i soldi veri il passaggio non c'è.
**Voce 7, il lato venduto nel 2026**: la perdita (−13,8% rispetto alla media, dal 1° gennaio al 4 ottobre) sta tutta in giugno-agosto e
in 12 monete (−50,6% insieme: H, DEXE, VVV, LIT, BAS, HYPE, XMR...), con il funding alto e il prezzo che ha continuato a salire; le
altre vendute guadagnano +36,8%. Nessuna prova nuova (il tetto per moneta peggiorava già, prova 61).
**Giro delle 16:17.** Notizie: 140 articoli nuovi da 22 fonti su 22, ma BeInCrypto e Crypto Briefing avevano la pagina piena (qualche
articolo fra un giro e l'altro può essere perso); 39 conti di Hyperliquid letti; controlli in avanti delle 16:22: niente di nuovo. Idee
nuove: niente di nuovo. **Voce 8**: il demo ora conta a ogni ribilancio le variazioni che restano sotto il minimo di Binance (solo
lettura); riavvio chiesto alla macchina (ops 0709), detto prima al proprietario.
**Giro delle 20:17.** Notizie: 95 articoli nuovi da 22 fonti su 22 (Crypto Briefing piena solo nella prima pagina: la seconda la
copre); 39 conti di Hyperliquid letti; controlli in avanti delle 20:22: niente di nuovo. Idee nuove: niente di nuovo. BeInCrypto era
stata piena due volte oggi (12 articoli, circa 5 ore): da oggi si legge anche la sua seconda pagina (23 fonti). G1: niente di nuovo da
misurare prima del ribilancio della mezzanotte, il primo vero del demo da 280 (demo a 267,99 alle 15:59, come alle 08:00).

### 7 novembre 2026 (00:30 UTC)

**Giro delle 00:17.** Notizie: 49 articoli nuovi da 23 fonti su 23 (con la seconda pagina di BeInCrypto), nessuna piena; 39 conti di
Hyperliquid letti; controlli in avanti delle 00:22: niente di nuovo. Idee nuove: niente di nuovo. **Il primo ribilancio vero del demo da
280**: 5 ordini, 50 variazioni sotto il minimo di Binance (19,2% del conto): il 91% saltate, come la prova 148 diceva (90%). **Capito
oggi**: con 280 USDT G1 sul conto vero si comporta come previsto sul passato.
**Giro delle 04:17.** Notizie: 13 articoli nuovi da 23 fonti su 23, nessuna piena; 39 conti di Hyperliquid letti; controlli in avanti
delle 04:22: niente di nuovo. Idee nuove: niente di nuovo. G1: niente di nuovo da misurare (demo a 268,34 alle 01:01, con i 5 ordini
del giorno ancora in corso); la prossima lettura è il riepilogo di lunedì.
**Il demo a 1.000 dalla mezzanotte (06:00).** Il proprietario: «cancella i 280 in demo e riparti a mezzanotte con il demo a 1000». Il
demo ora tiene un capitale nuovo in attesa fino alla decisione di G1 dopo, e lì chiude tutto, archivia la fase e riapre da zero (come
farà il conto vero). Prima il riavvio con il codice nuovo, poi il file a 1.000 (con il codice vecchio sarebbe partito subito).
**Giro delle 08:17.** Notizie: 16 articoli nuovi da 22 fonti su 23; 35 conti di Hyperliquid letti su 39; controlli in avanti delle 08:20:
niente di nuovo. Idee nuove: niente di nuovo. G1: il rapporto di stato delle 07:03 mostra il capitale nuovo da 1.000 USDT in attesa della
mezzanotte (demo a 268,52 sui 280); niente di nuovo da misurare prima del ribilancio.
**Giro delle 12:17.** Notizie: 38 articoli nuovi da 22 fonti su 23; 39 conti di Hyperliquid letti; controlli in avanti delle 12:20:
niente di nuovo. Idee nuove: niente di nuovo. G1: niente di nuovo da misurare prima della mezzanotte. **I subagent** (richiesta del
proprietario): quattro agenti in `.claude/agents/`, blocco dei segreti, regole dei token in `CLAUDE.md`; collaudo in
`docs/collaudo_agenti.md` (auditor FAIL con i tre errori voluti, segreti bloccati, revisore REQUEST CHANGES); il revisore ha trovato
un problema vero (la parità col backtest spegne i fermi: backlog P26). **Capito oggi**: un revisore indipendente con una checklist
fissa trova anche ciò che non gli si chiede.
**Giro delle 16:17.** Notizie: 51 articoli nuovi da 22 fonti su 23; 39 conti di Hyperliquid letti; controlli in avanti delle 16:20:
niente di nuovo. Idee nuove: niente di nuovo. **Percorso degli ordini**: corretti i 9 problemi Alti della revisione e i problemi nuovi
25-33, approvati dal revisore (commit 013f9426); gli allarmi del demo ora si vedono in dashboard e nel rapporto. Il riavvio aspetta
l'ok del proprietario. **Capito oggi**: una correzione può aprire un problema nuovo (il 25, posizione doppia dopo un annullo
rifiutato): la seconda revisione l'ha trovato prima che girasse.
**Riavvio con le correzioni (18:54 UTC)**, ok del proprietario («ok riavvia adesso»): il bot gira il commit 78bb70e3, che contiene le
correzioni approvate (013f9426); la riga nuova d'avvio dice `DRY_RUN=True, BINANCE_TESTNET=False, BACKTEST_PARITY=True` (la parità
col backtest è quella del vecchio paper, permessa solo con `DRY_RUN` vero: con `DRY_RUN` falso l'avvio ora si rifiuta). Nessun errore
nel log dopo l'avvio (`ops/results/0718-7nov-log-dopo-riavvio-correzioni.md`).
**Giro delle 20:17.** Notizie: 36 articoli nuovi da 23 fonti su 23; 39 conti di Hyperliquid letti; controlli in avanti delle 20:20:
niente di nuovo. Idee nuove: niente di nuovo. G1: niente di nuovo da misurare prima della mezzanotte (demo a 268,12 sui 280, il
capitale da 1.000 in attesa della decisione di G1).

### 8 novembre 2026 (00:20 UTC)
**Giro delle 00:17.** Notizie: 21 articoli nuovi da 22 fonti su 23; controlli in avanti delle 00:20: niente di nuovo. Idee nuove:
niente di nuovo. **Il demo a 1.000 è partito da zero alla mezzanotte, come chiesto dal proprietario.** Alle 00:18:20 il demo ha chiuso
le 52 posizioni della fase da 280 con 0 errori (valore vero del conto demo 5.347,91), alle 00:19:09 la decisione di G1 ha messo 48
ordini limite, 1 rifiutato (龙虾USDT, «Invalid symbol», come ogni giorno; ICPUSDT sul demo non c'è). Primo stato: equity 999,59 su
1.000 (−0,04%, le spese d'ingresso), 19 posizioni lunghe e 9 corte già eseguite, sotto il minimo di Binance solo **2 variazioni (0,8%
del conto) contro le 50 (19,2%) della prima notte a 280**; stop sul conto a 650 (`ops/results/0719-8nov-log-passaggio-1000.md`,
`0720-8nov-stato-passaggio-1000.md`). **Capito oggi**: la partenza da zero alla mezzanotte funziona senza errori ed è quella che farà il
conto vero; il primo giorno però apre tutto da zero (ordini grandi), quindi la misura vera dei minimi a 1.000 è il ribilancio di domani
notte (la prova 148 se ne aspetta eseguibile il 23% delle variazioni, il 77% del giro).
**Giro delle 04:17.** Notizie: 18 articoli nuovi da 22 fonti su 23; 39 conti di Hyperliquid letti su 39; controlli in avanti delle
04:22: niente di nuovo. Idee nuove: niente di nuovo. **Il demo a 1.000 dopo quattro ore** (`ops/results/0721-8nov-stato-demo-1000-dopo-4-ore.md`):
dei 48 ordini di G1, 45 eseguiti a limite e 3 a mercato, nessuno in attesa; 24 posizioni lunghe e 24 corte; equity 1.001,80 (+0,18%),
stop sotto 652,35. Scarto fra posizioni vere e volute 7,5% del conto, quasi tutto dalle due monete che il demo non ha (ICPUSDT 4,3%,
龙虾USDT 1,9%); nessun errore nuovo (l'ultimo è del 24 ottobre).
**Mattino delle 06:13 (domenica).** Notizie: 7 articoli nuovi da 22 fonti su 23; 39 conti di Hyperliquid letti; la copia dei trader
aggiornata (`research/trader_copiati/HYPERLIQUID_CONTO.md`). **La prova in avanti del programma 5 e il paper delle candidate del
programma 6 oggi non sono stati aggiornati**: il disco del contenitore di questa sessione ha settori illeggibili (428 errori di lettura
nel registro del sistema). Prima erano illeggibili tutti i file di pandas (sostituiti con una copia nuova), poi alcuni archivi dei prezzi
scaricati da Binance: i due calcoli si fermano con «Bus error» mentre li leggono. Gli scarichi dei dati nuovi sono andati a buon fine e
sono committati. È un guasto della macchina della sessione, non del bot (che gira sulla VPS). Per rimediare bisogna trovare gli archivi
rovinati nella cartella dei dati e riscaricarli; la lettura di quella cartella è vietata dalle regole dei token, quindi si chiede al
proprietario.
**Giro delle 08:17.** Notizie: 11 articoli nuovi da 23 fonti su 23; 39 conti di Hyperliquid letti. **Contenitore nuovo**: la sessione
gira su una macchina nuova, con il disco sano (0 errori di lettura), ma senza la cartella dei dati di mercato e senza i file di lavoro.
Lo script dei controlli in avanti, che stava fra i file di lavoro, ora è nel repo (`research/programma7/controlli_avanti.py`) con
l'elenco delle monete già viste (`controlli_avanti_coinbase.json`, 246 monete su Coinbase con il perpetuo di Binance): le prime candele
di Coinbase dal 5 ottobre mostrano solo due monete quotate dopo il 6 ottobre, PONS (7 ottobre, prima della misura in avanti) e STABLE
(27 ottobre, già in tabella). Controlli delle 08:30: niente di nuovo. Idee nuove: niente di nuovo. Gli aggiornamenti del mattino dei
programmi 5 e 6 ripartono adesso, con i dati riscaricati da zero.
**Giro delle 12:17.** Notizie: 30 articoli nuovi da 23 fonti su 23; 39 conti di Hyperliquid letti; controlli in avanti delle 12:20:
niente di nuovo (246 monete su Coinbase con il perpetuo, nessuna nuova). Idee nuove: niente di nuovo. G1: niente di nuovo da misurare
prima del ribilancio di mezzanotte (la misura vera dei minimi a 1.000 USDT). Nella mattina: due agenti nuovi (chi migliora le
strategie in corso, chi sceglie quale usare in produzione), la regola del proprietario che nessuna strategia del paper o del demo si
spegne (con il suo test), e la fase 1 del conto vero (i problemi rimasti del demo) approvata dal revisore al quarto giro
(`docs/conto_vero.md`); il riavvio del demo aspetta l'ok del proprietario. **Capito oggi**: ogni giro di correzioni sul percorso
degli ordini ha aperto un problema nuovo (40, 47, 50), sempre trovato dal revisore prima del commit: la revisione a giri serve.
**Giro delle 16:17.** Notizie: 40 articoli nuovi da 23 fonti su 23; 39 conti di Hyperliquid letti; controlli in avanti delle 16:20:
niente di nuovo. Idee nuove: niente di nuovo. G1: niente di nuovo da misurare prima del ribilancio di mezzanotte. La prova in avanti
del programma 5 è aggiornata con i dati scaricati da zero (le operazioni di ieri identiche); il paper delle candidate del programma 6
è ancora in corso (lo scarico da zero dei dati di tutte le monete richiede più di due ore).
**Riavvio con la fase 1 del conto vero (19:02 UTC)**, ok del proprietario («ok riavvia il demo, G1 neutra la decide l'allocatore
lunedì»): il bot gira il commit 83ddb809, che contiene la fase 1 approvata (1a8522f; nessuna modifica al bot dopo); riga d'avvio
`DRY_RUN=True, BINANCE_TESTNET=False, BACKTEST_PARITY=True`, nessun errore (`ops/results/0722-*`, `0723-*`). Stato delle 19:04
(`0724-*`): demo a 994,82 su 1.000, 24 posizioni per lato, nessun allarme; lo stop dice il livello nuovo (652,35, il più alto fra −35%
dal massimo e il 65% del capitale). La scelta fra G1 e G1 neutra per i soldi veri la fa portfolio-allocator lunedì.
**Giro delle 20:17.** Notizie: 38 articoli nuovi da 23 fonti su 23; 39 conti di Hyperliquid letti; controlli in avanti delle 20:20:
niente di nuovo. Idee nuove: niente di nuovo. G1: niente di nuovo da misurare prima del ribilancio di mezzanotte; il demo ha fatto il
primo giro con la fase 1 alle 19:05 senza errori né allarmi (`ops/results/0725-*`). Conto vero, fase 2 (il codice spento): la prima
revisione dice REQUEST CHANGES (due Alti: le protezioni con il conto spento e la versione approvata; nessun Bloccante; con `DRY_RUN`
falso il vecchio sistema non manda ordini né chiude posizioni, verificato), correzioni in corso; le decisioni del proprietario sono in
`reviews/reports/2026-11-08-fase2-conto-vero.md`.
**Conto vero, fase 2 (sera)**: il codice del conto vero di Binance per G1 è committato **spento** (ff89531), approvato da
live-path-reviewer al terzo giro più il controllo del problema 71. Il canale della macchina, che ora porta anche il tag della versione
approvata, risponde (`ops/results/0726-*`: la fotografia dice «conto vero spento»). Il bot lo caricherà al prossimo riavvio, con l'ok
del proprietario; prima dell'accensione restano la protezione del tag, i problemi 66, 70, 72, 73, la dashboard e le decisioni del
proprietario (`docs/conto_vero.md`). **Capito oggi**: con i soldi veri il punto debole non è il codice degli ordini ma chi può dire
«questa versione è approvata»: oggi lo può fare anche una sessione.
