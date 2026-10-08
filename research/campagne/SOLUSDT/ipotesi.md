# SOLUSDT — Ipotesi (Fase 1)

Scritte l'8 ottobre 2026 PRIMA di qualunque test di variante. Ogni idea ha fonte pubblicata
prima del 2024-01-01, affermazione falsificabile, sotto-domande, almeno 10 spiegazioni
concorrenti con la loro previsione e cosa le smentirebbe, l'ipotesi completa e TUTTE le varianti
con il loro motivo. Il codice di ogni variante è in `codice/varianti.py` (stesso id).

## Regole comuni a tutte le varianti

* Moneta SOLUSDT, periodo di costruzione 2020-09-01 → 2022-12-30 (Fase 0), serie e filtro dei
  mesi sotto la liquidità minima come in `fase0_dati.md`.
* Una sola direzione per variante. Segnale alla chiusura della barra, ingresso all'apertura della
  barra dopo. Una posizione alla volta.
* «ATR(n)» è l'Average True Range di Wilder su n barre; «σ» la deviazione standard dei rendimenti
  close-su-close delle barre indicate. Lo stop e il target si calcolano dal close della barra di
  segnale. «Uscita a tempo dopo N barre»: chiusura all'apertura della barra successiva alla N-esima
  barra tenuta. Ogni variante ha anche lo stop; il riempimento intra-barra è «stop prima».
* Riscaldamento: nessun segnale finché tutti gli indicatori della variante non sono calcolabili.
* Costo di un giro (commissione 0,05% + slippage 0,01% per lato, andata e ritorno: 0,12% del
  nozionale) in R = 0,12% / distanza dello stop. Ordini di grandezza attesi per SOL (non misurati
  sui risultati): stop di 2 ATR a 1d circa 12–16% → 0,01 R; a 4h circa 4–6% → 0,02–0,03 R; a 1h
  circa 2–4% → 0,03–0,06 R; a 30m circa 1,5–2,5% → 0,05–0,08 R. Più il funding (in media vicino
  a zero, ma con giorni estremi nel novembre 2022). Le previsioni sotto sono al netto dei costi.
* Bot: stop oltre il 6% non eseguibile così com'è (`stop_massimo_bot`), orizzonte del bot 96 barre;
  lo si dichiara per ogni candidato, non cambia le regole.
* Spiegazioni concorrenti «noiose» presenti in ogni idea (numerate N1–N5), con la stessa
  previsione e la stessa smentita:
  - **N1 Caso.** L'effetto è rumore: previsione t contro la (b) sotto la soglia; smentita: t sopra
    la soglia anche in validazione.
  - **N2 Trend di fondo.** SOL è salita di circa 100 volte nel 2021 ed è scesa del 94% nel 2022:
    ogni long del 2021 e ogni short del 2022 guadagna. Previsione: la variante non batte la (b),
    che entra a caso nella stessa direzione; R per anno con lo stesso segno del buy and hold.
    Smentita: battere nettamente la (b) e un R positivo anche nell'anno contrario.
  - **N3 È solo il mercato (BTC).** SOL segue BTC: l'effetto è quello di BTC. Previsione: lo stesso
    segnale calcolato su BTC dà lo stesso risultato. Smentita: effetto che dipende da qualcosa di
    proprio di SOL (si guarda solo se la variante diventa candidato).
  - **N4 Volatilità.** I segnali cadono in periodi più volatili, dove lo stop in ATR è più largo e
    l'R per trade cambia scala. Previsione: l'R medio si spiega con il livello di ATR. Smentita: la
    (b), che usa lo stesso calcolo di stop, non ha lo stesso R.
  - **N5 Costi e dati.** Il vantaggio lordo esiste ma i costi lo mangiano, o nasce da buchi o
    candele anomale. Previsione: R lordo positivo e netto vicino a zero; trade concentrati vicino ai
    buchi della Fase 0. Smentita: R netto positivo anche a costi doppi e senza i 3 trade migliori.

Per ogni idea sotto si aggiungono almeno cinque spiegazioni specifiche (S1…), così ognuna ha
almeno 10 spiegazioni concorrenti.

---

## I-01 — Momentum della serie (time-series momentum)

1. **Fonti.** T. J. Moskowitz, Y. H. Ooi, L. H. Pedersen, «Time series momentum», *Journal of
   Financial Economics* 104(2), maggio 2012. Y. Liu, A. Tsyvinski, «Risks and Returns of
   Cryptocurrency», NBER Working Paper 24877, agosto 2018 (poi *Review of Financial Studies* 34(6),
   2021): nel crypto il rendimento delle ultime 1–4 settimane prevede quello delle settimane dopo.
2. **Affermazione.** Se il rendimento di SOL degli ultimi 7 giorni è positivo, il rendimento dei
   7 giorni successivi è in media più alto di quello di un ingresso long a caso con la stessa
   uscita; se è negativo, quello successivo è più basso (vantaggio per lo short).
3. **Sotto-domande.** Vale di più dopo movimenti grandi o anche dopo +1%? Dipende dalla volatilità
   (nelle fasi calme il momentum è più debole)? Chi muove il prezzo: investitori che arrivano in
   ritardo inseguendo il rendimento passato (attenzione, notizie lente), trend follower
   sistematici. In quanto tempo: settimane, quindi candele giornaliere.
4. **Spiegazioni concorrenti.** N1–N5, più:
   - S1 *Il momentum è solo il 2021*: previsione R positivo nel 2021 e nullo o negativo nel 2022
     (long); smentita: R positivo in entrambi.
   - S2 *Inversione a breve*: dopo una settimana forte il prezzo torna indietro; previsione R
     negativo contro la (b); smentita: R sopra la (b).
   - S3 *Rumore delle soglie*: con la soglia a 0 metà dei segnali sono quasi casuali; previsione
     effetto concentrato nei rendimenti grandi; smentita: (si vede solo in Fase 3).
   - S4 *Stop largo*: con 2 ATR giornalieri lo stop scatta raramente e la variante è quasi un
     «compra e tieni 7 giorni»; previsione: pochissimi stop; smentita: molti stop.
   - S5 *Funding*: nelle fasi di momentum positivo il funding è alto e mangia i long; previsione
     costi di funding visibili nei long; smentita: funding trascurabile.
5. **Ipotesi completa.** SOLUSDT, momentum della serie su 7 giorni, timeframe 1d (il meccanismo è
   di settimane), una variante per direzione.
6. **Varianti.**
   - **SOLUSDT-001** (1d, long): rendimento close-su-close degli ultimi 7 giorni > 0; stop 2 ATR(14)
     sotto il close; nessun target; uscita a tempo dopo 7 barre (l'orizzonte di una settimana della
     fonte). Motivo: la versione diretta della fonte.
   - **SOLUSDT-002** (1d, short): rendimento degli ultimi 7 giorni < 0; stop 2 ATR(14) sopra; uscita
     dopo 7 barre. Motivo: stessa idea, direzione opposta (Moskowitz et al. usano entrambe).
   - Solo se una delle due è `scarto` per trade insufficienti: **SOLUSDT-001b / 002b**, identiche ma
     con uscita dopo 3 barre (la fonte trova l'effetto già dalla prima settimana; posizioni più corte
     = più ingressi). Motivo: raggiungere i trade minimi senza aver visto risultati.
   - Previsione (001): R medio fra 0 e +0,15, t contro la (b) fra 0 e 2. (002): R medio fra −0,1 e
     +0,1. Criterio di successo: battere nettamente (a) e (b) con R medio positivo.

## I-02 — Rottura del canale (sistema delle tartarughe)

1. **Fonti.** M. Covel, «The Complete TurtleTrader», HarperCollins, 2007; C. Faith, «Way of the
   Turtle», McGraw-Hill, 2007. Sistema 1: ingresso sulla rottura del massimo (minimo) delle ultime
   20 barre, uscita sulla rottura opposta delle ultime 10, stop a 2 N (N = ATR di 20 barre).
2. **Affermazione.** Dopo una chiusura sopra il massimo delle 20 barre precedenti il prezzo continua
   nella stessa direzione abbastanza da dare un R medio sopra quello di ingressi casuali con la
   stessa uscita (simmetrico per lo short).
3. **Sotto-domande.** Funziona nei regimi di trend e perde nei laterali? Quante rotture sono false?
   Chi compra la rottura: trend follower, stop degli short sopra i massimi, nuovi acquirenti
   attratti dai massimi. Tempo: giorni.
4. **Spiegazioni concorrenti.** N1–N5, più: S1 *Falsi segnali nei laterali* (previsione: perdite
   concentrate nei mesi senza trend; smentita: perdite distribuite); S2 *Stop degli short*
   (previsione: rotture con volume alto vanno meglio; smentita: nessuna differenza); S3 *Uscita
   lenta* (previsione: grandi guadagni restituiti, R medio basso con win rate basso; smentita: R
   tenuto); S4 *Rottura = volatilità alta* (previsione: R spiegato dall'ATR; smentita: (b) diversa);
   S5 *Pochi trend enormi* (previsione: senza i 3 migliori l'R va sotto la (b); smentita: resta
   sopra).
5. **Ipotesi completa.** SOLUSDT, rottura del canale di 20 barre, timeframe 4h. Il sistema
   originale è a 1d, ma a 1d le rotture di 20 giorni in circa due anni utili sono poche decine:
   il meccanismo (ordini sopra i massimi recenti) non dipende dalla scala; 4h è il timeframe più
   lento con una frequenza plausibile.
6. **Varianti.**
   - **SOLUSDT-003** (4h, long): close > massimo degli high delle 20 barre precedenti; stop 2 ATR(20)
     sotto il close; uscita («chiudi») quando il close scende sotto il minimo dei low delle 10 barre
     precedenti. Previsione: R medio fra −0,05 e +0,25, win rate sotto 45%.
   - **SOLUSDT-004** (4h, short): speculare. Previsione: R medio fra −0,1 e +0,2.

## I-03 — Incrocio con la media mobile (regola a tenuta fissa)

1. **Fonte.** W. Brock, J. Lakonishok, B. LeBaron, «Simple Technical Trading Rules and the
   Stochastic Properties of Stock Returns», *Journal of Finance* 47(5), dicembre 1992: dopo
   l'incrocio del prezzo sopra la media mobile lunga (con banda dell'1%) i 10 giorni seguenti
   rendono più della media.
2. **Affermazione.** Dopo un incrocio del close sopra la media mobile di 50 barre con margine
   dell'1%, i 10 giorni successivi rendono più di ingressi long casuali con la stessa uscita.
3. **Sotto-domande.** L'incrocio cattura l'inizio dei trend o arriva tardi? La banda dell'1% basta a
   filtrare i falsi incroci? Chi compra: i trend follower che usano le stesse medie.
4. **Spiegazioni concorrenti.** N1–N5, più: S1 *Arriva tardi* (previsione: R negativo dopo
   l'ingresso; smentita: positivo); S2 *Incroci multipli nei laterali* (previsione: perdite in
   grappoli; smentita: no); S3 *Effetto 2021* (previsione: R positivo solo nel 2021); S4 *Tenuta
   fissa troppo lunga* (previsione: buona prima metà, restituita nella seconda; si vede in Fase 3);
   S5 *Equivale al momentum di I-01* (previsione: stessi giorni di I-01; smentita: ingressi diversi).
5. **Ipotesi completa.** SOLUSDT, incrocio sopra la media di 50 barre a 4h (circa 8 giorni: la
   media di 50 giorni a 1d darebbe pochi incroci in due anni), tenuta di 10 giorni come nella fonte.
6. **Varianti.**
   - **SOLUSDT-005** (4h, long): close[i−1] ≤ 1,01 × SMA50[i−1] e close[i] > 1,01 × SMA50[i];
     stop 3 ATR(14) sotto (lo stop è solo di emergenza: la fonte non ne ha); uscita dopo 60 barre
     (10 giorni). Previsione: R medio fra −0,05 e +0,2. Una sola variante: il lato short del trend è
     già in I-01 e I-02.

## I-04 — RSI a 2 periodi sopra la media di 200 (Connors)

1. **Fonte.** L. Connors, C. Alvarez, «Short Term Trading Strategies That Work», TradingMarkets
   Publishing, 2008: compra quando il prezzo è sopra la media di 200 e l'RSI(2) è sotto 5, esci
   quando il close supera la media di 5; speculare per lo short.
2. **Affermazione.** In un trend rialzista (close sopra la media di 200 barre) un eccesso di vendita
   a brevissimo (RSI(2) < 5) rientra: il prezzo torna sopra la media di 5 con un R medio più alto
   di quello di ingressi casuali con la stessa uscita.
3. **Sotto-domande.** Funziona solo in trend? Quanto profondo è il ritracciamento che si rimbalza
   e quanto spesso diventa un crollo? Chi compra: chi offre liquidità a chi vende in fretta.
4. **Spiegazioni concorrenti.** N1–N5, più: S1 *Coltello che cade* (previsione: le perdite grandi
   sono le giornate di crollo, R molto negativo nel 2022); S2 *Rimbalzo meccanico* (ogni uscita
   alla media di 5 è facile dopo un calo: previsione win rate alto anche per la (b)? no: la (b)
   entra a caso, quindi win rate più basso; smentita: stesso win rate della (b)); S3 *Effetto
   2021* (previsione: tutto il guadagno nel 2021); S4 *Asimmetria* (molti piccoli guadagni e
   poche grandi perdite: previsione R medio vicino a zero); S5 *Costi* (trade brevi: costi alti in R).
5. **Ipotesi completa.** SOLUSDT, eccesso di breve in trend, timeframe 4h (a 1d con 200 giorni di
   riscaldamento resterebbero poche decine di segnali).
6. **Varianti.**
   - **SOLUSDT-006** (4h, long): close > SMA200 e RSI(2) < 5; uscita («chiudi») quando close >
     SMA5; stop 3 ATR(14) sotto (di emergenza: la fonte non ne usa). Previsione: R medio fra −0,05
     e +0,15, win rate sopra 60%.
   - **SOLUSDT-007** (4h, short): close < SMA200 e RSI(2) > 95; uscita quando close < SMA5; stop 3
     ATR(14) sopra. Previsione: R medio fra −0,1 e +0,1.

## I-05 — Inversione dopo un movimento estremo (fornitura di liquidità)

1. **Fonti.** B. N. Lehmann, «Fads, Martingales, and Market Efficiency», *Quarterly Journal of
   Economics* 105(1), febbraio 1990; S. Nagel, «Evaporating Liquidity», *Review of Financial
   Studies* 25(7), luglio 2012: l'inversione a breve è il compenso di chi fornisce liquidità ed è
   più grande quando la liquidità scarseggia.
2. **Affermazione.** Dopo una barra di 1h con rendimento oltre 3 σ (σ dei rendimenti di 1h delle
   168 barre precedenti) il prezzo recupera una parte del movimento nelle 6 ore dopo: un ingresso
   contro il movimento ha R medio sopra quello di ingressi casuali nella stessa direzione.
3. **Sotto-domande.** Vale per i crolli (liquidazioni a catena) più che per i rialzi? Vale di più
   quando BTC non si è mosso (shock solo di SOL)? Chi compra: market maker e arbitraggisti. Tempo:
   ore.
4. **Spiegazioni concorrenti.** N1–N5, più: S1 *Notizia vera* (il movimento è informazione e
   continua; previsione R negativo); S2 *Liquidazioni a catena che continuano* (previsione perdite
   grandi nei giorni di crollo); S3 *Rimbalzo del rumore delle candele* (prezzo medio: previsione
   effetto solo nella prima barra); S4 *Volatilità che resta alta* (stop colpiti spesso; previsione
   molti stop); S5 *Pochi eventi* (previsione: pochi trade estremi fanno tutto l'R).
5. **Ipotesi completa.** SOLUSDT, inversione dopo movimenti estremi di 1h, timeframe 1h.
6. **Varianti.**
   - **SOLUSDT-008** (1h, long): rendimento della barra < −3 σ(168, barre precedenti); stop 2
     ATR(14) sotto; uscita dopo 6 barre. Previsione: R medio fra −0,1 e +0,1.
   - **SOLUSDT-009** (1h, short): rendimento > +3 σ; stop 2 ATR(14) sopra; uscita dopo 6 barre.
     Previsione: R medio fra −0,15 e +0,05.

## I-06 — Inversione dei movimenti con volume alto

1. **Fonte.** J. Y. Campbell, S. J. Grossman, J. Wang, «Trading Volume and Serial Correlation in
   Stock Returns», *Quarterly Journal of Economics* 108(4), novembre 1993: le variazioni di prezzo
   accompagnate da volume alto tendono a invertirsi (pressione di liquidità), più di quelle a
   volume basso.
2. **Affermazione.** Una barra di 4h in calo oltre 2 σ (σ dei rendimenti di 4h delle 90 barre
   precedenti) con volume oltre il doppio della media delle 42 barre precedenti è seguita da un
   recupero nella giornata dopo: long con R medio sopra la (b).
3. **Sotto-domande.** Il volume distingue la vendita forzata dalla notizia? Vale anche in trend
   ribassista forte? Tempo: un giorno.
4. **Spiegazioni concorrenti.** N1–N5, più: S1 *Volume = notizia* (previsione: continua al ribasso);
   S2 *Uguale a I-05* (previsione: stessi giorni; smentita: ingressi diversi); S3 *Effetto 2022* (i
   crolli del 2022 continuano: previsione R negativo nel 2022); S4 *Volume in moneta base* (quando
   il prezzo scende lo stesso controvalore è più volume: previsione segnali concentrati nei cali
   forti; nota di misura); S5 *Rimbalzo tecnico generale* (anche senza volume: si confronta con la (a)).
5. **Ipotesi completa.** SOLUSDT, inversione al rialzo dopo cali forti con volume alto, 4h.
6. **Varianti.**
   - **SOLUSDT-010** (4h, long): rendimento < −2 σ(90) e volume > 2 × media del volume delle 42
     barre precedenti; stop 2 ATR(14) sotto; uscita dopo 6 barre. Previsione: R medio fra −0,1 e
     +0,15. Una sola variante: il lato short (rialzo con volume) è meno sostenuto dalla fonte.

## I-07 — Compressione della volatilità e rottura (NR7)

1. **Fonte.** T. Crabel, «Day Trading with Short Term Price Patterns and Opening Range Breakout»,
   Traders Press, 1990: la barra con l'escursione più stretta delle ultime 7 (NR7) precede
   un'espansione; si entra nella direzione della rottura.
2. **Affermazione.** Quando la barra dopo una NR7 chiude sopra il massimo della NR7, il prezzo
   continua al rialzo abbastanza da dare un R medio sopra la (b) con stop al minimo della NR7
   (speculare per lo short).
3. **Sotto-domande.** L'espansione ha una direzione prevedibile o è solo volatilità? La rottura
   alla chiusura arriva tardi? Chi muove: ordini accumulati ai bordi del range.
4. **Spiegazioni concorrenti.** N1–N5, più: S1 *Espansione senza direzione* (previsione R come la
   (b)); S2 *Stop stretto* (stop al minimo della NR7: molti stop e R di scala diversa; previsione
   win rate basso); S3 *Leva al tetto* (stop vicino = nozionale al tetto: trade ridotti); S4
   *Rottura falsa* (previsione: ritorno nel range nelle prime barre); S5 *Ore calme* (le NR7 cadono
   di notte/weekend: previsione effetto legato all'ora).
5. **Ipotesi completa.** SOLUSDT, NR7 e rottura confermata alla chiusura, 4h.
6. **Varianti.**
   - **SOLUSDT-011** (4h, long): la barra i−1 è NR7 (high−low minimo fra le 7 barre i−7…i−1) e
     close[i] > high[i−1]; stop = low[i−1]; uscita dopo 6 barre. Previsione: R medio fra −0,1 e +0,1.
   - **SOLUSDT-012** (4h, short): NR7 in i−1 e close[i] < low[i−1]; stop = high[i−1]; uscita dopo 6
     barre. Previsione: R medio fra −0,1 e +0,1.

## I-08 — Effetto del giorno della settimana (lunedì)

1. **Fonte.** G. M. Caporale, A. Plastun, «The day of the week effect in the cryptocurrency
   market», *Finance Research Letters* 31, dicembre 2019: per Bitcoin rendimenti anomali positivi
   il lunedì.
2. **Affermazione.** Il rendimento di SOL del lunedì (00:00–24:00 UTC) è in media più alto di quello
   di un giorno a caso con la stessa uscita.
3. **Sotto-domande.** Chi compra il lunedì: flussi che riprendono dopo il weekend (istituzionali,
   borse tradizionali aperte), notizie accumulate. Tempo: un giorno.
4. **Spiegazioni concorrenti.** N1–N5, più: S1 *Effetto solo di BTC* (previsione: assente su SOL);
   S2 *Pochi lunedì estremi* (previsione: senza i 3 migliori sparisce); S3 *Effetto nato e morto prima
   del 2020* (previsione: assente); S4 *Volatilità del lunedì più alta* (previsione: R medio spiegato
   da ATR); S5 *Data mining della fonte* (fra 7 giorni uno esce per caso: previsione nessun effetto).
5. **Ipotesi completa.** SOLUSDT, lunedì, 1d long.
6. **Varianti.**
   - **SOLUSDT-013** (1d, long): segnale alla chiusura della barra della domenica, ingresso
     all'apertura del lunedì, uscita dopo 1 barra; stop 2 ATR(14). Previsione: R medio fra −0,05 e
     +0,1. Una sola variante: la fonte non indica un lato short.

## I-09 — Momentum dentro la giornata (prima mezz'ora → ultima mezz'ora)

1. **Fonti.** L. Gao, Y. Han, S. Z. Li, G. Zhou, «Market intraday momentum», *Journal of Financial
   Economics* 129(2), agosto 2018; D. Shen, A. Urquhart, P. Wang, «Bitcoin intraday time series
   momentum», *The Financial Review* 57(2), 2022 (DOI 10.1111/fire.12290): per Bitcoin il rendimento
   della prima mezz'ora prevede quello dell'ultima, spinto dalla fornitura di liquidità.
2. **Affermazione.** Se la prima mezz'ora della giornata UTC (00:00–00:30) chiude in rialzo,
   l'ultima mezz'ora (23:30–24:00) rende più di una mezz'ora a caso con la stessa uscita (long);
   se chiude in calo, l'ultima rende meno (short). Adattamento dichiarato: Shen et al. definiscono
   la «giornata» col volume; qui si usa il confine UTC, quello delle candele giornaliere di Binance.
3. **Sotto-domande.** Vale di più nei giorni volatili? Il confine UTC è quello giusto per SOL? Chi
   muove: chi ribilancia a fine giornata, liquidità.
4. **Spiegazioni concorrenti.** N1–N5, più: S1 *Confine sbagliato* (previsione: nessun effetto a
   UTC); S2 *Costi* (mezz'ora: costi circa 0,06 R; previsione R lordo positivo e netto negativo); S3
   *Funding a mezzanotte* (il settlement delle 00:00 cade all'uscita: previsione costi di funding
   negli short del 2021); S4 *Effetto di BTC* (previsione: sparisce controllando BTC); S5 *Giorni
   di notizie* (previsione: pochi giorni estremi).
5. **Ipotesi completa.** SOLUSDT, momentum intragiornaliero, 30m.
6. **Varianti.**
   - **SOLUSDT-014** (30m, long): alla chiusura della barra 23:00–23:30, se close(00:00–00:30 dello
     stesso giorno) > open(00:00); ingresso alle 23:30, uscita dopo 1 barra; stop 2 ATR(14).
     Previsione: R medio fra −0,1 e +0,05.
   - **SOLUSDT-015** (30m, short): stessa ora, se la prima mezz'ora chiude sotto l'apertura.
     Previsione: R medio fra −0,1 e +0,05.

## I-10 — Funding alto e affollamento dei long

1. **Fonte.** M. Schmeling, A. Schrimpf, K. Todorov, «Crypto carry», BIS Working Paper 1087,
   aprile 2023: il carry (premio dei futures sullo spot) nel crypto è spinto da piccoli investitori
   che inseguono il trend con leva, e un carry alto prevede crolli e liquidazioni successive.
2. **Affermazione.** Quando la media degli ultimi 3 tassi di funding di SOL supera lo 0,05% per
   settlement (5 volte il tasso base), il giorno dopo SOL rende meno di un ingresso a caso: short
   con R medio sopra la (b). Speculare: funding molto negativo (short affollati) → rimbalzo.
3. **Sotto-domande.** Quanto deve essere alto il funding? Il crollo arriva entro un giorno o dopo?
   Chi vende: i long a leva liquidati. Il funding incassato dallo short aiuta (è un incasso).
4. **Spiegazioni concorrenti.** N1–N5, più: S1 *Funding alto = trend forte che continua*
   (previsione: R dello short negativo); S2 *Incasso del funding* (previsione: R lordo nullo, netto
   positivo solo per il funding); S3 *Pochi episodi* (previsione: pochi trade, in grappoli nello
   stesso mese); S4 *Effetto di tutto il mercato* (funding alto ovunque nello stesso momento);
   S5 *Ritardo* (il crollo arriva dopo più giorni: previsione nessun effetto entro 1 giorno).
5. **Ipotesi completa.** SOLUSDT, funding estremo, timeframe 8h (allineato ai settlement: il tasso
   di un settlement è noto alla chiusura della barra che lo contiene).
6. **Varianti.**
   - **SOLUSDT-016** (8h, short): media dei 3 ultimi tassi di funding con istante ≤ chiusura della
     barra > +0,0005; stop 2 ATR(14) sopra; uscita dopo 3 barre (1 giorno). Previsione: R medio
     fra −0,1 e +0,2.
   - **SOLUSDT-017** (8h, long): media dei 3 ultimi tassi < −0,0005; stop 2 ATR(14) sotto; uscita
     dopo 3 barre. Previsione: R medio fra −0,1 e +0,2.

## I-11 — BTC guida, SOL segue (lead-lag)

1. **Fonte.** K. Hou, «Industry Information Diffusion and the Lead-lag Effect in Stock Returns»,
   *Review of Financial Studies* 20(4), luglio 2007: le notizie comuni arrivano prima nei titoli
   grandi e si diffondono con ritardo nei piccoli.
2. **Affermazione.** Quando BTC sale in un'ora più di 2 σ (σ dei rendimenti di 1h di BTC delle 168
   barre precedenti) e SOL nella stessa ora è salita meno di BTC, SOL recupera nelle 3 ore dopo:
   long con R medio sopra la (b). Speculare per lo short.
3. **Sotto-domande.** In crypto la diffusione è di minuti: un'ora basta ancora? Vale nei giorni di
   notizie macro? Chi muove: arbitraggisti fra monete, algoritmi che seguono BTC.
4. **Spiegazioni concorrenti.** N1–N5, più: S1 *Diffusione già finita* (previsione: R come la (b));
   S2 *Divergenza vera* (SOL debole per motivi suoi: previsione continua a sottoperformare); S3
   *Inversione di BTC* (dopo +2 σ BTC torna giù e SOL con lui: previsione R negativo); S4 *Beta*
   (SOL ha beta > 1: previsione segnali rari); S5 *Volatilità* (stop in grappoli).
5. **Ipotesi completa.** SOLUSDT, ritardo rispetto a BTC, 1h.
6. **Varianti.**
   - **SOLUSDT-018** (1h, long): rendimento di BTC della barra > 2 σ_BTC(168) e rendimento di SOL della
     barra < rendimento di BTC; stop 2 ATR(14) sotto; uscita dopo 3 barre. Previsione: R medio fra
     −0,1 e +0,1.
   - **SOLUSDT-019** (1h, short): BTC < −2 σ_BTC e SOL > rendimento di BTC (è scesa meno); stop 2
     ATR(14) sopra; uscita dopo 3 barre. Previsione: R medio fra −0,1 e +0,1.

## I-12 — Premio dei giorni di volume alto

1. **Fonte.** S. Gervais, R. Kaniel, D. H. Mingelgrin, «The High-Volume Return Premium», *Journal of
   Finance* 56(3), giugno 2001: dopo un giorno di volume insolitamente alto (decile più alto dei 50
   giorni precedenti) il prezzo sale nei giorni seguenti (più attenzione, più acquirenti).
2. **Affermazione.** Dopo un giorno con volume sopra il 90° percentile dei 49 giorni precedenti SOL
   rende nei 5 giorni dopo più di un ingresso long a caso.
3. **Sotto-domande.** Conta il segno del rendimento del giorno? Attenzione o notizia? Tempo: giorni.
4. **Spiegazioni concorrenti.** N1–N5, più: S1 *Volume = capitolazione* (previsione: R negativo dopo
   i giorni di crollo); S2 *Volume in moneta base* (nei cali più monete per lo stesso controvalore:
   segnali sbilanciati sui cali); S3 *Effetto 2021*; S4 *Pochi segnali*; S5 *Volume di
   liquidazioni* (previsione: segnali nei crolli del 2022, R negativo).
5. **Ipotesi completa.** SOLUSDT, volume giornaliero insolito, 1d long.
6. **Varianti.**
   - **SOLUSDT-020** (1d, long): volume della barra > 90° percentile del volume delle 49 barre
     precedenti; stop 2 ATR(14) sotto; uscita dopo 5 barre. Previsione: R medio fra −0,1 e +0,15.
     Una sola variante.

## I-13 — Numeri tondi e ordini di stop (Osler)

1. **Fonte.** C. L. Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation for the
   Predictive Success of Technical Analysis», *Journal of Finance* 58(5), ottobre 2003: gli ordini
   stop-loss si accumulano appena oltre i numeri tondi, e attraversarli accelera il movimento.
2. **Affermazione.** Quando il close di 1h attraversa al rialzo un livello tondo, le 4 ore dopo
   rendono più di un ingresso long a caso (gli stop degli short appena sopra spingono il prezzo);
   speculare al ribasso. Livello tondo: multiplo di 5 × 10^(k−1) con k = parte intera di log10 del
   close precedente (sotto 10 USDT: multipli di 0,5; da 10 a 100: multipli di 5; da 100 in su: di 50).
3. **Sotto-domande.** I numeri tondi contano per SOL come per le valute? Contano più i livelli
   «grandi» (10, 50, 100)? Tempo: ore.
4. **Spiegazioni concorrenti.** N1–N5, più: S1 *Gli ordini take-profit ai tondi* (inversione:
   previsione R negativo); S2 *Attraversamento = momentum di 1h* (previsione: come qualsiasi barra in
   rialzo); S3 *Scala dei livelli arbitraria* (previsione: nessuna differenza con livelli spostati);
   S4 *Pochi livelli a prezzi alti* (sopra 100 solo multipli di 50: pochi segnali nel 2021 alto);
   S5 *Volatilità*.
5. **Ipotesi completa.** SOLUSDT, attraversamento dei numeri tondi, 1h.
6. **Varianti.**
   - **SOLUSDT-021** (1h, long): close[i−1] < L ≤ close[i] per un livello tondo L (passo calcolato
     dal close[i−1]); stop 2 ATR(14) sotto; uscita dopo 4 barre. Previsione: R medio fra −0,1 e +0,1.
   - **SOLUSDT-022** (1h, short): close[i−1] > L ≥ close[i]; stop 2 ATR(14) sopra; uscita dopo 4
     barre. Previsione: R medio fra −0,1 e +0,1.

---

## Criterio di successo (uguale per tutte)

Battere nettamente la baseline (a) e la (b) con `contro_baseline` sul periodo di costruzione, con
R medio dopo i costi positivo (sezione 8). Altrimenti la variante non è un vantaggio.

## Idee viste e scartate prima di scriverle

* Nessuna idea è stata scelta «perché so che ha funzionato» dopo il 2023 (regola 8).
* Il controllo positivo (voce SOLUSDT-N006) ha mostrato per caso che a 1h, dopo una barra in rialzo,
  la barra dopo va un po' meglio dell'ingresso casuale. Non è diventata un'idea: nessuna variante
  qui sopra usa la sola direzione della barra precedente.
