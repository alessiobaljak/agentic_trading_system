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
