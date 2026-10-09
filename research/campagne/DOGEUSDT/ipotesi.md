# Ipotesi della campagna DOGEUSDT

Scritte prima di qualunque test (Fase 1). Ogni idea ha la sua fonte (pubblicata prima del
2024-01-01), l'affermazione falsificabile, le sotto-domande, almeno 10 spiegazioni concorrenti
con la previsione che fanno e cosa le smentirebbe, e tutte le varianti con il loro motivo.
Fonti verificate il 9 ottobre 2026 su pagine di editori e archivi universitari.

Periodi (dal log, calcolati con `periodi_campagna`): costruzione 2020-07-01 → 2022-12-12,
validazione 2022-12-13 → 2023-12-31.

Regole comuni a tutte le varianti, decise prima dei test:

* serie dei segnali: last price; stop sul last; liquidazione sul mark (motore della sezione 7);
* ingresso all'apertura della barra dopo il segnale; una posizione alla volta;
* stop e target in multipli dell'ATR di Wilder a 14 barre del timeframe della variante,
  calcolati sulla chiusura della barra del segnale;
* nessun ingresso su segnali di barre dei mesi sotto la liquidità minima (Fase 0);
* «uscita a tempo dopo H barre» vuol dire: alla chiusura della H-esima barra tenuta la
  strategia chiede di chiudere, e la chiusura avviene all'apertura della barra dopo;
* lo stop massimo del bot (6% del prezzo) non si impone: si conta e si dichiara. Su DOGEUSDT
  l'ATR giornaliero è spesso sopra il 5%: le varianti a 12h e 1d con stop in ATR il bot non
  le può eseguire così come sono (lo dice `lezioni/metodo.md`), e lo si dichiara;
* costo di un giro (commissioni 0,05% e slippage 0,02% per lato): 0,14% del nozionale. In R
  vale 0,14% diviso la distanza dello stop: con stop a 2 ATR è circa 0,05 R a 1 ora
  (ATR orario circa 1,2-1,5%), 0,03 R a 4 ore, 0,01-0,02 R a 1 giorno, 0,10-0,15 R a 30 minuti
  (stime a occhio sull'ordine di grandezza della volatilità di DOGE, non misurate). Le
  previsioni sono scritte al netto di questo costo.

## Spiegazioni concorrenti comuni (valgono per ogni idea)

Ogni idea qui sotto ha queste otto spiegazioni concorrenti, più almeno due sue.

| # | Spiegazione | Previsione | Cosa la smentisce |
|---|---|---|---|
| C1 | Caso: l'effetto è rumore | R medio non distinguibile dalla (b); `t` contro la (b) vicino a zero | `t` contro la (b) oltre la soglia, e segno uguale in più anni |
| C2 | Trend di fondo: DOGE è salita moltissimo fra fine 2020 e metà 2021 e scesa nel 2022; una variante long (short) guadagna solo perché entra in quel periodo | la (b) nella stessa direzione ha R medio simile; R per anno segue il buy and hold | il candidato batte nettamente la (b), che entra a caso nella stessa direzione e periodo |
| C3 | È solo il mercato: DOGE segue BTC, e la condizione seleziona momenti in cui BTC si muove a favore | durante i trade BTC si muove a favore molto più spesso che in generale | rendimento di BTC durante i trade vicino a quello di un periodo qualunque, mentre il candidato batte la (b) |
| C4 | Volatilità: la condizione sceglie barre ad alta o bassa volatilità, dove l'R con stop in ATR si distribuisce diversamente | il vantaggio sparisce cambiando la misura dello stop (robustezza) o è uguale nella (a) | il vantaggio regge allo spostamento dei parametri (Fase 4) e batte la (a) |
| C5 | Artefatto dei dati: buchi del mark, ombre anomale, barre tolte dall'allineamento | pochi trade estremi fanno il risultato; differenza grande con la regola intra-barra opposta | R senza i 3 migliori ancora sopra la (b); regola intra-barra opposta con differenza piccola |
| C6 | Effetto costi: il vantaggio lordo esiste ma i costi lo mangiano | R medio dopo i costi non positivo | R medio positivo dopo i costi e a costi doppi |
| C7 | Pochi eventi estremi: le giornate dei messaggi di personaggi famosi e delle corse del 2021 | R concentrato nel 2021 e in 3-5 trade | R per anno sopra la (b) in più anni; R senza i 3 migliori ancora sopra la (b) |
| C8 | Errore di codice o sguardo nel futuro | il risultato crolla con il ritardo di una barra | il `t` col ritardo resta positivo e almeno metà |

---

## Idea I-01 — Momento della serie storica a una settimana

1. **Fonte.** Tobias J. Moskowitz, Yao Hua Ooi, Lasse Heje Pedersen, «Time series momentum»,
   Journal of Financial Economics 104(2), maggio 2012. Per le crypto: Yukun Liu, Aleh
   Tsyvinski, «Risks and Returns of Cryptocurrency», NBER Working Paper 24877, agosto 2018
   (Review of Financial Studies 34(6), 2021): il rendimento di una settimana prevede quello
   delle settimane successive.
2. **Affermazione falsificabile.** Su DOGEUSDT, dopo 7 giorni con rendimento positivo
   (negativo), il rendimento dei 3 giorni successivi è in media positivo (negativo) più che
   dopo un giorno qualunque, al netto dei costi.
3. **Sotto-domande.** Vale di più dopo movimenti grandi o piccoli? Con volatilità alta? Chi
   opera: piccoli investitori che inseguono il prezzo (attenzione) e chi copre posizioni short;
   l'effetto dovrebbe manifestarsi in giorni o settimane, non in ore.
4. **Spiegazioni concorrenti specifiche.**
   * S1 Inversione di breve: su DOGE le corse si sgonfiano in pochi giorni → previsione: R
     negativo nei primi giorni; smentita: R positivo anche a 3 giorni.
   * S2 Grappoli: le settimane positive sono tutte nel primo semestre del 2021 → previsione:
     quasi tutti i trade in pochi mesi; smentita: trade sparsi in più anni con R sopra la (b).
   * S3 Effetto del solo segno: conta l'ampiezza, non il segno → previsione: R medio vicino a
     zero per i rendimenti settimanali piccoli; non smentibile qui senza un ritocco (da Fase 3).
5. (previsioni e smentite sono nelle tabelle sopra e qui.)
6. **Ipotesi completa e varianti.** Timeframe 1d (il meccanismo è settimanale; 1d è il più
   corto che lo misura senza rumore intraday).
   * **I-01-L** (DOGEUSDT-001): 1d, long. Ingresso se close / close di 7 barre prima − 1 > 0.
     Uscita a tempo dopo 3 barre. Stop 2,5 ATR, nessun target. Motivo: la fonte dice che il
     segno della settimana passata prevede la settimana dopo; 3 giorni dimezzano l'esposizione
     al rumore e danno abbastanza trade.
   * **I-01-S** (DOGEUSDT-002): 1d, short, specchio (rendimento a 7 giorni < 0). Motivo: la
     fonte vale in entrambe le direzioni.
   Previsione (entrambe): R medio dopo i costi fra −0,05 e +0,15; non mi aspetto «netta».

## Idea I-02 — Momento intraday: la prima mezz'ora prevede l'ultima

1. **Fonte.** Dehua Shen, Andrew Urquhart, Pengfei Wang, «Bitcoin intraday time-series
   momentum», Financial Review 57(2), online il 26 ottobre 2021.
2. **Affermazione.** Su DOGEUSDT il rendimento della prima mezz'ora del giorno UTC
   (00:00-00:30) ha lo stesso segno, più spesso del caso, del rendimento dell'ultima mezz'ora
   (23:30-24:00), al netto dei costi.
3. **Sotto-domande.** La fonte definisce il giorno con il volume (Bitcoin non ha apertura): qui
   si usa il giorno UTC, un'approssimazione da dichiarare. Vale di più nei giorni con volume o
   volatilità alti (la fonte lo dice). Chi opera: fornitori di liquidità che chiudono le scorte
   a fine giornata (meccanismo della fonte).
4. **Spiegazioni specifiche.** S1 L'ultima mezz'ora UTC non è la fine della giornata di nessun
   mercato importante → previsione: nessun effetto; smentita: `t` contro la (b) oltre la
   soglia. S2 Il costo (circa 0,1-0,15 R a 30 minuti) supera ogni vantaggio → previsione: R
   lordo positivo, netto negativo. S3 L'effetto della fonte è di Bitcoin, non di DOGE →
   previsione: nulla su DOGE.
6. **Varianti.** Timeframe 30m (la fonte usa mezz'ore).
   * **I-02-L** (DOGEUSDT-003): 30m, long. Segnale alla chiusura della barra 23:00-23:30 UTC se
     la barra 00:00-00:30 dello stesso giorno ha chiuso sopra la sua apertura; ingresso 23:30,
     uscita a tempo dopo 1 barra (24:00). Stop 2 ATR, nessun target.
   * **I-02-S** (DOGEUSDT-004): specchio short (prima mezz'ora negativa).
   Previsione: R medio dopo i costi fra −0,15 e 0; con i costi a 30 minuti mi aspetto perdita.

## Idea I-03 — Rottura del canale di prezzo

1. **Fonte.** William Brock, Josef Lakonishok, Blake LeBaron, «Simple Technical Trading Rules
   and the Stochastic Properties of Stock Returns», Journal of Finance 47(5), dicembre 1992
   (regola «trading range break»); per le crypto Robert Hudson, Andrew Urquhart, «Technical
   trading and cryptocurrencies», Annals of Operations Research, online il 30 agosto 2019.
2. **Affermazione.** Su DOGEUSDT, dopo una chiusura sopra (sotto) il massimo (minimo) delle 50
   barre di 4 ore precedenti, il prezzo prosegue nella stessa direzione nei 5 giorni
   successivi più che dopo una barra qualunque, al netto dei costi.
3. **Sotto-domande.** Le rotture vere sono quelle con volume? In volatilità bassa? Chi opera:
   chi segue il trend e gli stop dei venditori allo scoperto sopra i massimi.
4. **Spiegazioni specifiche.** S1 Falsa rottura: il prezzo torna nel canale → R negativo.
   S2 Le rotture coincidono con i giorni di notizie (2021) → R concentrato. S3 La rottura
   segue già un movimento lungo, e l'inversione domina → R negativo nei primi giorni.
6. **Varianti.** Timeframe 4h (50 barre ≈ 8 giorni, rotture abbastanza frequenti da avere trade).
   * **I-03-L** (DOGEUSDT-005): 4h, long. Ingresso se close > massimo degli high delle 50 barre
     prima (esclusa la barra del segnale). Uscita a tempo dopo 30 barre (5 giorni). Stop 2 ATR.
   * **I-03-S** (DOGEUSDT-006): specchio short (close < minimo dei low delle 50 barre prima).
   Previsione: R medio fra −0,05 e +0,15.

## Idea I-04 — Rottura di volatilità dall'apertura del giorno

1. **Fonte.** Larry Williams, «Long-Term Secrets to Short-Term Trading», Wiley, 1999.
2. **Affermazione.** Su DOGEUSDT, quando il prezzo sale (scende) oltre l'apertura del giorno UTC
   di più di metà dell'escursione del giorno prima, prosegue fino a fine giornata più del caso,
   al netto dei costi.
3. **Sotto-domande.** Vale di più dopo giorni stretti? Chi opera: chi entra in ritardo su un
   movimento già avviato, chi chiude short. Si manifesta nelle ore successive, nello stesso giorno.
4. **Spiegazioni specifiche.** S1 Inversione intraday dopo movimenti forti → R negativo.
   S2 L'apertura UTC non è un riferimento per i partecipanti di DOGE → nessun effetto.
6. **Varianti.** Timeframe 1h (serve vedere l'attraversamento dentro il giorno).
   * **I-04-L** (DOGEUSDT-007): 1h, long. Livello = apertura delle 00:00 UTC + 0,5 × (massimo −
     minimo del giorno UTC precedente). Segnale alla prima chiusura oraria del giorno sopra il
     livello (tutte le chiusure precedenti dello stesso giorno sotto o uguali), non dopo la
     barra 22:00-23:00. Uscita alla chiusura della barra 23:00-24:00 (chiusura all'apertura del
     giorno dopo). Stop 2 ATR orari.
   * **I-04-S** (DOGEUSDT-008): specchio short (sotto apertura − 0,5 × escursione).
   Previsione: R medio fra −0,10 e +0,10.

## Idea I-05 — Ritorno dopo l'ipervenduto in un trend (RSI a 2 barre)

1. **Fonte.** Larry Connors, Cesar Alvarez, «Short Term Trading Strategies That Work»,
   TradingMarkets Publishing, 2008.
2. **Affermazione.** Su DOGEUSDT, in trend rialzista (close sopra la media a 200 barre), una
   RSI a 2 barre sotto 10 è seguita da un rimbalzo fino alla media a 5 barre più spesso del
   caso, al netto dei costi (short: specchio).
3. **Sotto-domande.** Vale con volatilità alta? Chi opera: fornitori di liquidità che comprano
   le vendite forzate. Tempo: poche barre.
4. **Spiegazioni specifiche.** S1 Su DOGE le cadute continuano (momento di breve) → R negativo.
   S2 Uscita sulla media corta: tanti piccoli guadagni e rare grandi perdite (R asimmetrici) →
   win rate alto e R medio vicino a zero.
6. **Varianti.** Timeframe 4h (a 1d i trade non bastano: circa 20 l'anno nella fonte).
   * **I-05-L** (DOGEUSDT-009): 4h, long. Ingresso se close > SMA200 e RSI(2) < 10. Uscita
     quando close > SMA5. Stop 3 ATR.
   * **I-05-S** (DOGEUSDT-010): specchio short (close < SMA200, RSI(2) > 90, uscita close < SMA5).
   Previsione: R medio fra −0,10 e +0,10.

## Idea I-06 — Premio del volume alto (visibilità)

1. **Fonte.** Simon Gervais, Ron Kaniel, Dan Mingelgrin, «The High-Volume Return Premium»,
   Journal of Finance 56(3), giugno 2001.
2. **Affermazione.** Su DOGEUSDT, dopo un giorno con volume in USDT molto sopra la media (oltre
   1,5 volte la media dei 20 giorni prima), il prezzo sale nei 5 giorni dopo più del caso;
   dopo un giorno con volume molto sotto (sotto 0,6 volte), scende.
3. **Sotto-domande.** Conta il segno del rendimento del giorno? (La fonte dice di no.) Chi
   opera: nuovi compratori attirati dalla visibilità. Tempo: giorni o settimane.
4. **Spiegazioni specifiche.** S1 Il volume alto coincide con i massimi delle corse (fine della
   corsa) → R negativo. S2 Il volume basso è nei periodi calmi, senza direzione → R nullo.
6. **Varianti.** Timeframe 1d (la fonte misura giorni e settimane). Volume dalla colonna
   `quote_volume` del last.
   * **I-06-L** (DOGEUSDT-011): 1d, long se volume > 1,5 × media dei 20 giorni precedenti.
     Uscita a tempo dopo 5 barre. Stop 2,5 ATR.
   * **I-06-S** (DOGEUSDT-012): 1d, short se volume < 0,6 × media dei 20 giorni precedenti.
     Uscita dopo 5 barre. Stop 2,5 ATR.
   Previsione: R medio fra −0,10 e +0,15.

## Idea I-07 — Domanda da lotteria (effetto del massimo)

1. **Fonte.** Turan G. Bali, Nusret Cakici, Robert F. Whitelaw, «Maxing out: Stocks as
   lotteries and the cross-section of expected returns», Journal of Financial Economics 99(2),
   febbraio 2011; per le crypto Klaus Grobys, Juha Junttila, «Speculation and lottery-like
   demand in cryptocurrency markets», Journal of International Financial Markets, Institutions
   and Money 71, 2021 (online alla fine del 2020).
2. **Affermazione.** Su DOGEUSDT, dopo una settimana con almeno un giorno sopra +10%, il
   rendimento dei 3 giorni dopo è più basso del caso (short); dopo una settimana senza giorni
   sopra +3%, più alto (long).
3. **Sotto-domande.** È l'inversione delle corse? Chi opera: compratori di «biglietti della
   lotteria» che pagano troppo dopo un salto. Tempo: giorni o settimane.
4. **Spiegazioni specifiche.** S1 La fonte è sezionale (fra monete), non nel tempo su una
   moneta: l'effetto può non esistere nel tempo → nessun effetto. S2 Dopo i salti viene il
   momento (I-01), non l'inversione → R negativo per lo short.
6. **Varianti.** Timeframe 1d.
   * **I-07-S** (DOGEUSDT-013): 1d, short se il massimo dei rendimenti giornalieri (close su
     close) delle ultime 7 barre ≥ 10%. Uscita dopo 3 barre. Stop 2,5 ATR.
   * **I-07-L** (DOGEUSDT-014): 1d, long se quel massimo < 3%. Uscita dopo 3 barre. Stop 2,5 ATR.
   Previsione: R medio fra −0,15 e +0,10.

## Idea I-08 — Funding estremo: posizioni a leva affollate

1. **Fonte.** Songrun He, Asaf Manela, Omri Ross, Victor von Wachter, «Fundamentals of
   Perpetual Futures», arXiv 2212.06888, dicembre 2022: il prezzo dei perpetui si discosta dal
   prezzo a pronti più di quanto l'arbitraggio dovrebbe permettere, e il funding misura quella
   distanza. Che un funding alto preceda un calo è una mia deduzione dal meccanismo
   (domanda di leva lunga che spinge il perpetuo sopra il valore), non un risultato della fonte.
2. **Affermazione.** Su DOGEUSDT, dopo un settlement con funding ≥ 0,05% (cinque volte il
   valore di base 0,01%), il prezzo nelle 24 ore dopo scende più del caso; dopo un funding
   negativo, sale.
3. **Sotto-domande.** Vale di più con funding molto alto? Chi opera: long a leva che vengono
   chiusi o liquidati. Tempo: ore o un giorno.
4. **Spiegazioni specifiche.** S1 Il funding alto segue il prezzo (è effetto, non causa): in
   trend forte resta alto e il prezzo continua → R negativo per lo short. S2 Il funding pagato
   dallo short è un incasso, e da solo crea un R positivo → si controlla con la (b), che entra
   a caso e incassa meno.
6. **Varianti.** Timeframe 8h (allineato ai settlement ogni 8 ore). Il funding usato è l'ultimo
   settlement con istante ≤ chiusura della barra del segnale.
   * **I-08-S** (DOGEUSDT-015): 8h, short se ultimo funding ≥ 0,0005. Uscita dopo 3 barre.
     Stop 2 ATR.
   * **I-08-L** (DOGEUSDT-016): 8h, long se ultimo funding < 0. Uscita dopo 3 barre. Stop 2 ATR.
   Previsione: R medio fra −0,10 e +0,10.

## Idea I-09 — Effetto del lunedì

1. **Fonte.** Guglielmo Maria Caporale, Alex Plastun, «The day of the week effect in the
   cryptocurrency market», Finance Research Letters 31, 2019 (CESifo Working Paper 6716,
   ottobre 2017): per Bitcoin i rendimenti del lunedì sono più alti degli altri giorni.
2. **Affermazione.** Su DOGEUSDT il rendimento del lunedì UTC è più alto di quello di un giorno
   a caso, al netto dei costi.
3. **Sotto-domande.** È un effetto del fine settimana (meno liquidità sabato e domenica)? Chi
   opera: istituzioni e piccoli investitori che tornano al lavoro. Tempo: un giorno.
4. **Spiegazioni specifiche.** S1 La fonte trova l'effetto solo per Bitcoin e dice che non è
   distinguibile dal caso nel trading → nulla. S2 Con 127 lunedì l'errore è grande → non
   valutabile o non netto.
6. **Variante unica.** Timeframe 1d.
   * **I-09-L** (DOGEUSDT-017): 1d, long. Segnale alla chiusura della domenica UTC, ingresso
     all'apertura del lunedì, uscita dopo 1 barra. Stop 2 ATR.
   Previsione: R medio fra −0,10 e +0,10.

## Idea I-10 — Strettoia delle bande di Bollinger

1. **Fonte.** John Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001: i periodi di
   volatilità bassa precedono espansioni, e la direzione dell'uscita dalla strettoia indica il
   movimento.
2. **Affermazione.** Su DOGEUSDT, una chiusura sopra (sotto) la banda superiore (inferiore) a 20
   barre e 2 deviazioni standard, quando l'ampiezza delle bande è nel quinto più basso delle
   ultime 120 barre, è seguita da un movimento nella stessa direzione più del caso.
3. **Sotto-domande.** Quanto è lunga la strettoia? Chi opera: ordini fermi sopra e sotto il
   canale stretto. Tempo: decine di ore.
4. **Spiegazioni specifiche.** S1 Si sovrappone alla rottura del canale (I-03) → stesso esito
   di I-03. S2 Le strettoie su DOGE sono solo pause prima del trend esistente → l'R dipende dal
   trend (C2).
6. **Varianti.** Timeframe 4h.
   * **I-10-L** (DOGEUSDT-018): 4h, long. Ampiezza = 4 × deviazione standard(20) / SMA20;
     ingresso se ampiezza ≤ 20° percentile delle ultime 120 ampiezze (barra corrente compresa)
     e close > SMA20 + 2 deviazioni. Uscita dopo 12 barre. Stop 2 ATR.
   * **I-10-S** (DOGEUSDT-019): specchio short.
   Previsione: R medio fra −0,10 e +0,10.

## Idea I-11 — Inversione dopo una barra estrema (fornitura di liquidità)

1. **Fonte.** Bruce N. Lehmann, «Fads, Martingales, and Market Efficiency», Quarterly Journal
   of Economics 105(1), febbraio 1990: i rendimenti di breve si invertono, perché chi fornisce
   liquidità a chi vende (compra) in fretta chiede un compenso.
2. **Affermazione.** Su DOGEUSDT, dopo una barra oraria con rendimento sotto −3 deviazioni
   standard (calcolate sulle 168 barre precedenti), il prezzo nelle 6 ore dopo risale più del
   caso; specchio per le barre sopra +3.
3. **Sotto-domande.** Vale di più con volume alto? Chi opera: chi compra dalle liquidazioni a
   cascata. Tempo: poche ore.
4. **Spiegazioni specifiche.** S1 Le barre estreme sono notizie, e le notizie proseguono →
   R negativo. S2 Dopo una barra estrema l'ATR si allarga e lo stop diventa largo → R piccoli.
6. **Varianti.** Timeframe 1h.
   * **I-11-L** (DOGEUSDT-020): 1h, long se rendimento della barra (close su close) <
     −3 × deviazione standard dei rendimenti delle 168 barre prima. Uscita dopo 6 barre. Stop 2 ATR.
   * **I-11-S** (DOGEUSDT-021): specchio short (sopra +3).
   Previsione: R medio fra −0,10 e +0,15.

## Idea I-12 — Inerzia dopo un giorno anomalo

1. **Fonte.** Guglielmo Maria Caporale, Alex Plastun, «Price overreactions in the
   cryptocurrency market», Journal of Economic Studies 46(5), 2019 (CESifo Working Paper 6861,
   gennaio 2018): dopo un giorno di sovrareazione il prezzo tende a proseguire nella stessa
   direzione (inerzia); la fonte dice che l'inerzia non è distinguibile dal caso nella loro
   simulazione di trading.
2. **Affermazione.** Su DOGEUSDT, dopo un giorno con rendimento oltre la media + 1,5 deviazioni
   standard dei 30 giorni prima, il giorno dopo prosegue nella stessa direzione più del caso.
3. **Sotto-domande.** Proseguimento o inversione? Chi opera: chi arriva in ritardo sulla notizia.
   Tempo: un giorno.
4. **Spiegazioni specifiche.** S1 Inversione (I-11 su scala giornaliera) → R negativo. S2 Si
   sovrappone a I-01 (momento) → stesso esito.
6. **Varianti.** Timeframe 1d.
   * **I-12-L** (DOGEUSDT-022): 1d, long se rendimento del giorno > media + 1,5 × deviazione
     standard dei 30 rendimenti giornalieri precedenti. Uscita dopo 1 barra. Stop 2 ATR.
   * **I-12-S** (DOGEUSDT-023): short se < media − 1,5 deviazioni.
   Previsione: R medio fra −0,10 e +0,10. Mi aspetto meno di 70 trade (giorni anomali circa
   il 7%): in quel caso è uno scarto.
