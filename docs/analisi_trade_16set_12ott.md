# I trade del paper dal 16 settembre al 12 ottobre: perché falliscono, e a cosa servono questi dati

Chiesta dal proprietario il 12 ottobre 2026. Fonti: 17 letture di sola lettura eseguite sulla macchina il 12 ottobre
fra le 16:52 e le 19:07 UTC (ops 0596-0612); quattro sono andate in timeout a 900 s e non hanno dato numeri
(`edge`, `confidenza`, `costi`, `timeframe`: ops 0602, 0603, 0610, 0606). Tutti i numeri qui sotto hanno accanto la
lettura da cui vengono. Il periodo è di 27 giorni, un solo mercato; i trade sono 508 chiusi (481 con apertura nota,
442 con R calcolabile) su 91 monete e 159 strategie: in media 3 trade per strategia.

Vincolo che vale per tutto il documento (`CLAUDE.md`): **il paper non si usa mai come insieme di addestramento.** I
trade del paper dicono come si perde e suggeriscono ipotesi; un'ipotesi si prova sulla storia, nel gate o nel
protocollo, mai tarandola sui trade stessi.

## 0. La risposta in breve

1. **I trade falliscono perché gli ingressi non portano informazione sulla direzione, e i costi fanno il resto.**
   Prima dei costi il trade medio rende −0,015 R (dal 27 settembre +0,003 R); i costi valgono 0,095 R a trade; dopo i
   costi −0,110 R (ops 0596). In denaro: perdita lorda 58,62 USDT, costi 67,59, perdita netta 126,21 (ops 0607). Con un
   guadagno lordo zero, ogni trade perde esattamente il suo costo.
2. **Ogni misura d'uscita del paper coincide con quella di un prezzo casuale con le nostre stesse regole d'uscita**
   (stop 44% contro 46%, massimo toccato mediano 0,80 R contro 0,81, vinti 55% contro 54%, al primo target 12% contro
   17%; ops 0596). Il paper si distingue dal caso in una cosa sola: perde un po' di più (−0,110 R contro −0,067).
3. **Non è l'esecuzione.** Sugli stessi segnali il motore storico fa −0,07 R e il bot −0,10 R, differenza +0,03 R con
   margine ±0,05 (ops 0600); 102 ingressi su 133 abbinati alla candela del motore con scarto 0 minuti, e 19 dei 31 non
   abbinati sono trade di prima della correzione del 27 settembre (ops 0608).
4. **È la scelta del gate.** Dopo la validazione il motore stesso, sulle coppie che il gate ha scelto, fa −0,06 R su
   396 segnali con margine ±0,10 (ops 0600): la promessa (profit factor 2,03) non regge sui dati successivi (0,70
   vissuto, ops 0612). Il «voto di affidabilità» del gate non separa le coppie buone dalle cattive (le più affidabili
   fanno −0,23 R, le altre −0,02; ops 0600) e un selettore addestrato su 150.000 trade del gate non batte «apri tutto»
   in 0 finestre su 3 per ogni famiglia (ops 0604).
5. **Questi dati non servono a creare strategie, e non possono migliorare il gate ritoccandone i parametri.** Servono a
   tre cose: dire dove NON cercare (uscite, trailing, size, «imparare dai referti»), confermare che il collo di
   bottiglia è l'informazione all'ingresso più i costi, e suggerire tre ipotesi da provare sulla storia con un
   controllo del caso (sezione 4). Il miglioramento del gate che i dati chiedono è strutturale: un confronto con
   entrate casuali per ogni candidata e una correzione per i 27.000 tentativi a giro. È esattamente quello che il
   protocollo di ricerca ha fatto, e il suo risultato è zero su 630.

## 1. Cosa è successo in 27 giorni

| Numero | Valore | Fonte |
|---|---|---|
| Trade chiusi | 508 (56% vinti) | ops 0607 |
| Risultato netto | −126,21 USDT (−12,6%); BTC nello stesso periodo +8,9% | ops 0607 |
| Costi stimati | 67,59 USDT: commissioni 37,36, scarto di prezzo 30,06, funding +0,17 | ops 0607 |
| Risultato lordo | −58,62 USDT | ops 0607 |
| Trade al giorno | media 17,8; 40 e 39 il 7 e 8 ottobre | ops 0596 |
| Durata media | 3,9 ore (minimo 0, massimo 24) | ops 0596 |
| Posizioni insieme | massimo 14-15, media 3,0 | ops 0596, 0607 |
| Come escono | trailing 222 (+171,45), stop 221 (−438,77), incasso parziale 48 (+87,25), tempo 13 (+25,12), target pieno 4 (+28,73) | ops 0607 |
| Gradini di incasso | 0 gradini nell'88% dei trade; primo gradino nel 9% | ops 0607 |
| Massimo toccato a favore | mediana 0,81 R; almeno 1 R nel 38%; almeno 1,5 R (primo gradino tipico) nel 15% | ops 0597 |
| Giornate | 22 in utile su 27 nel portafoglio simulato sugli stessi giorni (+127.728 su 10.000 per coppia), 8 in utile su 27 nel paper | ops 0600 |

## 2. Perché i trade falliscono, in ordine di peso

### 2.1 Gli ingressi non sanno la direzione (il peso maggiore)

* **Lordo a zero.** R medio prima dei costi −0,015 su 442 trade; dal 27 settembre, dopo la correzione della sessione
  oraria, +0,003 su 346 (ops 0596). Un trade che in media non guadagna nulla prima dei costi non ha informazione
  sulla direzione.
* **La curva del vantaggio del segnale è piatta.** Per ogni trade, la mossa del prezzo dopo 1, 4, 12 e 24 ore
  dall'ingresso, confrontata con 20 ingressi a caso sulla stessa moneta nello stesso giorno e nella stessa direzione:
  vantaggio +0,008, +0,066, +0,119, +0,028 mosse tipiche, tutti dentro il margine al 95% (ops 0597, 448 trade su 25
  giornate). Esito scritto: «nessun vantaggio misurabile». Le stime puntuali a 4 e 12 ore sono positive ma piccole:
  un indizio debole, non un fatto (sezione 4).
* **Il paper ha la firma del caso.** Confronto con un prezzo casuale giudicato con le nostre stesse uscite (ops 0596):
  stop 44% contro 46%; stop «d'ingresso» e «d'uscita» 46/54% contro 48,5/51,5%; massimo toccato 0,80 R contro 0,81;
  primo target 12% contro 17%; vinti 55% contro 54%. Nessuna di queste misure dice qualcosa sulle strategie: dice la
  forma delle regole d'uscita.
* **Il motore storico, sulle stesse coppie e dopo la data di validazione, fa lo stesso:** −0,06 R su 396 segnali,
  margine ±0,10 per giornata (ops 0600). Non è un problema del bot che esegue: è che le coppie scelte non hanno un
  vantaggio nei giorni dopo la scelta.

### 2.2 I costi trasformano lo zero in una perdita certa

* 0,095 R a trade di costi stimati (ops 0596), 67,59 USDT su 508 trade, 0,13 USDT a trade, di cui lo scarto di prezzo
  è il 44% (30,06; ops 0607). Il «pareggio» richiesto è il 7,7% del capitale (ops 0607).
* Con 17,8 trade al giorno e zero informazione, la perdita attesa è il costo: 17,8 × 0,13 = 2,3 USDT al giorno, cioè
  circa 63 USDT in 27 giorni; la perdita netta è 126 perché il lordo è stato anche un po' negativo (−58,62).
* I costi sono stimati dal modello del gate, non misurati sui riempimenti (ops 0607): il valore vero in mercato può
  essere diverso, e la lettura `costi` che li ricontrolla è andata in timeout (ops 0610).

### 2.3 La scala degli incassi non è raggiungibile, ma non è la causa

* Primo gradino tipico a 1,5 R; massimo toccato mediano 0,81 R; solo il 15% dei trade arriva a 1,5 R e l'11% incassa
  il primo gradino (ops 0597, 0607). Il livello «strutturale» (massimi e minimi recenti) sta in mediana a 3,29 R e
  viene raggiunto nell'8% dei trade: ancora più lontano.
* Dei 221 stop, 101 sono «mai andati a favore» (massimo sotto 0,25 R) e 119 «a favore ma sotto il primo gradino»
  (ops 0597): la metà dei trade persi era andata nel verso giusto senza arrivare a incassare.
* **Perché non è la causa:** il prezzo casuale con le stesse uscite dà la stessa quota di stop «d'ingresso» e
  «d'uscita» e lo stesso massimo toccato (2.1). Una scala più stretta (0,8/1,6/2,4) migliora l'R del modello
  semplificato da −0,749 a −0,265 (ops 0597), ma quel modello conta i gradini raggiunti come incassati; su un prezzo
  senza informazione qualunque scala vale zero prima dei costi, e cambia solo quanto oscilla il risultato. Le uscite
  si possono rendere più coerenti; non possono creare un vantaggio che all'ingresso non c'è.

### 2.4 La direzione: i long perdono il doppio degli short, e i long contro Bitcoin di più

* Long −0,161 R su 242, short −0,048 R su 200; dal 27 settembre −0,141 contro −0,026 (ops 0596).
* Con il verso di Bitcoin: long nel verso di BTC −0,126, long contro BTC −0,152, short nel verso −0,103, short contro
  BTC +0,030 (dal 27 settembre; ops 0596). Trade aperti con il regime «rialzo» −0,247 R su 64; con «ribasso» −0,011 su
  118 (ops 0596).
* Lettura onesta: 27 giorni di un mercato in cui BTC ha fatto +8,9% ma le altre monete no; il protocollo ha provato
  sul 2020-2023 le famiglie «con il trend» e «contro il trend» su 20 monete e sul gruppo di 80 e non ha trovato
  niente che batta entrate a caso nella stessa direzione (`research/confronto/risultati.md`). È un effetto di
  periodo, non una regola. Il gate giudica il regime della moneta e il bot dal vivo quello di Bitcoin per tutte: nei
  giorni di grandi movimenti i due discordano nel 22-37% dei casi su ETH e SOL (ops 0609).

### 2.5 Le funzioni che «imparano» dal paper non aiutano, e qualcuna va nel verso sbagliato

Tutte dentro il margine, quindi «non si vede ancora», ma il segno è sempre lo stesso (ops 0596):
* pesi alti (più size e leva a chi ha vinto di recente): toccati −0,177 R contro +0,099 R degli altri;
* leva sopra 1x: −0,156 contro −0,093;
* inclinazione per trend e sentimento: −0,175 contro −0,061;
* affollamento: trade aperti con 1-2 posizioni nello stesso verso −0,083 R, con 3-5 −0,126, con 6 o più −0,162
  (ops 0596). Le ondate (10-12 aperture nello stesso verso entro 5 minuti) sono il momento in cui il bot scommette
  tutto insieme sulla stessa cosa.
* Il trailing: 100 uscite premature contro 98 protette su 198 verdetti (ops 0612): esattamente a metà, come ci si
  aspetta da un prezzo che non ha direzione. Con keep 0,75 (12 coppie) 7 premature e 0 protette, R −0,35 su 21 trade:
  pochi, ma tutti nello stesso verso.
* Le ipotesi nate dai referti (13 in questa lettura, ops 0596) hanno campioni di 3-6 trade. La revisione del 30
  settembre aveva misurato che su 143 referti anche il puro rumore produce un «filo comune» da +0,21 R apparenti
  (`docs/revisione_sospese_30set.md`): sono da considerare rumore finché il gate non le prova sulla storia, e il gate
  le ha provate (3 nate, 1 variante, 0 passate; ops 0586 dell'11 ott).

### 2.6 Il gate sceglie sul rumore

* Nell'ultimo giro: 26.986 valutazioni, 78 passate (0,29%); l'81% delle bocciate cade su «rendimento totale troppo
  piccolo» (ops 0601). Con 27.000 prove per giro, a una soglia di t = 2 ci si aspettano circa 614 candidate per puro
  caso; per lasciarne passare al massimo una servirebbe t = 3,96, e nessuna candidata lo raggiunge (ops 0601).
* I «quasi-passaggi» sono i semi da cui il giro dopo fa nascere le varianti «nell'intorno»: nel paper le strategie
  nate così rendono −0,281 R su 13 trade, contro −0,103 di quelle casuali (ops 0596).
* Il voto di affidabilità non separa: coppie con t dell'ultimo esame ≥ 1,5 fanno −0,23 R, le altre −0,02 (ops 0600;
  lettura H1 chiusa). Le declassate (bocciate due giri di fila) fanno −0,078 R, le attive −0,125: le bocciate
  rendono quanto le promosse (ops 0596).
* Il selettore addestrato su 150.015 trade del gate con 18 variabili non batte «apri tutto» in nessuna delle 3
  finestre, per nessuna famiglia; i coefficienti sono tutti vicini a zero (ops 0604). La «confidenza» del regime non
  predice: vinti 54%, 60%, 50% nei tre terzi (ops 0596).
* Il 5 ottobre, sui prezzi mescolati a caso, il gate aveva fatto passare il doppio delle strategie che sui prezzi
  veri (16 contro 8 su 7.200; ops 0506).

## 3. Cosa NON è la causa (e dove non vale la pena lavorare)

| Sospetto | Misura | Verdetto |
|---|---|---|
| Il bot entra dove il gate non entrerebbe | 102 su 133 ingressi abbinati a 0 minuti; 19 dei 31 non abbinati sono di prima del 27 set (ops 0608) | no |
| Il bot esegue peggio del motore | stessi segnali: −0,10 R contro −0,07, differenza +0,03 ±0,05 (ops 0600) | no, dentro il margine |
| Il bot rifiuta segnali buoni | i rifiutati per «posizione aperta» fanno −0,10 R come gli aperti; quelli per «cooldown» +0,15 su 74 ma a prezzo puro senza costi, che vale 0,1-0,2 R (ops 0599) | no |
| Il bot sopprime segnali | 36,6 segnali apribili al giorno contro 17,8 trade (22-40 negli ultimi giorni) (ops 0605, 0596) | no |
| Le uscite sono sbagliate | stesse quote di un prezzo casuale (ops 0596) | non è la causa |
| Il trailing chiude troppo presto | 100 premature contro 98 protette (ops 0612) | no |
| La size e la leva | tutte le funzioni dentro il margine, segno negativo (ops 0596) | non aiutano |
| Le monete morte falsano il gate | 28 delistate su 897 nella finestra, 3,1% (ops 0611) | marginale |
| Serie di perdite anomale | 8 di fila al massimo; nel gate 3 finestre su 2.069 (ops 0598) | normale |

## 4. Questi dati possono creare strategie o migliorare il gate?

**Come insieme di addestramento: no**, per regola e per aritmetica. 442 trade con R su 159 strategie e 91 monete sono
3 trade per strategia; qualunque regola «imparata» qui è rumore, e il paper stesso lo ha dimostrato: il selettore con
150.000 trade del gate non predice niente (ops 0604), figurarsi 442.

**Come diagnosi: sì, ed è già conclusiva.** Dice che il collo di bottiglia è l'informazione all'ingresso più i
costi, e che uscite, trailing, size e «imparare dai referti» non sono leve. Da oggi queste cose si possono smettere
di misurare ogni giorno: il verdetto non cambierà con altri 500 trade.

**Come fonte di ipotesi: tre, da provare sulla storia con un confronto con entrate casuali (mai sul paper).**

1. **Costo per trade.** Lo scarto di prezzo è il 44% dei costi (ops 0607). Ipotesi: con ordini limite a mercato
   fermo, commissione maker e scarto quasi zero, il costo a trade scende da 0,095 R a circa 0,04-0,05 R (stima dalle
   commissioni Binance: maker 0,02% contro taker 0,05% per lato; lo scarto va misurato). Cosa cambierebbe: con lordo
   zero il paper perderebbe la metà, non guadagnerebbe. Serve una regola scritta prima su quando un ordine limite
   viene eseguito (freqtrade: eseguito se il prezzo lo attraversa, con tempo massimo; `docs/letture_esterne/`) e la
   misura sulla storia 2020-2023 del protocollo. Metro: costo di un giro misurato per moneta e per anno.
2. **Esposizione nello stesso verso.** I trade aperti quando 6 o più posizioni spingono nello stesso verso rendono
   −0,162 R contro −0,083 (ops 0596), e la campagna di gruppo ha misurato che 80 monete si muovono insieme (effetto
   grappolo 12: `research/confronto/risultati.md`). Ipotesi: un tetto di esposizione per verso (in R aperti) riduce
   le giornate da −15 USDT. Non crea vantaggio: riduce quanto oscilla il risultato. Si prova nel portafoglio
   rigiocato (ops 0600, sezione «stop giornaliero e freno di serie»), con regola scritta prima.
3. **Orizzonte di 4-12 ore.** La curva del vantaggio ha stime positive a 4 e 12 ore (+0,066 e +0,119 mosse tipiche,
   margini [−0,031, +0,164] e [−0,022, +0,240]; ops 0597) mentre i trade durano in media 3,9 ore e il 44% esce allo
   stop. È dentro il margine, quindi può essere nulla. Se si vuole provarla: sul 2020-2023, con il protocollo,
   «stessi ingressi, uscita a tempo di 8-12 ore con stop largo» contro entrate casuali; il costo per trade non
   cambia ma si pagano meno trade per unità di tempo. Attenzione: le famiglie «a tempo» del protocollo a 4h-1d non
   hanno battuto il caso (`research/confronto/risultati.md`, sezione 3.3).

**Per il gate: i dati chiedono cambiamenti strutturali, non tarature.**

| Cosa | Perché (dato) | Cosa farebbe |
|---|---|---|
| Confronto con entrate casuali, stesse uscite, per ogni candidata | il paper e il motore fanno come il caso (2.1); il gate giudica con soglie assolute (rendimento, profit factor, recupero) che un prezzo in salita supera da solo | la candidata passa solo se batte nettamente il caso: il protocollo lo fa già, e con questo controllo passa lo 0,41% delle strategie finte (`research/taratura/placebo/risultati.md`) |
| Correzione per i tentativi | 27.000 prove a giro: a t = 2 ne passano ~614 per caso (ops 0601) | soglia di t legata al numero di prove, o Benjamini-Hochberg per giro |
| Fuori campione vero | i tre «passaggi» sono finestre che si sovrappongono sullo stesso registro di 2.300 candidate riprovate ogni giro; dopo la validazione il motore fa −0,06 R (ops 0600) | una finestra mai vista, usata una volta sola per candidata, come il vault |
| Costi misurati per moneta | lo scarto è il 44% dei costi e dipende dalla moneta: le più costose DEXE, SYRUP, ZORA, UB, GPS (ops 0607) | bocciare le candidate il cui vantaggio lordo è sotto due giri di costi della loro moneta |
| Un solo regime | gate sulla moneta, bot su Bitcoin: discordano nel 22-37% degli spike (ops 0609) | stessa definizione di regime nel gate e dal vivo |
| Niente figlie dai quasi-passaggi | le strategie «nell'intorno» fanno −0,281 R (ops 0596); i quasi-passaggi sono rumore a t 1-2 (ops 0601) | spegnere la generazione nell'intorno |

Onestà sul punto: le prime tre righe sono il protocollo di ricerca, che è stato costruito proprio per questo e ha
dato zero su 630. Un gate così corretto direbbe «no» quasi sempre: è il risultato giusto, non un fallimento del gate.

## 5. Limiti di questa analisi

* Quattro letture in timeout (900 s): la stabilità del vantaggio nel tempo per coppia, l'analisi della confidenza
  per variabile, il ricontrollo dei costi, la prova ad altri timeframe (ops 0602, 0603, 0610, 0606). Si possono
  rilanciare una per volta, se servono.
* Numeri aggregati, non trade per trade: il canale ops non esporta l'elenco dei trade; per un'analisi riga per riga
  servirebbe una voce di sola lettura nuova nella lista bianca della macchina, che può aggiungere solo il
  proprietario.
* 27 giorni, un mercato, 3 trade per strategia: ogni spaccatura per strategia, regime o direzione è un'osservazione,
  non una regola.
* I costi sono stimati dal modello del gate, non misurati sui riempimenti (ops 0607).
* Il confronto trade per trade col motore ha coperto 18 coppie su 229 per il tempo massimo (ops 0608).

## 6. Fonti

ops 0596 (`trades`), 0597 (`mfe`), 0598 (`confronto`), 0599 (`rifiutati`), 0600 (`portafoglio`), 0601 (`autopsy`),
0604 (`selettore`), 0605 (`frequenza`), 0607 (`stato`), 0608 (`ingressi`), 0609 (`spike`), 0611 (`sopravvivenza`),
0612 (`controllo`), tutte del 12 ottobre 2026; ops 0506 (5 ottobre, prezzi mescolati); ops 0586 (11 ottobre, gate);
`docs/revisione_sospese_30set.md`; `research/confronto/risultati.md`; `research/taratura/placebo/risultati.md`;
`docs/letture_esterne/`.
