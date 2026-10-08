# Backlog — solo le cose DA FARE o IN ATTESA

**Aggiornato l'8 ottobre 2026, 06:20 ora italiana.** Su richiesta del proprietario qui restano
solo le voci ancora da fare o in attesa di qualcosa. Le voci fatte e le misure già avviate (che si
leggono da sole alla loro data: 3, 7, 14 ott, metà novembre) sono in `docs/backlog_archivio.md`,
con tutti i numeri; il calendario delle letture è nel diario (`docs/andremo_live.md`) e nel
controllo del mattino. Ogni voce qui sotto rimanda all'archivio con la sua sigla per il dettaglio.

**Regola d'ingresso:** ci si mette una voce quando si scopre qualcosa che vale la pena valutare ma
NON si fa subito: cosa, perché rimandata, il numero che l'ha fatta emergere. Senza numero è
un'opinione. **Regola d'uscita:** quando è fatta (il diario dice come e con quale misura) o quando si
decide di non farla, scrivendo perché. **Vincoli:** tutto passa dal GATE, mai solo dal paper; uscite,
size e freni non si toccano fino alle letture del 7-14 ott (revisione del 30 set).

| Gruppo | Voci | Cosa le sblocca |
|---|---|---|
| **0. Aspettano il tuo sì** | nessuna voce nuova: aspetta il tuo ok il testo della versione 4.4 del protocollo (voce P0, gruppo 1) | una tua risposta |
| **1. In lavorazione** | P0 (il protocollo di ricerca: prova di processo fatta il 7 ott; versione 4.4 scritta e rivista, da approvare; poi si rifanno le tre campagne), G7 (fatta il 5 ott: non si sa, 8 contro 16), R1 (fermata il 5 ott), R2 (fatta il 4 ott), J2 (cosa aspetta il sì in dashboard, in automatico), D8 (dati mancanti: attiva dal 1 ott), T2 (curva del vantaggio: primo esito il 2 ott, si rilegge) | lo strumento, poi 2 righe nella lista bianca della VPS |
| **2. Dopo le letture del 7-14 ott** | C5 (sì del 2 ott), I6 (affollamento), K9, K10, G6, B8, E4, I5, D6, T1 | il numero delle letture, poi il tuo sì |
| **3. A metà novembre** | G3 (voto t minimo nel gate) | la lettura H1 |
| **4. Prima dei soldi veri** | C4, K8, K5, K6, K4 | la decisione di passare a soldi veri |
| **5. Solo se serve** | D1 | lo spazio del registro che finisce |
| **6. Parcheggiate da te** | H3, H4, B5, B6, B7 | che tu le riprenda |

---

**Formato (1 ott 2026, J2):** questo file lo legge anche la macchina dopo ogni giro del gate
(`bot/learning/backlog_doc.py`) e lo pubblica in Firebase (`dashboard/backlog`, RTDB `/backlog`):
la dashboard mostra le voci senza una seconda copia da aggiornare. Quindi: un gruppo è
`## N. Nome`, una voce è `### SIGLA. Titolo` (o, nel gruppo 6, `* **SIGLA. Titolo:** testo`), e
le proposte che aspettano il sì del proprietario vanno nel gruppo 0.

## 0. Aspettano il tuo sì

Nessuna voce in attesa del tuo sì.

## 1. In lavorazione

### P0. Il protocollo di ricerca per moneta — Passi 0, 1 e 2 fatti; il 7 ott il proprietario ha scelto di RIFARE le tre campagne della prova con la versione 4.4 («sì, rifalle con queste quattro modifiche»): stima dei trade unica, «nettamente» unico, minimo 70, budget per intero. Testo 4.4 scritto, rivisto in due giri avversari, sul branch principale (b9659df, c4248a3, 3cffbae): DA RIVEDERE DAL PROPRIETARIO; dopo il suo ok si archiviano i tre branch e si riaprono le tre campagne. La campagna di gruppo resta il passo dopo se anche così non esce niente
**Perché:** cinque misure indipendenti dicono la stessa cosa: il gate non trova un vantaggio. Entrate a caso rendono come i segnali (240 trade, ops 0471); dopo la scelta del gate le validate fanno −0,03R su 182 segnali ±0,17 (ops 0498, lettura stampata: «la prossima modifica va nel gate»); una candidata nuova a caso non passa quasi mai (0 su 3.600, ops 0485); i costi superano il lordo (−0,089R netti, +0,088R di costi su 241, ops 0489); il gate rigiocato nel passato, su 8 date, dà promosse peggiori delle bocciate (−0,22R contro −0,14R su 45 trade, non decide, ops 0502). Aspettare il 14 ott non cambia il verdetto.
**Cosa:** salvare `research/PROTOCOLLO.md` (versione 4.2, rivista il 5 ott) ed eseguire il **Passo 0**: fatti (fonte dati e contratti delistati, commissioni, serie degli stop, regole di dimensione e forma di esecuzione del bot), motore con il blocco del periodo chiuso, test di controllo, tabella dei parametri da approvare. Non tocca dati di mercato né il bot. **Regola scritta prima:** il Passo 0 finisce con una tabella e uno STOP; nessuna campagna parte senza l'approvazione dei parametri. **Metro:** la tabella completa, i test di controllo passati, e la risposta alla domanda «il bot può eseguire una strategia scritta come codice?». **Non cambia:** bot, gate, paper, registro; le letture del 7 e 14 ott restano.


### G7. Il gate sul prezzo casuale: quante strategie passa per caso, a 1 ora? — FATTA il 5 ott: candele vere 8 passate su 7.200 (0,11%), rimescolate 16 su 7.200 (0,22%), rapporto 2,0 → per la regola NON SI SA (meno di 10 passate sul vero), ops 0506
**Perché:** a 1 ora il giro vero passa il 2,2% delle prove (218 su 9.840, ops 0468), a 15 minuti lo
0,12% (25 su 20.667, ops 0470); le prime validate a 1 ora entrano nel paper dall'8 ott. **Precisazione
scritta prima dei numeri (4 ott):** le due quote non si confrontano fra loro: la passata a 1 ora rivaluta
soprattutto spec già note a 1 ora (259 su 328, riga ORIGINI di ops 0468), cioè coppie già passate,
mentre il giro «solo urgenti» a 15 minuti è quasi tutto candidate nuove. Il confronto si fa quindi a
parità di tutto: **100 candidate nuove** (generatore del gate, seme 20261004) sulle **72 monete del piano
di R1**, giudicate dal gate di produzione a 1 ora due volte: sulle candele vere e sulle stesse candele
**rimescolate candela per candela** (ogni candela tiene forma e volume, cambia solo l'ordine: stesso
prezzo d'inizio e di fine, nessuna dipendenza nel tempo). Il rimescolamento a blocchi di un giorno della
proposta è stato scartato prima dei numeri: dentro il giorno terrebbe gli schemi veri. **Regola:** quota
sul caso ≥ metà di quella vera → a 1 ora il gate passa soprattutto rumore (la prossima modifica va nelle
soglie del gate, con R1); ≤ un quinto → il gate filtra il rumore (il problema del paper è altrove); in
mezzo → non si sa; con meno di 10 passate sulle candele vere → non si sa (troppo poche per un rapporto).
**Dove:** `scripts/gate_sul_caso.py`, dentro il lancio di R1 (comando `replay-gate`), dopo R2 e prima delle
unità di R1; solo file locali in `data/replay_gate/g7/1h/`; esito in `replay-gate-esito`. Costo stimato
~20 minuti con 4 worker (misurati ~30 s a unità di 100 candidate in locale su candele finte, 144 unità).
15 minuti si aggiunge solo se serve. **Non cambia:** bot, gate, registro, paper.

### R2. Taratura di R1 a parità di candidate — FATTA il 4 ott: 0 passate su 3.600 → lo 0 di R1 è vero (ops 0485); la scelta del piano è in R1b
R1 ha passato 0 candidate su 16.000 in 2 date recenti (17 e 3 set, ops 0458), mentre il gate vero
nell'ultimo giro ne ha passate 44 su 22.632 (0,19%) da un mix di 92 strategie (39 casuali nuove, 28
mutazioni dei quasi-passaggi, 25 rivalutate; ops 0448/0450) che non divide le 44 per origine: non si sa se
le casuali nuove passano quasi mai anche nel gate vero o se R1 è più severo. Prima di spendere le ~36 ore
di macchina rimaste, una prova sola: le stesse 50 candidate di R1 alla data del 17 set (seme della data)
giudicate dal gate di produzione coi dati di oggi sulle 72 coin operate (3.600 coppie), in una cartella
separata dal piano, senza registro né Firebase. **Regola scritta prima dei numeri:** attese 4-7 passate
se le casuali passassero come la media del giro (0,12-0,19%, ops 0423/0448); con ≥ 3 passate R1 è più
severo del gate (difetto da cercare fra holdout, finestre e dati alla data) e si ferma finché non è
corretto; con 0-1 passate lo 0 di R1 è vero e scatta subito il cambio di piano fissato il 2 ott (più
candidate per data, oppure le strategie che il gate ha già visto passare), senza aspettare le 5 date.
Costo ~20-35 min (stima: 3.600 coppie contro 22.632 in 1 h 56, oppure 72 unità × 109 s / 4 processi) e
un'opzione «giudica queste candidate» in `scripts/replay_gate.py`; non tocca bot, gate né paper.

### R1. Rigiocare il gate nel passato — FERMATA dal proprietario il 4 ott (opzione c, dopo R2): il lancio del 5 ott fa solo la prova sul prezzo casuale (G7) e poi toglie il file «attivo»; il gate torna a 8 giri al giorno. La scelta del gate si legge nel fuori campione del 7 e 14 ott
Invece di aspettare il 7-14 ott per sapere se il gate sceglie strategie con un vantaggio vero, si
rifà il gate a 26 date passate e si guarda come sono andate dopo le promosse contro le bocciate.
Regola da scrivere prima dei numeri: promosse meglio delle bocciate oltre il margine → il gate ha un
vantaggio; differenza + margine sotto 0,10R → il gate sceglie la fortuna; altrimenti non si sa.
**Serve:** il tuo sì (prima una prova piccola, poi completa) e 2 righe nuove nella lista bianca
della VPS da aggiungere a mano. **Attenzione tecnica:** non deve scrivere nel registro vero né
cancellare la cache del gate (si caricano i dati fino a oggi e si tagliano in memoria).

### J2. «Cosa aspetta il sì» in dashboard, senza aggiornarlo a mano — in lavorazione (1 ott)
La macchina legge questo file dopo ogni giro del gate e lo pubblica in Firebase; la dashboard mostra
le voci del gruppo 0 («Aspettano il tuo sì») e il resto del backlog. Una sola fonte, nessuna copia.

### D8. Raccolta dei dati mancanti (punto 4 del 1 ott) — ATTIVA dal riavvio del 1 ott 17:24 («[cattura]» nel log del bot)
Dodici dati nuovi, solo raccolta (nessuna decisione cambia: provato con motore ed executor identici
prima e dopo, `tests/test_dati_parita.py`): versione del codice e impostazioni per trade e per avvio;
promessa del gate congelata all'ingresso; verdetto del trailing alla maniera del gate; cosa fa il
prezzo dopo OGNI uscita; il motore rigiocato sullo stesso segnale; percorso dello stop e armamento del
lock; qualità dell'ingresso (prezzo del segnale, ritardo in R); scarti silenziosi contati; una riga al
giorno per sempre (`giorni/{data}`); regime globale all'ingresso; storia del gate in file locali;
motivo d'uscita nel motore. I punti 11 e 12 (gate) partono da soli al prossimo giro; gli altri col
riavvio del bot. **Resta da fare:** gli scarti silenziosi sono contati ma non simulati (costerebbe una
lettura Firestore per segnale); `data/gate_storia` non ha una pulizia automatica (~1-4,5 MB al
giorno, stima): da aggiungere se il disco lo chiede.

### T2. La curva del vantaggio del segnale — FATTA il 2 ott: «nessun vantaggio misurabile» (ops 0437); la sezione resta nel report `mfe` e si rilegge col crescere dei trade
Prima di toccare i TP, misurare SE e PER QUANTO i segnali delle strategie validate hanno un vantaggio:
sui trade del motore fuori campione, il movimento medio dopo 1, 4, 12 e 24 ore (in mosse tipiche di
24 ore della moneta) contro ingressi a caso sulla stessa moneta negli stessi giorni, con margine. Zero
parametri nuovi, sola lettura, non tocca bot, gate né paper: si può fare subito. Dice dove va messo il
TP (dove la curva smette di salire) o l'uscita a tempo. **Regola da scrivere prima dei numeri:** se a
tutte le durate la differenza dal caso sta dentro il margine, il lavoro sui TP si ferma e il problema
è l'ingresso. Contesto: domanda del proprietario «un trader quant serio come costruisce i TP?» (2 ott)
e revisione critica nel diario; legata a T1 e a R1.

## 2. Dopo le letture del 7-14 ottobre (toccano gate, size o freni)

### C5. Costi allineati a quelli veri di Binance — SÌ del proprietario il 2 ott, da fare DOPO le letture del 14 ott
Verifica sul codice e sulle tariffe ufficiali (FAQ Binance Futures, ricontrollata da un secondo
revisore). (1) **Commissioni troppo basse:** il modello usa 0,08% andata e ritorno
(`BACKTEST_COST_PER_TRADE`, `executor.py:178`, `engine.py:616`, `discover_strategies.py:3617`); Binance
USDⓈ-M al livello base fa pagare 0,05% a lato da «taker» = 0,10% (0,09% pagando in BNB). Effetto sul
paper: +4,77 USDT su 222 trade (−79,86 invece di −75,09), ~+0,012R a trade; nel gate PF −0,03/−0,04.
(2) **Funding giusto nel totale (−0,01 USDT), sbagliato nella struttura:** il tasso di ogni scadenza è
trattato come se fosse ogni 8 ore (`costs.py:27-39`), ma molte monete piccole pagano ogni 4 ore e quelle
«tirate» ogni ora (regola Binance dal 2 mag 2025): sottostimato ×2 o ×8 proprio dove pesa. (3) **Stop
senza scivolamento** (già K8): ~2,3 USDT per ogni 0,01% di scivolamento. (4) **Spread** plausibile ma
misurato una volta sola, a mercato calmo, prima dell'8 set. Gate e paper restano allineati fra loro.
**Proposta:** commissioni a 0,10% e funding con la sua scadenza vera, insieme nel bot e nel gate, con
la data scritta. Cambiano i verdetti del gate (le coppie vicine a PF 1,25), quindi **meglio dopo le
letture del 14 ott**, per non spostare il metro a metà misura. Prima: verificare che il `.env` della
VPS non cambi già il valore (campo `versione` dei trade dal 1 ott). Dettaglio nel diario del 2 ott.

### I6. Troppe posizioni nello stesso verso insieme (misura dal 2 ott)
Il 2 ott alle 20:47 10 long aperti in 20 s (ops 0442-0443): in parità il bot apre tutti i segnali
validi, il tetto di 5 è spento, il tetto per direzione è in rischio (3%) e con le puntate ridotte
ammette ~20 posizioni; la correlazione blocca solo chi arriva dopo. Nella simulazione il tetto per
direzione alza il PnL e abbassa il drawdown (ops 0387). **Misura** nel report `trades`, sezione
AFFOLLAMENTO (R per fascia 1-2 / 3-5 / 6+, ondate). **Da decidere dopo le letture:** un tetto sul
NUMERO di posizioni per verso (es. 5) o un tetto per direzione che non si riduca col freno.

### K9. La leva torna a 2x dopo una sola vincita
Con peso > 0,80 una strategia torna a leva piena, e ci si arriva con 1 vinta su 1 (`adaptation.py`,
`risk_manager.py`, `metrics.py`). Il 1 ott XPL e TST erano a 2x. È fortuna amplificata e non passa
dal gate. **Proposta da decidere:** un minimo di trade prima che il peso alzi la leva.

### K10. La soglia del win rate abbassata dal supervisore (seconda parte)
Il supervisore l'ha portata da 0,45 a 0,3966 (`tuning.env`) e non l'ha più rimessa. Primo conteggio
(ops 0403): 7 validate su 208 esistono solo grazie alla soglia bassa e nel paper fanno +0,244R su 11
trade, contro −0,054R su 50 di quelle a ≥ 0,45: nessun segno contro, campione minimo; 129 validate
non hanno il win rate salvato. **Da decidere:** rimetterla a 0,45 o no, col conteggio riletto
(sezione «SOGLIA DEL WIN RATE» del report `trades`).

### G6. Pesare di più i dati recenti anche nella validazione
Oggi la recenza (emivita 180 giorni) pesa solo nella scelta di scala, break-even e keep; i criteri
del gate no, quindi chi entra non cambia. Pesare anche la validazione cambia quali coppie passano:
si decide col tasso di passaggio prima/dopo come metro.

### B8. Le varianti giudicate senza i giorni del paper (seconda metà) — dal 2 ott le varianti dai referti sono SPENTE (DISCOVERY_VARIANTI_REFERTI=false): da riaccendere solo col taglio di pre-registrazione
Le varianti nate dai referti dovrebbero essere giudicate solo sui dati PRIMA del paper che le ha
fatte nascere (pre-registrazione). Il taglio è spento dal 24 set (`DISCOVERY_VARIANTI_TRONCATE=false`)
perché raddoppiava la memoria dei worker e ha ucciso quattro giri. Finché è spento, le figlie si
giudicano anche sulle perdite che le hanno generate. **Si riaccende** quando la memoria lo permette;
finora le varianti promosse sono 0 (ops 0391).

### E4. Strategie quasi gemelle e `min_adx` sulle spec già validate
Le nuove gemelle non entrano più; quelle già validate si stampano a ogni giro (`gemelle_validate`) e
vanno decise (tenerle tutte, una per coin, o nessuna). Resta anche `min_adx` sulle spec esistenti,
che seleziona i casi peggiori (salite verticali vendute short, MUBARAKUSDT 21 set +37%).

### I5. Validate senza la loro promessa nel registro
Molte validate non hanno `last_pf` (e ora si è visto: 129 su 208 senza `last_win_rate`), perché sono
state alleggerite prima della promozione. Per loro deriva e veto di regime non agiscono. Si
riempiono da sole quando ripassano il gate; riempirle prima riaccenderebbe il veto di regime, che è un
freno: per questo dopo le letture.

### D6. Le leve della spesa AI — il 2 ott SPENTE idee AI e autopsia (AI_HYPOTHESES_ENABLED=false): spesa attesa ~0 $; resta aperto solo se si riaccendono
Spesa misurata il 30 set: 2,80 $ in 57 chiamate (idee 55%); con filtro monete e ombra spenti dal 30
sera, stima circa 2,10 $ al giorno. Leve, nessuna fatta: (1) idee e autopsia una volta per giro invece
di due (~−0,95 $/giorno, stima); (2) idee solo al giro completo (~−1,3 $/giorno, ma meno idee);
(3) modello più economico (scelta tua). Prima si legge la riga «ORIGINI» del gate (fatta il 1 ott):
se le idee AI non producono validate, la leva (2) costa poco.

### T1. I take profit non si adattano al singolo trade (verificato il 2 ott) — CONGELATA dalla regola di T2 finché la curva del vantaggio non mostra un vantaggio
Oggi la scala dei TP (multipli di R) è scelta dal gate PER COPPIA e congelata all'apertura
(`bot/main.py:1795`, `:1818`; `executor.py:76-83`); per trade cambia solo il prezzo, perché R dipende
dall'ATR del segnale (`exit_logic.py:132-137`, `strategies/base.py:112`). Il paper propone scale
candidate (`scala_dal_paper`, scala per strategia con ≥ 5 trade: `discover_strategies.py:835-933`),
il gate decide sulla storia. Numeri: 111 coppie su 209 hanno la scala 2/4/6 (primo TP a 2R) mentre
il massimo a favore mediano dei trade è 0,85R e solo il 16% arriva a 1,5R; l'89% dei trade non tocca
nessun TP (`docs/state.md` del 1 ott 23:53 UTC; ops 0394, 0417). Cose non fatte, da valutare dopo le
letture (toccano le uscite): (a) misurare nel paper le 5 coppie con scala dal paper contro le altre;
(b) scegliere scala, pareggio e keep INSIEME, non uno dopo l'altro (`:2082-2117`); (c) cercare anche
le quote 30/30/40, oggi fisse; (d) le esplorative usano sempre la scala globale 1,5/3/5; (e) la scala
globale dal paper mescola i timeframe; (f) multipli scelti all'apertura dalle condizioni del momento
(volatilità, ADX) — solo se passa dal gate: i TP sui livelli del grafico sono già stati smentiti (A5).
**Misura del 2 ott (ops 0419, sezione nuova del report `mfe`)** sulle 7 posizioni aperte: da ingressi
casuali negli ultimi 90 giorni della stessa moneta, entro 96 candele e prima dello stop, il TP3 arriva
0-16% delle volte (CROSS a +23,7%: 4%; ENA a −12,4%: 0%; HUMA a −12,8%: 1%) e il TP2 5-23%; il
massimo a favore mediano in 24 ore va da 1,6% a 5,5%. Nel paper il 1% dei trade prende 2 o 3 gradini.
Il TP3 (40% della posizione) sta spesso oltre quanto la moneta si muove in un giorno: la scala in R
non guarda l'orizzonte di 24 ore. Idea da dare al gate dopo le letture: candidate di scala tarate sul
movimento tipico della moneta nell'orizzonte del trade. **Revisione del 2 ott (domanda «come costruisce i TP un quant serio?»):** i TP vanno misurati sul
movimento della moneta nel tempo del trade, non sullo stop (due «orologi» diversi), e scelti sul
guadagno medio, non sul rapporto rischio/rendimento. Oggi i TP decidono poco: l'89% dei trade non ne
tocca nessuno; decidono lo stop (44% delle uscite, −256,82 USDT) e la protezione del profitto (45%,
+98,61 USDT: `docs/state.md` del 1 ott 23:53 UTC). Attenzione: la protezione si arma a metà del
primo TP (`exit_logic.py:175-188`), quindi spostare il TP1 sposta anche lei. In ordine, dopo le
letture e solo se T2 mostra un vantaggio: (1) scala in «mosse tipiche di 24 ore» (ATR a 1 ora x √24),
UNA PER FAMIGLIA invece che per coppia, 2 candidate scritte prima, convertite in R all'ingresso
(l'executor non cambia), livello di armo della protezione fermo in R; prova contro la scala di oggi
nelle finestre e su date mai viste (R1); si scarta se non vince del 10% in 2 finestre su 3 o se
cambia segno spostando i TP del ±25%; (2) per le strategie di ritorno alla media (~70% dei trade
simulati delle passate, ops 0396) TP sulla media (banda di mezzo fissata all'ingresso), stessa prova.
Rinviate: ricerca congiunta scala/pareggio/keep (3-4 volte il tempo del giro), ricerca delle quote,
trailing «chandelier» per il trend. Nota: le scale ricavate dal paper (`ladder_from_mfe`) imparano
dalle uscite di oggi, che tagliano l'mfe: da togliere quando arriva (1). Note: la riga «0 con almeno 5 trade» del log del gate (ops 0411) conta solo la corsia urgente, non le
strategie con scala propria (11 il 1 ott, ops 0386); il freno di deriva confronta l'mfe con il primo
gradino GLOBALE (1,5R), non con quello della coppia (`drift.py:575-576`).
**4 ott (domanda del proprietario: «abbassare il primo incasso a 0,8R?»).** Risposta: non prima del 14 ott. Numeri a favore: nel modello semplificato le scale strette perdono meno (1/1,5/2,5 −0,35R contro 2/4/6 −0,85R su 264 trade, ops 0471); 58 stop su 111 morti sotto il primo gradino con mfe mediana 0,49R. Contro: senza vantaggio all'ingresso cambia la forma, non il segno; e il gate ha già 0,75/1,25/1,75 fra le candidate e la sceglie per 5 coppie sole, perché sulla storia le scale larghe rendono di più. Fatto: colonna 0,8/1,6/2,4 SOLO MISURA nella tabella del report `mfe` (`SCALE_SOLO_MISURA`); si legge il 7 e il 14 ott. Se regge, la mossa è far decidere al gate coppia per coppia.

## 3. A metà novembre

### G3. Un voto t minimo nel gate
La regola H1 è già decisa (solo la t dell'ultimo esame, soglia 1,5, almeno 80 segnali per gruppo).
A metà novembre: se le t alte rendono più delle basse oltre il margine, si propone la soglia nel gate;
se differenza + margine sta sotto 0,25R, l'idea si chiude.

## 4. Prima dei soldi veri (si fanno dopo il 14 ott, quando si decide di passare a soldi veri)

### C4. Nessuna pausa sugli annunci USA (FOMC, CPI, lavoro)
Il bot tiene le posizioni aperte durante i dati macro. Nessuna fonte gratuita e affidabile del
calendario è stata trovata (FRED vieta l'archiviazione). Va fatto prima dei soldi veri, non prima:
adesso renderebbe il paper diverso dal motore e sporcherebbe le letture.

### K8. Lo stop chiude esattamente al suo prezzo
Motore e paper chiudono lo stop al prezzo esatto, senza scivolamento (`executor.py`). Con soldi veri
non succede. I costi pesano già: 0,08R a trade (ops 0401).

### K5. Il quarto di size agisce poco con stop stretti
Con stop stretti il tetto per posizione taglia comunque, e declassata e attiva rischiano quasi uguale
(es. stop 1,3%: 0,125% contro 0,130%); con stop larghi agisce davvero. Il controllo scrive «size
ridotta» anche quando non lo è.

### K6. Il freno globale ha un'uscita irraggiungibile
Per spegnersi chiede un massimo toccato mediano sopra 1,05R: il paper è a 0,87R, il motore a 1,03R,
un prezzo casuale a 0,81R. Se si accende, di fatto non si spegne più.

### K4. Il paper per ora non si distingue dal caso
Con le nostre uscite, un prezzo casuale dà quasi gli stessi numeri del paper (stop 46% contro 46%,
vinti 54% contro 54%, ops 0401). Non è un lavoro da fare: è la condizione da superare prima dei soldi
veri. Lo diranno le letture.

## 5. Solo se serve

### D1. Il registro su più documenti
L'unico rimedio che scala, ma tocca bot, learning, quattro script e la dashboard: farlo di fretta
rischia di perdere settimane di conferme. Oggi c'è spazio per circa 17-18 giorni (stima del 1 ott,
dopo K2): si fa se la riga «ci stanno ancora ~N coppie» del gate scende sotto ~500 (soglia proposta, non decisa).

## 6. Parcheggiate da te

Restano solo come memoria; si riprendono se lo chiedi.

### H3. Stop giornaliero
Il bot si fermerebbe per il resto del giorno dopo una perdita (es. 3%). Tu: «non voglio limitare la
quantità, voglio trade migliori». Rigioco del 1 ott (ops 0404 paper, 0405 gate): sul paper +2,00 (3%)
e +5,09 (2%) su −81,11; sul portafoglio del gate −11.615 (3%) col drawdown da 11,7% a 20,3%. Sul paper
aiuta solo perché toglie esposizione a un sistema che perde: confermato il parcheggio.

### H4. Freno di serie
Meno size dopo una serie di perdite. Win rate dopo 4 perdite di fila 62,5% su 8 contro 68,2% (ops
0387, t −0,34): nessuna prova che serva. Rigioco del 1 ott: sul paper il migliore (3 perdite del bot
→ metà) +15,62 su −81,11; sul gate −3.957. Confermato il parcheggio.

### B5. Notizie e dati macro
Dati esterni: nessuna fonte gratuita e verificata (vedi C4).

### B6. Storico di open interest e long/short
Gratis ma mai usato; servirebbe come variabile nuova del gate.

### B7. Registrare noi lo storico da oggi
Non è «una riga di codice»: dettaglio nell'archivio.
