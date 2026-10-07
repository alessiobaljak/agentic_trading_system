# Cosa abbiamo capito — una sezione per giorno

La stella polare (CLAUDE.md, 1 ott 2026): ogni giorno il sistema deve essere un passo più vicino
all'obiettivo, e non solo in profitto: conta ciò che abbiamo CAPITO (come perdiamo, perché entriamo
in ritardo, perché il trailing chiude presto, quali idee funzionano dopo il gate). Ogni mattina il
controllo giornaliero aggiunge qui IN CIMA una sezione `## AAAA-MM-GG` con 2-5 punti, ognuno con il
numero e la sua fonte; se non c'è niente di nuovo lo scrive. La macchina pubblica l'ultima sezione
nel report giornaliero in dashboard (sezione «Cosa abbiamo capito»): non va copiata altrove.

## 2026-10-06
* Il numero guida resta sotto zero mentre il margine si stringe: −0,04R su 202 segnali ±0,16 (ops 0517; il 3 ott −0,03 su 130 ±0,18). La lettura ufficiale è domani: con questi numeri la regola («motore ≤ 0 con almeno 80 segnali») scatterebbe, e la lettura stampata lo dice già. Non è più un'oscillazione: in quattro giorni non è mai andato oltre +0,006.
* Il registro cresce da solo mentre il paper resta fermo: 257 validate su 82 monete (ops 0511), erano 235 ieri e 223 sabato. La spinta è l'«intorno» delle quasi-promosse: 204 figlie nel giro della notte, 3 promosse. Spazio nel registro ~758 coppie: di questo passo (stima: ~100 coppie al giorno fra validate e in attesa) l'allarme dei 400 arriva fra 3-4 giorni, non settimane.
* Dal 27 set il lordo è ancora positivo (+0,037R su 162) e i costi (0,093R) lo rovesciano in −0,057R (ops 0508): è la terza lettura di fila con lo stesso segno. Sui long si perde (−0,110R su 85), sugli short si pareggia (+0,002 su 77); il regime neutro resta il peggiore (−0,182R su 93).
* Nei 7 giorni il trailing ha chiuso troppo presto 38 volte e ha protetto 26 (ops 0521): seconda settimana con i prematuri sopra i protetti. La regola del referto settimanale (due settimane di fila → proporre di allentare il keep) si applica domenica, non prima.
* Le letture di Firebase salgono: 8.444 nelle 24 ore (ops 0512; il 4 ott 7.763), quasi tutte dai rifiutati (4.843). Lontano dalla quota (50.000), ma la tendenza va tenuta d'occhio.

## 2026-10-07 (controllo delle 08:00: la prima lettura ufficiale)
* **Lettura ufficiale del 7 ott, selezione: «la prossima modifica va nel gate».** Il motore, dopo la validazione, fa −0,05R a trade su 230 segnali, margine ±0,14R per giornata (ops 0532): la regola scritta il 30 set («almeno 80 segnali e motore ≤ 0») scatta. Esecuzione: non si decide (stessi 200 segnali: paper −0,09R, motore −0,04R, differenza +0,05 ±0,07). È la conferma formale di quello che le tre prove avevano già detto: il problema non è il bot, è come nascono le strategie. La direzione presa (il protocollo di ricerca) è quella che la regola indica. Seconda lettura il 14 ott.
* Il registro del gate si riempie più in fretta del previsto: spazio per ~603 coppie (ops 0526; ieri 758, sabato 1.021). Di questo passo l'allarme dei 400 scatta fra 1-2 giorni: 456 passate nell'ultimo giro, 238 figlie dell'intorno. Il gate produce più coppie di quante il registro possa tenere, mentre il paper peggiora (−88,03 USDT, ops 0524).
* Tredici posizioni aperte insieme stamattina (ops 0535; massimo precedente 12) e 48 rifiuti «posizione già aperta» in 24 ore (ops 0533): i segnali abbondano, la qualità no. Dal 27 set il lordo è a +0,007R a trade (quasi zero) e i costi 0,098R (ops 0523): il paper perde esattamente i costi.
* Sui long si perde (−0,163R su 112 dal 27 set), sugli short si pareggia (+0,004 su 85) (ops 0523): quarta lettura di fila con lo stesso segno. Non è una regola (uscite e ingressi non si toccano), ma è una cosa capita: le strategie long del gate sono peggio delle short in questo mercato.

## 2026-10-07 (mattina: Passo 1 del protocollo)
* L'universo «al 31 dicembre 2023» è molto più piccolo di quello che il gate usa oggi: su 895 contratti perpetui in USDT con dati, solo 100 hanno due anni di storia, dati fino a fine 2023 e almeno 20 milioni di USDT al giorno nel 2023 (`research/universo/conteggi.json`, branch di coordinamento). 759 sono nati dopo il 2022. Il gate lavora sulle prime 200 per volume di oggi: in gran parte monete senza storia abbastanza lunga per un giudizio.
* Il bias di sopravvivenza è misurato, non solo dichiarato: 24 delle 100 idonee oggi non sono più negoziate, e 2 stanno fra le 20 di campagna (MATIC, FTM). Con un universo «di oggi» quelle 24 sparirebbero e il periodo chiuso sembrerebbe migliore di quello che era.
* Il guardiano funziona dal vivo: con il marcatore di coordinamento attivo ha rifiutato a un agente due comandi che toccavano `tests/` e una variabile di shell. È la prima prova del blocco meccanico in una sessione vera, non in un test.
* Il revisore avversario ha trovato in `selezione.py` una perdita d'informazione che non avevo visto: la scheda della moneta diceva da dove veniva la data di listing, e «archivio» voleva dire «delistata». Un dettaglio innocuo nel codice era un indizio sul periodo chiuso: corretto prima di scrivere le schede.

## 2026-10-06 (sera: Passo 0 del protocollo)
* Il bot in paper fa scattare lo stop su un prezzo che non esiste nei dati storici: il percorso del MID bid/ask fra un tick e l'altro, allargato al mark price (`bot/execution/executor.py:570-571`, `bot/core/price_stream.py:258`); il gate invece usa le ombre delle candele last (`backtesting/engine.py:942`). Nessun ordine vero imposta `workingType`. Per il protocollo la serie dello stop è una scelta da dichiarare, non un fatto: proposta last price.
* Il bot può eseguire una strategia scritta come codice (classe `Strategy`, `bot/strategies/base.py:36-76`), ma una coppia opera solo se sta nel registro delle validate, scritto solo dal gate (`bot/learning/adaptation.py:498-510`, `scripts/optimize.py:1493-1500`): una strategia del protocollo non ha oggi una porta d'ingresso nel bot senza passare il gate. E dal vivo gli indicatori esistono solo per 1m, 5m, 15m, 1h (`bot/config.py:281`).
* Il modello dei costi del bot è più leggero del reale: 0,08% per l'intero trade, commissione e slittamento insieme (`executor.py:178`), contro lo 0,10% della sola commissione taker andata e ritorno; il funding è spalmato sulle ore invece che pagato ai settlement, sempre a 8 ore (`bot/execution/costs.py:27-39`). Il bot non imposta la modalità di margine e non simula la liquidazione.
* I dati storici dei futures su data.binance.vision partono da gennaio 2020 (BTC è quotato dal settembre 2019) e conservano i contratti delistati (verificati LUNA, FTT, SRM, BTCST, RAY): la selezione del Passo 1 potrà includere le monete morte. L'API ufficiale è bloccata dalla regione del server (HTTP 451), ma lo stesso elenco si legge da www.binance.com.
* Quattro revisori avversari sui moduli nuovi hanno trovato 36 difetti confermati (motore 14, guardiano 10, dati 5, statistica 3, fatti 4), tutti corretti: fra i più seri, il guardiano che lasciava riscrivere il proprio marcatore e non risolveva i link simbolici, il bootstrap che dava errore zero con un blocco lungo quanto la serie, il gap in apertura ignorato dal motore. Senza la revisione sarebbero entrati nelle campagne.

## 2026-10-05
* Il numero guida è tornato a −0,03R su 182 segnali, margine ±0,17 (ops 0498; ieri +0,006 su 156): la lettura stampata dice già «la promessa non regge dopo la validazione: la prossima modifica va nel gate». Il verdetto resta al 7 ott, ma in tre giorni il numero ha oscillato fra −0,03 e +0,006 senza mai uscire dal margine: è un sistema a zero, non un sistema in calo.
* Il gate rigiocato nel passato, su 8 date complete (ops 0502): 6 promosse su 25.631 giudizi, e i loro 45 trade fanno −0,22R contro −0,14R delle bocciate (differenza −0,08 ±0,31, non decide: ne servono 80). Primo indizio diretto che la scelta del gate non è migliore del mucchio; con R2 (0 su 3.600) chiude il quadro: le validate nascono dalla ricerca ripetuta, non da candidate buone.
* La colonna 0,8/1,6/2,4 chiesta ieri: nel modello semplificato è la scala che perde meno, −0,20R a trade su 291 contro −0,37 (1/1,5/2,5) e −0,86 (2/4/6) (ops 0495). Conferma che il primo incasso è lontano, ma non cambia il segno: anche la scala migliore resta sotto zero in quel modello.
* Il paper esplorativo non «contribuisce» più: 11 trade a +0,242R contro −0,089R, differenza +0,331 ±0,475 → non si vede ancora (ops 0489; ieri «contribuisce» su 10). Era il limite del campione minimo, come scritto ieri.
* La prova sul prezzo casuale del 4 ott ha scritto 144 unità in errore, tutte «'cfg'» (ops 0502): conferma la causa dedotta ieri (stato dei worker in un altro modulo), corretta. Gira oggi alle 13:10.
* Il giro completo della notte è durato 3 h 22 (ops 0492) con 42.274 valutazioni e 421 passate: l'intorno delle quasi-promosse ha generato 213 figlie (riga ORIGINI). È il meccanismo della ricerca ripetuta che gonfia il conto delle prove.

* La prova sul prezzo casuale, a 1 ora (ops 0506): le stesse 100 strategie nuove sulle 72 monete, giudicate dal gate di oggi, passano **8 volte su 7.200** sulle candele vere e **16 volte su 7.200** sulle stesse candele rimescolate. Per la regola scritta prima: NON SI SA (sotto le 10 passate sul vero il rapporto non si legge). Osservato: sui prezzi senza nessun vantaggio possibile il gate ha promosso il doppio che sui prezzi veri. Inferito: a 1 ora il gate non distingue il rumore dal mercato; con 8 e 16 passate la differenza può essere caso. Chiude il quadro con la prova del 4 ott (0 su 3.600 a 15 minuti) e il gate rigiocato nel passato (promosse −0,22R contro −0,14R): il filtro del gate non aggiunge valore misurabile alle candidate nuove.
## 2026-10-04
* La stella polare è passata da −0,03R su 130 segnali (ops 0454) a +0,006R su 156, margine ±0,17 (ops 0474), per una giornata sola: il 3 ott 16 trade delle validate, 15 vinti, +0,869R a trade (ops 0479). Il numero oscilla intorno a zero dentro il margine: oggi la regola del 7 ott («motore ≤ 0 con almeno 80 segnali → la modifica va nel gate») non scatterebbe, ieri sì. Il verdetto del 7 ott può dipendere da un giorno buono o cattivo: per questo c'è la conferma del 14.
* Entriamo un po' peggio del segnale: ingresso a +0,038R rispetto alla chiusura della candela del segnale, con 155 secondi di ritardo (mediane, dato D8 raccolto dal 1 ott; ops 0479). È circa metà dei costi stimati a trade (0,081R): non spiega le perdite da solo, ma pesa.
* A 1 ora il gate passa il 2,2% delle prove (218 su 9.840, ops 0468) contro lo 0,12% a 15 minuti (25 su 20.667, ops 0470), ma le due quote NON si confrontano: la passata a 1 ora rivaluta soprattutto spec già note a 1 ora (259 su 328, riga ORIGINI di ops 0468), cioè coppie già passate, mentre il giro «solo urgenti» a 15 minuti è quasi tutto candidate nuove. Il «diciotto volte» scritto stamattina era soprattutto composizione (corretto alle 09:30). La domanda giusta, a parità di candidate, la fa G7 (sì del 4 ott).
* Primo verdetto «contribuisce» nelle funzioni: i quasi-passaggi operati a un quarto (paper esplorativo) fanno +0,385R su 10 trade contro −0,065R delle validate, differenza +0,450 ±0,419 (ops 0465). È al limite del campione minimo (10) e il metro dice 100 trade; ma va nella stessa direzione di T2: oggi la scelta del gate non aggiunge un vantaggio misurabile.
* T2 su 240 trade (ieri 207): a 1 ora i segnali vanno leggermente contro, −0,080 mosse tipiche, margine [−0,184; +0,013] (ops 0471). Ancora «nessun vantaggio misurabile», ma la prima ora è la più vicina a «peggio del caso».
* USELESS e SUI a «0 su 7» non sono un difetto di oggi: tutti i 14 trade sono short, aperti fra il 21 e il 27 set (l'ultimo alle 11:15 UTC), e il motore non li riproduce nemmeno sui valori registrati dal paper (classe IGNOTO, ops 0483). È la firma del difetto della sessione oraria corretto il 27 set alle 19:40 UTC (J13: l'ora del processo al posto di quella della candela, fuori sessione era ammesso solo lo short). Sulle 18 coppie rigirate, tutti i 20 trade non riprodotti visibili sono di prima della correzione, e dopo la correzione nessun trade rigirato ha la regola che non scatta (7 abbinati, 1 col motore ancora dentro il trade prima; ops 0483). Quei 20 trade fanno −33,57 USDT, circa metà della perdita totale del paper (−62,59, ops 0466). Che le due spec usino la sessione è molto probabile ma non verificato.

* R2: le 50 candidate casuali di R1 del 17 set, giudicate dal gate di OGGI sulle 72 monete operate, passano 0 volte su 3.600 (ops 0485). Lo 0 di R1 è vero: una candidata nuova a caso non passa quasi mai, nemmeno nel gate di produzione (R1 ha la sua prima promossa al 20 ago, 1 su 9.050 giudizi). Le 223 validate quindi non vengono da candidate «fortunate al primo colpo», ma dalla ricerca ripetuta giro dopo giro (mutazioni dei quasi-passaggi, rivalutazioni): è lì che il numero delle prove cresce senza essere contato.
## 2026-10-03
* Lettura ufficiale del 3 ott: le declassate (−0,131R su 70) contro le attive (+0,127R su 33) fanno −0,258R con margine ±0,458R → «non si decide» (ops 0445). Il quarto di puntata ha risparmiato 29,04 USDT, ma non si può dire che scelga trade peggiori.
* Lo «0 promosse» di R1 su 16.000 candidate (ops 0458) è sospetto ma non dimostrato: il gate vero passa lo 0,19% di un mix di 92 strategie (39 casuali nuove, 28 mutazioni dei quasi-passaggi, 25 rivalutate; 44/22.632, ops 0448/0450) e non stampa quante delle 44 siano casuali. Le due date complete sono recenti (17 e 3 set), quindi non è «storia corta». Si decide solo a parità di candidate (R2).
* R1 lavora 2,5 ore a lancio per costruzione (`BUDGET_S`): ieri 315 unità in ~2,4 ore di calcolo, poi fermo fino al lancio di stamattina. A 200 monete restano ~36 ore (ops 0458): la lettura del 10 ott non è raggiungibile senza la restrizione alle monete operate.
* Metà degli stop sono ingressi sbagliati dall'inizio: 51 su 107 (48%) non vanno mai a favore di 0,25R, e dei 7 stop nuovi 5 sono così (ops 0451 vs 0426). Il selettore in ombra non li distingue: p media 0,649 nei vinti contro 0,648 nei persi, correlazione +0,003 su 166 (ops 0445).
* L'ondata di 10 long del 2 ott è a +4,27 USDT sulle 8 chiuse (ops 0445) e la fascia «6+ posizioni nello stesso verso» è l'unica in R positivo (+0,026 su 11, contro −0,100 su 137 e −0,125 su 90). Su questi numeri l'affollamento non è dove si perde; campione piccolo.
* Il motore dopo la validazione resta a −0,03R, ora su 130 segnali ±0,18 (ops 0454; ieri 106 ±0,21): il margine si stringe e il numero non si muove.

## 2026-10-02
* T2: i segnali del paper non hanno un vantaggio misurabile sul caso. Il prezzo dopo 1, 4, 12 e 24
  ore dall'ingresso non si distingue da ingressi a caso sulla stessa moneta e direzione, nelle 12 ore
  dopo (201 trade, 15 giornate; a 4 ore −0,001 mosse tipiche, margine ±0,13, cioè circa ±0,5%; ops
  0437). Per la regola il lavoro sui take profit si ferma (T1 congelata): il problema è l'ingresso o il
  gate (R1).
* Anteprima del fuori campione girata: dopo la scelta del gate il motore fa −0,03R a trade su 106
  segnali, ±0,21 (ops 0429), ieri +0,06 su 89 (ops 0387). La regola del 7-14 ott («motore ≤ 0 con
  almeno 80 segnali → la prossima modifica va nel gate») oggi scatterebbe; il verdetto resta alla data.
* Prima dei costi il paper dal 27 set è quasi a zero: +0,013R a trade su 81, costi 0,078R (ops 0420); e
  il modello dei costi è un po' ottimista rispetto a Binance: commissioni 0,08% contro 0,10%, ~0,012R a
  trade (C5).
* Dal 27 set si perde soprattutto col mercato neutro: −0,317R su 39 trade, contro +0,357R su 25 a
  favore del trend (ops 0420; margine non stampato).

## 2026-10-01
* Il bot esegue quasi come il motore: sugli stessi 79 segnali la differenza è +0,05R con margine
  ±0,16R (ops 0387). Un difetto grosso di esecuzione è quasi escluso; il problema sembra prima del bot.
* Dopo la scelta del gate le validate rendono poco anche nel motore: +0,06R a trade su 89 segnali,
  ±0,18 (ops 0387), contro le +0,18 promesse. È un indizio, non ancora un verdetto (letture 7-14 ott).
* Il paper per ora non si distingue da un prezzo casuale con le stesse uscite: 54% di vinti contro
  54%, 46% di stop contro 46% (ops 0401, K4). Le classi dei referti descrivono la forma delle uscite,
  non una diagnosi.
* Stop giornaliero e freno di serie non avrebbero aiutato: sul gate tolgono soprattutto i rimbalzi
  (stop 3%: −11.615 e drawdown da 11,7% a 20,3%, ops 0405).
* Nessuna funzione ha ancora un contributo dimostrato oltre il margine; l'ombra AI (spenta) avrebbe
  evitato trade a −0,10R contro +0,23R di quelli che approvava, diff −0,33 ±0,36 (ops 0409).
