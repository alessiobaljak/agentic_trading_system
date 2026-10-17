# Ipotesi della campagna BTC51 (Passo 2, Fase 1)

Scritto il 17 ottobre 2026 dalla sessione di ricerca, **prima di qualunque test di risultato**. Le stime dei trade
(8.4, solo conteggi) sono nel log come voci `nota` (file `codice/stime_1.json`, `codice/stime_2.json`).

Regola 7, dichiarata una volta per tutte: conosco la storia di BTC dal 2024 in poi (per esempio che il 2024 è stato
un anno di forte rialzo). Le idee qui sotto sono scelte dalla letteratura pubblicata prima del 2024 e sono le famiglie
classiche del catalogo (tendenza, medie, volume, funding, orari, ritorno verso la media, ritracciamenti, compressione
della volatilità). Per ogni idea dico se la conoscenza del dopo-2023 potrebbe averla spinta: dove la risposta è «forse»,
lo scrivo, e la tengo comunque perché è un'idea nota prima del 2024 e scelta per entrambe le direzioni.

Costi da tenere a mente (sezione 6): circa 0,12 R per trade con uno stop all'1%; con lo stop a 1,5 × ATR orario
(spesso fra 0,8% e 1,5%) i costi sono fra 0,08 e 0,15 R. Su 30 minuti e con stop stretti i costi pesano di più.

Le spiegazioni concorrenti valgono in comune per tutte le idee (elenco A) e si aggiungono quelle specifiche di ogni
idea. Per ognuna: cosa prevede, e cosa la smentisce.

## Elenco A — spiegazioni concorrenti comuni

| # | Spiegazione | Cosa prevede | Cosa la smentisce |
|---|---|---|---|
| A1 | Caso: il risultato è fortuna fra molte prove | p-value non piccolo; risultato instabile fra blocchi di tempo e con parametri vicini | p-value ≤ 0,023 e verifiche della Fase 4 superate |
| A2 | Tendenza di fondo: nel 2020-2021 BTC sale molto, nel 2022 scende | i long guadagnano solo nel 2020-2021, gli short solo nel 2022, indipendentemente dal segnale | le entrate casuali nella stessa direzione guadagnano quanto il segnale (p-value alto) |
| A3 | Volatilità: il segnale sceglie momenti agitati, dove target e uscite cambiano il risultato senza prevedere la direzione | R medio diverso dal caso solo per la larghezza dello stop | la regola delle 5 fasce di larghezza (10.1) neutralizza l'effetto: p-value alto |
| A4 | Costi: un vantaggio lordo piccolo sparisce dopo commissioni e slippage | R medio lordo positivo, netto vicino a zero o negativo | R medio netto ≥ 0,2 R e positivo a costi doppi |
| A5 | Artefatto dei dati: candele anomale (marzo 2020, 26 luglio 2021) o mark sostituito | pochi trade estremi fanno il risultato | togliendo il 5% dei trade migliori l'R medio resta positivo (verifica 4) |
| A6 | Pochi trade estremi: il risultato viene da 2-3 movimenti enormi | come A5 | verifica 4 |
| A7 | Un solo periodo: tutto il risultato in un blocco di 9 mesi | un blocco con oltre il 50% della somma | verifica 3 |
| A8 | Adattamento dei parametri: funziona solo con quel valore del catalogo | crollo con ±20% sui parametri | verifica 1 |
| A9 | Errore del motore che guarda il futuro | segnali diversi quando si tronca la serie | test di troncamento (verifica 6) |
| A10 | Regola dentro la candela: stop e target nella stessa candela decidono il risultato | grande differenza con la regola opposta | verifica 9 piccola |
| A11 | Funding: il risultato viene dal funding incassato o pagato, non dal prezzo | R medio dominato dal funding (trade lunghi) | funding piccolo rispetto all'R medio nel dettaglio dei trade |

---

## I-01 — Le rotture dei massimi e minimi recenti continuano (seguire la tendenza)

**Fonti.** Moskowitz, Ooi, Pedersen, «Time series momentum», Journal of Financial Economics 104(2), 2012; Liu,
Tsyvinski, «Risks and Returns of Cryptocurrency», Review of Financial Studies 34(6), 2021 (versione NBER w24877,
2018): il rendimento passato di BTC prevede quello delle settimane successive (momento nel tempo). La regola della
rottura del canale di Donchian è quella dei «Turtles»: C. Faith, «Way of the Turtle», McGraw-Hill, 2007.

**Affermazione verificabile.** Dopo una chiusura sopra il massimo delle 55 candele orarie (o delle 20 candele da 2
ore) precedenti, il prezzo di BTCUSDT nelle ore e nei giorni seguenti sale più di quanto salga partendo da un momento a
caso con la stessa larghezza di stop; simmetrico per le rotture dei minimi e lo short.

**Sotto-domande.** Vale di più con volatilità alta o bassa? Chi compra: chi segue la tendenza (fondi sistematici,
piccoli investitori con leva, sezione «Crypto carry» qui sotto), e gli short costretti a chiudere quando il prezzo
supera livelli visibili. L'effetto, se c'è, si manifesta in giorni, non in ore: per questo l'uscita è il trailing
(U3), che lascia correre.

**Spiegazioni concorrenti specifiche.**
| # | Spiegazione | Previsione | Smentita |
|---|---|---|---|
| 1-1 | Le rotture sono falsi segnali in mercato laterale; il guadagno viene solo dalle fasi di tendenza del 2020-21 | R medio positivo solo nei blocchi 2 e 3 | verifica 3 superata |
| 1-2 | Il trailing «fa» il risultato su qualunque ingresso (asimmetria dell'uscita) | le entrate casuali con le stesse uscite guadagnano quanto il segnale | p-value ≤ 0,023 |
| 1-3 | Liquidazioni a cascata dopo la rottura (movimento vero ma breve) | guadagno solo nelle prime candele | informativo: durata dei trade vincenti |

**Varianti.**
- **V-001** · 1h · long · nessun filtro · E3 Donchian 55 · nessuna conferma · M · S1 2 × ATR · U3 trailing 3 × ATR.
  Perché: 55 ore ≈ 2,3 giorni, rottura di un livello visibile; 1h per arrivare a 150 trade (stima 237); stop a 2 ATR
  per non uscire nel rumore della candela di rottura; trailing largo per lasciare correre.
- **V-002** · la stessa, short (stima 194). Perché: la tendenza vale nei due sensi; il 2022 è ribassista.
- **V-003** · 2h · long · E3 Donchian 20 · S1 2 × ATR · U3 3 × ATR (stima 199). Perché: 20 candele da 2 ore ≈ 1,7
  giorni, una rottura simile su candele più lunghe (meno rumore, meno costi in R).
- **V-004** · la stessa, short (stima 176).

Previsione: R medio fra −0,05 e +0,25 R; p-value fra 0,05 e 0,5. Prevedo che non superino (la tendenza di BTC esiste
ma con stop a 2 ATR e trailing la maggior parte dei trade esce in perdita piccola, e il caso con la stessa uscita
guadagna già). Conoscenza del dopo-2023: forse (il rialzo 2024); per questo le provo nei due sensi.

---

## I-02 — Il prezzo sopra la sua media mobile tende a restarci (medie mobili)

**Fonti.** Brock, Lakonishok, LeBaron, «Simple technical trading rules and the stochastic properties of stock
returns», Journal of Finance 47(5), 1992; Detzel, Liu, Strauss, Zhou, Zhu, «Learning and predictability via
technical analysis: Evidence from bitcoin and stocks with hard-to-value fundamentals», Financial Management 50(1),
2021: i rapporti fra prezzo e medie mobili prevedono i rendimenti di BTC.

**Affermazione.** Dopo che la chiusura da 4 ore incrocia verso l'alto la EMA 50 (o la EMA 20 incrocia la EMA 50
su 1h), il rendimento fino all'incrocio opposto supera quello di entrate casuali con le stesse uscite; simmetrico per
lo short.

**Sotto-domande.** Funziona perché i fondamentali di BTC sono difficili da valutare e gli investitori imparano dal
prezzo (Detzel e altri)? L'effetto è lento (settimane): l'uscita è il segnale opposto (U4) con stop largo.

**Concorrenti specifiche.** 2-1 Molti incroci in laterale (perdite piccole e frequenti) annullano i pochi grandi
guadagni: previsione PF vicino a 1, smentita PF ≥ 1,3 e R medio ≥ 0,2. 2-2 Il risultato è tutta la tendenza di fondo
(A2), smentita dal p-value.

**Varianti.**
- **V-005** · 4h · long · E2 chiusura incrocia EMA 50 · M · S1 3 × ATR · U4 segnale opposto (stima 201). Perché: 50
  candele da 4 ore ≈ 8 giorni, l'orizzonte del momento nel tempo; stop largo perché l'uscita vera è l'incrocio opposto.
- **V-006** · la stessa, short (stima 200).
- **V-007** · 1h · long · E1 EMA 20/50 · M · S1 3 × ATR · U4 (stima 214). Perché: incrocio più lento e meno rumoroso
  della chiusura sulla media, su 1h per avere abbastanza trade.

Previsione: R medio fra −0,1 e +0,3 R; prevedo che non superino (in BTC le medie funzionano sui rendimenti settimanali,
qui il guadagno per trade è diluito da molti falsi incroci). Conoscenza del dopo-2023: forse, come I-01.

---

## I-03 — Le candele con volume anomalo continuano nella loro direzione

**Fonti.** Gervais, Kaniel, Mingelgrin, «The high-volume return premium», Journal of Finance 56(3), 2001;
Caporale, Plastun, «Momentum effects in the cryptocurrency market after one-day abnormal returns», CESifo Working
Paper 7917, 2019 (poi in Financial Markets and Portfolio Management, 2020): dopo un movimento anomalo i prezzi
continuano nella stessa direzione fino a fine giornata e il giorno dopo, **ma per BTC i movimenti anomali verso l'alto
mostrano il contrario** (ritorno indietro).

**Affermazione.** Una candela con volume oltre 2 volte la media delle 20 precedenti e chiusura nella direzione del
movimento è seguita, nelle 12 candele seguenti, da un movimento nella stessa direzione maggiore del caso.

**Sotto-domande.** Chi opera: notizie e liquidazioni concentrano il volume; il movimento continua se l'informazione
si diffonde lentamente, si ritira se è una cascata di liquidazioni. Per BTC la fonte prevede: continuazione sui ribassi,
ritorno sui rialzi.

**Concorrenti specifiche.** 3-1 Le candele ad alto volume sono anche le più volatili (A3). 3-2 Liquidazioni a cascata:
rimbalzo dopo il volume ribassista (prevede R negativo per lo short). 3-3 Effetto dell'ora: il volume alto cade
all'apertura degli Stati Uniti.

**Varianti.**
- **V-008** · 4h · long · E12 volume relativo 2,0 · M · S1 1,5 × ATR · U1 target 2 R e U2 dopo 12 candele (stima 161).
- **V-009** · la stessa, short (stima 183).
- **V-010** · 1h · long · E12 2,0 · M · S1 1,5 × ATR · U1 2 R e U2 12 candele (stima 831).
Perché: 12 candele coprono «fino al giorno dopo» su 4h (2 giorni) e mezza giornata su 1h; target a 2 R per incassare la
continuazione; stop 1,5 ATR, più largo del rumore della candela.

Previsione: per la fonte, lo short (V-009) è quello con più probabilità; i long V-008 e V-010 dovrebbero dare R medio
vicino a zero o negativo. Conoscenza del dopo-2023: no.

---

## I-04 — Il funding estremo segnala posizioni affollate che poi si sgonfiano

**Fonte.** Schmeling, Schrimpf, Todorov, «Crypto carry», BIS Working Paper 1087, 2023: il carry (differenza fra
futures e spot, che nei perpetui si paga con il funding) è a volte altissimo e molto variabile, spinto dalla domanda di
leva di piccoli investitori che seguono la tendenza e da un capitale di arbitraggio scarso. **L'inferenza è mia**, non
della fonte: se il funding alto misura una domanda di leva affollata, quando è alto i long a leva sono vulnerabili e il
prezzo, nelle ore seguenti, tende a scendere più del caso; simmetrico quando il funding è negativo (short affollati).

**Affermazione.** Alla prima candela oraria dopo un regolamento con funding sopra +0,03% per 8 ore, il prezzo nelle 24
ore seguenti scende più che da un momento a caso (short); dopo un funding sotto 0,00% sale più del caso (long).

**Sotto-domande.** Il funding alto è più frequente nel 2021 (rialzo): lo short rischia di stare contro la tendenza
(A2, a favore delle entrate casuali long? no: le entrate casuali hanno la stessa direzione). Il funding stesso pesa: lo
short incassa il funding alto (A11), circa 0,03-0,1% per 8 ore, cioè 0,03-0,1 R per regolamento con stop al 2-3%.

**Concorrenti specifiche.** 4-1 Il funding alto accompagna la tendenza in corso, che continua (prevede R negativo per lo
short). 4-2 Il guadagno viene dal funding incassato (A11).

**Varianti.**
- **V-011** · 1h · short · E11 funding sopra +0,03% · M · S1 2 × ATR · U2 dopo 24 candele (stima 224). Perché: 24 ore,
  tre regolamenti; stop 2 ATR.
- **V-012** · 1h · long · E11 funding sotto 0,00% · M · S1 2 × ATR · U2 24 candele (stima 228).

Previsione: R medio fra −0,2 e +0,15 R; prevedo che non superino. Conoscenza del dopo-2023: no.

---

## I-05 — La rottura del range della notte asiatica all'apertura europea continua

**Fonti.** T. Crabel, «Day Trading with Short Term Price Patterns and Opening Range Breakout», Traders Press, 1990 (la
rottura del range d'apertura); Eross, McGroarty, Urquhart, Wolfe, «The intraday dynamics of bitcoin», Research in
International Business and Finance 49, 2019: volumi e volatilità di BTC crescono nelle ore europee e americane.

**Affermazione.** La prima chiusura oraria fra le 08:00 e le 16:00 UTC sopra il massimo delle ore 00-08 è seguita da un
rialzo fino a sera maggiore del caso; simmetrico sotto il minimo.

**Sotto-domande.** Chi opera: alle 08:00 UTC arrivano gli operatori europei, con nuove informazioni e volumi; il range
notturno è un livello visibile con ordini sopra e sotto. Effetto entro la giornata: uscita alle 21:00 UTC (U2s).

**Concorrenti specifiche.** 5-1 La rottura del range è solo un modo di entrare quando c'è movimento (A3). 5-2 I
movimenti europei si ritirano con l'apertura americana.

**Varianti.**
- **V-013** · 1h · long · E10 · M · S1 1,5 × ATR · U1 2 R e U2s alle 21:00 UTC (stima 380).
- **V-014** · la stessa, short (stima 361).

Previsione: R medio fra −0,15 e +0,1 R: è l'idea più nota e più vecchia, quindi la meno probabile da trovare ancora
viva. Conoscenza del dopo-2023: no.

---

## I-06 — In mercato laterale i ritorni dentro le bande di Bollinger tornano verso la media

**Fonti.** J. Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001; J. W. Wilder, «New Concepts in Technical
Trading Systems», 1978 (ADX come misura di tendenza).

**Affermazione.** Con ADX(14) sotto 20 (nessuna tendenza), quando la candela da 30 minuti torna dentro le bande dopo una
chiusura fuori, il prezzo nelle ore seguenti torna verso la media più del caso; comprare con un ordine limit poco sotto
la chiusura migliora il prezzo d'ingresso.

**Sotto-domande.** Chi opera: chi fornisce liquidità compra gli eccessi in mercato calmo; senza tendenza un movimento
fuori dalle bande è rumore. Effetto in poche ore: U2 12 candele (6 ore), target 1,5 R.

**Concorrenti specifiche.** 6-1 Il vantaggio è solo il prezzo limit (si vede dalla verifica 11, versione a mercato).
6-2 L'ordine limit è eseguito soprattutto quando il prezzo continua contro (selezione avversa): R medio peggiore del
previsto, verifica 8 la smaschera.

**Varianti.**
- **V-015** · 30m · long · F2 ADX sotto 20 · E5 ritorno da Bollinger k 2,0 · L k 0,25 validità 3 · S1 1,5 × ATR · U1
  1,5 R e U2 12 candele (stima 243 eseguiti su 303).
- **V-016** · la stessa, short (stima 276 su 332).
Perché 30m: su 1h con il filtro restano circa 100 trade, sotto i 150.

Previsione: R medio fra −0,2 e +0,05 R (costi alti su 30 minuti); prevedo che non superino. Conoscenza del dopo-2023:
no.

---

## I-07 — In tendenza rialzista i ribassi brevi si comprano

**Fonti.** L. Connors, C. Alvarez, «Short Term Trading Strategies That Work», TradingMarkets, 2009 (comprare
l'ipervenduto di breve periodo sopra la media a 200); Wilder, 1978 (RSI).

**Affermazione.** Con la chiusura da 30 minuti sopra la EMA 200, quando l'RSI(7) risale sopra 30 il prezzo nelle 12 ore
seguenti sale più del caso; l'ordine limit a 0,25 ATR sotto la chiusura migliora l'ingresso.

**Sotto-domande.** Chi opera: venditori di breve periodo spinti da notizie o liquidazioni, mentre la domanda di fondo
resta. Effetto in ore. Connors usa RSI(2): il catalogo parte da 7, quindi l'effetto è più lento e meno estremo.

**Concorrenti specifiche.** 7-1 È la tendenza di fondo (A2) con un ingresso qualunque. 7-2 Selezione avversa del limit
(come 6-2).

**Variante.**
- **V-017** · 30m · long · F1 chiusura sopra EMA 200 · E6 RSI 7, soglia 30 · L k 0,25 validità 3 · S1 2 × ATR · U1
  1,5 R e U2 24 candele (stima 327 su 383). Perché 30m: su 1h la stima è 149, sotto il minimo; su 4h 36.

Previsione: R medio fra −0,15 e +0,1 R. Conoscenza del dopo-2023: forse (comprare i ribassi nel rialzo); la provo
perché è un'idea classica del 2009, ma ne tengo conto.

---

## I-08 — Dopo la calma viene il movimento: rottura delle bande con volatilità bassa

**Fonti.** Bollinger, 2001 (la «compressione»: bande strette precedono movimenti ampi); Mandelbrot, «The variation of
certain speculative prices», Journal of Business 36(4), 1963 (la volatilità si raggruppa e cambia regime).

**Affermazione.** Quando la volatilità oraria (ATR percentile) è sotto il 30° percentile delle 500 candele precedenti,
una chiusura fuori dalla banda di Bollinger (k 2,0) è seguita da un movimento nella stessa direzione maggiore del caso.

**Sotto-domande.** Chi opera: dopo la calma, la rottura scatena gli stop accumulati vicino al range. Il movimento può
durare ore o giorni: uscita con trailing a 2 ATR.

**Concorrenti specifiche.** 8-1 Il trailing guadagna su qualunque ingresso dopo la calma, perché la volatilità torna
comunque (A3, ma la direzione no). 8-2 Falsa rottura: il prezzo rientra (R negativo).

**Varianti.**
- **V-018** · 1h · long · F3 volatilità bassa · E4 rottura di Bollinger k 2,0 · M · S1 1,5 × ATR · U3 trailing 2 × ATR
  (stima 230).
- **V-019** · la stessa, short (stima 187).

Previsione: R medio fra −0,1 e +0,2 R; prevedo che non superino. Conoscenza del dopo-2023: no.

---

## Fase 3 dopo il primo lotto (17 ottobre 2026)

Nessuna delle 19 varianti supera la Fase 2 (log, voci `risultato` da V-001 a V-019). Analisi dei trade delle tre più
vicine (`codice/fase3_analisi.py`, dettagli in `risultati/fase3_<id>.json`), osservato:

- **V-011** (funding sopra +0,03%, short): nessun trade nel 2022 (il funding non ha mai superato la soglia); metà della
  somma degli R viene dal primo semestre 2020. Il funding incassato vale +0,047 R a trade. Non si corregge con un
  filtro: manca un intero blocco di tempo.
- **V-012** (funding sotto 0, long): R medio positivo in 5 semestri su 6 (negativo solo nel primo semestre 2022);
  funding quasi nullo. **Feriali: 169 trade, +0,278 R; fine settimana: 59 trade, −0,134 R.**
- **V-018** (rottura dopo la calma, long): tre quarti della somma nel primo semestre 2020, negativa nel 2022; anche qui
  feriali +0,461 R contro fine settimana −0,175 R. Ha già un filtro (volatilità bassa) e il catalogo ne ammette uno:
  il giorno della settimana non si può aggiungere.

## I-09 — Nel fine settimana i segnali valgono meno (nata dalla Fase 3)

**Fonte.** Baur, Cahill, Godfrey, Liu, «Bitcoin time-of-day, day-of-week and month-of-year effects in returns and
trading volume», Finance Research Letters 31, 2019: il volume di BTC è stabilmente più basso nel fine settimana (le
anomalie di rendimento per giorno invece non persistono). Inferenza mia: con meno operatori (in particolare
istituzionali) il funding negativo del fine settimana misura meno una vera folla di short a leva, e il segnale vale meno.

**Attenzione: l'idea nasce dall'analisi dei trade di V-012, cioè dagli stessi dati.** È il caso tipico di adattamento
al passato (A8): 59 trade del fine settimana sono pochi e la differenza può essere caso. Per il protocollo è una
variante nuova, consuma un tentativo e passa la Fase 2 da capo; la validazione la giudica su dati non visti.

**Concorrenti specifiche.** 9-1 Caso: la differenza feriali/fine settimana sparisce in validazione. 9-2 Nel fine
settimana il funding negativo è più frequente nel primo semestre 2022 (ribasso), e il filtro toglie un periodo cattivo
più che un giorno cattivo: si vede dalla stabilità per blocchi.

**Variante.**
- **V-020** · 1h · long · F6 solo giorni feriali · E11 funding sotto 0,00% · M · S1 2 × ATR · U2 24 candele (stima
  180). Tutto il resto come V-012.

Previsione: R medio fra +0,15 e +0,30 R, p-value sotto 0,05; per l'origine dell'idea mi aspetto che in validazione
perda gran parte del vantaggio.

**Esito di V-020 (17 ottobre).** Supera la Fase 2 e la Fase 4 (log). Un indizio contro I-09 c'era già prima del
test, e lo scrivo qui: in V-011 (short sul funding alto) il fine settimana era migliore dei feriali (+0,314 contro
+0,072 R). L'effetto del giorno, se c'è, non vale per tutti i segnali del funding.

## Fase 5, prima parte: famiglie non ancora provate

Restano 20 tentativi. Per non fissarmi sul funding provo tre famiglie diverse, scelte prima di qualunque risultato su
di esse (stime in `codice/stime_4.json` e `stime_5.json`). Le altre famiglie hanno troppo pochi trade con regole
sensate (stocastico in laterale su 1h: 47 e 91 trade; RSI a metà su 4h: 80) oppure sono già state provate in forma
simile e con esito chiaramente negativo (ritorno verso la media su 30 minuti, V-015 e V-016). Le scarto senza testarle.

### I-10 — Il MACD nella direzione della tendenza lunga

**Fonti.** G. Appel, «Technical Analysis: Power Tools for Active Investors», FT Press, 2005 (il MACD, ideato da
Appel negli anni '70); Brock, Lakonishok, LeBaron, 1992 (filtrare con la tendenza lunga). **Affermazione:** con la
chiusura da 2 ore sopra la EMA 200, un incrocio verso l'alto del MACD sulla sua linea di segnale è seguito da un rialzo
che, lasciato correre con il trailing, supera il caso; simmetrico sotto la EMA 200 per lo short. **Concorrenti
specifiche:** 10-1 è la stessa cosa di I-01 e I-02 (tendenza) con un altro ingresso: se I-01 e I-02 non hanno
superato, anche questa probabilmente no; 10-2 il filtro EMA 200 sceglie solo i periodi di tendenza (A2).
- **V-021** · 2h · long · F1 sopra EMA 200 · E9 MACD (12, 26, 9) · M · S1 2 × ATR · U3 3 × ATR (stima 157).
- **V-022** · la stessa, short, F1 sotto EMA 200 (stima 165).
Previsione: R medio fra −0,05 e +0,2; non superano.

### I-11 — In tendenza ribassista i rimbalzi brevi si vendono (specchio di I-07)

**Fonte.** Connors, Alvarez, 2009 (la regola è simmetrica). **Affermazione:** con la chiusura oraria sotto la EMA 200,
quando l'RSI(7) riscende sotto 70 il prezzo nelle 24 ore seguenti scende più del caso; ordine limit a 0,25 ATR sopra
la chiusura. **Concorrenti:** come I-07.
- **V-023** · 1h · short · F1 sotto EMA 200 · E6 RSI 7, soglia 70 · L k 0,25 validità 3 · S1 2 × ATR · U1 1,5 R e U2
  24 candele (stima 152).
Previsione: R medio fra −0,15 e +0,1; non supera (V-017, la versione long su 30 minuti, ha dato +0,025).

**Esito (17 ottobre).** V-021 +0,050 R (p 0,606), V-022 −0,081 R (p 0,678), V-023 +0,023 R (p 0,201): nessuna
supera, come previsto.

## Fase 5 — sfida alla conclusione (17 ottobre 2026)

Varianti usate: 23 su 40. Candidati: uno, **V-020**. Le domande del protocollo, con i fatti:

1. **Mi sono fissato sulla prima idea decente?** In parte sì: V-020 è un ritaglio di V-012, la variante che ci era
   andata più vicino. Ma prima e dopo ho provato 11 famiglie diverse (tendenza, medie, volume, funding nei due sensi,
   range asiatico, ritorno verso la media, ritracciamenti nei due sensi, compressione, MACD), 22 varianti in tutto
   oltre a V-020. Le famiglie non provate (stocastico, RSI a metà, sessioni, VWAP) avevano troppo pochi trade con
   regole sensate oppure fonti deboli: le lascio. I 17 tentativi che restano non li uso: ogni variante in più aggiunge
   circa il 2,3% di probabilità di un falso candidato, e non ho idee con una fonte solida che non siano già state
   provate.
2. **Cosa direbbe uno scettico, con i test.**
   - «È solo il ribasso o il rialzo di fondo»: nel 2022 (BTC in forte ribasso) V-020, che è long, fa +0,117 R a trade
     su 91 trade, e le entrate casuali long nello stesso periodo fanno −0,004 R in media (Fase 2). Non è la tendenza.
   - «È la larghezza dello stop»: l'R medio è positivo in tutti e cinque i quinti di larghezza (da +0,107 a +0,402;
     `risultati/fase3_V-020.json`), e le entrate casuali hanno la stessa distribuzione.
   - «È il funding incassato»: il funding pesa −0,0003 R a trade, cioè niente.
   - «È un'ora del giorno»: positivo dopo tutti e tre i regolamenti (00, 08, 16 UTC).
   - «Sono pochi trade fortunati»: **qui lo scettico ha ragione a metà.** Togliendo i 9 trade migliori l'R medio
     scende da +0,223 a +0,012: la verifica 4 passa per poco. Il vantaggio vive di guadagni grandi e rari (le uscite a
     tempo fanno in media +1,24 R, gli stop −1,05 R).
3. **Cosa è più probabilmente fortuna.** (a) La scelta dei soli giorni feriali, nata guardando i 59 trade del fine
   settimana di V-012; V-011 mostra l'effetto opposto. (b) Il primo semestre 2020 (crollo di marzo e ripresa), che dà
   da solo il 42% della somma. (c) Il p-value 0,017 è vicino alla soglia 0,023, e viene dopo 19 varianti già provate.
4. **Conoscenza del 2024-2026.** Non so dire con certezza come sia andato il funding negativo dopo il 2023, e non ho
   scelto l'idea per quello; ma non posso escludere un'influenza inconsapevole. Lo dichiaro.

Conclusione onesta: c'è **un candidato debole**, statisticamente al limite e con un'origine (la scelta dei feriali)
che aumenta il rischio di adattamento al passato. La validazione su 15 mesi mai visti è la prova giusta.

## Seconda tornata (17 ottobre 2026, richiesta del proprietario: usare le 17 varianti restanti)

Il proprietario ha chiesto di usare anche i 17 tentativi rimasti, su idee nuove, prima della validazione. Il rischio
resta quello della sezione 8.3: con 40 varianti ci si attende circa 0,9 candidati falsi in tutto. Le idee qui sotto
sono scritte prima di qualunque risultato su di esse; le stime dei trade sono in `codice/stime_6.json` e
`stime_7.json` (log, voci `nota`). Idee scartate senza test perché sotto 150 trade con regole sensate: la «spremuta»
su 1h (71-82 trade), la tendenza nella calma su 1h e 2h (45-92), il ritorno da Bollinger nel fine settimana (129-134),
il funding negativo su 8h (131), la media a 20 su candele giornaliere (56). Il VWAP su 30 minuti (1.345 trade) lo
scarto per i costi: con lo stop a 2 ATR da 30 minuti i costi superano probabilmente il movimento atteso.

Regola 7 per tutta la tornata: nessuna di queste idee viene da quello che so del 2024-2026. Durante la verifica delle
fonti una ricerca ha mostrato il titolo di un articolo del 2026 sul funding: non l'ho aperto e non lo uso.

Elenco A delle spiegazioni concorrenti: vale come sopra per tutte.

### I-12 — Spremuta: la rottura contro la folla a leva

**Fonti.** Brunnermeier, Pedersen, «Market Liquidity and Funding Liquidity», Review of Financial Studies 22(6), 2009:
le perdite di chi è a leva fanno salire i margini e costringono a vendere (o ricomprare), e il movimento si alimenta da
solo; Schmeling, Schrimpf, Todorov, «Crypto carry», BIS Working Paper 1087, 2023: il funding misura la domanda di leva.
**Affermazione (inferenza mia):** quando il funding è negativo (folla di short a leva), una rottura del massimo delle 20
candele precedenti costringe gli short a ricomprare, e il rialzo prosegue più del caso; simmetrico con funding sopra
+0,03% (folla di long) e rottura del minimo. È un meccanismo diverso da I-04: lì si compra la folla affollata in
qualunque momento, qui si aspetta che il prezzo inizi a muoversi contro di lei. **Concorrenti specifiche:** 12-1 è I-01
(tendenza) con un filtro qualunque, e I-01 non ha superato; 12-2 il funding negativo cade nei ribassi del 2022 e le
rotture lì falliscono.
- **V-024** · 30m · long · F4 funding sotto 0,00% · E3 Donchian 20 · M · S1 2 × ATR · U1 2 R e U2 24 candele (stima
  160). Perché 30m: su 1h la stima è 82; 24 candele sono 12 ore, il tempo di una ricopertura forzata.
- **V-025** · la stessa, short, F4 funding sopra +0,03% (stima 184).
Previsione: R medio fra −0,1 e +0,2; non superano (costi su 30 minuti).

### I-13 — Nel fine settimana chi fornisce liquidità è pagato di più: i ribassi e i rialzi brevi tornano indietro

**Fonti.** Nagel, «Evaporating Liquidity», Review of Financial Studies 25(7), 2012: i guadagni delle strategie di
ritorno di breve periodo sono il compenso di chi fornisce liquidità, e crescono quando la liquidità scarseggia; Baur,
Cahill, Godfrey, Liu, Finance Research Letters 31, 2019: volume di BTC più basso nel fine settimana. **Affermazione:** nel
fine settimana, quando l'RSI(7) orario esce dalla zona di ipervenduto (risale sopra 30), il prezzo nelle 12 ore
seguenti risale più del caso; simmetrico per l'ipercomprato e lo short. È il rovescio di I-09: lì il fine settimana
toglieva valore a un segnale di folla, qui dà valore a un segnale di liquidità. **Concorrenti specifiche:** 13-1 il
ritorno verso la media su 30 minuti nei giorni qualsiasi (V-015, V-016) è andato male: se il fine settimana non è
diverso, andrà male anche questo; 13-2 selezione avversa del limit.
- **V-026** · 1h · long · F6 fine settimana · E6 RSI 7, soglia 30 · L k 0,25 validità 3 · S1 1,5 × ATR · U1 1,5 R e U2
  12 candele (stima 155).
- **V-027** · la stessa, short, soglia 70 (stima 164).
Previsione: R medio fra −0,15 e +0,15; non superano.

### I-14 — Le rotture valgono solo quando c'è già una tendenza forte

**Fonte.** J. W. Wilder, «New Concepts in Technical Trading Systems», Trend Research, 1978: l'ADX sopra 25 indica una
tendenza in atto, e i sistemi di tendenza si usano solo allora. **Affermazione:** con ADX(14) orario sopra 25, una
chiusura sopra il massimo delle 20 candele precedenti è seguita da un rialzo, lasciato correre con il trailing, maggiore
del caso; simmetrico per lo short. **Concorrenti:** 14-1 come 12-1 (I-01 con un filtro); 14-2 l'ADX alto arriva tardi,
a fine movimento.
- **V-028** · 1h · long · F2 ADX sopra 25 · E3 Donchian 20 · M · S1 2 × ATR · U3 3 × ATR (stima 230).
- **V-029** · la stessa, short (stima 214).
Previsione: R medio fra −0,1 e +0,15; non superano.

### I-15 — La tendenza funziona meglio nella calma

**Fonti.** Barroso, Santa-Clara, «Momentum has its moments», Journal of Financial Economics 116(1), 2015; Daniel,
Moskowitz, «Momentum crashes», Journal of Financial Economics 122(2), 2016: le strategie di momento crollano nei periodi
di volatilità alta e rendono di più in quelli calmi. **Affermazione:** con l'ATR percentile sotto il 30°, una rottura
del massimo delle 55 candele da 30 minuti precedenti, lasciata correre con il trailing, rende più del caso. Diversa da
I-08 (V-018): lì la rottura delle bande di Bollinger, qui il canale di Donchian, più lento. **Concorrenti:** 15-1 è I-08
con un altro ingresso. Short: 82 trade, sotto il minimo, non si prova.
- **V-030** · 30m · long · F3 volatilità bassa · E3 Donchian 55 · M · S1 2 × ATR · U3 3 × ATR (stima 180).
Previsione: R medio fra −0,05 e +0,25; non supera.

### I-16 — Sopra il VWAP comandano i compratori della giornata

**Fonte.** Zarattini, Aziz, «Volume Weighted Average Price (VWAP) The Holy Grail for Day Trading Systems», SSRN
4631351, 13 novembre 2023 (sul QQQ: long sopra il VWAP, short sotto). **Affermazione:** con la chiusura oraria sopra il
VWAP del giorno UTC, un incrocio verso l'alto della EMA 20 con volume relativo sopra 1,5 è seguito da un rialzo fino
alle 21:00 UTC maggiore del caso; simmetrico sotto il VWAP. **Concorrenti specifiche:** 16-1 un mercato che non chiude
mai non ha una «giornata» con un senso economico come la borsa: il VWAP dalla mezzanotte UTC è arbitrario (previsione:
niente); 16-2 la fonte è su un'azione statunitense, non su BTC.
- **V-031** · 1h · long · F7 sopra il VWAP · E2 chiusura incrocia EMA 20 · C1 volume relativo 1,5 · M · S1 2 × ATR ·
  U2s alle 21:00 UTC (stima 246).
- **V-032** · la stessa, short, sotto il VWAP (stima 331).
Previsione: R medio fra −0,2 e +0,1; non superano.

### I-17 — Il volume anomalo nelle ore americane porta informazione

**Fonti.** Eross, McGroarty, Urquhart, Wolfe, «The intraday dynamics of bitcoin», Research in International Business
and Finance 49, 2019: volumi e volatilità di BTC sono più alti quando sono aperte le borse americane; Gervais, Kaniel,
Mingelgrin, Journal of Finance 56(3), 2001. **Affermazione:** nella sessione americana (13:00-21:00 UTC) una candela
oraria con volume oltre il doppio della media e chiusura nella sua direzione è seguita da un movimento nella stessa
direzione fino a sera maggiore del caso. Differisce da I-03 (V-010) per la sessione: l'ipotesi è che il volume
americano sia più informato (istituzionale). **Concorrenti specifiche:** 17-1 V-010 (volume su 1h a tutte le ore) ha
dato −0,023 R: se la sessione non conta, andrà uguale; 17-2 nelle ore americane escono dati macro: movimenti grandi che
si ritirano.
- **V-033** · 1h · long · F5 sessione Stati Uniti · E12 volume relativo 2,0 · M · S1 1,5 × ATR · U1 2 R e U2s (stima
  451).
- **V-034** · la stessa, short (stima 460).
Previsione: R medio fra −0,15 e +0,1; non superano.

Totale della tornata: 11 varianti (V-024 … V-034), 34 su 40. Restano 6 tentativi per la Fase 3.

### Esito della seconda tornata e Fase 3 (17 ottobre)

Supera la Fase 2 solo **V-030** (tendenza nella calma, 30 minuti, long: 180 trade, +0,230 R, p 0,015), ma **fallisce
la Fase 4** (verifiche 2, 3 e 4: timeframe vicini −0,000 e −0,053 R; il 70% della somma in un blocco; senza i trade
migliori −0,117 R). Non è un candidato. La mia previsione era giusta.

Vicine: **V-024** (spremuta long con funding negativo, 30 minuti): +0,193 R con p 0,002, sotto la soglia di 0,2 R per i
costi (0,073 R di commissioni a trade); **V-032** (VWAP short): +0,016 R, p 0,034.

Osservato nell'analisi dei trade (`risultati/fase3_V-024.json`, `fase3_V-032.json`): lo schema «feriali meglio del fine
settimana» ricompare in V-024 (+0,285 contro −0,102 R) e V-032 (+0,098 contro −0,172 R), come in V-012 e V-018 (ma
non in V-011). È un'osservazione sugli stessi dati: **non** ne ricavo ritocchi delle varianti che l'hanno mostrata.

### I-18 — La rottura del range asiatico ha senso solo quando arriva l'Europa (riprende I-05)

**Fonti.** Crabel, 1990; Eross, McGroarty, Urquhart, Wolfe, RIBAF 49, 2019; Baur, Cahill, Godfrey, Liu, FRL 31, 2019. Il
meccanismo di I-05 è l'arrivo degli operatori europei alle 08:00 UTC con volumi e informazioni nuove: **nel fine
settimana le borse e le banche europee sono chiuse**, quindi il meccanismo non c'è e la rottura del sabato e della
domenica è rumore. Il ragionamento è di I-05 (scritto prima dei test del primo lotto); **lo spaccato per giorno di V-013
e V-014 non l'ho mai guardato**. È però una scelta fatta dopo aver visto lo schema in altre varianti: lo dichiaro.
**Concorrenti specifiche:** 18-1 V-013 (+−0,025 R) e V-014 (−0,156 R) erano negativi: togliere il fine settimana può
non bastare (previsione di questa spiegazione: R medio ancora sotto zero).
- **V-035** · 1h · long · F6 solo feriali · E10 · M · S1 1,5 × ATR · U1 2 R e U2s (stima 296).
- **V-036** · la stessa, short (stima 268).
Previsione: long fra −0,05 e +0,15 R, short fra −0,2 e 0; non superano.

**Esito (17 ottobre).** V-035 +0,012 R (p 0,067), V-036 −0,098 R (p 0,485): non superano, come previsto. Togliere il
fine settimana non salva la rottura del range asiatico.

### I-19 — Un eccesso con volume alto che rientra subito è liquidità, non informazione: torna indietro

**Fonti.** Campbell, Grossman, Wang, «Trading Volume and Serial Correlation in Stock Returns», Quarterly Journal of
Economics 108(4), 1993: i movimenti accompagnati da volume alto (domanda di liquidità, non informazione) tendono a
tornare indietro, e chi fornisce liquidità è pagato da questo ritorno; Caporale, Plastun, CESifo WP 7917, 2019: per BTC
gli eccessi verso l'alto sono seguiti da un ritorno indietro. **Affermazione:** quando una candela oraria torna dentro le
bande di Bollinger dopo una chiusura fuori, **con volume oltre 1,5 volte la media**, il prezzo nelle 12 ore seguenti
continua a tornare verso la media più del caso. La differenza con I-06 (V-015, V-016) è il volume alto, che secondo la
fonte separa la liquidità dall'informazione; qui l'ingresso è a mercato e senza filtro. Per lo short le due fonti
dicono la stessa cosa; per il long si contraddicono (Caporale e Plastun: dopo gli eccessi verso il basso BTC continua a
scendere). **Concorrenti specifiche:** 19-1 il ritorno verso la media è già andato male due volte (I-06): previsione di
questa spiegazione, R negativo; 19-2 il volume alto al rientro misura la fine di una cascata di liquidazioni, che è
proprio il caso della fonte.
- **V-037** · 1h · short · E5 ritorno da Bollinger k 2,0 · C1 volume relativo 1,5 · M · S1 1,5 × ATR · U1 1,5 R e U2
  12 candele (stima 150).
- **V-038** · la stessa, long (stima 233).
Previsione: short fra −0,1 e +0,15 R; long fra −0,2 e +0,05 R; non superano.

**Esito (17 ottobre).** V-037 −0,141 R (p 0,696), V-038 −0,229 R (p 0,990): non superano. V-038 fa peggio del caso
con chiarezza: dopo un eccesso al ribasso con volume alto, anche se la candela rientra nelle bande, BTC ha continuato a
scendere. È coerente con Caporale e Plastun (momento dopo gli eccessi al ribasso) e contro Campbell, Grossman e Wang.

### I-20 — Asimmetria degli eccessi in BTC: al ribasso continuano, al rialzo no (gli ultimi due tentativi)

**Fonte.** Caporale, Plastun, «Momentum effects in the cryptocurrency market after one-day abnormal returns», CESifo
Working Paper 7917, 2019 (Financial Markets and Portfolio Management, 2020): dopo un movimento anomalo i prezzi di BTC
continuano nella stessa direzione, **tranne dopo gli eccessi al rialzo**, che tornano indietro. La previsione era già
scritta in I-03 prima di qualunque test; V-038 la rende più interessante, e lo dichiaro: è anche un'idea nata vedendo un
risultato. **Affermazione:** una chiusura oraria sotto la banda di Bollinger inferiore (k 2,0) con volume oltre 2 volte
la media è seguita, nelle 24 ore, da un ribasso maggiore del caso (short); la stessa regola al rialzo **non** dà un
vantaggio. Le due varianti mettono alla prova insieme la continuazione e l'asimmetria. **Concorrenti:** 20-1 è I-08 senza
il filtro della calma e con il volume: le rotture delle bande senza filtro potrebbero non valere niente; 20-2 nel 2022 i
ribassi con volume sono la tendenza di fondo (A2).
- **V-039** · 1h · short · E4 rottura di Bollinger k 2,0 · C1 volume relativo 2,0 · M · S1 1,5 × ATR · U1 2 R e U2 24
  candele (stima 433).
- **V-040** · la stessa, long (stima 419).
Previsione: short fra −0,05 e +0,15 R, long fra −0,2 e 0 R; non superano.

## Piano dei tentativi

Primo lotto: 19 varianti (V-001 … V-019), una per riga, in quest'ordine. Restano 21 tentativi per la Fase 3 (filtri
nati dai fallimenti) e per famiglie del catalogo non ancora provate (stocastico, MACD, sessioni, giorno della settimana,
VWAP). Non aggiungo filtri a una variante prima di averne registrato il risultato.
