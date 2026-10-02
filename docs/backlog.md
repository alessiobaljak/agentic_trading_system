# Backlog — solo le cose DA FARE o IN ATTESA

**Aggiornato il 1 ottobre 2026, 17:00 ora italiana.** Su richiesta del proprietario qui restano
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
| **0. Aspettano il tuo sì** | C5 (costi allineati a Binance) | una tua risposta |
| **1. In lavorazione** | R1 (il gate rigiocato nel passato: sì del 1 ott), J2 (cosa aspetta il sì in dashboard, in automatico), D8 (dati mancanti: attiva dal 1 ott), T2 (curva del vantaggio: primo esito il 2 ott, si rilegge) | lo strumento, poi 2 righe nella lista bianca della VPS |
| **2. Dopo le letture del 7-14 ott** | K9, K10, G6, B8, E4, I5, D6, T1 | il numero delle letture, poi il tuo sì |
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

### C5. Costi allineati a quelli veri di Binance (verifica del 2 ott, richiesta del proprietario)
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

## 1. In lavorazione

### R1. Rigiocare il gate nel passato — SÌ del proprietario il 1 ott; dal 2 ott lavora AL POSTO del giro del gate delle 14:00 italiane (sì del 1 ott sera)
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

### B8. Le varianti giudicate senza i giorni del paper (seconda metà)
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

### D6. Le leve della spesa AI
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
