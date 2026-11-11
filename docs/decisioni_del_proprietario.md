# Le decisioni del proprietario e la storia dei protocolli (testo intero)

Spostato qui da `CLAUDE.md` il 7 novembre 2026, **parola per parola**, per tenere `CLAUDE.md` corto (si carica in ogni sessione e in
ogni subagent: regole dei token, richiesta del proprietario del 7 novembre). In `CLAUDE.md` resta l'elenco breve delle decisioni in
vigore. **Leggi questo file quando serve**: per citare una decisione alla lettera, per riaprire una campagna di ricerca con un
protocollo, o quando una decisione dell'elenco breve non basta.

## Cos'era questo sistema e le decisioni del proprietario (dal 13 ottobre al 5 novembre 2026)

Bot di trading crypto autonomo, in **paper trading**. Gira su una VPS Hetzner, tiene
lo stato su Firebase, e la dashboard Next.js (Vercel) lo mostra. La ricerca delle
strategie e' un job separato (`scripts/optimize.py`, `scripts/discover_strategies.py`)
che girava ogni 3 ore e alimentava il registro `strategy_registry/validated`. **Dal 13 ott 2026 la ricerca
automatica del gate è FERMA** (file `ops/gate_fermo`, sì del proprietario): il paper resta acceso come banco di
misura, con gli ingressi a ordine limite (`bot/execution/executor.py`, misure in RTDB `/paper/ordini_limite`).
La ricerca riparte con il **protocollo 3** (`research/PROTOCOLLO_3.md`: la versione 5.1 su BTC scritta dal
proprietario, con il collaudo del metodo; approvato il 16 ott 2026 alle 19:26 UTC). Prima si collauda il metodo
(Passo 0, sezione 13bis: tre prove), poi una sessione di ricerca sul branch `research/campagna/BTC51` cerca le
strategie su BTCUSDT; il paper è l'esame finale. La seconda edizione (`research/PROTOCOLLO_2.md`) è chiusa.
**Il vault 3 è stato aperto il 17 ott 2026** (frase del proprietario): l'unico candidato, V-020, non lo supera
(`research/vault/BTC51_risultati.md`), e sulle altre monete regge solo su 1 di 9 (`research/altre_monete_3/risultati.md`).
**La campagna BTC51 è chiusa** (17 ott 2026, nessuna strategia valida): lezioni e proposte per il prossimo protocollo
in `research/campagne/BTC51/lezioni.md`. **Dal 17 ott 2026 vale il protocollo 4** (`research/PROTOCOLLO_4.md`, versione 6,
approvato alle 20:12 UTC): ricerca su LINKUSDT con 9 monete di controllo, campagna `LINK6` sul branch
`research/campagna/LINK6` (rientra nell'eccezione dei branch di ricerca), vault con la frase esatta «APRI IL VAULT 4»
scritta al coordinamento. Decisioni e motivazioni in `research/protocollo_4_note.md`. **La campagna LINK6 è chiusa** (18 ott
2026, nessuna strategia valida: 33 varianti su 40, nessun candidato, vault 4 mai aperto): lezioni e proposte in
`research/campagne/LINK6/lezioni.md`. **Decisione del proprietario (18 ott 2026, ~08:40 UTC):** «dobbiamo continuare
fino a quando non trovi delle strategie valide... se serve riscriviamo totalmente il gate», ma prima va scritta la storia
completa del progetto (dati raccolti, cosa abbiamo imparato, cosa abbiamo cambiato, errori da evitare) in `docs/storia/`,
da leggere prima di ripartire (`docs/backlog.md`, P11). **Delega del proprietario (18 ott 2026, sera):** «non continuare a
chiedermi le autorizzazioni, procedi ad oltranza fino a che non avrai trovate delle strategie profittevoli che devono valere
le crypto ad oggi in corso, continua a lavorare in background se un job finisce e non ottieni risultati, registra e passa
ad un'altra idea e così via.. scrivimi solo quando avrai trovate diverse strategie che si possono applicare a diverse crypto
anche se ci volessero dei giorni». È il **programma 5** (`research/programma5/`: regole in `REGOLE.md`, stato e coda delle
idee in `STATO.md`): il coordinamento lavora da solo, non chiede permessi e non scrive al proprietario finché non ci sono
più strategie valide su più monete; restano ferme le regole che non si negoziano (`DRY_RUN` vero, niente soldi veri, niente
segreti, paper mai usato come training set) e il metodo (regole scritte prima, confronto con il caso, periodi usati una
volta, conferma sui dati recenti). Il proprietario, 18 ott 2026 ~17:15 UTC: «non chiedermi ogni volta di continuare, procedi in
autonomia fino a quando non mi presenterai delle strategie validate e in profitto ... devi analizzare l'intero universo o
almeno le top 100 su binance future ... se ci vogliono giorni va bene» (`research/programma5/REGOLE.md`, sezioni 7 e 7bis:
fase 2 sui dati recenti, universo delle 100 monete più scambiate). Il proprietario, 19 ott 2026: «comprare e tenere 12 ore non è trading
[...] trovare delle strategie [...] partendo dagli indicatori tecnici [...] il passato è pubblico [...] riprovare con metodo e
non a caso [...] non voglio aspettare dati nuovi [...] usa limit o margin, tutte le crypto del future binance»: è il
**programma 6** (`research/programma6/METODO.md`): strategie a indicatori con stop, obiettivo e stop che segue il prezzo,
provate con le finestre che avanzano (scelta su 12 mesi, prova sui 3 dopo, dal 2020 a oggi) e le correzioni per i tentativi. Il
proprietario, 19 ott 2026 sera: «continua a cercare in autonomia, non fermarti se pensi serva misurare in paper procedi hai
campo libero fino a che non trovi cosa funziona»: il coordinamento cerca da solo e può misurare in paper (`DRY_RUN` vero,
niente soldi veri) le strategie candidate; registro delle prove in `research/programma6/STATO.md`. Il proprietario, 20 ott
2026: «continua a cercare in autonomia ed in continuazione, fai girare modelli su modelli [...] traccia tutto quello che stai
facendo e provando in un log o diario così da non ripetere le stesse cose ma soprattutto traccia anche i vari risultati [...]
l'unico motivo per cui ti puoi fermare è se abbiamo strategie per tutte le crypto e nel momento in cui queste hanno lo stesso
riscontro nel paper»: **il registro unico è `research/REGISTRO.md`** (si guarda prima di ogni idea nuova, ogni prova ha la
sua riga prima e il risultato dopo, con la coda delle idee). Il proprietario, 21 ott 2026: «io non farò trading su [Gate.io] [...] perché devo aspettare il 2 novembre o fine novembre? non è quello che avevo chiesto» e «forse è meglio che il paper con il vecchio gate si fermi e la dashboard venga pulita [...] parti con il paper nuovo»: si giudica sul passato di Binance (il paper è una conferma, non una condizione); la dashboard parte dalla scheda «Strategie nuove» e le schede del vecchio sistema stanno sotto «Vecchio sistema (fermo)»; il vecchio paper si ferma con il pulsante STOP della dashboard (il kill switch). Il proprietario, 22 ott 2026: «accendi f5 [...] la
decisione di portare le strategie in paper anche questa falla in autonomia senza che io ti dica nulla nel momento in cui
pensi sia giusto»: F5 gira nel bot in paper (`bot/portafoglio/f5.py`, interruttore `ops/paper_f5_acceso`), e il
coordinamento decide da solo quali strategie portare in paper e quando (sempre `DRY_RUN` vero, niente soldi veri), e lo
scrive nel diario. **Il proprietario, 23 ott 2026** (arrabbiato, e con ragione): «io voglio anche fare trading tutti i giorni non solo
tenere una settimana (non te l'ho mai chiesto, anche se lo posso accettare come alternativa se è profittevole) [...] ti ho chiesto
di fare trading tutti i giorni»; e subito dopo: «l'obiettivo è fare soldi, un sistema che sia profittevole [...] non hai
limitazioni su quali strategie adottare, scalping oppure settimana oppure nuovi listing [...] l'importante è che non ti perdi delle
idee per strada, prova di tutto sempre con il criterio che ci siamo dati ma non lasciare nulla al caso [...] il trading giornaliero
non può essere escluso». Quindi: **l'obiettivo è il profitto, con qualunque tipo di strategia** (in giornata, scalping, a
settimana, eventi e nuove quotazioni), sempre con il metodo (regole prima, conto delle prove, asticella, revisore separato); il
trading di ogni giorno ha il suo filone, il **programma 7** (`research/programma7/METODO.md`), e non va mai lasciato indietro. **Il proprietario, 24 ott 2026:** «usiamo i dati passati e simuliamo con paper / live demo per qualche giorno, settimana, ma poi se funziona andiamo live» e «non bocciare 0,91 se ogni anno si alza la soglia»: una strategia con lo Sharpe corretto da 0,90 in su, ogni anno positiva e con il t sopra 3 non si boccia, va sul demo di Binance e nel paper, e poi ai soldi veri quando il proprietario lo chiede esplicitamente (`docs/backlog.md`, P26; `research/REGISTRO.md`, sezione 1). Le idee si prendono anche dai trader da copiare (`research/trader_copiati/`). **Il proprietario, 1° nov 2026:** «verdetto dopo 52 settimane? questo è inaccettabile, cosa usiamo a fare il backtesting e demo»: **niente attese fisse** (né 26, né 52, né 104 settimane) per nessuna misura in avanti; i numeri gli vanno ogni settimana, e ciò che passa la sua regola sul passato va subito in paper e sul demo (`research/programma6/paper/REGOLE.md`, sezione 17). **Il proprietario, 5 nov 2026:** «si cambia, e sono d'accordo miglioriamo quello che già funziona»: il giro delle 4 ore raccoglie i dati (notizie, Hyperliquid, controlli in avanti) e poi lavora a migliorare G1 (`research/programma7/MIGLIORARE_G1.md`, una voce alla volta, prima la misura); un'idea nuova di strategia solo con un perché forte, perché ogni prova in più alza l'asticella per tutte.
**Tutte le idee**, di ogni tipo e anche quelle del proprietario, stanno nella coda unica di `research/REGISTRO.md` (sezione 5):
nessuna si perde, ognuna o si prova o si scrive perché no. **Delega del
proprietario (17 ott, 21:10 UTC):** il coordinamento va avanti da solo con i passi (correzioni del collaudo, apertura
della sessione di ricerca, STOP, via libera alla validazione) senza chiedere il permesso, e lo informa; il vault no.


## Il protocollo di ricerca (dal 6 ott 2026)

Le strategie nuove nascono dal **protocollo di ricerca per moneta** (`research/PROTOCOLLO.md`,
versione 4.5, testo approvato dal proprietario il 9 ott 2026 alle 12:06 UTC): idee con un perche', periodo chiuso
(«vault», 2024-01-01 → 2026-09-30) che si apre una volta sola, un branch per campagna e un
guardiano meccanico (`research/src/guardiano.py`, attivo solo se esiste `research/.sessione`).
Chi lavora in una sessione di campagna legge solo i percorsi ammessi dal Passo 3 del
protocollo e non scrive ipotesi o risultati in questo file. Il gate attuale resta acceso come
gruppo di controllo finche' il proprietario non decide altrimenti.
Dalla 4.5 (sì del proprietario del 9 ott 2026) le sessioni delle campagne rimanenti le apre il coordinamento su
delega, al massimo tre campagne in corso, con il messaggio di apertura approvato (`research/apertura/campagna.md`
sul branch di coordinamento), un controllo ogni ora e le domande delle campagne girate subito al proprietario
(Passo 4 del protocollo). La prova a placebo dell'esame (`research/taratura/placebo/`, branch di coordinamento)
dice che l'esame regge sui prezzi veri.
**Dal 16 ott 2026 vale il protocollo 3** (`research/PROTOCOLLO_3.md`): una sola campagna, `BTC51`, su BTCUSDT.
Il Passo 0 (strumenti e collaudo del metodo) e i Passi 5-8 li fa il coordinamento sul branch principale; i Passi 1-4
una sessione di ricerca sul branch `research/campagna/BTC51`, con il marcatore `{"tipo": "campagna", "simbolo":
"BTC51"}`, aperta solo dopo il sì del proprietario agli esiti del Passo 0. Il vault si apre solo con la frase
esatta «APRI IL VAULT 3». Il branch `research/campagna/BTC51` rientra nell'eccezione dei branch di ricerca.

**Ogni sessione di campagna si apre con il modello `claude-opus-5-5` e con ultracode attivo** (richiesta
del proprietario, 8 ott 2026). Nella creazione si passano la sorgente del repository e il branch principale;
modello e ultracode si ereditano dalla sessione che crea (per ultracode non c'e' un parametro). L'eredita'
non e' sicura: l'8 ott le sessioni create fra le 05:12 e le 05:20 UTC avevano ultracode dalla creazione, le
tre create fra le 13:24 e le 13:50 UTC no, con o senza `model` passato, con gli stessi parametri; la causa
non e' nota. Dopo la creazione si controlla con `get_session` che il modello sia `claude-opus-5-5` e che
`external_metadata.flag_settings.ultracode` sia `true`; se manca, non si riapre a ripetizione: si dice al
proprietario, che decide se lasciarla lavorare o fermarla.

## 8 novembre 2026: le strategie in corso restano tutte, due agenti nuovi, la ricerca nuova con gli agenti

Le parole del proprietario (8 novembre, mattina): «va bene con le idee da te proposte, una cosa procedi con la creazione
dell'agente/i mancante, non puliamo il vault .. UNA COSA IMPORTANTE NON VOGLIO CHE NESSUNA DELEL STRATEGIE ORA IN PAPER O IN DEMO
VADA PERSA [...] DEVONO RIMANERE TUTTE IN CORSO, QUESTE SONO LE UNICHE SU CUI STIAMO TESTANDO LIVE E CHE POTREBBERO ANDARE CON SOLDI
VERI [...] poi a mio avviso serve un altro agente ma lascio a te che decida in live o con un demo combinata come usare diverse
strategie in produzione (ora ne abbiamo G1, G11, G1 Neutra e F5) che potrebbero tutte andare live ma il sistema a decidere quale è
meglio». Prima: «lascia g1 ogni 4 ora».

Le idee approvate («va bene con le idee da te proposte»): un agente che migliora le strategie in corso; il riesame delle prove
bocciate di poco (non il rifacimento di tutta la ricerca); la ricerca nuova con gli agenti: la 1:1:1 (una moneta, un intervallo, una
strategia) su 4 ore e un giorno, con un filtro veloce sul passato e poi in avanti nel paper con l'elenco e il criterio scritti prima,
le monete nate dopo ottobre, le idee in coda; il revisore delle prove sulle cinque strategie del paper. Il vault non si pulisce.

Cosa ne è venuto: `strategy-improver` e `portfolio-allocator` in `.claude/agents/` (memorie in `research/miglioramenti/` e
`allocazione/`); la regola in `CLAUDE.md`; il test `tests/test_strategie_restano_accese.py`, che fallisce se si toglie l'interruttore
di una delle sei strategie (G1 sul demo, G1, G1 neutra, G11, F5, eventi) o se il bot smette di crearla o di farla girare.

## 11 novembre 2026: la ricerca nuova non si ferma, le aree separate

Le parole del proprietario: «ok ma non fermarti a cercarne di nuove, non dico che queste non sono abbastanza ma dovremmo continuare a
provare cose nuove, dovremmo avere un sub agent per questo corretto?». Prima, lo stesso giorno: «una cartella con crypto dove ci
scrivi solo tu, una cartella con stock dove ci scrive l'altra sessione e altre cartelle che magari creo dopo tipo Forex» e «ok procedi
con la mappa e il blocco». Cosa ne è venuto: l'agente `strategy-scout` (le idee nuove con le regole scritte prima), il giro delle 4
ore con due binari (migliorare G1 e far avanzare la ricerca nuova), la prova 149 (la 1:1:1) partita; la mappa delle aree `AREE.md` con
il blocco `.claude/hooks/aree.py`. La decisione del 5 novembre («un'idea nuova solo con un perché forte») resta per la qualità delle
idee, non per la loro frequenza.
Più tardi, sempre l'11 novembre, dopo il riesame della prova 28 (`audits/reports/2026-11-11-PROVA28_K2_F5M7K2.md`): «ok va bene così,
famiglie e misurala a tavolino». Lo Sharpe corretto dell'esame si calcola contando le famiglie di prove simili (come per G1 e per
l'asticella del 22-23 ottobre), non le prove una per una; la miscela F5 + M7 + K2 non entra nel bot: si misura a tavolino ogni
settimana così com'è (`research/programma6/paper/PAPER.md`, riga «F5 + M7 + K2 a rischio uguale»), e se conferma si costruiscono nel
bot i due pezzi che mancano (K2 e M7), con le revisioni.
