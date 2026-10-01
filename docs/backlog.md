# Backlog — solo le cose DA FARE o IN ATTESA

**Aggiornato il 1 ottobre 2026, 13:00 ora italiana.** Su richiesta del proprietario qui restano
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
| **1. In lavorazione** | R1 (il gate rigiocato nel passato: sì del 1 ott) | lo strumento, poi 2 righe nella lista bianca della VPS |
| **2. Dopo le letture del 7-14 ott** | K9, K10, G6, B8, E4, I5, D6 | il numero delle letture, poi il tuo sì |
| **3. A metà novembre** | G3 (voto t minimo nel gate) | la lettura H1 |
| **4. Prima dei soldi veri** | C4, K8, K5, K6, K4 | la decisione di passare a soldi veri |
| **5. Solo se serve** | D1 | lo spazio del registro che finisce |
| **6. Parcheggiate da te** | H3, H4, B5, B6, B7, J2 | che tu le riprenda |

---

## 1. In lavorazione

### R1. Rigiocare il gate nel passato — **SÌ del proprietario il 1 ott, in lavorazione** (regola nel diario del 1 ott, scritta prima dei numeri)
Invece di aspettare il 7-14 ott per sapere se il gate sceglie strategie con un vantaggio vero, si
rifà il gate a 26 date passate e si guarda come sono andate dopo le promosse contro le bocciate.
Regola da scrivere prima dei numeri: promosse meglio delle bocciate oltre il margine → il gate ha un
vantaggio; differenza + margine sotto 0,10R → il gate sceglie la fortuna; altrimenti non si sa.
**Serve:** il tuo sì (prima una prova piccola, poi completa) e 2 righe nuove nella lista bianca
della VPS da aggiungere a mano. **Attenzione tecnica:** non deve scrivere nel registro vero né
cancellare la cache del gate (si caricano i dati fino a oggi e si tagliano in memoria).

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
* **H3. Stop giornaliero:** il bot si fermerebbe dopo una perdita del giorno (es. 3%). Nella
  simulazione sulle 160 strategie (ops 0232) andava peggio (−21%: dopo il blocco si perde il rimbalzo).
  Tu: «non voglio limitare la quantità, voglio trade migliori».
* **Rigioco del 1 ott (ops 0404 paper, 0405 gate), richiesto dal proprietario:** sul paper stop e freni
  migliorano di poco (il migliore, freno di serie dopo 3 perdite del bot: +15,62 su −81,11), sul portafoglio
  del gate peggiorano tutti (stop 3%: −11.615 e drawdown da 11,7% a 20,3%; freno 3 perdite del conto:
  −3.957). Sul paper aiutano solo perché tolgono esposizione a un sistema che perde: confermato parcheggio.
* **H4. Freno di serie:** meno size dopo 4 perdite di fila. Misurato (ops 0232): win rate 56% dopo 4
  perdite contro 63%, su 16 casi: nessuna prova che serva.
* **B5, B6, B7. Dati esterni:** notizie e dati macro, storico di open interest e long/short,
  registrazione nostra dello storico.
* **J2.** «Cosa aspetta il sì» in dashboard: oggi vive qui.
