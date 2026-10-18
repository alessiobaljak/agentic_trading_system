# Storia del progetto, dal 10 giugno al 18 ottobre 2026

Scritta il 18 ottobre 2026 su richiesta del proprietario: «prima però voglio che tu storicizzi tutti i dati raccolti,
quello che abbiamo imparato, cosa abbiamo cambiato, insomma tutto dall'inizio di questo progetto ad oggi per fare in
modo che quando ripartiamo, ripartiamo con la consapevolezza di cosa abbiamo già fatto e non ha funzionato oppure di
errori da evitare». La decisione che la precede, con le sue parole: «dobbiamo continuare fino a quando non trovi delle
strategie valide... se serve riscriviamo totalmente il gate».

**Questa pagina è il riassunto.** I sette capitoli qui sotto hanno i dettagli, con la fonte di ogni numero (un commit,
un file del repository o una risposta della macchina in `ops/results/`). Dove un numero è una stima o due fonti non
coincidono, il capitolo lo dice. Ogni capitolo è stato scritto da un lettore e ricontrollato da un secondo lettore
contro le fonti (sezione «Come è stata scritta» in fondo).

| Capitolo | Di cosa parla |
|---|---|
| [01 — Origini e sistema](01_origini_e_sistema.md) | giugno-agosto: com'è nato il bot, come è cambiato settimana per settimana, il gate dall'inizio a oggi, i cinque paper azzerati, gli incidenti |
| [02 — Settembre](02_settembre.md) | il paper che riparte il 16 settembre, le prime validate, «la porta del gate è larga», il «cervello», le misure del mese |
| [03 — Ottobre](03_ottobre.md) | le letture ufficiali del 7 e del 16 ottobre, il gate fermato, gli ordini limite, i numeri del paper fino a oggi |
| [04 — Le idee del backlog](04_backlog.md) | tutte le 102 idee di miglioramento mai registrate, con l'esito: provate e non funzionano, provate e rimaste, mai provate; le decisioni del proprietario |
| [05 — Ricerca per moneta e di gruppo](05_ricerca_per_moneta_e_gruppo.md) | 6-12 ottobre: il protocollo per moneta, 21 campagne, 630 varianti, il primo vault; tutte le idee per famiglia |
| [06 — Ricerca, protocolli 2-4](06_ricerca_protocolli_2_4.md) | 13-18 ottobre: ordini limite, paniere a barre giornaliere, BTC51, LINK6; il collaudo del metodo; le idee che tornano |
| [07 — Dati e sistema di oggi](07_dati_e_sistema_oggi.md) | dove sta ogni dato, cosa rischia di andare perso, i branch, la mappa del codice, cosa è acceso e cosa è spento |

---

## 1. In una pagina

**Cosa doveva essere.** Il 10 giugno 2026, in 17 commit, nasce un sistema «agentico e auto-apprendente» per i futures
crypto di Binance: un modello linguistico che sceglie un trade ogni 15 minuti, un motore di apprendimento che regola i
pesi delle strategie, un filtro sulla storia (il **gate**) che decide quali strategie il bot può usare, poi il paper
(soldi finti, `DRY_RUN=true`), poi i soldi veri (capitolo 01, sezione 1).

**Cosa è diventato.** Il modello linguistico non ha mai deciso un trade: dal 30 giugno il bot apre ogni segnale valido
con una regola fissa, per restare uguale al gate (capitolo 01, sezione 4.2). Il gate è diventato un filtro con dieci
criteri, un periodo finale tenuto da parte, tre conferme settimanali e un supervisore che ritocca le soglie; ogni 3 ore
provava circa 27.000 strategie generate a caso (capitolo 01, sezione 3; `ops/gate_fermo`). È fermo dal 13 ottobre. Da
ottobre le strategie si cercano con un **protocollo di ricerca** scritto prima dei numeri, con sessioni separate e un
periodo chiuso (il «vault») aperto una volta sola (capitoli 05 e 06).

**I numeri di oggi** (18 ottobre, 09:03 UTC, `ops/results/0622` e `0623`):

| Cosa | Numero |
|---|---|
| Paper dal 16 settembre (1.000 USDT di partenza) | **707 trade** (668 delle validate più 39 esplorativi), **56% vinti**, **−174,41 USDT**, equity **825,59** |
| In R a trade (629 trade con lo stop noto) | **netto −0,113**, lordo prima dei costi −0,026, costi stimati 0,087 |
| Promessa del gate contro paper | profit factor **2,02 promesso, 0,709 vissuto** (663 trade) |
| Il motore sulle coppie del gate, dopo la scelta | **−0,05 R** su 230 segnali (7 ottobre, `ops` 0532), **−0,03 R** su 566 (16 ottobre, `ops` 0619) |
| Il gate su prezzi rimescolati (dove nessun vantaggio può esistere) | promuove **16 strategie su 7.200**, contro **8 su 7.200** sui prezzi veri (`ops` 0506) |
| Ricerca a protocollo (6-18 ottobre) | circa **730 varianti** (630 + 30 + 40 + 33) in 24 campagne, **4 candidati** arrivati al vault, **0 superati** (capitoli 05 e 06) |
| Il metodo della ricerca, provato con vantaggi inseriti apposta | li trova: **88 su 88** da 0,35 R, 0 falsi su 90 (`research/collaudo_4/esiti.md`) |

**La conclusione, in tre frasi.**
1. **Gli ingressi non sanno la direzione.** Prima dei costi il paper fa circa zero (−0,026 R a trade), e ogni misura
   d'uscita è uguale a quella di un prezzo casuale con le stesse regole d'uscita; il paper perde quasi esattamente i suoi
   costi (capitolo 03, sezione 7; `ops` 0622).
2. **Il gate selezionava fortuna.** Con migliaia di prove a giro e soglie fisse, quello che passava era il massimo del
   rumore: dopo la scelta le coppie fanno circa zero, e sui prezzi rimescolati ne passano il doppio (capitolo 03, sezione
   3; capitolo 04, sezione 2).
3. **Il terreno cercato finora è povero.** Con le regole tecniche classiche, sulle grandi monete, a 15 minuti-4 ore e a
   barre giornaliere, nel 2020-2023, un vantaggio di 0,2 R a trade dopo i costi non c'era; il metodo che lo cerca invece
   funziona, quindi «niente trovato» è un'informazione, non un difetto dello strumento (capitolo 06, sezione 6.8).

---

## 2. La cronologia in breve

| Quando | Cosa | Dettagli |
|---|---|---|
| 10 giu | Primo commit: bot, gate «almeno una strategia in utile», dashboard, VPS | cap. 01, sez. 1 |
| 11-23 giu | Ottimizzazione walk-forward per moneta, costi, funding, strategie generate a caso, gate più severo (PF ≥ 1,25, vinti ≥ 45%, ritorno ≥ 15%) | cap. 01, settimane 1-3 |
| 24 giu | Si scopre che il gate validava anche su **dati sintetici** (Binance bloccato dai server di GitHub): registro «da buttare», gate spostato sulla VPS | cap. 01, sez. 2 e 5 |
| 30 giu | Parità: il bot fa esattamente ciò che il gate ha simulato; il modello linguistico non decide più | cap. 01, sez. 2 |
| 9 lug | «Causa radice»: il gate validava a 1 ora, il bot operava a 15 minuti | cap. 01, sez. 5 |
| 15 lug | Gate e bot a 15 minuti; un controllo trova 15 difetti | cap. 01, sez. 2 |
| 31 lug | **Riforma del gate**: periodo finale di 45 giorni mai usato per scegliere, conferme solo con dati nuovi, almeno 30 trade. Motivo: il fuori campione riusato a ogni giro «era diventato un training set» | cap. 01, sez. 3 |
| 10 ago | Quattro criteri contro le strategie fortunate (caso BIRBUSDT: profit factor 1,51 nel gate, 0,16 nel paper) | cap. 01, sez. 3 |
| 11-14 ago | Paper azzerato dopo 144 trade (da 1.000 a 788,41); upgrade, supervisore, canale ops, una conferma per settimana | cap. 01, sez. 2 e 6 |
| 19 ago | Revisione del backtest: la candela da 1 ora di **bitcoin veniva data a quasi tutte le monete** dal 15 luglio | cap. 01, sez. 5 |
| 31 ago | Il registro, pieno di strategie morte, cancellava a ogni giro le nuove: 137 prime conferme perse | cap. 01, sez. 5; `docs/incidente_31ago.md` |
| 14-16 set | Prime 7 strategie validate; il paper riparte il 16 settembre | cap. 02, sez. 1 |
| 20-30 set | Nasce il backlog; il «cervello» (selettore, figlie, varianti dai referti, freni, idee AI); «la porta del gate è larga» (167 validate su 182 non ripassano) | cap. 02 |
| 1-5 ott | Misure: nessun vantaggio all'ingresso a 1-24 ore; gate rigiocato nel passato e sui prezzi rimescolati; idee AI spente | cap. 03, sez. 3 |
| 6-12 ott | **Ricerca per moneta**: 21 campagne, 630 varianti, 3 candidati, vault aperto l'11 ottobre: 0 su 3 | cap. 05 |
| 7 ott | Prima lettura ufficiale: «la prossima modifica va nel gate» | cap. 03 |
| 11 ott | Report della mattina fermi per ordine del proprietario | cap. 03 |
| 13 ott | Prova degli ordini limite («conviene poco»); **gate fermo**; paper con ingressi a ordine limite | cap. 03 e 06 |
| 13-14 ott | Protocollo 2: paniere di 80 monete a barre giornaliere, nessuna strategia valida | cap. 06 |
| 16-17 ott | Protocollo 3 su BTC (testo del proprietario): collaudo del metodo, un candidato, caduto nel vault | cap. 06 |
| 17-18 ott | Protocollo 4 su LINK con 9 monete di controllo: 33 varianti, nessun candidato | cap. 06 |
| 18 ott | Il proprietario: si continua finché non si trovano strategie valide, prima la storia | `docs/backlog.md`, P11 |

---

## 3. Cosa abbiamo provato e non ha funzionato

«Non ha funzionato» vuol dire: costruito o misurato, e il numero dice che non migliora o non si distingue dal caso. La
tabella completa delle idee del sistema è nel capitolo 04, quella delle idee di ricerca nei capitoli 05 e 06.

### 3.1 Nel bot e nel gate

| Cosa | Il numero | Fonte |
|---|---|---|
| Un modello linguistico che decide i trade | mai usato: non riproducibile, romperebbe il confronto col gate; in ombra non ha cambiato niente | cap. 01, sez. 4.2; cap. 04, sez. 2 |
| Il gate «walk-forward + 3 conferme + periodo finale» con migliaia di strategie generate a caso | dopo la scelta −0,05 R e −0,03 R a trade; sui prezzi rimescolati passa il doppio; una candidata nuova a caso non passa quasi mai (0 su 3.600) | cap. 03, sez. 3; cap. 04, sez. 2 |
| Più conferme, soglie più severe, voto t | il voto t non separa le buone dalle fortunate (−0,21 ±0,24 e −0,09 ±0,21) | cap. 04, sez. 2 |
| Uscite: trailing, scala dei take profit, break-even, take profit dal grafico | il prezzo non arriva al primo gradino (mediana 0,78 R contro 1,5 R); il trailing protegge quanto taglia (100 contro 98); su un prezzo senza direzione nessuna uscita crea un vantaggio | cap. 02, sez. 3.4; cap. 04, sez. 2 |
| Dimensione e freni: freno di serie, per gruppo, stop giornaliero, pesi, leva, inclinazioni per trend e sentimento | segno contrario al voluto o dentro il margine; lo stop giornaliero sul portafoglio del gate peggiora (−11.615, caduta dall'11,7% al 20,3%) | cap. 04, sez. 2 |
| Imparare dal paper: varianti dai referti, figlie «nell'intorno», selettore, idee AI | 0 varianti passate su 13 ipotesi; figlie −0,281 R su 13 trade; selettore 0 finestre su 3; idee AI 4 validate su 117 | cap. 04, sez. 2 |
| Timeframe più lunghi nel gate (da 15 minuti a 1 ora) | più passaggi, nessun vantaggio fuori campione dimostrato | cap. 02, sez. 6.1; cap. 03 |
| Ordini limite in ingresso | costo da 0,062 a 0,039 R a trade, meno dei 0,04 R richiesti; i trade saltati sono i migliori (+0,68 R); «i costi scendono, un vantaggio non nasce» | cap. 06, sez. 1.1 |

### 3.2 Nella ricerca (famiglie di idee)

| Famiglia | Cosa è successo | Fonte |
|---|---|---|
| Tendenza (rotture, medie mobili, MACD, RSI a 50, incroci) | guadagna quanto un ingresso a caso nella stessa direzione: «è l'anno, non la regola»; mai sopra il caso con un vantaggio utile su BTC, LINK e paniere | cap. 05, sez. 3.A e 7.1; cap. 06, sez. 3.1 |
| Ritorno alla media (Bollinger, RSI agli estremi, stocastico) | perde sempre, in tutte le edizioni (18 varianti su 18 sotto 0,03 R nei protocolli 3-4) | cap. 05, sez. 3.B; cap. 06, sez. 3.4 |
| Funding sotto zero e poi acquisto | **tre edizioni, stesso esito**: la famiglia migliore in costruzione su BTC e LINK, caduta nel vault (2024-2026) e sulle altre monete; nei ribassi lunghi il funding resta negativo e il segnale perde | cap. 06, sez. 3.11 |
| Funding alto e poi vendita | perde o fa come il caso | cap. 06, sez. 3.11 |
| Ultima mezz'ora del giorno UTC (la più ripetuta, 6 campagne) | vale meno del costo di un giro; in validazione R negativo a mercato e a limite | cap. 05, sez. 3.D; cap. 06, sez. 3.11 |
| Ritardo delle monete dopo un giorno forte di BTC | due volte vicino alla soglia (gruppo a 1 ora, paniere a 1 giorno), mai oltre | cap. 05, sez. 3.G; cap. 06, sez. 3.3 |
| Short di tendenza con p-value piccolo | p 0,001-0,004 ma R fra +0,01 e +0,08: battono gli short casuali solo perché in un periodo che sale lo short a caso perde | cap. 06, sez. 3.11 |
| Range asiatico, VWAP, volume anomalo, fine settimana, lunedì, numeri tondi | vicino a zero o negativo | cap. 05, sez. 3; cap. 06, sez. 3 |
| Sotto l'ora, qualunque idea | i costi (0,05-0,14 R a giro a 30 minuti) valgono quanto gli effetti | cap. 05, sez. 7.1 |

Un'osservazione del capitolo 06 (sezione 3.11, punto 3): la ricerca su LINK, senza aver visto quella su BTC, ha riscritto
quasi le stesse varianti. **Con lo stesso catalogo, lo stesso modello e la stessa letteratura, cambiare moneta non vuol
dire cambiare idee.**

---

## 4. Cosa ha funzionato, o resta valido

Nessuna di queste cose ha reso il paper profittevole: hanno funzionato nel senso che hanno dato una risposta chiara o
tolto un difetto.

* **Il metodo della ricerca**: entrate casuali con le stesse uscite e la stessa larghezza di stop come termine di
  paragone, periodo chiuso aperto una volta sola, collaudo con vantaggi inseriti apposta (88 su 88), prova a placebo
  (0,41% di falsi positivi). Ha fermato tutti i candidati deboli prima del paper (capitoli 05 e 06).
* **Le regole di lettura scritte prima dei numeri**: hanno dato verdetti netti il 7 e il 16 ottobre e hanno evitato di
  leggere un giorno buono come una svolta (capitolo 04, sezione 3).
* **Il bot esegue quasi come il motore**: ingressi allineati all'81%, stessi segnali +0,05 R contro +0,01 R a fine
  settembre; il 16 ottobre una piccola perdita d'esecuzione propria (−0,06 R), appena fuori dal margine (capitolo 02,
  sezione 3.3; capitolo 03, sezione 3.13).
* **Il canale ops** (comandi chiesti via git ed eseguiti sulla macchina da una lista bianca) e il battito orario: 620
  risposte dal 14 agosto, 622 con quelle del 18 ottobre (capitolo 07, sezione 1.8).
* **Le sessioni di ricerca che si fermano e chiedono**: due difetti degli strumenti trovati dalla ricerca su BTC prima di
  qualunque variante; la sessione su LINK che non si fida di un messaggio automatico «a nome del proprietario»
  (capitolo 06, sezione 6.8).

---

## 5. Errori da non ripetere

Raccolti dai sette capitoli; ognuno ha la sua storia e i suoi numeri nel capitolo indicato.

**Dati**
1. **Mai un ripiego silenzioso su dati finti o sbagliati.** I dati sintetici hanno prodotto un registro intero di
   validate false (24 giugno); la candela da 1 ora di bitcoin data a tutte le monete ha falsato un mese di regimi (19
   agosto) (cap. 01, sez. 7.2).
2. **I dati hanno buchi e trappole**: il mark price manca per giorni interi, il primo mese di una moneta non è pieno, il
   volume è in moneta base, lo slippage stimato sul 2023 è ottimista per il 2020-2021, i contratti tolti dal listino hanno
   candele finte (cap. 05, sez. 6; cap. 06, sez. 5).

**Statistica**
3. **Il fuori campione si usa una volta**, e il paper non è un insieme di addestramento: finestre uguali a ogni giro hanno
   trasformato il fuori campione in addestramento (31 luglio); le funzioni che imparavano dal paper non hanno mai mostrato
   un contributo (cap. 01, sez. 7.2; cap. 04, sez. 6.1).
4. **Contare i tentativi.** Con 27.000 prove a giro e soglie fisse ci si aspettano circa 614 passaggi per puro caso; un
   passaggio su molte valutazioni non è una conferma (cap. 02, sez. 6.2; cap. 04, sez. 6.6).
5. **Confrontare con il caso, e con il caso giusto**: con entrate casuali che hanno uno stop diverso una regola senza
   direzione sembra buona; in un periodo che sale lo short a caso perde, quindi i p-value degli short sono piccoli per
   costruzione. La difesa che ha funzionato ogni volta è la soglia sull'R dopo i costi (cap. 05, sez. 7.5; cap. 06, sez.
   6.8).
6. **Non decidere su campioni piccoli**: «contribuisce» su 10 trade, «le short perdono sempre» su 7, il candidato con 3
   trade che facevano tutto l'R: tutti girati con più dati (cap. 03, sez. 7; cap. 04, sez. 6.2; cap. 05, sez. 7.5).
7. **Calcolare il costo di un giro in R prima di scegliere il timeframe**: sotto l'ora nessuna idea ha retto (cap. 05,
   sez. 7.5).

**Costruzione del software**
8. **Un limite tecnico non deve poter cancellare l'evidenza**: il tetto del registro, la scadenza delle generate, il taglio
   della rivalutazione hanno buttato via proprio ciò che il sistema produceva (cap. 01, sez. 7.2).
9. **Una sola copia di ogni regola, con un solo orologio**: tre copie della contabilità delle conferme, due orologi
   incompatibili (un giro ogni 3 ore contro una conferma a settimana), la sessione oraria letta dall'orologio del
   computer (cap. 01, sez. 7.2; cap. 02, sez. 6.2).
10. **Una protezione scritta ma non collegata è peggio di nessuna**: il controllo delle correlazioni non era mai stato
    collegato, l'agente macro restituiva sempre una lista vuota, il freno globale era solo un'etichetta (cap. 01, sez. 5).
11. **I test verdi non bastano, e i test rossi si sistemano subito**: test che leggevano la produzione, suite rossa solo
    sulla macchina, test rossi per giorni che nascondevano un difetto vero (cap. 01, sez. 7.2; cap. 03, sez. 6).
12. **Prima di azzerare, esportare**: il reset dell'11 agosto ha reso non rigiocabili 30 coppie su 31 (cap. 01, sez. 7.2).
13. **Un interruttore va seguito in tutto ciò che ne dipende**: col gate fermo si sono fermati anche il report giornaliero
    e il backlog in dashboard, e dopo 3 giorni i report vedono zero coppie validate (cap. 03, sez. 6, punti 24-25).

**Processo**
14. **Non cambiare le regole mentre si misura**: il gate è stato riformato o il registro azzerato almeno sette volte fra
    giugno e agosto, e il paper è ripartito da zero cinque volte; in tre mesi nessun campione del paper ha superato i 144
    trade (cap. 01, sez. 6.1 e 7.2).
15. **Scrivere la regola di lettura prima dei numeri, e poi rispettarla** (cap. 02, sez. 6.2; cap. 04, sez. 3).
16. **Una misura promessa va messa in calendario con lo strumento che la legge**: la misura degli ordini limite nel paper
    non è mai stata letta; quattro letture andate in tempo scaduto il 12 ottobre non sono mai state rifatte (cap. 03,
    sez. 7).
17. **Più tentativi non hanno mai aiutato**: i tentativi in più chiesti su BTC e su LINK hanno dato solo falsi o p-value
    piccoli con R vicino a zero (cap. 06, sez. 6.8).
18. **Troppe cose nuove in pochi giorni generano difetti nuovi**: a settembre più di 55.000 righe di codice; nessuna delle
    funzioni aggiunte ha un contributo misurato (cap. 02, sez. 6.2).
19. **Le istruzioni del proprietario si leggono nel senso, non alla lettera** (11 ottobre, il referto partito lo stesso)
    (cap. 03, sez. 6).

---

## 6. Cosa è acceso e cosa è spento oggi

Dettagli e fonti nel capitolo 03, sezione 2.3, e nel capitolo 07, sezione 3.4.

* **Acceso**: il bot in paper con `DRY_RUN=true`, sulle 249 coppie validate dal vecchio gate (ferme al 13 ottobre), con
  ingressi a ordine limite e il freno globale (size a metà); il supervisore orario; il canale ops e il battito.
* **Spento**: la ricerca automatica del gate (`ops/gate_fermo`, dal 13 ottobre); le idee AI, l'ombra AI e il filtro delle
  monete AI; le varianti dai referti; il freno di serie; i report della mattina (fino a nuovo ordine del proprietario).
* **Fermo senza che nessuno l'abbia deciso**: il report giornaliero e il backlog in dashboard, che si pubblicavano alla
  fine di un giro del gate (dedotto dal codice, capitolo 03, sezione 6, punto 24).

---

## 7. Dove sono i dati, e cosa rischia di andare perso

Inventario completo nel capitolo 07. In breve:

| Dati | Dove | Rischio |
|---|---|---|
| Diario, documenti, protocolli, risultati delle ricerche, risposte della macchina, fotografie dello stato ogni 2 ore | repository (branch principale) | basso |
| Trade del paper (707) e stato del conto | solo Firebase; `scripts/reset_paper.py` li cancella senza copia | **alto** |
| Registro del gate (2.435 coppie) e specifiche delle strategie generate | solo Firebase | **alto**: senza le specifiche le coppie non si possono più rigiocare |
| Misure che vivono solo sulla macchina (`data/gate_storia`, `data/selettore`, `data/voto_t`, backup dei reset) | solo VPS | **alto** |
| Elenchi dei trade e dell'avanzamento delle varianti del paniere (circa 133 MiB) e risultati delle varianti di LINK6 (1,2 MiB) | solo sui branch `research/campagna/PANIERE` e `.../LINK6` (quelli del gruppo, 114 MiB, sono nella storia del branch principale) | medio |
| Candele usate dalla ricerca (470 MB) | fuori dal repository; si riscaricano da Binance e si verificano con le impronte che sono nel repository | basso |

**Cosa è stato fatto il 18 ottobre per non perdere niente:**
* copiati sul branch principale i testi delle campagne che stavano solo sui loro branch: BTC51 (log, ipotesi,
  validazione, consegna, risultati delle 40 varianti), paniere (log, ipotesi, consegna, lezioni, codice), LINK6;
* questa storia.

Non è stato possibile mettere un'etichetta git sulle punte dei branch di ricerca: il proxy git della sessione rifiuta
il push delle etichette (errore 403). Gli elenchi dei trade e dell'avanzamento delle varianti del paniere (circa 133 MiB)
restano quindi solo sul suo branch; quelli del gruppo sono già nella storia del branch principale.

**Cosa resta da fare (serve una riga del proprietario sulla macchina):** l'esportazione dei dati che stanno solo in
Firebase e sulla VPS. Lo script è pronto nel repository (`scripts/esporta_storia.py`, capitolo 07, sezione 5); per
lanciarlo dal canale ops serve aggiungere la voce `esporta-storia` alla lista bianca della macchina, che per sicurezza
vive solo lì (`ops/README.md`).

---

## 8. Cose trovate scrivendo la storia

Nessun documento le scriveva; sono nel backlog (`docs/backlog.md`, voce P12) con la loro fonte.

1. **Un test della ricerca era rosso su GitHub dal 17 ottobre sera** (la cartella della campagna LINK6 contata fra le
   monete della prima edizione): corretto il 18 ottobre (commit `573d084d`), la suite della ricerca passa (3.151 test).
2. **Dopo 3 giorni di gate fermo i report vedono zero coppie validate**, mentre il bot continua a operarne 249: la
   funzione `coppie_validate` tiene solo le coppie viste dal gate negli ultimi 3 giorni (`bot/core/registry.py`). Una
   lettura del fuori campione fatta oggi uscirebbe vuota o falsata (capitolo 03, sezione 6, punto 25).
3. **La misura degli ordini limite nel paper non è mai stata letta**: tasso di esecuzione, costo, R dei segnali saltati
   (capitolo 03, sezione 3.14).
4. **Il supervisore conta 278 coppie validate, lo stato e il bot 249** (`ops` 0623): la differenza non è spiegata.
5. **Il testo di `ops/gate_fermo` è superato e in un punto impreciso**: rimanda alla seconda edizione, già chiusa, e il suo
   «−0,06 R a trade in paper» è il risultato del motore dopo la validazione (`ops` 0600), non del paper (capitolo 03,
   sezione 2.1). Non cambia il funzionamento.
6. **Alcuni stati del backlog sono vecchi** (voci date «in lavorazione» o «aspettano il sì» già fatte o già messe nel
   protocollo 4) (capitolo 04, sezione 6.10).
7. **`docs/firebase_schema.md` elenca una piccola parte di ciò che il bot scrive in Firebase** (capitolo 07, sezione 5).

---

## 9. Cosa dice la storia a chi riparte

Non è un piano: è ciò che i numeri di questi quattro mesi chiedono a qualunque versione nuova del gate o della ricerca.

1. **Il problema è l'informazione all'ingresso, non le uscite, la size o l'esecuzione**: lordo circa zero, costi circa
   0,09 R a trade. Cambiare uscite e freni non ha mai creato un vantaggio (sezione 3.1).
2. **Ogni candidata va confrontata con entrate casuali con le stesse uscite**, con una correzione per il numero di prove e
   un fuori campione usato una volta sola: sono le tre cose che il protocollo fa e il gate di produzione non ha mai avuto
   (capitolo 04, sezione 4, «Proposte strutturali per il gate»).
3. **Lo stesso terreno ridà lo stesso esito**: regole tecniche classiche, grandi monete, 15 minuti-4 ore, 2020-2023.
   Riscrivere l'esame senza cambiare le idee rischia di ridare zero (capitolo 06, sezione 6.8).
4. **Le idee già bruciate vanno dette alla ricerca come tali** (per esempio il funding sotto zero, tre volte), senza
   passarle i risultati del vault: è la regola che il protocollo 4 ha cominciato a seguire (capitolo 06, sezione 6.8).
5. **Il bot deve saper eseguire ciò che la ricerca trova**: oggi non sa eseguire nessuna variante del catalogo dei
   protocolli 3 e 4 (capitolo 04, voce P7; capitolo 06, sezione 6.8).
6. **Prima di riscrivere il gate, salvare il registro di oggi**: è la fotografia definitiva del vecchio gate (sezione 7).

---

## Come è stata scritta

Il 18 ottobre 2026 sette lettori hanno letto in parallelo, ognuno su un pezzo: i 3.956 commit dal 10 giugno, il diario
(`docs/andremo_live.md`), il backlog e le sue 143 versioni passate, le 620 risposte della macchina, i protocolli, le
campagne di ricerca e i loro branch. Ogni capitolo è stato poi ricontrollato da un secondo lettore, che ha aperto le fonti
di almeno 30 affermazioni a capitolo e corretto gli errori trovati. Questa pagina l'ha scritta il coordinamento dai sette
capitoli; i numeri del paper di oggi vengono da due richieste fatte alla macchina il 18 ottobre (`ops/results/0622` e
`0623`). Le cose incerte sono scritte in fondo a ogni capitolo.
