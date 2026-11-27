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

### 9 novembre 2026 (00:25 UTC)
**Giro delle 00:17.** Notizie: 41 articoli nuovi da 22 fonti su 23; 39 conti di Hyperliquid letti; controlli in avanti delle 00:20:
niente di nuovo. Idee nuove: niente di nuovo. **G1 sul demo a 1.000, il primo ribilancio normale** (`ops/results/0727-*`, `0728-*`):
19 ordini, 38 variazioni sotto il minimo di Binance (6,7% del conto), quindi eseguibile il 33% delle variazioni contro il 23% atteso
dalla prova 148 e il 9% a 280; equity 995,20 (−0,48% dalla partenza dell'8 novembre, spese d'ingresso comprese). **Capito oggi**: a
1.000 USDT il demo esegue un terzo delle variazioni di ogni giorno, più di quanto la prova sul passato prevedeva (un giorno solo).
**Giro delle 04:17.** Raccolta e controlli in avanti delle 04:20: niente di nuovo; idee nuove: niente di nuovo; G1: niente di nuovo da
misurare dopo il ribilancio di mezzanotte (la misura dei minimi è sopra).
**Riepilogo della settimana al proprietario (lunedì 9 novembre, mattina).** Paper dal 2 al 9 novembre (`ops/results/0690-*` e
`0729-*`): G1 +3,39%, G1 neutra +3,75%, G11 +4,03%, F5 +3,47%, eventi fermi (nessuna operazione). Demo a 1.000 dall'8 novembre: +0,27%.
Primo confronto di gate2-reconciler (`gate2/reports/2026-11-09-G1.md`): paper e demo seguono la ricerca (correlazione dei giorni 0,94 e
0,99), costi del demo a limite +26% sugli assunti, un giorno non spiegato (30 ottobre), soglie proposte da approvare. Primo giro di
portfolio-allocator (`allocazione/reports/2026-11-09.md`): regole proposte da approvare; applicandole uscirebbe «tieni G1»; nessuna
proposta di soldi veri possibile oggi (parità non ancora dimostrata).
**Giro delle 08:17.** Raccolta e controlli in avanti delle 08:20: niente di nuovo; idee nuove: niente di nuovo; G1: niente di nuovo da
misurare fino al ribilancio di stanotte. In attesa del proprietario: le regole dell'allocatore (miscela sopra i 500 USDT), le soglie
del confronto settimanale e le decisioni del conto vero.
**Giro delle 12:17.** Raccolta e controlli in avanti delle 12:20: niente di nuovo; idee nuove: niente di nuovo; G1: niente di nuovo da
misurare fino al ribilancio di stanotte.
**Giro delle 16:17.** Raccolta e controlli in avanti delle 16:20: niente di nuovo; idee nuove: niente di nuovo; G1: niente di nuovo da
misurare fino al ribilancio di stanotte.
**Giro delle 20:17.** Raccolta e controlli in avanti delle 20:20: niente di nuovo; idee nuove: niente di nuovo; G1: niente di nuovo da
misurare fino al ribilancio di stanotte. Nota sul giro delle 12:17: «piena» si riferiva alla sola prima pagina di Crypto Briefing; la
seconda pagina si legge dal 4 novembre e non era piena, quindi nessun articolo perso.
Le monete su Coinbase con il perpetuo di Binance passano da 246 a 245: TNSR è stata tolta da Coinbase (`TNSR-USD` «delisted»), mentre il
perpetuo di Binance è ancora attivo. Non tocca la misura in avanti delle quotazioni nuove (conta solo le entrate).

### 10 novembre 2026 (00:25 UTC)
**Giro delle 00:17.** Notizie: 77 articoli nuovi da 23 fonti su 23; controlli in avanti delle 00:20: niente di nuovo; idee nuove:
niente di nuovo. **G1 sul demo a 1.000, secondo ribilancio**: 8 ordini e 46 variazioni sotto il minimo (15% eseguibile); sui due giorni
il 24%, come la prova 148 prevedeva (23%); lo scarto dalle posizioni volute sale al 13,9% del conto. Demo +0,40% dall'8 novembre,
paper di G1 −0,97% negli stessi giorni (`ops/results/0730-*`, `0731-*`). **Capito oggi**: la prova sul passato con i minimi veri
prevede bene quanta parte del giro il conto piccolo riesce a eseguire.
**Giro delle 04:17.** Raccolta e controlli in avanti delle 04:20: niente di nuovo; idee nuove: niente di nuovo; G1: niente di nuovo da
misurare dopo il ribilancio di mezzanotte.
**Mattino delle 06:13 (martedì).** Notizie: 30 articoli nuovi da 22 fonti su 23; copia dei trader di Hyperliquid aggiornata. Prova in
avanti del programma 5 (dati fino all'8 novembre): M-001c 326 su 400, M-002 e M-003 non passano. **Il conto a tavolino del programma 6
era fatto su un giorno a metà**: l'archivio di Binance aveva l'8 novembre per 232 monete su circa 715, e le decisioni settimanali del
lunedì 9 uscivano con 70 monete «nuove nell'universo» invece di 22. Corretto il pannello (`research/programma6/seconda.py`,
`giorni_parziali_in_coda`: un ultimo giorno con meno del 90% delle monete del giorno prima non si usa; test nuovo) e rifatto il conto
quando l'8 novembre era completo: 20 monete nuove. Il bot non è toccato (prende i prezzi da Binance, non dall'archivio). **Capito
oggi**: l'archivio pubblico pubblica un giorno nuovo moneta per moneta, nel corso di ore; ogni calcolo sul giorno più recente deve
controllare che sia completo.
**Giro delle 08:17.** Raccolta e controlli in avanti delle 08:20: niente di nuovo; idee nuove: niente di nuovo; G1: niente di nuovo da
misurare fino al ribilancio di stanotte.
**Giro delle 12:17.** Raccolta e controlli in avanti delle 12:20: niente di nuovo; idee nuove: niente di nuovo; G1: niente di nuovo da
misurare fino al ribilancio di stanotte. In corso: la dashboard nuova chiesta dal proprietario («pulita semplice e veloce da leggere»).
**Dashboard nuova (10 novembre)**, richiesta del proprietario («pulita semplice e veloce da leggere [...] in tempo reale»): prima
schermata «Strategie» (stato del bot e allarmi del demo in cima; ordini veri, cioè G1 sul demo con i pulsanti e il conto vero spento;
paper: G1, G1 neutra, G11, F5, eventi; le curve a 100 dalla stessa data; G1 demo contro G1 paper giorno per giorno), schede
«Dettagli» e «Archivio» (il vecchio sistema, niente cancellato). Verificata in locale con dati finti (modulo `dashboard/prova/`, attivo
solo con `DASHBOARD_PROVA=1`, mai su Vercel): tsc e build riusciti. Mancano nel bot la data e il capitale di partenza di ogni ramo.
**Giro delle 16:17.** Raccolta e controlli in avanti delle 16:20: niente di nuovo; idee nuove: niente di nuovo; G1: niente di nuovo da
misurare fino al ribilancio di stanotte.
**Dashboard, seconda versione (10 novembre)**, dalle osservazioni del proprietario: in «Strategie» il confronto demo-paper diventa una
scheda corta (due numeri, la differenza, due piccole curve); «Dettagli» rifatta come «Strategie» (si sceglie la strategia; riquadri,
barre del giorno per giorno, pesi a barre, ultimo ribilancio, conto demo, il confronto giorno per giorno chiuso); «Archivio» com'era.
Scheda «Azioni» vuota per la sessione delle azioni, con i mattoni comuni (`dashboard/app/components/comuni/`) e la guida
`dashboard/GUIDA_SCHEDA_AZIONI.md` (scelta del proprietario: «la prima, prepara la scheda e la guida»). tsc e build riusciti, provata
con dati finti.
**Dashboard, terza versione (10 novembre)**: si chiama «Plancia»; in alto solo le aree (Crypto, Azioni), a sinistra il menu delle
pagine dell'area (sul telefono un pulsante che apre il menu); colonne giorno per giorno verdi in guadagno e arancioni in perdita; la
guida delle azioni dice come dichiarare le loro pagine. tsc e build riusciti, provata con dati finti.
**Giro delle 20:17.** Raccolta e controlli in avanti delle 20:20: niente di nuovo; idee nuove: niente di nuovo; G1: niente di nuovo da
misurare fino al ribilancio di stanotte. Dashboard: menu di sinistra richiudibile anche sul computer; la sessione delle azioni ha
riempito la sua area (pubblicazione su Firebase sotto `/azioni`, pagina «Operazioni»).

### 11 novembre 2026 (00:25 UTC)
**Giro delle 00:17.** Notizie: 57 articoli nuovi da 24 fonti su 24; controlli in avanti: niente di nuovo; idee nuove: niente di
nuovo. **G1 sul demo a 1.000, terzo ribilancio**: 7 ordini e 47 variazioni sotto il minimo; sui tre giorni eseguibile il 20% (atteso
23%); scarto dalle posizioni volute 15,8% del conto e in crescita; demo +0,27% dall'8 novembre, paper di G1 −0,87% (`ops/results/0732-*`,
`0733-*`). **Capito oggi**: con il conto piccolo le posizioni vere si allontanano piano dalle volute; finora il demo fa meglio del paper
(un punto in tre giorni), ma tre giorni non dicono niente.
**Giro delle 04:17.** Raccolta e controlli in avanti delle 04:20: niente di nuovo; idee nuove: niente di nuovo; G1: niente di nuovo da
misurare dopo il ribilancio di mezzanotte.
**Mattino delle 06:13 (mercoledì).** Notizie: 22 articoli nuovi da 23 fonti su 24; copia dei trader aggiornata. Prova in avanti (dati
fino al 9 novembre): M-001c 332 su 400 (−0,39% a trade). Conto a tavolino (dati fino al 9 novembre, 20 monete nuove nell'universo, il
giorno a metà non c'era): DXI per la prima volta sopra G1 sulle stesse monete (+4,45% contro +3,87% in 7 giorni); HLI −2,03% contro
+2,89%. Sette giorni: informazione, non verdetto.
**Le aree del repository (11 novembre)**, richiesta del proprietario («una cartella con crypto dove ci scrivi solo tu, una cartella
con stock dove ci scrive l'altra sessione e altre cartelle che magari creo dopo tipo Forex»): la mappa `AREE.md` e il blocco nel
codice `.claude/hooks/aree.py` (mappa `AREE.json`, test `tests/test_hook_aree.py`, 37 casi): ogni sessione scrive solo nella sua area e
nei file in comune; le due sessioni sono registrate (crypto e «trading stock»). Il trasloco delle crypto in `crypto/` è rimandato per
non fermare il bot sulla macchina. 2.730 test passano (la firma a parte).
**Giro delle 08:17.** Raccolta e controlli in avanti delle 08:20: niente di nuovo; idee nuove: niente di nuovo; G1: niente di nuovo da
misurare fino al ribilancio di stanotte.
**Giro delle 12:17.** Raccolta e controlli in avanti delle 12:20: niente di nuovo; idee nuove: niente di nuovo; G1: niente di nuovo da
misurare fino al ribilancio di stanotte.
**Gli eventi fermi (11 novembre, domanda del proprietario).** Il paper degli eventi non apre da giorni perché mancano gli eventi, non
per un guasto: Binance quota pochissimi perpetui nuovi (dai contratti esistenti oggi, `exchangeInfo`: 31 a settembre 2025, 29 a ottobre
2025, poi 2-3 al mese da luglio 2026; negli ultimi 30 giorni uno solo, PREDICTUSDT, che è un contratto «pre-market» e non una moneta,
quindi escluso). Le monete appena quotate (N3) non hanno materia prima; il funding al tetto (E4) è raro per natura. **Capito oggi**: una
strategia a eventi dipende dal ritmo delle quotazioni, che nel 2026 è sceso di circa dieci volte. **Ricerca nuova ripartita**: la
prova 149, la 1:1:1 (regole in `research/programma7/OTTANTASETTESIMA.md`), affidata a strategy-researcher.
**Prova 149, la 1:1:1 (11 novembre)**: 10 monete (le più scambiate nel 2023: BTC, ETH, SOL, XRP, DOGE, APT, BNB, LTC, MATIC, BCH) × 4
ore e un giorno × tendenza, rottura e ritorno alla media, con i parametri fissi: **0 combinazioni su 60 passano l'esame** (t più alto
2,42, Sharpe corretto più alto 0,10 con 306 prove; `research/programma7/RISULTATI_OTTANTASETTESIMA.md`). Le migliori rendono molto ma
non tutti gli anni (MATIC 1d rottura +123% l'anno, 3 anni su 4). **Capito oggi**: anche a 4 ore e a un giorno le regole classiche sul
prezzo di una moneta sola non reggono l'esame; conferma la lezione di ottobre (i vantaggi che reggono vengono da ragioni economiche,
non dagli indicatori). Agente nuovo strategy-scout per le idee; il giro delle 4 ore fa avanzare la ricerca nuova a ogni giro.
**Prova 150, l'asimmetria dei minuti (11 novembre, proposta da strategy-scout)**: **no**. Finestra di 7 giorni −1,4% l'anno (Sharpe
−0,04, 3 anni su 6: +35,9% nel 2021, −50,1% nel 2026), finestra di 30 giorni −10,8% l'anno; correlazione con G1 circa zero, la miscela
50/50 con G1 peggiora G1 (`research/programma7/RISULTATI_OTTANTOTTESIMA.md`; 450 monete, minuti dal 2021 scaricati dall'archivio). Il
conto delle prove è 308. **Da sistemare**: sul disco nuovo le candele a 1 ora della ricerca (`research/data/p6h`) ci sono solo per
pochi giorni e 10 monete, quindi i ricalcoli di G1 nella ricerca trattano quasi tutti gli ordini limite come ordini a mercato;
vanno riscaricate (`python3 -m research.programma6.scarico_ore`) prima del prossimo confronto settimanale. **Capito oggi**: due idee
nuove provate e scartate in un giorno, con le regole scritte prima; il fattore «lotteria» pubblicato sulle azioni sulle crypto
funzionava nel 2021-2023 e poi si è rovesciato.
Le candele a 1 ora della ricerca sono di nuovo complete: riscaricate dall'archivio di Binance per le 360 monete passate nell'universo di
G1 dal 2021, senza errori; impronte unite in `research/programma6/scarico_ore.json`.
**Prova 151, il weekend dei perpetui su azioni (11 novembre, strategy-scout)**: «dati troppo corti» (23 lunedì da giugno, 123 contratti
su azioni americane), e i numeri sono negativi: −9,6% l'anno, le spese 3,6 volte il guadagno lordo (`research/programma7/RISULTATI_OTTANTANOVESIMA.md`).
Si ricalcola a tavolino una volta al mese. **Riesame** (idea 137): l'elenco delle prove bocciate di poco è in `research/riesame/ELENCO.md`;
la prima, la miscela F5 + M7 + K2 della prova 28, con l'esame corretto del 22-23 ottobre avrebbe lo Sharpe corretto 0,94 e 5 anni su
5: è da backtest-auditor. Conto delle prove 309.
**Riesame, prova 28 (F5 + M7 + K2), backtest-auditor**: **PASS tecnico** (numeri rifatti con i dati di oggi: miscela Sharpe 2,15,
t 4,73, 5 anni su 5, discesa −28,4%; nessuno sguardo nel futuro; con costi doppi 2,01; `audits/reports/2026-11-11-PROVA28_K2_F5M7K2.md`).
Due Alti sull'esame: lo Sharpe corretto è 0,75 contando le prove del registro (309) e 0,89 contando i gruppi di prove simili (80), con
la soglia a 0,80; e le regole scritte prima la dichiarano una «costruzione» che non diventa candidata (scelte fatte dopo aver visto i
risultati). Decisioni chieste al proprietario. A 280 USDT la miscela scende a 1,53; K2 e M7 non esistono nel bot.
**Decisioni del proprietario (11 novembre, sera)**: «famiglie e misurala a tavolino». Lo Sharpe corretto conta le famiglie di prove
simili (per la miscela 0,89, sopra la soglia di 0,80); la miscela F5 + M7 + K2 è già nel conto a tavolino del programma 6 (+2,70% nelle
prime 2 settimane, `research/programma6/paper/PAPER.md`) e andrà nel riepilogo di ogni lunedì. Le prove 149-151 non cambiano verdetto
con il conto per famiglie (t sotto 3 e rendimenti negativi o quasi nulli).
**Riesame, prova 113 (le monete nuove distribuite gratis)**: resta bocciata anche con i dati corretti (p 0,0268 contro 0,01). Il
riesame ha trovato un errore vecchio: il file degli eventi delle monete nuove (prova 32) era di prima di una correzione e aveva perso 19
eventi; il verdetto della 32 non cambia (p 0,0020), ma il file va rifatto e con lui le prove che lo leggono (backlog P32). **Capito
oggi**: il riesame serve anche quando non promuove niente: trova file vecchi che altre prove usano ancora.

### 12 novembre 2026 (00:25 UTC)
**Giro delle 00:17.** Notizie: 88 articoli nuovi da 24 fonti su 24; controlli in avanti: niente di nuovo. **G1 sul demo a 1.000, quarto
ribilancio**: 10 ordini, 43 variazioni sotto il minimo; sui quattro giorni eseguibile il 20% (atteso 23%); scarto dalle volute 12,2%;
demo −0,99% dall'8 novembre contro −2,08% del paper di G1 (`ops/results/0734-*`, `0735-*`). Ricerca: in corso il rifacimento del file
degli eventi delle monete nuove (backlog P32).
**Il file degli eventi delle monete nuove rifatto (backlog P32)**: 632 eventi (19 recuperati); nessun verdetto cambia (prova 32 +4,26%
per evento, p 0,0020; 113 resta bocciata; N3 a portafoglio Sharpe 0,64; G1 più eventi 2,83). Restano l'elenco ufficiale dei contratti
che non sono monete (24 eventi del 2026 su 87 sospetti) e due script vecchi da rifare.
**Giro delle 04:17.** Raccolta (27 articoli da 23 fonti su 24) e controlli in avanti: niente di nuovo. Con l'elenco ufficiale di Binance:
38 degli 87 eventi delle monete nuove del 2026 nella ricerca sono contratti su azioni o fondi (il bot li esclude già); nessuno di questi
contratti è mai entrato fra le 100 monete di G1, quindi G1 non è toccato. Le monete nuove vere del 2026 rendono −0,80% a evento (backlog
P32). **Capito oggi**: nel 2026 Binance quota più contratti su azioni che monete nuove; la ricerca deve riconoscerli dal tipo, non dal
nome.
**Controllo degli agenti e dei punti in sospeso (12 novembre, richiesta del proprietario).** Trovato: la revisione di G1 con
backtest-auditor promessa l'8 novembre non era stata fatta (lanciata ora); la modalità verifica del ricercatore non era mai stata usata
(le prove 149-151 hanno avuto 5-7 letture delle regole scelte da chi calcolava: da oggi si fa prima del calcolo); il piano di G1 non
aveva passi aperti per strategy-improver (aggiunte le voci 9-13); indice della ricerca e stato della sessione fermi al 7-8 novembre
(aggiornati). Sui punti per il proprietario: **la regola di GitHub consigliata l'8 e l'11 novembre non basta**, perché la sessione
agisce su GitHub come l'utente del proprietario (`get_me`); nella lista delle sue decisioni ne mancavano quattro chieste dal revisore;
le soglie proposte del confronto settimanale sono già superate per le monete che il demo non ha (ICPUSDT oltre il 2% per quattro
giorni; monete mancanti circa 7% contro 3%). Lista corretta in `docs/conto_vero.md`. **Capito oggi**: rileggere i rapporti invece di
andare a memoria ha trovato un consiglio sbagliato sui soldi veri prima che servisse.
**Le regole di Firebase pubblicate (12 novembre, foto del proprietario)**: chiuse e con il suo identificativo, ma senza i due blocchi dei
comandi del demo: i pulsanti «Chiudi tutto» e «Riparti» del demo in dashboard sono rifiutati da Firebase dal giorno in cui sono nati
(7 novembre); funzionano lo stop automatico e i comandi da file. Dati al proprietario i due blocchi da aggiungere. Per la versione dei
soldi veri ha scelto l'approvazione dalla dashboard: lavoro avviato. **Capito oggi**: un pulsante d'emergenza va provato fino in fondo,
regole pubblicate comprese; averlo nel codice e nei test non basta.
**La revisione di G1 con backtest-auditor (12 novembre)**: PASS tecnico, i conti rifatti da capo tornano (Sharpe 1,98; a 280 USDT 1,90;
ogni anno positivo; nessun dato del futuro). Ma quattro problemi Alti: l'esame passa solo se gli ordini limite pagano davvero la
commissione bassa (a 280 USDT 0,81 contro la soglia 0,80; tutto a mercato 0,77); la soglia scritta prima era 0,95; una moneta venduta
è arrivata al 43,7% del capitale; il funding del demo è circa il 40% sotto il paper negli ultimi due giorni
(`audits/reports/2026-11-12-G1_CONTO_VERO.md`). Avviati il confronto su funding e commissioni e le regole della prova 152 sulla
concentrazione. **Capito oggi**: G1 guadagna davvero sul passato, ma il suo margine sopra l'esame sta tutto nell'ipotesi che gli ordini
limite si eseguano a basso costo, e quella ipotesi sul conto non l'abbiamo mai misurata.
**Prova 152, la concentrazione di G1 (12 novembre)**: il tetto del 20% per moneta dimezza il peso peggiore di una moneta venduta (dal
43,7% al 20,0%) per 0,03 di Sharpe (1,95 contro 1,98) e 2,5 punti di discesa in più; secondo l'esame scritto non passa (ordini saltati a
280 USDT: 8 in più su circa 123.000). Le regole erano state verificate e corrette due volte prima del calcolo (10 ambiguità, poi una
definizione). **Confronto del demo**: funding al 70% del paper in 4 giorni, commissione dell'8 novembre circa 0,038% (stima): servono
le esecuzioni dalla macchina (backlog P33). Conto delle prove 312. **Capito oggi**: limitare il peso di una moneta costa poco sul
passato; quello che non sappiamo è quanto costano davvero gli ordini sul conto.

**Voce 12 di G1, il lato venduto nel 2026 (12 novembre, misura di strategy-improver, `research/programma7/misure_g1/voce12_rapporto.md`)**:
la perdita del lato venduto nel 2026 (−13,4 punti al 4 ottobre: prezzo −20,4, funding +9,4, spese −2,5) è concentrata, non è il
mercato intero: monete piccole −14,5 contro medie +1,8 e grandi −0,7; monete con meno di un anno sul perpetuo −10,0; 176 giornate di
rialzo oltre il 20% su monete vendute (altri anni 22-85) valgono −119,3 sul prezzo; le 10 giornate peggiori valgono −19,7 da sole.
Non è un caso unico (2021 −150,1, 2023 −17,0). Il funding resta normale. **Capito oggi**: G1 perde quando vende monete piccole e
nuove che fanno fiammate; la prova 152 (tetto al peso) tocca proprio questo. Un'uscita dopo un rialzo forte sarebbe una prova nuova,
con le regole scritte prima.
**12 novembre, pomeriggio (cosa abbiamo capito)**: (1) **le commissioni vere del demo** (prima lettura da Binance,
`ops/results/0736-*`): a regime 0,025% del valore scambiato, come il paper; il ribilancio da vuoto costa 0,032% perché metà degli
ordini limite al prezzo mark si eseguono subito a commissione da mercato; commissione del conto demo 0,02% e 0,04%. (2) **Il funding
del paper si perdeva** quando Binance pubblicava un regolamento in ritardo (due difetti in `f5.py`, uno in `eventi.py`, corretti e
approvati, `reviews/reports/2026-11-12-funding-dei-paper.md`; valgono dal prossimo riavvio): il paper incassava un po' meno, quindi lo
scarto del demo (70% del paper) resta da spiegare. (3) **Lo Sharpe corretto contava solo le prove fino alla 102**: con il mazzo
completo e corretto (`research/programma6/MAZZO_ASTICELLA.md`, revisione `audits/reports/2026-11-12-MAZZO_ASTICELLA.md`) G1 scende da
0,867 a 0,755 (0,945 contando le prove fino alla 57, quando è stata trovata), la miscela F5 + M7 + K2 da 0,890 a 0,812: decisione di
metodo al proprietario. (4) Riesami chiusi (28, 113, 96, 55): nessuna prova bocciata di poco cambia verdetto. (5) Il lato venduto di
G1 perde nel 2026 sulle monete piccole e nuove con le fiammate (voce 12).
**Prova 153, il libro degli ordini fra le monete (12 novembre, sera)**: idea di strategy-scout, regole verificate e corrette prima del
calcolo, 137.200 file di Binance scaricati: **non passa, va al contrario dell'ipotesi** (A −40,9% l'anno, t −3,09; B −26,4%, t −2,45;
nessun anno positivo). Il verso opposto non regge negli anni (solo il 2025 positivo). Conto delle prove 314. **Capito oggi**: gli ordini
fermi vicino al prezzo, misurati giorno per giorno, non dicono dove andrà la moneta il giorno dopo nel verso atteso.
**Prova 154, la dimensione media dello scambio (13 novembre, notte)**: idea di strategy-scout con un dato mai usato (il numero di scambi
delle candele), regole verificate e corrette prima del calcolo: **non passa** (A +0,08% l'anno, t 0,01; B −4,7%, t −0,38; 2 anni
positivi su 5; il contrario non rende). Conto delle prove 316. **Capito oggi**: chi scambia (piccoli o grandi, misurato dalla
dimensione media) non dice nulla sulla direzione delle monete il giorno dopo; la ricerca fra monete ogni giorno, fuori dal funding, ha
dato 0 su 6 varianti nelle ultime tre prove (152 a parte).

**Giro delle 08:17 del 13 novembre**: raccolta (24 fonti su 24) e controlli in avanti (nessun annuncio di chiusura, nessuna moneta
nuova su Coinbase). **Ricerca nuova**: strategy-scout non ha trovato idee con un perché forte; le cinque valutate sono nella coda del
registro (idee 138-140) con il perché no. **G1, voce 9** (`research/programma7/misure_g1/voce9_rapporto.md`, fonti `ops/results/0721-0738`):
lo scarto fra posizioni vere e volute del demo a 1.000 USDT (8,9-15,8% del conto) si spiega quasi tutto con le variazioni sotto il
minimo di Binance (6-10% a regime, 22% degli ordini, come il 23% atteso dalla prova 148) più le monete che il demo non ha (ICP fino al
10 novembre, 龙虾USDT, IRYSUSDT); il demo resta sopra il paper (−0,99% contro −2,08% all'11 novembre) e nei giorni 9-13 il demo ha
perso 0,23 punti sul paper, tutti di funding. **Capito oggi**: (1) il conto piccolo non costa in prezzo quanto si temeva, la differenza
col paper è nel funding incassato; (2) **una trappola della ricerca**: dopo l'ultimo file mensile del funding (31 ottobre) il pannello
mette la media dei 90 giorni prima, lo stesso numero ogni giorno, e il ricalcolo di G1 sui giorni di novembre usciva sbagliato di 3
punti; con la stima dall'indice del premio torna sui giorni di controllo (6-7 novembre) ma resta 2,2 punti sotto il paper l'8-11
novembre, da chiarire quando esce il funding vero di novembre (nota in `research/INDEX.md`).
**Giro delle 12:17 del 13 novembre**: raccolta (24 fonti su 24) e controlli in avanti (niente di nuovo). **G1, voce 11**
(`research/programma7/misure_g1/voce11_rapporto.md`, fonti `ops/results/0720-0738`): il demo fa meglio del paper dall'8 novembre
(+0,62 punti all'ultima lettura) **solo per il primo giorno** (+0,84): il paper vendeva JCTUSDT (peso 0,39%), salita del 303% l'8
novembre, e il demo non l'aveva aperta perché 3,9 USDT sono sotto il minimo di Binance. A regime (9-13 novembre) il paper
**sopravvaluta** il conto vero di circa 0,045 punti al giorno, tutti di funding (il demo incassa il 20% in meno). **Ricerca nuova**:
strategy-scout propone la prova 155, G1 frenata nei giorni in cui l'indice di paura delle opzioni sul Bitcoin è alto (regole committate
prima di ogni calcolo; verifica in corso). **Capito oggi**: per i soldi veri si conta circa −0,05 punti al giorno rispetto al paper;
la vendita delle monete piccole e appena nate con le fiammate (voce 12) torna anche nel demo: un caso solo ha fatto 1,17 punti.
**Prova 155, G1 frenata dall'indice di paura delle opzioni (13 novembre, pomeriggio)**: idea di strategy-scout, regole verificate e
corrette prima del calcolo; dati del DVOL di Deribit dal 24 marzo 2021, giudizio dal 21 settembre 2021 al 4 ottobre 2026. **Non passa**:
mezza esposizione nei giorni di paura alta (A) porta lo Sharpe da 1,70 a 1,77 e la discesa massima da −30,1% a −21,6%, ma costa 2 punti
l'anno e la differenza con G1 non è distinguibile dal caso (t −0,79); lo Sharpe corretto è 0,51 (B 0,47). Conto delle prove 318.
**Capito oggi**: (1) G1 guadagna poco nei giorni di paura alta (+14% l'anno contro +46% negli altri), ma toglierla in quei giorni non
paga abbastanza; il freno resta un numero utile per il capitale piccolo, non una regola. (2) Le spese di G1 sul passato erano un po'
sovrastimate: nel calcolo di ottobre 6.105 ordini su 117.045 non avevano le candele a 1 ora e si contavano a mercato, oggi 137
(spese totali 0,3665 contro 0,3774, circa 0,19 punti l'anno in meno; il 2024 e il 2025 identici).
**Giro delle 16:17 del 13 novembre**: raccolta (24 fonti su 24) e controlli in avanti (niente di nuovo); lo scout non trova idee negli
annunci di Binance (tutte le categorie già nel registro). **G1, voce 10** (`research/programma7/misure_g1/voce10_rapporto.md`): il
«30 ottobre» del confronto settimanale è in realtà la finestra dal ribilancio del 29 a quello del 30 (paper +4,40, ricerca +2,75); nella
ricerca TRXUSDT pesava il 34,7% e da sola ha fatto +2,5 punti; l'orario d'ingresso del paper (mark delle 00:05 contro apertura delle
00:00) spiega circa 0,65 punti, il resto aspetta i pesi per moneta del paper. **Capito oggi**: un giorno con una moneta a un terzo del
lato pesa più di tutto il resto (la concentrazione della voce 13 torna anche qui).
**Giro delle 20:17 del 13 novembre**: raccolta (24 fonti su 24) e controlli in avanti (niente di nuovo). **G1, voce 6**: nel paper dal
23 ottobre G1 +4,54%, G11 +5,84% (dal 6 novembre G1 +0,38%, G11 −0,90%): il vantaggio di G11 scende da 2,7 a 1,3 punti, non si
distingue dal caso. **Ricerca**: nessuno scout nuovo (tre oggi, l'ultimo senza idee); il test del mazzo dello Sharpe corretto falliva
dal commit della prova 154 perché le prove 153-155 non c'erano: aggiunte, G1 0,757 e la miscela 0,813 (quasi uguali). Test: 2.797
passati; uno (`test_firma_dei_tre_tipi_di_chiave`) fallisce in questo contenitore per una libreria di crittografia mancante, anche
senza la modifica. **Capito oggi**: ogni prova nuova deve entrare nel mazzo nello stesso commit dei risultati, se no l'esame delle
prove dopo conta meno prove di quelle fatte.
**14 novembre, 04:40 UTC, il sesto ribilancio del demo** (`ops/results/0740-14nov-stato-ribilancio-1000.md`): demo 1.007,27 (+0,73%
dall'8 novembre), G1 nel paper +1,07%: il demo ora è 0,34 punti sotto. Il 13 novembre il demo ha fatto 1,15 punti meno del paper in un
giorno; la moneta che il demo non ha (龙虾USDT, −7,3%) ne spiega circa 0,23, il resto aspetta i pesi per moneta del paper. **Capito
oggi**: la stima di stamattina del costo del conto vero (−0,045 punti al giorno, voce 11) è troppo ottimista se un giorno come il 13
si ripete; con 6 giorni non si sa ancora, il confronto di lunedì lo misura.
**Giro delle 08:17 del 14 novembre**: raccolta (24 fonti su 24) e controlli in avanti (niente di nuovo); lo scout non trova idee forti
(la deriva del Bitcoin prima delle riunioni della Banca centrale americana ha troppi pochi casi: idea 142, non si fa). **Prova 156, G1
che esce dal lato venduto dopo una fiammata** (voce 12; regole di strategy-improver, verificate e corrette prima del calcolo, eseguite
da strategy-researcher): **non passa**. La variante a 7 giorni ha Sharpe 2,07 contro 1,99 e discesa −25,8% contro −30,1%, ma la
differenza con G1 sta dentro il caso (t 0,60), viene quasi tutta dal 2021 ed è positiva solo in 2 anni su 5 fra il 2021 e il 2025;
Sharpe corretto 0,79. Conto delle prove 320; la prova entra nel mazzo dello Sharpe corretto nello stesso commit. **Capito oggi**: le
monete vendute da G1 che salgono di colpo, nella mediana, nei giorni dopo non continuano a salire: il danno è tutto nel giorno della
fiammata, e una regola che esce dopo non lo evita. Per difendersi servirebbe agire prima (un tetto o uno stop dentro la giornata), e il
tetto è già stato provato (prova 152).
**Giro delle 16:17 del 14 novembre**: raccolta (24 fonti su 24) e controlli in avanti (niente di nuovo). **Lo stato della macchina ora
scrive i pesi di oggi di G1 moneta per moneta, nel paper e sul demo** (sola lettura; revisione con due giri, APPROVE dopo le correzioni,
senza riavvio; commit 96c6094). Prima lettura alle 16:41: il demo tiene il 179% di esposizione lorda contro il 200% del paper, con 3,8
punti di monete che il demo non ha e il resto più piccolo quasi su ogni moneta. **Capito oggi**: una parte del ritardo del demo sul paper
può venire da un'esposizione più bassa di circa un decimo; le letture dei prossimi giorni diranno quanto è movimento dei prezzi e quanto
resti sotto il minimo.
**Giro delle 20:17 del 14 novembre**: raccolta e controlli in avanti (niente di nuovo). **Correzione della lettura delle 16:41**: portando
il paper ai prezzi della lettura (prezzi pubblici di Binance) la sua esposizione è il 186,8%, non il 200%; il demo (179,3%) ne tiene circa
il 4% in meno, metà per le monete che non ha. **Capito oggi**: la differenza di esposizione non spiega il ritardo del demo; restano da
spiegare il funding incassato in meno e il giorno del 13 novembre, con le letture moneta per moneta dei prossimi giorni.
**14 novembre, sera, la domanda del proprietario su G1 e il mercato** (`research/programma7/misure_g1/g1_e_il_mercato.py`): sul passato
(2021-2026) G1 guadagna quasi tutto nei giorni in cui il mercato scende (+0,41% al giorno in media, somma +402 punti) e perde un poco in
quelli in cui sale (−0,08%, somma −90), ogni anno; il funding entra uguale in tutti e due. **Capito oggi**: G1 è una protezione nei giorni
di ribasso più che una scommessa al ribasso; il suo rischio è un mercato che sale a lungo con le monete affollate che salgono di più
(il lato venduto della voce 12).
**14 novembre, sera, G1 nei rialzi e G1 neutra** (domanda del proprietario; `research/programma7/misure_g1/g1_nei_rialzi.py`): per mese G1
non segue il mercato e nei mesi di forte rialzo guadagna come in quelli di forte ribasso (+6,2% e +5,7% al mese in media); il suo periodo
peggiore è stato quello prima dell'halving del 2024, quando salivano le monete piccole e affollate (novembre 2023 - aprile 2024: G1 −21,3%,
G1 neutra −15,3%). **Capito oggi**: il nemico di G1 non è il rialzo, è il rialzo delle monete affollate; G1 neutra ne attenua solo una
parte e dal 2025 rende meno (Sharpe corretto 0,70 contro 0,75).
**15 novembre, 04:40 UTC, il demo contro il paper** (`ops/results/0744-15nov-stato-ribilancio-1000.md`, `research/programma7/misure_g1/voce11_attribuzione_14nov.py`):
il 14 novembre demo +2,26% contro paper +3,51%; con i pesi moneta per moneta si spiegano 0,96 dei 1,25 punti: 0,59 da una sola moneta
che il paper vende e il demo non ha (龙虾USDT, −18,5% quel giorno; sul conto vero esiste), il resto da posizioni vendute un po' più piccole
sul demo. **Capito oggi**: il ritardo del demo nei giorni forti viene soprattutto da monete che il demo non ha; il conto vero le avrebbe.
**15 novembre, le prove chieste dal proprietario** (prova 157 funding coperto, prova 158 G1 con più leva, prova 159 base dei trimestrali):
la **157 passa l'esame scritto** (Bitcoin ed Ether comprati a pronti e venduti sul perpetuo: +10,5% l'anno sul capitale, discesa −0,4%,
62 mesi positivi su 70, Sharpe corretto 1,00; ma dopo il 2021 rende 1-14% l'anno) ed è da backtest-auditor, che attacca il margine del
perpetuo nei rialzi lunghi. La **158 non passa**: con la leva al 300-400% lo Sharpe resta quello di G1 (corretto 0,74-0,76), la discesa
arriva a −42/−47% e lo stop scatta 1-2 volte. **Capito oggi**: la fonte di guadagno più regolare che abbiamo trovato è il funding
coperto; rende poco ma quasi senza discese, e si muove quasi indipendente da G1 (correlazione 0,15).
**15 novembre, la prova 159, la base dei future trimestrali** (`research/programma7/RISULTATI_NOVANTASETTESIMA.md`): **non passa**. Comprare
a pronti e vendere il trimestrale fino alla scadenza rende il 5,5% l'anno con i contratti in moneta (discesa −4%, 2020 negativo, Sharpe
corretto 0,41) e il 3% con quello in USDT, che si fa liquidare 6 volte su 19 trimestri. **Capito oggi**: la base dei trimestrali paga meno
del funding dei perpetui negli stessi trimestri (7,3% contro 11,1% l'anno); fra i guadagni «quasi fissi» il funding coperto (157) resta il
migliore. Conto delle prove 326.
**15 novembre, il verdetto della revisione sulla prova 157** (`audits/reports/2026-11-15-PROVA157.md`): **FAIL sul calcolo**. I conti si
rifanno identici e dati, costi e sguardo nel futuro sono puliti, ma il margine del perpetuo era sbagliato: nei rialzi lunghi il conto dei
future sarebbe andato sotto zero e liquidato 9 volte in una variante e 5 nell'altra. Con le liquidazioni il guadagno è circa +7-8% l'anno, e
**dal 2022 circa +4% l'anno** (40 USDT su 1.000); il 2021 da solo fa più di metà del guadagno. **Capito oggi**: il funding coperto è
regolare ma rende poco fuori dagli anni di euforia, e su Binance richiede di spostare il margine fra pronti e future in tempo, cosa che il
bot oggi non sa fare.
**15 novembre, sera, la prova 160 (G1 con una parte di funding coperto) e un effetto sul conto delle prove**: la miscela 60/40 ha la discesa
−17,5% contro −30,1% di G1 e uno Sharpe un poco più alto, ma rende 41% l'anno contro 66% e non passa l'esame (Sharpe corretto 0,72); il
coperto non protegge nelle giornate peggiori di G1, la discesa scende solo perché G1 pesa meno. **Capito oggi**: le prove a incasso quasi
fisso, con le settimane legate fra loro, gonfiano lo Sharpe settimanale e abbassano lo Sharpe corretto di tutte le altre (G1 da 0,756 a
0,596 senza che G1 cambi); c'è una correzione nota (Lo 2002) da decidere con il proprietario (backlog P34). Conto delle prove 330.
**Riepilogo settimanale del 16 novembre** (dal 9 al 16 novembre, Bitcoin −12,7%): demo di G1 +2,8% (1.002,74 → 1.031,22 USDT); paper del
bot: G1 +5,3%, G11 +3,3%, G1 neutra +4,8%, F5 +5,0%, eventi fermi; conto a tavolino: HLI −6,8% e DXI −1,1% dal 2 novembre, G1 sulle stesse
monete +5,1% e +4,4%; copia dei trader di Hyperliquid dal 2 al 5 novembre: migliori del mese +22,3%, a esposizione uguale +22,1%, balene
+60,9% (tutti molto venduti in una settimana di forte ribasso; G1 nel paper negli stessi giorni circa +8,8% e +5,8%). Confronto
settimanale (`gate2/reports/2026-11-16-G1.md`): il demo fa −0,30 punti al giorno sul paper, quasi tutto il 13 e 14 novembre; la ricerca
non riproduce il paper dal 9 novembre (funding di novembre stimato); commissioni 1,38 volte l'assunto. Allocatore
(`allocazione/reports/2026-11-16.md`): tieni G1, una strategia sola. **Capito questa settimana**: G1 guadagna nelle settimane di ribasso
come quella appena passata; il demo ne prende circa la metà del guadagno nei giorni forti per le monete che non ha.
**16 novembre, 07:36 UTC, il riavvio con la fase 2** (ok del proprietario «ok riavvio»; `ops/results/0747`, `0748`, `0753`, `0754`): il bot
gira la versione 884b9b1a (conto vero spento senza interruttore, pulsante di approvazione della versione, funding dei paper per
regolamento); `DRY_RUN` vero; dopo un'ora paper G1, G11, G1 neutra, F5, eventi e demo hanno fatto il loro giro (08:07-08:25), nessun errore
nuovo nel registro (restano i soliti rifiuti dell'interesse aperto di due monete tolte dal listino, del vecchio sistema). 2.810 test passati
prima del riavvio.
**17 novembre, la prova in avanti del programma 5 arriva al verdetto** (`research/programma5/avanti/A.md`, dati fino al 15 novembre): M-001c
chiude 422 operazioni con −0,41% a operazione (p 0,72): **non passa**; con M-002 e M-003 già bocciate, nessuna delle procedure di scelta
mensile del programma 5 regge sui dati nuovi. Resta in corso la seconda tornata (N-001, N-002, N-003). **Capito oggi**: le regole scelte
ogni mese per moneta sul passato recente non hanno funzionato in avanti in nessuna delle tre versioni.
**17 novembre, perché il demo incassa meno funding del paper** (`ops/results/0757-17nov-stato-funding-demo-paper.md`): il conto demo di
Binance ha un funding suo, con molte meno monete pagate ogni 4 ore; sul mercato vero 49 delle 67 monete di G1 di oggi pagano più spesso che
ogni 8 ore, e il paper conta quei pagamenti veri. Il 16 novembre paper +0,22% del conto, demo +0,13%. **Capito oggi**: la parte più grande
dello scarto fra demo e paper «a regime» viene dal conto demo, non da un costo che il conto vero avrebbe; il conto vero incasserebbe il
funding del mercato vero, come il paper. Resta da confermare leggendo dalla macchina gli intervalli del funding del demo.
**17 novembre, 12:30 UTC, giro delle 4 ore**: raccolta 24 fonti su 24, nessuna chiusura nuova dopo il 21 ottobre. G1, voce 3: gli
incassi del demo stesso confermano che il conto demo ha meno monete a 4 ore (agli orari diversi da 00, 08 e 16 il demo riceve il funding
su 15-20 monete per regolamento, il paper su 52-54; `MIGLIORARE_G1.md`), quindi niente lettura in più dalla macchina. Voce 2: dal 12 al
17 novembre la commissione del demo è lo 0,0273% del valore scambiato, con il 34% del valore a commissione piena (era il 27% dal 9 al
12). Ricerca nuova: strategy-scout non trova idee con un perché forte (scartate con il perché in `research/idee/LOG.md`); nella coda
l'idea 146, gli eventi di CoinMarketCap, in attesa del proprietario. **Capito oggi**: un terzo del valore scambiato da G1 paga la
commissione piena; sul conto vero la quota può essere diversa (il libro degli ordini del demo non è quello vero), ma è la misura
migliore che abbiamo, ed è sopra quella del modello.
**17 novembre, 16:30 UTC, giro delle 4 ore**: raccolta 24 fonti su 24, nessuna chiusura nuova. G1, voce 2: l'ordine «solo nel libro»
(mai a commissione piena) farebbe risparmiare al massimo circa 0,9 punti l'anno (stima dai numeri del demo dal 12 al 17 novembre,
`MIGLIORARE_G1.md`), meno gli ordini che non si eseguirebbero: non si fa ora. Ricerca: nessuna prova pronta e lo scout già passato
alle 12:30 senza idee forti; la coda è stata riallineata (idee 136 e 137 chiuse: erano già fatte, prova 149 e riesami dell'11-12
novembre; 37 idee aperte). **Capito oggi**: il costo in più delle commissioni del demo vale poco meno di un punto l'anno; non è lì
che G1 può migliorare di molto.
**17 novembre, 20:20 UTC, giro delle 4 ore**: raccolta 24 fonti su 24, ma le tre pagine di Crypto Briefing erano tutte piene (98 articoli
pubblicati fra le 16 e le 20, `research/notizie/archivio/giri.csv`): fra le 16:16 e le 16:33 qualche articolo di quella fonte può
mancare. Aggiunta la quarta pagina (`research/notizie/raccolta.py`; alle 20:30 copriva dalle 13:55 alle 16:38). Nessuna chiusura nuova.
G1: nessun passo nuovo possibile in questo giro (la voce 2 aspetta i 13 giorni a regime del 21 novembre, la voce 8 la lettura del
mattino). Ricerca: nessuna prova pronta, scout già passato oggi. **Capito oggi** (sera): niente di nuovo sulle strategie.
**18 novembre, 04:50 UTC, l'undicesimo ribilancio del demo a 1.000 USDT** (`ops/results/0758`, `0759`): nessun errore nuovo, gli stessi
3 rifiuti (EVAA, UAI, LIT), 8 ordini, 45 variazioni sotto il minimo. Demo +3,33% dall'8 novembre, paper G1 +4,92%. Il 17 novembre il demo
ha fatto 0,62 punti meno del paper nella tabella del giorno: le posizioni diverse ne spiegano 0,13 (`misure_g1/voce11_attribuzione_17nov.py`),
funding e spese sono uguali, il resto non si spiega con i prezzi del mercato vero (prezzi propri del conto demo o ore diverse delle
letture; il 18 restituisce già 0,23). Raccolta delle 04:20: 25 fonti su 25. **Capito oggi**: con il conto piccolo i resti sotto il
minimo pesano soprattutto sulle monete piccole che si muovono molto (il demo vendeva meno di due monete scese del 30% e del 16%).
**18 novembre, 08:30 UTC, giro delle 4 ore**: raccolta 25 fonti su 25, nessuna chiusura nuova. Ricerca nuova: strategy-scout propone
l'idea 147, **il funding fra il perpetuo in USDT e quello in USDC della stessa moneta** (comprato uno, venduto l'altro: niente rischio sul
prezzo, guadagno regolare se la differenza dura; dato mai usato). Regole in `research/programma7/CENTESIMA.md`, corrette prima del
commit (la differenza si misura per giorno, perché i due contratti possono pagare a intervalli diversi); prova 162 nel registro, prima la
verifica di strategy-researcher. Probabilità medio-bassa (lordo piccolo, quattro gambe di spese).
**18 novembre, 09:40 UTC, la prova 162 non passa** (`research/programma7/RISULTATI_CENTESIMA.md`): il funding fra il perpetuo in USDT e
quello in USDC della stessa moneta, su 40 monete dal febbraio 2024. A (decisione mensile) +0,10% l'anno netto, B (settimanale) −5,55%;
t 0,15 e −10,15; il funding lordo raccolto è 2,2% e 4,6% l'anno, le spese 1,9% e 10,4%. Con il margine in comune nessun giorno a rischio.
Conto delle prove 332 (serie aggiunte al mazzo). Le letture del ricercatore non previste dalle regole (orari al minuto, storia non
consecutiva, chiusure, margine ora per ora) non cambiano l'esito e si accettano. **Capito oggi**: su Binance i due contratti della stessa
moneta pagano funding molto simili; la differenza è di pochi punti l'anno e non copre le spese di cambiare lato.
**18 novembre, sera**: raccolte delle 12:20, 16:20 e 20:20 regolari (25, 24 e 25 fonti su 25; alle 16:20 non ha risposto ZyCrypto),
nessuna chiusura nuova. Lo scout delle 12:30 non trova idee forti (`research/idee/LOG.md`); non è stato richiamato alle 16:17 e alle
20:17. G1: nessun passo nuovo fino alla lettura del mattino. **Capito oggi**: la prova 162 (funding fra USDT e USDC) chiude un'altra
strada del guadagno «senza prezzo» su Binance: il funding coperto (161) rende poco, circa +3% l'anno dal 2022, e questa rende quasi
zero dopo le spese.
**19 novembre, 04:40 UTC, il dodicesimo ribilancio del demo a 1.000 USDT** (`ops/results/0760`, `0761`): 13 ordini tutti a limite, nessun
errore nuovo, gli stessi 3 rifiuti più IRYSUSDT che sul demo non c'è. Demo +2,39% dall'8 novembre, paper G1 +3,60%. Il 18 novembre il demo
recupera 0,51 punti sul paper, quasi tutto lo scarto del 17. Raccolta delle 04:20: 24 fonti su 25. **Capito oggi**: gli scarti di un giorno
solo fra demo e paper si compensano spesso il giorno dopo; conta la somma su più giorni, che a regime viene dalle monete mancanti e dai
resti sotto il minimo.
**19 novembre, 08:30 UTC, giro delle 4 ore**: raccolta 24 fonti su 25, nessuna chiusura nuova. Lo scout delle 08:17 non trova idee forti
(terza volta su quattro dal 17 novembre; scartate in `research/idee/LOG.md`): le idee con un dato nuovo sono quasi finite; le prossime
verranno soprattutto dai dati che raccogliamo noi in avanti (posizioni di Hyperliquid oltre i tre mesi, verso febbraio 2027; storia più
lunga dei perpetui su azioni). Prova in avanti del programma 5 e conto a tavolino aggiornati (`research/programma5/STATO.md`).
**19 novembre, sera**: raccolte delle 12:20, 16:20 e 20:20 regolari, nessuna chiusura nuova. La seconda tornata della prova in avanti del
programma 5 da domani si lancia a parte (`SALTA_AVANTI2=1`, `research/programma5/avanti/aggiorna.sh`). G1 e ricerca: nessun passo nuovo
nel pomeriggio (scout già passato alle 08:17). **Capito oggi**: vedi la voce delle 04:40 (gli scarti di un giorno fra demo e paper si
compensano il giorno dopo).
**20 novembre, 04:40 UTC, il tredicesimo ribilancio del demo a 1.000 USDT** (`ops/results/0762`, `0763`): 7 ordini, nessun errore nuovo,
gli stessi rifiuti. Demo +1,39% dall'8 novembre, paper G1 +2,53% (il demo 1,14 punti sotto). Il 19 novembre demo e paper quasi uguali
(−1,11% e −1,13%). L'esposizione del demo scende al 189,6% (paper 200%) perché le variazioni sotto il minimo arrivano a 47 (8,7% del
conto). Raccolta delle 04:20: 23 fonti su 25. **Capito oggi**: con 1.000 USDT i resti sotto il minimo non solo spostano le monete, ma
abbassano anche l'esposizione totale di qualche punto; sul conto vero con la stessa cifra succederebbe lo stesso.
**20 novembre, 08:30 UTC, giro delle 4 ore**: raccolta 22 fonti su 25, nessuna chiusura nuova. Lo scout guarda il rischio di G1 (freni,
stop, esposizione variabile) e trova ogni freno ragionevole già provato (prove 42, 61, 88, 89, 92-94, 120, 124, 152, 155, 156, 158, 160,
161): nessuna idea nuova (`research/idee/LOG.md`). Prova in avanti del programma 5: da oggi le due tornate finiscono nel tempo. **Capito
oggi**: per avere guadagni più regolari non resta un freno di G1 da provare con i nostri dati; restano le misure in avanti (G1 contro G1
neutra, la miscela con il funding coperto a tavolino) e i dati che raccogliamo noi. Da dire al proprietario nel riepilogo di lunedì.
**20 novembre, 16:40 UTC, perché G1 non guadagna nel ribasso del 18-19 novembre** (domanda del proprietario;
`research/programma7/misure_g1/voce12_ribasso_18_19nov.py`): il 18 le monete comprate scendono più di quelle vendute (−2,41% contro
−1,10%), il 19 le vendute salgono (+1,20%) mentre il Bitcoin scende; una sola moneta piccola venduta, ICNTUSDT, sale del 21% e poi del
28% e costa da sola circa 1,2 punti in due giorni. Raccolta delle 16:20: 24 fonti su 25. **Capito oggi**: G1 non guadagna nei ribassi in
quanto tale, ma solo quando le monete vendute scendono più di quelle comprate; le fiammate delle monete piccole vendute sono il suo punto
debole del 2026.
**21 novembre, 04:40 UTC, il quattordicesimo ribilancio del demo a 1.000 USDT** (`ops/results/0764`, `0765`): 18 ordini tutti a limite,
nessun errore nuovo. Il 20 novembre, con il Bitcoin −5,1%, G1 guadagna: demo +1,88%, paper +1,16%; dall'8 novembre demo +3,09%, paper
+3,27% (scarto sceso a 0,18 punti). Fra le 00:05 e le 04:20 il Bitcoin scende di un altro 5%. Costo degli ordini sui 13 giorni a regime:
68,5% del valore a commissione bassa, 0,0272% medio, 1,36 volte l'assunto. Raccolta delle 04:20: 25 fonti su 25. **Capito oggi**: in 13
giorni il demo ha recuperato quasi tutto lo scarto con il paper; resta il costo delle commissioni, un terzo sopra il modello.
**21 novembre, 08:30 UTC, giro delle 4 ore**: raccolta e controlli regolari. Strategy-scout **non** è stato chiamato: il proprietario
ha chiesto che le strade nuove partano solo con il suo via libera (21 novembre: le regole della prova 163 scritte senza via libera sono
state tolte). In attesa della sua risposta sulla strada proposta (l'arbitraggio vero del funding fra Binance e Hyperliquid, con dati
gratuiti). Approvata invece la prova gratuita «leggo io le notizie delle monete vendute da G1 ogni mattina, prima dei prezzi», da domani.
**21 novembre, 12:30 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (38 articoli nuovi, 40 conti di Hyperliquid), nessuna chiusura
di perpetui dopo il 21 ottobre e nessuna moneta nuova su Coinbase. Ricerca nuova: la prova 163 (l'arbitraggio vero del funding fra
Binance e Hyperliquid, via libera del proprietario «procedi») ha le regole verificate e chiuse (commit 8fe0339) ed è in calcolo: il
ricercatore sta scaricando lo storico di Hyperliquid. G1: nessun passo nuovo in questo giro (le misure di oggi aspettano la lettura
delle 04:17 di domani). Strategy-scout non chiamato: strade nuove solo con il via libera del proprietario. **Capito oggi**: niente di
nuovo in questo giro; si aspetta il risultato della 163.
**21 novembre, 16:00 UTC, prova 163: l'arbitraggio vero del funding fra Binance e Hyperliquid non passa** (`research/programma7/
RISULTATI_CENTOUNESIMA.md`): dal 5 giugno 2023 al 31 ottobre 2026, 156 monete, 1.000 USDT. Netto A −9,27% l'anno, B +1,77%; tutte e due
con 2 liquidazioni su Binance nel 2025 (il crollo del 10 ottobre 2025 entra in tutte e due), Sharpe corretto 0,00. Lo scarto di funding
c'è (lordo 11,0% e 21,5% l'anno sul valore delle gambe), ma le spese ne mangiano una parte (4,0% e 11,8%) e i crolli una gamba sola alla
volta, perché i margini delle due borse sono separati. Il guadagno di B viene quasi tutto da una moneta (MAVIA: senza, −14,9%). Solo
Bitcoin ed Ether (controllo descrittivo, non una variante): +2,55% e +1,85% l'anno senza liquidazioni, ma nel 2026 nessun segnale.
Conto delle prove 334. **Capito oggi**: fra due borse lo scarto di funding è grande sulle monete piccole, ma lì i crolli liquidano la
gamba comprata prima che si possano spostare i soldi; sulle monete grandi il rischio sparisce ma il guadagno è sotto il 3% l'anno.
**21 novembre, 16:30 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (57 articoli nuovi, 40 conti di Hyperliquid), nessuna chiusura
di perpetui dopo il 21 ottobre, nessuna moneta nuova su Coinbase. G1: nessun passo nuovo (si aspetta la lettura delle 04:17). Ricerca
nuova: nessuna prova in corso dopo il «no» della 163; strategy-scout non chiamato, perché le strade nuove (Polymarket contro le opzioni,
le occasioni del conto piccolo) aspettano il via libera del proprietario. **Capito oggi**: niente di nuovo in questo giro.
**21 novembre, 20:45 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (36 articoli nuovi, 40 conti di Hyperliquid), nessuna chiusura
di perpetui dopo il 21 ottobre, nessuna moneta nuova su Coinbase. **G1, voce 14 nuova**: scritte le regole della lettura delle notizie
delle monete vendute, prima della prima lettura di domani (`research/programma7/misure_g1/VOCE14_REGOLE.md`, foglio preparato da
`voce14_lettura.py`); è una misura, non cambia G1. Provato lo script sulla lettura «stato» di stamattina (fuori dal repo, non conta):
delle 30 monete vendute solo 5 hanno articoli nel nostro archivio delle 24 ore (491 articoli), le piccole nessuno. Per questo le regole
ammettono al più una ricerca sul web per moneta con peso di almeno il 2%. **Capito oggi**: il nostro archivio di 25 siti copre le monete
grandi, quasi mai quelle piccole dove arrivano le fiammate; per leggerle servono altre fonti (il web, gli annunci delle borse).
**22 novembre, 00:25 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (27 articoli nuovi, 40 conti di Hyperliquid), nessuna chiusura
di perpetui dopo il 21 ottobre, nessuna moneta nuova su Coinbase. G1: la prima lettura delle notizie delle monete vendute (voce 14) è
nel giro delle 04:17. Ricerca nuova: nessuna prova in corso; le strade nuove aspettano il via libera del proprietario. **Capito oggi**:
niente di nuovo in questo giro.
**22 novembre, 04:30 UTC, il quindicesimo ribilancio del demo a 1.000 USDT e la prima lettura delle notizie** (`ops/results/0766`,
`0767`; `research/programma7/misure_g1/voce14_letture/2026-11-22.md`): solo 4 ordini, tutti a limite, gli stessi rifiuti, nessun errore
nuovo. Il 21 novembre G1 perde il 3,1% (demo −3,13%, paper −3,07%): dall'8 novembre demo +0,81%, paper +1,22%. Prima lettura delle
notizie delle 31 monete vendute, salvata alle 04:22:56 prima di qualunque prezzo di oggi: nessuna a rischio di salire (nell'archivio
nulla di specifico, 21 ricerche sul web senza notizie datate nelle 48 ore). Raccolta delle 04:20: 25 fonti su 25. **Capito oggi**: per
le monete piccole vendute da G1 le notizie del giorno quasi non esistono nelle fonti pubbliche che leggiamo; se le fiammate hanno una
causa, sta altrove (annunci delle borse, canali dei progetti) o non si legge prima.
**22 novembre, 08:45 UTC, decisione del proprietario: le idee nuove si provano da sole** («perché aspetti il mio via libera, le idee le
devi provare in automatico»; `docs/decisioni_del_proprietario.md`). Partite insieme: (1) le monete che arrivano nei portafogli delle borse
prima della quotazione (prova 164): **non eseguibile gratis**, lo storico dei trasferimenti chiede una chiave (Etherscan, solo Ethereum)
o un servizio a pagamento; (2) la mappa delle liquidazioni di Hyperliquid: **raccolta partita** a ogni giro, 600 conti, prima lettura
2.337 posizioni sopra i 10.000 dollari per 2,82 miliardi (`research/trader_copiati/LIQUIDAZIONI.md`). Idee nuove in coda e regole
scritte: prevedere le chiusure dei perpetui di Binance (prova 165), le società con le monete in cassa che valgono meno di loro (prova
166), entrambe in verifica; le proposte di governo dei gettoni (idea 157) dallo scout. **Capito oggi**: nella prima lettura, sul
Bitcoin ci sono 48,7 milioni di posizioni corte con il prezzo di liquidazione entro il +10% e nessuna lunga entro il −10%: dopo il
crollo i grandi conti sono quasi tutti venduti (lo stesso che si vede nella copia delle balene).
**22 novembre, 08:45 UTC, giro delle 4 ore**: raccolta 24 fonti su 25, 40 conti copiati, **seconda lettura della mappa delle
liquidazioni** (600 conti, 2.338 posizioni sopra i 10.000 dollari, 109 secondi); nessuna chiusura nuova, nessuna moneta nuova su Coinbase.
Ricerca nuova: la prova 166 (le società con le monete in cassa) **non si fa sul passato**: la verifica trova meno di 23 eventi
indipendenti, il verdetto sarebbe quasi certamente «non conclusivo» (decisione prima di ogni calcolo, riga 166). In verifica le prove
165 (le chiusure dei perpetui prima dell'annuncio) e 167 (le votazioni dei possessori). G1: nessun passo nuovo in questo giro. **Capito
oggi**: un fenomeno nuovo (le società di tesoreria, nate nel 2025) ha il perché più forte ma la storia più corta: le idee davvero nuove
spesso non si possono giudicare sul passato, solo in avanti.
**22 novembre, 10:30 UTC, prova 167 (le votazioni dei possessori che spostano soldi a chi tiene il gettone): campione troppo piccolo**
(`research/programma7/RISULTATI_CENTOCINQUESIMA.md`): dalle 1.599 proposte di Snapshot con le parole fissate, dopo i filtri scritti prima
(spazi ufficiali verificati, approvate, perpetuo esistente, 30 giorni fra due eventi) restano 26 eventi in sei anni; sotto i 40 la prova si
ferma prima di caricare i prezzi e non entra nel conto. **Capito oggi**: i voti che spostano soldi ai possessori sono rari sulle monete con
il perpetuo di Binance (una manciata l'anno): l'idea è giusta ma il mercato è troppo piccolo per una regola sul passato.
**22 novembre, 11:30 UTC, prova 165: prevedere le chiusure dei perpetui di Binance prima dell'annuncio non passa**
(`research/programma7/RISULTATI_CENTOTREESIMA.md`): A +5,67% l'anno, B +20,66%, ma il 2026 perde il 43% e il 47%, t 0,30 e 0,75,
Sharpe corretto 0,005 e 0,015, sotto le scelte a caso. Il guadagno non viene dalle chiusure (A: nessuna posizione poi annunciata; B: 22%
dopo l'annuncio, 0% prima): la regola vende semplicemente le monete poco scambiate, che nel 2024-2025 scendono e nel 2026 salgono. Conto
delle prove 336. **Capito oggi**: con il solo volume non si riconosce in anticipo quale contratto Binance chiuderà; le chiusure sono poche
(87 in cinque anni) e i contratti poco scambiati che restano vivi sono molti di più.
**22 novembre, 14:30 UTC, la reazione dopo la notizia** (domanda del proprietario: «non si tratta di predire prima [...] ma sai benissimo
la reazione ci sarà dopo»): scritte le regole della lettura dei fatti gravi del giorno prima (`research/notizie/FATTI_GRAVI.md`, idea
158), prima lettura domattina. Il perché viene dai numeri: le regole fisse dopo la notizia guadagnano poco (attacchi +3,94% su 28 casi,
chiusure +7,89% su 77, Coinbase +4,03% su 104, vinte il 57-67%); nelle azioni la sessione «trading stock» trova oggi che dopo le
dimissioni del capo il calo arriva prima di poter entrare (−1,17%, t −3,02) e dopo, in media, niente su 243 casi. **Capito oggi**: la
notizia ovvia è già nel prezzo quando la si può usare; se c'è un guadagno, sta nel riconoscere i casi che continuano per giorni.
**22 novembre, 12:30 UTC, giro delle 4 ore**: raccolta 24 fonti su 25 (45 articoli nuovi), 40 conti copiati, mappa delle liquidazioni
(600 conti, 2.352 posizioni); nessuna chiusura nuova, nessuna moneta nuova su Coinbase. Ricerca nuova: la prova 168 (G1, G11, G1 neutra
e F5 insieme sullo stesso conto, idea del proprietario) è in calcolo dopo la verifica. G1: nessun passo nuovo in questo giro. **Capito
oggi**: niente di nuovo in questo giro.
**22 novembre, 13:30 UTC, prova 168: G1, G11, G1 neutra e F5 insieme sullo stesso conto** (idea del proprietario,
`research/programma7/RISULTATI_CENTOSESTA.md`): su 300 settimane dal 2021 un portafoglio solo con la media dei pesi fa +55,2% l'anno,
Sharpe 2,14, discesa −24,9%; G1 da sola sulle stesse settimane +54,1%, Sharpe 1,97, discesa −28,8%. Ogni anno positivo, t 5,13, ma lo
Sharpe corretto è 0,75 (G1 0,76): per l'esame scritto no. Correlazione con G1 0,98. In avanti dal 31 ottobre (22 giorni) un quarto a
testa +3,17%, G1 +2,62%. Conto delle prove 338. **Capito oggi**: le quattro sono quasi la stessa strategia; insieme tolgono 3-4 punti
di discesa senza perdere rendimento, ma non aggiungono un guadagno nuovo.
**22 novembre, 16:30 UTC, giro delle 4 ore**: raccolta 24 fonti su 25 (40 articoli nuovi), 40 conti copiati, mappa delle liquidazioni
(600 conti, 2.349 posizioni); nessuna chiusura nuova, nessuna moneta nuova su Coinbase. Coda della ricerca senza prove pronte (164-168
chiuse oggi): strategy-scout cerca una o due idee «fatto → chi è costretto a comprare o vendere dopo», con dati gratuiti e almeno 60
eventi. G1: nessun passo nuovo. **Capito oggi**: niente di nuovo in questo giro.
**22 novembre, 17:30 UTC, idea nuova dello scout scartata prima del calcolo**: la scadenza delle opzioni di Deribit il venerdì alle 08:00
(idea 159; regole in `research/programma7/CENTOSETTIMA.md`) non si fa: viene da uno studio pubblicato (da manuale per la decisione del
21 novembre) e quattro scambi costano circa lo 0,24% per un movimento di poche ore. Scartate dallo scout anche gli ETF a leva (storia dal
2023, effetto piccolo), i cambi di contratto dei gettoni (meno di 20 eventi) e i dimezzamenti delle altre monete (meno di 10). **Capito
oggi**: le conseguenze meccaniche con una data fissa e tanti casi sono quasi tutte già note e piccole; i fatti con conseguenze grandi
sono rari, e per quelli la strada è la lettura caso per caso in avanti.
**22 novembre, 20:30 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (40 articoli nuovi), 40 conti copiati, mappa delle liquidazioni
(600 conti, 2.341 posizioni); nessuna chiusura nuova, nessuna moneta nuova su Coinbase. G1: nessun passo nuovo (le due letture delle
notizie partono alle 04:17). Ricerca: nessuna prova pronta; lo scout del pomeriggio non ha trovato un'idea da provare (idea 159 scartata).
**Capito oggi**: niente di nuovo in questo giro.
**23 novembre, 00:30 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (36 articoli nuovi); il lunedì rinnova i conti scelti di
Hyperliquid (migliori del mese, balene e i 600 della mappa delle liquidazioni); mappa: 600 conti, 2.341 posizioni. Nessuna chiusura nuova,
nessuna moneta nuova su Coinbase. G1: nessun passo nuovo in questo giro (alle 04:17 il ribilancio, le due letture delle notizie e poi il
confronto settimanale). **Capito oggi**: niente di nuovo in questo giro.
**23 novembre, 04:30 UTC, il sedicesimo ribilancio del demo e le due letture del mattino** (`ops/results/0768`, `0769`): 27 ordini tutti a
limite, una moneta in più rifiutata perché manca sul demo (PIEVERSE). Dall'8 novembre demo −2,47%; dal 9 novembre demo −2,00%, paper
−0,22% (il demo 1,8 punti sotto in 15 giorni, −0,12 al giorno). Prima lettura dei fatti gravi (`research/notizie/fatti_gravi/2026-11-23.md`,
commit 55e0176 alle 04:20, prima dei prezzi): **ACE giù forza 2** (ponte svuotato, squadra che chiede di fermare gli scambi), **CYBER giù
forza 1** (monete coniate senza permesso, Upbit e Bithumb fermano i trasferimenti), **APT su forza 1** (scelta da PayPal per la sua moneta
stabile); due collegamenti completati a mano, corretti sotto con l'ora. Monete vendute da G1: nessuna a rischio di salire. Raccolta delle
04:20: vedi sopra. **Capito oggi**: in una sola notte le notizie danno tre casi di fatti propri con una direzione chiara; il nostro archivio
li prende tutti (le ricerche sul web, due mattine su due, non aggiungono niente).
**23 novembre, 07:30 UTC, riepilogo settimanale al proprietario** (fonti: `ops/results/0746` e `0769`, `gate2/reports/2026-11-23-G1.md`,
`allocazione/reports/2026-11-23.md`, `research/programma6/paper/PAPER.md`, `research/trader_copiati/HYPERLIQUID_CONTO.md`): settimana dal 16
al 23 novembre (letture delle 04:18) G1 nel paper −5,99%, G11 −6,55%, G1 neutra −5,33%, F5 −1,24%, eventi fermi; demo −5,42%. Il crollo di
sabato a 55.000 e il rimbalzo di domenica: le monete piccole vendute salgono (VVV, XMR, PIEVERSE negli articoli; attribuzione non ancora
misurata). Allocatore: tieni. Le monete rifiutate dal demo (LIT, EVAA, UAI, IRYS, PIEVERSE, JCT) sul mercato vero di Binance sono tutte
aperte e scambiabili (`exchangeInfo`, «TRADING»): lo scarto del demo per le monete mancanti sul conto vero non ci sarebbe. **Capito oggi**:
la settimana peggiore di G1 da quando è nel paper viene dal rimbalzo dopo un crollo, il caso che la misura sul passato indicava come il suo
punto debole (mercato su, monete piccole vendute che salgono).
**23 novembre, 08:00 UTC, il trading AI riparte** (decisione del proprietario: conto demo suo da 1.000 USDT, Opus 5.5, 5 euro al giorno):
sessione «trading AI» riaperta e compito mandato con un messaggio programmato; la chiave del modello sulla macchina funziona
(`ops/results/0770-23nov-chiave-del-modello.md`; il vecchio livello AI spende oggi circa 0,01 dollari a settimana). Il conto demo nuovo e le
sue chiavi li crea il proprietario. **Capito oggi**: la macchina ha già tutto per chiamare il modello; manca solo il conto demo separato.
**23 novembre, 08:30 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (36 articoli nuovi), mappa delle liquidazioni (600 conti, 2.342
posizioni); nessuna chiusura nuova, nessuna moneta nuova su Coinbase. G1: strategy-improver misura sul passato cosa fanno i due lati di G1
nei giorni dopo un crollo del Bitcoin (la lezione della settimana, voce 12; solo misura). Ricerca: nessuna prova pronta; lo scout del
pomeriggio di ieri non ha dato idee da provare, oggi il passo è sulla debolezza vista in avanti. Trading AI: in attesa del lavoro della
sua sessione e del conto demo del proprietario.
**23 novembre, 09:30 UTC, G1 nei giorni dopo un crollo del Bitcoin** (voce 12, solo misura, `research/programma7/misure_g1/voce12_rimbalzi.md`):
26 crolli dal 2021 (Bitcoin giù almeno del 10% in 3 giorni, regola scritta prima). Nei 7 giorni dopo il lato venduto di G1 guadagna +2,6
punti (normale +0,05), il comprato perde −2,8 (normale +0,95), G1 intero −0,16 contro +1,01 normale; l'errore è grande quanto la media e le
monete piccole vendute non perdono di più. **Capito oggi**: la perdita della settimana (le piccole vendute che salgono nel rimbalzo) non è il
comportamento tipico di G1 dopo un crollo; resta un caso in avanti, e nessuna regola sul lato venduto ha un perché.
**23 novembre, 12:40 UTC, giro delle 4 ore**: raccolta 24 fonti su 25 (104 articoli nuovi, CryptoBriefing piena: qualche articolo della
fonte può mancare), mappa delle liquidazioni (600 conti, 2.340 posizioni); nessuna chiusura nuova, nessuna moneta nuova su Coinbase.
Trading AI: la sua sessione ha scritto il codice con i test e una richiesta (`trader_ai/RICHIESTE_CRYPTO.md`); il proprietario le ha
detto che il modello sceglie da solo quando essere richiamato (non ogni 4 ore). Risposta in `docs/risposte_trading_ai.md`: un servizio
suo installato una volta dal proprietario come quello delle azioni, senza toccare il bot. **Capito oggi**: il trading AI può stare sulla
macchina accanto al bot senza codice nell'area delle crypto, come le azioni.
**23 novembre, 16:30 UTC, giro delle 4 ore**: raccolta 23 fonti su 25 (188 articoli nuovi in 4 ore; CryptoBriefing piena su due pagine:
qualche articolo di quella fonte può mancare), mappa delle liquidazioni (600 conti, 2.321 posizioni); nessuna chiusura nuova, nessuna
moneta nuova su Coinbase. Trading AI: la sua sessione ha preso la risposta (voci 1 e 2 chiuse) e lavora allo script di installazione.
G1: nessun passo nuovo. **Capito oggi**: niente di nuovo in questo giro.
**23 novembre, 20:30 UTC, giro delle 4 ore e F5 contro G1** (domanda del proprietario): sulle letture dello stato dal 16 al 23 novembre F5
−1,24% (giorno peggiore −1,26%), G1 nel paper −5,99% (−2,86%), demo −5,42%; sul passato (300 settimane, prova 168) quasi pari: F5 +55,4%
l'anno, Sharpe 1,88, settimane positive 61%, settimana peggiore −14,7%, spese 4,9%; G1 +54,1%, 1,97, 59%, −9,4%, 6,5%; correlazione
0,80. Raccolta delle 20:19: 24 fonti su 25 (133 articoli). Trading AI: la sua sessione è alla versione 3 delle regole, con le scelte del
proprietario (moneta e intervalli suoi, obiettivo 50 USDT al giorno, leva fino a 10), sempre sul demo suo. **Capito oggi**: in una
settimana di crollo e rimbalzo decidere solo il lunedì ha perso molto meno che decidere ogni giorno; sul passato le due cose si equivalgono.
**24 novembre, 00:30 UTC, giro delle 4 ore**: raccolta 23 fonti su 25 (70 articoli nuovi; CryptoBriefing piena), mappa delle liquidazioni
(600 conti, 2.383 posizioni); nessuna chiusura nuova, nessuna moneta nuova su Coinbase. Trading AI: il codice degli ordini del trader è
passato da live-path-reviewer sette volte il 23 novembre; l'ultima dice **approvato con condizioni** (ok del proprietario, prova sul demo
con «TUTTO BENE», conto pulito). Collegate le revisioni nei registri del revisore (voce 3 delle richieste). **Capito oggi**: niente di
nuovo sul mercato in questo giro.
**24 novembre, 04:30 UTC, il diciassettesimo ribilancio e le letture del mattino** (`ops/results/0771`, `0772`): 9 ordini, gli stessi
rifiuti. Il 23 novembre, con il ritorno di Huang in Nvidia e il Bitcoin +17% dai 55.000, G1 risale: demo +1,71%, paper +0,96%, F5 +2,1%
fra le due letture. Dal 9 novembre demo −0,22%, paper +1,91%. Fatti gravi (commit 1377db3, prima dei prezzi): **SKY giù forza 2** (Upbit e
Bithumb la mettono «con cautela», il cofondatore deve 77 milioni e pensa di vendere), **MON giù forza 1** (sblocco da 190 milioni più grande
del suo valore); ACE e CYBER non contate di nuovo (già segnate ieri). Monete vendute da G1: nessuna a rischio. Su 552 articoli in 24 ore,
nessun fatto nuovo di mercato oltre il ritorno di Huang. **Capito oggi**: nelle notizie di una giornata grande i fatti propri di una
moneta sono pochi (due su 41 monete citate); il resto è mercato in generale.
**24 novembre, 08:30 UTC, giro delle 4 ore**: raccolta 23 fonti su 25 (32 articoli nuovi), mappa delle liquidazioni; nessuna chiusura
nuova, nessuna moneta nuova su Coinbase. Ricerca: strategy-scout scrive le regole del «giudice delle balene» (idea 152), una misura in
avanti in cui la sessione giudica ogni lunedì quali conti grandi di Hyperliquid guadagnano con la scelta delle monete e quali solo con la
direzione del mercato. G1: nessun passo nuovo. **Capito oggi**: niente di nuovo in questo giro.
**24 novembre, 12:40 UTC, giro delle 4 ore**: raccolta 23 fonti su 25 (106 articoli nuovi; CryptoBriefing piena), nessuna chiusura nuova,
nessuna moneta nuova su Coinbase. Scritto `research/trader_copiati/giudice_balene.py` (il foglio del lunedì del giudice delle balene);
provato sui dati fino al 23 novembre fuori dal repository: 407 conti letti, 18 giudicabili (la mappa delle liquidazioni ha solo due
giorni), proposte 0 costanti, 14 «mercato», 4 «caso»; esposizione netta venduta fino a 9 volte il valore del conto. **Capito oggi**: nel
mese del crollo i grandi conti di Hyperliquid hanno guadagnato quasi solo con la direzione del mercato (parte propria fra +4% e +41% del
conto contro parte del mercato fino a +306%): copiarli oggi vuol dire scommettere sul ribasso.
**24 novembre, 16:30 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (206 articoli nuovi in 4 ore; piene le prime tre pagine di
CryptoBriefing e Bitcoinist: la quarta pagina di CryptoBriefing non è piena, quindi quella fonte è coperta; per Bitcoinist qualche articolo
può mancare), mappa delle liquidazioni; nessuna chiusura nuova, nessuna moneta nuova su Coinbase. G1: nessun passo nuovo. **Capito oggi**:
niente di nuovo in questo giro.
**24 novembre, 20:30 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (129 articoli nuovi), mappa delle liquidazioni; nessuna chiusura
nuova, nessuna moneta nuova su Coinbase. G1: nessun passo nuovo (alle 04:17 il ribilancio e le due letture del mattino). **Capito oggi**:
niente di nuovo in questo giro.
**24 novembre, 18:00 UTC, F5 contro G1 nel paper** (domanda del proprietario, `docs/state.md` delle 17:45 e `ops/results/0746`, `0772`):
oggi F5 +0,51%, G1 −0,48%; dal 16 novembre F5 +1,38%, G1 −4,45%; dalla partenza F5 +8,07%, G1 +6,13%; spese F5 12,65 dollari contro
34,42 (circa 0,2 punti: lo scarto viene dalle posizioni). Proposte al proprietario, senza avviare niente: F5 candidata per il conto
piccolo, oppure una prova «ogni giorno con il mercato in tendenza, una volta a settimana senza tendenza».
**25 novembre, 00:30 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (52 articoli nuovi), mappa delle liquidazioni; nessuna chiusura
nuova, nessuna moneta nuova su Coinbase. G1: nessun passo nuovo. **Capito oggi**: nel paper, in un mercato che va su e giù, decidere una
volta a settimana ha battuto decidere ogni giorno di quasi 6 punti in 8 giorni; sul passato le due cose si equivalgono.
**25 novembre, 04:30 UTC, il diciottesimo ribilancio e le letture del mattino**: 4 ordini a limite, gli stessi rifiuti. Fra le letture
delle 04:18 del 24 e del 25 novembre F5 +1,16%, G1 nel paper +0,07%, demo −0,16%; dal 9 novembre demo −0,37%, paper +1,98%. Fatti gravi
(commit be1600b, prima dei prezzi): **AAVE, LINK e UNI su, forza 1** (Fidelity le apre ai suoi clienti al dettaglio; un fatto solo, tre
casi). Monete vendute da G1: nessuna a rischio (Arthur Hayes nomina NEAR e VVV fra le sue preferite: opinione, non fatto). **Capito oggi**:
lo scarto fra demo e paper di G1 continua ad allargarsi (−0,14 punti al giorno in 17 giorni): le monete che mancano sul demo (EVAA, LIT,
UAI, IRYS, PIEVERSE) pesano ogni giorno, in un verso o nell'altro.
**25 novembre, 08:30 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (35 articoli nuovi), mappa delle liquidazioni; nessuna chiusura
nuova, nessuna moneta nuova su Coinbase. Il conto vero esegue F5 (commit 03ee29e, spento, APPROVE di live-path-reviewer per il commit).
Due passi su F5 con strategy-improver: la misura del peso massimo per moneta con la deriva della settimana (problema 180, voce P36) e le
regole della prova 169 «G1 o F5 secondo il mercato» (ogni giorno con una direzione, il lunedì senza), scritte prima del calcolo.
**Capito oggi**: niente di nuovo sul mercato in questo giro.
**25 novembre, 10:00 UTC, quanto può pesare una moneta in F5** (`research/programma7/misure_g1/f5_peso_massimo.md`, 300 settimane dal 2021,
solo misura): al lunedì il peso più alto è 43,7% (BLZ, 5 febbraio 2024), in settimana con i prezzi che si muovono 44,9%: il tetto del 60%
per moneta non si è mai avvicinato. La somma dei pesi invece si allarga in settimana: mediana dei massimi 209,9%, 99° percentile 268%, una
volta 397% (8 febbraio 2021, gli short salivano). La perdita peggiore di una moneta venduta in una settimana è −14,5% del conto (XRP, gennaio
2021, +81%). **Capito oggi**: con le posizioni ferme una settimana il rischio non è una moneta sola troppo grande ma l'esposizione totale che
cresce quando le monete vendute salgono; lo stop del conto a −35% resta l'unica protezione (voce P36).
**25 novembre, 12:00 UTC, prova 169: «G1 o F5 secondo il mercato» non passa** (`research/programma7/RISULTATI_CENTOSETTIMA_BIS.md`): con la
direzione del Bitcoin sui 30 giorni a decidere fra i pesi di G1 (ogni giorno) e quelli di F5 (il lunedì), A fa Sharpe 1,99 e B 2,10 contro
1,97 di G1 e 1,88 di F5, ma lo Sharpe corretto è 0,61 e 0,72 e le spese dei cambi di stato mangiano più della metà del guadagno. L'ipotesi non
regge: nel 2023 la misura dice «con direzione», eppure lì F5 ha battuto G1 di 23 punti; e dal 16 al 23 novembre avrebbe seguito G1, quella
che perdeva. Conto delle prove 340. **Capito oggi**: quando decidere una volta a settimana batte decidere ogni giorno non dipende dalla
direzione del Bitcoin; il vantaggio di F5 di queste settimane non si sa prevedere con una regola semplice.
**25 novembre, 12:30 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (105 articoli nuovi), mappa delle liquidazioni; nessuna chiusura
nuova, nessuna moneta nuova su Coinbase. G1 e F5: le due misure di stamattina sono chiuse (peso massimo di F5, prova 169 no). Ricerca: nessuna
prova in corso. **Capito oggi**: niente di nuovo in questo giro.
**25 novembre, 16:30 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (186 articoli nuovi; tre pagine di CryptoBriefing piene, la quarta no:
la fonte è coperta), mappa delle liquidazioni; nessuna chiusura nuova, nessuna moneta nuova su Coinbase. G1: nessun passo nuovo. **Capito
oggi**: niente di nuovo in questo giro.
**25 novembre, 20:30 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (148 articoli nuovi), mappa delle liquidazioni; nessuna chiusura
nuova, nessuna moneta nuova su Coinbase. G1: nessun passo nuovo (alle 04:17 il ribilancio e le due letture del mattino). **Capito oggi**:
niente di nuovo in questo giro.
**26 novembre, 00:30 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (53 articoli nuovi), mappa delle liquidazioni; nessuna chiusura
nuova, nessuna moneta nuova su Coinbase. G1: nessun passo nuovo. **Capito oggi**: niente di nuovo in questo giro.
**26 novembre, 04:30 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (24 articoli nuovi), mappa delle liquidazioni (600 conti); nessuna
chiusura nuova, nessuna moneta nuova su Coinbase. Fatti gravi: nessun caso nella lettura; con una correzione scritta dopo, prima dei
prezzi, HYPE su (Franklin Templeton la mette nel suo fondo quotato dal 1° dicembre). Voce 14, quinta lettura: le prime due «sì», HYPE e
VVV. Voce 8, diciannovesimo ribilancio: 6 ordini, gli stessi 4 rifiuti; dal 9 novembre demo −0,80%, paper +0,87% (`ops/results/0776`).
**Capito oggi**: il foglio dei fatti gravi mostrava solo 6 titoli per moneta, e il fatto di HYPE era nascosto fra gli altri 11. Da oggi i
due fogli mostrano tutti i titoli.
**26 novembre, 08:30 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (36 articoli nuovi), mappa delle liquidazioni; nessuna chiusura
nuova, nessuna moneta nuova su Coinbase. Righe della quattordicesima revisione del trader AI applicate in `reviews/`. Ricerca: lo scout ha
guardato otto strade (ricerca automatica di regole, annunci letti da un modello, aggiornamenti di rete, ricavi dei protocolli, tassi di
prestito, Wikipedia, residui statistici, Polymarket) e non ha scritto nessuna idea: già provate, dati a pagamento o troppo corti
(`research/idee/LOG.md`). **Capito oggi**: con i dati gratuiti che abbiamo, le strade nuove con storia abbastanza lunga sono quasi finite;
quello che resta sono le misure in avanti già accese.
**26 novembre, 12:30 UTC, giro delle 4 ore**: raccolta 25 fonti su 25 (94 articoli nuovi), mappa delle liquidazioni; nessuna chiusura
nuova, nessuna moneta nuova su Coinbase. G1: nessun passo nuovo (ribilancio e letture alle 04:17). Ricerca: nessuna prova in coda (lo
scout delle 08:17 non ha trovato idee con un perché forte). **Capito oggi**: niente di nuovo in questo giro.
**26 novembre, 16:30 UTC, giro delle 4 ore**: raccolta 24 fonti su 25 (127 articoli nuovi; una pagina di CryptoBriefing piena: qualche
articolo di quella fonte può mancare), mappa delle liquidazioni; nessuna chiusura nuova, nessuna moneta nuova su Coinbase. G1: nessun
passo nuovo. Ricerca: nessuna prova in coda. **Capito oggi**: niente di nuovo in questo giro.
**26 novembre, 20:30 UTC, giro delle 4 ore**: raccolta 24 fonti su 25 (97 articoli nuovi; di nuovo una pagina di CryptoBriefing piena),
mappa delle liquidazioni; nessuna chiusura nuova, nessuna moneta nuova su Coinbase. G1: nessun passo nuovo. Ricerca: al posto dello scout,
su richiesta del proprietario («fai un audit per capire se c'è qualcosa che ci stiamo perdendo nel trovare strategie [...] altri bug da
correggere») parte un audit del sistema in sei aree, ognuna con un verificatore. **Capito oggi**: niente di nuovo in questo giro (l'esito
dell'audit va nel suo rapporto).
**27 novembre, 02:40 UTC, giro delle 00:17 (partito alle 02:12 per il limite d'uso)**: raccolta 24 fonti su 25 (69 articoli nuovi;
CryptoBriefing «piena» è un falso allarme, vedi sotto), mappa delle liquidazioni (600 conti, 2.425 posizioni); nessuna chiusura nuova,
nessuna moneta nuova su Coinbase. **Audit del sistema finito**: 52 problemi, tutti confermati dal verificatore (4 Alti, 26 Medi, 22
Bassi; rapporto `audits/reports/2026-11-26-AUDIT_SISTEMA.md`, backlog P37). Corretti subito: (1) dal 23 al 26 novembre i fogli del
mattino (fatti gravi e voce 14) sono stati preparati prima della raccolta dello stesso giro, e le notizie delle 00:18-04:18 UTC non sono
entrate in nessun foglio (dal 4,5 al 20% degli articoli di ogni mattina, i più freschi): ora i due fogli si fermano se la raccolta ha più
di 15 minuti; (2) VVV era stata tolta dai fatti gravi del 26 per un motivo falso (è nell'elenco del mese): terza correzione sotto il
foglio, la misura si riporta con e senza VVV; (3) lo scout seguiva ancora «al massimo due idee»: ora segue la decisione del 22 novembre.
Le altre correzioni sono al lavoro (un agente per gruppo di file; quelle del percorso degli ordini passano da live-path-reviewer).
Note per le misure: il giro delle 08:17 del 12 novembre manca (5,6 ore senza raccolta fra le 06:13 e le 11:47) e non era scritto; la
«pagina piena» di CryptoBriefing del 26 novembre era un falso allarme (la seconda pagina aveva 16 e 6 articoli nuovi su 30).
**Capito oggi**: la differenza fra demo e paper dal 9 novembre (−1,67 punti) non viene dalle monete che mancano al demo (lo hanno
aiutato di circa +1 punto): sta nelle monete che hanno tutti e due, circa −0,15 punti al giorno, e per più di metà non ha ancora una
spiegazione (fonte: audit, area ordini, sulle risposte 0720-0776). E l'esame delle prove nuove chiede oggi più di quanto chiedono le
regole, per due difetti di conto che vanno in direzioni opposte.
**27 novembre, 04:30 UTC, giro delle 04:17**: raccolta alle 04:18 da una copia pulita del repository (i file della raccolta sono in
correzione), 24 fonti su 25, 21 articoli nuovi; mappa delle liquidazioni 598 conti su 600. Nessuna chiusura nuova, nessuna moneta nuova
su Coinbase. Fatti gravi (preparati alle 04:21, dopo la raccolta): due casi, Monero giù (KuCoin la toglie dal 30 novembre) e Fluid giù
(la sua borsa decentralizzata ferma dopo un controllo di sicurezza). Voce 14, sesta lettura: due «sì», HYPE (il fondo di Franklin dal 1°
dicembre) e NEAR (taglio dell'emissione). Voce 8, ventesimo ribilancio a 1.000 USDT: 10 ordini tutti a limite, 43 variazioni sotto il
minimo, i soliti 4 rifiuti; dal 9 novembre demo +0,49%, paper +2,25%. **L'audit ha chiuso il secondo giro**: il controllo di completezza
ha trovato l'unica area che nessuno aveva guardato, i test automatici di GitHub, e lì 9 problemi reali (in tutto 61). Il più grave:
dal 19 ottobre ogni corsa dei test su GitHub si fermava prima di cominciare (mancava numba nei requisiti), 1.533 corse fallite su 1.537,
e nessuno se n'era accorto. Corretto: `requirements-ricerca.txt` con le versioni fisse, due lavori in parallelo, un limite di tempo
largo, il documento di ottobre segnato come storico; qui i test della ricerca passano tutti (3.142, 9 saltati con il motivo). Il giro
delle 4 ore ora guarda l'esito dei test e lancia a mano il monitor e lo stato. **La revisione di F5 per il conto vero è FAIL a 280-300
USDT** (con i minimi veri il conto rifiuterebbe il 61% delle variazioni: Sharpe 1,40-1,57, 2026 fra −5% e +1%, e il bot non chiude le
posizioni rimaste sotto il minimo), PASS tecnico a 1.000 USDT; il conto vero è spento, la scelta della taglia è del proprietario.
**Capito oggi**: un controllo che nessuno guarda è come non averlo: i test di GitHub erano l'unico controllo automatico su ogni commit
e sono stati fermi per 39 giorni. E una strategia scelta per un conto piccolo va provata con i minimi di quel conto: F5 tiene l'81-84%
del suo Sharpe a 280 USDT, G1 nella prova 148 il 96% (simulatori diversi, rumore di circa 0,1: fonte il rapporto di F5), il contrario di
quello che si pensava il 25 novembre.
**27 novembre, 05:00 UTC, correzioni dell'audit, prima parte (scarico e notizie)**: lo scarico del paper delle candidate non si ferma
più a un errore di una moneta (il 20 e il 26 novembre una lettura interrotta lo aveva fermato a metà, nascosto da «|| true», e il paper
era rimasto ai dati del 23); PAPER.md scrive in fondo «Scarico incompleto» quando mancano monete. La raccolta delle notizie: «piena» si
calcola per sito (il falso allarme di CryptoBriefing del 26), un articolo già visto non si salva di nuovo dopo 10 giorni (17 righe doppie
su 12.866), le ore si leggono sempre in UTC, e cinque sigle contano solo con il «$». La prova in avanti delle notizie è pronta per il 30
novembre (`research/notizie/prova_avanti.py`). **Capito**: il conto automatico sbagliava moneta su cinque sigle (ARK Invest, la società
HIVE, la legge GENIUS, le azioni SATS di Strive, «APR» il tasso annuo: 50 articoli di novembre in tutto, numeri dell'audit); la prova
in avanti dirà ogni settimana quanto pesavano.
**27 novembre, 05:20 UTC, ricerca nuova e registro**: tre cercatori di idee insieme, con lenti diverse (i dati di Binance gratuiti e mai
usati; chi guadagna e come si vede; come lo farebbe un'intelligenza artificiale), poi per ogni idea un controllo che prova a smentirla:
**8 idee con le regole scritte, 8 bocciate prima di ogni calcolo** (idee 160-167: varianti di prove già fallite o fattori pubblicati;
copiare sul passato i conti di Hyperliquid non si può perché l'interfaccia gratuita dà solo le ultime 10.000 operazioni di ogni conto,
quindi si sceglierebbe con il futuro). Il registro: il riepilogo diceva «48 idee aperte» ma contava anche le regole in testa al file e
le voci chiuse a parole; ora legge solo la coda e lo stato di ogni voce (163 voci: nessuna aperta, 9 in avanti, 12 in attesa del
proprietario, dei dati o di una data), e `--cerca` legge anche le idee. Misure: la regola dell'idea 45 (F5 a metà quando il funding
medio dei 7 giorni è sotto −11% l'anno) si conta ogni settimana dal 30 novembre (`paper/funding_medio.py`, primo numero verso l'8-9
dicembre); la misura delle monete gratis della prova 113 è chiusa senza numeri. **Capito oggi**: dal 22 ottobre Binance non apre
perpetui su monete (dei 38 contratti nuovi dal 1° ottobre, 36 sono azioni): le strategie sulle quotazioni nuove di Binance sono senza
materia prima; e le idee nuove con un perché forte si sono esaurite sui dati che abbiamo: tre lenti diverse, nessuna idea sopravvissuta.
**27 novembre, 05:30 UTC, correzioni dell'audit sulla raccolta di Hyperliquid**: metà dei 600 conti della mappa delle liquidazioni non
aveva posizioni a leva, perché il valore in classifica comprende anche il saldo a pronti. Dal 30 novembre si scelgono i 600 con più
posizioni aperte fra i primi della classifica (prova dal vivo delle 04:33, fuori dal repository: 1.228 candidati letti in 239 secondi): i
conti con posizioni passano da 329 a 600, la parte dell'interesse aperto vista dalla mappa dal 19% al 27% per le lunghe e dal 26% al 30%
per le corte. Le balene saltano i conti con il conto a leva a zero (4 delle 20 di questa settimana). Da oggi si salva a ogni giro anche il
mercato intero di Hyperliquid (interesse aperto, funding, premio), che dopo non si recupera. **Capito**: Hyperliquid ci accetta circa
300-360 letture al minuto, non 600 (a 7 al secondo ne ha rifiutate 199 su 1.500); il primo giudizio delle balene, il 30 novembre, sarà
fatto dei soli 24 conti scelti.
**27 novembre, 11:40 UTC, giro delle 08:17 (fatto alle 11:20, in ritardo per il limite d'uso della sessione)**: raccolta delle 11:20
(86 articoli nuovi, 24 fonti su 25; 40 conti dei trader e 600 della mappa letti); controlli in avanti: nessun annuncio di chiusura dei
perpetui dopo il 21 ottobre, nessuna moneta nuova su Coinbase con il perpetuo (245). G1: nessun dato nuovo dopo le letture delle 04:17
(lo stato e il registro del bot si leggono una volta al giorno); il passo di oggi su G1 è l'esame delle varianti (sotto). Ricerca nuova:
la coda non ha idee aperte e i tre cercatori di stamattina hanno già cercato (8 su 8 bocciate), quindi niente cercatore in questo giro.
GitHub: test in corso sugli ultimi commit (l'ultimo finito, delle 07:29, verde); monitor e stato lanciati a mano. Il mattino delle 06:13: il
programma 5 è a posto (M-002 4.048 trade, p 0,24; M-003 1.643, p 0,99; N-002 170, +0,14%); il conto del paper del programma 6 è stato
fermato dal limite di tempo dei comandi in fondo, dopo uno scarico completo (884 monete, nessuna senza il 25 novembre: la correzione dello
scarico ha funzionato al primo giro vero) ed è stato rilanciato alle 11:18. L'esame: la funzione unica (`asticella.esame`) è pronta e
verificata; ogni candidata perde circa 0,03 (168 B da 0,749 a 0,722), nessun verdetto cambia. **Capito oggi**: le settimane di G1 sono
legate fra loro: il suo t robusto è 3,7, non 4,7, e lo 0,945 di quando è stata scelta vale 0,90 con le settimane efficaci (0,87 con 13
ritardi). A una variante di G1 oggi serve uno Sharpe di 2,27 su 300 settimane (G1 ha 1,97). Fonte:
`research/programma6/ESAME_NUMERI_2026-11-27.md`.
