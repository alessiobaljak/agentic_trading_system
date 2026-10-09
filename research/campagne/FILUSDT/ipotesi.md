# Ipotesi della campagna FILUSDT

Ogni idea è scritta qui PRIMA del suo primo test (Fase 1 del protocollo, regola 6). Le varianti di
un'idea sono tutte elencate qui, con il loro motivo, prima del primo test di quell'idea. Le fonti
sono pubblicazioni precedenti al 2024-01-01; nessuna viene dal gate, dal registro, dal paper o da
altre monete.

## Regole comuni a tutte le varianti

* **Periodo di costruzione:** 2020-10-01 → 2023-01-08 (830 giorni). Validazione: 2023-01-09 →
  2023-12-31, una volta sola, dopo la Fase 5.
* **Motore:** `src/motore.py`, parametri di `config/parametri.yaml` e della scheda: commissione
  0,05% per lato, slippage 0,02% per lato, rischio 1% a trade, leva massima 2, margine isolato,
  mantenimento 0,025; segnali sul last, stop sul last, liquidazione sul mark; serie caricate con
  `carica_serie_allineate`.
* **Costi in R.** Un giro costa 2 × (0,05% + 0,02%) = 0,14% del nozionale. Con lo stop a distanza
  d dal prezzo d'ingresso il costo vale 0,0014 / d in R: 0,047 R con d = 3%, 0,028 R con d = 5%,
  0,14 R con d = 1%. Il funding si aggiunge (in media positivo: costo per i long, incasso per gli
  short). Le previsioni sotto sono già al netto di questo costo.
* **Filtro di liquidità della Fase 0:** nessun ingresso su segnali di barre dei mesi elencati in
  `mesi_esclusi.json` (uguale per conta dei trade, test e baseline (a); vietati alla (b)).
* **Indicatori:** calcolati solo con barre chiuse (codice in `codice/quadro.py` e
  `codice/varianti.py`). ATR di Wilder. L'ingresso avviene all'apertura della barra dopo il segnale.
* **Stop del bot:** il bot rifiuta stop oltre il 6% (`stop_massimo_bot`); il motore non lo impone,
  ma per ogni variante si riporta la quota di trade con stop oltre il 6%.

---

## I-01 — Momento della serie storica (time-series momentum)

1. **Fonte.** Tobias J. Moskowitz, Yao Hua Ooi, Lasse Heje Pedersen, «Time series momentum»,
   *Journal of Financial Economics* 104(2), maggio 2012. Per le criptovalute: Yukun Liu e Aleh
   Tsyvinski, «Risks and Returns of Cryptocurrency», NBER Working Paper 24877, agosto 2018: il
   rendimento della settimana passata predice positivamente quello della settimana successiva (per
   Bitcoin e per l'indice di mercato delle criptovalute), con un effetto che dura alcune settimane.
2. **Affermazione verificabile.** Su FILUSDT, dopo una settimana (42 barre da 4 ore) con
   rendimento positivo, il rendimento della settimana successiva è in media più alto di quello
   di un ingresso casuale con la stessa uscita; simmetricamente per gli short dopo una settimana
   negativa. Falsificata se l'R medio non supera nettamente la baseline (b) o se è negativo.
3. **Sotto-domande.** Vale di più dopo movimenti grandi o anche dopo quelli piccoli (qui: solo il
   segno, come nella fonte)? Dipende dal regime (rialzo 2021, ribasso 2022)? Chi opera: investitori
   che reagiscono in ritardo alle notizie e trend-follower che comprano dopo i rialzi (sotto-reazione
   iniziale, poi rincorsa); l'effetto, secondo la fonte, si manifesta in 1-4 settimane.
4. **Spiegazioni concorrenti** (con la previsione e cosa la smentirebbe):
   1. *Effetto casuale.* Prevede R medio vicino alla (b) e un `t` sotto 2; smentita da un `t`
      nettamente positivo e stabile negli anni.
   2. *È solo il mercato (FIL segue BTC).* Prevede che il segnale costruito sul rendimento di BTC
      dia lo stesso risultato; smentita se il vantaggio resta quando BTC ha segno opposto.
   3. *Trend di fondo del periodo.* Nel 2021-2022 FIL è stata soprattutto in ribasso: gli short
      vincerebbero comunque. La (b) entra a caso nella stessa direzione, quindi il trend lo misura
      lei; smentita se il candidato batte la (b), non solo il buy and hold.
   4. *Volatilità.* Dopo settimane forti la volatilità è alta: R più disperso, non più alto. Prevede
      R medio uguale alla (b) con errore più grande; smentita da una media più alta.
   5. *Artefatto dei dati.* Buchi o barre tolte all'allineamento producono rendimenti a 42 barre
      falsi. Prevede vantaggio concentrato vicino ai buchi; smentita se i trade vicini ai buchi sono
      pochi e non diversi dagli altri.
   6. *Effetto costi.* Il vantaggio lordo esiste ma i costi lo mangiano. Prevede R lordo positivo e
      netto vicino a zero; si vede dai costi medi in R.
   7. *Funding.* Dopo i rialzi il funding è alto: i long pagano, gli short incassano. Prevede che
      gli short guadagnino in parte dal funding; si vede dal funding totale in R.
   8. *Pochi episodi estremi.* Due o tre rally del 2021 fanno tutto il risultato. Prevede R medio
      senza i 3 migliori vicino a zero; smentita se resta sopra la (b).
   9. *Inversione invece di momento.* Sulle altcoin a orizzonte settimanale potrebbe dominare
      l'inversione (eccesso di reazione). Prevede R medio sotto la (b); smentita dal contrario.
   10. *Sovrapposizione dei trade.* Ingressi consecutivi nello stesso trend contano come trade
       indipendenti. Il blocco del bootstrap lo copre; il `t` contro la (b) lo dice.
   11. *Dipendenza dal regime.* Funziona in un anno solo. Prevede R per anno di segno diverso;
       smentita se più della metà degli anni supera la (b).
5. Le previsioni e le smentite sono scritte accanto a ogni spiegazione.
6. **Ipotesi completa.** FILUSDT, momento della serie storica settimanale, candele da 4 ore (il
   segnale settimanale si misura su 42 barre; 4 ore danno ingressi a cadenza fine senza costi
   proporzionalmente alti). Due direzioni, due varianti:
   * **I-01 V1 (long):** alla chiusura di una barra, se il rendimento delle ultime 42 barre (close
     su close di 42 barre prima) è positivo, entra long. Stop: close − 2 × ATR(14). Nessun
     target. Uscita: dopo 42 barre in posizione (una settimana), all'apertura della barra dopo.
   * **I-01 V2 (short):** speculare: rendimento a 42 barre negativo, short, stop close + 2 × ATR(14),
     uscita dopo 42 barre.
   Motivo dei parametri: 42 barre = una settimana, l'orizzonte della fonte; 2 ATR è lo stop usuale
   dei trend-follower, abbastanza largo da non uscire per il rumore di una settimana e in media
   sotto il 6% del bot sulle candele da 4 ore.
7. **Previsione.** Debole: R medio fra −0,05 e +0,10 in entrambe le direzioni; per il long una
   differenza contro la (b) non netta.

---

## I-02 — Rottura del canale dei prezzi (trading range break)

1. **Fonte.** William Brock, Josef Lakonishok, Blake LeBaron, «Simple Technical Trading Rules and
   the Stochastic Properties of Stock Returns», *The Journal of Finance* 47(5), dicembre 1992: la
   regola di rottura del massimo (minimo) dei giorni precedenti produce rendimenti successivi più
   alti (più bassi) di quelli incondizionati. Regola d'uscita a canale opposto più corto: Curtis M.
   Faith, «Way of the Turtle», McGraw-Hill, 2007.
2. **Affermazione verificabile.** Su FILUSDT, quando il close da 4 ore supera il massimo delle 30
   barre precedenti (5 giorni), i rendimenti successivi fino alla rottura del minimo delle 15 barre
   precedenti sono più alti di quelli di ingressi casuali con la stessa uscita; speculare per gli
   short.
3. **Sotto-domande.** La rottura funziona meglio con volatilità bassa prima (compressione)? Chi
   opera: ordini stop accumulati sopra il massimo (chi è short chiude, chi aspettava la rottura
   compra), più trend-follower sistematici; l'effetto dovrebbe vedersi nelle prime barre dopo la
   rottura e durare finché il trend tiene.
4. **Spiegazioni concorrenti:**
   1. *Effetto casuale:* `t` contro la (b) sotto 2; smentita da `t` netto e stabile.
   2. *È solo il mercato:* le rotture di FIL coincidono con quelle di BTC; prevede lo stesso
      risultato entrando sulle rotture di BTC; smentita se le rotture di FIL senza BTC rendono uguale.
   3. *Trend di fondo:* nel ribasso del 2022 gli short vincono comunque; lo misura la (b).
   4. *Falsi segnali in laterale:* molte rotture fallite pagano poco ciascuna e poche vincono
      molto; prevede win rate basso e R medio trainato dai migliori; si vede senza i 3 migliori.
   5. *Volatilità:* le rotture avvengono con volatilità in espansione; lo stop in ATR si allarga e
      l'R si comprime; prevede R vicino alla (b).
   6. *Artefatto dei dati:* barre tolte creano massimi falsi; smentita se i trade vicino ai buchi
      sono pochi.
   7. *Costi:* l'uscita a canale genera molti trade brevi in laterale; prevede costi medi alti in R.
   8. *Pochi episodi estremi:* il rally di aprile 2021 o il crollo di maggio 2021 fanno tutto.
   9. *Ritorno verso la media dopo la rottura (falso breakout sulle altcoin):* prevede R sotto la (b).
   10. *Funding:* dopo le rotture al rialzo il funding sale; il long paga; si vede dal funding in R.
   11. *Dipendenza dal regime:* un anno solo; si vede dall'R per anno.
5. Previsioni e smentite accanto a ogni spiegazione.
6. **Ipotesi completa.** FILUSDT, rottura del canale, candele da 4 ore (rotture di 5 giorni: la
   scala intermedia fra la fonte, a giorni, e la frequenza necessaria ai trade minimi).
   * **I-02 V1 (long):** close > massimo degli high delle 30 barre precedenti → long. Stop iniziale
     close − 2 × ATR(14). Uscita «chiudi» quando il close scende sotto il minimo dei low delle 15
     barre precedenti. Nessun target.
   * **I-02 V2 (short):** close < minimo dei low delle 30 barre precedenti → short. Stop close +
     2 × ATR(14). Uscita quando il close sale sopra il massimo degli high delle 15 barre precedenti.
   Motivo: 30/15 riprende il rapporto 2:1 delle due finestre della fonte delle tartarughe (20/10 e
   55/20) su una scala di 5 giorni.
7. **Previsione.** R medio fra −0,10 e +0,15; win rate sotto il 40%; nessuna delle due nettamente
   sopra la (b).

**Aggiunta del 2026-10-09, dopo il conteggio dei trade (nessun risultato visto).** V1 e V2 sono
scarti: `conta_trade` dà 52 e 49 trade, sotto i 70 minimi. Le varianti che seguono allentano le
soglie per arrivare ai trade minimi (regola 6: è ancora una variante dell'idea nuova), con i
parametri del «sistema 1» della fonte delle tartarughe (rottura di 20, uscita a 10), sulla
stessa scala di 4 ore. Restano due varianti testabili per questa fonte.
   * **I-02 V3 (long):** close > massimo degli high delle 20 barre precedenti → long. Stop close −
     2 × ATR(14). Uscita quando il close scende sotto il minimo dei low delle 10 barre precedenti.
   * **I-02 V4 (short):** close < minimo dei low delle 20 barre precedenti → short. Stop close +
     2 × ATR(14). Uscita quando il close sale sopra il massimo degli high delle 10 barre precedenti.
   Previsione per V3 e V4: come sopra (R medio fra −0,10 e +0,15, non netto).

---

## I-03 — Inversione a breve dopo i movimenti estremi

1. **Fonte.** Bruce N. Lehmann, «Fads, Martingales, and Market Efficiency», *The Quarterly Journal
   of Economics* 105(1), febbraio 1990; Narasimhan Jegadeesh, «Evidence of Predictable Behavior of
   Security Returns», *The Journal of Finance* 45(3), luglio 1990: i rendimenti di breve periodo si
   invertono in parte, per eccesso di reazione e per la pressione di chi chiede liquidità.
2. **Affermazione verificabile.** Su FILUSDT, dopo un calo nelle ultime 24 ore oltre 2 deviazioni
   standard (misurate sui 30 giorni precedenti), le 24 ore successive rendono più di un ingresso
   casuale long con la stessa uscita; speculare per gli short dopo un rialzo oltre 2 deviazioni.
3. **Sotto-domande.** Vale per cali con notizie (che non si invertono) o senza? Chi opera: venditori
   forzati (liquidazioni dei long a leva, margini) che spingono il prezzo sotto il valore, e
   fornitori di liquidità che comprano con uno sconto; l'effetto dovrebbe chiudersi in ore o giorni.
4. **Spiegazioni concorrenti:**
   1. *Effetto casuale:* `t` sotto 2.
   2. *È solo il mercato:* il calo di FIL è un calo di tutto il mercato e il rimbalzo è quello di
      BTC; prevede lo stesso risultato condizionando sul calo di BTC.
   3. *Trend di fondo:* nel 2022 i rimbalzi dei long falliscono più spesso; lo misura la (b).
   4. *Momento invece che inversione:* le cadute continuano (liquidazioni a catena); prevede R
      sotto la (b).
   5. *Volatilità:* dopo un movimento estremo la volatilità è alta; R più disperso.
   6. *Artefatto dei dati:* un buco nei dati simula un movimento di 24 ore; smentita se i segnali
      vicino ai buchi sono pochi.
   7. *Costi:* il rimbalzo vale meno di 0,14% + slippage reale; prevede R lordo positivo ma netto
      vicino a zero.
   8. *Pochi episodi:* due o tre crolli (maggio 2021) fanno tutto il risultato.
   9. *Notizie:* i movimenti con notizie non si invertono; il risultato dipende dalla quota di
      movimenti senza notizie, che non si osserva; prevede alta dispersione.
   10. *Funding:* dopo un crollo il funding diventa negativo e il long incassa; si vede dal funding.
   11. *Grappoli:* i segnali arrivano a grappoli nello stesso episodio; il blocco lo copre.
5. Previsioni e smentite accanto a ogni spiegazione.
6. **Ipotesi completa.** FILUSDT, inversione a breve, candele da 1 ora (il movimento di 24 ore si
   misura su 24 barre; un'ora è abbastanza fine da entrare vicino all'estremo).
   * **I-03 V1 (long):** z = rendimento delle ultime 24 barre / (deviazione standard dei
     rendimenti orari delle 720 barre precedenti × √24); se z < −2 → long. Stop close − 3 ×
     ATR(24). Uscita dopo 24 barre. Nessun target.
   * **I-03 V2 (short):** se z > +2 → short. Stop close + 3 × ATR(24). Uscita dopo 24 barre.
   Motivo: 2 deviazioni standard isolano i movimenti estremi senza ridurre troppo i trade; 3 ATR
   orari (circa 3%) lasciano spazio al rumore dopo un movimento estremo.
7. **Previsione.** Long: R medio fra 0 e +0,10, non netto; short: fra −0,10 e +0,05.

---

Nota sulle idee che seguono (scritta dopo i risultati di I-01 e I-03, che non cambiano nessuna
idea): lo stop di 2 ATR a 4 ore e di 3 ATR orari su FILUSDT vale il 7-9% del prezzo, oltre il
tetto del 6% del bot. Le idee da I-04 in poi scelgono uno stop più stretto (1-1,5 ATR) o in
percentuale, con il motivo scritto qui prima del test.

## I-04 — Inversione delle barre estreme con volume alto (domanda di liquidità)

1. **Fonte.** John Y. Campbell, Sanford J. Grossman, Jiang Wang, «Trading Volume and Serial
   Correlation in Stock Returns», *The Quarterly Journal of Economics* 108(4), novembre 1993: le
   variazioni di prezzo accompagnate da volume alto tendono a invertirsi, perché sono spesso
   domanda di liquidità di operatori non informati, assorbita da chi fornisce liquidità in cambio
   di un rendimento atteso.
2. **Affermazione verificabile.** Su FILUSDT, dopo una barra oraria con un calo oltre 3 deviazioni
   standard dei rendimenti orari (30 giorni) e un volume in USDT oltre 3 volte la media delle 168
   barre precedenti (una settimana), le 12 ore successive rendono più di un ingresso long casuale
   con la stessa uscita; speculare per gli short dopo un rialzo con volume alto.
3. **Sotto-domande.** Chi vende in quella barra: liquidazioni dei long a leva (vendita forzata,
   non informata), stop a cascata; chi compra dopo: market maker e arbitraggisti. L'effetto
   dovrebbe esaurirsi in poche ore. Vale meno se la barra è una notizia (informata): il volume da
   solo non le distingue.
4. **Spiegazioni concorrenti:**
   1. *Effetto casuale:* `t` contro la (b) sotto la soglia; smentita da un `t` netto e stabile.
   2. *È solo il mercato:* la barra estrema è un movimento di BTC; il rimbalzo è quello di BTC;
      prevede lo stesso risultato condizionando sulle barre estreme di BTC.
   3. *Notizie (operatori informati):* le barre con notizie continuano; prevede R sotto la (b) se
      prevalgono.
   4. *Liquidazioni a catena:* la prima barra estrema ne chiama altre; prevede stop frequenti e R
      negativo.
   5. *Volatilità:* dopo la barra estrema la volatilità resta alta; R più disperso, media uguale.
   6. *Trend di fondo:* nel ribasso gli short vincono comunque; lo misura la (b).
   7. *Artefatto dei dati:* barre dopo un buco (riapertura) sembrano estreme; smentita se i segnali
      accanto ai buchi sono pochi.
   8. *Costi:* il rimbalzo in 12 ore vale meno dei costi; prevede R lordo positivo e netto nullo.
   9. *Pochi episodi:* i crolli di maggio 2021 fanno tutto il risultato; si vede senza i 3 migliori.
   10. *Funding:* dopo un crollo il funding scende e i long incassano; si vede dal funding.
   11. *Volume gonfiato:* il volume dei futures include scambi di copertura e di arbitraggio che
       non spingono il prezzo; prevede che la condizione sul volume non aggiunga nulla al solo
       movimento estremo (confronto con la (a)).
5. Previsioni e smentite accanto a ogni spiegazione.
6. **Ipotesi completa.** FILUSDT, inversione delle barre estreme con volume alto, candele da 1 ora
   (la fonte guarda il giorno; sulle crypto la pressione di liquidità si esaurisce in ore).
   * **I-04 V1 (long):** rendimento della barra (close su close precedente) < −3 × deviazione
     standard dei rendimenti orari delle 720 barre fino alla corrente, e volume in USDT della barra
     > 3 × la media delle 168 barre precedenti → long. Stop close − 1,5 × ATR(24). Uscita dopo 12
     barre. Nessun target.
   * **I-04 V2 (short):** rendimento della barra > +3 deviazioni standard e volume > 3 × la media →
     short. Stop close + 1,5 × ATR(24). Uscita dopo 12 barre.
   Motivo: 3 deviazioni e 3 volte il volume isolano le barre di pressione forzata; 12 ore è la
   scala dell'assorbimento; 1,5 ATR orari (circa 4-5%) resta sotto il 6% del bot.
7. **Previsione.** Long: R medio fra −0,05 e +0,15, non netto; short: fra −0,15 e +0,05.

---

## I-05 — Ritracciamento a breve dentro il trend (RSI a 2 periodi)

1. **Fonte.** Larry Connors e Cesar Alvarez, «Short Term Trading Strategies That Work»,
   TradingMarkets Publishing, 2008: comprare quando il prezzo è sopra la media mobile a 200 periodi
   e l'RSI a 2 periodi è sotto 5-10, uscire quando il close torna sopra la media mobile a 5
   periodi; speculare per gli short sotto la media a 200.
2. **Affermazione verificabile.** Su FILUSDT a 4 ore, dentro un trend al rialzo (close sopra la
   media a 200 barre), un ritracciamento brusco (RSI(2) < 10) è seguito da un ritorno sopra la
   media a 5 barre con un R medio più alto di un ingresso casuale long con la stessa uscita;
   speculare per gli short nel trend al ribasso.
3. **Sotto-domande.** Funziona solo in trend netti? Chi opera: chi vende per prendere profitto o
   per paura dopo una serie di barre rosse, contro i compratori del trend che rientrano sui
   ribassi; l'effetto dovrebbe chiudersi in poche barre.
4. **Spiegazioni concorrenti:**
   1. *Effetto casuale:* `t` contro la (b) sotto la soglia.
   2. *È solo il mercato:* i ritracciamenti di FIL sono quelli di BTC; prevede lo stesso
      risultato col segnale su BTC.
   3. *Trend di fondo:* il filtro della media a 200 sceglie i periodi di rialzo; la (b) entra a
      caso su tutte le barre valide, quindi il confronto con la (b) misura insieme il filtro di
      trend e l'RSI; se il vantaggio fosse solo del filtro, una variante senza RSI darebbe lo
      stesso (lo si guarda in Fase 3, non come variante).
   4. *Mean reversion generica:* l'RSI basso funziona anche fuori dal trend; prevede che il filtro
      a 200 non aggiunga nulla.
   5. *Uscita asimmetrica:* uscire sopra la media a 5 produce molti piccoli guadagni e rare grandi
      perdite; prevede win rate alto e mediana positiva con media vicina a zero.
   6. *Volatilità:* i ritracciamenti avvengono in volatilità alta; stop più colpiti.
   7. *Artefatto dei dati:* buchi che fanno crollare l'RSI; pochi segnali vicino ai buchi.
   8. *Costi:* rimbalzi piccoli rispetto ai costi; prevede R lordo positivo e netto nullo.
   9. *Pochi episodi:* due mesi del 2021 fanno tutto.
   10. *Funding:* nei trend al rialzo il funding è alto e i long pagano.
   11. *Regola nata sulle azioni:* sulle crypto a 4 ore la persistenza dei movimenti potrebbe
       prevalere sul ritorno; prevede R sotto la (b).
5. Previsioni e smentite accanto a ogni spiegazione.
6. **Ipotesi completa.** FILUSDT, ritracciamento nel trend, candele da 4 ore (la fonte usa candele
   giornaliere: a 1 giorno i segnali sarebbero troppo pochi in 815 giorni; a 4 ore la media a 200
   barre copre 33 giorni).
   * **I-05 V1 (long):** close > media semplice dei close a 200 barre e RSI(2) < 10 → long. Uscita
     quando il close supera la media semplice a 5 barre. Stop close − 1,5 × ATR(14).
   * **I-05 V2 (short):** close < media a 200 e RSI(2) > 90 → short. Uscita quando il close scende
     sotto la media a 5. Stop close + 1,5 × ATR(14).
   Motivo: soglie 10/90 e medie 200/5 sono quelle della fonte; lo stop (assente nella fonte)
   serve al motore e al bot: 1,5 ATR a 4 ore è circa il 5%.
7. **Previsione.** Long: R medio fra −0,10 e +0,10, win rate sopra il 55%; short: simile.

---

## I-06 — Funding alto o negativo (carry delle crypto)

1. **Fonte.** Maik Schmeling, Andreas Schrimpf, Karamfil Todorov, «Crypto Carry», BIS Working
   Papers n. 1087, aprile 2023: un carry alto (la differenza fra prezzo dei futures e prezzo a
   pronti, che nei perpetui si paga col funding) segnala domanda di leva degli speculatori e
   predice rendimenti futuri più bassi e un rischio di crollo più alto.
2. **Affermazione verificabile.** Su FILUSDT, quando la media degli ultimi 3 settlement di funding
   (un giorno) è sopra lo 0,03% per 8 ore (tre volte il livello base dello 0,01%), uno short
   aperto lì e tenuto 3 giorni rende più di uno short casuale con la stessa uscita. Speculare: con
   funding medio sotto lo
   −0,01% (short affollati), un long rende più di un long casuale.
3. **Sotto-domande.** Vale di più quando il funding è estremo e il prezzo è salito molto? Chi
   opera: speculatori a leva che pagano per stare long (o short); quando il movimento si ferma
   chiudono, e le liquidazioni accelerano l'inversione. L'effetto dovrebbe vedersi in giorni.
4. **Spiegazioni concorrenti:**
   1. *Effetto casuale:* `t` contro la (b) sotto la soglia.
   2. *È solo il mercato:* il funding di FIL è alto quando è alto quello di tutto il mercato; il
      rendimento dopo è quello di BTC.
   3. *Momento:* il funding alto segue i rialzi, e i rialzi continuano (I-01); prevede short in
      perdita.
   4. *Trend di fondo:* gli short guadagnano nel 2021-2022 comunque; lo misura la (b).
   5. *Incasso del funding:* lo short incassa il funding alto: parte del guadagno è funding, non
      prezzo; si vede dal funding in R.
   6. *Volatilità:* il funding alto arriva con volatilità alta; stop colpiti più spesso.
   7. *Artefatto dei dati:* il 2020 ha funding molto negativo per l'avvio del contratto (Fase 0):
      i long del 2020 incassano molto; prevede risultato del long concentrato nel 2020.
   8. *Pochi episodi:* due o tre ondate di funding alto fanno tutto; si vede senza i 3 migliori.
   9. *Costi:* lo short incassa il funding, i costi di commissione sono piccoli a 3 giorni.
   10. *Tempistica del settlement:* il funding si conosce solo al settlement; un segnale che usasse
       il settlement non ancora avvenuto sarebbe lookahead (qui si usano solo i settlement con
       istante entro la chiusura della barra).
   11. *Funding come misura di affollamento imperfetta:* con funding al tetto il prezzo può
       continuare per giorni; prevede alta dispersione.
5. Previsioni e smentite accanto a ogni spiegazione.
6. **Ipotesi completa.** FILUSDT, carry, candele da 8 ore (allineate ai settlement del funding).
   * **I-06 V1 (short):** media degli ultimi 3 settlement con istante entro la chiusura della barra
     > 0,0003 → short. Uscita dopo 9 barre (3 giorni). Stop close + 1 × ATR(14).
   * **I-06 V2 (long):** media degli ultimi 3 settlement < −0,0001 → long. Uscita dopo 9 barre.
     Stop close − 1 × ATR(14).
   Motivo: 0,03% è tre volte il funding base; −0,01% vuol dire che gli short pagano; 3 giorni è
   la scala delle ondate di leva; 1 ATR a 8 ore (circa 6%) resta vicino al tetto del bot.
7. **Previsione.** Short: R medio fra −0,10 e +0,20, non netto; long: fra −0,10 e +0,20, con
   gran parte dei trade nel 2020.

---

## I-07 — Effetto del lunedì

1. **Fonte.** Guglielmo Maria Caporale e Alex Plastun, «The day of the week effect in the
   cryptocurrency market», *Finance Research Letters* 31, dicembre 2019: per Bitcoin i rendimenti
   del lunedì sono anormalmente alti. Anche Dor Aharon e Mahmoud Qadan, «Bitcoin and the
   day-of-the-week effect», *Finance Research Letters* 31, 2019: rendimenti più alti il lunedì.
2. **Affermazione verificabile.** Su FILUSDT, un long aperto all'apertura del lunedì (00:00 UTC) e
   chiuso dopo 24 ore rende più di un long casuale di 24 ore con lo stesso stop.
3. **Sotto-domande.** È un effetto di flussi (ritorno degli operatori istituzionali e delle borse
   tradizionali dopo il fine settimana)? Vale per una moneta piccola come per Bitcoin?
4. **Spiegazioni concorrenti:**
   1. *Effetto casuale:* `t` sotto la soglia (i giorni della settimana sono sette prove).
   2. *È solo il mercato:* il lunedì di FIL è il lunedì di BTC; prevede lo stesso risultato su BTC.
   3. *Trend di fondo:* nel ribasso del 2022 nessun giorno rende; lo misura la (b).
   4. *Volatilità del lunedì:* il lunedì ha più volatilità, non più rendimento.
   5. *Fuso orario:* il «lunedì» UTC comincia la domenica sera in America; l'effetto potrebbe
      cadere in ore diverse.
   6. *Artefatto dei dati:* giorni mancanti (buchi) spostano poco; pochi lunedì toccati.
   7. *Costi:* un giorno di movimento contro costi di 0,14% e lo stop largo: costi piccoli in R.
   8. *Pochi episodi:* tre lunedì del 2021 fanno tutto.
   9. *Effetto scoperto e scomparso:* pubblicato nel 2019, l'effetto potrebbe essere stato
      arbitrato; prevede R vicino alla (b).
   10. *Funding:* i long pagano 3 settlement; costo piccolo.
   11. *Dipendenza dal periodo:* vale solo nel 2021.
5. Previsioni e smentite accanto a ogni spiegazione.
6. **Ipotesi completa.** FILUSDT, effetto del lunedì, candele da 1 giorno.
   * **I-07 V1 (long):** alla chiusura della candela giornaliera della domenica → long all'apertura
     del lunedì. Uscita dopo 1 barra. Stop close × 0,94 (6%, il tetto del bot: una sola giornata).
   Una sola variante: la fonte indica una sola direzione.
7. **Previsione.** R medio fra −0,05 e +0,10, non netto.

---

## I-08 — Ritardo di FIL rispetto a BTC (lead-lag)

1. **Fonte.** Kewei Hou e Tobias J. Moskowitz, «Market Frictions, Price Delay, and the
   Cross-Section of Expected Stock Returns», *The Review of Financial Studies* 18(3), 2005: i
   titoli meno seguiti incorporano in ritardo le notizie di mercato. Per le crypto: Imtiaz Mohammad
   Sifat, Azhar Mohamad, Mohamed Shariff, «Lead-Lag relationship between Bitcoin and Ethereum:
   Evidence from hourly and daily data», *Research in International Business and Finance* 50,
   dicembre 2019.
2. **Affermazione verificabile.** Su FILUSDT a 1 ora, dopo che BTC è salito di oltre il 2% nelle
   ultime 4 ore mentre FIL è salito meno di BTC, le 8 ore successive di FIL rendono più di un long
   casuale con la stessa uscita; speculare dopo un calo di BTC oltre il 2% con FIL calato meno.
3. **Sotto-domande.** Il ritardo dura ore o minuti (arbitraggio veloce)? Chi opera: i market maker
   che aggiornano le quote delle altcoin dopo BTC, i trader che ruotano da BTC alle altcoin.
4. **Spiegazioni concorrenti:**
   1. *Effetto casuale:* `t` sotto la soglia.
   2. *Arbitraggio veloce:* il ritardo si chiude in minuti, non in ore; prevede R vicino alla (b).
   3. *Divergenza informata:* FIL resta indietro per una sua notizia negativa; prevede R sotto la (b).
   4. *Inversione di BTC:* dopo un movimento forte BTC si inverte e trascina FIL; prevede stop.
   5. *Trend di fondo:* lo misura la (b).
   6. *Volatilità:* dopo un movimento di BTC la volatilità di tutte le monete sale.
   7. *Artefatto dei dati:* i buchi di FIL disallineano i rendimenti; segnali nei buchi pochi.
   8. *Costi:* 8 ore di ritardo valgono meno dei costi.
   9. *Pochi episodi:* pochi giorni di grandi movimenti di BTC.
   10. *Funding:* trascurabile su 8 ore.
   11. *Beta diverso:* FIL ha beta verso BTC diverso da 1; «meno di BTC» è normale per una moneta
       con beta basso; prevede nessun recupero.
5. Previsioni e smentite accanto a ogni spiegazione.
6. **Ipotesi completa.** FILUSDT, ritardo rispetto a BTC, candele da 1 ora.
   * **I-08 V1 (long):** rendimento di BTC sulle ultime 4 barre > +2% e rendimento di FIL sulle
     stesse 4 barre < rendimento di BTC → long. Uscita dopo 8 barre. Stop close − 1,5 × ATR(24).
   * **I-08 V2 (short):** rendimento di BTC sulle ultime 4 barre < −2% e rendimento di FIL >
     rendimento di BTC → short. Uscita dopo 8 barre. Stop close + 1,5 × ATR(24).
   Motivo: 2% in 4 ore è un movimento netto di BTC; 8 ore è la scala dell'aggiustamento in ore
   della fonte; 1,5 ATR orari (circa 4-5%) sotto il tetto del bot.
7. **Previsione.** R medio fra −0,10 e +0,10, non netto, in entrambe.
