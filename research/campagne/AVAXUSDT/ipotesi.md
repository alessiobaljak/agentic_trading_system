# Ipotesi della campagna AVAXUSDT

Scritte prima di ogni test della loro idea (Fase 1). Le varianti di ogni idea sono tutte qui,
con il loro motivo, prima del primo test dell'idea (regola 6). Nessuna idea viene da risultati
del gate, del registro, del paper o di altre monete, e nessuna è scelta "perché so che ha
funzionato" dopo il 2023 (regola 8).

## Elementi comuni

**Periodi** (log, voce N003): costruzione 2020-09-01 → 2022-12-30; validazione 2022-12-31 →
2023-12-31. In costruzione ci sono circa 851 giorni: 70 trade sono un ingresso ogni 12 giorni.

**Costo di un giro in R** (lezione di metodo «previsioni al netto dei costi»): commissione
0,05% e slippage 0,02% per lato, quindi 0,14% del nozionale andata e ritorno, più il funding.
In R vale 0,14% diviso la distanza dello stop in percentuale: stop all'1% → 0,14 R; al 2% →
0,07 R; al 5% → 0,03 R; al 10% → 0,014 R. Le distanze tipiche le scrivo per ogni idea, come
ordine di grandezza (non misurate sui risultati): ATR(14) di AVAXUSDT stimato a grandi linee
come 1-1,5% a 1 ora, 0,7-1% a 30 minuti, 2,5-3,5% a 4 ore, 4-5% a 8 ore, 7-9% a 1 giorno.

**Tetto di stop del bot** (`stop_massimo_bot`, 6%): uno stop di 2 ATR a 1 giorno lo supera
quasi sempre. Il motore lo riporta (`stop_oltre_6_per_cento`) e non lo impone; un candidato
così non è eseguibile dal bot com'è, e va dichiarato.

**Spiegazioni concorrenti comuni.** Per ogni idea le prime sei sono le stesse sei «noiose»,
con previsione e smentita adattate all'idea; seguono quelle specifiche (almeno quattro).
Le sei comuni, in generale:

| Spiegazione | Previsione che fa | Cosa la smentisce |
|---|---|---|
| Caso | Il `t` contro la (b) sta entro ±2; percentile fra il 10 e il 90 | `t` oltre la soglia e un R medio stabile per anno |
| Volatilità | Il risultato viene dai periodi di volatilità alta (2021), dove gli R in valore assoluto sono più grandi; la (b) con la stessa uscita lo cattura | L'effetto c'è anche negli anni a volatilità più bassa (2022) |
| Trend di fondo | Un long guadagna nel 2021 e perde nel 2022 come la (b) della stessa direzione | Battere la (b), che entra a caso nella stessa direzione, in entrambi gli anni |
| Artefatto dei dati | Il risultato dipende da barre tolte dall'allineamento, buchi o candele anomale | Nessuna dipendenza da pochi trade (R senza i 3 migliori) e regola intra-barra opposta simile |
| Effetto costi | R lordo positivo ma netto vicino a zero o negativo | R netto positivo con margine sul costo in R scritto sopra |
| È solo il mercato | AVAXUSDT segue BTCUSDT: il segnale è un segnale di BTC e la (b) nella stessa direzione lo spiega | Il vantaggio resta contro la (b); controllo con BTC dove l'idea lo permette |

## Controllo positivo degli strumenti (non è una variante)

Una strategia che legge di proposito il close della barra successiva (entra long se la barra
dopo chiude sopra la sua apertura), 1 ora, uscita dopo una barra, stop 2 ATR(14). Deve battere
nettamente la (b) e crollare con il ritardo di una barra. Si registra come nota.

---

## I-01 Momentum di serie temporale a 1 giorno

1. **Fonte.** T. J. Moskowitz, Y. H. Ooi, L. H. Pedersen, «Time series momentum», Journal of
   Financial Economics 104(2), 2012. Per le crypto: Y. Liu, A. Tsyvinski, «Risks and Returns of
   Cryptocurrency», NBER working paper 24877, agosto 2018 (Review of Financial Studies 34(6), 2021):
   il rendimento delle settimane passate predice quello delle settimane successive.
2. **Affermazione verificabile.** Su AVAXUSDT, dopo 14 giorni con rendimento positivo (negativo),
   il rendimento dei 3 giorni successivi è in media più alto (più basso) di quello di un ingresso
   casuale nella stessa direzione con la stessa uscita.
3. **Sotto-domande.** Vale nei trend lunghi (2021) e non nei laterali? Più forte dopo movimenti
   ampi? Chi opera: investitori che reagiscono in ritardo all'informazione (sotto-reazione) e
   inseguitori di trend; l'effetto si manifesta in giorni-settimane.
4-5. **Spiegazioni concorrenti** (oltre alle sei comuni, adattate: trend di fondo è qui la più
   forte, perché un long dopo rendimenti positivi è quasi sempre dentro un rialzo):
   | Spiegazione | Previsione | Smentita |
   |---|---|---|
   | Caso | `t` contro la (b) entro ±2 | `t` oltre soglia in entrambi gli anni |
   | Volatilità | Guadagni solo nel 2021 | Effetto anche nel 2022 |
   | Trend di fondo | Long buoni nel 2021, cattivi nel 2022 come la (b) | Battere la (b) in entrambi gli anni |
   | Artefatto dei dati | Dipende da poche candele giornaliere estreme | R senza i 3 migliori ancora sopra la (b) |
   | Effetto costi | Con stop larghi i costi in R sono piccoli: non spiega | — |
   | È solo il mercato | Il rendimento di 14 giorni di AVAX coincide con quello di BTC | Effetto anche quando AVAX e BTC divergono |
   | Sotto-reazione all'informazione | L'effetto cresce col tempo di tenuta fino a settimane | Effetto solo nel primo giorno (sarebbe microstruttura) |
   | Inversione a breve | Dopo rialzi forti il primo giorno scende | R medio positivo sui 3 giorni |
   | Regime di liquidità (2021) | Effetto concentrato nei mesi di afflusso | Effetto distribuito |
   | Rumore del rendimento a 14 giorni | Segnale che cambia ogni pochi giorni, trade casuali | Persistenza del segno |
6. **Ipotesi completa e varianti.** Moneta AVAXUSDT, timeframe 1 giorno (il meccanismo è di
   giorni-settimane), due direzioni separate:
   - **V-01 (long).** Alla chiusura del giorno i, se close(i)/close(i−14) − 1 > 0: long
     all'apertura del giorno dopo; stop = close(i) − 2·ATR(14); nessun target; uscita dopo 3
     barre (chiusura all'apertura della quarta). Motivo: orizzonte di giorni della fonte; 3
     giorni danno abbastanza ingressi in 851 giorni.
   - **V-02 (short).** Specchio: rendimento a 14 giorni < 0, short, stop = close + 2·ATR(14),
     uscita dopo 3 barre.
   Previsione (al netto dei costi, circa 0,02 R a giro con stop al 15-20%): R medio fra 0 e
   0,10; poco probabile battere nettamente la (b), perché la (b) entra nella stessa direzione
   negli stessi anni di trend.

## I-02 Rottura del canale di Donchian a 4 ore

1. **Fonte.** C. Faith, «Way of the Turtle», McGraw-Hill, 2007 (le regole delle Tartarughe di
   R. Dennis: ingresso sulla rottura del massimo di 20 periodi, uscita sul minimo di 10, stop a
   2 N con N l'ATR di 20); R. Donchian, canali di prezzo (anni '60, descritti nella stessa fonte).
2. **Affermazione.** Quando il close di 4 ore supera il massimo delle 20 barre precedenti, il
   prezzo continua nella direzione della rottura più di quanto faccia dopo un ingresso casuale
   con la stessa uscita (canale di 10 barre e stop 2 ATR).
3. **Sotto-domande.** Rotture con volume alto o basso? In regimi di volatilità in espansione?
   Chi opera: ordini di stop sopra i massimi recenti, inseguitori di trend, liquidazioni di short;
   l'effetto dura ore-giorni.
4-5. **Spiegazioni concorrenti.**
   | Spiegazione | Previsione | Smentita |
   |---|---|---|
   | Caso | `t` entro ±2 | `t` oltre soglia |
   | Volatilità | Guadagni solo nelle fasi di espansione 2021 | Effetto anche nel 2022 |
   | Trend di fondo | Long guadagna nel 2021 come la (b) | Battere la (b) |
   | Artefatto dei dati | Pochi trade enormi fanno il totale | R senza i 3 migliori sopra la (b) |
   | Effetto costi | Stop di 2 ATR a 4 ore (circa 6%): 0,02 R a giro, non spiega | — |
   | È solo il mercato | Le rotture di AVAX coincidono con rotture di BTC | — (lo misura la (b) solo in parte) |
   | Caccia agli stop (falsa rottura) | Molte uscite in perdita entro poche barre | Durata media lunga dei vincenti |
   | Asimmetria vincenti-perdenti | Win rate basso, pochi trade lunghi fanno tutto | R per anno positivo in più anni |
   | Rottura su barra anomala (ombra) | Usare il close evita le ombre: non spiega | — |
   | Sovrapposizione col momentum di I-01 | Stessi giorni di ingresso | Correlazione bassa fra i due |
6. **Varianti.** 4 ore (il meccanismo degli stop sopra i massimi agisce in ore-giorni; a 1
   giorno 20 barre sono un mese e i trade sarebbero pochi).
   - **V-03 (long).** close(i) > massimo degli high delle barre i−20..i−1 → long; stop =
     close(i) − 2·ATR(20); uscita quando close < minimo dei low delle 10 barre precedenti.
   - **V-04 (short).** Specchio: close(i) < minimo dei low delle 20 precedenti → short; stop
     close + 2·ATR(20); uscita quando close > massimo degli high delle 10 precedenti.
   Previsione: R medio fra −0,05 e 0,15, win rate 30-40%; `t` contro la (b) sotto la soglia.

## I-03 Ritorno verso la media con RSI a 2 periodi, a 4 ore

1. **Fonte.** L. Connors, C. Alvarez, «Short Term Trading Strategies That Work», TradingMarkets
   Publishing, 2008 (RSI(2) sotto 10 sopra la media a 200 periodi; uscita sopra la media a 5).
2. **Affermazione.** In un trend rialzista (close sopra la media a 200 barre), un ipervenduto di
   breve (RSI(2) < 10) è seguito da un rimbalzo più frequente di un ingresso casuale con la
   stessa uscita (close sopra la media a 5) e lo stesso stop.
3. **Sotto-domande.** Vale solo nei rialzi? Dopo cali con volume alto (liquidazioni)? Chi opera:
   fornitori di liquidità che comprano le vendite forzate; l'effetto si esaurisce in poche barre.
4-5. **Spiegazioni concorrenti.**
   | Spiegazione | Previsione | Smentita |
   |---|---|---|
   | Caso | `t` entro ±2 | `t` oltre soglia |
   | Volatilità | Rimbalzi più grandi nel 2021 | Effetto anche nel 2022 |
   | Trend di fondo | Long nel rialzo 2021 vince come la (b) | Battere la (b) |
   | Artefatto dei dati | Ipervenduti da candele anomale | R senza i 3 migliori |
   | Effetto costi | Uscite rapide, stop larghi (3 ATR ≈ 9%): costo 0,015 R, non spiega | — |
   | È solo il mercato | Gli ipervenduti di AVAX sono ipervenduti di BTC | — |
   | Molti piccoli guadagni e rare grandi perdite | Win rate alto, R medio rovinato da pochi stop | R medio positivo con lo stop |
   | Rimbalzo del gatto morto nei crolli | Le perdite si concentrano a maggio 2021 e nel 2022 | — |
   | Bid-ask rimbalzo | Sui contratti liquidi a 4 ore non conta | — |
   | Filtro della media a 200 che lavora da solo | La (a) (senza RSI) fa quasi lo stesso | Battere la (a) |
6. **Varianti.** 4 ore: la fonte è giornaliera su azioni, ma le crypto girano 24 ore su 24 e
   l'ipervenduto di breve si riassorbe in ore (Wen e coautori 2022 trovano inversioni infragiornaliere);
   a 1 giorno, con 200 giorni di riscaldamento, i trade sarebbero troppo pochi.
   - **V-05 (long).** RSI(2) < 10 e close > media semplice a 200 → long; stop close − 3·ATR(14)
     (la fonte non usa stop: questo è uno stop di disastro); uscita quando close > media a 5.
   - **V-06 (short).** Specchio: RSI(2) > 90 e close < media a 200 → short; stop close + 3·ATR(14);
     uscita quando close < media a 5.
   Previsione: win rate 60-70%, R medio fra −0,05 e 0,10.

## I-04 Funding estremo come segnale contrario, a 8 ore

1. **Fonte.** S. He, A. Manela, O. Ross, V. von Wachter, «Fundamentals of Perpetual Futures»,
   arXiv 2212.06888, dicembre 2022; N. Christin, B. Routledge, K. Soska, A. Zetlin-Jones, «The
   Crypto Carry Trade», bozza dell'1 agosto 2022 (Carnegie Mellon): il funding misura la
   domanda di leva lunga; quando è alto la posizione è affollata.
2. **Affermazione.** Dopo un settlement con funding ≥ 0,03% per 8 ore (tre volte il livello
   base 0,01%), il prezzo nelle 24 ore dopo scende più di un ingresso short casuale con la
   stessa uscita; dopo un funding negativo (short affollati) sale più di un long casuale.
3. **Sotto-domande.** Vale nei rialzi euforici o in ogni regime? Il funding alto anticipa
   liquidazioni dei long? Chi opera: arbitraggisti del carry (vendono il perpetuo), long a leva
   che chiudono; effetto in ore-giorni.
4-5. **Spiegazioni concorrenti.**
   | Spiegazione | Previsione | Smentita |
   |---|---|---|
   | Caso | `t` entro ±2 | `t` oltre soglia |
   | Volatilità | Funding alto nei periodi più volatili, R grandi in entrambe le direzioni | Effetto di segno stabile |
   | Trend di fondo | Funding alto nel rialzo: lo short perde come la (b) short | Battere la (b) |
   | Artefatto dei dati | Settlement mancanti o intervallo cambiato | Fase 0 senza problemi di funding |
   | Effetto costi | Lo short incassa il funding alto: parte del guadagno è il funding, non il prezzo | Guardare il funding totale nel risultato |
   | È solo il mercato | Funding alto su tutte le monete insieme | — |
   | Il funding segue il prezzo (è effetto, non causa) | Dopo il funding alto il trend continua | R medio dello short negativo |
   | Arbitraggio del carry già lo neutralizza | Nessun effetto sul prezzo | — |
   | Pochi episodi di euforia fanno tutto | Trade concentrati in pochi mesi | Trade distribuiti |
   | Soglia vicina al tetto/pavimento del funding | Molti settlement uguali alla soglia | — |
6. **Varianti.** 8 ore: il funding si regola ogni 8 ore (00, 08, 16 UTC); la barra di 8 ore che
   chiude al settlement vede il tasso appena pagato.
   - **V-07 (short).** Ultimo funding regolato entro la chiusura della barra ≥ 0,0003 → short;
     stop close + 2·ATR(14); uscita dopo 3 barre (24 ore).
   - **V-08 (long).** Ultimo funding < 0 → long; stop close − 2·ATR(14); uscita dopo 3 barre.
   Previsione: V-07 R medio fra −0,1 e 0,1; V-08 fra −0,05 e 0,15. Trade: non so se bastano.

## I-05 Ritardo di AVAX rispetto a BTC, a 1 ora

1. **Fonte.** A. Mohamad, I. M. Sifat, M. S. Mohamed Shariff, «Lead-Lag relationship between
   Bitcoin and Ethereum: Evidence from hourly and daily data», Research in International Business
   and Finance 50, 2019: causalità fra le due a frequenza oraria (con poco spazio di profitto
   secondo gli autori). L'idea da provare: una moneta minore incorpora in ritardo un movimento
   forte di BTC.
2. **Affermazione.** Se in un'ora BTCUSDT sale di almeno l'1% e AVAXUSDT sale meno della metà,
   nelle 3 ore successive AVAX recupera più di un long casuale con la stessa uscita (specchio
   per il ribasso).
3. **Sotto-domande.** Vale nelle ore di liquidità bassa? Il recupero arriva entro 1-3 ore? Chi
   opera: arbitraggisti fra monete e investitori che guardano BTC come guida.
4-5. **Spiegazioni concorrenti.**
   | Spiegazione | Previsione | Smentita |
   |---|---|---|
   | Caso | `t` entro ±2 | `t` oltre soglia |
   | Volatilità | Ore di BTC forte sono ore volatili: R grandi in entrambi i sensi | Segno stabile |
   | Trend di fondo | Long nel 2021 | Battere la (b) |
   | Artefatto dei dati | Barre di BTC e AVAX non sincrone | Stesso ts di apertura per costruzione |
   | Effetto costi | Stop 2 ATR orario ≈ 2,5%: 0,055 R a giro; un recupero piccolo non li copre | R netto positivo |
   | È solo il mercato | Proprio l'idea: AVAX segue BTC; ma se segue subito non c'è ritardo | — |
   | Divergenza informativa (notizia propria di AVAX) | AVAX non recupera: decorrelazione vera | R medio negativo |
   | Inversione di BTC | BTC torna indietro e AVAX non deve recuperare | — |
   | Liquidità sottile di AVAX nel 2020 | Effetto solo nei mesi illiquidi (esclusi dal filtro) | — |
   | Soglia dell'1% troppo comune/rara | — | lo dice `conta_trade` |
6. **Varianti.** 1 ora (la fonte usa dati orari).
   - **V-09 (long).** Rendimento orario di BTC ≥ +1% e rendimento orario di AVAX ≤ metà di
     quello di BTC → long; stop close − 2·ATR(14); uscita dopo 3 barre.
   - **V-10 (short).** BTC ≤ −1% e AVAX ≥ metà di quello di BTC (è sceso meno) → short; stop
     close + 2·ATR(14); uscita dopo 3 barre.
   Previsione: R medio fra −0,1 e 0,05; i costi pesano.

## I-06 Momento infragiornaliero: il rendimento del giorno predice l'ultima mezz'ora

1. **Fonte.** L. Gao, Y. Han, S. Z. Li, G. Zhou, «Market intraday momentum», Journal of
   Financial Economics 129(2), 2018; Z. Wen, E. Bouri, Y. Xu, Y. Zhao, «Intraday return
   predictability in the cryptocurrency markets: Momentum, reversal, or both», North American
   Journal of Economics and Finance 62, 2022 (dati fino a maggio 2020, quindi pubblicazione e dati
   prima del 2024).
2. **Affermazione.** Il segno del rendimento dalle 00:00 UTC alle 23:30 UTC predice il segno
   dell'ultima mezz'ora del giorno UTC (23:30-24:00) meglio di un ingresso casuale di mezz'ora.
3. **Sotto-domande.** Più forte nei giorni di movimento ampio? Chi opera: chi ribilancia o
   copre a fine giornata UTC (ora di riferimento dei conti delle piattaforme); effetto in 30 minuti.
4-5. **Spiegazioni concorrenti.**
   | Spiegazione | Previsione | Smentita |
   |---|---|---|
   | Caso | `t` entro ±2 | `t` oltre soglia |
   | Volatilità | Ultima mezz'ora volatile nei giorni volatili, segno casuale | Segno coerente |
   | Trend di fondo | Long nei giorni di rialzo del 2021 | Battere la (b) |
   | Artefatto dei dati | Barre mancanti a fine giorno | Fase 0 |
   | Effetto costi | Stop 2 ATR a 30 minuti ≈ 1,6%: 0,09 R a giro: il vantaggio deve superarlo | R netto positivo |
   | È solo il mercato | Lo stesso schema su BTC | — |
   | Inversione (Wen e coautori trovano anche questa) | Ultima mezz'ora contraria al giorno | R medio negativo del long |
   | Funding alle 00:00 UTC | Chiusure prima del settlement spingono il prezzo contro le posizioni affollate | Effetto indipendente dal funding |
   | Rumore di microstruttura | Effetto di pochi punti base, sotto i costi | — |
   | Ritardo dei partecipanti informati in tardi | Effetto più forte con molta informazione nel giorno | — |
6. **Varianti.** 30 minuti (la fonte lavora sulla mezz'ora).
   - **V-11 (long).** Alla chiusura della barra 23:00-23:30 UTC, se close/open delle 00:00 − 1 > 0
     → long alla 23:30; uscita all'apertura della barra dopo (00:00); stop close − 2·ATR(14).
   - **V-12 (short).** Specchio con rendimento del giorno < 0.
   Previsione: R medio fra −0,1 e 0,02 (i costi in R sono alti per un movimento di mezz'ora).

## I-07 Effetto del lunedì, a 1 giorno

1. **Fonte.** G. M. Caporale, A. Plastun, «The day of the week effect in the cryptocurrency
   market», Finance Research Letters 31, 2019: rendimenti anomali di BTC il lunedì.
2. **Affermazione.** Il rendimento del lunedì UTC di AVAXUSDT è più alto di quello di un giorno
   long casuale con la stessa uscita.
3. **Sotto-domande.** Dipende dal fine settimana (meno liquidità sabato e domenica)? Chi opera:
   istituzionali e desk che rientrano il lunedì; effetto in un giorno.
4-5. **Spiegazioni concorrenti.**
   | Spiegazione | Previsione | Smentita |
   |---|---|---|
   | Caso | `t` entro ±2 (con circa 120 lunedì, molto rumore) | `t` oltre soglia |
   | Volatilità | Lunedì più volatile, segno casuale | Segno stabile |
   | Trend di fondo | Long nel 2021 | Battere la (b) |
   | Artefatto dei dati | Candela giornaliera del lunedì incompleta | Fase 0 |
   | Effetto costi | Stop 2 ATR giornaliero: costo trascurabile | — |
   | È solo il mercato | Anche BTC ha lo stesso schema | — |
   | Recupero del fine settimana | Lunedì sale dopo weekend in calo | — |
   | Notizie del fine settimana | Effetto con segno variabile | — |
   | Effetto pubblicato e già arbitraggiato | Nessun effetto dopo il 2019 | — |
   | Pochi lunedì estremi | Il totale viene da 3 lunedì | R senza i 3 migliori |
6. **Variante.** 1 giorno (il meccanismo è il giorno della settimana).
   - **V-13 (long).** Alla chiusura della domenica → long all'apertura del lunedì; stop close −
     2·ATR(14); uscita dopo 1 barra (apertura del martedì).
   Previsione: R medio fra −0,05 e 0,1; non netto.

## I-08 Seguire le reazioni eccessive, a 4 ore

1. **Fonte.** G. M. Caporale, A. Plastun, «Price overreactions in the cryptocurrency market»,
   Journal of Economic Studies 46(5), 2019 (versione CESifo n. 6861, gennaio 2018): dopo un
   rendimento anomalo il movimento successivo tende a seguire la direzione della reazione
   (loro: un robot "momentum" sopra il caso ma non in modo significativo).
2. **Affermazione.** Dopo una barra di 4 ore con rendimento oltre 2 deviazioni standard (calcolate
   sulle 180 barre precedenti, 30 giorni), il prezzo continua nella stessa direzione nelle 24 ore
   successive più di un ingresso casuale.
3. **Sotto-domande.** Più forte con volume alto? Chi opera: inseguitori e liquidazioni a catena;
   effetto in ore.
4-5. **Spiegazioni concorrenti.**
   | Spiegazione | Previsione | Smentita |
   |---|---|---|
   | Caso | `t` entro ±2 | `t` oltre soglia |
   | Volatilità | Dopo shock la volatilità resta alta, R grandi in entrambi i sensi | Segno stabile |
   | Trend di fondo | Shock al rialzo nel 2021, al ribasso nel 2022 | Battere la (b) per anno |
   | Artefatto dei dati | Barre anomale da dati sbagliati | Barre allineate col mark |
   | Effetto costi | Stop 2 ATR a 4 ore ≈ 6%: costo piccolo | — |
   | È solo il mercato | Shock comuni con BTC | — |
   | Inversione (la stessa fonte prova il contrario) | R medio negativo | R medio positivo |
   | Cascate di liquidazione | Continuazione per poche barre, poi inversione | — |
   | Notizie proprie della moneta | Continuazione più lunga | — |
   | Soglia di 2 deviazioni troppo comune | — | lo dice `conta_trade` |
6. **Varianti.** 4 ore (la fonte è giornaliera; a 1 giorno i rendimenti oltre 2 deviazioni sono
   troppo pochi in 851 giorni).
   - **V-14 (long).** z = rendimento della barra / deviazione standard dei rendimenti delle 180
     barre precedenti; z > 2 → long; stop close − 2·ATR(14); uscita dopo 6 barre.
   - **V-15 (short).** z < −2 → short; stop close + 2·ATR(14); uscita dopo 6 barre.
   Previsione: R medio fra −0,1 e 0,1.

## I-09 Rottura della volatilità del giorno (Williams, Crabel), a 1 ora

1. **Fonte.** L. Williams, «Long-Term Secrets to Short-Term Trading», Wiley, 1999 (rottura
   dell'apertura più una frazione dell'escursione del giorno prima); T. Crabel, «Day Trading with
   Short Term Price Patterns and Opening Range Breakout», Traders Press, 1990.
2. **Affermazione.** La prima ora del giorno UTC che chiude sopra apertura del giorno + 0,5 ×
   escursione (massimo − minimo) del giorno prima è seguita da un rialzo fino a fine giornata più
   grande di quello di un long casuale con la stessa uscita.
3. **Sotto-domande.** Più forte dopo un giorno stretto? Chi opera: inseguitori della rottura;
   effetto entro la giornata.
4-5. **Spiegazioni concorrenti.**
   | Spiegazione | Previsione | Smentita |
   |---|---|---|
   | Caso | `t` entro ±2 | `t` oltre soglia |
   | Volatilità | Giorni di rottura = giorni volatili | Segno stabile |
   | Trend di fondo | Long nel 2021 | Battere la (b) |
   | Artefatto dei dati | Ore mancanti | Fase 0 |
   | Effetto costi | Stop all'apertura del giorno: distanza ≥ 0,5 escursione (≈ 3-4%): costo 0,04 R | — |
   | È solo il mercato | Rotture comuni con BTC | — |
   | Falsa rottura | Ritorno sotto il livello in poche ore | — |
   | Esaurimento a fine giornata | Il guadagno sparisce prima delle 24 | — |
   | Rottura tardiva (sera) senza tempo per svilupparsi | R medio dipende dall'ora | — |
   | Rumore orario | — | — |
6. **Varianti.** 1 ora (la rottura si legge sulle ore del giorno).
   - **V-16 (long).** Livello = apertura del giorno UTC + 0,5 × (massimo − minimo del giorno UTC
     precedente); la prima barra oraria del giorno che chiude sopra il livello → long; stop =
     apertura del giorno; uscita alla chiusura della barra 23:00-24:00 (all'apertura del giorno dopo).
   - **V-17 (short).** Specchio: livello = apertura − 0,5 × escursione; prima chiusura sotto →
     short; stop = apertura del giorno; uscita a fine giorno.
   Previsione: R medio fra −0,1 e 0,1.

## I-10 Rottura dopo la compressione delle bande di Bollinger, a 4 ore

1. **Fonte.** J. Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001 (la «squeeze»:
   l'ampiezza delle bande al minimo di sei mesi precede un'espansione; la direzione la dà la
   rottura della banda).
2. **Affermazione.** Dopo che l'ampiezza delle bande (20 barre, 2 deviazioni) è al minimo delle
   ultime 125 barre, la prima chiusura fuori dalla banda (entro 10 barre) è seguita da un
   movimento nella stessa direzione più grande di un ingresso casuale con la stessa uscita.
3. **Sotto-domande.** La compressione precede davvero un'espansione? Chi opera: venditori di
   volatilità che coprono, stop sopra/sotto il range; effetto in ore-giorni.
4-5. **Spiegazioni concorrenti.**
   | Spiegazione | Previsione | Smentita |
   |---|---|---|
   | Caso | `t` entro ±2 | `t` oltre soglia |
   | Volatilità | Ritorno alla media della volatilità: espansione certa, direzione casuale | Segno stabile |
   | Trend di fondo | Rotture al rialzo nel 2021 | Battere la (b) |
   | Artefatto dei dati | Compressioni da barre piatte (dati mancanti) | Fase 0 |
   | Effetto costi | Stop 2 ATR a 4 ore: costo piccolo | — |
   | È solo il mercato | Compressioni comuni con BTC | — |
   | Falsa rottura | Rientro rapido nella banda | — |
   | Sovrapposizione con Donchian (I-02) | Stessi ingressi | Ingressi diversi |
   | Pochi episodi | Trade sotto il minimo | `conta_trade` |
   | Uscita alla media mobile troppo stretta | Vincenti tagliati presto | — |
6. **Varianti.** 4 ore (6 mesi di barre giornaliere sono troppo pochi qui; 125 barre di 4 ore
   sono circa 3 settimane: la stessa regola su un orizzonte più corto, dichiarato).
   - **V-18 (long).** Ampiezza = 4·devstd(20)/media(20); compressione alla barra j se l'ampiezza
     di j è il minimo delle 125 barre fino a j; alla barra i, se c'è una compressione in i−10..i e
     close(i) > banda superiore → long; stop close − 2·ATR(14); uscita quando close < media(20).
   - **V-19 (short).** Specchio: close < banda inferiore → short; uscita quando close > media(20).
   Previsione: R medio fra −0,05 e 0,15; trade forse pochi.

## I-11 Forza relativa contro BTC, a 1 giorno

1. **Fonte.** Y. Liu, A. Tsyvinski, X. Wu, «Common Risk Factors in Cryptocurrency», NBER working
   paper 25882, maggio 2019 (Journal of Finance 77(2), 2022): il fattore momentum fra monete.
   Qui in forma di serie: la forza di AVAX rispetto a BTC.
2. **Affermazione.** Quando il rapporto AVAX/BTC è salito negli ultimi 14 giorni, il long su AVAX
   nei 3 giorni dopo rende più di un long casuale con la stessa uscita.
3. **Sotto-domande.** Vale anche quando BTC scende? Chi opera: chi ruota il capitale verso le
   monete forti; effetto in giorni-settimane.
4-5. **Spiegazioni concorrenti.**
   | Spiegazione | Previsione | Smentita |
   |---|---|---|
   | Caso | `t` entro ±2 | `t` oltre soglia |
   | Volatilità | Forza relativa nei periodi volatili | — |
   | Trend di fondo | Long nel 2021 | Battere la (b) |
   | Artefatto dei dati | Giorni di BTC mancanti | Allineamento per ts |
   | Effetto costi | Stop larghi: costo piccolo | — |
   | È solo il mercato | Forza relativa = beta alto in un mercato in rialzo | Effetto anche con BTC in calo |
   | Coincide con I-01 | Stessi giorni d'ingresso | — |
   | Rotazione di settore (notizie dell'ecosistema) | Pochi episodi | — |
   | Inversione fra monete a breve | R negativo nei primi giorni | — |
   | Rapporto rumoroso | — | — |
6. **Variante.** 1 giorno.
   - **V-20 (long).** (close AVAX/close BTC)(i) / (stesso rapporto)(i−14) − 1 > 0 → long; stop
     close − 2·ATR(14); uscita dopo 3 barre.
   Previsione: R medio fra 0 e 0,1; poco probabile netto.

## I-12 Premio del volume alto, a 4 ore

1. **Fonte.** S. Gervais, R. Kaniel, D. H. Mingelgrin, «The High-Volume Return Premium», Journal
   of Finance 56(3), 2001: dopo un volume anomalo alto il prezzo sale (più visibilità, più
   compratori).
2. **Affermazione.** Dopo una barra di 4 ore con volume oltre 3 volte la media delle 180 barre
   precedenti, il long nelle 24 ore successive rende più di un long casuale con la stessa uscita.
3. **Sotto-domande.** Dipende dal segno della barra? Chi opera: nuovi partecipanti attratti
   dall'attenzione; effetto in giorni (nella fonte, settimane).
4-5. **Spiegazioni concorrenti.**
   | Spiegazione | Previsione | Smentita |
   |---|---|---|
   | Caso | `t` entro ±2 | `t` oltre soglia |
   | Volatilità | Volume alto = barre volatili: R grandi in entrambi i sensi | Segno stabile |
   | Trend di fondo | Long nel 2021 | Battere la (b) |
   | Artefatto dei dati | Volume in moneta base: con prezzo che sale il volume in moneta scende (bias) | — |
   | Effetto costi | Stop 2 ATR: costo piccolo | — |
   | È solo il mercato | Volume alto comune al mercato | — |
   | Capitolazione (volume alto nei crolli) | Long dopo crolli: rimbalzo o continuazione | — |
   | Euforia (volume alto nei picchi) | Long sul picco perde | — |
   | Liquidazioni | Volume da liquidazioni, non da nuovi compratori | — |
   | Pochi eventi | `conta_trade` | — |
6. **Variante.** 4 ore (la fonte è giornaliera-settimanale; a 1 giorno gli eventi oltre 3 volte
   la media sarebbero pochi).
   - **V-21 (long).** volume(i) > 3 × media del volume delle 180 barre precedenti → long; stop
     close − 2·ATR(14); uscita dopo 6 barre.
   Previsione: R medio fra −0,1 e 0,1.
